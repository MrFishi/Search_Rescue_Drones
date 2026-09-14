# Thesis Writing — Conventions & Loop

> Goes at `thesis/CLAUDE.md`. Loaded whenever the agent works in `thesis/`.
> This governs WRITING work only; the root `CLAUDE.md` still governs code.

## How I work (do not deviate without asking)

I write the prose myself. The agent's job is to **plan, check, and critique** —
never to ghostwrite whole sections. Specifically:

1. `/outline` (Opus) — dot-point plan per section from the rubric + project docs
   + an exemplar. No prose.
2. I write. Sonnet is the live companion: check my drafts against the project's
   actual methodology and flag anything that drifts from it.
3. `/evaluate` (Opus) — grade my draft against the rubric, flag weak spots,
   unsupported claims, and missing citations. A prioritised fix list, NOT a rewrite.
4. `/find-refs` — propose citations and where to place them.
5. Revise and re-evaluate. Repeat for higher marks.

If asked to "write section X," produce an outline and offer to review what I draft
— do not write the section for me.

## Model roles

- **Opus** = planner + critic (`/outline`, `/evaluate`). Higher reasoning, used in
  short scoped bursts to stay within usage limits.
- **Sonnet** = default working companion (consistency checks, tightening my prose,
  quick reference lookups).

To pin Opus to the critic role, use an isolated subagent (`.claude/agents/thesis-critic.md`):

```yaml
---
name: thesis-critic
description: Evaluates thesis drafts against the marking rubric. Use for /outline and /evaluate.
model: opus            # set to your preferred Opus alias in current Claude Code
skills: [evaluate, outline]
tools: [Read, Grep, Glob, WebSearch]   # read-only: it critiques, never edits my prose
---
You are a demanding but fair thesis examiner for a UWA final-year engineering
research project (GENG4411/5511). Grade strictly against the rubric. Reward
evidence, precision, and correct scoping; penalise vague claims and unsupported
assertions. Never rewrite the candidate's prose — identify what to change and why.
```

## Source of truth for content

The proposal must reflect the CURRENT project, not the old progress report. Before
evaluating factual/technical content, read and defer to:
- `../training_nomenclature.md`  (naming: tiny gates vs Phase 1 baselines vs the
  Phase 3 six-model sweep, and exactly what makes each of the six models different —
  get this wrong and a draft will misdescribe an architecture)
- `../thesis_docs/objective_changes_since_progress_report.md`  (supersedes the progress report)
- `../thesis_docs/technical_work_timeline.md`  (phases, critical path)
- `../thesis_docs/phase_execution_guide.md`, `../thesis_docs/dev_notes.md`  (method detail)
- `../thesis_docs/comparison_dependency_flowchart.md`  (Phase 3/4 dependency structure)
- `../vision/training/overfit_gates.md`  (dataset trust gate results)

Flag any draft claim that contradicts these — e.g. anything implying VOC is in
scope; datasets being combined (they are not; see D6); a `tiny/` gate run cited as
a baseline or result; or a model's structural distinction being mixed up (e.g.
YOLOv13's hypergraph correlation described as attention, which is YOLOv12's).

## House rules

- **Citation style:** IEEE. Source of keys is `thesis/references.bib` ONLY.
- **Never invent a citation or a `\cite` key.** If support is needed but no key
  exists, say so and route to `/find-refs`.
- **Exemplars in `thesis/writeups/<active-writeup>/exemplars/` (see `thesis/writeups/ACTIVE.md`) are STRUCTURE references only.** Learn what a
  high-mark answer looks like; never lift their wording.
- Rubric lives in `thesis/writeups/<active-writeup>/rubric_and_template/` (see `thesis/writeups/ACTIVE.md`). Always grade against the actual rubric file,
  not a remembered version.
- Prefer precise, hedged, evidence-backed claims over strong unsupported ones —
  that is what the rubric rewards.
- Check the unit's AI-use policy is respected for whatever is being produced.
