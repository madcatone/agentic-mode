#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical half of the OKF doc-style playbook's conformance checklist.

Usage: ``python3 scripts/okf_lint.py <bundle-root>`` or ``--selftest``.

K1 parseable frontmatter with non-empty ``type`` on every non-reserved .md
K2 ``index.md`` frontmatter only at bundle root, ``okf_version`` only
K3 ``log.md`` headings ISO ``YYYY-MM-DD``, newest first
K4 timestamps ISO 8601 with explicit UTC offset
K5 ``generated.by`` / ``verified[].by`` follow the actor convention
K6 body footnote labels (references and definitions) match a ``sources[].id``
K7 ``status`` is draft / stable / deprecated
K8 ``sources[].usage_count`` framed by ``usage_window`` (shared or per-entry)

Findings print as ``<path>: [K1] message``; exit 0 clean, 1 violations,
2 usage/I/O error (including non-UTF-8 files). Pure stdlib; the judgment
half stays with the reader.
"""

import argparse
import re
import sys
from pathlib import Path

from okf_parse import front_lines, parse_frontmatter

ISO_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})$")
ISO_DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ACTOR_RE = re.compile(r"^(?:human:.+|process:.+|[^:\s]+/\S+)$")
FOOTNOTE_LABEL_RE = re.compile(r"\[\^([^\]]+)\]")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"^\s*(?:```|~~~)", re.MULTILINE)
STATUS_VALUES = {"draft", "stable", "deprecated"}

def _events(fm):
    """generated and verified entries as a flat list of dicts."""
    out = []
    for key in ("generated", "verified"):
        value = fm.get(key)
        if isinstance(value, dict):
            out.append(value)
        elif isinstance(value, list):
            out += [e for e in value if isinstance(e, dict)]
    return out

def _strip_fences(text):
    out, fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return "\n".join(out)

def check_concept(rel, text):
    front = front_lines(text)
    fm = parse_frontmatter(front) if front else None
    if fm is None:
        return ["%s: [K1] no parseable frontmatter block" % rel]
    out = []
    type_value = fm.get("type")
    if not isinstance(type_value, str) or not type_value.strip():
        out.append("%s: [K1] frontmatter lacks a non-empty `type`" % rel)
    status = fm.get("status")
    if isinstance(status, str) and status and status not in STATUS_VALUES:
        out.append("%s: [K7] status %r is not draft/stable/deprecated" % (rel, status))
    stamps = []
    generated = fm.get("generated")
    if isinstance(generated, dict) and not generated.get("by"):
        out.append("%s: [K5] generated carries no `by` actor" % rel)
    for event in _events(fm):
        stamps.append(event.get("at", ""))
        by = event.get("by", "")
        if by and not ACTOR_RE.match(by):
            out.append("%s: [K5] actor %r is not producer/version, human:, or process:"
                       % (rel, by))
    stale = fm.get("stale_after")
    if isinstance(stale, str) and stale:
        stamps.append(stale)
    window = fm.get("usage_window")
    if isinstance(window, dict):
        stamps += [window.get("from", ""), window.get("to", "")]
    sources = fm.get("sources")
    sources = sources if isinstance(sources, list) else []
    ids, unframed = set(), 0
    for source in sources:
        if not isinstance(source, dict):
            continue
        ids.add(source.get("id") or "")
        stamps.append(source.get("last_modified", ""))
        entry_window = source.get("usage_window")
        if isinstance(entry_window, dict):
            stamps += [entry_window.get("from", ""), entry_window.get("to", "")]
        if source.get("usage_count") and not isinstance(entry_window, dict) \
                and not isinstance(window, dict):
            unframed += 1
    ids.discard("")
    for stamp in (s for s in stamps if s):
        if not ISO_TS_RE.match(stamp):
            out.append("%s: [K4] timestamp %r is not ISO 8601 with a UTC offset"
                       % (rel, stamp))
    if unframed:
        out.append("%s: [K8] usage_count present with no usage_window" % rel)
    for label in set(FOOTNOTE_LABEL_RE.findall(text)):
        if label not in ids:
            out.append("%s: [K6] footnote label %r matches no sources[].id"
                       % (rel, label))
    return out

def check_index(rel, text, is_root):
    front = front_lines(text)
    if not front:
        return []
    if not is_root:
        return ["%s: [K2] index.md carries frontmatter outside the bundle root" % rel]
    keys = {line.partition(":")[0].strip() for line in front
            if line.strip() and not line.lstrip().startswith("#")}
    extra = keys - {"okf_version"}
    if extra:
        return ["%s: [K2] index.md frontmatter beyond okf_version: %s"
                % (rel, ", ".join(sorted(extra)))]
    return []

def check_log(rel, text):
    headings = HEADING_RE.findall(_strip_fences(text))
    out = ["%s: [K3] heading %r is not an ISO YYYY-MM-DD date" % (rel, day)
           for day in headings if not ISO_DAY_RE.match(day)]
    days = [d for d in headings if ISO_DAY_RE.match(d)]
    if days != sorted(days, reverse=True):
        out.append("%s: [K3] date headings are not newest first" % rel)
    return out

def scan_bundle(root):
    out = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8-sig")
        if path.name == "log.md":
            out += check_log(rel, text)
        elif path.name == "index.md":
            out += check_index(rel, text, path.parent == root)
        else:
            out += check_concept(rel, text)
    return out

def main(argv=None):
    parser = argparse.ArgumentParser(prog="okf_lint.py",
                                     description="Mechanical OKF v0.2 bundle checks.")
    parser.add_argument("root", nargs="?", help="bundle root directory")
    parser.add_argument("--selftest", action="store_true",
                        help="run the built-in fixture cases and exit")
    args = parser.parse_args(sys.argv[1:] if argv is None else list(argv))
    if args.selftest:
        from okf_selftest import run
        return run(scan_bundle)
    if not args.root:
        print("okf_lint: no bundle root given", file=sys.stderr)
        return 2
    root = Path(args.root)
    if not root.is_dir():
        print("okf_lint: not a directory: %s" % root, file=sys.stderr)
        return 2
    try:
        findings = scan_bundle(root)
    except OSError as exc:
        print("okf_lint: I/O error: %s" % exc, file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print("okf_lint: bundle contains non-UTF-8 markdown: %s" % exc, file=sys.stderr)
        return 2
    print("okf-lint: %s (%d findings)" % (root, len(findings)))
    for finding in findings:
        print("  " + finding)
    return 1 if findings else 0

if __name__ == "__main__":
    sys.exit(main())
