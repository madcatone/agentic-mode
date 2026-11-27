#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every template renders clean in every doc-set state; a rendered target proves its regions.

T1  every `*.template.md` under templates/ renders clean in all eight states of the three
    optional docs
T2  a rendered target proves its regions (RUNBOOK.md, "Upgrading the doc-set profile", step 4)

    python3 tests/check_template_renders.py               T1, then T2 on examples/minimal-cli
    python3 tests/check_template_renders.py --selftest    inject each fault into copies of the
                                                          real files and check that it goes red,
                                                          and that untouched copies stay clean
    python3 tests/check_template_renders.py --target DIR  T2 on one rendered target (after a
                                                          bootstrap, an adoption or an upgrade),
                                                          held against this checkout's templates/

The first two forms need this checkout's `examples/minimal-cli`; the selftest
also needs its doctrine. A copy vendored without them serves `--target` only.
Such a copy sits one directory below the directory that carries its own
`templates/`, and it exits 2 on the other two forms.

Output: one `<file>:<line>: [<category>] <message>` line per finding or notice, then a summary
line per part. Exit 0 clean, 1 a finding or a failed selftest check, 2 a usage or I/O error (a
directory that cannot be listed, an unusable config, a selftest anchor that no longer occurs
exactly once in the real file). Pure standard library.

