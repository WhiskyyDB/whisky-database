#!/usr/bin/env python3
"""
WhiskyDB statistics page generator (`WhiskyDB-public`).

Reads the FULL working snapshot (the private pipeline's SQLite, never the public
sample) and writes a citable, embeddable statistics page:

    stats/index.html          the page (URL /stats/)
    stats/charts/<slug>.svg   one standalone SVG per chart (for <img> embeds elsewhere)
    stats/data.json           every figure on the page, machine-readable

Only aggregates leave the private database -- no row-level data is written.
Every figure states its denominator and filter so a reader can reproduce it.

Producers, not appellations: from the 2026.10 edition the snapshot flags the EU eAmbrosia
GI register's rows ("Official GI Producer - Cognac", 273 in 2026-09) with
distilleries.is_gi_appellation = 1. They stay in the dataset but are places of origin, not
companies, so every producer figure (count, countries, country and founded-year coverage)
leaves them out and data.json reports them apart as totals.gi_appellations. A snapshot
without the column (2026.09 and older) is read exactly as before: every row is a producer
and the output is byte-identical to the generator before this rule.

ABV provenance: from the 2026.11 edition each spirit carries spirits.abv_source (label,
producer, off, name: stated by the source; default / unverified: the documented 40.0). The
ABV section then counts the source-stated ABVs, a stated 40.0 included. A snapshot without
the column (2026.10 and older) cannot tell a stated 40.0 from the default, so it counts the
ABVs other than 40.0, a lower bound, and says so (data.json abv.rule).

Producers & brands (owner decision 2026-10-04): the US label registry, Open Food Facts and
the Wikipedia brands list name brands, not producers, so the page calls the producer rows
"producers and brands"; the count is unchanged.

Re-run after each data refresh, then `python scripts/generate_seo_pages.py`
(sitemap), `python scripts/i18n_common.py build` and `... check`.

Usage:
    python scripts/generate_stats.py                 # ../../06_Fine_Spirits_WhiskyDB/data/whiskydb.sqlite
    python scripts/generate_stats.py --db PATH       # or WHISKYDB_SQLITE=PATH
"""
import argparse
import datetime as dt
import html
import json
import os
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

import section_links  # scripts/section_links.py, the portfolio copy: keeps #fragment arrivals on their section

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "stats"
CHART_DIR = OUT_DIR / "charts"
BASE_URL = "https://whiskydb.dataengineered.io"
PAGE_URL = f"{BASE_URL}/stats/"
BRAND = "WhiskyDB"
FIRST_PUBLISHED = "2026-09-17"
DEFAULT_DB = BASE_DIR.parent / "06_Fine_Spirits_WhiskyDB" / "data" / "whiskydb.sqlite"
DEFAULT_ABV = 40.0  # documented fallback where the source publishes no ABV; excluded from ABV statistics
STATED_ABV = ("label", "producer", "off", "name")  # spirits.abv_source values stated by the source

# Counting countries, not country labels: a label can name several countries (an EU
# geographical indication shared across borders: "France, Italy"), the same country under
# another name, or one of the UK's nations / Companies House jurisdictions. ISO 3166 names
# written with a comma ("Venezuela, Bolivarian Republic of") are one country, not a list.
COUNTRY_SYNONYMS = {"Russian Federation": "Russia", "Slovak Republic": "Slovakia",
                    "People's Republic of China": "China", "Ivory Coast": "Côte d'Ivoire",
                    "United States": "USA", "United States of America": "USA",
                    "Venezuela, Bolivarian Republic of": "Venezuela", "Bolivia, Plurinational State of": "Bolivia",
                    "Korea, Republic of": "South Korea", "Moldova, Republic of": "Moldova",
                    "Iran, Islamic Republic of": "Iran", "Tanzania, United Republic of": "Tanzania",
                    "Taiwan, Province of China": "Taiwan"}
UK_LABELS = {"United Kingdom", "United Kingdom (Northern Ireland)", "England", "Wales", "Scotland",
             "Northern Ireland", "England & Wales"}

# Dark surface palette of the WhiskyDB catalog pages. Single-series charts only:
# one hue (the site gold) per chart, text in ink/muted tokens, never the data color.
P = dict(surface="#0a0b0d", surface2="#111318", ink="#f0f2f8", muted="#949ab1",
         grid="#22252d", accent="#d4af37")
FONT = "'Inter', 'Outfit', system-ui, -apple-system, 'Segoe UI', sans-serif"
MONO = "'Fira Code', ui-monospace, Menlo, Consolas, monospace"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s), quote=True)


def n(v):
    return f"{int(round(v)):,}"


def pct(part, whole, digits=1):
    return 0.0 if not whole else round(100.0 * part / whole, digits)


def gbp(v):
    return f"£{int(round(v)):,}"


def data(v):
    """A data value (country, distillery, type...) kept verbatim by scripts/i18n_common.py."""
    return f'<span translate="no">{esc(v)}</span>'


def countries_of(label):
    """The countries a (normalized) country label names: multi-country labels are split,
    synonyms merged, and the UK's nations and jurisdictions counted as the United Kingdom."""
    out = set()
    for part in COUNTRY_SYNONYMS.get(label, label).split(","):
        part = COUNTRY_SYNONYMS.get(part.strip(), part.strip())
        out.add("United Kingdom" if part in UK_LABELS else part)
    return out


def nice_step(vmax, target_ticks=5):
    raw = vmax / target_ticks
    mag = 10 ** (len(str(int(raw))) - 1) if raw >= 1 else 1
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


# ---------------------------------------------------------------------------
# SVG charts (self-contained: work inline and as standalone files)
# ---------------------------------------------------------------------------

def _svg_head(width, height, title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-labelledby="t d" font-family="{FONT}" font-size="12">',
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(subtitle)}</desc>',
        f'<rect width="{width}" height="{height}" fill="{P["surface"]}"/>',
        f'<text x="20" y="26" font-size="15" font-weight="600" fill="{P["ink"]}">{esc(title)}</text>',
        f'<text x="20" y="44" font-size="12" fill="{P["muted"]}">{esc(subtitle)}</text>',
    ]


def _svg_foot(width, height, note):
    return [f'<text x="20" y="{height - 12}" font-size="11" fill="{P["muted"]}">{esc(note)}</text>', "</svg>"]


def chart_ids(svg, slug):
    """Scope a chart's <title id="t">/<desc id="d"> (and its aria-labelledby) to its slug: a page
    inlines many charts, and repeated ids make every chart's accessible name the first chart's.
    Same as the portfolio's stats_common.chart_ids: figure() applies it to the inline copy and
    main() to stats/charts/<slug>.svg; the two stay identical."""
    return (svg.replace('aria-labelledby="t d"', f'aria-labelledby="t-{slug} d-{slug}"', 1)
               .replace('<title id="t">', f'<title id="t-{slug}">', 1)
               .replace('<desc id="d">', f'<desc id="d-{slug}">', 1))


