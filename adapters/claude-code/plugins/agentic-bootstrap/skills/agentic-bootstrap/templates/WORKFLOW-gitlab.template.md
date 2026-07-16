<!--
TEMPLATE: docs/WORKFLOW.md for ci.platform == "gitlab". This doc is COPIED ~AS-IS into the target repo:
substitute only the H1 platform name, the Template-Source marker, and the {{PLACEHOLDER}} test/build
commands (from AGENTS Development Commands). Do NOT re-author the review-loop body — the issue→branch→
commit→MR→review conventions and red lines are platform constants.
BILINGUAL comment rule (dual-language external replies + EOF-terminated multi-line format) applies ONLY
when config bilingual.enabled == true; if monolingual, replies are single-language (still self-contained,
still EOF-terminated multi-line). Chat replies are never bound by the external-reply format.
`glab` appears here because this is the GitLab platform doc — it is the ONLY doc allowed to name it.
Harness-neutral otherwise: never name a specific agent product or model.
Template-Source: agentic-bootstrap/WORKFLOW-gitlab@v1
-->

# GitLab Workflow — Collaborator Rule

This document is the authoritative GitLab workflow rule for anyone (human or agent) working in this repo. Read it before touching issues, branches, commits, or MRs. It complements `README.md` and `AGENTS.md` (code/scope/test discipline) — this file focuses on the issue → branch → commit → MR → review loop. Assume the reader is new and has no chat history. All commands run from the repo root.

## 0. Iron Rules (apply in every context)

- **Without explicit user consent, do not commit, push, amend, rebase, force-push, or `--no-verify`.** "The user agreed once" is not standing consent; ask every time.
- **No blanket staging** (`git add -A` / `git add .`). Stage files explicitly: `git add <file1> <file2>`. Ignored directories can still let stray untracked files slip into the stage.
- **Never claim tests pass without actually running them.** Run the repo's real commands (from AGENTS Development Commands): build/compile `{{BUILD_CMD}}`; tests `{{TEST_CMD}}`. Green means you saw the passing summary, not "should pass."
- **A behavior change must sync docs in the same change** (REQUIREMENTS iteration history + observable-surface doc + VALIDATION). Otherwise it is not done.
- **MR and issue comments must be self-contained.** The reader has not seen your chat history; write so a cold read is enough.
- External replies posted to GitLab issues/MRs use an EOF-terminated multi-line format (HEREDOC). {{IF_BILINGUAL: post both languages.}} Chat replies are exempt.

## 1. Issue — research and communication

### Read
```bash
glab issue view --comments <N>
```

### Post research / progress to an issue
1. Keep the issue title in the primary title language the platform expects (relevant to auto-derived MR titles).
2. Summarize findings and conclusions into at least one comment on the issue.
3. When the user asks to "investigate and reply on the issue," write the comment with a HEREDOC:

```bash
glab issue note <N> -m "$(cat <<'EOF'
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

### Naming
Decide the English branch name first, then create the issue-driven MR without letting `glab mr create` implicitly reuse your current feature branch:

```bash
glab mr create --related-issue <N> \
  --source-branch <branch> \
  --target-branch main \
  --create-source-branch
```

The older auto-create command shows as deprecated in current CLIs:
```bash
glab mr for <N>   # deprecated — prefer the explicit form above
```

The MR must target `main`. Do not branch from or merge into another feature branch unless the user says so.

### Get the branch name and check it out
```bash
glab mr view <MR_IID>
glab mr checkout <MR_IID>
git status --short --branch
```

### One-to-one principle
One issue → one branch → one MR. Do not smuggle unrelated changes into a branch.

## 3. Commit

### Format
Conventional commit (team convention — the canonical rules live in the team-skills plugin's `gcm` skill):
```
<type>[ <TICKET>]: <Subject>

<body — explain WHY, not what>
```

**Types:** `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `build`, `ci`, `ops`, `chore`, `revert` (dependency bumps are `build`, not `chore`; only CI-config changes are `ci`).
**Ticket (as-needed):** when the change maps to a tracked ticket, put its ID between the type and the colon, space-separated, no parentheses (`fix PROJ-123: Correct session teardown`); omit it when there is no ticket.
**Subject:** ≤ 50 chars, type lowercase, subject first letter capitalized, imperative mood ("Add X" not "Added X"), no trailing period.
**Body:** a few tight lines; explain motivation/trade-offs/pitfalls; include measured evidence (numbers, fingerprint, repro case); reference the requirement ID ("implements {{PREFIX}}-0NN") and `Closes #N`. Omit the body entirely when the diff already shows the why.
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
- doc sync → its own commit or folded into the feature commit (by size).
- review response → its own commit, message tagged `(MR #N review)`.

### Never
- `git commit --no-verify` (unless the user says so).
- `git commit --amend` / `git rebase -i` on already-pushed commits.
- `git push --force` to any branch (especially `main`).
- `git reset --hard` anything without asking first.
- Stage `.env`, credentials, or ignored runtime output.
- Reference chat context in a commit message ("as the user said earlier…").

## 4. Test and verify (run before committing)

Run the repo's real commands from AGENTS Development Commands, e.g.:
```bash
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
# Docs coherence gate:
python scripts/check_agentic_docs.py --config agentic-mode/config.json
```
**All green is the only "done."** Claim tests pass only after you see the passing summary.

