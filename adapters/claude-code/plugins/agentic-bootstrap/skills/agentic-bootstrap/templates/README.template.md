<!--
TEMPLATE: README.md — onboarding map for the target repo.
Filled from config.json (project.*, id.prefix, docs.*, checks.commands, checks.entrypoints)
and Phase-A answers (purpose/audience, entry points, quick start, neutrality placeholders).
Architecture Overview is DERIVED from the architecture doc when one is seeded — do not hand-maintain it.
README is the onboarding map, NOT the final authority for behavior (REQUIREMENTS) or workflow.
Workflow authority is the WORKFLOW doc when one is seeded and the AGENTS co-op contract otherwise.
The entry table's second row is a sample. Write one row per entry point and delete the samples. The
no-value rule does not apply to a sample.
A placeholder that describes something the target does not have follows the RUNBOOK's Phase-B rule
for a placeholder with no value. `{{SUPPORT_MODULE_1}}` and `{{TESTS_DIR}}` each own a line.
`{{TESTS_DIR}}` is the path of the tests, a directory or a single file. When the target needs no
runtime placeholders, delete the sentence that says to provide them and the checklist bullet that
lists them.
Main Components: `{{SYMBOL_n}}` is one bullet per public function, class, or module of that entry
point. Leave out a name that starts with an underscore unless a requirement row cites it.
`{{SECONDARY_USE_CASE_TITLE_OR_DELETE}}`: a second quick start the target has. When there is none,
delete the heading and its code block. It is not the secondary entry point of Phase A question 6.
`{{REGION_LIST_FROM_JSON}}`: with no regions in the architecture doc,
write `none`.
Data Flow: one numbered step per stage, from what enters to what leaves. The two lines are samples.
A target with no entry point (RUNBOOK Phase A, question 6) lists pages. `{{ENTRY_n}}` is a page a
reader enters by, `{{WANT_n}}` is what a reader finds there, and each `{{INSTALL_n_OR_NONE}}` is
`none`. `{{SYMBOL_n}}` is a heading of that page. `{{SUPPORT_MODULE_1}}` is one more such page.
Write one line, and one `###` section under Main Components, per page a reader enters by.
The `## Pick a Tool / Entry Point` heading stays as written, because a heading is a cross-repo
reference anchor. Its rows list the pages.
In Quick Start each command and its fence become one line,
``Read `<page>#<heading>` for <what the reader needs>.``
The use-case headings stay as the sample and no-value rules leave them.
`Data Flow` lists the reading path, one step per line. `Before editing core logic` reads
`Before editing a page`, and `Edit the code.` reads `Edit the page.`
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Resolve `{{IF ...}}` regions per BOOTSTRAP-CORE, "Conditional Text in Templates".
The CI-runners stand-in under Verification is kept only while no WORKFLOW doc is seeded.
`{{CI_RUNNERS}}`: resolve from config `ci.runners` (comma-separated runner names); when config
declares no runners, DELETE that whole line. The doc gate checks the `ci-runners:` marker
against config.
Template-Source: agentic-bootstrap/README@v3  (@v2: Data Flow is two sample lines, the two component
bullets name their own job slot, and the header states the no-value rule and the sample rule for
this template's slots; the verification sentence no longer says "above";
commands run `python3`.
@v3: a target with no entry point lists pages in place of entry points and reading lines in place of
Quick Start commands, as the header says; every other target renders no change)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# {{PROJECT_NAME}}

{{ONE_LINE_PURPOSE}}. {{AUDIENCE_SCOPE}}.

**Requirements:** {{RUNTIME_PREREQS — e.g. language/runtime versions, or "none beyond the standard toolchain"}}.

{{INSTALL_OR_STDLIB_NOTE}}

## Pick a Tool / Entry Point

| Want | Use | Install |
| --- | --- | --- |
| {{WANT_1}} | `{{ENTRY_1}}` | {{INSTALL_1_OR_NONE}} |
| {{WANT_2}} | `{{ENTRY_2}}` | {{INSTALL_2_OR_NONE}} |

## What This Repository Contains

