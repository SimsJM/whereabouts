# Home Inventory App — Competitor Analysis

> Copied verbatim from the project (26 September 2026). Written when the product was unnamed; "the proposed app" = Whereabouts. One recommendation is overridden: photo-to-inventory is **not** in v1 (see `../decision-log.md` D-20).

26 September 2026 · Jamie Sims

Live doc: https://claude.ai/code/artifact/d7793d24-c0bf-43a2-8094-664a6de67083

## Executive summary

The basics of home inventory are well served: nested locations, QR labels and photo-based capture are table stakes, and the low end of the market is crowded. The open ground is voice capture, private AI built into the product rather than bolted on, and AI agents that can safely write to the inventory.

- **Closest competitor:** Homebox, a free, self-hosted open-source app whose new data model matches the proposed location tree. AI reaches it only through third-party add-ons.
- **Closest concept:** HomeHoard, a Homebox rewrite with Home Assistant voice, an MCP server and item check-out. It is a single-developer project with 2 GitHub stars.
- **Consumer apps** (StuffID, Rorg, Shelver, SnapFind and others) compete on photo-to-inventory AI and cloud sync. Voice-first capture exists in only one app, SmartStow, on Android.
- **Strongest differentiators:** voice capture with a review step, transcription on the user's own server, agent write access made safe by an event log with undo, and print-ready A4 and roll labels.

**Recommendation:** position as a voice-first, private, AI-native household inventory for people who self-host, with moving house as the entry point. Keep the backend in-house rather than extending Homebox.

## Scope and method

The need assessed is simple: a household knows where everything is stored and can find it quickly, on a phone, by search or voice.

The proposed app has these characteristics:

- Self-hosted on Proxmox, with a mobile progressive web app (PWA).
- A nested location tree (room, location, container) with items at any level.
- Search and voice search, with speech transcribed by the household's own Whisper server.
- Adding items by voice, with a review screen before saving, plus bulk CSV import.
- QR labels for boxes and locations, produced as print-ready PDFs (62 mm roll and A4 24-up sheets).
- Multiple users per household, an event log with attribution and undo, and an MCP server for AI agents.

Competitors were identified through web research in September 2026, covering self-hosted projects, app-store listings, community MCP servers and business inventory tools used at home. Feature claims come from each product's own pages or repository and were not tested hands-on.

## Market landscape

The market splits into six segments. Self-hosted tools are the direct competition; the others set user expectations.

