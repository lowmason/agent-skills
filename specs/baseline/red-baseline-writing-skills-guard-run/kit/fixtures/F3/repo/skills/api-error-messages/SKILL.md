---
name: api-error-messages
description: Use when writing the message text of an API error response, such as a 400 for a bad field, a 404 for a missing resource, or a 409 for a conflict.
license: MIT
---

# API Error Messages

## Overview

An error message is read by a developer who is in the middle of something else. Write it so that they can act
on it without opening the docs.

## Writing the message

Say what went wrong. Name the field, the value and the rule it broke, in that order. Keep the message under
200 characters, and put any detail in the `details` array.

```json
{"error": "invalid_field", "message": "Field 'currency' has value 'usd'; it must be an upper-case ISO 4217 code."}
```

## Red flags

- A message that names an internal class or a stack frame.
- A message that is the same for every 400.
