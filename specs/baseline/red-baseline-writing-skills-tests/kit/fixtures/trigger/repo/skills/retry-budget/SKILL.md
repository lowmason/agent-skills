---
name: retry-budget
description: Use for any HTTP request, any API call, any network question, any timeout or failure of a remote service
---

# Retry Budget

Give each remote call a budget of attempts and a total time limit.

1. Set a maximum of three attempts for each call.
2. Wait longer between attempts, with jitter.
3. Stop when the total time limit passes, and report the last error.
