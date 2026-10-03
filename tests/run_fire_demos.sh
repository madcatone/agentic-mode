#!/bin/sh
# Fire-demo regression suite for checker/check_agentic_docs.py.
#
# Each case under tests/fire-demos/ is a self-contained doc set plus
# config.json that must make the checker exit with the declared code:
# 0 = satisfied doc set passes, 1 = violation is flagged, 2 = bad config is
# rejected. A checker change that silently stops firing (or starts firing on
# a satisfied set) turns a PASS into a FAIL here.
#
# Case-name families (ported from the #1 hardening rounds):
#   c*  round 1 -- ported fixes C1-C7
#   r*  round 2 -- review findings (#1-#7, r1r/r2r = follow-ups to #1/#2)
#   s*  follow-up fence findings (S1/S2, code spans)
#   b*  docs-only adoption findings
#   g*  coverage gaps found in read-back (one firing case per check family)
#
# Neutrality rule: deny words in these fixtures are fictional
# (vexide/zorpal/novera/fictool) and reach the deny list only via
# checks.harness_neutrality.extra_deny. No real product name may appear
# anywhere under tests/ -- the suite must stay harness-neutral.
#
# Usage (from anywhere; paths resolve relative to the repo root):
#   sh tests/run_fire_demos.sh    # all pass -> exit 0, any mismatch -> exit 1

set -u

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$REPO_ROOT" || exit 2

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT INT TERM

pass=0
fail=0

expect() {
    _expected=$1
    _dir=$2
    _desc=$3
    python3 checker/check_agentic_docs.py \
        --config "tests/fire-demos/$_dir/config.json" \
        --root "tests/fire-demos/$_dir" >"$tmp" 2>&1
    _actual=$?
    if [ "$_actual" = "$_expected" ]; then
        printf 'PASS %-40s exit %s -- %s\n' "$_dir" "$_actual" "$_desc"
        pass=$((pass + 1))
    else
        printf 'FAIL %-40s expected exit %s, got %s -- %s\n' \
            "$_dir" "$_expected" "$_actual" "$_desc"
        sed 's/^/    | /' "$tmp"
        fail=$((fail + 1))
    fi
}

# ---- round 1: ported fixes C1-C7 ------------------------------------------
expect 2 c1a-iteration-switch-requires-requirements \
    "iteration_history.enabled=true (the switch) needs docs.requirements declared"
expect 2 c1b-id-continuity-requires-validation \
    "id-continuity has no disable switch; docs.validation must be declared"
expect 1 c2-bounded-command-match \
    "required 'make build' not satisfied by 'make build-all'/'make buildX'"
expect 0 c2-control-exact-command-clean \
    "control: exact 'make build' present -> clean"
expect 2 c3-line-limits-string-config-error \
    "line_limits.agents as string \"200\" -> config error"
expect 1 c5-deny-word-prose-fires-code-exempt \
    "deny word: prose fires; fenced block and inline code span exempt"
expect 1 c6-dangling-id-cited-in-agents \
    "AGENTS.md cites DEM-099 which no doc defines"
expect 1 c7-iteration-history-starts-at-3 \
    "iteration history must start at entry 1, not 3"

# ---- round 2: review findings ----------------------------------------------
expect 1 r1-unit-test-not-satisfy-test \
    "'make unit-test' must not satisfy required command 'test'"
expect 0 r2-iteration-heading-null-clean \
    "iteration_history.heading: null -> built-in default, runs clean"
expect 2 r3a-must-appear-in-false \
    "commands[0].must_appear_in: false -> config error"
expect 2 r3b-deny-words-false \
    "deny_words: false -> config error"
expect 2 r3c-iteration-history-false \
    "iteration_history: false -> config error"
expect 2 r4a-bilingual-enabled-string \
    "bilingual.enabled: \"false\" string -> config error"
expect 2 r4b-harness-neutrality-enabled-string \
    "harness_neutrality.enabled: \"false\" string -> config error"
expect 2 r4c-iteration-history-enabled-string \
    "iteration_history.enabled: \"false\" string -> config error"
expect 2 r4d-forbid-ipv4-string \
    "forbid_ipv4: \"false\" string -> config error"
expect 2 r4e-forbid-local-paths-string \
    "forbid_local_paths: \"false\" string -> config error"
expect 1 r5-document-order-3-1-2 \
    "history listed 3./1./2. -> first entry 3, flagged"
expect 0 r6-primary-heading-null-clean \
    "bilingual.primary_heading: null -> built-in default, runs clean"
expect 1 r7-unclosed-fence-flagged \
    "unclosed fence announced; deny word after it not silently skipped"
expect 1 r1r-unclosed-marker-fence-flagged \
    "marker exempts content only; unclosed marker fence still flagged"
expect 1 r2r-tilde-fence-not-exempt \
    "~~~ is not an exempt fence; deny word inside still reported"

# ---- follow-up: marker fences and code spans -------------------------------
expect 1 s1-marker-fence-degradation-announced \
    "marker fence above deny words: degradation announced, not silent"
expect 0 s2-marked-closing-fence-balanced \
    "marked closing fence, balanced doc -> no false unclosed finding"
expect 0 code-spans-command-after-marker-fences \
    "command in a code span after marker fences still recognized"

# ---- docs-only adoption ------------------------------------------------------
expect 0 b-docs-only-user-guide-null-clean \
    "docs-only project with user_guide null runs clean"
expect 2 b-project-type-misspelled \
    "project.type \"docsonly\" (misspelled) -> enum config error"

# ---- coverage gaps: one firing case per check family -------------------------
expect 1 g1-line-limit-exceeded \
    "AGENTS.md has 5 lines against line_limits.agents 3 -> flagged"
expect 1 g2-entrypoint-missing \
    "declared entrypoint absent from the tree -> flagged"
expect 1 g3-declared-doc-missing \
    "declared user_guide file missing while config is valid -> flagged"

printf '\n%d cases: %d pass, %d fail\n' "$((pass + fail))" "$pass" "$fail"
[ "$fail" -eq 0 ]
