# TICKET-331 — done state lost between runs

Type: bug-fix
Component: cli

## Symptom

After `todo done 1`, running `todo list` again (a fresh process) shows task 1
as not done. The done mark does not survive a run boundary.

## Acceptance criteria

- AC1: After `todo done <id>`, later runs must still report the task as done
  (`todo list --all` shows `[x]`); the mark survives process restarts.
- AC2: Plain `todo list` hides done tasks; `todo list --all` lists them with a
  `[x]` marker.
- AC3: Task ids stay stable across save/load: a task keeps the id it was
  assigned at `add` time, across restarts and `rm` of other tasks.
- AC4: `todo done` with an unknown id prints `error: unknown task id <n>` to
  stderr and exits with code 1 — no traceback.

## Repro

    todo add "write report"
    todo done 1
    todo list --all      # task 1 shows as not done -- the bug
