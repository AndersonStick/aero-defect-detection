from collections import Counter
from pathlib import Path
import statistics as st
import xml.etree.ElementTree as ET

ROOT = Path("data/raw/NEU-DET")
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}

xmls = sorted((ROOT / "ANNOTATIONS").glob("*.xml"))
imgs = {p.stem: p for p in (ROOT / "IMAGES").rglob("*") if p.suffix.lower() in IMG_EXT}

boxes_per_class = Counter()
sizes = Counter()
n_boxes_img, widths, heights = [], [], []
missing, degenerate = [], 0

for x in xmls:
    root = ET.parse(x).getroot()
    if x.stem not in imgs:
        missing.append(x.stem)
    s = root.find("size")
    sizes[(s.findtext("width"), s.findtext("height"), s.findtext("depth"))] += 1
    objs = root.findall("object")
    n_boxes_img.append(len(objs))
    for o in objs:
        b = o.find("bndbox")
        xmin, ymin, xmax, ymax = (float(b.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax"))
        w, h = xmax - xmin, ymax - ymin
        if w <= 0 or h <= 0:
            degenerate += 1
            continue
        boxes_per_class[o.findtext("name")] += 1
        widths.append(w)
        heights.append(h)

print(f"XML files: {len(xmls)} | images found: {len(imgs)} | XML without image: {len(missing)}")
print(f"Image sizes (w, h, channels): {dict(sizes)}")
print(f"Boxes per class: {dict(boxes_per_class)}")
print(f"Boxes per image: min={min(n_boxes_img)} mean={st.mean(n_boxes_img):.2f} max={max(n_boxes_img)}")
print(f"Box width : min={min(widths):.0f} median={st.median(widths):.0f} max={max(widths):.0f}")
print(f"Box height: min={min(heights):.0f} median={st.median(heights):.0f} max={max(heights):.0f}")
print(f"Degenerate boxes: {degenerate}")