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

Run the repo-local gate:

```bash
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
```

It automates ID continuity (`TODO-NNN` resolves and is cited), command-surface
consistency, the `AGENTS.md` line limit, the neutrality sweep, and — enabled in
this example — the IPv4 / machine-path leak sweeps and the iteration-history
numbering check. Everything it cannot mechanize stays a manual review in
`agentic-mode/SELF-TEST.md`.

CI platform: **github**. The gate runs on every change.

## Routing

- **Doctrine** → the agentic-mode repo's `doctrine/BOOTSTRAP-CORE.md`.
- **Machine config** → `agentic-mode/config.json`.
- **Full cross-layer self-test** → `agentic-mode/SELF-TEST.md`.
