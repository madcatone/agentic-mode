# todo — User Guide

The observable surface of the `todo` CLI: its commands, flags, output, and
failure messages. Each behavior cites the `TODO-NNN` requirement it satisfies.

## Purpose

`todo` is a one-shot task tracker: each invocation runs a single subcommand
against a JSON store and exits. It is standalone — it shares no state with any
other tool and needs nothing beyond a Python 3 interpreter.

## Choosing the Store

The task store path is resolved in this order (TODO-001):

1. `--store <path>` if given.
2. the `TODO_STORE` environment variable if set.
3. `tasks.json` in the current directory.

```bash
python3 todo.py --store work.json add "review the PR"
TODO_STORE=home.json python3 todo.py list
```

## Commands

```bash
python3 todo.py add "buy milk"      # TODO-002
python3 todo.py list                # TODO-003 — open tasks only
python3 todo.py list --all          # TODO-003 — include completed
python3 todo.py done 2              # TODO-004
python3 todo.py remove 2            # TODO-005
```

## Command Reference

| Command | Effect | Requirement |
| --- | --- | --- |
| `add <text>` | Append a task; print its assigned id. | TODO-002 |
| `list` | Print open tasks. | TODO-003 |
| `list --all` | Print open and completed tasks. | TODO-003 |
| `done <id>` | Mark the task complete. | TODO-004 |
| `remove <id>` | Delete the task. | TODO-005 |

## Output Format

`list` prints one task per line: `[ ]` for open, `[x]` for done, then `#id` and
the text. With no matching tasks it prints `(no tasks)`.

```text
[ ] #1 buy milk
[x] #2 review the PR
```

## Troubleshooting

- **`no such task: #N`** — `done`/`remove` were given an id that is not in the
  store. Run `python3 todo.py list --all` to see the live ids (TODO-004, TODO-005).
- **Empty output / `(no tasks)`** — the store resolved to a different path than
  you expected. Check `--store` and `TODO_STORE` (TODO-001).
