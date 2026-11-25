---
name: global-claude
description: >
  Check the user-global Claude Code instruction file (~/.claude/CLAUDE.md, or
  $CLAUDE_CONFIG_DIR/CLAUDE.md when that variable is set). Use when the user
  wants that file created on a new machine, reviewed for bloat, contradictions,
  project-specific rules, secrets, or machine paths, or turned into a one-line
  pointer at a global AGENTS.md. A missing file is shown and written only after
  an explicit yes. An existing file is reviewed and left untouched until the
  user approves a specific diff. Triggers on: "global CLAUDE.md", "check my
  ~/.claude/CLAUDE.md", "/global-claude", "set up global instructions",
  "檢查全域 CLAUDE.md", "建立全域 CLAUDE.md", "我的 CLAUDE.md 太長".
---

# global-claude — user-global CLAUDE.md

Check the user-global Claude Code instruction file. Create it only when it is
missing, and only after the user approves the exact bytes. When it already
exists, review it and leave it unchanged until the user approves a specific
edit.

agentic-mode keeps **AGENTS.md** as the canonical instruction file and
**CLAUDE.md** as a thin pointer (`See @<path>`), the same shape as this
repository's root `CLAUDE.md`. This skill applies that split at user scope:
global preferences live in one short file; project facts stay in the repo.

**Announce at start:** "I'm using the global-claude skill to check your global Claude Code instruction file."

## Write rules

Follow these for the whole run.

1. The only path you may write is the global `CLAUDE.md` from Step 1. Do not create or edit `~/.agents/AGENTS.md`, `~/.codex/AGENTS.md`, or any repo file.
2. The detector is read-only. Do not add a write path to it.
3. **Missing file.** Show the exact bytes. Write them only after an explicit write instruction: "write it", "create it", "yes, write that file", or "approve the write". "ok", "looks good", "thanks", and silence are not approval. If the user returns an edited body together with a write instruction, write the edited body.
4. **Existing file.** Do not edit it as part of the review. A proposed diff is text in the report, not a write. Apply it only after a later reply that says "apply the diff" or names the item numbers to apply. "LGTM" is not approval.
5. Create the parent directory of `CLAUDE.md` only while performing an approved create, and only that directory. Write with exclusive create (`open(path, "x")`). On `FileExistsError`, stop and switch to the review branch. Never delete the file in order to recreate it.
6. Re-run the detector immediately before any approved write. If the status is no longer the one you reported, stop and say what changed.
7. Do not quote a secret. Report the line number and delete by line number when an approved edit removes it.

## Step 1 — Detect

From the directory that contains this `SKILL.md`, run:

```bash
python3 scripts/detect_global_claude.py
```

Exit 0 means the report is valid. Any other exit: show stderr and stop. Do not invent a status.

Read these keys:

| Key | Meaning |
| --- | --- |
| `claude_md_status` | `missing`, `exists`, `not_a_file`, `broken_symlink`, or `unreadable` |
| `claude_md_path` | Absolute path that was resolved |
| `claude_md_via` | `default` (`~/.claude/CLAUDE.md`) or `CLAUDE_CONFIG_DIR` |
| `claude_md_lines` | Logical lines (`str.splitlines()`), `0` when missing, `-` when unreadable |
| `claude_md_kind` | `missing`, `empty`, `pointer`, `prose`, or the same value as a non-file status |
| `agents_md_status` | `~/.agents/AGENTS.md` |
| `codex_agents_md_status` | `~/.codex/AGENTS.md` |
| `preferred_agents_md` | First existing file, `~/.agents` before `~/.codex`, else `none` |
| `pointer_import` | Token to put after `@`, or `-` |
| `secret_lines` | Candidate line numbers, or `none`. The line text is not printed |
| `machine_path_lines` | Candidate line numbers, or `none` |
| `pointer_target` | One row per `See @` target when `kind` is `pointer`; otherwise `-` |

