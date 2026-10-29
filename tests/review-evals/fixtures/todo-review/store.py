"""Persistence for the todo CLI: one JSON file holding every task.

The store is the single source of truth for task state; every command is a
fresh process, so anything not written here is lost between runs.
"""

import json
import os

_TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "tasks.json")


class Task:
    """One task: an id, a title, and whether it is done."""

    def __init__(self, task_id, title, done=False):
        self.id = task_id
        self.title = title
        self.done = done


def next_id(tasks):
    """Return the id for the next added task."""
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1


def load():
    """Load all tasks from disk (empty list when the file is missing)."""
    if not os.path.exists(_TASKS_FILE):
        return []
    with open(_TASKS_FILE, "r", encoding="utf-8") as fh:
        rows = json.load(fh)
    return [Task(i, row["title"]) for i, row in enumerate(rows, start=1)]


def save(tasks):
    """Write every task to disk."""
    rows = [{"id": t.id, "title": t.title} for t in tasks]
    with open(_TASKS_FILE, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
        fh.write("\n")
