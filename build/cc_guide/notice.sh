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

DAY=86400             # seconds; notice.py measures a day the same way
LOCK_MINUTES=60       # R9.3: a lock older than an hour is broken
BUDGET=300            # seconds check --hook may run, since async hooks have no timeout
UNFINISHED_LIMIT=3    # R9.4: three unfinished runs in a row are an error

unset CDPATH
here=$(cd "$(dirname "$0")" && pwd -P)
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
    { printf '%s %s\n' "$today" "$digest" > "$cache/.notice-shown.$$.tmp" && mv -f "$cache/.notice-shown.$$.tmp" "$cache/notice-shown"; } 2>/dev/null || rm -f "$cache/.notice-shown.$$.tmp" 2>/dev/null
    return 0
}

# The last good check's epoch second, read from the line notice.py writes; empty when none.
ok_epoch() {
    sed -n 's/^ *"ok_epoch": \([0-9][0-9]*\),\{0,1\}$/\1/p' "$cache/last-check.json" 2>/dev/null
}

# The age of the last good check, as notice.py words it.
age_words() {
    ok=$(ok_epoch)
    if [ -n "$ok" ]; then
        printf 'last good check %s d ago' $(( ($(date +%s) - ok) / DAY ))
    else
        printf 'no good check yet'
    fi
}

# True while the last good check is under a day old.
fresh() {
    ok=$(ok_epoch)
    [ -n "$ok" ] && [ $(( $(date +%s) - ok )) -lt "$DAY" ]
}

# Write one of refresh's two error notices: notice.json, then its digest, each renamed into
# place. $1 says what failed and $2 what to do. Neither holds a quote or a backslash, so the
# JSON needs no escaping beyond the two \u escapes written here.
fail_notice() {
    message="cc-guide \\u00b7 $1 \\u00b7 $(age_words) \\u2192 $2"
    tmp="$cache/.notice.$$.tmp"
    { printf '{"systemMessage": "%s"}\n' "$message" > "$tmp" && mv -f "$tmp" "$cache/notice.json"; } 2>/dev/null \
        || return 0
    sum=$(cksum < "$cache/notice.json")
    { printf '%s\n' "${sum%% *}" > "$tmp" && mv -f "$tmp" "$cache/notice.digest"; } 2>/dev/null
    return 0
}

# Take the lock, breaking one older than LOCK_MINUTES. find -mmin is BSD and GNU, not POSIX.
take_lock() {
    mkdir "$lock" 2>/dev/null && return 0
    [ -n "$(find "$lock" -prune -mmin +"$LOCK_MINUTES" 2>/dev/null)" ] || return 1
    rm -rf "$lock" && mkdir "$lock" 2>/dev/null
}

# Print the uv to run: the one on PATH, else the first in the fallback directories.
find_uv() {
    command -v uv 2>/dev/null && return 0
    set -f
    old_ifs=$IFS
    IFS=:
    for dir in ${CC_GUIDE_UV_FALLBACK-$HOME/.local/bin:/opt/homebrew/bin}; do
        if [ -x "$dir/uv" ]; then
            IFS=$old_ifs
            set +f
            printf '%s\n' "$dir/uv"
            return 0
        fi
    done
    IFS=$old_ifs
    set +f
    return 1
}

# Count the run unfinished, then run check --hook through uv under the budget and see whether
# it finished: a finished run leaves its ID in last-check.json, which notice.py writes last of
# all. The run is counted before it starts, since a refresh ended mid-check never gets past it.
check_now() {
    for name in $(env | sed -n 's/^\(GIT_[A-Za-z0-9_]*\)=.*/\1/p'); do
        unset "$name"   # a caller's GIT_DIR or GIT_INDEX_FILE would redirect check's git reads
    done
    budget=${CC_GUIDE_BUDGET:-$BUDGET}
    case $budget in ''|*[!0-9]*) budget=$BUDGET ;; esac
    before=$(cat "$cache/unfinished" 2>/dev/null)
    case $before in ''|*[!0-9]*) before=0 ;; esac
    if [ "$before" -ge "$UNFINISHED_LIMIT" ]; then
        fail_notice "the drift check did not finish $before times in a row" 'run build/cc_guide/cli.py check'
    fi
    count=$((before + 1))
    { printf '%s\n' "$count" > "$cache/.unfinished.$$.tmp" && mv -f "$cache/.unfinished.$$.tmp" "$cache/unfinished"; } 2>/dev/null || rm -f "$cache/.unfinished.$$.tmp" 2>/dev/null
    id="$$.$(date +%s)"
    "$1" run --python 3.13 python "$here/cli.py" check --hook --run "$id" </dev/null >/dev/null 2>&1 &
    pid=$!
    trap 'kill "$pid" 2>/dev/null; exit 0' HUP INT TERM   # a signalled refresh takes its check with it
    waited=0
    while kill -0 "$pid" 2>/dev/null; do
        if [ "$waited" -ge "$budget" ]; then
            kill "$pid" 2>/dev/null   # uv passes SIGTERM on to the check
            break
        fi
        sleep 1
        waited=$((waited + 1))
    done
    wait "$pid" 2>/dev/null
    if grep -qF "\"run\": \"$id\"" "$cache/last-check.json" 2>/dev/null; then
        rm -f "$cache/unfinished" 2>/dev/null
        return 0
    fi
    if [ "$count" -ge "$UNFINISHED_LIMIT" ]; then
        fail_notice "the drift check did not finish $count times in a row" 'run build/cc_guide/cli.py check'
    fi
    return 0
}

# While a good check under a day old is on record no refresh runs a check, so a stored count of
# unfinished runs is stale: each return on a fresh check removes it.
refresh() {
    mkdir -p "$cache" 2>/dev/null || return 0
    if fresh; then
        rm -f "$cache/unfinished" 2>/dev/null
        return 0
    fi
    lock="$cache/lock"
    take_lock || return 0
    trap 'rm -rf "$lock"' EXIT
    trap 'exit 0' HUP INT TERM
    if fresh; then   # another session may have finished a check while this one waited
        rm -f "$cache/unfinished" 2>/dev/null
        return 0
    fi
    if ! uv=$(find_uv); then
        fail_notice 'the drift check cannot run: no uv on PATH, in ~/.local/bin or in /opt/homebrew/bin' 'install uv'
        return 0
    fi
    check_now "$uv"
}

case "${1:-}" in
    show) show ;;
    refresh) refresh ;;
    *) echo 'usage: notice.sh show | refresh' >&2 ;;
esac
exit 0
