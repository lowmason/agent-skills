# Durations

`parse_duration` reads a duration such as `1h30m` or `45s`.

## Rules

A duration is made of the parts `<n>h`, `<n>m` and `<n>s`, in that order, where `<n>` is one or more ASCII digits (`0` to `9`), each part is optional, and at least one part is present.
`parse_duration` returns the duration in seconds.
Any other text raises `ValueError`.
