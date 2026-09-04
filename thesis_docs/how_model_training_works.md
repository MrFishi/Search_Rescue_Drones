# How model training works

A short, exam-ready explanation aimed at your pipeline: YOLO detectors, HERIDAL /
Weitefeld / your own bush data, tiling, and the Phase 3 sweep. Each section ends with
the marker question you should be ready for. Glossary at the end.

---

## The one-paragraph version

A detector is a function that takes an image and outputs boxes with class labels and
confidence scores. It has millions of internal numbers called weights. Training nudges
those numbers, over and over, so the outputs move closer to your labels, measured by a
loss and driven by gradient descent. You never hand-write "a backpack has straps." You
show thousands of labelled examples and let the optimiser find weights that produce
correct outputs. The model does not understand anything; it finds patterns that
correlate with your labels. That is why a leaked split or bad tiling quietly produces
numbers that look good and mean nothing.

---

## Data splits

You divide data into three piles. Train is what the weights are updated on. Validation
is checked during training to spot overfitting and to make decisions (learning rate,
when to stop), but no weight update touches it. Test is looked at once, at the very
end, and shapes nothing, so it is your honest estimate of performance on new data.

Overfitting is the core risk: a model with millions of weights can memorise the
training set and fail on anything new. You catch it when training accuracy keeps
rising while validation flattens or drops, and you stop (early stopping).

The hard part is not the ratio, it is what you split on. Random per-image splits leak
when near-duplicates land on both sides. So you split on the true unit of independence:
HERIDAL by source photo (all its tiles stay together), Weitefeld by physical finding
(one tarp shot 85 times stays in one split), your bush data by placement or site.

Marker Q: *Why not split randomly?* Near-duplicate images would leak across the split
and inflate the test score without reflecting real generalisation. So I split on the
unit of independence, not the individual image.

---

## Tiling

YOLO resizes every input to a fixed size, say 1024x1024. HERIDAL photos are 4000x3000
and Weitefeld is 8416x6032, so feeding a whole frame in shrinks a small person to a
few pixels, below what is recognisable. Tiling cuts the big frame into overlapping
crops first, so a target stays large inside its own tile. The converter uses 20
percent overlap so boundary objects land whole in at least one tile, and drops any tile
where less than 30 percent of a clipped box survives, because a sliver box or a missing
label both teach the model something false.

Two separate moments: the converter tiles once to build the training set, while SAHI
tiles on the fly at evaluation and stitches detections back to full-frame coordinates,
which tests real deployment conditions.

Marker Q: *Why tile?* Fixed-input detectors shrink large images so far that small
targets vanish. Tiling keeps them large enough to detect.

---

## Inside the model: backbone, neck, head

The backbone extracts visual features from the raw image, from edges up to object
parts, at several scales. It is the expensive part and the transferable part. The neck
merges those multi-scale features so objects of different sizes are handled together.
The head produces the actual output, one slot per class you train.

This structure explains your Phase 3 options. A0 is one head predicting all classes.
A2 shares the backbone and neck but splits into two heads, one for person and one for
the HPI classes, so the rare-class signal can be weighted up without the common person
class drowning it out, at almost no extra inference cost since the backbone runs once.
A2b is two full separate models, which roughly doubles compute, so it is the stretch
option.

Marker Q: *Why does A2 barely cost more than A0?* The backbone is shared and runs once.
The second head is a small branch, not a second network. It targets class imbalance.

---

## Weights and pretraining

Weights are the learnable numbers. They start either random (the model knows nothing
and needs huge data) or pretrained. You use pretrained: COCO weights already encode
general features like edges and shapes, and fine-tuning continues training them on your
data so they specialise to aerial bush occlusion. That is what `yolo11s.pt` and similar
files are. Training from scratch is not defensible here because your bush data (about 40
placements per class) is far too small to learn general features from nothing. Your D7
experiment just tests whether Weitefeld-pretrained beats COCO-pretrained as the start.

Marker Q: *Why start from COCO not random?* COCO weights already hold general visual
features. My dataset is too small to learn those from scratch, so fine-tuning is far
more data-efficient.

---

## The training loop

The training set is cut into batches (yours is 8 images). One epoch is one full pass
through all batches; you run 150. Each step is: forward pass produces predictions, the
loss measures how wrong they are against the labels (box, classification, and
objectness terms combined), backpropagation computes for every weight which direction
reduces loss, and the optimiser (AdamW) nudges each weight by a small step. The
learning rate (`lr0=0.001`) sets the step size: too high overshoots, too low crawls.
Validation is checked each epoch, and you keep the best checkpoint, not the last one,
because later epochs can overfit.

Marker Q: *Walk me through one step.* Forward pass, compute loss against labels,
backprop the gradient for every weight, optimiser updates the weights to reduce loss.

