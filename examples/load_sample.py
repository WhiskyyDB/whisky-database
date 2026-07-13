"""Load and explore the WhiskyDB free sample with the standard library only."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(os.path.dirname(HERE), "samples")
TAXONOMY = os.path.join(os.path.dirname(HERE), "taxonomy")


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


spirits = load(os.path.join(SAMPLES, "spirits.csv"))
distilleries = load(os.path.join(SAMPLES, "distilleries.csv"))
casks = load(os.path.join(TAXONOMY, "casks.csv"))
flavors = load(os.path.join(TAXONOMY, "flavors.csv"))

print(f"{len(spirits)} spirits | {len(distilleries)} distilleries | "
      f"{len(casks)} cask styles | {len(flavors)} flavor descriptors")

# Spirits by type
by_type = {}
for s in spirits:
    by_type[s["type"]] = by_type.get(s["type"], 0) + 1
print("\nSpirits by type:")
for spirit_type, count in sorted(by_type.items(), key=lambda kv: -kv[1]):
    print(f"  {spirit_type:<22} {count}")

# Cask taxonomy as a hierarchy
print("\nCask taxonomy (category > sub_type > specific_style):")
for c in casks[:5]:
    print(f'  {c["category"]} > {c["sub_type"]} > {c["specific_style"]} ({c["wood_species"]})')
print(f"  ... {len(casks)} styles total")

# Provenance: every record names its source
sources = sorted({s["source_name"] for s in spirits})
print("\nSample provenance sources:", ", ".join(sources))