What T1 proves, per template: every region is closed, not nested, spelled exactly, outside a
heading line (ATX or setext, a blockquote's too), and guarded by one of the three optional path
placeholders; an optional path placeholder appears only in the first branch of its own region;
no marker survives a render in any state. A marker inside a code fence or inline code is not a
marker to this script, and it is reported as residue: it would survive every render, so a
template cannot show the syntax in an example.

What T1 does not go red for: a list marker, a blockquote marker or an empty table cell that a
dropped region leaves on its line (doctrine :193 defines no such line), and an ATX heading
inside a list item, which is not known as a heading line.

What T2 proves, per doc that carries a `Template-Source` note, region by region, against this
checkout's template of the same name and version: for a declared layer the first branch is in
the doc and the stand-in is gone, searched for whole and sentence by sentence; for an undeclared
layer the first branch is gone, searched for on its own or, when it is only a path and too light
for that, as the template's line with a path where the region stood; no marker is left behind.
The note is the first HTML comment to carry `Template-Source:`: another comment or other content
may stand before it, and a BOM may open the file; what stands before the note stays the doc's
text and is searched. Upper and lower case are one on both sides. A doc whose note names another
version, or a template this checkout does not carry, is reported and not proven.

What T2 cannot prove; nothing is reported for it:
- a stand-in that was rewritten: only the template's wording of it is searched for;
- a bilingual span: the proof does not read `bilingual.enabled`, so a doc that keeps the text of
  a span the config turns off, or lacks the text of one it turns on, is not reported;
- the path of an undeclared layer that is only a path, when it is not alone where the region
  stood: beside the stand-in, or worded into the line. On a line that holds other regions too,
  the template's line is searched for as it spells them, so the path is found only where those
  are in the doc as first branches;
- a stale fill-in sentence, the prose written at bootstrap that describes the doc set: no
  search finds it, and step 4 leaves it to the reader;
- a stand-in left in another doc: each doc is searched for its own template's regions only;
- a doc without a `Template-Source` note, one no run rendered from a template or added pieces
  to: it is not searched. A note behind other comments or content, or under a BOM at the head
  of the file, is still found;
- a numbered list left unrenumbered by a dropped item: the doctrine's renumbering rule is for
  whoever renders a target. This script's reference renderer does not renumber, and no target
  is checked for it.
A translated doc cannot be proven either, and not every region of it is reported as unproven:
the notice goes out only for a declared layer whose first branch is not found in the doc, or an
undeclared layer whose stand-in is heavy enough to be searched for and is not found. A declared
layer with an empty first branch, and an undeclared layer without a stand-in, leave no notice.

`[unproven]` is a notice and never changes the exit code. It marks a region the proof could
not settle, so a reader must: a declared layer whose first branch is not in the doc where the
doc does not carry the template's text around that place, a first branch too short to search
for, or an undeclared layer whose stand-in a hand-written doc does not carry. It names the line
to start reading from, when the doc carries a template line above the place. `clean` means that
no defect this script can prove was found, not that every region is right: the summary line's
`regions` counts the regions the proof searched for something in, `unproven` those it could
not settle.

Known false positive: a hand-written sentence that happens to carry the wording of a first
branch (`target-first-branch-remains`; for a first branch that is only a path, a hand-written
line that follows the template's line and has any path where the region stood), or of a
stand-in or one of its sentences (`target-stand-in-remains`). Case is no difference to either.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from typing import Dict, Iterator, List, NamedTuple, Optional, Sequence, Set, Tuple

__all__ = ["main"]   # a script, not a library: the command line is its only interface

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the directory that carries templates/
TEMPLATES_DIR = os.path.join(REPO, "templates")
EXAMPLE_DIR = os.path.join(REPO, "examples", "minimal-cli")
DOCTRINE = os.path.join(REPO, "doctrine", "BOOTSTRAP-CORE.md")

# ---------------------------------------------------------------- 1. doctrine facts
# doctrine/BOOTSTRAP-CORE.md, "Conditional Text in Templates"
OPTIONAL = {                  # doctrine :191: placeholder -> the docs key that gives it a value
    "SURFACE_DOC_PATH": "user_guide",   # docs.api_reference for a library (state_from_config)
    "WORKFLOW_PATH": "workflow",
    "ARCHITECTURE_PATH": "architecture",
}
DOCTRINE_HEADING = "## Conditional Text in Templates"
_NAME = r"[A-Za-z_][A-Za-z0-9_]*"
MARKER_RE = re.compile(r"\{\{IF (%s)\}\}|\{\{(ELSE|END IF)\}\}" % _NAME)
BILING_RE = re.compile(r"\{\{IF_BILINGUAL: ((?:[^{}]|\{\{[^{}]*\}\})+)\}\}")
# Beyond the doctrine: shapes that look like a marker but are not an exact one. Canon
# placeholders may open with natural language ("{{If the component has ...}}",
# "{{if bilingual: ...}}"), so a lower- or title-case `if` counts only when exactly
# one name follows it.
_INNER = r"(?:[^{}]|\{\{[^{}]*\}\})*"   # what a misspelled marker may hold, one nested placeholder deep
NEAR_MISS = (
    (re.compile(r"\{\{\s*(?:end[\s_-]*if|else(?:\s?if(?:\s+%s)?)?|elif(?:if)?(?:\s+%s)?)\s*\}\}"
                % (_NAME, _NAME), re.I), "is not one of the exact markers"),
    (re.compile(r"\{\{\s*if\s+%s\s*\}\}" % _NAME, re.I),
     "is not the exact form {{IF <PLACEHOLDER>}}"),
    (re.compile(r"\{\{\s*IF(?![A-Za-z0-9_])%s\}\}" % _INNER),
     "is not the exact form {{IF <PLACEHOLDER>}}"),
    (re.compile(r"\{\{\s*IF[\s_-]*BILINGUAL(?![A-Za-z0-9_])%s\}\}" % _INNER),
     "is not the exact form {{IF_BILINGUAL: <text>}}"),
    (re.compile(r"\{\{\s*if[_-]?bilingual(?![A-Za-z0-9_])%s\}\}" % _INNER),
     "is not the exact form {{IF_BILINGUAL: <text>}}"),
    (re.compile(r"(?<!\{)\{\s*(?:end[\s_-]*if|else|if\s+%s|elif\s+%s)\s*\}(?!\})" % (_NAME, _NAME), re.I),
     "uses a single brace"),
)
SINGLE_BRACE_RE = NEAR_MISS[-1][0]
SOURCE_RE = re.compile(r"Template-Source:\s*agentic-bootstrap/([A-Za-z0-9_.-]+)@v(\d+)")


# ---------------------------------------------------------------- 2. types
class Fail(Exception):
    """Usage or I/O error: exit 2."""


class State(NamedTuple):
    """The value of each optional placeholder (doctrine :191): its config path, or None."""
    values: Dict[str, Optional[str]]
    bilingual: bool                     # bilingual.enabled (doctrine :195)

    def value(self, placeholder: str) -> Optional[str]:
        return self.values.get(placeholder)

    def label(self) -> str:
        return "%s, bilingual %s" % (", ".join("%s %s" % (p, "set" if self.value(p) else "null")
                                                 for p in OPTIONAL), self.bilingual)


class Token(NamedTuple):
    kind: str      # IF | ELSE | END | BILING | PH
    start: int     # offsets in the template body
    end: int
    arg: str       # IF and PH: placeholder name; BILING: the kept text
    line: int      # 1-based line of the template file


class Region(NamedTuple):
    placeholder: str
    line: int
    if_s: int
    if_e: int
    else_s: int    # -1 when the region has no {{ELSE}}
    else_e: int
    end_s: int
    end_e: int
    first: str     # "" when the first branch is empty
    stand: Optional[str]  # None when the region has no {{ELSE}}


class Parsed(NamedTuple):
    """A template whose regions can be trusted. Only a template without a structure finding
    gets one, and every function that reads regions takes this type: a broken template
    cannot reach the renderer, the path rule or the target proof."""
    name: str
    version: Optional[int]
    body: str
    line0: int                          # 1-based number of the body's first line
    tokens: Tuple[Token, ...]
    regions: Tuple[Region, ...]
    lines: Tuple[Tuple[int, int], ...]  # (start, end) offset of every body line
    skel: Tuple[str, ...]               # per line: regions and bilingual spans replaced by \x00
    frame: Tuple[int, ...]              # per line: word chars outside regions; -1 = inside a region

    def line_of(self, offset: int) -> int:
        return self.line0 + self.body.count("\n", 0, offset)


class Template(NamedTuple):
    name: str
    version: Optional[int]
    parsed: Optional[Parsed]            # None: a structure finding makes the regions untrustworthy
    findings: Tuple[Finding, ...]       # structure and marker findings, on the template's own lines


class OutLine(NamedTuple):
    text: str
    src: int


class Norm(NamedTuple):
    """Text as both sides of a comparison see it: a run of blanks is one space, a soft wrap
    one "\n", a paragraph break one "\n\n", typographic quotes ASCII ones."""
    text: str
    line: Tuple[int, ...]   # for every offset of `text`: the 1-based line it came from


class Pat(NamedTuple):
    narrow: "re.Pattern"    # a value never wraps
    wide: "re.Pattern"      # a value may soft-wrap inside the doc, never across a paragraph
    weight: int             # word characters of literal text (a bound path value counts)
    sample: str


class Finding(NamedTuple):
    file: str
    line: int
    category: str
    message: str

    def render(self) -> str:
        return "%s:%d: [%s] %s" % (self.file, self.line, self.category, self.message)


class Doc(NamedTuple):
    display: str
    name: str
    version: Optional[int]
    marker: int   # the line carrying the Template-Source marker
    norm: Norm    # the Template-Source note blanked, then normalised


class Report(NamedTuple):
    findings: List[Finding]
    notices: List[Finding]
    stats: Dict[str, int]


class Outcome(NamedTuple):
    findings: List[Finding]
    notice: Optional[Finding]
    searched: bool = False    # a pattern was searched for in the doc: the proof ran for this region


# ---------------------------------------------------------------- 3. lexing
FENCE_RE = re.compile(r" {0,3}(`{3,}|~{3,})")                     # a code fence line, opening or closing
HEADING_RE = re.compile(r" {0,3}#{1,6}(?:\s|$)")                  # an ATX heading line
# the line under a setext heading: the line above it is a heading line too
SETEXT_RE = re.compile(r" {0,3}(?:=+|-+)[ \t]*")
# the blockquote markers a line may open with, nested ones too: strip them before either test
BQUOTE_RE = re.compile(r"\A(?: {0,3}>[ \t]?)+")


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise Fail("cannot read %s: %s" % (path, exc))


def line_spans(text: str) -> List[Tuple[int, int]]:
    return [m.span() for m in re.finditer(r"[^\n]*\n?", text) if m.end() > m.start()]


def split_header(text: str) -> Tuple[int, str]:
    """(newlines inside the header comment, body). The header is not rendered."""
    m = re.match(r"\s*<!--.*?-->", text, re.S)
    return (0, text) if not m else (m.group(0).count("\n"), text[m.end():])


def _blank_fences(text: str, keep_delimiters: bool) -> str:
    out: List[str] = []
    fence: Optional[str] = None
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if fence is not None:
            if re.fullmatch(r" {0,3}%s{%d,}[ \t]*" % (re.escape(fence[0]), len(fence)), line):
                fence = None
                out.append(line if keep_delimiters else " " * len(line))
            else:
                out.append(" " * len(line))
        elif m:
            fence = m.group(1)
            out.append(line if keep_delimiters else " " * len(line))
        else:
            out.append(line)
    return "\n".join(out)


def unfenced(text: str) -> str:
    """Fenced blocks blanked (same length): braces inside a fence cannot swallow prose."""
    return _blank_fences(text, False)


def mask_code(text: str) -> str:
    """Code fences and inline code blanked: same length, same newlines."""
    return "\n".join(line if FENCE_RE.match(line) else mask_inline(line)
                     for line in _blank_fences(text, True).split("\n"))


def mask_inline(line: str) -> str:
    chars, i = list(line), 0
    while i < len(line):
        if line[i] != "`":
            i += 1
            continue
        j = i
        while j < len(line) and line[j] == "`":
            j += 1
        k, close = j, -1
        while k >= 0 and close < 0:            # a code span closes with a run of the same length
            k = line.find("`", k)
            if k < 0:
                break
            e = k
            while e < len(line) and line[e] == "`":
                e += 1
            if e - k == j - i:
                close = e
            k = e
        if close < 0:
            i = j
            continue
        for t in range(i, close):
            chars[t] = " "
        i = close
    return "".join(chars)


def _unquote(line: str) -> str:
    """A line without the blockquote markers it opens with."""
    m = BQUOTE_RE.match(line)
    return line[m.end():] if m else line


def brace_groups(text: str) -> Tuple[List[Tuple[int, int, str]], List[int]]:
    """(outermost balanced {{ ... }} groups, offsets of `{{` that nothing closes)."""
    groups: List[Tuple[int, int, str]] = []
    open_at: List[int] = []
    i = 0
    while i < len(text):
        if text.startswith("{{", i):
            open_at.append(i)
            i += 2
        elif text.startswith("}}", i) and open_at:
            s = open_at.pop()
            if not open_at:
                groups.append((s, i + 2, text[s + 2:i]))
            i += 2
        else:
            i += 1
    return groups, open_at


def marker_like(inner: str) -> bool:
    """A brace group that names a marker, exactly or misspelled, is never a placeholder."""
    group = "{{" + inner + "}}"
    return bool(MARKER_RE.fullmatch(group) or BILING_RE.fullmatch(group)
                or any(rx.fullmatch(group) for rx, _ in NEAR_MISS))


def lex(body: str) -> Tuple[List[Token], List[Tuple[int, str, str]]]:
    """Tokens in document order, plus (offset, category, message) for misspelled or broken braces.

    Markers count only in prose: inside a code fence or inline code they are text that
    survives a render (doctrine :194), so the per-state residue check reports them.
    """
    prose = mask_code(body)
    toks: List[Token] = []
    exact: set = set()
    for m in MARKER_RE.finditer(prose):
        exact.add(m.start())
        inner = m.group(0)[2:-2]
        toks.append(Token("END" if inner == "END IF" else "ELSE" if inner == "ELSE" else "IF",
                          m.start(), m.end(), "" if inner in ("ELSE", "END IF") else inner[3:],
                          body.count("\n", 0, m.start()) + 1))
    for m in BILING_RE.finditer(prose):
        exact.add(m.start())
        toks.append(Token("BILING", m.start(), m.end(), m.group(1), body.count("\n", 0, m.start()) + 1))
    problems: List[Tuple[int, str, str]] = []
    seen: set = set()
    for rx, why in NEAR_MISS:
        for m in rx.finditer(prose):
            # an exact marker matches these shapes too, and one misspelling matches several of
            # them: one finding per misspelled marker
            if m.start() not in exact and m.start() not in seen:
                seen.add(m.start())
                problems.append((m.start(), "marker-malformed", "`%s` %s" % (m.group(0), why)))
    # unlike a marker, an optional path placeholder is a token inside inline code too
    for s, e, inner in brace_groups(unfenced(body))[0]:
        if inner.strip() in OPTIONAL:
            toks.append(Token("PH", s, e, inner.strip(), body.count("\n", 0, s) + 1))
    for s in brace_groups(unfenced(body))[1]:
        problems.append((s, "render-residue", "`{{` has no closing `}}`"))
    toks.sort(key=lambda t: t.start)
    return toks, problems


# ---------------------------------------------------------------- 4. template model
def parse_template(name: str, text: str, rel: str) -> Template:
    """Structure findings carry the template's own line numbers. A template with one, or with
    a `{{` that nothing closes, gets no Parsed: no check that needs regions can run on it."""
    findings: List[Finding] = []
    newlines, body = split_header(text)
    line0 = newlines + 1
    src = SOURCE_RE.search(text[:len(text) - len(body)])
    version = int(src.group(2)) if src else None
    toks, problems = lex(body)
    tokens = [t._replace(line=t.line + newlines) for t in toks]
    for s, cat, msg in sorted(problems):
        findings.append(Finding(rel, line0 + body.count("\n", 0, s), cat, msg))
    broken = any(cat == "render-residue" for _, cat, _ in problems)
    prose = [_unquote(line) for line in mask_code(body).split("\n")]
    for no, line in enumerate(prose):
        setext = no + 1 < len(prose) and SETEXT_RE.fullmatch(prose[no + 1])
        if not HEADING_RE.match(line) and not setext:      # doctrine :192: none sits inside a heading line
            continue
        t = next((t for t in tokens if t.kind in ("IF", "ELSE", "END") and t.line == line0 + no), None)
        if t:
            findings.append(Finding(rel, t.line, "region-in-heading",
                                    "`%s` sits in a heading line" % body[t.start:t.end]))
    regions: List[Region] = []
    cur: Optional[Dict[str, int]] = None

    def stop(line: int, msg: str) -> None:
        nonlocal broken
        findings.append(Finding(rel, line, "region-structure", msg))
        broken = True

    for t in ([] if broken else tokens):
        shown = body[t.start:t.end]
        if t.kind == "IF":
            if t.arg not in OPTIONAL:              # doctrine :191: exactly three placeholders are optional
                stop(t.line, "%s guards a placeholder that is not one of the three optional ones" % shown)
            elif cur is not None:                  # doctrine :192: regions do not nest
                stop(t.line, "%s opens inside the region opened on line %d: regions do not nest, "
                             "or that region lacks {{END IF}}" % (shown, cur["line"]))
            else:
                cur = {"ph": t.arg, "line": t.line, "if_s": t.start, "if_e": t.end, "else_s": -1,
                       "else_e": -1}
        elif t.kind == "ELSE":
            if cur is None or cur["else_s"] >= 0:
                stop(t.line, "%s outside a region, or a second {{ELSE}} in one region" % shown)
            else:
                cur["else_s"], cur["else_e"] = t.start, t.end
        elif t.kind == "END":
            if cur is None:
                stop(t.line, "%s without an open {{IF ...}}" % shown)
            else:
                has_else = cur["else_s"] >= 0
                regions.append(Region(cur["ph"], cur["line"], cur["if_s"], cur["if_e"], cur["else_s"],
                                      cur["else_e"], t.start, t.end,
                                      body[cur["if_e"]:cur["else_s"] if has_else else t.start],
                                      body[cur["else_e"]:t.start] if has_else else None))
                cur = None
    if cur is not None and not broken:
        stop(cur["line"], "{{IF %s}} has no {{END IF}}" % cur["ph"])
    parsed: Optional[Parsed] = None
    if not broken:
        skel = list(body)
        for s, e in [(r.if_s, r.end_e) for r in regions] + [(t.start, t.end) for t in tokens
                                                            if t.kind == "BILING"]:
            skel[s:e] = ["\x00"] * (e - s)       # the sentinel to_pattern turns into a gap
        skel_lines, frame = [], []
        for a, b in line_spans(body):
            end = b - 1 if body[a:b].endswith("\n") else b
            bare = re.sub(r"\x00+", " ", "".join(skel[a:b]))
            for s, e, _ in brace_groups(bare)[0]:
                bare = bare[:s] + " " * (e - s) + bare[e:]
            inside = any(r.if_e <= a and end <= r.end_s for r in regions)
            frame.append(-1 if inside else len(re.findall(r"\w", bare)))
            skel_lines.append("".join(skel[a:b]))
        parsed = Parsed(name, version, body, line0, tuple(tokens), tuple(regions),
                        tuple(line_spans(body)), tuple(skel_lines), tuple(frame))
    return Template(name, version, parsed, tuple(findings))


def line_index(tmpl: Parsed, offset: int) -> int:
    return next(i for i, (a, b) in enumerate(tmpl.lines) if a <= offset < b)


def parse_templates(tdir: str, base: str = "templates") -> Dict[str, Template]:
    """Every *.template.md directly in `tdir`, in name order."""
    try:
        files = sorted(fn for fn in os.listdir(tdir) if fn.endswith(".template.md"))
    except OSError as exc:
        raise Fail("cannot list %s: %s" % (tdir, exc))
    canon: Dict[str, Template] = {}
    for fn in files:
        name = fn[:-len(".template.md")]
        canon[name] = parse_template(name, read(os.path.join(tdir, fn)), base + "/" + fn)
    return canon


# ---------------------------------------------------------------- 5. renderer
_TO_BITS = bytes.maketrans(bytes([0, 1]), b"01")  # the keep array as 0/1 text: 1-runs are kept text
_PUNCT = " \t\n.,;:!?)]}"                           # what may follow dropped inline text


def all_states(bilingual: bool = True) -> Iterator[State]:
    """The eight states of the three optional placeholders (doctrine :191), each with
    `bilingual.enabled` off and on when `bilingual` (doctrine :195)."""
    for bits in range(1 << len(OPTIONAL)):
        on = {p for i, p in enumerate(OPTIONAL) if bits >> i & 1}
        for bi in ((False, True) if bilingual else (False,)):
            yield State({p: sample_path(p) if p in on else None for p in OPTIONAL}, bi)


def sample_path(placeholder: str) -> str:
    """A value for T1's renders, derived from the placeholder's name (no second list)."""
    return "docs/" + placeholder.lower().replace("_", "-") + ".md"


def dummy(placeholder: str, st: State) -> Optional[str]:
    """What a placeholder is replaced with. None = it stays in the text as residue: an
    optional path without a value, or anything that names a marker."""
    if marker_like(placeholder):
        return None
    if placeholder in OPTIONAL:
        return st.value(placeholder)
    return "<" + re.sub(r"[^A-Za-z0-9]+", "-", placeholder).strip("-").lower()[:40] + ">"


def render(tmpl: Parsed, st: State) -> List[OutLine]:
    """Reference renderer for doctrine :193 (regions) and :195 (bilingual spans)."""
    body, keep, joins = tmpl.body, bytearray([1]) * len(tmpl.body), []
    for r in tmpl.regions:
        keep[r.if_s:r.if_e] = bytes(r.if_e - r.if_s)
        keep[r.end_s:r.end_e] = bytes(r.end_e - r.end_s)
        if st.value(r.placeholder) is not None:            # keep the first branch, drop the stand-in
            if r.else_s >= 0:
                keep[r.else_s:r.end_s] = bytes(r.end_s - r.else_s)
        elif r.stand is not None:                          # keep the stand-in, drop the first branch
            keep[r.if_e:r.else_e] = bytes(r.else_e - r.if_e)
        else:                                              # nothing is kept
            keep[r.if_e:r.end_s] = bytes(r.end_s - r.if_e)
        joins += [r.if_s, r.end_e]
    for t in tmpl.tokens:
        if t.kind == "BILING":
            if st.bilingual:
                opened = t.start + len("{{IF_BILINGUAL: ")
                keep[t.start:opened] = bytes(opened - t.start)
                keep[t.end - 2:t.end] = bytes(2)
            else:
                keep[t.start:t.end] = bytes(t.end - t.start)
                joins.append(t.start)
    # Beyond the doctrine: one space before dropped inline text goes when a space, punctuation
    # or the end of the line follows. The render the worked example carries does exactly this.
    for pos in joins:
        a = pos - 1
        while a >= 0 and not keep[a]:
            a -= 1
        b = pos
        while b < len(body) and not keep[b]:
            b += 1
        if (a >= 0 and body[a] in " \t" and "\n" not in body[a:pos]
                and (b >= len(body) or body[b] in " \t" + _PUNCT)):
            keep[a] = 0
    runs = [(m.start(), m.end()) for m in re.finditer("1+", keep.translate(_TO_BITS).decode())]
    rows, dropped, r = [], False, 0                       # (text, src line, a line was dropped before)
    for a, b in tmpl.lines:
        text = ""
        while r < len(runs) and runs[r][0] < b:
            s, e = runs[r]
            text += body[max(s, a):min(e, b)]
            if e > b:                       # the run goes on behind this line's end
                break
            r += 1
        if text.strip() == "" and body[a:b].strip():      # :193 a dropped region leaves no line behind
            dropped = True
            continue
        rows.append((text, tmpl.line_of(a), dropped))
        dropped = False
    out, i = [], 0
    while i < len(rows):                                  # :193 blank lines a dropped block leaves -> one
        if rows[i][0].strip() == "":
            j = i
            while j < len(rows) and rows[j][0].strip() == "":
                j += 1
            touched = any(rows[k][2] for k in range(i, min(j + 1, len(rows))))
            out += rows[i:(i + 1 if touched and j - i > 1 else j)]
            i = j
        else:
            out.append(rows[i])
            i += 1
    text = "".join(row[0] for row in out)
    for s, e, inner in reversed(brace_groups(text)[0]):
        val = dummy(inner.strip(), st)
        if val is not None:
            text = text[:s] + re.sub(r"[{}\n]", "", val) + text[e:]   # a value adds no braces, no lines
    pieces = text.split("\n")
    lines = [OutLine(piece + "\n", out[k][1]) for k, piece in enumerate(pieces[:-1])]
    return lines + ([OutLine(pieces[-1], out[-1][1])] if pieces[-1] else [])


# ---------------------------------------------------------------- 6. patterns
MIN_WEIGHT = 8                   # word characters a literal needs before it is searched for in a doc
PIECE_MIN_CHARS, PIECE_MIN_WORDS = 16, 4   # a stand-in's piece also needs this many characters and words
_CUT_PLACEHOLDER = re.compile(r"\{\{[^{}]*\}\}")
_CUT_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_FUNCTION_WORDS = frozenset("and or but the a an of to in with for per".split())
_SENTENCE_END = re.compile(r"[.!?]")
_LETTER = re.compile(r"[^\W\d_]")                         # a letter: digits alone are not a statement
# A doc may type a typographic quote or a dash the ASCII way: both sides read them the same.
FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"})
_EDGE_A, _EDGE_B = r"(?<![A-Za-z0-9_])", r"(?![A-Za-z0-9_])"   # a literal does not start or end inside a word
# A gap is the text standing for one placeholder. In the normalised text a line break is
# "\n" and a paragraph break "\n\n", so "a value may wrap, but not across a paragraph" is
# one lookahead.
_GAP = {"value": r"[^\n]*?", "wrapped": r"(?:[^\n]|\n(?!\n))*?", "path": r"[^ \n]+?", "any": r"[\s\S]*?"}


def normalize(text: str) -> Norm:
    """Beyond the doctrine. A doc goes through this one function and template text becomes a
    pattern by the same rules (`to_pattern`), so that a soft wrap, a double space, a
    typographic quote or a dash typed as a hyphen on either side is no difference. Every
    pattern is compiled with `re.I`: a first branch typed in another case is no difference
    either."""
    out, lines, i, n, line = [], [], 0, len(text), 1
    while i < n:
        j = i + 1
        if text[i] in " \t\n":
            while j < n and text[j] in " \t\n":
                j += 1
            piece = (" ", "\n", "\n\n")[min(text.count("\n", i, j), 2)]
        else:
            piece = text[i].translate(FOLD)
        out.append(piece)
        lines += [line] * len(piece)
        line += text.count("\n", i, j)
        i = j
    return Norm("".join(out), tuple(lines))


def to_pattern(text: str, bind: Optional[Dict[str, Optional[str]]] = None) -> Pat:
    """Template text -> regexes over normalised text. \x00 runs and placeholders become gaps;
    an optional path placeholder with a value is bound to that value, without one it is a path.
    A literal that begins or ends in a word may not begin or end inside a doc's word."""
    bind = bind or {}
    items: List[Tuple[str, str]] = []                    # ("lit", text) | ("ws", blanks) | ("gap", kind)
    weight = 0
    for n, piece in enumerate(re.split(r"\x00+", text.strip())):
        if n:                                            # what stood between two pieces: a gap
            items.append(("gap", "value"))
        pos = 0
        for s, e, inner in brace_groups(piece)[0]:
            weight += _literal(items, piece[pos:s])
            val = bind.get(inner.strip(), False)
            if val:
                weight += _literal(items, val)
            else:
                items.append(("gap", "path" if val is None else "value"))
            pos = e
        weight += _literal(items, piece[pos:])

    def neighbour(i: int, step: int) -> Optional[Tuple[str, str]]:
        """The nearest item that is not blanks: what a literal touches at that side."""
        k = i + step
        while 0 <= k < len(items) and items[k][0] == "ws":
            k += step
        return items[k] if 0 <= k < len(items) else None

    def compose(wrapped: bool) -> "re.Pattern":
        """Group 1 is the pattern's first word: a finding names the line it sits on, never the
        line above, where a pattern that opens on a gap may open its match."""
        out = []
        first = next((i for i, (kind, _) in enumerate(items) if kind == "lit"), None)
        for i, (kind, val) in enumerate(items):
            if kind == "gap":
                out.append(_GAP["wrapped" if wrapped and val == "value" else val])
                continue
            if kind == "ws":
                out.append("\\n\\n" if val.count("\n") > 1 else "(?: |\\n)")
                continue
            before, after = neighbour(i, -1), neighbour(i, 1)
            if re.match(r"[A-Za-z0-9_]", val) and (before is None or before[0] == "gap"):
                out.append(_EDGE_A)
            word = re.escape(val.translate(FOLD))
            out.append(("(" + word + ")") if i == first else word)
            if re.search(r"[A-Za-z0-9_]\Z", val) and (after is None or after[0] == "gap"):
                out.append(_EDGE_B)
        return re.compile("()" + "".join(out) if first is None else "".join(out), re.I)
    sample = re.sub(r"\s+", " ", text.replace("\x00", "[…]"))[:70]
    return Pat(compose(False), compose(True), weight, sample)


def _literal(items: List[Tuple[str, str]], text: str) -> int:
    weight = 0
    for run in re.findall(r"\s+|\S+", text):
        items.append(("ws", run) if run.isspace() else ("lit", run))
        weight += 0 if run.isspace() else len(re.findall(r"\w", run))
    return weight


def stand_in_pieces(first: str, stand: str, bind: Dict[str, Optional[str]]) -> List[Pat]:
    """The stand-in cut where a placeholder stood, then at sentence ends, each piece a pattern
    of its own: what is left when a stand-in was only partly removed. Kept are the pieces that
    state something (`_is_statement`)."""
    shared = {" ".join(sentence.split()) for literal in _CUT_PLACEHOLDER.split(first)
              for sentence in _CUT_SENTENCE.split(literal)}
    out: List[Pat] = []
    for literal in _CUT_PLACEHOLDER.split(stand):
        for raw in _CUT_SENTENCE.split(literal):
            piece = raw.strip()
            if _is_statement(piece, shared):
                pat = to_pattern(piece, bind)
                if pat.weight >= MIN_WEIGHT:
                    out.append(pat)
    return out


def _is_statement(piece: str, shared: Set[str]) -> bool:
    """Whether a stand-in piece states something of its own, so that finding it in a doc is
    evidence of the stand-in: long enough and holding a letter; not a clause a placeholder cut
    off (it ends in a function word and no sentence end follows); not a lead-in the first
    branch shares with the stand-in."""
    words = list(re.finditer(r"\w+", piece))
    if (len(piece) < PIECE_MIN_CHARS or len(words) < PIECE_MIN_WORDS or not _LETTER.search(piece)
            or " ".join(piece.split()) in shared):
        return False
    cut_off = (words[-1].group().lower() in _FUNCTION_WORDS
               and not _SENTENCE_END.search(piece[words[-1].end():]))
    return not cut_off


def join(left: Pat, right: Pat) -> Pat:
    """A whole-line region's site: the template line above and the one below, anything between."""
    whole = left.narrow.pattern + _GAP["any"] + right.narrow.pattern
    return Pat(re.compile(whole, re.I), re.compile(whole, re.I), 0, "site")


def find(text: str, pat: Optional[Pat]) -> Optional[int]:
    """Offset in the normalised text of the first word of the first match of the narrow pattern,
    or None."""
    m = pat.narrow.search(text) if pat is not None else None
    return m.start(1) if m else None


def carries(text: str, pat: Optional[Pat]) -> bool:
    """Whether the wide pattern matches. Only when this is false may something be called
    missing."""
    return pat is not None and pat.wide.search(text) is not None


def line_of(norm: Norm, offset: int) -> int:
    return norm.line[offset]


# ---------------------------------------------------------------- 7. T1
def optional_path_findings(tmpl: Parsed, rel: str) -> List[Finding]:
    """doctrine :194: an optional path placeholder may appear only inside the first branch of
    its own region. A stand-in is kept only when the placeholder has no value, so a path
    inside it would name a doc the doc-set does not carry."""
    out: List[Finding] = []
    cur: Optional[Region] = None
    stand = False                    # inside the stand-in of the open region
    for t in tmpl.tokens:
        if t.kind == "IF":
            cur, stand = next(r for r in tmpl.regions if r.if_s == t.start), False
        elif t.kind == "ELSE":
            stand = True
        elif t.kind == "END":
            cur = None
        elif t.kind == "PH" and (cur is None or cur.placeholder != t.arg or stand):
            if cur is None:
                where = "outside any region"
            elif cur.placeholder != t.arg:
                where = "inside the region for %s" % cur.placeholder
            else:
                where = ("inside the stand-in of its own region, and a stand-in is kept only when "
                         "`{{%s}}` has no value" % t.arg)
            out.append(Finding(rel, t.line, "optional-path-outside-region",
                               "`{{%s}}` sits %s" % (t.arg, where)))
    return out


def residue_findings(tmpl: Parsed, rel: str) -> Tuple[List[Finding], int]:
    """Render the template in all eight states of the optional docs, the bilingual axis only
    for a template that carries a bilingual span; nothing spelled with braces may survive
    (doctrine :194, RUNBOOK Phase-C placeholder sweep)."""
    out, seen, renders = [], set(), 0
    bilingual = any(t.kind == "BILING" for t in tmpl.tokens)
    for st in all_states(bilingual):
        renders += 1
        for line in render(tmpl, st):
            if ("{{" in line.text or SINGLE_BRACE_RE.search(line.text)) and line.src not in seen:
                seen.add(line.src)
                out.append(Finding(rel, line.src, "render-residue",
                                   "brace group survives rendering (%s)" % st.label()))
    return out, renders


def template_report(canon: Dict[str, Template], base: str = "templates") -> Report:
    """T1: every template's structure findings, then the path rule and the render of each
    template whose regions can be trusted."""
    findings = structure_findings(canon)
    stats = {"files": len(canon), "regions": 0, "renders": 0}
    for name, tmpl in canon.items():
        rel = "%s/%s.template.md" % (base, name)
        if tmpl.parsed is None:
            continue
        stats["regions"] += len(tmpl.parsed.regions)
        findings += optional_path_findings(tmpl.parsed, rel)
        found, renders = residue_findings(tmpl.parsed, rel)
        findings += found
        stats["renders"] += renders
    return Report(findings, [], stats)


# ---------------------------------------------------------------- 8. T2
def state_from_config(config: dict) -> State:
    """doctrine :191: which optional placeholders have a value in this target."""
    docs = config.get("docs") if isinstance(config, dict) else None
    if not isinstance(docs, dict):
        raise Fail("`docs` in config.json is missing or not an object")

    def part(name: str) -> dict:
        val = config.get(name)
        if val is not None and not isinstance(val, dict):
            raise Fail("`%s` in config.json is not an object" % name)
        return val or {}

    keys = dict(OPTIONAL)
    if part("project").get("type") == "library":
        keys["SURFACE_DOC_PATH"] = "api_reference"

    def path(key: str) -> Optional[str]:
        val = docs.get(key)
        if val is not None and (not isinstance(val, str) or not val.strip()):
            raise Fail("`docs.%s` must be a path or null" % key)
        return val
    return State({p: path(key) for p, key in keys.items()}, bool(part("bilingual").get("enabled")))


def discover_docs(root: str) -> List[Doc]:
    """Every doc rendered from a template carries its Template-Source marker (RUNBOOK :413),
    and so does a doc that gained the template's pieces (RUNBOOK :378)."""
    docs: List[Doc] = []

    def unreadable(exc: OSError) -> None:       # a directory that cannot be listed is not a clean target
        raise Fail("cannot list %s: %s" % (exc.filename, exc))

    for dirpath, dirnames, filenames in os.walk(root, onerror=unreadable):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d != "node_modules")
        for fn in sorted(filenames):
            if not fn.endswith(".md") or fn.endswith(".template.md"):
                continue
            text = read(os.path.join(dirpath, fn))
            # the first HTML comment to carry the note, not the file's first: another comment or
            # text may stand above it, and that stays in the doc as its own text
            note = next((c for c in re.finditer(r"<!--(.*?)-->", text, re.S)
                         if "Template-Source:" in c.group(1)), None)
            if note is None:
                continue                  # a hand-written doc carries no marker: nothing to prove
            src = SOURCE_RE.search(note.group(1))
            # RUNBOOK :403: the Template-Source note is not searched: it quotes a stand-in
            docs.append(Doc(os.path.relpath(os.path.join(dirpath, fn), root), src.group(1) if src else "",
                            int(src.group(2)) if src else None,
                            text.count("\n", 0, note.start(1) + src.start()) + 1 if src else 1,
                            normalize(text[:note.start()] + re.sub(r"[^\n]", " ", note.group(0))
                                      + text[note.end():])))
    return docs


def site_of(tmpl: Parsed, region: Region, bind: Dict[str, Optional[str]]) -> Optional[Pat]:
    """The template text around the region, the region itself left open: what a doc must
    carry for a missing first branch to count as a fault. An inline region is recognised by
    the rest of its own line, a whole-line region by the heavy line on each side of it."""
    idx = line_index(tmpl, region.if_s)
    if tmpl.frame[idx] >= MIN_WEIGHT:
        return to_pattern(tmpl.skel[idx], bind)

    def anchor(i: int, step: int) -> Optional[Pat]:
        while 0 <= i < len(tmpl.lines):
            if tmpl.frame[i] >= MIN_WEIGHT:
                return to_pattern(tmpl.skel[i], bind)
            i += step
        return None
    left, right = anchor(idx - 1, -1), anchor(idx + 1, 1)
    return join(left, right) if left is not None and right is not None else None


def locate(norm: Norm, site: Optional[Pat]) -> Optional[int]:
    """The doc line that carries the site's first word, or None: the doc does not follow the
    template there."""
    hit = find(norm.text, site)
    return line_of(norm, hit) if hit is not None else None


def _excerpt(pat: Optional[Pat]) -> str:
    return "\"%s\"" % (pat.sample if pat else "")


def _where(tmpl: Template, region: Region) -> str:
    return "%s region (templates/%s.template.md:%d)" % (region.placeholder, tmpl.name, region.line)


def near_line(tmpl: Parsed, doc: Doc, region: Region, bind: Dict[str, Optional[str]]) -> Optional[int]:
    """The doc line that carries the nearest template line above the region: where a reader
    starts when the place itself is not recognised."""
    for i in range(line_index(tmpl, region.if_s) - 1, -1, -1):
        if tmpl.frame[i] >= MIN_WEIGHT:
            hit = find(doc.norm.text, to_pattern(tmpl.skel[i], bind))
            if hit is not None:
                return line_of(doc.norm, hit)
    return None


def first_branch_shape(tmpl: Parsed, region: Region, bind: Dict[str, Optional[str]]) -> Pat:
    """The template's own line with the region replaced by its first branch. For a first branch
    that is only a path, too light to be searched for on its own: a doc that keeps the
    template's line there and a path where the region stood names a doc it does not seed."""
    a, b = tmpl.lines[line_index(tmpl, region.if_s)]
    return to_pattern(tmpl.body[a:region.if_s] + region.first + tmpl.body[region.end_e:b], bind)


def _holds_stand_in(doc: Doc, stand: Optional[Pat], hit: "re.Match") -> bool:
    """Whether a first branch's shape was found in the stand-in's own line: the stand-in lies
    inside the hit, so the path is the stand-in's, not a first branch that remains."""
    return stand is not None and any(hit.start() <= s.start() and s.end() <= hit.end()
                                     for s in stand.wide.finditer(doc.norm.text))


def prove_region(tmpl: Parsed, doc: Doc, region: Region, st: State, rel: str) -> Outcome:
    """RUNBOOK step 4, run both ways. Declared: first branch in, stand-in gone. Undeclared:
    first branch out (doctrine :187). A missing stand-in is reported, not failed: a
    hand-written doc, or a line the template says to delete, does not carry one.

    The stand-in is searched for whole, then sentence by sentence (`stand_in_pieces`): one
    that was only partly removed is still a stand-in that remains.

    A first branch that is only a path is too light to be searched for on its own. For an
    undeclared layer it is searched for as the template's own line, the path left open where
    the region stood (`first_branch_shape`), except where the stand-in lies inside that line:
    a stand-in that is one path in backticks has the same shape as such a first branch.

    Both ways lean towards not reporting, and only evidence fails: a `remains` finding needs
    the narrow pattern to hit (`find`: a value does not wrap), a missing first branch is
    stated only when the wide pattern misses (`carries`: even a wrapped value counts as there).
    A first branch that is not in the doc fails only where the doc carries the template's
    text around that place (site_of); anywhere else the doc may have been rewritten or
    translated, and the region is reported as unproven.

    `Outcome.searched` says whether anything at all was searched for in the doc. A region
    where nothing is has nothing to go wrong, so `check_target` counts only the others."""
    bind = st.values
    first = to_pattern(region.first, bind) if region.first.strip() else None
    stand = to_pattern(region.stand, bind) if region.stand and region.stand.strip() else None

    def heavy(pat: Optional[Pat]) -> bool:
        return pat is not None and pat.weight >= MIN_WEIGHT

    def unproven(message: str, excerpt: str = "") -> Finding:
        """A notice: nothing is proven, so nothing fails. It names the line a reader starts at."""
        hint = near_line(tmpl, doc, region, bind)
        return Finding(rel, hint or 1, "unproven", message
                       + (", starting after line %d" % hint if hint else "")
                       + (" (%s)" % excerpt if excerpt else ""))

    found: List[Finding] = []
    notice: Optional[Finding] = None
    ran = False
    if st.value(region.placeholder) is not None:
        if first is not None and not carries(doc.norm.text, first):    # RUNBOOK :403: must be in the doc
            if first.weight < MIN_WEIGHT:
                notice = unproven("the first branch of the %s is too short to search for"
                                  % _where(tmpl, region))
            else:
                line = locate(doc.norm, site_of(tmpl, region, bind))
                if line is not None:
                    found.append(Finding(rel, line, "target-first-branch-missing",
                                         "the first branch of the %s is not in this doc: %s"
                                         % (_where(tmpl, region), _excerpt(first))))
                else:
                    notice = unproven("the first branch of the %s is not in this doc, and the doc "
                                      "does not carry the template's text around that place: check it "
                                      "by hand" % _where(tmpl, region), _excerpt(first)[1:-1])
        # RUNBOOK :403: the stand-in must be gone
        patterns = [stand]
        if stand is not None:
            patterns += stand_in_pieces(region.first, region.stand, bind)
        for pat in patterns:
            hit = find(doc.norm.text, pat) if heavy(pat) else None
            if hit is not None:
                found.append(Finding(rel, line_of(doc.norm, hit), "target-stand-in-remains",
                                     "the stand-in of the %s is still in this doc: %s"
                                     % (_where(tmpl, region), _excerpt(pat))))
                break
        ran = first is not None or any(heavy(pat) for pat in patterns)
    else:
        if heavy(stand) and not carries(doc.norm.text, stand):
            notice = unproven("the stand-in of the %s is not in this doc; expected when the doc is "
                              "hand-written or the line was deleted on the template's instruction"
                              % _where(tmpl, region))
        hit = find(doc.norm.text, first) if heavy(first) else None
        shape = first
        if hit is None and first is not None:
            shape = first_branch_shape(tmpl, region, bind)
            m = shape.narrow.search(doc.norm.text) if heavy(shape) else None
            hit = m.start(1) if m and not _holds_stand_in(doc, stand, m) else None
        ran = heavy(stand) or heavy(shape)
        if hit is not None:                                 # doctrine :187: dropped when it has no value
            found.append(Finding(rel, line_of(doc.norm, hit), "target-first-branch-remains",
                                 "%s has no value in config, yet this doc carries the first branch "
                                 "of the %s: %s" % (region.placeholder, _where(tmpl, region),
                                                    _excerpt(shape))))
    return Outcome(found, notice, ran)


def marker_residue(doc: Doc, rel: str) -> List[Finding]:
    """A rendered doc keeps no marker, in any spelling (RUNBOOK Phase-C placeholder sweep)."""
    out: List[Finding] = []
    exact = {m.start() for m in BILING_RE.finditer(doc.norm.text)}
    seen: set = set()
    for m in MARKER_RE.finditer(doc.norm.text):
        exact.add(m.start())
        out.append(Finding(rel, line_of(doc.norm, m.start()), "target-marker-residue",
                           "`%s` left in the rendered doc" % m.group(0)))
    for rx, why in NEAR_MISS:
        for m in rx.finditer(doc.norm.text):
            if m.start() not in exact and m.start() not in seen:
                seen.add(m.start())
                out.append(Finding(rel, line_of(doc.norm, m.start()), "target-marker-residue",
                                   "`%s` %s" % (m.group(0), why)))
    return out


def structure_findings(canon: Dict[str, Template]) -> List[Finding]:
    return [f for tmpl in canon.values() for f in tmpl.findings]


def check_target(root: str, canon: Dict[str, Template]) -> Report:
    """T2: prove every doc of a rendered target that carries a Template-Source marker."""
    if not os.path.isdir(root):
        raise Fail("%s is not a directory" % root)
    try:
        st = state_from_config(json.loads(read(os.path.join(root, "agentic-mode", "config.json"))))
    except ValueError as exc:
        raise Fail("the config of %s is unusable: %s" % (root, exc))
    findings: List[Finding] = []
    notices: List[Finding] = []
    stats = {"docs": 0, "regions": 0, "unproven": 0}
    for doc in discover_docs(root):
        stats["docs"] += 1
        tmpl = canon.get(doc.name)
        if tmpl is None or tmpl.version != doc.version:
            # RUNBOOK :393: the docs must first be at the toolkit's current template versions
            findings.append(Finding(doc.display, doc.marker, "target-template-version" if tmpl else
                                    "target-unknown-template", "rendered from %s@v%s; this toolkit "
                                    "carries %s" % (doc.name, doc.version, "%s@v%s" % (doc.name, tmpl.version)
                                                    if tmpl else "no such template")))
            continue
        findings += marker_residue(doc, doc.display)
        if tmpl.parsed is None:
            continue                 # its structure finding is reported with the templates
        for region in tmpl.parsed.regions:
            out = prove_region(tmpl.parsed, doc, region, st, doc.display)
            stats["regions"] += out.searched
            findings += out.findings
            if out.notice is not None:
                notices.append(out.notice)
                stats["unproven"] += 1
    return Report(findings, notices, stats)


# ---------------------------------------------------------------- 9. selftest
def doctrine_paths() -> Set[str]:
    """The optional path placeholders doctrine names. Doctrine is the only definition of the
    syntax, so the selftest holds OPTIONAL against it: a fourth one in doctrine must fail
    until this script knows it too."""
    text = read(DOCTRINE)
    if DOCTRINE_HEADING not in text or "\n## " not in text.split(DOCTRINE_HEADING, 1)[1]:
        raise Fail("%s no longer carries the section %r" % (DOCTRINE, DOCTRINE_HEADING))
    section = text.split(DOCTRINE_HEADING, 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"\b[A-Z][A-Z0-9_]*_PATH\b", section))


