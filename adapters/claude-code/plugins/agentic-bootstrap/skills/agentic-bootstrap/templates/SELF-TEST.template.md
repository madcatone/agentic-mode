<!--
TEMPLATE: agentic-mode/SELF-TEST.md — resident cross-layer coherence gate for the target repo.
Filled from config.json (id.prefix, docs.*, ci.platform, checks.*). The automated section is a single
command; the manual section is intentionally minimal. This file MUST carry the four guardrails and the
zero-context read-back probe unchanged in spirit.
Under the `light` co-op profile the append-only rows relax; every other row still binds.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
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

- **ID continuity** — every `{{PREFIX}}-NNN` cited in README, AGENTS, the observable-surface doc, VALIDATION, and the latest commit/MR/PR resolves to a row in `{{REQUIREMENTS_PATH}}`; every observable behavior maps to ≥1 ID; uniform format `^[A-Z]{2,6}-[0-9]{3,}$`.
- **Command-surface consistency** — README quick-start ↔ observable-surface doc; every `checks.commands` entry appears in the files its `must_appear_in` lists; no surviving `<command>` / `{{PLACEHOLDER}}` / empty smoke command in any verification block.
- **Line limit** — the generated `{{AGENTS_PATH}}` stays within `checks.line_limits`.
- **Neutrality / harness-neutrality** — the configurable forbidden-token sweep (`checks.deny_words`, `checks.harness_neutrality`) over docs/examples, honoring `agentic-gate: allow` markers.
- **Layer presence + cross-links** — required layer files exist and README links to them.

Run it until it exits clean before touching the manual rows. **CI:** platform is `{{CI_PLATFORM}}`; when not `none`, this command runs on every change.

---

## B. Manual section — what the script cannot judge

Walk these by hand (kept deliberately short — the script owns everything mechanizable):

- [ ] **Architecture ↔ prose coherence.** If `docs/architecture.json` exists: every entry point in README is a component in the JSON and vice-versa; component labels naming a symbol exist in source; connection labels naming a flag match a real flag. (Skip if no architecture doc.)
- [ ] **Dev commands actually run clean.** From a fresh checkout, the AGENTS Development Commands build/compile, test, and smoke all exit 0 with the expected output. The script checks that they are *cited*; only a human/agent run proves they *work*.
- [ ] **Append-only provenance holds.** REQUIREMENTS Iteration History and VALIDATION blocks were appended, not rewritten — verifiable via `git diff` across recent commits (only appends). *(Relaxed under the `light` co-op profile.)*
- [ ] **Process-doc boundary holds.** `{{AGENTS_PATH}}` defers change-flow to `{{WORKFLOW_PATH}}` and names no platform CLI. The WORKFLOW doc is the copied-as-is template with only the H1 / `Template-Source` substituted.
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

**Canonical questions.** The resident `{{INDEX_PATH}}` lists **N** canonical questions this repo's docs must answer cold. Seed them from the Layered Reading Order — for example:

1. What does this project do, and which entry point do I pick for {{PRIMARY_USE_CASE}}?
2. What am I allowed and not allowed to do in this repo, and when must I stop and ask?
3. What is the behavior contract for {{KEY_BEHAVIOR}}, and which `{{PREFIX}}-XXX` ID governs it?
4. What is the observable surface for {{KEY_BEHAVIOR}} (the command / key / endpoint / API)?
5. How do I prove a change to {{KEY_BEHAVIOR}} is done, and how do I move it through review?

**Protocol.**
1. Hand a zero-context reviewer *only* the repo's committed docs — no chat history, no walkthrough.
2. Ask them the canonical questions. They answer *solely* from the docs, citing the file:section (and `{{PREFIX}}-XXX` where relevant) that supplied each answer.
3. Any question they cannot answer, or answer wrongly, marks a **doc gap** — the docs, not the reader, are at fault. Fix the offending layer.
4. **Record the outcome in `{{VALIDATION_PATH}}`**: the date, who/what read back, each question's pass/fail, and the citation or the gap found. A clean read-back is part of the done evidence for a bootstrap or a major doc change.

A repo passes the read-back probe when every canonical question is answerable, cold, from the docs alone.
