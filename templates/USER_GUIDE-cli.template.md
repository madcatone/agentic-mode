<!--
TEMPLATE: docs/USER_GUIDE.md for project.type == "cli". Observable surface: commands, flags, keys,
views, output, troubleshooting. Filled from config.json (id.prefix, bilingual.*) and Phase-A answers
(the CLI surface mined from --help / argument parsing).
Every behavior subsection CITES its owning {{PREFIX}}-XXX from REQUIREMENTS. Keyboard/flag tables
must match the source 1:1 (the checker parity-checks these where the source exposes grep-able constants).
BILINGUAL: keep the second track ONLY IF config bilingual.enabled == true; else delete it.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
-->

# {{COMPONENT}} — User Guide

## English

### Purpose
{{1-2 sentences: what this tool is, that it is separate from any sibling tools, when to choose it.}}

### Project-Neutral Usage
- Use `{{FLAG_1}} <placeholder>` only when {{runtime need}}.
- Use `{{FLAG_2}} <placeholder>` only when {{runtime need}}.
- {{Other runtime placeholders + supported enum values, or delete.}}

### Common Commands
{{One fenced bash block per primary flow, using placeholders (e.g. open a saved input, live read, live+save, replay).}}
```bash
{{command_example_1}}
{{command_example_2}}
```

### Flags
| Flag | Effect | Requirement |
| --- | --- | --- |
| `{{--flag}}` | {{what it does}} | {{PREFIX}}-0NN |

### Views
{{Describe the default view + any alternate view; include a short text-art skeleton of each; cite {{PREFIX}}-XXX for the view-switch key. Delete if the CLI has no interactive views.}}

### Keyboard Controls
<!-- Delete this section for a non-interactive CLI. Otherwise the table must match the key handler 1:1. -->
| Key | Action |
| --- | --- |
| `{{key}}` | {{action}} ({{PREFIX}}-0NN) |

### Output / Exports
{{Describe export keys, dump flags, and the file paths produced. Cite IDs.}}

### Highlighting and Error Semantics
{{Prefix/marker rules, threshold-based coloring, missing/alert conditions, timeout pairing — cite IDs. Delete if not applicable.}}

### Feature Subsections (one per surfaced behavior family)
{{For each: what triggers it, what the user sees, which filter/flag surfaces it, owning {{PREFIX}}-XXX.}}

### Troubleshooting
{{Each failure mode the code explicitly handles + the copy-paste fix command.}}

<!-- ==== SECOND LANGUAGE TRACK — keep ONLY if config bilingual.enabled == true; else delete from here down ==== -->
## {{SECONDARY_LANGUAGE_HEADER}}
{{Mirror every section above in lock-step: same headings, same keyboard table, same flag list, same command count.}}
