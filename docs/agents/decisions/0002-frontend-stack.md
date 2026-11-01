# 0002. Frontend stack

- **Status:** Accepted · **Date:** 2026-11-01 · **Decided by:** Jamie (O-01), approving the Architect's design note for this ADR
- **Completes:** the "Decision: to be written" section of the `0002-frontend-stack` handover note, which this ADR replaces
- **Settled inputs:** D-05 (FastAPI + SQLite), D-06 (PWA), D-07 (Jamie must be able to contribute), D-09/D-10 (own Whisper; LLM for parsing only), D-16/D-17 (server-side PDFs; QR encodes `/c/<code>`), D-18 (Pivi Pro look, Jost), D-24 (open models build most of it), NFR-04 (no third parties at runtime, strict CSP), NFR-07/08/09/11.

> Identifier conventions below: `D-xx` / `O-xx` cite the decision log (`docs/agents/decision-log.md`), `Sxx` the screen inventory, `FR-xx` / `NFR-xx` the requirements, and bare `§` the handover pack (architecture, test strategy). Where anything in the pack disagrees with the decision log, the log wins.

## Context

- PWA, mobile-first (390 × 844), camera (QR) and mic, works over VPN. Design system tokens live in the pack's `tokens.css`.
- Jamie (Python background) must be able to contribute to it over time (D-07).
- Agents (open models on Ollama Cloud) build most of it: favour conventional, well-documented patterns (D-24).
- E2E tests target `data-testid` attributes defined before the UI exists (NFR-11, test-strategy §1).
- No third-party runtime calls; strict CSP (NFR-04).

### The three hard flows any stack must pass

**Voice review screen (S09, FR-VOI-02…06).** Mic capture with a *live transcript while listening*, then a review list: per-row quantity steppers (min 1), remove, duplicate banner with Merge (merge adds quantity to the existing item), "Record again", "Add N items". Nothing is saved before confirm.

**QR scanner (S10, FR-QR-03…05).** Dark scanner screen, camera view, decode loop, FOUND card, then open the box/place; also scan-to-file and scan-to-unpack entry points. E2E drives it by *injecting a decoded code* (test-strategy §3).

**Start a move (S18, FR-MOVE-01).** Three-step wizard: from-home + moving day chips; new-home name + room chips (defaults given); then every top-level labelled box, ticked by default, auto-mapped to a destination room, **tap to cycle** the destination, live summary, one confirm that must land in a single transaction (architecture §4.3).

## Options evaluated

### Option 1 — Jinja + HTMX + Alpine.js (October sketch)

- Voice: mic capture is custom JavaScript in *every* option (the browser speech API is banned by D-09, so MediaRecorder is the only path); live transcript needs SSE either way. Review edits fit HTMX round trips fine on a LAN/VPN.
- Scanner: needs the same camera island regardless of what surrounds it.
- Start a move: natural — chips are styled radios that work without JS; steps are server-rendered forms.
- Best D-07 story (templates + Python), tiny bundle. But standard Alpine evaluates expressions and so needs `script-src 'unsafe-eval'`, which breaks NFR-04's strict CSP; its CSP build moves component logic into JS files — at which point it is just a third idiom next to HTMX and the islands, with no flow only it can unlock.

### Option 2 — SPA (SvelteKit/React) over a FastAPI JSON API

- Voice/scanner: the identical MediaRecorder and camera code; no advantage where the hard part actually is.
- Start a move: wizard state is comfortable client-side, but `start_move(from, day, name, rooms[], boxes{id: room})` plus search, tree navigation, events, undo, import preview, label queue… become a designed, versioned, tested **second contract** parallel to the service layer, which agents (smaller contexts, D-24) must keep in sync and Jamie cannot read.
- Weakest D-07 story: Node toolchain, component state, two ecosystems.
- Bundle 100–200 KB+ gz (React) and a build pipeline in dev, CI and the container; CSP needs hash-chunking to stay strict.

### Option 3 — Hybrid: server-rendered pages with small islands for scanner/voice

