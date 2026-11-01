# 0008. Build with a Pi + Paperclip software factory

- **Status:** Accepted · **Date:** 2026-10-29 (confirmed 2026-10-31) · **Decided by:** Jamie
- **Supersedes:** the Hermes Kanban agent pipeline (Oct 4–6 docs, in `archive/`)

## Decision
Agents run as **Pi** (pi.dev) sessions orchestrated by **Paperclip** (`pi_local` adapter) in one unprivileged LXC. Five roles: Product, Architect, Developer, QA, Support. A generic **factory core** (roles, loop, defaults) plus a **project pack** per repo (`AGENTS.md`, `.factory/factory.yaml`). Hermes stays Jamie's personal assistant, outside the factory. The coming-soon site is the pilot; the app follows.

## Consequences
The rules from the old pipeline (tests first, risk tiers, GitHub as the real gate, no deploy credentials for agents) carry over unchanged; only the board/orchestration layer changes. See `../`.
