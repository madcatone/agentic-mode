# Commander Runbook — for any agent, any tool

<!-- Entry point for agents that do not support the packaged skill format.
     Point your agent at this file ("read this file and run it") and it can
     adopt the commander dispatch loop into a repo with nothing but file
     reads, shell commands, and questions to its user. -->

You are an agent (or a human operator). This runbook lets you adopt the
**commander** dispatch-and-score loop into a repo without any plugin or skill
system.

## Definitions

- **TOOLKIT** — the directory containing this file. Everything you need is
  inside it: `SKILL.md` (the full adopt flow), `reference/COMMANDER.md` (the
  constitution), `reference/REPORT-PROTOCOL.md` and `reference/TASK-TEMPLATE.md`
  (the two contracts subagents follow), and `scripts/oc-dispatch.sh` +
  `scripts/oc-score.sh` (the dispatch and L1 scoring tools).
- **TARGET** — the repository you have been asked to set the loop up in: the
  repo your session is working in (ask your user if ambiguous). All generated
  files are written into TARGET; nothing is ever written into TOOLKIT.

## Procedure

1. Read `SKILL.md` in TOOLKIT. Ignore its YAML frontmatter (packaging metadata
   for one particular tool); everything below it is the protocol, written for
   any executor. Where it references paths like `reference/…` or `scripts/…`,
   resolve them against TOOLKIT; where it references generated files
   (`docs/COMMANDER.md`, `Benchmarks/…`, `scripts/oc-*.sh`), resolve them
   against TARGET.
2. Follow the **Adopt flow** exactly, in order, gate by gate:
   1. **Confirm the mechanical gate** — find TARGET's one `exit 0`-when-green
      command (build / test / lint / custom checker). No gate ⇒ **stop** and
      tell your user to stand one up first; the loop's quality floor depends on
      it. Never invent an always-green gate.
   2. **Copy the constitution** `reference/COMMANDER.md` → `TARGET/docs/COMMANDER.md`
      (or the repo's preferred docs path). Leave §0–§6 verbatim; fill only §7's
      binding table with TARGET's real gate command and paths, then delete the
      commented `例：…` example block.
   3. **Scaffold** `TARGET/Benchmarks/`: `LEDGER.md` (title + table header only,
      no run rows), `TASK-TEMPLATE.md` and `REPORT-PROTOCOL.md` copied from
      `reference/` (resolve `<gate 指令>` in the template), and empty `tasks/`
      + `runs/` directories.
   4. **Copy both scripts** verbatim into `TARGET/scripts/`. Drive them with env
      only: `OC_GATE_CMD` (the gate — **required**; export it, since without it
      the gate never runs and L1 scores `INCONCLUSIVE`, not PASS), `OC_BIN`
      (your subagent CLI, default `opencode`), `OC_MODEL`, `OC_TIMEOUT`,
      `OC_STALL`, `OC_RUN_ROOT`.
   5. **Prove the pipeline** with one small task: `oc-dispatch.sh` (it prints
      `RUN_DIR=…` naming the run dir it just claimed, `<date>-<slug>-<NN>`),
      then `oc-score.sh <that dir>` — expect a real PASS or FAIL. An
      `INCONCLUSIVE` means one of the three **required** checks could not run:
      the *gate* (export `OC_GATE_CMD`), the *scope* check (the task file needs
      a `<!-- oc-scope: … -->` line), or the *commit* check (missing HEAD
      snapshots). The scorecard names the check and the fix; fix it and
      re-dispatch. Then append the first row to `LEDGER.md`.
3. Runtime requirements: POSIX `sh`, `git`, `perl` (the portable timeout guard),
   Python 3 (standard library only — the dispatch script uses it to extract the
   report), and a headless subagent CLI on `OC_BIN`. Nothing else.

## Ground rules (same as the skill's hard rules)

- **The gate is a prerequisite, not an output.** Do not adopt the loop into a
  repo with no red-capable gate, and never stand in a fake always-green one. A
  required check that did not run is a fake green too — that is what
  `INCONCLUSIVE` means, and it is never an accepted run in the ledger.
- **One dispatch, one run directory.** A same-day re-run of the same slug (the
  A/B verification after a patch) claims the next `-NN`; run A's artifacts are
  never overwritten. Run A is the lower `NN`. Do not delete or hand-edit run
  dirs to tidy up — the ledger's attribution points at them.
- **§0–§6 of the constitution are verbatim; only §7 is per-repo.** Do not
  re-author the harness-neutral core.
- Never advance past a failed step gate. If the same step fails after two fix
  attempts, stop and escalate to your user with the failure trail.
- **The author never signs off its own work**: L3 acceptance is always a
  fresh-context judge.
- **Scaffold, do not clobber**: merge into any existing ledger / template /
  protocol; never overwrite hand-written content.

## Done means

`TARGET/docs/COMMANDER.md` exists with §7 filled in (no `<填入…>` placeholder
left), the `Benchmarks/` tree is scaffolded, both `scripts/oc-*.sh` are in
place, one small task has run end to end through `dispatch → score`, and
`LEDGER.md` carries its first real run row. Then hand your user the daily loop
**exactly as SKILL.md "The loop, once adopted" states it** (dispatch → score →
attribute → ledger → reflect). Do not restate a shortened version; SKILL.md is
the single source.
