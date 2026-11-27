<!--
TEMPLATE: AGENTIC-MODE.md — resident root index for the target repo.
Filled from config.json: project.name, project.type, id.prefix, docs.*, ci.platform,
bilingual.enabled, and the surface row's `{{SURFACE_DOC_ROLE}}`. `{{SURFACE_DOC_ROLE}}` is
`commands, flags, and output` for a CLI, `endpoints and screens` for a web service, or
`endpoints` for one with no screens, `the public API` for a library (RUNBOOK Phase B, step 4).
`{{TOOLKIT_LOCATION}}` is where a reader opens the toolkit's doctrine.
RUNBOOK Phase A sets it.
The project-neutral sentence in the Project line stays at every target, because it
states the rule. A target with no runtime placeholders drops the words from
`replace any placeholder` up to and including the semicolon. That leaves
`It is project-neutral — do not hardcode brand/host/serial tokens.`
Rows and cells that name an optional doc sit inside `{{IF ...}}` regions,
resolved per BOOTSTRAP-CORE, "Conditional Text in Templates". This file is META and RESIDENT:
it is meant to be read every session. Keep it short — it routes; it is not the content.
The Canonical Questions section is seeded here (one list, one home) — SELF-TEST §D
consumes it for the zero-context read-back probe. The five Canonical Questions below are the seed,
drawn from the doctrine's Layered Reading Order (BOOTSTRAP-CORE). Resolve their placeholders.
Keep between three and seven questions.
Render body prose in the TARGET's primary language; keep the section headings in
canonical English (they are cross-repo reference anchors — doctrine and upgrades
cite them by name).
A target with no entry point makes four substitutions. In the Doc Inventory, the README row's
`which entry point to pick` reads `which page to pick`. In the Canonical Questions, question 1's
`which entry point do I pick` reads `which page do I pick`, and question 4's
`(the command / key / endpoint / API)` reads `(the page and heading)`. In the Source-of-Truth
Precedence table, `What should users type, press, see, or call?` reads `Which page answers a
reader's question?`.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Template-Source: agentic-bootstrap/AGENTIC-MODE@v5  (@v4: the inventory lists the layers in reading
order, architecture third, and a short paragraph under it says so; the Enforcement paragraph
routes each non-mechanized check to where it lives instead of to SELF-TEST §B, and ends with two
sentences on the placeholder sweep; the Canonical Questions carry no seeding instruction and no
question count; the doctrine pointers say this repo keeps no copy and take the toolkit's
location; the requirements row allows for no event model; the process-rules row no longer names
the H1 as a substitution point; commands run `python3`; the header says which words a target
without runtime placeholders drops.
@v5: the behavior-contract stand-in also allows a page in place of a command, and the header names
the four substitutions a target with no entry point makes; the IF branches are unchanged, so a
copy rendered with a surface doc needs no port)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# AGENTIC-MODE.md — Doc Contract for Agent + Human Co-Development

> What this is: the resident index for a **layered, ID-joined, harness-neutral** documentation contract. Any collaborator — human or agent, in any tool, with no chat history — reads top-down from here and reaches productive context in minutes. This file is **meta and resident**: read it every session. It owns *What* (repo facts, behavior contract) and *Done* (acceptance evidence); it never dictates *How/Who* (which tool or model you use). Doctrine lives in the toolkit's `doctrine/BOOTSTRAP-CORE.md`, at {{TOOLKIT_LOCATION}}. This repo keeps no copy of it. The machine config is `agentic-mode/config.json`.

Project: **{{PROJECT_NAME}}** ({{PROJECT_TYPE}}). ID prefix: `{{PREFIX}}`. It is project-neutral — replace any placeholder such as `<package.name>` with your own runtime values; do not hardcode brand/host/serial tokens.

---

## Doc Inventory — One Job Per File

| Layer | Canonical file | Single responsibility |
|---|---|---|
| Onboarding | `{{README_PATH}}` | What is this, which entry point to pick, quick start, neutrality/contracts. |
| Repo facts + co-op contract | `{{AGENTS_PATH}}` | Scope, key files, dev commands, change-flow, the platform-neutral MR / PR policy, sign-off points, Stop-and-Ask list — *What/Done* only. |
{{IF ARCHITECTURE_PATH}}| Architecture inventory | `{{ARCHITECTURE_PATH}}` | Component graph as committed, diffable JSON. |{{END IF}}
| Behavior contract | `{{REQUIREMENTS_PATH}}` | Problem/Goals/Non-Goals, enumerated functional requirements with stable IDs{{IF SURFACE_DOC_PATH}} (each row names the observable surface it governs){{ELSE}}, each row carrying the observable surface and the command or page that carries it{{END IF}}, event/domain model when there is one, append-only iteration history, acceptance criteria, verification commands. |
{{IF SURFACE_DOC_PATH}}| Observable surface | `{{SURFACE_DOC_PATH}}` | {{SURFACE_DOC_ROLE}} — what users see, press, or call. |{{END IF}}
| Done evidence | `{{VALIDATION_PATH}}` | Per-feature checklist: Code Implementation / Integration Points / User Requirements Met / Documentation Updates / Testing / Verification Commands / Status. |
{{IF WORKFLOW_PATH}}| Process rules | `{{WORKFLOW_PATH}}` | Issue → branch → commit → MR/PR → review loop, red lines, platform CLI conventions — copied as-is except its declared substitution points. |{{END IF}}

