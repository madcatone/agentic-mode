#!/bin/sh
# oc-dispatch.sh — dispatch a task file to a headless subagent CLI.
# usage: scripts/oc-dispatch.sh <task-file> <slug>
# env:   OC_BIN      subagent CLI (default: opencode) — set to a stub for smoke tests
#        OC_MODEL    (default zai-coding-plan/glm-5.2)
#        OC_TIMEOUT  seconds (default 1800)
#        OC_STALL    seconds of no-event silence before kill (default 300)
#        OC_REPO     (default: git root of cwd) — the repo the agent works in
#        OC_RUN_ROOT (default: OC_REPO) — where the run dir is created; set this
#                    to a surviving repo when OC_REPO is a throwaway worktree
#                    (sandbox) so run artifacts outlive the sandbox.
#        OC_GATE_CMD the repo's mechanical gate command (e.g. "python3 scripts/check.py").
#                    Run in OC_REPO for pre/post snapshots. Unset => gate snapshots
#                    are skipped (a skip marker is written, scoring SKIPs the gate
#                    check and rules the whole run INCONCLUSIVE — never PASS).
# Produces <OC_RUN_ROOT>/Benchmarks/runs/<date>-<slug>-<NN>/ with task/events/
# report plus pre/post snapshots of git status and the gate (both taken in
# OC_REPO) for L1 scoring. The run dir is printed as RUN_DIR= on the last line.
set -eu
TASK="$1"; SLUG="$2"
REPO="${OC_REPO:-$(git rev-parse --show-toplevel)}"
RUN_ROOT="${OC_RUN_ROOT:-$REPO}"
BIN="${OC_BIN:-opencode}"
MODEL="${OC_MODEL:-zai-coding-plan/glm-5.2}"
TO="${OC_TIMEOUT:-1800}"

# Claim a run dir. The idempotency key is (date, slug, sequence) — a same-day
# re-run of the same slug is the *expected* case (patch → A/B verify), so it
# must never land on run A's directory and overwrite its evidence. mkdir is the
# atomic claim, so parallel dispatches cannot pick the same sequence either.
# Sequence is zero-padded, so `ls` orders runs the way they happened: the lowest
# NN of a given <date>-<slug> is run A, the next one up is run B.
RUNS_DIR="$RUN_ROOT/Benchmarks/runs"
DAY=$(date +%F)
mkdir -p "$RUNS_DIR"
seq_n=1
while :; do
  RUN=$(printf '%s/%s-%s-%02d' "$RUNS_DIR" "$DAY" "$SLUG" "$seq_n")
  mkdir "$RUN" 2>/dev/null && break
  seq_n=$((seq_n + 1))
  if [ "$seq_n" -gt 99 ]; then
    echo "error: 99 runs of ${DAY}-${SLUG} already exist; archive them first" >&2
    exit 1
  fi
done
cp "$TASK" "$RUN/task.md"
# meta.txt is the only append-only file here; start it empty so a STALL_KILL /
# DISPATCH_RC marker can only ever describe *this* run.
: > "$RUN/meta.txt"

# gate_snapshot <output-file> — run OC_GATE_CMD once in OC_REPO, capture its
# output and record its exit code as a trailing GATE_EXIT= line; skip cleanly
# when OC_GATE_CMD is unset. A non-zero gate (red) is an expected signal, so
# capture the code set-e-safely instead of letting it abort the script.
gate_snapshot() {
  out="$1"
  if [ -z "${OC_GATE_CMD:-}" ]; then
    echo "gate snapshot skipped (OC_GATE_CMD unset)" > "$out"
    return 0
  fi
  ( cd "$REPO" && sh -c "$OC_GATE_CMD" ) > "$out" 2>&1 && rc=0 || rc=$?
  echo "GATE_EXIT=$rc" >> "$out"
  return 0
}

( cd "$REPO" && git status --porcelain ) > "$RUN/git-pre.txt"
( cd "$REPO" && git rev-parse HEAD ) > "$RUN/head-pre.txt"
gate_snapshot "$RUN/gate-pre.txt"

# GNU timeout is absent on stock macOS; perl alarm is the portable guard.
perl -e 'alarm shift; exec @ARGV' "$TO" \
  "$BIN" run -m "$MODEL" --auto --format json --dir "$REPO" \
  "Read the file $RUN/task.md and execute it fully. Work only within the scope it declares. Your final message is the entire report." \
  > "$RUN/events.json" 2> "$RUN/stderr.txt" &
OC_PID=$!

# Stall watchdog: a hung provider call emits no events but never exits. Kill
# after OC_STALL seconds without events.json growth; the total alarm still
# caps runtime.
STALL="${OC_STALL:-300}"
last=0; still=0
while kill -0 "$OC_PID" 2>/dev/null; do
  sleep 30
  size=$(wc -c < "$RUN/events.json" 2>/dev/null || echo 0)
  if [ "$size" -gt "$last" ]; then
    last=$size; still=0
  else
    still=$((still+30))
    if [ "$still" -ge "$STALL" ]; then
      echo "STALL_KILL=${still}s_no_events" >> "$RUN/meta.txt"
      kill "$OC_PID" 2>/dev/null
      break
    fi
  fi
done
wait "$OC_PID" || echo "DISPATCH_RC=$?" >> "$RUN/meta.txt"

( cd "$REPO" && git status --porcelain ) > "$RUN/git-post.txt"
( cd "$REPO" && git rev-parse HEAD ) > "$RUN/head-post.txt"
gate_snapshot "$RUN/gate-post.txt"

# Extract the report: text parts of the last message; keep the longest text
# seen per part id (tolerates cumulative streaming).
python3 - "$RUN" <<'EOF'
import json, os, sys
run = sys.argv[1]
parts, order, msg_of = {}, [], {}
for line in open(os.path.join(run, 'events.json')):
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except ValueError:
        continue
    if ev.get('type') != 'text':
        continue
    p = ev.get('part', {})
    pid, mid, txt = p.get('id'), p.get('messageID'), p.get('text', '')
    if pid not in parts:
        order.append(pid)
        msg_of[pid] = mid
    if len(txt) >= len(parts.get(pid, '')):
        parts[pid] = txt
last_msg = msg_of.get(order[-1]) if order else None
body = '\n'.join(parts[pid] for pid in order if msg_of.get(pid) == last_msg)
open(os.path.join(run, 'report.md'), 'w').write(body or '(no text events)')
print('report bytes:', os.path.getsize(os.path.join(run, 'report.md')))
EOF
echo "RUN_DIR=$RUN"
