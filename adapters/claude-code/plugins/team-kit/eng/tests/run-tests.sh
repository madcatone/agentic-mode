#!/bin/sh
# run-tests.sh — fixture-driven tests for the team-kit/eng gate scripts.
# Every decision branch of verify-on-stop.sh and reviewer-git-only.sh gets at
# least one positive and one negative case; verify.sh is exercised end-to-end
# through verify-on-stop.sh against real mini projects, and directly for its
# config validation (empty step name/cmd must be a loud error).
set -u

ENG=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FIX=$ENG/tests/fixtures
VOS=$ENG/verify-on-stop.sh
RGO=$ENG/reviewer-git-only.sh

# Keep parent env from leaking into cases.
unset AGENT_STATE_HOME TEAM_KIT_ROOT TK_VERIFY_CMD TK_MAX_ATTEMPTS TK_TAIL_LINES

pass=0; fail=0; tmpdirs=''
okc() { pass=$((pass+1)); printf 'ok   %s\n' "$1"; }
badc() { fail=$((fail+1)); printf 'FAIL %s: %s\n' "$1" "$2"; }
newst() { st=$(mktemp -d); tmpdirs="$tmpdirs
$st"; }
# newline-separated list; loop instead of unquoted rm (zsh does not word-split)
cleanup() {
  if [ -n "$tmpdirs" ]; then
    printf '%s\n' "$tmpdirs" | while IFS= read -r d; do [ -n "$d" ] && rm -rf "$d"; done
  fi
}
trap cleanup EXIT INT TERM

# --- reviewer-git-only.sh ---------------------------------------------------
# rgo_case <name> <fixture> allow|deny [reason-substring]
rgo_case() {
  out=$(sh "$RGO" < "$FIX/$2" 2>/dev/null); rc=$?
  if [ "$3" = allow ]; then
    if [ -z "$out" ] && [ "$rc" -eq 0 ]; then okc "$1"; else badc "$1" "expected silent allow, got rc=$rc out=[$out]"; fi
    return
  fi
  dec=$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null)
  reason=$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecisionReason // empty' 2>/dev/null)
  n=$(printf '%s' "$out" | grep -c '' 2>/dev/null)
  verdict=ok
  [ "$rc" -eq 0 ] || verdict="exit $rc"
  [ "$dec" = deny ] || verdict="decision=$dec"
  [ "$n" -eq 1 ] || verdict="lines=$n"
  if [ $# -ge 4 ]; then
    case $reason in *"$4"*) ;; *) verdict="reason lacks '$4'" ;; esac
  fi
  if [ "$verdict" = ok ]; then okc "$1"; else badc "$1" "$verdict out=[$out]"; fi
}

