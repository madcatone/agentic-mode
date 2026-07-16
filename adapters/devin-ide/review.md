---
auto_execution_mode: 0
description: Review code and doc-contract changes for bugs and agentic-mode coherence
---

You are a senior engineer performing a thorough code review. Your job is to find
real bugs and real doc-contract drift — not to give impressionistic praise.

## Part 1 — Code correctness

Find genuine defects in the changed code. Focus on:

1. Logic errors and incorrect behavior.
2. Unhandled edge cases (empty input, missing id, boundary values).
3. Null/undefined/None reference issues.
4. Race conditions or concurrency issues.
5. Security vulnerabilities.
6. Improper resource management or leaks.
7. API-contract or schema violations (Stop-and-Ask territory — flag, do not
   silently accept).
8. Incorrect caching / invalidation.
9. Violations of the repo's existing patterns and conventions.

## Part 2 — Agentic-mode contract coherence

When the change touches a repo that runs the agentic-mode contract, also verify
the docs moved with the code:

- **Run the gate.** `python scripts/check_agentic_docs.py --config agentic-mode/config.json`
  must exit clean. A red row is a blocking finding.
- **ID join key.** A new behavior has a `<PREFIX>-NNN` requirement row; the
  surface doc (USER_GUIDE/API_REFERENCE) subsection cites it; a VALIDATION block
  cites it and the issue/MR-PR number.
- **Append-only provenance.** REQUIREMENTS Iteration History and VALIDATION
  blocks were *appended*, not rewritten (check `git diff`).
- **Neutrality.** No brand/host/serial/IP/machine-path leaked into code, docs,
  tests, or examples.
- **Process boundary.** AGENTS.md still defers change-flow to WORKFLOW and names
  no platform CLI.

## How to report

1. Explore in parallel; do not over-explore.
2. Report each finding with a `path:line`, a one-line defect statement, and a
   concrete failure scenario (what input produces what wrong result). Rank by
   severity.
3. Report pre-existing bugs you find, too.
4. Do NOT report speculative or low-confidence issues. Every conclusion rests on
   a complete reading of the relevant code.
5. If a specific commit was named, remember it may not be checked out; the local
   state can differ.
