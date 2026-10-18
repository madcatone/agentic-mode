#!/bin/sh
# reviewer-git-only.sh — PreToolUse hook (matcher: Bash) for the read-only roles
# (reviewer / fortify).
#
# Claude Code hook contract implemented here:
#   - stdin:  hook JSON (tool_name / tool_input.command). Parse failure -> deny.
#   - allow = print NOTHING and exit 0 (PreToolUse allow is no output).
#   - deny  = exactly one line:
#       {"hookSpecificOutput":{"hookEventName":"PreToolUse",
#        "permissionDecision":"deny","permissionDecisionReason":"..."}}
#     assembled with jq (jq -c -n --arg), never hand-concatenated.
#
# Decision order:
#   (1) tool_name matching a write/execute class
#       (edit|write|create|delete|rename|patch|task|notebook|terminal|execute|run)
#       -> deny "read-only".
#   (1b) no tool_input.command and not caught at (1): read/search tools
#       (Read, Grep, Glob, ...) -> silent allow (VS Code Local mounting feeds
#       every tool call into this hook; denying reads would blind the reviewer).
#   (2) command must pass three gates:
#       a. metachar blacklist: ` $( ; & | < > ( CR LF   (<< is covered by <)
#       b. whitelist, walked token by token: `git`, then any number of safe
#          global prefixes — `--no-pager` and `-C <dir>` (separate or attached
#          `-C<dir>`), each <dir> restricted to a conservative path charset —
#          then exactly one read-only subcommand
#          (status|diff|log|show|ls-files|blame|rev-parse) as the first
#          remaining token, then arbitrary arguments.
#          Security note (why -C does not break the read-only guarantee):
#          -C only changes git's working directory before running the SAME
#          whitelisted read-only subcommand; the metachar blacklist (gate a)
#          and the --output/--ext-diff/--textconv deny (gate c) both match the
#          WHOLE command string, so they apply to the -C value too, and the
#          -C value charset gate (2b) additionally rejects quotes, $, globs
#          and anything else outside [A-Za-z0-9_./~+:@=-]. --no-pager only
#          disables the pager subprocess — no file writes, no external
#          helpers, no config injection (that is why -c/--git-dir/--work-tree
#          and friends stay OUT: -c injects arbitrary config, e.g. pager or
#          diff helper commands, and the long path flags widen the parser
#          surface for no read-only gain).
#       c. --output / --ext-diff / --textconv anywhere -> deny
#   (3) all gates passed -> silent allow.
set -u

input=$(cat)

deny() { # <reason>
  printf '%s\n' "$(jq -c -n --arg r "$1" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}')"
  exit 0
}

# Parse failure -> deny outright (never let an unreadable payload through).
printf '%s' "$input" | jq -e . >/dev/null 2>&1 || deny "read-only gate: cannot parse hook input"

tool=$(printf '%s' "$input" | jq -r '.tool_name // ""')
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

# (1) write/execute-class tool names -> deny.
case $(printf '%s' "$tool" | tr '[:upper:]' '[:lower:]') in
  *edit*|*write*|*create*|*delete*|*rename*|*patch*|*task*|*notebook*|*terminal*|*execute*|*run*)
    deny "read-only role: tool '$tool' writes or executes; only whitelisted read-only git commands are allowed"
    ;;
esac

# (1b) non-command tools (no tool_input.command): read/search tools such as
# Read / Grep / Glob pass silently. VS Code Local mounting ignores the hook
# matcher and feeds EVERY tool call into this hook — denying reads would blind
# the reviewer under that mounting. Write/exec-class names were already caught
# at (1); command gates below never apply to a tool without a command.
[ -n "$cmd" ] || exit 0

# (2a) sh metachar blacklist (backtick, $(), ;, &, |, <, >, (, CR, LF).
# NB: command substitution strips trailing newlines, so guard with a marker char.
cr=$(printf '\rX'); cr=${cr%X}
lf=$(printf '\nX'); lf=${lf%X}
case "$cmd" in
  *'`'*|*'$('*|*';'*|*'&'*|*'|'*|*'<'*|*'>'*|*'('*|*"$cr"*|*"$lf"*)
    deny "read-only role: shell metacharacter in command (backtick, \$(), ;, &, |, <, >, (, newline) is not allowed"
    ;;
esac

# (2b) whitelist: `git`, then safe global prefixes (`-C <dir>`, `--no-pager`),
# then exactly one read-only subcommand as the first remaining token.
# Tokens are pulled one at a time through awk (no unquoted expansion / word
# splitting — zsh does not word-split unquoted parameters, this stays portable).
ntok=$(printf '%s' "$cmd" | awk '{print NF}')
tok() { printf '%s' "$cmd" | awk -v i="$1" '{print $i}'; }

if [ "$(tok 1)" != "git" ]; then
  deny "read-only role: only read-only git subcommands are allowed ([-C <dir>] [--no-pager] status diff log show ls-files blame rev-parse)"
fi

i=2
subcmd=''
while :; do
  [ "$i" -le "$ntok" ] || break
  t=$(tok "$i")
  case $t in
    --no-pager)
      i=$((i + 1))
      ;;
    -C)
      dirarg=$(tok $((i + 1)))
      case $dirarg in
        '') deny "read-only role: git -C requires a directory argument" ;;
      esac
      case $dirarg in
        *[!A-Za-z0-9_./~+:@=-]*)
          deny "read-only role: git -C directory '$dirarg' has characters outside the allowed path set (no quotes, \$, globs or metacharacters)"
          ;;
      esac
      i=$((i + 2))
      ;;
    -C?*)
      dirarg=${t#-C}
      case $dirarg in
        *[!A-Za-z0-9_./~+:@=-]*)
          deny "read-only role: git -C directory '$dirarg' has characters outside the allowed path set (no quotes, \$, globs or metacharacters)"
          ;;
      esac
      i=$((i + 1))
      ;;
    *)
      subcmd=$t
      break
      ;;
  esac
done

case $subcmd in
  status|diff|log|show|ls-files|blame|rev-parse) ;;
  '')
    deny "read-only role: no whitelisted git subcommand found (expected one of: status diff log show ls-files blame rev-parse)"
    ;;
  *)
    deny "read-only role: git subcommand '$subcmd' is not whitelisted"
    ;;
esac

# (2c) flags that can write files or execute external helpers -> deny.
case "$cmd" in
  *--output*|*--ext-diff*|*--textconv*)
    deny "read-only role: --output / --ext-diff / --textconv can write files or execute helpers"
    ;;
esac

# (3) all gates passed -> silent allow: no output, exit 0.
exit 0
