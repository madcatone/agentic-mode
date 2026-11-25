# AGENTS.md — Claude Code adapter

Adapter-local contract for this directory. The repo-wide contract is the root
[`AGENTS.md`](../../AGENTS.md); this file holds the harness-specific facts that
do not belong there. The plugin catalog is [`README.md`](README.md).

## Scope

- This tree packages the harness-neutral toolkit as Claude Code plugins,
  distributed through the repo marketplace. The neutral core (`doctrine/`,
  `RUNBOOK.md`, `templates/`, `checker/`, `playbooks/`) does not name a product.
  This tree does.
- Root `CLAUDE.md` is the one-line import `See @AGENTS.md`. It is not a second
  contract. Claude Code autoloads that filename; the import keeps
  [`AGENTS.md`](../../AGENTS.md) as the only copy of the rules.

## Key Files

- [`../../.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json):
  the marketplace manifest. Plugin entries live here; install paths are
  `./adapters/claude-code/plugins/<name>`.
- [`../../scripts/sync_plugins.py`](../../scripts/sync_plugins.py): one-way
  vendoring sync (canon → plugins) and the `--check` drift gate.
- [`plugins/team-kit/`](plugins/team-kit/): the four-role worker kit
  (observer / coder / reviewer / fortify) — rules, hook scripts, and the state
  contract. Self-canonical; edit it in place. The state surface is
  [`plugins/team-kit/STATE-CONTRACT.md`](plugins/team-kit/STATE-CONTRACT.md).
  When that contract and the kit code disagree, follow the code and update the
  contract (the file says the same).
- [`dispatch/`](dispatch/): the dispatch kit, a dated snapshot of the origin
  machine's `~/.claude/` commander-mode dispatch system (rule files and
  subagent definitions). Install it by copying the contents of `home/` into
  `~/.claude/`. The kit is not a plugin and has no marketplace entry. It is not
  in the sync MANIFEST either, because its canon is on the origin machine. To
  update it, re-package from that machine. It is the evolved counterpart to the
  `fable5` founding prompt. See [`dispatch/README.md`](dispatch/README.md).

## Vendoring

A plugin skill reads only files under its own directory, so synced plugins
carry a vendored copy. The canon is authoritative in one direction:

1. Edit the harness-neutral source (`playbooks/*.md`, root `RUNBOOK.md`,
   `doctrine/BOOTSTRAP-CORE.md`, `templates/`, `checker/`).
2. From the repo root, run `python3 scripts/sync_plugins.py`.
3. `python3 scripts/sync_plugins.py --check` must exit 0. Never hand-edit a
   vendored copy under `plugins/` for a plugin that is in the sync MANIFEST.

`fable5`, `commander`, `idea-to-spec`, `pstack`, and `team-kit` are
self-canonical: no neutral playbook counterpart, not in the sync MANIFEST,
edited in place. Add a marketplace entry for a new self-canonical plugin; do
not add a MANIFEST row.

## Portable skills

Every `SKILL.md` under `plugins/*/skills/` and every file it references must
resolve by paths **relative to its own skill directory**. Never use a
harness-injected variable (`${CLAUDE_PLUGIN_ROOT}` and the like) or an absolute
path — the open skills CLI installs these directories into other agents' skill
folders, where that variable is undefined. The root contract's check must
print `clean` and exit 0 only when grep exits 1 (a match or a grep error fails):

```bash
rc=0; grep -rn 'PLUGIN_ROOT' adapters/claude-code/plugins || rc=$?; if [ "$rc" -eq 1 ]; then echo clean; elif [ "$rc" -eq 0 ]; then echo FOUND; exit 1; else echo "grep error: exit ${rc}"; exit "$rc"; fi
```

## Commands

Canonical command list: root [`AGENTS.md`](../../AGENTS.md) Development
Commands. Run these from the repo root:

```bash
python3 scripts/sync_plugins.py --check
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo ok
sh adapters/claude-code/plugins/team-kit/eng/tests/run-tests.sh
```

The team-kit eng tests require `jq` on `PATH`.
