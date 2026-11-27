---
name: poteto-help
description: "Answer a question about the shipped pstack skills and hand back a prompt. Use for /poteto-help, \"which skill\", or \"how do I use pstack\"."
---

# Poteto help

Answer the user's question about the skills shipped in this pack. Hand them a prompt they can send, and link the skill file the answer came from. For a help question, don't start the work. The user asked how, and a run spends real tokens, so let them send the prompt.

A message that asks for work, such as "use pstack to fix this bug", is not a help question. Name the skill that fits, give the prompt, and stop. Do not start the task in this turn.

This file maps questions to the skills shipped beside it. Those files own the details. Read the file you route to before you quote it, and trust it when it disagrees with this map.

This pack does not ship a setup skill, a mode skill, or these fourteen skills: `automate-me`, `bro`, `correct`, `how`, `make-bot-ui`, `no-comments`, `poteto-mode`, `recall`, `reflect`, `setup-pstack`, `show-me-your-work`, `swarm`, `teach`, `why`. When a question names one of those, say it is not in this pack and route to the closest shipped skill.

## Find out what they need

Infer the need from the message and the conversation. A named situation, such as "which skill reviews a PR?", goes straight to its section. If the message names no situation, ask one multiple-choice question with these options, then answer only the section they pick:

- Pick a skill for a situation
- Word a prompt
- Fix a run that went wrong
- Catch up on this chat

Check the state that changes the answer, and mention it only when it does:

- No `verify-*` skill in the project's skills directory means agents have no scripted way to drive the app. Mention `/create-verification-skill` when the question is about proving a change works.
- No formal verification skill in the project means no property is checked past what tests reach. Mention `/create-formal-verification-skill` when the question is about a race, an invariant, or another case tests rarely hit. When one exists and the code it covers changed after the commit it records as last in sync, mention `/maintain-formal-verification-skill` if the question touches that code.

## Pick a skill

Name a skill directly. Read the skill before you recommend it, and give one example prompt from [`references/recipes.md`](references/recipes.md).

| The user wants to | Skill |
|---|---|
| Check that the agent understood their goal and the problem before it starts | `/in-your-own-words` |
| Get a deeper prompt than the one you would send | `/sharpen` |
| Learn the expert words for what they're building, then get the description rewritten with those words | `/reframe` |
| Catch up on what changed in this chat since their last message | `/ketchup` |
| Catch up like `/ketchup`, as a short subtitled video. The text reply is the fallback when the machine lacks a slide-to-video tool | `/ketchup-video` |
| Know what a small diff could break outside itself | `/blast-radius` |
| Settle types and module shape before code that crosses a function boundary | `/architect` |
| Get several attempts at one brief, merged into the best one | `/arena` |
| Have adversaries try to break a diff, and keep only findings a run proves | `/interrogate` |
| Fix a bug test-first when a cheap local test exists | `/tdd` |
| Apply TypeScript rules to `.ts` or `.tsx` work | `/typescript-best-practices` |
| Clean AI tells out of prose | `/unslop` |
| Write docs, an RFC, a README, a PR description, or a commit message to a standard | `/technical-writing` |
| Give agents a scripted way to drive the app and prove behavior | `/create-verification-skill` |
| Bring a verification skill and its feature map back in line with the app | `/maintain-verification-skill` |
| Formally verify a race, invariant, or other property that tests rarely reach | `/create-formal-verification-skill` |
| Bring a formal verification back in line after the code it covers changed | `/maintain-formal-verification-skill` |
| Draw a TLA+ model as a Mermaid statechart and report the shortest path to each broken rule | `/statechart` |
| Vet a performance number before reporting or acting on it | `/benchmark-checklist` |
| Run a large or cross-cutting change, or one to review after stepping away | `/figure-it-out` |
| Find their way around this pack | `/poteto-help` |

If a skill directory next to this one is missing from the table, read its frontmatter and route by its description. The `principle-*` directories are covered under principles below.

Close calls:

- `/interrogate` reviews the diff and keeps a finding only when a run proves it. `/blast-radius` looks for breakage outside the diff and proves the one fact that makes the change safe.
- `/arena` gives every worker the same brief and merges the best parts.
- `/ketchup` covers only this chat since the user's last message. `/ketchup-video` shows that same window as slides. `/in-your-own-words` restates the goal before work starts.
- `/figure-it-out` designs one rigorous run when no narrower skill fits. `/architect` sketches the shape first. `/sharpen` rewrites the prompt and does not do the task.

## Catch up on this chat

Use `/ketchup` for a plain-words catch-up since the user's last message in this chat, with every call that waits on them. Use `/ketchup-video` for that same window as a short subtitled video. When no slide-to-video tool is available, `/ketchup-video` names the missing tool and gives the `/ketchup` text.

## Principles

Principles are one-rule skills. The user rarely invokes one. They steer with the names instead, as in "apply prove it works. show me the real output." Typing `/principle-<name>` still loads one on demand. The twenty-four shipped principles are:

- `principle-attack-the-premise`
- `principle-boundary-discipline`
- `principle-build-the-lever`
- `principle-encode-lessons-in-structure`
- `principle-exhaust-the-design-space`
- `principle-experience-first`
- `principle-explain-the-number`
- `principle-fix-root-causes`
- `principle-foundational-thinking`
- `principle-guard-the-context-window`
- `principle-laziness-protocol`
- `principle-make-operations-idempotent`
- `principle-migrate-callers-then-delete-legacy-apis`
- `principle-minimize-reader-load`
- `principle-model-the-domain`
- `principle-never-block-on-the-human`
- `principle-outcome-oriented-execution`
- `principle-prove-it-works`
- `principle-redesign-from-first-principles`
- `principle-separate-before-serializing-shared-state`
- `principle-sequence-verifiable-units`
- `principle-subtract-before-you-add`
- `principle-test-behavior-not-implementation`
- `principle-type-system-discipline`

## Word a prompt

A good prompt states the goal and how to tell it's done. It does not list a hand-written sequence of skills. Read [`references/prompting.md`](references/prompting.md) before you help word one. Name a skill only when the user wants that skill's procedure.

## Fix a run that went wrong

| Symptom | Fix |
|---|---|
| A question got treated as the next step of the last task | Say "new task". |
| The reply claims success from a green build | Ask for the real command, flow, stored value, or profile. That is the prove-it-works principle. |
| Parallel agents overwrote each other | Give each agent its own worktree. |
| A skill did not load | The user types its slash name, names it in the prompt, or the message matches a trigger phrase in that skill's description. |
| The reply is too long to catch up on | Run `/ketchup`. Use `/ketchup-video` when a slide video can be rendered. |

For a run that drifts, [`references/prompting.md`](references/prompting.md) has one-line steers.

## Reply

Lead with the answer. Give at most one example prompt in a code block, adapted from [`references/recipes.md`](references/recipes.md) when one fits, then the link to that file. Keep it short unless the user asked for the whole map.
