# Prompts worth copying

Swap in the real paths, skills, and done checks. Informal wording works. Each prompt uses a skill this pack ships.

## Understand

- `/in-your-own-words <long or messy ask>`
- `/sharpen <the prompt you're about to send>`
- `/reframe <what you are building, in your words>`
- `read <thread>. restate the underlying issue in your own words, in plain english. run /in-your-own-words.`
- `investigate <symptom>. give me what we know, what data you used, and your best hypotheses. don't change any code yet.`
- `read <subsystem> and state what it does and why it is shaped that way before you edit.`
- `convince me you implemented it this way and not <other way>. what did you trade off?`
- `/figure-it-out take over this branch. read the decision log, find what's done, and continue. don't redo finished work.`

## Build

- Bug: `<symptom>. repro first, then fix and verify.`
- Bug in an app: `repro this with the project's verify skill. if it repros on main, fix it and show me evidence.`
- Bug with a cheap test: `repro <bug> first. if there's a cheap test path, /tdd it. then fix and rerun.`
- Feature: `add <behavior>. <current output> stays byte-identical. verify both.`
- Refactor: `move <code> into one module, zero behavior change. record the current output first and prove it's unchanged after.`
- Perf: `<operation> takes <time> on <fixture>. trace it, fix the measured cause, show me before and after. run /benchmark-checklist on the number.`

## Design and plan

- `prototype a few options for <feature>. take screenshots for me to compare.`
- `/architect we need <feature>. answer open questions with prototypes. let me review before proceeding.`
- `write a tutorial for how i would use <new package> first, under /technical-writing. then make the case for why it beats the current one.`
- `/arena give me a second opinion on this thread and our approach.`
- `/figure-it-out turn this design into a plan. small verifiable PRs, each with its own verification steps.`
- `/figure-it-out plan the migration of <library> to <target>. small verifiable PRs. the result must match the original exactly, bugs included.`

## Review and ship

- `/interrogate the whole branch. don't change anything yet.` Read the Dropped list too.
- `/create-formal-verification-skill prove <property> holds in <module>, even when <steps> interleave or retry.` After merges or refactors in that code: `/maintain-formal-verification-skill`.
- `/blast-radius what could this diff break outside itself? prove the one fact.`
- `open the pr. small ordered commits, evidence in the description. run /technical-writing on the body.`
- `/unslop this doc.`
- `/typescript-best-practices review the .ts change. branded ids go through a type guard.`

## Away and back

- `/figure-it-out <goal> in a fresh worktree off <base>. done means <checks>. keep a decision log. don't ask me before committing. if you are still blocked after 2 hours, stop and write up the blocker.`
- `/ketchup` catches you up on this chat since your last message and lists every call that waits on you.
- `/ketchup-video` does the same as a short subtitled video. When no slide-to-video tool is available, it falls back to the `/ketchup` text and names the missing tool.
