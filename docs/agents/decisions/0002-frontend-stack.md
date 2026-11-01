# 0002. Frontend stack

- **Status:** Proposed — **Architect to complete** (first design issue) · **Decided by:** Jamie

## Context
- PWA, mobile-first (390 × 844), camera (QR) and mic, works over VPN. Design system in `../design/`.
- Jamie (Python background) must be able to contribute over time (D-07).
- Agents (open models on Ollama Cloud) build most of it: favour conventional, well-documented patterns.
- E2E tests target `data-testid` attributes defined before the UI exists.
- No third-party runtime calls; strict CSP.

## Options to evaluate
1. **Server-rendered Jinja + HTMX + Alpine.js** (proposed in October): one language, minimal JS, easy for Jamie; check fit for the voice review screen, scanner, and stateful multi-step flows (start a move).
2. **SPA (e.g. Svelte/SvelteKit or React) over a FastAPI JSON API**: richer client state; adds a JS toolchain and an API contract.
3. Hybrid: server-rendered pages with small islands for scanner/voice.

## Decision
_To be written._ Include: routing, state, how tokens.css is consumed, PWA service worker approach, how `data-testid`s are applied, bundle/CSP implications.
