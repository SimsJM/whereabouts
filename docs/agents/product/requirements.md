# Whereabouts — Requirements (v1 / MVP)

> v1.0 · 31 October 2026 · Owner: Product agent (maintains), Jamie (approves).
> Sources: spec (9 Oct), clickable prototype (`../design/prototype/home-inventory-demo.html`), competitor analysis, decisions in `decision-log.md`.
> **Priority:** M = must for v1, S = should for v1, C = could, L = later (post-MVP, see `roadmap.md`).
> **IDs are stable.** Issues, tests and PRs reference them (e.g. `FR-SRCH-03`). Never renumber; deprecate instead.
> **Terminology:** the UI never says "location". It says Home, Room, Place, Box (see `../design/design-system.md` §8).

---

## 1. Households, users and access

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-USR-01 | M | A household has multiple users. | Admin can invite a person by email or link; invitee joins the same household and sees the same data. |
| FR-USR-02 | M | Roles: **admin** and **member**. | Only admins can invite/remove users and manage homes; members can do everything else. |
| FR-USR-03 | M | Every change is attributed to a person (or agent). | Each event shows actor name and time; history rows show the actor's initial avatar. |
| FR-USR-04 | M | Authentication. | Method per ADR (O-02: passkeys vs OIDC). A **test-only login** exists when `TEST_LOGIN=on` and is impossible to enable in production. |
| FR-USR-05 | M | Account screen. | Shows name, role and household; household member list with roles; "Invite someone". |
| FR-USR-06 | L | Read-only role for guests/kids. | — |

