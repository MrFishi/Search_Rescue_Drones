# Thesis AI Setup — What's Here & Where It Goes

This bundle sets up the lean, four-layer AI workflow for the SAR drone thesis.

## The four layers

1. **Context (always on):** `CLAUDE.md` at the repo root. Loaded every session by both
   Claude Code and (as `AGENTS.md`) Codex. Holds project identity, environment facts,
   and the hard guardrails. This is what keeps all your AI up to date on the project.
2. **Heavy coding:** the **Superpowers** plugin (plan → test-first → review). Install
   instructions below. Use it for multi-file features, refactors, migrations.
3. **Quick coding:** raw Claude Code / Codex. No ceremony for small, well-scoped edits.
4. **Writing loop:** the three skills in `.claude/skills/` (`/outline`, `/evaluate`,
   `/find-refs`) plus `thesis/CLAUDE.md`, which defines the loop and the Opus-critic /
   Sonnet-companion model roles.

## Where each file goes (relative to `~/Documents/Search_Rescue_Drones`)

```
Search_Rescue_Drones/
├── CLAUDE.md                          ← from this bundle's CLAUDE.md
├── training_nomenclature.md           ← already in your repo, now wired into the
│                                          writing loop (model/run naming reference)
├── thesis_docs/                       ← already in your repo — project/method docs,
│                                          UNCHANGED, this bundle only reads from it
├── thesis/                            ← NEW, from this bundle — for WRITING inputs
│   ├── CLAUDE.md                      ← from this bundle's thesis/CLAUDE.md
│   ├── references.bib                 ← your Zotero (Better BibTeX) auto-export
│   ├── rubrics/                       ← drop your proposal marking rubric here
│   └── exemplars/                     ← drop a past high-scoring proposal here
└── .claude/
    └── skills/
        ├── README.md                  ← skills index
        ├── outline/SKILL.md
        ├── evaluate/SKILL.md
        ├── find-refs/SKILL.md
        └── humanizer/SKILL.md
```

**`thesis/` and `thesis_docs/` are different, both correct.** `thesis_docs/` is your
existing project/method documentation — leave it as is. `thesis/` (new) is where the
writing loop's inputs live: rubric, exemplar, bib, and the loop's own conventions file.

Paths actually confirmed against `git ls-files`, so the skills point at real files:
`vision/training/overfit_gates.md`, `results/runs.csv`, `simulation/sim_setup.README.md`,
and per-dataset `data/{raw,processed}/<dataset>/PROVENANCE.md` (five separate files,
not one). `training_nomenclature.md` sits at the repo root, not in `thesis_docs/`.

Then, so Codex reads the same context: `ln -s CLAUDE.md AGENTS.md` at the repo root.

## Before the writing loop works

- Set your **citation style** in `thesis/CLAUDE.md` (the one placeholder).
- Put the **proposal rubric** in `thesis/rubrics/` and a **high-scoring exemplar** in
  `thesis/exemplars/`. The skills read these files rather than hardcoding anything.
- First move: `/outline` on the introduction.

---

## Installing Superpowers (Claude Code)

Requires a recent Claude Code (2.0.13+). In an active Claude Code session:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

For it to activate across all projects, add the global flag:

```
/plugin install superpowers@superpowers-marketplace --global
```

Then **quit and restart** Claude Code. Verify with `/help` — you should see
`/superpowers:brainstorm`, `/superpowers:write-plan`, `/superpowers:execute-plan`.
If install errors with a schema-validation message, update Claude Code first
(`npm update -g @anthropic-ai/claude-code`) and retry.

Use it by describing substantial work; it auto-runs a brainstorm → plan → execute
flow. For a tiny edit, tell it to skip planning, or just use raw Claude Code.

---

## Installing Graphify (codebase knowledge graph)

Graphify maps your repo — code, docs, PDFs — into a queryable graph so Claude looks
up structure instead of grepping through files. Correct package name is `graphifyy`
(double-y on PyPI; the command it installs is `graphify`).

**Install (from the repo root):**

```bash
uv tool install graphifyy          # or: pipx install graphifyy
graphify install                   # registers the /graphify skill with Claude Code
```

If `graphify` isn't found right after, your shell's PATH doesn't have uv's tool bin
dir yet: run `uv tool update-shell` and open a new terminal.

**Build the graph**, from inside a Claude Code session in the repo:

```
/graphify .
```

This writes `graphify-out/` (`graph.html`, `GRAPH_REPORT.md`, `graph.json`). Skim
`GRAPH_REPORT.md` first — it surfaces god nodes, surprising cross-file links, and
suggested questions the graph is positioned to answer.

**Make Claude always consult it** (one-time, after the first build):

```bash
graphify claude install
```

This appends a section to your root `CLAUDE.md` and installs a `PreToolUse` hook
that nudges Claude toward `graphify query "..."` before it greps or reads files one
by one. It edits `CLAUDE.md` directly — you don't need to write anything yourself.

**Recommended `.graphifyignore`** (repo root) — your tracked `results/baselines/`
folder has PNG/JPG training curves and batch previews. Docs/PDFs/images all get
sent to your assistant's model for semantic extraction (code stays local, parsed by
tree-sitter, no API calls), so those images would burn calls for no benefit:

```
# .graphifyignore
results/**/*.png
results/**/*.jpg
```

Everything else large in your repo (`data/raw/`, `data/processed/` tiles,
`weights/*.pt`, ROS2 `build/`/`install`/`log`) is already git-ignored, and Graphify
respects `.gitignore` automatically — no extra exclusion needed there.

**Protect Claude Code's prompt cache** — add this to `.claudeignore` so
`graphify-out/` writes don't force a full context re-upload on every turn:

```
# .claudeignore
graph.json
graphify-out/
```

**Try it once built:**

```
/graphify query "how does the occlusion tool connect to the training configs?"
/graphify explain "heridal_to_yolo"
```

**Keeping it current:** run `graphify hook install` once — it rebuilds the graph
automatically on every `git commit` and branch switch (AST only, no API cost). After
`git pull`, run `graphify update .` to catch teammate changes (there's only one of
you here, but this also covers pulling your own commits made from the other machine).

Since code is parsed 100% locally with no API key, this works even before you
connect any model key — interactive queries inside Claude Code use your existing
subscription automatically.

---

## Installing a downloaded skill zip (e.g. humanizer)

A skill downloaded from GitHub as `something-main.zip` unzips to a folder that
usually contains a `SKILL.md` (sometimes nested one level down). To install it:

```bash
# from your repo root
unzip ~/Downloads/humanizer-main.zip -d /tmp/humanizer
# find the folder that directly contains SKILL.md
find /tmp/humanizer -name SKILL.md
# copy THAT folder in, renamed to the skill's name:
cp -r /tmp/humanizer/humanizer-main .claude/skills/humanizer
```

The target must end up as `.claude/skills/humanizer/SKILL.md`. Open the `SKILL.md`
and check the `name:` in the frontmatter matches the folder (`humanizer`); fix it if
the zip used a different name. Restart Claude Code and it'll be available as
`/humanizer` (or auto-loaded when its description matches).

**Integrity note:** a humanizer that removes AI-writing tells is a legitimate editing
aid on *your own* prose — it pairs fine with this loop, which is coach-and-critic, not
ghostwriter. Don't use it to disguise AI-generated text as your own; that's what
academic-integrity rules exist to catch. Keep the writing yours and use it to polish.
