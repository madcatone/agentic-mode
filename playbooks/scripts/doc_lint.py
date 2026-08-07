#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical half of the doc-linter protocol.

The rule catalog in ``SKILL.md`` mixes two kinds of rules: rules a machine can
decide (a hedge word is present or it is not) and rules that need judgment (is
this sentence an instruction or explanatory prose?). Reading alone cannot tell
the two apart, so a reader who misses a line reports the category as *passed* --
the user hears "checked, clean" instead of "not found". This script removes the
miss: every mechanically detectable pattern is found by grep-grade matching, and
only the judgment half is left to the reader.

Run it before the reading pass::

    python3 scripts/doc_lint.py <target> [--type skill|claude-md|handoff|readme|runbook|generic]

``python3 scripts/doc_lint.py --selftest`` runs the built-in rule cases instead,
and exits non-zero if any of them regressed.

Output has three parts:

``VIOLATIONS``
    Deterministic. The pattern alone proves the rule is broken (an approximate
    numeric threshold, a condition on the agent's own uncertainty, stacked
    negations, identifier case drift, a skill without frontmatter, an oversize
    body). Each one is a finding. Exit status is 1 when this list is non-empty.

``CANDIDATES``
    Detected mechanically, decided by the reader. The pattern is present; only a
    human or an agent can say whether the sentence is an instruction (finding)
    or explanatory prose (acceptable). Every candidate must be adjudicated and
    then either reported as a finding or dropped -- never left silent.

``COVERAGE``
    Which rule IDs this script decides, which it only detects, and which it does
    not touch at all. The last group is what the report must list under
    ``Not checked``.

Each finding prints as::

    <file>:<line>: [<rule-id>] <message>

Exit status: 0 = no violations, 1 = at least one violation, 2 = usage or I/O
error. Candidates never change the exit status.

Skipped text: fenced code blocks, blockquote lines (``>``), inline code spans,
and quoted strings (``"..."``, ``「...」``, ``『...』``). Deliberate bad examples
belong in one of those. To silence one line, end it with ``<!-- doc-lint:ignore
-->``; to silence a region, wrap it in ``<!-- doc-lint:ignore-start -->`` and
``<!-- doc-lint:ignore-end -->``.

Pure standard library, Python 3.8+.
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# Rule inventory. coverage: "decide" = violation-grade, "detect" = candidate
# only (reader adjudicates), "none" = no mechanical coverage at all.
# --------------------------------------------------------------------------

RULES: List[Tuple[str, str, str]] = [
    ("T1", "one name per concept", "none"),
    ("T2", "define on first use", "none"),
    ("T3", "identifiers match between prose and code", "decide"),
    ("S1", "imperative active voice", "detect"),
    ("S2", "one action per step", "detect"),
    ("S3", "sentence length (25 words / 40 chars)", "detect"),
    ("S4", "number every procedure", "none"),
    ("H1", "no hedge words in instructions", "detect"),
    ("H2", "conditions have testable criteria", "decide"),
    ("H3", "no vague quantifiers", "detect"),
    ("N1", "prohibitions carry a positive alternative", "detect"),
    ("N2", "no stacked negations", "decide"),
    ("P1", "warnings before the step they guard", "none"),
    ("P2", "split files only when the split survives distribution", "none"),
    ("P3", "deletion test", "none"),
    ("P4", "no duplicate or conflicting instructions", "detect"),
    ("E1", "good/bad pairs for critical behavior", "none"),
    ("E2", "examples use the rules' terminology", "none"),
]