| Segment | Main players | Business model | Relevance |
| --- | --- | --- | --- |
| Self-hosted, open source | [Homebox](https://github.com/sysadminsmedia/homebox), [HomeHoard](https://github.com/Amantux/homehoard) | Free (AGPL-3.0); hosted Homebox at $9/month via [ElfHosted](https://store.elfhosted.com/product/homebox/) | Direct competitors for the same user |
| Add-ons to Homebox | [Homebox Companion](https://github.com/Duelion/homebox-companion), [homebox-mcp](https://pypi.org/project/homebox-mcp/) and other community MCP servers | Free, community-maintained | Show the demand for AI and agents; fragile |
| Consumer AI apps | [StuffID](https://apps.apple.com/us/app/ai-home-inventory-stuffid/id6762598494), [Rorg](https://apps.apple.com/eg/app/ai-home-inventory-rorg/id6759187513), [Shelver](https://apps.apple.com/us/app/-/id6756636954), [SnapFind](https://apps.apple.com/us/app/snapfind-home-inventory/id6740042892), [Vorby](https://vorby.com/), [ShelfLily](https://www.shelflily.com/) | Freemium, subscriptions, cloud | Set the bar for capture speed and polish |
| Voice-first | [SmartStow](https://www.alternativeto.net/software/smartstow/about/) | Subscription, $2–16/month, Android only | Only direct precedent for voice capture |
| Business tools used at home | [Sortly](https://clubofthings.app/blog/sortly-alternatives-free) | Free plan capped at 100 items; QR labels from $49/month | Price anchor; poor fit for households |
| Insurance-focused | [HomeZada](https://www.homezada.com/homeowners/home-inventory) | Subscription | Different job: documenting value, not finding things |

**Homebox** is the incumbent. It supports nested locations, photo and document uploads, CSV import and export, and QR labels. Its v0.26 release in June 2026 merged items and locations into a single "entity" structure and added an AR scanner that overlays a box's contents when the camera sees its QR code ([release notes](https://github.com/sysadminsmedia/homebox/releases/tag/v0.26.0)).

**HomeHoard** is the closest concept. It runs as a Home Assistant add-on, answers "where is my drill?" by voice, ships an in-container MCP server with 13 tools, and supports checking items in and out. Its agent tools deliberately exclude adding or deleting items.

## Feature comparison

The proposed app matches the incumbents on structure and labels, and leads on voice, agent safety and print output. It trails on photo-based capture.

| Capability | Proposed app | Homebox | HomeHoard | Consumer AI apps | Sortly | SmartStow |
| --- | --- | --- | --- | --- | --- | --- |
| Self-hosted | Yes | Yes | Yes | No | No | No |
| Nested locations and containers | Yes, any depth | Yes | Yes, with bins | Yes (e.g. Shelver: locations, boxes, items) | Folders | Items, containers, locations |
| QR labels | Yes, print-ready PDF: 62 mm roll, A4 24-up, calibration | Yes, sheets for Avery 5260 (US Letter) | Yes, several codes per object | Common (Shelver, ShelfLily) | Paid plans only, from $49/month | Not stated |
| Photo-to-inventory AI | Planned | Via Homebox Companion add-on | On roadmap | Core feature | Not found | Not found |
| Adding items by voice | Core, with review screen | No | No | SnapFind (voice and text add) | No | Core |
| Voice search | Yes, local Whisper | No | Yes, via Home Assistant Assist | Rare | No | Not stated |
| AI agent access (MCP) | Native, read and write, with undo | Community servers only | Built in; no add or delete | No | Not found | No |
| Household users | Yes, with attribution per change | Collections (groups) | Groups with invitations | Shared spaces (Shelver, SnapFind) | 1 user on free plan | Not stated |
| Check-out or "last seen" | Under consideration | Not found | Yes | Not found | Not found | Not found |
| Price | Free (own build) | Free | Free | Freemium | Free to $49+/month | $2–16/month |

"Not found" means the capability did not appear in the product's own materials; it may exist but is not promoted.

## How competitors meet the need

Most products solve retrieval well; the hard part they all fight is getting a household's belongings recorded in the first place.

- **Capture.** Photo recognition is the dominant answer. StuffID identifies every item in a photo of a shelf, drawer or pile; HomeZada and Rorg do the same. One industry guide notes that most people start a home inventory but never finish it, which is the problem AI capture targets ([Smart Home Admin](https://www.smarthomeadmin.com/blog/ai-home-inventory-apps/)). Voice capture appears only in SmartStow and, as a secondary input, in SnapFind.
- **Retrieval.** Every product offers text search. Homebox and HomeHoard show the full location path in results. HomeHoard adds fixed voice phrases through Home Assistant ("where is my drill?", "what's in the garage?") and full natural language when an LLM is connected.
- **Labelling.** QR codes that open a box's contents are standard. Homebox prints sheets formatted for Avery 5260; HomeHoard allows several codes per object; ShelfLily sells physical QR stickers and can make codes publicly readable. Sortly charges $49/month before QR labels can be printed.
- **AI and agents.** In the self-hosted world, AI is supplied by separate projects: Homebox Companion for photo cataloguing and chat, and at least five community MCP servers. Homebox's v0.26 release replaced its item and location API endpoints entirely, so each integration had to be rewritten. HomeHoard builds MCP in, but limits agents to searching, moving and editing.
- **Households.** Consumer apps share inventories across family members (Shelver, SnapFind). Homebox and HomeHoard support groups. None of the products reviewed promotes per-person attribution of changes or an undo history.

## Gaps and differentiation opportunities

Five gaps are open, and the proposed design already addresses each. The third is the hardest to copy.

| # | Gap | Evidence | How the proposed app differentiates |
| --- | --- | --- | --- |
| 1 | Voice capture while packing | Only SmartStow is voice-first; everyone else is photo-first, which suits open shelves but not a box being filled | Speak the contents, review a parsed list, confirm. Duplicates are flagged for merging |
| 2 | Private AI | Consumer apps process photos in the cloud; self-hosted AI comes from add-ons that broke with Homebox v0.26 | Transcription on the household's own Whisper server; data model and AI tools designed together |
| 3 | Safe agent write access | HomeHoard's MCP deliberately blocks adding and deleting; community servers expose raw create and delete calls | Every change logged with its actor, one-step undo, per-user tokens scoped to read or write, no hard deletes |
| 4 | Print quality for UK users | Homebox formats for Avery 5260, a US Letter sheet | Vector PDFs for 62 mm rolls and A4 24-up sheets, a print queue, and an alignment test with offset nudging |
| 5 | Design quality in self-hosted tools | Self-hosted tools are functional; one long-time Homebox user reports dates displaying a day early ([AlternativeTo](https://www.alternativeto.net/software/homebox/about/)) | A calm, glanceable mobile interface built for one-handed use |

The combination matters more than any single feature. No product reviewed combines voice capture, local processing and safe agent writes.

## Where the proposed app is behind

Three capabilities are expected by users who have tried competitors; two should be added and one deliberately left out.

| Capability | Who has it | Recommendation |
| --- | --- | --- |
| Photo-to-inventory | Consumer AI apps as a core feature; Homebox through Companion | Bring forward from v2. It covers what voice misses: open shelves and existing storage. It needs a cloud vision model, since the homelab has no GPU |
| Check-out or "last seen" | HomeHoard: one-tap check-out, who has it, due date | Add as an optional status, separate from an item's usual home. This settles the open "wandering items" question |
| Warranty, value and maintenance tracking | Homebox, HomeHoard, HomeZada | Leave out. It serves insurance documentation, a different job, and would dilute the "find it fast" focus |

## Strategic assessment and recommendations

As a commercial product this is a hard market; as a personal build with a possible open-source release, it has a clear and defensible niche.

**Market attractiveness.** Homebox is free and established, and consumer AI apps are cheap and numerous. Sortly shows households will not pay business prices. Paid demand would most likely come from moving house, where a one-off, high-pain task justifies effort.

**Positioning.** A voice-first, private, AI-native household inventory for people who self-host. The message: say what goes in the box, and ask your assistant where it went.

**Build or extend Homebox.**

| Option | For | Against |
| --- | --- | --- |
| Front end and AI layer on top of Homebox | Reuses a mature backend, label tools and import; Homebox's entity model now matches the location tree | Its API changes break integrations (v0.26 replaced the item and location endpoints); AGPL-3.0 licensing; no event log or undo to build safe agent writes on |
| Own backend (recommended) | Event log, attribution and undo designed in from the start; the MCP and data model evolve together | More to build: data layer, import, label generation |

**Recommendations**

1. Keep the backend in-house. The event log is the foundation of the strongest differentiator, safe agent writes.
2. Make moving house the launch scenario: voice capture while packing, label sheets, and scanning at the new home.
3. Add photo-to-inventory and check-out to the first release scope.
4. Offer CSV import that accepts Homebox exports, so switching costs little.
5. If releasing publicly, pursue Home Assistant integration early; HomeHoard shows it is the natural home for voice retrieval among self-hosters.

## Sources

- [Homebox repository (sysadminsmedia)](https://github.com/sysadminsmedia/homebox) and [v0.26.0 release notes](https://github.com/sysadminsmedia/homebox/releases/tag/v0.26.0)
- [HomeHoard repository](https://github.com/Amantux/homehoard)
- [Homebox Companion v3.0.0 release](https://github.com/Duelion/homebox-companion/releases/tag/v3.0.0)
- [homebox-mcp on PyPI](https://pypi.org/project/homebox-mcp/) and [community Homebox MCP server (jeeves5454)](https://github.com/jeeves5454/Homebox-mcp)
- [ElfHosted: hosted Homebox](https://store.elfhosted.com/product/homebox/)
- [MakeUseOf: Homebox on Raspberry Pi (Avery 5260 labels)](https://www.makeuseof.com/raspberry-pi-homebox-track-belongings-self-hosting/)
- [AlternativeTo: Homebox reviews](https://www.alternativeto.net/software/homebox/about/) and [SmartStow](https://www.alternativeto.net/software/smartstow/about/)
- App store listings: [StuffID](https://apps.apple.com/us/app/ai-home-inventory-stuffid/id6762598494), [Rorg](https://apps.apple.com/eg/app/ai-home-inventory-rorg/id6759187513), [Shelver](https://apps.apple.com/us/app/-/id6756636954), [SnapFind](https://apps.apple.com/us/app/snapfind-home-inventory/id6740042892)
- [Vorby](https://vorby.com/), [ShelfLily](https://www.shelflily.com/), [HomeZada](https://www.homezada.com/homeowners/home-inventory)
- [Club of Things: Sortly free plan limits 2026](https://clubofthings.app/blog/sortly-alternatives-free)
- [Smart Home Admin: Best AI home inventory apps (2026)](https://www.smarthomeadmin.com/blog/ai-home-inventory-apps/)
