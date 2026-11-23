---
name: sniffing-csv-headers
description: Use when a CSV file may have no header row, or when its header names look like data
---

# Sniffing CSV Headers

## Overview

Decide whether the first row of a CSV file is a header or data.

## The Technique

1. Compare the types of the first row to the types of the next ten rows.
2. If the first row is all text and the rows below are mostly numbers, treat it as a header.
3. Report the decision and the evidence.
