# 0003. Authentication

- **Status:** Proposed — **Architect to complete** · **Decided by:** Jamie

## Context
Multiple users per household with roles admin/member (readonly later). Self-hosted, reached over VPN. QA automation and per-PR previews need a **test-only login** that can never be enabled in production. MCP (v1.1) adds per-user API tokens.

## Options
1. **Local accounts with passkeys** (WebAuthn) — no extra infrastructure; needs recovery flow.
2. **OIDC** (e.g. Authentik on the homelab) — central identity; another dependency for self-hosters.
3. Both, with passkeys as the default and OIDC optional.

## Decision
_To be written._ Must specify: session handling, CSRF, invite flow, recovery, how `TEST_LOGIN=on` works and how startup refuses it when `APP_ENV=production`.

Auth and permissions are **high-risk paths** (Jamie merges).
