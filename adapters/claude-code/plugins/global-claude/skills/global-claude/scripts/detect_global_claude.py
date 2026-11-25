#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only detector for the user-global Claude Code instruction file.

Resolves ``CLAUDE.md`` from ``CLAUDE_CONFIG_DIR`` when that variable is set
and non-empty (whitespace-only counts as unset), otherwise
``~/.claude/CLAUDE.md``. Also reports ``~/.agents/AGENTS.md`` and
``~/.codex/AGENTS.md``. Prints status, a logical line count, and mechanical
flags. Never creates or modifies a file.

``--selftest`` runs against temporary directories only. Exit 0 is a
successful report or a passing selftest, 1 is a failed selftest, 2 is a
usage error. Pure standard library.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import List, NamedTuple, Optional, Sequence, Tuple


_POINTER = re.compile(r"^See\s+@(\S+)\s*$")
_ASSIGN = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|pwd)\b\s*[:=]\s*(\S+)"
)
_PREFIXES = (
    re.compile(r"\bsk-[A-Za-z0-9]{10,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
)
_MACHINE = (
    re.compile(r"(?:^|[\s`'\"=(])/(?:Users|home)/[A-Za-z0-9._-]+"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+"),
)
_SIBLING_HOMES = {".agents", ".codex"}


class Report(NamedTuple):
    claude_status: str
    claude_path: Path
    claude_via: str
    claude_lines: str
    claude_kind: str
    agents_path: Path
    agents_status: str
    codex_path: Path
    codex_status: str
    preferred: Optional[Path]
    pointer_import: str
    secret_lines: List[int]
    machine_path_lines: List[int]
    pointer_targets: List[Tuple[str, str]]


def env_home() -> Path:
    raw = os.environ.get("HOME")
    if raw and raw.strip():
        return Path(raw).expanduser()
    return Path.home()


def env_config_dir() -> Optional[Path]:
    """Return CLAUDE_CONFIG_DIR, or None when unset or whitespace-only."""
    raw = os.environ.get("CLAUDE_CONFIG_DIR")
    if raw is None:
        return None
    stripped = raw.strip()
    if not stripped:
        return None
    return Path(stripped).expanduser()


def classify_path(path: Path) -> str:
    """exists | missing | not_a_file | broken_symlink | unreadable."""
    try:
        if path.is_symlink() and not path.exists():
            return "broken_symlink"
        if not path.exists():
            return "missing"
        if not path.is_file():
            return "not_a_file"
        return "exists"
    except OSError:
        return "unreadable"


def _read_text(path: Path) -> Tuple[str, Optional[str]]:
    status = classify_path(path)
    if status != "exists":
        return status, None
    try:
        return "exists", path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "unreadable", None


def kind_of(text: str) -> str:
    nonempty = [line.strip() for line in text.splitlines() if line.strip()]
    if not nonempty:
        return "empty"
    if all(_POINTER.match(line) for line in nonempty):
        return "pointer"
    return "prose"


def _assigned_secret(value: str) -> bool:
    value = value.strip("\"'`")
    if len(value) >= 20:
        return True
    if len(value) >= 12 and re.search(r"[^A-Za-z]", value):
        return True
    return False


def secret_line_numbers(text: str) -> List[int]:
    found: List[int] = []
    for index, line in enumerate(text.splitlines(), start=1):
        assigned = any(
            _assigned_secret(match.group(1)) for match in _ASSIGN.finditer(line)
        )
        if assigned or any(pattern.search(line) for pattern in _PREFIXES):
            found.append(index)
    return found


def machine_path_line_numbers(text: str) -> List[int]:
    found: List[int] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in _MACHINE):
            found.append(index)
    return found


def resolve_import(claude_file: Path, token: str) -> Path:
    if token.startswith("~"):
        return Path(token).expanduser()
    path = Path(token)
    if path.is_absolute():
        return path
    return claude_file.parent / path


def pointer_targets(claude_file: Path, text: str) -> List[Tuple[str, str]]:
    targets: List[Tuple[str, str]] = []
    for line in text.splitlines():
        match = _POINTER.match(line.strip())
        if not match:
            continue
        token = match.group(1)
        targets.append((token, classify_path(resolve_import(claude_file, token))))
    return targets


def pointer_import(claude_file: Path, agents_file: Path) -> str:
    """Short sibling hop, otherwise the absolute path of the AGENTS.md."""
    claude_abs = claude_file.expanduser().resolve(strict=False)
    agents_abs = agents_file.expanduser().resolve(strict=False)
    try:
        relative = Path(os.path.relpath(agents_abs, claude_abs.parent))
    except ValueError:
        return agents_abs.as_posix()
    parts = relative.parts
    if (
        len(parts) == 3
        and parts[0] == ".."
        and parts[1] in _SIBLING_HOMES
        and parts[2] == "AGENTS.md"
    ):
        return relative.as_posix()
    return agents_abs.as_posix()


def _first_file(paths: Sequence[Path]) -> Optional[Path]:
    for path in paths:
        if classify_path(path) == "exists":
            return path.expanduser().resolve(strict=False)
    return None


def detect(home: Path, config_dir: Optional[Path]) -> Report:
    home_abs = home.expanduser().resolve(strict=False)
    if config_dir is not None:
        claude = config_dir.expanduser().resolve(strict=False) / "CLAUDE.md"
        via = "CLAUDE_CONFIG_DIR"
    else:
        claude = home_abs / ".claude" / "CLAUDE.md"
        via = "default"
    agents = home_abs / ".agents" / "AGENTS.md"
    codex = home_abs / ".codex" / "AGENTS.md"
    status, text = _read_text(claude)
    if status == "exists" and text is not None:
        kind = kind_of(text)
        lines = str(len(text.splitlines()))
        secrets = secret_line_numbers(text)
        machines = machine_path_line_numbers(text)
        targets = pointer_targets(claude, text) if kind == "pointer" else []
    elif status == "missing":
        kind = "missing"
        lines = "0"
        secrets = []
        machines = []
        targets = []
    else:
        kind = status
        lines = "-"
        secrets = []
        machines = []
        targets = []
    preferred = _first_file((agents, codex))
    return Report(
        claude_status=status,
        claude_path=claude,
        claude_via=via,
        claude_lines=lines,
        claude_kind=kind,
        agents_path=agents,
        agents_status=classify_path(agents),
        codex_path=codex,
        codex_status=classify_path(codex),
        preferred=preferred,
        pointer_import=pointer_import(claude, preferred) if preferred else "-",
        secret_lines=secrets,
        machine_path_lines=machines,
        pointer_targets=targets,
    )


def _join_numbers(numbers: Sequence[int]) -> str:
    if not numbers:
        return "none"
    return ",".join(str(number) for number in numbers)


def render(report: Report) -> str:
    rows = [
        "claude_md_status: {0}".format(report.claude_status),
        "claude_md_path: {0}".format(report.claude_path.as_posix()),
        "claude_md_via: {0}".format(report.claude_via),
        "claude_md_lines: {0}".format(report.claude_lines),
        "claude_md_kind: {0}".format(report.claude_kind),
        "agents_md_path: {0}".format(report.agents_path.as_posix()),
        "agents_md_status: {0}".format(report.agents_status),
        "codex_agents_md_path: {0}".format(report.codex_path.as_posix()),
        "codex_agents_md_status: {0}".format(report.codex_status),
        "preferred_agents_md: {0}".format(
            report.preferred.as_posix() if report.preferred else "none"
        ),
        "pointer_import: {0}".format(report.pointer_import),
        "secret_lines: {0}".format(_join_numbers(report.secret_lines)),
        "machine_path_lines: {0}".format(_join_numbers(report.machine_path_lines)),
    ]
    if report.pointer_targets:
        rows.extend(
            "pointer_target: {0} {1}".format(token, status)
            for token, status in report.pointer_targets
        )
    else:
        rows.append("pointer_target: -")
    return "\n".join(rows) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Report the user-global CLAUDE.md and the global AGENTS.md homes. "
            "Read-only."
        )
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run the built-in fixture suite and exit",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=None,
        help="home directory to inspect (default: HOME, else the current user)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="override CLAUDE_CONFIG_DIR for this run",
    )
    parser.add_argument(
        "--no-config-dir",
        action="store_true",
        help="ignore CLAUDE_CONFIG_DIR and use <home>/.claude/CLAUDE.md",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(None if argv is None else list(argv))
    if args.selftest and (args.home or args.config_dir or args.no_config_dir):
        parser.error("--selftest does not take path flags")
    if args.selftest:
        return selftest()
    if args.no_config_dir:
        config_dir = None
    elif args.config_dir is not None:
        config_dir = args.config_dir
    else:
        config_dir = env_config_dir()
    home = args.home if args.home is not None else env_home()
    sys.stdout.write(render(detect(home, config_dir)))
    return 0


class _Check:
    def __init__(self) -> None:
        self.n = 0
        self.fails: List[str] = []

    def eq(self, label: str, got: object, want: object) -> None:
        self.n += 1
        if got != want:
            self.fails.append("{0}: got {1!r} want {2!r}".format(label, got, want))

    def true(self, label: str, cond: bool, detail: str = "") -> None:
        self.n += 1
        if not cond:
            self.fails.append("{0}: {1}".format(label, detail))

    def not_in(self, label: str, needle: str, haystack: str) -> None:
        self.n += 1
        if needle in haystack:
            self.fails.append("{0}: output contains {1!r}".format(label, needle))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def selftest() -> int:
    """Fixture suite. Touches only temporary directories."""
    check = _Check()
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        _case_missing_creates_nothing(check, root / "missing")
        _case_prefer_agents_over_codex(check, root / "both")
        _case_codex_only(check, root / "codex")
        _case_config_dir_wins(check, root / "cfgwin")
        _case_absolute_pointer_when_not_sibling(check, root / "abs")
        _case_prose_lines_and_flags(check, root / "prose")
        _case_pointer_and_dangling(check, root / "pointer")
        _case_not_a_file_and_broken_symlink(check, root / "special")
        _case_unreadable(check, root / "unreadable")
        _case_cli_and_env(check, root / "cli")
    if check.fails:
        for failure in check.fails:
            print("FAIL {0}".format(failure), file=sys.stderr)
        print(
            "selftest: {0} failed, {1} checks".format(len(check.fails), check.n),
            file=sys.stderr,
        )
        return 1
    print("selftest: {0} passed".format(check.n))
    return 0


def _case_missing_creates_nothing(check: _Check, home: Path) -> None:
    before = set(home.rglob("*")) if home.exists() else set()
    report = detect(home, None)
    after = set(home.rglob("*")) if home.exists() else set()
    check.eq("missing status", report.claude_status, "missing")
    check.eq("missing kind", report.claude_kind, "missing")
    check.eq("missing lines", report.claude_lines, "0")
    check.eq("missing via", report.claude_via, "default")
    check.eq("missing agents", report.agents_status, "missing")
    check.eq("missing codex", report.codex_status, "missing")
    check.eq("missing preferred", report.preferred, None)
    check.eq("missing import", report.pointer_import, "-")
    check.eq("missing secrets", report.secret_lines, [])
    check.eq("missing machines", report.machine_path_lines, [])
    check.eq("missing targets", report.pointer_targets, [])
    check.true(
        "missing path",
        report.claude_path == (home.resolve() / ".claude" / "CLAUDE.md"),
        report.claude_path.as_posix(),
    )
    check.eq("missing writes nothing", after, before)
    check.true("missing parent absent", not (home / ".claude").exists())


def _case_prefer_agents_over_codex(check: _Check, home: Path) -> None:
    _write(home / ".agents" / "AGENTS.md", "# agents\n")
    _write(home / ".codex" / "AGENTS.md", "# codex\n")
    report = detect(home, None)
    check.eq("both agents", report.agents_status, "exists")
    check.eq("both codex", report.codex_status, "exists")
    check.eq(
        "both preferred",
        report.preferred,
        (home / ".agents" / "AGENTS.md").resolve(),
    )
    check.eq("both import", report.pointer_import, "../.agents/AGENTS.md")
    rendered = render(report)
    check.true(
        "both render import",
        "pointer_import: ../.agents/AGENTS.md\n" in rendered,
    )


def _case_codex_only(check: _Check, home: Path) -> None:
    _write(home / ".codex" / "AGENTS.md", "# codex\n")
    report = detect(home, None)
    check.eq("codex preferred status", report.agents_status, "missing")
    check.eq(
        "codex preferred path",
        report.preferred,
        (home / ".codex" / "AGENTS.md").resolve(),
    )
    check.eq("codex import", report.pointer_import, "../.codex/AGENTS.md")


def _case_config_dir_wins(check: _Check, root: Path) -> None:
    home = root / "home"
    config = root / "custom"
    _write(home / ".claude" / "CLAUDE.md", "See @AGENTS.md\n")
    report = detect(home, config)
    check.eq("config status", report.claude_status, "missing")
    check.eq("config via", report.claude_via, "CLAUDE_CONFIG_DIR")
    check.eq(
        "config path",
        report.claude_path,
        config.resolve() / "CLAUDE.md",
    )
    check.eq(
        "config leaves default file",
        (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"),
        "See @AGENTS.md\n",
    )
    _write(config / "CLAUDE.md", "alpha\nbeta\n")
    found = detect(home, config)
    check.eq("config exists", found.claude_status, "exists")
    check.eq("config lines", found.claude_lines, "2")
    check.eq("config kind", found.claude_kind, "prose")


def _case_absolute_pointer_when_not_sibling(check: _Check, root: Path) -> None:
    home = root / "home"
    config = root / "other" / "cfg"
    _write(home / ".agents" / "AGENTS.md", "# agents\n")
    report = detect(home, config)
    expected = (home / ".agents" / "AGENTS.md").resolve().as_posix()
    check.eq("abs import", report.pointer_import, expected)
    check.true(
        "abs import is absolute",
        report.pointer_import.startswith("/"),
        report.pointer_import,
    )


def _case_prose_lines_and_flags(check: _Check, home: Path) -> None:
    secret = "sk-TESTSECRETVALUE123456"
    text = "\n".join(
        [
            "See @../.agents/AGENTS.md",
            "Also keep notes in /home/alice/proj.",
            "password: required",
            "api_key=abcd1234efgh",
            "use {0} please".format(secret),
            "token: ask-me-first",
            "Windows lives at C:\\Users\\bob\\src",
            "prefer ~/.claude/CLAUDE.md",
        ]
    )
    _write(home / ".claude" / "CLAUDE.md", text)
    report = detect(home, None)
    rendered = render(report)
    check.eq("prose kind", report.claude_kind, "prose")
    check.eq("prose lines", report.claude_lines, "8")
    check.eq("prose no trailing extra", len(text.splitlines()), 8)
    check.eq("prose secrets", report.secret_lines, [4, 5, 6])
    check.eq("prose machines", report.machine_path_lines, [2, 7])
    check.eq("prose hides targets", report.pointer_targets, [])
    check.true("prose target row", "pointer_target: -\n" in rendered)
    check.not_in("prose hides secret", secret, rendered)
    check.not_in("prose hides assigned secret", "abcd1234efgh", rendered)
    one_line = "See @AGENTS.md"
    _write(home / ".claude" / "CLAUDE.md", one_line)
    no_nl = detect(home, None)
    check.eq("no newline lines", no_nl.claude_lines, "1")
    _write(home / ".claude" / "CLAUDE.md", one_line + "\n")
    with_nl = detect(home, None)
    check.eq("trailing newline lines", with_nl.claude_lines, "1")
    _write(home / ".claude" / "CLAUDE.md", "\n  \n")
    blank = detect(home, None)
    check.eq("blank kind", blank.claude_kind, "empty")
    check.eq("blank status", blank.claude_status, "exists")
    check.eq("blank lines", blank.claude_lines, "2")


def _case_pointer_and_dangling(check: _Check, home: Path) -> None:
    _write(home / ".agents" / "AGENTS.md", "# canon\n")
    _write(
        home / ".claude" / "CLAUDE.md",
        "\nSee @../.agents/AGENTS.md\n\n",
    )
    report = detect(home, None)
    check.eq("pointer kind", report.claude_kind, "pointer")
    check.eq("pointer lines", report.claude_lines, "3")
    check.eq(
        "pointer target",
        report.pointer_targets,
        [("../.agents/AGENTS.md", "exists")],
    )
    rendered = render(report)
    check.true(
        "pointer row",
        "pointer_target: ../.agents/AGENTS.md exists\n" in rendered,
    )
    _write(home / ".claude" / "CLAUDE.md", "See @missing.md\nSee @/no/such.md\n")
    dangling = detect(home, None)
    check.eq("dangling kind", dangling.claude_kind, "pointer")
    check.eq(
        "dangling targets",
        dangling.pointer_targets,
        [("missing.md", "missing"), ("/no/such.md", "missing")],
    )


def _case_not_a_file_and_broken_symlink(check: _Check, home: Path) -> None:
    directory = home / ".claude" / "CLAUDE.md"
    directory.mkdir(parents=True)
    report = detect(home, None)
    check.eq("dir status", report.claude_status, "not_a_file")
    check.eq("dir kind", report.claude_kind, "not_a_file")
    check.eq("dir lines", report.claude_lines, "-")
    directory.rmdir()
    link = home / ".claude" / "CLAUDE.md"
    link.symlink_to(home / ".claude" / "nope")
    broken = detect(home, None)
    check.eq("symlink status", broken.claude_status, "broken_symlink")
    check.eq("symlink lines", broken.claude_lines, "-")
    check.true("symlink target not created", not (home / ".claude" / "nope").exists())


def _case_unreadable(check: _Check, home: Path) -> None:
    euid = getattr(os, "geteuid", lambda: 1)()
    if euid == 0:
        check.true("unreadable skipped as root", True)
        return
    path = home / ".claude" / "CLAUDE.md"
    _write(path, "secret text\n")
    path.chmod(0)
    try:
        report = detect(home, None)
    finally:
        path.chmod(0o600)
    check.eq("unreadable status", report.claude_status, "unreadable")
    check.eq("unreadable lines", report.claude_lines, "-")
    check.not_in("unreadable hides body", "secret text", render(report))


def _case_cli_and_env(check: _Check, root: Path) -> None:
    home = root / "home"
    _write(home / ".agents" / "AGENTS.md", "# agents\n")
    saved_config = os.environ.get("CLAUDE_CONFIG_DIR")
    saved_home = os.environ.get("HOME")
    try:
        os.environ["CLAUDE_CONFIG_DIR"] = "   "
        check.eq("blank env config", env_config_dir(), None)
        os.environ["CLAUDE_CONFIG_DIR"] = ""
        check.eq("empty env config", env_config_dir(), None)
        custom = root / "from-env"
        os.environ["CLAUDE_CONFIG_DIR"] = str(custom)
        os.environ["HOME"] = str(home)
        parsed = env_config_dir()
        check.true(
            "env config path",
            parsed is not None and parsed == Path(str(custom)),
            repr(parsed),
        )
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = main(["--home", str(home), "--no-config-dir"])
        output = buffer.getvalue()
        check.eq("cli exit", code, 0)
        check.true(
            "cli default path",
            "claude_md_path: {0}".format(
                (home.resolve() / ".claude" / "CLAUDE.md").as_posix()
            )
            in output,
            output,
        )
        check.true("cli via default", "claude_md_via: default\n" in output)
        check.true(
            "cli sees agents",
            "pointer_import: ../.agents/AGENTS.md\n" in output,
            output,
        )
        flagged = io.StringIO()
        with contextlib.redirect_stdout(flagged):
            flagged_code = main(["--home", str(home), "--config-dir", str(custom)])
        flagged_out = flagged.getvalue()
        check.eq("flag exit", flagged_code, 0)
        check.true(
            "flag path",
            "claude_md_path: {0}".format((custom.resolve() / "CLAUDE.md").as_posix())
            in flagged_out,
            flagged_out,
        )
        check.true(
            "flag via",
            "claude_md_via: CLAUDE_CONFIG_DIR\n" in flagged_out,
        )
    finally:
        if saved_config is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = saved_config
        if saved_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = saved_home


if __name__ == "__main__":
    sys.exit(main())