# (1) write/execute-class tool_name -> deny
rgo_case rgo-edit-deny          rgo-edit.json      deny "read-only"
rgo_case rgo-write-deny         rgo-write.json     deny "read-only"
rgo_case rgo-terminal-deny      rgo-terminal.json  deny "read-only"
# ...a non-writing tool still has to pass the git-only gate (this is a git-only hook)
rgo_case rgo-nonbash-nongit-deny rgo-bashclass.json deny "git"
# (1b) non-command tools (no tool_input.command), not write/exec class -> silent allow
rgo_case rgo-read-allow        rgo-read.json            allow
rgo_case rgo-grep-allow        rgo-grep.json            allow
rgo_case rgo-glob-allow        rgo-glob.json            allow
rgo_case rgo-webfetch-nocmd-allow rgo-webfetch-nocmd.json allow
# (2a) metachar blacklist -> deny
rgo_case rgo-pipe-deny          rgo-pipe.json         deny "metacharacter"
rgo_case rgo-semi-deny          rgo-semi.json         deny "metacharacter"
rgo_case rgo-backtick-deny      rgo-backtick.json     deny "metacharacter"
rgo_case rgo-subshell-deny      rgo-subshell.json     deny "metacharacter"
rgo_case rgo-amp-deny           rgo-amp.json          deny "metacharacter"
rgo_case rgo-redirout-deny      rgo-redirect-out.json deny "metacharacter"
rgo_case rgo-redirin-deny       rgo-redirect-in.json  deny "metacharacter"
rgo_case rgo-heredoc-deny       rgo-heredoc.json      deny "metacharacter"
rgo_case rgo-paren-deny         rgo-paren.json        deny "metacharacter"
rgo_case rgo-newline-deny       rgo-newline.json      deny "metacharacter"
# (2b) whitelist
rgo_case rgo-git-status-allow   rgo-git-status.json       allow
rgo_case rgo-git-status-flags-allow rgo-git-status-flags.json allow
rgo_case rgo-git-show-allow     rgo-git-show.json         allow
rgo_case rgo-git-revparse-allow rgo-git-revparse.json     allow
rgo_case rgo-git-blame-allow    rgo-git-blame.json        allow
rgo_case rgo-git-lsfiles-allow  rgo-git-lsfiles.json      allow
rgo_case rgo-non-git-deny       rgo-non-git.json          deny "git subcommands are allowed"
rgo_case rgo-git-push-deny      rgo-git-push.json         deny "not whitelisted"
# (2b-F7) git -C <dir> prefix + --no-pager: allow read-only, deny the rest
rgo_case rgo-git-c-status-allow   rgo-git-c-status.json      allow
rgo_case rgo-git-c-log-allow      rgo-git-c-log.json         allow
rgo_case rgo-git-c-attached-allow rgo-git-c-attached.json    allow
rgo_case rgo-git-c-nopager-allow  rgo-git-c-nopager.json     allow
rgo_case rgo-git-c-push-deny      rgo-git-c-push.json        deny "not whitelisted"
rgo_case rgo-git-c-metachar-deny  rgo-git-c-metachar.json    deny "metacharacter"
rgo_case rgo-git-c-quote-deny     rgo-git-c-quote-deny.json  deny "allowed path set"
rgo_case rgo-git-c-dollar-deny    rgo-git-c-dollar-deny.json deny "allowed path set"
rgo_case rgo-git-c-output-deny    rgo-git-c-output-deny.json deny "--output"
rgo_case rgo-git-c-noarg-deny     rgo-git-c-noarg-deny.json  deny "whitelisted git subcommand"
rgo_case rgo-git-c-config-deny    rgo-git-c-config-deny.json deny "not whitelisted"
rgo_case rgo-git-c-extdiffval-deny rgo-git-c-extdiff-val.json deny "--ext-diff"
# (2c) dangerous flags -> deny
rgo_case rgo-extdiff-deny       rgo-ext-diff.json  deny "--ext-diff"
rgo_case rgo-output-deny        rgo-output.json    deny "--output"
rgo_case rgo-textconv-deny      rgo-textconv.json  deny "--textconv"
# parse failure -> deny
rgo_case rgo-invalid-deny       rgo-invalid.json   deny "parse"

# --- verify-on-stop.sh ------------------------------------------------------
# vos_allow <name> <fixture> [KEY=VAL...] — expect {} and exit 0
vos_allow() {
  name=$1; fix=$2; shift 2
  newst
  out=$(env AGENT_STATE_HOME="$st" "$@" sh "$VOS" < "$FIX/$fix" 2>/dev/null); rc=$?
  if [ "$rc" -eq 0 ] && [ "$out" = "{}" ]; then okc "$name"; else badc "$name" "expected {} exit 0, got rc=$rc out=[$out]"; fi
}
# vos_block <name> <fixture> <reason-substring> [KEY=VAL...] — expect one-line block JSON
vos_block() {
  name=$1; fix=$2; substr=$3; shift 3
  newst
  out=$(env AGENT_STATE_HOME="$st" "$@" sh "$VOS" < "$FIX/$fix" 2>/dev/null); rc=$?
  dec=$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)
  reason=$(printf '%s' "$out" | jq -r '.reason // empty' 2>/dev/null)
  n=$(printf '%s' "$out" | grep -c '' 2>/dev/null)
  verdict=ok
  [ "$rc" -eq 0 ] || verdict="exit $rc"
  [ "$dec" = block ] || verdict="decision=$dec"
  [ "$n" -eq 1 ] || verdict="lines=$n"
  case $reason in *"$substr"*) ;; *) verdict="reason lacks '$substr'" ;; esac
  if [ "$verdict" = ok ]; then okc "$name"; else badc "$name" "$verdict out=[$out]"; fi
}

