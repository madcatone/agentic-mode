# pstack skills added in the 0.15.48 resync

This pack now ships 45 skills: the previous 36, plus the nine below. Upstream
is `cursor/plugins` path `pstack/` at `9e278fe4d4ecd8bfe98b1b79bf4be662efb338cc`
(plugin version 0.15.48). The local plugin version is 1.1.0. Attribution and
the port adaptations are in [`../THIRD-PARTY-NOTICE.md`](../THIRD-PARTY-NOTICE.md).
Traditional Chinese: [`new-skills-zh.md`](new-skills-zh.md).

Invoke a skill by its slash name (`/ketchup`) or by the trigger phrases in its
frontmatter. Each file below is the procedure. This page is the operator guide.

## in-your-own-words

### Rules

The skill restates the user's goal and the problem they are solving, in the
agent's own words. It adds no plan, no code, and no extra questions. Stop when
the restatement is written. The restatement is the whole output.

### How to use

Trigger: `/in-your-own-words`, or "restate the goal before you start".

Input: the user's message, and any thread or spec they point at.

Example. The user pastes a long bug report and types `/in-your-own-words`.
The agent replies with the goal ("search returns notes from the wrong
notebook") and the problem ("the filter uses the account id, not the notebook
id"). It does not open a file.

Expected output: one restatement of the goal and one restatement of the
problem. `interrogate` consumes this restatement as the intent.

### Analysis

The skill exists because a long ask hides the goal, and the agent then solves
a nearby problem. Use it at the start of a messy thread, and before
`interrogate`. Skip it when the user already wrote a one-sentence goal and a
falsifiable done check. It relates to `sharpen` (which rewrites the prompt
after this check) and to `figure-it-out` (which needs a falsifiable predicate).
Pitfall: treating the restatement as permission to start the work. The skill
stops at the restatement.

## sharpen

### Rules

The skill makes the task deeper, not bigger, then rewrites the prompt. Before
the rewrite it must do four things, in order:

1. Say what a top professional in this field would do here that the user is
   not asking for.
2. Name the raw material that professional would start from, instead of a
   digest.
3. Name the methods and tools they would use.
4. Say what, other than the user or the agent, would show the result is right.

The rewritten prompt asks the agent to prototype any choice an experiment can
settle, and to recommend from what it observed. Choices that no experiment can
settle stay with the user. Stop when the four points and the rewritten prompt
are written. Do not do the task.

### How to use

Trigger: `/sharpen`.

Input: the prompt the user was about to send.

Example. The user writes "add caching to the feed". `/sharpen` answers the
four points (measure the feed's limiter first, start from production traces,
use the benchmark checklist, a profile is the outside check) and returns a
prompt that asks for a prototype of two cache shapes with before and after
numbers. It does not add a cache.

Expected output: four numbered points, then one rewritten prompt.

### Analysis

Shallow prompts produce shallow diffs. The skill exists to raise the task to
the work a specialist would actually do, without adding scope. Use it before
a non-trivial prompt. Skip it for a typo, a named one-line fix, or a prompt
that already names the raw material and the outside check. It sits in front of
`architect`, `arena`, and `figure-it-out`. Pitfall: "deeper" turning into
"more features". Depth is a better starting point and a real check, not a
longer backlog.

## reframe

### Rules

The skill teaches the expert words for what the operator is building, borrows
words from neighboring fields that solved the same shape of problem, then
rewrites the description with those words. It starts from the operator's
files, code, and description.

If the description could name more than one problem, first list the two or
three problems it could be. Each entry has the one term that names it and the
sign that tells it apart. Then teach the words for the most likely one and
say why that one was picked.

Then:

1. Give 8 to 12 terms, ranked by how much each would change what gets built.
   For each: the word, its meaning in one plain sentence, the part of the
   description it names, one real project, paper, or system that uses it that
   way, with a link, and what it lets the operator ask an agent for.
2. Pick 2 or 3 neighboring fields. For each, say what carries over, where the
   analogy breaks, and which terms come back.
3. Name what the operator did not mention and should care about.
4. Rewrite the description with the new words.

Open every link and confirm it uses the term that way. Cut any citation you
cannot confirm. Stop when the ranked terms, the neighboring fields, the
missing concerns, and the rewritten description are written. No padding.

### How to use

Trigger: `/reframe`.

Input: the operator's description, plus the files and code it points at.

Example. The user says "a queue that retries failed jobs". The description
could be at-least-once delivery or a saga. The agent lists both, with the
sign that tells them apart (a retry of the same job, versus a compensating
step), picks at-least-once, teaches 8 terms (idempotency key, dead letter,
and the rest) with checked links, names two neighboring fields, and rewrites
the description. It does not implement the queue.

Expected output: the disambiguation list when it applies, 8 to 12 terms, 2
or 3 fields, the missing concerns, and one rewritten description. Every link
was opened.

### Analysis

People describe systems in everyday words, then ask an agent to build the
wrong object. The skill exists to put the expert name on the object before
design starts. Use it when a description is vague or could be two known
problems. Skip it when the codebase already uses the standard term and the
description matches that term. It feeds `sharpen` and `architect`. Pitfall:
citations the agent did not open, and a rewrite that adds scope instead of
renaming the same scope.

## ketchup

### Rules

The skill catches the user up on this chat since the last message they wrote
before `/ketchup`, and lists every call that waits on them. Notifications and
subagent results are not their messages. The turn is read-only: do not change
code, start an app or a job, or post anything. Visuals come only from
material the chat already has.

An action item is a call only the user can take. Work the agent can still do
is not an action item. Do not invent a call. Keep what happened under 100
words, not counting pictures. Give each item 30 words. Keep every item. A
word count is not a reason to replace the list with a count or a link.

Voice: plain words, short sentences, no jargon. Say what changed for the
user. Leave out hashes, file paths, commands, build numbers, and test counts
unless the user needs one to act.

Stop when the reply has the opening sentence, the pictures, the summary
lines, at most three extra lines, and the action items. If nothing happened
and nothing waits, say so and stop.

### How to use

Trigger: `/ketchup`.

Input: the current chat. No extra argument.

Example. The user returns after a long implementation turn and types
`/ketchup`. The reply opens with "Two PRs wait on your merge." It embeds the
screenshot the earlier turn already captured, lists what came of each request
in one spoken line, and gives two action items: merge the index fix (low
risk, tests passed) and pick a color for the empty state.

Expected output: one opening sentence, inline pictures that already exist,
one short bullet per requested thing, then the action items with a pick, the
user-facing change, the evidence, and the risk.

### Analysis

A long agent turn buries the decision. The skill exists so the user can
decide from the reply alone, without scrolling the trace. Use it when you
return to a chat. Skip it when you want a cross-chat history (this pack does
not ship that skill) or a design. It is the text path that `ketchup-video`
falls back to. Pitfall: marking done a thing that still waits on the user, or
inventing a screenshot.

## ketchup-video

### Rules

Follow `ketchup`, with one change: show what happened as a short silent
landscape video of slides, instead of ketchup's summary and visuals. The
window starts at the last message the user wrote before `/ketchup-video`.
Writing and rendering the video, outside the repo, is the one exception to
ketchup's read-only rule.

Render with a slide-to-video tool available in the environment. When no such
tool is available, skip the video, name the missing tool in one line, and
give the `/ketchup` text reply. That fallback is a port adaptation. Upstream
assumes a renderer.

Slides: at most 10, one point each, built by changing one picture. A subtitle
is ten words, in a strip below the slide, burned into the frames. Hold each
slide at least one second for each three words it adds. Before embedding,
look at one frame from each slide at chat size and measure each hold from
the file's frames. Fix any slide you cannot read in that time, render again,
and check again.

The reply is ketchup's opening sentence, the embedded video, one line naming
work the agent can still do, and the action items. If the render fails, say
so in one line and give only the calls.

### How to use

Trigger: `/ketchup-video`.

Input: the current chat, plus a slide-to-video tool on the machine.

Example. The same return as `/ketchup`, but the user types `/ketchup-video`.
The agent writes one sentence the user should leave with, drafts six slides
from screenshots already in the chat, renders an mp4, checks a frame of each
slide, and replies with the opening sentence, the video, and the two merge
calls. On a machine with no renderer, the reply is one line naming the
missing tool plus the `/ketchup` text.

Expected output: opening sentence, video, leftover-work line, action items.
Or the named-tool fallback plus the ketchup text.

### Analysis

Some changes are easier to see than to read. The skill exists for that case,
with the same decision list as `ketchup`. Use it when the chat already has
screenshots or a visible before and after. Skip it for a pure library change
with nothing to point at, or when you only need the text. It depends on
`ketchup` for the window, the voice, and the action items. Pitfall: recording
the screen instead of rendering frames, or a subtitle that covers the slide.

## poteto-help

### Rules

Answer a question about the skills this pack ships. Hand back a prompt the
user can send, and link the skill file. Do not start the work. A message that
asks for work is not a help question: name the skill, give the prompt, and
stop.

Catalog only the 45 shipped skills. When the user names a skill this pack
does not ship, say so and route to the closest shipped skill. Do not send
them to a mode skill, a setup skill, or a personal rules file. That catalog
limit is a port adaptation. Upstream lists the whole collection.

If the message names no situation, ask one multiple-choice question (pick a
skill, word a prompt, fix a run, catch up) and answer only that section.
Mention `/create-verification-skill` when the question is about proving a
change and the project has no `verify-*` skill. Mention the formal pair when
the question is about a race or an invariant.

Stop when the answer, at most one example prompt, and the file link are
written.

### How to use

Trigger: `/poteto-help`, "which skill", "how do I use pstack".

Input: a question. Not a task.

Example. The user asks "which skill reviews a PR without changing it?"
The reply names `/interrogate`, gives one prompt from `references/recipes.md`,
and links `skills/interrogate/SKILL.md`. It does not review the PR.

Expected output: the skill name, one prompt in a code block, the link. The
whole map only when the user asks for it.

### Analysis

The pack is 45 procedures. The skill exists so the user can pick one without
reading every file. Use it when you do not know the slash name. Skip it when
you already know the skill, and when you want the work done in this turn.
Prompt wording lives in `references/prompting.md`. Copy-paste prompts live in
`references/recipes.md`. Pitfall: starting the task inside the help turn, or
recommending a skill this pack does not contain.

## create-formal-verification-skill

### Rules

Find the promise in the repo where a break harms users and tests rarely reach
the breaking case. Verify one property of it. Leave a project-local skill the
next agent can run cold.

Pick the cheapest tool that answers the question. A bad order of events
defaults to a TLA+ model checker, in any language. A property of the code
itself (memory safety, overflow, a data-structure invariant) uses a verifier
that runs on the code. If no verifier runs on this language, say so, test the
real code with generated inputs, and skip a hand model of the function.

The generated skill must be true to the code, able to fail (show each
property failing on a broken variant), honest about bounds, readable without
the tool, cheap to rerun, and marked with the files it covers and the commit
where that was last confirmed. The skill registers only when it has
frontmatter. Do not weaken the property to make the current code pass. Do not
change product code unless the user asks.

If the check is a TLA+ model, tell the next agent to read every result with
`/statechart`, by name. Copy none of statechart's commands into the generated
skill.

Prove it: follow the generated skill once on a scratch change that breaks the
property. It must catch the break. Drop the scratch change and confirm the
check is back where it started. A skill that was never run is a draft. Stop
when that proof has run and the hand-off is written. Point at
`/maintain-formal-verification-skill` for later drift.

### How to use

Trigger: `/create-formal-verification-skill`, "model-check this race", "prove
this invariant".

Input: a repo, and an area or bug if the user named one. Otherwise the agent
picks the strongest target it can observe.

Example. A payments service has a retry that can double-charge. The agent
writes a small TLA+ model, shows the invariant failing when the idempotency
check is removed, restores the check, generates `verify-charges/SKILL.md` in
the project's skills directory, runs that skill once, and tells the user the
tool, the bounds, the command, and what is left out.

Expected output: a project-local skill with a coverage record and a sync
commit, plus a hand-off in plain words. The scratch break is gone.

### Analysis

Tests check the cases someone wrote. The skill exists for the cases they did
not: interleavings, retries, parsers, unsafe code. Use it when a bug there is
expensive and tests do not reach it. Skip it for ordinary UI behavior
(`create-verification-skill` drives the app) and for a one-off bug with a
cheap test (`tdd`). `statechart` reads the TLA+ result. `maintain-formal-verification-skill`
keeps the model true after later commits. Pitfall: a check that has never
been seen to fail. Also a model whose parts do not point at a file a reviewer
can open.

## maintain-formal-verification-skill

### Rules

Bring a formal check back in line with the code after commits that skipped
the verify skill. Edit only the verification: models, harnesses, property
files, and the verify skill. Leave product code alone unless the user asks.
Do not weaken a property to make a check pass.

Each check gets one outcome: **in sync**, **updated**, **bug**, or
**blocked**. A check can be both updated and bug.

The pass:

1. Find the verify skill by what it does. If none exists, stop and point at
   `/create-formal-verification-skill`.
2. Run each check once before any edit. A pass here means the old description
   still holds. It does not mean the code is right.
3. Read every change to covered code from the sync commit, including renames
   and new writers of the guarded state. Class each change: no effect, the
   verification no longer describes the code, the promise changed on purpose
   (cite the evidence), or the promise may be broken.
4. Update from the code, before the rerun. Do not shape the model by what
   makes the check pass.
5. Rerun. On a pass, break the new code the way the property guards against,
   confirm the check catches it, and drop the break. On a fail, replay the
   counterexample on the real code. A step that cannot happen means the
   verification is wrong. A step that can happen is a bug.
6. Update the sync commit only for a check you brought back. Follow the
   verify skill once so its steps still run.

Stop when the report is written and verification updates sit in their own
change, separate from any product fix.

### How to use

Trigger: `/maintain-formal-verification-skill`, "is the model still true to
the code", after merges that touched verified code.

Input: the project-local verify skill, or the one the user names.

Example. Three commits renamed `charge` and added a refund path. The agent
runs the old model (it still passes), reads the commits, updates the model so
the refund is a step, breaks the refund idempotency check on a scratch copy,
sees the checker catch it, restores the scratch, and reports outcome
**updated** with the new sync commit. A real double-refund that the replay
can perform is outcome **bug**, with the commit that introduced it.

Expected output: one outcome per check, the commits read, what changed in the
verification and the evidence, the rerun, the break used to show it can still
fail, and each bug as steps in the code's words.

### Analysis

A stale model that still passes is worse than a failing test, because it
looks like a proof. The skill exists to separate drift from bugs. Use it
after merges and refactors in covered code. Skip it when the verify skill
does not exist yet, and when you are creating the first model (use
`create-formal-verification-skill`). It is the upkeep pair of that skill, the
way `maintain-verification-skill` is the upkeep pair of
`create-verification-skill`. Pitfall: editing product code during the pass, or
moving the sync commit on a blocked check.

## statechart

### Rules

Check a TLA+ model of a system that moves between states, and draw it as a
Mermaid statechart. The report gives the shortest path to each state that
breaks a rule. The reader decides whether the behavior is right.

Work in a scratch folder outside the repo. Write the spec and config, then
run `scripts/statechart` from this skill's directory (a POSIX shell script
that runs the TypeScript). On native Windows, run the `.ts` file with Node
22.18 to 22.x, or Node 23.6 or later. The first run installs TLC and Java and
needs a network.

