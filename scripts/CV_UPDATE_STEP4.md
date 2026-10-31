# CV incremental update — step 4: the server pushes to GitHub after each publish

Status: implemented 2026-10-31. Companions: `CV_UPDATE_STEP2.md` (§12 decisions),
`CV_UPDATE_STEP3.md` (the admin tab that drives this engine).

## The problem

A publish (or rollback) commits its changes on the server's site checkout
(`/home/hurlab/apache-tomcat-9.0.37/webapps/hurlab`). Until step 4 that commit lived only on the
server: GitHub did not have it, a local clone could not see it, and `~/deploy.sh` (server copy
and repo copy `scripts/deploy.sh` are byte-identical) deliberately refuses to run while the
server holds commits GitHub lacks. Every publish therefore needed a manual "bring the server
commit into GitHub" step before the next deploy.

## Decision: use the existing HTTPS git credentials — no deploy key

The server's global git config already routes github.com HTTPS credentials through `gh`
(`credential.https://github.com.helper=!/usr/bin/gh auth git-credential`; `gh auth status`:
logged in, `repo` scope, live-verified 2026-10-31). The 2026-10-30 design draft proposed a
repo-scoped read-write deploy key; on 2026-10-31 the user chose the simpler path — the existing
credential is already there, so no new key, no GitHub-side change, no ssh config change, and the
remote stays HTTPS. Trade-off accepted by the user: the automation depends on that token staying
valid; if it is ever revoked, pushes stop (non-fatally — see below) until a new credential is
set up. **Server-side setup for step 4: none.**

## What changed

- `scripts/cv_publish.py`:
  - new `_git_push()` — `git push origin main` in the site checkout, `GIT_TERMINAL_PROMPT=0`,
    60 s timeout, capture_output. Returns True/False; never raises into the publish path.
  - `cmd_publish` and `cmd_rollback` call it once after a successful `_git_commit`. When the
    commit step was skipped (no repo — that is the unit-test path; or none of the written files
    are inside the repo) no push is attempted.
  - Push failure is NON-fatal and the exit code stays 0: the data files and `applied.jsonl` are
    already written and live on the site. The output says `PUSH FAILED (GitHub behind)` plus a
    WARNING line naming the manual retry (`git -C <site> push origin main`). Meanwhile
    `~/deploy.sh` keeps its guard: it stops while the server is ahead of GitHub, so nothing is
    silently stale.
- `scripts/deploy-from-local.sh` (new) — the local half of the same rule, closing the loop.
  Run it from any checkout instead of hand-running `ssh hurlab@… ~/deploy.sh`: it fetches
  origin/main and refuses while THIS checkout's branch is behind origin/main (commits not
  pulled locally — in practice the server's publish commit), then runs `~/deploy.sh` on the
  server. Flags pass through (`--dry-run`). Refusal names the fix
  (`git -C <repo> merge --ff-only origin/main`).

## Message contract (publish / rollback output)

| Situation | Trailing clause |
|---|---|
| committed + pushed | `, committed, pushed` |
| committed + push failed | `, committed, PUSH FAILED (GitHub behind)` + WARNING line |
| commit skipped (tests) | publish: `, git skipped` · rollback: `''` — unchanged from step 2 |

## Verification

- Unit: `tests/unit/test_cv_publish.py` class `PushHook` — push fires on publish and on
  rollback, is NOT attempted when the commit was skipped, a failed push keeps exit 0 with the
  WARNING text, and `_git_push()` handles ok / non-zero / timeout via a fake subprocess.
- Live: after deploy, `git push --dry-run origin main` on the server proves the credential path
  end to end without moving any ref; the first real publish (PI's drive of the CV Update tab)
  proves the hook itself.