- Everything except the two device flows is Jinja + HTMX; the two device flows are self-contained vanilla ES modules. Same D-07 story as option 1, with the unavoidable JS *named and fenced* instead of smeared across every screen.
- Voice: the island owns capture, chunked upload and SSE transcript display; the review list is server-rendered and edited with HTMX; merge/min-qty/empty-state logic lives once, in the service layer, testable with plain pytest — the browser shows exactly what the server validated.
- Scanner: the island only decodes and then navigates to `/c/<code>` — the very URL the physical label encodes (D-17). No API at all.
- Start a move: three server-rendered steps carrying their state in the form itself; each interaction posts and swaps a fragment; one confirm POST. Refresh- and back-safe by construction.

| Test | Opt 1 | Opt 2 | Opt 3 |
|---|---|---|---|
| Mic/camera JS is bespoke in every option | same | same | same, but fenced in 2 modules |
| Review/merge logic lives once, server-side | mostly | no (client store) | yes |
| Second API contract to design/version/test | no | yes | no |
| Jamie can contribute (D-07) | best | worst | best |
| Strict CSP with zero relaxations | Alpine needs CSP build | needs chunk-hashing | yes |
| Test-first: real URLs + data-testid before UI exists | yes | after router boot | yes |
| Toolchains | Python | Python + Node | Python |
| PWA (app-shell-only caching, settled) | fits | most natural | fits |

## Decision

**Option 3.** Server-rendered **Jinja2 + HTMX 2** pages with **two vanilla ES-module islands** (voice capture, QR scanner), **no Alpine, no SPA, no Node, no client build step**.

Reasons, in order of weight:

1. **The device JS is identical in all three options**, so the only real question is where everything *else* lives. Option 3 keeps it in Python + Jinja — the one language the household can own over time (D-07).
2. **One service layer, no parallel API contract** (architecture rule 1). Web handlers call services directly; MCP v1.1 reuses the same services. Less surface for open models to break, less for Jamie to review.
3. **Test-first** (NFR-11, test-strategy §1): every screen is a URL with stable `data-testid`s, so QA's Playwright tests can exist before the UI and need no client router to boot; most behaviour is testable without a browser at all.
4. **Strictest CSP with no workarounds** (NFR-04): `script-src 'self'`, nothing inline, no eval. Alpine is dropped deliberately: HTMX + native elements (`<dialog>` sheets, radio chips, CSS animations) cover all 21 screens; Alpine's default build would force `unsafe-eval` and its CSP build is just more JS. If a screen ever proves to need local reactive state, add a small vanilla helper first; revisit Alpine only with evidence.
5. **Fewest moving parts** for CI and the container: no Node, no lockfile (`package.json` never exists; CODEOWNERS keeps guarding it), GitHub-hosted runners install pip + Playwright and run one uvicorn for e2e.

We knowingly give up: offline data editing (not wanted — "data stays live" is settled), client-side optimistic UI (writes are real events anyway, FR-ITM-04), and wizard interactions that re-render a fragment instead of mutating a client store (fine at LAN/VPN latency; revisit with evidence against NFR-09).

## The decision, in detail

### Routing

- **Every screen is a real URL** served by FastAPI/Jinja, following screen-inventory's route column: `/` · `/search` · `/rooms` · `/r/{id}` · `/c/{code}` (box **or** place by code, case-insensitive) · `/i/{id}` · `/voice?dest=` · `/scan` · `/new-box` · `/c/{code}/label` · `/labels/queue` · `/import` · `/history` · `/account` · `/move` · `/move/new` · `/move/pack` · `/move/unpack/{code}` · `/picker` (overlay route) · `/offline`. PDFs are routes too: `/c/{code}/label.pdf`, `/labels/queue.pdf`, `/labels/alignment-test.pdf` (server-side, FR-LBL-09).
- **Screen-to-screen navigation is ordinary full-page GETs.** Deep links work (a printed QR opens `/c/B-0042` directly), the browser back stack behaves (FR-NAV-07), and rail tabs reset it for free.
- **HTMX is for in-page fragment updates only**: search-as-you-type (debounced), home tab lists, quantity steppers, wizard steps, review edits, sheets, toasts. No `hx-boost`, no `hx-push-url` — the address bar always matches a fully renderable screen. Fragment endpoints are the same routes answering a `?partial=` convention (pinned in the build ticket). Post-then-redirect for actions that change screens (e.g. import → room), so refresh/back never re-POST.
- `/c/{code}` keeps its special behaviour: auth → resolve → 302 to Box or Place; unknown → closest matches; archived → "archived" page (architecture §4.2). The scanner navigates to the same URL, so there is exactly one code-resolution path.

