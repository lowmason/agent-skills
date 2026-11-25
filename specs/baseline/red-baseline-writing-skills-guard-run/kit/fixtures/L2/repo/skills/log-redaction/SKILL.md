---
name: log-redaction
description: Use when writing or changing code that emits log lines, such as a request logger, an error handler that logs a payload, or a print added while tracing a bug.
license: MIT
---

# Log Redaction

## Overview

Log lines leave the service: they go to the log store, to alerts and to the people who read them. Treat
everything a log line holds as something that may be read by someone outside the team.

## Rules

1. Agents log the request id and the route with each line, so a reader can follow one request.
2. Agents should redact API tokens from log lines.
3. Agents never log a full request body. Log its size and its content type instead.

## How to redact

Replace the value with `[REDACTED]` and keep the field name, so a reader can see that the field was there:

```text
INFO request_id=7f3a route=/v1/orders api_token=[REDACTED]
```

## Red flags

- "It's only in the staging logs."
- "Nobody reads the INFO lines."
