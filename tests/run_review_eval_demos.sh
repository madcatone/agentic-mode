#!/bin/sh
# Review-eval demo suite for tests/review-evals/score_review.py.
#
# The LLM step of a review eval (a reviewer writing a report from the
# fixtures) is never run by CI; what CI runs is the deterministic machinery:
# the scorer byte-compiles, its built-in selftest passes, the planted
# change.patch still applies to the base fixture, the canned compliant
# report scores exit 0 end-to-end, the canned deficient report scores
# exit 1 with the intended detections (missing count line, PLAUSIBLE without
# an upgrade condition, mislabeled origin, missing root-cause section, one
# noise finding), and the blind smoke-report sample -- a real-format report
# kept verbatim under samples/ -- still scores exit 0 (tolerance regression:
# a grammar narrowing that stops accepting real reports turns its PASS into
# a FAIL). A scorer change that silently stops firing -- or starts passing a
# deficient report -- turns a PASS into a FAIL here.
#
# The exit code alone proves nothing: an unhandled crash also exits 1 with
# confusing output, so each case additionally asserts the substance of the
# output (a summary or finding marker the crashed run cannot produce).
#
# Usage (from anywhere; paths resolve relative to the repo root):
#   sh tests/run_review_eval_demos.sh   # all pass -> exit 0

set -u

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$REPO_ROOT" || exit 2

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT TERM

pass=0
fail=0

expect_exit() {
    _expected=$1
    _frag=$2
    _desc=$3
    shift 3
    "$@" >"$tmp/out" 2>&1
    _actual=$?
    _why=
    if [ "$_actual" != "$_expected" ]; then
        _why="expected exit $_expected, got $_actual"
    elif grep -q 'Traceback' "$tmp/out"; then
        _why='traceback present -- a crashed run satisfies no contract'
    elif [ -n "$_frag" ] && ! grep -Fq -- "$_frag" "$tmp/out"; then
        _why="output lacks '$_frag'"
    fi
    if [ -z "$_why" ]; then
        printf 'PASS %-44s exit %s\n' "$_desc" "$_actual"
        pass=$((pass + 1))
    else
        printf 'FAIL %-44s %s\n' "$_desc" "$_why"
        sed 's/^/    | /' "$tmp/out"
        fail=$((fail + 1))
    fi
}

expect_exit 0 "" "scorer byte-compiles" \
    python3 -m py_compile tests/review-evals/score_review.py

expect_exit 0 "2 of 2 cases passed" "scorer built-in selftest passes" \
    python3 tests/review-evals/score_review.py --selftest

expect_exit 0 "" "todo-review change.patch applies to the base fixture" \
    sh -c 'cd tests/review-evals/fixtures/todo-review && git apply --check change.patch'

expect_exit 0 "-> PASS" "canned compliant report scores exit 0 end-to-end" \
    sh -c 'python3 tests/review-evals/score_review.py --emit-selftest-report "pass:$1" &&
           python3 tests/review-evals/score_review.py "$1"' sh "$tmp/pass-report.md"

expect_exit 1 "[count-line]" "canned deficient report scores exit 1 and fires" \
    sh -c 'python3 tests/review-evals/score_review.py --emit-selftest-report "fail:$1" &&
           python3 tests/review-evals/score_review.py "$1"' sh "$tmp/fail-report.md"

expect_exit 0 "-> PASS" "blind smoke-report sample scores exit 0 (tolerance regression)" \
    python3 tests/review-evals/score_review.py tests/review-evals/samples/smoke-report-r1.md

printf '\n%d cases: %d pass, %d fail\n' "$((pass + fail))" "$pass" "$fail"
[ "$fail" -eq 0 ]
