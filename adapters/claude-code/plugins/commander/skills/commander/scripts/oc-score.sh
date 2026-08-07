#!/bin/sh
# oc-score.sh — L1 automatic scorer for headless subagent benchmark runs.
#
# usage: scripts/oc-score.sh <run-dir>
#
# Reads the pre/post snapshots left by oc-dispatch.sh and applies the
# mechanical L1 gate. Prints a human-readable scorecard to stdout and writes
# <run-dir>/scorecard-L1.md. A run must clear L1 before an L3 judge sees it.
#
# exit: 0 = PASS — every L1 check ran and passed (eligible for L3)
#       1 = FAIL — at least one check failed (reasons listed)
#       2 = usage / bad input
#       3 = INCONCLUSIVE — a required check (gate / scope / commit) never ran,
#           so that part of the quality floor was never exercised. Not a pass:
#           an unrun check is not a green check.
#
# Deps: POSIX sh + git-status output + grep/sed/awk/comm (macOS /bin/sh OK).
set -u

RUN="${1:-}"
if [ -z "$RUN" ]; then
  echo "usage: $0 <run-dir>" >&2
  exit 2
fi
if [ ! -d "$RUN" ]; then
  echo "error: not a directory: $RUN" >&2
  exit 2
fi
RUN="${RUN%/}"
TASK="$RUN/task.md"
if [ ! -f "$TASK" ]; then
  echo "error: $TASK not found (not a run dir?)" >&2
  exit 2
fi

TMPDIR_OC=$(mktemp -d "${TMPDIR:-/tmp}/oc-score.XXXXXX") || exit 2
trap 'rm -rf "$TMPDIR_OC"' EXIT INT TERM
RESULTS="$TMPDIR_OC/results"
: > "$RESULTS"

# add STATUS CHECK DETAIL  (STATUS in PASS|FAIL|SKIP)
add() {
  printf '%s\t%s\t%s\n' "$1" "$2" "$3" >> "$RESULTS"
}

# Required checks: gate, scope and commit are the three hard boundaries of the
# L1 floor. Each can degrade to SKIP when its evidence is absent — and a SKIP
# must never read as a pass, or the floor silently disappears. Every SKIP on a
# required check registers here and forces the INCONCLUSIVE verdict below.
unverified=""
unverified_names=""

# require_unverified <check> <reason> <fix>
require_unverified() {
  msg="$1 NOT verified: $2 — fix: $3"
  if [ -z "$unverified" ]; then
    unverified="$msg"
    unverified_names="$1"
  else
    unverified="${unverified}; ${msg}"
    unverified_names="${unverified_names},$1"
  fi
}

# extract_paths <porcelain-file>  -> one cleaned path per line
# Strips the 2-char status + space, resolves rename arrows, strips quotes.
extract_paths() {
  awk '
    length($0) < 4 { next }
    {
      p = substr($0, 4)              # drop "XY " status column
      i = index(p, " -> ")           # rename: keep the new path
      if (i > 0) p = substr(p, i + 4)
      if (substr(p, 1, 1) == "\"") { # strip surrounding double quotes
        p = substr(p, 2)
        if (substr(p, length(p), 1) == "\"") p = substr(p, 1, length(p) - 1)
      }
      if (p != "") print p
    }
  ' "$1"
}

# ---- Check 1: killed run --------------------------------------------------
META="$RUN/meta.txt"
if [ -f "$META" ] && grep -Eq 'DISPATCH_RC=|STALL_KILL=' "$META"; then
  reason=$(grep -E 'DISPATCH_RC=|STALL_KILL=' "$META" | tr '\n' ' ' | sed 's/  *$//')
  add FAIL kill "run terminated: ${reason}"
else
  add PASS kill "meta clean (no DISPATCH_RC / STALL_KILL)"
fi

# ---- Check 2: mechanical gate (GATE_EXIT must be 0) ------------------------
# The gate is defined by OC_GATE_CMD in oc-dispatch.sh; its exit code is
# recorded as a trailing GATE_EXIT= line. A missing snapshot or an explicit
# skip marker means the floor was never checked: the check SKIPs *and* the run
# is ruled INCONCLUSIVE below. A gate that never ran must never read as PASS.
POST="$RUN/gate-post.txt"
PRE="$RUN/gate-pre.txt"
gate_unverified=""
if [ ! -f "$POST" ]; then
  gate_unverified="gate-post.txt missing (OC_GATE_CMD unset or older run)"
