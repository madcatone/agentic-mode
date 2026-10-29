# Code review canon — todo CLI

The local review checklist for this repo. The Standards axis of a review uses
this file as its primary list; generic smell lists come second.

## What failure looks like (per sensitive area)

- Persistence: it loses or mutates task state across a run boundary — what
  the user saved is not what the user gets back.
- Output: the listing prints a task under the wrong state or the wrong id —
  the display disagrees with the store.
- Errors: a bad input reaches the user as a traceback instead of a message.

## Rules

- R1: Persistent task state lives in `tasks.json` and nowhere else. Do not
  add side files, shadow stores, or a second source of truth for task state.
- R2: User-facing errors print an `error: ` prefix to stderr and exit
  non-zero. Tracebacks reaching the terminal are a violation.
