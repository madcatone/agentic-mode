<!--
TEMPLATE: docs/REQUIREMENTS.md — the behavior contract (source of truth for What).
Filled from config.json (project.name, id.prefix, bilingual.*) and Phase-A answers
(problem/goals/non-goals, one requirement per observable behavior mined from entry points/tests,
verification commands from AGENTS Development Commands).

ID DISCIPLINE (highest-leverage rule):
- Every functional requirement gets {{PREFIX}}-001, {{PREFIX}}-002, ... NEVER renumber.
- New behavior APPENDS the next ID; superseded requirements are MARKED, not deleted.
- IDs match ^[A-Z]{2,6}-[0-9]{3,}$. One prefix per component.
- The ID is cited in the surface doc, VALIDATION, commits, and MR/PR notes — it is the join key.

ITERATION HISTORY is APPEND-ONLY: never rewrite/renumber a past entry; a reversal APPENDS a new
entry referencing the old one. Lead with the decision, then the evidence.

BILINGUAL: keep the second-language track ONLY IF config bilingual.enabled == true. If enabled,
both tracks share identical ID set / count / order. If disabled, DELETE the second track entirely.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
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
| ID | Requirement |
| --- | --- |
| {{PREFIX}}-001 | The {{component}} shall {{testable behavior statement — no "fast/better/improved"}}. |
| {{PREFIX}}-002 | {{next behavior}}. |

<!-- One row per observable behavior (each CLI flag / key / endpoint / public API / documented output).
     Superseded rows stay, marked e.g. "(superseded by {{PREFIX}}-0NN)" — never deleted. -->

### {{Domain / Timeline}} Event Model
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
