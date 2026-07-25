# agentic-mode

A **documentation contract** that makes any repository legible to any
collaborator — human or agent, in any tool, with **no chat history**. It is a
small set of layered, cross-linked docs joined by stable IDs, plus a
config-driven checker and a CI gate that keep those docs from drifting out of
sync with the code.

This repo is the **canonical source** of the methodology. Downstream copies (a
Claude Code plugin, a Devin IDE rule, a vendored subtree in your own repo) should
sync *from here* — see [Adapters](#adapters) and [Canonical source](#canonical-source).

## Why

Chat history is not a durable substrate. The moment a new collaborator arrives —
a different person, a different agent, a fresh session — everything that lived
only in the conversation is gone. Teams paper over this with a `NOTES.md` that
mixes contract, guide, status, and process until no one knows which section is
authoritative, and it rots.

agentic-mode fixes that with three principles (full doctrine in
[`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md)):

1. **Layered, non-overlapping docs.** Each file has exactly one job; facts have a
   single canonical home and are cross-linked, not duplicated into independent
   authorities.
2. **Stable IDs for every behavior.** Requirements carry `PREFIX-001` IDs; the
   user guide, validation blocks, commits, and MR/PR notes all cite them. The ID
   is the **join key** that lets any reader jump across layers without chat history.
3. **Append-only provenance + per-feature done evidence.** Iteration history
   records *why* a change landed (never rewritten); validation blocks record
   *that it was actually done* and how to re-verify.

The contract owns **What** (repo facts, behavior contract) and **Done**
(acceptance evidence). It never dictates **How/Who** (which tool, model, or
dispatch you use) — that stays with whoever does the work, which is what keeps
the contract portable across every harness.

## Quick start

You need only Python 3 (standard library) and git. The one entry point is
[`RUNBOOK.md`](RUNBOOK.md): point any agent at it ("read this file and run it"),
or follow it yourself.

### Bootstrap a new repo

Run the four-phase protocol in `RUNBOOK.md`: a repo scan + a 10-question
interview (Phase A), generate the layered docs in dependency order with each gate
passing (Phase B), copy the checker and wire CI (Phase C), hand off to
self-operation (Phase D). The result is a repo any collaborator can operate cold.

### Adopt an existing repo

If the repo already has an `AGENTS.md`, a `README`, or ad-hoc `docs/`, use
**Adopt mode** (also in `RUNBOOK.md`): inventory what exists, never overwrite a
hand-written doc, fill only the missing layers, and reconcile the config to point
at wherever the real files live. Adopt is deliberately conservative — the win is
coherence and enforceability, not a rewrite.

### See it working

[`examples/minimal-cli/`](examples/minimal-cli/) is a complete, passing contract
for a tiny fictional `todo` CLI. Run the gate against it:

```bash
python3 checker/check_agentic_docs.py \
  --config examples/minimal-cli/agentic-mode/config.json \
  --root examples/minimal-cli
```

It exits `0` with every check clean. Read the example's docs top-down to see a
filled-in contract end to end.

## The checker

`checker/check_agentic_docs.py` is a pure-standard-library, config-driven gate.
Everything project-specific (ID prefix, doc paths, bilingual headings, entry
points, command rules, deny words, allowlists) lives in an external
`agentic-mode/config.json` — the framework code never changes between projects.
Copy it into a repo (conventionally as `scripts/check_agentic_docs.py`), drop a
config beside it, and run from that repo's root:

```bash
python3 scripts/check_agentic_docs.py --config agentic-mode/config.json
```

It reports `<file>:<line>: [<category>] <message>` and exits `0` (clean), `1`
(findings), or `2` (bad config / I/O). Check categories:

| Category | What it enforces |
| --- | --- |
| `id-continuity` | `PREFIX-NNN` IDs are gap-free and duplicate-free; IDs cited in the surface/validation docs are defined; bilingual regions share identical ID sets. |
| `iteration-continuity` | *(opt-in)* the numbered Iteration History entries are gap-free. |
| `command-consistency` | each configured command string appears verbatim in every doc that must carry it. |
| `neutrality` | deny-listed words, a built-in harness deny list, non-allowlisted URL hosts, and *(opt-in)* IPv4 literals / single-machine paths. |
| `line-limit` | per-file maximum line counts (e.g. `AGENTS.md`). |
| `entrypoint` | declared entry points exist; `.py` ones byte-compile. |
| `doc-presence` | every declared doc path exists. |

A line carrying the marker `agentic-gate: allow` is skipped by the text scans, so
rule/spec docs can quote a bad example on purpose. See
[`checker/config.example.json`](checker/config.example.json) for every knob.

## Playbooks

Alongside the doc contract, [`playbooks/`](playbooks/) holds a small set of
**harness-neutral collaboration playbooks** — canonical rules any collaborator
(human or agent, in any tool) can read directly as a rules file. They are
**optional and policy-overridable**: a repo's own hooks, review canon, or
`AGENTS.md` rules always take precedence.

| Playbook | What it covers |
| --- | --- |
| [`COMMIT-MESSAGES.md`](playbooks/COMMIT-MESSAGES.md) | A Conventional-Commits variant: type table with build/ci/chore adjudications, an optional on-demand ticket, and scope rules — deferring to a local commit-msg hook. |
| [`TWO-AXIS-REVIEW.md`](playbooks/TWO-AXIS-REVIEW.md) | Dual-axis review — Standards (written right) and Spec (meets the ticket) audited on independent axes that never cross-rank. |
| [`REVIEW-RESPONSE.md`](playbooks/REVIEW-RESPONSE.md) | Discipline for the author answering review feedback: verify before implementing, no sycophantic openers, push back with evidence. |
| [`DOC-LINTER.md`](playbooks/DOC-LINTER.md) | Lint agent-facing documents for ambiguity — terminology drift, passive voice, hedge words, stacked negations, structure — with rules adapted from ASD-STE100 Simplified Technical English. |

## Install as Claude Code plugins

This repo is also a **Claude Code plugin marketplace**. Once it is on GitHub,
add the marketplace and install any subset of the six plugins — each is
independent and optional:

```
/plugin marketplace add madcatone/agentic-mode
/plugin install agentic-bootstrap@agentic-mode
/plugin install gcm@agentic-mode
/plugin install two-axis-review@agentic-mode
/plugin install review-response@agentic-mode
/plugin install doc-linter@agentic-mode
/plugin install fable5@agentic-mode
```

| Plugin | Installs | Canonical source |
| --- | --- | --- |
| `agentic-bootstrap` | The doc-contract bootstrapper skill (runs the RUNBOOK). | `RUNBOOK.md` + `doctrine/` + `templates/` + `checker/` (vendored) |
| `gcm` | Commit-message convention skill. | [`playbooks/COMMIT-MESSAGES.md`](playbooks/COMMIT-MESSAGES.md) |
| `two-axis-review` | Dual-axis review skill. | [`playbooks/TWO-AXIS-REVIEW.md`](playbooks/TWO-AXIS-REVIEW.md) |
| `review-response` | Review-response discipline skill. | [`playbooks/REVIEW-RESPONSE.md`](playbooks/REVIEW-RESPONSE.md) |
| `doc-linter` | Agent-facing document linter skill. | [`playbooks/DOC-LINTER.md`](playbooks/DOC-LINTER.md) |
| `fable5` | Commander-mode operating discipline + the strong-model founding prompt. | The plugin directory itself (self-canonical) |

The commit/review conventions differ from team to team, which is why they are
optional plugins and policy-overridable playbooks rather than part of the core.
Each of those plugins vendors a self-contained copy of its canonical source; see
[`adapters/claude-code/README.md`](adapters/claude-code/README.md) for the
vendoring + anti-drift sync.

`fable5` is the exception: it is **Claude Code-specific with no harness-neutral
playbook counterpart** — it governs how you operate a *session* (the main model
as advisor/dispatcher, subagent tiers, output written into a per-user config
home) rather than a repo's document contract, so it cannot live in the neutral
core. Its **plugin directory is its own canon**: nothing is vendored into it and
it is not part of the `sync_plugins.py` sync.

## Repo map

| Path | What it is |
| --- | --- |
| [`RUNBOOK.md`](RUNBOOK.md) | The single executable protocol — bootstrap/adopt, Phases A–D, config schema, hard rules. Start here. |
| [`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md) | The doctrine: why the layers exist, the ID discipline, append-only rules, precedence, adoption profiles. |
| [`doctrine/FIELD-NOTES.md`](doctrine/FIELD-NOTES.md) | Field lessons from the origin project that shaped the doctrine. |
| [`checker/`](checker/) | The config-driven checker and an annotated example config. |
| [`templates/`](templates/) | The fill-in skeletons for every generated doc + CI files. |
| [`playbooks/`](playbooks/) | Harness-neutral collaboration canon (commit messages, two-axis review, review response, doc linting) — optional, local rules override. |
| [`adapters/`](adapters/) | Harness-specific packaging (Claude Code plugins + marketplace, Devin IDE rule + review workflow). |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | The Claude Code plugin marketplace manifest. |
| [`scripts/sync_plugins.py`](scripts/sync_plugins.py) | One-way vendoring sync (canon → plugins) with a `--check` drift gate. |
| [`examples/minimal-cli/`](examples/minimal-cli/) | A complete worked example that passes the checker. |
| [`AGENTS.md`](AGENTS.md) | This repo's own contract (it dogfoods the methodology). |

## Adapters

The core (doctrine, RUNBOOK, templates, checker) is **harness-neutral** — it never
names a specific agent product, model, or proprietary tool. Harness-specific
packaging lives only under [`adapters/`](adapters/):

- [`adapters/claude-code/`](adapters/claude-code/) — a Claude Code plugin
  marketplace: the `agentic-bootstrap` toolkit, the four playbooks, and the
  self-canonical `fable5` commander-mode discipline packaged as optional,
  independently installable plugins (see
  [its README](adapters/claude-code/README.md) and [Install as Claude Code
  plugins](#install-as-claude-code-plugins) above).
  - Alongside the plugins, [`adapters/claude-code/dispatch/`](adapters/claude-code/dispatch/)
    ships a dated snapshot of the origin machine's `~/.claude/` commander-mode
    dispatch system (rule files + subagent definitions) as a directly installable
    kit — the evolved counterpart to the `fable5` founding prompt (see [its
    README](adapters/claude-code/dispatch/README.md)).
- [`adapters/devin-ide/`](adapters/devin-ide/) — a Devin IDE rule and a review
  workflow.

Each adapter is thin: it points at (or vendors) the canonical core and resolves
paths to it. Add a new adapter for a new harness; do not fork the doctrine.

## Canonical source

This repository is the canonical source of the agentic-mode methodology. When you
vendor it downstream (a plugin, an IDE rule, a subtree), sync **from here** and do
not hand-edit the vendored `doctrine/`, `templates/`, or `checker/` — a downstream
edit that never flows back becomes silent drift. If a downstream repo needs a new
capability, add it here first, then re-sync.

## License

[MIT](LICENSE) — © agentic-mode contributors.
