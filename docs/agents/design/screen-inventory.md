# Whereabouts — Screen inventory and test IDs

> v1.0 · 31 October 2026. Every screen in the prototype, what it contains, where it leads, and the **`data-testid` contract** QA writes tests against before the UI exists (pipeline rule: tests first, against stable test IDs agreed in acceptance criteria).
> **Convention:** `data-testid="<screen>.<element>"`, lowercase, dot-separated, hyphens inside words. Repeated rows add `data-id="<entity id or code>"`. Changing a test ID is a breaking change: QA must approve it.

## 0. Global

| Element | Test ID | Notes |
|---|---|---|
| Bottom rail | `rail` | `<nav aria-label="Main">`; visible on home, move, search, rooms, room, place, box, item, history, account |
| Rail buttons | `rail.home`, `rail.search`, `rail.add`, `rail.scan`, `rail.rooms` | aria-labels: Home, Search, Add items, Scan a label, Rooms. Active has `aria-current="page"` |
| Toast | `toast` | `role=status` |
| Back / close | `header.back` / `header.close` | aria-label Back / Close / Cancel / Close scanner |
| Level label | `header.level` | Text is the level (HOME, ROOM, PLACE, BOX, ITEM…) |
| Home switcher trigger | `home-switcher.open` | aria-label "Switch home"; shows current home name |
| Add sheet | `add-sheet`, `add-sheet.voice`, `add-sheet.scan`, `add-sheet.new-box`, `add-sheet.start-move`, `add-sheet.pack`, `add-sheet.bulk`, `add-sheet.cancel` | `start-move` only when no move; `pack` only during a move |
| Homes sheet | `homes-sheet`, `homes-sheet.home[data-id]`, `homes-sheet.current`, `homes-sheet.add-move-home`, `homes-sheet.add-home`, `homes-sheet.cancel` | |
| PDF viewer | `pdf`, `pdf.filename`, `pdf.spec`, `pdf.tip`, `pdf.print`, `pdf.share`, `pdf.save`, `pdf.printed-ok`, `pdf.close` | `printed-ok` only for sheet PDFs |

## 1. Screens

