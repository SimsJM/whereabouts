# 0001. Own backend: FastAPI + SQLite

- **Status:** Accepted · **Date:** 2026-10-02 · **Decided by:** Jamie

## Context
Homebox (AGPL-3.0) is the incumbent self-hosted backend and its v0.26 "entity" model now resembles our tree, but its API churn broke every integration and it has no event log or undo to build safe agent writes on. Jamie's background is Python; the homelab has no GPU and modest CPUs.

## Decision
Build our own backend in **Python (FastAPI) with SQLite** (WAL) on a ZFS dataset, packaged as one container image. Offer CSV import that accepts Homebox exports so switching is cheap.

## Consequences
We own data layer, import and label generation (more to build). The event log, attribution and undo are designed in from day one, and the MCP layer evolves with the data model. SQLite keeps ops trivial and snapshot-friendly; revisit only if concurrency demands it.
