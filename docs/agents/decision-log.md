# Decision log and conflict resolutions

> **Status:** v1.0 — 31 October 2026. Owner: Jamie (maintainer, architect of record).
> **Read this first.** Where any document in this pack (or in `archive/`) disagrees with this log, **this log wins**. Raise further conflicts with Jamie; do not resolve them yourself.

## 1. How to read this

- **Settled** decisions are binding. Agents implement them; they do not reopen them.
- **Open** decisions are listed in §4 with an owner. An agent that needs one answered blocks the issue and asks.
- **Superseded** items are listed in §3 so that nobody re-implements something from an older doc in `archive/`.

## 2. Settled decisions

| # | Area | Decision | Date | Source |
|---|---|---|---|---|
| D-01 | Name | The product is **Whereabouts**. "Rummage" (clashed with tryrummage.com) and the Norse names (Vör, Mímir, Muninn, etc.) are retired and must not appear in code, copy or docs. | 4–6 Oct | naming chat, website handover |
| D-02 | Repo | App repo: `https://github.com/SimsJM/whereabouts` (public, Issues on). `whereabouts-home` was suggested as a technical name to avoid the Kubernetes "whereabouts" plugin; not adopted for the repo. | 6–8 Oct | website handover |
| D-03 | Purpose | Help a household know where everything is stored and find it fast on a phone, by search, voice or scanning a QR label. Built from Jamie's own pain ("where is X?" asked of his other half). | 2 Oct | spec |
| D-04 | Positioning | Voice-first, private, AI-native household inventory for self-hosters; **moving house is the launch scenario**. | 26 Sep | competitor analysis |
| D-05 | Backend | Own backend (not built on Homebox). **FastAPI + SQLite**, Python. One service layer shared by web and (later) MCP. | 2 Oct | spec, competitor analysis |
| D-06 | Client | **PWA** (installable, camera for QR, mic). Not a native app. | 2 Oct | spec |
| D-07 | Frontend stack | **Open — the Architect's first decision record** (ADR-0002). Jinja + HTMX + Alpine.js was proposed so Jamie (Python background) can contribute; an SPA is the alternative. Constraint: Jamie must be able to contribute to it over time. | 31 Oct | Jamie, this handover |
| D-08 | Hosting | Self-hosted on Jamie's Proxmox homelab. Database on ZFS for snapshots. Shipped as a container image `ghcr.io/simsjm/whereabouts`. | 2–6 Oct | spec, pipeline |
| D-09 | Speech | Speech-to-text on Jamie's **own Whisper server** (Wyoming). Browser speech API is not used (Android sends audio to Google). Whisper does **not** need Ollama. | 2–8 Oct | spec, site chat |
| D-10 | LLM use | Only **voice-transcript → structured items** needs an LLM in v1. No GPU on the nodes, so it calls a **cloud model**; the model is configuration only so it can move to local later. Search, duplicate flagging and box-name suggestions use non-LLM methods (FTS, fuzzy match, rules). | 3 Oct | hardware chat |
| D-11 | Location model | One location tree: **Home › Room › Place › Box**. Levels can be skipped, never inverted. Boxes may sit inside boxes. Multiple homes per household. Items sit on a Room or deeper. | 9 Oct | spec |
| D-12 | Terminology | "Location" is **internal only** (data model, API, MCP). The UI says Home, Room, Place, Box, "Move to…", "Where is it?". "Spot" and "Unit" rejected (Spot too American). | 9 Oct | spec |
| D-13 | Codes | Boxes `B-0001`, places `P-0001`. Sequential, unique per household, **never reused**. (The pipeline doc's `L-` prefix is wrong — see §3.) | 9 Oct | spec |
| D-14 | Deletes | **No hard deletes.** Archive, or quantity zero. | 2 Oct | spec |
| D-15 | Event log | Append-only event log for every write, with actor (user or agent). Powers history, "where was it last?", one-step undo and attribution. | 2 Oct | spec |
| D-16 | Labels | Always a **print-ready PDF** handed to the phone's print/share sheet. No direct printer integration. 62 × 29 mm roll and A4 24-up (63.5 × 33.9 mm). | 2 Oct | spec |
| D-17 | QR content | QR encodes a URL to the code (`https://<app-host>/c/B-0042`), never the contents. | 2 Oct | spec |
| D-18 | Look and feel | Land Rover Defender Pivi Pro centre console: warm neutrals, single bronze accent, letter-spaced uppercase labels, thin line icons, Jost font. | 2 Oct | spec |
| D-19 | Home screen | **The prototype's single page wins**: "Where's…?" search bar with mic, conditional moving-house card, and Changes / Looked for / Pinned / Lent out tabs. The spec's swipeable SEARCH/ROOMS/RECENT panels are superseded. | 31 Oct | Jamie, this handover |
| D-20 | MVP scope | v1 = search, voice search, add by voice (with review), rooms/places/boxes, QR labels + PDFs + print queue + calibration, QR scanning, bulk CSV import, history/undo, multi-user households, multiple homes, **moving-house mode**, **Lent out** and **Pinned**. **Not v1:** MCP server, photo-to-inventory. | 31 Oct | Jamie, this handover |
| D-21 | Out of scope | Warranty, value and maintenance tracking (different job: insurance). | 26 Sep | competitor analysis |
| D-22 | Agent platform | **Software factory: Pi (pi.dev) as harness, Paperclip as orchestrator** via the `pi_local` adapter. Hermes is **not** part of the factory; it remains Jamie's personal assistant. | 29 Oct | factory chat; confirmed 31 Oct |
| D-23 | Roles | Five roles: **Product, Architect, Developer, QA, Support**. Product and Support are company-wide; Architect, Developer, QA are per project. The old Triage, Reviewer and Maintainer roles are folded in (Support ≈ Triage; Architect does PR review; maintenance becomes scheduled Developer issues). | 29–31 Oct | factory chat; confirmed 31 Oct |
| D-24 | Models | Ollama Cloud (Pro, 3 concurrent requests), key separate from Hermes. Two tiers per pack: `build` (Developer, QA) and `review` (Product, Architect, Support). No GPU purchase. | 3–29 Oct | cost chats, factory chat |
| D-25 | Factory host | Paperclip + Pi in one unprivileged LXC on the homelab, non-root `factory` user, no sudo. **No agent holds deploy credentials.** | 29 Oct | factory chat |
| D-26 | Workspaces | Paperclip isolated workspaces: one git worktree + branch per issue; every issue ends in a PR. | 29 Oct | factory chat |
| D-27 | Test before merge | Regression runs on every PR (GitHub-hosted runners). `main` only holds code that passed. Same-repo PRs also get an ephemeral homelab preview. | 6 Oct | pipeline v0.4 |
| D-28 | Build once | Images tagged by git tree hash (`tree-<hash>`); the tested image is the one promoted. | 6 Oct | pipeline v0.4 |
| D-29 | Merging | Jamie merges features, refactors, high-risk fixes and maintenance. Low-risk confirmed bug fixes may auto-merge — **off for the first month**. | 4–6 Oct | pipeline v0.4 |
| D-30 | Bugs | Confirmed bugs skip Jamie's approval; QA writes a failing repro test first. | 4 Oct | pipeline |
| D-31 | Agent wiki | Public agent docs live in the app repo under `docs/agents/`, entry point `AGENTS.md`, built with MkDocs Material to GitHub Pages. **No hostnames, IPs, VLAN names or secrets** in it. | 4 Oct | agents chat |
| D-32 | Website | Separate coming-soon site (Starlette + SQLite sign-ups, Watchtower, behind existing Caddy). It is a second project in the same Paperclip company and is the **factory pilot**; the app follows. | 8–29 Oct | website handover, factory chat |
| D-33 | Open source | Start as a low-cost "here's my code" release (README, Docker Compose, maintained for own use); step up only if demand appears. Hosted SaaS is being explored via the site's interest list (price TBC). | 2–8 Oct | spec, site |
| D-34 | Codebase map | No graphical codebase map. Text-first: `architecture.md` + Mermaid; optional LSP MCP (e.g. Serena) and an auto-generated repo map regenerated on merge. | 6 Oct | codebase-viz chat |

## 3. Superseded or corrected content

| Where (in `archive/`) | What it says | Now |
|---|---|---|
| `home-inventory-spec.md` §8 | Home = swipeable SEARCH/ROOMS/RECENT panels with page dots; "Decision: keep the big panels" | D-19: single-page home from the prototype |
| `home-inventory-spec.md` header, §11 | "Working name not yet chosen"; Norse shortlist | D-01: Whereabouts |
| `home-inventory-spec.md` §2 | "One LXC running FastAPI + SQLite + the PWA" | Still the production shape, but delivered as a container image via CI (D-08, D-28) |
| `deployment-pipeline.md` v0.4 §2–4, §10 | Hermes profiles, Hermes Kanban board, card chains, Telegram via Hermes | D-22/D-23: Paperclip + Pi; see `factory/` |
| `deployment-pipeline.md` §7 | "Box (`B-`) and location (`L-`) codes" | D-13: `B-` and `P-` |
| `deployment-pipeline.md` §2 | Reviewer on a different model lab, required Reviewer approval | Architect reviews; Jamie's review is the required GitHub approval (see O-06) |
| `hermes-agent-setup.md` | Whole document | Superseded by D-22. Kept for reference only (Hermes is still Jamie's personal assistant) |
| `home-inventory-demo.html` | Loads Jost from Google Fonts | App must self-host fonts (no third-party calls, as on the site) |
| `home-inventory-demo.html` bulk import | Copy "Rooms, locations and boxes…", tag "New location" | Violates D-12. Use "Rooms, places and boxes…" and tag "New place"/"New box" |
| `home-inventory-demo.html` | Footer/notes say "decorative QR codes" | Real QR codes encoding the D-17 URL |
| Competitor analysis | Recommends photo-to-inventory in first release | D-20: not v1 (needs a cloud vision model) — first post-MVP candidate |

## 4. Open decisions

| # | Question | Owner | Default until decided |
|---|---|---|---|
| O-01 | Frontend stack (D-07) | Architect proposes ADR-0002; Jamie approves | Nothing UI-heavy is built before ADR-0002 is accepted |
| O-02 | Authentication: local accounts with passkeys vs OIDC (e.g. Authentik). A **test-only login** is required either way for QA and previews | Architect → Jamie | Build behind an auth interface; test login behind `TEST_LOGIN=on` |
| O-03 | Same item in two places: separate rows per location vs one item with quantity per location | Product → Jamie | v1: one item = one location (separate rows) |
| O-04 | Cross-home search ("all homes" option) | Product | v1: current home only, with an empty-state hint |
| O-05 | Cloud model and provider for voice parsing (D-10) | Architect | Config-driven; recorded fixtures in tests |
| O-06 | GitHub identities: one PAT per repo (factory chat) vs one account per agent (pipeline v0.4). With a single identity an agent cannot formally approve its own PR | Jamie | Jamie's review is the required approval; Architect leaves a review comment |
| O-07 | Model IDs for `build` and `review` tiers on Ollama Cloud, and its OpenAI-compatible base URL | Jamie | Candidates listed in `factory/factory-overview.md` §6 |
| O-08 | Site repo name and whether it is separate from `SimsJM/whereabouts` (recommended: separate, e.g. `SimsJM/whereabouts-site`) | Jamie | Separate repo |
| O-09 | Production hostname/domain (candidates checked: trywhereabouts.com, whereabouts.house/.place/.family, use-/hey-/gowhereabouts.com) | Jamie | `<app-host>` placeholder |
| O-10 | Final CSV template columns | Product | `item, quantity, category, room, place, box_code` (+ optional `unit, tags, notes`) |
| O-11 | First big load-in workflow (room by room vs bulk vs dictation while packing) | Product | Support all three; design for moving-house dictation |
| O-12 | PDF engine: WeasyPrint vs ReportLab | Architect | Either; must produce vector QR + embedded fonts |
| O-13 | Size threshold for high-risk PRs | Jamie | ~200 changed lines |
| O-14 | Preview TLS: Caddy internal CA vs real certs via DNS challenge | Jamie | Internal CA |
| O-15 | Merge queue availability on a user-owned repo | Developer checks | Fall back to "require branches up to date" |
| O-16 | Paperclip/Pi verification items (skills under `pi_local`, `PAPERCLIP_PI_PROVIDERS` env, isolated workspaces experimental → pin version, CLI vs API for `factory-apply`, company export/import) | Jamie + Claude Code | See `factory/factory-overview.md` §9 |
| O-17 | Privacy notice page for the site (UK GDPR — it collects emails) and for the app once hosted | Jamie | Add before the site goes live |
| O-18 | Whether to publish the safe-write MCP pattern separately | Jamie | Later |
| O-19 | Read-only role for guests/kids | Product | Post-MVP |
| O-20 | Mascot based on Jamie's dog Skye that "finds things for you" (feature, not app name) | Product | Post-MVP idea |
