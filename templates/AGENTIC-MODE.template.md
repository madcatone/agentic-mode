<!--
TEMPLATE: AGENTIC-MODE.md — resident root index for the target repo.
Filled from config.json: project.name, project.type, id.prefix, docs.*, ci.platform,
bilingual.enabled. The Doc Inventory rows are pruned to the layers this repo actually
seeded (doc-set profile). This file is META and RESIDENT: it is meant to be read every
session. Keep it short — it routes; it is not the content.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
-->

# AGENTIC-MODE.md — Doc Contract for Agent + Human Co-Development

> What this is: the resident index for a **layered, ID-joined, harness-neutral** documentation contract. Any collaborator — human or agent, in any tool, with no chat history — reads top-down from here and reaches productive context in minutes. This file is **meta and resident**: read it every session. It owns *What* (repo facts, behavior contract) and *Done* (acceptance evidence); it never dictates *How/Who* (which tool or model you use). Doctrine lives in the agentic-mode canonical repo's `doctrine/BOOTSTRAP-CORE.md`; the machine config is `agentic-mode/config.json`.

Project: **{{PROJECT_NAME}}** ({{PROJECT_TYPE}}). ID prefix: `{{PREFIX}}`. It is project-neutral — replace any placeholder such as `<package.name>` with your own runtime values; do not hardcode brand/host/serial tokens.

---

## Doc Inventory — One Job Per File

| Layer | Canonical file | Single responsibility |
|---|---|---|
| Onboarding | `{{README_PATH}}` | What is this, which entry point to pick, quick start, neutrality/contracts. |
| Repo facts + co-op contract | `{{AGENTS_PATH}}` | Scope, key files, dev commands, change-flow, sign-off points, Stop-and-Ask list — *What/Done* only. |
| Behavior contract | `{{REQUIREMENTS_PATH}}` | Problem/Goals/Non-Goals, enumerated functional requirements with stable IDs, event/domain model, append-only iteration history, acceptance criteria, verification commands. |
| Observable surface | `{{SURFACE_DOC_PATH}}` | {{SURFACE_DOC_ROLE}} — what users see, press, or call. |
| Done evidence | `{{VALIDATION_PATH}}` | Per-feature checklist: Code Implementation / Integration Points / User Requirements Met / Documentation Updates / Testing / Verification Commands / Status. |
| Process rules | `{{WORKFLOW_PATH}}` | Issue → branch → commit → MR/PR → review loop, red lines, platform CLI conventions — copied as-is except the H1 and `Template-Source` line. |
| Visual architecture (optional) | `{{ARCHITECTURE_PATH_OR_NA}}` | Component graph as committed, diffable JSON. |

**Anti-pattern:** a single `NOTES.md` / `DESIGN.md` mixing contract, guide, status, and process. It rots because no one knows which section is authoritative. <!-- agentic-gate: allow -->

## Source-of-Truth Precedence When Docs Conflict

Resolve by responsibility, not by recency.

| Question | Winning layer |
|---|---|
| What is allowed during git / issue / MR/PR operations? | `{{WORKFLOW_PATH}}` |
| What safety and repo-scope rules bind collaborators? | `{{AGENTS_PATH}}` |
| What is the required behavior? | `{{REQUIREMENTS_PATH}}` |
| What should users type, press, see, or call? | `{{SURFACE_DOC_PATH}}` |
| What proved a feature was completed? | `{{VALIDATION_PATH}}` |
| What components exist and how do they connect? | `{{ARCHITECTURE_PATH_OR_NA}}` |
| What should a newcomer read first? | `{{README_PATH}}` |

README is the onboarding map, not the final authority for behavior or workflow. VALIDATION records done evidence, not new requirements. Iteration history explains why a decision changed; the current functional-requirement table states the live contract.

## Enforcement

The mechanical parts of the self-test are executable. Run the repo-local gate:

```bash
python scripts/check_agentic_docs.py --config agentic-mode/config.json
```

It automates the mechanizable check classes — ID continuity (`{{PREFIX}}-NNN` resolves and is cited; format `^[A-Z]{2,6}-[0-9]{3,}$`), command-surface consistency (README ↔ surface doc; no unfilled `<command>` / `{{PLACEHOLDER}}` in any verification block), the `{{AGENTS_PATH}}` line limit, and the configurable neutrality / harness-neutrality sweep. Lines that must show a bad example are exempted with a trailing `agentic-gate: allow` marker. Everything the script cannot mechanize stays a manual review in `agentic-mode/SELF-TEST.md`.

CI platform: **{{CI_PLATFORM}}**. When not `none`, the gate above runs on every change.

## Routing

- **Doctrine** (why the layers exist, ID discipline, append-only rules, adoption profiles) → the agentic-mode canonical repo's `doctrine/BOOTSTRAP-CORE.md`.
- **Machine config** (paths, prefix, checks, profiles) → `agentic-mode/config.json`.
- **Full cross-layer self-test** (all rows, manual + automated, guardrails, read-back probe) → `agentic-mode/SELF-TEST.md`.
