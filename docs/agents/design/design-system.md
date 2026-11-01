# Whereabouts — Design system

> v1.0 · 31 October 2026 · Source of truth for UI. Values are extracted from the clickable prototype (`prototype/home-inventory-demo.html`) and the spec's look-and-feel section. Machine-readable tokens: `tokens.json` and `tokens.css`. Icons: `icons.svg`.
> **Stack-agnostic:** the frontend stack is not yet chosen (ADR-0002). Implement these tokens as CSS custom properties whatever the stack.

## 1. Design intent

Modelled on the **Land Rover Defender Pivi Pro** centre console (reference photo shared by Jamie in the original design chat — not in this pack; ask Jamie if needed):

- Warm neutral panels: cream/stone in light mode, charcoal/warm grey in dark mode.
- **One** muted bronze accent. No other hues except fixed print/scanner surfaces.
- Letter-spaced UPPERCASE labels in the accent sit above one large, calm hero value.
- Thin line icons (~1.25 px stroke).
- At most **three actions per panel**.
- Calm, glanceable, one-handed. Generous spacing, few borders, hairline separators.
- Every screen's header **names its level** (HOME, ROOM, PLACE, BOX, ITEM) so the hierarchy reads the same everywhere.

## 2. Colour

### 2.1 Theme tokens

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#EFEBE4` | `#171614` | App background, sheets, rail |
| `--panel-a` | `#F8F5EF` | `#22201D` | Primary panel (search bar, label card, quantity panel, review card) |
| `--panel-b` | `#F3EFE7` | `#1E1C1A` | Alternate room tile |
| `--panel-c` | `#EDE7DC` | `#262420` | Label preview backdrop, third room tile |
| `--text` | `#26231F` | `#EEE9E0` | Primary text, icons |
| `--muted` | `#6A6258` | `#A69E92` | Secondary text, sub-lines, chevrons |
| `--accent` | `#7A5B32` | `#C8A471` | Bronze accent: labels, primary buttons, active tab, links |
| `--on-accent` | `#FBF8F2` | `#1A1815` | Text/icon on accent fills |
| `--line` | `#D8D0C3` | `#3A3631` | Hairlines, outlines, inactive borders |
| `--flag-bg` | `#F1E6D3` | `#2E2820` | Soft highlight banners (moving card, packed, lent, duplicate, queue), "Current" pill |

Room tiles cycle `panel-a → panel-b → panel-c`.

### 2.2 Fixed surfaces (same in both themes)

| Token | Value | Use |
|---|---|---|
| `--scan-bg` | `#11100E` | Scanner screen |
| `--scan-frame` | `#1C1A17` | Camera viewport |
| `--scan-card` | `#22201D` | "FOUND" card |
| `--scan-chip-line` | `#3A3631` | Chips on scanner |
| `--scan-accent` | `#C8A471` | Corner frame, sweep line, labels on scanner |
| `--scan-text` / `--scan-muted` | `#EEE9E0` / `#A69E92` | Scanner text |
| `--pdf-bg` | `#2A2825` | PDF viewer overlay |
| `--pdf-tip-bg` / `--pdf-tip-text` | `#36312A` / `#E2C79C` | Print tip banner |
| `--pdf-btn-line` | `#4A453F` | Secondary buttons in PDF viewer |
| `--label-paper` | `#FFFFFF` | Label/sticker surfaces |
| `--label-ink` | `#1A1815` | QR modules, label text, "FOR <ROOM>" band background |
| `--label-ink-muted` | `#4A453F` | Path line on labels |
| `--label-placeholder` | `#8A8278` | Placeholder name on label preview |
| `--label-band-muted` | `#C8C0B4` | "FOR" / "LABELLED FOR" caption on the black band |
| `--sheet-slot-line` | `#DDD6CA` / `#E8E2D8` | A4 slot outlines (queue / PDF) |
| `--test-mark` | `#9A9186` | Alignment-test slot outline |
| `--scrim` | `rgba(20,18,16,0.45)` | Behind bottom sheets |
| Prototype desktop backdrop | `#D9D3C9` (body), `#1C1B19` (phone bezel), text `#2F2B26`, notes `#5F584F` | Demo framing only — not app tokens |

### 2.3 Rules

- Accent is for **one primary action per area** plus labels. Secondary actions are outlined (`--line`) or text links in accent.
- Contrast: verify AA for `--muted` on `--panel-*` in both themes when implementing (light `#6A6258` on `#EDE7DC` is the tightest pair).
- Theme: **System / Light / Dark** setting; System follows `prefers-color-scheme`.

## 3. Typography

