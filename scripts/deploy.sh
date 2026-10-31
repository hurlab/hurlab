#!/usr/bin/env bash
# deploy.sh - update the Hur Lab website on this server from GitHub (origin/main).
#
# Run on the server as hurlab, no sudo needed:   ~/deploy.sh   (or --dry-run: change nothing)
#
# What it does:
#   1. fetch origin/main; stop if the server has commits GitHub does not have, or if an incoming
#      commit touches a file that is edited locally on the server (e.g. data/team.json)
#   2. fast-forward the site checkout (git merge --ff-only; local live edits are kept).
#      Tomcat serves the files straight from this checkout and reloads web.xml by itself.
#   3. restart the admin panel if scripts/ changed (systemd user service)
#   4. health checks against the local ports: every page and data file answers 200, the served
#      JSON is identical to the file on disk, and scripts/ + WEB-INF/ stay private (403)
# Each run is logged to ~/deploy-logs/.

set -euo pipefail

SITE=${HURLAB_SITE:-/home/hurlab/apache-tomcat-9.0.37/webapps/hurlab}
BRANCH=main
SITE_URL=http://127.0.0.1:8081/hurlab/
ADMIN_URL=http://127.0.0.1:8180/
ADMIN_UNIT=hurlab-admin.service
LOG_DIR=$HOME/deploy-logs

say()  { printf '%s\n' "$*"; }
UNDO=  # set once the checkout has moved, so every later STOP says how to go back
fail() {
    printf 'STOP: %s\n' "$*" >&2
    [ -z "$UNDO" ] || printf '      to undo the code update: git -C %s reset --keep %s\n' "$SITE" "$UNDO" >&2
    exit 1
}

http_code() { curl -s -o /dev/null -m 10 -w '%{http_code}' "$1" || true; }

wait_for_200() {  # url, seconds
    local i
    for ((i = 0; i < $2; i += 2)); do
        [ "$(http_code "$1")" = 200 ] && return 0
        sleep 2
    done
    return 1
}

health_check() {
    local bad=0 n=0 f code tmp
    tmp=$(mktemp)
    for f in $(git -C "$SITE" ls-files -- ':(glob)*.html' ':(glob)data/*.json'); do  # top level only
        n=$((n + 1))
        code=$(curl -s -o "$tmp" -m 10 -w '%{http_code}' "$SITE_URL$f" || true)
        if [ "$code" != 200 ]; then
            say "  FAIL $f -> HTTP $code"; bad=1
        elif [[ $f == *.json ]] && ! cmp -s "$tmp" "$SITE/$f"; then
            say "  FAIL $f -> served copy differs from the file on disk"; bad=1
        fi
    done
    rm -f "$tmp"
    say "   checked $n pages and data files"
    [ "$n" -gt 0 ] || { say "  FAIL no pages found to check"; bad=1; }
    for f in scripts/cv_diff.py WEB-INF/web.xml; do
        code=$(http_code "$SITE_URL$f")
        [ "$code" = 403 ] || { say "  FAIL $f should be private (403) but is HTTP $code"; bad=1; }
    done
    [ "$(http_code "$ADMIN_URL")" = 200 ] || { say "  FAIL admin panel $ADMIN_URL not answering"; bad=1; }
    return $bad
}

main() {
    local dry=0
    for a in "$@"; do
        case $a in
            --dry-run) dry=1 ;;
            -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
            *) fail "unknown option $a (see --help)" ;;
        esac
    done

    [ "$(id -u)" -ne 0 ] || fail "run as hurlab without sudo: ~/deploy.sh"
    command -v git >/dev/null && command -v curl >/dev/null || fail "git and curl are required"
    cd "$SITE" || fail "site checkout $SITE not found"
    [ "$(git branch --show-current)" = "$BRANCH" ] || fail "site checkout is not on $BRANCH"

    mkdir -p "$LOG_DIR"
    local log="$LOG_DIR/deploy-$(date +%Y%m%d-%H%M%S).log"
    exec > >(tee -a "$log") 2>&1
    say "== Hur Lab deploy $(date '+%Y-%m-%d %H:%M:%S %Z')  (log: $log)"

    say "-- 1. fetching origin/$BRANCH"
    GIT_TERMINAL_PROMPT=0 timeout 60 git fetch --quiet origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH" || fail "git fetch failed (network or GitHub)"
    local old behind ahead counts
    old=$(git rev-parse --short HEAD)
    counts=$(git rev-list --left-right --count "origin/$BRANCH...HEAD") || fail "could not compare with origin/$BRANCH"
    read -r behind ahead <<<"$counts"
    say "   server at $old; GitHub has $behind new commit(s); server has $ahead commit(s) GitHub lacks"

    if [ "$ahead" -gt 0 ]; then
        git log --oneline "origin/$BRANCH..HEAD"
        fail "the server has commits that are not on GitHub (above; usually admin-panel saves).
      Bring them into GitHub first (pull them locally and push), then run this again."
    fi

    local incoming local_edits clash restart_admin=0
    if [ "$behind" -gt 0 ]; then
        git log --oneline "HEAD..origin/$BRANCH"
        incoming=$(git diff --no-renames --name-only HEAD "origin/$BRANCH")
        local_edits=$(git status --porcelain --untracked-files=all | cut -c4-)
        # here-strings, not pipes: grep -q exiting early would trip pipefail
        clash=$(grep -xF -f <(printf '%s\n' "$incoming") <<<"$local_edits" || true)
        [ -z "$clash" ] || fail "these files are edited on the server AND changed on GitHub:
$clash
      Resolve them by hand (commit the server copy and bring it into GitHub), then run again."
        grep -q '^scripts/' <<<"$incoming" && restart_admin=1
    else
        say "   already up to date"
    fi
    say "   admin restart: $([ $restart_admin = 1 ] && echo yes || echo no)"

    if [ $dry = 1 ]; then
        say "-- dry run: nothing changed; running health checks on the current site"
        health_check && say "== OK (dry run)" || fail "health check failed (see FAIL lines)"
        return 0
    fi

    if [ "$behind" -gt 0 ]; then
        say "-- 2. updating the site ($old -> $(git rev-parse --short "origin/$BRANCH"))"
        git merge --ff-only --quiet "origin/$BRANCH" || fail "fast-forward failed; site left at $old"
        UNDO=$old
    fi

    if [ $restart_admin = 1 ]; then
        say "-- 3. restarting the admin panel"
        systemctl --user restart "$ADMIN_UNIT" || fail "could not restart $ADMIN_UNIT"
        wait_for_200 "$ADMIN_URL" 30 || fail "admin panel did not come back within 30 s"
    fi

    say "-- 4. health checks"
    [ "$behind" -eq 0 ] || sleep 6   # Tomcat caches static files for up to 5 s
    if health_check; then
        say "== OK: site at $(git rev-parse --short HEAD) (was $old)"
    else
        fail "health check failed (see FAIL lines)"
    fi
}

main "$@"
exit $?