### State

- **Server**: an authed session cookie (mechanism = ADR-0003, O-02) holding the current home. Every read renders from the service layer per request.
- **Client**: no app store, no global JS state. Multi-step flows (voice review, start a move, import preview) **carry their state in the form itself** — hidden inputs plus visible controls — and every edit posts the form to its fragment endpoint, which revalidates and re-renders (a server echo). Nothing persists before the confirm POST reaches a service (FR-VOI-04, FR-BLK-03, FR-MOVE-01). No draft rows, no draft cleanup, no tension with "no hard deletes".
- **Islands** hold only ephemeral device state (recording session, camera stream, decode loop) and hand over to server-rendered screens at their boundaries. `app.js` is a few dozen lines of vanilla helpers (toast timers, the step-3 destination cycling, the scanner test hook) — no framework.

### tokens.css

- Vendored **verbatim** from the design pack into `src/whereabouts/web/static/css/tokens.css` — plain CSS custom properties; no preprocessor, no build, no CSS-in-JS.
- Pages load plain `<link>`s in order: `tokens.css` → `base.css` → `components.css`, cache-busted with `?v=<tree-hash>` rendered by the server.
- All styling via classes consuming `var(--…)`; **no inline `style=` attributes** (strict CSP; dynamic visuals use state classes — e.g. move progress is one `<div class="seg">` per box, done/todo).
- Themes (FR-SET-01): tokens define light + dark on `:root` / `[data-theme]`; System follows `prefers-color-scheme`, Light/Dark set `data-theme` from the account preference. Jost is self-hosted as woff2 with `@font-face` in `base.css` (`font-src 'self'`) — the demo's Google Fonts link is already superseded (decision-log §3).

### PWA and the service worker

- `manifest.webmanifest` at `/manifest.webmanifest`: name, icons (192/512 + maskable), `display: standalone`, `start_url: /`, theme colours from tokens. Installable per D-06.
- `/sw.js` is **served by the app**, rendered with the current tree hash as its cache version, so every deploy re-precache atomically. Hand-written, ~40 lines, no Workbox, no Node: precache static assets at install; **cache-first for versioned `/static/*`; network-only for HTML, data and SSE** ("app shell cache only; data stays live" — architecture §2); navigation fallback to the cached `/offline` page ("Offline / server unreachable" screen, calm message + retry).
- Registered from `app.js`. Camera/mic and installability already require HTTPS (NFR-02); no offline data editing.

### data-testids

- Applied **literally in the Jinja templates**, one template per screen: `data-testid="<screen>.<element>"` exactly as in screen-inventory, repeated rows adding `data-id`. No abstraction layer — greppable and stable; changes are breaking changes QA must approve.
- Islands attach behaviour to server-rendered IDs; they never render their own test IDs. Because the server is the single render path, an optional later contract test can parse screen-inventory and grep templates for every ID.

### Bundle and CSP

- **JS (all vendored, all same-origin, no CDN at runtime):** htmx 2.x (~14 KB gz), a QR fallback decoder for engines without `BarcodeDetector` (iOS/Safari; exact library pinned in the build ticket — pure-JS, vendored, ~10 KB), `app.js`, `islands/voice.js`, `islands/scanner.js`. **Target < 60 KB gz total, no bundler.**
- Vendoring: `scripts/vendor-frontend.sh` downloads pinned versions with checksums into `static/vendor/`, run only on a bump; files are committed.
- **CSP** on every document (NFR-04; the security test row asserts no third-party origins):
  `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'; object-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'`
  - No `unsafe-inline`, no `unsafe-eval` anywhere. Therefore: no inline handlers or `hx-on:` attributes (banned by convention + a lint grep); htmx configured via `<meta name="htmx-config">`; no inline styles; the PDF viewer embeds same-origin PDFs via `<embed>` (why `object-src` is `'self'`, not `'none'`); SSE and fragment fetches are same-origin.
- CSS target < 40 KB; Jost woff2 subset (~two weights) self-hosted.

### Layout in the repo

```
src/whereabouts/
  web/                 # FastAPI routers, CSP + session middleware, fragment conventions
    templates/         # base.html + one template per screen (S01–S21)
    static/
      css/    tokens.css base.css components.css
      js/     app.js islands/voice.js islands/scanner.js
      vendor/ htmx.min.js qr-fallback.js
      fonts/  icons/  manifest.webmanifest
scripts/vendor-frontend.sh
tests/{unit,integration,contracts,pdf,e2e}/
```

