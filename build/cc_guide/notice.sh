#!/bin/sh
# notice.sh: the drift check's session-start pair (specs/claude-code-drift-automation-spec.md, R9).
#   notice.sh show     synchronous: print the notice check --hook left, once a day per notice (R9.2)
#   notice.sh refresh  async: run cli.py check --hook once the last good check is a day old (R9.3)
# Both exit 0 and print nothing but show's notice. .claude/settings.json wires the pair on
# SessionStart's startup matcher. JSON takes no comments, so this file carries the citation
# for the whole settings file, its model keys included: read .claude/settings.json with this
# file before restamping it (R4.2). notice.py's docstring lists the cache files the two
# languages share, and the order they are written and read in.
# Test seams: CC_GUIDE_UV_FALLBACK, colon-separated directories searched for uv after PATH,
# and CC_GUIDE_BUDGET, the seconds the check may run.
# cc-guide: hooks.events hooks.exit-codes hooks.configuration hooks.patterns hooks.pitfalls lean.model-routing rules.settings @2.1.302

cache="${HOME:-}/.cache/agent-skills/cc-guide"

# Print the notice unless this notice was already shown today. The digest is read before the
# notice, the reverse of the order they are written in, so a notice replaced between the two
# reads is shown once more and never skipped.
show() {
    digest=$(cat "$cache/notice.digest" 2>/dev/null)
    text=$(cat "$cache/notice.json" 2>/dev/null)
    [ -n "$text" ] || return 0
    today=$(date +%Y-%m-%d)
    [ "$(cat "$cache/notice-shown" 2>/dev/null)" = "$today $digest" ] && return 0
    printf '%s\n' "$text"
    { printf '%s %s\n' "$today" "$digest" > "$cache/notice-shown"; } 2>/dev/null
    return 0
}

case "${1:-}" in
    show) show ;;
    *) echo 'usage: notice.sh show | refresh' >&2 ;;
esac
exit 0
