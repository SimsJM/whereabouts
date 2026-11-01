# Whereabouts — Labels, QR codes and printing

> v1.0 · 31 October 2026 · Requirements FR-LBL-*, FR-QR-*. Design rules in `../design/design-system.md` §10.

## 1. Principles

- **Output is always a print-ready PDF**, handed to the phone's print/share sheet. No printer drivers or direct printer integration.
- PDFs are generated **server-side** (WeasyPrint or ReportLab — O-12) so an agent can request labels via MCP later.
- **Vector** QR codes and text, **embedded fonts** (Jost). Sharp at any printer resolution.
- The **box/place record exists before** its label prints.

## 2. QR content

- Encodes a URL to the code, never the contents: `https://<app-host>/c/B-0042` (`PUBLIC_BASE_URL` + `/c/` + code). Labels therefore never go stale.
- Error correction level **M** or higher (labels get scuffed). [Architect: confirm vs. size]
- Human-readable code printed beside the QR as a fallback.
- The phone camera opens the URL directly; the in-app scanner decodes the same URL (or a bare code) and navigates internally.

## 3. Formats

| Format | Page | Label | Layout | File name |
|---|---|---|---|---|
| **Roll** | 62 × 29 mm, one label per page | 62 × 29 mm | QR left (~22 mm), code, name, path | `label-B-0042.pdf` |
| **A4 sheet** | 210 × 297 mm | **24-up, 63.5 × 33.9 mm** (3 columns × 8 rows) | Mini QR + code + name per slot; unused positions **left blank** so part-used sheets can be reused | `label-sheet-5-labels.pdf` |
| **Alignment test** | A4 | Outlines of all 24 positions with a centre cross | Print on plain paper, hold against a label sheet to the light | `alignment-test.pdf` |
| **Move label** | Roll (and sheet) | As roll + full-width black band "FOR <ROOM>" | Room large so the carrier knows where it goes | `label-B-0063.pdf` |

**[Architect]** confirm A4 sheet margins and pitch for the common UK 24-up 63.5 × 33.9 mm sheet (e.g. top/bottom margin ≈ 13 mm, side ≈ 7 mm, column gap ≈ 2.5 mm) and document them as constants with a test.

## 4. Print queue

- "Add to A4 sheet" adds the location to `label_queue`.
- "Create sheet PDF" renders the first 24 queued labels.
- The queue is cleared **only** when the user taps **"Printed OK: clear these from the queue"** — a paper jam never loses labels.
- Removing a row from the queue is allowed; adding one already queued says "<code> is already on the sheet".

## 5. Calibration

- Settings › Labels: **Nudge across** and **Nudge down** in **0.5 mm** steps (display "+0.5 mm", "−1.0 mm"), stored per household, applied to every sheet PDF (and the test sheet).
- PDF viewer spec line notes any nudge ("Nudged +0.5 mm across, 0.0 mm down.").
- Viewer reminder on every label PDF: **"Print at 100% (actual size). Turn off "Fit to page" or the QR codes will shrink."**
- Test sheet tip: "If the marks sit off-centre, adjust the nudge settings and print the test again."

## 6. Events

- Single label: `label.printed` ("Label B-0042 · Label PDF made").
- Sheet: `label.sheet_printed` on Printed OK ("Label sheet · Printed 5 labels").
- New box: `location.created` ("Created as B-0063 · label PDF made" / "· label queued").

## 7. Tests (QA)

- Golden-file tests: page size exactly 62 × 29 mm / A4; label rectangles at the documented positions ± 0.1 mm; nudge shifts every rectangle by the offset.
- Decode every QR in a generated PDF (rasterise → decode) and assert the URL.
- Fonts embedded (no system-font fallback in the PDF).