### Docs sync checklist (every behavior change)
- [ ] REQUIREMENTS — append an iteration-history entry {{IF_BILINGUAL: one per language track, kept in lock-step}}.
- [ ] Add a new `{{PREFIX}}-XXX` requirement row if a new behavior surfaced.
- [ ] VALIDATION — append a per-feature block (Code / Testing / Verification Commands / Status).
- [ ] README / observable-surface doc — update if a command, key, endpoint, or visible behavior changed.
- [ ] `python scripts/check_agentic_docs.py --config agentic-mode/config.json` passes.

## 5. Push and MR

### Do not push unless the user says so
Commits stay local by default. Push only on request: `git push -u origin <branch>`.

### Create the MR
`glab` already creates the MR from the issue; manual creation only on request:
```bash
glab mr create --title "<subject>" --description "$(cat <<'EOF'
## Summary
- 1-3 bullets: what changed and why

## Test plan
- [ ] 1-2 bullets a reviewer can reproduce

Closes #<issue>
EOF
)"
```
**Title:** ≤ 70 chars, conventional-commit style. Do not prefix the issue number (the platform shows it).
**Body:** `## Summary` in bullets (not prose); `## Test plan` is a reproducible step list; end with `Closes #<issue>`. glab's body flag is `-d`/`--description` (there is no `--body`; `-b` is `--target-branch`).

### Assignee
Assign the MR to the current authenticated GitLab user unless the user names another assignee. `glab` has no `@me` shortcut for assignees, so confirm your username first, then pass it explicitly:
```bash
glab auth status                              # confirm the authenticated username
glab mr create ... --assignee <your-username> # comma-separate, or repeat -a, for several
```

### Description formatting (avoid literal `\n`)
Write the description as real Markdown with real newlines. Do not pass a multiline body through a shell-escaped `"...\n..."` string — GitLab may render the `\n` literally. `glab mr create` has **no** body-file flag (`-f`/`--fill` fills from commit history, not a file), so for a long body write it to a temporary `.md` file and feed its content through `--description` with command substitution, which preserves the newlines:
```bash
glab mr create --title "<subject>" --description "$(cat mr-body.md)"
glab mr update <iid> --description "$(cat mr-body.md)"   # same for updating an existing MR
```

### Verify and report
After creating or updating, view the MR and confirm the title, description formatting, source branch, target branch, assignee, and pipeline status; then report back:
```bash
glab mr view <iid>
```
Report the MR URL and key metadata (source→target, assignee, pipeline status) to the user.

## 6.a Code review — requesting
- Review the MR the user names.
- Find non-nitpick issues where possible.
- Raise findings in MR replies; a blocking finding may stay a default resolvable discussion.
- If quality is fine, reply `LGTM`; informational/status notes add `--resolvable=false`.

```bash
glab mr note create <N> --resolvable=false -m "$(cat <<'EOF'
## Code Review Summary
LGTM
EOF
)"
```

## 6.b Code review — responding to findings
### Read
```bash
glab mr view --comments <N>
```
### Rhythm
1. Separate the reviewer's **blocking** from **non-blocking** items.
2. Fix blocking (mandatory) + cheap non-blocking (batch them to save round-trips).
3. **One review round = one commit**, message `fix(<scope>): <what> (MR #N review)`.
4. Re-run full verification (§4).
5. Commit, then post a summary note to the MR.

### Notes
- **A bug fix must include a before/after repro** — reproduce the reviewer's condition once (wrong result), fix, reproduce again (right result). That is the only credible proof.
- **Non-blocking trade-off:** if a change balloons scope, split it into a follow-up issue and say so in the note.
- **Do not silently drop a reviewer's point:** if you disagree with a blocking item, argue the case in reply rather than ignoring it.

```bash
glab mr note create <N> --resolvable=false -m "$(cat <<'EOF'
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
Note: `glab mr note <N> -m` is deprecated — use `glab mr note create <N> -m`. Add `--resolvable=false` to informational summary notes.

## 6.c LGTM
- Reading `LGTM` means the code quality is accepted; no further review needed.

## 7. Cleanup after merge
- After the MR merges, the local branch may be deleted: `git branch -d <branch>` (merged only; never `-D`).
- Do not proactively delete the remote branch (project settings may auto-delete).

## 8. glab quick reference
```bash
glab issue view --comments <N>
glab issue note <N> -m "..."
glab issue list
glab mr view --comments <N>
glab mr note create <N> --resolvable=false -m "..."
glab mr create --related-issue <N> --source-branch <branch> --target-branch main --create-source-branch
glab mr checkout <N>
glab mr list
```

## 9. Anti-patterns (done and corrected before)
| Anti-pattern | Correct |
|---|---|
| Claiming green after a partial test run | Run the repo's full commands from AGENTS Development Commands; see the passing summary |
| Treating an import/setup failure as "pre-existing infra" | First sync the declared dev/test dependencies; it is usually a missing setup step |
| Commit message describing *what* in prose | Bullets describing *why* + concrete evidence |
| `git add .` | Explicit `git add <file1> <file2>` |
| Committing a fix without a repro | Run before/after repro; put the evidence in the message and review note |
| Citing an iteration number ("entry #42") across languages | Cite by description — the two counters may differ by one |
| Batching unrelated entry-point changes into one commit | Split by entry point / invariant |
| `glab mr note -m` (deprecated) | `glab mr note create <N> -m`; add `--resolvable=false` for informational notes |

## 10. Red lines (never, in any context)
- Force-push to `main` / the default / protected branches.
- Commit a secret / `.env` / credentials.
- `--no-verify` past a pre-commit hook (unless the user explicitly says so and you have explained the root cause).
- Claim tests pass without running them.
- Reply to an issue without reading `glab issue view --comments <N>` in full.
- Put chat context into a commit message or MR description.
- Assume the reader remembers a prior conversation; MR/issue comments must be self-contained.
