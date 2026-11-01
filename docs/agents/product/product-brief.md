# Whereabouts — Product brief

> v1.0 · 31 October 2026 · Owner: Jamie · Audience: Product agent first, everyone second.

## 1. The problem

Households lose track of where things are stored: the loft, the garage shelves, the box under the stairs. The usual fix is asking someone else ("where are the allen keys?"). Jamie built Whereabouts to stop asking his other half.

Most people who start a home inventory never finish it, because recording things is tedious. The hard part is **capture**, not retrieval.

## 2. The product

A self-hosted, mobile-first web app (PWA) that knows where everything in the home is kept.

- **Find:** type or say "Where's…?" and get the full path: *Garage › Shelf 2 › Toolbox (B-0042)*.
- **Capture fast:** scan or pick a box, say what's going in ("three extension leads, a cordless sander and a box of wall plugs"), review the parsed list, confirm.
- **Label:** every box and place gets a QR label as a print-ready PDF. Scanning the label opens the box.
- **Share:** the whole household uses it; every change is attributed and can be undone.
- **Move house:** pack and label boxes for rooms in the new home, scan to unpack.

**One-line message:** say what goes in the box, and ask your assistant where it went.

## 3. Users

| User | Needs |
|---|---|
| Household admin (Jamie) | Sets up homes and rooms, invites people, prints labels, runs the server |
| Household member (partner) | Finds things, moves things, adds things, undoes others' mistakes |
| Mover | Packs and labels quickly, unpacks into the right room |
| AI assistant (post-MVP, via MCP) | Reads and safely writes the inventory on a person's behalf |
| Guests / kids (later) | Read-only |

Primary context: one hand on a phone, standing in front of a shelf or an open box.

## 4. Positioning

**Voice-first, private, AI-native household inventory for people who self-host, with moving house as the entry point.**

Differentiators (from the competitor analysis; see `competitor-analysis.md`):

1. **Voice capture with a review step** — only SmartStow (Android, subscription) is voice-first.
2. **Private by default** — transcription on the household's own Whisper server; no third-party calls.
3. **Safe agent writes** — event log, attribution, one-step undo, scoped tokens, no hard deletes (MCP arrives post-MVP but the data model is built for it now).
4. **UK-friendly print output** — A4 24-up and 62 mm roll PDFs, print queue, alignment calibration. Homebox prints US Letter (Avery 5260).
5. **Calm, polished mobile design** — self-hosted tools are usually functional, not pleasant.

No product reviewed combines voice capture, local processing and safe agent writes.

## 5. Market summary

- **Homebox** (free, self-hosted, AGPL-3.0) is the incumbent; its v0.26 merged items and locations into one "entity" model and broke integrations. AI only via add-ons.
- **HomeHoard** is the closest concept (Home Assistant voice, MCP with 13 tools, check-out) but agents cannot add or delete; single developer.
- **Consumer AI apps** (StuffID, Rorg, Shelver, SnapFind, Vorby, ShelfLily) compete on photo-to-inventory and cloud sync.
- **Sortly** shows households won't pay business prices ($49/month for QR labels).
- As a commercial product it's a hard market; as a personal build with a possible open-source release it has a defensible niche. Paid demand most likely comes from moving house.

## 6. Goals for v1

1. Jamie's household uses it daily instead of asking each other.
2. A full room can be captured by voice in minutes, with labels printed.
3. A house move can be run end to end in the app (pack → label → scan → unpack → finish).
4. Nothing is ever lost: every change is attributed and undoable; no hard deletes.

## 7. Success measures (proposed)

- Time from "where is X?" to answer: under 10 seconds on a phone.
- Voice capture: a 10-item box recorded and confirmed in under 60 seconds.
- Zero data loss incidents; every write produces an event (`event-log-coverage` check).
- Partner uses it unprompted within the first month.

## 8. Strategy notes

- **Release:** low-cost "here's my code" open-source release first (README, Docker Compose). Step up only with demand. The safe-write MCP pattern might be worth publishing on its own.
- **Hosted option:** being tested via the coming-soon site's interest list (`plan = self | hosted | unsure`). Price TBC.
- **Switching cost:** CSV import should accept Homebox exports.
- **Ecosystem:** if released publicly, pursue Home Assistant integration early — it's where self-hosters do voice retrieval.

## 9. Non-goals

- Warranty, value, receipts, maintenance tracking.
- Native mobile apps.
- Direct printer drivers.
- Cloud-hosted data by default.
