---
name: okf-doc-style
description: >
  Use when a knowledge corpus must be authored in, or converted into, Open Knowledge
  Format (OKF) v0.2: data catalogs, metric definitions, runbooks about data systems,
  descriptions of tables, APIs, and processes. Walks the 9-step workflow — bundle root,
  concept mapping, frontmatter families (provenance, trust, lifecycle, attested
  computation), actor and path conventions, index/log files — and runs the mechanical
  conformance pass (K1–K8) through a stdlib script (scripts/okf_lint.py). It reads and
  writes markdown documents only; it executes nothing. Triggers on: "apply OKF",
  "convert to OKF", "OKF bundle", "knowledge catalog format", "套用 OKF", "OKF 文件風格".
---
# OKF Doc Style — author a knowledge bundle in the Open Knowledge Format (playbook)

**About this playbook.** This file is the canonical, harness-neutral version.
Any collaborator — human or agent, in any tool — can read it directly as a rules
file. It applies **Open Knowledge Format (OKF) v0.2**; that spec is
self-contained and authoritative, and when this playbook and the spec disagree,
follow the spec. This file names no address for the spec: the local repository's
configuration supplies the authoritative OKF v0.2 source. **Local repo rules
(an existing doc contract, a house style guide) take precedence over this
playbook.** This playbook reads and writes knowledge documents; it executes
nothing. Its only companion is `scripts/okf_lint.py` — pure standard library,
no network, no installs — which decides the mechanical half of the conformance
checklist (K1–K8) before you read.

OKF represents *knowledge*: the metadata, context, and curated insight that
surrounds data and systems. A corpus is a **bundle** — a directory tree of UTF-8
markdown files, each carrying YAML frontmatter. No schema registry, no central
authority, no required tooling: a person reads a bundle with `cat`, an agent
parses it with any YAML-aware reader, and git diffs it line by line. Ship the
bundle as a git repository when you can; history and attribution come free.

## When to apply

Apply this playbook when you author or convert a corpus of knowledge documents
that both people and agents read: data catalogs, metric definitions, runbooks
about data systems, descriptions of tables, APIs, and processes.

Choose a different tool when:

- The repo already mandates a doc contract. Follow that contract; this playbook
  defers to local rules.
- The artifact is code or configuration rather than knowledge. OKF describes
  things; mirrored code conventionally lives under a `references/` subdirectory
  (a convention, not a requirement).
- The content needs a domain schema (Avro, Protobuf, OpenAPI). Point the
  concept's `resource` at the schema; do not restate the schema as prose.

## The format on one page

```
path/to/bundle/
  index.md            # Optional. Directory listing.
  log.md              # Optional. Update history, newest first.
  <concept>.md        # One concept per non-reserved .md file.
  <subdirectory>/     # Subdirectories group concepts.
    ...
```

A **concept** is one markdown document: a YAML frontmatter block delimited by
`---`, then a free-form markdown body. Its **concept ID** is its path with the
`.md` suffix removed (`/tables/events`). `index.md` and `log.md` are reserved at
every level; keep them off concept filenames. Every other `.md` file in the tree
is a concept.

### Frontmatter families

Identity:

| Key | Status | Shape |
| --- | --- | --- |
| `type` | Required — the only always-required key | A short, self-explanatory string, e.g. `Warehouse Table`, `Metric`, `Playbook`, `Attested Computation`. Not centrally registered. |
| `title` | Recommended | Display name. Consumers may derive one from the filename when absent. |
| `description` | Recommended | One sentence; `index.md` entries reprint it. |
| `resource` | Recommended when the concept describes an asset | Canonical URI of the underlying asset. Omit for abstract ideas. |
| `tags` | Optional | YAML list of short strings for cross-cutting grouping. |

Provenance and trust:

| Key | Shape | Records |
| --- | --- | --- |
| `sources` | List; each entry requires `resource`. `id`, `title`, and the signals below are optional | The materials the concept derives from. `resource` is either a followable artifact (URL, bundle path, `references/` path) or a scope descriptor ("all queries in project X"). |
| `sources[].author` | Actor (see Actors) or a team identifier (e.g. `team:finance-fpa`) | Who produced the source. An authority signal. |
| `sources[].usage_count` | Integer, measured over `usage_window` | How often the source was exercised. A liveness signal, not a score. |
| `sources[].last_modified` | ISO 8601 datetime | When the source itself changed. Distinct from `generated.at`. |
| `usage_window` | `{ from, to }`, written once as a sibling of `sources`; an entry may override it | The range every `usage_count` is measured over. |
| `generated` | `{ by, at }`; `by` is required within the block | How the current content was produced. `at` marks the last meaningful change. |
| `verified` | List of `{ by, at }` events | Independent confirmations. Recency is the latest `at`. A single `{ by, at }` mapping without the list dash is legal. |

Lifecycle:

