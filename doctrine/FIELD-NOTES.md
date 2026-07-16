# FIELD-NOTES.md — Lessons from the origin project

The agentic-mode contract was distilled from an agent-maintained real project —
a log-inspection TUI with a console tool, a web service, and a browser UI, kept
alive across many sessions by different agents with no shared chat history.
These are the field lessons that shaped the doctrine. Each is written
harness-neutral and generalized away from the origin project; where the origin
project is referenced it is called "the origin project."

Read [`BOOTSTRAP-CORE.md`](BOOTSTRAP-CORE.md) for the doctrine itself; this file
is the *why-it-earned-its-place* record behind several of its rules.

---

## 1. Give the reader a "questions to answer before editing" checklist

The single most effective onboarding artifact in the origin project was not prose
about the architecture — it was a short list of **questions an agent must answer
before touching the core logic**. For a log parser it read roughly:

- **Trigger pattern** — which input pattern creates or updates this event?
- **Ownership** — does the event start a new unit of work, attach to the current
  one, or enrich an earlier one?
- **Placement** — which category/group should own it?
- **Correlation key** — does it carry a stable id that joins it to related events?
- **Late data** — can a later line add richer detail to an existing node?
- **Error behavior** — what should a failed/timeout/incomplete case produce?
- **Regression coverage** — which test or fixture must be added or updated?
- **Neutrality** — did this introduce a real brand, package, host, or device id?

The value is that it converts "understand the whole system first" into a bounded
set of concrete decisions. A cold reader who can answer these can make a correct
change without having read every line. **Generalization:** every project has a
core-logic hotspot; the README/onboarding should carry a small, project-specific
question list gating edits to it, not just an architecture tour. This is why the
README template ships an "Agent Onboarding Guide" with a *questions-before-editing*
slot rather than only a component diagram.

---

## 2. A prose "docs sync checklist" is not enough — mechanize it into a gate

The origin project first tried to keep its docs coherent with a **hand-written
checklist** in the workflow doc: "on every behavior change, update the
requirements iteration history, add a requirement row if new behavior surfaced,
append a validation block, update the README/user-guide." It read well and was
almost never followed completely under time pressure.

The failure modes were mundane and repetitive:

- the same test command written six subtly different ways across README, AGENTS,
  and the docs — some of them silently wrong (skipping a whole test suite);
- requirement ids that skipped a number or duplicated one;
- a neutrality rule ("no hardcoded hosts/serials") that nobody actually ran;
- a docs-sync step quietly dropped because the diff "looked done."

A prose checklist relies on a human/agent remembering and self-auditing — exactly
what fails without chat history. The fix was to turn every *mechanizable* row into
an **executable gate** (`check_agentic_docs.py`) wired into CI, so drift fails the
build instead of being caught by luck in review. What the script cannot judge
(do the commands actually run? is the prose comprehensible cold?) stayed a short
manual list. **Generalization:** any checklist item that can be expressed as
"grep/parse and compare" should become a check, not a bullet; the checklist
shrinks to only the genuinely human-judgment rows. This is the origin of the
config-driven checker and the split between SELF-TEST's automated §A and manual §B.

---

## 3. Split a resident index from a cold-start pack — don't make everyone read the bootstrap manual

The portable protocol started life as a single ~800-line document that described
both *how to stand up the contract in a new repo* and *how this repo's contract
works day to day*. Every agent touching the repo — even for a one-line fix — was
implicitly asked to read the whole bootstrap manual.

The reorganization that fixed it kept two things strictly apart:

- a **resident index** (`AGENTIC-MODE.md`) scoped to what *every session* needs:
  the doc inventory, source-of-truth precedence, and how the checker enforces it.
  Short enough to read every session.
- a **cold-start pack** (the doctrine, templates, and self-test) that *only a
  bootstrap or a major doc change* needs to load.

