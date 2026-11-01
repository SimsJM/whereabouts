# 0009. Test before merge; build once, promote the same image

- **Status:** Accepted · **Date:** 2026-10-06 · **Decided by:** Jamie

## Decision
Regression runs on every PR on GitHub-hosted runners (required check), so `main` only holds tested code. Images are tagged by git tree hash and the tested image is promoted to production. Same-repo PRs also get an ephemeral homelab preview. Self-hosted runners never run `pull_request` workflows.

## Consequences
See `../infrastructure/ci-cd.md`. Requires a merge queue or "require up to date" (O-15).
