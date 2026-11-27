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
  `checker/` (the mechanical checker). Nothing is ever written into TOOLKIT.
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
docs/WORKFLOW.md             # platform review loop (ported as-is from a WORKFLOW template)
docs/architecture.json       # optional component graph (by project.type / need)
scripts/check_agentic_docs.py  # the checker, copied verbatim from TOOLKIT/checker/
.gitlab-ci.yml | .github/workflows/agentic-docs.yml   # CI gate (placed unless ci.platform: none)
```

The doc-set profile (Phase A, question 2) decides how much of this layout
exists: a Lite target has neither the surface doc nor `docs/WORKFLOW.md`, and
only a Full target has `docs/architecture.json` (Phase B). Where a template
sentence depends on one of those three docs, it sits inside a `{{IF ...}}`
region (BOOTSTRAP-CORE, "Conditional Text in Templates").

## config.json — schema v1 (the single source of machine truth)

```json
{
  "schema_version": 1,
  "project": {"name": "str", "type": "cli|library|web-service|docs-only", "description": "str"},
  "id": {"prefix": "[A-Z]{2,6}"},
  "docs": {"index": "AGENTIC-MODE.md or null", "readme": "README.md or null",
           "agents": "AGENTS.md or null",
           "requirements": "docs/REQUIREMENTS.md — required; never null",
           "user_guide": "docs/USER_GUIDE.md or null (surface rule below)",
           "api_reference": "docs/API_REFERENCE.md or null (surface rule below)",
           "validation": "docs/VALIDATION.md — required; never null",
           "workflow": "docs/WORKFLOW.md or null",
           "architecture": "docs/architecture.json or null"},
  "bilingual": {"enabled": false,
                "primary_heading": "## English", "secondary_heading": "## 繁體中文"},
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
  "ci": {"platform": "gitlab|github|none", "runners": []}
}
```

Under `docs`, a value is a path or `null`. `requirements` and `validation` must
be declared as non-empty paths — `null` or a missing key is a config error. The
surface doc selected by `project.type` must be a non-empty path or an explicit
`null` — the Lite opt-out, spelled out under **Undeclared dependencies** below —
and the other surface key is never required. Every other key (`index`, `readme`,
`agents`, `workflow`, `architecture`) takes a path, `null`, or no key at all,
and an undeclared doc gets no scans. Two edges are not config errors. A doc
that a rule under `checks.commands` names in `must_appear_in` is skipped there
only when it is declared `null`. Left out of `docs` entirely, it raises a
`command-consistency` finding. `agents` left `null` while
`checks.line_limits.agents` is set is a `line-limit` finding.

The checker is invoked exactly one way:
`python scripts/check_agentic_docs.py --config agentic-mode/config.json`.
(`forbid_ipv4`, `forbid_local_paths`, and `iteration_history` are opt-in leak /
continuity sweeps; `ci.runners` is the opt-in runner-declaration sweep — when
non-empty, a governed doc must carry a matching `<!-- ci-runners: ... -->`
marker. The workflow doc carries it by convention; the checker reads it in any
governed doc. See [`checker/config.example.json`](checker/config.example.json)
and the checker's module docstring.)

The config is validated before any check runs; a violation exits `2` naming the
offending key and a remedy. Two families are rejected:

- **Wrong types.** Every field the checker reads must carry the right type:
  `docs.*` is a string or `null`, `checks.line_limits.*` an integer, list
  fields lists of strings, every `enabled` / `forbid_*` switch an actual
  boolean — a truthy `"false"` string cannot flip an opt-in check on, and a
  falsy `false` cannot silently stand in for an empty list — and
  `project.type` one of `cli` / `library` / `web-service` / `docs-only`.
  A wrong type is
  an error — never a silent coercion and never a traceback. A `null` on an
  optional field means "not provided": the optional list fields and the
  `harness_neutrality` / `iteration_history` objects fall back to their
  built-in default (empty lists and disabled objects — except
  `checks.ipv4_allowlist`, whose default is the built-in loopback /
  any-address allowlist), and the string fields with a built-in default
  (`iteration_history.heading`, `bilingual.primary_heading` /
  `secondary_heading`) take that default. A `null` on a structural section
  (`docs`, `id`, `bilingual`, `checks`, `project`, `line_limits`, `commands`)
  is itself a type error.
- **Undeclared dependencies.** An active check's dependent docs must be
  declared under `docs` — a missing key or `null` silently disabling a check
  is how a gate degrades to nothing. `id-continuity` requires
  `docs.requirements`, `docs.validation`, and the observable-surface doc
  selected by `project.type`: `cli` / `web-service` require
  `docs.user_guide`, `library` requires `docs.api_reference`, and
  `docs-only` requires neither (no surface doc — REQUIREMENTS carries the
  surface). The type-selected surface doc admits exactly one explicit
  exemption: declaring it as `null` (the key present, value `null`) is the
  **Lite-profile opt-out** — the doc is deliberately absent, so
  `doc-presence` skips it, cross-doc references do not scan it, and a
  `command-consistency` rule's `must_appear_in` target naming it withdraws.
  A merely *missing* surface key — and a `null` on any other dependency
  (`docs.requirements`, `docs.validation`) — is still an error.
  `iteration_history` (when enabled) requires `docs.requirements`.
  When `project.type` is absent the checker takes the strict reading (a
  surface project, so `docs.user_guide`) and the dependency stays. Checks
  without a disable switch tell you to declare the path; `iteration_history`
  offers its `enabled: false` switch instead.

On the doc side, a governed prose doc whose fence scan ends inside a block is
itself a `neutrality` finding at the opening fence line — an unclosed fence
would make the deny-word scan of the remainder unreliable, so it is never
skipped silently. Both backtick and tilde fences are recognized as code
blocks, at any indentation (deliberately wider than CommonMark's three-space
indent cap, so code samples nested in lists keep their exemption); a closing
fence repeats the opening fence's character and may trail only spaces and
tabs — for the deny-word exemption and this finding alike. The widening
cuts both ways: prose between a stray deeply indented, balanced fence pair
is silently exempt from the scan — balanced fences raise no finding. Treat
an unexpected exemption as a cue to look for stray indented fences. The
`agentic-gate: allow` marker exempts only a line's content: a fence line
carrying it still opens or closes its block for every check.

## Tooling preference for file inspection

Prefer simple shell tools first: `echo`, `jq`, `sed`, `head`, `grep`, `sort`,
`uniq`, `tr`. Use a Python script only when those are insufficient.

---

## Decide first: bootstrap vs. adopt

- **Bootstrap** — TARGET has none (or almost none) of the layout above. Run the
  full four-phase protocol.
- **Adopt** — TARGET already has some of these docs (a hand-written `AGENTS.md`,
  a `README`, ad-hoc `docs/`). Do **not** overwrite. Jump to **Adopt mode**,
  inventory what exists, and fill only the gaps. If TARGET was rendered from
  these templates before (its docs carry `Template-Source:` markers) and this
  run changes its doc-set profile, go to **Upgrading the doc-set profile**
  instead.

If unsure, list the target paths. A hit on any **contract doc** (AGENTS,
REQUIREMENTS, VALIDATION, WORKFLOW, AGENTIC-MODE, a surface guide) → adopt. A
`README.md` alone does not force adopt: a trivial stub (≤15 non-blank lines and
no `##` headings) folds into the bootstrap-generated README; anything longer, or
containing any heading, → adopt.

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

