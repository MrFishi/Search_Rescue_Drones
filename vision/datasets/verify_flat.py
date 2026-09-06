#!/usr/bin/env python3
"""Render YOLO-format label boxes onto images in a flat images/+labels/ folder.

Usage:
    python verify_flat.py <folder_with_images_and_labels_subdirs> [--n N]

Writes annotated renders to <folder>/_verify_flat/.
"""
import argparse
import random
from pathlib import Path

import cv2

CLASS_NAMES = {0: "unknown", 1: "shelter", 2: "object", 3: "person"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()

    img_dir = args.folder / "images"
    lbl_dir = args.folder / "labels"
    out_dir = args.folder / "_verify_flat"
    out_dir.mkdir(exist_ok=True)

    images = sorted(img_dir.glob("*.jpg"))
    random.seed(0)
    sample = images if len(images) <= args.n else random.sample(images, args.n)

    for img_path in sample:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  ! could not read image {img_path}")
            continue
        h, w = img.shape[:2]

        if not lbl_path.exists():
            print(f"  ! no label file for {img_path.name}")
        else:
            lines = [ln for ln in lbl_path.read_text().splitlines() if ln.strip()]
            if not lines:
                print(f"  ! empty label file for {img_path.name}")
            for ln in lines:
                parts = ln.split()
                cls = int(parts[0])
                cx, cy, bw, bh = (float(x) for x in parts[1:5])
                x1 = int((cx - bw / 2) * w)
                y1 = int((cy - bh / 2) * h)
                x2 = int((cx + bw / 2) * w)
                y2 = int((cy + bh / 2) * h)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = CLASS_NAMES.get(cls, f"cls{cls}")
                cv2.putText(img, label, (x1, max(0, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print(f"  {img_path.name}: cls={cls}({label}) "
                      f"px=({x1},{y1})-({x2},{y2}) img_size=({w}x{h})")

        cv2.imwrite(str(out_dir / img_path.name), img)

    print(f"\nWrote renders to {out_dir}")


if __name__ == "__main__":
    main()
