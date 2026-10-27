#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Score a two-axis review report against a fixture's expected findings.

Usage::

    python3 tests/review-evals/score_review.py <report.md>
    python3 tests/review-evals/score_review.py --selftest
    python3 tests/review-evals/score_review.py --emit-selftest-report pass:<path>
    python3 tests/review-evals/score_review.py --emit-selftest-report fail:<path>

The report is what a reviewer produces when following
``playbooks/TWO-AXIS-REVIEW.md`` over ``fixtures/todo-review/`` (base tree +
``change.patch`` + ``TICKET.md``, with ``.dev-notes/CODE-REVIEW.md`` as the
local canon). The review itself needs judgment and is never run by CI; this
scorer is the deterministic half of the eval.

Mechanical (format) checks -- each violation prints as one ``[code]`` line:

  [count-line]        the first non-empty line must be either the total
                      count line "共 N 個 finding：X 個 CONFIRMED／Y 個
                      PLAUSIBLE／Z 個 pre-existing" (whose N/X/Y/Z must then
                      agree with the findings actually present in the body)
                      or a leading per-axis count line such as "Standards
                      軸共 3 個 finding：..." (the playbook's §5 aggregated
                      form, where each axis's count line leads its section;
                      accepted as-is). With neither present the check fires.
  [finding-format]    every finding needs a file:line citation, an axis (a
                      Standards/Spec section heading or an inline tag), a
                      CONFIRMED/PLAUSIBLE verdict, and an
                      introduced/pre-existing origin marker
  [upgrade-condition] every PLAUSIBLE finding must carry an
                      upgrade-condition line (升級條件)
  [origin-mislabel]   an expected item marked "origin_strict" must be
                      reported with exactly that origin -- a planted
                      pre-existing issue reported as introduced is a
                      mislabel
  [root-cause]        a bug-fix ticket's report must carry a root-cause
                      section (a heading or label line with 成因 / root
                      cause)

Finding grammar (block-shaped, because real reports spread the parts of one
finding across a header line, a location bullet, and body lines): a finding
block starts at (a) a markdown heading that carries a verdict/origin marker
or a file:line citation, or (b) any non-heading line with a file:line
citation; it extends to the next such start or the next heading, whichever
comes first. Verdict, origin, axis, the upgrade-condition line, match
keywords, and citations may sit on ANY line of the block. A block carrying
neither a verdict nor an origin marker is prose (an analysis note that cites
code) and is ignored.

Matching (recall): an expected item is HIT when some finding's text contains
any ``match_any`` keyword AND one of the finding's citations names the same
file (basename) with a line inside one of the item's ``line_ranges``
(widened by ``line_tolerance``). A finding may cite several locations and
matches through any of them. Keywords are code identifiers on purpose --
reports are written in Traditional Chinese, so matching must be
language-robust. A report finding that hits no expected item is NOISE. One
finding may legitimately satisfy two adjacent expected items (a compound
finding); the scorer trades that strictness for language robustness.

Gate (all must hold; thresholds are the constants below):

  classes hit >= MIN_CLASSES_HIT of the fixture's expected classes,
  format violations <= MAX_FORMAT_VIOLATIONS,
  noise <= MAX_NOISE.

Exit codes: 0 pass, 1 gate failed, 2 usage or I/O error. Per-item verdicts
are not enforced (a single-reviewer environment caps verdicts at PLAUSIBLE
per the playbook); the ``verdict`` field in expected-findings.json documents
intent only. Pure stdlib.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_EXPECTED_PATH = HERE / "expected-findings.json"

# ---- Gate thresholds (adjustable) ------------------------------------------
MIN_CLASSES_HIT = 5         # of the fixture's expected classes
MAX_NOISE = 1               # unmatched report findings allowed
MAX_FORMAT_VIOLATIONS = 0   # mechanical format violations allowed
DEFAULT_LINE_TOLERANCE = 5  # lines of slack around each expected range

# ---- Report grammar ---------------------------------------------------------
COUNT_LINE_RE = re.compile(
    r"^共\s*(\d+)\s*個\s*finding\s*[:：]\s*"
    r"(\d+)\s*個\s*CONFIRMED\s*[/／]\s*"
    r"(\d+)\s*個\s*PLAUSIBLE\s*[/／]\s*"
    r"(\d+)\s*個\s*pre-existing\s*$",
    re.IGNORECASE)
