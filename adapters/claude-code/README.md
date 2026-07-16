# Claude Code adapter

This directory packages the harness-neutral agentic-mode toolkit as **Claude
Code plugins**, distributed through a plugin marketplace. It is the only place in
this repo that names a specific agent product — the core (`doctrine/`,
`RUNBOOK.md`, `templates/`, `checker/`, `playbooks/`) stays neutral.

## The marketplace

The marketplace manifest lives at the repo root:
[`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json). Once
this repo is on GitHub, a user adds it and installs any subset of plugins:

```
/plugin marketplace add <owner>/<repo>
/plugin install agentic-bootstrap@agentic-mode
/plugin install gcm@agentic-mode
/plugin install two-axis-review@agentic-mode
/plugin install review-response@agentic-mode
```

Each plugin is independent and optional — install only what your team wants.

## The plugins

| Plugin | What it installs | Canonical source |
| --- | --- | --- |
| [`agentic-bootstrap`](plugins/agentic-bootstrap) | The doc-contract bootstrapper: a skill that runs the RUNBOOK to bootstrap/adopt agentic-mode in any repo. | `RUNBOOK.md`, `doctrine/`, `templates/`, `checker/` (all vendored into the skill) |
| [`gcm`](plugins/gcm) | Commit-message convention skill. | [`playbooks/COMMIT-MESSAGES.md`](../../playbooks/COMMIT-MESSAGES.md) |
| [`two-axis-review`](plugins/two-axis-review) | Dual-axis (Standards + Spec) review skill. | [`playbooks/TWO-AXIS-REVIEW.md`](../../playbooks/TWO-AXIS-REVIEW.md) |
| [`review-response`](plugins/review-response) | Discipline for responding to review feedback. | [`playbooks/REVIEW-RESPONSE.md`](../../playbooks/REVIEW-RESPONSE.md) |

## Vendoring and the sync relationship

A Claude Code skill can only read files **under its own directory** — it cannot
reach back into the repo with `../`. So every plugin carries a **vendored copy**
of whatever canonical file it needs:

- The three playbook plugins keep their own `SKILL.md` frontmatter (the `name` +
  `description` that drive skill triggering) and take their **body verbatim**
  from the matching `playbooks/*.md` canon file.
- `agentic-bootstrap` vendors the RUNBOOK, the doctrine (`reference/BOOTSTRAP-CORE.md`),
  the checker, and the templates so the skill is fully self-contained.

That duplication is a drift risk, so the sync is **owned by one script** and
gated in CI:

```bash
python3 scripts/sync_plugins.py          # write canon -> plugin
python3 scripts/sync_plugins.py --check   # verify only; exit 1 on any drift
```

The canon is authoritative in **one direction**: edit the `playbooks/*.md` (or
the root `RUNBOOK.md` / `doctrine/` / `templates/` / `checker/`), then re-run
`sync_plugins.py`. Never hand-edit a vendored copy — the `--check` gate in
[`.github/workflows/agentic-docs.yml`](../../.github/workflows/agentic-docs.yml)
will fail the build if a vendored file drifts from its source.

## Adding a new plugin

1. Write the canonical, harness-neutral source (a `playbooks/*.md`, or reuse the
   core toolkit).
2. Create `plugins/<name>/.claude-plugin/plugin.json` and
   `plugins/<name>/skills/<name>/SKILL.md` (frontmatter only for a synced body).
3. Add the canon→target mapping to the `MANIFEST` in `scripts/sync_plugins.py`.
4. Add the plugin entry to `.claude-plugin/marketplace.json`.
5. Run `python3 scripts/sync_plugins.py` and commit the vendored output.