## 2. Homes and the location tree

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-LOC-01 | M | One tree of levels: **Home (1) › Room (2) › Place (3) › Box (4)**. | Data stored in a single `locations` structure with `kind`. |
| FR-LOC-02 | M | Levels may be skipped but never inverted. | A box can sit directly in a room; a room can never be inside a place or box; only homes have no parent. Violations are rejected by the service layer with an actionable error. |
| FR-LOC-03 | M | Boxes may sit inside boxes (e.g. Tackle box inside Fishing crate). | A box's parent may be a box; nesting depth is unlimited; cycles are rejected. |
| FR-LOC-04 | M | Multiple homes per household (main house, second house, parent's house). | Header shows HOME + current home name; tapping opens the home switcher listing every home with "N rooms · N items" and a "Current" pill. Switching resets room/box context to that home and shows a toast "Switched to <home>". |
| FR-LOC-05 | M | Add a room, place or box. | Available from Rooms (Add room tile), Room (+ / New box), Place (New box here) and the + sheet. |
| FR-LOC-06 | M | Moving a place or box moves everything inside it. | One parent change; contents' paths update immediately. |
| FR-LOC-07 | M | Breadcrumbs. | Every Place/Box/Item shows its path (e.g. `Garage › Shelf 1`); tapping the crumb opens the room. |
| FR-LOC-08 | M | "Anywhere in <Room>" is a real destination. | Items can be filed directly on a room; Room screen shows an "ANYWHERE IN <ROOM>" group when such items exist; Place screen for a room reads "Things in this room without a specific place". |
| FR-LOC-09 | M | Codes: boxes `B-0001`, places `P-0001`. | Sequential, unique across the household, **never reused** even after archiving. Homes and rooms have no code. Next code shown on new-box screens before creation. |
| FR-LOC-10 | M | Archive (never delete) rooms, places and boxes. | Archived locations disappear from lists and search; their codes stay reserved; scanning an archived label shows an "archived" message, never a different box. |

## 3. Items

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-ITM-01 | M | Item fields: name, category, quantity, unit, tags, optional photo, notes. | Name and quantity required; others optional. |
| FR-ITM-02 | M | Each item points at **one** location that is a Room or deeper. | Every item therefore has a home and a room. Filing an item on a Home is rejected. |
| FR-ITM-03 | M | Item screen. | Shows category (uppercase label), name, location card (box icon if in a box, pin icon otherwise; "Anywhere in <Room>" when on a room), quantity stepper, Move, Archive, pin star, lent banner if lent, and the item's history. |
| FR-ITM-04 | M | Adjust quantity. | − / + steppers on item, box and place screens; minimum 0; each change is an event. Quantity 0 keeps the item (does not archive). |
| FR-ITM-05 | M | Move an item. | "Move" opens a picker ("MOVE TO · Where is <item> going?") grouped by room: "Anywhere in <Room>" plus every place and box with code and path; current location marked "Current". Moving produces an event with undo; toast "Moved to <dest>". |
| FR-ITM-06 | M | Archive an item. | Item leaves lists and search; event recorded; toast "<item> archived"; returns to previous screen. |
| FR-ITM-07 | S | Optional photo per item/box. | Never required. v1 = container photos. |
| FR-ITM-08 | L | Same item in multiple places with per-location quantities (O-03). | — |

## 4. Search and retrieval

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-SRCH-01 | M | Text search with fuzzy matching across items, places and boxes. | SQLite FTS to start. Matches item name + category and location name + code. Token match tolerant of plurals ("batteries" ↔ "battery"). |
| FR-SRCH-02 | M | Results show the full path. | Item rows: name, path, right-hand "Qty N" (prefixed "Packed · " if its box is packed for a move). Box/place rows: name, `code · path`, right-hand "Box"/"Place". Header "N RESULTS". |
| FR-SRCH-03 | M | Scoped to the current home. | Home switcher available on the search screen. Empty state: "Nothing in <home> matches "<q>"" + "Try a category, or a box code like B-0042". |
| FR-SRCH-04 | M | Search by code. | Typing `B-0051` returns that box. |
| FR-SRCH-05 | M | Suggestions. | With an empty query, a "TRY" row of chips (e.g. recent or popular queries). |
| FR-SRCH-06 | M | Reachable from everywhere. | Bottom rail Search tab, home "Where's…?" bar, and search from any screen. |
| FR-SRCH-07 | L | Semantic search via embeddings ("the thing for hanging pictures"). | — |
| FR-SRCH-08 | L | "All homes" search option (O-04). | — |

## 5. Voice

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-VOI-01 | M | Voice search. | Tap mic (home bar or search screen) → "LISTENING · Say what you are looking for" with pulse animation → audio transcribed on **own Whisper server** → normal search runs with the transcript as the query. |
| FR-VOI-02 | M | Add by voice to a chosen destination. | From a box, place, the + sheet or after printing a label. Screen "ADD BY VOICE · ADDING TO <dest>" with path/code and a "Change" link (opens picker in voice mode: "ADD TO · Where are these going?"). Live transcript while listening; hint "Say items with quantities — "two tape measures, a spirit level""; "Done" stops. |
| FR-VOI-03 | M | Transcript parsed into structured items by an LLM. | Each parsed item has name, category, quantity (and unit if spoken). Model is config-only (O-05). |
| FR-VOI-04 | M | **Review screen before saving.** | Shows "WHAT I HEARD" + transcript and a "PARSED · N items" list; each row has quantity stepper (min 1) and remove (×). "Record again" restarts; primary button "Add N items" (disabled "Nothing to add" when empty). Nothing is saved until confirm. |
| FR-VOI-05 | M | Duplicate flagging and merge. | If a parsed item matches an existing item in the home, show "Already have these in <path>" + "Merge". After merge: "Will add to the existing entry in <path>"; confirming adds quantity to the existing item instead of creating a new one. |
| FR-VOI-06 | M | Confirm writes one event per change plus a summary event. | Toast "N items added to <dest>"; returns to the destination screen. |
| FR-VOI-07 | M | Audio privacy. | Audio goes only to the household's Whisper server; never to the browser speech API or a third party. The transcript (text only) may go to the configured parsing model. |

## 6. Boxes, labels and printing

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-LBL-01 | M | New box flow. | Name (with suggestion chips, e.g. Camping gear, Cables, Kids clothes, Party supplies), "WHERE IN <ROOM>" chips (Anywhere + each place), live label preview with auto-assigned code, format choice **Print now** / **Add to A4 sheet**. The box record exists **before** the label prints. Create disabled until a name is entered. |
| FR-LBL-02 | M | "Print now" → label-ready screen. | "LABEL READY · Stick it on the box" with label preview; actions "Fill it by voice", "Scan to check", "Open the label PDF again". |
| FR-LBL-03 | M | Single label PDF: 62 × 29 mm, one per page. | Vector QR + code + name + path, embedded fonts. File name `label-<code>.pdf`. |
| FR-LBL-04 | M | A4 sheet PDF: 24-up at 63.5 × 33.9 mm (3 × 8). | Unused positions left blank so part-used sheets can be reused. File name `label-sheet-<n>-labels.pdf`. |
| FR-LBL-05 | M | A4 print queue. | Labels accumulate ("N labels waiting to print" banner on Rooms with "Make PDF"); Label sheet screen shows a 24-slot preview, "N spaces left", rows with remove; "Create sheet PDF". Queue cleared **only** when the user taps "Printed OK: clear these from the queue" (a jam doesn't lose them). Adding a box already queued shows "<code> is already on the sheet". |
| FR-LBL-06 | M | Labels for any location except a home. | Places have "Print place label"; boxes have Print label. Same feature. |
| FR-LBL-07 | M | PDF viewer hand-off. | Shows the PDF with spec text, tip "Print at 100% (actual size). Turn off "Fit to page" or the QR codes will shrink.", Print, Share, Save to Files. Hands off to the phone's print/share sheet. |
| FR-LBL-08 | M | Calibration. | Settings › Labels: "Nudge across" / "Nudge down" in 0.5 mm steps (shown as e.g. "+0.5 mm"), applied to sheet PDFs; "Alignment test sheet (PDF)" outlines all 24 positions with centre marks. |
| FR-LBL-09 | M | PDFs generated server-side. | So agents can request labels later via MCP. |
| FR-LBL-10 | M | Label printed is an event. | "Label <code> · Label PDF made" / "Label sheet · Printed N labels". |

## 7. QR scanning

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-QR-01 | M | QR encodes `https://<app-host>/c/<CODE>`. | Never the contents, so labels don't go stale. Human-readable code printed as fallback. |
| FR-QR-02 | M | Phone camera opens it directly. | `/c/B-0042` resolves (after auth) to the box; `/c/P-0003` to the place. Unknown code: actionable error with closest matches. |
| FR-QR-03 | M | In-app scanner. | Bottom rail scan button and "Scan a box first" in + sheet. Dark scanner screen with corner frame, sweep line, "Point the camera at a box label"; on find shows "FOUND · <code> · <name> · <room> · Opening…" and opens it. "OR OPEN A RECENT LABEL" chips. |
| FR-QR-04 | M | Scan-to-file. | Scanning from an add flow sets the destination for adding items. |
| FR-QR-05 | M | Scan-to-unpack during a move (see §11). | Scanning a packed box opens the Unpack screen instead of the box. |

## 8. Bulk import

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-BLK-01 | M | CSV import. | Columns `item, quantity, category, room, place, box_code` (final template O-10). "Download template" provided. Choose a CSV or "Use the sample file". |
| FR-BLK-02 | M | Missing rooms/places/boxes are auto-created. | Preview tags each row **New**, **New place/New box**, or **Merge**. |
| FR-BLK-03 | M | Preview/review before saving. | Summary sentence (e.g. "5 new items, 1 merge, and a new Shelf 3 with a Car kit box"); row list with name ×qty and full path; "Import N rows" (becomes "Already imported"); "Choose another file". Duplicates flagged. |
| FR-BLK-04 | M | Import is one summary event plus per-item events, undoable as a batch (Architect to confirm undo granularity). | Toast "N rows imported · <created> created". |
| FR-BLK-05 | S | Accept Homebox exports. | Map Homebox CSV columns to ours. |

## 9. History and undo

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-HIS-01 | M | Append-only event log. | Event types at least: item added, moved, quantity changed, archived, returned/lent, pinned/unpinned (optional), location created/moved/archived, label printed, label sheet printed, import, voice add, move started/packed/unpacked/finished. Each records actor (user or agent), time, before/after. |
| FR-HIS-02 | M | Household history screen. | "HISTORY · Household activity": rows with actor initial, subject, "<detail> · <actor> · <when>". |
| FR-HIS-03 | M | Per-item history. | Item screen "HISTORY" list; "No changes recorded yet" when empty. |
| FR-HIS-04 | M | One-step undo. | Undo the most recent undoable change (moves at minimum). Undo writes a new event ("Moved back to <from>"), never edits history. If the item was archived: toast "That item was archived". Toast "Undone: <item> is back in <from>". |
| FR-HIS-05 | M | "Where was it last?" | Derivable from move events. |

## 10. Home screen lists

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-HOME-01 | M | Single-page home (D-19). | Header (HOME label + home name ▾ switcher; account avatar), "Where's…?" search bar + accent mic button, optional moving card, tab list, bottom rail. |
| FR-HOME-02 | M | **Changes** tab. | "What other people have changed since you last looked." Shows recent changes by **other** actors (people and agents) in the current home, each with Undo where undoable; "Full household history" link. Badge with count. Default tab when non-empty. |
| FR-HOME-03 | M | **Looked for** tab. | "Things you looked for recently, and where they are now." Up to 6 most recently opened items (per user), with current path. |
| FR-HOME-04 | M | **Pinned** tab. | "Things that must never go missing. Pin anything from its page." Star on the item screen toggles (toast "Pinned to your home screen" / "Removed from Pinned"). Per user (assumption — Product to confirm). |
| FR-HOME-05 | M | **Lent out** tab. | "Things that are out of the house right now." Rows "Lent to <who> · since <when>" with **Returned** button. Badge with count. |
| FR-HOME-06 | M | Empty states. | Changes: "Nobody else has changed anything since you last looked." Looked for: "Search for something and it shows up here." Pinned: "Nothing pinned yet. Tap the star on any item to pin it." Lent: "Nothing is lent out." |

## 11. Lending (check-out)

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-LEND-01 | M | Mark an item lent: to whom, since when. | Separate from the item's usual home (location unchanged). Event recorded. *(Prototype shows lent state but not the "lend" action UI — design it in the item screen.)* |
| FR-LEND-02 | M | Item screen lent banner. | "Lent to <who> since <when>" + Returned. |
| FR-LEND-03 | M | Mark returned. | Clears lent state; event "Returned by <who>"; toast "<item> is back". |
| FR-LEND-04 | C | Due date. | — |

## 12. Moving house

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-MOVE-01 | M | Start a move (3 steps). | From + sheet ("Start a move") or home switcher ("Add the home we're moving to"). Step 1: MOVING FROM (home chips) + MOVING DAY (date or "Not decided yet"). Step 2: name for the new home + rooms chips (default set: Kitchen, Living room, Bedroom 1, Bedroom 2, Bathroom, Loft, Garage); Next disabled without a name and ≥1 room. Step 3: "Bring the boxes you already have": every top-level labelled box in the old home, ticked by default, each auto-mapped to a new room by name (Bedroom → Bedroom 1, otherwise first room), tap to cycle the destination room; boxes inside boxes come along. Button "Start move with N boxes". |
| FR-MOVE-02 | M | Starting a move creates the new home and rooms, re-parents brought boxes to their destination rooms and marks them **Packed**. | Boxes keep their codes (no new labels needed). Event "Move started · N boxes added". Toast "Move started · N boxes ready to go". |
| FR-MOVE-03 | M | Moving card on home. | Shown when current home is the move's from or to home: "MOVING · <FROM> → <TO>", "N boxes to unpack" / "Every box is unpacked" / "Pack your first box", segmented progress bar (one segment per box). |
| FR-MOVE-04 | M | Moving house screen. | Route, moving day, "TO UNPACK · N boxes", stat "N boxes · N unpacked", progress, **Pack a box**, **Scan to unpack**, groups "FOR THE <ROOM>" of packed boxes, "UNPACKED" list with "In <room>". |
| FR-MOVE-05 | M | Pack a new box for the move. | Name + suggestions, "GOING TO" room chips (new home's rooms), label preview with a large black **FOR <ROOM>** band so whoever carries it knows where it goes; "Create box and label PDF". Box created as Packed. |
| FR-MOVE-06 | M | Unpack. | Scan or tap a packed box → Unpack screen: "Arrived at <home>", name, code, "LABELLED FOR <ROOM>", INSIDE list, "PUT IT IN" room chips (defaults to labelled room), "Unpacked in the <room>", "Keep it packed for now". Box becomes Unpacked. Toast "<box> unpacked in the <room>". |
| FR-MOVE-07 | M | Packed state is visible everywhere. | Box rows show "· Packed"; box screen shows "Packed for the <room>" banner with Unpack; search shows "Packed · Qty N". |
| FR-MOVE-08 | M | Add by voice into a packed box. | Same voice flow; returns to the move screen. |
| FR-MOVE-09 | M | Finish move. | When all unpacked: "Every box is unpacked · Finish move". Otherwise "Finish move" asks "N boxes still packed. They stay marked Packed, so you can still find them." with "Finish anyway" / "Not yet". Finishing clears Unpacked flags, switches to the new home, event "Move finished", toast "Welcome to <home>". |
| FR-MOVE-10 | M | Only one active move per household at a time (as prototyped). | + sheet shows "Pack a box for the move" instead of "Start a move" while active. |

## 13. Add sheet and navigation

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-NAV-01 | M | Bottom rail: Home, Search, centre **+** (raised ring), Scan, Rooms. | Active tab in accent. Rail hidden on full-screen flows (voice, pickers, new box, label, bulk, start move, pack, unpack, queue). |
| FR-NAV-02 | M | + sheet "ADD": By voice ("Say what is going into <current box/place>"), Scan a box first, New box, Start a move / Pack a box for the move, Bulk import, Cancel. | Context-aware: destination is the current box/place. |
| FR-NAV-03 | M | Rooms screen. | "ROOMS · <home> · N rooms · N items"; 2-column grid of room tiles (ROOM NAME label, big item count, "items · N containers"), dashed "Add room" tile, print-queue banner when non-empty. |
| FR-NAV-04 | M | Room screen. | "ROOM" header, name, "N items · N containers", one group per place (label + code, rows of boxes and loose items), "ANYWHERE IN <ROOM>" group, "New box in <Room>". |
| FR-NAV-05 | M | Place screen. | PLACE (or ROOM) header, breadcrumb, name, code + "Print place label", "ITEMS HERE", "BOXES HERE", "Add by voice", "New box here". |
| FR-NAV-06 | M | Box screen. | BOX header with print icon, breadcrumb, name, code, label card ("Scan to open this box", Print label), packed banner, CONTENTS with steppers, "BOXES INSIDE", "Add by voice", "More ways". |
| FR-NAV-07 | M | Back behaves as a stack; tabs reset the stack. | — |

## 14. Settings

| ID | P | Requirement | Acceptance criteria |
|---|---|---|---|
| FR-SET-01 | M | Appearance: System / Light / Dark. | System follows `prefers-color-scheme`. |
| FR-SET-02 | M | Labels: formats listed; nudges; alignment test. | See FR-LBL-08. |
| FR-SET-03 | L | AI ACCESS (MCP): list of tokens (e.g. "Claude · Read & write · acts as Jamie", "Home Assistant · Read only"), "Create access token" (shown once, then hidden). | Prototyped; ships with MCP. |

---

## 15. Non-functional requirements

| ID | P | Requirement |
|---|---|---|
| NFR-01 | M | **Self-hosted** on the homelab; one container image; SQLite on ZFS. No cloud dependency except the configured parsing model. |
| NFR-02 | M | **HTTPS required** (camera and mic need a secure context). |
| NFR-03 | M | **Remote access** only via the existing VPN; no public exposure of the app by default. |
| NFR-04 | M | **No third parties at runtime**: no analytics, trackers, CDNs or Google Fonts. Fonts self-hosted. Strict CSP. |
| NFR-05 | M | **Every write goes through the service layer and produces an event** (enforced by `event-log-coverage`). |
| NFR-06 | M | **No hard deletes** anywhere, including admin tools. |
| NFR-07 | M | **Accessibility:** touch targets ≥ 44 × 44 px; every icon button has an `aria-label`; tabs use `role=tablist/tab` + `aria-selected`; toggles use `aria-pressed`; toasts use `role=status`; visible focus ring (2 px accent, 2 px offset); `prefers-reduced-motion` disables pulse/sweep animations; text contrast WCAG AA in both themes. |
| NFR-08 | M | **Mobile-first**: designed at 390 × 844; one-handed; works installed as a PWA. |
| NFR-09 | M | **Performance:** search results < 300 ms for a 5,000-item household on homelab hardware; home screen interactive < 2 s on a mid-range phone over VPN. (Proposed — tune.) |
| NFR-10 | M | **Backups:** ZFS snapshot before every production deploy; restore tested. |
| NFR-11 | M | **Testability:** stable `data-testid` attributes agreed in acceptance criteria; fakes for Whisper (recorded audio + transcripts) and for the parsing model (canned responses); seeded fixtures. |
| NFR-12 | M | **Config by environment**: `APP_ENV`, `DATABASE_URL`, `SEED_FIXTURES`, `TEST_LOGIN`, Whisper URL, parsing model provider/key. Names final once the Architect settles config. |
| NFR-13 | M | **Security:** no secrets, hostnames, IPs or network names in the repo or public wiki; private vulnerability reporting via `SECURITY.md`. |
| NFR-14 | S | **Agent-safety readiness:** data model and service layer designed so MCP can add scoped tokens, agent attribution and undo without schema rework. |
| NFR-15 | M | **British English** in all copy. |