---

## Augmentation

Each training image is randomly modified every time it is shown (flip, rotate, scale,
brightness), so the model never sees the exact same image twice and cannot just
memorise. Yours are chosen for aerial data: full rotation and vertical flips because
aerial imagery has no fixed up, scale jitter for altitude variation, brightness jitter
for sun versus canopy shadow. Distractor pasting adds occluders to background as well
as targets, so the model cannot learn the shortcut "that occluder texture means
something is hidden." Augmentation is training only; you never augment val or test.

Marker Q: *Do you augment the test set?* No. Augmentation is training-only, otherwise
the evaluation stops measuring performance on real images.

---

## Evaluation

IoU is overlap area over combined area of a predicted and true box; a detection counts
if IoU clears a threshold, usually 0.5. Precision is the fraction of detections that
are correct; recall is the fraction of real targets found. They trade off with the
confidence threshold, and for SAR a miss is worse than a false alarm, so a
recall-leaning operating point is defensible. mAP is the single-number summary:
mAP@50 uses IoU 0.5, mAP@50-95 averages stricter thresholds and rewards tighter boxes.

Two project-specific points. You report per-class, not just aggregate, because a model
can score a good average on the common person class while scoring near zero on rare HPI
classes, which is the whole research question. And you add a centre-distance metric
because on tiny targets a near-correct box can fall below IoU 0.5 and be scored a miss
even though it clearly located the person; report it as a complement to mAP, not a
replacement.

Marker Q: *Why per-class rather than aggregate mAP?* Aggregate can be carried by the
common class and hide near-zero performance on the rare HPI classes I actually care
about.

---

## Your biggest risk: overfitting

Underfitting is a model too simple, where train and val are both poor. Overfitting is a
model that fits training noise, where train is strong but val lags. Yours is
overfitting, because a small dataset plus a large pretrained model is the classic
setup. Every defence in your pipeline points at this: split by placement, heavy
augmentation, weight decay, keep the best val checkpoint, and the overfit gate before
real runs. Raise this yourself in a viva rather than being caught on it.

Marker Q: *Which is your bigger risk and how do you mitigate it?* Overfitting, because
the bush dataset is small. I mitigate with placement-level splits, augmentation, weight
decay, early stopping, and an overfit gate.

---

## Why YOLO, and getting onto the Jetson

Two-stage detectors like Faster R-CNN are accurate but slower. One-stage detectors like
YOLO predict in a single pass, which suits real-time inference on the Orin Nano within
a power budget, and the family has strong tooling, clean TensorRT export, and a large
SAR literature for comparison. The Phase 3 sweep tests this rather than assuming it.

The trained checkpoint is not what runs on the drone. You export it to ONNX, compile a
TensorRT engine for the Orin, and quantise (FP16) to save memory and time, then
re-measure accuracy, latency, and power on-device, since Phase 3 selection depends on
on-device numbers, not accuracy alone. P1.7 rehearses this whole export path on HERIDAL
first so Phase 3 is not where you first meet a TensorRT quirk.

Marker Q: *Why YOLO not Faster R-CNN?* One-stage single-pass inference suits real-time,
on-device, power-limited deployment on the Orin, and the sweep tests the choice rather
than assuming it.

---

## Glossary

- Backbone: feature-extracting body of the network; expensive and transferable.
- Backpropagation: computes, for every weight, which direction reduces the loss.
- Batch / epoch: a group of images processed together / one full pass over the set.
- Checkpoint: a saved snapshot of the weights.
- Fine-tuning: continuing to train a pretrained model on your own data.
- Head: output layers producing boxes and class scores.
- IoU: overlap over combined area of two boxes; decides if a detection counts.
- Leakage: test information reaching training, inflating results.
- Loss: single number for how wrong predictions are; training minimises it.
- mAP: mean Average Precision across classes; @50 vs @50-95 are IoU thresholds.
- Neck: merges multi-scale backbone features (FPN, PANet).
- Optimiser / learning rate: updates weights from the gradient / the step size.
- Overfitting vs underfitting: fitting training noise vs too simple to fit at all.
- Precision / recall: fraction of detections correct / fraction of targets found.
- Pretrained weights: weights learned first on a large dataset (COCO).
- Quantisation: lower weight precision (FP16) for speed and memory, small accuracy cost.
- SAHI: tiling at evaluation on full frames, merged back to full-frame coordinates.
- TensorRT: NVIDIA's optimised inference runtime, the format the Orin runs.
- Tiling: cutting large images into overlapping crops so small objects stay detectable.
- Unit of independence: what you split on (photo, finding, placement), not the image.
- Weights: the learnable numbers inside the network.