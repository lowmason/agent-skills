Spec: specs/duration.md

specs/duration.md:7: A duration is made of the parts `<n>h`, `<n>m` and `<n>s`, in that order, where `<n>` is one or more ASCII digits (`0` to `9`), each part is optional, and at least one part is present.
specs/duration.md:8: `parse_duration` returns the duration in seconds.
specs/duration.md:9: Any other text raises `ValueError`.