class Mutation(NamedTuple):
    fault: str            # F1..F6; R1, R2 = the reverse rule: a layer is not declared, its first branch is
    what: str             #   still in the doc (R1: withdrawn from the config; R2: only a path)
    tree: str             # "templates" | "example"
    file: str             # the file mutated, and where the finding must land ...
    find: str             # ... must occur exactly once in the real file
    replace: str
    expect: Optional[str]  # the category that must go red; None: the edit is no fault, nothing may
    offset: int = 0       # finding line = line of `find` in the real file + offset
    where: str = ""       # ... unless the finding lands in another file (R1)


T1 = (
    Mutation("F1", "optional path named outside its region", "templates", "AGENTS.template.md",
             "- Docs coherence gate: `python3 scripts/check_agentic_docs.py --config agentic-mode/config.json`",
             "- Docs coherence gate: `python3 scripts/check_agentic_docs.py --config agentic-mode/config.json`"
             " (see `{{WORKFLOW_PATH}}`)", "optional-path-outside-region"),
    Mutation("F1", "optional path named inside its own stand-in", "templates", "AGENTS.template.md",
             "no WORKFLOW doc is seeded, so this section is the whole review policy.",
             "no WORKFLOW doc is seeded at `{{WORKFLOW_PATH}}`, so this section is the whole review "
             "policy.", "optional-path-outside-region"),
    Mutation("F2", "region never closed", "templates", "AGENTS.template.md",
             "- `{{SURFACE_DOC_PATH}}`: observable surface ({{SURFACE_DOC_ROLE}}).{{END IF}}",
             "- `{{SURFACE_DOC_PATH}}`: observable surface ({{SURFACE_DOC_ROLE}}).", "region-structure", 2),
    Mutation("F2", "END IF without IF", "templates", "AGENTS.template.md",
             "above{{IF WORKFLOW_PATH}} and per `{{WORKFLOW_PATH}}`{{END IF}}. **Boundary test:**",
             "above and per `{{WORKFLOW_PATH}}`{{END IF}}. **Boundary test:**", "region-structure"),
    Mutation("F2", "nested regions", "templates", "README.template.md",
             "{{IF SURFACE_DOC_PATH}}- Observable surface: `{{SURFACE_DOC_PATH}}`{{ELSE}}"
             "- Observable surface: the requirement rows in `{{REQUIREMENTS_PATH}}`{{END IF}}",
             "{{IF ARCHITECTURE_PATH}}{{IF SURFACE_DOC_PATH}}- Observable surface: `{{SURFACE_DOC_PATH}}`"
             "{{ELSE}}- Observable surface: the requirement rows in `{{REQUIREMENTS_PATH}}`{{END IF}}{{END IF}}",
             "region-structure"),
    Mutation("F2", "misspelled marker", "templates", "AGENTS.template.md",
             "- `{{WORKFLOW_PATH}}`: platform review loop (see Change Flow below).{{END IF}}",
             "- `{{WORKFLOW_PATH}}`: platform review loop (see Change Flow below).{{ENDIF}}",
             "marker-malformed"),
    Mutation("F2", "marker quoted in code survives every render", "templates", "README.template.md",
             "- Resident index: `{{INDEX_PATH}}`",
             "- Resident index: `{{INDEX_PATH}}`\n\nClose a region with `{{END IF}}`.", "render-residue", 2),
    Mutation("F2", "marker quoted in code that opens the line survives every render", "templates",
             "README.template.md", "- Resident index: `{{INDEX_PATH}}`",
             "- Resident index: `{{INDEX_PATH}}`\n\n`{{IF_BILINGUAL: keep this}}` is the old form.",
             "render-residue", 2),
    Mutation("F3", "region inside a heading line", "templates", "AGENTS.template.md",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list",
             "## {{IF ARCHITECTURE_PATH}}<!-- Reconcile this list", "region-in-heading"),
    Mutation("F3", "region inside a heading line quoted in a blockquote", "templates", "AGENTS.template.md",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list",
             "> ## {{IF ARCHITECTURE_PATH}}<!-- Reconcile this list", "region-in-heading"),
    Mutation("F3", "region inside a setext heading line (===)", "templates", "AGENTS.template.md",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->"
             "{{END IF}}",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->"
             "{{END IF}}\n===", "region-in-heading"),
    Mutation("F3", "region inside a setext heading line (---)", "templates", "AGENTS.template.md",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->"
             "{{END IF}}",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->"
             "{{END IF}}\n---", "region-in-heading"),
    Mutation("F3", "region inside a setext heading line quoted in a blockquote (===)", "templates",
             "AGENTS.template.md",
             "{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->"
             "{{END IF}}",
             "> {{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->"
             "{{END IF}}\n> ===", "region-in-heading"),
)
T2 = (
    Mutation("F4", "stand-in put back beside the ported region", "example", "AGENTS.md",
             "- `docs/REQUIREMENTS.md`: behavior contract (IDs: `TODO-XXX`).",
             "- `docs/REQUIREMENTS.md`: behavior contract (IDs: `TODO-XXX`). Also carries the observable "
             "surface, one exercising command or page per row.", "target-stand-in-remains"),
    Mutation("F4", "CI-runners stand-in line put back", "example", "README.md", "## Project-Neutrality Checklist",
             "CI runners executing this repo's pipelines: linux-small <!-- ci-runners: linux-small -->\n\n"
             "## Project-Neutrality Checklist", "target-stand-in-remains"),
    Mutation("F4", "CI-runners stand-in line put back without its comment", "example", "README.md",
             "## Project-Neutrality Checklist",
             "CI runners executing this repo's pipelines: selftest-runner\n\n## Project-Neutrality Checklist",
             "target-stand-in-remains"),
    Mutation("F4", "last sentence of a stand-in left behind a ported row", "example",
             "agentic-mode/SELF-TEST.md",
             "or a hand-written doc, with any local exception declared in its header.",
             "or a hand-written doc, with any local exception declared in its header. "
             "No WORKFLOW doc is seeded.", "target-stand-in-remains"),
    Mutation("F4", "last sentence of a stand-in left behind a ported row, typed in lower case", "example",
             "agentic-mode/SELF-TEST.md",
             "or a hand-written doc, with any local exception declared in its header.",
             "or a hand-written doc, with any local exception declared in its header, "
             "no WORKFLOW doc is seeded.", "target-stand-in-remains"),
    Mutation("F4", "CI-runners stand-in line put back, a lint comment above the Template-Source note",
             "example", "README.md", "<!--\nTemplate-Source:",
             "CI runners executing this repo's pipelines: selftest-runner\n\n"
             "<!-- markdownlint-disable MD013 -->\n<!--\nTemplate-Source:", "target-stand-in-remains"),
    Mutation("F4", "CI-runners stand-in line put back, the doc opening with a UTF-8 BOM",
             "example", "README.md", "<!--\nTemplate-Source:",
             "\ufeffCI runners executing this repo's pipelines: selftest-runner\n\n"
             "<!--\nTemplate-Source:", "target-stand-in-remains"),
    Mutation("F5", "first branch of a whole-line region never ported", "example", "AGENTS.md",
             "- `docs/USER_GUIDE.md`: observable surface (commands, flags, output).\n", "",
             "target-first-branch-missing", -1),
    Mutation("F5", "first branch of a whole-line region never ported, the line above typed in another case",
             "example", "AGENTS.md",
             "- `docs/REQUIREMENTS.md`: behavior contract (IDs: `TODO-XXX`).\n"
             "- `docs/USER_GUIDE.md`: observable surface (commands, flags, output).\n",
             "- `docs/REQUIREMENTS.md`: Behavior Contract (IDs: `TODO-XXX`).\n", "target-first-branch-missing"),
    Mutation("F5", "first branch of an inline region never ported", "example", "AGENTIC-MODE.md",
             "stable IDs (each row names the observable surface it governs), event/domain",
             "stable IDs, event/domain", "target-first-branch-missing"),
    Mutation("F5", "table row that is a first branch never ported", "example", "AGENTIC-MODE.md",
             "| Observable surface | `docs/USER_GUIDE.md` | Commands, flags, output — what users see, press, "
             "or call. |\n", "", "target-first-branch-missing", -1),
    Mutation("F6", "raw region left in the doc", "example", "AGENTS.md",
             "- `docs/WORKFLOW.md`: platform review loop (see Change Flow below).",
             "- {{IF WORKFLOW_PATH}}`{{WORKFLOW_PATH}}`: platform review loop (see Change Flow below)."
             "{{END IF}}", "target-marker-residue"),
    Mutation("R1", "config withdraws a layer the docs still carry", "example", "agentic-mode/config.json",
             '"workflow": "docs/WORKFLOW.md"', '"workflow": null', "target-first-branch-remains",
             0, "AGENTS.md"),
    Mutation("R2", "a layer that is not declared: the index keeps the path that is its first branch",
             "example", "AGENTIC-MODE.md",
             "`README.md` Main Components / Data Flow and `AGENTS.md` Key Files. No architecture doc "
             "is seeded |", "`docs/ARCHITECTURE.md` |", "target-first-branch-remains"),
)
# Edits that are no fault: the proof must answer as it does on the untouched example.
CTL = (
    Mutation("F5", "a first branch typed in another case is carried", "example", "AGENTS.md",
             "- `docs/USER_GUIDE.md`: observable surface (commands, flags, output).\n",
             "- `docs/USER_GUIDE.md`: Observable Surface (commands, flags, output).\n", None),
)