1. **Co-op profile** — `full` / `docs-only` / `light`? Sets how strictly the **append-only ritual** binds; it does **not** decide the CI gate — gate placement follows `ci.platform` (Q3), for every profile.
   - `full`: append-only provenance enforced. *(default; repo expected to outlive one feature cycle.)*
   - `docs-only`: append-only provenance enforced. *(docs/knowledge repos.)*
   - `light`: **no append-only ritual** — iteration history + per-feature VALIDATION encouraged, not required.
2. **Project type + doc-set profile** — `cli` / `library` / `web-service` / `docs-only`, and `Lite` / `Standard` / `Full`? (The type selects the observable-surface doc: `cli`→USER_GUIDE-cli, `library`→API_REFERENCE, `web-service`→USER_GUIDE-web, `docs-only`→none. The doc-set profile selects how many layers Phase B seeds, per the doctrine's doc-set table — Lite, Standard, or Full — and is independent of the co-op profile in Q1. Default `Full` for a repo expected to outlive one feature cycle, as the doctrine's table says.)
3. **CI platform** — `gitlab` / `github` / `none`? `none` governs only the CI **gate**; the WORKFLOW doc, when the doc-set profile seeds one, still follows the team's **actual review platform**.
4. **Primary language + test/build command** — the one command that compiles/builds and the one that runs tests, verbatim. No build step? Agree on a cheap static sanity command (syntax check, lint, byte-compile) to fill `{{BUILD_CMD}}`. A placeholder must never survive unresolved.
5. **One-line purpose + audience** — internal tool vs external product; who reads/uses it.
6. **Entry points** — which is primary maintained vs secondary/legacy.
7. **Component name + ID prefix** for REQUIREMENTS (`^[A-Z]{2,6}$`, one prefix per component).
8. **Problem statement + Goals / Non-Goals** — not derivable from code.
9. **Bilingual?** — one clean language, or two full tracks? If two, name the secondary-language header.
10. **Runtime placeholders + neutrality** — which placeholders TARGET needs (e.g. `<package.name>`, `<device-serial>`), and whether the harness-neutrality sweep (and optional IPv4 / machine-path leak sweeps) should run.

