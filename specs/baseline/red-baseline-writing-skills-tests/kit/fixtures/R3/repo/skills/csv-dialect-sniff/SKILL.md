---
name: csv-dialect-sniff
description: Use when a CSV file arrives with an unknown delimiter, quote character or line ending, before parsing it
---

# CSV Dialect Sniff

## Overview

Detect the dialect of a CSV file from a sample of its first rows, then parse with that dialect.

## The Technique

1. Read the first 64 KB of the file.
2. Count candidate delimiters (comma, semicolon, tab, pipe) in each row. Pick the one with a stable count.
3. Check the quote character and the line ending the same way.
4. Report the dialect before any parse.
