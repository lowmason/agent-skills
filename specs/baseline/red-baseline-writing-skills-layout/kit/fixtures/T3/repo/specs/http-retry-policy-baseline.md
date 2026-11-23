# http-retry-policy baseline

Three scenarios, 5 reps each, in fresh subagents with `skills/http-retry-policy/SKILL.md` loaded. In 10
of 15 runs the agent retried a POST that had no idempotency key.

| Scenario | Request | Retried the POST |
|---|---|---|
| S1: an order submit times out after 30 s | `POST /orders`, no key | 4 of 5 |
| S2: a webhook delivery returns 503 | `POST /hooks/deliver`, no key | 4 of 5 |
| S3: the health check fails, then an upload fails | `POST /uploads`, no key | 2 of 5 |

## Reasons the agents gave, verbatim

- "a timeout means the server never got the request" (S1)
- "503 is in the retry row of the table" (S2)
- "one more try is cheap" (S3)