Record the answers as the **bootstrap input bundle** and write them into
`TARGET/agentic-mode/config.json`. The doc-set profile has no key of its own:
it reaches config only as the `null`s under `docs`. Write the whole `docs` block
here, every layer the profile defers already `null`, before any doc is rendered:
templates read that block, and nothing else, to learn which layers exist
(BOOTSTRAP-CORE, "Conditional Text in Templates").

---

## Phase B — Produce docs in dependency order (each gated before the next)

Read [`doctrine/BOOTSTRAP-CORE.md`](doctrine/BOOTSTRAP-CORE.md) now if you have
not. The **doc-set profile** (Q2) decides which steps run, per the doctrine's
doc-set table: every target runs steps 3, 5, 6, and 7 (Lite), Standard adds
steps 2 and 4, and Full adds step 1 as well. For each doc: open the
matching `TOOLKIT/templates/*.template.md`, resolve every `{{PLACEHOLDER}}`
from the bundle, write the file into TARGET, then run its inline gate. **Do not
advance on a failed gate.** A step whose doc is `null` under `docs` in config
is skipped and leaves no file behind. The other templates name that doc only
inside `{{IF ...}}` regions: resolve them per BOOTSTRAP-CORE, "Conditional Text
in Templates", keeping the stand-in where one is written, so no
`{{PLACEHOLDER}}` survives. Production order:

