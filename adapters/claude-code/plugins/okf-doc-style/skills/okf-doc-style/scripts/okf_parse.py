#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frontmatter parser for the OKF field dialect (shared by okf_lint.py).

Covers what OKF v0.2 concepts actually carry: scalars, flow ``{...}`` and
``[...]`` values, block lists of scalars or mappings, block mappings under a
bare key (``verified:`` followed by indented ``by``/``at``), quoted flow
scalars, and producer-extension keys of any shape. YAML outside that dialect
is out of scope and returns ``None`` from ``parse_frontmatter``.
Pure standard library, Python 3.8+.
"""

import re
from typing import Dict, List, Optional, Sequence, Union

KEY_RE = re.compile(r"^([^:\s]+):\s*(.*)$")
Value = Union[str, Dict[str, str], List[str], List[Dict[str, str]]]


def _unquote(text: str) -> str:
    t = text.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    return t


def _split_flow(text: str) -> List[str]:
    parts, depth, cur, quote = [], 0, "", ""
    for ch in text:
        if quote:
            if ch == quote:
                quote = ""
            cur += ch
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        if ch == "," and depth == 0 and not quote:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def parse_flow(text: str) -> Value:
    """Parse a flow value: ``{...}`` mapping, ``[...]`` list, or scalar."""
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        pairs = {}
        for part in _split_flow(t[1:-1]):
            key, _, value = part.partition(":")
            pairs[key.strip()] = parse_flow(value)
        return pairs
    if t.startswith("[") and t.endswith("]"):
        return [_unquote(part) for part in _split_flow(t[1:-1])]
    return _unquote(t)


def front_lines(text: str) -> List[str]:
    """Return the raw frontmatter lines of a document, or [] when absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return []


def parse_frontmatter(lines: Sequence[str]) -> Optional[Dict[str, Value]]:
    """Parse frontmatter lines; ``None`` when the dialect does not hold."""
    fm: Dict[str, Value] = {}
    key: Optional[str] = None
    item: Optional[dict] = None

    def flush() -> None:
        nonlocal item
        if key is not None and isinstance(item, dict):
            entries = fm.setdefault(key, [])
            if isinstance(entries, list):
                entries.append(item)
        item = None

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if key is None or isinstance(fm.get(key), dict):
                return None
            flush()
            body = line[2:]
            match = KEY_RE.match(body)
            if match:
                item = {match.group(1): parse_flow(match.group(2))}
            else:
                entries = fm.setdefault(key, [])
                if isinstance(entries, list):
                    entries.append(parse_flow(body))
            continue
        match = KEY_RE.match(line)
        if not match:
            return None
        if raw[:1].isspace():
            # Indented lines continue a block list item, open a block mapping
            # under a bare key, or extend an open block mapping.
            if isinstance(item, dict):
                item[match.group(1)] = parse_flow(match.group(2))
            elif key is not None and fm.get(key) == []:
                fm[key] = {match.group(1): parse_flow(match.group(2))}
            elif isinstance(fm.get(key), dict):
                fm[key][match.group(1)] = parse_flow(match.group(2))
            else:
                return None
            continue
        flush()
        key = match.group(1)
        fm[key] = parse_flow(match.group(2)) if match.group(2) else []
    flush()
    return fm