| Key | Shape |
| --- | --- |
| `status` | `draft` / `stable` / `deprecated`. Absent means `stable`. |
| `stale_after` | An absolute ISO 8601 instant. The concept is stale when `now >= stale_after`. Write an instant, never a relative TTL. |

Computation — these keys appear only on `type: Attested Computation`:

| Key | Shape |
| --- | --- |
| `runtime` | Required for this type. How the computation runs (`sql`, `dbt`, `python`, ...); it defines what `parameters` mean. |
| `parameters` | List of `{ name, type, required }` — the only holes an agent may fill. |
| `computation` | Path to the computation file. Absent means the body's `# Computation` fenced block is the computation. |
| `executor` | `{ resource, receipt }` — run instructions plus the fields a run must return as evidence. |
| `attester` | `{ resource }` — deterministic, no-LLM code that turns a receipt into a verdict. |

Any additional frontmatter key is a legal producer extension. Preserve unknown
keys when you rewrite a concept.

### Actors

`generated.by` and `verified[].by` follow one convention, and trust
classification keys off its `human:` prefix:

- Agents and tools: `<producer>/<version>`, e.g. `catalog-agent/2.3`.
- People: `human:<id>`, e.g. `human:iri`.
- Automated processes: `process:<id>`, e.g. `process:nightly-audit`.

### Paths and links

Path-valued keys (`resource`, `sources[].resource`, `computation`,
`executor.resource`, `attester.resource`) accept an absolute URL, a
bundle-relative path beginning with `/`, or a relative path.

For links between concepts, write the `/`-rooted bundle-relative form; it
survives a document moving within its subdirectory. A link asserts an untyped
relationship — the prose around it names the kind (joins-with, depends-on,
references). A link to a target that does not exist yet is legal not-yet-written
knowledge; write one only for knowledge somebody committed to writing.

### Body

Write structural markdown — headings, lists, tables, fenced code blocks. Use the
conventional headings `# Schema`, `# Examples`, and `# Computation` where they
fit. Attribute a specific claim with a markdown footnote whose label equals the
`sources[].id` it cites; consumers join on the label and ignore the footnote
prose. Labels are keyed, never positional: a stable `id` survives reordering the
`sources` list.

### Index and log files

`index.md`, in any directory: one or more sections under headings, each entry a
bulleted link. Include the target's `description` in the entry — that is
producer discipline; the spec makes it a SHOULD, and conformance does not
depend on it. No frontmatter, with one
exception — the bundle-root `index.md` may declare `okf_version: "0.2"`.

`log.md`, at any level: date-grouped entries, newest first, with headings in
exactly the `## YYYY-MM-DD` form. Entries are prose; a leading bold word
(`**Update**`, `**Creation**`, `**Deprecation**`) is convention.

## Workflow

Follow these steps in order.

### Step 1 — Fix the bundle root

Choose the directory that holds the whole corpus as the bundle root. Confirm it
can ship as one unit: a git repository, an archive, or one subdirectory of a
larger repo. Every `/`-rooted path resolves against this root.

### Step 2 — Map the corpus to concepts

Split the material so each non-reserved `.md` file holds exactly one concept.
Group concepts into subdirectories the way the corpus is browsed. The directory
tree carries only hierarchy; express every other relationship as a link.

### Step 3 — Write the identity frontmatter

Give every concept a non-empty `type`, then `title`, `description`, `resource`
(when it describes a tangible asset), and `tags`. Keep `description` to one
sentence, because index entries reprint it.

### Step 4 — Record provenance

List every material the concept derives from under `sources`. Give an entry an
`id` whenever the body cites it, and attribute each borrowed claim with a
footnote labeled by that `id`. Record the credibility signals you can actually
measure — `author`, `usage_count` framed by `usage_window`, `last_modified` —
and omit the ones you cannot. Write a measured number or write nothing; never
estimate a signal.

### Step 5 — Record trust and lifecycle as they are

Write `generated: { by, at }` and name yourself in the actor convention. Add a
`verified` entry only for a confirmation that actually happened, and use the
`human:` prefix only for an actual person — the trust tier is derived from
exactly this prefix. Set `status: draft` until a review exists. Set
`stale_after` to the absolute instant after which the content needs
re-confirmation; omit the key when the concept does not decay.

Correct:

```yaml
generated: { by: catalog-agent/2.3, at: 2026-06-20T22:53:05Z }
# no verified key: nobody has confirmed it yet
```

Wrong:

```yaml
generated: { by: catalog-agent/2.3, at: 2026-06-20T22:53:05Z }
verified: { by: human:iri, at: 2026-06-20T22:53:05Z }  # fabricated
```

### Step 6 — Link concepts

Turn every prose mention of another concept into a `/`-rooted markdown link,
and let the surrounding prose name the relationship. Resolve links you broke
while reorganizing before you finish.

### Step 7 — Add index.md and log.md

