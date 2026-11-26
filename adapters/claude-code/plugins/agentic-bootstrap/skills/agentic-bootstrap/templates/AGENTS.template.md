<!--
TEMPLATE: AGENTS.md — LEAN. Repo facts + co-operation contract ONLY (What/Done).
Filled from config.json (project.*, id.prefix, docs.*, checks.commands, checks.entrypoints,
checks.line_limits.agents) and Phase-A answers (scope, key files, dev commands).

DO put here: scope, key files, dev/verify commands, the change-flow, sign-off points,
the Stop-and-Ask list.
DO NOT put here: generic agent discipline (how to dispatch, which model/tool to use, how to
parallelize) — that is the executor's environment (How/Who), not this contract.
DO NOT put here: platform-CLI rules or comment styles — those belong in the WORKFLOW doc when one is seeded, and never here.

HARD LIMIT: the generated file MUST stay <= checks.line_limits.agents (set the limit explicitly
in agentic-mode/config.json — an absent key means the checker enforces no line limit).
The checker enforces this mechanically. Keep it terse; push depth to REQUIREMENTS and to the
WORKFLOW doc when one is seeded.
`{{LIGHT_PROFILE_NOTE_OR_DELETE}}`: under the `light` co-op profile write
``*(Under the `light` co-op profile this entry and the VALIDATION block in item 5 of this list are encouraged, not required.)*``.
Under every other profile delete it.
`{{SURFACE_DOC_ROLE}}` is `commands, flags, and output` for a CLI, `endpoints and screens` for a
web service, or `endpoints` for one with no screens, `the public API` for a library (RUNBOOK Phase
B, step 4).
A placeholder that describes something the target does not have follows the RUNBOOK's Phase-B rule
for a placeholder with no value. `{{TESTS_DIR}}` is the path of the tests, a directory or a single
file. `{{TESTS_DIR}}` and `{{FIXTURES_DIR}}` sit on one line. Delete the line when the target has
no tests. Delete only the clause that starts with `; fixtures in` when the target has tests but no
fixtures directory. When the target needs no runtime placeholders, delete the sentence that starts
with `Use runtime placeholders`. When it has no fixtures directory, delete the sentence that starts
with `Raw fixture lines`. `{{SECONDARY_ENTRY_OR_NONE}}` takes its whole sentence with it.
`{{TEST_CMD}}` and `{{TEST_FOCUSED_CMD_OR_NONE}}` each own a line.
`{{TEST_FOCUSED_CMD_OR_NONE}}` is filled only when TARGET already declares a focused test command.
Otherwise the line goes.
`{{INDEPENDENCE_INVARIANT_OR_NONE}}` is the one rule every entry point keeps, whatever the
others do, for example a shared store format. It has no value when the target has one entry point.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Resolve `{{IF ...}}` regions per BOOTSTRAP-CORE, "Conditional Text in Templates".
Template-Source: agentic-bootstrap/AGENTS@v2  (@v2: Git Hygiene allows deleting a merged local
branch, as the WORKFLOW doc does; the header states the light-profile note and the no-value rule
for this template's optional slots; the Change-Flow Boundary heading drops its parenthetical;
Change Flow step 6 exempts a command that failed before the change; commands run `python3`)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# AGENTS.md — {{PROJECT_NAME}}

Repo facts and the human/agent co-operation contract for this repository. It states *what is true here* and *what "done" requires*. It does **not** tell you which tool, model, or dispatch to use — that is your own environment's business. Read `{{README_PATH}}` first, then this.

## Project Scope

- {{ONE_LINE_SCOPE — what this repo is, kept project-neutral}}.
- Primary maintained entry point: `{{PRIMARY_ENTRY}}`. Secondary/legacy: `{{SECONDARY_ENTRY_OR_NONE}}`. {{INDEPENDENCE_INVARIANT_OR_NONE}}.
- **Project-neutral.** Do not add brand names, product codenames, hardcoded package names, device serials, IP literals, or environment-specific hosts to code, docs, tests, or examples. Use runtime placeholders ({{RUNTIME_PLACEHOLDERS}}) in docs and examples. Raw fixture lines are the only exception, and stay inside the fixtures directory.

## Key Files

- `{{README_PATH}}`: onboarding, entry picker, quick start.
- `{{PRIMARY_ENTRY}}`: {{ROLE — primary maintained path}}.
- `{{SECONDARY_ENTRY_OR_NONE}}`: {{ROLE — legacy/optional, or delete this line}}.
- `{{REQUIREMENTS_PATH}}`: behavior contract (IDs: `{{PREFIX}}-XXX`).{{IF SURFACE_DOC_PATH}}{{ELSE}} Also carries the observable surface, one exercising command per row.{{END IF}}
{{IF SURFACE_DOC_PATH}}- `{{SURFACE_DOC_PATH}}`: observable surface ({{SURFACE_DOC_ROLE}}).{{END IF}}
- `{{VALIDATION_PATH}}`: per-feature done evidence.
{{IF WORKFLOW_PATH}}- `{{WORKFLOW_PATH}}`: platform review loop (see Change Flow below).{{END IF}}
- `{{TESTS_DIR}}`: {{WHAT_TESTS_COVER}}; fixtures in `{{FIXTURES_DIR}}`.
{{IF ARCHITECTURE_PATH}}<!-- Reconcile this list with `{{ARCHITECTURE_PATH}}` components[]. -->{{END IF}}