STUB_FAIL='echo "make: error E1234 in parser.c" >&2; echo "  12 tests failed"; exit 1'
STUB_FAIL_SILENT='exit 1'

# (0-F1) jq unavailable (PATH carries no jq): the gate must fail LOUD, not
#        silently — stderr warning + hook-log "jq missing—gate inert" line,
#        decision stays allow {} (blocking would deadlock the status: BLOCKED
#        escape hatch, and the block JSON itself needs jq).
newst
fakebin=$(mktemp -d); tmpdirs="$tmpdirs
$fakebin"
for t in sh dirname cat mkdir date; do ln -s "$(command -v "$t")" "$fakebin/$t"; done
out=$(env AGENT_STATE_HOME="$st" PATH="$fakebin" sh "$VOS" < "$FIX/vos-coder-fail.json" 2>"$st/err"); rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "{}" ] && grep -q 'jq missing' "$st/err" \
   && grep -qF 'jq missing—gate inert' "$st/team-kit/hook-log.txt"; then
  okc vos-jq-missing-allow
else
  badc vos-jq-missing-allow "rc=$rc out=[$out] err=[$(cat "$st/err" 2>/dev/null)] log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# (1) non-coder agent_type / null / unparseable input -> allow {}
vos_allow vos-noncoder-allow   vos-noncoder.json
vos_allow vos-nulltype-allow   vos-null-type.json
vos_allow vos-invalid-allow    vos-invalid.json
# hook-log.txt gets one pipe-separated line per decision
newst
env AGENT_STATE_HOME="$st" TK_VERIFY_CMD="$STUB_FAIL" sh "$VOS" < "$FIX/vos-coder-fail.json" >/dev/null 2>&1
if [ -s "$st/team-kit/hook-log.txt" ] && grep -q 'block' "$st/team-kit/hook-log.txt"; then okc vos-hooklog-written; else badc vos-hooklog-written "no block line in hook-log.txt"; fi
# (2) status: BLOCKED escape hatch -> allow (exact and case-insensitive)
vos_allow vos-blocked-allow      vos-coder-blocked.json
vos_allow vos-blocked-ci-allow   vos-coder-blocked-ci.json
# coder-family suffix (coder-fast) is still gated -> block
vos_block vos-coder-suffix-block vos-coder-suffix.json "attempt 1" TK_VERIFY_CMD="$STUB_FAIL"
# (6)(8) verify fails -> block with reason (summary + tail + attempt no)
vos_block vos-fail-block         vos-coder-fail.json "E1234" TK_VERIFY_CMD="$STUB_FAIL"
vos_block vos-fail-silent-fallback vos-coder-fail.json "no diagnostic line" TK_VERIFY_CMD="$STUB_FAIL_SILENT"
vos_block vos-fail-escape-hint   vos-coder-fail.json "status: BLOCKED" TK_VERIFY_CMD="$STUB_FAIL"
# VERIFY FAILED summary branch (stub prints it; no "error" word on that line)
vfstub='echo step output; echo "VERIFY FAILED at '"'"'test'"'"' (exit 1)"; exit 1'
vos_block vos-fail-vfsummary     vos-coder-fail.json "VERIFY FAILED at 'test' (exit 1)" TK_VERIFY_CMD="$vfstub"

