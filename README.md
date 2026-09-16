<div align="center">

# 🥃 WhiskyDB — Fine Spirits & Whisky Dataset

**2,301 whiskies & fine spirits · 3,764 distilleries & producers · 21,156 monthly auction-price benchmarks (2005 → today) · 100% provenance-tracked**

[![Sample: 15 rows](https://img.shields.io/badge/Free%20Sample-15%20rows-brightgreen.svg)](samples/spirits.csv)
[![🤗 Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-sample%20dataset-ffd21e.svg)](https://huggingface.co/datasets/Ichlibitiche/whiskydb-fine-spirits-sample)
[![🤗 Explorer](https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-sample%20explorer-ffd21e.svg)](https://huggingface.co/spaces/Ichlibitiche/dataset-sample-explorers)
[![Kaggle](https://img.shields.io/badge/Kaggle-sample%20dataset-20BEFF.svg)](https://www.kaggle.com/datasets/ahtiticheamine/whiskydb-fine-spirits-sample)
[![Distilleries: 3,764](https://img.shields.io/badge/Distilleries-3%2C764-8a5a44.svg)](#whats-inside)
[![Price history: 2005→](https://img.shields.io/badge/Auction%20history-2005%E2%86%92today-gold.svg)](#auction-price-history--the-differentiated-part)
[![Snapshot: 2026.07](https://img.shields.io/badge/Snapshot-2026.07-blue.svg)](CHANGELOG.md)
[![Taxonomies: open](https://img.shields.io/badge/Cask%20%26%20Flavor%20taxonomies-open%20source-2ea44f.svg)](taxonomy/)
[![Get the data](https://img.shields.io/badge/Get%20the%20data-whiskydb.dataengineered.io-d4a643.svg)](https://whiskydb.dataengineered.io/)

**[→ Get the full dataset at whiskydb.dataengineered.io](https://whiskydb.dataengineered.io/)**

**Free sample:** [15 rows](samples/spirits.csv) · **Full catalog: $49 one-time** → [Buy on Stripe](https://buy.stripe.com/eVq3cw4p2afccI382s38401) · or [$49 / month with the auto-delivered monthly refresh](https://buy.stripe.com/bJeaEY6xa1IG7nJaaA38402)

</div>

---

A structured, relational dataset of whiskies and fine spirits built **entirely from open, legally accessible public sources** — government label registries, corporate registries, open product databases, open encyclopedias, and open auction statistics — with a **provenance ledger entry behind every record** so any fact can be traced to its source.

This is a **catalog + market-index** dataset — strong on distillery breadth, product identity, spirit classification, and a deep **19-year monthly auction price history**. It is *not* a tasting-notes-at-scale dataset; the honest [field-coverage table](#field-coverage-the-honest-numbers) below shows exactly what is and isn't populated. No hype — just what's in the box.

## What's inside

| | Full dataset | Free sample |
| :--- | ---: | ---: |
| Spirits & bottlings | **2,301** | 15 |
| Distilleries, brands & producers | **3,764** | 15 |
| Countries represented | **110+** | — |
| Monthly auction-price benchmarks | **21,156** | — |
| Protected GI appellations (EU/UK) | **270+** | — |
| Open cask & flavor taxonomies | 14 styles · 15 descriptors | ✔ included |
| Formats | SQLite · CSV | CSV |

The free [`samples/spirits.csv`](samples/spirits.csv) and [`samples/distilleries.csv`](samples/distilleries.csv) are curated subsets showing the schema and quality. Explore them interactively in the [🤗 Sample Explorer](https://huggingface.co/spaces/Ichlibitiche/dataset-sample-explorers), or load them straight from the [🤗 sample dataset](https://huggingface.co/datasets/Ichlibitiche/whiskydb-fine-spirits-sample) or [Kaggle](https://www.kaggle.com/datasets/ahtiticheamine/whiskydb-fine-spirits-sample) (with a [live starter notebook](https://www.kaggle.com/code/ahtiticheamine/whiskydb-fine-spirits-starter-notebook)). The [`taxonomy/`](taxonomy/) CSVs (hierarchical cask styles and controlled flavor vocabulary) are **fully open source** — use them in your own projects with attribution.

## Field coverage (the honest numbers)

Measured across the full dataset. Public sources don't all publish every attribute — these numbers are up front so you can decide if the fields you need are covered.

| Field | Coverage | | Field | Coverage |
| :--- | ---: | --- | :--- | ---: |
| Spirit name / type | 100% | | Distillery country | 88% |
| Barcode / label ID | 99% | | Distillery founded year | 23% |
| Explicit label ABV | 16%* | | Age statement | <1%† |

\* 16% of spirits carry an explicitly sourced ABV (e.g. from US federal label details, cask-strength values up to 62.5%); the rest carry the documented 40.0 default — the legal minimum for whisky in the US/EU — clearly identifiable and upgraded monthly as label-registry quota allows.
† Most public listings are NAS (no age statement) or don't state age; treat this column as sparse.

## Auction price history — the differentiated part

- **21,156** distillery-level monthly auction statistics: mean winning bid (GBP + USD-normalized), one row per distillery per month.
- **225 consecutive months** — November 2005 → today — across **33 whisky distilleries** and 93 linked bottlings.
- Honestly labeled: every row is a `Distillery Auction Index` (market-level index), **never** passed off as a bottle-specific realization.
- Sourced from open statistical auction data; ideal for valuation models, trend analysis, and price-vs-age studies.

## Provenance

Every table row carries a `source_id` into a provenance ledger (`data_sources`) recording the source name, endpoint, license, and access timestamp. Sources include:

| Source | License | Contributes |
| :--- | :--- | :--- |
| US TTB COLA label registry | Public domain (17 U.S.C. § 105) | Label approvals, brands, classes, ABVs, barcodes |
| UK Companies House | Open Government Licence v3.0 | Distillery incorporations, founding years, status |
| EU eAmbrosia GI register | EU open data | Protected spirit appellations (PGI/PDO) |
| Open Food Facts | ODbL | Bottled products, barcodes, volumes |
| Wikipedia / Wikidata | CC-BY-SA / CC0 | Distillery names, regions, founding years |
| WhiskyHunter open statistics | Open data | Monthly auction price indices |

See [`SOURCES.md`](SOURCES.md) for full attribution and license details, and [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for every field.

## Pricing

| Tier | What | Price |
| :--- | :--- | :--- |
| **Sample** | This repo: sample CSVs + open taxonomies | Free |
| **Standard Catalog** | Full dataset snapshot · SQLite + CSV · 21,156 auction-price benchmarks · commercial license | **$49** one-time ([Stripe](https://buy.stripe.com/eVq3cw4p2afccI382s38401)) |
| **Monthly refresh subscription** | The same catalog, each monthly refresh auto-delivered | **$49** / month ([Stripe](https://buy.stripe.com/bJeaEY6xa1IG7nJaaA38402)) |

**[→ Get it at whiskydb.dataengineered.io](https://whiskydb.dataengineered.io/)** · or use the [contact form](https://whiskydb.dataengineered.io/#contact-section) (whiskydb@dataengineered.io) for the full dataset and custom work.

## Use cases

- Bar-menu & hospitality software (clean names, types, ABV, volumes, barcodes)
- Collection-tracking and spirits-discovery apps
- Whisky investment analytics on a 19-year monthly auction index
- Flavor/cask-based recommendation engines on the open taxonomies
- ML / RAG corpora over a provenance-tracked spirits knowledge base

## Quick look

```python
import csv
spirits = list(csv.DictReader(open("samples/spirits.csv", encoding="utf-8")))
print(len(spirits), "spirits, e.g.", spirits[0]["name"], f'({spirits[0]["abv"]}% ABV)')
# → 15 spirits, e.g. Lagavulin 16 Year Old (43.0% ABV)
```

A fuller example is in [`examples/load_sample.py`](examples/load_sample.py). A human-readable preview of the sample is in [`SAMPLE_PREVIEW.md`](SAMPLE_PREVIEW.md).

## Localized pages (i18n)

The site pages (`index.html`, `404.html`, `spirits/`, `distilleries/`) are also published under `/es/`, `/de/`, `/fr/` and `/pt-br/`. Those copies are generated by `scripts/i18n_common.py` (config in `i18n.config.json`, translations in `locales/<lang>.json`). The English pages at the root stay the source of truth, so never hand-edit the `<lang>/` directories.

- After regenerating the English pages (`python scripts/generate_seo_pages.py`, which also rewrites `sitemap.xml` without the locale URLs) or editing `index.html`, run `python scripts/i18n_common.py build`, then `python scripts/i18n_common.py check` (must report 0 errors). `build` re-adds the hreflang block and language switcher to the English pages and rewrites `sitemap.xml` with every locale URL.
- New or changed copy: `python scripts/i18n_common.py todo --lang <lang>` writes the untranslated segments to `locales/_work/todo/` (git-ignored). Translate them following the portfolio's `scripts/i18n_style.md`, run `python scripts/i18n_common.py merge --lang <lang> <file>`, then `build` and `check` again.
- Data values (spirit, distillery and bottling names, types, regions, countries, source names) are marked `translate="no"` in the generator and `index.html`; keep new data-bearing markup marked the same way. Runtime UI text used by `app.js` lives in the `#i18n-strings` table in `index.html`, not in `app.js`. When `app.js` changes, bump `CACHE_NAME` in `sw.js`.

## License

- **Sample data & docs in this repo:** CC-BY-NC-4.0 — free to use with attribution, non-commercial (see [`LICENSE`](LICENSE)).
- **Taxonomies (`taxonomy/`):** CC-BY-4.0 — free for any use with attribution, including commercial.
- **Full dataset:** commercial license. Records derived from ODbL/CC-BY-SA sources retain their upstream attribution obligations — see [`SOURCES.md`](SOURCES.md).

Want a record corrected or removed? Write to whiskydb@dataengineered.io or [open an issue](https://github.com/WhiskyyDB/whisky-database/issues).
