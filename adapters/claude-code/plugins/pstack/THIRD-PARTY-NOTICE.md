# Third-party notice: pstack

The 45 skills in `skills/` of this plugin come from the pstack collection
published at https://github.com/cursor/plugins/tree/main/pstack (repository
`https://github.com/cursor/plugins`, path `pstack/`). This copy is taken from
commit `9e278fe4d4ecd8bfe98b1b79bf4be662efb338cc`, which ships upstream plugin
version 0.15.48. They are used under the MIT license reproduced verbatim at
the end of this file.

## Included skills

Twenty-one workflow skills:

- `architect`
- `arena`
- `benchmark-checklist`
- `blast-radius`
- `create-formal-verification-skill`
- `create-verification-skill` (with `references/feature-map-example/`)
- `figure-it-out`
- `in-your-own-words`
- `interrogate`
- `ketchup`
- `ketchup-video`
- `maintain-formal-verification-skill`
- `maintain-verification-skill`
- `poteto-help` (with `references/prompting.md` and `references/recipes.md`)
- `reframe`
- `sharpen`
- `statechart` (with `scripts/` and `references/render.md`)
- `tdd`
- `technical-writing`
- `typescript-best-practices` (with `references/patterns.md`)
- `unslop`

Twenty-four principle skills, each under `principle-<name>`:

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

Guides for the nine skills added in this resync (rules, usage, analysis), in
English and Traditional Chinese:

- `docs/new-skills.md`
- `docs/new-skills-zh.md`

## Not included

Fourteen upstream skills are still omitted. Shipping them is a follow-up
decision for the owner:

- `automate-me`
- `bro`
- `correct`
- `how`
- `make-bot-ui`
- `no-comments`
- `poteto-mode`
- `recall`
- `reflect`
- `setup-pstack`
- `show-me-your-work`
- `swarm`
- `teach`
- `why`

## Modifications relative to the source

- The frontmatter of each `SKILL.md` keeps the `name` and `description` fields
  only. The harness-specific `disable-model-invocation` key is removed. The
  `paths:` key on `typescript-best-practices` is removed.
- Model names, agent-tool identifiers, and personal configuration paths from
  the source are rewritten in neutral, portable terms. A runner list lives in
  "the project's agent configuration". A generated verify skill lives in "the
  project's skills directory". Scratch directories are run-scoped and sit
  outside the repo. This copy does not use `/tmp`.
- The wording in this copy passes this repo's ASD-STE100 doc check on the
  shipped instruction files. Test corpus reports under `statechart/scripts/test/`
  are upstream fixtures and are unchanged. Modifications are permitted under
  the MIT license.
- Skills that are not shipped are not named as steps. Where upstream pointed
  at one, the step states the same action in place, or points at a skill this
  pack does ship (`architect`, `arena`, `in-your-own-words`, and the rest).
- `poteto-help` catalogs only the 45 skills in this pack. It does not route
  to a mode skill, a setup skill, a personal rules file, or the fourteen
  omitted skills. Its prompt and recipe files use the shipped slash names.
- `ketchup` states the plain-words voice in the skill body. Charts are drawn
  from numbers the reply already has. It does not call an unshipped chart
  command.
- `ketchup-video` follows `ketchup`, then renders a silent slide video with
  whatever slide-to-video tool the environment provides. When no such tool is
  available, the skill skips the video, names the missing tool, and gives the
  `ketchup` text reply.
- `statechart` ships its TypeScript runner, tests, and corpus. The first run
  installs TLC and Java and needs a network. Chart images use the renderer
  named in `references/render.md`. The skill's own scratch folder stays
  outside the repo.
- Upstream reference files this commit stopped citing are absent from this
  copy: `architect/references/design-red-flags.md`,
  `architect/references/rationale-template.md`,
  `architect/references/runner-prompt.md`,
  `interrogate/references/code-quality-review.md`,
  `interrogate/references/lead-judgment.md`,
  `interrogate/references/reviewer-prompt.md`,
  `interrogate/references/rubric.md`.

## License

<!-- doc-lint:ignore-start -->
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
<!-- doc-lint:ignore-end -->