# (3) counter increments across stops; key sanitized for odd agent_ids
newst
env AGENT_STATE_HOME="$st" TK_VERIFY_CMD="$STUB_FAIL" sh "$VOS" < "$FIX/vos-coder-fail.json" >/dev/null 2>&1
env AGENT_STATE_HOME="$st" TK_VERIFY_CMD="$STUB_FAIL" sh "$VOS" < "$FIX/vos-coder-fail.json" >"$st/out2" 2>/dev/null
if grep -q 'attempt 2' "$st/out2" && [ "$(cat "$st/team-kit/verify-attempts-cod-2.txt" 2>/dev/null)" = "2" ]; then
  okc vos-counter-increments
else
  badc vos-counter-increments "expected attempt 2 + counter=2, counter=$(cat "$st/team-kit/verify-attempts-cod-2.txt" 2>/dev/null)"
fi
newst
env AGENT_STATE_HOME="$st" TK_VERIFY_CMD="$STUB_FAIL_SILENT" sh "$VOS" < "$FIX/vos-coder-weird-id.json" >/dev/null 2>&1
if [ "$(cat "$st/team-kit/verify-attempts-a_b_c___x.txt" 2>/dev/null)" = "1" ]; then okc vos-key-sanitized; else badc vos-key-sanitized "sanitized-key count file missing/wrong"; fi

# (5) verify passes -> allow {} and counter file removed
newst
mkdir -p "$st/team-kit"
echo 3 > "$st/team-kit/verify-attempts-cod-2.txt"
env AGENT_STATE_HOME="$st" TK_VERIFY_CMD='exit 0' sh "$VOS" < "$FIX/vos-coder-fail.json" >"$st/outp" 2>/dev/null
if [ "$(cat "$st/outp")" = "{}" ] && [ ! -f "$st/team-kit/verify-attempts-cod-2.txt" ]; then
  okc vos-pass-clears-counter
else
  badc vos-pass-clears-counter "out=[$(cat "$st/outp")] counter-still-there=$([ -f "$st/team-kit/verify-attempts-cod-2.txt" ] && echo yes || echo no)"
fi

# (7) MaxAttempts reached -> allow {} and counter removed
newst
env AGENT_STATE_HOME="$st" TK_MAX_ATTEMPTS=1 TK_VERIFY_CMD="$STUB_FAIL_SILENT" sh "$VOS" < "$FIX/vos-coder-fail.json" >/dev/null 2>&1
env AGENT_STATE_HOME="$st" TK_MAX_ATTEMPTS=1 TK_VERIFY_CMD="$STUB_FAIL_SILENT" sh "$VOS" < "$FIX/vos-coder-fail.json" >"$st/outm" 2>/dev/null
if [ "$(cat "$st/outm")" = "{}" ] && [ ! -f "$st/team-kit/verify-attempts-cod-2.txt" ]; then
  okc vos-maxattempts-allow
else
  badc vos-maxattempts-allow "second stop should allow, got [$(cat "$st/outm")]"
fi

# (4) default path: the real sibling verify.sh against real mini projects.
mini_ok=$(mktemp -d); tmpdirs="$tmpdirs
$mini_ok"
mini_bad=$(mktemp -d); tmpdirs="$tmpdirs
$mini_bad"
printf '%s' '{"steps":[{"name":"build","cmd":"true"},{"name":"test","cmd":"true"}]}' > "$mini_ok/team-kit.json"
printf '%s' '{"steps":[{"name":"build","cmd":"true"},{"name":"test","cmd":"false"}]}' > "$mini_bad/team-kit.json"
vos_allow vos-real-verify-green  vos-coder-fail.json TEAM_KIT_ROOT="$mini_ok" TK_VERIFY_CMD=
vos_block vos-real-verify-red    vos-coder-fail.json "VERIFY FAILED at 'test' (exit 1)" \
  TEAM_KIT_ROOT="$mini_bad" TK_VERIFY_CMD=