def svg_hbar(title, subtitle, rows, note, width=720, label_w=196):
    """rows: [(label, value, display)] -- one series, bars in the accent hue,
    <= 24px thick, 4px rounded data-end and square at the baseline, value at the tip."""
    top, row_h, bar_h, val_w = 62, 30, 18, 84
    x0 = label_w + 12
    plot_w = width - x0 - val_w - 16
    vmax = max(v for _, v, _ in rows) or 1
    height = top + len(rows) * row_h + 40
    out = _svg_head(width, height, title, subtitle)
    out.append(f'<line x1="{x0}" y1="{top - 6}" x2="{x0}" y2="{top + len(rows) * row_h}" stroke="{P["grid"]}" stroke-width="1"/>')
    for i, (label, v, disp) in enumerate(rows):
        y = top + i * row_h + (row_h - bar_h) / 2
        w = max(2.0, plot_w * v / vmax)
        if w >= 8:
            shape = (f'<path d="M{x0} {y} h{w - 4:.1f} a4 4 0 0 1 4 4 v{bar_h - 8} a4 4 0 0 1 -4 4 h-{w - 4:.1f} z" '
                     f'fill="{P["accent"]}"/>')
        else:
            shape = f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{P["accent"]}"/>'
        out.append(
            f'<g><title>{esc(label)}: {esc(disp)}</title>'
            f'<rect x="0" y="{top + i * row_h}" width="{width}" height="{row_h}" fill="transparent"/>'
            f'{shape}'
            f'<text x="{x0 - 10}" y="{y + bar_h / 2 + 4}" text-anchor="end" fill="{P["ink"]}">{esc(label)}</text>'
            f'<text x="{x0 + w + 8:.1f}" y="{y + bar_h / 2 + 4}" fill="{P["muted"]}" '
            f'font-family="{MONO}" font-size="11">{esc(disp)}</text></g>')
    out += _svg_foot(width, height, note)
    return "\n".join(out)


