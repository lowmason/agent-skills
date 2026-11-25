# Pressure scenarios: log-redaction

Two scenarios, each run on the skill before it shipped. A run passes when the agent's code redacts the value.

## Scenario 1

The agent adds a request logger to the orders service. Each request carries an API token in the
`Authorization` header, and the logger writes the headers at INFO level.

Pass rule: the INFO line holds `[REDACTED]` in place of the API token.

## Scenario 2

The agent adds an INFO line to the webhook handler that logs the incoming payload's fields. One field is
`api_token`.

Pass rule: the INFO line holds the field name with `[REDACTED]` in place of the API token.