# (4b) root resolution via the hook payload's cwd (no TEAM_KIT_ROOT in env):
#      cwd present -> verify.sh runs against that project root (green + red);
#      cwd absent  -> verify.sh falls back to its own default root, which has
#      no team-kit.json -> block naming that root in the hook log.
mini_cwd_ok=$(mktemp -d); tmpdirs="$tmpdirs
$mini_cwd_ok"
mini_cwd_bad=$(mktemp -d); tmpdirs="$tmpdirs
$mini_cwd_bad"
printf '%s' '{"steps":[{"name":"test","cmd":"true"}]}' > "$mini_cwd_ok/team-kit.json"
printf '%s' '{"steps":[{"name":"test","cmd":"false"}]}' > "$mini_cwd_bad/team-kit.json"
newst
printf '{"agent_type":"coder","agent_id":"cod-9","cwd":"%s"}' "$mini_cwd_ok" > "$st/in-cwd.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in-cwd.json" 2>/dev/null); rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "{}" ] && grep -qF "root=$mini_cwd_ok" "$st/team-kit/hook-log.txt"; then
  okc vos-cwd-green
else
  badc vos-cwd-green "rc=$rc out=[$out] log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi
newst
printf '{"agent_type":"coder","agent_id":"cod-9","cwd":"%s"}' "$mini_cwd_bad" > "$st/in-cwd.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in-cwd.json" 2>/dev/null); rc=$?
dec=$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)
if [ "$rc" -eq 0 ] && [ "$dec" = block ] && grep -qF "root=$mini_cwd_bad" "$st/team-kit/hook-log.txt"; then
  okc vos-cwd-red
else
  badc vos-cwd-red "rc=$rc dec=$dec log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi
newst
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$FIX/vos-coder-fail.json" 2>/dev/null); rc=$?
dec=$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)
reason=$(printf '%s' "$out" | jq -r '.reason // empty' 2>/dev/null)
fallback_hit=ok
case "$reason" in *"no team-kit.json under project root"*) ;; *) fallback_hit="reason lacks fallback marker" ;; esac
if [ "$rc" -eq 0 ] && [ "$dec" = block ] && [ "$fallback_hit" = ok ] \
   && grep -qF "root=default" "$st/team-kit/hook-log.txt"; then
  okc vos-cwd-absent-fallback
else
  badc vos-cwd-absent-fallback "rc=$rc dec=$dec $fallback_hit log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# (4c-F1) root resolution priority: env TEAM_KIT_ROOT > cwd-with-config >
#         root-recent.txt hint > verify.sh fallback. Hint file: one line, one
#         path, overwrite semantics (coder skill writes it at task start).
mini_hint_ok=$(mktemp -d); tmpdirs="$tmpdirs
$mini_hint_ok"
mini_hint_red=$(mktemp -d); tmpdirs="$tmpdirs
$mini_hint_red"
mini_nocfg=$(mktemp -d); tmpdirs="$tmpdirs
$mini_nocfg"
mini_badcfg=$(mktemp -d); tmpdirs="$tmpdirs
$mini_badcfg"
printf '%s' '{"steps":[{"name":"test","cmd":"true"}]}'  > "$mini_hint_ok/team-kit.json"
printf '%s' '{"steps":[{"name":"test","cmd":"false"}]}' > "$mini_hint_red/team-kit.json"
printf '%s' 'not-json' > "$mini_badcfg/team-kit.json"

# env beats a cwd that itself carries a (red) config
newst
printf '{"agent_type":"coder","agent_id":"cod-10","cwd":"%s"}' "$mini_hint_red" > "$st/in.json"
out=$(env AGENT_STATE_HOME="$st" TEAM_KIT_ROOT="$mini_hint_ok" sh "$VOS" < "$st/in.json" 2>/dev/null); rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "{}" ] && grep -qF "root=$mini_hint_ok" "$st/team-kit/hook-log.txt"; then
  okc vos-env-beats-cwd
else
  badc vos-env-beats-cwd "rc=$rc out=[$out] log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# cwd with parseable config wins over a hint pointing at a green project
newst
mkdir -p "$st/team-kit"
printf '%s\n' "$mini_hint_ok" > "$st/team-kit/root-recent.txt"
printf '{"agent_type":"coder","agent_id":"cod-10","cwd":"%s"}' "$mini_hint_red" > "$st/in.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in.json" 2>/dev/null); rc=$?
dec=$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)
if [ "$rc" -eq 0 ] && [ "$dec" = block ] && grep -qF "root=$mini_hint_red" "$st/team-kit/hook-log.txt"; then
  okc vos-cwd-config-beats-hint
