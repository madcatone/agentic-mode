# SELF-TEST.md — Cross-Layer Self-Test

Run this once all seeded docs exist. Every row is a gate: a failure blocks
hand-off. **Fix the offending doc, not the test.**

## A. Automated section — one command

```bash
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
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

## D. Cold-reader read-back probe

A zero-context reader should answer these using only the committed docs:

1. What does `todo` do, and how do I add my first task?
2. What am I allowed and not allowed to do here, and when must I stop and ask?
3. What is the behavior contract for the store path, and which `TODO-XXX` governs it?
4. What is the observable surface for `list` (the command and its `--all` flag)?
5. How do I prove a change to `done` is complete, and how do I move it through review?

Any question they cannot answer marks a **doc gap** — fix the offending layer,
then record the read-back outcome in `docs/VALIDATION.md`.