## Commands (Python 3.12 everywhere; no Node in dev, CI or the container)

| Slot | Command |
|---|---|
| Install | `pip install -e ".[dev]"` |
| Vendor static libs (on bump only) | `scripts/vendor-frontend.sh` |
| Lint | `ruff check . && djlint src/whereabouts/web/templates --lint` |
| Format check (same CI job) | `ruff format --check . && djlint src/whereabouts/web/templates --check` |
| Type-check | `mypy src tests` (config in `pyproject.toml`) |
| Unit | `pytest tests/unit -q` |
| Full pre-merge suite (CI `unit` job) | `pytest -q -m "not e2e"` (unit + integration + contracts + pdf) |
| E2E, one-time | `playwright install chromium` |
| E2E | `pytest tests/e2e -q` |
| Build | `docker build -t "ghcr.io/simsjm/whereabouts:tree-$(git rev-parse HEAD^{tree})" .` |

- E2E boots the app itself (uvicorn, temp SQLite, `APP_ENV=test`, `SEED_FIXTURES=demo`, `TEST_LOGIN=on`, Whisper + parser fakes, scanner driven by the injected-code hook), viewport 390 × 844 plus one desktop smoke. In CI the same suite runs against the built image (ci-cd §5).
- These slots land in `AGENTS.md` and `.factory/factory.yaml` (`commands.test` = `pytest -q -m "not e2e"`) in the first build ticket; QA's checks and the Developer/QA hires are unblocked by this table.

## Consequences

- **No data changes.** No new tables, no draft storage (flows are stateless forms), no change to events or the domain model.
- New endpoints for the islands only: chunked audio upload + SSE transcript stream (voice), and the inject-a-code test hook (gated to `APP_ENV != production`). The scanner needs none — it navigates to `/c/<code>`.
- Build tickets (once Developer/QA are hired) add: `web/` routes/templates/static, the two islands, the vendor script, `pyproject.toml` toolchain, real steps for the CI placeholder jobs `lint`/`types`/`unit`/`e2e` (`.github/` is high-risk — Jamie merges), and the AGENTS.md/factory.yaml command slots; architecture.md §2/§8 are completed against this ADR, which is adopted by this file.

### Risks and mitigations

1. **Island sprawl** — capped at the two device flows; a lint grep bans `hx-on:` and inline handlers; new islands need an ADR note.
2. **CSP strictness slows early UI work** — prototype HTML can't be pasted wholesale (no inline styles/handlers); tokens + component classes are designed once in the scaffolding ticket. Worth it for NFR-04.
3. **Server-echo patterns are unfamiliar to SPA-raised agents** — one worked example per pattern (stepper, chip cycle, wizard step, review edit) goes into the scaffolding ticket and architecture.md.
4. **Live transcript over VPN** (chunked upload + SSE) is the hardest single flow; the same UI degrades to transcript-on-stop if streaming proves heavy — see "Still open", flagged to Jamie, decided in the voice build ticket.
5. **Per-tap round trips** rely on LAN/VPN latency staying small — accepted for MVP against NFR-09; revisit with evidence.
6. **Hand-rolled SW** must not serve stale assets — cache name derives from the tree hash the app serves; the smoke test asserts SW version matches the image.

## Still open in the decision log

These are needed by the chosen stack, but not decided here:

- **O-02** (auth ADR-0003) — the stack assumes a cookie session + CSRF token per form; sign-in screens are blocked on it, the stack is not.
- **O-09** production hostname — QR URLs and manifest render from `PUBLIC_BASE_URL`; CSP unaffected (same-origin).
- **O-05** parser provider — the island and e2e fakes depend only on the transcript/JSON contract.
- **O-10** CSV columns, **O-12** PDF engine — screen fields and the embedded PDF's producer; not stack-blocking.
- **O-13/O-15/O-16** pipeline mechanics — affect CI wiring of these commands, not the commands.
- **New flag for the log (Product → Jamie):** is "live transcript while listening" (FR-VOI-02) required for v1, or acceptable as transcript-on-stop with the same review screen? The stack supports both; it sizes the voice build ticket.