| # | Screen (route suggestion) | Level label | Contents | Leads to | Key test IDs |
|---|---|---|---|---|---|
| S01 | **Home** `/` | HOME | Home switcher + name; account avatar; "Where's…?" bar; mic; moving card (conditional); tabs Changes / Looked for / Pinned / Lent out with badges; intro line; tab list; empty state | Search, Account, Move, Item, History | `home.search-bar`, `home.mic`, `home.account`, `home.move-card`, `home.tab.changes`, `home.tab.looked`, `home.tab.pinned`, `home.tab.lent`, `home.tab-badge`, `home.list`, `home.row[data-id]`, `home.row.undo`, `home.row.returned`, `home.full-history`, `home.empty` |
| S02 | **Search** `/search?q=` | (HOME switcher) | Back; search input "Find something"; mic; home switcher; LISTENING state; TRY chips; N RESULTS list; empty state | Item, Box, Place | `search.input`, `search.mic`, `search.listening`, `search.chip`, `search.result-count`, `search.result[data-id]`, `search.result.kind` (Box/Place/Qty), `search.empty` |
| S03 | **Rooms** `/rooms` | ROOMS | Home name; "N rooms · N items"; print-queue banner; room tiles; Add room | Room, Label sheet | `rooms.stat`, `rooms.queue-banner`, `rooms.tile[data-id]`, `rooms.tile.count`, `rooms.add` |
| S04 | **Room** `/r/<id>` | ROOM | Back; + (New box in this room); name; "N items · N containers"; groups per place (label + code → Place) with box/item rows; ANYWHERE IN group; New box in <Room> | Place, Box, Item, New box | `room.title`, `room.stat`, `room.group[data-id]`, `room.group.open`, `room.row[data-id]`, `room.anywhere`, `room.new-box` |
| S05 | **Place** `/c/P-xxxx` | PLACE (or ROOM for "Anywhere in") | Breadcrumb; title; code + Print place label; ITEMS HERE with steppers; BOXES HERE; Add by voice; New box here | Box, Item, Label, Voice, New box | `place.crumb`, `place.title`, `place.code`, `place.print-label`, `place.items`, `place.item[data-id]`, `place.item.dec`, `place.item.inc`, `place.item.qty`, `place.boxes`, `place.box[data-id]`, `place.voice`, `place.new-box`, `place.empty-items`, `place.empty-boxes` |
| S06 | **Box** `/c/B-xxxx` | BOX | Back; print icon; breadcrumb; name; code; label card (QR, "Scan to open this box", Print label); packed banner + Unpack; CONTENTS with steppers; BOXES INSIDE; Add by voice; More ways | Label, Voice, Unpack, Add sheet, child Box | `box.crumb`, `box.title`, `box.code`, `box.qr`, `box.print-label`, `box.packed-banner`, `box.unpack`, `box.contents`, `box.item[data-id]`, `box.item.dec`, `box.item.inc`, `box.item.qty`, `box.children`, `box.child[data-id]`, `box.voice`, `box.more`, `box.empty` |
| S07 | **Item** `/i/<id>` | ITEM | Back; pin star (`aria-pressed`); category; name; location card (box or pin icon, name·code, path); lent banner + Returned; QUANTITY panel; Move; Archive; HISTORY | Box/Place, Picker | `item.pin`, `item.category`, `item.title`, `item.location`, `item.lent-banner`, `item.returned`, `item.qty`, `item.dec`, `item.inc`, `item.move`, `item.archive`, `item.history`, `item.history-row`, `item.lend` *(new — lend action to design)* |
| S08 | **Picker** (overlay route) | MOVE TO / ADD TO | Cancel; question line; groups per room: "Anywhere in <Room>" + places/boxes with code and path; "Current" pill | Back to caller | `picker.title`, `picker.group[data-id]`, `picker.option[data-id]`, `picker.current` |
| S09 | **Add by voice** `/voice?dest=` | ADD BY VOICE | Close; ADDING TO dest + path/code; Change; LISTENING (pulse, live transcript, hint, Done); review: WHAT I HEARD, PARSED list with steppers, remove, duplicate banner + Merge, merged note; Record again; Add N items | Picker, destination | `voice.dest`, `voice.change`, `voice.listening`, `voice.transcript`, `voice.done`, `voice.heard`, `voice.parsed-count`, `voice.parsed[data-id]`, `voice.parsed.dec`, `voice.parsed.inc`, `voice.parsed.remove`, `voice.dup`, `voice.merge`, `voice.merged`, `voice.again`, `voice.confirm` |
| S10 | **Scan** `/scan` | SCAN A LABEL | Close; camera frame; sweep; prompt; FOUND card · Opening…; OR OPEN A RECENT LABEL chips | Box, Place, Unpack | `scan.viewport`, `scan.prompt`, `scan.found`, `scan.found.code`, `scan.recent[data-id]` |
| S11 | **Print label** `/c/<code>/label` | PRINT LABEL | Back; label preview; FORMAT (62 mm roll / A4 sheet); note; Create print PDF / Add to label sheet / Already on the sheet | PDF viewer, back | `label.preview`, `label.format.roll`, `label.format.a4`, `label.note`, `label.submit` |
| S12 | **New box** `/new-box?room=&place=` | NEW BOX | Cancel; NAME input + suggestion chips; WHERE IN <ROOM> chips (Anywhere + places); LABEL preview with next code; format Print now / Add to A4 sheet; note; Create | Label ready, Box | `new-box.name`, `new-box.suggestion`, `new-box.where[data-id]`, `new-box.code`, `new-box.preview`, `new-box.format.now`, `new-box.format.queue`, `new-box.create` |
| S13 | **Label ready** | LABEL READY | Close; tilted printed-label preview; "Stick it on the box"; instructions; Fill it by voice; Scan to check; Open the label PDF again | Voice, Scan, PDF, Box | `label-ready.preview`, `label-ready.voice`, `label-ready.scan`, `label-ready.reopen` |
| S14 | **Label sheet (queue)** `/labels/queue` | LABEL SHEET | "N labels ready"; "A4 sticker sheet · 24 per page · N spaces left"; 24-slot preview; ON THIS SHEET rows with remove; Create sheet PDF; Add another box | PDF viewer, New box | `queue.count`, `queue.free`, `queue.slot`, `queue.row[data-id]`, `queue.row.remove`, `queue.create-pdf`, `queue.add-box`, `queue.empty` |
| S15 | **Bulk import** `/import` | BULK IMPORT | Step 1: headline, Choose a CSV file drop area, Use the sample file, COLUMNS chips, explainer, Download template. Step 2: file card, summary sentence, PREVIEW rows with tag (New / New place / New box / Merge), Import N rows, Choose another file | Room | `import.choose`, `import.sample`, `import.template`, `import.columns`, `import.file`, `import.summary`, `import.row[data-row]`, `import.row.tag`, `import.submit`, `import.restart` |
| S16 | **History** `/history` | HISTORY | "Household activity"; rows with initial, subject, "detail · actor · when", Undo on latest undoable | — | `history.row[data-id]`, `history.row.actor`, `history.undo` |
| S17 | **Account** `/account` | ACCOUNT | Avatar, name, "Admin · <household>"; HOUSEHOLD members + roles + Invite someone; AI ACCESS (MCP) *(v1.1)*; LABELS formats, Nudge across/down, Alignment test sheet; APPEARANCE System/Light/Dark | PDF (test) | `account.name`, `account.members`, `account.invite`, `account.tokens` *(v1.1)*, `account.new-token` *(v1.1)*, `account.nudge-x.dec`, `account.nudge-x.inc`, `account.nudge-x.value`, `account.nudge-y.dec`, `account.nudge-y.inc`, `account.nudge-y.value`, `account.alignment-test`, `account.theme.system`, `account.theme.light`, `account.theme.dark` |
| S18 | **Start a move** `/move/new` | START A MOVE | Step N of 3 + progress; title per step; step 1 MOVING FROM + MOVING DAY chips; step 2 NAME FOR THE NEW HOME + ROOMS chips; step 3 box checklist with "→ Room" cycle chip, summary; Back/Cancel; Next / Start move with N boxes | Move | `start-move.step`, `start-move.from[data-id]`, `start-move.day`, `start-move.name`, `start-move.room[data-name]`, `start-move.box[data-id]`, `start-move.box.toggle`, `start-move.box.dest`, `start-move.summary`, `start-move.back`, `start-move.next` |
| S19 | **Moving house** `/move` | MOVING HOUSE | Route; Moving day; TO UNPACK panel + stat + segments; Pack a box; Scan to unpack; all-done banner + Finish move; FOR THE <ROOM> groups; UNPACKED list; finish confirmation; Finish move link | Pack, Scan, Unpack, Box | `move.route`, `move.day`, `move.left`, `move.stat`, `move.segment`, `move.pack`, `move.scan`, `move.all-done`, `move.group[data-id]`, `move.box[data-id]`, `move.unpacked[data-id]`, `move.finish`, `move.confirm`, `move.finish-anyway`, `move.not-yet` |
| S20 | **Pack a box** `/move/pack` | PACK A BOX | "For the move to <home>"; NAME + suggestions; GOING TO room chips; LABEL preview with FOR band; explainer; Create box and label PDF | Label ready | `pack.name`, `pack.suggestion`, `pack.room[data-id]`, `pack.preview`, `pack.for`, `pack.create` |
| S21 | **Unpack** `/move/unpack/<code>` | UNPACK | "Arrived at <home>"; name; code; LABELLED FOR band; INSIDE list; PUT IT IN room chips; Unpacked in the <room>; Keep it packed for now | Move | `unpack.title`, `unpack.code`, `unpack.for`, `unpack.items`, `unpack.room[data-id]`, `unpack.submit`, `unpack.keep` |

## 2. Screens not in the prototype (design needed)

| Screen | Why | Notes |
|---|---|---|
| Sign in / passkey / OIDC | Auth (O-02) | Plus test-only login |
| Invite accept / join household | FR-USR-01 | — |
| Add room / add place / add home | Prototype toasts "not in this demo" | Follow the New box pattern |
| Edit item (name, category, unit, tags, notes, photo) | FR-ITM-01 | — |
| Lend item ("Lend to…", since) | FR-LEND-01 | From item screen |
| Archived label scanned / unknown code | FR-LOC-10, FR-QR-02 | Actionable error with closest codes |
| Offline / server unreachable | PWA over VPN | Calm message; retry |
| Mic/camera permission denied | Voice/scan | Explain and offer typing / manual code entry |

## 3. Prototype behaviours worth keeping

- Back is a **stack**; rail tabs reset it.
- After confirming voice items, the app returns to the destination (or to the move screen if the box is packed).
- After importing, the app opens the affected room.
- Switching home resets room/box context to the new home and toasts.
- The Changes list includes **agent** actors (e.g. "Claude · Quantity set to 12 via MCP"), so the actor model must not assume humans only.
