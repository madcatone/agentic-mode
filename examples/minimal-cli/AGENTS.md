<!--
Template-Source: agentic-bootstrap/AGENTS@v2  (@v2: Git Hygiene allows deleting a merged local
branch, as the WORKFLOW doc does; the header states the light-profile note and the no-value rule
for this template's optional slots; the Change-Flow Boundary heading drops its parenthetical)
-->

# AGENTS.md — todo

Repo facts and the human/agent co-operation contract for the `todo` example. It
states *what is true here* and *what "done" requires*. It does not tell you which
tool, model, or dispatch to use — that is your own environment's business. Read
`README.md` first, then this.

## Project Scope

- A tiny standard-library CLI task tracker, and the worked example for the
  agentic-mode documentation contract.
- Primary maintained entry point: `todo.py`. There is no secondary entry point.
- **Project-neutral.** Do not add brand names, hardcoded hosts, IP literals, or
  absolute machine paths to code, docs, tests, or examples. The store path is a
  runtime input (`--store` / `TODO_STORE`).

## Key Files

- `README.md`: onboarding, entry picker, quick start.
- `todo.py`: the CLI entry point — add / list / done / remove.
- `docs/REQUIREMENTS.md`: behavior contract (IDs: `TODO-XXX`).
- `docs/USER_GUIDE.md`: observable surface (commands, flags, output).
- `docs/VALIDATION.md`: per-feature done evidence.
- `docs/WORKFLOW.md`: platform review loop (see Change Flow below).

## Development Commands

- Build / compile: `python3 -m py_compile todo.py`
- Smoke / run: `python3 todo.py list`
- Docs coherence gate. Same check; run the invocation that matches your cwd:
  - From the agentic-mode repo root: `python3 checker/check_agentic_docs.py --config examples/minimal-cli/agentic-mode/config.json --root examples/minimal-cli`
  - From this directory (`examples/minimal-cli/`): `python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json`

Every command in `checks.commands` (config.json) that lists `"agents"` in
`must_appear_in` MUST appear verbatim in this section — the checker verifies it.

## Change Flow (What "Done" Requires)

A behavior change is **not done** until all of these hold. The ID is the join
key that keeps them in sync:

1. Code edited.
2. `docs/REQUIREMENTS.md` — the `TODO-XXX` requirement is added or updated, with
   a new **append-only** Iteration History entry (decision first, then evidence:
   numbers / fingerprint / issue-PR link).
3. `docs/USER_GUIDE.md` — the subsection for that behavior is updated and cites
   the `TODO-XXX` ID.
4. `README.md` — quick-start updated **iff** a user-visible command changed.
5. `docs/VALIDATION.md` — a per-feature block is **appended**, citing the
   `TODO-XXX` ID and the issue/PR number.
6. Verification commands run clean and the docs gate exits clean.

## Sign-Off Points

- The author of a change does not sign off their own completion claim on evidence
  they merely asserted. Completion is proven by **objective command output**
  (build / gate) or by a **fresh-context reviewer** re-verifying against the
  acceptance criteria — not by "looks fine."
- A reviewer (human or agent) can re-verify any landed feature by running the
  Verification Commands in its `docs/VALIDATION.md` block.

## Stop-and-Ask (do NOT proceed silently)

Stop and ask a human before any of these, even if permissions technically allow it:

- Changing the on-disk **store schema** (breaks existing `tasks.json` files).
- **Irreversible deletion** of files, data, or history.
- **CI / release configuration** changes, or anything touching credentials or auth.
- Any **irreversible or externally visible** action not explicitly requested.
- A user premise the evidence contradicts — report the evidence first.

## MR / PR Governance

Landing a change on `main`, the default branch, or any protected branch happens
**only** through a merge/pull request (MR/PR) — never a direct commit or push,
even where permissions technically allow it. This section is the platform-neutral
policy; the CLI and exact commands live in `docs/WORKFLOW.md`.

- **Route through review, positively.** Every completed change meant for a
  protected branch gets an MR/PR opened or updated for it. The obligation is to
  *land through review*, not merely to avoid pushing directly.
- **Authorization inference.** When the user says "push the completed work," read
  it as *push the source branch and open or update its MR/PR* — unless they
  explicitly name a non-protected branch **and** say not to open one.
- **Before opening one, verify:** the correct cwd and worktree, the current
  branch, a clean tree, the intended target branch, and whether an open MR/PR
  already exists for the same source branch. Never open one from an unpushed
  branch — push the source branch first, and only when the user asked. If the
  target branch is unclear, ask.
- **After opening or updating one, verify it** through the platform's own
  tooling: confirm the title, description, source and target branches, assignee,
  and pipeline/checks status all match intent.
- **Report back** the MR/PR URL and its key metadata to the user.
- **Recovery.** If a change reaches a protected branch directly by mistake,
  restore review flow with a revert branch and a revert MR/PR — never force-push
  or rewrite protected history. Run parallel MRs/PRs in separate worktrees so
  they do not collide.

## Change-Flow Boundary

- Move changes through review per **MR / PR Governance** above and per
  `docs/WORKFLOW.md`. **Boundary test:** if a rule names the platform CLI or a
  platform-specific comment style, it belongs in `docs/WORKFLOW.md`.

## Git Hygiene

- Do not commit the runtime task store (`tasks.json`) or other transient output.
- Explicit file staging; never commit secrets or `.env` values.
- Do not push, force-push, tag, or delete branches unless the user explicitly
  asks. Never push directly to `main` — open a pull request instead. You may
  delete one kind of branch unasked. A local branch whose commits are already
  merged goes with `git branch -d`, never `-D`.
