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
- Docs coherence gate: `python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json`

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

## Change-Flow Boundary (defer to WORKFLOW)

- Move changes through review per `docs/WORKFLOW.md`. **Boundary test:** if a rule
  names the platform CLI or a platform-specific comment style, it belongs in
  `docs/WORKFLOW.md`, not here.

## Git Hygiene

- Do not commit the runtime task store (`tasks.json`) or other transient output.
- Explicit file staging; never commit secrets or `.env` values.
- Never push directly to `main` — open a pull request instead.
