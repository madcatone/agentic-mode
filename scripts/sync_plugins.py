#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vendor the canonical agentic-mode assets into the Claude Code plugins.

A Claude Code skill can only read files under its own directory, so each plugin
must carry a self-contained (vendored) copy of whatever canonical file it needs
— it may not reach back into the repo with ``../``. That duplication is a
drift risk, so this script owns the one-way sync canon -> plugin and can verify
it in CI.

MANIFEST (the constant below) maps every canonical file to its vendored target:

* SKILL body sync -- the plugin's ``SKILL.md`` keeps its own YAML frontmatter
  (name + description, which drive skill triggering) and takes its BODY verbatim
  from a ``playbooks/*.md`` canon file.
* Verbatim file  -- the target is a byte-for-byte copy of a single canon file.
* Verbatim dir   -- every file in a canon directory is copied byte-for-byte into
  a target directory (and stray target files are reported as drift).

Two modes::

    python scripts/sync_plugins.py            # default: write canon -> plugin
    python scripts/sync_plugins.py --check     # verify only; exit 1 on any drift

Exit status: 0 = in sync / synced, 1 = drift found (``--check`` only), 2 = error
(missing source, malformed frontmatter, I/O). Pure standard library.
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
]

# canon file -> byte-for-byte vendored copy.
VERBATIM_FILES = [
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


def _read_bytes(p: Path) -> bytes:
    return p.read_bytes()


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
        yield ("file", s, d, lambda s=s: _read_bytes(s))
    for src_dir, dst_dir in VERBATIM_DIRS:
        s_dir, d_dir = ROOT / src_dir, ROOT / dst_dir
        if not s_dir.is_dir():
            raise SyncError(f"missing source dir: {src_dir}")
        for s in sorted(p for p in s_dir.iterdir() if p.is_file()):
            d = d_dir / s.name
            yield ("file", s, d, lambda s=s: _read_bytes(s))


def _dir_extras():
    """Yield vendored-dir files that have no canon counterpart (drift)."""
    for src_dir, dst_dir in VERBATIM_DIRS:
        s_dir, d_dir = ROOT / src_dir, ROOT / dst_dir
        if not d_dir.is_dir():
            continue
        canon_names = {p.name for p in s_dir.iterdir() if p.is_file()}
        for d in sorted(p for p in d_dir.iterdir() if p.is_file()):
            if d.name not in canon_names:
                yield d


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
        for extra in _dir_extras():
            rel = extra.relative_to(ROOT)
            if check:
                drift.append(f"  {rel}  (no canonical source — stray vendored file)")
            else:
                print(f"WARNING: stray vendored file with no canon source: {rel}")
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
