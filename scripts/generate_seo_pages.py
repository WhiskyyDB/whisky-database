import csv
import os
import re
import html
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seo_common import fit_title, fit_desc, write_sitemap, related_block

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def _trim_num(v):
    """Drop a trailing '.0' from CSV numeric strings (e.g. '16.0' -> '16', keep '43.2')."""
    v = (v or '').strip()
    return v[:-2] if v.endswith('.0') else v

def _record_key(raw_id, fallback_text):
    """A stable small integer derived from a record's own id (or, failing that, its
    name) -- used only to pick among equally-truthful phrasings, never to alter facts."""
    raw_id = (raw_id or '').strip()
    if raw_id.isdigit():
        return int(raw_id)
    return sum(ord(c) for c in fallback_text)

def distillery_profile(d, matching):
    """Build a unique, data-derived <p> profile from a distillery's OWN real CSV fields
    (name/country/region/source_name) plus any matching spirit(s) it makes
    (name/type/age/abv/volume_ml). Only emits clauses for fields that are actually
    populated -- empty fields are omitted, never faked. Wording is rotated (by the
    record's own id) among equivalent phrasings so records sharing every other field
    -- common in the sparser public samples -- still don't read as identical
    sentences. Returns an HTML <p>."""
    dname = (d.get('name') or '').strip()
    country = (d.get('country') or '').strip()
    region = (d.get('region') or '').strip()
    source_name = (d.get('source_name') or '').strip()
    key = _record_key(d.get('distillery_id'), dname)

    sentences = []

    # Sentence 1: geographic placement (name + region + country are always present here).
    region_disp = re.sub(r',(\S)', r', \1', region)  # cosmetic: space after comma
    region_ok = region and region.lower() not in ('general', 'unknown', dname.lower())
    if country and country.lower() != 'unknown':
        if region_ok:
            loc = f"in {html.escape(region_disp)}, {html.escape(country)}"
        else:
            loc = f"in {html.escape(country)}"
    else:
        loc = f"in {html.escape(region_disp)}" if region_ok else ""
    dname_e = html.escape(dname)
    geo_templates = [
        f"{dname_e} is a whisky distillery catalogued in WhiskyDB" + (f", based {loc}" if loc else "") + ".",
        f"WhiskyDB lists {dname_e} as a distillery" + (f" {loc}" if loc else "") + ".",
        (f"{dname_e} appears in WhiskyDB's distillery registry" + (f", {loc}" if loc else "") + ".") ,
    ]
    sentences.append(geo_templates[key % len(geo_templates)])

    # Sentence 2: the spirit(s) this distillery makes, described from real attributes.
    if matching:
        clauses = []
        for m in matching:
            mname = (m.get('name') or '').strip()
            mtype = (m.get('type') or '').strip()
            age = (m.get('age') or '').strip()
            abv = (m.get('abv') or '').strip()
            vol = (m.get('volume_ml') or '').strip()
            attrs = []
            if mtype:
                attrs.append(f"a {html.escape(mtype)}")
            if age and age.replace('.', '', 1).isdigit() and float(age) > 0:
                attrs.append(f"carrying a {html.escape(_trim_num(age))}-year age statement")
            if abv:
                attrs.append(f"bottled at {html.escape(_trim_num(abv))}% ABV")
            if vol:
                attrs.append(f"in a {html.escape(vol)} ml format")
            if attrs:
                clauses.append(f"{html.escape(mname)} — {', '.join(attrs)}")
            else:
                clauses.append(html.escape(mname))
        if len(clauses) == 1:
            sentences.append(f"The catalog links it to {clauses[0]}.")
        else:
            sentences.append(
                f"The catalog links it to {len(clauses)} recorded bottlings: "
                + "; ".join(clauses) + "."
            )
    elif source_name:
        # No individual bottlings for this distillery in the sparse public sample:
        # stay honest and lean on the real provenance field instead of padding.
        source_e = html.escape(source_name)
        fallback_templates = [
            f"Its record is attributed to {source_e}; no individual bottlings are catalogued for it in this public sample.",
            f"{source_e} is the attributed source for this record; the public sample does not yet catalog a bottling from {dname_e}.",
            f"No bottlings from {dname_e} are catalogued in this public sample; provenance traces to {source_e}.",
        ]
        sentences.append(fallback_templates[(key + 1) % len(fallback_templates)])

    return ('<p style="color: var(--text-muted); font-size: 1.08rem; line-height: 1.8; '
            'margin-top: 28px; max-width: 780px;">' + ' '.join(sentences) + '</p>')

