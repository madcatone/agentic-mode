<!--
Template-Source: agentic-bootstrap/AGENTIC-MODE@v3  (@v3: optional-layer rows and precedence
cells moved inside regions, each with a stand-in for the absent doc; the AGENTS inventory
row names the platform-neutral MR / PR policy; "Visual architecture (optional)" is now
"Architecture inventory"; the Enforcement paragraph says "surface parity" and no longer
quotes the placeholder sweep's braces; Routing no longer says the config carries profiles)
-->

# AGENTIC-MODE.md — Doc Contract for Agent + Human Co-Development

> What this is: the resident index for a **layered, ID-joined, harness-neutral** documentation contract. Any collaborator — human or agent, in any tool, with no chat history — reads top-down from here and reaches productive context in minutes. This file is **meta and resident**: read it every session. It owns *What* (repo facts, behavior contract) and *Done* (acceptance evidence); it never dictates *How/Who* (which tool or model you use). Doctrine lives in the agentic-mode canonical repo's `doctrine/BOOTSTRAP-CORE.md`; the machine config is `agentic-mode/config.json`.

Project: **todo** (cli). ID prefix: `TODO`. It is project-neutral — replace any placeholder such as `<package.name>` with your own runtime values; do not hardcode brand/host/serial tokens.

---

## Doc Inventory — One Job Per File

| Layer | Canonical file | Single responsibility |
|---|---|---|
| Onboarding | `README.md` | What is this, which entry point to pick, quick start, neutrality/contracts. |
| Repo facts + co-op contract | `AGENTS.md` | Scope, key files, dev commands, change-flow, the platform-neutral MR / PR policy, sign-off points, Stop-and-Ask list — *What/Done* only. |
| Behavior contract | `docs/REQUIREMENTS.md` | Problem/Goals/Non-Goals, enumerated functional requirements with stable IDs (each row names the observable surface it governs), event/domain model, append-only iteration history, acceptance criteria, verification commands. |
| Observable surface | `docs/USER_GUIDE.md` | Commands, flags, output — what users see, press, or call. |
| Done evidence | `docs/VALIDATION.md` | Per-feature checklist: Code Implementation / Integration Points / User Requirements Met / Documentation Updates / Testing / Verification Commands / Status. |
| Process rules | `docs/WORKFLOW.md` | Issue → branch → commit → MR/PR → review loop, red lines, platform CLI conventions — copied as-is except the H1 and `Template-Source` line. |

**Anti-pattern:** a single `NOTES.md` / `DESIGN.md` mixing contract, guide, status, and process. It rots because no one knows which section is authoritative. <!-- agentic-gate: allow -->

## Source-of-Truth Precedence When Docs Conflict

Resolve by responsibility, not by recency.

| Question | Winning layer |
|---|---|
| What is allowed during git / issue / MR/PR operations? | `docs/WORKFLOW.md` |
| What safety and repo-scope rules bind collaborators? | `AGENTS.md` |
| What is the required behavior? | `docs/REQUIREMENTS.md` |
| What should users type, press, see, or call? | `docs/USER_GUIDE.md` |
| What proved a feature was completed? | `docs/VALIDATION.md` |
| What components exist and how do they connect? | `README.md` Main Components / Data Flow and `AGENTS.md` Key Files. No architecture doc is seeded |
| What should a newcomer read first? | `README.md` |

README is the onboarding map, not the final authority for behavior or workflow. VALIDATION records done evidence, not new requirements. Iteration history explains why a decision changed; the current functional-requirement table states the live contract.

## Enforcement

The mechanical parts of the self-test are executable. Run the repo-local gate from `examples/minimal-cli/`:

```bash
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
```

It automates the mechanizable check classes — ID continuity (`TODO-NNN` rows are duplicate-free and gap-free; IDs cited in the other governed docs resolve), command-surface consistency (every `checks.commands` entry appears in the docs its `must_appear_in` lists), the `AGENTS.md` line limit, the configurable neutrality / harness-neutrality sweep, and — enabled in this example — the IPv4 / machine-path leak sweeps and the iteration-history numbering check. Lines that must show a bad example are exempted with a trailing `agentic-gate: allow` marker. What it does not mechanize — the `^[A-Z]{2,6}-[0-9]{3,}$` ID format itself, README ↔ surface parity beyond the configured commands, commit/MR/PR reference hygiene, and the placeholder sweep (RUNBOOK Phase C) — stays with manual review per `agentic-mode/SELF-TEST.md`.

CI platform: **github**. When not `none`, the gate above runs on every change.

## Canonical Questions — Answerable Cold From the Docs Alone

These are the questions a **zero-context reviewer** (never seen this repo, no chat history) must be able to answer from the committed docs alone. Seed them from the Layered Reading Order, keep three to seven, and maintain them **here** — `agentic-mode/SELF-TEST.md` §D consumes this list for the read-back probe; it does not carry a second copy.

1. What does `todo` do, and how do I add my first task?
2. What am I allowed and not allowed to do in this repo, and when must I stop and ask?
3. What is the behavior contract for the store path, and which `TODO-XXX` governs it?
4. What is the observable surface for `list` (the command and its `--all` flag)?
5. How do I prove a change to `done` is complete, and how do I move it through review?

## Routing

- **Doctrine** (why the layers exist, ID discipline, append-only rules, adoption profiles) → the agentic-mode canonical repo's `doctrine/BOOTSTRAP-CORE.md`.
- **Machine config** (paths, prefix, checks, and the `null`s that record which layers are deferred) → `agentic-mode/config.json`.
- **Full cross-layer self-test** (all rows, manual + automated, guardrails, read-back probe protocol) → `agentic-mode/SELF-TEST.md`; the questions it asks live in the Canonical Questions section above.
