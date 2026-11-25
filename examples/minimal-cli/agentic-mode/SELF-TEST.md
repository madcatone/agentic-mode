<!--
Template-Source: agentic-bootstrap/SELF-TEST@v2  (@v2: §D now points at the index's Canonical
Questions section instead of embedding its own example list; Template-Source marker added)
-->

# SELF-TEST.md — Cross-Layer Self-Test

Run this once all seeded docs exist. Every row is a gate: a failure blocks
hand-off. **Fix the offending doc, not the test.**

## A. Automated section — one command

Same check; run the invocation that matches your cwd.

From `examples/minimal-cli/`:

```bash
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
```

From the agentic-mode repo root:

```bash
python3 checker/check_agentic_docs.py --config examples/minimal-cli/agentic-mode/config.json --root examples/minimal-cli
```

It enforces, from `agentic-mode/config.json`:

- **ID continuity** — every `TODO-NNN` cited in the user guide and validation
  resolves to a row in `docs/REQUIREMENTS.md`; IDs are gap-free.
- **Iteration continuity** — the Iteration History entries are numbered
  gap-free (enabled in this example).
- **Command-surface consistency** — every `checks.commands` entry appears in the
  files its `must_appear_in` lists.
- **Line limit** — `AGENTS.md` stays within `checks.line_limits`.
- **Neutrality** — the harness-neutrality sweep plus the IPv4 and machine-path
  leak sweeps, honoring `agentic-gate: allow` markers.
- **Layer presence + entrypoint** — declared docs exist; `todo.py` byte-compiles.

Run it until it exits clean before touching the manual rows.

## B. Manual section — what the script cannot judge

- [ ] **Dev commands actually run clean.** From a fresh checkout, `python3 -m
  py_compile todo.py` and the smoke flow exit 0.
- [ ] **Append-only provenance holds.** REQUIREMENTS Iteration History and
  VALIDATION blocks were appended, not rewritten (verify via `git diff`).
- [ ] **Process-doc boundary holds.** `AGENTS.md` defers change-flow to
  `docs/WORKFLOW.md` and names no platform CLI.
- [ ] **Read-back probe passes** (section D).

## C. Four guardrails (bind every collaborator, human or agent)

**(a) Two failed fixes of one check → stop and escalate.** Write down the
hypothesis, the failing output, and what each attempt changed; then escalate.

**(b) Stop-and-Ask before high-consequence actions** — store-schema changes,
irreversible deletion, CI/credential changes, any irreversible or externally
visible action not explicitly requested.

**(c) Uncertainty = not done.** If you are not sure a requirement is met, mark it
unverified and say what evidence is missing.

**(d) Never mark done because budget or time ran out.** Report the remaining gap
and hand off.

## D. Zero-context read-back probe

The ultimate test of the contract is whether a **zero-context reviewer** (a human or agent who has never seen this repo or any chat history) can answer the repo's canonical questions using **only the committed docs**. This catches gaps the mechanical checker cannot: an ID that resolves but whose prose is incomprehensible cold, a workflow rule that reads fine to the author but not to a stranger.

**Canonical questions.** The resident `AGENTIC-MODE.md` lists **five** canonical questions this repo's docs must answer cold, in its **Canonical Questions** section. Seed and maintain them **there** — one list, one home; this probe consumes that list and does not carry a second copy. Seed from the Layered Reading Order (see BOOTSTRAP-CORE), keep three to seven questions.

**Protocol.**
1. Hand a zero-context reviewer *only* the repo's committed docs — no chat history, no walkthrough.
2. Ask them the canonical questions. They answer *solely* from the docs, citing the file:section (and `TODO-XXX` where relevant) that supplied each answer.
3. Any question they cannot answer, or answer wrongly, marks a **doc gap** — the docs, not the reader, are at fault. Fix the offending layer.
4. **Record the outcome in `docs/VALIDATION.md`**: the date, who/what read back, each question's pass/fail, and the citation or the gap found. A clean read-back is part of the done evidence for a bootstrap, a major doc change, or a release tag (WORKFLOW release checklist).

A repo passes the read-back probe when every canonical question is answerable, cold, from the docs alone.
