# WhiskyDB — Data Dictionary

Field reference for the WhiskyDB fine spirits dataset (snapshot `2026.10`).
The free samples (`samples/spirits.csv`, `samples/distilleries.csv`) use the columns
below. The full dataset ships the same fields plus the complete 10-table relational
SQLite build described at the bottom.

## `samples/spirits.csv`

| Column | Type | Description | Coverage* |
| :--- | :--- | :--- | ---: |
| `spirit_id` | integer | Stable primary key | 100% |
| `name` | string | Canonical bottling name (Latin-script, cleaned) | 100% |
| `type` | enum | `Single Malt Scotch` · `Bourbon` · `Rye Whiskey` · `Irish Whiskey` · `Japanese Whisky` · `Scotch Whisky` · `Whisky` … | 100% |
| `age` | integer | Age statement in years; empty = NAS or unstated | <1% |
| `abv` | float | Alcohol by volume (%). Stated by the source for at least 22% of records (e.g. federal label details): the share whose ABV differs from 40.0. A 40.0 is either stated by the source or the documented default, which this edition cannot tell apart | 100% |
| `volume_ml` | integer | Bottle volume normalized to milliliters (700/750/1000…). Where the source states none, a documented default: 750 on every US label-registry (TTB COLA) record, whose labels do not publish volume; 700 on the curated seed rows and on Open Food Facts records without a stated quantity | 100% |
| `source_name` | string | Provenance: source the record came from | 100% |
| `source_url` | string | Provenance: source endpoint | 100% |

## `samples/distilleries.csv`

| Column | Type | Description | Coverage* |
| :--- | :--- | :--- | ---: |
| `distillery_id` | integer | Stable primary key | 100% |
| `name` | string | Producer, distillery, brand or company name: the US label registry, Open Food Facts and the Wikipedia brands list name brands, not producers | 100% |
| `country` | string | Country (normalized: `USA`, `Scotland`, `Northern Ireland`…), as a source states it: where a distillery stands, a company's headquarters, or where a brand's whisky is made. `Global` when the dataset has no single stated country: none stated, or several origins (supermarket own labels); never "sold worldwide". Up to the 2026.10 edition it also covered nine Wikipedia list entries that name their country after a dash, such as "Kavalan – Taiwan". Two exceptions up to the 2026.10 edition: Open Food Facts producers carried the first country a product is sold in, and owner companies from Wikipedia's brands list the country of the section they appear in (Diageo "USA"). From 2026.11 both follow the rule (a stated origin, the company's headquarters, or `Global`), and the full dataset ships the evidence for each corrected row | 99% specific |
| `region` | string | Region / locality (`Islay`, `Kentucky`, GI category…) | 100% |
| `source_name` | string | Provenance: source the record came from | 100% |
| `source_url` | string | Provenance: source endpoint | 100% |

## `taxonomy/casks.csv` (open source, CC-BY-4.0)

| Column | Description |
| :--- | :--- |
| `category` | Tier 1 — `Sherry` · `Bourbon` · `Port` · `Wine` · `Rum` · `Virgin Oak` · `Japanese Oak` |
| `sub_type` | Tier 2 — `Pedro Ximenez` · `Oloroso` · `Ex-Bourbon` · `Ruby Port` · `Mizunara` … |
| `specific_style` | Tier 3 — `PX Sherry Butt` · `1st Fill Bourbon Barrel` · `Mizunara Oak Cask` … |
| `wood_species` | Botanical species — `Quercus alba` · `Quercus robur` · `Quercus mongolica` |
| `description` | Short human-readable description |

## `taxonomy/flavors.csv` (open source, CC-BY-4.0)

| Column | Description |
| :--- | :--- |
| `macro_category` | `Peat & Smoke` · `Sweet & Vanilla` · `Fruity` · `Spicy & Woody` · `Rich & Nutty` |
| `descriptor` | Controlled descriptor — `Peat Smoke` · `Vanilla` · `Dried Figs` · `Oak Spice` … |

## Full dataset — relational build (SQLite)

The commercial snapshot normalizes into 10 tables:

| Table | What it holds |
| :--- | :--- |
| `data_sources` | Provenance ledger: source name, type, endpoint, license notes, access timestamp |
| `distilleries` | 2,500+ producers & brands with country, region, founded year, active/dissolved status; the table also holds the 270+ protected spirit appellations of the EU GI register (eAmbrosia), which are places of origin, not producers, and are not counted in the 2,500+ |
| `brands` | Brand ownership (e.g. Lagavulin → Diageo) |
| `spirits` | 2,700+ bottlings: type, ABV, volume, barcode/label ID, age, NAS flag |
| `mash_bills` | Producer-published grain compositions (corn/rye/barley/wheat %) |
| `cask_taxonomy` | The 3-tier cask hierarchy: the styles of `taxonomy/casks.csv` plus those the cask mapper derives from product names (e.g. Port Pipe) |
| `spirit_casks` | 1,200+ spirit↔cask maturation mappings with stage and fill type (rule-derived from product names and US labeling law, producer-published for the curated seed) |
| `flavor_taxonomy` | The controlled flavor vocabulary (mirrors `taxonomy/flavors.csv`) |
| `spirit_tasting_notes` | Standardized flavor tags with phase (Nose/Palate/Finish) and 1–3 intensity |
| `price_benchmarks` | 20,000+ rows of monthly distillery auction indices, Nov 2005 → Oct 2024, GBP + USD; one row per linked bottling per month (a distillery's index repeats for its linked bottlings; some bottlings linked by recent monthly refreshes carry only its latest months) |

Every content table carries a `source_id` foreign key into `data_sources` (`primary_source_id` on `spirits`) — 100% of rows resolve to a valid provenance entry (enforced and tested).

\* Share of the full dataset with a non-empty / non-default value.

Questions or corrections: whiskydb@dataengineered.io · [issues](https://github.com/WhiskyyDB/whisky-database/issues)
