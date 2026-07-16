# RUNBOOK — Bootstrap or adopt agentic-mode in any repo

This is the single executable entry point for the **agentic-mode documentation
contract**: a small set of layered, cross-linked docs that let any collaborator
— human or agent, in any tool — reach productive context top-down with **no chat
history**. Point any agent (or read it yourself) at this file and run it with
nothing but file reads, shell commands, and questions to your user.

The contract owns *What* (repo facts, behavior contract) and *Done* (acceptance
evidence); it never dictates *How/Who* (which tool, model, or dispatch the
executor uses). That boundary is what keeps it portable across every harness.
The doctrine behind every rule lives in [`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md)
— read it before Phase B. Hard-won field lessons live in
[`doctrine/FIELD-NOTES.md`](doctrine/FIELD-NOTES.md).

## Definitions

- **TOOLKIT** — this repository. It carries everything you need: this RUNBOOK,
  `doctrine/` (the doctrine), `templates/` (all document templates), and
  `checker/` (the mechanical gate). Nothing is ever written into TOOLKIT.
- **TARGET** — the repository you are bootstrapping. All generated files are
  written into TARGET. Ask your user if TARGET is ambiguous.

Runtime requirements: Python 3 (standard library only) for the checker; git.
Nothing else — no network access, no package installs.

## Layout this produces in TARGET

```
AGENTIC-MODE.md              # resident root index + precedence + enforcement pointer
AGENTS.md                    # repo facts + co-op contract (lean; machine-enforced line limit)
agentic-mode/config.json     # the single machine-readable config (schema below)
agentic-mode/SELF-TEST.md    # coherence gate + four guardrails + read-back probe
docs/REQUIREMENTS.md         # behavior contract, stable IDs, append-only iteration history
docs/USER_GUIDE.md | docs/API_REFERENCE.md   # observable surface (by project.type)
docs/VALIDATION.md           # per-feature done evidence (seeded empty)
docs/WORKFLOW.md             # platform review loop (copied ~as-is from a WORKFLOW template)
docs/architecture.json       # optional component graph (by project.type / need)
scripts/check_agentic_docs.py  # the checker, copied verbatim from TOOLKIT/checker/
.gitlab-ci.yml | .github/workflows/agentic-docs.yml   # CI gate (unless the profile skips it)
```

## config.json — schema v1 (the single source of machine truth)

```json
{
  "schema_version": 1,
  "project": {"name": "str", "type": "cli|library|web-service|docs-only", "description": "str"},
  "id": {"prefix": "[A-Z]{2,6}"},
  "docs": {"index": "AGENTIC-MODE.md", "readme": "README.md", "agents": "AGENTS.md",
           "requirements": "docs/REQUIREMENTS.md", "user_guide": "docs/USER_GUIDE.md",
           "validation": "docs/VALIDATION.md", "workflow": "docs/WORKFLOW.md",
           "architecture": "docs/architecture.json or null"},
  "bilingual": {"enabled": false, "secondary_language": "zh-TW"},
  "checks": {
    "line_limits": {"agents": 200},
    "deny_words": [],
    "harness_neutrality": {"enabled": true, "extra_deny": []},
    "url_allowlist": [],
    "forbid_ipv4": false,
    "ipv4_allowlist": ["127.0.0.1", "0.0.0.0"],
    "forbid_local_paths": false,
    "iteration_history": {"enabled": false, "heading": "Iteration History"},
    "commands": [{"run": "str", "must_appear_in": ["agents", "readme"]}],
    "entrypoints": []
  },
  "ci": {"platform": "gitlab|github|none"}
}
```

The checker is invoked exactly one way:
`python scripts/check_agentic_docs.py --config agentic-mode/config.json`.
(`forbid_ipv4`, `forbid_local_paths`, and `iteration_history` are opt-in leak /
continuity sweeps — see [`checker/config.example.json`](checker/config.example.json)
and the checker's module docstring.)

## Tooling preference for file inspection

Prefer simple shell tools first: `echo`, `jq`, `sed`, `head`, `grep`, `sort`,
`uniq`, `tr`. Use a Python script only when those are insufficient.

---

## Decide first: bootstrap vs. adopt

- **Bootstrap** — TARGET has none (or almost none) of the layout above. Run the
  full four-phase protocol.
- **Adopt** — TARGET already has some of these docs (a hand-written `AGENTS.md`,
  a `README`, ad-hoc `docs/`). Do **not** overwrite. Jump to **Adopt mode**,
  inventory what exists, and fill only the gaps.

If unsure, list the target paths. A hit on any **contract doc** (AGENTS,
REQUIREMENTS, VALIDATION, WORKFLOW, AGENTIC-MODE, a surface guide) → adopt. A
`README.md` alone does not force adopt: a trivial stub (≤15 lines, no structure
worth preserving) folds into the bootstrap-generated README; a substantive
README → adopt.

---

## Phase A — Gather inputs (repo scan + 10-question interview)

Scan TARGET first; only ask what the scan cannot derive. The scan is
**language-agnostic** — never assume a stack.

- **Entry points / surface.** How is the project run or imported? Root scripts, a
  `bin/`, a `main`/`cmd` dir, package-manifest bin/scripts, console-scripts, an
  exported library index, a service entrypoint. List dirs and read the manifest.
- **Existing commands.** Read build/test/lint commands from wherever TARGET
  declares them (Makefile, package scripts, `pyproject`/`tox`, `justfile`,
  existing CI). **Mine, do not invent.**
- **Test surface.** Locate tests/fixtures/examples — each encodes a behavior that
  will need a requirement ID.
- **Platform.** Inspect the remote to tell GitLab vs GitHub; this decides which
  WORKFLOW template to copy.
- **Existing docs.** Check the target paths so you know bootstrap vs adopt.

Then ask the user **only** these 10 questions. **Question 1 is always first** —
it sets the rigor for everything after:

1. **Co-op profile** — `full` / `docs-only` / `light`?
   - `full`: CI gate runs on every change; append-only provenance enforced. *(default)*
   - `docs-only`: **no CI gate** (checker still runnable by hand); append-only enforced.
   - `light`: **no append-only ritual** (iteration history + per-feature VALIDATION encouraged, not required); CI optional.
2. **Project type** — `cli` / `library` / `web-service` / `docs-only`? (Selects the observable-surface doc: `cli`→USER_GUIDE-cli, `library`→API_REFERENCE, `web-service`→USER_GUIDE-web, `docs-only`→none.)
3. **CI platform** — `gitlab` / `github` / `none`? `none` governs only the CI **gate**; the WORKFLOW doc still follows the team's **actual review platform**.
4. **Primary language + test/build command** — the one command that compiles/builds and the one that runs tests, verbatim. No build step? Agree on a cheap static sanity command (syntax check, lint, byte-compile) to fill `{{BUILD_CMD}}`. A placeholder must never survive unresolved.
5. **One-line purpose + audience** — internal tool vs external product; who reads/uses it.
6. **Entry points** — which is primary maintained vs secondary/legacy.
7. **Component name + ID prefix** for REQUIREMENTS (`^[A-Z]{2,6}$`, one prefix per component).
8. **Problem statement + Goals / Non-Goals** — not derivable from code.
9. **Bilingual?** — one clean language, or two full tracks? If two, name the secondary-language header.
10. **Runtime placeholders + neutrality** — which placeholders TARGET needs (e.g. `<package.name>`, `<device-serial>`), and whether the harness-neutrality sweep (and optional IPv4 / machine-path leak sweeps) should run.

Record the answers as the **bootstrap input bundle** and write them into
`TARGET/agentic-mode/config.json`.

---

## Phase B — Produce docs in dependency order (each gated before the next)

Read [`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md) now if you have
not. For each doc: open the matching `TOOLKIT/templates/*.template.md`, resolve
every `{{PLACEHOLDER}}` from the bundle, write the file into TARGET, then run its
inline gate. **Do not advance on a failed gate.** Production order:

1. **`docs/architecture.json`** *(optional — skip unless Q2/need calls for it; set `docs.architecture: null`)*. Gate: every `connection.from`/`.to` resolves; every component label naming a real symbol exists in source; JSON parses.
2. **`docs/WORKFLOW.md`** — **copied ~as-is** from `WORKFLOW-<platform>.template.md`. Substitute the H1 platform name, the `Template-Source:` marker, and every `{{PLACEHOLDER}}` in the body (build/test/smoke commands, prefix, bilingual conditionals). Do **not** re-author its prose — the review loop, comment style, and red lines are platform constants.
3. **`docs/REQUIREMENTS.md`** — Problem/Goals/Non-Goals, enumerated `{{PREFIX}}-001..N` requirements (one per observable behavior), domain/event model, **empty** Iteration History (append-only from here), acceptance criteria, verification commands. Gate: every entry-point behavior maps to ≥1 ID; if bilingual, both tracks share identical ID set/count/order.
4. **`docs/USER_GUIDE.md` or `docs/API_REFERENCE.md`** — the observable surface, template chosen by `project.type`. Each behavior subsection cites its owning `{{PREFIX}}-XXX`. Gate: every cited ID exists in REQUIREMENTS; surface tables match source 1:1.
5. **`README.md`** — onboarding: entry table, quick start, architecture overview *derived from the JSON when present*, agent-onboarding pointer, verification commands, neutrality checklist, doc cross-links. Gate: every quick-start command appears in the surface doc; neutrality sweep clean.
6. **`AGENTS.md`** — **lean**: repo facts + the co-op contract (change-flow, sign-off, Stop-and-Ask). *What/Done* only — **no** generic agent discipline, **no** platform-CLI rules. Gate: every Key-Files path exists; every dev command runs clean; **≤ `checks.line_limits.agents` lines**; no platform-CLI rule leaked in.
7. **`docs/VALIDATION.md`** — seed **empty** with the file H1 and the per-feature block template in a comment, placeholders resolved to TARGET's real prefix and commands. Gate: file exists; seed parses; no `<command>`/`{{PLACEHOLDER}}` left.

