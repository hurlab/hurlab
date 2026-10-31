#!/usr/bin/env bash
# deploy-from-local.sh - the local half of deploying the Hur Lab website (step 4).
#
# A publish on the server now commits AND pushes to GitHub, so a local checkout that has not
# pulled would be blind to the server's commits. This wrapper fetches origin/main and refuses
# while THIS checkout's branch is behind, then runs ~/deploy.sh on the server (no sudo; identical
# copy in the repo: scripts/deploy.sh).
#
# Usage, from any checkout of the repo:
#   scripts/deploy-from-local.sh              # normal deploy
#   scripts/deploy-from-local.sh --dry-run    # server-side preview, changes nothing
#
# Requires ssh access as hurlab@100.94.67.89 (Tailscale; the public hostname :22 times out off
# campus). The server side does the real work: fetch, ff-only, admin restart, health checks.

set -euo pipefail

REMOTE=hurlab@100.94.67.89

repo=$(git rev-parse --show-toplevel) || { echo "REFUSE: run from inside a checkout of the repo" >&2; exit 1; }
branch=$(git branch --show-current)
[ -n "$branch" ] || { echo "REFUSE: detached HEAD ($repo); deploy from a named branch" >&2; exit 1; }

echo "-- fetching origin/main"
git fetch --quiet origin +refs/heads/main:refs/remotes/origin/main

behind=$(git rev-list --count "HEAD..origin/main")
ahead=$(git rev-list --count "origin/main..HEAD")
echo "   branch ${branch} at $(git rev-parse --short HEAD); origin/main has ${behind} commit(s) not pulled here; this branch has ${ahead} unpushed commit(s)"

if [ "$behind" -gt 0 ]; then
    git log --oneline "HEAD..origin/main"
    echo "REFUSE: origin/main has commits not pulled into this checkout (above)." >&2
    echo "        Bring this checkout up to date first, then run again:" >&2
    echo "          git -C $repo merge --ff-only origin/main" >&2
    exit 1
fi

echo "-- running ~/deploy.sh on the server"
# '~' quoted: the REMOTE shell must expand it (to /home/hurlab); unquoted, the local shell
# would expand it to the invoking user's home and the server would get a nonexistent path.
exec ssh -o BatchMode=yes -o ConnectTimeout=10 "$REMOTE" '~/deploy.sh' "$@"
