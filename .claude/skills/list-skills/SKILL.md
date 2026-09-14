---
name: list-skills
description: "List every skill currently available to the user — both repo-local skills in .claude/skills/ and global/built-in skills injected into the session. Use whenever the user asks what skills they have, what's available, or to enumerate/inventory skills."
---

# List Skills

## Purpose

Give the user a single, accurate inventory of every skill they can invoke right
now, split into the two sources that actually exist:

1. **Repo-local skills** — live on disk in this repo at `.claude/skills/<name>/SKILL.md`.
   Discoverable by reading the filesystem directly.
2. **Global/built-in skills** — bundled with the harness (e.g. `code-review`,
   `dataviz`, `design`, `update-config`, `init`, etc.). These are NOT on disk
   anywhere in this repo or a user-writable global skills folder — they are
   injected into the conversation via the "Available skills" system-reminder
   listing. Do not try to find them with `find`/`ls`; read them from that
   listing already present in context for this turn.

## Steps

1. **Enumerate repo-local skills.** Run:
   ```
   find .claude/skills -maxdepth 2 -name SKILL.md
   ```
   For each result, read the YAML frontmatter (`name:` and `description:`) —
   do not read the whole body, the frontmatter is enough for a listing.

2. **Enumerate global skills.** Use the skill names + one-line descriptions
   already present in the current turn's "Available skills" system-reminder.
   Do not guess or invent names — only list what actually appears there. If
   for some reason no such listing is present in context, say so explicitly
   rather than fabricating one.

3. **De-duplicate.** If a skill name appears in both places (a repo skill that
   shadows or matches a global one), list it once under repo-local and note
   the overlap.

4. **Present as two short lists** (repo-local first, since those are specific
   to this project), each as `name` — `description`, plus a total count per
   group and a combined total. Keep descriptions to one line each; do not
   paste full SKILL.md bodies.

## Notes

- This skill only reads and reports — it never edits, creates, or removes any
  skill file.
- Counts will drift as skills are added/removed from `.claude/skills/` or as
  the harness's built-in set changes between sessions — always re-enumerate
  live rather than trusting a remembered count.
