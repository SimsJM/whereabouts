# Whereabouts — Roadmap and initial backlog

> v1.0 · 31 October 2026 · Owner: Product agent (maintains), Jamie (approves order).

## 1. Release plan

| Release | Contents | Notes |
|---|---|---|
| **0. Factory pilot** | The coming-soon **site** run through the factory (Developer + Product only, `merge: human`) | Proves the core/pack split before the app. See `../infrastructure/website-handover.md` and `../factory/packs/site.factory.yaml` |
| **1. MVP** | Everything marked **M** in `requirements.md` (incl. moving house, lent out, pinned) | Launch scenario: moving house |
| **1.1** | **MCP server** (read + safe write) and Settings › AI access | Design paused; resume per `../architecture/mcp.md` |
| **1.2** | **Photo-to-inventory** (one photo of an open box → suggested items → same review screen) | Needs a cloud vision model (no GPU). Competitor analysis says this is the biggest gap vs consumer apps |
| **Later** | Semantic search (embeddings); all-homes search; same item in many places; read-only role; Home Assistant integration; Homebox import polish; lend due dates; Skye mascot; hosted SaaS | Ordered by Product with Jamie |
| **Never** | Warranty/value/maintenance tracking; native apps; direct printer drivers | — |

## 2. Suggested MVP build order (epics)

Dependencies flow downward. Each epic becomes a chain of issues (Design → Test → Build) per `../factory/loop.md`.

| # | Epic | Requirements | Large feature? (needs Architect design first) |
|---|---|---|---|
| E0 | **Foundations**: repo skeleton, `AGENTS.md`, `docs/agents/`, CI required checks (stubs ok), container image, preview + prod pipeline, seed fixtures, test login | NFR-05, NFR-11, NFR-12 | Yes |
| E1 | **ADRs**: frontend stack (ADR-0002), auth (ADR-0003), PDF engine, config names | O-01, O-02, O-12 | Architect only |
| E2 | **Data model + service layer + event log** (locations, items, events, households, users) with `import-linter` contracts and `event-log-coverage` | FR-LOC-01…10, FR-ITM-01/02, FR-HIS-01 | Yes |
| E3 | **Auth, households, users, invite** | FR-USR-* | Yes (high-risk path) |
| E4 | **App shell + design system** (tokens, Jost self-hosted, rail, headers, sheets, toasts, theming, PWA manifest + service worker) | FR-NAV-01/07, FR-SET-01, NFR-07/08 | Yes |
| E5 | **Browse**: Rooms, Room, Place, Box, Item screens; quantity; move picker; archive | FR-NAV-03…06, FR-ITM-03…06, FR-LOC-04…08 | No |
| E6 | **Search** (FTS) + home switcher | FR-SRCH-01…06 | No |
| E7 | **History + undo** screens | FR-HIS-02…05 | No |
| E8 | **Labels**: codes, new-box flow, PDF generation (roll, sheet, test), queue, calibration, `/c/<code>` resolver | FR-LBL-*, FR-QR-01/02 | Yes |
| E9 | **Scanner** (in-app QR) | FR-QR-03/04 | No |
| E10 | **Voice**: Whisper client, voice search, add-by-voice with parsing + review + merge | FR-VOI-* | Yes (external services) |
| E11 | **Bulk import** (+ Homebox mapping) | FR-BLK-* | No |
| E12 | **Home lists**: Changes, Looked for, Pinned, Lent out + lending | FR-HOME-*, FR-LEND-* | No |
| E13 | **Moving house** | FR-MOVE-* | Yes |
| E14 | **Hardening**: accessibility audit, performance, backup/restore drill, release README + Docker Compose for self-hosters | NFR-* | No |

## 3. First issues for the factory (ready to create)

1. `[DESIGN] Draft docs/agents/architecture.md from the handover pack` — Architect.
2. `[DESIGN] ADR-0002 Frontend stack` — Architect; options and recommendation; Jamie decides.
3. `[DESIGN] ADR-0003 Authentication (passkeys vs OIDC) incl. test-only login` — Architect.
4. `[BUILD] Repo skeleton, CI stubs for all required checks, Dockerfile, pr.yml` — Developer (high-risk paths → Jamie merges).
5. `[TEST] Seed fixtures loader using quality/seed-fixtures.yaml` — QA.
6. `[BUILD] Footer version string` — the trivial dry-run feature used to prove the loop end to end.

## 4. Open product questions (Product owns, Jamie decides)

See `decision-log.md` §4: O-03 (same item in two places), O-04 (cross-home search), O-10 (CSV template), O-11 (first load-in workflow), O-19 (read-only role), O-20 (Skye mascot). Also to confirm: Pinned and Looked-for are **per user** (assumed).
