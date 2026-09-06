Any file/dir in this github that have tiny associated with them are throwaway
sanity-check subsets, not real training or evaluation data. Each `tiny/` folder
holds a small handful of tiles (20, by convention) copied out of a real
processed dataset's `train/` split, with `train` and `val` in the matching
`*_tiny.yaml` config both pointing at that same folder. The point is to prove
the data pipeline works end to end (correct images, correct labels, correct
class indices) before spending real time on a full run: a healthy pipeline
should trivially memorise 20 images and clear mAP@50 > 0.95 in minutes, so a
failure here means something upstream is broken, not that the model is weak.

Nothing downstream reads from a `tiny/` folder or a `*_tiny.yaml` config once
its gate has passed. They are not part of Baseline A/B, Phase 3, or any
reported result, and can be safely deleted or left in place as a record that
the check was run.

Current instances:
- `data/processed/heridal_yolo_v1/tiny/` + `vision/training/configs/heridal_tiny.yaml`
- `data/processed/weitefeld_yolo_v1/tiny/` + `vision/training/configs/weitefeld_tiny.yaml`



Overfit gate run on yolo11n for both HERIDAL and Weitefeld. Smallest and fastest model and used to prove data pipeline works, not a real contendor for anything downstream. 

For Phase 1, two baselines are being trained, both on yolo11s, one size up from the gate model. Baseline A is HERIDAL, person-only. Baseline B is Weitefeld, multi-class. I picked yolo11s for these specifically because these numbers actually get reported and compared against the literature, so they need to mean something, not just prove the plumbing works.


Then in Phase 3, the real architecture sweep is run, six candidates, deliberately chosen to span four different structural approaches so I'm not just comparing minor variants of the same idea:

Model choices across this project
#	Model	What makes it structurally different	Cost
1	YOLO11s	Plain CNN, local convolution. This is my Phase 1 continuity point, the reference everything else has to beat	                    Free

2	YOLO26s	Edge-optimized CNN, deliberately stripped down (no DFL, no NMS step), with an optional extra small-object detection head	        Free

3	YOLOv12s	A CNN with self-attention bolted in, attention only within local regions, not a full transformer	                        Free

4	YOLOv13s	CNN plus a hypergraph mechanism that lets scattered, non-adjacent regions of the image correlate directly, I think this one's especially relevant given how much of my problem is partial occlusion	    Moderate effort

5	RF-DETR	A genuine full transformer detector, and it's the one candidate on a different license (Apache-2.0 instead of AGPL), worth having as a fallback if licensing ever becomes an issue	                        Moderate effort

6	D-FINE-S	Also a transformer, DETR-family, but built specifically for tighter, more precise box localization, which matters most for exactly the small targets I care about	                                Moderate effort


From those six, only the top two, ranked by mAP but only counting ones that actually hit real-time latency and memory limits on the Jetson, get carried forward into my A0/A2 head comparison.