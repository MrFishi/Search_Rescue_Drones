# HPI Taxonomy and Held-Out Split (P0.2)

**Status: class list locked 2026-10-06.** Per-class annotation protocol and
instance-count targets still to be worked through (see Section 4 — TODO).
This defines the primary contribution and the headline Phase 4 result. Per
CLAUDE.md HARD RULE 1/3, this list is fixed before annotation starts; changing
it afterward needs the same "Ask before" sign-off as the other HARD RULES.

This doc is the source the eventual thesis appendix ("Dataset and Taxonomy
Protocol") gets written from.

---

## 1. Class list — three tiers

| Tier | Classes | Role |
|---|---|---|
| Primary | `person` | Baseline, comparability to HERIDAL/Weitefeld literature |
| HPI-trained | `backpack`, `water_bottle`, `footwear`, `clothing_item`, `sunglasses`, `flashlight_headlamp` | Trained in A0/A2, the main HPI result |
| HPI-heldout | `trail_marker_tape`, `discarded_gear`, `campfire_remains`, `emergency_blanket` | **Never trained.** Reserved for the D-arm and VLM evaluation |

Selection was driven by **replicability**: every class above can be staged
with real physical variety from household items (clothing closet, footwear
collection, sunglasses, backpacks/duffels) or cheap reusable prop kits
(charcoal/ash for `campfire_remains`, a multi-pack of mylar blankets for
`emergency_blanket`), across the ≥5 sessions / ≥3 sites the instance-count
targets (Section 4, TODO) will require.

`clothing_item` deliberately absorbs gloves and hats/caps rather than giving
them their own classes — same reasoning as the "cut classes rather than
accept thin ones" rule below: three distinct wearable-accessory classes with
thin counts each is worse than one well-populated `clothing_item` class.

## 2. Explicitly excluded, with reasoning on record

**`footprint`/`footsteps`** — fails on two independent grounds, not staging
difficulty:
- **Collectability:** footprints only register a visible impression on
  specific substrates (soft dirt, mud, sand, snow). The target terrain for
  this drone is dense bush/forest floor (leaf litter, grass, rock) where a
  footstep usually leaves no visible mark at all — you can't manufacture
  instances across sessions/sites the way you can drop a backpack anywhere.
- **Visual consistency at altitude:** a footprint is a shallow 2D depression,
  not a 3D object with volume/colour contrast. From 5–10m up it's only
  visible under the right raking light; wrong sun angle or overcast sky and
  it's indistinguishable from any other patch of disturbed ground. That
  ambiguity would fail the inter-annotator agreement check (phase_execution_
  guide.md "Run an inter-annotator agreement check").
- Reference: `phase_execution_guide.md:231` already flags this for the same
  reason in the original P0.2 draft.

**`pocket_knife`** — same underlying failure as footprints: at search
altitude it falls below the "recognisable silhouette, not a speck" bar every
other class protocol is built around, closed or open.

Both are candidates for a later **stretch ablation only** (see Section 3),
never the primary locked taxonomy or the headline Phase 4 result.

## 3. Planned stretch ablation (time-permitting, after the primary result exists)

Once the primary held-out result (Section 1's 4 held-out classes, never
trained) is recorded, an optional follow-up experiment can swap classes
between tiers to see which perform better trained vs. held-out — e.g. train
on `emergency_blanket` and see if accuracy improves over its held-out
baseline, or test `footprint`/`pocket_knife` as a curiosity despite the
issues above. This must never replace or retroactively alter the primary
held-out result — see CLAUDE.md HARD RULE 3 and the discussion in this
project's chat history on why swapping after seeing held-out results would
be p-hacking the headline claim.

## 4. TODO — still to work through together

- Per-class annotation protocol (positive definition, box tightness
  convention, minimum visible size, ambiguous-case handling, photo example)
  for each of the 11 classes above.
- Instance count targets per class (placements vs. boxes vs. sessions/sites),
  informed by `phase_execution_guide.md` P2.6's correction to the original
  P0.2 targets.
- Downstream dependency notes for P0.6 (CVAT label set) and P1.4/P1.5/P1.6
  (held-out seal assert).