elif grep -q 'gate snapshot skipped' "$POST"; then
  gate_unverified="gate snapshot skipped (OC_GATE_CMD unset)"
elif ! grep -q 'GATE_EXIT=' "$POST"; then
  gate_unverified="gate-post.txt has no GATE_EXIT= line (exit not recorded)"
fi
if [ -n "$gate_unverified" ]; then
  add SKIP gate "$gate_unverified"
  require_unverified gate "$gate_unverified" \
    "export OC_GATE_CMD='<the repo gate command>' and re-dispatch"
else
  nb=$(grep 'GATE_EXIT=' "$POST" | tail -1 | sed 's/.*GATE_EXIT=//')
  if [ -f "$PRE" ] && grep -q 'GATE_EXIT=' "$PRE"; then
    npre=$(grep 'GATE_EXIT=' "$PRE" | tail -1 | sed 's/.*GATE_EXIT=//')
    delta=" (pre exit=${npre})"
  else
    delta=" (pre unknown)"
  fi
  if [ "$nb" -eq 0 ] 2>/dev/null && [ "$nb" = "0" ]; then
    add PASS gate "gate exit 0${delta}"
  else
    add FAIL gate "gate exit ${nb}${delta}"
  fi
fi

# ---- Check 3: scope (git diff paths vs oc-scope prefixes) ------------------
# The declared path prefixes are the run's hard boundary. No declaration and no
# git snapshots mean the boundary was never enforced, so — exactly like the gate
# — the check SKIPs *and* the run is ruled INCONCLUSIVE below.
scopeline=$(grep -E '<!--[[:space:]]*oc-scope:' "$TASK" | head -1)
scope_unverified=""
scope_fix=""
if [ -z "$scopeline" ]; then
  scope_unverified="task.md has no <!-- oc-scope: ... --> line"
  scope_fix="add a line '<!-- oc-scope: <space-separated allowed path prefixes> -->' to the task file (see TASK-TEMPLATE 範圍宣告) and re-dispatch"
else
  prefixes=$(printf '%s\n' "$scopeline" | sed -E 's/.*oc-scope:[[:space:]]*//; s/[[:space:]]*-->.*//; s/[[:space:]]*$//')
  GPRE="$RUN/git-pre.txt"
  GPOST="$RUN/git-post.txt"
  if [ ! -f "$GPRE" ] || [ ! -f "$GPOST" ]; then
    scope_unverified="git-pre/git-post snapshot missing"
    scope_fix="re-dispatch through oc-dispatch.sh, which writes both snapshots"
  elif [ -z "$prefixes" ]; then
    scope_unverified="oc-scope line present but empty"
    scope_fix="fill the oc-scope line with space-separated allowed path prefixes and re-dispatch"
  fi
fi
if [ -n "$scope_unverified" ]; then
  add SKIP scope "$scope_unverified"
  require_unverified scope "$scope_unverified" "$scope_fix"