- `{{ENTRY_1}}`: {{ONE_LINE_COMPONENT_JOB}}.
- `{{SUPPORT_MODULE_1}}`: {{ONE_LINE_SUPPORT_JOB}}.
- `{{TESTS_DIR}}`: {{TEST_SCOPE}}.
- `docs/`: {{DOCS_SCOPE}}.

This repository is project-neutral: no hardcoded {{FORBIDDEN_TOKEN_CLASSES}}. Provide {{RUNTIME_PLACEHOLDERS}} at runtime.

## Quick Start

### {{PRIMARY_USE_CASE_TITLE}}

```bash
{{PRIMARY_QUICK_START_COMMAND}}
```

### {{SECONDARY_USE_CASE_TITLE_OR_DELETE}}

```bash
{{SECONDARY_QUICK_START_COMMAND}}
```

## Platform-Specific Notes

{{PER_PLATFORM_DEP_OR_NOTE_OR_DELETE}}

{{IF ARCHITECTURE_PATH}}
## Architecture Overview

Diagram: `{{ARCHITECTURE_PATH}}` (source of truth; any `.svg`/`.html` is rendered). Components: {{COMPONENT_LIST_FROM_JSON}}. Boundaries: {{REGION_LIST_FROM_JSON}}. Do not hand-maintain — derive from the JSON.
{{END IF}}

## Data Flow

1. {{first step: what enters, from where}}.
2. {{next step}}.

## Main Components

### `{{ENTRY_1}}`
- `{{SYMBOL_1}}`: {{JOB_OF_SYMBOL_1}}.
- `{{SYMBOL_2}}`: {{JOB_OF_SYMBOL_2}}.

## Agent Onboarding Guide

A cold-start collaborator (human or agent, no chat history) reads in this order: this README → `{{AGENTS_PATH}}`{{IF ARCHITECTURE_PATH}} → `{{ARCHITECTURE_PATH}}`{{END IF}} → `{{REQUIREMENTS_PATH}}`{{IF SURFACE_DOC_PATH}} → `{{SURFACE_DOC_PATH}}`{{END IF}} → `{{VALIDATION_PATH}}`{{IF WORKFLOW_PATH}} → `{{WORKFLOW_PATH}}`{{END IF}}.

Before editing core logic, answer: {{QUESTIONS_BEFORE_EDITING}}.

Safe-change pattern:
1. Edit the code.
2. Update the requirement ID and its iteration history.
3. {{IF SURFACE_DOC_PATH}}Update the surface doc.{{ELSE}}Update the observable surface in that requirement row.{{END IF}}
4. Append a validation block.
5. Run the docs gate.

## Verification

```bash
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
# Docs coherence gate (ID continuity, command-surface consistency, neutrality)
python3 scripts/check_agentic_docs.py --config agentic-mode/config.json
```

Every command in `checks.commands` (config.json) that lists `"readme"` in `must_appear_in` MUST appear verbatim in this file.

{{IF WORKFLOW_PATH}}{{ELSE}}CI runners executing this repo's pipelines: {{CI_RUNNERS}} <!-- ci-runners: {{CI_RUNNERS}} -->{{END IF}}

## Project-Neutrality Checklist

- No brand names / codenames / hardcoded packages / serials / IPs / environment hosts in code, docs, tests, or examples.
- Runtime placeholders used in all docs/examples: {{RUNTIME_PLACEHOLDERS}}.
- {{EXTRA_NEUTRALITY_BULLET_OR_DELETE}}.

## Doc Cross-Links

- Behavior contract: `{{REQUIREMENTS_PATH}}`
{{IF SURFACE_DOC_PATH}}- Observable surface: `{{SURFACE_DOC_PATH}}`{{ELSE}}- Observable surface: the requirement rows in `{{REQUIREMENTS_PATH}}`{{END IF}}
- Validation: `{{VALIDATION_PATH}}`
{{IF WORKFLOW_PATH}}- Workflow: `{{WORKFLOW_PATH}}`{{ELSE}}- Review policy: **MR / PR Governance** in `{{AGENTS_PATH}}`{{END IF}}
- Resident index: `{{INDEX_PATH}}`
