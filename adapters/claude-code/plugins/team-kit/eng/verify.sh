#!/bin/sh
# verify.sh — single verification entry point (human / hook / CI share this one).
#
# Steps are NOT hardcoded: they come from <root>/team-kit.json, e.g.
#   {"steps":[{"name":"build","cmd":"make build"},{"name":"test","cmd":"make test"}]}
# <root> = parent of this script's directory (eng/), overridable via TEAM_KIT_ROOT.
# Output contract:
#   per step:  "### <name>" then "> <full command>" (command self-documents)
#   first failing step: "VERIFY FAILED at '<name>' (exit <code>)" then exit 1 immediately
#   all green: "VERIFY PASSED" then exit 0
#   empty steps[].name or steps[].cmd anywhere: config error naming the step
#   number -> stderr + exit 1 (a typo must never pass as a silent skip)
set -u

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=${TEAM_KIT_ROOT:-$(CDPATH= cd -- "$script_dir/.." && pwd)}
config=$root/team-kit.json

if [ ! -f "$config" ]; then
  echo "verify.sh: no team-kit.json under project root: $root (set TEAM_KIT_ROOT)" >&2
  exit 1
fi

# jq -r '.steps[] | "<name><US><cmd>"'; unparseable config or missing steps -> error out.
# The field separator is the ASCII unit separator (US, \037), NOT tab: tab is
# IFS whitespace, so `read` would strip a leading tab and misread an empty
# name as an empty cmd; US is a plain delimiter and keeps empty fields intact.
sep=$(printf '\037')
steps=$(jq -r --arg sep "$sep" '.steps[]? | "\(.name)\($sep)\(.cmd)"' "$config" 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$steps" ]; then
  echo "verify.sh: no steps readable from $config (need steps[].name and steps[].cmd)" >&2
  exit 1
fi

# Clear last run's results dir so nothing can read stale results.
results_dir=${results_dir:-TestResults}
case $results_dir in
  ''|.|..|/*|./*|../*)
    echo "verify.sh: refusing unsafe results_dir '$results_dir'" >&2
    exit 1
    ;;
esac
rm -rf "$root/$results_dir"

step_no=0
while IFS="$sep" read -r name cmd; do
  step_no=$((step_no + 1))
  if [ -z "$name" ]; then
    printf "verify.sh: config error: step %d has an empty name (steps[].name) in %s\n" "$step_no" "$config" >&2
    exit 1
  fi
  if [ -z "$cmd" ]; then
    printf "verify.sh: config error: step %d ('%s') has an empty cmd (steps[].cmd) in %s\n" "$step_no" "$name" "$config" >&2
    exit 1
  fi
  printf '### %s\n' "$name"
  printf '> %s\n' "$cmd"
  (cd "$root" && sh -c "$cmd")
  rc=$?
  if [ "$rc" -ne 0 ]; then
    printf "VERIFY FAILED at '%s' (exit %d)\n" "$name" "$rc"
    exit 1
  fi
done <<EOF
$steps
EOF

printf 'VERIFY PASSED\n'
exit 0