Also write **`AGENTIC-MODE.md`** (root index) and **`agentic-mode/SELF-TEST.md`**
(from their templates). These are resident meta files, not part of the chain.

---

## Phase C — Wire enforcement and run the checker clean

1. **Copy the checker** verbatim: `TOOLKIT/checker/check_agentic_docs.py` →
   `TARGET/scripts/check_agentic_docs.py`.
2. **Place the CI gate** unless the profile skips it (`docs-only`/`light` with
   `ci.platform: none`):
   - gitlab → `templates/ci-gitlab.template.yml` → `.gitlab-ci.yml`
   - github → `templates/ci-github.template.yml` → `.github/workflows/agentic-docs.yml`
3. **Run** `python scripts/check_agentic_docs.py --config agentic-mode/config.json`.
   Fix the offending **doc**, not the checker, and re-run until it exits clean.
   A failed row blocks hand-off. (`checks.entrypoints` byte-compiles `.py`
   entries; non-Python entrypoints get an existence check only.)
4. **Placeholder sweep.** The checker does not govern `AGENTIC-MODE.md`,
   `agentic-mode/SELF-TEST.md`, or the CI file — sweep every generated file
   yourself: `grep -rn '{{'` over the index, AGENTS, README, `docs/`,
   `agentic-mode/`, and the CI file must return **nothing**.

---

## Phase D — Hand off to self-operation

Once the checker is clean, TARGET is collaborator-operable with no chat history.
Summarize for the user:

- **What was created** — the file list, the chosen profiles, and the one
  verification command: `python scripts/check_agentic_docs.py --config agentic-mode/config.json`.
- **The daily loop** — for any behavior change: edit code → append/update the
  requirement ID in REQUIREMENTS (with an Iteration History entry) → update the
  USER_GUIDE/API_REFERENCE subsection citing that ID → update README quick-start
  if the surface changed → **append** a VALIDATION block citing the ID +
  issue/MR-PR number → run the checker → move the change through
  `docs/WORKFLOW.md`. The ID is the join key.
- **The guardrails** — point them at `agentic-mode/SELF-TEST.md`: two failed
  fixes of one check → stop and escalate; the Stop-and-Ask list; "uncertainty =
  not done"; never mark done because budget/time ran out.

---

## Adopt mode — merging into a repo that already has docs

TARGET already carries some layers. **Merge, never clobber.**

1. **Inventory.** Map what exists to the target layout. Record path + which
   contract role it fills.
2. **Do not overwrite.** Treat every existing file as authoritative for its own
   content. Never replace a hand-written doc wholesale with a template.
3. **Fill gaps only.** For each **missing** layer, generate it from its template
   (Phase B rules and gates apply per file). For each **partial** layer, add only
   the missing contract pieces — e.g. an existing REQUIREMENTS without stable IDs
   gets an ID column and an (empty, append-only) Iteration History appended; an
   existing AGENTS gains the co-op-contract / Stop-and-Ask section if absent, and
   is trimmed toward the line limit only with the user's ok.
4. **Reconcile the config.** Point `docs.*` at wherever the real files live
   (names may differ from defaults — the config is the indirection layer).
5. **Wire enforcement + converge.** Copy the checker, add the CI gate per
   profile, run the checker, and close the reported gaps until clean. Report
   every gap you filled and every existing file you left untouched.

Adopt is deliberately conservative: the win is coherence and enforceability, not
a rewrite.

---

## Hard rules

- **Harness neutrality (iron rule).** Nothing generated — no template output, no
  doctrine — may name a specific agent product, model, or proprietary tool
  mechanism. Write to the weakest common primitive shared by every collaborator:
  *read a file, run a command, open a merge/pull request.* Say "any agent or
  human collaborator." Harness-specific packaging lives only under `adapters/`.
- **Gate before advancing.** Every Phase-B doc passes its inline gate before the
  next is produced. Phase C must exit the checker clean before Phase D.
- **The config is the single machine truth.** Any command, path, prefix, or limit
  a doc references must match `agentic-mode/config.json`.
- **Never advance past a failed gate.** If the same check fails after two fix
  attempts, stop and escalate to your user with the failure trail.

## Done means

The checker exits 0 in TARGET, the placeholder sweep finds nothing, and your
hand-off summary tells the user the daily loop above.
