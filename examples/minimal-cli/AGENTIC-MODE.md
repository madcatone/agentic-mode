<!--
Template-Source: agentic-bootstrap/AGENTIC-MODE@v2  (@v2: added Canonical Questions
section + Template-Source marker; headings rule made explicit)
-->

# AGENTIC-MODE.md — Doc Contract for todo

> The resident index for this repo's **layered, ID-joined, harness-neutral**
> documentation contract. Any collaborator — human or agent, in any tool, with
> no chat history — reads top-down from here and reaches productive context in
> minutes. This file is **meta and resident**: read it every session. It owns
> *What* (repo facts, behavior contract) and *Done* (acceptance evidence); it
> never dictates *How/Who*. Doctrine lives in the agentic-mode repo's
> `doctrine/BOOTSTRAP-CORE.md`; the machine config is `agentic-mode/config.json`.

Project: **todo** (cli). ID prefix: `TODO`.

## Doc Inventory — One Job Per File

| Layer | Canonical file | Single responsibility |
|---|---|---|
| Onboarding | `README.md` | What is this, which entry point, quick start, neutrality. |
| Repo facts + co-op contract | `AGENTS.md` | Scope, key files, dev commands, change-flow, Stop-and-Ask — *What/Done* only. |
| Behavior contract | `docs/REQUIREMENTS.md` | Problem/Goals/Non-Goals, `TODO-NNN` requirements, append-only iteration history. |
| Observable surface | `docs/USER_GUIDE.md` | Commands, flags, output — what users type and see. |
| Done evidence | `docs/VALIDATION.md` | Per-feature checklist citing the `TODO-NNN` IDs. |
| Process rules | `docs/WORKFLOW.md` | Issue → branch → commit → PR → review loop — copied ~as-is. |

## Source-of-Truth Precedence When Docs Conflict

Resolve by responsibility, not by recency.

| Question | Winning layer |
|---|---|
| What is allowed during git / issue / PR operations? | `docs/WORKFLOW.md` |
| What safety and repo-scope rules bind collaborators? | `AGENTS.md` |
| What is the required behavior? | `docs/REQUIREMENTS.md` |
| What should users type, press, or see? | `docs/USER_GUIDE.md` |
| What proved a feature was completed? | `docs/VALIDATION.md` |
| What should a newcomer read first? | `README.md` |

## Enforcement

Run the repo-local gate. Same check; run the invocation that matches your cwd.

From this directory (`examples/minimal-cli/`):

```bash
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
```

From the agentic-mode repo root:

```bash
python3 checker/check_agentic_docs.py --config examples/minimal-cli/agentic-mode/config.json --root examples/minimal-cli
```

It automates ID continuity (`TODO-NNN` resolves and is cited), command-surface
consistency, the `AGENTS.md` line limit, the neutrality sweep, and — enabled in
this example — the IPv4 / machine-path leak sweeps and the iteration-history
numbering check. Everything it cannot mechanize stays a manual review in
`agentic-mode/SELF-TEST.md`.

CI platform: **github**. The gate runs on every change.

## Canonical Questions — Answerable Cold From the Docs Alone

These are the questions a **zero-context reviewer** (never seen this repo, no chat history) must be able to answer from the committed docs alone. Seed them from the Layered Reading Order, keep three to seven, and maintain them **here** — `agentic-mode/SELF-TEST.md` §D consumes this list for the read-back probe; it does not carry a second copy.

1. What does `todo` do, and how do I add my first task?
2. What am I allowed and not allowed to do here, and when must I stop and ask?
3. What is the behavior contract for the store path, and which `TODO-XXX` governs it?
4. What is the observable surface for `list` (the command and its `--all` flag)?
5. How do I prove a change to `done` is complete, and how do I move it through review?

## Routing

- **Doctrine** → the agentic-mode repo's `doctrine/BOOTSTRAP-CORE.md`.
- **Machine config** → `agentic-mode/config.json`.
- **Full cross-layer self-test** → `agentic-mode/SELF-TEST.md`; the questions it asks live in the Canonical Questions section above.