else
  badc vos-cwd-config-beats-hint "rc=$rc dec=$dec log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# cwd without config + hint -> hint is the root (green allow / red block)
newst
mkdir -p "$st/team-kit"
printf '%s\n' "$mini_hint_ok" > "$st/team-kit/root-recent.txt"
printf '{"agent_type":"coder","agent_id":"cod-11","cwd":"%s"}' "$mini_nocfg" > "$st/in.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in.json" 2>/dev/null); rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "{}" ] && grep -qF "root=$mini_hint_ok" "$st/team-kit/hook-log.txt"; then
  okc vos-hint-green
else
  badc vos-hint-green "rc=$rc out=[$out] log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi
newst
mkdir -p "$st/team-kit"
printf '%s\n' "$mini_hint_red" > "$st/team-kit/root-recent.txt"
printf '{"agent_type":"coder","agent_id":"cod-11","cwd":"%s"}' "$mini_nocfg" > "$st/in.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in.json" 2>/dev/null); rc=$?
dec=$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)
if [ "$rc" -eq 0 ] && [ "$dec" = block ] && grep -qF "root=$mini_hint_red" "$st/team-kit/hook-log.txt"; then
  okc vos-hint-red
else
  badc vos-hint-red "rc=$rc dec=$dec log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# cwd with UNPARSEABLE config does not count as a config -> hint still wins
newst
mkdir -p "$st/team-kit"
printf '%s\n' "$mini_hint_ok" > "$st/team-kit/root-recent.txt"
printf '{"agent_type":"coder","agent_id":"cod-11","cwd":"%s"}' "$mini_badcfg" > "$st/in.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in.json" 2>/dev/null); rc=$?
if [ "$rc" -eq 0 ] && [ "$out" = "{}" ] && grep -qF "root=$mini_hint_ok" "$st/team-kit/hook-log.txt"; then
  okc vos-cwd-badconfig-hint
else
  badc vos-cwd-badconfig-hint "rc=$rc out=[$out] log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# cwd without config + no hint -> fallback (block names root=default)
newst
printf '{"agent_type":"coder","agent_id":"cod-12","cwd":"%s"}' "$mini_nocfg" > "$st/in.json"
out=$(env AGENT_STATE_HOME="$st" sh "$VOS" < "$st/in.json" 2>/dev/null); rc=$?
dec=$(printf '%s' "$out" | jq -r '.decision // empty' 2>/dev/null)
reason=$(printf '%s' "$out" | jq -r '.reason // empty' 2>/dev/null)
fb=ok
case "$reason" in *"no team-kit.json under project root"*) ;; *) fb="reason lacks fallback marker" ;; esac
if [ "$rc" -eq 0 ] && [ "$dec" = block ] && [ "$fb" = ok ] \
   && grep -qF "root=default" "$st/team-kit/hook-log.txt"; then
  okc vos-cwd-noconfig-nohint-fallback
else
  badc vos-cwd-noconfig-nohint-fallback "rc=$rc dec=$dec $fb log=[$(cat "$st/team-kit/hook-log.txt" 2>/dev/null)]"
fi

