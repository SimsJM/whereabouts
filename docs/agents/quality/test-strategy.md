# Whereabouts — Test strategy

> v1.0 · 31 October 2026 · Owner: QA agent. Applies to the app repo. The site pilot only needs `build` + `link-check` plus the acceptance checks in `../infrastructure/website-handover.md` §6.

## 1. Principles

1. **Tests first.** QA writes failing acceptance tests (features) or reproductions (bugs) before Developer starts. The chain order guarantees they never share the branch at the same time.
2. **Test before merge.** Everything below runs on every PR; `main` only holds code that passed.
3. **Deterministic.** Fixed clock adapter, seeded fixtures, no network, fakes for external services.
4. **Test the contract, not the implementation.** E2E tests use the `data-testid` contract (`../design/screen-inventory.md`), copy strings from `../product/requirements.md`, and requirement IDs.

## 2. Layers

| Layer | Tooling (proposed) | Scope | Where |
|---|---|---|---|
| Unit | pytest | Domain rules (tree ordering, codes, paths, parsing validation), pure functions | `tests/unit/` |
| Service/integration | pytest + temp SQLite | Use-cases end to end through services: events emitted, transactions, undo | `tests/integration/` |
| Contract | pytest | `import-linter`; `event-log-coverage` (every service write emits an event); no `DELETE` outside migrations | `tests/contracts/` |
| PDF | pytest + rasterise/decode | Page sizes, slot geometry ± 0.1 mm, nudge offsets, QR decodes to the right URL, fonts embedded | `tests/pdf/` |
| E2E | Playwright (Python or JS per ADR-0002) at **390 × 844** (+ one desktop smoke) | User journeys J1–J12 (`../product/user-journeys.md`) | `tests/e2e/` |
| Accessibility | axe-core in Playwright | No critical violations on every screen in both themes | `tests/e2e/a11y/` |

## 3. Environment for tests

- Container built from the PR (`tree-<hash>`), fresh SQLite, `SEED_FIXTURES=demo` (`seed-fixtures.yaml`), `TEST_LOGIN=on`, `APP_ENV=test`.
- **Whisper fake:** returns the transcript for a recorded audio fixture (the three transcripts in `seed-fixtures.yaml` → `voice_fakes`).
- **Parser fake:** returns the canned structured items for each transcript, including the duplicate (`Wall plugs (box)` → `i7`).
- **Camera/QR:** e2e drives the scanner by injecting a decoded code (test hook) and separately tests `/c/<code>` routing via HTTP.
- **Clock:** fixed at fixture load time; relative times ("2h ago") computed from it.

## 4. Must-have regression set for MVP

| Area | Tests (requirement IDs) |
|---|---|
| Tree rules | FR-LOC-02/03 inversion rejected; box-in-box allowed; cycle rejected; item on home rejected (FR-ITM-02) |
| Codes | FR-LOC-09 sequential, unique, never reused after archive; next code shown before create |
| Search | FR-SRCH-01…04 plural tolerance, paths, scoping to current home, code search, empty state copy |
| Voice | FR-VOI-02…06 review before save, quantity edit, remove, merge into existing, toast + return |
| Labels | FR-LBL-01…10 new box flow both formats, queue survives until Printed OK, duplicate queue message, nudges applied |
| QR | FR-QR-01/02 URL content, resolve box/place, unknown code suggestions, archived message |
| Import | FR-BLK-01…04 using `templates/garage-shelves.sample.csv`: 5 new, 1 merge, Shelf 3 + Car kit created |
| History/undo | FR-HIS-04 undo writes a new event; archived item → "That item was archived" |
| Home lists | FR-HOME-02…06 Changes shows other actors (incl. agent) only, Undo; Looked for order; Pinned toggle; Lent/Returned; empty states |
| Moving | FR-MOVE-01…10 full journey J7; finish with packed boxes confirmation; only one active move |
| Multi-home | FR-LOC-04 switching scopes rooms/search |
| Security | Test login refused when `APP_ENV=production`; members can't manage users; CSP has no third-party origins |

## 5. Integrity rules (enforced in CI)

- `qa-scope`: QA's commits touch only `tests/`.
- `test-integrity`: flags deleted QA tests, removed assertions, `skip`/`xfail` added, loosened comparisons. Developer may **add** tests.
- Naming: `test_<REQ_ID>_<behaviour>` (e.g. `test_FR_LBL_05_queue_kept_until_printed_ok`).

## 6. Fixture notes

- `seed-fixtures.yaml` mirrors the prototype exactly (2 homes, 6 rooms, 9 places, 12 boxes, 42 items, 2 loans, 3 pins, 4 recent views, 1 queued label, 5 events including one agent event).
- The sample CSV references box code `B-0060` which doesn't exist yet → import must create a box (name: the prototype calls it "Car kit"; the CSV has no box-name column — O-10 should add `box_name`).
- After loading, `code_counters` must be B → 63, P → 10 (so the next new box is `B-0063`; the prototype's next code also comes out as `B-0063`).

## 7. Exploratory / manual (Jamie, on previews)

Real phone over VPN: camera scan of a printed label; real Whisper round-trip; print a roll label and an A4 sheet at 100 %; alignment test; dark mode; installed PWA.
