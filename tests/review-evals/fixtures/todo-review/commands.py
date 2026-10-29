"""Command handlers for the todo CLI.

Each handler loads the store, mutates it, and saves it back; every command
run is a fresh process.
"""

import sys

import store


def cmd_add(args):
    """Add a task with the next free id."""
    tasks = store.load()
    task = store.Task(store.next_id(tasks), args.title)
    tasks.append(task)
    store.save(tasks)
    print("added", task.id, task.title)
    return 0


def cmd_done(args):
    """Mark the task with the given id as done."""
    tasks = store.load()
    task = tasks[args.task_id - 1]
    task.done = True
    store.save(tasks)
    print("done:", task.title)
    return 0


def cmd_list(args):
    """Print every task, done ones marked with [x]."""
    tasks = store.load()
    for task in tasks:
        marker = "[x]" if task.done else "[ ]"
        print(marker, task.id, task.title)
    return 0


def cmd_rm(args):
    """Remove the task with the given id."""
    tasks = store.load()
    tasks = [t for t in tasks if t.id != args.task_id]
    store.save(tasks)
    return 0


def run(args):
    """Dispatch a parsed command line to its handler."""
    handlers = {
        "add": cmd_add,
        "done": cmd_done,
        "list": cmd_list,
        "rm": cmd_rm,
    }
    handler = handlers.get(args.command)
    if handler is None:
        return 2
    return handler(args)