TYPE_RULES = {
    "skill": [
        ("D-SK1", "triggering information lives in the frontmatter", "decide"),
        ("D-SK2", "description names concrete trigger phrases", "none"),
        ("D-SK3", "body opens with the workflow", "none"),
        ("D-SK4", "body under 500 lines", "decide"),
    ],
    "claude-md": [
        ("D-CM1", "every line is an imperative rule or a needed fact", "none"),
        ("D-CM2", "rules grouped by topic with headers", "none"),
    ],
    "handoff": [
        ("D-HO1", "every state claim is verifiable", "none"),
        ("D-HO2", "next actions are imperative and self-contained", "none"),
        ("D-HO3", "entries are timestamped and appended", "none"),
        ("D-HO4", "open questions listed explicitly", "none"),
    ],
    "readme": [
        ("D-RM1", "first screen answers what/who/how", "none"),
        ("D-RM2", "setup commands are complete and copy-pasteable", "none"),
        ("D-RM3", "stable parts marked against descriptive prose", "none"),
    ],
    "runbook": [
        ("D-RB1", "trigger condition is explicit", "none"),
        ("D-RB2", "side-effect steps state precondition and rollback", "none"),
        ("D-RB3", "expected end state is stated", "none"),
    ],
    "generic": [],
}

BODY_LINE_LIMIT = 500

# --------------------------------------------------------------------------
# Patterns
# --------------------------------------------------------------------------

CJK = "\u4e00-\u9fff"

EN_HEDGES = [
    "it might be necessary", "should ideally", "when appropriate",
    "as appropriate", "feel free to", "if possible", "attempt to",
    "appears to", "if needed", "as needed", "seems to", "generally",
    "typically", "ideally", "usually", "consider", "attempt", "might",
    "prefer", "could", "try to", "may",
]

ZH_HEDGES = [
    "建議可以", "一般來說", "如有需要", "儘可能", "應該要", "視情況", "必要時",
    "適當地", "原則上", "基本上", "看起來", "或許", "可能", "適時", "盡量",
    "通常", "似乎", "考慮",
]


def _en_alt(words: Sequence[str]) -> str:
    return "|".join(r"\b" + re.escape(w).replace(" ", r"\s+") + r"\b" for w in words)


HEDGE_RE = re.compile(_en_alt(EN_HEDGES) + "|" + "|".join(re.escape(w) for w in ZH_HEDGES),
                      re.IGNORECASE)

# H2 -- a condition on the agent's own uncertainty can never be tested.
UNDECIDABLE_RE = re.compile(
    r"\b(?:if|when|whenever)\b[^.;:]{0,30}?\b"
    r"(?:unsure|uncertain|unclear|not\s+sure|in\s+doubt|ambiguous)\b"
    r"|(?:若|如果|當)[^。；]{0,15}?(?:不確定|不清楚|不明確)"
    r"|(?:不確定|不清楚|不明確)(?:時|的話)",
    re.IGNORECASE,
)

# H2 -- an approximate number is not a threshold.
APPROX_RE = re.compile(
    r"~\s*\d+|\b(?:about|around|roughly|approximately)\s+\d+|約\s*\d+|大約|左右",
    re.IGNORECASE,
)

# H2 -- a condition whose test is a vague adjective.
COND_RE = re.compile(r"\b(?:if|unless|when|whenever)\b|若|如果|除非|當", re.IGNORECASE)
VAGUE_RE = re.compile(
    r"\b(?:large|small|long|short|slow|fast|big|heavy|complex|simple|messy|"
    r"enough|appropriate|necessary|reasonable|significant|too\s+\w+)\b"
    r"|太大|太長|太多|太少|過大|過長|適當|必要|足夠|合理|複雜",
    re.IGNORECASE,
)

# H3 -- vague quantifiers.
QUANTIFIER_RE = re.compile(
    r"\b(?:some|a\s+few|several|a\s+couple|multiple|as\s+many\s+as\s+needed|"
    r"various|numerous)\b|若干|幾個|一些|數個|許多",
    re.IGNORECASE,
)