1. **`docs/architecture.json`** *(Full profile — Lite and Standard skip this step; under Full the doctrine still gates the doc on `project.type` and need. Any skip sets `docs.architecture: null` before any template is rendered.)* No template file exists for it; the shape below is its only statement. Start from the skeleton. The doctrine derives the component list from the entry points, AGENTS Key Files, and README Main Components; AGENTS and README are written in steps 5 and 6, so mine the list from the source's entry points now and keep the three in step when you write them:

   ```json
   {
     "components": [
       { "id": "<entry-point path>", "label": "<symbol>", "region": "<region id>",
         "position": { "x": 0, "y": 0 }, "size": { "w": 4, "h": 2 } }
     ],
     "connections": [
       { "from": "<component id>", "to": "<component id>", "label": "<what flows>" }
     ],
     "regions": [
       { "id": "<region id>", "label": "<boundary name>" }
     ]
   }
   ```

   | Field | Rule |
   |---|---|
   | `components[].id` | Stable; never renamed. An entry point uses its repo-relative path — the one the README entry table prints. Any other component (a store, a client, a module) uses a stable name of the same kind: its path for a file, its symbol for a module. |
   | `components[].label` | What a reader looks for in source. When it names a symbol, the symbol exists. |
   | `components[].region` | Optional; an `id` from `regions`. |
   | `components[].position`, `.size` | Renderer coordinates in any consistent unit; they change only in an intentional restructure. |
   | `connections[].from`, `.to` | Each is a `components[].id`. That is what "resolves" means. |
   | `connections[].label` | What flows. When it names a flag, the flag exists. |
   | `regions[]` | Optional boundaries; README's Architecture Overview lists their labels. |

   Gate: JSON parses; every `connections[].from` and `.to` is a `components[].id`; every component or connection label that names a symbol or a flag exists in source.
2. **`docs/WORKFLOW.md`** *(Standard and Full — Lite skips this step and `docs.workflow` stays `null`)* — **ported as-is** (verbatim except its declared substitution points) from `WORKFLOW-<platform>.template.md`. The platform is the team's review platform, not `ci.platform`: when neither Q3 nor the remote settles it, ask which one before porting. Substitute the H1 platform name, the `Template-Source:` marker, and every `{{PLACEHOLDER}}` in the body (build/test/smoke commands, prefix, bilingual conditionals). Resolve the CI-runners line from config `ci.runners` (comma-separated runner names), or **delete the whole line** when config declares no runners — the doc gate checks its `ci-runners:` marker against config. While no WORKFLOW doc is seeded and config declares runners, that line sits in README instead: the README template's stand-in for this doc carries it. The checker reads the marker in any governed doc. Do **not** re-author its prose — the review loop, comment style, and red lines are platform constants. Gate: no `{{` remains in the doc, and it differs from its template only at its declared substitution points.
3. **`docs/REQUIREMENTS.md`** — Problem/Goals/Non-Goals, enumerated `{{PREFIX}}-001..N` requirements (one per observable behavior), domain/event model, **empty** Iteration History (append-only from here), acceptance criteria, verification commands. Gate: every entry-point behavior maps to ≥1 ID; while no surface doc is seeded, every row carries, in a code span, the command / call that exercises it; if bilingual, both tracks share identical ID set/count/order.
4. **`docs/USER_GUIDE.md` or `docs/API_REFERENCE.md`** *(Standard and Full)* — the observable surface, template chosen by `project.type`. Under Lite, do not write it: the type-selected key stays the explicit `null` Phase A declared (`docs.user_guide: null` for `cli` / `web-service`, `docs.api_reference: null` for `library`) — the Lite opt-out, with REQUIREMENTS carrying the surface until the upgrade. `docs-only` has no surface doc at any profile. `{{SURFACE_DOC_ROLE}}` is the kind of surface: `commands, flags, and output` for a CLI, `endpoints and screens` for a web service, `the public API` for a library. Each behavior subsection cites its owning `{{PREFIX}}-XXX`. A doc you write must also be declared: keep its key at the real path, because a written doc left `null` gets no scans. Gate: every cited ID exists in REQUIREMENTS; surface tables match source 1:1.
5. **`README.md`** — onboarding: entry table, quick start, architecture overview *derived from the JSON when present*, agent-onboarding pointer, verification commands, neutrality checklist, doc cross-links. Gate: every quick-start command appears in the surface doc (under Lite or `docs-only`, in the REQUIREMENTS row that carries that surface); neutrality sweep clean. While no surface doc is seeded, a quick-start command's `must_appear_in` names `readme` and `requirements` instead of the surface key: a rule that targets only the unseeded surface key withdraws.
6. **`AGENTS.md`** — **lean**: repo facts + the co-op contract (change-flow, sign-off, Stop-and-Ask). *What/Done* only — **no** generic agent discipline, **no** platform-CLI rules. Gate: every Key-Files path exists; every dev command runs clean; **≤ `checks.line_limits.agents` lines**; no platform-CLI rule leaked in.
7. **`docs/VALIDATION.md`** — seed **empty** with the file H1 and the per-feature block template in a comment, placeholders resolved to TARGET's real prefix and commands. Gate: file exists; seed parses; no `<command>`/`{{PLACEHOLDER}}` left.

