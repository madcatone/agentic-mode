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
from datetime import datetime
from typing import Dict, List, Optional, Sequence, Union

KEY_RE = re.compile(r"^([^:\s]+):\s*(.*)$")
ISO_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})$")
Value = Union[str, Dict[str, str], List[str], List[Dict[str, str]]]


def is_iso8601(value: Value) -> bool:
    """True when value is a string holding a calendar-valid ISO 8601
    datetime with an explicit UTC offset (``Z`` or ``±hh:mm``/``±hhmm``)."""
    if not isinstance(value, str) or not ISO_TS_RE.match(value):
        return False
    if value.endswith("Z"):
        core = value[:-1]
    else:
        core, offset = value[:-6], value[-6:]
        if ":" not in offset:
            offset = offset[:3] + ":" + offset[3:]
        if int(offset[1:3]) > 23 or int(offset[4:6]) > 59:
            return False
    try:
        datetime.strptime(core, "%Y-%m-%dT%H:%M:%S")
        return True
    except ValueError:
        return False


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


class MalformedFlowError(ValueError):
    """Unbalanced, mismatched, or unterminated flow syntax."""


def _balanced(text: str) -> bool:
    stack, quote = [], ""
    for ch in text:
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack or stack.pop() != ("{" if ch == "}" else "["):
                return False
    return not stack and not quote


def parse_flow(text: str) -> Value:
    """Parse a flow value: ``{...}`` mapping, ``[...]`` list, or scalar.

    Malformed flow syntax (unclosed, mismatched, or with an unterminated
    quote) raises :class:`MalformedFlowError` so the caller reports K1.
    """
    t = text.strip()
    if t[:1] in ("}", "]"):
        raise MalformedFlowError(t)
    if t[:1] in ("{", "["):
        closer = "}" if t[0] == "{" else "]"
        inner = t[1:-1] if t.endswith(closer) else None
        if inner is None or not _balanced(inner):
            raise MalformedFlowError(t)
        if closer == "}":
            pairs = {}
            for part in _split_flow(inner):
                key, _, value = part.partition(":")
                pairs[key.strip()] = parse_flow(value)
            return pairs
        return [_unquote(part) for part in _split_flow(inner)]
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

    try:
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
                # Indented lines continue a block list item, open a block
                # mapping under a bare key, or extend an open block mapping.
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
    except MalformedFlowError:
        return None
    flush()
    return fm