Resolution: a non-empty `CLAUDE_CONFIG_DIR` wins, including when `~/.claude/CLAUDE.md` also exists. Whitespace-only is unset. A global `AGENTS.md` is noted, not required. Prefer `~/.agents/AGENTS.md` over `~/.codex/AGENTS.md` when both exist.

`not_a_file`, `broken_symlink`, and `unreadable` are blockers. Report the path and the status. Do not write.

## Step 2 — Missing file

Take this branch only when `claude_md_status` is `missing`.

1. Choose the body.
   - When `preferred_agents_md` is not `none`, the entire file is one line: `See @` plus the `pointer_import` value, then a single trailing newline. Do not add a title, a second line, or a rewritten path.
   - When `preferred_agents_md` is `none`, the body is the exact bytes of `templates/GLOBAL-CLAUDE.md`. Change only the Language section, and only when the conversation is not in English: state the user's language there. Say which sentence you changed. Leave every other section verbatim.
2. Show the destination path, why this body (pointer, or starter because no global AGENTS.md exists), both AGENTS.md statuses, and the full body in a fence.
3. Ask for a write instruction. State that you have not written anything, and that an approved write will create the parent directory if it is missing.
4. On approval, re-run the detector. If the status is still `missing`, exclusive-create the file. Then re-run the detector and report `exists`, the line count, and the kind.

Do not invent project names, hosts, absolute machine paths, or secrets in the body. If the user asks for a global `AGENTS.md`, stop. That file is out of scope until they confirm a separate body.

## Step 3 — Existing file

Take this branch when `claude_md_status` is `exists`. Read the file. Do not edit it in this step.

A `pointer` with exactly one target, that target existing, and that token equal to `pointer_import`, needs no change. Say so in a short report. Still list both AGENTS.md statuses. Two or more `See @` lines are P2 duplication: keep the one that equals `pointer_import` when that target exists, otherwise keep the first live target.

A `pointer` whose target is `missing` or `not_a_file` is a dangling pointer. Priority P0. Do not call language, stop-and-ask, or verification "missing"; they are not delegated until the target exists.

A live `pointer` whose token differs from `pointer_import`, while `preferred_agents_md` exists, is P1. Propose retargeting to `pointer_import`. Quote both tokens. Do not retarget a pointer that already matches.

A live pointer delegates language, stop-and-ask, and verification to its target. Read the target. Mark the three as delegated only after you have seen them there. If the target lacks one, report that gap against the target path, and do not propose stuffing it back into `CLAUDE.md`.

For `empty` and `prose`, write the report below. Check every item. A clean item goes under Passed with the evidence (detector key, or the section you read). An item you did not check goes under Not verified. Do not mark a check passed because you skipped it.

### Length

Use `claude_md_lines`. Skip this item for `kind: pointer`.

- 80 or fewer: pass.
- 81–150: P2. Name the sections to cut.
- 151–200: P1. Same, plus the line count.
- More than 200: P0. A global file this long is loaded into every session.

### Duplication and contradiction

Quote both sites. Two wordings of the same obligation are duplication (P2). Two different thresholds, or "always" against "never" for the same action, are a contradiction (P0 when one of them is destructive, otherwise P1).

### Project-specific content

P1 when the file carries one repo's facts: a repository path, a single service's build or deploy command, a ticket prefix, a customer hostname, "in this repo", or a tree such as `src/app/...`. Generic "run the checks the repo names" is not project-specific. The fix is to move the lines into that repo's `AGENTS.md`. Do not perform the move.

### Vague rules

P2 when an instruction cannot be checked or skipped on a stated condition. "Be careful", "high quality", "when appropriate", "use good judgment", "don't break things", and "keep it clean" qualify. Rewrite each as a command, a threshold, or a stop condition, or delete it.

### Missing essentials

Check `empty` and `prose` only. Do not flag a live pointer.

