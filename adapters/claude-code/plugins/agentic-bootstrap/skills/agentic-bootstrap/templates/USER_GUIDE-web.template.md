<!--
TEMPLATE: docs/USER_GUIDE.md for project.type == "web-service". Observable surface = endpoints/routes,
screens/views, and state flows. Filled from config.json (id.prefix, bilingual.*) and Phase-A answers
(the HTTP surface mined from the router / route definitions, and the UI screens if any).
Every endpoint/screen/state CITES its owning {{PREFIX}}-XXX from REQUIREMENTS. The endpoint and route
tables must match the source router 1:1.
BILINGUAL: keep the second track ONLY IF config bilingual.enabled == true; else delete it.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
-->

# {{COMPONENT}} — User Guide (Web Service)

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
| `GET` | `{{/path}}` | {{what it returns}} | {{none/token/session}} | {{PREFIX}}-0NN |
| `POST` | `{{/path}}` | {{what it does}} | {{...}} | {{PREFIX}}-0NN |

#### `{{METHOD}} {{/path}}`  ({{PREFIX}}-0NN)
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
| {{screen name}} | `{{/ui/route}}` | {{what the user does here}} | {{PREFIX}}-0NN |

For each screen: {{what triggers it, what the user sees, what actions it exposes, owning {{PREFIX}}-XXX.}}

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
