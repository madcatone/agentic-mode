<!--
Template-Source: agentic-bootstrap/SELF-TEST@v4  (@v4: §A names where each check that is not
machine-checked lives and no longer cites a toolkit doc; §D carries no question count and no
seeding instruction; a read-back record follows the VALIDATION record template, and a probe that
could not run is recorded as not run; the §B read-back row accepts that record; the §B
dev-command row names every listed command and exempts one that failed before the change under
test; commands run `python3`)
-->

# SELF-TEST.md — Cross-Layer Self-Test

Run this once all seeded docs exist. Every row is a gate: a failure blocks hand-off. **Fix the offending doc, not the test.** This is the coherence contract that turns independent files into one ID-joined system.

---

## A. Automated section — one command

The mechanizable checks run from a single repo-local command (run it from `examples/minimal-cli/`):

```bash
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
```

It enforces, from `agentic-mode/config.json`:

- **ID continuity** — every `TODO-NNN` cited in another governed prose doc resolves to a row in `docs/REQUIREMENTS.md` (rows are duplicate-free and gap-free; bilingual regions carry identical ID sets). Not machine-checked: references in commit/MR/PR messages (a review discipline — the checker reads docs, not git history), the uniform format `^[A-Z]{2,6}-[0-9]{3,}$` itself, and "every observable behavior maps to ≥1 ID" (a gate the bootstrap runs).
- **Iteration continuity** — the Iteration History entries are numbered gap-free (enabled in this example).
- **Command-surface consistency** — every `checks.commands` entry appears in the files its `must_appear_in` lists. README quick-start ↔ surface parity beyond the configured commands is a review matter. A leftover placeholder, in any generated file, is swept by hand whenever these docs are generated or upgraded.
- **Line limit** — the generated `AGENTS.md` stays within `checks.line_limits`.
- **Neutrality / harness-neutrality** — the configurable forbidden-token sweep (`checks.deny_words`, `checks.harness_neutrality`) over docs/examples, honoring `agentic-gate: allow` markers, plus — enabled in this example — the IPv4 and machine-path leak sweeps.
- **Layer presence** — every doc path declared under `docs` in the config exists. (That README cross-links the layers is not machine-checked.)
- **Entrypoint** — every path in `checks.entrypoints` exists; `.py` entrypoints byte-compile (`todo.py`).

Run it until it exits clean before touching the manual rows. **CI:** platform is `github`; when not `none`, this command runs on every change.

---

## B. Manual section — what the script cannot judge

Walk these by hand (kept deliberately short — the script owns everything mechanizable):

- [ ] **Dev commands actually run clean.** From a fresh checkout, each command in the AGENTS Development Commands exits 0 with the expected output. This example carries no test command. A command that already failed before the change under test is reported, and does not fail this row. The script checks that they are *cited*; only a human/agent run proves they *work*.
- [ ] **Append-only provenance holds.** REQUIREMENTS Iteration History and VALIDATION blocks were appended, not rewritten — verifiable via `git diff` across recent commits (only appends, plus the one post-merge backfill the VALIDATION header declares). *(Relaxed under the `light` co-op profile.)*
- [ ] **Process-doc boundary holds.** `AGENTS.md` defers change-flow to `docs/WORKFLOW.md` and names no platform CLI. The WORKFLOW doc is the copied-as-is template with only its declared substitution points resolved, or a hand-written doc, with any local exception declared in its header.
- [ ] **Read-back probe passes**, or the latest read-back record in `docs/VALIDATION.md` says not run (section D below).

---

## C. Four guardrails (bind every collaborator, human or agent)

These are not style rules; they are stop conditions. A collaborator who violates them has not done the work, regardless of what the diff shows.

**(a) Two failed fixes of one check → stop and escalate.** If the same check fails twice after two distinct fix attempts, stop iterating. Write down the current hypothesis, the exact failing output, and what each attempt changed; then escalate to a human (or a stronger reviewer). Do not keep trying variations on the same approach.

**(b) Stop-and-Ask before high-consequence actions.** Do not proceed silently on any action in the `AGENTS.md` **Stop-and-Ask** list — ask a human first, even if tooling permits it. That list is authoritative; this guardrail binds you to it and does not restate it.

**(c) Uncertainty = not done.** If you are not sure a requirement is met, a test truly passed, or a fact is correct, it is **not** complete. Mark it unverified and say what evidence is missing. Never round "probably fine" up to "done."

**(d) Never mark done because budget or time ran out.** Running out of steps, tokens, or patience is not completion. If you cannot finish, report the exact remaining gap and hand off — do not check the box to close the loop.

---

## D. Zero-context read-back probe

The ultimate test of the contract is whether a **zero-context reviewer** (a human or agent who has never seen this repo or any chat history) can answer the repo's canonical questions using **only the committed docs**. This catches gaps the mechanical checker cannot: an ID that resolves but whose prose is incomprehensible cold, a workflow rule that reads fine to the author but not to a stranger.

**Canonical questions.** The resident `AGENTIC-MODE.md` lists the canonical questions this repo's docs must answer cold, in its **Canonical Questions** section. Maintain them **there**. One list, one home. This probe consumes that list and does not carry a second copy.

**Protocol.**
1. Hand a zero-context reviewer *only* the repo's committed docs — no chat history, no walkthrough.
2. Ask them the canonical questions. They answer *solely* from the docs, citing the file:section (and `TODO-XXX` where relevant) that supplied each answer.
3. Any question they cannot answer, or answer wrongly, marks a **doc gap** — the docs, not the reader, are at fault. Fix the offending layer.
4. **Record the outcome in `docs/VALIDATION.md`** with the read-back record template the file carries: the date, who/what read back, each question's pass/fail, and the citation or the gap found. A clean read-back is part of the done evidence for a bootstrap or a major doc change. When no zero-context reader is available, record the probe as not run. That record does not block hand-off. Before a release tag the probe is an optional drift check (WORKFLOW release checklist).

A repo passes the read-back probe when every canonical question is answerable, cold, from the docs alone.
