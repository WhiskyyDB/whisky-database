#!/usr/bin/env python3
"""
WhiskyDB shopfront claims check (`WhiskyDB-public`).

The homepage, README.md, llms.txt and DATA_DICTIONARY.md state dataset figures by hand
(bottlings, distilleries, auction benchmarks, snapshot edition, auction date range, field
coverage). This script asserts that every one of them equals `stats/data.json`, which
`scripts/generate_stats.py` computes from the full snapshot with SQL (count(*), never
line counts: the paid CSVs hold quoted fields with embedded line breaks, so `wc -l`
overcounts -- that is how 2,301 / 3,764 got onto the site for the 2,294 / 3,762 build of
2026-09-02).

    python scripts/check_claims.py          # exit 1 and list every mismatch
    python scripts/check_claims.py --fix    # rewrite the English sources to data.json

Stdlib only, no network. Release order after a data refresh:
    generate_stats.py -> check_claims.py --fix -> generate_seo_pages.py (sitemap lastmods)
    -> i18n_common.py build + check -> check_claims.py

What is compared (English sources only; the /es/ /de/ /fr/ /pt-br/ pages are generated from
index.html, so the plain check also confirms that their hero figures were rebuilt):
  spirits, producers, price_rows, price_distilleries   totals in data.json
  auction months / date range     price_first..price_last (whole months, both ends included)
  snapshot edition                YYYY.MM of data.json "snapshot" (the refresh date)
  coverage %                      floored, so a claim never rounds up: explicit ABV = abv.denominator
                                  / spirits, country = producers_with_country / producers, founded
                                  year = founded.denominator / producers; ABV max = abv.max
  countries floor                 README "Countries represented N+": producer_countries minus
                                  producer_countries_off_only, floored to a multiple of 10
  GI appellations floor           README "Protected GI appellations (EU/UK) N+": gi_appellations
                                  floored to a multiple of 10, once data.json reports it (below)
Not in data.json, so still checked by hand: the "linked bottlings" count in README.md, the
barcode and age-statement coverage, and the "+" floors in DATA_DICTIONARY.md.

Producers, not appellations (from the 2026.10 edition): the snapshot flags the 273 EU
eAmbrosia GI appellation rows ("Official GI Producer - Cognac") with
distilleries.is_gi_appellation = 1, and generate_stats.py then leaves them out of every
producer figure: `producers`, `producers_with_country`, the country counts and the founded
denominator. So the distilleries claims, the country and founded-year coverage and the
countries floor are all measured on producers only, and data.json gains
`totals.gi_appellations`. A data.json without that key (2026.09 and older) has the GI floor
rule's sentence count checked but not its value. Measured on the flagged database of
2026-09-29 (the 2026.09 edition minus 15 non-producer rows): 2,565 producers + 273
appellations, country coverage 2,556 / 2,565 -> 99%, founded year 696 / 2,565 -> 27%, 31
countries of which 12 only on Open Food Facts rows -> 19 -> "10+" (the 16 countries named
only by appellations drop out).

Countries, not country labels: data.json `producer_countries` splits multi-country labels
("France, Italy", appellations shared across borders), merges synonyms ("Russia" / "Russian
Federation") and counts the UK's six labels (United Kingdom, England, Wales, "England & Wales",
Scotland, Northern Ireland) once; see generate_stats.countries_of. The README floor leaves out
the countries named only by Open Food Facts rows (`producer_countries_off_only`), whose country
is the first one a product is sold in, not where it is made (Chivas -> Bolivia). In the
2026.09 edition published on 2026-09-28 (the cleaned table plus that day's refresh): 47
countries, 6 of them only on Open Food Facts rows, so 41 -> "40+". (Before the cleanup,
as in the 2026-09-02 build, the distilleries table also held 748 Wikidata rows that were
reservoirs and lakes and 375 Wikipedia navigation links: 106 labels and 88 countries, 41
of them only through the reservoir rows -- the Isle of Man is one of the 41, since
countries_of counts it apart from the UK.)

Every rule must match its exact number of occurrences: if a sentence is reworded so that
a rule no longer finds it, the check fails instead of silently skipping the claim --
update the sentence or RULES below.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

NUM = r"\d{1,3}(?:,\d{3})+|\d+"          # 2,294 or 59
NUM_URL = r"\d{1,3}(?:%2C\d{3})+|\d+"    # shields.io badge form: 3%2C762
EDITION = r"\d{4}\.\d{2}"
RANGE_LONG = r"[A-Z][a-z]+ \d{4} → (?:[A-Z][a-z]+ \d{4}|today)"            # November 2005 → September 2024
RANGE_SHORT = r"(?:[A-Z][a-z]{2} )?\d{4} → (?:[A-Z][a-z]{2} \d{4}|\d{4}|today)"  # Nov 2005 → Sep 2024

# Hero figures on the homepage, in page order; checked on the generated locale copies too.
HERO_KEYS = ("spirits", "producers", "price_rows")
# Thousands separator per locale, as scripts/i18n_common.py LOCALES formats grouped numbers.
LOCALE_GROUP = {"es": ".", "de": ".", "pt-br": ".", "fr": "\u202f", "it": ".", "nl": ".", "id": ".", "tr": "."}


def rule(file, label, pattern, key, count=1, optional=False):
    """`pattern` holds one `(?P<v>...)` group: the claimed value, compared with expected[key].
    optional: the key may be missing from an older data.json; the occurrence count is still
    checked, the value only when the key is there."""
    return dict(file=file, label=label, rx=re.compile(pattern), key=key, count=count, optional=optional)


RULES = [
    # --- index.html: <title>, meta/og descriptions, hero stat strip, FAQ (JSON-LD + HTML) ---
    rule("index.html", "title + og:title bottlings", rf"Database: (?P<v>{NUM}) Bottlings", "spirits", 2),
    rule("index.html", "meta description bottlings", rf"Download (?P<v>{NUM}) whisky and whiskey bottlings", "spirits"),
    rule("index.html", "og:description bottlings", rf'content="(?P<v>{NUM}) whisky and whiskey bottlings', "spirits"),
    rule("index.html", "meta + og description distilleries", rf"bottlings from (?P<v>{NUM}) distilleries", "producers", 2),
    rule("index.html", "meta + og description benchmarks", rf"(?P<v>{NUM}) (?:monthly )?auction benchmarks", "price_rows", 2),
    rule("index.html", "FAQ benchmarks (JSON-LD + HTML)", rf"The (?P<v>{NUM}) monthly distillery auction-price benchmarks", "price_rows", 2),
    rule("index.html", "hero Spirits & Bottlings",
         rf'stat-num">(?P<v>{NUM})</span>\s*<span class="stat-label">Spirits &amp; Bottlings<', "spirits"),
    rule("index.html", "hero Global Distilleries",
         rf'stat-num">(?P<v>{NUM})</span>\s*<span class="stat-label">Global Distilleries<', "producers"),
    rule("index.html", "hero Auction-Price Benchmarks",
         rf'stat-num">(?P<v>{NUM})</span>\s*<span class="stat-label">Auction-Price Benchmarks<', "price_rows"),

    # --- README.md: headline, badges, What's inside, field coverage, auction section, pricing ---
    rule("README.md", "headline spirits", rf"\*\*(?P<v>{NUM}) whiskies & fine spirits · ", "spirits"),
    rule("README.md", "headline distilleries", rf" · (?P<v>{NUM}) distilleries & producers · ", "producers"),
    rule("README.md", "headline benchmarks", rf" · (?P<v>{NUM}) monthly auction-price benchmarks \(", "price_rows"),
    rule("README.md", "headline auction range", rf"monthly auction-price benchmarks \((?P<v>{RANGE_SHORT})\)", "range_short"),
    rule("README.md", "Distilleries badge text", rf"\[!\[Distilleries: (?P<v>{NUM})\]", "producers"),
    rule("README.md", "Distilleries badge URL", rf"/badge/Distilleries-(?P<v>{NUM_URL})-", "producers_url"),
    rule("README.md", "Auction history badge text", r"\[!\[Price history: (?P<v>\d{4}→\w*)\]", "years"),
    rule("README.md", "Auction history badge URL", r"/badge/Auction%20history-(?P<v>\d{4}%E2%86%92\w+)-", "years_url"),
    rule("README.md", "Snapshot badge text", rf"\[!\[Snapshot: (?P<v>{EDITION})\]", "edition"),
    rule("README.md", "Snapshot badge URL", rf"/badge/Snapshot-(?P<v>{EDITION})-", "edition"),
    rule("README.md", "table Spirits & bottlings", rf"\| Spirits & bottlings \| \*\*(?P<v>{NUM})\*\* \|", "spirits"),
    rule("README.md", "table Distilleries", rf"\| Distilleries, brands & producers \| \*\*(?P<v>{NUM})\*\* \|", "producers"),
    rule("README.md", "table benchmarks", rf"\| Monthly auction-price benchmarks \| \*\*(?P<v>{NUM})\*\* \|", "price_rows"),
    rule("README.md", "table Countries floor", r"\| Countries represented \| \*\*(?P<v>\d+)\+\*\* \|", "countries_floor"),
    rule("README.md", "table GI appellations floor", r"\| Protected GI appellations \(EU/UK\) \| \*\*(?P<v>\d+)\+\*\* \|",
         "gi_floor", optional=True),
    rule("README.md", "coverage Distillery country", r"\| Distillery country \| (?P<v>\d+)% \|", "pct_country"),
    rule("README.md", "coverage Distillery founded year", r"\| Distillery founded year \| (?P<v>\d+)% \|", "pct_founded"),
    rule("README.md", "coverage Explicit label ABV", r"\| Explicit label ABV \| (?P<v>\d+)%\\?\*", "pct_abv"),
    rule("README.md", "ABV footnote share", r"\\\* (?P<v>\d+)% of spirits carry an explicitly sourced ABV", "pct_abv"),
    rule("README.md", "ABV footnote maximum", r"cask-strength values up to (?P<v>\d+(?:\.\d+)?)%", "abv_max"),
    rule("README.md", "auction benchmarks bullet", rf"- \*\*(?P<v>{NUM})\*\* distillery-level monthly auction statistics", "price_rows"),
    rule("README.md", "auction months", r"\*\*(?P<v>\d+) consecutive months\*\*", "months"),
    rule("README.md", "auction range", rf"consecutive months\*\* — (?P<v>{RANGE_LONG}) — ", "range_long"),
    rule("README.md", "auction distilleries", rf"across \*\*(?P<v>{NUM}) whisky distilleries\*\*", "price_distilleries"),
    rule("README.md", "pricing benchmarks", rf"SQLite \+ CSV · (?P<v>{NUM}) auction-price benchmarks", "price_rows"),

    # --- llms.txt ---
    rule("llms.txt", "spirits and bottlings", rf"(?P<v>{NUM}) spirits and bottlings", "spirits", 2),
    rule("llms.txt", "global distilleries", rf"(?P<v>{NUM}) global distilleries", "producers", 2),
    rule("llms.txt", "coverage benchmarks", rf"Includes (?P<v>{NUM}) monthly distillery auction-price benchmarks", "price_rows"),
    rule("llms.txt", "coverage auction range", rf"auction-price benchmarks spanning (?P<v>{RANGE_LONG})\.", "range_long"),
    rule("llms.txt", "Standard Catalog benchmarks", rf"SQLite \+ CSV, (?P<v>{NUM}) monthly auction-price benchmarks", "price_rows"),
    rule("llms.txt", "Snapshot", rf"Snapshot: (?P<v>{EDITION})\.", "edition"),

    # --- DATA_DICTIONARY.md ---
    rule("DATA_DICTIONARY.md", "snapshot", rf"\(snapshot `(?P<v>{EDITION})`\)", "edition"),
    rule("DATA_DICTIONARY.md", "abv explicit share", r"Explicitly sourced for (?P<v>\d+)% of records", "pct_abv"),
    rule("DATA_DICTIONARY.md", "country coverage", r"\| (?P<v>\d+)% specific \|", "pct_country"),
    rule("DATA_DICTIONARY.md", "price_benchmarks range", rf"auction indices, (?P<v>{RANGE_SHORT}), ", "range_short"),
]


MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")  # English, whatever the OS locale (strftime %B is locale-dependent)


def month(d, short=False):
    name = MONTHS[d.month - 1]
    return f"{name[:3] if short else name} {d.year}"


def grouped(n, sep=","):
    return f"{n:,}".replace(",", sep)


def floor_pct(part, whole):
    return str(part * 100 // whole)


def expected_values(data):
    t = data["totals"]
    first = dt.date.fromisoformat(t["price_first"])
    last = dt.date.fromisoformat(t["price_last"])
    snap = dt.date.fromisoformat(data["snapshot"])
    abv_max = float(data["abv"]["max"])
    exp = {
        "spirits": grouped(t["spirits"]),
        "producers": grouped(t["producers"]),
        "producers_url": grouped(t["producers"], "%2C"),
        "price_rows": grouped(t["price_rows"]),
        "price_distilleries": grouped(t["price_distilleries"]),
        "months": str((last.year - first.year) * 12 + last.month - first.month + 1),
        "range_long": f"{month(first)} → {month(last)}",
        "range_short": f"{month(first, True)} → {month(last, True)}",
        "years": f"{first.year}→{last.year}",
        "years_url": f"{first.year}%E2%86%92{last.year}",
        "edition": f"{snap.year}.{snap.month:02d}",
        "pct_abv": floor_pct(data["abv"]["denominator"], t["spirits"]),
        "pct_country": floor_pct(t["producers_with_country"], t["producers"]),
        "pct_founded": floor_pct(data["founded"]["denominator"], t["producers"]),
        "countries_floor": str((t["producer_countries"] - t["producer_countries_off_only"]) // 10 * 10),
        "abv_max": f"{abv_max:g}",
    }
    if "gi_appellations" in t:  # data.json from a snapshot that flags the EU GI appellations
        exp["gi_floor"] = str(t["gi_appellations"] // 10 * 10)
    return exp


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:  # newline="" keeps CRLF checkouts byte-stable
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def check_sources(root, exp, fix):
    """Return (problems, fixed) for the English sources; with fix, rewrite wrong values."""
    problems, fixed = [], []
    texts = {}
    for r in RULES:
        path = root / r["file"]
        if r["file"] not in texts:
            texts[r["file"]] = read(path) if path.exists() else None
        text = texts[r["file"]]
        if text is None:
            problems.append(f"{r['file']}: file missing")
            continue
        matches = list(r["rx"].finditer(text))
        if len(matches) != r["count"]:
            problems.append(f"{r['file']}: {r['label']}: expected {r['count']} occurrence(s), found {len(matches)} "
                            f"(sentence reworded? update it or RULES in scripts/check_claims.py)")
            continue
        if r["optional"] and r["key"] not in exp:
            continue
        want = exp[r["key"]]
        wrong = [m for m in matches if m.group("v") != want]
        if not wrong:
            continue
        if fix:
            for m in reversed(wrong):
                text = text[:m.start("v")] + want + text[m.end("v"):]
            texts[r["file"]] = text
            fixed.append(f"{r['file']}: {r['label']}: {wrong[0].group('v')} -> {want}")
        else:
            for m in wrong:
                line = text.count("\n", 0, m.start("v")) + 1
                problems.append(f"{r['file']}:{line}: {r['label']}: states {m.group('v')}, data.json says {want}")
    if fix:
        for name, text in texts.items():
            if text is not None and text != read(root / name):
                write(root / name, text)
    return problems, fixed


def check_locales(root, data):
    """The generated /<lang>/index.html hero strip must carry the same figures (locale-grouped)."""
    problems = []
    cfg_path = root / "i18n.config.json"
    if not cfg_path.exists():
        return problems
    locales = json.loads(read(cfg_path)).get("locales", [])
    for loc in locales:
        page = root / loc / "index.html"
        if not page.exists():
            continue
        sep = LOCALE_GROUP.get(loc)
        if sep is None:
            problems.append(f"{loc}/index.html: no thousands separator known for '{loc}' (add it to LOCALE_GROUP)")
            continue
        want = [grouped(data["totals"][k], sep) for k in HERO_KEYS]
        got = re.findall(r'class="stat-num">([^<]*)<', read(page))[:len(HERO_KEYS)]
        if got != want:
            problems.append(f"{loc}/index.html: hero states {' / '.join(got)}, expected {' / '.join(want)} "
                            f"(run: python scripts/i18n_common.py build)")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    ap.add_argument("--fix", action="store_true", help="rewrite the English sources to the data.json figures")
    ap.add_argument("--root", type=Path, default=BASE_DIR, help="site repo root (default: this repo)")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    if hasattr(sys.stdout, "reconfigure"):  # a cp1252 Windows console cannot print "→"; escape it, never crash
        sys.stdout.reconfigure(errors="backslashreplace")

    data = json.loads(read(root / "stats" / "data.json"))
    exp = expected_values(data)
    problems, fixed = check_sources(root, exp, args.fix)
    for line in fixed:
        print(f"fixed  {line}")
    if args.fix:
        if fixed:
            print("now run: python scripts/generate_seo_pages.py, then python scripts/i18n_common.py build "
                  "&& python scripts/i18n_common.py check, then python scripts/check_claims.py")
    else:
        problems += check_locales(root, data)

    print(f"claims vs stats/data.json (snapshot {data['snapshot']}, edition {exp['edition']}): "
          f"{exp['spirits']} spirits, {exp['producers']} distilleries, {exp['price_rows']} price rows, "
          f"auctions {exp['range_short']}")
    if problems:
        for p in problems:
            print(f"ERROR  {p}")
        print(f"check_claims: {len(problems)} problem(s)" + ("" if args.fix else "; `--fix` rewrites wrong values"))
        return 1
    print(f"check_claims: {len(RULES)} rules" + ("" if args.fix else " + locale hero strips") + ", 0 problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