def svg_line(title, subtitle, points, fmt, note, width=720, height=320, peak_label=None, last_label=None):
    """points: [(xlabel, value)] -- one 2px line in the accent hue, 10% area wash,
    hairline solid gridlines, >= 8px end marker with a 2px surface ring, direct labels
    only at the end and the peak, per-point hover titles."""
    top, left, right, bottom = 62, 56, 96, 46
    plot_w, plot_h = width - left - right, height - top - bottom
    vmax = max(v for _, v in points)
    step = nice_step(vmax)
    ymax = step * (int(vmax / step) + 1)
    xs = [left + plot_w * i / (len(points) - 1) for i in range(len(points))]
    ys = [top + plot_h - plot_h * v / ymax for _, v in points]
    out = _svg_head(width, height, title, subtitle)
    t = 0
    while t <= ymax + 1e-9:
        y = top + plot_h - plot_h * t / ymax
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="{P["grid"]}" stroke-width="1"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" fill="{P["muted"]}" font-size="11" '
                   f'font-family="{MONO}">{esc(fmt(t))}</text>')
        t += step
    every = max(1, len(points) // 9)
    for i, (xl, _) in enumerate(points):
        if i % every == 0 or i == len(points) - 1:
            out.append(f'<text x="{xs[i]:.1f}" y="{top + plot_h + 18}" text-anchor="middle" fill="{P["muted"]}" '
                       f'font-size="11" font-family="{MONO}">{esc(xl)}</text>')
    path = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]:.1f} {ys[i]:.1f}" for i in range(len(points)))
    out.append(f'<path d="{path} L{xs[-1]:.1f} {top + plot_h} L{xs[0]:.1f} {top + plot_h} Z" fill="{P["accent"]}" fill-opacity="0.1"/>')
    out.append(f'<path d="{path}" fill="none" stroke="{P["accent"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    for i, (xl, v) in enumerate(points):
        out.append(f'<g><title>{esc(xl)}: {esc(fmt(v))}</title><circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="12" fill="transparent"/></g>')
    if peak_label:
        pi = max(range(len(points)), key=lambda i: points[i][1])
        out.append(f'<circle cx="{xs[pi]:.1f}" cy="{ys[pi]:.1f}" r="5" fill="{P["accent"]}" stroke="{P["surface"]}" stroke-width="2"/>')
        out.append(f'<text x="{xs[pi]:.1f}" y="{ys[pi] - 12:.1f}" text-anchor="middle" fill="{P["ink"]}" font-size="11">{esc(peak_label)}</text>')
    out.append(f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="5" fill="{P["accent"]}" stroke="{P["surface"]}" stroke-width="2"/>')
    if last_label:
        out.append(f'<text x="{xs[-1] + 10:.1f}" y="{ys[-1] + 4:.1f}" fill="{P["ink"]}" font-size="11">{esc(last_label)}</text>')
    out += _svg_foot(width, height, note)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def compute(db_path):
    con = sqlite3.connect(str(db_path))

    def q(sql, *a):
        return con.execute(sql, a).fetchall()
    s = {}

    # Producer rows: every distilleries row, minus the flagged EU GI appellations when the
    # snapshot has the flag (see the module docstring). Without the column the filter is the
    # constant 1 and every query below returns what it did before the flag existed.
    flagged = "is_gi_appellation" in {r[1] for r in q("pragma table_info(distilleries)")}
    prod = "d.is_gi_appellation = 0" if flagged else "1"
    s["gi_appellations"] = q("select count(*) from distilleries where is_gi_appellation = 1")[0][0] if flagged else None

    s["snapshot_date"] = q("select max(date(access_timestamp)) from data_sources")[0][0]
    s["spirits"] = q("select count(*) from spirits")[0][0]
    # bottlings with a bottle volume: all of them up to 2026.10 (documented defaults filled the
    # rest), only the source-stated ones from 2026.11 (check_claims.py words the disclosure by it)
    s["volume_stated"] = q("select count(*) from spirits where volume_ml is not null")[0][0]
    s["producers"] = q(f"select count(*) from distilleries d where {prod}")[0][0]
    s["producers_with_country"] = q(f"select count(*) from distilleries d where d.country<>'Global' and {prod}")[0][0]
    s["price_rows"] = q("select count(*) from price_benchmarks")[0][0]
    s["price_first"], s["price_last"] = q("select min(valuation_date), max(valuation_date) from price_benchmarks")[0]

    # --- auction index: one value per distillery per month (the benchmark row is
    # repeated for every bottling linked to the distillery, so dedupe first) ---
    dm = {}
    for did, name, month, gbp_v, usd_v in q(
            "select d.distillery_id, d.name, substr(p.valuation_date,1,7), avg(p.original_price), avg(p.price_usd) "
            "from price_benchmarks p join spirits s using(spirit_id) join distilleries d using(distillery_id) "
            "where p.original_currency='GBP' group by 1,2,3"):
        dm.setdefault(did, {"name": name, "months": {}})["months"][month] = (gbp_v, usd_v)
    s["price_distilleries"] = len(dm)
    s["price_distillery_months"] = sum(len(d["months"]) for d in dm.values())
    first_year, last_year = int(s["price_first"][:4]), int(s["price_last"][:4])
    # like-for-like: distilleries with data in the first full year and in the last year
    lfl = [did for did, d in dm.items()
           if any(m.startswith(str(first_year + 1)) for m in d["months"]) and any(m.startswith(str(last_year)) for m in d["months"])]
    s["lfl_n"] = len(lfl)
    s["lfl_names"] = sorted(dm[d]["name"] for d in lfl)
    s["lfl_months"] = sum(len(dm[d]["months"]) for d in lfl)
    years = list(range(first_year + 1, last_year + 1))
    per_dist_year = {did: {} for did in lfl}
    for did in lfl:
        by_year = defaultdict(list)
        for m, (g, _) in dm[did]["months"].items():
            by_year[int(m[:4])].append(g)
        for y, vals in by_year.items():
            per_dist_year[did][y] = statistics.mean(vals)
    index = []
    for y in years:
        vals = [per_dist_year[d][y] for d in lfl if y in per_dist_year[d]]
        index.append((y, round(statistics.mean(vals), 1), len(vals)))
    s["index_years"] = index
    s["last_year_months"] = len({m for d in lfl for m in dm[d]["months"] if m.startswith(str(last_year))})
    peak = max(index, key=lambda t: t[1])
    s["index_peak"] = dict(year=peak[0], value=peak[1])
    s["index_first"] = dict(year=index[0][0], value=index[0][1])
    s["index_last"] = dict(year=index[-1][0], value=index[-1][1])
    s["index_multiple"] = round(index[-1][1] / index[0][1], 2)
    s["index_from_peak_pct"] = round(100.0 * (index[-1][1] / peak[1] - 1), 1)
    # peak month across the like-for-like set
    month_vals = defaultdict(list)
    for d in lfl:
        for m, (g, _) in dm[d]["months"].items():
            month_vals[m].append(g)
    pm = max(month_vals, key=lambda m: statistics.mean(month_vals[m]))
    s["index_peak_month"] = dict(month=pm, value=round(statistics.mean(month_vals[pm]), 1))
    # per distillery: decade change and latest level
    y_lo, y_hi = last_year - 10, last_year
    per = []
    for d in lfl:
        a, b, c = per_dist_year[d].get(y_lo), per_dist_year[d].get(y_hi), per_dist_year[d].get(years[0])
        if a and b:
            per.append((dm[d]["name"], round(c, 1) if c else None, round(a, 1), round(b, 1), round(100.0 * (b / a - 1), 1)))
    s["per_distillery"] = sorted(per, key=lambda t: -t[3])
    s["decade_lo"], s["decade_hi"] = y_lo, y_hi

    # --- spirit types ---
    types = q("select spirit_type, count(*) from spirits group by 1 order by 2 desc")
    s["types"] = [(k, v, pct(v, s["spirits"])) for k, v in types]

    # --- ABV: stated by the source only (abv_source); without the column, ABVs other than 40.0 ---
    s["abv_by_source"] = "abv_source" in {r[1] for r in q("pragma table_info(spirits)")}
    marks = ",".join("?" * len(STATED_ABV))
    abv_filter, abv_args = ((f"abv_source in ({marks})", STATED_ABV) if s["abv_by_source"]
                            else ("abv_percentage<>?", (DEFAULT_ABV,)))
    abv = [v for (v,) in q(f"select abv_percentage from spirits where {abv_filter}", *abv_args)]
    s["abv_n"] = len(abv)
    s["abv_mean"] = round(statistics.mean(abv), 1)
    s["abv_median"] = round(statistics.median(abv), 1)
    s["abv_max"] = max(abv)
    s["abv_cask_strength_pct"] = pct(sum(1 for v in abv if v >= 50), len(abv))
    buckets = [("Below 40%", 0, 40), ("40 to 42.9%", 40, 43), ("43 to 45.9%", 43, 46), ("46 to 49.9%", 46, 50),
               ("50 to 54.9%", 50, 55), ("55 to 59.9%", 55, 60), ("60% and above", 60, 999)]
    s["abv_buckets"] = [(lbl, sum(1 for v in abv if lo <= v < hi), pct(sum(1 for v in abv if lo <= v < hi), len(abv)))
                        for lbl, lo, hi in buckets]
    s["abv_by_type"] = [(k, c, round(m, 1), round(mx, 1)) for k, c, m, mx in q(
        f"select spirit_type, count(*), avg(abv_percentage), max(abv_percentage) from spirits where {abv_filter} "
        "group by 1 having count(*)>=10 order by 3 desc", *abv_args)]

    # --- producers by country (Open Food Facts tags like "en:switzerland" are normalized). The
    # chart and table list the labels as recorded; the country count splits and merges them
    # (countries_of). Up to the 2026.10 edition Open Food Facts rows carried the first country
    # the product is sold in (16 of them as a raw "en:" tag in 2026.10); from 2026.11 (owner
    # decision 2026-10-04) a producer's country is a stated origin or headquarters, or 'Global',
    # and the private pipeline's tests forbid raw tags. A raw tag in the snapshot therefore marks
    # the old rule: the method note below says which one applies, and data.json carries
    # "producer_country_rule": "stated" only under the new one (check_claims.py compares it with
    # the edition). ---
    s["off_sold_in_countries"] = q("select count(*) from distilleries d join data_sources ds using(source_id) "
                                   "where ds.source_name like 'Open Food Facts%' and d.country like 'en:%'")[0][0] > 0
    pc = defaultdict(int)
    named, named_elsewhere = set(), set()
    for k, off, v in q("select d.country, ds.source_name like 'Open Food Facts%', count(*) from distilleries d "
                       f"join data_sources ds using(source_id) where d.country<>'Global' and {prod} group by 1, 2"):
        if k.startswith("en:"):
            k = k[3:].replace("-", " ").title().replace("Cote D Ivoire", "Côte d'Ivoire").replace("Usa", "USA")
        pc[k] += v
        named |= countries_of(k)
        if not off:
            named_elsewhere |= countries_of(k)
    s["producer_countries"] = len(named)
    s["producer_countries_off_only"] = len(named - named_elsewhere)
    s["producers_by_country"] = [(k, v, pct(v, s["producers_with_country"])) for k, v in sorted(pc.items(), key=lambda t: (-t[1], t[0]))]

    # --- founding decades (every source that carries a founded_year) ---
    fy = q(f"select d.founded_year from distilleries d where d.founded_year between 1500 and 2100 and {prod}")
    s["founded_n"] = len(fy)
    s["founded_src"] = {name: c for name, c in q(
        "select ds.source_name, count(*) from distilleries d join data_sources ds using(source_id) "
        f"where d.founded_year between 1500 and 2100 and {prod} group by 1 order by 2 desc")}
    dec = defaultdict(int)
    for (y,) in fy:
        dec[(y // 10) * 10] += 1
    s["founded_by_decade"] = [(f"{d}s", c, pct(c, len(fy))) for d, c in sorted(dec.items()) if d >= 1900]
    s["founded_pre1900"] = sum(c for d, c in dec.items() if d < 1900)
    s["founded_2010_plus"] = sum(c for d, c in dec.items() if d >= 2010)
    s["founded_2010_plus_pct"] = pct(s["founded_2010_plus"], len(fy))

    # --- Companies House status by UK jurisdiction ---
    st = defaultdict(lambda: defaultdict(int))
    for c, status, cnt in q("select d.country, d.status, count(*) from distilleries d join data_sources ds using(source_id) "
                            f"where ds.source_name like 'UK Companies House%' and {prod} group by 1,2"):
        st[c][status] += cnt
    s["uk_status"] = [(c, sum(v.values()), v.get("Active", 0), v.get("Dissolved", 0),
                       pct(v.get("Dissolved", 0), sum(v.values()))) for c, v in sorted(st.items(), key=lambda t: -sum(t[1].values()))]
    con.close()
    return s


# ---------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------

CSS = """
    :root { --bg-dark: #0a0b0d; --bg-card: #111318; --gold: #d4af37; --gold-light: #e2c044; --text-main: #f0f2f8;
            --text-muted: #949ab1; --border: rgba(212, 175, 55, 0.2); }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-main); line-height: 1.6; padding-bottom: 60px; }
    .heading { font-family: 'Outfit', sans-serif; font-weight: 700; }
    .mono { font-family: 'Fira Code', monospace; }
    header { border-bottom: 1px solid var(--border); padding: 20px 0; background: rgba(17, 19, 24, 0.8); backdrop-filter: blur(10px); }
    .container { max-width: 1000px; margin: 0 auto; padding: 0 24px; }
    .nav-bar { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
    .brand { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text-main); text-decoration: none; }
    .brand span { color: var(--gold); }
    .btn-link { color: var(--text-main); text-decoration: none; font-size: 0.9rem; border: 1px solid var(--border); padding: 8px 16px; border-radius: 6px; transition: all 0.2s; display: inline-block; }
    .btn-link:hover { background: var(--gold); color: #0a0b0d; border-color: var(--gold); }
    a { color: var(--gold-light); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .hero { padding: 48px 0 8px; }
    h1 { font-size: 2.6rem; line-height: 1.15; }
    h2 { font-size: 1.5rem; color: var(--gold); }
    h3 { font-size: 1.05rem; }
    .lede { color: var(--text-muted); font-size: 1.08rem; margin-top: 14px; max-width: 72ch; }
    .tiles { list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 28px; padding: 0; }
    .tiles li { background: var(--bg-card); border: 1px solid var(--border); padding: 16px 18px; border-radius: 10px; }
    .tiles span { display: block; color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }
    .tiles strong { font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 700; line-height: 1.2; }
    .tiles li.date strong { font-size: 1.15rem; white-space: nowrap; }
    .toc { margin-top: 28px; padding: 16px 20px; border: 1px solid var(--border); border-radius: 10px; font-size: 0.9rem; }
    .toc ol { margin: 8px 0 0 18px; columns: 2; column-gap: 32px; }
    .toc li { break-inside: avoid; }
    section.stat { margin-top: 56px; padding-top: 32px; border-top: 1px solid var(--border); }
    .finding { margin-top: 12px; font-size: 1.02rem; max-width: 72ch; }
    .finding strong { color: var(--gold-light); }
    figure { margin: 24px 0 0; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
    figure svg { display: block; width: 100%; height: auto; }
    figcaption { padding: 10px 14px; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border); display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    details { margin-top: 14px; font-size: 0.88rem; }
    summary { cursor: pointer; color: var(--gold-light); }
    details pre { margin-top: 10px; padding: 12px 14px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; font-family: 'Fira Code', monospace; font-size: 0.74rem; white-space: pre-wrap; word-break: break-all; }
    .copy { margin-top: 8px; background: none; border: 1px solid var(--border); color: var(--text-main); font-family: inherit; font-size: 0.78rem; padding: 6px 12px; border-radius: 6px; cursor: pointer; }
    .copy:hover { border-color: var(--gold); color: var(--gold-light); }
    .tbl { overflow-x: auto; margin-top: 18px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    th, td { padding: 9px 12px; text-align: left; border-bottom: 1px dashed rgba(212,175,55,0.15); vertical-align: top; }
    th { background: var(--bg-card); text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; color: var(--text-muted); }
    td.num, th.num { text-align: right; font-family: 'Fira Code', monospace; font-variant-numeric: tabular-nums; white-space: nowrap; }
    .method { margin-top: 12px; font-size: 0.86rem; color: var(--text-muted); max-width: 80ch; }
    .method li { margin: 6px 0 0 18px; }
    .cta { margin-top: 60px; padding: 32px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; text-align: center; }
    footer { margin-top: 60px; border-top: 1px solid var(--border); padding: 32px 0; text-align: center; font-size: 0.85rem; color: var(--text-muted); }
    @media (max-width: 640px) { h1 { font-size: 1.8rem; } .toc ol { columns: 1; } }
"""


def embed_block(slug, title):
    img = f"{BASE_URL}/stats/charts/{slug}.svg"
    snippet = (f'<a href="{PAGE_URL}#fig-{slug}"><img src="{img}" alt="{esc(title)}" width="720" '
               f'style="max-width:100%;height:auto"></a>\n'
               f'<p><small>Source: <a href="{PAGE_URL}">{BRAND} whisky statistics</a> (CC BY 4.0)</small></p>')
    return (f'<details><summary>Embed this chart</summary>'
            f'<p style="margin-top:8px;color:var(--text-muted)">Paste the snippet into your post. It links the chart back to this page, which is the only attribution we ask for.</p>'
            f'<pre translate="no"><code id="embed-{slug}">{esc(snippet)}</code></pre>'
            f'<button type="button" class="copy" data-target="embed-{slug}">Copy snippet</button></details>')


def figure(slug, svg, title, note):
    return (f'<figure id="fig-{slug}">{chart_ids(svg, slug)}<figcaption><span>{esc(note)}</span>'
            f'<a href="/stats/charts/{slug}.svg" download="whiskydb-{slug}.svg">Download SVG</a></figcaption></figure>'
            + embed_block(slug, title))


def table(headers, rows, num_cols):
    th = "".join(f'<th{" class=\"num\"" if i in num_cols else ""}>{esc(h)}</th>' for i, h in enumerate(headers))
    body = []
    for r in rows:
        tds = []
        for i, c in enumerate(r):
            tds.append(f'<td class="num">{esc(c)}</td>' if i in num_cols else f"<td>{data(c)}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def section(slug, heading, finding, fig_html, table_html, method):
    return (f'<section class="stat" id="{slug}"><h2 class="heading">{heading}</h2>'
            f'<p class="finding">{finding}</p>{fig_html}{table_html}'
            f'<p class="method">{method}</p></section>')


def build_page(s, charts):
    snap = s["snapshot_date"]
    today = dt.date.today().isoformat()
    src_note = f"Source: WhiskyDB, whiskydb.dataengineered.io/stats · snapshot {snap} · CC BY 4.0"
    sections = []
    ix = s["index_years"]
    f_year, l_year = s["index_first"]["year"], s["index_last"]["year"]
    last_label = f"{l_year} (Jan to {dt.date(2000, int(s['price_last'][5:7]), 1).strftime('%b')})" if s["last_year_months"] < 12 else str(l_year)

    # 1. auction index
    charts["auction-index"] = svg_line(
        f"Whisky auction price index, {f_year} to {l_year}",
        f"Mean monthly winning bid (GBP) across {s['lfl_n']} distilleries tracked over the whole period",
        [(str(y), v) for y, v, _ in ix], gbp, src_note,
        peak_label=f"{gbp(s['index_peak']['value'])} peak ({s['index_peak']['year']})", last_label=gbp(s["index_last"]["value"]))
    sections.append(section(
        "auction-index", "The whisky auction price index",
        f"Across the {s['lfl_n']} distilleries with auction results in both {f_year} and {l_year}, the mean winning bid rose from "
        f"<strong>{gbp(s['index_first']['value'])}</strong> in {f_year} to a peak of <strong>{gbp(s['index_peak']['value'])}</strong> in {s['index_peak']['year']}, "
        f"a {round(s['index_peak']['value'] / s['index_first']['value'], 1)}x increase. It has since eased "
        f"<strong>{abs(s['index_from_peak_pct'])}%</strong> to {gbp(s['index_last']['value'])} in {last_label}, "
        f"still {s['index_multiple']}x its {f_year} level. The single strongest month was {data(s['index_peak_month']['month'])} at {gbp(s['index_peak_month']['value'])}.",
        figure("auction-index", charts["auction-index"], f"Whisky auction price index, {f_year} to {l_year}", f"{s['lfl_n']} distilleries, {n(s['lfl_months'])} distillery-months ({n(s['price_distillery_months'])} across all {n(s['price_distilleries'])} auction distilleries)"),
        table(["Year", "Mean winning bid (GBP)", "Distilleries"], [(str(y) if y != l_year else last_label, gbp(v), n(c)) for y, v, c in ix], {1, 2}),
        f"Source: WhiskyHunter open auction statistics, one distillery-level index value per month (mean winning bid at UK online whisky auctions, GBP), "
        f"{s['price_first']} to {s['price_last']}. Each year is the mean of the distilleries' yearly means, every distillery weighted equally. "
        f"Only the {s['lfl_n']} distilleries with data in both {f_year} and {l_year} are included, so the index compares like with like; "
        f"{s['price_first'][:4]} is dropped as a partial year and {l_year} covers {s['last_year_months']} months. "
        f"This is a market-level index, never a bottle-specific price. Distilleries: {', '.join(s['lfl_names'])}."))

    # 2. per distillery
    per = s["per_distillery"]
    charts["distillery-index"] = svg_hbar(
        f"Distilleries with the highest auction index, {l_year}",
        f"Mean winning bid (GBP), {last_label}",
        [(name, b, gbp(b)) for name, _, _, b, _ in per[:12]], src_note)
    gain = sorted(per, key=lambda t: -t[4])
    charts["distillery-gain"] = svg_hbar(
        f"Ten-year change in auction index, {s['decade_lo']} to {l_year}",
        f"Change in mean winning bid, distilleries tracked since {f_year}",
        [(name, ch, f"+{ch}%" if ch >= 0 else f"{ch}%") for name, _, _, _, ch in gain[:12]], src_note)
    sections.append(section(
        "distilleries", "Which distilleries command the highest prices",
        f"{data(per[0][0])} tops the {l_year} index at <strong>{gbp(per[0][3])}</strong> per lot, ahead of {data(per[1][0])} ({gbp(per[1][3])}) and {data(per[2][0])} ({gbp(per[2][3])}). "
        f"Over the last ten years {data(gain[0][0])} gained the most, <strong>+{gain[0][4]}%</strong> from {gbp(gain[0][2])} to {gbp(gain[0][3])}, "
        f"while {data(gain[-1][0])} moved {gain[-1][4]}%.",
        figure("distillery-index", charts["distillery-index"], f"Distilleries with the highest auction index, {l_year}", f"top 12 of {len(per)} distilleries")
        + figure("distillery-gain", charts["distillery-gain"], f"Ten-year change in auction index, {s['decade_lo']} to {l_year}", f"top 12 of {len(per)} distilleries"),
        table(["Distillery", f"{f_year} (GBP)", f"{s['decade_lo']} (GBP)", f"{l_year} (GBP)", f"Change {s['decade_lo']} to {l_year}"],
              [(name, gbp(c) if c else "", gbp(a), gbp(b), (f"+{ch}%" if ch >= 0 else f"{ch}%")) for name, c, a, b, ch in per], {1, 2, 3, 4}),
        f"Same source and method as the index above: yearly mean of the distillery's monthly index values. {l_year} covers {s['last_year_months']} months. "
        f"Percentage change compares {l_year} with {s['decade_lo']}."))

    # 3. spirit types
    ty = s["types"]
    charts["spirit-types"] = svg_hbar("What is in the catalogue", f"Share of {n(s['spirits'])} bottlings by spirit type",
                                      [(k, v, f"{p}%") for k, v, p in ty[:10]], src_note)
    bourbon = next((p for k, _, p in ty if k == "Bourbon"), 0)
    scotch = sum(p for k, _, p in ty if "Scotch" in k)
    sections.append(section(
        "types", "What is in the catalogue",
        f"<strong>{bourbon}%</strong> of the {n(s['spirits'])} bottlings are Bourbon and <strong>{round(scotch, 1)}%</strong> are Scotch of some kind "
        f"(single malt or blended); {next(p for k, _, p in ty if k == 'Whisky')}% carry only the generic class Whisky on their label filing.",
        figure("spirit-types", charts["spirit-types"], "What is in the catalogue", f"{n(s['spirits'])} bottlings"),
        table(["Spirit type", "Bottlings", "Share"], [(k, n(v), f"{p}%") for k, v, p in ty], {1, 2}),
        "Type is the class stated on the label filing or product record, normalized. The catalogue is built from US federal label approvals (TTB COLA), "
        "Open Food Facts and curated producer data, so it over-represents spirits sold in the United States."))

    # 4. ABV
    ab = s["abv_buckets"]
    if s["abv_by_source"]:
        abv_set, abv_head = "bottlings with an ABV stated by the source", "Bottlings with a stated ABV"
        abv_lead = "Where the source states the ABV"
        abv_note = (f"Only the {n(s['abv_n'])} of {n(s['spirits'])} bottlings whose ABV is stated by the source (the US label, the producer, "
                    f"the Open Food Facts record or the product name; a stated {DEFAULT_ABV:.0f}% included) are counted. The rest carry the documented "
                    f"{DEFAULT_ABV:.0f}% legal-minimum default, because the source states no ABV or because their US label has not been read yet, "
                    f"and are excluded here. Types with fewer than 10 stated ABVs are omitted from the table.")
    else:
        abv_set, abv_head = "bottlings with an ABV other than the 40% default", "Bottlings with an ABV other than 40%"
        abv_lead = "Among bottlings whose ABV differs from the 40% default"
        abv_note = (f"Only the {n(s['abv_n'])} of {n(s['spirits'])} bottlings whose ABV differs from the documented {DEFAULT_ABV:.0f}% legal-minimum default "
                    f"are counted, all of them stated by the source (mostly US label details). In this edition a {DEFAULT_ABV:.0f}% stated by the source "
                    f"cannot be told apart from that default, so it is left out too, and these figures skew towards labels that state a non-standard strength. "
                    f"Types with fewer than 10 such ABVs are omitted from the table.")
    charts["abv"] = svg_hbar("Bottling strength (ABV)", f"Share of {n(s['abv_n'])} {abv_set}",
                             [(k, v, f"{p}%") for k, v, p in ab], src_note)
    sections.append(section(
        "abv", "How strong the bottlings are",
        f"{abv_lead}, the median bottling is <strong>{s['abv_median']}%</strong> and "
        f"<strong>{s['abv_cask_strength_pct']}%</strong> are bottled at 50% or above, cask-strength territory. "
        f"The strongest on record is {s['abv_max']}%. By type, {data(s['abv_by_type'][0][0])} averages the highest at {s['abv_by_type'][0][2]}%.",
        figure("abv", charts["abv"], "Bottling strength (ABV)", f"{n(s['abv_n'])} {abv_set}"),
        table(["Spirit type", abv_head, "Mean ABV", "Highest ABV"],
              [(k, n(c), f"{m}%", f"{mx}%") for k, c, m, mx in s["abv_by_type"]], {1, 2, 3}),
        abv_note))

    # 5. producers by country
    pc = s["producers_by_country"]
    gi = s["gi_appellations"]
    who = ("Producers are distilleries, brands, bottlers and whisky companies from label registries, corporate registries, Wikipedia lists "
           "and open product databases")
    if gi is None:  # a snapshot without the GI flag: the appellations are counted as producers
        who += ", plus the protected spirit appellations of the EU GI register; "
        split = "The country count splits labels that name several countries (appellations shared across borders), merges name variants"
    else:
        who += (f". The {n(gi)} protected spirit appellations of the EU GI register (Scotch Whisky, Cognac, Armagnac…) are in the "
                "dataset as places of origin, not producers, so they are left out here; ") if gi else "; "
        split = "The country count splits labels that name several countries, merges name variants"
    charts["producers-by-country"] = svg_hbar("Where the producers and brands are",
                                              f"Share of {n(s['producers_with_country'])} producers with a stated country",
                                              [(k, v, f"{p}%") for k, v, p in pc[:14]], src_note)
    sections.append(section(
        "countries", "Where the producers and brands are",
        f"{data(pc[0][0])} accounts for <strong>{pc[0][2]}%</strong> of producers with a stated country, {data(pc[1][0])} for {pc[1][2]}% and "
        f"{data(pc[2][0])} for {pc[2][2]}%; {n(s['producer_countries'])} countries appear in total"
        + (f", {n(s['producer_countries_off_only'])} of them only on Open Food Facts records." if s["producer_countries_off_only"] else "."),
        figure("producers-by-country", charts["producers-by-country"], "Where the producers and brands are", f"{n(s['producers_with_country'])} producers"),
        table(["Country", "Producers", "Share"], [(k, n(v), f"{p}%") for k, v, p in pc[:30]], {1, 2}),
        f"{who}{n(s['producers'] - s['producers_with_country'])} records whose country is Global are excluded. "
        f"England & Wales and Scotland follow UK Companies House jurisdictions. {split} and counts the UK once. "
        + ("Open Food Facts records carry the first country the product is listed as sold in, which is not necessarily where it is made."
           if s["off_sold_in_countries"] else
           "A producer's country is where a distillery stands, a company's headquarters or where a brand's whisky is made, as a source "
           "states it; never a country the product is merely sold in. An Open Food Facts producer carries the origin or headquarters a "
           "source states for it (its own Open Food Facts records, its US label or its Wikidata item), or none.")))

    # 6. founding decades
    fd = s["founded_by_decade"]
    charts["founded"] = svg_hbar("When whisky companies were founded", f"Share of {n(s['founded_n'])} producers with a known founding year, by decade",
                                 [(k, v, f"{p}%") for k, v, p in fd], src_note)
    sections.append(section(
        "founded", "The craft distilling boom",
        f"<strong>{s['founded_2010_plus_pct']}%</strong> of producers with a known founding year were founded in {s['founded_by_decade'][-2][0][:4]} or later, "
        f"{n(s['founded_2010_plus'])} companies in under two decades, against {n(s['founded_pre1900'])} founded before 1900.",
        figure("founded", charts["founded"], "When whisky companies were founded", f"{n(s['founded_n'])} producers with a founding year"),
        table(["Decade", "Producers founded", "Share"], [(k, n(v), f"{p}%") for k, v, p in fd], {1, 2}),
        "Founding years come from " + "; ".join(f"{k} ({n(v)})" for k, v in s["founded_src"].items()) + ". "
        "Companies House supplies incorporation dates of UK whisky-related companies, so the recent decades reflect UK company formation "
        "and long-established distilleries are under-counted. Read this as a UK registration signal, not a global census."))

    # 7. UK company status
    uk = s["uk_status"]
    charts["uk-status"] = svg_hbar("UK whisky companies dissolved, by jurisdiction",
                                   "Share of Companies House whisky-related registrations now dissolved",
                                   [(c, d_pct, f"{d_pct}%") for c, _, _, _, d_pct in uk], src_note)
    worst = max(uk, key=lambda t: t[4])
    best = min(uk, key=lambda t: t[4])
    sections.append(section(
        "uk-status", "Survival of UK whisky companies",
        f"<strong>{worst[4]}%</strong> of whisky-related companies registered in {data(worst[0])} have been dissolved, "
        f"against {best[4]}% in {data(best[0])}.",
        figure("uk-status", charts["uk-status"], "UK whisky companies dissolved, by jurisdiction", f"{n(sum(t[1] for t in uk))} Companies House records"),
        table(["Jurisdiction", "Registrations", "Active", "Dissolved", "Dissolved share"],
              [(c, n(t), n(a), n(d), f"{p}%") for c, t, a, d, p in uk], {1, 2, 3, 4}),
        "Company status as recorded by UK Companies House (Open Government Licence) for companies whose registered name or activity is whisky-related. "
        "Jurisdiction follows the company number prefix. Statuses other than Active and Dissolved (applied, registered) are counted in the total only."))

    toc = "".join(f'<li><a href="#{slug}">{title}</a></li>' for slug, title in [
        ("auction-index", "Auction price index"), ("distilleries", "Distillery rankings"), ("types", "Spirit types"),
        ("abv", "Bottling strength"), ("countries", "Producer countries"), ("founded", "Founding decades"),
        ("uk-status", "UK company survival"), ("method", "Method, reuse and citation")])

    title_tag = f"Whisky Statistics {snap[:4]} — Auction Price Index, Types, ABV | {BRAND}"
    desc = (f"Whisky in numbers: a {f_year} to {l_year} auction price index across {s['lfl_n']} distilleries, distillery rankings, "
            f"spirit types, ABV, producer countries and the craft boom, from {n(s['spirits'])} bottlings and {n(s['producers'])} producers. Free to cite and embed.")
    ld_article = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": "Whisky in numbers: auction price index and market statistics from WhiskyDB",
        "description": desc, "url": PAGE_URL, "datePublished": FIRST_PUBLISHED, "dateModified": today,
        "image": f"{BASE_URL}/hero.png", "inLanguage": "en",
        "author": {"@type": "Organization", "name": BRAND, "url": BASE_URL},
        "publisher": {"@type": "Organization", "name": "DataEngineered", "url": "https://dataengineered.io/"},
        "isBasedOn": BASE_URL + "/", "license": "https://creativecommons.org/licenses/by/4.0/",
        "about": ["whisky", "whisky auction prices", "scotch whisky", "bourbon", "distilleries"]}, ensure_ascii=False, indent=2)
    ld_crumbs = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Statistics", "item": PAGE_URL}]}, ensure_ascii=False, indent=2)

    tiles = "".join(
        f'<li{" class=\"date\"" if lbl in ("Snapshot", "Auction history") else ""}><span>{lbl}</span><strong>{val}</strong></li>' for lbl, val in [
            ("Bottlings", n(s["spirits"])), ("Producers & brands", n(s["producers"])), ("Countries", n(s["producer_countries"])),
            ("Auction benchmarks", n(s["price_distillery_months"])), ("Auction history", f"{s['price_first'][:4]} to {s['price_last'][:4]}"), ("Snapshot", snap)])
    gi_li = "" if not s["gi_appellations"] else (
        "\n        <li><strong>Producers, not appellations.</strong> The dataset also lists the "
        f"{n(s['gi_appellations'])} protected spirit appellations of the EU GI register. An appellation is a protected place "
        "of origin, not a company, so every producer figure on this page leaves them out; "
        '<a href="/stats/data.json">data.json</a> reports them apart as <span translate="no">totals.gi_appellations</span>.</li>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title_tag)}</title>
  <meta name="description" content="{esc(desc)}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{PAGE_URL}" />
  <link rel="alternate" hreflang="en" href="{PAGE_URL}" />
  <meta property="og:title" content="Whisky in numbers — {BRAND} statistics {snap[:4]}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{PAGE_URL}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="{BASE_URL}/hero.png" />
  <meta name="twitter:card" content="summary_large_image" />

  <script type="application/ld+json">
{ld_article}
  </script>
  <script type="application/ld+json">
{ld_crumbs}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet"></noscript>
  <style>{CSS}  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="/" class="brand">Whisky<span>DB</span></a>
      <div>
        <a href="/#live-demo-section" class="btn-link">← Explorer</a>
        <a href="/#pricing-section" class="btn-link" style="margin-left: 12px; background: rgba(212,175,55,0.1);">Get Full Dataset ($49)</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="badge mono" style="display:inline-block;background:rgba(212,175,55,0.15);color:var(--gold-light);padding:4px 12px;border-radius:4px;font-size:0.8rem;font-weight:600;margin-bottom:12px;border:1px solid rgba(212,175,55,0.3);">MARKET STATISTICS · SNAPSHOT {esc(snap)}</span>
      <h1 class="heading">Whisky in numbers</h1>
      <p class="lede">Aggregate statistics computed from the full WhiskyDB snapshot: {n(s['spirits'])} bottlings, {n(s['producers'])} producers and brands, and {n(s['price_distillery_months'])} monthly distillery auction benchmarks reaching back to {s['price_first'][:4]}, every record traced to an open public source. Refreshed monthly. Every figure is free to cite, quote and embed with a link to this page.</p>
      <ul class="tiles">{tiles}</ul>
      <nav class="toc" aria-label="Contents"><strong>On this page</strong><ol>{toc}</ol></nav>
    </section>

{"".join(sections)}

    <section class="stat" id="method">
      <h2 class="heading">Method, reuse and citation</h2>
      <ul class="method">
        <li><strong>Source.</strong> The full WhiskyDB snapshot of {snap}, built entirely from open sources: the US TTB COLA label registry, UK Companies House, the EU eAmbrosia GI register, Open Food Facts, Wikipedia and WhiskyHunter's open auction statistics. Every row carries a provenance ledger entry; see <a href="/SOURCES.md">Sources &amp; licenses</a>.</li>
        <li><strong>Coverage is uneven by design.</strong> Open registries do not all publish every attribute. Every figure above names its denominator, so a percentage is always a share of the records that state that attribute, never of the whole catalogue. Blank fields are never guessed, and the documented 40% ABV fallback is excluded from every ABV figure.</li>{gi_li}
        <li><strong>The auction index is a market index.</strong> Each value is a distillery-level mean winning bid for one month, never the price of a specific bottle. Yearly figures average the distilleries equally so a distillery with many linked bottlings does not dominate.</li>
        <li><strong>Refresh.</strong> The catalogue is refreshed monthly; this page and its charts are regenerated after each refresh, so figures move. Cite the snapshot date.</li>
        <li><strong>Reuse.</strong> The figures and charts on this page are published under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>: use them in articles, slides and posts with a link to <span translate="no">{PAGE_URL}</span>. The machine-readable version is <a href="/stats/data.json">data.json</a>. Figures derived from WhiskyHunter, Companies House and Wikipedia retain those sources' attribution terms. The underlying row-level dataset is a separate <a href="/#pricing-section">commercial product</a>.</li>
        <li><strong>Suggested citation.</strong> <span translate="no">WhiskyDB ({snap[:4]}). <em>Whisky in numbers</em>, snapshot {snap}. DataEngineered. {PAGE_URL}</span></li>
        <li><strong>Questions or corrections:</strong> <a href="/#contact-section">contact form</a> or whiskydb@dataengineered.io.</li>
      </ul>
    </section>

    <div class="cta">
      <h3 class="heading" style="font-size: 1.4rem; color: var(--gold);">Need the row-level data behind these numbers?</h3>
      <p style="color: var(--text-muted); margin-top: 8px;">Every bottling, producer and monthly auction benchmark with its provenance, as SQLite and CSV.</p>
      <a href="/#pricing-section" class="btn-link" style="margin-top: 16px; background: rgba(212,175,55,0.1);">Get the full dataset ($49) →</a>
    </div>
  </main>

  <footer>
    <div class="container">
      <p>WhiskyDB — Canonical Global Fine Spirits Catalog · <a href="/#pricing-section" style="color:var(--gold); text-decoration:none;">License Enterprise Dataset ($49/mo)</a></p>
      <div class="catalog-line" style="text-align:center; margin-top:14px; font-size:0.85rem; opacity:0.85;"><a href="https://dataengineered.io/">Part of the DataEngineered catalog →</a> · <a href="https://dataengineered.io/about">About</a> · <a href="https://dataengineered.io/terms">Terms</a> · <a href="https://dataengineered.io/privacy">Privacy</a> · <a href="https://dataengineered.io/refund-policy">Refund policy</a></div>
    </div>
  </footer>
  <script>
    document.querySelectorAll('button.copy').forEach(function (b) {{
      b.addEventListener('click', function () {{
        var el = document.getElementById(b.getAttribute('data-target'));
        if (!el) return;
        var done = function () {{ var old = b.textContent; b.textContent = 'Copied'; setTimeout(function () {{ b.textContent = old; }}, 1500); }};
        var select = function () {{ var r = document.createRange(); r.selectNodeContents(el); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }};
        if (navigator.clipboard && navigator.clipboard.writeText) {{
          navigator.clipboard.writeText(el.textContent).then(done, select);
        }} else {{ select(); }}
      }});
    }});
  </script>
</body>
</html>
"""


def build_data_json(s):
    return {
        "dataset": BRAND, "page": PAGE_URL, "generated": dt.date.today().isoformat(), "snapshot": s["snapshot_date"],
        "license": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) - attribute with a link to the page; "
                   "WhiskyHunter, Companies House and Wikipedia-derived figures retain those sources' attribution terms",
        # gi_appellations only when the snapshot flags them (older snapshots: the key is absent, as before)
        "totals": {k: s[k] for k in ("spirits", "producers", "gi_appellations", "producers_with_country", "producer_countries",
                                     "producer_countries_off_only", "price_rows", "price_first", "price_last",
                                     "price_distilleries", "price_distillery_months", "volume_stated")
                   if k != "gi_appellations" or s[k] is not None},
        # only under the 2026.11 rule (stated origin or headquarters), so older snapshots' data.json is unchanged
        **({} if s["off_sold_in_countries"] else {"producer_country_rule": "stated"}),
        "auction_index_gbp": {
            "method": "mean monthly winning bid per distillery (WhiskyHunter), yearly mean per distillery, then mean across distilleries",
            "distilleries": s["lfl_names"], "last_year_months": s["last_year_months"],
            "years": [dict(year=y, mean_gbp=v, distilleries=c) for y, v, c in s["index_years"]],
            "peak_year": s["index_peak"], "peak_month": s["index_peak_month"], "multiple_first_to_last": s["index_multiple"],
            "change_from_peak_pct": s["index_from_peak_pct"],
            "per_distillery": [dict(distillery=nm, first_year_gbp=c, decade_ago_gbp=a, latest_gbp=b, decade_change_pct=ch)
                               for nm, c, a, b, ch in s["per_distillery"]],
            "decade": [s["decade_lo"], s["decade_hi"]]},
        "spirit_types": [dict(type=k, bottlings=v, share_pct=p) for k, v, p in s["types"]],
        "abv": {"denominator": s["abv_n"], "excluded_default_abv": DEFAULT_ABV,
                # which bottlings the ABV figures count: the source-stated ones (abv_source), or, in a
                # snapshot without that column, those whose ABV is not 40.0 (a lower bound of the stated ones)
                "rule": "abv_source in (label, producer, off, name)" if s["abv_by_source"] else "abv_percentage <> 40.0",
                "mean": s["abv_mean"], "median": s["abv_median"],
                "max": s["abv_max"], "share_50_plus_pct": s["abv_cask_strength_pct"],
                "buckets": [dict(bucket=k, bottlings=v, share_pct=p) for k, v, p in s["abv_buckets"]],
                "by_type": [dict(type=k, n=c, mean=m, max=mx) for k, c, m, mx in s["abv_by_type"]]},
        "producers_by_country": [dict(country=k, producers=v, share_pct=p) for k, v, p in s["producers_by_country"]],
        "founded": {"denominator": s["founded_n"], "sources": s["founded_src"], "pre_1900": s["founded_pre1900"],
                    "from_2010": s["founded_2010_plus"], "from_2010_pct": s["founded_2010_plus_pct"],
                    "by_decade": [dict(decade=k, producers=v, share_pct=p) for k, v, p in s["founded_by_decade"]]},
        "uk_company_status": [dict(jurisdiction=c, registrations=t, active=a, dissolved=d, dissolved_pct=p) for c, t, a, d, p in s["uk_status"]],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default=os.environ.get("WHISKYDB_SQLITE", str(DEFAULT_DB)))
    args = ap.parse_args()
    db = Path(args.db)
    if not db.is_file():
        raise SystemExit(f"SQLite snapshot not found: {db}")
    s = compute(db)
    charts = {}
    page = section_links.insert(build_page(s, charts))  # the shared snippet, right after the header
    OUT_DIR.mkdir(exist_ok=True)
    CHART_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8", newline="\n")
    for slug, svg in charts.items():
        (CHART_DIR / f"{slug}.svg").write_text(chart_ids(svg, slug) + "\n", encoding="utf-8", newline="\n")
    (OUT_DIR / "data.json").write_text(json.dumps(build_data_json(s), ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8", newline="\n")
    print(f"stats/index.html + {len(charts)} charts + data.json  (snapshot {s['snapshot_date']}, "
          f"{s['spirits']:,} bottlings, index {s['index_first']['year']}-{s['index_last']['year']} over {s['lfl_n']} distilleries)")


if __name__ == "__main__":
    main()
