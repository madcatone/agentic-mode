<!--
TEMPLATE: agentic-mode/SELF-TEST.md — resident cross-layer coherence gate for the target repo.
Filled from config.json (id.prefix, docs.*, ci.platform, checks.*). The automated section is a single
command; the manual section is intentionally minimal. This file MUST carry the four guardrails and the
zero-context read-back probe unchanged in spirit. The canonical questions the probe asks live in the
resident index's Canonical Questions section — this file points at them, it does not duplicate them.
Under the `light` co-op profile the append-only rows relax; every other row still binds.
Render body prose in the TARGET's chosen language; keep the section headings in canonical English.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Resolve `{{IF ...}}` regions per BOOTSTRAP-CORE, "Conditional Text in Templates".
Template-Source: agentic-bootstrap/SELF-TEST@v3  (@v3: rows that name an optional doc moved inside
regions; the ID-continuity and command-surface bullets are reworded and no longer quote the
placeholder sweep's braces; §B names the VALIDATION backfill exception; §D makes the pre-release
read-back optional; the process-doc boundary row names the declared substitution points and
allows a declared local exception)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# SELF-TEST.md — Cross-Layer Self-Test

Run this once all seeded docs exist. Every row is a gate: a failure blocks hand-off. **Fix the offending doc, not the test.** This is the coherence contract that turns independent files into one ID-joined system.

---

## A. Automated section — one command

The mechanizable checks run from a single repo-local command:

```bash
python scripts/check_agentic_docs.py --config agentic-mode/config.json
```

It enforces, from `agentic-mode/config.json`:

- **ID continuity** — every `{{PREFIX}}-NNN` cited in another governed prose doc resolves to a row in `{{REQUIREMENTS_PATH}}` (rows are duplicate-free and gap-free; bilingual regions carry identical ID sets). Not machine-checked: references in commit/MR/PR messages (a review discipline — the checker reads docs, not git history), the uniform format `^[A-Z]{2,6}-[0-9]{3,}$` itself, and "every observable behavior maps to ≥1 ID" (a Phase-B gate in the RUNBOOK).
- **Command-surface consistency** — every `checks.commands` entry appears in the files its `must_appear_in` lists. README quick-start ↔ surface parity beyond the configured commands is a review matter; surviving `<command>` / `<placeholder>` markers and any unresolved region marker are swept by hand in Phase C (RUNBOOK).
- **Line limit** — the generated `{{AGENTS_PATH}}` stays within `checks.line_limits`.
- **Neutrality / harness-neutrality** — the configurable forbidden-token sweep (`checks.deny_words`, `checks.harness_neutrality`) over docs/examples, honoring `agentic-gate: allow` markers.
- **Layer presence** — every doc path declared under `docs` in the config exists. (That README cross-links the layers is not machine-checked.)

Run it until it exits clean before touching the manual rows. **CI:** platform is `{{CI_PLATFORM}}`; when not `none`, this command runs on every change.

---

## B. Manual section — what the script cannot judge

Walk these by hand (kept deliberately short — the script owns everything mechanizable):

{{IF ARCHITECTURE_PATH}}- [ ] **Architecture ↔ prose coherence.** Every entry point in README is a component in `{{ARCHITECTURE_PATH}}` and vice-versa; component labels naming a symbol exist in source; connection labels naming a flag match a real flag.{{END IF}}
- [ ] **Dev commands actually run clean.** From a fresh checkout, the AGENTS Development Commands build/compile, test, and smoke all exit 0 with the expected output. The script checks that they are *cited*; only a human/agent run proves they *work*.
- [ ] **Append-only provenance holds.** REQUIREMENTS Iteration History and VALIDATION blocks were appended, not rewritten — verifiable via `git diff` across recent commits (only appends, plus the one post-merge backfill the VALIDATION header declares). *(Relaxed under the `light` co-op profile.)*
{{IF WORKFLOW_PATH}}- [ ] **Process-doc boundary holds.** `{{AGENTS_PATH}}` defers change-flow to `{{WORKFLOW_PATH}}` and names no platform CLI. The WORKFLOW doc is the copied-as-is template with only its declared substitution points resolved, or a hand-written doc, with any local exception declared in its header.{{ELSE}}- [ ] **Process-doc boundary holds.** `{{AGENTS_PATH}}` names no platform CLI and carries the platform-neutral review policy in full. No WORKFLOW doc is seeded.{{END IF}}
- [ ] **Bilingual lock-step** *(only if `bilingual.enabled`)* — both tracks share identical ID set/count/order and identical surface tables; cross-language citations are descriptive, not numeric.
- [ ] **Read-back probe passes** (section D below).

---

## C. Four guardrails (bind every collaborator, human or agent)

These are not style rules; they are stop conditions. A collaborator who violates them has not done the work, regardless of what the diff shows.

**(a) Two failed fixes of one check → stop and escalate.** If the same check fails twice after two distinct fix attempts, stop iterating. Write down the current hypothesis, the exact failing output, and what each attempt changed; then escalate to a human (or a stronger reviewer). Do not keep trying variations on the same approach.

**(b) Stop-and-Ask before high-consequence actions.** Do not proceed silently on any action in the `{{AGENTS_PATH}}` **Stop-and-Ask** list — ask a human first, even if tooling permits it. That list is authoritative; this guardrail binds you to it and does not restate it.

**(c) Uncertainty = not done.** If you are not sure a requirement is met, a test truly passed, or a fact is correct, it is **not** complete. Mark it unverified and say what evidence is missing. Never round "probably fine" up to "done."

**(d) Never mark done because budget or time ran out.** Running out of steps, tokens, or patience is not completion. If you cannot finish, report the exact remaining gap and hand off — do not check the box to close the loop.

---

## D. Zero-context read-back probe

The ultimate test of the contract is whether a **zero-context reviewer** (a human or agent who has never seen this repo or any chat history) can answer the repo's canonical questions using **only the committed docs**. This catches gaps the mechanical checker cannot: an ID that resolves but whose prose is incomprehensible cold, a workflow rule that reads fine to the author but not to a stranger.

**Canonical questions.** The resident `{{INDEX_PATH}}` lists **N** canonical questions this repo's docs must answer cold, in its **Canonical Questions** section. Seed and maintain them **there** — one list, one home; this probe consumes that list and does not carry a second copy. Seed from the Layered Reading Order (see BOOTSTRAP-CORE), keep three to seven questions.

**Protocol.**
1. Hand a zero-context reviewer *only* the repo's committed docs — no chat history, no walkthrough.
2. Ask them the canonical questions. They answer *solely* from the docs, citing the file:section (and `{{PREFIX}}-XXX` where relevant) that supplied each answer.
3. Any question they cannot answer, or answer wrongly, marks a **doc gap** — the docs, not the reader, are at fault. Fix the offending layer.
4. **Record the outcome in `{{VALIDATION_PATH}}`**: the date, who/what read back, each question's pass/fail, and the citation or the gap found. A clean read-back is part of the done evidence for a bootstrap or a major doc change; before a release tag it is an optional drift check{{IF WORKFLOW_PATH}} (WORKFLOW release checklist){{END IF}}.

A repo passes the read-back probe when every canonical question is answerable, cold, from the docs alone.
