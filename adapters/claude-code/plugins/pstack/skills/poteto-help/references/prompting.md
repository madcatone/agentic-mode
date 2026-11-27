# Word the prompt

A prompt states the intent and the check for done. A few plain sentences beat a spec.

## Put in

- The goal. Say what is wrong or what the user wants.
- The done check. It can pass or fail. "Make it better" and a duration are not checks.
- The proof to show. Ask for the real command output, a video of the flow, the stored value, or a before and after number.
- What the user already knows. A symptom, a repro step, a log, or a link saves the agent a search.
- The real constraints. "repro first", "don't change any code yet", "zero behavior change", and "let me review before proceeding" each change what the agent does.

## Leave out

- The method. Say what to achieve, and leave the agent room to find a better way.
- A list of skills or steps. A hand-written order drops or reorders steps. Name a skill only to pick that skill's procedure.
- The user's theory of the cause, until the agent restates the problem. A stated guess narrows the search.

## Load the context first

- For a noisy report, run `/in-your-own-words` before any other work. A misreading shows up before any code exists.
- Before a change to unfamiliar code, have the agent state what the code does and why it is shaped that way, from the files, before it edits.
- Ask the agent to make the case for a choice, as in "convince me it fixes the cause and not the symptom". A case is easier to check than a summary.
- Run `/reframe` when the description lacks the expert words for the thing being built. Run `/sharpen` when the prompt is too shallow.

## Design before the plan

- Never take the first design. Ask for prototypes of a few options, with screenshots or videos for UI, and pick from the evidence. `/architect` sketches the shape. `/arena` compares attempts.
- Let prototypes answer the open questions. Skip an adversarial review of an abstract plan. Reviewers invent risks that do not occur in the code.
- For a shared package or API, ask for the README or a tutorial first, then work back to the code. The doc becomes the target the agent checks itself against.
- Ask for the plan only after the design is settled. Each step of the plan ends in a check. `/figure-it-out` is the skill for a large run.

## Follow up short

- "do it", "continue", and "keep going until done" are whole prompts once the chat holds the task.
- Start with "new task" when the subject changes.

## Before stepping away

- Say "im going to bed" or "im stepping away" so the agent stops asking.
- Write done as checks every iteration can run.
- Ask for a fresh worktree off a named base.
- Pre-answer what the agent would stop for, such as "don't ask me before committing".
- Ask for a decision log to audit later. `/figure-it-out` keeps that trail.
- Give an exit: "if you are still blocked after 2 hours, stop and write up the blocker".

## Steer in one line

- Restate the goal: "i said the goal is to repro. i did not ask for a fix yet."
- Name the principle: "apply prove it works. show me the real output, not the build log."
- A principle name works because the agent can read the rule. Its reply names the decision the rule changed.
