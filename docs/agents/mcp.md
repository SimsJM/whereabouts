# Whereabouts — MCP server (release 1.1, design paused)

> v1.0 · 31 October 2026 · **Not in the MVP** (D-20). Captured here so the MVP's data model and service layer stay ready for it (NFR-14). Resume by writing the 10–15 real requests first.

## 1. Shape

- A **thin layer over the same service code** as the app (never touches the DB directly — import-linter contract).
- Transport: **Streamable HTTP**.
- Auth: **per-user API tokens**, scoped **read** or **read + write**; the agent acts as that user; token shown once, then hidden (Settings › AI ACCESS: e.g. "Claude · Read & write · acts as Jamie", "Home Assistant · Read only").
- Exposed **only on the homelab's AI-agent network segment** (exact network detail in private infra notes).
- Every agent change is logged with the **agent as actor**, so it appears in Changes/History and can be undone.

## 2. Candidate tools

`search_items` / `find_item`, `get_location_contents`, `add_item`, `move_item`, `adjust_quantity`, `get_history`, `undo_last_change` — plus, later, label requests (server-side PDFs make this possible).

## 3. Design principles

1. **Start from real requests people would say** ("where's the drill?", "what's in the loft?", "I've put the fairy lights back in the Christmas box").
2. **Tools match intentions, not tables.**
3. **Resolve fuzzy references server-side** (names, codes, paths) and return candidates when ambiguous.
4. **Short, model-readable outputs** with IDs and full paths; capped result counts.
5. Annotate with **`readOnlyHint` / `destructiveHint`**.
6. **Actionable errors**: "No box B-0043. Closest: B-0034 (Loft)".
7. **Log every agent change** with the agent as actor.
8. No hard deletes; undo available.

## 4. Why this matters (positioning)

HomeHoard's MCP blocks adding and deleting; community Homebox MCP servers expose raw create/delete calls. Safe agent writes (event log, attribution, one-step undo, scoped tokens, no hard deletes) are the **hardest differentiator to copy**. The pattern may be worth publishing on its own (O-18).

## 5. Next step

Product writes 10–15 real requests → Architect derives the tool list and permission model → `[DESIGN]` issue for Jamie's approval.
