# Settings key check

`checkconf.py` checks a service's settings file before the service starts. The file holds one `key = value` pair on each line.

## Rules

`main` prints `unknown key: <key>` for each key that is not `name`, `port` or `debug`.
It returns 1 when the file has an unknown key, and 0 otherwise.
