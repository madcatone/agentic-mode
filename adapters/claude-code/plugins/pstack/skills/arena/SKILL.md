---
name: arena
description: "Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact would lock in the wrong shape."
---

# Arena

Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners from the `arena runners` line in the project's agent configuration (a rules or settings file the harness reads). With no configured models, default to your strongest available model plus one runner each from two other model families. Where fewer families are available, fill the seats with the strongest model of each family not yet used. Where only one family exists, run every seat on your strongest available model. State in the synthesis record whenever model diversity is reduced. A slug's family is the text before its first hyphen, after you drop a leading harness-vendor token. When one slug's family text is a prefix of another's, the longer text is the family. An `auto` or `inherit-parent` entry is the parent model, so omit the model setting and spawn a general-purpose subagent. If the harness rejects a slug, use the nearest valid slug of the same family or drop the seat. Keep at least two runners, and say so when you drop a seat or change a family. Spawn more runners for multiple design directions, and repeat one model when the work is generation-bound, not judgment-sensitive. Pick each subagent's reasoning level for the job.
4. Give each candidate its own output location (a git worktree where possible, otherwise a per-candidate scratch directory outside the repo), per the **separate-before-serializing-shared-state** principle skill.

## Phase B: Fan out

Spawn all N subagents in one message so they run in parallel, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artifact and a short rationale naming the alternatives it considered and what it rejected.

If a candidate produces no output, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After all Phase B candidates complete, spawn one read-only judge from the `arena cross-judge pool` line in that same agent configuration. With no configured pool, use the same defaults as Phase A. The judge is never from the parent's vendor. When you do not know the parent's model, use the first real slug and say that the vendor check did not run. An `auto` or `inherit-parent` entry is the parent model, so omit the model setting. If the harness rejects a slug, use the nearest valid slug of the same family, then the next such entry, or skip the judge, and say so. While you read in Phase D, the judge scores each candidate, by path label, on each rubric criterion and recommends a base.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the **laziness-protocol** principle skill.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