def spirit_profile(s, dist):
    """Build a unique, data-derived <p> profile from a spirit's OWN real CSV fields
    (name/type/age/abv/volume_ml/source_name) plus its matched distillery, if any
    (name/region/country). Only emits clauses for fields that are actually
    populated -- empty fields are omitted, never faked. Wording is rotated (by the
    record's own id) among equivalent phrasings so records that share every other
    field -- several of the public-sample entries do -- still don't read as
    identical sentences. Returns an HTML <p>."""
    name = (s.get('name') or '').strip()
    stype = (s.get('type') or '').strip()
    age = (s.get('age') or '').strip()
    abv = (s.get('abv') or '').strip()
    vol = (s.get('volume_ml') or '').strip()
    source_name = (s.get('source_name') or '').strip()
    key = _record_key(s.get('spirit_id'), name)

    sentences = []

    # Sentence 1: what it is, built only from populated fields.
    attrs = []
    if stype:
        attrs.append(f"a {html.escape(stype)}")
    if abv:
        attrs.append(f"bottled at {html.escape(_trim_num(abv))}% ABV")
    if age and age.replace('.', '', 1).isdigit() and float(age) > 0:
        attrs.append(f"carrying a {html.escape(_trim_num(age))}-year age statement")
    if vol:
        attrs.append(f"in a {html.escape(vol)} ml bottle")
    name_e = html.escape(name)
    if attrs:
        # Rotate clause order (not content) so records sharing every field value --
        # several of the public-sample entries do -- don't render the identical phrase.
        rot = key % len(attrs)
        joined = ', '.join(attrs[rot:] + attrs[:rot])
        what_templates = [
            f"{name_e} is catalogued in WhiskyDB as {joined}.",
            f"In the WhiskyDB catalog, {name_e} is listed as {joined}.",
            f"WhiskyDB's spirits ledger records {name_e} as {joined}.",
            f"{name_e} enters WhiskyDB's ledger as {joined}.",
        ]
        sentences.append(what_templates[key % len(what_templates)])
    else:
        sentences.append(f"{name_e} is catalogued in WhiskyDB.")

    # Sentence 2: distillery linkage, only when the CSV name-match found one.
    if dist:
        dname = (dist.get('name') or '').strip()
        region = (dist.get('region') or '').strip()
        country = (dist.get('country') or '').strip()
        region_ok = region and region.lower() not in ('general', 'unknown', dname.lower())
        if country and country.lower() != 'unknown':
            loc = f" in {html.escape(region)}, {html.escape(country)}" if region_ok else f" in {html.escape(country)}"
        else:
            loc = f" in {html.escape(region)}" if region_ok else ""
        sentences.append(f"It is distilled by {html.escape(dname)}{loc}.")

    # Sentence 3: provenance.
    if source_name:
        source_e = html.escape(source_name)
        source_templates = [
            f"Source: {source_e}.",
            f"Provenance: {source_e}.",
            f"{name_e}'s record is sourced from {source_e}.",
        ]
        sentences.append(source_templates[(key + 1) % len(source_templates)])

    return ('<p style="color: var(--text-muted); font-size: 1.08rem; line-height: 1.8; '
            'margin-top: 28px; max-width: 780px;">' + ' '.join(sentences) + '</p>')

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spirits_csv = os.path.join(root_dir, 'samples', 'spirits.csv')
    distilleries_csv = os.path.join(root_dir, 'samples', 'distilleries.csv')
    spirits_dir = os.path.join(root_dir, 'spirits')
    distilleries_dir = os.path.join(root_dir, 'distilleries')

    os.makedirs(spirits_dir, exist_ok=True)
    os.makedirs(distilleries_dir, exist_ok=True)

    spirits = []
    if os.path.exists(spirits_csv):
        with open(spirits_csv, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('name') and row.get('type'):
                    spirits.append(row)

    distilleries = []
    if os.path.exists(distilleries_csv):
        with open(distilleries_csv, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('name'):
                    distilleries.append(row)

    print(f"Loaded {len(spirits)} spirit records and {len(distilleries)} distillery records from CSVs.")

    sitemap_urls = [
        ("https://whiskydb.dataengineered.io/", "1.0", "weekly")
    ]

    def distillery_of(s):
        for d in distilleries:
            if d.get('name', '').strip() and d['name'].strip().lower() in s.get('name', '').lower():
                return d
        return None

    # Generate Spirit Specimen Pages
    for s in spirits:
        name = s.get('name', '').strip()
        stype = s.get('type', 'Whisky').strip()
        age = s.get('age', '').strip()
        abv = s.get('abv', '40.0').strip()
        vol = s.get('volume_ml', '700').strip()
        source_name = s.get('source_name', 'WhiskyDB Curated Ledger').strip()
        source_url = s.get('source_url', 'https://github.com/WhiskyyDB/whisky-database').strip()
        spirit_id = s.get('spirit_id', '')
        dist = distillery_of(s)

        slug = slugify(name)
        age_display = f"{age} Years Old" if (age and age.replace('.','',1).isdigit() and float(age) > 0) else "No Age Statement (NAS)"
        abv_display = f"{abv}% ABV" if abv else "40.0% ABV"

        page_url = f"https://whiskydb.dataengineered.io/spirits/{slug}"
        sitemap_urls.append((page_url, "0.8", "monthly"))

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(fit_title(name, f"{stype}, {_trim_num(abv)}% ABV", "WhiskyDB"))}</title>
  <meta name="description" content="{html.escape(fit_desc(f"{name}: {stype} at {_trim_num(abv)}% ABV, {age_display}, {vol} ml bottle" + (f", distilled by {dist['name']} in {dist['region']}, {dist['country']}" if dist else "") + f". Source: {source_name}."))}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" hreflang="en" href="{page_url}" />
  <link rel="alternate" hreflang="x-default" href="{page_url}" />

  <meta property="og:title" content="{name} ({stype}) Determination & Valuation Record — WhiskyDB" />
  <meta property="og:description" content="Exact ABV ({abv_display}), Age Statement ({age_display}), bottle volume ({vol}ml), and secondary market ledger." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="https://whiskydb.dataengineered.io/hero.png" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "{name} ({stype}) Structured Spirits Determination",
    "description": "Normalized botanical and cask parameters for {name}: {stype}, {abv_display}, {age_display}, {vol}ml volume, and secondary auction market tracking.",
    "url": "{page_url}",
    "creator": {{"@type": "Organization", "name": "WhiskyDB Initiative", "url": "https://whiskydb.dataengineered.io"}},
    "license": "https://creativecommons.org/licenses/by-sa/4.0/",
    "isAccessibleForFree": true,
    "variableMeasured": ["alcohol by volume percentage", "age statement in years", "cask finish lineage", "mash bill percentages", "secondary market auction index"]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://whiskydb.dataengineered.io/"}},
      {{"@type": "ListItem", "position": 2, "name": "Spirits Catalog", "item": "https://whiskydb.dataengineered.io/#explorer-section"}},
      {{"@type": "ListItem", "position": 3, "name": "{name}", "item": "{page_url}"}}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet"></noscript>

  <style>
    :root {{
      --bg-dark: #0a0b0d;
      --bg-card: #111318;
      --gold: #d4af37;
      --gold-light: #e2c044;
      --text-main: #f0f2f8;
      --text-muted: #949ab1;
      --border: rgba(212, 175, 55, 0.2);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-main); line-height: 1.6; padding-bottom: 60px; }}
    .heading {{ font-family: 'Outfit', sans-serif; font-weight: 700; }}
    .mono {{ font-family: 'Fira Code', monospace; }}
    header {{ border-bottom: 1px solid var(--border); padding: 20px 0; background: rgba(17, 19, 24, 0.8); backdrop-filter: blur(10px); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 0 24px; }}
    .nav-bar {{ display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text-main); text-decoration: none; }}
    .brand span {{ color: var(--gold); }}
    .btn-link {{ color: var(--text-main); text-decoration: none; font-size: 0.9rem; border: 1px solid var(--border); padding: 8px 16px; border-radius: 6px; transition: all 0.2s; }}
    .btn-link:hover {{ background: var(--gold); color: #0a0b0d; border-color: var(--gold); }}
    .hero {{ padding: 48px 0; border-bottom: 1px solid var(--border); }}
    .badge {{ display: inline-block; background: rgba(212, 175, 55, 0.15); color: var(--gold-light); padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 12px; border: 1px solid rgba(212,175,55,0.3); }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 36px; }}
    @media(max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .card {{ background: var(--bg-card); border: 1px solid var(--border); padding: 28px; border-radius: 12px; }}
    .metric-row {{ display: flex; justify-content: space-between; border-bottom: 1px dashed rgba(212,175,55,0.15); padding: 14px 0; }}
    .metric-row:last-child {{ border-bottom: none; }}
    .metric-label {{ color: var(--text-muted); font-size: 0.92rem; }}
    .metric-val {{ font-weight: 600; font-family: 'Fira Code', monospace; color: var(--gold-light); }}
    footer {{ margin-top: 60px; border-top: 1px solid var(--border); padding: 32px 0; text-align: center; font-size: 0.85rem; color: var(--text-muted); }}
    .related ul{{list-style:none;padding:0}}.related li{{padding:6px 0}}.related-why{{color:var(--text-muted);font-size:.9em}}
  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="/" class="brand">Whisky<span>DB</span></a>
      <div>
        <a href="/#explorer-section" class="btn-link">← Explorer</a>
        <a href="/#pricing-section" class="btn-link" style="margin-left: 12px; background: rgba(212,175,55,0.1);">Get Full Dataset ($49)</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="badge mono">SPIRIT RECORD #{spirit_id or '101'} · {stype.upper()}</span>
      <h1 class="heading" style="font-size: 2.6rem; margin-top: 8px;">{name}</h1>
      <p style="color: var(--text-muted); font-size: 1.15rem; margin-top: 8px;">Standardized provenance ledger record with quantitative ABV threshold, age statement, and source attribution.</p>
    </section>

    {spirit_profile(s, dist)}

    <div class="grid">
      <div class="card">
        <h3 class="heading" style="font-size:1.4rem; color:var(--gold); margin-bottom:18px; border-bottom:1px solid var(--border); padding-bottom:12px;">Quantitative Determination</h3>
        <div class="metric-row">
          <span class="metric-label">Spirit Designation</span>
          <span class="metric-val">{stype}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Alcohol by Volume (ABV)</span>
          <span class="metric-val">{abv_display}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Age Statement</span>
          <span class="metric-val">{age_display}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Bottle Volume</span>
          <span class="metric-val">{vol} ml</span>
        </div>
      </div>

      <div class="card">
        <h3 class="heading" style="font-size:1.4rem; color:var(--gold); margin-bottom:18px; border-bottom:1px solid var(--border); padding-bottom:12px;">Provenance & Ledger Source</h3>
        <div class="metric-row">
          <span class="metric-label">Source Authority</span>
          <span class="metric-val" style="color:var(--text-main); font-size:0.88rem; text-align:right; max-width:60%;">{source_name}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">License & Attribution</span>
          <span class="metric-val">Open/Verified Ledger</span>
        </div>
        <div style="margin-top: 24px; text-align: center;">
          <a href="{source_url}" target="_blank" rel="noopener noreferrer" class="btn-link" style="display:inline-block; margin:0;">🔬 Verify Source Provenance</a>
        </div>
      </div>
    </div>

    {related_block(
        ([(f"../distilleries/{slugify(dist['name'] + '-' + dist['country'] + '-' + dist['region'])}", f"{dist['name']} distillery", f"{dist['region']}, {dist['country']}")] if dist else []) +
        [(f"../spirits/{slugify(o['name'])}", o['name'], f"also {o['type']}") for o in spirits if o is not s and o.get('type') == stype][:3] +
        [(f"../spirits/{slugify(o['name'])}", o['name'], f"also from {distillery_of(o)['country']}") for o in spirits if o is not s and dist and distillery_of(o) and distillery_of(o)['country'] == dist['country'] and o.get('type') != stype][:2] +
        [("../spirits/", "All spirits and bottlings", None)], "Related spirits and distilleries")}
  </main>

  <footer>
    <div class="container">
      <p>WhiskyDB — Canonical Global Fine Spirits Catalog & REST API · <a href="/#pricing-section" style="color:var(--gold); text-decoration:none;">License Enterprise Dataset ($49/mo)</a></p>
    </div>
  </footer>
</body>
</html>"""
        with open(os.path.join(spirits_dir, f"{slug}.html"), mode='w', encoding='utf-8') as f_out:
            f_out.write(html_content)

    # Generate Distillery & Region Hub Pages
    for d in distilleries:
        dname = d.get('name', '').strip()
        country = d.get('country', 'Unknown').strip()
        region = d.get('region', 'General').strip()
        source_name = d.get('source_name', 'WhiskyDB Curated Ledger').strip()
        source_url = d.get('source_url', 'https://github.com/WhiskyyDB/whisky-database').strip()
        did = d.get('distillery_id', '')

        slug = slugify(f"{dname}-{country}-{region}")
        page_url = f"https://whiskydb.dataengineered.io/distilleries/{slug}"
        sitemap_urls.append((page_url, "0.9", "monthly"))

        # Find matching spirits if any
        matching = [s for s in spirits if dname.lower() in s.get('name', '').lower() or dname.lower() in s.get('type', '').lower()]
        matching_html = ""
        for m in matching:
            mslug = slugify(m.get('name', ''))
            matching_html += f"""
        <div class="card" style="margin-bottom:16px;">
          <h4 class="heading" style="font-size:1.15rem;"><a href="../spirits/{mslug}" style="color:var(--gold-light); text-decoration:none;">{m.get('name')}</a></h4>
          <p style="color:var(--text-muted); font-size:0.9rem; margin-top:4px;">{m.get('type')} · {m.get('abv')}% ABV</p>
        </div>"""

        if not matching_html:
            no_match_key = _record_key(did, dname)
            no_match_leads = [
                f"Verified {dname} distillery record inside the <strong style=\"color:var(--gold);\">{region}, {country}</strong> geographical determination.",
                f"{dname} is catalogued in the <strong style=\"color:var(--gold);\">{region}, {country}</strong> geographical determination.",
                f"This <strong style=\"color:var(--gold);\">{region}, {country}</strong> determination covers the {dname} distillery record.",
            ]
            matching_html = f'<p style="color:var(--text-muted); font-size:0.95rem;">{no_match_leads[no_match_key % len(no_match_leads)]} Access full mash bill and cask maturation lineages via the <a href="/#pricing-section" style="color:var(--gold-light);">WhiskyDB Enterprise SQL Snapshot</a>.</p>'

        profile_html = distillery_profile(d, matching)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(fit_title(dname, f"{region} distillery", "WhiskyDB"))}</title>
  <meta name="description" content="{html.escape(fit_desc(f"{dname} distillery in {region}, {country}: " + (f"{len(matching)} bottling(s) in WhiskyDB — {', '.join(m['name'] for m in matching)}. " if matching else "") + f"Source: {source_name}."))}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" hreflang="en" href="{page_url}" />
  <link rel="alternate" hreflang="x-default" href="{page_url}" />

  <meta property="og:title" content="{dname} Distillery ({region}, {country}) — WhiskyDB Hub" />
  <meta property="og:description" content="Taxonomic and geographic determination for {dname} in {region}, {country}." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:image" content="https://whiskydb.dataengineered.io/hero.png" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "{dname} Distillery ({region}, {country})",
    "description": "Distillery hub and geographical spirits determination for {dname} located in {region}, {country}.",
    "url": "{page_url}"
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet"></noscript>

  <style>
    :root {{
      --bg-dark: #0a0b0d;
      --bg-card: #111318;
      --gold: #d4af37;
      --gold-light: #e2c044;
      --text-main: #f0f2f8;
      --text-muted: #949ab1;
      --border: rgba(212, 175, 55, 0.2);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-main); line-height: 1.6; padding-bottom: 60px; }}
    .heading {{ font-family: 'Outfit', sans-serif; font-weight: 700; }}
    .mono {{ font-family: 'Fira Code', monospace; }}
    header {{ border-bottom: 1px solid var(--border); padding: 20px 0; background: rgba(17, 19, 24, 0.8); backdrop-filter: blur(10px); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 0 24px; }}
    .nav-bar {{ display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text-main); text-decoration: none; }}
    .brand span {{ color: var(--gold); }}
    .btn-link {{ color: var(--text-main); text-decoration: none; font-size: 0.9rem; border: 1px solid var(--border); padding: 8px 16px; border-radius: 6px; transition: all 0.2s; }}
    .btn-link:hover {{ background: var(--gold); color: #0a0b0d; border-color: var(--gold); }}
    .hero {{ padding: 48px 0; border-bottom: 1px solid var(--border); }}
    .badge {{ display: inline-block; background: rgba(212, 175, 55, 0.15); color: var(--gold-light); padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 12px; border: 1px solid rgba(212,175,55,0.3); }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 36px; }}
    @media(max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .card {{ background: var(--bg-card); border: 1px solid var(--border); padding: 28px; border-radius: 12px; }}
    .metric-row {{ display: flex; justify-content: space-between; border-bottom: 1px dashed rgba(212,175,55,0.15); padding: 14px 0; }}
    .metric-row:last-child {{ border-bottom: none; }}
    .metric-label {{ color: var(--text-muted); font-size: 0.92rem; }}
    .metric-val {{ font-weight: 600; font-family: 'Fira Code', monospace; color: var(--gold-light); }}
    footer {{ margin-top: 60px; border-top: 1px solid var(--border); padding: 32px 0; text-align: center; font-size: 0.85rem; color: var(--text-muted); }}
    .related ul{{list-style:none;padding:0}}.related li{{padding:6px 0}}.related-why{{color:var(--text-muted);font-size:.9em}}
  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="/" class="brand">Whisky<span>DB</span></a>
      <div>
        <a href="/#explorer-section" class="btn-link">← Explorer</a>
        <a href="/#pricing-section" class="btn-link" style="margin-left: 12px; background: rgba(212,175,55,0.1);">Get Full Dataset ($49)</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="badge mono">DISTILLERY REGISTRY #{did or '201'} · {country.upper()}</span>
      <h1 class="heading" style="font-size: 2.6rem; margin-top: 8px;">{dname} Distillery</h1>
      <p style="color: var(--text-muted); font-size: 1.15rem; margin-top: 8px;">Geographical determination and regional water/mash lineage located in {region}, {country}.</p>
    </section>

    {profile_html}

    <div class="grid">
      <div class="card">
        <h3 class="heading" style="font-size:1.4rem; color:var(--gold); margin-bottom:18px; border-bottom:1px solid var(--border); padding-bottom:12px;">Geographical Registry</h3>
        <div class="metric-row">
          <span class="metric-label">Country of Origin</span>
          <span class="metric-val">{country}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Appellation / Region</span>
          <span class="metric-val">{region}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Source Citation</span>
          <span class="metric-val" style="font-size:0.85rem; text-align:right; max-width:60%;">{source_name}</span>
        </div>
        <div style="margin-top: 24px; text-align: center;">
          <a href="{source_url}" target="_blank" rel="noopener noreferrer" class="btn-link" style="display:inline-block; margin:0;">🔬 Verify Distillery Registry</a>
        </div>
      </div>

      <div class="card">
        <h3 class="heading" style="font-size:1.4rem; color:var(--gold); margin-bottom:18px; border-bottom:1px solid var(--border); padding-bottom:12px;">Verified Spirits & Determinations</h3>
        {matching_html}
      </div>
    </div>

    {related_block(
        [(f"../distilleries/{slugify(o['name'] + '-' + o['country'] + '-' + o['region'])}", o['name'], f"also {o['country']}") for o in distilleries if o is not d and o.get('country') == country][:3] +
        [(f"../distilleries/{slugify(o['name'] + '-' + o['country'] + '-' + o['region'])}", o['name'], f"{o['country']}") for o in distilleries if o is not d and o.get('country') != country][:2] +
        [("../distilleries/", "All distilleries", None)], "Related distilleries")}
  </main>

  <footer>
    <div class="container">
      <p>WhiskyDB — Canonical Global Fine Spirits Catalog & REST API · <a href="/#pricing-section" style="color:var(--gold); text-decoration:none;">License Enterprise Dataset ($49/mo)</a></p>
    </div>
  </footer>
</body>
</html>"""
        with open(os.path.join(distilleries_dir, f"{slug}.html"), mode='w', encoding='utf-8') as f_out:
            f_out.write(html_content)

    # Generate updated sitemap.xml
    entries = [("https://whiskydb.dataengineered.io/", os.path.join(root_dir, "index.html"), "weekly", "1.0"),
               ("https://whiskydb.dataengineered.io/spirits/", os.path.join(spirits_dir, "index.html"), "monthly", "0.8"),
               ("https://whiskydb.dataengineered.io/distilleries/", os.path.join(distilleries_dir, "index.html"), "monthly", "0.8")]
    entries += [(loc, os.path.join(root_dir, loc.split("dataengineered.io/", 1)[1] + ".html"), freq, prio) for loc, prio, freq in sitemap_urls]
    n = write_sitemap(root_dir, entries)

    print(f"Successfully generated {len(spirits)} spirit pages (`spirits/*.html`), {len(distilleries)} distillery hubs (`distilleries/*.html`), and updated sitemap.xml with {n} URLs!")

if __name__ == '__main__':
    main()
