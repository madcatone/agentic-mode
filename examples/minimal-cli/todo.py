#!/usr/bin/env python3
"""todo — a tiny standard-library task tracker (agentic-mode example entrypoint).

This is a deliberately small, fictional CLI that exists so the example repo has
a real, byte-compilable entry point for the documentation gate to check. It
stores tasks as JSON and supports add / list / done / remove. It is not meant to
be a production tool — it is the "observable surface" the example docs describe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List


def _store_path(explicit: str | None) -> str:
    """Resolve the task-store path from a flag or the TODO_STORE env var."""
    return explicit or os.environ.get("TODO_STORE", "tasks.json")


def _load(path: str) -> List[Dict]:
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save(path: str, tasks: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, indent=2)


def cmd_add(tasks: List[Dict], text: str) -> str:
    new_id = (max((t["id"] for t in tasks), default=0)) + 1
    tasks.append({"id": new_id, "text": text, "done": False})
    return f"added #{new_id}: {text}"


def cmd_list(tasks: List[Dict], show_all: bool) -> str:
    rows = tasks if show_all else [t for t in tasks if not t["done"]]
    if not rows:
        return "(no tasks)"
    return "\n".join(
        f"[{'x' if t['done'] else ' '}] #{t['id']} {t['text']}" for t in rows
    )


def cmd_done(tasks: List[Dict], task_id: int) -> str:
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return f"done #{task_id}"
    return f"no such task: #{task_id}"


def cmd_remove(tasks: List[Dict], task_id: int) -> str:
    before = len(tasks)
    tasks[:] = [t for t in tasks if t["id"] != task_id]
    return f"removed #{task_id}" if len(tasks) < before else f"no such task: #{task_id}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="A tiny task tracker.")
    parser.add_argument("--store", help="path to the JSON task store")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("text", help="task description")

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--all", action="store_true", help="include completed tasks")

    p_done = sub.add_parser("done", help="mark a task complete")
    p_done.add_argument("id", type=int, help="task id")

    p_remove = sub.add_parser("remove", help="delete a task")
    p_remove.add_argument("id", type=int, help="task id")

    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    path = _store_path(args.store)
    tasks = _load(path)

    if args.command == "add":
        message = cmd_add(tasks, args.text)
    elif args.command == "list":
        print(cmd_list(tasks, args.all))
        return 0
    elif args.command == "done":
        message = cmd_done(tasks, args.id)
    elif args.command == "remove":
        message = cmd_remove(tasks, args.id)
    else:  # pragma: no cover - argparse enforces a valid subcommand
        return 2

    _save(path, tasks)
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
