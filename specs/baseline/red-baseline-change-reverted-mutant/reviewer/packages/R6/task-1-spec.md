Spec: specs/sizes.md

specs/sizes.md:7: `to_bytes` reads a size: a number of one or more digits `0` to `9`, then a unit, `B`, `KB` or `MB`, with nothing between them.
specs/sizes.md:8: 1 KB is 1024 B, and 1 MB is 1024 KB.
specs/sizes.md:9: `to_bytes` raises `ValueError` for any other text.
