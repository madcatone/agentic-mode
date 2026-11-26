<!--
Template-Source: agentic-bootstrap/AGENTIC-MODE@v4  (@v4: the inventory lists the layers in reading
order, architecture third, and a sentence under it says so; the Enforcement paragraph routes each
non-mechanized check to where it lives instead of to SELF-TEST §B, and ends with two sentences on
the placeholder sweep; the Canonical Questions carry no seeding instruction; the doctrine pointers
say this repo keeps no copy and take the toolkit's location; the requirements row allows for no
event model; the process-rules row no longer names the H1 as a substitution point; commands run
`python3`)
-->

# AGENTIC-MODE.md — Doc Contract for Agent + Human Co-Development

> What this is: the resident index for a **layered, ID-joined, harness-neutral** documentation contract. Any collaborator — human or agent, in any tool, with no chat history — reads top-down from here and reaches productive context in minutes. This file is **meta and resident**: read it every session. It owns *What* (repo facts, behavior contract) and *Done* (acceptance evidence); it never dictates *How/Who* (which tool or model you use). Doctrine lives in the toolkit's `doctrine/BOOTSTRAP-CORE.md`, at the root of the repository that contains this example. This repo keeps no copy of it. The machine config is `agentic-mode/config.json`.

Project: **todo** (cli). ID prefix: `TODO`. It is project-neutral — replace any placeholder such as `<package.name>` with your own runtime values; do not hardcode brand/host/serial tokens.

---

## Doc Inventory — One Job Per File

| Layer | Canonical file | Single responsibility |
|---|---|---|
| Onboarding | `README.md` | What is this, which entry point to pick, quick start, neutrality/contracts. |
| Repo facts + co-op contract | `AGENTS.md` | Scope, key files, dev commands, change-flow, the platform-neutral MR / PR policy, sign-off points, Stop-and-Ask list — *What/Done* only. |
| Behavior contract | `docs/REQUIREMENTS.md` | Problem/Goals/Non-Goals, enumerated functional requirements with stable IDs (each row names the observable surface it governs), event/domain model when there is one, append-only iteration history, acceptance criteria, verification commands. |
| Observable surface | `docs/USER_GUIDE.md` | Commands, flags, output — what users see, press, or call. |
| Done evidence | `docs/VALIDATION.md` | Per-feature checklist: Code Implementation / Integration Points / User Requirements Met / Documentation Updates / Testing / Verification Commands / Status. |
| Process rules | `docs/WORKFLOW.md` | Issue → branch → commit → MR/PR → review loop, red lines, platform CLI conventions — copied as-is except its declared substitution points. |

The table lists the layers in the order a newcomer reads them. The index itself comes first. It is the map.

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

It automates the mechanizable check classes — ID continuity (`TODO-NNN` rows are duplicate-free and gap-free; IDs cited in the other governed docs resolve), command-surface consistency (every `checks.commands` entry appears in the docs its `must_appear_in` lists), the `AGENTS.md` line limit, the configurable neutrality / harness-neutrality sweep, and — enabled in this example — the IPv4 / machine-path leak sweeps and the iteration-history numbering check. Lines that must show a bad example are exempted with a trailing `agentic-gate: allow` marker. What it does not mechanize stays with review, and `agentic-mode/SELF-TEST.md` §A names each item: the `^[A-Z]{2,6}-[0-9]{3,}$` ID format itself, README ↔ surface parity beyond the configured commands, and commit/MR/PR reference hygiene. The placeholder sweep runs by hand whenever these docs are generated or upgraded. The checker never looks for a leftover placeholder.

CI platform: **github**. When not `none`, the gate above runs on every change.

## Canonical Questions — Answerable Cold From the Docs Alone

These are the questions a **zero-context reviewer** (never seen this repo, no chat history) must be able to answer from the committed docs alone. Keep them **here** and maintain them as the docs change. `agentic-mode/SELF-TEST.md` §D consumes this list for the read-back probe; it does not carry a second copy.

1. What does `todo` do, and how do I add my first task?
2. What am I allowed and not allowed to do in this repo, and when must I stop and ask?
3. What is the behavior contract for the store path, and which `TODO-XXX` governs it?
4. What is the observable surface for `list` (the command and its `--all` flag)?
5. How do I prove a change to `done` is complete, and how do I move it through review?

## Routing

- **Doctrine** (why the layers exist, ID discipline, append-only rules, adoption profiles) → the toolkit's `doctrine/BOOTSTRAP-CORE.md`, at the root of the repository that contains this example. This repo keeps no copy.
- **Machine config** (paths, prefix, checks, and the `null`s that record which layers are deferred) → `agentic-mode/config.json`.
- **Full cross-layer self-test** (all rows, manual + automated, guardrails, read-back probe protocol) → `agentic-mode/SELF-TEST.md`; the questions it asks live in the Canonical Questions section above.
