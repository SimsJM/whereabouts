# Whereabouts — CI/CD, risk tiers and merge rules

> v1.0 · 31 October 2026 · Carries over §5–§9 of the 6 Oct pipeline (v0.4, in `archive/`), adapted to the Pi + Paperclip factory: "card" → **issue**, Hermes board → **Paperclip**, Reviewer → **Architect review + Jamie's approval**. The GitHub-side rules are unchanged. Owner: Jamie (workflows and Compose files are high-risk paths).

## 1. Principles

1. **Jamie is the final authority.** Agents propose, build, review and test; Jamie decides what ships, except where §4 allows automatic deployment.
2. **Risk is decided by rules, not by agent judgement** — which files a change touches and which branch it comes from.
3. **Least privilege.** No agent holds deploy credentials. Each role's token holds only what it needs.
4. **Public input is untrusted.** Issue and comment text may contain instructions aimed at agents (see `../factory/security.md`).
5. **Everything is reversible.** No hard deletes, a snapshot before every production deploy, a kill switch on automation.
6. **The orchestrator coordinates; GitHub enforces.** Paperclip gates are conventions; the hard gates (merge, deploy) live in GitHub.

## 2. Working on a branch

- **Tests come first.** QA creates the branch and pushes failing acceptance tests; Developer then builds on the same branch. The issue chain means they never work on it at the same time. (With Paperclip isolated workspaces each issue gets its own worktree; the Developer issue must check out QA's branch — verify how Paperclip handles a branch shared across two issues, O-16.)
- Branch names: `feat/<issue>`, `fix/<issue>`, `refactor/<issue>`, `maint/<issue>`.
- **Separate folders:** QA commits only under `tests/`. The `qa-scope` check fails if QA's identity changes anything else. *(If all agents share one PAT/identity — O-06 — `qa-scope` must key off commit trailers such as `Agent-Role: qa` instead of the GitHub account.)*
- **Test integrity:** Developer may add tests but must not delete or weaken QA's tests. `test-integrity` flags deleted or loosened assertions in QA's tests.
- **Testable UI:** e2e tests target the `data-testid` contract in `../design/screen-inventory.md`.
- **Disposable environments:** every PR's e2e tests run against a fresh container with a new SQLite file.
- **Fakes for external services:** recorded audio + transcripts instead of Whisper; canned responses instead of the parser model.
- **No force-pushes.**

## 3. Required checks (branch protection on `main`)

| Check | What it does | Status at start |
|---|---|---|
| `lint` | e.g. ruff (+ frontend linter per ADR-0002) | Stub OK |
| `types` | e.g. mypy/pyright | Stub OK |
| `unit` | pytest | Stub OK |
| `e2e` | Playwright against the built image, seeded fixtures, fakes, test login | Stub OK |
| `qa-scope` | QA changes only `tests/` | Real from day 1 |
| `test-integrity` | No deleted/weakened QA assertions | Real from day 1 (simple diff heuristics first) |
| `import-linter` | Layer contracts (`../architecture/architecture.md` §3) | Real once packages exist |
| `event-log-coverage` | Every write path produces an event | Real once services exist |
| `risk-classify` | Labels `needs-jamie`, blocks auto-merge unless low-risk `fix/` | Real from day 1 |
| Review | **Jamie's approving review** (code-owner review required on high-risk paths). Architect posts a review comment against acceptance criteria + `architecture.md` | — |

Mark placeholder workflows clearly (`# STUB:` header and a job that echoes "stub").

## 4. Risk tiers and merging

**High-risk** if a PR touches any of: authentication or permissions; `migrations/`; the event log; `Dockerfile`, Compose files or `.github/`; dependency files; `CODEOWNERS`, `docs/agents/`, `.factory/` or the architecture contracts (`.importlinter`) — **or** the diff exceeds ~**200 lines** (tunable, O-13). Everything else (templates, CSS, copy, ordinary handlers) is **low-risk**.

| Change | Branch | Approval to start | Merge |
|---|---|---|---|
| Feature | `feat/` | Jamie approves the issue chain | Jamie |
| Refactor | `refactor/` | Jamie approves | Jamie |
| High-risk bug fix | `fix/` | None (confirmed bug) | Jamie |
| Low-risk bug fix | `fix/` | None (confirmed bug) | **Automatic** once all checks pass — **off for the first month** |
| Maintenance | `maint/` | None (scheduled) | Jamie |

Enforcement on GitHub:
- Branch protection on `main`: PRs only, no direct pushes, no force-pushes, required checks above, code-owner review.
- `CODEOWNERS` names Jamie on every high-risk path.
- `risk-classify` adds `needs-jamie` and blocks auto-merge unless the PR is from `fix/`, touches no high-risk path and is under the size threshold.
- Paperclip should not mark a Build issue done until the PR's required checks are green (equivalent of the old completion contract — verify how, O-16).

## 5. Pipeline

```
PR opened / updated
 ├─ pr.yml (GitHub-hosted)
 │    lint · types · unit · qa-scope · test-integrity · import-linter · event-log-coverage · risk-classify
 │    build image → push ghcr.io/<owner>/whereabouts:tree-<hash>
 │    e2e regression against that image (fresh SQLite, seeded fixtures, fakes)
 └─ preview.yml (preview runner, via workflow_run; same-repo branches only)
      deploy pr-<n>.<preview-domain> → comment the link on the PR

Merge (Jamie, or auto-merge for low-risk fixes)
 ├─ merge queue re-runs pr.yml on the exact commit that will land
 └─ deploy.yml (prod runner, on push to main)
      kill switch → snapshot → migration rehearsal → deploy → smoke test → release note
```

| Workflow | Trigger | Runner | Does |
|---|---|---|---|
| `pr.yml` | `pull_request`, `merge_group` | GitHub-hosted | All checks, image build + push, e2e |
| `preview.yml` | `workflow_run` (after `pr.yml` succeeds), `workflow_dispatch` | Self-hosted `preview` | Deploy/update the PR's preview stack; comment link |
| `preview-reaper.yml` | `schedule` (hourly) | Self-hosted `preview` | Tear down previews whose PR is closed or idle > 7 days; prune images nightly |
| `deploy.yml` | `push` to `main`, `workflow_dispatch` | Self-hosted `prod` | Promote to production; roll back on failure |

**Principles:** test before merge; **build once, promote the same image** (tag `tree-<hash>` so the merged commit resolves to the tested image); PR code reaches the homelab only by choice; **homelab workflows run from `main`'s definitions only** (`workflow_run`, `push`, `schedule`, `workflow_dispatch` — never `pull_request`).

### Previews
- Every PR from a branch inside the repo (where all agent work happens). Fork PRs only when Jamie runs `preview.yml` manually after reading the diff.
- `preview.yml` never checks out PR code; it pulls the already-built image and starts it with the compose template from `main` as project `whereabouts-pr-<n>`.
- Own SQLite volume, seeded fixtures, test login; no secrets, no external services.
- `concurrency: preview-pr-<n>` with `cancel-in-progress`.
- At most **5** concurrent previews; beyond that the least recently updated is torn down. 7-day idle timeout.
- Routing by **caddy-docker-proxy** labels and a wildcard DNS record; internal only, over the VPN.
- One PR comment with the link, updated in place.
- Teardown by hourly reconciliation (`docker compose -p whereabouts-pr-<n> down -v`), never a `pull_request: closed` job.

### Production deploy (`deploy.yml`, `production` environment, `main` only)
1. **Resolve the image** for the commit's tree hash. If missing (main moved after test), build and run full e2e first.
2. **Kill switch:** if repo variable `AUTO_DEPLOY` is `off`, stop; Jamie promotes manually with `workflow_dispatch` + tree hash.
3. **Snapshot** the production container and database (ZFS).
4. **Rehearse migrations** on a clone of that snapshot; stop if they fail.
5. **Deploy**, pinning the image by digest.
6. **Smoke test** (`scripts/smoke.sh`).
7. **On failure:** restore snapshot, roll back image, open a `deploy-failure` issue, alert Jamie.
8. **Post the release note.**

A `deploy-failure` issue becomes a follow-up chain linked to the original Build issue. `deploy.yml` can roll back to any earlier tree hash.

### Runners
| Runner | Lives on | Used by | Never |
|---|---|---|---|
| GitHub-hosted | GitHub | `pr.yml` | — |
| `preview` | Isolated preview host | `preview.yml`, `preview-reaper.yml` | Holds production credentials |
| `prod` | Production deploy host | `deploy.yml` | Runs PR or preview workflows |

Neither self-hosted runner is on the factory host.

### Files this adds to the repo
`.github/workflows/{pr,preview,preview-reaper,deploy}.yml`, `deploy/preview/compose.yml`, `deploy/prod/compose.yml`, `scripts/smoke.sh` — all high-risk (Jamie merges).

## 6. Open items

- O-15 merge queue availability on a user-owned repo (else "require branches to be up to date"; tree-hash tagging still matches images).
- O-14 preview TLS; preview limits (5 / 7 days) to tune; seed fixtures now in `../quality/seed-fixtures.yaml`.
- O-06 identities: per-role GitHub accounts vs a single PAT changes how `qa-scope` and reviews work.
