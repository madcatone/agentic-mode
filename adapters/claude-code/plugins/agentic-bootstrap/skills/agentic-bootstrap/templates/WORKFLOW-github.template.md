<!--
TEMPLATE: docs/WORKFLOW.md for ci.platform == "github". PR-based equivalent of the GitLab workflow,
using the `gh` CLI. Copied ~as-is: substitute only the H1, the Template-Source marker, and the
{{PLACEHOLDER}} build/test commands (from AGENTS Development Commands). Do NOT re-author the review-loop body.
NOTE: NEW — not yet battle-tested. The GitLab variant is the field-proven one; this GitHub variant mirrors
its structure onto issues → branch → commit → PR → review. Treat deviations as bugs to report upstream.
BILINGUAL dual-language external replies apply ONLY when config bilingual.enabled == true.
`gh` appears here because this is the GitHub platform doc — it is the ONLY doc allowed to name it.
Harness-neutral otherwise: never name a specific agent product or model.
Template-Source: agentic-bootstrap/WORKFLOW-github@v1
-->

# GitHub Workflow — Collaborator Rule

> **Status: NEW — not yet battle-tested.** This mirrors the field-proven GitLab workflow onto GitHub's PR model. If a step does not fit `gh`'s actual behavior, fix it and note the deviation.

This document is the authoritative GitHub workflow rule for anyone (human or agent) working in this repo. Read it before touching issues, branches, commits, or PRs. It complements `README.md` and `AGENTS.md` (code/scope/test discipline) — this file focuses on the issue → branch → commit → PR → review loop. Assume the reader is new and has no chat history. All commands run from the repo root.

## 0. Iron Rules (apply in every context)

- **Without explicit user consent, do not commit, push, amend, rebase, force-push, or `--no-verify`.** "The user agreed once" is not standing consent; ask every time.
- **No blanket staging** (`git add -A` / `git add .`). Stage files explicitly: `git add <file1> <file2>`.
- **Never claim tests pass without running them.** Run the repo's real commands (from AGENTS Development Commands): build/compile `{{BUILD_CMD}}`; tests `{{TEST_CMD}}`. Green means you saw the passing summary.
- **A behavior change must sync docs in the same change** (REQUIREMENTS iteration history + observable-surface doc + VALIDATION). Otherwise it is not done.
- **PR and issue comments must be self-contained.** The reader has not seen your chat history.
- External replies posted to GitHub issues/PRs use an EOF-terminated multi-line format (HEREDOC). {{IF_BILINGUAL: post both languages.}} Chat replies are exempt.

## 1. Issue — research and communication

### Read
```bash
gh issue view <N> --comments
```

### Post research / progress to an issue
Summarize findings into at least one comment. When asked to "investigate and reply on the issue," use a HEREDOC:
```bash
gh issue comment <N> --body "$(cat <<'EOF'
## <title> — research

Body (dense; use tables; give concrete commit SHAs and line numbers).

- key point (optional)
- conclusion
EOF
)"
```

**Style:**
- Match the issue author's language in the reply. {{IF_BILINGUAL: reply in the author's language.}}
- Each comment is self-contained; do not assume the reader saw the previous one.
- Cite code as `path/to/file:LINE` so the reviewer can click through.
- Give concrete evidence — commit SHA, fingerprint, measured numbers — not "much faster" / "looks fine."
- Do not reference "the plan" — the user cannot see plan-mode content.

## 2. Branch

### Naming and creation
Decide an English branch name, create it, and (optionally) link it to the issue. Unlike GitLab's issue-driven MR creation, GitHub's PR is created from a pushed branch:

```bash
git switch -c <branch>            # e.g. 12-export-format
# ... commits ...
git push -u origin <branch>       # only when the user asks to push / open a PR
```

Target `main` (the default branch). Do not branch from or merge into another feature branch unless the user says so. Optionally associate work with an issue by writing `Closes #<N>` in the PR body (auto-closes on merge).

### One-to-one principle
One issue → one branch → one PR. Do not smuggle unrelated changes into a branch.

## 3. Commit