# N2 -- stacked negation.
# Implicit negators are listed in the bare form only. The stack this rule hunts
# always governs them with a preceding negator ("do not fail to check"), and
# English requires the bare infinitive in exactly that position, so the bare form
# loses no true positive. The finite forms are descriptive instead of governed --
# "if even that fails to execute, the IDE can't run bundled shell" is a
# conditional whose two halves negate different predicates, not a polarity the
# reader has to unwind -- so they stay out. `omit` is excluded for the mirror
# reason: its bare form is also the free imperative documents use constantly
# ("omit it when there is no ticket"), where the neighbouring negator states the
# condition rather than stacking with it, so the free imperative cannot be told
# apart from the governed "never omit Y" without a reader-level judgement.
NEG_RE = re.compile(
    r"\bnot\b|\bnever\b|\bno\b|\bnone\b|\bcannot\b|\bwithout\b|\bunless\b|n't\b"
    r"|\bfail\s+to\b|\bneglect\s+to\b|\brefrain\s+from\b"
    r"|不|沒|未|勿|別|非|除非",
    re.IGNORECASE,
)
# Compounds that contain a negation character without negating.
NEG_FALSE_FRIENDS = ["非常", "非同步", "未來", "不僅", "不但", "不只", "無論"]
# CJK clause boundaries. A negation on each side of one of these negates its own
# predicate: a further enumerated item (、), the next table cell (|), a coordinate
# predicate (不修 bug 也不加功能), an aside, or the exception a prohibition hangs
# off (不加作者行，除非使用者明確要求). Only negations inside one clause stack into
# a polarity the reader has to compute, so N2 counts each clause on its own.
# `除非` opens its clause instead of ending one, so 除非不 still stacks.
CJK_CLAUSE_BREAK_RE = re.compile(
    r"[、|；：（）()【】\[\]／/]|——|[且並也又而或]|(?=除非)"
)
# English clause boundaries, same principle as the CJK ones but deliberately
# narrower: only the exception opener, which is the English 除非. A prohibition
# and the exception it hangs off negate different predicates (do not merge
# unless the build is green), so each side is its own clause. The opener stays
# with the clause it introduces, so "unless ... not ..." still stacks.
EN_CLAUSE_BREAK_RE = re.compile(
    r"(?=\bunless\b)|(?=\bexcept\s+(?:when|if)\b)", re.IGNORECASE
)

# N1 -- a prohibition with no stated alternative.
PROHIBIT_RE = re.compile(r"\b(?:do\s+not|don't|never|avoid)\b|不要|不得|禁止|勿",
                         re.IGNORECASE)
ALTERNATIVE_RE = re.compile(r"\binstead\b|\brather\s+than\b|改用|請改|改成|應改|改為",
                            re.IGNORECASE)

# S1 -- passive voice.
PASSIVE_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ed|done|made|given|taken|"
    r"written|known|shown|kept|held|sent|built|found|left|set)\b",
    re.IGNORECASE,
)

# S2 -- a step that carries more than one action.
COMPOUND_RE = re.compile(r",\s*(?:and|then)\s+\w|，\s*(?:並|然後|再)|、\s*(?:並|然後)",
                         re.IGNORECASE)

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
SENTENCE_SPLIT_RE = re.compile(r"[.!?;。！？；]+\s*")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
WS_RE = re.compile(r"\s+")
CJK_RE = re.compile("[" + CJK + "]")
CODE_TOKEN_RE = re.compile(r"`([^`]+)`")
IDENT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]{3,}$")

MASK_RE = re.compile(r"`[^`]*`|\"[^\"]*\"|\u201c[^\u201d]*\u201d"
                     r"|\u300c[^\u300d]*\u300d|\u300e[^\u300f]*\u300f")

IGNORE_LINE = "<!-- doc-lint:ignore -->"
IGNORE_START = "<!-- doc-lint:ignore-start"
IGNORE_END = "<!-- doc-lint:ignore-end"

SENTENCE_WORD_LIMIT = 25
SENTENCE_CHAR_LIMIT = 40

# --------------------------------------------------------------------------
# Scanning
# --------------------------------------------------------------------------


class Finding:
    def __init__(self, line: int, rule: str, message: str) -> None:
        self.line = line
        self.rule = rule
        self.message = message


