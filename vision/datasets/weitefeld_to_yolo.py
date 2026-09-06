#!/usr/bin/env python3
"""
weitefeld_to_yolo.py — convert the Weitefeld aerial forest anomaly dataset into a
tiled, multi-class YOLO dataset.

Dataset: Nathan et al., "An aerial color image anomaly dataset for search missions
in complex forested terrain", Scientific Data 13:747 (2026).
DOI 10.1038/s41597-026-07101-w  |  Zenodo 15848419  |  https://weitefeld.cg.jku.at/

Why this dataset matters here: it is the only public aerial dataset with labelled
shelters and objects under real vegetative occlusion in forest. HERIDAL is
person-only, so it cannot validate a multi-class HPI pipeline. This can.

Classes in data.txt: 0=unknown, 1=shelter, 2=object, 3=person.

CRITICAL — split by FINDING, not by image. Each of the 405 physical findings was
photogrammetrically back-projected into up to 85 overlapping frames, producing
34,424 labels. Splitting by image puts the same physical tarp in train and test.
That leak is far worse than the tile-level one, because it is the same object, not
merely a similar scene. This script groups by a finding key and assigns splits at
that level.

TWO FORMAT ASSUMPTIONS YOU MUST VERIFY against the real data.txt (they are taken
from the paper's prose, not from the file itself):
  1. Box encoding is `x y height width` where x,y is described as the "lower-left"
     corner. Whether y increases downward (image convention) or upward is
     ambiguous in the paper. Use --box-origin to switch, then run --verify and
     LOOK at the renders. If boxes sit below the objects, flip it.
  2. There is no explicit finding ID column, so findings are grouped by their
     comment strings, which repeat across back-projections. The script reports how
     many unique findings it detected — if that number is nowhere near ~405,
     the grouping heuristic is wrong for your copy of the file and you should
     group on whatever ID column your data.txt actually has.

Usage:
    python weitefeld_to_yolo.py \
        --images-root data/raw/weitefeld/images \
        --data-txt   data/raw/weitefeld/data.txt \
        --out        data/processed/weitefeld_yolo_v1 \
        --tile 1024 --overlap 0.2 --core-only --seed 42

    python weitefeld_to_yolo.py --verify data/processed/weitefeld_yolo_v1 --n 16
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
import shlex
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

# data.txt class codes -> our YOLO indices.
CLASS_NAMES = {0: "unknown", 1: "shelter", 2: "object", 3: "person"}
N_CORE_ENTRIES = 34424  # peer-reviewed core; later rows are community additions


# --------------------------------------------------------------------------- #
# data.txt parsing
# --------------------------------------------------------------------------- #

def parse_data_txt(path: Path, core_only: bool, drop_unknown: bool):
    """
    Yield dicts for entries that carry a usable bounding box.

    Expected 13 whitespace-separated, quote-aware tokens:
      strip img px py cls "volunteer comment"
      strip img bx by bh bw "police comment"
    Missing values are -1 / "NA".
    """
    rows, skipped = [], {"no_box": 0, "malformed": 0, "unknown_cls": 0}

    for n, raw in enumerate(path.read_text(errors="replace").splitlines()):
        if core_only and n >= N_CORE_ENTRIES:
            break
        raw = raw.strip()
        if not raw:
            continue
        try:
            t = shlex.split(raw)
        except ValueError:
            skipped["malformed"] += 1
            continue
        if len(t) < 12:
            skipped["malformed"] += 1
            continue

        try:
            strip, img_no = int(t[0]), int(t[1])
            cls = int(t[4])
            vol_comment = t[5] if len(t) > 5 else "NA"
            bx, by, bh, bw = (int(t[8]), int(t[9]), int(t[10]), int(t[11]))
            pol_comment = t[12] if len(t) > 12 else "NA"
        except (ValueError, IndexError):
            skipped["malformed"] += 1
            continue

        if min(bx, by, bh, bw) < 0:
            skipped["no_box"] += 1   # point-only label, no box to train on
            continue
        if cls not in CLASS_NAMES:
            skipped["unknown_cls"] += 1
            continue
        if drop_unknown and cls == 0:
            continue

        # No explicit finding ID in the documented format. Comments are authored
        # per finding and repeat across back-projections, so they act as a key.
        # Normalise case/whitespace first: "Shelter" and "shelter" describing the
        # same object should hash identically, not fragment into two findings.
        # Note this does NOT fix the opposite failure mode -- two genuinely
        # different objects both described with a generic phrase like "shelter"
        # will still collide into one key. That is a structural limitation of
        # grouping by comment text with no real finding-ID column in data.txt,
        # not something normalisation can repair. Document it as a known
        # limitation rather than treat it as solved.
        def _norm(s: str) -> str:
            return " ".join(s.lower().split())

        fkey = hashlib.sha1(
            f"{_norm(vol_comment)}|{_norm(pol_comment)}".encode()
        ).hexdigest()[:12]

        rows.append({"strip": strip, "img_no": img_no, "cls": cls,
                     "bx": bx, "by": by, "bh": bh, "bw": bw, "finding": fkey})

    return rows, skipped


def index_images(images_root: Path) -> dict[tuple[int, int], Path]:
    """Map (strip, image_number) -> file. Names are AA_BBBBB_<ts>_<us>_RGB.jpg."""
    idx = {}
    for p in images_root.rglob("*_RGB.jpg"):
        parts = p.stem.split("_")
        if len(parts) < 2:
            continue
        try:
            idx[(int(parts[0]), int(parts[1]))] = p
        except ValueError:
            continue
    return idx


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #

def to_xyxy(r, H: int, origin: str):
    """data.txt box -> absolute (x1, y1, x2, y2). See format caveat in docstring.

    Three interpretations of "by", since the paper's wording ("lower-left
    corner" of the box) is ambiguous about which image convention it assumes:
      - 'topleft':      by is the box's TOP edge; extend downward. (legacy default)
      - 'bottomleft':   by is measured from the BOTTOM of the whole image
                        (i.e. the image itself is y-flipped).
      - 'bottomedge':   by is literally the row of the box's BOTTOM edge under
                        standard top-left image coordinates (y down); extend
                        upward from it. This is the literal reading of "lower-
                        left corner of a bounding box" and was previously
                        missing as an option -- verify against --verify renders,
                        especially on SMALL boxes. A vertical offset of one box
                        height is invisible on large boxes (still overlaps a
                        big structure) but completely misses small ones.
    """
    x1, w, h = r["bx"], r["bw"], r["bh"]
    if origin == "topleft":
        y1 = r["by"]
    elif origin == "bottomedge":
        y1 = r["by"] - h
    else:  # 'bottomleft': y measured from the image bottom
        y1 = H - r["by"] - h
    return float(x1), float(y1), float(x1 + w), float(y1 + h)


def tile_origins(size: int, tile: int, stride: int) -> list[int]:
    if size <= tile:
        return [0]
    xs = list(range(0, size - tile + 1, stride))
    if xs[-1] != size - tile:
        xs.append(size - tile)
    return xs


# --------------------------------------------------------------------------- #
# Conversion
# --------------------------------------------------------------------------- #

def convert(a):
    images_root, out = Path(a.images_root), Path(a.out)
    rng = random.Random(a.seed)
    stride = max(1, int(a.tile * (1 - a.overlap)))

    rows, skipped = parse_data_txt(Path(a.data_txt), a.core_only, a.drop_unknown)
    if not rows:
        sys.exit("No usable boxed entries parsed — check --data-txt and the format.")

    findings = {r["finding"] for r in rows}
    print(f"Parsed {len(rows)} boxed labels across {len(findings)} unique findings")
    print(f"  skipped: {skipped}")
    if not 200 <= len(findings) <= 700:
        print(f"  ! WARNING: expected roughly 405 findings, detected {len(findings)}.\n"
              f"    The comment-based grouping is probably wrong for your data.txt.\n"
              f"    Inspect the file and group on its real ID column before trusting\n"
              f"    these splits — a bad grouping silently leaks objects across splits.")

    # --- splits assigned at FINDING level ---------------------------------- #
    ordered = sorted(findings)
    rng.shuffle(ordered)
    n_test = max(int(len(ordered) * a.test_frac), 1)
    n_val = max(int(len(ordered) * a.val_frac), 1)
    split_of = {}
    for i, f in enumerate(ordered):
        split_of[f] = "test" if i < n_test else ("val" if i < n_test + n_val
                                                 else "train")
    print(f"Findings -> train {len(ordered) - n_test - n_val}, "
          f"val {n_val}, test {n_test}")

    by_image: dict[tuple[int, int], list] = defaultdict(list)
    for r in rows:
        by_image[(r["strip"], r["img_no"])].append(r)

    img_index = index_images(images_root)
    print(f"Indexed {len(img_index)} images under {images_root}")
    missing = [k for k in by_image if k not in img_index]
    if missing:
        print(f"  ! {len(missing)} labelled images not found on disk "
              f"(expected if you downloaded only some strips)")

    for s in ("train", "val", "test"):
        (out / s / "images").mkdir(parents=True, exist_ok=True)
        (out / s / "labels").mkdir(parents=True, exist_ok=True)

    class_ids = sorted(c for c in CLASS_NAMES if not (a.drop_unknown and c == 0))
    remap = {c: i for i, c in enumerate(class_ids)}

    manifest, stats = [], defaultdict(lambda: defaultdict(int))
    done = 0

    for key, recs in by_image.items():
        p = img_index.get(key)
        if p is None:
            continue

        # An image can host back-projections of several findings. Mixed splits
        # within one image would reintroduce the leak, so route the image to a
        # single split and drop labels belonging to findings assigned elsewhere.
        votes = defaultdict(int)
        for r in recs:
            votes[split_of[r["finding"]]] += 1
        split = max(votes, key=votes.get)
        recs = [r for r in recs if split_of[r["finding"]] == split]
        if not recs:
            continue

        img = cv2.imread(str(p))
        if img is None:
            continue
        H, W = img.shape[:2]
        boxes = [(to_xyxy(r, H, a.box_origin), remap[r["cls"]]) for r in recs]

        for oy in tile_origins(H, a.tile, stride):
            for ox in tile_origins(W, a.tile, stride):
                kept, ambiguous = [], False
                for (x1, y1, x2, y2), c in boxes:
                    area = max((x2 - x1) * (y2 - y1), 1e-9)
                    cx1, cy1 = max(x1, ox), max(y1, oy)
                    cx2, cy2 = min(x2, ox + a.tile), min(y2, oy + a.tile)
                    if cx2 <= cx1 or cy2 <= cy1:
                        continue
                    if ((cx2 - cx1) * (cy2 - cy1)) / area < a.min_visible:
                        ambiguous = True
                        break
                    kept.append((cx1 - ox, cy1 - oy, cx2 - ox, cy2 - oy, c))
                if ambiguous:
                    stats[split]["dropped"] += 1
                    continue
                if not kept and rng.random() > a.neg_ratio:
                    continue

                tid = f"{key[0]:02d}_{key[1]}_x{ox}_y{oy}"
                cv2.imwrite(str(out / split / "images" / f"{tid}.jpg"),
                            img[oy:oy + a.tile, ox:ox + a.tile],
                            [cv2.IMWRITE_JPEG_QUALITY, 95])
                (out / split / "labels" / f"{tid}.txt").write_text("\n".join(
                    f"{c} {((x1 + x2) / 2) / a.tile:.6f} {((y1 + y2) / 2) / a.tile:.6f} "
                    f"{(x2 - x1) / a.tile:.6f} {(y2 - y1) / a.tile:.6f}"
                    for x1, y1, x2, y2, c in kept))

                stats[split]["pos" if kept else "neg"] += 1
                for *_, c in kept:
                    stats[split][f"cls_{class_ids[c]}"] += 1
                manifest.append({
                    "tile_id": tid, "split": split, "provenance": "Weitefeld",
                    "strip": key[0], "source_image": key[1],
                    "tile_x": ox, "tile_y": oy, "n_boxes": len(kept),
                    "findings": ";".join(sorted({r["finding"] for r in recs})),
                })

        done += 1
        if done % 200 == 0:
            print(f"  {done} source images processed")

    if not manifest:
        sys.exit("No tiles written — check --images-root and the box format flags.")

    (out / "manifests").mkdir(exist_ok=True)
    with open(out / "manifests" / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)

    names = "\n".join(f"  {i}: {CLASS_NAMES[c]}" for i, c in enumerate(class_ids))
    (out / "data.yaml").write_text(
        f"path: {out.resolve()}\ntrain: train/images\nval: val/images\n"
        f"test: test/images\nnc: {len(class_ids)}\nnames:\n{names}\n")

    (out / "PROVENANCE.md").write_text(
        "# weitefeld_yolo_v1\n\n"
        "Source: Nathan et al., Sci Data 13:747 (2026), "
        "doi:10.1038/s41597-026-07101-w, Zenodo 15848419.\n"
        "Generated by weitefeld_to_yolo.py\n\n"
        f"tile={a.tile} overlap={a.overlap} min_visible={a.min_visible} "
        f"neg_ratio={a.neg_ratio} box_origin={a.box_origin} "
        f"core_only={a.core_only} drop_unknown={a.drop_unknown} seed={a.seed}\n\n"
        "Splits assigned per FINDING, so back-projections of one physical object "
        "never span train/val/test.\n")

    print("\n--- summary ---")
    for s in ("train", "val", "test"):
        d = stats[s]
        print(f"{s:>5}: {d['pos'] + d['neg']:6d} tiles "
              f"({d['pos']} pos / {d['neg']} neg), {d['dropped']} dropped")
        per = {CLASS_NAMES[c]: d[f"cls_{c}"] for c in class_ids if d[f"cls_{c}"]}
        print(f"       boxes per class: {per or '(none)'}")
    print(f"\nWrote {out}\nNOW RUN --verify AND LOOK AT THE RENDERS — the box "
          f"origin convention is unverified.")


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

def verify(dataset: Path, n: int):
    out_dir = dataset / "_verify"
    out_dir.mkdir(exist_ok=True)
    rng = random.Random(0)

    names = {}
    y = (dataset / "data.yaml")
    if y.exists():
        for ln in y.read_text().splitlines():
            s = ln.strip()
            if s and s[0].isdigit() and ":" in s:
                i, nm = s.split(":", 1)
                names[int(i)] = nm.strip()

    cands = [(s, l) for s in ("train", "val", "test")
             for l in (dataset / s / "labels").glob("*.txt") if l.stat().st_size]
    if not cands:
        sys.exit("No non-empty labels found.")

    palette = [(0, 255, 0), (0, 200, 255), (255, 120, 0), (255, 0, 200)]
    for split, lbl in rng.sample(cands, min(n, len(cands))):
        img = cv2.imread(str(dataset / split / "images" / f"{lbl.stem}.jpg"))
        if img is None:
            continue
        h, w = img.shape[:2]
        for line in lbl.read_text().strip().splitlines():
            c, xc, yc, bw, bh = line.split()
            c = int(c)
            xc, yc, bw, bh = (float(v) for v in (xc, yc, bw, bh))
            x1, y1 = int((xc - bw / 2) * w), int((yc - bh / 2) * h)
            x2, y2 = int((xc + bw / 2) * w), int((yc + bh / 2) * h)
            col = palette[c % len(palette)]
            cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)
            cv2.putText(img, names.get(c, str(c)), (x1, max(y1 - 5, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1, cv2.LINE_AA)
        cv2.imwrite(str(out_dir / f"{split}_{lbl.stem}.jpg"), img)

    print(f"Wrote renders to {out_dir}\n"
          "If boxes are vertically mirrored relative to the objects, re-run the "
          "conversion with the other --box-origin value.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images-root", type=str)
    p.add_argument("--data-txt", type=str)
    p.add_argument("--out", type=str)
    p.add_argument("--tile", type=int, default=1024)
    p.add_argument("--overlap", type=float, default=0.2)
    p.add_argument("--min-visible", type=float, default=0.3)
    p.add_argument("--neg-ratio", type=float, default=0.05,
                   help="Lower than HERIDAL: these frames are mostly empty forest")
    p.add_argument("--val-frac", type=float, default=0.15)
    p.add_argument("--test-frac", type=float, default=0.15)
    p.add_argument("--box-origin", choices=["topleft", "bottomleft", "bottomedge"],
                   default="topleft", help="See the format caveat in the docstring")
    p.add_argument("--core-only", action="store_true",
                   help="Use only the first 34,424 peer-reviewed entries")
    p.add_argument("--drop-unknown", action="store_true",
                   help="Exclude class 0 ('unknown'), which is semantically messy")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verify", type=str)
    p.add_argument("--n", type=int, default=16)
    a = p.parse_args()

    if a.verify:
        verify(Path(a.verify), a.n)
    elif a.images_root and a.data_txt and a.out:
        convert(a)
    else:
        p.error("provide --images-root, --data-txt and --out, or --verify")


if __name__ == "__main__":
    main()