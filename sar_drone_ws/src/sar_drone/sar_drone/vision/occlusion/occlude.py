#!/usr/bin/env python3
"""
occlude.py — controlled synthetic occlusion for the O1 degradation sweep.

Occludes a target percentage of each annotated box's PIXEL AREA and writes a
frozen dataset to disk. Frozen matters: every model in the Phase 3 sweep must be
evaluated on byte-identical images, or the degradation curve is comparing RNG.

Modes, in increasing realism:
  cutout   solid axis-aligned rectangle. Crude lower bound. Fast.
  blobs    overlapping random ellipses. Irregular silhouette, wrong texture.
  texture  vegetation patches sampled from ELSEWHERE IN THE SAME IMAGE.
           Correct local texture, lighting and colour balance for free, with no
           external asset library. This is the default and the one to report.
  foliage  alpha-matted leaf/branch PNGs from --foliage-dir. Most realistic,
           needs an asset library.

Label policy: boxes are UNCHANGED. An 80%-occluded person keeps its full original
box, because the ground truth is "a person is present here", not "visible pixels
are here". Shrinking boxes would silently convert this into a small-object
detection experiment instead of an occlusion experiment.

LEAKAGE WARNING: if you use this as a TRAINING augmentation and only ever paste
occluders over targets, the model learns "occluder texture => person underneath".
It will ace your synthetic test set and fail on real foliage. --distractor-rate
pastes identical occluders at random background locations. Always use it when
generating training data.

Usage:
    # frozen eval buckets
    for f in 0 10 20 40 60 80; do
      python occlude.py --in data/processed/heridal_yolo_v1/test \
        --out data/occluded/heridal_occ_v1/frac_$f \
        --frac 0.$f --mode texture --seed 42
    done

    # training augmentation, with background distractors
    python occlude.py --in .../train --out .../train_occ \
        --frac 0.35 --frac-jitter 0.2 --mode texture \
        --distractor-rate 1.0 --seed 42
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import cv2
import numpy as np


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #

def stable_rng(*parts) -> np.random.Generator:
    """Seed derived from content, not call order — so re-running any single
    bucket reproduces byte-identical output."""
    key = "|".join(str(p) for p in parts).encode()
    return np.random.default_rng(int(hashlib.sha256(key).hexdigest()[:16], 16))


# --------------------------------------------------------------------------- #
# Mask builders — each returns a float mask in [0,1] over the box region
# --------------------------------------------------------------------------- #

def mask_cutout(h: int, w: int, frac: float, rng) -> np.ndarray:
    m = np.zeros((h, w), np.float32)
    if frac <= 0:
        return m
    # Random aspect, but area is fixed to frac. Clamp the aspect rather than the
    # dimensions, otherwise a high-frac rectangle gets truncated by the box edge
    # and silently undershoots (0.8 target landing at ~0.66).
    area = frac * h * w
    ar = rng.uniform(0.4, 2.5)
    bh_f = np.sqrt(area / ar)
    bw_f = area / bh_f
    if bw_f > w:
        bw_f, bh_f = float(w), area / w
    if bh_f > h:
        bh_f, bw_f = float(h), area / h
    bh = int(np.clip(round(bh_f), 1, h))
    bw = int(np.clip(round(bw_f), 1, w))
    y = int(rng.integers(0, max(h - bh, 0) + 1))
    x = int(rng.integers(0, max(w - bw, 0) + 1))
    m[y:y + bh, x:x + bw] = 1.0
    return m


def mask_blobs(h: int, w: int, frac: float, rng) -> np.ndarray:
    """
    Organic irregular occluder with EXACT coverage.

    Built by thresholding a smoothed low-frequency noise field at its (1-frac)
    quantile. Coverage is exact by construction, which matters: an earlier
    accumulate-ellipses-until-target approach overshot by 10-25% because the last
    ellipse always pushed past the goal, so a "40% bucket" was really ~50%.
    """
    if frac <= 0:
        return np.zeros((h, w), np.float32)
    if frac >= 1:
        return np.ones((h, w), np.float32)

    coarse = rng.random((max(h // 12, 3), max(w // 12, 3))).astype(np.float32)
    field = cv2.resize(coarse, (w, h), interpolation=cv2.INTER_CUBIC)
    field = cv2.GaussianBlur(field, (0, 0),
                             sigmaX=max(w / 18.0, 1.0),
                             sigmaY=max(h / 18.0, 1.0))
    return (field >= np.quantile(field, 1.0 - frac)).astype(np.float32)


def sample_texture_patch(img: np.ndarray, boxes, ph: int, pw: int, rng):
    """Grab a patch from the image that does not overlap any annotated box, so we
    never paste one person's pixels over another."""
    H, W = img.shape[:2]
    if ph >= H or pw >= W:
        return None
    for _ in range(40):
        y = int(rng.integers(0, H - ph))
        x = int(rng.integers(0, W - pw))
        if not any(x < bx2 and x + pw > bx1 and y < by2 and y + ph > by1
                   for bx1, by1, bx2, by2 in boxes):
            return img[y:y + ph, x:x + pw].copy()
    return None