The table lists the layers in the order a newcomer reads them. The index itself comes first. It is the map.

**Anti-pattern:** a single `NOTES.md` / `DESIGN.md` mixing contract, guide, status, and process. It rots because no one knows which section is authoritative. <!-- agentic-gate: allow -->

## Source-of-Truth Precedence When Docs Conflict

Resolve by responsibility, not by recency.

| Question | Winning layer |
|---|---|
| What is allowed during git / issue / MR/PR operations? | {{IF WORKFLOW_PATH}}`{{WORKFLOW_PATH}}`{{ELSE}}`{{AGENTS_PATH}}`, its **MR / PR Governance** and **Git Hygiene** sections. No WORKFLOW doc is seeded{{END IF}} |
| What safety and repo-scope rules bind collaborators? | `{{AGENTS_PATH}}` |
| What is the required behavior? | `{{REQUIREMENTS_PATH}}` |
| What should users type, press, see, or call? | {{IF SURFACE_DOC_PATH}}`{{SURFACE_DOC_PATH}}`{{ELSE}}`{{REQUIREMENTS_PATH}}`, its requirement rows. No surface doc is seeded{{END IF}} |
| What proved a feature was completed? | `{{VALIDATION_PATH}}` |
| What components exist and how do they connect? | {{IF ARCHITECTURE_PATH}}`{{ARCHITECTURE_PATH}}`{{ELSE}}`{{README_PATH}}` Main Components / Data Flow and `{{AGENTS_PATH}}` Key Files. No architecture doc is seeded{{END IF}} |
| What should a newcomer read first? | `{{README_PATH}}` |

README is the onboarding map, not the final authority for behavior or workflow. VALIDATION records done evidence, not new requirements. Iteration history explains why a decision changed; the current functional-requirement table states the live contract.

## Enforcement

The mechanical parts of the self-test are executable. Run the repo-local gate:

```bash
python3 scripts/check_agentic_docs.py --config agentic-mode/config.json
```

It automates the mechanizable check classes — ID continuity (`{{PREFIX}}-NNN` rows are duplicate-free and gap-free; IDs cited in the other governed docs resolve), command-surface consistency (every `checks.commands` entry appears in the docs its `must_appear_in` lists), the `{{AGENTS_PATH}}` line limit, and the configurable neutrality / harness-neutrality sweep. Lines that must show a bad example are exempted with a trailing `agentic-gate: allow` marker. What it does not mechanize stays with review, and `agentic-mode/SELF-TEST.md` §A names each item: the `^[A-Z]{2,6}-[0-9]{3,}$` ID format itself, README ↔ surface parity beyond the configured commands, and commit/MR/PR reference hygiene. The placeholder sweep runs by hand whenever these docs are generated or upgraded. The checker never looks for a leftover placeholder.

CI platform: **{{CI_PLATFORM}}**. When not `none`, the gate above runs on every change.

## Canonical Questions — Answerable Cold From the Docs Alone

These are the questions a **zero-context reviewer** (never seen this repo, no chat history) must be able to answer from the committed docs alone. Keep them **here** and maintain them as the docs change. `agentic-mode/SELF-TEST.md` §D consumes this list for the read-back probe; it does not carry a second copy.

1. What does this project do, and which entry point do I pick for {{PRIMARY_USE_CASE}}?
2. What am I allowed and not allowed to do in this repo, and when must I stop and ask?
3. What is the behavior contract for {{KEY_BEHAVIOR}}, and which `{{PREFIX}}-XXX` ID governs it?
4. What is the observable surface for {{KEY_BEHAVIOR}} (the command / key / endpoint / API)?
5. How do I prove a change to {{KEY_BEHAVIOR}} is done, and how do I move it through review?

## Routing

- **Doctrine** (why the layers exist, ID discipline, append-only rules, adoption profiles) → the toolkit's `doctrine/BOOTSTRAP-CORE.md`, at {{TOOLKIT_LOCATION}}. This repo keeps no copy.
- **Machine config** (paths, prefix, checks, and the `null`s that record which layers are deferred) → `agentic-mode/config.json`.
- **Full cross-layer self-test** (all rows, manual + automated, guardrails, read-back probe protocol) → `agentic-mode/SELF-TEST.md`; the questions it asks live in the Canonical Questions section above.
