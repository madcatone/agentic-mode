# BOOTSTRAP-CORE.md — Doctrine for the Agentic Doc System

> Load this when standing up the doc system in a new repo, or when you need the doctrine behind the resident `AGENTIC-MODE.md`. It carries the core doctrine (why the layers exist), the ID discipline, the append-only rules, the anti-patterns, the controlled-duplication and precedence policies, the two-layer division of labor, and the adoption profiles. The step-by-step bootstrap procedure and the ten interview questions live in `RUNBOOK.md`; the fill-in skeletons live in `templates/`; the cross-layer coherence check ships as `templates/SELF-TEST.template.md`.

This document is **harness-neutral**. It never names a specific agent product, model, or tool. It is written to the weakest common primitive shared by every collaborator — human or agent: *read a file, run a command, open a merge/pull request.* Wherever it says "any agent or human collaborator," it means exactly that.

---

## Core Idea

Three principles make a repo legible to a cold reader — human or agent — with no chat history:

1. **Layered, non-overlapping docs.** Each doc has exactly one job. Don't duplicate the same fact in two files — pick the canonical home and cross-link.
2. **Stable IDs for every behavior.** Requirements carry IDs (`{{PREFIX}}-001`). User-guide sections, validation checklists, commit messages, and merge/pull-request notes cite those IDs. Any reader can jump across docs by ID. The ID is also the **bootstrap join key**: it is what lets README ↔ REQUIREMENTS ↔ USER_GUIDE/API_REFERENCE ↔ VALIDATION ↔ commit/MR stay in sync during both initial production and ongoing self-operation. Treat ID-integrity (SELF-TEST §1) as a release gate, not a nicety.
3. **Append-only provenance + per-feature done evidence.** Iteration history records *why* a change landed (never rewritten). Validation checklists record *that it was actually done* and how to re-verify.

When all three hold, a new collaborator can bootstrap understanding top-down, and a reviewer can audit any claim by following the ID trail.

---

## The Two-Layer Division of Labor — What This Contract Owns, and What It Does Not

This is the most important boundary in the whole system. Draw it wrong and the docs either go stale or start dictating things they have no authority over.

**This documentation contract owns *What* and *Done*:**

- *What* — the repo's facts: what it does, what the behavior contract is (requirement IDs), what commands exist, what the observable surface is, what the architecture is.
- *Done* — the acceptance evidence: what proves a feature was actually completed, how to re-verify it, what the release gates are.

**The executor owns *How* and *Who*:**

- *How* — the mechanics of getting work done: how to dispatch sub-tasks, which model or tool to use, how to parallelize, how to budget effort, how to route between a planner and an implementer.
- *Who* — which collaborator (which human, which agent, which harness) does the work.

The contract states *what must be true and how completion is proven*; it never states *how you personally should organize your work or which tools you should reach for*. Those belong to whatever environment the collaborator operates in — their own agent harness, their own IDE, their own team process.

**Why the split matters.** If this contract tried to encode *How/Who* — "dispatch a search agent," "use model X for review," "run these in parallel" — it would (a) bind the repo to one harness and rot the moment that harness changed, and (b) leak assumptions no cold reader can satisfy. By owning only *What/Done*, the contract stays portable across every collaborator and every tool generation. A human with an editor, an agent in harness A, and an agent in harness B all read the same *What/Done* and each apply their own *How/Who*.

**Boundary test.** If a candidate rule tells the reader *which tool to use, which model to pick, how to split up their own labor, or how to talk to a background process*, it is *How/Who* — it does **not** belong in these docs. Push it back to the executor's environment. If a candidate rule states *a repo fact, a required behavior, an acceptance gate, or a stop-and-ask boundary*, it is *What/Done* — it belongs here.

---

## Layered Reading Order — How a Cold Reader Bootstraps

A cold-start collaborator reads in this order; each layer answers a different question:

