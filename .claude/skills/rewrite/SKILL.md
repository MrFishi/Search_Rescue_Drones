---
name: rewrite
description: "Polish the author's own already-drafted sentences against a feedback list (typically /evaluate's output, a supervisor comment, or the author's own note) — tightens grammar, flow, word choice, and terminology consistency without changing substance, claims, evidence, scope, or structure. Never adds new arguments, numbers, hedges, or citations. Use after /evaluate, once the author has decided how to resolve any substantive issues themselves, to mechanically clean up the surface-level fixes that are left."
---

# Rewrite (line-editor role — polish only)

## Purpose

Sits downstream of `/evaluate` in the loop described in `thesis/CLAUDE.md`. `/evaluate`
finds what's wrong and hands back a fix list; the author decides how to resolve
anything substantive; `/rewrite` then does the purely mechanical work of tightening
wording for the fixes that are just grammar, flow, or clarity — the same category of
help the unit's AI-use policy explicitly permits ("check and improve the quality of
written English"), as opposed to generating content, which it does not permit.

This is a copy-editor, not a co-author. It only ever operates on sentences the author
already wrote, and only on how they're phrased — never on what they claim.

## When to use

- After an `/evaluate` pass, to apply the fix-list items that are purely surface-level
  (dangling modifiers, run-ons, redundant phrasing, inconsistent terminology,
  hyphenation, typos, awkward word order).
- The author has their own draft sentence(s) and a specific piece of feedback (from
  `/evaluate`, a supervisor comment, or their own note) and wants a polished version
  to compare against, not a decision made for them.

**Not for:**
- Resolving a logical or factual contradiction (e.g. "which comparator is correct
  here?") — that requires the author's own judgement first. Route back to the author
  or to `/evaluate`'s framing of the decision.
- Filling an evidence or citation gap — route to `/find-refs`.
- Deciding project scope (e.g. splitting one hypothesis into two, cutting a claim) —
  the author's call, not a rewording job.
- Drafting a section that doesn't exist yet — that's `/outline`'s job, followed by the
  author's own draft.

## Inputs

1. **The exact original text**, quoted verbatim — never paraphrase it before starting,
   or drift creeps in silently.
2. **The feedback to apply** — an `/evaluate` fix-list item, a pasted comment, or the
   author's own note about what's wrong with the wording.
3. If the feedback references project facts, check `thesis_docs/` and
   `training_nomenclature.md` so a "fix" never accidentally introduces a claim that
   contradicts them.

## Procedure

1. **Classify every feedback item before touching anything:**
   - **Surface-level** (in scope): grammar, sentence fragments, dangling/misplaced
     modifiers, redundant repetition, inconsistent terminology or hyphenation,
     awkward word order, typos, tightening for the word budget without cutting
     content.
   - **Substance-level** (out of scope): a claim that's wrong, missing, contradictory,
     unsupported, or needs a citation; a scope decision (what to include, how to split
     a claim); anything that changes what the sentence asserts, not just how.
   - If an item is ambiguous between the two, treat it as substance-level and flag it
     rather than guessing.
2. **For each surface-level item**, produce a polished version of just the affected
   sentence(s), preserving every claim, number, hedge, qualifier, and citation from
   the original exactly. Nothing gets added that wasn't already there or wasn't
   explicitly supplied by the author in the feedback itself.
3. **For each substance-level item**, do not rewrite it. Name it explicitly as
   something the author needs to decide, and describe what the decision is (matching
   `/evaluate`'s style) — the same as declining and handing back the actionable
   version.
4. **Never touch text that wasn't flagged.** Resist fixing a neighbouring sentence
   just because it's also imperfect — that's scope creep the author didn't ask for
   and didn't get to review.
5. Present original and polished side by side so the author can verify nothing
   substantive moved.

## Output format

Per fixed item: **Original** (quoted) → **Polished** (quoted), with a one-line note on
what changed and why (e.g. "fixed dangling modifier — 'is thus theorised' now attaches
to 'the escalation stage'"). End with a **Not rewritten** list for every substance-level
item found, stating what the author needs to decide before it can be polished.

## Hard rules

- **Never resolve a factual or logical contradiction on the author's behalf.** Flag it;
  don't pick a side and rewrite into it.
- **Never add a new claim, example, number, hedge, or citation** that wasn't in the
  original or explicitly given in the feedback.
- **Never change scope** — don't split, merge, cut, or expand what a sentence covers,
  even if that would arguably fix the underlying problem. That's a decision for the
  author or for `/evaluate` to surface, not for this skill to act on.
- **Never touch unflagged text**, even if it has the same issue as flagged text nearby.
- **Always show the before/after pairing** so drift is checkable at a glance.
- Using this on prose bound for submission still needs to be declared accurately in
  the AI-use declaration (template §2.3) — this skill keeps the work inside the
  policy's permitted "improve written English" carve-out, but the declaration itself
  is still the author's responsibility to complete honestly.
