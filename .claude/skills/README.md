# Skills Index

Quick reference for the skills in this directory. Each skill lives in its own folder
as `<name>/SKILL.md` and is invoked by its name (e.g. `/outline`). Claude also loads a
skill automatically when a task matches its description.

> When you add a skill, add a row below.

## Active — writing loop

| Invoke | What it does |
|---|---|
| `/outline` | Dot-point writing plan for a section, built from the rubric, current project docs, and an exemplar. Planning only — never prose. *(run on Opus)* |
| `/evaluate` | Grades a draft against the marking rubric and returns a prioritised, mark-raising fix list. Flags unsupported claims, missing citations, and inconsistencies with the project docs. Never rewrites your prose. *(run on Opus)* |
| `/find-refs` | Finds supporting references for a claim or section and proposes exactly where to place citations. Checks `references.bib`/Zotero first. Never invents a citation, DOI, or key. |
| `/humanizer` | Rewrites AI-sounding prose so it reads like you wrote it, without changing meaning. Third-party skill (blader/humanizer, MIT), based on Wikipedia's "Signs of AI writing." Use to polish your own drafts — not to launder AI-generated text. |

## Drafted, not active

These were written but are kept out of the active set for now (some are better as code,
some are premature). Add them when the trigger actually recurs:

`lit-review`, `presentation`, `log-run`, `overfit-gate`, `verify-seal`,
`occlusion-sweep`, `jetson-bench`, `doc-sync`, plus suggested `pre-register` and
`supervisor-update`. Note: `verify-seal` and `log-run` are better implemented as an
assert/hook and a small script respectively, rather than as skills.

## Adding a new skill

1. Create a folder: `.claude/skills/<new-name>/`
2. Add `SKILL.md` inside it with frontmatter:
   ```
   ---
   name: <new-name>
   description: "What it does + when to use it. This line is how Claude decides to load it, so make the trigger clear."
   ---
   ```
3. Add a row to the table above using: `| \`/<new-name>\` | One-line description. |`