1. `README.md` → *What does this project do, and which entry point / tool do I pick?*
2. `AGENTS.md` → *What am I allowed to do in this repo, where are the key files, and what is the co-operation contract?*
3. `docs/architecture.json` → *What components exist, and how does data flow between them?* (Optional; readable without rendering when present.)
4. `docs/REQUIREMENTS.md` → *What is the contract for each behavior, and why was each decision made?*
5. `docs/USER_GUIDE.md` **or** `docs/API_REFERENCE.md` → *What is the observable surface of those same behaviors?* (Which of the two depends on `project.type` — see below.)
6. `docs/VALIDATION.md` → *For each landed feature, what was touched and how do I re-verify it?*
7. `docs/WORKFLOW.md` → *How do I move a change through review safely?*

If any layer is missing, the reader fills the gap with assumptions or chat history — both of which decay. The layers exist so chat history is never load-bearing.

**Observable-surface selection by project type.** The observable-surface doc is chosen from `project.type` in `agentic-mode/config.json`:

| `project.type` | Observable-surface doc | Template |
|---|---|---|
| `cli` | `docs/USER_GUIDE.md` | `USER_GUIDE-cli.template.md` |
| `library` | `docs/API_REFERENCE.md` | `API_REFERENCE-library.template.md` |
| `web-service` | `docs/USER_GUIDE.md` | `USER_GUIDE-web.template.md` |
| `docs-only` | (none; REQUIREMENTS carries the surface) | — |

---

## The ID Discipline

This is the single highest-leverage convention.

- **Stable requirement IDs.** Every functional requirement gets `{{PREFIX}}-001`, `{{PREFIX}}-002`, … Never renumber. New behavior appends the next ID; superseded requirements are marked, not deleted.
- **IDs are cited everywhere.** User-guide / API-reference sections cite `{{PREFIX}}-029` next to the behavior they describe. Validation checklists list `Requirements Met: {{PREFIX}}-058 ✓`. Commit messages and MR/PR notes reference IDs instead of prose ("implements {{PREFIX}}-061" beats "adds the export").
- **Iteration history is descriptive, not numeric-cited.** When two language tracks exist, their numbering may be off by one. Cite by description ("the export-format entry") when referencing across languages.
- **ID format.** `{{PREFIX}}-NNN` where PREFIX is uppercase letters, one prefix per component. IDs match `^[A-Z]{2,6}-[0-9]{3,}$`. This removes the ambiguity a reader would otherwise hit between `FOO-001` / `FOO_001` / `FEAT-1`. <!-- agentic-gate: allow -->
- **The ID is the bootstrap join key.** See `RUNBOOK.md` for the production procedure and SELF-TEST §1 for the integrity self-test.

The ID is the join key between contract, surface, evidence, and history. Without it, the four layers drift.

---

## Iteration History — Append-Only Provenance

`docs/REQUIREMENTS.md` ends with a numbered **Iteration History**. Each entry is one landed change: what was decided, why, and what evidence (fingerprint, measurement, issue/MR link).

Rules:

- **Append-only.** Never rewrite or renumber past entries. If a decision is reversed, add a new entry that says so and references the old one.
- **Two language tracks kept in sync (only if bilingual is enabled).** Each track is an independent counter but should agree on count and order. Cite descriptively across languages (see The ID Discipline above).
- **Lead with the decision, then the evidence.** "Peak memory dropped 329 MB → 47 MB, output byte-identical" is useful. "Improved performance" is not.
- **Reference issue/MR numbers when available.** `Closes #3` / `MR !13` / `PR #13` give a clickable trail.

Iteration history is the only place where *why-decisions* accumulate. Without it, every collaborator re-derives the rationale from scratch.

*(Under the `light` co-op profile the append-only ritual is relaxed — see Adoption Profiles. All other profiles treat append-only as a hard rule.)*

---

## Per-Feature Validation Checklist

Every non-trivial landed change gets a block in `docs/VALIDATION.md`. The block is the *evidence layer*: it exists so a reviewer (human or agent) can re-verify any feature by running the commands, and so future readers know which feature touched which surface without grepping the whole diff.

Three rules the block enforces:

1. **Each `User Requirements Met` bullet MUST cite a stable ID** drawn from the REQUIREMENTS table — not prose.
2. **Each feature block header MUST cite its issue or MR/PR number**, matching a `Closes #N` / `MR !N` / `PR #N` marker in Iteration History.
3. **Verification Commands MUST include** (a) a build/compile of touched entry points, (b) a test step, (c) ≥1 smoke run against a fixture or example — sourced from AGENTS.md Development Commands, not reinvented.