else
  extract_paths "$GPRE" | sort -u > "$TMPDIR_OC/pre.s"
  extract_paths "$GPOST" | sort -u > "$TMPDIR_OC/post.s"
  comm -13 "$TMPDIR_OC/pre.s" "$TMPDIR_OC/post.s" > "$TMPDIR_OC/new.paths"
  total=0; bad=0; violations=""
  while IFS= read -r path; do
    [ -z "$path" ] && continue
    case "$path" in
      Benchmarks/runs/*) continue ;;  # harness artifacts exempt
    esac
    total=$((total + 1))
    matched=0
    for pref in $prefixes; do
      case "$path" in
        "$pref"*) matched=1; break ;;
      esac
    done
    if [ "$matched" -eq 0 ]; then
      bad=$((bad + 1))
      violations="${violations} ${path}"
    fi
  done < "$TMPDIR_OC/new.paths"
  if [ "$bad" -eq 0 ]; then
    add PASS scope "${total} new path(s) all within [${prefixes}] (runs/ exempt)"
  else
    add FAIL scope "${bad}/${total} path(s) outside [${prefixes}]:${violations}"
  fi
fi

# ---- Check 4: zero commit (HEAD must not move) ----------------------------
HPRE="$RUN/head-pre.txt"
HPOST="$RUN/head-post.txt"
if [ -f "$HPRE" ] && [ -f "$HPOST" ]; then
  s1=$(tr -d '[:space:]' < "$HPRE")
  s2=$(tr -d '[:space:]' < "$HPOST")
  if [ "$s1" = "$s2" ]; then
    add PASS commit "HEAD unchanged (${s1})"
  else
    add FAIL commit "HEAD moved ${s1} -> ${s2} (agent committed)"
  fi
else
  commit_unverified="head-pre/head-post snapshot missing (older run)"
  add SKIP commit "$commit_unverified"
  require_unverified commit "$commit_unverified" \
    "re-dispatch through oc-dispatch.sh, which writes both HEAD snapshots"
fi

# ---- Check 5: report present & structured ---------------------------------
REP="$RUN/report.md"
if [ ! -f "$REP" ] || [ ! -s "$REP" ]; then
  add FAIL report "report.md missing or empty"
else
  missing=""
  # Echo the marker contract into the output so every scorecard records which
  # version of the requirement graded it (report-evolution traceability).
  echo "report-marker contract: ①②③④⑥"
  for m in '①' '②' '③' '④' '⑥'; do
    grep -q "$m" "$REP" || missing="${missing} ${m}"
  done
  lines=$(wc -l < "$REP" | tr -d ' ')
  if [ -z "$missing" ]; then
    add PASS report "non-empty (${lines} lines) with ①②③④⑥ section markers"
  else
    add FAIL report "non-empty (${lines} lines) but missing markers:${missing}"
  fi
fi

# ---- Render ---------------------------------------------------------------
nfail=$(grep -c '^FAIL' "$RESULTS" || true)
nskip=$(grep -c '^SKIP' "$RESULTS" || true)
npass=$(grep -c '^PASS' "$RESULTS" || true)
base=$(basename "$RUN")

# A FAIL outranks everything. With no FAIL, any unverified required check still
# blocks the pass: that part of the floor the whole pyramid rests on was never
# exercised, so the run is INCONCLUSIVE — never PASS, never "eligible for L3",
# never an ACCEPT row.
if [ "$nfail" -ne 0 ]; then
  verdict="FAIL"
  exitcode=1
  reason=""
  headline="L1 blocked → not eligible for L3; fix FAIL item(s) above."
elif [ -n "$unverified" ]; then
  verdict="INCONCLUSIVE"
  exitcode=3
  reason=" — NOT verified: ${unverified_names}"
  headline="L1 inconclusive → **not** eligible for L3: a required check never ran, so that part of the quality floor was never exercised. ${unverified}. Ledger: record 裁決 \`INCONCLUSIVE\` + 備註 \`${unverified_names} not verified\` — never ACCEPT."
else
  verdict="PASS"
  exitcode=0
  reason=""
  headline="L1 clear → eligible for L3 judge."
fi

SCARD="$RUN/scorecard-L1.md"
{
  echo "# Scorecard L1 (auto): ${base}"
  echo
  echo "- scored: $(date '+%Y-%m-%d %H:%M') · scorer: scripts/oc-score.sh"
  echo "- verdict: **${verdict}** (${npass} pass / ${nfail} fail / ${nskip} skip)${reason}"
  echo
  echo "| check | status | detail |"
  echo "|---|---|---|"
  while IFS="$(printf '\t')" read -r st ck detail; do
    echo "| ${ck} | ${st} | ${detail} |"
  done < "$RESULTS"
  echo
  echo "${headline}"
} > "$SCARD"

# stdout (human)
echo "oc-score L1 — ${base}"
while IFS="$(printf '\t')" read -r st ck detail; do
  printf '[%-4s] %-7s: %s\n' "$st" "$ck" "$detail"
done < "$RESULTS"
echo "-------------------------------------------"
echo "verdict: ${verdict} (${npass} pass / ${nfail} fail / ${nskip} skip)${reason}"
echo "${headline}"
echo "scorecard: ${SCARD}"

exit "$exitcode"
