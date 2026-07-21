# Agent Doc Linter — ASD-STE100-adapted document lint (playbook)

**About this playbook.** This file is the canonical, harness-neutral version.
Any collaborator — human or agent, in any tool — can read it directly as a rules
file; installation as an optional plugin is described under `adapters/`. It is
**pure markdown, self-contained, and writes nothing** except the one document you
point it at in fix mode, after you accept the rewrites. **Local repo rules (a
style guide, a terminology glossary) take precedence over this playbook.**

Lint instruction documents with rules adapted from ASD-STE100 (Simplified Technical English). The premise: an AI agent fails in the same way an aircraft technician fails — it executes the literal text, and ambiguity causes wrong actions. The linter finds the ambiguity before the agent does.

This playbook applies to any document that an agent or a person must follow: skills, CLAUDE.md, HANDOFF.md, README, runbooks, prompts, slash commands, onboarding guides.

This file is self-contained by design: the full rule catalog is below, so it works even when someone copies this single file into another project or tool. Do not split the catalog into separate reference files.

## Workflow

Follow these steps in order.

### Step 1 — Classify the document

Identify:
- **Document type**: skill / claude-md / handoff / readme / runbook-or-prompt / generic. If unsure, ask the user.
- **Language**: English / Traditional Chinese / mixed. Lint rules apply to all languages. Write the report in the language the user speaks in the conversation.

### Step 2 — Build the terminology map

Before you check any other rule, read the full document once and list each key concept with every name the document uses for it. Example:

```
concept: the generated output file
  names used: "report", "document", "deliverable", "the file"
```

A concept with 2+ names is a T1 finding. Do this step first because terminology drift hides inside every other rule.

### Step 3 — Run the rule catalog

