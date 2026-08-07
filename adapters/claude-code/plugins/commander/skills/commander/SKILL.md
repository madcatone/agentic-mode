---
name: commander
description: >
  Use when one model should dispatch work to subagents and grade it inside a repo — standing up
  a runnable dispatch-and-score loop. A single-file constitution scores subagent output on a
  three-layer pyramid (mechanical gate → contract → fresh-context judge), attributes every
  failure, and patches the harness so quality compounds. If the user says "commander mode" and
  wants something that actually runs, it is this skill. Do NOT use for the machine-wide advisor
  model and its founding prompt (→ fable5), nor for a repo's documentation contract and CI gate
  (→ agentic-bootstrap). Triggers on: "set up a dispatch loop", "commander mode", "dispatch and
  grade", "派工閉環", "建立派工評分迴圈", "讓弱模型做事再打分".
---

# Commander

Stand up in a repo the **commander dispatch loop**: a single-file constitution (`COMMANDER.md`) that turns any model into a commander who **dispatches** tasks to subagents, **scores** their output on a three-layer pyramid, **attributes** each failure to the right layer, and **patches** the harness so the next run is easier — quality floor held by a machine gate, ceiling lifted by a coaching loop. It is harness-neutral: the commander needs only three primitives — *read a file, run a command, ask the user*.

This skill **adopts the loop into a target repo**. It does not run the loop for you; it installs the constitution, the report protocol, the task template, the two dispatch/score scripts, and the ledger scaffold, wires them to the repo's own mechanical gate, and proves the pipeline with one small run.

**To start, jump to _Adopt flow_ below.** The layout and relationship sections above it are orientation, not prerequisites.

## Relationship to sibling skills

- **`agentic-bootstrap`** gives a repo its **document contract and a mechanical gate** (`What`/`Done`). The commander loop **requires** such a gate — it is the quality floor the whole pyramid rests on. If the target repo has no runnable gate, bootstrap one first (or build a config-driven checker in that spirit), *then* adopt commander.
- **`fable5`** is the same commander/advisor *doctrine* as a machine-wide reference and founding prompt — read-only, no repo writes. `commander` is the **runnable, per-repo** instance: it ships scripts and scaffolds a scoring ledger so a cheaper model can actually do subagent work under scoring in *this* repo.
- Together: **bootstrap** makes a repo legible and gated; **commander** makes any model able to dispatch work into it and grade the result. The two combined = any repo where any model can take on work at high, verified quality.

## Layout this skill produces in the target repo

```
docs/COMMANDER.md            # the constitution (copied from reference/, §7 filled in)
Benchmarks/
  LEDGER.md                  # append-only run ledger (empty header seeded)
  TASK-TEMPLATE.md           # task-file template (gate placeholder resolved)
  REPORT-PROTOCOL.md         # the ①–⑥ report contract subagents must follow
  tasks/                     # one task file per dispatch (you author these)
  runs/                      # per-run artifacts, one dir per dispatch:
                             #   <date>-<slug>-<NN>, NN counting up from 01
                             #   meta.txt is truncated at dispatch start, so
                             #   STALL_KILL=/DISPATCH_RC= describe this run only
scripts/
  oc-dispatch.sh             # dispatch a task file to a headless subagent CLI
  oc-score.sh                # L1 mechanical scorer over a run dir
```

Paths are defaults — put `COMMANDER.md`, `Benchmarks/`, and the scripts wherever the repo's conventions prefer, then record the real locations in `COMMANDER.md` §7 and in the scripts' env.

---

## Adopt flow

Do these five steps in order. Each has a gate; do not advance on a failed gate.

### 1. Confirm the repo has a mechanical gate (hard prerequisite)

The loop's entire quality floor is **one command that exits 0 when the repo is green** (build / test / lint / a custom checker). Find it: read the repo's `AGENTS.md`, `README`, CI config, `Makefile`/`package.json`/`pyproject`. Ask the user if it is not obvious.

