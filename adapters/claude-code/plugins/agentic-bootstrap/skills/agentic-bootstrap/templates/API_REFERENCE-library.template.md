<!--
TEMPLATE: docs/API_REFERENCE.md for project.type == "library". Observable surface = the PUBLIC API:
exported symbols, signatures, usage examples, and compatibility promises. Filled from config.json
(id.prefix, bilingual.*) and Phase-A answers (the public surface mined from the exported index /
package manifest / public symbols).
Every documented symbol CITES its owning {{PREFIX}}-XXX from REQUIREMENTS. Signatures must match the
source 1:1. Document only the PUBLIC surface — internal/private symbols are out of scope here.
BILINGUAL: keep the second track ONLY IF config bilingual.enabled == true; else delete it.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
-->

# {{COMPONENT}} — API Reference

## English

### Purpose
{{1-2 sentences: what this library provides, what problem it solves for a caller, when to reach for it.}}

### Installation / Import
```bash
{{install_command_or_none}}
```
```{{lang}}
{{import_or_require_example}}
```

### Public API Surface
The stable, supported surface. Anything not listed here is internal and may change without notice.

| Symbol | Kind | Summary | Requirement |
| --- | --- | --- | --- |
| `{{name}}` | {{function/class/constant/type}} | {{one-line job}} | {{PREFIX}}-0NN |

### Reference

#### `{{symbol_signature}}`  ({{PREFIX}}-0NN)
- **Purpose:** {{what it does}}.
- **Parameters:** `{{param}}` — {{type}}, {{meaning; required/optional; default}}.
- **Returns:** {{type}} — {{meaning}}.
- **Raises / errors:** {{error condition → error type/value}}.
- **Example:**
  ```{{lang}}
  {{minimal runnable usage example with placeholder inputs}}
  ```

<!-- Repeat one block per public symbol. Signature MUST match source exactly. -->

### Usage Patterns
{{2-4 short end-to-end examples of common real tasks composed from the public API. Placeholders for any environment-specific values.}}

### Compatibility Promise
- **Versioning:** {{scheme, e.g. semantic versioning: MAJOR breaks the public surface, MINOR adds, PATCH fixes}}.
- **Stable surface:** the symbols in the Public API Surface table above. Additions are backward-compatible; removals/signature changes are breaking and go in a MAJOR release with an Iteration History entry.
- **Deprecation:** a symbol is marked deprecated (kept working) for at least {{DEPRECATION_WINDOW}} before removal; the deprecation is announced in REQUIREMENTS Iteration History and here.
- **Explicitly unstable:** {{list any experimental/unstable symbols, or "none"}}.

### Errors and Exceptions
{{Enumerate the error/exception types the public API can surface and the condition that triggers each. Cite IDs.}}

### Troubleshooting
{{Common misuse → symptom → fix.}}

<!-- ==== SECOND LANGUAGE TRACK — keep ONLY if config bilingual.enabled == true; else delete from here down ==== -->
## {{SECONDARY_LANGUAGE_HEADER}}
{{Mirror every section above in lock-step: same symbol table, same reference blocks in the same order, same compatibility promise.}}
