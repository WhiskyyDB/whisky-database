# WhiskyDB — Sample Preview

Human-readable preview of the free sample (snapshot `2026.07`). Machine-readable
CSVs live in [`samples/`](samples/); full field documentation in
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

## Spirits (`samples/spirits.csv`)

| spirit_id | name | type | age | abv | volume_ml | source_name |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Lagavulin 16 Year Old | Single Malt Scotch | 16.0 | 43.0 | 700 | Seed Academic DB |
| 2 | Eagle Rare 10 Year Old | Bourbon | 10.0 | 45.0 | 700 | Seed Academic DB |
| 3 | Yamazaki 12 Year Old | Single Malt Japanese | 12.0 | 43.0 | 700 | Seed Academic DB |
| 4 | Woodford Reserve Kentucky Straight Bourbon | Bourbon | — | 43.2 | 700 | Seed Academic DB |
| 5 | Bulleit Bourbon | Bourbon | — | 45.0 | 700 | Seed Academic DB |
| 6 | Four Roses Single Barrel | Bourbon | — | 50.0 | 700 | Seed Academic DB |
| 7 | Ballantine's Finest | Whisky | — | 40.0 | 700 | Open Food Facts / Open Drinks Facts (ODbL) |
| 8 | Jack Daniel's Whiskey | Whisky | — | 40.0 | 700 | Open Food Facts / Open Drinks Facts (ODbL) |
| 9 | Johnnie Walker Red Scotch whisky | Scotch Whisky | — | 40.0 | 700 | Open Food Facts / Open Drinks Facts (ODbL) |
| 10 | Monkey Shoulder | Whisky | — | 40.0 | 700 | Open Food Facts / Open Drinks Facts (ODbL) |
| 11 | Jack Daniel's No.7 | Whisky | — | 40.0 | 1000 | Open Food Facts / Open Drinks Facts (ODbL) |
| 12 | Jameson Whiskey | Whisky | — | 40.0 | 1000 | Open Food Facts / Open Drinks Facts (ODbL) |
| 13 | Whisky Old N°7 | Whisky | — | 40.0 | 700 | Open Food Facts / Open Drinks Facts (ODbL) |
| 14 | Whisky Ecosse blended sans âge 1 L Sir Edwards | Whisky | — | 40.0 | 1000 | Open Food Facts / Open Drinks Facts (ODbL) |
| 15 | Whisky Ecosse Blended 40% vol. | Whisky | — | 40.0 | 1000 | Open Food Facts / Open Drinks Facts (ODbL) |

## Distilleries (`samples/distilleries.csv`)

| distillery_id | name | country | region | source_name |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Lagavulin | Scotland | Islay | Seed Academic DB |
| 2 | Buffalo Trace | USA | Kentucky | Seed Academic DB |
| 3 | Yamazaki | Japan | Osaka | Seed Academic DB |
| 4 | Woodford Reserve | USA | Kentucky | Seed Academic DB |
| 5 | Bulleit Distilling Co. | USA | Kentucky | Seed Academic DB |
| 6 | Four Roses | USA | Kentucky | Seed Academic DB |
| 7 | Aberargie | Scotland | Aberargie | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 8 | Aberfeldy | Scotland | Aberfeldy | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 9 | Aberlour | Scotland | Aberlour | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 10 | Abhainn Dearg | Scotland | Uig,Isle of Lewis | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 11 | Ailsa Bay | Scotland | Girvan | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 12 | Allt-A-Bhainne | Scotland | Glenrinnes | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 13 | Annandale | Scotland | Annan | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 14 | Arbikie | Scotland | Inverkeilor | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |
| 15 | Ardbeg | Scotland | Port Ellen | Wikipedia - List of distilleries in Scotland (CC-BY-SA) |

## Cask taxonomy (`taxonomy/casks.csv`, open source)

| category | sub_type | specific_style | wood_species |
| :--- | :--- | :--- | :--- |
| Sherry | Pedro Ximenez | PX Sherry Butt | Quercus alba |
| Sherry | Oloroso | Oloroso Sherry Puncheon | Quercus robur |
| Bourbon | Ex-Bourbon | 1st Fill Bourbon Barrel | Quercus alba |
| Bourbon | Ex-Bourbon | Refill Bourbon Barrel | Quercus alba |
| Port | Ruby Port | Ruby Port Pipe | Quercus robur |
| Port | Tawny Port | Tawny Port Pipe | Quercus robur |
| Rum | Caribbean Rum | Rum Cask | Quercus alba |
| Wine | Red Wine | Bordeaux Wine Cask | Quercus robur |
| Virgin Oak | American Oak | Virgin American Oak | Quercus alba |
| Virgin Oak | European Oak | Virgin Spanish Oak | Quercus robur |
| Sherry | Generic Sherry | Sherry Butt | Quercus robur |
| Bourbon | Ex-Bourbon | American Oak Cask | Quercus alba |
| Japanese Oak | Mizunara | Mizunara Oak Cask | Quercus mongolica |

## Flavor vocabulary (`taxonomy/flavors.csv`, open source)

| macro_category | descriptor |
| :--- | :--- |
| Peat & Smoke | Peat Smoke |
| Peat & Smoke | Medicinal / Iodine |
| Peat & Smoke | Bonfire Smoke |
| Sweet & Vanilla | Vanilla |
| Sweet & Vanilla | Caramel / Toffee |
| Sweet & Vanilla | Honey |
| Fruity | Citrus |
| Fruity | Dried Figs |
| Fruity | Orchard Fruit (Apple/Pear) |
| Fruity | Dark Berries |
| Spicy & Woody | Cinnamon |
| Spicy & Woody | Oak Spice |
| Spicy & Woody | Black Pepper |
| Rich & Nutty | Dark Chocolate |
| Rich & Nutty | Almond / Marzipan |

---

The full dataset adds mash bills, cask maturation mappings, standardized tasting
tags, and 20,000+ monthly auction price benchmarks — see the
[README](README.md#pricing) for access.
