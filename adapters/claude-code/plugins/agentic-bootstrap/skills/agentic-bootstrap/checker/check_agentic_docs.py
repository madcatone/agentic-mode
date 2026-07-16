#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executable documentation-consistency gate (project-agnostic framework).

Prose checklists spread across README / AGENTS / docs tend to drift out of
sync -- the same test command written six different ways, a neutrality
checklist that nobody runs, requirement IDs that skip a number. This script
turns those checks into an executable gate so CI can catch doc rot on every
merge / pull request.

Everything project-specific (ID prefix, doc file names, bilingual headings,
entry points, command rules, deny words, URL allowlist) lives in an external
JSON config -- the framework code below never changes between projects. Copy
this file to ``scripts/check_agentic_docs.py`` in any repo, drop a
``agentic-mode/config.json`` next to it, and run::

    python scripts/check_agentic_docs.py --config agentic-mode/config.json

Each finding is printed as::

    <file>:<line>: [<category>] <message>

Exit status is ``0`` when nothing is found and ``1`` when there is at least one
finding (``2`` for a hard error such as a bad config or I/O failure). A
trailing summary reports the finding count per category.

Check categories
----------------
1. ``id-continuity`` -- in the configured requirements doc: ``<prefix>-NNN``
   IDs must be duplicate-free and gap-free from min to max. IDs cited in the
   user-guide and validation docs must exist in the requirements doc. When
   ``bilingual.enabled`` is true the two language regions must additionally
   carry identical ID sets; when false, no bilingual structure is required.
2. ``command-consistency`` -- each rule in ``checks.commands`` requires its
   ``run`` string to appear verbatim (inside a fenced code block or inline
   code) in every doc named by ``must_appear_in``.
3. ``neutrality`` -- across the full text: config ``deny_words`` plus (when
   ``harness_neutrality.enabled``) a conservative built-in harness deny list;
   plus, when ``url_allowlist`` is non-empty, http(s) URLs whose host is not
   on the allowlist; plus two opt-in leak sweeps -- ``checks.forbid_ipv4``
   flags IPv4 literals outside ``checks.ipv4_allowlist`` (default loopback /
   any-address), and ``checks.forbid_local_paths`` flags single-machine
   absolute paths (``~/.`` , ``/Users/`` , ``/home/``).
4. ``line-limit`` -- per-file maximum line counts from ``checks.line_limits``.
5. ``entrypoint`` -- each path in ``checks.entrypoints`` must exist; ``.py``
   files are additionally byte-compiled with ``py_compile``.
6. ``doc-presence`` -- every path declared under ``docs`` must exist (a value
   of ``null`` means "not used by this project" and is skipped).
7. ``iteration-continuity`` -- opt-in via ``checks.iteration_history.enabled``.
   Inside the requirements doc's Iteration History section (heading configurable
   via ``checks.iteration_history.heading``, default ``Iteration History``) the
   ``N.`` numbered entries must be duplicate-free and gap-free; when bilingual,
   each language region's history is checked independently.

Any line containing the marker ``agentic-gate: allow`` is skipped by every
text-scanning check, so rule/spec docs can quote a bad example on purpose.

Pure standard library, Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import sys
from typing import Dict, List, NamedTuple, Optional, Sequence, Set, Tuple


SCHEMA_VERSION = 1

# Line-level exemption marker. Any line containing this substring is skipped by
# every text-scanning check, so rule/spec docs can show a bad example on
# purpose.
ALLOW_MARKER = "agentic-gate: allow"

# Conservative built-in harness deny list, enabled via
# ``checks.harness_neutrality.enabled``. Kept deliberately narrow to avoid
# false positives: harness product names, model family names, and a couple of
# harness-proprietary tool names. Bare generic words like "agent" are
# intentionally NOT here. Matching is case-insensitive with word boundaries and
# is exemptible via ALLOW_MARKER; ``extra_deny`` extends the list per project.
HARNESS_DENY_WORDS: Tuple[str, ...] = (
    "claude code",
    "claude-code",
    "anthropic",
    "openai",
    "chatgpt",
    "copilot",
    "cursor",
    "windsurf",
    "codeium",
)