Write each rule the reader agrees to as an INVARIANT. Do not weaken a rule to
make it hold. A state with no step out breaks `NoDeadlock`, including a
correct end state: add a do-nothing action that is true only in the end
states.

Put judgment in a view module (`--view`): the words on states and arrows, the
phases, the colors, the title. Keep the chart to 20 arrows or fewer. Keep
every state of a bug path. Keep two states that break different rules as two
states. When you hide steps, keep every chart state reachable, keep one arrow
out of each state that has a step out, and hide all of an arrow or none of it.

The chart has a budget of 500 states. Above that, it draws only the paths to
broken rules. Show `chart.mmd` as a mermaid code block. Images use the
renderer named in `references/render.md`.

Stop when the reader has each chart, one line per bug (rule, sentence, path),
what the model leaves out, and the command that regenerates the files. When
the model describes code, replay each bug path against the real code. If the
bug does not occur, treat the model as wrong until you show otherwise.

### How to use

Trigger: `/statechart`, or "show this bug as a path through states".

Input: a TLA+ spec, or a description the agent turns into one. A view module
when the reader needs specific words.

Example. A login flow can skip the second factor. The agent writes the spec
in a scratch folder, runs the script, and replies with the mermaid chart, the
line "Invariant second factor: Login, Password, Home", and the command that
rebuilds the files. The path is then replayed as a test against the real
handlers.

Expected output: `chart.mmd` (when the state count is within 500 or a rule
breaks), the report's shortest paths, and the hand-off lines. No chart file
when no rule breaks and the model is over 500 states. The report still lists
the state count.

### Analysis

A counterexample dumped by the model checker is hard to read. The skill exists
to show the shortest path in the reader's words. Use it for a product flow, a
protocol, or a service, and whenever `create-formal-verification-skill`
produced a TLA+ model. Skip it for a property that is not a state machine
(use the verifier that skill already chose) and for a bug with a cheap local
test. It consumes models. It does not replace `interrogate` or `tdd`.
Pitfall: labels that use variable names, a chart that merges two broken
rules into one state, and copying this skill's command lines into another
skill (those paths change between machines).