class Block:
    """One logical unit of prose: a list item, or a paragraph.

    Hard-wrapped documents break a sentence across several source lines, so a
    line-by-line scan misses every pattern that straddles the break. Blocks join
    the wrapped lines back together and map each match to the source line it
    came from.
    """

    def __init__(self, is_item: bool) -> None:
        self.is_item = is_item
        self.text = ""
        self.starts: List[Tuple[int, int]] = []

    def add(self, line_no: int, masked: str) -> None:
        self.starts.append((len(self.text), line_no))
        self.text += masked.strip() + " "

    def locate(self, pos: int) -> int:
        line = self.starts[0][1]
        for offset, line_no in self.starts:
            if offset > pos:
                break
            line = line_no
        return line


def mask(text: str) -> str:
    """Blank out code spans and quoted strings, keeping the line length."""
    return MASK_RE.sub(lambda m: " " * len(m.group(0)), text)


def classify(path: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    name = path.rsplit("/", 1)[-1].lower()
    if name == "skill.md":
        return "skill"
    if name == "claude.md" or name == "agents.md":
        return "claude-md"
    if name.startswith("handoff"):
        return "handoff"
    if name.startswith("readme"):
        return "readme"
    if name.startswith("runbook"):
        return "runbook"
    return "generic"


def split_sentences(text: str) -> List[Tuple[int, str]]:
    """Sentences as (offset in text, sentence)."""
    out = []
    pos = 0
    for match in SENTENCE_SPLIT_RE.finditer(text):
        if text[pos:match.start()].strip():
            out.append((pos, text[pos:match.start()]))
        pos = match.end()
    if text[pos:].strip():
        out.append((pos, text[pos:]))
    return out


def sentence_too_long(sentence: str) -> Optional[str]:
    cjk = len(CJK_RE.findall(sentence))
    if cjk >= 4:
        if cjk > SENTENCE_CHAR_LIMIT:
            return "%d Chinese characters (limit %d)" % (cjk, SENTENCE_CHAR_LIMIT)
        return None
    words = len(WORD_RE.findall(sentence))
    if words > SENTENCE_WORD_LIMIT:
        return "%d words (limit %d)" % (words, SENTENCE_WORD_LIMIT)
    return None


def count_negations(sentence: str) -> List[str]:
    """Negations that force the reader to compute the polarity.

    A repeated ASCII negator is an enumeration ("no network, no installs"), so
    those count once. Mixed negators stack ("do not run it without a review").

    CJK negators count every time *within one clause*, because a repeated one
    there is the double negative itself (不要不做). Across clause boundaries
    (CJK_CLAUSE_BREAK_RE) they are separate statements -- an enumerated list of
    prohibitions, one table row after another -- so the sentence is scored by
    its worst clause rather than by its total.

    ASCII negators are scored the same way across the exception openers of
    EN_CLAUSE_BREAK_RE, so "do not merge unless the build is green" reads as a
    prohibition plus its exception rather than as a stack, matching how the CJK
    side reads 不要合併，除非 build 是綠的. Both sides are counted per clause but
    on their own clause boundaries, so a sentence with neither opener is scored
    exactly as before.

    An implicit negator ("do not fail to check") is a multi-word form, so its
    inner spacing is collapsed before it joins the set: a line-wrapped "fail to"
    and a single-spaced one are the same negator and must dedupe to one. Every
    single-word negator is unaffected.
    """
    cleaned = sentence
    for friend in NEG_FALSE_FRIENDS:
        cleaned = cleaned.replace(friend, " ")
    worst_ascii = set()
    for clause in EN_CLAUSE_BREAK_RE.split(cleaned):
        ascii_forms = {WS_RE.sub(" ", m.lower()) for m in NEG_RE.findall(clause)
                       if not CJK_RE.search(m)}
        if len(ascii_forms) > len(worst_ascii):
            worst_ascii = ascii_forms
    worst_cjk = []
    for clause in CJK_CLAUSE_BREAK_RE.split(cleaned):
        cjk_forms = [m for m in NEG_RE.findall(clause) if CJK_RE.search(m)]
        if len(cjk_forms) > len(worst_cjk):
            worst_cjk = cjk_forms
    return sorted(worst_ascii) + worst_cjk


def scan_frontmatter(lines: Sequence[str]) -> Tuple[List[str], int]:
    """Return the frontmatter lines and the index of the first body line."""
    if not lines or lines[0].strip() != "---":
        return [], 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return list(lines[1:i]), i + 1
    return [], 0


def scan(path: str, doc_type: str) -> Tuple[List[Finding], List[Finding], int]:
    with open(path, "r", encoding="utf-8") as handle:
        raw = handle.read().splitlines()

    violations: List[Finding] = []
    candidates: List[Finding] = []

    front, body_start = scan_frontmatter(raw)
    body_lines = len(raw) - body_start

    if doc_type == "skill":
        joined = "\n".join(front)
        if not front:
            violations.append(Finding(1, "D-SK1", "no YAML frontmatter: a skill "
                                      "carries its triggering information there"))
        else:
            for field in ("name", "description"):
                if not re.search(r"^%s:\s*\S" % field, joined, re.MULTILINE):
                    violations.append(Finding(1, "D-SK1", "frontmatter has no "
                                              "non-empty `%s` field" % field))
        if body_lines > BODY_LINE_LIMIT:
            violations.append(Finding(body_start + 1, "D-SK4", "body is %d lines "
                                      "(limit %d)" % (body_lines, BODY_LINE_LIMIT)))

    in_fence = False
    in_ignore = False
    code_tokens = {}
    blocks: List[Block] = []
    current: Optional[Block] = None

    for index, text in enumerate(raw, start=1):
        stripped = text.strip()

        if stripped.startswith(IGNORE_START):
            in_ignore, current = True, None
            continue
        if stripped.startswith(IGNORE_END):
            in_ignore, current = False, None
            continue
        if in_ignore or IGNORE_LINE in text:
            current = None
            continue

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            current = None
            continue
        if in_fence or stripped.startswith(">"):
            current = None
            continue

        # T3 needs the code spans, so read them before masking.
        for token in CODE_TOKEN_RE.findall(text):
            token = token.strip()
            if IDENT_RE.match(token):
                key = token.lower().replace("_", "").replace("-", "")
                seen = code_tokens.setdefault(key, {})
                seen.setdefault(token, index)

        line = mask(text)
        if not line.strip() or line.lstrip().startswith("#") or stripped == "---":
            current = None
            continue

        if LIST_ITEM_RE.match(line) or current is None:
            current = Block(bool(LIST_ITEM_RE.match(line)))
            blocks.append(current)
        current.add(index, line)

    for block in blocks:
        body = block.text

        for match in UNDECIDABLE_RE.finditer(body):
            violations.append(Finding(block.locate(match.start()), "H2",
                                      "condition tests the agent's own certainty and "
                                      "can never be decided: %r"
                                      % match.group(0).strip()))
        for match in APPROX_RE.finditer(body):
            violations.append(Finding(block.locate(match.start()), "H2",
                                      "approximate threshold %r is not testable: "
                                      "state the exact number"
                                      % match.group(0).strip()))

        for offset, sentence in split_sentences(body):
            line_no = block.locate(offset)
            negations = count_negations(sentence)
            if len(negations) > 1:
                violations.append(Finding(line_no, "N2", "%d negations in one sentence "
                                          "(%s): rewrite as a positive statement"
                                          % (len(negations),
                                             ", ".join(repr(n) for n in negations))))
            if block.is_item:
                too_long = sentence_too_long(sentence)
                if too_long:
                    candidates.append(Finding(line_no, "S3", "%s -- split it, unless "
                                              "this sentence is explanatory prose"
                                              % too_long))
            prohibition = PROHIBIT_RE.search(sentence)
            if prohibition and not ALTERNATIVE_RE.search(sentence[prohibition.end():]):
                candidates.append(Finding(line_no, "N1", "prohibition %r with no "
                                          "alternative after it: check whether the "
                                          "next sentence states what to do instead"
                                          % prohibition.group(0).strip()))

        for match in HEDGE_RE.finditer(body):
            candidates.append(Finding(block.locate(match.start()), "H1",
                                      "hedge word %r -- a finding in an instruction "
                                      "sentence, acceptable in explanatory prose"
                                      % match.group(0).strip()))
        for match in QUANTIFIER_RE.finditer(body):
            candidates.append(Finding(block.locate(match.start()), "H3",
                                      "vague quantifier %r -- replace it with a number "
                                      "when the quantity changes behavior"
                                      % match.group(0).strip()))
        vague = VAGUE_RE.search(body)
        if COND_RE.search(body) and vague:
            candidates.append(Finding(block.locate(vague.start()), "H2",
                                      "condition rests on a vague term %r -- check "
                                      "that the agent can test it"
                                      % vague.group(0).strip()))
        for match in PASSIVE_RE.finditer(body):
            candidates.append(Finding(block.locate(match.start()), "S1",
                                      "passive construction %r -- name the actor if "
                                      "this line is an instruction"
                                      % match.group(0).strip()))
        if block.is_item:
            match = COMPOUND_RE.search(body)
            if match:
                candidates.append(Finding(block.locate(match.start()), "S2",
                                          "step carries more than one action -- split "
                                          "it into one action per step"))

    for key, spellings in code_tokens.items():
        if len(spellings) > 1:
            names = sorted(spellings)
            violations.append(Finding(min(spellings.values()), "T3",
                                      "identifier spelled %s -- one spelling per "
                                      "identifier" % " and ".join(repr(n) for n in names)))

    # P4 -- the same instruction stated twice.
    seen_items = {}
    in_fence = False
    in_ignore = False
    for index, text in enumerate(raw, start=1):
        stripped = text.strip()
        if stripped.startswith(IGNORE_START):
            in_ignore = True
            continue
        if stripped.startswith(IGNORE_END):
            in_ignore = False
            continue
        if in_ignore or IGNORE_LINE in text:
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        if not LIST_ITEM_RE.match(text):
            continue
        norm = re.sub(r"[\s*`_]+", " ", LIST_ITEM_RE.sub("", text)).strip().lower()
        if len(norm) < 20:
            continue
        if norm in seen_items:
            candidates.append(Finding(index, "P4", "repeats the instruction on line "
                                      "%d -- state each rule once, or state the "
                                      "precedence" % seen_items[norm]))
        else:
            seen_items[norm] = index

    violations.sort(key=lambda f: (f.line, f.rule))
    candidates.sort(key=lambda f: (f.line, f.rule))
    return violations, candidates, body_lines


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def emit(path: str, findings: Sequence[Finding]) -> None:
    for finding in findings:
        print("  %s:%d: [%s] %s" % (path, finding.line, finding.rule, finding.message))


def plural(count: int, word: str) -> str:
    return "%d %s%s" % (count, word, "" if count == 1 else "s")


def report(path: str, doc_type: str) -> int:
    violations, candidates, body_lines = scan(path, doc_type)
    rules = RULES + TYPE_RULES.get(doc_type, [])

    print("doc-lint: %s (type: %s, %d body lines)" % (path, doc_type, body_lines))
    print("")
    print("VIOLATIONS (deterministic -- each one is a finding)")
    if violations:
        emit(path, violations)
    else:
        print("  none")
    print("  %s" % plural(len(violations), "violation"))
    print("")
    print("CANDIDATES (detected here, decided by you -- adjudicate every one)")
    if candidates:
        emit(path, candidates)
    else:
        print("  none")
    print("  %s" % plural(len(candidates), "candidate"))
    print("")
    print("COVERAGE")
    decided = [r for r in rules if r[2] == "decide"]
    detected = [r for r in rules if r[2] == "detect"]
    uncovered = [r for r in rules if r[2] == "none"]
    print("  decided by this script: %s" % ", ".join(r[0] for r in decided))
    print("  detected here, you decide: %s" % ", ".join(r[0] for r in detected))
    print("  NOT CHECKED -- read for these yourself, or report them as not checked:")
    for rule_id, name, _ in uncovered:
        print("    %s -- %s" % (rule_id, name))
    return 1 if violations else 0


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

# (sentence, expected negation count). The count is what N2 reports; N2 fires
# above 1. These pin the boundary between an enumeration of separately negated
# items, which reads fine, and a stack the reader has to unwind.
N2_CASES = [
    # Enumerations and coordinate predicates -- one negation per statement.
    ("不接受括號 scope、不接受 `ops` type、另接受 `release` type", 1),
    ("| `refactor` | 重寫／重組程式碼，不修 bug 也不加功能 | | `style` | 純格式，不改語意 |", 1),
    ("以上皆非且不動 src/test 檔", 1),
    ("無 type、非祈使、未大寫", 1),
    ("只有 CI 設定歸 ci，不歸 build——兩型不重疊", 1),
    # A prohibition plus the exception it hangs off.
    ("不加作者行，除非使用者明確要求", 1),
    # False friends stay invisible.
    ("非常重要，所以不要略過", 1),
    # Real stacks -- the reader has to compute the polarity.
    ("不要不做已經排程的檢查", 2),
    ("不要不去不做這件事", 3),
    ("非做不可", 2),
    ("不得不改寫這段", 2),
    ("不要提交，除非測試沒失敗", 2),
    # ASCII enumerations behave as before.
    ("no network, no installs", 1),
    # A prohibition plus the exception it hangs off -- the English 不要 X，除非 Y.
    ("do not merge unless the build is green", 1),
    ("do not commit unless the reviewer asked for the change", 1),
    ("do not deploy except when there is no rollback plan", 1),
    # Real ASCII stacks -- the reader has to compute the polarity.
    ("never not run the scheduled check", 2),
    ("do not leave the branch without a review", 2),
    ("you cannot merge without a second approval", 2),
    # The stack sits inside the exception clause, so it still counts.
    ("do not commit unless the tests did not fail", 2),
    # Implicit negators. Alone they are the sentence's own single polarity.
    ("fail to check the manifest and the release breaks", 1),
    ("refrain from merging on a red build", 1),
    # Governed by a negator, they are the double negative this rule hunts.
    ("do not fail to check the manifest before you tag", 2),
    ("never refrain from filing the incident note", 2),
    ("do not neglect to update the changelog", 2),
    # Finite forms are descriptive, so they are not negators: the only negation
    # here is the consequent's, and the conditional is not a stack.
    ("if even that fails to execute, the IDE can't run bundled shell", 1),
    # `omit` stays out -- the free imperative reads as a condition, not a stack.
    ("omit the ticket id when there is no ticket", 1),
]


def selftest() -> int:
    failures = 0
    for sentence, expected in N2_CASES:
        found = count_negations(sentence)
        ok = len(found) == expected
        if not ok:
            failures += 1
        print("  %-4s N2 expected %d, got %d %-28s %s"
              % ("PASS" if ok else "FAIL", expected, len(found),
                 "(" + ", ".join(found) + ")", sentence))
    print("")
    print("doc_lint selftest: %s of %s N2 cases passed"
          % (len(N2_CASES) - failures, len(N2_CASES)))
    return 1 if failures else 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="doc_lint.py",
        description="Mechanical checks for the doc-linter rule catalog.",
    )
    parser.add_argument("paths", nargs="*", help="document(s) to lint")
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="run the built-in rule cases and exit",
    )
    parser.add_argument(
        "--type",
        dest="doc_type",
        choices=sorted(TYPE_RULES),
        default=None,
        help="document type (default: inferred from the file name)",
    )
    return parser.parse_args(list(argv))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.selftest:
        return selftest()
    if not args.paths:
        print("doc_lint: no document given", file=sys.stderr)
        return 2
    status = 0
    for i, path in enumerate(args.paths):
        if i:
            print("")
        try:
            status = max(status, report(path, classify(path, args.doc_type)))
        except OSError as exc:
            print("doc_lint: I/O error: %s" % exc, file=sys.stderr)
            return 2
        except UnicodeDecodeError as exc:
            print("doc_lint: %s is not UTF-8 text: %s" % (path, exc), file=sys.stderr)
            return 2
    return status


if __name__ == "__main__":
    sys.exit(main())
