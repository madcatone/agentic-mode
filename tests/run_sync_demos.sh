#!/bin/sh
# Fire-demo suite for the sync gate's structural assertions (issue #16):
# the bootstrap skill dir's file set must be exactly what its manifest
# explains, and every canon path cited by the vendored RUNBOOK must be
# vendored there or disclosed in SKILL.md. An assertion that stops firing
# (or one that fires on a pristine tree) turns a PASS into a FAIL here.
#
# Each case plants its violation in a throwaway copy of the repo (sans .git
# and __pycache__), so the working tree is never touched. The exit code alone
# proves nothing, so the output must also name the planted path (a traceback
# satisfies no contract).
#
# Usage (from anywhere): sh tests/run_sync_demos.sh   # all pass -> exit 0

set -u

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SKILL=adapters/claude-code/plugins/agentic-bootstrap/skills/agentic-bootstrap

pass=0
fail=0
base=$(mktemp -d)
trap 'rm -rf "$base"' EXIT INT TERM

expect() {
    _expected=$1; _plant=$2; _pattern=$3; _desc=$4
    rm -rf "$base/repo"
    mkdir -p "$base/repo"
    (cd "$REPO_ROOT" && git ls-files -z | tar --null -T - -cf -) |
        (cd "$base/repo" && tar -xf -)
    (cd "$base/repo" && sh -c "$_plant")
    python3 "$base/repo/scripts/sync_plugins.py" --check >"$base/out" 2>&1
    _actual=$?
    _why=
    if [ "$_actual" != "$_expected" ]; then
        _why="expected exit $_expected, got $_actual"
    elif grep -q Traceback "$base/out"; then
        _why='traceback present -- a crashed run satisfies no contract'
    elif [ "$_expected" = 0 ]; then
        grep -q 'in sync' "$base/out" || _why='no "in sync" verdict'
    else
        grep -qF -- "$_pattern" "$base/out" ||
            _why="output does not name '$_pattern'"
    fi
    if [ -z "$_why" ]; then
        printf 'PASS exit %s -- %s\n' "$_actual" "$_desc"
        pass=$((pass + 1))
    else
        printf 'FAIL %s -- %s\n' "$_why" "$_desc"
        sed 's/^/    | /' "$base/out"
        fail=$((fail + 1))
    fi
}

expect 0 ':' control 'pristine tree passes clean'

expect 1 "touch $SKILL/reference/STRAY.md" \
    "$SKILL/reference/STRAY.md" \
    'stray file inside the skill dir is named as drift'

expect 1 "printf '\nSee \140examples/minimal-cli/README.md\140 for details.\n' >> RUNBOOK.md; printf '\nSee \140examples/minimal-cli/README.md\140 for details.\n' >> $SKILL/RUNBOOK.md" \
    'examples/minimal-cli/README.md' \
    'RUNBOOK citation with no vendored copy and no SKILL.md disclosure fires'

expect 1 "mv $SKILL/RUNBOOK.md RUNBOOK.hold" \
    "$SKILL/RUNBOOK.md" \
    'missing vendored RUNBOOK reports manifest drift, no traceback'

printf '\n%d cases: %d pass, %d fail\n' "$((pass + fail))" "$pass" "$fail"
[ "$fail" -eq 0 ]
