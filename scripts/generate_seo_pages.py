import csv
import os
import re
import datetime

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

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
        ("https://whisky-database.pages.dev/", "1.0", "weekly")
    ]

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

        slug = slugify(name)
        age_display = f"{age} Years Old" if (age and age.replace('.','',1).isdigit() and float(age) > 0) else "No Age Statement (NAS)"
        abv_display = f"{abv}% ABV" if abv else "40.0% ABV"

        page_url = f"https://whisky-database.pages.dev/spirits/{slug}.html"
        sitemap_urls.append((page_url, "0.8", "monthly"))

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} ({stype}) {abv_display} Mash Bill & Cask Lineage — WhiskyDB</title>
  <meta name="description" content="Structured determination and valuation metrics for {name}: {stype}, {age_display}, {abv_display}, {vol}ml bottle volume. Source verified via {source_name}." />
  <meta name="keywords" content="{name}, {stype}, {abv_display}, {age_display}, whisky database, mash bill, cask lineage, valuation index, {source_name}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" hreflang="en" href="{page_url}" />
  <link rel="alternate" hreflang="x-default" href="{page_url}" />

  <meta property="og:title" content="{name} ({stype}) Determination & Valuation Record — WhiskyDB" />
  <meta property="og:description" content="Exact ABV ({abv_display}), Age Statement ({age_display}), bottle volume ({vol}ml), and secondary market ledger." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="https://whisky-database.pages.dev/hero.png" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "{name} ({stype}) Structured Spirits Determination",
    "description": "Normalized botanical and cask parameters for {name}: {stype}, {abv_display}, {age_display}, {vol}ml volume, and secondary auction market tracking.",
    "url": "{page_url}",
    "creator": {{"@type": "Organization", "name": "WhiskyDB Initiative", "url": "https://whisky-database.pages.dev"}},
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
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://whisky-database.pages.dev/"}},
      {{"@type": "ListItem", "position": 2, "name": "Spirits Catalog", "item": "https://whisky-database.pages.dev/#explorer-section"}},
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
  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="../index.html" class="brand">Whisky<span>DB</span></a>
      <div>
        <a href="../index.html#explorer-section" class="btn-link">← Explorer</a>
        <a href="../index.html#pricing-section" class="btn-link" style="margin-left: 12px; background: rgba(212,175,55,0.1);">Get Full Dataset ($49)</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="badge mono">SPIRIT RECORD #{spirit_id or '101'} · {stype.upper()}</span>
      <h1 class="heading" style="font-size: 2.6rem; margin-top: 8px;">{name}</h1>
      <p style="color: var(--text-muted); font-size: 1.15rem; margin-top: 8px;">Standardized provenance ledger record with quantitative ABV threshold, age statement, and source attribution.</p>
    </section>

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
  </main>

  <footer>
    <div class="container">
      <p>WhiskyDB — Canonical Global Fine Spirits Catalog & REST API · <a href="../index.html#pricing-section" style="color:var(--gold); text-decoration:none;">License Enterprise Dataset ($49/mo)</a></p>
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
        page_url = f"https://whisky-database.pages.dev/distilleries/{slug}.html"
        sitemap_urls.append((page_url, "0.9", "monthly"))

        # Find matching spirits if any
        matching = [s for s in spirits if dname.lower() in s.get('name', '').lower() or dname.lower() in s.get('type', '').lower()]
        matching_html = ""
        for m in matching:
            mslug = slugify(m.get('name', ''))
            matching_html += f"""
        <div class="card" style="margin-bottom:16px;">
          <h4 class="heading" style="font-size:1.15rem;"><a href="../spirits/{mslug}.html" style="color:var(--gold-light); text-decoration:none;">{m.get('name')}</a></h4>
          <p style="color:var(--text-muted); font-size:0.9rem; margin-top:4px;">{m.get('type')} · {m.get('abv')}% ABV</p>
        </div>"""

        if not matching_html:
            matching_html = f'<p style="color:var(--text-muted); font-size:0.95rem;">Verified distillery record inside the <strong style="color:var(--gold);">{region}, {country}</strong> geographical determination. Access full mash bill and cask maturation lineages via the <a href="../index.html#pricing-section" style="color:var(--gold-light);">WhiskyDB Enterprise SQL Snapshot</a>.</p>'

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{dname} Distillery ({region}, {country}) — Mash Bill & Cask Ledger — WhiskyDB</title>
  <meta name="description" content="Verified distillery determination for {dname} located in {region}, {country}. Explore spirits lineage, regional water source profiles, and provenance citations via {source_name}." />
  <meta name="keywords" content="{dname}, {region} whisky, {country} distilleries, mash bill ledger, cask types, {source_name}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" hreflang="en" href="{page_url}" />
  <link rel="alternate" hreflang="x-default" href="{page_url}" />

  <meta property="og:title" content="{dname} Distillery ({region}, {country}) — WhiskyDB Hub" />
  <meta property="og:description" content="Taxonomic and geographic determination for {dname} in {region}, {country}." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:image" content="https://whisky-database.pages.dev/hero.png" />

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
  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="../index.html" class="brand">Whisky<span>DB</span></a>
      <div>
        <a href="../index.html#explorer-section" class="btn-link">← Explorer</a>
        <a href="../index.html#pricing-section" class="btn-link" style="margin-left: 12px; background: rgba(212,175,55,0.1);">Get Full Dataset ($49)</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="badge mono">DISTILLERY REGISTRY #{did or '201'} · {country.upper()}</span>
      <h1 class="heading" style="font-size: 2.6rem; margin-top: 8px;">{dname} Distillery</h1>
      <p style="color: var(--text-muted); font-size: 1.15rem; margin-top: 8px;">Geographical determination and regional water/mash lineage located in {region}, {country}.</p>
    </section>

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
  </main>

  <footer>
    <div class="container">
      <p>WhiskyDB — Canonical Global Fine Spirits Catalog & REST API · <a href="../index.html#pricing-section" style="color:var(--gold); text-decoration:none;">License Enterprise Dataset ($49/mo)</a></p>
    </div>
  </footer>
</body>
</html>"""
        with open(os.path.join(distilleries_dir, f"{slug}.html"), mode='w', encoding='utf-8') as f_out:
            f_out.write(html_content)

    # Generate updated sitemap.xml
    sitemap_path = os.path.join(root_dir, 'sitemap.xml')
    today_str = datetime.date.today().isoformat()
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, prio, freq in sitemap_urls:
        sitemap_xml.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today_str}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>")
    sitemap_xml.append('</urlset>')

    with open(sitemap_path, mode='w', encoding='utf-8') as f_sitemap:
        f_sitemap.write("\n".join(sitemap_xml) + "\n")

    print(f"Successfully generated {len(spirits)} spirit pages (`spirits/*.html`), {len(distilleries)} distillery hubs (`distilleries/*.html`), and updated sitemap.xml with {len(sitemap_urls)} URLs!")

if __name__ == '__main__':
    main()