- **Language.** A sentence that names the reply language.
- **Stop and ask.** A list of actions that require asking first. Destructive actions (delete, force-push, publish, credentials) must be on it.
- **Verification.** An instruction to run a check and show the command plus the result before claiming done.

Each absence is P1. The starter template is the default rewrite for an empty file. For prose, add the missing sentence. Do not paste the whole template over a file that already has real rules.

### Stale tool references

A reference is stale only when you can show it. If the file names a binary or a path, test it (`command -v`, or read the path). P1 when the test fails and the file tells the agent to use that tool. If you cannot test it, list it under Not verified. Do not call a tool stale because it is old.

### Secrets and machine-specific paths

`secret_lines` are candidates. Read those lines. If the value is a live credential, a private key, a connection string, or a token prefix (`sk-`, `AKIA`, `ghp_`, `xox`), it is P0: report "line N matches a secret pattern" and do not quote the value. If the line is an instruction whose value is not a credential (`password: required`), drop it or record it as a false positive under Passed.

`machine_path_lines` are candidates. Quote the path. P1 when the instruction sends the agent to a user home such as `/Users/<name>` or `/home/<name>`, or to a drive path such as `C:\Users\<name>`. P2 when it is only an example. Suggest `~` or deletion. An IP literal that names one machine is P1; mention it only when you see one.

### Pointer recommendation

When `kind` is `empty` and `preferred_agents_md` is not `none`: P1. The proposed file is the one-line pointer from Step 2. An empty file has no rules to drop.

When `kind` is `prose` and `preferred_agents_md` is not `none`, read that AGENTS.md before you recommend a pointer.

- The global rules are already in that AGENTS.md: P1. The proposed file is the one-line pointer from Step 2. List the rules that the pointer would drop, and say they already live in the AGENTS.md.
- Some rules would be lost: P2. Do not propose replacing the file yet. List the rules to copy into the AGENTS.md first. State that copying them is out of scope until the user asks.
- `preferred_agents_md` is `none`: do not recommend a pointer. You may note that a later global AGENTS.md would let this file become one line. Do not create that file.

## Step 4 — Report

Use this structure. Write it in the language the user is using.

```
# Global CLAUDE.md review

**Path**: <claude_md_path>
**Status**: <status> | **Lines**: <n> | **Kind**: <kind> | **Via**: <via>
**Detector**: `python3 scripts/detect_global_claude.py`
**Global AGENTS.md**: ~/.agents <status>; ~/.codex <status>
**Preferred pointer**: `See @<pointer_import>` or "none"

## Prioritized changes
1. [P0|P1|P2] <one line>
or "None."

## Findings
### [P0] <title>
**Evidence**: <verbatim quote and location, or "line N, secret pattern, not quoted">
**Change**: <the exact replacement, or "delete line N">

## Passed
<each check you ran that was clean, with the evidence>

## Not verified
<each check you did not run, with the reason. "none" only when the list is empty>

## Proposed diff
<unified diff, or "none">
Not applied. Reply "apply the diff" or name item numbers to apply. Any other reply leaves the file untouched.
```

Order findings P0, then P1, then P2. Every finding appears in the prioritized list. Cap the list at the 15 most important findings. Summarize the rest in one line.

The diff is built from the current bytes and the proposed bytes. Do not shell-redirect onto the real path. Redact a removed secret line as `***redacted***`. A diff that would print the secret is not a diff you may show.

## Step 5 — Apply only on approval

Skip this step unless the user gave an apply instruction that names the diff or the item numbers.

1. Re-run the detector and re-read the file.
2. If the bytes differ from the bytes you reviewed, stop and re-report. Do not apply a stale diff.
3. Apply only the approved items. Leave every other line as it is.
4. For an approved secret deletion, delete that line number. Do not copy the secret into the write.
5. Show the resulting line count and kind. Do not claim the file is clean unless you re-ran the checks that the edit touched.
