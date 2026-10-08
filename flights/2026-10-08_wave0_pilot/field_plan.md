# Wave 0 pilot: field plan, 2026-10-08

Update after the session: the slope check was dropped and the camera angle is now fixed at 45°;
see `thesis_docs/collection_plan.md` 3.2. This sheet is kept as the record of what was planned.

Props: bottles, sunglasses, backpacks, 4 people. Level ground, take off at the same level
as the scene, so the app's height = height above ground. Gimbal angles: **90° = straight
down, 45° = halfway down**. Photos record height, angle and GPS themselves, so you only
need to write down scene names, what you placed and where.

Priority if light runs out: 1 sweep, 2 scenes, 3 passes and slope. Sunset about 18:10.

## 0. Before takeoff (10 min)

- [ ] Video captions ON (needed for the .SRT file). 4K, 60 fps.
- [ ] Batteries charged, SD card space checked. Note wind (little, some, strong).
- [ ] Measure each prop in cm and write it down: backpack (length x width), bottle
      (height, diameter), sunglasses (width across), each person lying (length).
- [ ] Reference scene on open level ground, 1 to 1.5 m between items, tape measure along
      them: 1 backpack, 2 bottles, 2 sunglasses. Two people nearby (1 lying, 1 sitting),
      5 m away. Do not move this scene until the sweep is done.

## 1. Height sweep (battery 1, about 12 min)

Same scene, one still at each angle at each height. At 45° the camera looks ahead, so
**hover back from the scene by the same distance as your height** (5 m high = 5 m back).
At 90° hover directly over the scene.

- 3 m:  45° x1, 90° x1
- 5 m:  45° x1, 90° x1
- 8 m:  45° x1, 90° x1
- 10 m: 45° x1, 90° x1
- 15 m: 45° x1, 90° x1
- 20 m: 45° x1, 90° x1
- 30 m: 45° x1, 90° x1

Extras: at 3 m take a still, hover 10 s, take another (did rotor wash move anything?). At
5 m and 10 m take a second 45° still from the opposite side (turn around, same distance).
Land at the low-battery warning. Note flight time and battery % at landing.

## 2. Pilot scenes (battery 2 and start of 3, about 25 min)

Per scene, 8 stills:
- Side A: 45° at 5 m, 10 m, 15 m (3 stills; hover back from the scene by your height).
- Side B, the opposite side: 45° at 5 m, 10 m, 15 m (3 stills).
- Straight down over the scene: 90° at 5 m and 10 m (2 stills).

Every time you move an object it is a new placement. Never shoot the same layout twice.

- **T1 exposed:** backpack, 2 bottles, sunglasses on open ground, nothing covering them.
- **T2 partial:** same four items in new spots, about half hidden under a bush or branch.
- **T3 deep:** same four items in new spots under canopy, mostly hidden from above.
- **T4 mixed (optional):** 2 backpacks, bottle, sunglasses, mixed exposure.
- **P1 people:** all 4 people at once, 5 m or more apart, 4 poses: lying on back, sitting
  cross-legged, standing, crouching.
- **P2 people:** 4 other poses: curled on side, lying face down, sitting against a bush,
  standing in shade. Different clothing from each other where possible.
- **C1 with objects:** one person sitting, backpack 2 m away, bottle 1 m away.
- **N negatives:** 10 stills, 45° at 10 m, of empty bush, logs, rocks, dark shadows.

For each scene write: scene name, time, what is where, how hidden (exposed, half, deep).

## 3. Slow passes and slope check (battery 3, about 12 min)

- [ ] **2 slow video passes**, 45° down, 8 m height, about 60 s each, in a straight line
      over the T2 / T3 area. Go as slowly and steadily as you can, at or under 2 m/s (the
      app shows speed). Note the speed you used.
- [ ] **Slope check, if you have a slope:** put a backpack at the bottom, middle and top
      (a few metres of rise). Take off at the bottom. Hold a fixed height of **8 m** on the
      app, hover over each backpack, take one 90° still each. Note the rise by pacing or a
      phone altimeter. A bigger backpack at the top means true height is less than the app says.

## 4. After flying

1. Offload to the card under `thesis/wave0_pilot/2026-10-08/` into `calibration/`,
   `trained/`, `person/`, `negatives/`, `video/`. Rename with height and angle for the sweep.
2. From `vision/`: `uv run python telemetry/extract.py <footage> --out
   ../flights/2026-10-08_wave0_pilot --check`, then `plot.py`.
3. Send me the stills (or your pixel measurements) and your notes. I will build the
   pixel-size table per class and height, set the bands, and update the exit criteria.

## Log

| Scene | Time | What is where | Hidden (exposed/half/deep) | Notes |
|---|---|---|---|---|
| | | | | |

Also: flight time per battery, wind, anything that blew around at 3 m, speed of the passes.
