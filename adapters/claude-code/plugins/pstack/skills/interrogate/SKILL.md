---
name: interrogate
description: "Use for \"interrogate\", \"adversarial review\", \"multi-model review\", \"challenge this\", \"stress test this code\", \"find blind spots\", or \"tear this apart\". Multiple LLM reviewers challenge changes from independent angles."
---

# Interrogate

Spawn one reviewer per model to adversarially review code changes. Each model gets the same prompt and rubric. The adversarial signal comes from model diversity, not assigned personas.

The deliverable is a synthesized verdict. Do NOT auto-apply changes.

## Step 1, Determine Scope

Identify what to review from context:

- If the user points at specific files or a diff, use that
- If on a feature branch, run `git diff main...HEAD` (or the base branch this repo uses) for the full changeset
- If the user's message references recent work, gather the relevant files

Package the diff (or file contents) plus any surrounding context files the reviewers need to understand the code.

## Step 2, State the Intent

Before spawning reviewers, state the intent explicitly. Derive this from:

- The user's message
- Commit messages
- PR description if one exists
- The code itself

Write one clear paragraph. If the intent is vague, unstated, or contradictory, ask the user to state it before you review.

## Step 3, Spawn Reviewers

Launch all reviewers in a single message. Use the reviewer models set in the project's agent configuration (a rules or settings file your harness reads), one reviewer per entry, extending or shrinking the Reviewer A/B/C labels below to the configured entry count. With no configured models, use the table defaults.

| Subagent | Default model |
|----------|---------------|
| Reviewer A | Your strongest available model |
| Reviewer B | A second model from a different family, where one is available |
| Reviewer C | A third model, from a family the first two do not cover |

Where the available models cover fewer than three families, fill each seat with the strongest model from a family not yet used. Where every available family is already used — a third reviewer in a two-family environment, for example — run that reviewer on your strongest available model. In a single-family environment, run every reviewer on your strongest model. Say so in the verdict whenever the diversity shown above is reduced.

For each reviewer, spawn a read-only general-purpose subagent on the configured entry, or on the table default with no configured models. For an `auto` or `inherit-parent` entry, omit the model setting so that reviewer runs on the parent model.

If the harness rejects a configured model, run that reviewer on the strongest available model of the same family and say so in the verdict; where that family offers no available model, switch that reviewer to a different family and say so. Do not block the review on the model question. An `auto` or `inherit-parent` entry is an alias for the parent model, so treat it as configured, never as rejected.

Read `references/reviewer-prompt.md` and fill in the template with:
1. The stated intent
2. The diff or file contents
3. The review rubric from `references/rubric.md`
4. The code-quality lens from `references/code-quality-review.md`

The same filled template goes to all reviewers, so every model applies the code-quality lens.

## Step 4, Synthesize

As results come back, build a unified picture:

1. **Parse all findings** from the reviewers
2. **Identify consensus**. Findings raised by 2+ models independently are highest signal.
3. **Identify lone-model findings**. Still worth reading, but weight accordingly.
4. **Deduplicate**. Different models may describe the same issue differently. Merge these and note which models raised it.
5. **Note disagreements**. If one model flags something and another explicitly says the opposite, that's useful context for the verdict.

## Step 5, Lead Judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.

Read `references/lead-judgment.md` for the full framework.

Categorize every finding using these buckets:

- **Act on**. Real issues affecting correctness, security, or maintainability given the actual goals. These would block a real PR.
- **Consider**. Legitimate points, but you're not sure they outweigh the cost of addressing them right now. Worth the user's attention.
- **Noted**. Technically valid but not actionable. Context-dependent, premature optimization, or low-impact given the current stage.
- **Dismissed**. Wrong, nitpicky, or missing context. Brief explanation why.

For each finding, include:
- Which model(s) raised it
- The category (act on / consider / noted / dismissed)
- A one-line rationale for the categorization

## Output Format

Present the verdict in this structure:

### Intent
> [The stated intent paragraph from Step 2]

### Reviewers
- Reviewer [label]: [model name], [N findings] (one bullet per reviewer)

### Act On
[Findings that should be addressed. For each: description, which models raised it, why it matters.]

### Consider
[Findings worth thinking about. For each: description, which models raised it, tradeoff involved.]

### Noted
[Valid but low-priority. Brief list.]

### Dismissed
[Rejected findings with brief rationale.]

### Agreement Map
[Where did models agree, where did they diverge, and what does the pattern of agreement/disagreement tell us?]
