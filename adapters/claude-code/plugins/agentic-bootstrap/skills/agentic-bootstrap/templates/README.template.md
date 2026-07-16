<!--
TEMPLATE: README.md — onboarding map for the target repo.
Filled from config.json (project.*, id.prefix, docs.*, checks.commands, checks.entrypoints)
and Phase-A answers (purpose/audience, entry points, quick start, neutrality placeholders).
Architecture Overview is DERIVED from docs/architecture.json when present — do not hand-maintain it.
README is the onboarding map, NOT the final authority for behavior (REQUIREMENTS) or workflow (WORKFLOW).
Harness-neutral: never name a specific agent product, model, or proprietary tool.
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

## Architecture Overview

<!-- If docs/architecture.json exists, this section is derived from it; otherwise delete it. -->
Diagram: `docs/architecture.json` (source of truth; any `.svg`/`.html` is rendered). Components: {{COMPONENT_LIST_FROM_JSON}}. Boundaries: {{REGION_LIST_FROM_JSON}}. Do not hand-maintain — derive from the JSON.

## Data Flow

1. {{STEP_1_INPUT}}.
2. {{STEP_2}}.
N. {{STEP_N_OUTPUT}}.

## Main Components

### `{{ENTRY_1}}`
- `{{SYMBOL_1}}`: {{JOB}}.
- `{{SYMBOL_2}}`: {{JOB}}.

## Agent Onboarding Guide

A cold-start collaborator (human or agent, no chat history) reads in this order: this README → `{{AGENTS_PATH}}` → `docs/architecture.json` (if present) → `{{REQUIREMENTS_PATH}}` → `{{SURFACE_DOC_PATH}}` → `{{VALIDATION_PATH}}` → `{{WORKFLOW_PATH}}`. Questions to answer before editing core logic: {{QUESTIONS_BEFORE_EDITING}}. Safe-change pattern: edit code → update the requirement ID + iteration history → update the surface doc → append a validation block → run the docs gate.

## Verification

```bash
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
# Docs coherence gate (ID continuity, command-surface consistency, neutrality)
python scripts/check_agentic_docs.py --config agentic-mode/config.json
```

Every command in `checks.commands` (config.json) that lists `"readme"` in `must_appear_in` MUST appear verbatim above.

## Project-Neutrality Checklist

- No brand names / codenames / hardcoded packages / serials / IPs / environment hosts in code, docs, tests, or examples.
- Runtime placeholders used in all docs/examples: {{RUNTIME_PLACEHOLDERS}}.
- {{EXTRA_NEUTRALITY_BULLET_OR_DELETE}}.

## Doc Cross-Links

- Behavior contract: `{{REQUIREMENTS_PATH}}`
- Observable surface: `{{SURFACE_DOC_PATH}}`
- Validation: `{{VALIDATION_PATH}}`
- Workflow: `{{WORKFLOW_PATH}}`
- Resident index: `{{INDEX_PATH}}`
