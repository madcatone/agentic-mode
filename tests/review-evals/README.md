# Review evals — scoring two-axis review reports against planted findings

This directory extends the fire-demo idea (deterministic, re-runnable, red
when violated) from the doc checker to the two-axis review playbook
([`playbooks/TWO-AXIS-REVIEW.md`](../../playbooks/TWO-AXIS-REVIEW.md)). A
fictional change with planted defects is reviewed by a reviewer; the
resulting report is scored mechanically against a list of expected findings.
That turns "did the review improve?" into something measurable: recall of the
planted classes, noise on clean hunks, and compliance with the playbook's
report-format rules.

**What CI runs and what it does not.** Writing the review report requires
judgment, so that step is never executed by CI — it is run on demand by a
human or an agent (whoever follows the playbook). What CI runs is the
deterministic machinery only: the scorer byte-compiles, its built-in selftest
passes, the canned compliant report scores exit 0 end-to-end, the canned
deficient report scores exit 1 with the intended detections, and the planted
`change.patch` still applies to the base fixture:

```bash
sh tests/run_review_eval_demos.sh
```

## Layout

- `fixtures/todo-review/` — the change under review: a small fictional todo
  CLI (base tree), `change.patch` (the diff a reviewer receives),
  `TICKET.md` (a bug-fix ticket with numbered acceptance criteria), and
  `.dev-notes/CODE-REVIEW.md` (the fixture's own review canon, first link of
  the playbook's §2 lookup chain).
- `expected-findings.json` — one entry per planted issue (class, file, line
  ranges, axis, expected verdict/origin, match keywords) plus the list of
  clean-hunk noise zones. Line numbers refer to the tree **after** the patch
  is applied.
- `score_review.py` — the stdlib scorer (below).
- `samples/smoke-report-r1.md` — a blind, real-format report (produced by a
  fresh-context reviewer following the playbook) kept verbatim as a
  tolerance regression sample: the demo suite scores it end-to-end and
  asserts exit 0, so a grammar narrowing that stops accepting real reports
  turns CI red.

## Producing a report

1. Read `playbooks/TWO-AXIS-REVIEW.md`.
2. The change under review is `fixtures/todo-review/`: read the base tree,
   apply `change.patch` (mentally, or in a scratch copy —
   `git apply --check change.patch` inside the fixture directory proves it
   applies), read `TICKET.md`, and use `.dev-notes/CODE-REVIEW.md` as the
   Standards-axis canon.
3. Follow the playbook: both axes, the count line as the first line, the
   finding format of §4 (`file:line` + failure scenario + severity + verdict
   + origin, upgrade-condition line for every PLAUSIBLE finding), and the
   root-cause check (§3) since the ticket is a bug-fix. Write the report to
   a file (Traditional Chinese is the convention the keywords tolerate).

The scorer's finding grammar is **block-shaped**, so the report does not
have to cram everything onto one line: a finding block starts at a heading
that carries a verdict/origin marker or a `file:line` citation, or at any
non-heading line with a `file:line` citation, and runs to the next such
start or heading. Verdict, origin, the upgrade-condition line, and
citations may sit on any line of the block — the axis is read from the
block's first line or from the axis heading above it. A heading with
the verdict followed by a 位置/location bullet with the citations is
fine — that is exactly the shape of `samples/smoke-report-r1.md`. A block with neither a
verdict nor an origin marker is treated as prose and ignored. The first
line may be the total count line (`共 N 個 finding：…`) or a leading
per-axis count line (`Standards 軸共 3 個 finding：…` — the playbook's §5
aggregated form); with neither, the `[count-line]` check fires.

## Scoring

```bash
python3 tests/review-evals/score_review.py <report.md>
```

- **Recall**: an expected item is hit when a finding's text contains one of
  the item's keywords and one of the finding's citations (a finding may cite
  several locations) names the same file with a line inside the item's
  ranges (± tolerance). Keywords are code identifiers, not prose — reports
  are in Traditional Chinese, matching must be language-robust.
- **Noise**: a finding that matches no expected item — findings on the
  deliberately clean hunks are the classic case.
- **Format**: the count line (total form checked against the body, or the
  leading per-axis form accepted as-is), per finding `file:line` + axis
  (start line or axis heading) + verdict + origin (anywhere in the
  finding's block), upgrade-condition
  lines, strict origin labels for the planted pre-existing issue, and the
  root-cause section for bug-fix tickets.

Gate (constants at the top of `score_review.py`): at least 5 of the 6 planted
classes hit, 0 format violations, at most 1 noise finding. Exit codes:
0 pass, 1 gate failed, 2 usage/I-O error. One compound finding may satisfy
two adjacent expected items — a deliberate leniency in exchange for language
robustness.

## Adding a new fixture

1. Create `fixtures/<name>/` with a base tree, a `change.patch` that applies
  to it (`git apply --check` must pass), a ticket, and ideally a local canon
  under `.dev-notes/`.
2. Plant issues from the classes you care about and record one entry per
  issue in `expected-findings.json` (or a per-fixture JSON passed via
  `--expected`), with line numbers taken from the **post-patch** tree and
  keywords that are code identifiers appearing in the fixture.
3. List the deliberately clean hunks under `noise_zones`.
4. Keep every fixture neutral: fictional project, no brand, no tool names —
  same rule as the fire-demos.
