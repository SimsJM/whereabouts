# 0005. Append-only event log, no hard deletes

- **Status:** Accepted · **Date:** 2026-10-02 · **Decided by:** Jamie

## Decision
Every write goes through the service layer and appends an event (actor = user or agent, before/after) in the same transaction. Events are never edited or deleted. Nothing is hard-deleted: archive or quantity 0. Undo is a compensating event.

## Consequences
Powers history, "where was it last?", one-step undo, per-person attribution, and safe agent writes (the core differentiator). Enforced by the `event-log-coverage` CI test and a DB trigger blocking `DELETE` on events. The event log is a **high-risk path**.
