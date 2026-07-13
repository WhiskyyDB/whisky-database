# Changelog

All notable changes to the WhiskyDB dataset snapshots.

> Counts are stated as **minimums** (e.g. `1,290+`). The dataset is refreshed
> monthly (automated label-registry ingestion), so the live figures only grow —
> the numbers below stay accurate between snapshots.

## 2026.07 — 2026-07-07

- Initial public snapshot.
- **1,290+** whiskies & fine spirits from **3,200+** distilleries, brands, and producers across **110+** countries.
- **20,000+** monthly distillery-level auction price benchmarks spanning **225 consecutive months** (Nov 2005 → Jul 2026 window), GBP + USD-normalized.
- **270+** protected EU/UK spirit geographical indications (PGI/PDO).
- **500+** spirit↔cask maturation mappings on the open 3-tier cask taxonomy; producer-published mash bills; standardized tasting tags.
- 100% provenance: every record resolves to a `data_sources` ledger entry (source, license, timestamp) — enforced by the automated test suite.
- Automated monthly refresh pipeline: new US label approvals ingested and fallback ABVs progressively upgraded to explicit label values.
