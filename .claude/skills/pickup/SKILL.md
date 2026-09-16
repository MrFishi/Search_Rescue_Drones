---
name: pickup
description: Continue work recorded in a handoff note, found by session name. Use when the user says continue, pick up or resume a named session, including one started on the other machine.
argument-hint: "<session name or slug>"
arguments: [name]
---

# Pick up a handoff

Requested: "$name"

## Notes, newest first (file | session | machine | created | status)

!`bash "${CLAUDE_SKILL_DIR}/list.sh"`

## This machine now

!`bash "${CLAUDE_SKILL_DIR}/../handoff/state.sh" "${CLAUDE_SESSION_ID}"`

## Steps

1. **Match** the request against session names and slugs, case-insensitive, partial matches allowed; prefer `status: open`. One match: use it. Several: list them and ask. None: show the newest open notes and ask. Nothing requested: offer the newest open note and confirm first.
2. **Read** the note in full, then its "Read first" pointers.
3. **Reconcile** the note with this machine: `repo_ref` against the current ref (behind means `git pull` first, and check the note's `machine` isn't this one with unpushed work still sitting on the other side), uncommitted files the note lists that are absent here (they are still on the note's machine, uncommitted).
4. **Summarise** in at most ten lines: the goal, where it stopped, any drift found in step 3, the next step.
5. **Ask before acting** on the next steps unless the user already said to go ahead. When the thread is finished, set the note's `status: done`.