- **Gate found** → record the exact command; it becomes `OC_GATE_CMD` and `COMMANDER.md` §7's gate row.
- **No gate** → stop and tell the user: the commander loop needs one first. Recommend standing up a config-driven checker in the spirit of the `agentic-bootstrap` skill (a stdlib checker + a single `exit 0` invocation), then returning here. Do **not** fabricate a gate that always passes — a gate that never goes red defeats the whole floor.

### 2. Copy the constitution and fill §7

Copy `reference/COMMANDER.md` into the target repo (default `docs/COMMANDER.md`). Leave §0–§6 **verbatim** — they are the harness-neutral core. Fill only **§7's binding table**, replacing every `<填入：…>` placeholder with this repo's real values:

- **機械 gate** — the exit-0 command from step 1.
- **派工 / L1 評分** — the two script invocations, with paths matching where you place the scripts (step 4).
- **任務書模板 / 回報協議 / 台帳** — the paths you scaffold in step 3.

Delete the commented `例：…` binding example block once §7 is filled (it is illustration, not config).

### 3. Scaffold the Benchmarks tree

Create the ledger, template, protocol, and two working directories:

- `Benchmarks/LEDGER.md` — seed with the title + the append-only table **header only** (columns: `run | 日期 | 任務 | 模型 | 裁決 | 失敗分類 | 時長 | 備註`) and a `累計：dispatched 0 · accepted 0 · accept rate —` line. No run rows yet.
- `Benchmarks/TASK-TEMPLATE.md` — copy from `reference/TASK-TEMPLATE.md`; resolve the `<gate 指令>` placeholder to this repo's gate command.
- `Benchmarks/REPORT-PROTOCOL.md` — copy from `reference/REPORT-PROTOCOL.md` as-is (it is already generic).
- `Benchmarks/tasks/` and `Benchmarks/runs/` — create both (a `.gitkeep` in each is fine).

### 4. Copy the two scripts and set env for this repo

Copy `scripts/oc-dispatch.sh` and `scripts/oc-score.sh` verbatim into the target repo's `scripts/`. They are repo-agnostic; you drive them entirely with env:

- `OC_GATE_CMD` — the step-1 gate command. **Required on every dispatch**: unset ⇒ the gate snapshot is skipped, L1 SKIPs the gate check, and the run is scored `INCONCLUSIVE` (exit 3) — never PASS, never eligible for L3. Export it once per shell so a later dispatch cannot silently lose it.
- `OC_BIN` — your subagent CLI (default `opencode`); `OC_MODEL` — the model id it dispatches to.
- `OC_TIMEOUT` / `OC_STALL` — runtime cap and stall-watchdog seconds; enlarge `OC_STALL` when a task itself spawns long-running child processes.
- `OC_RUN_ROOT` — where `Benchmarks/runs/<date>-<slug>-<NN>/` is created (default: the repo root).

**Three required checks, three ways to score `INCONCLUSIVE`.** `oc-score.sh` treats the gate, the scope declaration and the zero-commit check as the L1 floor. Each can only be *checked* when its evidence exists, and evidence that is absent is not evidence of green — so a missing one SKIPs the check *and* rules the run `INCONCLUSIVE` (exit 3), never PASS:

| required check | what makes it unverifiable | fix |
|---|---|---|
| gate | `OC_GATE_CMD` unset at dispatch time (or `gate-post.txt` missing / carrying no `GATE_EXIT=`) | export `OC_GATE_CMD` and re-dispatch |
| scope | the task file has no `<!-- oc-scope: … -->` line, the line is empty, or `git-pre/git-post.txt` is missing | add the oc-scope line to the task file (see `TASK-TEMPLATE.md` 範圍宣告) and re-dispatch |
| commit | `head-pre/head-post.txt` missing | re-dispatch through `oc-dispatch.sh`, which writes both |

The scorecard names the unverified check(s) and the fix. **If you are adopting into a repo that already has task files, add the `<!-- oc-scope: … -->` line to each of them before the next dispatch** — a task file without it used to score PASS on 4 of 5 checks and now scores `INCONCLUSIVE`. That is the intended reading: a run whose boundary was never declared was never boundary-checked.

### 5. Prove the pipeline with one small run

