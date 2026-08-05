# WhiskyDB — Sources & Upstream Licenses

Every record in WhiskyDB traces to a provenance ledger entry naming one of the
open sources below. Records derived from share-alike or attribution sources
retain those upstream obligations.

| Source | URL | License | Contributes |
| :--- | :--- | :--- | :--- |
| US TTB COLA Registry (via COLA Cloud API) | ttbonline.gov / app.colacloud.us | Public domain — US federal work (17 U.S.C. § 105) | Label approvals: brand, class, origin, ABV, barcode |
| UK Companies House | company-information.service.gov.uk | Open Government Licence v3.0 | Distillery incorporations: founding year, status, jurisdiction |
| EU eAmbrosia GI Register | ec.europa.eu/agriculture/eambrosia | EU open data (Decision 2011/833/EU) | Protected spirit appellations (PGI/PDO) |
| Open Food Facts / Open Drinks Facts | openfoodfacts.org | Open Database License (ODbL) v1.0 | Bottled products: names, brands, barcodes, volumes, ABV |
| Wikipedia (List of distilleries in Scotland; List of whisky brands) | en.wikipedia.org | CC-BY-SA 4.0 | Distillery and brand names, regions |
| Wikidata | wikidata.org | CC0 1.0 (public domain) | Distillery entities, countries, inception years |
| WhiskyHunter | whiskyhunter.net/api | Open statistical API | Distillery-level monthly auction price indices |
| Producer-published specifications | producers' official sites | Facts (not copyrightable); curated | Published mash bills, cask programs, brand ownership |
| US labeling law (27 CFR 5.143) | ecfr.gov | Public domain | New-charred-oak cask derivation for straight bourbon/rye |

## WhiskyDB Curated Seed

Six benchmark spirits and their distilleries (Lagavulin, Buffalo Trace, Yamazaki,
Woodford Reserve, Bulleit, Four Roses) carry the source
`WhiskyDB Curated Seed (producer-published)`. These records were **hand-curated
by WhiskyDB**, with every fact taken from the producers' own official
publications: mash bills as published by the distilleries (e.g. Woodford
Reserve 72/18/10), founding years, cask maturation programs, and
producer-stated tasting descriptors. They exist so the dataset ships with a
fully populated, verifiable reference set across all 10 tables (mash bills,
cask mappings, tasting notes) — attributes most open registries don't publish.
Factual specifications are not copyrightable; the curation and normalization
are WhiskyDB's.

## Attribution obligations for reuse

- **ODbL-derived records** (source `Open Food Facts…`): if you publicly use a
  substantial part, you must attribute Open Food Facts and share derivative
  *databases* under ODbL.
- **CC-BY-SA-derived records** (source `Wikipedia…`): attribute Wikipedia and
  share adaptations of those records under a compatible license.
- **Public-domain and OGL records** (TTB, Wikidata, Companies House, eAmbrosia):
  attribution appreciated; OGL requires acknowledging the source.

The `source_name` column on every sample row (and the `data_sources` ledger in
the full dataset) tells you which regime applies to each record.
