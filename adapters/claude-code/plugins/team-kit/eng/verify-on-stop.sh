#!/bin/sh
# verify-on-stop.sh — SubagentStop hook for coder agents.
#
# Claude Code hook contract implemented here:
#   - stdin:  hook JSON (agent_type / agent_id / session_id / cwd /
#     last_assistant_message). Parse failure is treated as null (never
#     crashes): a null agent_type is "not coder" -> allow.
#     Root resolution for the default verify path (priority, see step (4)):
#     explicit TEAM_KIT_ROOT env > payload cwd when <cwd>/team-kit.json exists
#     and parses > <state_dir>/root-recent.txt hint (coder writes it at task
#     start) > verify.sh's own default, the kit directory.
#   - stdout: ALWAYS exactly one line of JSON, exit code ALWAYS 0 — blocking is
#     expressed via JSON, not exit status:
#       allow -> {}                                    (SubagentStop allow = empty JSON object)
#       block -> {"decision":"block","reason":"..."}   (reason assembled with jq, never hand-concatenated)
#   - every decision appends one line to <state>/team-kit/hook-log.txt
#     (ISO-8601 UTC | decision | detail); logging failures are silent and NEVER reach stdout.
#   - jq is a hard prerequisite (payload parsing + block JSON assembly). When
#     jq is not on PATH the gate fails LOUD but stays open: one stderr warning
#     (SubagentStop shows stderr to the user), one hook-log line
#     "jq missing—gate inert", allow {} exit 0. Never block on missing jq —
#     the block JSON itself needs jq, and a blocked stop would deadlock the
#     status: BLOCKED escape hatch. See INSTALL.md (prerequisites).
#
# Env knobs: AGENT_STATE_HOME (default ~/.agent-state), TK_MAX_ATTEMPTS
# (default 0 = unlimited blocked stops), TK_TAIL_LINES (default 40),
# TK_VERIFY_CMD (override the verify command, used by tests to inject stubs).
set -u

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
state_base=${AGENT_STATE_HOME:-$HOME/.agent-state}
state_dir=$state_base/team-kit
max_attempts=${TK_MAX_ATTEMPTS:-0}
tail_lines=${TK_TAIL_LINES:-40}

input=$(cat)

# jq helpers on the raw payload; any parse failure collapses to empty output.
jstr() { printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null; }
jtest() { # <jq-path> <regex>
  printf '%s' "$input" | jq -r --arg re "$2" "($1 // \"\") | test(\$re)" 2>/dev/null
}

log_line() { # <decision> <detail>
  mkdir -p "$state_dir" 2>/dev/null
  printf '%s|%s|%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" \
    >> "$state_dir/hook-log.txt" 2>/dev/null
}

allow() { log_line allow "$1"; printf '{}\n'; exit 0; }
block() { log_line block "$1"; printf '%s\n' "$2"; exit 0; }

# (0) jq is a hard prerequisite of this gate (payload parsing, block JSON
#     assembly). Missing jq must never degrade into a SILENT fail-open: warn
#     on stderr (shown to the user on SubagentStop), log the inert state,
#     allow the stop. Blocking is not an option — the block JSON itself
#     needs jq, and a blocked stop would deadlock the status: BLOCKED
#     escape hatch.
if ! command -v jq >/dev/null 2>&1; then
  printf 'verify-on-stop.sh: jq missing—gate inert: cannot parse the hook payload or assemble a block decision; allowing this stop. Install jq (see team-kit INSTALL.md) to arm the gate.\n' >&2
  allow "jq missing—gate inert"
fi

# (1) agent_type not in the coder family -> allow, hook is a no-op for others.
agent_type=$(jstr '.agent_type')
case $(jtest '.agent_type' '^coder(-[a-z0-9_-]+)?$') in
  true) ;;
  *) allow "agent_type=${agent_type:-<null>} is not coder" ;;
esac

# (2) escape hatch: the agent declares itself blocked -> allow, upper layer decides.
case $(jtest '.last_assistant_message' '(?im)^\s*status:\s*BLOCKED') in
  true) allow "last_assistant_message declares status: BLOCKED" ;;
esac

# (3) attempt counter: key = agent_id, else session_id, else "default";
#     sanitized to [A-Za-z0-9_-] (foreign chars mapped to '_').
raw_key=$(jstr '.agent_id')
[ -n "$raw_key" ] || raw_key=$(jstr '.session_id')
[ -n "$raw_key" ] || raw_key=default
key=$(printf '%s' "$raw_key" | tr -c 'A-Za-z0-9_-' '_')
[ -n "$key" ] || key=default
count_file=$state_dir/verify-attempts-$key.txt