Dispatch one deliberately small, low-risk task end to end so the whole `dispatch → score → ledger` path is exercised before you trust it with real work:

```
export OC_GATE_CMD='<gate cmd>'   # required — without it the gate never runs and L1 cannot clear
scripts/oc-dispatch.sh Benchmarks/tasks/<slug>.md <slug>   # prints RUN_DIR=… on its last line
scripts/oc-score.sh Benchmarks/runs/<date>-<slug>-01       # expect verdict PASS/FAIL, not INCONCLUSIVE
```

Score the directory `oc-dispatch.sh` printed as `RUN_DIR=`; the `-NN` suffix makes each dispatch its own directory, so never assume the bare `<date>-<slug>`.

Then append the first row to `LEDGER.md` (run id, verdict, failure class if any, duration). **Done when**: §7 is filled with no `<填入…>` left, the Benchmarks tree exists, both scripts are in place, `oc-score.sh` returned a real PASS or FAIL (an `INCONCLUSIVE` means a required check never ran — read which one off the scorecard, fix it, and re-dispatch), and `LEDGER.md` carries its first real run row.

---

## The loop, once adopted (hand this to the user)

- **Dispatch**: author a task file from `TASK-TEMPLATE.md` (four parts — 目標與動機 / 驗收條件 / 範圍宣告 / 回報格式 — none omittable), run `oc-dispatch.sh`.
- **Score**: run `oc-score.sh` (L1 mechanical). L1 clear → optionally an L2 contract check and an L3 **fresh-context** judge (a subagent given only the task file + the output, never the work history — the author never signs off its own work).
- **Attribute**: every non-ACCEPT run gets classed `harness-fixable` / `infra-flaky` / `model-ceiling` (COMMANDER §3). Patch the offending **layer**, one theme per patch, each patch citing the run id that triggered it, then re-run the same task to verify (A/B). The re-run gets its own directory — same date and slug, next `-NN` — so run A's evidence stays put: **run A is the lower `NN`, run B the next one up** (`2026-08-01-fix-tests-01` vs `-02`). Cite both run ids in the ledger and diff their scorecards; a patch you cannot A/B against surviving evidence is not verified.
- **Ledger**: one row per run, failures especially. Maintain a running accept rate. Circuit-breaker: accept rate <50% over 6 runs → pause and reassess with the user. Graduation: a task family with 3 consecutive ACCEPTs moves to routine execution (auto L1 + spot-check L3).
- **Reflect**: every 3–5 runs, read the ledger + the `⑥ instruction-friction` field of each report; route each recurring friction down the decision ladder — scriptable → into the gate; rule-shaped → into the task template; taste → escalate to a stronger model or the user.

---

## Hard rules for this skill

- **The gate is the prerequisite, not an output.** Never adopt the loop into a repo with no red-capable mechanical gate, and never stand in a fake always-green gate. If there is no gate, stop and bootstrap one first. A check that *did not run* counts as a fake green — this holds for all three required checks (gate, scope, commit): `oc-score.sh` rules such a run `INCONCLUSIVE`, and an `INCONCLUSIVE` is never recorded as an accepted run in the ledger (it would hide the circuit-breaker's accept rate behind a floor nobody ever exercised).
- **One dispatch, one run directory.** Run dirs are keyed `(date, slug, sequence)` and claimed atomically; never hand-edit a run dir's artifacts to make a re-run "fit", and never delete run A to tidy up after an A/B. The ledger's attribution chain is only as good as the evidence it points at.
- **§0–§6 are verbatim; only §7 is per-repo.** The constitution's core is harness-neutral doctrine — do not re-author it. All repo specifics live in the §7 binding table and in the scripts' env.
- **The author never signs off its own work.** L3 acceptance is always a fresh-context judge, and the commander's own outputs are verified by someone else too (COMMANDER §2).
- **Never mark done because budget ran out.** Uncertainty = not done; an honest partial beat a truncated near-complete (COMMANDER §1, TASK-TEMPLATE 預算意識).
- **Scaffold, do not clobber.** If the target repo already has a `LEDGER.md`, task template, or report protocol, merge into it — do not overwrite hand-written content.
