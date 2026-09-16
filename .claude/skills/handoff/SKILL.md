---
name: handoff
description: Write a handoff note, keyed by session name, so this work continues in a fresh session or on the other machine.
disable-model-invocation: true
argument-hint: "[session name]"
arguments: [name]
---

# Handoff

## Facts

!`bash "${CLAUDE_SKILL_DIR}/state.sh" "${CLAUDE_SESSION_ID}"`

Name passed to this command: "$name"

Existing notes:

!`bash "${CLAUDE_SKILL_DIR}/../pickup/list.sh"`

## Steps

1. **Session name.** Use the first that exists: the name passed to this command, `rename_name`, `generated_title`. Make a slug of it: lowercase, hyphens, at most six words. If only `generated_title` exists, tell the user and suggest `/rename <name>` so the session picker and the note agree.
2. **Write** `.claude/handoffs/<filename_stamp>_<slug>.md`:

   ```markdown
   ---
   session_name: "<name as shown to the user>"
   slug: <slug>
   session_id: <session_id>
   machine: <machine>
   created: <now>
   repo_ref: <branch @ sha>
   status: open
   supersedes: <earlier note's filename, if any>
   ---
   ```

   Then these sections, facts only, each bullet checkable:
   - **Goal**: what this thread of work is for, in one or two lines.
   - **Done**: with evidence (command and result, files changed).
   - **In flight**: exact state of anything half done; each uncommitted file and why it is uncommitted.
   - **Decisions**: what was decided, and whether it's recorded anywhere else in the repo (e.g. `thesis_docs/`, `CLAUDE.md`) yet.
   - **Open questions**: what waits on the user, a person or data.
   - **Next steps**: ordered and runnable.
   - **Gotchas**: what surprised this session and would bite the next.
   - **Read first**: at most eight `path:line` pointers.

   At most 80 lines. No secrets, no pasted logs.
3. If an existing note has the same slug and `status: open`, set its `status: superseded`.
4. **Don't commit automatically.** Tell the user, briefly:
   - the note's path and the session name to use;
   - any other uncommitted files in the repo stay on this machine until committed and pushed;
   - to carry the note to the other machine: `git add .claude/handoffs && git commit -m "handoff: <slug>" && git push`, then on the other machine `git pull` and, in a new session, `/pickup <session name>`.
