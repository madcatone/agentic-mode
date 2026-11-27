<!--
TEMPLATE: docs/USER_GUIDE.md for project.type == "cli". Observable surface: commands, flags, keys,
views, output, troubleshooting. Filled from config.json (id.prefix, bilingual.*) and Phase-A answers
(the CLI surface mined from --help / argument parsing).
Every behavior subsection CITES its owning {{PREFIX}}-XXX from REQUIREMENTS. Keyboard/flag tables
must match the source 1:1 (a RUNBOOK Phase-B gate, checked by hand — the checker never parses project source).
The Views, Keyboard Controls, and Highlighting and Error Semantics sections are for an interactive
tool. A CLI with none of them loses those three sections, headings included, and the prompts that
assume a screen are rewritten for a plain run (RUNBOOK Phase B, step 4).
BILINGUAL: keep the second track ONLY IF config bilingual.enabled == true; else delete it.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Template-Source: agentic-bootstrap/USER_GUIDE-cli@v2  (@v2: the title takes the component-name
slot; no descriptive slot holds a second placeholder; a command sketch marks its argument as a
value, not a placeholder; the ID examples use three digits; the header names the sections that
belong to an interactive tool and the cut for a CLI whose flags take no value; the instruction
above the feature subsections is a comment, not a heading; each command sample is its own fenced
block with a lead sentence)
`{{FLAG_1}}` and `{{FLAG_2}}`: one bullet per flag that takes a value. A target
with no such flag loses the Project-Neutral Usage section, headings included.
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# {{COMPONENT_NAME}} — User Guide

## English

### Purpose
{{1-2 sentences: what this tool is, that it is separate from any sibling tools, when to choose it.}}

### Project-Neutral Usage
- Use `{{FLAG_1}} <value>` only when {{runtime need}}.
- Use `{{FLAG_2}} <value>` only when {{runtime need}}.
- {{Other runtime placeholders + supported enum values, or delete.}}

### Common Commands
{{A one-line lead for the first primary flow. Use runtime placeholders where the target has them.}}:
```bash
{{command_example_1}}
```

{{A one-line lead for the next primary flow. Delete the lead and its block when the target has none.}}:
```bash
{{command_example_2}}
```

### Flags
| Flag | Effect | Requirement |
| --- | --- | --- |
| `{{--flag}}` | {{what it does}} | {{PREFIX}}-NNN |

### Views
{{Describe the default view + any alternate view; include a short text-art skeleton of each; cite the owning requirement ID for the view-switch key. Delete if the CLI has no interactive views.}}

### Keyboard Controls
<!-- Delete this section for a non-interactive CLI. Otherwise the table must match the key handler 1:1. -->
| Key | Action |
| --- | --- |
| `{{key}}` | {{action}} ({{PREFIX}}-NNN) |

### Output / Exports
{{Describe export keys, dump flags, and the file paths produced. Cite IDs.}}

### Highlighting and Error Semantics
{{Prefix/marker rules, threshold-based coloring, missing/alert conditions, timeout pairing — cite IDs. Delete if not applicable.}}

<!-- Repeat one subsection per behavior family, the commands that serve one task. Each has its own heading and cites its owning requirement ID. -->
{{For each: what triggers it, what the user sees, which filter/flag surfaces it, and its owning requirement ID.}}

### Troubleshooting
{{Each failure mode the code explicitly handles + the copy-paste fix command.}}

<!-- ==== SECOND LANGUAGE TRACK — keep ONLY if config bilingual.enabled == true; else delete from here down ==== -->
## {{SECONDARY_LANGUAGE_HEADER}}
{{Mirror every section above in lock-step: the same sections, same keyboard table, same flag list, same command count.}}