No doctrine changed in the split — it was purely about *what a reader is forced to
load when*. **Generalization:** separate resident/hot context (read constantly,
must stay small) from cold/bootstrap context (read rarely, can be large). A
monolith that mixes them taxes every future reader with the setup manual. This is
why AGENTIC-MODE.md is deliberately a thin router and the depth lives in
`doctrine/` and `templates/`.

---

## 4. Bilingual docs need ID-alignment discipline, not translation

The origin project maintained two full language tracks of its requirements and
user guide. The trap is treating the second language as a translation footnote;
it decays instantly. The discipline that held was:

- both tracks are **first-class**, each with its own full Problem/Goals/
  Requirements/Iteration-History sections;
- requirement tables stay in **lock-step**: same id, same count, same order across
  both languages;
- iteration-history counters are **independent per language** and may legitimately
  drift by one, so cross-language references cite **by description**, not by raw
  number ("the export-format entry", never "entry #42");
- half-translated is worse than one clean language — if you cannot maintain two
  full tracks, keep one.

**Generalization:** the requirement id is the join key *across languages* too. The
checker enforces this mechanically: when `bilingual.enabled` is true, the two
region's id sets must be identical, or the gate fails. Bilingual coherence is an
ID-integrity problem, not a linguistic one.

---

## 5. Append-only iteration history is where rationale survives

Every landed change in the origin project appended one numbered entry to an
**Iteration History** that was never rewritten or renumbered. Each entry led with
the *decision* and then the *evidence* — a measurement, a fingerprint, an issue/MR
link — e.g. "peak memory dropped 329 MB → 47 MB, output byte-identical," not
"improved performance."

Why append-only, specifically:

- it is the **only** place where *why-decisions* accumulate; the current
  requirement table states *what is true now*, but not *why it changed*;
- rewriting history destroys exactly the context a future cold reader needs —
  including the reasoning behind a reversal (a reversal appends a new entry that
  references the old one, it never edits the old one);
- "lead with the number" makes each entry auditable; an unmeasured claim
  ("faster", "cleaner") is unverifiable and therefore worthless to a reviewer.

**Generalization:** provenance is append-only or it is not provenance. A gap-free,
never-rewritten numbered log is cheap to maintain and is the highest-value artifact
for the next agent. The checker's opt-in `iteration_history` continuity check
exists to keep that log gap-free.

---

## 6. From a hardcoded checker to a config-driven one

The first checker was written *for the origin project*: it hardcoded the id prefix,
the exact test-command policy (which interpreter covers which suite), the three
entry-point filenames, the two bilingual region headings, and a specific deny-word
and host allowlist. It worked — and it was unshippable to any other repo, because
every project-specific fact was baked into the code.

The rewrite pulled every project-specific fact out into an external
`agentic-mode/config.json` and left the framework code identical between projects:
prefix, doc paths, bilingual headings, entry points, command rules, deny words,
URL allowlist, line limits, and the opt-in leak/continuity sweeps all live in
config. The same file now drops into any repo unchanged.

Two lessons rode along:

- **Preserve escape hatches when you generalize.** The line-level
  `agentic-gate: allow` marker — which lets a rule/spec doc quote a bad example on
  purpose without tripping the gate — had to survive the rewrite, or the doctrine
  files themselves would fail their own checker. <!-- agentic-gate: allow -->
- **Generalization can silently drop coverage.** The project-specific gate also
  detected raw IPv4 literals and single-machine absolute paths as leak signals.
  The first config-driven version lost those. They were restored as *opt-in*
  config flags (`forbid_ipv4`, `forbid_local_paths`) rather than dropped or forced
  on — so no existing config breaks, but the capability is reachable. When you
  refactor a checker toward config, diff the *old* behavior against the new and
  account for every check that disappeared.

**Generalization:** a reusable tool separates *mechanism* (the checks) from
*policy* (which checks, with which parameters). Policy belongs in a config the
downstream repo owns; mechanism stays frozen so every repo shares one auditable
implementation.