Check the document against every rule in the [Rule catalog](#rule-catalog) below, then apply the matching section of [Document-type checks](#document-type-checks).

### Step 4 — Write the report

Use this exact structure:

```
# Lint report: <document name>

**Type**: <type> | **Language**: <language> | **Findings**: <N> (<x> error, <y> warning, <z> info)

## Summary
<2-3 sentences: the document's biggest systemic problem, not a list of findings.>

## Findings

### [T1 · error] <one-line title>
> <verbatim quote of the offending text, with location such as section name or step number>

**Problem**: <why an agent misreads this — one or two sentences.>
**Rewrite**:
> <the corrected text, ready to paste>

<repeat per finding, ordered by severity: error → warning → info>

## Passed
<one line listing the categories with no findings, so the user knows they were checked.>
```

Severity levels:
- **error** — an agent following the text literally does the wrong thing, or cannot decide what to do.
- **warning** — the text is decidable but costs extra inference (hedge words, drift, passive voice).
- **info** — style and structure improvements (length, ordering, deletion candidates).

Rules for the report itself:
- Quote the document verbatim in every finding. Never paraphrase the evidence.
- Every finding includes a ready-to-paste rewrite. A finding without a rewrite is not a finding.
- Do not invent findings to look thorough. A clean document gets a short report. Cap the report at the 15 most important findings; summarize the rest in one line.

### Step 5 — Offer fix mode

After the report, offer to apply the rewrites. If the user accepts:
1. Copy the document to a writable location if the original is read-only.
2. Apply the rewrites with edits. Do not restructure beyond the findings unless the user asks.
3. Show a summary of what changed.

## Constraints

- Lint the writing, not the logic. If a step seems technically wrong (a wrong command, a wrong API), flag it once as a separate note outside the findings — that is a review comment, not a lint finding.
- Preserve the author's voice in rewrites. Fix the ambiguity; do not flatten the style.
- Do not apply STE's 900-word approved vocabulary. Agents handle rich vocabulary well. The controlled part is structure and ambiguity, not word choice.
- This playbook's own file follows its own rules. If you find a violation in this file, tell the user.

---

# Rule catalog

Each rule has an ID, a severity, detection guidance, and a before/after example.

## T — Terminology

### T1 · error — One name per concept
Each concept gets exactly one name across the whole document: title, description, body, examples, and code comments.

**Detect**: Use the terminology map from Step 2. Any concept with 2+ names is a finding. Watch for English/Chinese pairs that name the same concept ("報告" and "report" in one document counts as drift unless the pairing is defined once).

Before:
> Generate the report. Save the document to outputs. Present the deliverable to the user.

After:
> Generate the report. Save the report to outputs. Present the report to the user.

### T2 · warning — Define on first use
Define each project-specific term, acronym, or internal tool name the first time it appears. After the definition, use the term without re-explaining.

Before:
> Sync the MR corpus into ES before drift detection runs.

After:
> Sync the merge request (MR) corpus into Elasticsearch (ES) before drift detection runs.

### T3 · warning — Names match between rules and code
Identifiers in prose match identifiers in code blocks exactly, including case. If the prose says `output_dir` the code block must not say `outputDir`.

## S — Sentences

### S1 · error — Imperative active voice for instructions
Write every instruction as a command with an explicit actor and action. Passive voice hides the actor, and an agent may read a passive sentence as background description instead of a step to execute.

Before:
> The file should be validated before processing is started.

After:
> Validate the file before you start processing.

### S2 · error — One action per step
Each numbered step contains one action. An agent frequently executes the first clause of a compound step and drops the rest.

Before:
> 3. Parse the config, apply the overrides, and restart the service if any value changed.

After:
> 3. Parse the config.
> 4. Apply the overrides.
> 5. If any value changed, restart the service.

### S3 · info — Sentence length
Keep instruction sentences under about 25 words (English) or about 40 characters (Chinese). Split longer sentences at each conjunction. This limit applies to instructions, not to explanatory prose.

### S4 · warning — Number every procedure
When steps must run in order, use a numbered list. Use bullets only when order does not matter. Prose paragraphs that hide a sequence ("first do X, then after Y you can Z") are a finding.

## H — Hedging and ambiguity

### H1 · warning — No hedge words in instructions
Hedge words make an instruction optional without saying when to skip it. Remove the hedge, or replace it with an explicit condition. See [Hedge word lists](#hedge-word-lists).

Before:
> Ideally, clean the data before analysis if it appears to be messy.

After:
> Examine the data first. If it has merged cells, missing headers, or mixed types, clean it before you start the analysis.

### H2 · error — Conditions have testable criteria
Every "if" must be decidable from information the agent has. "If the input is large" is not decidable; "if the input exceeds 10 MB" is.

Before:
> If the response takes too long, retry.

After:
> If the response does not arrive within 30 seconds, retry once.

### H3 · warning — No vague quantifiers where a number matters
"Some", "a few", "several", "as many as needed" — replace with a number or an explicit range when the quantity changes behavior.

Before:
> Include a few representative examples.

After:
> Include 2 to 3 representative examples.

## N — Negation

### N1 · error — Pair every prohibition with a positive alternative
A bare "do not X" leaves the agent without a path forward, and stating X alone pulls X into attention. State what to do instead.

Before:
> Do not use pypdf.

After:
> Do not use pypdf. Use pdfplumber instead.

### N2 · warning — No stacked negations
More than one negation in a sentence forces the reader to compute the polarity. Rewrite as a positive statement.

Before:
> Do not skip validation unless the input is not user-provided.

After:
> Validate all user-provided input. Skip validation only for input that the system generated itself.

## P — Placement and structure

### P1 · error — Warnings before the step they guard
Place a warning or precondition immediately before the step it applies to. An agent decides at the step; a warning at the end of the document arrives after the decision.

Before:
> 1. Delete the old index.
> 2. Rebuild from the corpus.
> ...
> Note: never delete the index while a sync job is running.

After:
> 1. Confirm that no sync job is running. Never delete the index during a sync.
> 2. Delete the old index.
> 3. Rebuild from the corpus.

### P2 · info — Split files only when the split survives distribution
Move content to a separate reference file only when both conditions hold: the content is read conditionally (only some runs need it), and the distribution method guarantees the file travels with the main document. Content that every run needs stays in the main document. A pointer to a file that may not exist is worse than a long document.

### P3 · info — Deletion test
For each rule in the document, ask: if I delete this line, does the agent's behavior change? If no, delete it. Filler that restates common sense dilutes the rules that matter.

### P4 · error — No duplicate or conflicting instructions
The same instruction stated twice drifts into two versions over time. Two rules that conflict force the agent to pick one silently. State each rule once; when a conflict is intentional, state the precedence explicitly.

## E — Examples

### E1 · warning — Good/bad pairs for critical behavior
For each behavior where failure is costly, include one correct example and one incorrect example, labeled. A rule without an example is instruction; a rule with a contrasting pair is training data.

### E2 · warning — Examples use the rules' terminology
An example that introduces a new synonym undoes T1. Check every example against the terminology map.

---

# Document-type checks

Apply the section that matches the document type. These add to the rule catalog; they do not replace it.

## skill (SKILL.md)

- **D-SK1 · error** — All triggering information lives in the frontmatter `description`, none in the body. The body is invisible until the skill triggers.
- **D-SK2 · warning** — The description names concrete trigger phrases a user would actually type, in each language the user works in.
- **D-SK3 · warning** — The body opens with the workflow, not with background. Background goes after the workflow or into a reference file.
- **D-SK4 · info** — Body under ~500 lines. If longer, cut with the deletion test (P3) first; split into reference files only when the split passes P2.

## claude-md (CLAUDE.md / project memory)

- **D-CM1 · error** — Every line is an imperative rule or a fact the agent needs. Narrative history, aspirations, and explanations of why the project exists are findings.
- **D-CM2 · warning** — Rules are grouped by topic with headers, so a rule can be found and updated without reading the whole file.

## handoff (HANDOFF.md / session notes)

- **D-HO1 · error** — Every claim about project state is verifiable: it names a file path, a commit, a command output, or a ticket ID. "The refactor is mostly done" is a finding; "modules A and B migrated, C remains — see commit abc123" passes.
- **D-HO2 · error** — Next actions are imperative and self-contained. The next session must be able to execute them without asking what they mean.
- **D-HO3 · warning** — Each entry has a timestamp and appends to the file; nothing overwrites prior entries.
- **D-HO4 · warning** — Open questions and known-broken states are listed explicitly, not implied.

## readme (README)

- **D-RM1 · warning** — The first screen answers: what is this, who is it for, how do I run it. History and design rationale come later.
- **D-RM2 · error** — Setup commands are complete and copy-pasteable: they include the working directory and prerequisites, and they run in the order written.
- **D-RM3 · warning** — The README states which parts an agent may rely on as stable (commands, paths) versus descriptive prose that may lag the code.

## runbook-or-prompt (runbooks, slash commands, system prompts)

- **D-RB1 · error** — The trigger condition is explicit: exactly when does this procedure apply, and when does it not.
- **D-RB2 · error** — Every step with a side effect (deploy, delete, send, publish) states its precondition and its rollback or abort path.
- **D-RB3 · warning** — The expected end state is stated, so the executor can verify completion.

## generic

Apply the rule catalog only.

---

# Hedge word lists

Flag these when they appear in an instruction sentence. In explanatory prose they are acceptable.

**English**: might, may (as "perhaps"), could, should ideally, ideally, if possible, if needed, as needed, as appropriate, when appropriate, appears to, seems to, generally, usually, typically, try to, attempt to, consider doing, it might be necessary, feel free to, prefer (when the rule is mandatory).

**中文**: 可能、或許、視情況、必要時、如有需要、適當地、適時、盡量、儘可能、原則上、基本上、一般來說、通常、似乎、看起來、考慮、建議可以、應該要(當作「大概要」使用時)。

**Replacement pattern**: for each hedge, either delete it (the instruction is mandatory) or replace it with a testable condition (H2). "盡量保持句子簡短" → "指令句不超過 40 字;超過就拆句"。
