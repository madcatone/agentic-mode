"""Command-line parsing for the todo CLI."""

import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title")

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("task_id", type=int)

    p_list = sub.add_parser("list", help="list tasks")

    p_rm = sub.add_parser("rm", help="remove a task")
    p_rm.add_argument("task_id", type=int)

    return parser


def parse_args(argv):
    return build_parser().parse_args(argv)
