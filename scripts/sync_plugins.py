#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vendor the canonical agentic-mode assets into the Claude Code plugins.

A Claude Code skill reads only files under its own directory, so each plugin
carries a vendored copy of what it needs (no ``../`` reaches into the repo).
That duplication is a drift risk, so this script owns the one-way sync
canon -> plugin and can verify it in CI.

MANIFEST maps canon -> target three ways: SKILL body sync (target SKILL.md
keeps frontmatter, body verbatim from a playbooks/*.md file), file, dir.

``--check`` also asserts two invariants of the bootstrap skill dir: its file
set is exactly what the manifest explains, and every canon path cited by the
vendored RUNBOOK (code span or link; prose and scripts/ are not citations)
is vendored there (doctrine/ -> reference/) or disclosed in SKILL.md.

Usage: ``python scripts/sync_plugins.py [--check]``; exit 0 = in sync / synced,
1 = drift (``--check`` only), 2 = error. Pure standard library.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Repo root = parent of the scripts/ directory this file lives in.
ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = "adapters/claude-code/plugins/agentic-bootstrap/skills/agentic-bootstrap"

# canon path -> plugin SKILL.md whose BODY (post-frontmatter) must equal it.
SKILL_SYNC = [
    ("playbooks/COMMIT-MESSAGES.md",
     "adapters/claude-code/plugins/gcm/skills/gcm/SKILL.md"),
    ("playbooks/TWO-AXIS-REVIEW.md",
     "adapters/claude-code/plugins/two-axis-review/skills/two-axis-review/SKILL.md"),
    ("playbooks/REVIEW-RESPONSE.md",
     "adapters/claude-code/plugins/review-response/skills/review-response/SKILL.md"),
    ("playbooks/DOC-LINTER.md",
     "adapters/claude-code/plugins/doc-linter/skills/doc-linter/SKILL.md"),
    ("playbooks/OKF-DOC-STYLE.md",
     "adapters/claude-code/plugins/okf-doc-style/skills/okf-doc-style/SKILL.md"),
]

# canon file -> byte-for-byte vendored copy.
VERBATIM_FILES = [
    ("playbooks/scripts/doc_lint.py",
     "adapters/claude-code/plugins/doc-linter/skills/doc-linter/scripts/doc_lint.py"),
    ("playbooks/scripts/okf_parse.py",
     "adapters/claude-code/plugins/okf-doc-style/skills/okf-doc-style/scripts/okf_parse.py"),
    ("playbooks/scripts/okf_lint.py",
     "adapters/claude-code/plugins/okf-doc-style/skills/okf-doc-style/scripts/okf_lint.py"),
    ("playbooks/scripts/okf_selftest.py",
     "adapters/claude-code/plugins/okf-doc-style/skills/okf-doc-style/scripts/okf_selftest.py"),
    ("RUNBOOK.md", f"{BOOTSTRAP}/RUNBOOK.md"),
    ("doctrine/BOOTSTRAP-CORE.md", f"{BOOTSTRAP}/reference/BOOTSTRAP-CORE.md"),
    ("checker/check_agentic_docs.py", f"{BOOTSTRAP}/checker/check_agentic_docs.py"),
    ("checker/config.example.json", f"{BOOTSTRAP}/checker/config.example.json"),
]

# canon dir -> vendored dir (every regular file copied byte-for-byte).
VERBATIM_DIRS = [
    ("templates", f"{BOOTSTRAP}/templates"),
]

_FRONTMATTER = re.compile(r"\A(---\n.*?\n---\n\n?)", re.DOTALL)


def _split_frontmatter(text: str):
    """Return (frontmatter_region, body) or (None, None) if no frontmatter."""
    m = _FRONTMATTER.match(text)
    if not m:
        return None, None
    return m.group(1), text[m.end():]


class SyncError(Exception):
    pass


def _skill_expected(canon: Path, target: Path) -> bytes:
    """Compose the expected SKILL.md bytes: target frontmatter + canon body."""
    if not target.exists():
        raise SyncError(f"missing target SKILL.md: {target.relative_to(ROOT)}")
    fm, _ = _split_frontmatter(target.read_text(encoding="utf-8"))
    if fm is None:
        raise SyncError(
            f"target SKILL.md has no YAML frontmatter: {target.relative_to(ROOT)}")
    body = canon.read_text(encoding="utf-8")
    return (fm + body).encode("utf-8")


def _iter_units():
    """Yield (label, source_path, target_path, expected_bytes_fn) tuples."""
    for src, dst in SKILL_SYNC:
        s, d = ROOT / src, ROOT / dst
        yield ("skill", s, d, lambda s=s, d=d: _skill_expected(s, d))
    for src, dst in VERBATIM_FILES:
        s, d = ROOT / src, ROOT / dst
        yield ("file", s, d, lambda s=s: s.read_bytes())
    for src_dir, dst_dir in VERBATIM_DIRS:
        s_dir, d_dir = ROOT / src_dir, ROOT / dst_dir
        if not s_dir.is_dir():
            raise SyncError(f"missing source dir: {src_dir}")
        for s in sorted(p for p in s_dir.iterdir() if p.is_file()):
            d = d_dir / s.name
            yield ("file", s, d, lambda s=s: s.read_bytes())


_CANON_REF = re.compile(
    r"\b(?:doctrine|checker|templates|examples|playbooks|tests)/[\w./-]+")


def _skill_strays():
    """Yield (path, kind) breaking the exact file set: 'extra' or 'missing'."""
    expected = {ROOT / BOOTSTRAP / "SKILL.md"} | {
        ROOT / d for _, d in VERBATIM_FILES if d.startswith(BOOTSTRAP)}
    expected |= {ROOT / dst / p.name for src, dst in VERBATIM_DIRS
                 for p in (ROOT / src).iterdir() if p.is_file()}
    actual = {p for p in (ROOT / BOOTSTRAP).rglob("*")
              if p.is_file() and "__pycache__" not in p.parts}
    yield from ((p, "missing") for p in sorted(expected - actual))
    yield from ((p, "extra") for p in sorted(actual - expected))


def _uncovered_refs():
    """Yield canon paths cited (code span or link) by the vendored RUNBOOK
    that the skill neither vendors nor discloses in SKILL.md."""
    skill = ROOT / BOOTSTRAP
    if not (skill / "RUNBOOK.md").is_file() or not (skill / "SKILL.md").is_file():
        return  # a missing unit is already reported as manifest drift
    runbook = (skill / "RUNBOOK.md").read_text(encoding="utf-8")
    wrapper = (skill / "SKILL.md").read_text(encoding="utf-8")
    cited = set()
    for line in runbook.splitlines():
        for chunk in re.findall(r"`[^`\n]+`|\]\([^)\n]+\)", line):
            cited.update(_CANON_REF.findall(chunk))
    for ref in sorted(cited):
        local = skill / ref.replace("doctrine/", "reference/", 1)
        if not local.is_file() and ref not in wrapper:
            yield ref


def run(check: bool) -> int:
    drift = []
    try:
        for label, src, dst, expected_fn in _iter_units():
            if not src.exists():
                raise SyncError(f"missing source: {src.relative_to(ROOT)}")
            expected = expected_fn()
            actual = dst.read_bytes() if dst.exists() else None
            if actual == expected:
                continue
            rel = dst.relative_to(ROOT)
            if check:
                reason = "missing" if actual is None else "out of sync"
                drift.append(f"  {rel}  ({reason} with {src.relative_to(ROOT)})")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(expected)
                print(f"synced  {rel}")
        for path, kind in _skill_strays():
            rel = path.relative_to(ROOT)
            if check:
                drift.append(f"  {rel}  ({kind} file — manifest expects an exact set)")
            else:
                print(f"WARNING: {kind} file, manifest expects an exact set: {rel}")
        for ref in _uncovered_refs():
            if check:
                drift.append(f"  {ref}  (RUNBOOK citation not vendored or disclosed)")
            else:
                print(f"WARNING: RUNBOOK citation not vendored or disclosed: {ref}")
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if check:
        if drift:
            print("plugin vendoring is OUT OF SYNC with the canon:")
            print("\n".join(drift))
            print("\nrun `python3 scripts/sync_plugins.py` to fix.")
            return 1
        print("plugin vendoring is in sync with the canon.")
        return 0
    print("sync complete.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="verify only; do not write. Exit 1 on any drift.")
    args = ap.parse_args()
    return run(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
