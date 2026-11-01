# 0007. Voice: own Whisper + cloud transcript parser

- **Status:** Accepted · **Date:** 2026-10-03 · **Decided by:** Jamie

## Decision
Audio is transcribed by the household's own Whisper server (Wyoming); the browser speech API is not used (Android sends audio to Google). Only transcript → structured items needs an LLM; with no GPU this calls a configurable cloud model (text only). Duplicate flagging, search and name suggestions use non-LLM methods. A **review screen** always precedes saving.

## Consequences
Private by default; a model change is config only, so local inference can come later (a GPU purchase is not planned; it would mainly matter for photo-to-inventory). Tests use recorded audio/transcripts and canned parser responses.
