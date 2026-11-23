---
name: http-retry-policy
description: Use when a call to an HTTP service fails or times out and you are deciding whether to send it again, or when writing client code that retries requests.
---

# HTTP Retry Policy

## Overview

A retry helps when a failure is brief and the request is safe to send twice. It hurts when the service
is down, because each retry adds load, and when the request changes state, because a second send can
create a second order or a second charge.

## Check the service first

Before any retry, check the service's health endpoint:

```bash
curl -sf https://status.example.invalid/health
```

A non-zero exit means the service is down. Fail fast and report it, because a retry cannot help.

## Which requests to retry

| Request | Response | Action |
|---|---|---|
| GET, HEAD, PUT or DELETE | 502, 503, 504 or a timeout | Retry up to 3 times, after 1 s, 2 s and 4 s |
| POST with an `Idempotency-Key` header | 502, 503, 504 or a timeout | Retry with the same key |
| POST with no idempotency key | any failure | Fail fast |
| any | 400, 401, 403, 404, 409 or 422 | Fail fast and fix the request |

## Retry-After

When a 429 or 503 response has a `Retry-After` header, wait that long before the next attempt, even when
it is longer than the backoff.