# Leading per-axis count line (playbook §5 aggregated form), e.g.
# "Standards 軸共 3 個 finding：0 個 CONFIRMED／3 個 PLAUSIBLE／1 個 pre-existing".
AXIS_COUNT_LINE_RE = re.compile(
    r"^\s*(?:Standards|Spec)\b[^\n:：]{0,16}?共\s*(\d+)\s*個\s*finding\s*[:：]\s*"
    r"(\d+)\s*個\s*CONFIRMED\s*[/／]\s*"
    r"(\d+)\s*個\s*PLAUSIBLE\s*[/／]\s*"
    r"(\d+)\s*個\s*pre-existing\s*$",
    re.IGNORECASE)
FILE_LINE_RE = re.compile(
    r"([A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,8})[:：](\d+)(?:\s*[-–—~]\s*(\d+))?")
VERDICT_RE = re.compile(r"\b(CONFIRMED|PLAUSIBLE)\b")
ORIGIN_RE = re.compile(r"\b(introduced|pre-existing)\b", re.IGNORECASE)
AXIS_WORD_RE = re.compile(r"\b(Standards|Spec)\b", re.IGNORECASE)
UPGRADE_LINE_RE = re.compile(r"升級條件|upgrade\s*condition", re.IGNORECASE)
ROOT_CAUSE_RE = re.compile(r"成因|root[\s-]?cause", re.IGNORECASE)
ROOT_CAUSE_LABEL_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?\s*(?:成因|root\s*cause)\s*[:：]", re.IGNORECASE)


def die(code, message):
    print("error: %s" % message, file=sys.stderr)
    raise SystemExit(code)


