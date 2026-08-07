# Claude dispatch kit

A **dated release snapshot** of one machine's commander-mode dispatch system for
Claude Code — the machine-wide operating rules (`CLAUDE.md` + `rules/`) and the
subagent-dispatch definition files (`agents/`) that live under `~/.claude/`.
Install it and a colleague's Claude Code sessions inherit the same
delegate-heavy operating model: the main model converses, decides, dispatches,
and integrates, while large reads, repo scans, and batch edits go to tiered
subagents that return only conclusions.

> English version. 繁體中文：[README-ZH.md](README-ZH.md) — informationally equivalent.

## How this relates to `fable5`

The [`fable5`](../plugins/fable5) plugin and this kit are **two paths to the same
operating model**, and they complement each other:

- **`fable5` ships the *founding prompt*** — you spend one strong-model session
  that builds the system *from your own machine's realities* (settings, repos,
  tools) and writes the rule files from scratch.
- **the dispatch kit ships the *evolved finished product*** — the rule files this
  origin machine already grew and hardened over many sessions (they keep evolving
  through their `LESSONS.md`). Drop them into `~/.claude/` and adopt the result
  directly, no founding session required.

Use `fable5` to grow your own; use the dispatch kit to adopt a battle-tested
instance and then let it keep evolving through *your* `LESSONS.md`.

## Snapshot positioning & sync discipline

- **This kit is a `2026-08-07` snapshot.** It is a point-in-time copy, not a live
  feed. This refresh re-packaged the same file set from the origin machine:
  `CLAUDE.md`, `rules/`, and `agents/` came back unchanged (the previous
  `2026-07-25` snapshot was already current for them), and the whole delta is
  **nine new `LESSONS.md` entries** (`2026-07-11` … `2026-07-27`) covering
  the two-way distribution-chain discipline (a feature landed in a copy must
  flow back to the canon), grounding a port in the target product's actual
  artifacts before packaging,
  observability as a v1 requirement, a five-run blind model-tier comparison and
  the "honest escape hatch" it produced, the `tool_uses=0` empty-shell subagent
  signature, sampling by render path rather than by page, line-number rot in
  append/prepend-only files, and splitting a report's claims by evidence
  strength.
- **The canon lives on the origin machine's `~/.claude/`.** That copy keeps
  evolving (it appends to `LESSONS.md`, revises `rules/` as the harness changes).
  This kit does not.
- **To update the kit:** re-package from the origin machine's `~/.claude/` (re-run
  the de-personalization pass), bump the snapshot date. There is no upstream sync
  in this repo — the kit is **not** part of `scripts/sync_plugins.py`, because its
  canon is on the origin machine, not in this repo.
- **Your local evolution stays local.** After you install, that `~/.claude/` is
  *yours*: append your own lessons to your `LESSONS.md`, tune the rules to your
  environment. Do **not** try to flow your edits back to the kit or the origin
  machine.

## Install

The kit's [`home/`](home) directory mirrors what should live under `~/.claude/`.
Installing = back up whatever you already have, then copy `home/`'s contents in.
It only writes `CLAUDE.md`, `rules/*.md`, and `agents/*.md`; it never touches your
`settings.json`, `projects/`, or anything else under `~/.claude/`.

Run from **this directory** (`adapters/claude-code/dispatch/`).

### bash / zsh (macOS, Linux)

```bash
# 1) Back up anything that already exists (skipped if absent)
ts=$(date +%Y%m%d-%H%M%S)
for p in ~/.claude/CLAUDE.md ~/.claude/rules ~/.claude/rules-ref ~/.claude/agents; do
  [ -e "$p" ] && cp -R "$p" "$p.bak-$ts"
done

# 2) Merge the kit into ~/.claude (adds/overwrites only the kit's files)
mkdir -p ~/.claude
cp -R home/. ~/.claude/
```

### PowerShell (Windows)

```powershell
# 1) Back up anything that already exists (skipped if absent)
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
foreach ($p in @("$HOME\.claude\CLAUDE.md","$HOME\.claude\rules","$HOME\.claude\rules-ref","$HOME\.claude\agents")) {
  if (Test-Path $p) { Copy-Item $p "$p.bak-$ts" -Recurse -Force }
}

# 2) Merge the kit into ~\.claude (merge-safe: creates the dir, then recurses)
New-Item -ItemType Directory -Force -Path "$HOME\.claude" | Out-Null
Copy-Item -Path "home\*" -Destination "$HOME\.claude" -Recurse -Force
```

New or renamed `agents/` definitions **only take effect in a newly opened
session** — restart Claude Code after installing (see the note in
`home/agents/README.md`).

## `settings.json` guidance (do this yourself; the kit never edits it)

The kit deliberately ships no `settings.json`. Set these by hand:

