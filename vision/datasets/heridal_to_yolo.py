#!/usr/bin/env python3
"""
heridal_to_yolo.py — convert HERIDAL (VOC XML, 4000x3000) into a tiled YOLO dataset.

Why tiling: HERIDAL persons are ~20-60 px in a 4000x3000 frame. Resizing the full
frame to 640 or even 1024 shrinks them to a handful of pixels and the baseline
becomes meaningless. Tiling preserves native resolution.

Key guarantees:
  * Splits are assigned by SOURCE IMAGE, never by tile. Overlapping tiles from one
    photo are near-duplicates; leaking them across train/val inflates val mAP badly.
  * Boxes clipped below --min-visible cause the whole tile to be DROPPED, rather
    than emitting a sliver box or an unlabelled person. Both alternatives teach
    the model something false.
  * Person-free tiles are subsampled to --neg-ratio. All-negatives dominate ~9:1
    otherwise.
  * A manifest CSV records every tile's provenance. Commit it; gitignore the images.

Usage:
    python heridal_to_yolo.py --heridal-root data/raw/heridal \
        --out data/processed/heridal_yolo_v1 \
        --tile 1024 --overlap 0.2 --min-visible 0.3 --neg-ratio 0.10 --seed 42

    python heridal_to_yolo.py --verify data/processed/heridal_yolo_v1 --n 12
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import cv2
import numpy as np

IMG_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


# --------------------------------------------------------------------------- #
# VOC parsing
# --------------------------------------------------------------------------- #

def parse_voc(xml_path: Path) -> list[tuple[float, float, float, float]]:
    """Return [(x1, y1, x2, y2), ...] in absolute pixel coords."""
    root = ET.parse(xml_path).getroot()
    boxes = []
    for obj in root.findall("object"):
        bnd = obj.find("bndbox")
        if bnd is None:
            continue
        try:
            x1 = float(bnd.findtext("xmin"))
            y1 = float(bnd.findtext("ymin"))
            x2 = float(bnd.findtext("xmax"))
            y2 = float(bnd.findtext("ymax"))
        except (TypeError, ValueError):
            continue
        if x2 > x1 and y2 > y1:
            boxes.append((x1, y1, x2, y2))
    return boxes


def find_pairs(root: Path) -> dict[str, list[tuple[Path, Path]]]:
    """
    Locate (image, xml) pairs for each HERIDAL split.

    HERIDAL folder naming varies between distributions. We probe several common
    layouts rather than hardcoding one, and report clearly if nothing matches.
    """
    candidates = {
        "train": [("trainImages", "trainLabels"), ("train/images", "train/labels"),
                  ("training/images", "training/labels")],
        "test": [("testImages", "testLabels"), ("test/images", "test/labels"),
                 ("testing/images", "testing/labels")],
    }

    out: dict[str, list[tuple[Path, Path]]] = {}
    for split, options in candidates.items():
        for img_rel, lbl_rel in options:
            img_dir, lbl_dir = root / img_rel, root / lbl_rel
            if not (img_dir.is_dir() and lbl_dir.is_dir()):
                continue
            pairs = []
            for img in sorted(img_dir.iterdir()):
                if img.suffix not in IMG_EXTS:
                    continue
                xml = lbl_dir / f"{img.stem}.xml"
                if xml.exists():
                    pairs.append((img, xml))
            if pairs:
                out[split] = pairs
                print(f"  {split}: {len(pairs)} pairs from {img_rel} / {lbl_rel}")
                break

    if not out:
        sys.exit(
            f"No image/label pairs found under {root}.\n"
            "Inspect the extracted archive and pass the correct layout, or rename "
            "folders to trainImages/trainLabels and testImages/testLabels."
        )
    return out


# --------------------------------------------------------------------------- #
# Tiling
# --------------------------------------------------------------------------- #

def tile_origins(size: int, tile: int, stride: int) -> list[int]:
    """Origins covering [0, size), with the last tile flush to the right edge."""
    if size <= tile:
        return [0]
    xs = list(range(0, size - tile + 1, stride))
    if xs[-1] != size - tile:
        xs.append(size - tile)
    return xs


def clip_boxes(boxes, ox, oy, tile, min_visible):
    """
    Clip boxes into the tile at (ox, oy).

    Returns (kept, ambiguous) where `kept` are tile-local boxes and `ambiguous`
    is True if any box was clipped to between 0 and min_visible of its area,
    which means the tile should be dropped entirely.
    """
    kept, ambiguous = [], False
    for x1, y1, x2, y2 in boxes:
        orig_area = (x2 - x1) * (y2 - y1)
        cx1, cy1 = max(x1, ox), max(y1, oy)
        cx2, cy2 = min(x2, ox + tile), min(y2, oy + tile)
        if cx2 <= cx1 or cy2 <= cy1:
            continue  # entirely outside this tile
        frac = ((cx2 - cx1) * (cy2 - cy1)) / max(orig_area, 1e-9)
        if frac < min_visible:
            ambiguous = True
            break
        kept.append((cx1 - ox, cy1 - oy, cx2 - ox, cy2 - oy))
    return kept, ambiguous


def to_yolo(box, tile: int) -> str:
    x1, y1, x2, y2 = box
    return (f"0 {((x1 + x2) / 2) / tile:.6f} {((y1 + y2) / 2) / tile:.6f} "
            f"{(x2 - x1) / tile:.6f} {(y2 - y1) / tile:.6f}")


# --------------------------------------------------------------------------- #
# Conversion
# --------------------------------------------------------------------------- #

def convert(args):
    root, out = Path(args.heridal_root), Path(args.out)
    rng = random.Random(args.seed)
    stride = max(1, int(args.tile * (1 - args.overlap)))

    print(f"Scanning {root} ...")
    pairs = find_pairs(root)

    # --- assign splits BY SOURCE IMAGE ------------------------------------- #
    assign: dict[Path, str] = {}
    train_pairs = pairs.get("train", [])
    shuffled = train_pairs[:]
    rng.shuffle(shuffled)
    n_val = int(len(shuffled) * args.val_frac)
    if shuffled and n_val == 0:
        n_val = 1  # never produce an empty val split
    for img, _ in shuffled[:n_val]:
        assign[img] = "val"
    for img, _ in shuffled[n_val:]:
        assign[img] = "train"
    for img, _ in pairs.get("test", []):
        assign[img] = "test"

    print(f"Source images -> train {len(shuffled) - n_val}, val {n_val}, "
          f"test {len(pairs.get('test', []))}")

    for split in ("train", "val", "test"):
        (out / split / "images").mkdir(parents=True, exist_ok=True)
        (out / split / "labels").mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    stats = {s: {"pos": 0, "neg": 0, "dropped": 0, "boxes": 0}
             for s in ("train", "val", "test")}

    all_pairs = [(i, x) for v in pairs.values() for (i, x) in v]
    for n, (img_path, xml_path) in enumerate(all_pairs, 1):
        split = assign[img_path]
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ! unreadable, skipping: {img_path.name}")
            continue
        H, W = img.shape[:2]
        boxes = parse_voc(xml_path)

        for oy in tile_origins(H, args.tile, stride):
            for ox in tile_origins(W, args.tile, stride):
                kept, ambiguous = clip_boxes(boxes, ox, oy, args.tile,
                                             args.min_visible)
                if ambiguous:
                    stats[split]["dropped"] += 1
                    continue

                is_neg = len(kept) == 0
                # Keep all negatives in test (honest full-coverage eval);
                # subsample them in train/val to control class balance.
                if is_neg and split != "test" and rng.random() > args.neg_ratio:
                    continue

                tile_id = f"{img_path.stem}_x{ox}_y{oy}"
                cv2.imwrite(str(out / split / "images" / f"{tile_id}.jpg"),
                            img[oy:oy + args.tile, ox:ox + args.tile],
                            [cv2.IMWRITE_JPEG_QUALITY, 95])
                (out / split / "labels" / f"{tile_id}.txt").write_text(
                    "\n".join(to_yolo(b, args.tile) for b in kept))

                stats[split]["neg" if is_neg else "pos"] += 1
                stats[split]["boxes"] += len(kept)
                manifest_rows.append({
                    "tile_id": tile_id, "split": split,
                    "source_image": img_path.name, "provenance": "HERIDAL",
                    "tile_x": ox, "tile_y": oy, "tile_size": args.tile,
                    "n_person": len(kept),
                })

        if n % 100 == 0:
            print(f"  {n}/{len(all_pairs)} source images")

    # --- outputs ----------------------------------------------------------- #
    man_dir = out / "manifests"
    man_dir.mkdir(exist_ok=True)
    with open(man_dir / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        w.writeheader()
        w.writerows(manifest_rows)

    (out / "data.yaml").write_text(
        f"path: {out.resolve()}\n"
        f"train: train/images\nval: val/images\ntest: test/images\n"
        f"nc: 1\nnames:\n  0: person\n"
    )

    (out / "PROVENANCE.md").write_text(
        f"# heridal_yolo_v1\n\n"
        f"Source: HERIDAL (Bozic-Stulic, Marusic & Gotovac, IJCV 2019)\n"
        f"Generated by heridal_to_yolo.py\n\n"
        f"tile={args.tile} overlap={args.overlap} min_visible={args.min_visible} "
        f"neg_ratio={args.neg_ratio} val_frac={args.val_frac} seed={args.seed}\n\n"
        f"Splits assigned by source image, not by tile.\n"
    )

    print("\n--- summary ---")
    for s, v in stats.items():
        total = v["pos"] + v["neg"]
        print(f"{s:>5}: {total:6d} tiles ({v['pos']} pos / {v['neg']} neg), "
              f"{v['boxes']} boxes, {v['dropped']} dropped (ambiguous clip)")
    print(f"\nWrote {out}\nNOW RUN --verify BEFORE TRAINING.")


# --------------------------------------------------------------------------- #
# Verification renders — do not skip this
# --------------------------------------------------------------------------- #

def verify(dataset: Path, n: int):
    """Render n random tiles with boxes drawn. Coordinate bugs are only ever
    visible here, and are invisible in every metric downstream."""
    out_dir = dataset / "_verify"
    out_dir.mkdir(exist_ok=True)
    rng = random.Random(0)

    # prefer tiles that actually contain boxes
    candidates = []
    for split in ("train", "val", "test"):
        for lbl in (dataset / split / "labels").glob("*.txt"):
            if lbl.stat().st_size > 0:
                candidates.append((split, lbl))
    if not candidates:
        sys.exit("No non-empty label files found — conversion produced no boxes.")

    for split, lbl in rng.sample(candidates, min(n, len(candidates))):
        img_p = dataset / split / "images" / f"{lbl.stem}.jpg"
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        h, w = img.shape[:2]
        for line in lbl.read_text().strip().splitlines():
            _, xc, yc, bw, bh = (float(v) for v in line.split())
            x1, y1 = int((xc - bw / 2) * w), int((yc - bh / 2) * h)
            x2, y2 = int((xc + bw / 2) * w), int((yc + bh / 2) * h)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imwrite(str(out_dir / f"{split}_{lbl.stem}.jpg"), img)

    print(f"Wrote renders to {out_dir}\n"
          "Open them. Every box must sit on a person. If any box is offset, "
          "flipped, or scaled wrongly, fix it now — the baseline is worthless "
          "otherwise.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--heridal-root", type=str)
    p.add_argument("--out", type=str)
    p.add_argument("--tile", type=int, default=1024)
    p.add_argument("--overlap", type=float, default=0.2)
    p.add_argument("--min-visible", type=float, default=0.3,
                   help="Drop the tile if any box is clipped below this fraction")
    p.add_argument("--neg-ratio", type=float, default=0.10,
                   help="Fraction of person-free tiles to keep in train/val")
    p.add_argument("--val-frac", type=float, default=0.10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verify", type=str, help="Path to a converted dataset")
    p.add_argument("--n", type=int, default=12)
    a = p.parse_args()

    if a.verify:
        verify(Path(a.verify), a.n)
    elif a.heridal_root and a.out:
        convert(a)
    else:
        p.error("provide --heridal-root and --out, or --verify")


if __name__ == "__main__":
    main()
