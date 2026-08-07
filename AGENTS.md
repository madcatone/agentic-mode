# AGENTS.md — agentic-mode

Repo facts and the human/agent co-operation contract for this repository. This
repo *is* the agentic-mode methodology, so it dogfoods its own rules. It states
*what is true here* and *what "done" requires*; it does not tell you which tool,
model, or dispatch to use. Read [`README.md`](README.md) first, then this.

## Project Scope

- The canonical source of the agentic-mode documentation contract: doctrine, an
  executable RUNBOOK, document templates, a config-driven checker, harness
  adapters, and a worked example.
- **Harness-neutral core (iron rule).** Nothing in `doctrine/`, `RUNBOOK.md`,
  `templates/`, or `checker/` may name a specific agent product, model, or
  proprietary tool. Harness-specific content lives **only** under `adapters/`.
- **Project-neutral.** No hardcoded brands, hosts, IP literals, or absolute
  machine paths anywhere. The worked example uses a fictional project.

## Key Files

- `README.md` / `README-ZH.md`: onboarding (English / Traditional Chinese).
- `RUNBOOK.md`: the single executable protocol (bootstrap/adopt, Phases A–D).
- `doctrine/BOOTSTRAP-CORE.md`: the doctrine behind every rule.
- `doctrine/FIELD-NOTES.md`: field lessons from the origin project.
- `checker/check_agentic_docs.py`: the config-driven gate (pure stdlib).
- `checker/config.example.json`: an annotated config with every knob.
- `templates/`: fill-in skeletons for every generated doc + CI files.
- `playbooks/`: harness-neutral collaboration canon (commit messages, two-axis
  review, review response, doc linting) — optional, local rules override them.
- `playbooks/scripts/doc_lint.py`: the doc-linter's mechanical pass (pure stdlib).
- `adapters/`: Claude Code plugins + marketplace, Devin IDE rule + review workflow.
- `.claude-plugin/marketplace.json`: the Claude Code plugin marketplace manifest.
- `scripts/sync_plugins.py`: one-way vendoring sync (canon → plugins) + `--check` gate.
- `examples/minimal-cli/`: a complete contract that passes the checker.

## Development Commands

- Byte-compile the checker:

```bash
python3 -m py_compile checker/check_agentic_docs.py
```

- Run the gate on the worked example (must exit 0):

```bash
python3 checker/check_agentic_docs.py --config examples/minimal-cli/agentic-mode/config.json --root examples/minimal-cli
```

- Sweep for leftover template placeholders in the example:

```bash
grep -rn '{{' examples/minimal-cli && echo "FOUND" || echo "clean"
```

- Byte-compile the doc linter and lint its own playbook (must exit 0):

```bash
python3 -m py_compile playbooks/scripts/doc_lint.py
cd playbooks && python3 scripts/doc_lint.py DOC-LINTER.md
```

- Verify the plugin vendored copies are in sync with the canon (must exit 0):

```bash
python3 scripts/sync_plugins.py --check
```

- Validate the marketplace + plugin manifests parse:

```bash
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo ok
```

## Change Flow (What "Done" Requires)

1. Code / doctrine / template edited.
2. If the checker's behavior changed, `checker/config.example.json` and the
   checker's module docstring are updated to match.
3. If the doc-set changed, the templates and `RUNBOOK.md`'s layout/schema stay
   in sync (the config schema is stated in exactly one place — `RUNBOOK.md`).
4. The worked example still passes the gate (see Development Commands).
5. If a `playbooks/` file or a vendored core file (`RUNBOOK.md`, `doctrine/`,
   `templates/`, `checker/`) changed, `python3 scripts/sync_plugins.py` was run
   so the plugin copies match, and `--check` exits 0. Never hand-edit a vendored
   copy under `adapters/claude-code/plugins/`. (Exception: the `fable5` and
   `commander` plugins are self-canonical — not vendored and not in the sync
   MANIFEST — so their files are edited in place.)
6. `README.md` and `README-ZH.md` stay information-equivalent when either changes.

## Sign-Off Points

- The author does not sign off their own completion claim on asserted evidence.
  Completion is proven by the checker's objective output or a fresh-context
  read-back — not by "looks fine."
- A change to the checker must ship with both a passing example run and a
  demonstration that the new/changed check fires when violated.

## Stop-and-Ask (do NOT proceed silently)

Stop and ask a human before any of these, even if permissions allow it:

- Changing the `config.json` **schema** (breaks every downstream repo's config).
- Adding a harness name into the neutral core (`doctrine/`, `RUNBOOK.md`,
  `templates/`, `checker/`) — it belongs in `adapters/`.
- **Irreversible deletion** of files or history; force-pushing; publishing.
- **CI / release configuration** changes, or anything touching credentials.
- A user premise the evidence contradicts — report the evidence first.

## Change-Flow Boundary (defer to WORKFLOW)

- Move changes through review per your platform's workflow. **Boundary test:** if
  a rule names a platform CLI or a platform-specific comment style, it belongs in
  a WORKFLOW doc/adapter, not here.

## Git Hygiene

- Do not commit `__pycache__/`, `.venv/`, or the example's runtime `tasks.json`.
- Explicit file staging; never commit secrets or `.env` values.
- Never push directly to `main` — open a merge/pull request instead.