### Format
Conventional commit (team convention — the canonical rules live in the team-skills plugin's `gcm` skill):
```
<type>[ <TICKET>]: <Subject>

<body — explain WHY, not what>
```
**Types:** `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `build`, `ci`, `ops`, `chore`, `revert` (dependency bumps are `build`, not `chore`; only CI-config changes are `ci`).
**Ticket (as-needed):** when the change maps to a tracked ticket, put its ID between the type and the colon, space-separated, no parentheses (`fix PROJ-123: Correct session teardown`); omit it when there is no ticket.
**Subject:** ≤ 50 chars, type lowercase, subject first letter capitalized, imperative, no trailing period.
**Body:** a few tight lines; explain motivation/trade-offs/pitfalls; include measured evidence; reference the requirement ID ("implements {{PREFIX}}-0NN") and `Closes #N`. Omit the body entirely when the diff already shows the why.
**Precedence:** if this repo has a commit-msg hook or its own documented convention, that takes precedence over these defaults.

### HEREDOC example
```bash
git commit -m "$(cat <<'EOF'
<type>[ <TICKET>]: <Subject>

<why this change; the trade-off; the pitfall avoided>

Verified: <build/test/smoke evidence — concrete numbers or fingerprint>.

Closes #<N>.
EOF
)"
```

### One logical thing per commit
- bug fix + its test → same commit.
- main feature + its test → same commit.
- doc sync → its own commit or folded into the feature commit.
- review response → its own commit, message tagged `(PR #N review)`.

### Never
- `git commit --no-verify` (unless the user says so).
- `git commit --amend` / `git rebase -i` on already-pushed commits.
- `git push --force` to any branch (especially `main`).
- `git reset --hard` anything without asking first.
- Stage `.env`, credentials, or ignored runtime output.
- Reference chat context in a commit message.

## 4. Test and verify (run before committing)

Run the repo's real commands from AGENTS Development Commands, e.g.:
```bash
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
# Docs coherence gate:
python scripts/check_agentic_docs.py --config agentic-mode/config.json
```
**All green is the only "done."**

### Docs sync checklist (every behavior change)
- [ ] REQUIREMENTS — append an iteration-history entry {{IF_BILINGUAL: one per language track, kept in lock-step}}.
- [ ] Add a new `{{PREFIX}}-XXX` requirement row if a new behavior surfaced.
- [ ] VALIDATION — append a per-feature block.
- [ ] README / observable-surface doc — update if a command, key, endpoint, or visible behavior changed.
- [ ] `python scripts/check_agentic_docs.py --config agentic-mode/config.json` passes.

## 5. Push and PR

### Do not push unless the user says so
Commits stay local by default. Push only on request: `git push -u origin <branch>`.

### Create the PR
```bash
gh pr create --base main --head <branch> --title "<subject>" --body "$(cat <<'EOF'
## Summary
- 1-3 bullets: what changed and why

## Test plan
- [ ] 1-2 bullets a reviewer can reproduce

Closes #<issue>
EOF
)"
```
**Title:** ≤ 70 chars, conventional-commit style. Do not prefix the issue number.
**Body:** `## Summary` in bullets; `## Test plan` is a reproducible step list; end with `Closes #<issue>`.

### Assignee
Assign the PR to the current authenticated GitHub user unless the user names another assignee. `gh` accepts the `@me` self-assign shortcut; confirm your identity first if unsure:
```bash
gh auth status                    # confirm the authenticated account
gh pr create ... --assignee @me   # or --assignee <user1>,<user2>
```

### Description formatting (avoid literal `\n`)
Write the body as real Markdown with real newlines. Do not pass a multiline body through a shell-escaped `"...\n..."` string — it may render the `\n` literally. For a long body, write it to a temporary `.md` file and pass it with `--body-file`, which preserves the newlines:
```bash
gh pr create --title "<subject>" --body-file pr-body.md
gh pr edit <N> --body-file pr-body.md   # same for updating an existing PR
```

### Verify and report
After creating or updating, view the PR and confirm the title, description formatting, base and head branches, assignee, and checks status; then report back:
```bash
gh pr view <N>
```
Report the PR URL and key metadata (head→base, assignee, checks status) to the user.

## 6.a Code review — requesting
- Review the PR the user names: `gh pr view <N> --comments` and `gh pr diff <N>`.
- Find non-nitpick issues where possible.
- Raise findings as PR review comments. If quality is fine, approve with `LGTM`.

```bash
gh pr review <N> --comment --body "$(cat <<'EOF'
## Code Review Summary
- 1-3 bullets
EOF
)"
# When quality is accepted:
gh pr review <N> --approve --body "LGTM"
```

## 6.b Code review — responding to findings
### Read
```bash
gh pr view <N> --comments
```
### Rhythm
1. Separate the reviewer's **blocking** from **non-blocking** items.
2. Fix blocking (mandatory) + cheap non-blocking (batch them).
3. **One review round = one commit**, message `fix(<scope>): <what> (PR #N review)`.
4. Re-run full verification (§4).
5. Commit, push, then post a summary comment.

### Notes
- **A bug fix must include a before/after repro** — reproduce the reviewer's condition (wrong result), fix, reproduce again (right result).
- **Non-blocking trade-off:** if a change balloons scope, split it into a follow-up issue and say so.
- **Do not silently drop a reviewer's point:** argue the case in reply rather than ignoring it.

```bash
gh pr comment <N> --body "$(cat <<'EOF'
## Review response — commit <SHA>

### Blocking: <item> ✓
<fix explanation + repro before/after>

### Non-blocking
1. <item>: <what was done>

### Verification
- build/compile ✓
- tests ✓ — N passing
EOF
)"
```

## 6.c LGTM
- Reading an approval / `LGTM` means the code quality is accepted; no further review needed.

## 7. Cleanup after merge
- After the PR merges, the local branch may be deleted: `git branch -d <branch>` (merged only; never `-D`).
- GitHub can auto-delete the head branch on merge (repo setting); do not force it manually.

## 8. gh quick reference
```bash
gh issue view <N> --comments
gh issue comment <N> --body "..."
gh issue list
gh pr view <N> --comments
gh pr diff <N>
gh pr create --base main --head <branch> --title "..." --body "..."
gh pr review <N> --approve --body "LGTM"
gh pr comment <N> --body "..."
gh pr list
```

## 9. Anti-patterns (mirror of the GitLab list)
| Anti-pattern | Correct |
|---|---|
| Claiming green after a partial test run | Run the repo's full commands; see the passing summary |
| Treating an import/setup failure as "pre-existing infra" | First sync the declared dev/test dependencies |
| Commit message describing *what* in prose | Bullets describing *why* + concrete evidence |
| `git add .` | Explicit `git add <file1> <file2>` |
| Committing a fix without a repro | Run before/after repro; put the evidence in the message and review comment |
| Citing an iteration number across languages | Cite by description — the two counters may differ by one |
| Opening a PR from an unpushed branch | Push the source branch first (only when the user asks) |

## 10. Red lines (never, in any context)
- Force-push to `main` / the default / protected branches.
- Commit a secret / `.env` / credentials.
- `--no-verify` past a pre-commit hook (unless the user explicitly says so and you have explained the root cause).
- Claim tests pass without running them.
- Reply to an issue without reading `gh issue view <N> --comments` in full.
- Put chat context into a commit message or PR description.
- Assume the reader remembers a prior conversation; PR/issue comments must be self-contained.
