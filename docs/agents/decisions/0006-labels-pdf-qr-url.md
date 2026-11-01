# 0006. Labels as server-side PDFs; QR encodes a URL to the code

- **Status:** Accepted · **Date:** 2026-10-02 · **Decided by:** Jamie

## Decision
Labels are always print-ready vector PDFs (62 × 29 mm roll; A4 24-up 63.5 × 33.9 mm; alignment test) generated on the server and handed to the phone's print/share sheet — no printer integration. QR codes encode `https://<app-host>/c/<code>`, never contents.

## Consequences
Works with any printer; UK-friendly (Homebox only does US Letter). Labels never go stale. Agents can request labels via MCP later. Needs calibration (nudge offsets) and a print queue that survives jams.
