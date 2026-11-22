import random
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

ROOT = Path("data/raw/NEU-DET")
OUT = Path("reports/figures/eda_samples.png")
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}
CLASSES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]

imgs = {p.stem: p for p in (ROOT / "IMAGES").rglob("*") if p.suffix.lower() in IMG_EXT}

by_class = {c: [] for c in CLASSES}
for x in sorted((ROOT / "ANNOTATIONS").glob("*.xml")):
    first = ET.parse(x).getroot().find("object").findtext("name")
    by_class[first].append(x)

rng = random.Random(0)  # fixed seed -> reproducible figure
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
for ax, cls in zip(axes.ravel(), CLASSES):
    xml_path = rng.choice(by_class[cls])
    root = ET.parse(xml_path).getroot()
    ax.imshow(Image.open(imgs[xml_path.stem]), cmap="gray")
    for o in root.findall("object"):
        b = o.find("bndbox")
        xmin, ymin, xmax, ymax = (float(b.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax"))
        ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                               fill=False, edgecolor="red", linewidth=1.5))
        ax.text(xmin, ymin - 2, o.findtext("name"), color="yellow", fontsize=7)
    ax.set_title(f"{cls} ({xml_path.stem})")
    ax.axis("off")

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"Saved {OUT}")