def load_expected(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        die(2, "cannot read expected-findings %s: %s" % (path, exc))
    except ValueError as exc:
        die(2, "expected-findings %s is not valid JSON: %s" % (path, exc))
    if not isinstance(data, dict) or not isinstance(data.get("expected"), list):
        die(2, "expected-findings %s lacks an 'expected' list" % path)
    return data


# ---- Parsing ----------------------------------------------------------------

def parse_report(text):
    """Split a report into block-shaped findings and format violations.

    A finding block starts at (a) a markdown heading that carries a
    verdict/origin marker or a file:line citation, or (b) any non-heading
    line with a file:line citation. It extends to the next such start or the
    next heading, whichever comes first. Verdict, origin, axis, the
    upgrade-condition line, and citations may sit on any line of the block.
    A block carrying neither a verdict nor an origin marker is prose (an
    analysis note that cites code) and is ignored. See the module docstring
    for why: real reports put the verdict in the finding heading and the
    citations in a location bullet below it.
    """
    lines = text.splitlines()
    violations = []
    findings = []
    root_cause_found = False
    current_axis = None
    n = len(lines)

    def has_marker(line):
        return bool(VERDICT_RE.search(line) or ORIGIN_RE.search(line))

    blocks = []  # (start, end, section_axis); end is exclusive
    i = 0
    while i < n:
        line = lines[i]
        if line.startswith("#"):
            if ROOT_CAUSE_RE.search(line):
                root_cause_found = True
            am = AXIS_WORD_RE.search(line)
            if am:
                current_axis = am.group(1).capitalize()
            if has_marker(line) or FILE_LINE_RE.search(line):
                # Finding heading: the block runs to the next heading of any
                # kind; citation lines inside it (location bullets) belong
                # to this finding, they do not start new ones.
                j = i + 1
                while j < n and not lines[j].startswith("#"):
                    j += 1
                blocks.append((i, j, current_axis))
                i = j
                continue
            i += 1
            continue
        if ROOT_CAUSE_LABEL_RE.match(line):
            root_cause_found = True
        if FILE_LINE_RE.search(line):
            # Non-heading citation (plain or bold finding header): the block
            # runs to the next citation line or heading.
            j = i + 1
            while (j < n and not lines[j].startswith("#")
                   and not FILE_LINE_RE.search(lines[j])):
                j += 1
            blocks.append((i, j, current_axis))
            i = j
            continue
        i += 1

    for start, end, section_axis in blocks:
        block_text = "\n".join(lines[start:end])
        head = lines[start].strip()
        verdict = VERDICT_RE.search(block_text)
        origin = ORIGIN_RE.search(block_text)
        if not verdict and not origin:
            continue  # prose that cites code, not a finding
        citations = [(m.group(1), int(m.group(2)),
                      int(m.group(3)) if m.group(3) else int(m.group(2)))
                     for m in FILE_LINE_RE.finditer(block_text)]
        inline_axis = AXIS_WORD_RE.search(lines[start])
        findings.append({
            "head": head,
            "citations": citations,
            "verdict": verdict.group(1).upper() if verdict else None,
            "origin": origin.group(1).lower() if origin else None,
            "axis": (inline_axis.group(1).capitalize() if inline_axis
                     else section_axis),
            "text": block_text,
        })

    # -- count line -----------------------------------------------------------
    first_idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if first_idx is None:
        violations.append(
            ("count-line", "report is empty -- no count line, no findings"))
    else:
        total = COUNT_LINE_RE.match(lines[first_idx])
        axis_count = AXIS_COUNT_LINE_RE.match(lines[first_idx])
        if total:
            n_, x_, y_, z_ = (int(g) for g in total.groups())
            got = (len(findings),
                   sum(1 for f in findings if f["verdict"] == "CONFIRMED"),
                   sum(1 for f in findings if f["verdict"] == "PLAUSIBLE"),
                   sum(1 for f in findings if f["origin"] == "pre-existing"))
            if (n_, x_, y_, z_) != got:
                violations.append(
                    ("count-line",
                     "count line says %d/%d CONFIRMED/%d PLAUSIBLE/%d "
                     "pre-existing but the body has %d findings/%d "
                     "CONFIRMED/%d PLAUSIBLE/%d pre-existing"
                     % ((n_, x_, y_, z_) + got)))
        elif axis_count:
            pass  # leading per-axis count line (§5 aggregated form): accepted
        else:
            violations.append(
                ("count-line",
                 "first non-empty line is neither a total count line ('共 N "
                 "個 finding：...') nor a leading per-axis count line "
                 "('Standards 軸共 N 個 finding：...'): %r"
                 % lines[first_idx][:60]))

    # -- per-finding format ---------------------------------------------------
    for f in findings:
        label = f["head"][:48]
        if not f["citations"]:
            violations.append(
                ("finding-format",
                 "finding block %r carries no file:line citation" % label))
        if f["verdict"] is None:
            violations.append(
                ("finding-format",
                 "finding block %r has no CONFIRMED/PLAUSIBLE verdict"
                 % label))
        if f["origin"] is None:
            violations.append(
                ("finding-format",
                 "finding block %r has no introduced/pre-existing origin "
                 "marker" % label))
        if f["axis"] is None:
            violations.append(
                ("finding-format",
                 "finding block %r has no axis (no Standards/Spec section "
                 "heading above it and no inline tag)" % label))
        if f["verdict"] == "PLAUSIBLE" and not UPGRADE_LINE_RE.search(f["text"]):
            violations.append(
                ("upgrade-condition",
                 "finding block %r is PLAUSIBLE but carries no "
                 "upgrade-condition line (升級條件)" % label))

    return findings, violations, root_cause_found


# ---- Matching ---------------------------------------------------------------

def first_citation(finding):
    """Display label for a finding: its first citation, else its head line."""
    if finding["citations"]:
        path, lo, _ = finding["citations"][0]
        return "%s:%d" % (path, lo)
    return finding["head"][:40]


def finding_matches(item, finding, tolerance):
    blob = finding["text"].lower()
    if not any(kw.lower() in blob for kw in item["match_any"]):
        return False
    for path, lo, hi in finding["citations"]:
        if Path(path).name != item["file"]:
            continue
        for rlo, rhi in item["line_ranges"]:
            if max(lo, rlo - tolerance) <= min(hi, rhi + tolerance):
                return True
    return False


def zone_label(finding, noise_zones):
    for path, lo, _ in finding["citations"]:
        name = Path(path).name
        for zone in noise_zones:
            zlo, zhi = zone["lines"]
            if name == zone["file"] and zlo <= lo <= zhi:
                return "clean zone %s (%s)" % (zone["id"], zone["why_clean"])
    return None


def score_report_text(text, expected):
    findings, violations, root_cause_found = parse_report(text)
    items = expected["expected"]
    tolerance = int(expected.get("line_tolerance", DEFAULT_LINE_TOLERANCE))
    noise_zones = expected.get("noise_zones", [])

    lines = ["fixture: %s (ticket_type=%s); %d expected items"
             % (expected.get("fixture", "?"),
                expected.get("ticket_type", "?"), len(items)),
             "-- expected items --"]

    hit_ids, miss_ids = [], []
    hits_by_item = {}
    for item in items:
        matched = [f for f in findings if finding_matches(item, f, tolerance)]
        hits_by_item[item["id"]] = matched
        if matched:
            hit_ids.append(item["id"])
            lines.append("[HIT ] %-5s %-13s %s"
                         % (item["id"], "(" + item["class"] + ")",
                            first_citation(matched[0])))
        else:
            miss_ids.append(item["id"])
            lines.append("[MISS] %-5s %-13s no finding matched %s:%d-%d "
                         "(keywords: %s)"
                         % (item["id"], "(" + item["class"] + ")",
                            item["file"], item["line_ranges"][0][0],
                            item["line_ranges"][-1][1],
                            "|".join(item["match_any"])))

    lines.append("-- noise --")
    noise = []
    for f in findings:
        if any(f in hits_by_item[i["id"]] for i in items):
            continue
        label = zone_label(f, noise_zones)
        noise.append(f)
        where = first_citation(f)
        if label:
            lines.append("[NOISE] %s matches no expected item -- %s"
                         % (where, label))
        else:
            lines.append("[NOISE] %s matches no expected item" % where)
    if not noise:
        lines.append("none")

    # -- origin mislabel (strict items only) ----------------------------------
    for item in items:
        if not item.get("origin_strict"):
            continue
        for f in hits_by_item[item["id"]]:
            if f["origin"] and f["origin"] != item["origin"]:
                violations.append(
                    ("origin-mislabel",
                     "%s is a planted %s issue but the finding at %s is "
                     "marked %s" % (item["id"], item["origin"],
                                    first_citation(f), f["origin"])))

    # -- root-cause section ----------------------------------------------------
    if expected.get("ticket_type") == "bug-fix" and not root_cause_found:
        violations.append(
            ("root-cause",
             "the ticket is a bug-fix but the report carries no root-cause "
             "section (a heading or label line with 成因 / root cause)"))

    lines.append("-- format --")
    if violations:
        for code, message in violations:
            lines.append("[%s] %s" % (code, message))
    else:
        lines.append("none")

    classes = sorted({i["class"] for i in items})
    classes_hit = len({i["class"] for i in items if i["id"] in hit_ids})
    passed = (classes_hit >= MIN_CLASSES_HIT
              and len(violations) <= MAX_FORMAT_VIOLATIONS
              and len(noise) <= MAX_NOISE)
    lines.append("-- summary --")
    lines.append(
        "recall %d/%d items; classes %d/%d hit (min %d); noise %d (max %d); "
        "violations %d (max %d) -> %s"
        % (len(hit_ids), len(items), classes_hit, len(classes),
           MIN_CLASSES_HIT, len(noise), MAX_NOISE, len(violations),
           MAX_FORMAT_VIOLATIONS, "PASS" if passed else "FAIL"))

    return {
        "lines": lines,
        "exit_code": 0 if passed else 1,
        "hit_ids": hit_ids,
        "miss_ids": miss_ids,
        "noise": noise,
        "violations": violations,
        "classes_hit": classes_hit,
        "classes_total": len(classes),
    }


# ---- Built-in selftest ------------------------------------------------------

CANNED_PASS_REPORT = """\
共 6 個 finding：0 個 CONFIRMED／6 個 PLAUSIBLE／3 個 pre-existing

單人審查環境（無獨立複核條件），依規則 verdict 上限為 PLAUSIBLE。

## Standards 軸

### [PLAUSIBLE] [introduced] commands.py:12 — 新增 done.log 違反 R1
`_DONE_LOG` 為任務狀態建立第二份持久化檔案，違反 .dev-notes/CODE-REVIEW.md R1（狀態只存在於 tasks.json）。
失效情境：`todo done 1` 後 tasks.json 內容不變、done.log 另行記錄，兩份狀態各自演化；只讀 tasks.json 的任何消費者都會把該任務視為未完成。
升級條件：用第二個工具讀取 tasks.json 驗證 done 欄位確實缺席，即可升 CONFIRMED。

### [PLAUSIBLE] [pre-existing] commands.py:86 — 無子命令時靜默退出
`run()` 在 `handlers.get(args.command)` 得到 None 時直接回 2，不印 usage；base 即如此，本 diff 未觸及（pre-existing，不擋 merge、建議另開票）。
失效情境：裸執行 `todo` → 無任何輸出、exit code 2，使用者無從得知可用子命令。
升級條件：實際以無參數執行 `todo` 並記錄輸出與 exit code，即可升 CONFIRMED。

## Spec 軸

### [PLAUSIBLE] [introduced] commands.py:40 — append_done_id 以 "w" 模式覆寫 done.log
`append_done_id()` 以 `open(_DONE_LOG, "w")` 開檔，每次 `todo done` 都會清空先前記錄。
失效情境：`todo add a; todo add b; todo done 1; todo done 2; todo list --all` → 任務 1 已被標完成卻顯示 `[ ]`。
升級條件：實跑上述指令序列並貼上輸出，即可升 CONFIRMED。

### [PLAUSIBLE] [introduced] commands.py:20 — cmd_add 拒絕重複標題（票未要求）
`cmd_add` 對 `task.title == args.title` 印 `error: task already exists` 並回 1；TICKET-331 為 bug-fix 票，四條 AC 皆未要求此行為。
失效情境：同一標題輸入兩次 `todo add "write report"` → 第二次被拒（exit 1），既有自動化流程中斷。
升級條件：逐條對照 TICKET.md 的 AC1–AC4 確認無一涵蓋，即為文件可證之確定事實。

### Root cause 查核（bug-fix）

成因：`store.save()` 寫出的 rows 只含 id 與 title，`done` 欄位從未進入 tasks.json（store.py:36），`load()` 也從不讀回；done 狀態的往返在 base 就是斷的。本 patch 未指認此成因，改以 done.log 側檔繞過症狀——依 §3 應開 finding 要求補指認：修法應讓 save()/load() 往返 `done` 欄位。

### [PLAUSIBLE] [pre-existing] store.py:41 — root cause 未修：save() 未寫出 done 欄位
承接上段：修法只壓症狀、成因仍在。save() 的 rows 產生式只含 id/title，done 永不持久化，同型缺陷會再發。
失效情境：即使把 done.log 改成 append 模式，tasks.json 依舊缺少 done 狀態；任何其他讀者讀到的都是過期資料。
升級條件：執行票面 repro 後檢查 tasks.json 內容（無 done 欄位），即可升 CONFIRMED。

### [PLAUSIBLE] [pre-existing] store.py:36 — AC3 未達成：load() 以 enumerate 重新編號
`load()` 用 `enumerate(rows, start=1)` 重新賦 id，save/load 往返後 id 不穩定；AC3 要求「ids stay stable across restarts」，本 diff 未處理（成因屬既有碼）。
失效情境：`todo add a; todo add b; todo add c; todo rm 2; todo list` → 剩餘任務顯示 id 1、2（新增時為 1、3）。
升級條件：實跑上列指令並比對前後 id，即可升 CONFIRMED。
"""

CANNED_FAIL_REPORT = """\
# TICKET-331 變更審查報告

## Spec 軸

### [PLAUSIBLE] [introduced] commands.py:40 — done.log 每次被覆寫
`append_done_id` 以 "w" 模式開檔，第二次 `todo done` 會清掉前一次的記錄。
失效情境：`todo done 1; todo done 2; todo list --all` → 任務 1 顯示 `[ ]`。

### [PLAUSIBLE] [introduced] parse.py:17 — 新增 --all 旗標
diff 加了 `--all` 旗標；沒有對照票面確認是否被要求，先報再說。
失效情境：使用者多了一個未經票面核可的選項。
升級條件：對照 TICKET-331 確認 --all 是否在 AC 內。

### [PLAUSIBLE] [introduced] store.py:30 — id 重新編號
`enumerate(rows, start=1)` 每次載入都重新賦 id，AC3 的 stable 要求未達成。
失效情境：rm 之後重新 list，id 與新增時不同。
升級條件：實跑 add/rm/list 序列並比對 id。

## Standards 軸

### [PLAUSIBLE] [introduced] commands.py:12 — 違反 R1
新增 done.log 作為第二份狀態檔，違反 .dev-notes/CODE-REVIEW.md 的 R1。
失效情境：tasks.json 與 done.log 各自記錄狀態，消費者看到不一致。
升級條件：讀 R1 條文並對照 done.log 的寫入位置。

### [PLAUSIBLE] [introduced] commands.py:86 — 無 usage 輸出
`handlers.get` 拿不到 handler 時直接 return 2，使用者看不到 usage。
失效情境：裸執行 `todo` 無輸出、exit 2。
升級條件：無參數執行一次並記錄結果。
"""

CANNED_REPORTS = {"pass": CANNED_PASS_REPORT, "fail": CANNED_FAIL_REPORT}


def _check_pass_case(result):
    problems = []
    if result["exit_code"] != 0:
        problems.append("expected exit 0, got %d" % result["exit_code"])
    if sorted(result["hit_ids"]) != ["EF-1", "EF-2", "EF-3", "EF-4",
                                     "EF-5", "EF-6"]:
        problems.append("expected all six items hit, got %s"
                        % sorted(result["hit_ids"]))
    if result["noise"]:
        problems.append("expected 0 noise, got %d" % len(result["noise"]))
    if result["violations"]:
        problems.append("expected 0 violations, got %s"
                        % [v[0] for v in result["violations"]])
    return problems


def _check_fail_case(result):
    problems = []
    if result["exit_code"] != 1:
        problems.append("expected exit 1, got %d" % result["exit_code"])
    codes = {code for code, _ in result["violations"]}
    for wanted in ("count-line", "upgrade-condition", "origin-mislabel",
                   "root-cause"):
        if wanted not in codes:
            problems.append("violation [%s] not reported" % wanted)
    for missed in ("EF-3", "EF-6"):
        if missed not in result["miss_ids"]:
            problems.append("%s should be missed" % missed)
    if len(result["noise"]) != 1:
        problems.append("expected exactly 1 noise finding, got %d"
                        % len(result["noise"]))
    return problems


def run_selftest(expected_path):
    expected = load_expected(Path(expected_path))
    cases = [
        ("canned compliant report scores exit 0 (all items, no noise)",
         CANNED_PASS_REPORT, _check_pass_case),
        ("canned deficient report is caught (exit 1, violations + noise)",
         CANNED_FAIL_REPORT, _check_fail_case),
    ]
    failures = 0
    for label, text, check in cases:
        result = score_report_text(text, expected)
        problems = check(result)
        ok = not problems
        failures += 0 if ok else 1
        print("%-4s %s" % ("PASS" if ok else "FAIL", label))
        for problem in problems:
            print("      - %s" % problem)
        if not ok:
            for line in result["lines"]:
                print("      | %s" % line)
    print("")
    print("score_review selftest: %d of %d cases passed"
          % (len(cases) - failures, len(cases)))
    return 1 if failures else 0


# ---- Entry ------------------------------------------------------------------

def score_file(report_path, expected_path):
    try:
        text = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        die(2, "cannot read report %s: %s" % (report_path, exc))
    except UnicodeDecodeError as exc:
        die(2, "report %s is not valid UTF-8: %s" % (report_path, exc))
    expected = load_expected(expected_path)
    return score_report_text(text, expected)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Score a two-axis review report against expected "
                    "findings (see tests/review-evals/README.md).")
    parser.add_argument("report", nargs="?",
                        help="review report file to score")
    parser.add_argument("--selftest", action="store_true",
                        help="run the built-in canned-report cases")
    parser.add_argument("--expected", metavar="PATH",
                        default=str(DEFAULT_EXPECTED_PATH),
                        help="expected-findings JSON (default: alongside "
                             "this script)")
    parser.add_argument("--emit-selftest-report", dest="emit",
                        metavar="WHICH:PATH",
                        help="write a built-in canned report to PATH "
                             "(WHICH is pass or fail) and exit 0")
    args = parser.parse_args(argv)

    if args.emit:
        which, sep, path = args.emit.partition(":")
        if which not in CANNED_REPORTS or not sep or not path:
            parser.error("--emit-selftest-report must be pass:PATH or "
                         "fail:PATH")
        Path(path).write_text(CANNED_REPORTS[which], encoding="utf-8")
        return 0
    if args.selftest:
        return run_selftest(Path(args.expected))
    if not args.report:
        parser.error("a report file is required (or use --selftest)")
    result = score_file(Path(args.report), Path(args.expected))
    print("scoring %s against %s" % (args.report, args.expected))
    for line in result["lines"]:
        print(line)
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