# --- verify.sh (F4) -----------------------------------------------------------
# Empty name or empty cmd in steps[] is a config error: verify.sh must say
# which step is broken and exit 1 — never skip silently, never run nothing
# and print VERIFY PASSED.
# vs_err <name> <steps-json> <stderr-substring> — expect exit 1 + message
vs_err() {
  d=$(mktemp -d); tmpdirs="$tmpdirs
$d"
  printf '{"steps":[%s]}' "$2" > "$d/team-kit.json"
  out=$(env TEAM_KIT_ROOT="$d" sh "$ENG/verify.sh" 2>"$d/err"); rc=$?
  if [ "$rc" -ne 0 ] && grep -qF "$3" "$d/err"; then
    okc "$1"
  else
    badc "$1" "expected exit 1 with '$3', got rc=$rc err=[$(cat "$d/err" 2>/dev/null)] out=[$out]"
  fi
}
vs_err vs-empty-name-deny '{"name":"build","cmd":"true"},{"name":"","cmd":"true"}' 'step 2 has an empty name'
vs_err vs-empty-cmd-deny  '{"name":"build","cmd":""}'                             "step 1 ('build') has an empty cmd"
vs_err vs-empty-both-deny '{"name":"","cmd":""}'                                  'step 1 has an empty name'
# control: named, non-empty steps still pass end-to-end
d=$(mktemp -d); tmpdirs="$tmpdirs
$d"
printf '%s' '{"steps":[{"name":"build","cmd":"true"},{"name":"test","cmd":"true"}]}' > "$d/team-kit.json"
out=$(env TEAM_KIT_ROOT="$d" sh "$ENG/verify.sh" 2>&1); rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q '^VERIFY PASSED$'; then
  okc vs-valid-config-green
else
  badc vs-valid-config-green "rc=$rc out=[$out]"
fi

# --- STATE-CONTRACT anchors (issue #36) ----------------------------------------
# tests/anchors.list pins every file:line citation STATE-CONTRACT.md makes
# about the kit: one <relpath>:<lineno>:<keyword> triple per line, relpath
# relative to the kit root. Each triple is one case: the file must exist, the
# line number must be inside the file, and the keyword must sit on exactly
# that line — so any insertion that shifts a cited line (or edits away its
# anchor text) turns the suite red with the drifted line named.
# Silent-drop guards (review F1): a missing or unreadable list, a list whose
# triples were all lost, and a final line without a trailing newline must
# never collapse this section into a green suite — the first two are FAIL
# cases in their own right, the third keeps the last triple inside the loop.
KIT=$(CDPATH= cd -- "$ENG/.." && pwd)
a_list="$ENG/tests/anchors.list"
a_checked=0
if [ ! -f "$a_list" ] || [ ! -r "$a_list" ]; then
  badc "anchors.list" "list missing or unreadable ($a_list) — every anchor case dropped"
else
  while IFS= read -r triple || [ -n "$triple" ]; do
    case "$triple" in ''|'#'*) continue ;; esac
    a_checked=$((a_checked + 1))
    a_file=${triple%%:*}
    a_rest=${triple#*:}
    a_line=${a_rest%%:*}
    a_kw=${a_rest#*:}
    a_id="anchor $a_file:$a_line"
    if [ ! -f "$KIT/$a_file" ]; then
      badc "$a_id" "file missing (kit root=$KIT)"
      continue
    fi
    case "$a_line" in ''|*[!0-9]*) badc "$a_id" "malformed line number '$a_line'"; continue ;; esac
    if [ -z "$a_kw" ]; then badc "$a_id" "empty keyword"; continue; fi
    a_total=$(wc -l < "$KIT/$a_file" | tr -d ' ')
    if [ "$a_line" -gt "$a_total" ]; then
      badc "$a_id" "line $a_line beyond EOF ($a_file has $a_total lines)"
      continue
    fi
    a_content=$(sed -n "${a_line}p" "$KIT/$a_file")
    case "$a_content" in
      *"$a_kw"*) okc "$a_id" ;;
      *)
        a_hits=$(grep -nF -- "$a_kw" "$KIT/$a_file" | cut -d: -f1 | tr '\n' ' ')
        badc "$a_id" "keyword [$a_kw] not on line $a_line (line reads: [$a_content]) — actually at: ${a_hits:-nowhere}"
        ;;
    esac
  done < "$a_list"
  if [ "$a_checked" -lt 1 ]; then
    badc "anchors.list" "no parseable triples in $a_list — every anchor case dropped"
  fi
fi

# --- summary -----------------------------------------------------------------
total=$((pass + fail))
printf -- '----\ntests: %d passed, %d failed (total %d)\n' "$pass" "$fail" "$total"
[ "$fail" -ne 0 ] && exit 1
exit 0