The file-level seed lives in `templates/VALIDATION.template.md`.

---

## Architecture-as-Code (Optional, by Project Type)

When present, `docs/architecture.json` is the source of truth; any rendered `.svg`/`.html` is generated. This means:

- The diagram is **diffable** in code review.
- A reader can read component relationships, boundaries, and connections directly from JSON without rendering.
- Updates go through the JSON first; rendering is regenerated, never hand-edited.
- Derive the component list by mining entry points + AGENTS Key Files + README Main Components — do not hand-author.
- **Stability rule.** Append components/connections; do not rename existing ids or reflow position/size unless intentionally restructuring — diffability is the point.

The architecture doc is **optional** and gated on `project.type` and the team's need. A single-entry `cli` or a `docs-only` repo may skip it; a multi-component `web-service` benefits most. When skipped, set `docs.architecture` to `null` in config.

Anti-pattern: a `.png` or `.drawio` committed directly, with no source. It rots the first time someone is too lazy to open the editor. <!-- agentic-gate: allow -->

---

## Process vs. Repo Rules — Keep Them Separate

Two collaborator-facing docs, with different jobs:

- **`AGENTS.md`** (repo root) — *the repo's facts and the co-operation contract*: project scope, key files, development commands, the change-flow / sign-off / stop-and-ask contract. It carries *What/Done* only. Stable; changes rarely.
- **`docs/WORKFLOW.md`** — *how to operate the platform's review loop*: the CLI conventions, comment style, code-review protocol (request/response/LGTM), anti-patterns, red lines for the specific hosting platform.

Keeping them separate avoids one giant rules file that no one re-reads.

**The `WORKFLOW.md` doc is PORTED-AS-IS.** When adopting this mode in a new repo, copy the canonical platform workflow doc verbatim — only substitute the platform name in the H1. Do not re-author its body; its baked-in conventions (comment style, review loop, red lines) are platform constants and out of scope for regeneration.

**Boundary test:** if a candidate AGENTS.md rule names the platform CLI or a platform-specific comment style, it belongs in WORKFLOW, not AGENTS.md.

### Workflow template versioning

Because the platform WORKFLOW doc is copied as-is, every imported copy should record where it came from:

- **Template marker.** Add a short header note such as `Template-Source: <canonical-repo-or-skill>@<version>` near the top of the copied WORKFLOW doc.
- **No local drift.** Local repos should not hand-edit platform constants. If a platform rule changes, update the canonical template first, then replace the copied WORKFLOW body from that version.
- **Review visibility.** Merge/pull requests that update WORKFLOW should state whether they are a template refresh or a local repo-specific exception. Exceptions should be rare and explicitly justified.

This preserves the "copied as-is" rule while still making long-term template drift visible.

---

## Bilingual Discipline (Config-Gated — Optional Section)

**This section applies only when `bilingual.enabled` is `true` in `agentic-mode/config.json`.** If bilingual is disabled, skip this section entirely and keep every doc in one clean language — half-translated docs are worse than one clean language.

When the team works in two languages:

- **Both language tracks are first-class.** Each track has full Problem/Goals/Non-Goals/Requirements/Iteration History under its own `## English` / `## {{SECONDARY_LANGUAGE_HEADER}}` heading. Neither is a translation footnote.
- **Requirement tables stay in lock-step.** Same ID, same count, same order.
- **External replies on the issue/MR platform use the platform's required multi-line comment format, in both languages.** Chat replies are not bound by this.
- **Match the author's language in replies.** A reply matches the language of the issue/MR it answers.

**Detection.** The bootstrap interview (RUNBOOK.md Phase A, the bilingual question) decides this. If yes, both REQUIREMENTS and the observable-surface doc get two full tracks; VALIDATION stays single-language (checklists are bilingual-neutral). If monolingual, drop this section and collapse the templates to one track.

---

## Project-Neutrality Contract

For tools meant to be reused across environments:

