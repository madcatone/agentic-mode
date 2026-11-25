# Changelog

All notable changes to the agentic-mode toolkit. Versions track the
`agentic-bootstrap` plugin version and the git tags on `main`. The date is
the tag date.

## [Unreleased]

### Added

- `global-claude` plugin (self-canonical, under
  `adapters/claude-code/plugins/global-claude`): one skill that checks the
  user-global Claude Code instruction file (`~/.claude/CLAUDE.md`, or
  `$CLAUDE_CONFIG_DIR/CLAUDE.md` when that variable is set). A missing file
  is shown as a short global-scope starter, or as a one-line `See @` pointer
  when `~/.agents/AGENTS.md` or `~/.codex/AGENTS.md` already exists, and is
  written only after an explicit yes. An existing file is reviewed and edited
  only when the user approves a diff. `scripts/detect_global_claude.py` is a
  read-only standard-library detector with `--selftest`.

## [1.3.0] — 2026-11-18

### Added
- AGENTIC-MODE template: **Canonical Questions** section — the seed list of
  questions a zero-context reviewer must answer cold now has a skeleton in the
  resident index. SELF-TEST §D always pointed at "the resident index lists N
  canonical questions" but no template ever carried that section; one adopter
  built it by hand from the pointer, proving the demand. The section is now
  canonical, and SELF-TEST consumes it instead of duplicating a list.
- `Template-Source` markers for AGENTIC-MODE and SELF-TEST (@v2). These two
  resident files were previously untrackable generations — only WORKFLOW
  carried a marker — so an upgrade could not cite the base it ported from.
- **Rendering-language rule** (doctrine "Rendering Language and Canonical
  Headings" + RUNBOOK Phase B + bootstrap skill directive): body prose renders
  in the target repo's language; section headings stay canonical English.
  Root cause of the divergence found across adopters: nothing told the
  bootstrapping agent that headings are cross-repo anchors, so three ad-hoc
  heading translations appeared in one week and no cross-repo instruction
  could resolve by name.

### Changed
- SELF-TEST template §D: the embedded five-question example list is removed;
  the probe consumes the index's Canonical Questions section (one list, one
  home — two copies could drift independently).

## [1.2.0] — 2026-11-12

### Added
- RUNBOOK: "Upgrading an adopted repo to a newer toolkit version" — the
  fourth lifecycle stage (bootstrap → adopt → upgrade → release) now has a
  documented procedure: read the checker delta against the tag before
  swapping, swap verbatim (a new check firing is the upgrade working — fix
  the docs, not the checker), re-port WORKFLOW templates only at declared
  substitution points, record the upgrade like any change.
- Doctrine: FIELD-NOTES lessons 7-8 promoted into `BOOTSTRAP-CORE.md` —
  verification procedures live in scripts, not prose; docs record the
  verification action, not the status name (one paragraph in Per-Feature
  Validation, two Anti-Patterns rows).

### Changed
- WORKFLOW-github template: retired the stale "NEW — not yet battle-tested"
  status note; the variant is field-proven (validated end-to-end in a real
  adoption through multiple tagged releases, including a CI-runner
  migration).

## [1.1.1] — 2026-11-12

### Fixed
- `ci-runners` scan now exempts inline code spans — a marker quoted in
  backticks (docs explaining the syntax) is a mention, not a declaration.
  Found by the first real adopter within the hour of 1.1.0 shipping; same
  exemption principle the neutrality check already applies. New fire-demo
  `m5` proves a quoted marker stays clean while the real declaration gates.

## [1.1.0] — 2026-11-12

First tagged release.

### Added
- Checker: opt-in `ci-runners` gate — `<!-- ci-runners: ... -->` markers in
  governed prose must match config `ci.runners` exactly; a declared set with
  no marker, and a marker with no declared set, both fire. Fenced code and
  inline code spans are exempt. Config schema gains the optional
  `ci.runners` string list.
- WORKFLOW templates v2: one-line runner declaration whose marker the gate
  verifies (config is the single source of truth), and §11 release checklist
  (inventory → release branch → prepare commit → squash merge → tag → verify
  the deployed artifact via script → back-merge → optional read-back probe →
  post-merge evidence backfill).
- VALIDATION template: post-merge evidence clause — the only declared
  exception to append-only (Status subsection only, must cite the original
  PR/MR).
- SELF-TEST template: zero-context read-back probe cadence now includes
  release tags.
- doctrine/FIELD-NOTES: lessons 7 (encode verification procedures as
  scripts, not prose) and 8 (docs record how to verify, not what a status is
  called), distilled from a CI-migration field-notes cycle.

All distilled from the 2026-11-11 CI-migration field notes: eight
verification-layer breadcrumbs, none caught by the structural gate, each
mapped to a mechanism (gate check, template clause, doctrine, or script
encoding).