# --------------------------------------------------------------------------- #
# Compositing
# --------------------------------------------------------------------------- #

def feather(mask: np.ndarray, px: int = 3) -> np.ndarray:
    """Soften edges. Hard edges are a texture the network can memorise."""
    if px <= 0:
        return mask
    k = px * 2 + 1
    return np.clip(cv2.GaussianBlur(mask, (k, k), 0), 0, 1)


def apply_occlusion(img, x1, y1, x2, y2, frac, mode, rng, boxes, foliage=None):
    """Occlude the region in place. Returns achieved coverage fraction."""
    x1, y1 = max(int(x1), 0), max(int(y1), 0)
    x2, y2 = min(int(x2), img.shape[1]), min(int(y2), img.shape[0])
    h, w = y2 - y1, x2 - x1
    if h < 2 or w < 2 or frac <= 0:
        return 0.0

    if mode == "cutout":
        mask = mask_cutout(h, w, frac, rng)
        fill = np.zeros((h, w, 3), np.uint8)
        fill[:] = (int(rng.integers(30, 90)), int(rng.integers(50, 110)),
                   int(rng.integers(30, 80)))  # muted BGR, vegetation-ish

    elif mode == "blobs":
        mask = mask_blobs(h, w, frac, rng)
        fill = np.zeros((h, w, 3), np.uint8)
        fill[:] = (int(rng.integers(25, 80)), int(rng.integers(45, 105)),
                   int(rng.integers(25, 75)))

    elif mode == "texture":
        mask = mask_blobs(h, w, frac, rng)
        patch = sample_texture_patch(img, boxes, h, w, rng)
        if patch is None:
            patch = np.zeros((h, w, 3), np.uint8)
            patch[:] = (50, 75, 45)
        fill = patch

    elif mode == "foliage":
        if not foliage:
            raise ValueError("--mode foliage requires --foliage-dir with RGBA PNGs")
        ov = foliage[int(rng.integers(0, len(foliage)))]
        ov = cv2.resize(ov, (w, h), interpolation=cv2.INTER_AREA)
        alpha = ov[:, :, 3].astype(np.float32) / 255.0
        # scale the asset's own alpha to hit the requested coverage
        cur = alpha.mean()
        mask = np.clip(alpha * (frac / cur), 0, 1) if cur > 1e-6 else alpha
        fill = ov[:, :, :3]
    else:
        raise ValueError(f"unknown mode {mode}")

    mask = feather(mask, 3)
    region = img[y1:y2, x1:x2].astype(np.float32)
    m3 = mask[:, :, None]
    img[y1:y2, x1:x2] = (region * (1 - m3) +
                         fill.astype(np.float32) * m3).astype(np.uint8)
    return float(mask.mean())


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #

def run(args):
    src, dst = Path(args.inp), Path(args.out)
    (dst / "images").mkdir(parents=True, exist_ok=True)
    (dst / "labels").mkdir(parents=True, exist_ok=True)

    foliage = None
    if args.mode == "foliage":
        foliage = [cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
                   for p in sorted(Path(args.foliage_dir).glob("*.png"))]
        foliage = [f for f in foliage if f is not None and f.shape[2] == 4]
        if not foliage:
            raise SystemExit("No RGBA PNGs found in --foliage-dir")

    images = sorted(p for p in (src / "images").iterdir()
                    if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not images:
        raise SystemExit(f"No images under {src / 'images'}")

    log, n_inst = [], 0

    for i, img_p in enumerate(images, 1):
        img = cv2.imread(str(img_p))
        if img is None:
            continue
        H, W = img.shape[:2]
        lbl_p = src / "labels" / f"{img_p.stem}.txt"
        lines = lbl_p.read_text().strip().splitlines() if lbl_p.exists() else []

        boxes = []
        for ln in lines:
            parts = ln.split()
            if len(parts) < 5:
                continue
            xc, yc, bw, bh = (float(v) for v in parts[1:5])
            boxes.append(((xc - bw / 2) * W, (yc - bh / 2) * H,
                          (xc + bw / 2) * W, (yc + bh / 2) * H))

        rng = stable_rng(args.seed, img_p.stem, args.frac, args.mode)

        for j, (x1, y1, x2, y2) in enumerate(boxes):
            f = args.frac
            if args.frac_jitter > 0:
                f = float(np.clip(rng.normal(f, args.frac_jitter * f), 0, 0.95))
            achieved = apply_occlusion(img, x1, y1, x2, y2, f, args.mode,
                                       rng, boxes, foliage)
            n_inst += 1
            log.append({"image": img_p.name, "instance": j,
                        "target_frac": round(f, 4),
                        "achieved_frac": round(achieved, 4)})

        # background distractors — prevents "occluder texture => target here"
        n_dist = int(round(args.distractor_rate * max(len(boxes), 1)))
        for _ in range(n_dist):
            if not boxes:
                bw_, bh_ = W // 12, H // 12
            else:
                bw_ = int(np.mean([b[2] - b[0] for b in boxes]))
                bh_ = int(np.mean([b[3] - b[1] for b in boxes]))
            bw_, bh_ = max(bw_, 4), max(bh_, 4)
            if bw_ >= W or bh_ >= H:
                continue
            dx = int(rng.integers(0, W - bw_))
            dy = int(rng.integers(0, H - bh_))
            # don't cover a real target
            if any(dx < b[2] and dx + bw_ > b[0] and dy < b[3] and dy + bh_ > b[1]
                   for b in boxes):
                continue
            apply_occlusion(img, dx, dy, dx + bw_, dy + bh_, args.frac,
                            args.mode, rng, boxes, foliage)

        cv2.imwrite(str(dst / "images" / img_p.name), img,
                    [cv2.IMWRITE_JPEG_QUALITY, 95])
        # labels copied verbatim — see label policy in the docstring
        if lbl_p.exists():
            shutil.copy(lbl_p, dst / "labels" / lbl_p.name)
        else:
            (dst / "labels" / f"{img_p.stem}.txt").write_text("")

        if i % 500 == 0:
            print(f"  {i}/{len(images)}")

    # Preserve the source class map rather than assuming single-class. Weitefeld
    # and the collected HPI data are multi-class; hardcoding nc:1 would silently
    # drop every class but the first.
    src_yaml = None
    for cand in (src / "data.yaml", src.parent / "data.yaml"):
        if cand.exists():
            src_yaml = cand
            break
    if src_yaml:
        body = src_yaml.read_text()
        keep = "\n".join(ln for ln in body.splitlines()
                         if not ln.startswith(("path:", "train:", "val:", "test:")))
        (dst / "data.yaml").write_text(
            f"path: {dst.resolve()}\ntrain: images\nval: images\ntest: images\n"
            f"{keep}\n")
    else:
        print("  ! no source data.yaml found — write one manually before training")

    achieved = [r["achieved_frac"] for r in log]
    meta = {
        "source": str(src), "mode": args.mode, "target_frac": args.frac,
        "frac_jitter": args.frac_jitter, "distractor_rate": args.distractor_rate,
        "seed": args.seed, "n_images": len(images), "n_instances": n_inst,
        "achieved_frac_mean": round(float(np.mean(achieved)), 4) if achieved else 0,
        "achieved_frac_std": round(float(np.std(achieved)), 4) if achieved else 0,
    }
    (dst / "occlusion_meta.json").write_text(json.dumps(meta, indent=2))
    (dst / "occlusion_log.json").write_text(json.dumps(log, indent=2))

    print(f"\n{len(images)} images, {n_inst} instances occluded")
    print(f"target {args.frac:.2f} -> achieved "
          f"{meta['achieved_frac_mean']:.3f} +/- {meta['achieved_frac_std']:.3f}")
    print(f"Wrote {dst}")
    print("Report the ACHIEVED fraction in the thesis. It tracks the target "
          "closely, but jitter and edge clipping shift it slightly and the "
          "per-instance log is your evidence that the buckets are what you "
          "claim they are.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--in", dest="inp", required=True,
                   help="split dir containing images/ and labels/")
    p.add_argument("--out", required=True)
    p.add_argument("--frac", type=float, required=True,
                   help="target fraction of BOX AREA to occlude, 0.0-0.95")
    p.add_argument("--frac-jitter", type=float, default=0.0,
                   help="relative stddev. Use 0 for frozen eval buckets.")
    p.add_argument("--mode", choices=["cutout", "blobs", "texture", "foliage"],
                   default="texture")
    p.add_argument("--foliage-dir", type=str)
    p.add_argument("--distractor-rate", type=float, default=0.0,
                   help="background occluders per target. Use ~1.0 for TRAINING "
                        "augmentation to prevent shortcut learning.")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    if a.mode == "foliage" and not a.foliage_dir:
        p.error("--mode foliage requires --foliage-dir containing RGBA PNGs")
    if not 0.0 <= a.frac <= 0.95:
        p.error("--frac must be in [0.0, 0.95]")
    run(a)


if __name__ == "__main__":
    main()
