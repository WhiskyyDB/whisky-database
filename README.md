<div align="center">

# 🥃 WhiskyDB — Fine Spirits & Whisky Dataset

**1,290+ whiskies & fine spirits · 3,200+ distilleries & producers · 20,000+ monthly auction-price benchmarks (2005 → today) · 100% provenance-tracked**

[![Sample: 15 rows](https://img.shields.io/badge/Free%20Sample-15%20rows-brightgreen.svg)](samples/spirits.csv)
[![🤗 Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-sample%20dataset-ffd21e.svg)](https://huggingface.co/datasets/Ichlibitiche/whiskydb-fine-spirits-sample)
[![🤗 Explorer](https://img.shields.io/badge/%F0%9F%A4%97%20Spaces-sample%20explorer-ffd21e.svg)](https://huggingface.co/spaces/Ichlibitiche/dataset-sample-explorers)
[![Kaggle](https://img.shields.io/badge/Kaggle-sample%20dataset-20BEFF.svg)](https://www.kaggle.com/datasets/ahtiticheamine/whiskydb-fine-spirits-sample)
[![Distilleries: 3,200+](https://img.shields.io/badge/Distilleries-3%2C200%2B-8a5a44.svg)](#whats-inside)
[![Price history: 2005→](https://img.shields.io/badge/Auction%20history-2005%E2%86%92today-gold.svg)](#auction-price-history--the-differentiated-part)
[![Snapshot: 2026.07](https://img.shields.io/badge/Snapshot-2026.07-blue.svg)](CHANGELOG.md)
[![Taxonomies: open](https://img.shields.io/badge/Cask%20%26%20Flavor%20taxonomies-open%20source-2ea44f.svg)](taxonomy/)
[![Get the data](https://img.shields.io/badge/Get%20the%20data-whisky--database.pages.dev-d4a643.svg)](https://whisky-database.pages.dev/)

**[→ Get the full dataset at whisky-database.pages.dev](https://whisky-database.pages.dev/)**

</div>

---

A structured, relational dataset of whiskies and fine spirits built **entirely from open, legally accessible public sources** — government label registries, corporate registries, open product databases, open encyclopedias, and open auction statistics — with a **provenance ledger entry behind every record** so any fact can be traced to its source.

This is a **catalog + market-index** dataset — strong on distillery breadth, product identity, spirit classification, and a deep **19-year monthly auction price history**. It is *not* a tasting-notes-at-scale dataset; the honest [field-coverage table](#field-coverage-the-honest-numbers) below shows exactly what is and isn't populated. No hype — just what's in the box.

## What's inside

| | Full dataset | Free sample |
| :--- | ---: | ---: |
| Spirits & bottlings | **1,290+** | 15 |
| Distilleries, brands & producers | **3,200+** | 15 |
| Countries represented | **110+** | — |
| Monthly auction-price benchmarks | **20,000+** | — |
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

- **20,000+** distillery-level monthly auction statistics: mean winning bid (GBP + USD-normalized), one row per distillery per month.
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
| **Standard Catalog** | Full dataset snapshots · SQLite + CSV · monthly refreshes | **$49** / month |
| **API & Valuation** | Live REST API · auction price benchmarks · commercial license | **$99** / month |
| **Live scrape** | On-demand, self-serve via Apify Actor | pay-per-result *(listing pending)* |

**[→ Get it at whisky-database.pages.dev](https://whisky-database.pages.dev/)** · or email **[whiskeydn.kite979@simplelogin.com](mailto:whiskeydn.kite979@simplelogin.com)** for the full dataset and custom work.

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

## License

- **Sample data & docs in this repo:** CC-BY-NC-4.0 — free to use with attribution, non-commercial (see [`LICENSE`](LICENSE)).
- **Taxonomies (`taxonomy/`):** CC-BY-4.0 — free for any use with attribution, including commercial.
- **Full dataset:** commercial license. Records derived from ODbL/CC-BY-SA sources retain their upstream attribution obligations — see [`SOURCES.md`](SOURCES.md).

Want a record corrected or removed? Email **[whiskeydn.kite979@simplelogin.com](mailto:whiskeydn.kite979@simplelogin.com)** or [open an issue](https://github.com/WhiskyyDB/whisky-database/issues).