Also write **`AGENTIC-MODE.md`** (root index) and **`agentic-mode/SELF-TEST.md`**
(from their templates), under every doc-set profile. These are resident meta
files, not part of the chain. Gate: every path in the index's Doc Inventory
and precedence tables exists, and every section a precedence cell names exists.
Render their body prose in the TARGET's chosen language, but keep the canonical
English section headings and the `Template-Source:` markers exactly as the
templates carry them — headings are cross-repo reference anchors (see
BOOTSTRAP-CORE, "Rendering Language and Canonical Headings").

If TARGET also seeds a local review canon (an optional `CODE-REVIEW.md`),
seed it with an **empty** "what failure looks like" section — one line per
sensitive area — for the code owner to fill in.

---

## Phase C — Wire enforcement and run the checker clean

1. **Copy the checker** verbatim: `TOOLKIT/checker/check_agentic_docs.py` →
   `TARGET/scripts/check_agentic_docs.py`.
2. **Place the CI gate whenever `ci.platform` is `gitlab` or `github`** — for
   every co-op profile and every doc-set profile, `docs-only` included; the
   placed gate runs the checker on **all** changes (docs-only changes are not
   exempt). The only thing that skips a CI file is `ci.platform: none`:
   - gitlab → `templates/ci-gitlab.template.yml` → `.gitlab-ci.yml`
   - github → `templates/ci-github.template.yml` → `.github/workflows/agentic-docs.yml`

   This gate is the toolkit's whole CI automation at every profile: it runs the
   SELF-TEST §A command, and §B stays manual.