# Doc keys whose file paths are subject to text scanning / command lookup.
# ``architecture`` is excluded because it is JSON, not prose.
PROSE_DOC_KEYS: Tuple[str, ...] = (
    "index",
    "readme",
    "agents",
    "requirements",
    "user_guide",
    "validation",
    "workflow",
)

# Absolute http(s) URL; capture the host portion.
URL_RE = re.compile(r"https?://([^/\s)\"'`>\]]+)")

# IPv4 literal (validated for octet range at match time). Used only when
# ``checks.forbid_ipv4`` is enabled.
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# Single-machine absolute paths: ``~/.`` , ``/Users/...`` , ``/home/...``. Used
# only when ``checks.forbid_local_paths`` is enabled.
LOCAL_PATH_RE = re.compile(
    r"(?:(?<![\w/])~/\.[^\s)\"'`]*|(?<![\w])/(?:Users|home)/[^\s)\"'`]*)"
)

# Neutral IPv4 literals that never trip ``forbid_ipv4`` (loopback / any-address).
DEFAULT_IPV4_ALLOWLIST: Tuple[str, ...] = ("127.0.0.1", "0.0.0.0")

# Iteration-history numbered item: a line that begins with ``N.`` followed by
# whitespace. Used only when ``checks.iteration_history.enabled`` is true.
ITER_ITEM_RE = re.compile(r"^\s*(\d+)\.\s")


class Finding(NamedTuple):
    path: str          # repo-relative path for display
    line: int          # 1-based line number (0 when file-scoped)
    category: str
    message: str


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------
class ConfigError(Exception):
    """Raised when the config file is missing, malformed, or wrong schema."""


