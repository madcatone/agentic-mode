<!--
TEMPLATE: docs/USER_GUIDE.md for project.type == "web-service". Observable surface = endpoints/routes,
screens/views, and state flows. Filled from config.json (id.prefix, bilingual.*) and Phase-A answers
(the HTTP surface mined from the router / route definitions, and the UI screens if any).
Every endpoint/screen/state CITES its owning {{PREFIX}}-XXX from REQUIREMENTS. The endpoint and route
tables must match the source router 1:1.
`{{RUNTIME_PLACEHOLDERS}}`: when the target needs none, delete the sentence that starts with `Provide`.
`{{BASE_URL_PLACEHOLDER — e.g. http://localhost:<port>}}`: the address a developer uses locally. Write
the target's real local address when it has one.
A service with no authentication loses the Authentication section, headings included, and its Auth
column reads `none`.
BILINGUAL: keep the second track ONLY IF config bilingual.enabled == true; else delete it.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Template-Source: agentic-bootstrap/USER_GUIDE-web@v2  (@v2: the title takes the component-name
slot; no descriptive slot holds a second placeholder; the ID examples use three digits; the
header states the cuts for a service with no runtime placeholders and for one with no
authentication)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# {{COMPONENT_NAME}} — User Guide (Web Service)

## English

### Purpose
{{1-2 sentences: what this service does, who calls it, when to choose it over siblings.}}

### Running Locally
```bash
{{run_server_command}}
```
Base URL: `{{BASE_URL_PLACEHOLDER — e.g. http://localhost:<port>}}`. Provide {{RUNTIME_PLACEHOLDERS}} at runtime; do not hardcode hosts.

### Endpoints
The HTTP surface. Must match the router 1:1.

| Method | Path | Purpose | Auth | Requirement |
| --- | --- | --- | --- | --- |
| `GET` | `{{/path}}` | {{what it returns}} | {{none/token/session}} | {{PREFIX}}-NNN |
| `POST` | `{{/path}}` | {{what it does}} | {{...}} | {{PREFIX}}-NNN |

#### `{{METHOD}} {{/path}}`  ({{PREFIX}}-NNN)
- **Request:** {{path/query params, body schema — with placeholder values}}.
- **Response:** {{status codes + body schema}}.
- **Errors:** {{status → condition}}.
- **Example:**
  ```bash
  curl -X {{METHOD}} "{{BASE_URL_PLACEHOLDER}}{{/path}}" {{-d '<json>' or headers}}
  ```

<!-- Repeat one block per endpoint. -->

### Screens / Views
<!-- Delete this section for a headless / API-only service. -->
| Screen | Route | Purpose | Requirement |
| --- | --- | --- | --- |
| {{screen name}} | `{{/ui/route}}` | {{what the user does here}} | {{PREFIX}}-NNN |

For each screen: {{what triggers it, what the user sees, what actions it exposes, and its owning requirement ID.}}

### State Flow
{{Describe the primary state transitions as a fenced text diagram — e.g. request lifecycle, session/auth states, or a resource's status machine (created → active → closed). Cite the IDs that govern each transition.}}
```text
{{state_A}} --{{event}}--> {{state_B}} --{{event}}--> {{state_C}}
```

### Authentication & Sessions
{{How a caller authenticates, how sessions/tokens are issued and expire, what an expired/invalid credential does. Cite IDs. This surface is Stop-and-Ask territory — see AGENTS.md before changing it.}}

### Troubleshooting
{{Each failure mode the service explicitly handles (4xx/5xx conditions) + the fix.}}

<!-- ==== SECOND LANGUAGE TRACK — keep ONLY if config bilingual.enabled == true; else delete from here down ==== -->
## {{SECONDARY_LANGUAGE_HEADER}}
{{Mirror every section above in lock-step: same endpoint table, same per-endpoint blocks in the same order, same screens, same state flow.}}
