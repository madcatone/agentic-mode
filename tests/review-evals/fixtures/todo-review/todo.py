"""todo - a tiny task list for the terminal.

Every command is a fresh process: state lives in the database between runs.
"""
import sys

from parse import parse_args
from commands import run


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