def load_config(config_path: str) -> Dict:
    """Load and lightly validate the JSON config.

    Missing optional keys are tolerated (callers use ``.get`` with defaults);
    a mismatched ``schema_version`` is a hard error so a v2 config never runs
    silently under v1 logic.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("config root must be a JSON object")

    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ConfigError(
            f"unsupported schema_version {version!r}; this checker handles "
            f"version {SCHEMA_VERSION}"
        )
    return data


def doc_paths(config: Dict) -> Dict[str, Optional[str]]:
    """Return the ``docs`` mapping (doc key -> repo-relative path or None)."""
    docs = config.get("docs", {})
    return docs if isinstance(docs, dict) else {}


def resolve(root: str, rel_path: Optional[str]) -> Optional[str]:
    """Join a repo-relative path onto ``root`` (None passes through)."""
    if not rel_path:
        return None
    return os.path.join(root, rel_path)


# ---------------------------------------------------------------------------
# File discovery and helpers
# ---------------------------------------------------------------------------
def discover_targets(root: str, config: Dict) -> List[str]:
    """Return absolute paths of the prose docs in scope, de-duplicated.

    Scope is exactly the prose doc paths declared in the config (index,
    readme, agents, requirements, user_guide, validation, workflow). Only
    existing files are returned; ``null`` / missing declarations are skipped.
    Unlike the original repo-specific version this does not walk directories
    -- the config is the single source of truth for which files are governed.
    """
    docs = doc_paths(config)
    targets: List[str] = []
    seen: Set[str] = set()
    for key in PROSE_DOC_KEYS:
        candidate = resolve(root, docs.get(key))
        if candidate and os.path.isfile(candidate) and candidate not in seen:
            seen.add(candidate)
            targets.append(candidate)
    return targets


def read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().splitlines()


def make_rel(root: str):
    """Return a function that renders paths relative to ``root`` for display."""
    def rel(path: str) -> str:
        return os.path.relpath(path, root)
    return rel


def in_code_block_flags(lines: Sequence[str]) -> List[bool]:
    """Return a per-line flag marking whether the line sits inside a fenced
    code block. Fence lines (``` ...) themselves are marked False so the
    delimiter itself is never treated as code content.
    """
    flags: List[bool] = []
    inside = False
    for line in lines:
        is_fence = line.lstrip().startswith("```")
        if is_fence:
            # The fence line itself is a boundary, not code content.
            flags.append(False)
            inside = not inside
        else:
            flags.append(inside)
    return flags


def code_spans(lines: Sequence[str]) -> List[str]:
    """Return the text of every location a command may legally live: full
    fenced-code lines plus the contents of inline ``code`` spans on any line.

    A command rule is satisfied if its ``run`` string appears verbatim inside
    one of these spans anywhere across the governed docs. Lines carrying the
    allow-marker are skipped so counter-examples do not count as fulfilment.
    """
    flags = in_code_block_flags(lines)
    spans: List[str] = []
    for idx, line in enumerate(lines):
        if ALLOW_MARKER in line:
            continue
        if flags[idx]:
            spans.append(line)
            continue
        # Inline code: everything between a pair of backticks on this line.
        for match in re.finditer(r"`([^`]+)`", line):
            spans.append(match.group(1))
    return spans


# ---------------------------------------------------------------------------
# 1. id-continuity
# ---------------------------------------------------------------------------
def _id_row_re(prefix: str) -> re.Pattern:
    """Match a requirement table row like ``| REQ-061 | ... |``.

    Anchoring to a leading table pipe (optionally preceded by whitespace)
    matches only definition rows, so prose citations such as ``(REQ-060)`` in
    an iteration-history paragraph are not miscounted as duplicate definitions.
    """
    return re.compile(r"^\s*\|\s*" + re.escape(prefix) + r"-(\d+)\b")


def _id_ref_re(prefix: str) -> re.Pattern:
    """Match any ``<prefix>-NNN`` reference anywhere on a line."""
    return re.compile(r"\b" + re.escape(prefix) + r"-(\d+)\b")


def _region_bounds(lines: Sequence[str], primary: str,
                   secondary: str) -> Optional[Tuple[int, int, int]]:
    """Locate the two bilingual region boundaries by their heading text.

    The requirements file is split by two headings whose exact stripped text
    is ``primary`` and ``secondary`` (e.g. ``## English`` / ``## 繁體中文``).
    Returns 0-based (primary_start, secondary_start, end) or None if the two
    headings are not both present with primary before secondary.
    """
    primary_start = secondary_start = None
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == primary and primary_start is None:
            primary_start = idx
        elif stripped == secondary and secondary_start is None:
            secondary_start = idx
    if (primary_start is None or secondary_start is None
            or secondary_start <= primary_start):
        return None
    return primary_start, secondary_start, len(lines)


def _collect_ids(lines: Sequence[str], start: int, end: int,
                 pattern: re.Pattern, rel, path: str,
                 kind: str) -> Tuple[Dict[int, int], List[Finding]]:
    """Collect integer IDs matched by ``pattern`` within ``lines[start:end]``.

    Returns a mapping id -> first-seen 1-based line number, plus findings for
    any duplicate ID (each duplicate reported at its own line). Allow-marked
    lines are skipped.
    """
    seen: Dict[int, int] = {}
    findings: List[Finding] = []
    for offset in range(start, end):
        line = lines[offset]
        if ALLOW_MARKER in line:
            continue
        match = pattern.match(line)
        if not match:
            continue
        value = int(match.group(1))
        lineno = offset + 1
        if value in seen:
            findings.append(Finding(
                rel(path), lineno, "id-continuity",
                f"duplicate {kind} id {value} (first seen at line {seen[value]})",
            ))
        else:
            seen[value] = lineno
    return seen, findings


def _gap_findings(seen: Dict[int, int], rel, path: str, kind: str,
                  region: str, region_line: int) -> List[Finding]:
    """Report every missing integer between min and max of the collected ids."""
    findings: List[Finding] = []
    if not seen:
        return findings
    lo, hi = min(seen), max(seen)
    for value in range(lo, hi + 1):
        if value not in seen:
            suffix = f" in {region} region" if region else ""
            findings.append(Finding(
                rel(path), region_line, "id-continuity",
                f"missing {kind} id {value}{suffix} (sequence {lo}..{hi} has a gap)",
            ))
    return findings


def check_id_continuity(root: str, config: Dict, rel,
                        contents: Dict[str, List[str]]) -> List[Finding]:
    """Validate requirement-ID continuity and cross-doc reference integrity.

    ``contents`` maps absolute path -> lines for the already-read prose docs.
    """
    findings: List[Finding] = []
    docs = doc_paths(config)
    req_path = resolve(root, docs.get("requirements"))
    if not req_path or req_path not in contents:
        return findings  # doc-presence check reports a missing requirements doc

    prefix = config.get("id", {}).get("prefix", "")
    if not prefix:
        findings.append(Finding(
            rel(req_path), 0, "id-continuity",
            "config id.prefix is empty; cannot check requirement IDs",
        ))
        return findings

    row_re = _id_row_re(prefix)
    ref_re = _id_ref_re(prefix)
    req_lines = contents[req_path]

    bilingual = config.get("bilingual", {})
    is_bilingual = bool(bilingual.get("enabled"))

    defined: Set[int] = set()

    if is_bilingual:
        primary = bilingual.get("primary_heading", "## English")
        secondary = bilingual.get("secondary_heading", "## 繁體中文")
        bounds = _region_bounds(req_lines, primary, secondary)
        if bounds is None:
            findings.append(Finding(
                rel(req_path), 0, "id-continuity",
                f"bilingual.enabled but could not locate both '{primary}' and "
                f"'{secondary}' region headings",
            ))
            return findings
        p_start, s_start, end = bounds
        p_ids, p_dups = _collect_ids(req_lines, p_start, s_start, row_re, rel,
                                     req_path, prefix)
        s_ids, s_dups = _collect_ids(req_lines, s_start, end, row_re, rel,
                                     req_path, prefix)
        findings.extend(p_dups)
        findings.extend(s_dups)
        findings.extend(_gap_findings(p_ids, rel, req_path, prefix, "primary",
                                      p_start + 1))
        findings.extend(_gap_findings(s_ids, rel, req_path, prefix, "secondary",
                                      s_start + 1))
        for value in sorted(set(p_ids) - set(s_ids)):
            findings.append(Finding(
                rel(req_path), p_ids[value], "id-continuity",
                f"{prefix} id {value} present in primary region but missing "
                "from secondary region",
            ))
        for value in sorted(set(s_ids) - set(p_ids)):
            findings.append(Finding(
                rel(req_path), s_ids[value], "id-continuity",
                f"{prefix} id {value} present in secondary region but missing "
                "from primary region",
            ))
        defined = set(p_ids) | set(s_ids)
    else:
        # Single-language repo: no bilingual structure is required or checked.
        ids, dups = _collect_ids(req_lines, 0, len(req_lines), row_re, rel,
                                 req_path, prefix)
        findings.extend(dups)
        findings.extend(_gap_findings(ids, rel, req_path, prefix, "", 0))
        defined = set(ids)

    # Cross-doc references: every <prefix>-NNN cited in user_guide / validation
    # must be defined in the requirements doc.
    for key in ("user_guide", "validation"):
        ref_path = resolve(root, docs.get(key))
        if not ref_path or ref_path not in contents:
            continue
        for idx, line in enumerate(contents[ref_path], start=1):
            if ALLOW_MARKER in line:
                continue
            for match in ref_re.finditer(line):
                value = int(match.group(1))
                if value not in defined:
                    findings.append(Finding(
                        rel(ref_path), idx, "id-continuity",
                        f"{key} references {prefix}-{match.group(1)} which is "
                        "not defined in the requirements doc",
                    ))
    return findings


# ---------------------------------------------------------------------------
# 1b. iteration-continuity (opt-in)
# ---------------------------------------------------------------------------
def _is_heading(line: str) -> bool:
    """A Markdown ATX heading line (``#`` .. ``######`` followed by space)."""
    stripped = line.lstrip()
    return bool(re.match(r"#{1,6}\s", stripped))


def check_iteration_history(root: str, config: Dict, rel,
                            contents: Dict[str, List[str]]) -> List[Finding]:
    """Validate the ``N.`` numbering of the Iteration History section(s).

    Opt-in via ``checks.iteration_history.enabled``. Each section is bounded by
    a heading whose text contains the configured phrase (default
    ``Iteration History``) and runs until the next heading. Within a section the
    numbered items must be duplicate-free and gap-free from min to max. Multiple
    sections (e.g. one per bilingual region) are each checked independently.
    """
    findings: List[Finding] = []
    checks = config.get("checks", {})
    iter_cfg = checks.get("iteration_history", {}) or {}
    if not iter_cfg.get("enabled"):
        return findings

    docs = doc_paths(config)
    req_path = resolve(root, docs.get("requirements"))
    if not req_path or req_path not in contents:
        return findings  # doc-presence reports a missing requirements doc

    heading_phrase = iter_cfg.get("heading", "Iteration History")
    lines = contents[req_path]

    # Locate every section start (heading containing the phrase) + its end.
    starts = [
        idx for idx, line in enumerate(lines)
        if _is_heading(line) and heading_phrase in line
    ]
    if not starts:
        findings.append(Finding(
            rel(req_path), 0, "iteration-continuity",
            f"iteration_history enabled but no heading containing "
            f"'{heading_phrase}' was found",
        ))
        return findings

    for start in starts:
        end = len(lines)
        for idx in range(start + 1, len(lines)):
            if _is_heading(lines[idx]):
                end = idx
                break
        seen: Dict[int, int] = {}
        for offset in range(start + 1, end):
            line = lines[offset]
            if ALLOW_MARKER in line:
                continue
            match = ITER_ITEM_RE.match(line)
            if not match:
                continue
            value = int(match.group(1))
            lineno = offset + 1
            if value in seen:
                findings.append(Finding(
                    rel(req_path), lineno, "iteration-continuity",
                    f"duplicate iteration entry {value} "
                    f"(first seen at line {seen[value]})",
                ))
            else:
                seen[value] = lineno
        if seen:
            lo, hi = min(seen), max(seen)
            for value in range(lo, hi + 1):
                if value not in seen:
                    findings.append(Finding(
                        rel(req_path), start + 1, "iteration-continuity",
                        f"missing iteration entry {value} "
                        f"(sequence {lo}..{hi} has a gap)",
                    ))
    return findings


# ---------------------------------------------------------------------------
# 2. command-consistency
# ---------------------------------------------------------------------------
def check_command_consistency(root: str, config: Dict, rel,
                              contents: Dict[str, List[str]]) -> List[Finding]:
    """Each command rule requires ``run`` to appear in every doc it names.

    A rule is::

        {"run": "<literal>", "must_appear_in": ["agents", "readme", ...]}

    The literal must occur inside a fenced code block or an inline code span in
    each named doc. A finding (scoped to the doc, line 0) is emitted per doc
    where it is absent.
    """
    findings: List[Finding] = []
    checks = config.get("checks", {})
    commands = checks.get("commands", []) or []
    docs = doc_paths(config)

    # Pre-compute the code spans of every prose doc once.
    spans_by_path: Dict[str, List[str]] = {
        path: code_spans(lines) for path, lines in contents.items()
    }

    for rule in commands:
        run = rule.get("run", "")
        targets = rule.get("must_appear_in", []) or []
        if not run:
            continue
        for key in targets:
            doc_path = resolve(root, docs.get(key))
            if not doc_path or doc_path not in spans_by_path:
                # The doc is not present at all; doc-presence reports that.
                findings.append(Finding(
                    key, 0, "command-consistency",
                    f"required command not found (doc '{key}' is missing): {run!r}",
                ))
                continue
            if not any(run in span for span in spans_by_path[doc_path]):
                findings.append(Finding(
                    rel(doc_path), 0, "command-consistency",
                    f"required command missing from a code block: {run!r}",
                ))
    return findings


# ---------------------------------------------------------------------------
# 3. neutrality
# ---------------------------------------------------------------------------
def _build_deny_words(config: Dict) -> List[Tuple[str, re.Pattern]]:
    """Return (display word, compiled word-boundary regex) for every deny word.

    Combines ``checks.deny_words`` with the built-in harness list (plus
    ``extra_deny``) when ``harness_neutrality.enabled`` is true. Matching is
    case-insensitive with word boundaries so a deny word is not tripped by a
    longer word that merely contains it.
    """
    checks = config.get("checks", {})
    words: List[str] = list(checks.get("deny_words", []) or [])

    harness = checks.get("harness_neutrality", {})
    if harness.get("enabled"):
        words.extend(HARNESS_DENY_WORDS)
        words.extend(harness.get("extra_deny", []) or [])

    compiled: List[Tuple[str, re.Pattern]] = []
    seen: Set[str] = set()
    for word in words:
        if not word or word.lower() in seen:
            continue
        seen.add(word.lower())
        pattern = re.compile(
            r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", re.IGNORECASE
        )
        compiled.append((word, pattern))
    return compiled


def check_neutrality(config: Dict, rel, path: str,
                     lines: Sequence[str],
                     deny: List[Tuple[str, re.Pattern]]) -> List[Finding]:
    """Flag deny-listed words and (when configured) non-allowlisted URL hosts.

    Two further sweeps are opt-in per config (both default off, so existing
    configs are unaffected): ``checks.forbid_ipv4`` flags IPv4 literals not on
    ``checks.ipv4_allowlist`` (default loopback / any-address), and
    ``checks.forbid_local_paths`` flags single-machine absolute paths. Both
    carry over the leak-detection behavior of the original repo-specific gate.
    """
    findings: List[Finding] = []
    checks = config.get("checks", {})
    url_allow = {h.lower() for h in checks.get("url_allowlist", []) or []}

    forbid_ipv4 = bool(checks.get("forbid_ipv4"))
    ipv4_allow = {
        a for a in (checks.get("ipv4_allowlist") or DEFAULT_IPV4_ALLOWLIST)
    }
    forbid_local_paths = bool(checks.get("forbid_local_paths"))

    for idx, line in enumerate(lines, start=1):
        if ALLOW_MARKER in line:
            continue

        # (a) deny-list words (case-insensitive, word-boundary).
        for original, pattern in deny:
            if pattern.search(line):
                findings.append(Finding(
                    rel(path), idx, "neutrality",
                    f"deny-list word '{original}' found",
                ))

        # (b) URLs with a non-allowlisted host (only when an allowlist is set).
        if url_allow:
            for match in URL_RE.finditer(line):
                host = match.group(1)
                host = host.split("@")[-1].split(":")[0].lower()
                if host not in url_allow:
                    findings.append(Finding(
                        rel(path), idx, "neutrality",
                        f"URL host '{host}' is not on the allowlist",
                    ))

        # (c) IPv4 literals outside the allowlist (opt-in leak sweep).
        if forbid_ipv4:
            for match in IPV4_RE.finditer(line):
                addr = match.group(0)
                if any(int(octet) > 255 for octet in addr.split(".")):
                    continue  # not a valid IPv4 (e.g. a version string)
                if addr not in ipv4_allow:
                    findings.append(Finding(
                        rel(path), idx, "neutrality",
                        f"IPv4 literal '{addr}' is not neutral",
                    ))

        # (d) single-machine absolute paths (opt-in leak sweep).
        if forbid_local_paths:
            for match in LOCAL_PATH_RE.finditer(line):
                findings.append(Finding(
                    rel(path), idx, "neutrality",
                    f"single-machine path '{match.group(0)}' should not be "
                    "hard-coded",
                ))
    return findings


# ---------------------------------------------------------------------------
# 4. line-limit
# ---------------------------------------------------------------------------
def check_line_limits(root: str, config: Dict, rel,
                      contents: Dict[str, List[str]]) -> List[Finding]:
    """Enforce per-file maximum line counts from ``checks.line_limits``.

    Keys may be a doc key (``AGENTS.md`` value resolved via config.docs is
    supported by also accepting a raw repo-relative path). The original config
    keys line limits by file basename / path; here we accept either a declared
    doc *path* or a doc *key* for convenience.
    """
    findings: List[Finding] = []
    checks = config.get("checks", {})
    limits = checks.get("line_limits", {}) or {}
    docs = doc_paths(config)

    # Build a lookup from both the doc-key and the doc-path to its absolute path.
    key_to_path: Dict[str, Optional[str]] = {}
    for key, value in docs.items():
        key_to_path[key] = resolve(root, value)
        if value:
            key_to_path[value] = resolve(root, value)  # allow path-keyed limits
            key_to_path[os.path.basename(value)] = resolve(root, value)

    for name, limit in limits.items():
        abs_path = key_to_path.get(name)
        if abs_path is None:
            abs_path = resolve(root, name)  # a raw path not declared in docs
        if not abs_path or not os.path.isfile(abs_path):
            findings.append(Finding(
                name, 0, "line-limit",
                f"line_limits target '{name}' does not resolve to a file",
            ))
            continue
        lines = contents.get(abs_path) or read_lines(abs_path)
        count = len(lines)
        if count > int(limit):
            findings.append(Finding(
                rel(abs_path), 0, "line-limit",
                f"file has {count} lines, exceeding the limit of {limit}",
            ))
    return findings


# ---------------------------------------------------------------------------
# 5. entrypoint existence + py_compile
# ---------------------------------------------------------------------------
def check_entrypoints(root: str, config: Dict, rel) -> List[Finding]:
    """Every entrypoint must exist; ``.py`` entrypoints must byte-compile."""
    findings: List[Finding] = []
    checks = config.get("checks", {})
    for entry in checks.get("entrypoints", []) or []:
        abs_path = resolve(root, entry)
        if not abs_path or not os.path.isfile(abs_path):
            findings.append(Finding(
                entry, 0, "entrypoint",
                "declared entrypoint does not exist",
            ))
            continue
        if abs_path.endswith(".py"):
            try:
                py_compile.compile(abs_path, doraise=True)
            except py_compile.PyCompileError as exc:
                findings.append(Finding(
                    rel(abs_path), 0, "entrypoint",
                    f"py_compile failed: {exc.msg}",
                ))
    return findings


# ---------------------------------------------------------------------------
# 6. doc-presence
# ---------------------------------------------------------------------------
def check_doc_presence(root: str, config: Dict, rel) -> List[Finding]:
    """Every declared doc path must exist; ``null`` means "not used" and skips."""
    findings: List[Finding] = []
    docs = doc_paths(config)
    for key, value in docs.items():
        if value is None:
            continue  # explicitly opted out
        abs_path = resolve(root, value)
        if not abs_path or not os.path.isfile(abs_path):
            findings.append(Finding(
                value, 0, "doc-presence",
                f"declared doc '{key}' does not exist",
            ))
    return findings


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def run(config_path: str, root_override: Optional[str]) -> int:
    config = load_config(config_path)
    root = root_override or os.path.dirname(os.path.abspath(config_path)) or "."
    # If the config lives in agentic-mode/, the repo root is its parent.
    if root_override is None:
        parent = os.path.dirname(os.path.dirname(os.path.abspath(config_path)))
        if parent:
            root = parent
    rel = make_rel(root)

    targets = discover_targets(root, config)
    contents: Dict[str, List[str]] = {path: read_lines(path) for path in targets}

    findings: List[Finding] = []

    # File-scoped structural checks first.
    findings.extend(check_doc_presence(root, config, rel))
    findings.extend(check_entrypoints(root, config, rel))
    findings.extend(check_line_limits(root, config, rel, contents))
    findings.extend(check_id_continuity(root, config, rel, contents))
    findings.extend(check_iteration_history(root, config, rel, contents))
    findings.extend(check_command_consistency(root, config, rel, contents))

    # Per-line neutrality scan across every governed prose doc.
    deny = _build_deny_words(config)
    for path in targets:
        findings.extend(check_neutrality(config, rel, path, contents[path], deny))

    # Stable ordering: file, then line, then category, then message.
    findings.sort(key=lambda f: (f.path, f.line, f.category, f.message))
    for finding in findings:
        print(f"{finding.path}:{finding.line}: [{finding.category}] {finding.message}")

    # Per-category summary.
    categories = (
        "id-continuity",
        "iteration-continuity",
        "command-consistency",
        "neutrality",
        "line-limit",
        "entrypoint",
        "doc-presence",
    )
    counts: Dict[str, int] = {}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1

    print("")
    print("Summary:")
    for category in categories:
        print(f"  {category}: {counts.get(category, 0)}")
    print(f"  total: {len(findings)}")

    return 1 if findings else 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executable documentation-consistency gate (config-driven).",
    )
    parser.add_argument(
        "--config",
        default="agentic-mode/config.json",
        help="path to the JSON config (default: agentic-mode/config.json)",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="repo root for resolving doc paths "
             "(default: the parent directory of the config file)",
    )
    return parser.parse_args(list(argv))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return run(args.config, args.root)
    except ConfigError as exc:
        print(f"check_agentic_docs: config error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:  # pragma: no cover - surfaced to CI as a hard error
        print(f"check_agentic_docs: I/O error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