- **Keep `"env"` empty of `CLAUDE_CODE_SUBAGENT_MODEL`.** That variable is a
  global override — it beats both the per-call `model` argument *and* the agent
  definition-file frontmatter, so setting it collapses the whole dispatch table
  onto a single model with no warning. Leave it unset.
- **Quality-first cost posture.** The rules default to strong models and only
  downgrade for clearly mechanical batch work. If you want a cheaper default,
  that is a deliberate posture change — see `rules/10-DISPATCH.md`.
- **Consider `permissions.defaultMode: "auto"`.** It lets a classifier approve
  routine actions instead of prompting on every one; where the classifier is
  unavailable the CLI falls back to the normal `default` prompting, so it does
  not lower your backstop. This suits the delegate-heavy model — fewer
  interruptions on the dispatch loop.
- The rules were verified against Claude Code `2.1.204` on darwin (2026-07-17).
  On a newer build, re-verify the harness facts in `rules/10-DISPATCH.md` §0.

## Post-install machine-adaptation checklist

The origin machine's private hand-off letter is deliberately **excluded** from
this kit. Its job — telling you what to adapt to *your* environment — is done by
this checklist instead. Walk it once after installing:

1. **Swap the build/test commands.** The rules use `cd <你的專案> && npm run build`
   as a placeholder. Replace it (in your habits, and when you write dispatch
   prompts) with your project's real gate command(s).
2. **Restart before relying on `agents/`.** Definition files are recognized only
   in a session that started *after* they were installed.
3. **Audit your own permission allowlist.** A lesson from the origin machine: its
   `settings.local.json` allowlist was broader than ideal (e.g. unrestricted
   `ssh`), and the harness will *not* gate risky actions for you. Read your own
   `~/.claude/settings*.json` and confirm you are comfortable with what is
   auto-approved — the rules assume *you* are the backstop.
4. **Your `memory/` starts empty.** The rules reference a per-project memory
   mechanism (project facts + a `MEMORY.md` index). The kit ships none — that is
   your content to accumulate as you work each repo.
5. **Re-check the harness facts.** `rules/10-DISPATCH.md` §0 records subagent
   parameters, the model-resolution order, and Explore's inheritance behavior as
   observed on a specific Claude Code build. If yours differs, fix the file per
   `rules/40-MAINTENANCE.md` §5 and mark it `(verified <date>)`.
6. **Don't duplicate team plugin skills in personal `~/.claude/skills/`.** If a
   skill is already distributed as a team plugin, keep it there as the single
   source of truth; a personal copy under `~/.claude/skills/` drifts out of sync
   the moment either side changes.

## What was adapted from the origin machine

To make the snapshot portable, the de-personalization pass:

- **Removed** all absolute home paths, IP literals, internal host names, and
  credentials (there were none of the latter in these files).
- **Generalized** project-specific examples in `rules/` (specific feature IDs,
  deployment vendors, a specific spec-browser project, `poc/` build commands)
  into generic descriptions that keep their teaching value.
- **Relabeled** `00-DIAGNOSIS.md`'s "本機證據" (this-machine evidence) blocks as
  "原始機器上的實例（採用時對照你自己的環境）" — instances on the origin machine,
  compare against your own.
- **Curated `LESSONS.md`**: kept only lessons that still hold in a different repo
  (with internal repo names, ticket/MR numbers, and internal tool names
  generalized); dropped entries that were specific to the origin machine's own
  pipelines. The append-only format and dates are preserved.
- **Excluded** `50-LETTER.md` (the origin machine's private hand-off letter) and
  `60-DOCKER.md` (its local container/service conventions) entirely, and dropped
  both routing-table rows from `CLAUDE.md` — along with `CLAUDE.md`'s pointer to
  a machine-local personal skill.

`~/.claude/…`-relative paths are kept verbatim — they resolve the same way on any
colleague's machine.

## Contents

```
dispatch/
  README.md            # this file
  README-ZH.md         # 繁體中文（等價）
  home/                # mirrors ~/.claude/ — the install payload
    CLAUDE.md          # machine-wide router + 6 hard rules + standard behavior
    rules/             # always-loaded every session
      10-DISPATCH.md   # model dispatch protocol, subagent params, cost levers
      20-JUDGMENT.md   # judgment rubrics (done-ness, when to ask, quality floor)
      30-TEMPLATES.md  # fill-in dispatch prompt templates
      40-MAINTENANCE.md# how to evolve the rules without rotting them
    rules-ref/         # read on demand (kept out of the always-loaded context)
      00-DIAGNOSIS.md  # the three failure modes every rule file fixes
      LESSONS.md       # curated, append-only field lessons
    agents/            # subagent definition files (dispatch table as files)
      README.md        # how the definitions work + known gaps
      Explore.md implementer.md reviewer.md verifier.md
      researcher.md bulk-editor.md log-digger.md
```