3. **Run** `python scripts/check_agentic_docs.py --config agentic-mode/config.json`.
   Fix the offending **doc**, not the checker, and re-run until it exits clean.
   A failed row blocks hand-off. (`checks.entrypoints` byte-compiles `.py`
   entries; non-Python entrypoints get an existence check only.) Then check by
   hand that every path that README, AGENTS, and the index name as part of
   TARGET exists, and that every section their pointers name exists (the index's
   precedence table, README's cross-links); the checker checks neither. A path
   outside TARGET is not checked: the toolkit's own docs, or a file the program
   writes at run time.
4. **Placeholder sweep.** No check in the checker looks for a leftover
   placeholder, in any file: it scans a declared index for IDs and deny words
   but never for `{{`, and it does not scan `agentic-mode/SELF-TEST.md` or the
   CI file at all. Sweep every generated file yourself: `grep -rn '{{'` over
   the index, AGENTS, README, `docs/`, `agentic-mode/`, and the CI file, when
   one was placed, must return **nothing**. In Adopt mode, sweep the files you
   generated or added pieces to; a hand-written doc you did not touch is not
   swept. That sweep also catches an unresolved region.

---

## Phase D — Hand off to self-operation

Once the checker is clean, TARGET is collaborator-operable with no chat history.
Summarize for the user:

- **What was created** — the file list, the chosen profiles, and the one
  verification command: `python scripts/check_agentic_docs.py --config agentic-mode/config.json`.
- **The daily loop** — for any behavior change: edit code → append/update the
  requirement ID in REQUIREMENTS (with an Iteration History entry) → update the
  USER_GUIDE/API_REFERENCE subsection citing that ID (under Lite or
  `docs-only` there is none; the requirement row carries the surface) → update README quick-start if the
  surface changed → **append** a VALIDATION block citing the ID + issue/MR/PR
  number → run the checker → move the change through `docs/WORKFLOW.md`
  (Standard and Full; Lite has no WORKFLOW doc). The ID is the join key.
- **The guardrails** — point them at `agentic-mode/SELF-TEST.md`: two failed
  fixes of one check → stop and escalate; the Stop-and-Ask list; "uncertainty =
  not done"; never mark done because budget/time ran out.

---

## Adopt mode — merging into a repo that already has docs

TARGET already carries some layers. **Merge, never clobber.** If TARGET was
rendered from these templates (its docs carry `Template-Source:` markers) and
the run changes its doc-set profile, use **Upgrading the doc-set profile**
below: this mode never overwrites, so it cannot move a rendered doc to a new
profile.

1. **Inventory.** Map what exists to the target layout. Record path + which
   contract role it fills. Run the Phase A scan and interview first if they have
   not run: steps 3 and 4 need their answers.
2. **Do not overwrite.** Treat every existing file as authoritative for its own
   content. Never replace a hand-written doc wholesale with a template.
3. **Reconcile the config.** Point `docs.*` at wherever the real files live
   (names may differ from defaults — the config is the indirection layer). Seed
   every layer that the doc-set profile includes, and keep every layer that
   the target already has, even a layer that the profile does not include.
   Declare a path for each of those layers, and for the resident index
   (`AGENTIC-MODE.md`). The resident index and `agentic-mode/SELF-TEST.md`
   belong to every doc-set profile: never declare `docs.index` `null`. Declare
   `null` only for a layer that neither exists nor belongs to the profile.
   `null` means that no such doc exists. Templates read this block to learn
   which layers exist, so write all of it before step 4.
4. **Fill gaps only.** For each layer that the profile includes and that the
   target still lacks, and for each of the two resident files (`AGENTIC-MODE.md`,
   `agentic-mode/SELF-TEST.md`) when it is missing, generate it from its template
   (Phase B rules and gates apply per file). For each **partial** layer, add
   only the missing contract pieces, under the template's headings and without
   moving any hand-written text — e.g. an existing REQUIREMENTS without stable
   IDs gets an ID column and an (empty, append-only) Iteration History appended;
   an existing README gains the template's missing sections after its own text,
   and its hand-written quick start gets the `Quick Start` heading above it; an
   existing AGENTS gains the template's missing sections by their headings, from
   Project Scope and Key Files through MR / PR Governance and Git Hygiene, and
   is trimmed toward the line limit only with the user's ok. A doc you added
   pieces to carries that template's `Template-Source:` marker from then on, so
   a later upgrade finds its regions.
5. **Wire enforcement + converge.** Copy the checker, add the CI gate whenever
   `ci.platform` is `gitlab` or `github` (Phase C step 2), run the checker and
   close the reported gaps until clean, then run the Phase-C hand check of paths
   and section names and the placeholder sweep. Report every gap you filled and
   every existing file you left untouched, and summarize as Phase D does.

Adopt is deliberately conservative: the win is coherence and enforceability, not
a rewrite.

---

## Upgrading the doc-set profile

When a trigger in the doctrine's doc-set table fires, move up to the row the request names. The repo's row is the highest row of that table whose every layer that `project.type` does not rule out is upgraded. When the repo's row is the requested row or above it, only the first two cases below can apply. A layer is upgraded when its proof in step 4 holds: it is declared, every region for it is ported, and no stand-in text or stale fill-in sentence for it remains. The docs must first be at the toolkit's current template versions: when a `Template-Source:` marker names an older version, follow "Upgrading an adopted repo to a newer toolkit version" first. Then start with the proof in step 4, which changes nothing, for each layer of the requested row that `project.type` does not rule out:

- The proof holds, and an Iteration History entry and a VALIDATION block already record the upgrade: there is nothing to do.
- The proof holds, and either record is missing: do step 5 only.
- The layer's path is already declared but the proof fails: an earlier run stopped mid-way. Run all five steps again; their guards skip what is already done.
- Otherwise: run all five steps once, covering every layer that the requested row adds and that `project.type` does not rule out.

1. **Write the layer** with its Phase B step and gate, in Phase B order, and declare the layer's path under `docs` in the same step. There is no interview bundle here: resolve placeholders from the target's own config and AGENTS Development Commands. A written doc that is left `null` gets no scans. A layer whose file already exists keeps that file, declared or not; a hand-written doc is never rewritten. Everything else in this step still applies to it: the declaration, the `must_appear_in` move, and the gate. For a surface doc, also move each quick-start command's `must_appear_in` target from `requirements` to the surface key, so the new doc becomes the one the checker reads. The quick-start commands are the ones README's Quick Start lists; other command rules stay as they are. The surface key is `docs.user_guide`, or `docs.api_reference` for a library. For the WORKFLOW doc, port the platform template that matches the team's review platform, and ask which one if the interview did not settle it.
2. **Move what the stand-in held for the layer.** The content a stand-in kept for the layer now has its home in the new doc: the CI-runners line leaves README for the WORKFLOW doc, and the surface doc carries the exercising commands it took from the requirement rows when step 1 wrote it. Remove every stand-in whose region has an empty first branch: search the templates for the layer's opener followed directly by `{{ELSE}}`. What a stand-in wrote for itself stays where it is as an allowed mirror. For a surface doc that is the exercising commands in the requirement rows. For the architecture doc those are README Main Components, README Data Flow, and AGENTS Key Files. `AGENTS.md` keeps its MR / PR Governance and Git Hygiene sections at every profile. The Controlled-Duplication table in BOOTSTRAP-CORE lists these mirrors.
3. **Port the regions.** Search the templates for `{{IF <PLACEHOLDER>}}` with the new layer's placeholder: `SURFACE_DOC_PATH` for a surface doc, `WORKFLOW_PATH` for the WORKFLOW doc, `ARCHITECTURE_PATH` for the architecture doc. Each region is one item to port into the doc that was rendered from that template, and one line can hold several regions. Where the doc carries the stand-in, replace it with the first branch. Where the region left nothing behind, add its first branch where the region sits in the template. A region whose first branch is empty was handled in step 2. If the doc already carries the first branch where the region sits, leave it as it is, so a re-run after an interruption adds nothing twice. Then re-read the fill-in text you wrote at bootstrap that describes the doc set: it sits in no region, and it is found where a placeholder asked for it, in README's sentence listing what `docs/` contains, its onboarding text, AGENTS Project Scope and Key Files, and the index's inventory prose. Name the new layer where it belongs, and rewrite any sentence that still describes the doc set as it was. Re-run the Phase B gate of every doc you changed.
4. **Prove the upgrade.** Run the checker, the Phase-C hand check of paths and section names, and the Phase-C placeholder sweep. Then check the regions themselves, because the checker does not. Run `python3 TOOLKIT/tests/check_template_renders.py --target TARGET` to search each doc for its own template's regions. It proves only what a template's own wording can match, so a translated doc, a stand-in that someone rewrote, and each line it marks `[unproven]` are yours to read against the rules that follow. For each region of each new layer's placeholder: the first branch, when it has text, must be in the doc that was rendered from its template, and its stand-in must be gone from that doc. Search that doc only, and skip its `Template-Source` note, which quotes a stand-in on purpose. Once a WORKFLOW doc exists, README must no longer carry the CI-runners line. Once a surface doc exists, each quick-start command's `must_appear_in` names the surface key. Then read the fill-in text from step 3: no search finds a stale sentence for you, and it must describe the doc set as it is now. A failed check points back to its step: a failed gate to step 1 (repair a file this upgrade wrote; a hand-written doc that fails its gate is reported to the user, not rewritten), a remaining stand-in whose region has an empty first branch (the CI-runners line is one) to step 2, a missing first branch or any other remaining stand-in to step 3, and a stale fill-in sentence to step 3 as well. Redo that step, then prove again.
5. **Record the upgrade once.** The record cites the change that carries the upgrade: its issue or MR/PR, or else the commit that completes steps 1 to 4. When you commit, commit on the branch the target's WORKFLOW doc prescribes, and commit steps 1 to 4 first. When the repo's rules forbid committing without consent, ask first, as its Stop-and-Ask list requires. Add an Iteration History entry and a VALIDATION block with that citation; the block follows the block template in the target's `docs/VALIDATION.md`. The upgrade is a major doc change, so also run the read-back probe (SELF-TEST §D) and record its outcome; when no zero-context reader is available, record the probe as not run. Then run the checker once more. On a re-run, an entry and a block that already record this upgrade stay as they are: add nothing.

A target that was rendered from these templates goes through these steps when it changes its doc-set profile. Adopt mode does not do this for it.

---

## Upgrading an adopted repo to a newer toolkit version

Adopted repos carry two kinds of artifact that age: the checker (copied
verbatim in Phase C) and every doc rendered from a Markdown template — each
carries a `Template-Source:` marker. A toolkit release changes none of them
silently — upgrade on purpose, and record it like any change.

1. **Read the delta before swapping.** Diff your checker against the new tag
   before replacing it (`git -C <toolkit-repo> show <tag>:checker/check_agentic_docs.py`
   against your `scripts/check_agentic_docs.py`) — know the behavioral change,
   not just the version number. Opt-in checks (e.g. `ci.runners`) stay inert
   until your config declares them.
2. **Swap the checker verbatim from the tag**, byte-compile it, run the gate.
   A new check firing on your current docs is the upgrade working as designed —
   fix the docs (add the missing declaration), not the checker.
3. **Re-port each marked doc only at its declared substitution points** when
   its `Template-Source` bumps (@v1 → @v2): the marker lists what moved
   (new lines, new sections). Check every doc that carries a marker, not only
   WORKFLOW, because a release can move the index or SELF-TEST template too. A
   doc rendered from a template that gained its marker in a later release
   carries none yet: port what that first marked version's note lists, then add
   the marker. Port the changes into your copy; local sections you authored
   yourself (recipes, checklists) are yours to keep — `Template-Source` records
   the base you ported from, not a lockstep contract.
4. **Record it like any change**: REQUIREMENTS iteration-history entry +
   VALIDATION block citing the PR, with the diff-against-tag as evidence.

---

## Hard rules

- **Harness neutrality (iron rule).** Nothing generated — no template output, no
  doctrine — may name a specific agent product, model, or proprietary tool
  mechanism. Write to the weakest common primitive shared by every collaborator:
  *read a file, run a command, open a merge/pull request.* Say "any agent or
  human collaborator." Harness-specific packaging lives only under `adapters/`.
  The sole root exception is the one-line `CLAUDE.md` pointer `See @AGENTS.md`
  (an import of the contract, not a second copy of the rules).
- **Gate before advancing.** Every Phase-B doc passes its inline gate before the
  next is produced. Phase C must exit the checker clean before Phase D.
- **The config is the single machine truth.** Any command, path, prefix, or limit
  a doc references must match `agentic-mode/config.json`.
- **Never advance past a failed inline doc gate** (the per-file check at the end
  of each Phase-B step). If the same check fails after two fix attempts, stop and
  escalate to your user with the failure trail.

## Done means

The checker exits 0 in TARGET, the placeholder sweep finds nothing, and your
hand-off summary tells the user the daily loop above.