mkdir -p "$state_dir" 2>/dev/null
attempts=0
if [ -f "$count_file" ]; then
  attempts=$(cat "$count_file" 2>/dev/null)
  case $attempts in ''|*[!0-9]*) attempts=0 ;; esac
fi

# (4) run verify in a subprocess; merge stdout+stderr; take its exit code.
#     Root resolution priority (F1):
#       1. explicit TEAM_KIT_ROOT env (tests / CI inject it) — wins outright;
#       2. hook payload cwd, but only when <cwd>/team-kit.json exists AND
#          parses (jq -e): nested dispatch (subagent-of-subagent) reports the
#          parent session's cwd, which usually has no config — such a cwd must
#          NOT shadow the hint below;
#       3. <state_dir>/root-recent.txt — one line, one absolute path, written
#          (overwrite mode) by the coder skill at task start from the
#          TEAM_KIT_ROOT the dispatcher handed it.
#          Concurrency caveat: last-writer wins — two coders on different
#          roots running interleaved stops can pick up each other's root.
#          Accepted for a personal (single-user) kit; revisit before any
#          multi-user / multi-root adoption.
#       4. fallback: verify.sh's own default (the kit directory).
if [ -n "${TK_VERIFY_CMD:-}" ]; then
  verify_root=stub
  out=$(sh -c "$TK_VERIFY_CMD" 2>&1); rc=$?
else
  verify_root=''
  if [ -n "${TEAM_KIT_ROOT:-}" ]; then
    verify_root=$TEAM_KIT_ROOT
  else
    cwd=$(jstr '.cwd')
    if [ -n "$cwd" ] && [ -f "$cwd/team-kit.json" ] \
       && jq -e . "$cwd/team-kit.json" >/dev/null 2>&1; then
      verify_root=$cwd
    elif [ -s "$state_dir/root-recent.txt" ]; then
      verify_root=$(sed -n '1p' "$state_dir/root-recent.txt" 2>/dev/null)
      [ -n "$verify_root" ] || verify_root=''
    fi
  fi
  if [ -n "$verify_root" ]; then
    out=$(TEAM_KIT_ROOT="$verify_root" "$script_dir/verify.sh" 2>&1); rc=$?
  else
    verify_root=default
    out=$("$script_dir/verify.sh" 2>&1); rc=$?
  fi
fi

# (5) verify passed -> drop the counter, allow the stop.
if [ "$rc" -eq 0 ]; then
  rm -f "$count_file" 2>/dev/null
  allow "verify passed (root=$verify_root) after $attempts prior blocked stop(s); counter cleared"
fi

# (6) failure summary: first line containing "error" -> "VERIFY FAILED" line -> fallback.
summary=$(printf '%s' "$out" | awk 'tolower($0) ~ /error/ {print; exit}')
[ -n "$summary" ] || summary=$(printf '%s' "$out" | awk '$0 ~ /^VERIFY FAILED/ {print; exit}')
[ -n "$summary" ] || summary="verify exited $rc with no diagnostic line"

# (7) MaxAttempts reached -> drop the counter and allow; upper layer judges.
new=$((attempts + 1))
if [ "$max_attempts" -gt 0 ] && [ "$new" -gt "$max_attempts" ]; then
  rm -f "$count_file" 2>/dev/null
  allow "max attempts ($max_attempts) reached after $attempts blocked stop(s); escalating"
fi

# (8) otherwise block; reason carries attempt no (with cap when set), exit code,
#     remediation guidance incl. the status: BLOCKED escape, and the output tail.
printf '%s\n' "$new" > "$count_file" 2>/dev/null
attempt_desc="attempt $new"
[ "$max_attempts" -gt 0 ] && attempt_desc="attempt $new/$max_attempts"
tail_part=$(printf '%s' "$out" | tail -n "$tail_lines")
reason_text=$(printf 'coder stop rejected: verify failed (exit %s), %s. First hint: %s\nFix per the output below and stop again; if the spec or the environment is the problem, end with "status: BLOCKED".\n--- verify output (last %s lines) ---\n%s' \
  "$rc" "$attempt_desc" "$summary" "$tail_lines" "$tail_part")
block_json=$(jq -c -n --arg reason "$reason_text" '{decision:"block", reason:$reason}')
block "attempt $new, exit $rc, key=$key, root=$verify_root, summary=$summary" "$block_json"
