<!--
TEMPLATE: docs/REQUIREMENTS.md — the behavior contract (source of truth for What).
Filled from config.json (project.name, id.prefix, bilingual.*) and Phase-A answers
(problem/goals/non-goals, one requirement per observable behavior mined from entry points/tests,
or, for a target with no entry point, one per commitment mined from its pages,
the verification commands, the same ones AGENTS Development Commands lists in Phase B, step 6).

ID DISCIPLINE (highest-leverage rule):
- Every functional requirement gets {{PREFIX}}-001, {{PREFIX}}-002, ... NEVER renumber.
- New behavior APPENDS the next ID; superseded requirements are MARKED, not deleted.
- IDs match ^[A-Z]{2,6}-[0-9]{3,}$. One prefix per component.
- The ID is cited wherever the observable surface is documented, and in VALIDATION, commits, and MR/PR notes — it is the join key.
- With a surface doc, the surface doc carries the exercising command; a row names the surface element it governs and may keep the command as a mirror. Without one, each row IS the surface: state the behavior, then, in a code span, the exact command / call that exercises it and what the user observes. A README quick-start command appears verbatim in the row it exercises. For a target with no entry point the code span is the page's path, then `#` and the heading, as the page writes it, when the page carries several rows, where the reader meets the commitment. A commitment above a page's title heading names the page alone. Such a target also deletes `Current User Flows`, its heading and its fence. `` `{{PRIMARY_ENTRY}}` builds/compiles `` then reads `The static sanity command exits 0.`. `{{observable offline smoke check}} produces expected output.` then reads `The docs gate command exits 0.` With no tests it deletes `{{test_suite}} passes` too. `Documentation updated when commands/keys/output/event behavior change` then reads `Contract docs updated when a page's commitment changes`.

ITERATION HISTORY is APPEND-ONLY: never rewrite/renumber a past entry; a reversal APPENDS a new
entry referencing the old one. Lead with the decision, then the evidence.
The two Iteration History entries are samples. The history starts empty.

BILINGUAL: keep the second-language track ONLY IF config bilingual.enabled == true. If enabled,
both tracks share identical ID set / count / order. If disabled, DELETE the second track entirely.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Resolve `{{IF ...}}` regions per BOOTSTRAP-CORE, "Conditional Text in Templates".
Template-Source: agentic-bootstrap/REQUIREMENTS@v3  (@v2: the Event Model heading is one
descriptive slot; the two Iteration History entries are samples and the history starts empty;
the superseded-row note shows a three-digit ID; the rule that superseded rows stay is a
rendered sentence.
@v3: the no-surface stand-in also allows a page in place of a command, and the header states
what a target with no entry point does; the IF branches are unchanged, so a copy rendered
with a surface doc needs no port)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# {{COMPONENT_NAME}} — Requirements and Evolution

## English

### Problem
{{1-3 sentences: what pain exists without this component; what existing tool it complements and does not replace.}}

### Goals
- {{goal_1}}
- {{goal_n}}

### Non-Goals
- {{explicit_non_goal_1}}
- {{explicit_non_goal_n}}

### Current User Flows
```bash
{{canonical_invocation_1}}
{{canonical_invocation_n}}
```

### Functional Requirements

{{IF SURFACE_DOC_PATH}}Each row states one behavior. Its observable surface is documented in `{{SURFACE_DOC_PATH}}`, which cites the row's ID.{{ELSE}}No surface doc is seeded, so each row is the surface: state the behavior, then, in a code span, the exact command or call that exercises it, or the page and heading that carry it, and what the user observes.{{END IF}}

| ID | Requirement |
| --- | --- |
| {{PREFIX}}-001 | The {{component}} shall {{testable behavior statement — no "fast/better/improved"}}. |
| {{PREFIX}}-002 | {{next behavior}}. |

Rows are never deleted. A superseded row stays, marked for example as "(superseded by {{PREFIX}}-NNN)".

<!-- Repeat one row per observable behavior: each CLI flag, key, endpoint, public API, or documented output. -->

### {{event model heading: the domain or timeline name}}
{{If the component has an in-memory model or event ordering, describe the canonical flow here as a fenced text diagram. Otherwise delete this section.}}

### Iteration History
<!-- APPEND-ONLY. Newest entry has the highest number. Never edit a past entry. -->
1. {{decision lead, then evidence: measurement / fingerprint / issue or MR/PR link}}.
2. {{append-only; never renumber}}.

### Acceptance Criteria
- `{{PRIMARY_ENTRY}}` builds/compiles.
- {{test_suite}} passes.
- {{observable offline smoke check}} produces expected output.
- Documentation updated when commands/keys/output/event behavior change.
- {{if bilingual: recent changes reflected in both language tracks — else delete}}.

### Verification Commands
```bash
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
```

<!-- ==== SECOND LANGUAGE TRACK — keep ONLY if config bilingual.enabled == true; else delete from here down ==== -->
## {{SECONDARY_LANGUAGE_HEADER}}
{{Mirror every section above with IDENTICAL requirement IDs in IDENTICAL order. Requirement count and order MUST match the English track. Cite across languages by description, not by raw number.}}