def _copy(src: str, dest: str) -> None:
    try:
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    except OSError as exc:
        raise Fail("cannot copy %s: %s" % (src, exc))


def _apply(root: str, mut: Mutation) -> None:
    """Mutate the copy. Fail (exit 2) when canon moved and the anchor is gone: never a silent
    pass, and never a finding either, because nothing in the templates is at fault."""
    path = os.path.join(root, mut.file)
    text = read(path)
    if text.count(mut.find) != 1:
        raise Fail("anchor found %d times in %s: canon moved, update the mutation"
                   % (text.count(mut.find), mut.file))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(mut.find, mut.replace))


def _anchor_line(mut: Mutation) -> int:
    """The line the finding must name: counted in the real file, so that it does not move
    with the mutation."""
    origin = TEMPLATES_DIR if mut.tree == "templates" else EXAMPLE_DIR
    text = read(os.path.join(origin, mut.file))
    return text.count("\n", 0, text.index(mut.find)) + 1 + mut.offset


def _write_config(dest: str, st: State) -> None:
    """A target's config.json for one state, holding what T2 reads of it (state_from_config)."""
    os.makedirs(os.path.join(dest, "agentic-mode"), exist_ok=True)
    config = {"schema_version": 1, "project": {"name": "demo", "type": "cli"}, "id": {"prefix": "DEMO"},
              "docs": {"user_guide": st.value("SURFACE_DOC_PATH"), "api_reference": None,
                       "workflow": st.value("WORKFLOW_PATH"), "architecture": st.value("ARCHITECTURE_PATH")},
              "bilingual": {"enabled": st.bilingual}}
    with open(os.path.join(dest, "agentic-mode", "config.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


def _opposite(st: State) -> State:
    """The state with every optional placeholder, and the bilingual axis, the other way round."""
    return State({p: None if st.value(p) else sample_path(p) for p in OPTIONAL}, not st.bilingual)


def _synthetic_target(dest: str, st: State, canon: Dict[str, Template]) -> None:
    """A target laid out from canon itself: every template that has a Parsed, rendered in one
    state, as a doc of its own. No list of names: a template added to canon is covered."""
    for name, tmpl in sorted(canon.items()):
        if tmpl.parsed is None:
            continue
        with open(os.path.join(dest, name + ".md"), "w", encoding="utf-8") as fh:
            fh.write("<!--\nTemplate-Source: agentic-bootstrap/%s@v%s\n-->\n%s"
                     % (name, tmpl.parsed.version, "".join(line.text for line in render(tmpl.parsed, st))))
    _write_config(dest, st)


def _render_cases() -> List[Tuple[str, bool, str]]:
    """The renderer against doctrine :193 and :195 on three-line templates."""
    off = State({p: None for p in OPTIONAL}, False)
    on = State({p: sample_path(p) for p in OPTIONAL}, True)

    def run(text: str, st: State) -> str:
        return "".join(l.text for l in render(parse_template("syn", text, "syn").parsed, st))
    block = "a\n\n{{IF WORKFLOW_PATH}}\n## S\n\ntext\n{{END IF}}\n\nb\n"
    inline = "a {{IF SURFACE_DOC_PATH}}b{{ELSE}}c {{END IF}} d\n"
    bil = "e {{IF_BILINGUAL: t}}.\n"
    return [
        ("a dropped block leaves one blank line", run(block, off) == "a\n\nb\n", run(block, off)),
        ("a kept block is verbatim", run(block, on) == "a\n\n## S\n\ntext\n\nb\n", run(block, on)),
        ("an inline stand-in meets its sentence without a double space", run(inline, off) == "a c d\n",
         run(inline, off)),
        ("a dropped bilingual span takes its space with it", run(bil, off) == "e.\n", run(bil, off)),
        ("a kept bilingual span keeps its text", run(bil, on) == "e t.\n", run(bil, on)),
    ]


def selftest() -> int:
    fails: List[str] = []
    passed = 0

    def ok(label: str, cond: bool, detail: str = "") -> None:
        nonlocal passed
        if cond:
            passed += 1
        else:
            fails.append("%s%s" % (label, (" -- " + detail[:400]) if detail else ""))

    def shown(rep: Report) -> str:
        return "; ".join(f.render() for f in rep.findings) or "nothing"

    def tally(rep: Report, regions: int) -> str:
        """What a failed proof was made of: the findings, then the notices, then the count."""
        return "%s; regions %d of %d" % ("; ".join(f.render() for f in rep.findings + rep.notices)
                                         or "nothing", rep.stats["regions"], regions)

    with tempfile.TemporaryDirectory() as tmp:
        tdir, edir = os.path.join(tmp, "canon"), os.path.join(tmp, "example")
        _copy(TEMPLATES_DIR, tdir)
        _copy(EXAMPLE_DIR, edir)
        canon = parse_templates(tdir)
        ctl1 = template_report(canon)
        ctl2 = check_target(edir, canon)
        ok("control: canon renders clean in every state", not ctl1.findings, shown(ctl1))
        ok("control: doctrine names the optional placeholders this script knows",
           doctrine_paths() == set(OPTIONAL), "doctrine names %s; this script knows %s"
           % (sorted(doctrine_paths()), sorted(OPTIONAL)))
        # Every region of canon must be in play. The example rewrites one numbered list into a
        # sentence (README, the safe-change pattern), so that region cannot be proven and leaves
        # one notice: the only one allowed. It may go when the example is edited back to the
        # template's wording; any other notice, or a region nothing was searched for, is drift.
        regions = sum(len(t.parsed.regions) for t in canon.values() if t.parsed)
        rewritten = next((r for r in canon["README"].parsed.regions
                          if r.first.strip() == "Update the surface doc."), None)
        if rewritten is None:
            raise Fail("the region the worked example rewrites by hand is gone from "
                       "templates/README.template.md: update the selftest")
        ok("control: the worked example proves clean, every region of canon in play, but for the "
           "region it rewrote by hand",
           not ctl2.findings and ctl2.stats["regions"] == regions
           and all(f.file == "README.md" and _where(canon["README"], rewritten) in f.message
                   for f in ctl2.notices),
           tally(ctl2, regions))
        text = read(os.path.join(edir, "AGENTIC-MODE.md"))
        for typed, name, dash in (("a hyphen", "hyphens", "-"), ("an en dash", "en-dashes", "–")):
            variant = os.path.join(tmp, name)
            _copy(edir, variant)
            path = os.path.join(variant, "AGENTIC-MODE.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text.replace("—", dash))
            rep = check_target(variant, canon)
            ok("control: a doc that types the em dash as %s proves the same" % typed,
               "—" in text and not rep.findings and len(rep.notices) == len(ctl2.notices),
               "; ".join(f.render() for f in rep.findings + rep.notices) or "nothing")
        # the mirror of the index's stand-in sentence is no stand-in: the piece a placeholder cuts
        # off ends in a function word, and the piece after it is under both length floors
        mirror = normalize("`README.md` Main Components / Data Flow and `AGENTS.md` Key Files.").text
        pieces = [p for r in canon["AGENTIC-MODE"].parsed.regions
                  if r.stand and "Main Components" in r.stand
                  for p in stand_in_pieces(r.first, r.stand, {"ARCHITECTURE_PATH": "docs/ARCHITECTURE.md"})]
        ok("control: a stand-in piece cut off by a function word, or under the length floors, is "
           "not searched for", bool(pieces) and all(p.narrow.search(mirror) is None for p in pieces))
        # each length floor on its own: the index's stand-in has a three-word piece over the
        # character floor, and four words fit under it
        mirror = normalize("`docs/REQUIREMENTS.md`, its requirement rows.").text
        pieces = [p for r in canon["AGENTIC-MODE"].parsed.regions
                  if r.stand and "its requirement rows" in r.stand
                  for p in stand_in_pieces(r.first, r.stand, {"SURFACE_DOC_PATH": "docs/USER_GUIDE.md"})]
        ok("control: a stand-in piece of three words over the character floor is not searched for",
           bool(pieces) and all(p.narrow.search(mirror) is None for p in pieces))
        ok("control: a stand-in piece of four words under the character floor is not searched for",
           not stand_in_pieces("", "not in this doc", {}))
        for mut in CTL + T1 + T2:
            dest = os.path.join(tmp, "mutated")
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            _copy(tdir if mut.tree == "templates" else edir, dest)
            _apply(dest, mut)
            rep = template_report(parse_templates(dest)) if mut.tree == "templates" \
                else check_target(dest, canon)
            if mut.expect is None:                  # a control: the edit is no fault, nothing may go red
                line, hit = None, not rep.findings and rep.notices == ctl2.notices
                want, got = "no finding and the notices unchanged", tally(rep, regions)
            else:
                line = None if mut.fault == "R1" else _anchor_line(mut)
                hit = any(f.category == mut.expect
                          and f.file.replace("\\", "/").endswith(mut.where or mut.file)
                          and (line is None or f.line == line) for f in rep.findings)
                want, got = "[%s] at %s:%s" % (mut.expect, mut.where or mut.file, line), shown(rep)
            ok("%s %s" % (mut.fault, mut.what), hit, "expected %s, got %s" % (want, got))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            bad_target = main(["--target", dest])          # `dest` still holds the last mutation
            no_target = main(["--target", os.path.join(tmp, "no-such-target")])
        ok("exit code: a target with a finding exits 1", bad_target == 1, str(bad_target))
        ok("exit code: a target that is not a directory exits 2", no_target == 2, str(no_target))
        # A stand-in that is one path in backticks is what a doc keeps for a layer that is not
        # declared, and it has the shape of a first branch that is only a path: it is no fault.
        # The empty region at the end has nothing to search for in any state: it is not in play.
        off = State({p: None for p in OPTIONAL}, False)
        pod = os.path.join(tmp, "path-only")
        os.makedirs(os.path.join(pod, "templates"))
        with open(os.path.join(pod, "templates", "PATH-ONLY.template.md"), "w", encoding="utf-8") as fh:
            fh.write("<!-- Template-Source: agentic-bootstrap/PATH-ONLY@v1 -->\n"
                     "See {{IF WORKFLOW_PATH}}`{{WORKFLOW_PATH}}`{{ELSE}}`CONTRIBUTING.md`{{END IF}} "
                     "for the loop.{{IF ARCHITECTURE_PATH}}{{END IF}}\n")
        one = parse_templates(os.path.join(pod, "templates"))
        with open(os.path.join(pod, "PATH-ONLY.md"), "w", encoding="utf-8") as fh:
            fh.write("<!--\nTemplate-Source: agentic-bootstrap/PATH-ONLY@v1\n-->\n"
                     + "".join(line.text for line in render(one["PATH-ONLY"].parsed, off)))
        _write_config(pod, off)
        rep = check_target(pod, one)
        ok("control: a stand-in that is one path in backticks is not a first branch that remains",
           not rep.findings and not rep.notices,
           "; ".join(f.render() for f in rep.findings + rep.notices) or "nothing")
        ok("control: a region nothing can be searched for is not counted as in play",
           rep.stats["regions"] == 1, "regions %d of 2" % rep.stats["regions"])
        # round trip: a faithful render of canon passes the target proof in every state, every
        # region of it searched for. The same docs held against the config of the opposite state
        # must go red: a proof that settles nothing passes the first half, never the second.
        for st in all_states():
            dest = os.path.join(tmp, "roundtrip")
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            os.makedirs(dest)
            _synthetic_target(dest, st, canon)
            rep = check_target(dest, canon)
            ok("round trip: %s" % st.label(),
               not rep.findings and not rep.notices and rep.stats["regions"] == regions,
               tally(rep, regions))
            _write_config(dest, _opposite(st))
            rep = check_target(dest, canon)
            ok("round trip, the config of the opposite state: %s" % st.label(),
               bool(rep.findings), shown(rep))
        # the tidy rule against the lines the worked example really carries
        ex = read(os.path.join(EXAMPLE_DIR, "docs", "WORKFLOW.md")).split("\n")
        workflow = next(d.name for d in discover_docs(EXAMPLE_DIR) if d.name.startswith("WORKFLOW-"))
        rendered = [l.text for l in render(canon[workflow].parsed, off)]
        for anchor in ("(HEREDOC).", "language in the reply.", "iteration-history entry."):
            want = next(l.strip() for l in ex if anchor in l)
            ok("oracle: the render carries the example's %r line" % anchor,
               any(want in line for line in rendered), want)
        for label, cond, detail in _render_cases():
            ok("renderer: " + label, cond, repr(detail))
    for f in fails:
        print("FAIL " + f, file=sys.stderr)
    print("check_template_renders selftest: %d of %d checks passed" % (passed, passed + len(fails)))
    return 1 if fails else 0


# ---------------------------------------------------------------- 10. CLI
def _emit(rep: Report, label: str) -> List[Finding]:
    for f in sorted(rep.findings + rep.notices, key=lambda f: (f.file, f.line, f.category)):
        print(f.render())
    print("%s: %s" % (label, ", ".join("%s %d" % kv for kv in sorted(rep.stats.items()))
                      + (", findings %d" % len(rep.findings) if rep.findings else "")))
    return rep.findings


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Check that every template renders clean in every doc-set "
                                              "state, and that a rendered target carries its regions.")
    ap.add_argument("--selftest", action="store_true", help="inject each fault class into copies of the real files")
    ap.add_argument("--target", metavar="DIR", help="a rendered target: bootstrap, adopt, or after an upgrade")
    args = ap.parse_args(argv)
    if args.selftest and args.target:
        ap.error("--selftest and --target are mutually exclusive")
    try:
        if args.selftest:
            return selftest()
        canon = parse_templates(TEMPLATES_DIR)
        if args.target:
            rep = check_target(os.path.abspath(args.target), canon)
            rep = Report(structure_findings(canon) + rep.findings, rep.notices, rep.stats)
            return 1 if _emit(rep, "target %s" % args.target) else 0
        bad = _emit(template_report(canon), "templates")
        bad += _emit(check_target(EXAMPLE_DIR, canon), "target examples/minimal-cli")
    except Fail as exc:
        print("check_template_renders: %s" % exc, file=sys.stderr)
        return 2
    print("check_template_renders: %s" % ("clean" if not bad else "%d findings" % len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