- **No hardcoded brand names, product codenames, package names, device serials, IP addresses, or environment-specific hosts** in code, docs, tests, or examples.
- **Use runtime placeholders** (e.g. `<package.name>`, `<device-serial>`) in all docs and examples.
- **Raw fixture lines are the only exception** — when a fixture must preserve original text, the environment-bound tokens stay in the fixture file alone, not in code or docs.

This keeps the repo reusable across projects and prevents accidental leaks into docs that get shared. The specific placeholder set for a repo is chosen at bootstrap (RUNBOOK.md Phase A) and recorded so the neutrality sweep can enforce it. The neutrality sweep is opt-in per repo via `checks.harness_neutrality` and `checks.deny_words` in config.

### Sensitive data and fixture redaction

Project-neutrality is necessary but not sufficient. A repo can be project-neutral and still leak sensitive user, device, or service data.

- **Never commit secrets**: API keys, OAuth tokens, cookies, auth headers, private keys, credentials, signed URLs, internal-only passwords, or `.env` values.
- **Redact personal data** in docs/examples/tests unless the exact raw token is required to reproduce behavior: user names, phone numbers, emails, home/work addresses, precise coordinates, account IDs, device serials, and persistent user identifiers.
- **Raw fixtures are isolated exceptions.** If a fixture must preserve original raw text, keep the sensitive fragment only inside the fixtures directory, make it as small as possible, and document why synthetic data would not reproduce the behavior.
- **Synthetic first.** Prefer neutral synthetic values (`<user-id>`, `<device-serial>`, `example.invalid`) for docs and tests.
- **Generated output is suspect.** Before committing captured logs, exports, screenshots, downloads, or renders, inspect them for secrets and environment-specific data.
- **Review red flag.** Any merge/pull request that adds raw logs or fixtures should explicitly state whether redaction was performed and which sensitive classes were checked.

---

## Controlled-Duplication Policy

The rule is not "never repeat words." The rule is "never let duplicated facts become independent authorities." Some facts must appear in more than one layer because each audience enters through a different door.

| Fact type | Canonical owner | Allowed mirrors | Update rule |
|---|---|---|---|
| Development / verification commands | `AGENTS.md` Development Commands | README Verification, REQUIREMENTS Verification Commands, per-feature VALIDATION blocks | Mirrors copy the current command or explicitly say they are a focused subset. |
| User-visible commands, flags, keys, endpoints, API signatures | `docs/USER_GUIDE.md` or `docs/API_REFERENCE.md` | README Quick Start, REQUIREMENTS requirement rows | Mirrors must be checked by the command-surface parity tests (SELF-TEST §3). |
| Behavior contract and stable IDs | `docs/REQUIREMENTS.md` | USER_GUIDE/API_REFERENCE citations, VALIDATION `Requirements Met`, commits/MRs | Mirrors cite IDs; they do not redefine the requirement. |
| Per-feature completion evidence | `docs/VALIDATION.md` | MR/PR description, issue closure comment | Mirrors may summarize, but the validation block is the re-verification home. |
| Workflow / review commands | `docs/WORKFLOW.md` | AGENTS one-line deferral | Do not duplicate platform-specific steps in AGENTS. |
| Architecture inventory | `docs/architecture.json` | README Main Components, AGENTS Key Files | Prose derives from JSON; JSON remains the diffable source. |

If a mirror disagrees with its canonical owner, update the mirror unless the canonical owner is wrong. If the canonical owner is wrong, fix it first, then refresh every mirror in the same change.

---

## Source-of-Truth Precedence When Docs Conflict

When two layers disagree, resolve by responsibility, not by recency:

| Question | Winning layer |
|---|---|
| What is allowed during git / issue / MR operation? | `docs/WORKFLOW.md` |
| What safety and repo-scope rules bind collaborators? | `AGENTS.md` |
| What is the required behavior? | `docs/REQUIREMENTS.md` |
| What should users type, press, see, or call? | `docs/USER_GUIDE.md` or `docs/API_REFERENCE.md` |
| What proved a feature was completed? | `docs/VALIDATION.md` |
| What components exist and how do they connect? | `docs/architecture.json` |
| What should a newcomer read first? | `README.md` |