Write an `index.md` for each directory a reader browses, at minimum the bundle
root, with every entry carrying the linked concept's `description`. Declare
`okf_version: "0.2"` in the root index's frontmatter. Create a root `log.md`
recording today's entries under today's date heading.

### Step 8 — Record attested computations; do not author them

When a figure must be produced a sanctioned way, create one standalone
`type: Attested Computation` concept per figure, carry the contract fields in
its frontmatter, and link to it from the narrating concept. The `# Computation`
fence (or the file named by `computation`) is the sanctioned artifact: supply
values for the declared `parameters` and nothing else. To change what the
computation does, change the policy it derives from and re-record it through
its own source; an agent-edited computation can no longer attest.

### Step 9 — Run the conformance checklist

Run `python3 scripts/okf_lint.py <bundle-root>` from this playbook's directory
first; it decides the mechanical rules (K1–K8 below). Then read the bundle for
the judgment half. Fix every failure, then re-check until the list is clean.

## Reading a bundle

When you consume an OKF bundle, hold this discipline:

- Treat a bare `verified` mapping as a one-element list.
- Derive the trust tier from `verified` alone: no key means unverified;
  non-`human:` verifiers only means machine-confirmed; any `human:` verifier
  means human-reviewed. Tiers advise; they never gate access.
- Treat a concept as stale when `now >= stale_after`.
- Read a link whose target is missing as not-yet-written knowledge, not as an
  error.
- Do not reject a concept for a missing optional family, an unknown `type`, an
  unknown frontmatter key, a broken link, or a missing `index.md`; keep the
  unknown keys when you rewrite the concept.
- Surface a failing attestation to the reader; never silently drop it.

## Conformance checklist

A bundle is conformant with OKF v0.2 exactly when all three hold:

1. [K1] Every non-reserved `.md` file in the tree carries a parseable YAML
   frontmatter block with a non-empty `type`.
2. [K3] Every `index.md` present is sections of bulleted links, and every
   `log.md` present is date-headed (`## YYYY-MM-DD`), newest-first entries.
3. [K2] Only the bundle-root `index.md` carries frontmatter, and it carries
   only `okf_version`.

Producer discipline — `okf_lint.py` decides K1 through K8 mechanically; you
read for the rest:

- [K4] Every timestamp is ISO 8601 with an explicit UTC offset
  (`2026-06-30T14:00:00Z`).
- [K5] Every `generated.by` and `verified[].by` follows the actor convention;
  reading confirms `human:` names an actual person.
- [K6] Every footnote label matches a `sources[].id`.
- [K7] `status`, when written, is `draft`, `stable`, or `deprecated`.
- [K8] Every `usage_count` is measured over a stated `usage_window`; reading
  confirms the number was actually measured.

## Converting from OKF v0.1

- Replace `timestamp` with `generated: { by, at }`.
- Move a body `# Citations` list into `sources`, and re-key the citations as
  footnotes labeled by their `sources[].id`.
- Leave the rest as is: every other v0.2 change is additive.

## Worked example (fictional)

`/tables/events.md`:

```markdown
---
type: Warehouse Table
title: Events
description: One row per tracked product event, loaded hourly.
resource: warehouse://analytics/events
tags: [analytics, events]
status: stable
generated: { by: catalog-agent/2.3, at: 2026-06-28T14:00:00Z }
verified:
  - { by: human:iri, at: 2026-06-25T09:00:00Z }
stale_after: 2026-12-31T00:00:00Z
sources:
  - id: tracking-spec
    resource: https://example.test/specs/tracking
    title: Tracking event specification
    author: team:product-analytics
    last_modified: 2026-06-18T00:00:00Z
---

# Schema

| Column | Type | Description |
| --- | --- | --- |
| `event_id` | STRING | Globally unique event identifier. |
| `session_id` | STRING | Foreign key into [sessions](/tables/sessions.md). |

Events load hourly from the collector.[^tracking-spec]

[^tracking-spec]: Tracking event specification
```

Bundle-root `index.md`:

```markdown
---
okf_version: "0.2"
---

# Tables

* [Events](tables/events.md) - One row per tracked product event, loaded hourly.
```

Bundle-root `log.md`:

```markdown
# Update Log

## 2026-06-28
* **Creation**: Established the catalog with [Events](/tables/events.md).
```

## Constraints

- The spec is authoritative and this playbook pins v0.2. Before a large
  conversion, check the spec for a newer version and read its changes section.
- Absence is meaningful and legal. A concept carrying only `type` is fully
  conformant; add frontmatter to record facts, never to look thorough.
- Do not fabricate trust. `verified` entries, `usage_count` values, and the
  `human:` prefix must name things that actually happened.
- This playbook's own file follows the doc-linter's rules:
  `python3 scripts/doc_lint.py OKF-DOC-STYLE.md` reports zero violations. If
  you find one, tell the user.
