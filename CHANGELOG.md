# Changelog

All notable changes to the WhiskyDB dataset snapshots.

> Counts are stated as **minimums** (e.g. `1,290+`). The dataset is refreshed
> monthly (automated label-registry ingestion), so the live figures only grow —
> the numbers below stay accurate between snapshots.

## Unreleased — site updates through 2026-09-28

Site, distribution and localization updates since the initial snapshot (no new dataset snapshot
is recorded in this repo's history for this period).

- **Repository files off the website**: the translation catalogs (`/locales/`), the build scripts (`/scripts/`), `i18n.config.json`, `README.md`, `vercel.json` and the dotfiles belong to this repository, not to the website, but the site served them as plain files. They now answer the site's normal 404 page (also when requested as `/locales%2Fes.json` or `//locales/es.json`) and stay available here on GitHub. Pages, data files, samples, `llms.txt` and the sitemap are unchanged; the committed `scripts/__pycache__` bytecode file is no longer tracked (2026-09-28).
- **Hero layout**: on screens wider than 1024 px the homepage hero now shows the headline and the decanter image side by side (columns `1.1fr 0.9fr`), as designed. A typo in `index.css` (`1.1f`, an invalid unit) made browsers drop the whole column rule, so the hero stacked in one column at every width. Phones and tablets (1024 px and below) are unchanged. `index.css?v=` bumped on the homepage in every language, and the service-worker cache bumped (2026-09-28).
- **Section links**: links to a section (`/#pricing-section`, `/stats/#abv`, …) now land on it. The sticky header no longer covers the heading, and an arrival from another page is re-aligned once the web fonts and the homepage's spirit cards have loaded (shared `scripts/section_links.py` snippet on the homepage in every language and on `/stats/`; `app.js` calls it after rendering the cards). The hero image has explicit dimensions, so it no longer pushes the sections down while it loads. Dead links fixed: the "← Explorer" header link and the breadcrumbs pointed at a missing `/#explorer-section` (now `/#live-demo-section`), the 404 page's "Get the dataset" at `/#pricing` (now `/#pricing-section`), and four `/stats/` "Embed this chart" snippets at missing ids (all eight now link `#fig-<slug>`, the chart itself). Visible text and data unchanged; `app.js?v=` and the service-worker cache bumped (2026-09-27).
- **Translated Dataset markup**: on the Spanish, German, French and Portuguese pages the Dataset structured data now names its English original in `sameAs` (next to any existing `sameAs` links), so dataset search can tie the language copies to one canonical entry. English pages and all visible text are unchanged (2026-09-27).
- **Sale attribution**: every Stripe buy link carries `?client_reference_id=<brand>_<lang>_<surface>` (`home` / `landing`); the i18n build swaps the language token per locale and the delivery worker prints the id in the order email. Stripe does not store UTM parameters, so this is the only per-page attribution that reaches the order record (2026-09-20).
- **Domain**: moved to `whiskydb.dataengineered.io`; the `pages.dev` host 301s (2026-09-05). Brand contact moved to `@dataengineered.io` (2026-09-10).
- **`/stats/`**: citable whisky statistics page with an auction price index (2026-09-17).
- **i18n wave 1**: Spanish, German, French and Brazilian Portuguese copies under `/es/`, `/de/`, `/fr/`, `/pt-br/`, with a header and footer language menu; `app.js` is versioned so localized pages never run a stale cached copy (2026-09-17).
- **Phones**: fixed horizontal overflow (glow, hero stats, grid children, footer links) and busted the CSS cache (2026-09-17).
- **SEO**: distillery and spirit directory hubs, in-limit titles and descriptions, spirit↔distillery links, spirit profiles, git-dated sitemap, meta keywords dropped; the "whiskey" spelling carried; `git_lastmod` ignores CR/LF so regenerated pages keep their lastmod (2026-09-12 to 2026-09-19).
- **Footer trust links**: hub trust links on every generated page (2026-09-15).
- **Pricing and copy**: one-time $49 is the primary purchase; the API tier, quickstart and annual toggle were removed; `llms.txt` tiers match the site; one distillery count; no `mailto:` CTAs; homepage states 2,301 / 3,764 / 21,156 in the hero stat strip, matching README and `llms.txt` (2026-09-10 to 2026-09-11).
- **Kaggle**: links point at the new `dataengineered` username (2026-09-19).

## 2026.07 — 2026-07-07

- Initial public snapshot.
- **1,290+** whiskies & fine spirits from **3,200+** distilleries, brands, and producers across **110+** countries.
- **20,000+** monthly distillery-level auction price benchmarks spanning **225 consecutive months** (Nov 2005 → Jul 2026 window), GBP + USD-normalized.
- **270+** protected EU/UK spirit geographical indications (PGI/PDO).
- **500+** spirit↔cask maturation mappings on the open 3-tier cask taxonomy; producer-published mash bills; standardized tasting tags.
- 100% provenance: every record resolves to a `data_sources` ledger entry (source, license, timestamp) — enforced by the automated test suite.
- Automated monthly refresh pipeline: new US label approvals ingested and fallback ABVs progressively upgraded to explicit label values.