## Development Commands

- Build / compile: `{{BUILD_CMD}}`
- Full tests: `{{TEST_CMD}}`
- Focused tests: `{{TEST_FOCUSED_CMD_OR_NONE}}`
- Smoke / run: `{{SMOKE_CMD}}`
- Docs coherence gate: `python3 scripts/check_agentic_docs.py --config agentic-mode/config.json`

Every command in `checks.commands` (config.json) that lists `"agents"` in `must_appear_in` MUST appear verbatim in this section — the checker verifies it.

## Change Flow (What "Done" Requires)

A behavior change is **not done** until all of these hold. The ID is the join key that keeps them in sync:

1. Code edited.
2. `{{REQUIREMENTS_PATH}}` — the requirement `{{PREFIX}}-XXX` is added or updated, with a new **append-only** Iteration History entry (lead with the decision, then the evidence: numbers/fingerprint/issue-MR link). {{LIGHT_PROFILE_NOTE_OR_DELETE}}
3. {{IF SURFACE_DOC_PATH}}`{{SURFACE_DOC_PATH}}` — the subsection for that behavior is updated and cites the `{{PREFIX}}-XXX` ID.{{ELSE}}The observable surface. The requirement row from step 2 records the command / call that exercises the behavior and what the user observes.{{END IF}}
4. `{{README_PATH}}` — quick-start updated **iff** a user-visible command/entry changed.
5. `{{VALIDATION_PATH}}` — a per-feature block is **appended**, citing the `{{PREFIX}}-XXX` ID and the issue/MR/PR number.
6. Verification commands run clean (see Development Commands) and the docs gate exits clean. A command that already failed before this change is reported, and does not fail this step.

## Sign-Off Points

- The author of a change does not sign off their own completion claim on evidence they merely asserted. Completion is proven by **objective command output** (build/test/gate) or by a **zero-context reviewer** re-verifying against the acceptance criteria — not by "looks fine."
- A reviewer (human or agent) can re-verify any landed feature by running the Verification Commands in its `{{VALIDATION_PATH}}` block. If they cannot, the block is incomplete.

## Stop-and-Ask (do NOT proceed silently)

Stop and ask a human before any of these, even if permissions technically allow it:

- Changing a **public API surface** or a serialized **schema** (breaking downstream callers/data).
- **Irreversible deletion** of files, data, or history.
- **CI / release configuration** changes, or anything touching credentials, tokens, or **auth/security**.
- Any **irreversible or externally visible** action not explicitly requested (deploy, force-push, publish, send).
- A user premise that the evidence contradicts — report the evidence to the user first and wait for their decision. Do not act on the original premise, and do not substitute your own alternative, until they respond.

## MR / PR Governance

Landing a change on `main`, the default branch, or any protected branch happens **only** through a merge/pull request (MR/PR) — never a direct commit or push, even where permissions technically allow it. This section is the platform-neutral policy; {{IF WORKFLOW_PATH}}the CLI and exact commands live in `{{WORKFLOW_PATH}}`.{{ELSE}}no WORKFLOW doc is seeded, so this section is the whole review policy.{{END IF}}

- **Route through review, positively.** Every completed change meant for a protected branch gets an MR/PR opened or updated for it. The obligation is to *land through review*, not merely to avoid pushing directly.
- **Authorization inference.** When the user says "push the completed work," read it as *push the source branch and open or update its MR/PR* — unless they explicitly name a non-protected branch **and** say not to open one.
- **Before opening one, verify:** the correct cwd and worktree, the current branch, a clean tree, the intended target branch, and whether an open MR/PR already exists for the same source branch. Never open one from an unpushed branch — push the source branch first, and only when the user asked. If the target branch is unclear, ask.
- **After opening or updating one, verify it** through the platform's own tooling: confirm the title, description, source and target branches, assignee, and pipeline/checks status all match intent.
- **Report back** the MR/PR URL and its key metadata to the user.
- **Recovery.** If a change reaches a protected branch directly by mistake, restore review flow with a revert branch and a revert MR/PR — never force-push or rewrite protected history. Run parallel MRs/PRs in separate worktrees so they do not collide.

## Change-Flow Boundary

- Move changes through review per **MR / PR Governance** above{{IF WORKFLOW_PATH}} and per `{{WORKFLOW_PATH}}`{{END IF}}. **Boundary test:** if a rule names the platform CLI or a platform-specific comment style, it {{IF WORKFLOW_PATH}}belongs in `{{WORKFLOW_PATH}}`{{ELSE}}does not belong here{{END IF}}.

## Git Hygiene

- Keep transient output, generated assets, local virtual environments, and dependency folders out of commits — add them to the ignore file instead of staging them.
- Stage files explicitly; never blanket-add. Keep secrets and `.env` values out of every commit — load them from the environment at runtime instead.
- Do not push, force-push, tag, or delete branches unless the user explicitly asks. Never push directly to `main` / the default / protected branches — open a merge/pull request instead. You may delete one kind of branch unasked. A local branch whose commits are already merged goes with `git branch -d`, never `-D`.