- **Family:** `Jost` (free stand-in; Land Rover's typeface is proprietary). Fallbacks: `'Futura', 'Century Gothic', sans-serif`.
- **Weights:** 300 (light — headings, hero values, inputs), 400 (body), 500 (labels, buttons, codes).
- **Self-host** the woff2 files (as the website does). No Google Fonts at runtime.

| Role | Size / weight | Letter-spacing | Example |
|---|---|---|---|
| Hero number | 48 / 300 (qty), 38 / 300 (room tile count) | — | `24` |
| Page title (h1) | 34–36 / 300, line-height 1.1 | — | "Toolbox" |
| Section title | 28–30 / 300 | — | "Household activity", "Main house" on Rooms |
| Sub-title / input | 22 / 300 (inputs, card titles), 20 / 300 (home name, search bar) | — | "Where's…?" |
| Item row title | 16–17 / 400 | — | "Allen key set" |
| Body | 15 / 400 | — | Toast-length copy |
| Secondary | 13–14 / 400, `--muted` | — | "Garage › Shelf 2 › Toolbox" |
| Caption | 12 / 400, `--muted` | — | Category under item |
| **Level label** | 11 / 500, `--accent`, UPPERCASE | **0.32em** (headers), 0.28em (section labels) | `BOX`, `CONTENTS` |
| Sub-label | 11 / 400, `--muted`, UPPERCASE | 0.24em | `ADDING TO`, `LABEL` |
| Listening | 12 / 500, accent | 0.4em | `LISTENING` |
| Code | 13 / 500, accent | 0.24em | `B-0042` |
| Code on label | 22–24 / 500, ink | 0.08em | `B-0042` |
| "FOR <ROOM>" band | 22 / 500, white on ink | 0.12em | `FOR KITCHEN` |
| Tab | 13 / 500 active, 400 inactive | — | `Changes` |

Centre-aligned letter-spaced labels add `padding-left` equal to the tracking so they optically centre.

## 4. Spacing, size and shape

- **Base canvas:** 390 × 844 (phone). Screen side padding **24 px**; header bar side padding 12 px.
- **Vertical rhythm:** sections separated by 20–28 px; label-to-content 8–10 px.
- **Touch targets:** minimum **44 × 44 px**. Icon buttons 44 px; primary pill buttons **52 px** tall; chips 44 px (36 px for suggestion chips); list rows ≥ 56–64 px.
- **Radii:** panels/banners **4 px**; labels/stickers 6 px; bottom sheets **16 px** top corners; pills = height ÷ 2 (52→26, 48→24, 44→22); progress segments 2 px; badges 9 px.
- **Separators:** 1 px `--line` on the top of each list row (`border-top`), never boxed lists.
- **Elevation:** none in-app except label previews (`0 1px 3px rgba(0,0,0,0.12)`; printed label `0 2px 8px rgba(0,0,0,0.14)`, rotated −2°) and PDF pages (`0 6px 20px rgba(0,0,0,0.45)`).
- **Header bar:** 56 px (search: 64 px) — Back (left), LEVEL LABEL (centre), one action or spacer (right).
- **Bottom rail:** 84 px with 10 px bottom padding.

## 5. Iconography

- 24 × 24 viewBox, `fill="none"`, `stroke="currentColor"`, **stroke-width 1.25** (1.5 on icons inside filled accent buttons; 2.5 for the checkbox tick), round caps and joins.
- Rendered at 14–30 px. Decorative icons get `aria-hidden="true"`; the button gets the `aria-label`.
- The full set is in `icons.svg` as `<symbol>`s: `home, search, plus, scan, rooms, mic, chevron-left, chevron-right, chevron-down, close, box, pin, print, star, move-arrow, archive, upload, file, van, check, minus, info`.

## 6. Components

| Component | Spec |
|---|---|
| **Level header** | Back icon button · centred LEVEL label (11/500/0.32em accent) · optional right icon (print, +, star) |
| **Home header** | Left: HOME label over home name (20/300) + chevron-down → opens home switcher. Right: 44 px circular avatar (initial) outlined `--line` → Account |
| **Search bar (home)** | 64 px pill, `--panel-a`, 1 px line, search icon + "Where's…?" (20/300 muted); beside it a 64 px **accent circle mic** |
| **Search field (search screen)** | Underlined input (18/300), Back left, accent mic right; HOME switcher below |
| **Tabs** | `role=tablist`; equal-width 48 px tabs; active: text colour, weight 500, 2 px accent bottom border; badge = 18 px accent pill with count |
| **List row** | Title (16) + sub (13 muted) + optional right text (13 muted) + chevron-right (16, muted); optional leading box/pin icon (22) |
| **Stepper row** | Name + category, − (44) · qty (17, 28 px wide) · + (44) |
| **Quantity panel** | `--panel-a`, QUANTITY label, 52 px outlined − / + around a 48/300 number |
| **Primary button** | 52 px pill, accent fill, on-accent text 15/500, optional 20 px icon (stroke 1.5). Disabled = 50 % opacity |
| **Secondary button** | 52 px pill, 1 px `--line`, text colour 15/400 |
| **Outlined accent button** | 52 px pill, 1 px accent border, accent text ("New box in Garage") |
| **Text link** | Accent 14/500, 44–48 px tall, left aligned; in lists it carries a top hairline |
| **Choice chip** | 44 px pill; off: 1 px line, transparent; on: accent fill + on-accent text; `aria-pressed` |
| **Suggestion chip** | 36 px pill, 1 px line, muted 13 px |
| **Banner** | `--flag-bg`, 4 px radius, accent text, optional icon + right-aligned action ("Make PDF", "Unpack", "Returned", "Merge") |
| **Moving card** | `--flag-bg` button: MOVING · ROUTE label + chevron, 22/300 title, segmented progress (6 px; 8 px on move screen) — accent = unpacked, line = packed |
| **Room tile** | 156 px tall, 2-column grid, gap 12; ROOM label top, 38/300 count bottom, "items · N containers". "Add room" tile = 1 px dashed line |
| **Label preview** | White card 290 px wide: QR (80–104 px) + code (22–24/500) + name (16) + path (12, ink-muted). Move variant adds the black "FOR <ROOM>" band |
| **A4 sheet preview** | 3 × 8 grid of slots; filled = mini QR + code; empty = dashed outline |
| **Bottom sheet** | Scrim + `--bg` sheet, 16 px top radius, 36 × 4 grab handle, section label, 68 px option rows (24 px accent icon + title 17 + sub 13), Cancel secondary button |
| **Toast** | Centred pill, inverted colours (`--text` bg, `--bg` text), 14 px, `role=status`, auto-hide **2.6 s**, 100 px above bottom when rail visible (else 32 px) |
| **Avatar initial** | 36 px circle, 1 px line, initial 14 px (history rows); 64 px accent outline on Account |
| **"Current" pill** | `--flag-bg` + accent 12 px, radius 12 |
| **Listening indicator** | 88–104 px circle (outlined or filled accent) with two pulsing rings (1.6 s, second delayed 0.8 s) |
| **Scanner frame** | 280 px square, 40 px accent corner brackets (2 px), sweeping 1 px accent line (2.4 s) |
| **Bottom rail** | Home · Search · raised **+** (58 px accent-outlined circle) · Scan · Rooms. Active = accent, else text colour |

## 7. Motion

- `pulse` (listening): scale 1 → 1.8, opacity 0.6 → 0, 1.6 s ease-out, infinite; second ring offset 0.8 s.
- `sweep` (scanner): top 10 % → 88 % → 10 %, 2.4 s ease-in-out, infinite.
- Toast fade only. No page transitions required.
- **`prefers-reduced-motion: reduce` disables pulse and sweep.**

## 8. Language, terminology and copy

- **British English** ("colour", "dialogue", "archived", "organise").
- **Never show "location"** in the UI. Use the level names: **Home, Room, Place, Box**, and "Anywhere in <Room>" for room-level items. Use "Move to…", "Where is it?", "Where's…?".
- A **Place** is a shelf, wardrobe, drawer unit, hook, windowsill etc. ("Spot" and "Unit" were rejected.)
- Codes are shown exactly: `B-0042`, `P-0003`.
- Paths use ` › ` between levels and omit the home (`Garage › Shelf 2 › Toolbox`). Breadcrumbs above titles use double-spaced `  ›  `. Label paths use ` · `.
- Counts pluralise correctly ("1 box", "2 boxes", "1 item").
- Tone: calm, short, helpful. Toasts confirm what happened and where ("Moved to Toolbox", "3 items added to Toolbox", "Undone: Picture hooks is back in Drawer 1").
- Empty states say what to do next (see `requirements.md` FR-HOME-06 and screen inventory).
- Known copy fixes from the prototype: bulk import "Rooms, **places** and boxes that don't exist yet are created for you"; preview tag **"New place" / "New box"** instead of "New location".

## 9. Accessibility checklist

- Every icon-only button has an `aria-label` (see screen inventory for the agreed labels).
- Inputs have `<label>` (visually hidden where needed, `.sr` pattern).
- Tabs: `role=tablist`, `role=tab`, `aria-selected`. Toggles/chips: `aria-pressed`. Toasts: `role=status`. Rail: `<nav aria-label="Main">`.
- Focus ring: `outline: 2px solid var(--accent); outline-offset: 2px` on `:focus-visible`.
- 44 px targets; no hover-only affordances.
- QR previews in the UI are `role="img"` with an `aria-label`; real labels always print the human-readable code.

## 10. Labels (print design)

See `../architecture/labels-and-printing.md` for geometry. Visual rules: white paper, ink `#1A1815`, QR left, code large and letter-spaced, name below, path smallest. Move labels add a full-width black band with "FOR" caption and the destination room in 22/500 uppercase — big enough for whoever carries the box.