README is the onboarding map, not the final authority for behavior or workflow. VALIDATION records done evidence, not new requirements. Iteration history explains why a decision changed, but the current functional requirement table states the live contract.

---

## Anti-Patterns to Reject

| Anti-pattern | Cost | Do instead |
|---|---|---|
| One giant `NOTES.md` mixing contract + guide + status + process | Rots; no canonical home | Split by layer (see Doc Inventory in resident AGENTIC-MODE.md). |
| Requirements without stable IDs | Cannot cross-link; drift | `{{PREFIX}}-XXX` enumeration (The ID Discipline). |
| Renumbering or rewriting iteration history | Lost provenance | Append-only (Iteration History). |
| "Improved performance" without measurement | Unverifiable claim | Lead with numbers, fingerprints, repro cases (Iteration History, Per-Feature Validation). |
| Committed image diagram with no source | Diagram rots | JSON source of truth + rendered output (Architecture-as-Code). |
| Half-translated docs | Worse than monolingual | Either two full tracks or one clean language (Bilingual Discipline). |
| Behavior change landed without docs sync | Hidden context; future reader re-derives | Update contract + guide + validation in the same change (Per-Feature Validation). |
| Hardcoded package/serial/host in code or docs | Locks repo to one env; leak risk | Runtime placeholders (Project-Neutrality Contract). |
| Chat-context references in commit messages or MR descriptions | Unreadable to anyone cold | Self-contained prose; cite IDs and SHA, not conversation. |
| Encoding *How/Who* (tool choice, dispatch, model) into these docs | Binds repo to one harness; rots | Keep it in the executor's environment (Two-Layer Division of Labor). |
<!-- agentic-gate: allow -->

---

## Mental Model — One Sentence

> Docs are a **layered, ID-joined, append-only pipeline** owning *What* and *Done*; each layer answers a different question, stable IDs let any collaborator jump across them without reading chat history, and *How/Who* stays with whoever does the work.

---

## Adoption Profiles

Not every repo can adopt the full system on day one, and not every team wants the same rigor. Two orthogonal knobs control this: the **co-op profile** (how much collaboration ritual) and the **doc-set profile** (how many layers).

### Co-op profile (chosen at bootstrap — RUNBOOK.md Phase A, question 1)

| Co-op profile | CI gate | Append-only ritual | Use when |
|---|---|---|---|
| `full` | Yes — `ci.platform` set, gate runs on every change | Enforced | Default. Repo expected to live beyond one feature cycle, multiple collaborators. |
| `docs-only` | **No CI gate** — the checker is still runnable by hand, but no pipeline enforces it | Enforced | Docs/knowledge repos, or teams not ready to wire CI. The contract is honored manually. |
| `light` | Optional | **Relaxed** — iteration history and per-feature VALIDATION blocks are encouraged, not required | Small, low-churn repos, prototypes, solo work where full provenance is overhead. |

The co-op profile sets `ci.platform` (to `none` for `docs-only`/`light` if desired) and signals to collaborators how strictly the append-only rules bind.

### Doc-set profile (how many layers to seed initially)

| Doc-set profile | Include | Use when | Upgrade trigger |
|---|---|---|---|
| Lite | `README.md`, `AGENTS.md`, `docs/REQUIREMENTS.md`, seeded `docs/VALIDATION.md` | Small single-entry tool, low surface, no established MR workflow yet | First visible behavior change or second collaborator. |
| Standard | Lite + observable-surface doc (`USER_GUIDE`/`API_REFERENCE`) + `docs/WORKFLOW.md` | Active feature work with issue/MR review | Repeated architecture questions or cross-component changes. |
| Full | Standard + `docs/architecture.json` + full SELF-TEST automation in CI | Multi-component repo, multiple collaborators, protected branches | Default for repos expected to live beyond one feature cycle. |

A profile is a starting point, not a fork of the rules. The target architecture remains the Full model; Lite and Standard simply defer lower-risk layers until the repo needs them.

When the seeded layers exist AND SELF-TEST passes, any new collaborator (human or agent) can read top-down per the Layered Reading Order and reach productive context in minutes, with no chat history required.
