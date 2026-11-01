# 0004. One location tree: Home › Room › Place › Box

- **Status:** Accepted · **Date:** 2026-10-09 · **Decided by:** Jamie

## Decision
- Single `locations` table with `kind` ∈ {home (1), room (2), place (3), box (4)}.
- A parent must have a **lower rank** than its child: levels can be skipped, never inverted. **Exception:** a box may sit in a box. Only homes have no parent. Multiple homes per household.
- Items point at one location that is a room or deeper.
- "Location" is internal only; the UI names the levels. "Place" chosen over "Spot" (too American) and "Unit".
- Codes `B-0001` (boxes) and `P-0001` (places), sequential per household, never reused.
- Same item in many places: deferred (O-03).

## Consequences
One recursive query gives paths and "everything in X"; moving a box moves its contents with one update; labels are one feature for places and boxes.
