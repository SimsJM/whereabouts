# Software factory — overview (Pi + Paperclip)

> v1.0 · 31 October 2026 · Decided 29 Oct (ADR-0008), confirmed 31 Oct. Replaces the Hermes Kanban pipeline (archived). Read with `loop.md`, `security.md`, `roles/*.md`, `packs/*.yaml`.
> Hostnames, CT IDs and network names are in `../../private/homelab.md`, not here.

## 1. Components

| Piece | What | Notes |
|---|---|---|
| **Harness** | **Pi** (pi.dev, `@earendil-works/pi-coding-agent`) | Minimal coding harness; per-project SYSTEM.md, on-demand skills, branchable sessions, 15+ providers |
| **Orchestrator** | **Paperclip** (paperclip.ing, `paperclipai`) with the built-in **`pi_local`** adapter | Agents run in heartbeats; Pi sessions resume via `--session`, scoped per agent; per-agent monthly budget cap; atomic task checkout; plan/approve gates; blocked-task inbox |
| **Host** | One unprivileged LXC; non-root `factory` user; no sudo | `pi_local` runs Pi on the same machine as Paperclip. Remote execution (Paperclip Runner) is experimental and doesn't list Ollama Cloud keys — don't plan around it |
| **Paperclip mode** | `authenticated` + `private`, systemd user service, reached over the VPN | Paperclip blocks plain HTTP; its own previews need Tailscale (not used here) → CI + homelab previews own previews |
| **Models** | Ollama Cloud (Pro, 3 concurrent), key separate from Hermes | Passed via `PAPERCLIP_PI_PROVIDERS` (systemd drop-in). `pi_local` requires an explicit model per agent |
| **GitHub** | Fine-grained PAT per repo, Paperclip secret, bound as `GH_TOKEN` + `GITHUB_TOKEN` (HTTPS) | Per-role scopes in §4; identity question O-06 |
| **Workspaces** | **Isolated**: one git worktree + branch per issue; every issue ends in a PR | Experimental in Paperclip → **pin the Paperclip version** |
| **Hermes** | Not in the factory | Jamie's personal assistant |

## 2. Company and projects

- One Paperclip **company: "Whereabouts"**, two **projects**, each its own repo and pack:
  - **Site** (pilot) — `SimsJM/whereabouts-site` (recommended; O-08).
  - **App** — `SimsJM/whereabouts`.
- One company per factory where hard separation is wanted; one project per repo.

## 3. Core + pack

**Rule: if it would change for a second project, it belongs in the pack, not the core.**

- **`factory-core` repo** (Gitea): `roles/{product,architect,developer,qa,support}.md`, `skills/`, `loop.md`, `defaults.yaml`, `bin/factory-apply`.
- **Project pack** in each repo: root `AGENTS.md` (stack and commands) + `.factory/factory.yaml` (roles on, model per tier, budgets, gates, environments).
- **`factory-apply <repo>`** (to build): reads defaults + pack; creates/updates the Paperclip project and workspace; builds one instructions file per role (core role + pack addition, passed via `instructionsFilePath`); creates `pi_local` agents with model, instructions path, secret refs and budget. **Idempotent**, with **`--dry-run`**.
- **Model tiers:** `build` (Developer, QA) and `review` (Product, Architect, Support). Each pack maps tier → model ID.
- **Role scope:** `company` roles have one agent shared across projects (Product, Support); `project` roles have one agent per project (Architect, Developer, QA), each with its own budget and repo instructions. Example: an app feature shipping makes Product create an "update the features page" issue on the site.

## 4. Roles, tools and credentials

Every role needs `bash`: agents call the Paperclip API with curl using the injected `PAPERCLIP_API_KEY`, `PAPERCLIP_API_URL`, `PAPERCLIP_AGENT_ID`, `PAPERCLIP_RUN_ID`.

| Role | Scope | Tier | Pi tools | Via bash | GitHub token |
|---|---|---|---|---|---|
| **Product** | company | review | read, grep, find, ls, bash | Paperclip API (issues, comments); `gh issue view` | Issues read-only |
| **Architect** | project | review | all | Paperclip API; push design notes/ADRs; `gh pr create/review` | Write |
| **Developer** | project | build | all | Paperclip API; install/build/test/lint; `git push`; `gh pr create/checks` | Write |
| **QA** | project | build | all | Paperclip API; tests and regression; push tests to PR; `gh pr checks/comment` | Write |
| **Support** | company | review | read, grep, find, ls, bash | Paperclip API; `gh issue list/view/comment`; run tests to reproduce | Issues read/write |

**The real enforcement is credentials, branch protection and the container — not Pi's tool list** (`pi_local` enables all tools by default).

Mapping from the retired Hermes roles: Triage → **Support**; Reviewer → **Architect** (PR review) + **Jamie** (required approval); Maintainer → scheduled **Developer** `maint/` issues.

## 5. Notifications

Paperclip's inbox (blocked tasks, approvals) is the primary channel. A lightweight alert channel (Telegram or Slack) is optional; Paperclip's outbound Slack notifications were experimental in October. Jamie must hear about: chains awaiting approval, blocked issues, Build issues ready to merge, `deploy-failure` issues (GitHub alerts).

## 6. Model candidates (verify against Ollama's current cloud catalogue — O-07)

| Use | Candidates from October research |
|---|---|
| `build` (Developer) | `kimi-k2.7-code` (long coding tasks) |
| `build` (QA) | `minimax-m3` (tool use for Playwright) |
| `review` (Architect) | `deepseek-v4-pro` (off-peak); or a frontier model (e.g. Claude Opus 5.5 via API) — Architect runs rarely but shapes everything |
| `review` (Product, Support) | `deepseek-v4.1-flash`, `glm-5.3`, `gemma4` (cheap, high volume) |

- Keep reviewing and building on **different labs** where possible, so blind spots differ.
- When Developer struggles on one issue, override the model **for that issue only**.
- Schedule batch work (backlog review, sweeps, maintenance) **outside 12:00–18:00 UTC on weekdays** (Ollama Cloud peak).
- Token efficiency: measure fixed prompt overhead; disable unused tools/skills; prune MCP tool schemas; avoid mid-session model switches (they reset the prompt cache); route sub-tasks to a cheaper model; compact deliberately; start fresh sessions per task with durable context in a lean `AGENTS.md`.

## 7. Pilot plan (site first)

Site pack: Developer + Product on; Architect, QA, Support off; `gates.merge: human`; nothing skips approval; nothing auto-deploys; `environments.preview: none`; prod = rebuilt container on the Caddy host, deployed by CI.

**Pilot passes when:** `factory-apply` works with **no core edits**; Product turns a request into a ticket; Developer ships **3 PRs Jamie would merge as-is**; a failed check comes back green without Jamie; budgets hold. Then switch on QA and start the app pack.

## 8. App phase-in

1. App pack with Architect, Developer, QA (Product shared from the site). First issues in `../product/roadmap.md` §3.
2. Dry-run the approval rule: an **unapproved/unassigned issue must never be picked up** — verify in Paperclip before relying on it.
3. Dry-run a trivial feature end to end (footer version string): QA failing tests → Developer PR → Architect review → checks green → Jamie merges.
4. Verify handoff metadata carries `issue`, `acceptance_criteria` (unchanged from the head issue), `branch`, `pr`.
5. Verify concurrency queues work beyond 3 Ollama requests.
6. Switch on Support once public issues start arriving.
7. After a clean month: allow auto-merge for low-risk confirmed bug fixes.

## 9. Open verification items (O-16)

- [ ] Do shared Pi skills load under `pi_local`? Paperclip swaps in a managed agent dir each run, so `~/.pi/agent` skills likely won't load.
- [ ] Confirm Paperclip reads `PAPERCLIP_PI_PROVIDERS` from the service process env.
- [ ] Ollama Cloud's OpenAI-compatible base URL and model IDs for `build`/`review`.
- [ ] Isolated workspaces are experimental → pin the Paperclip version.
- [ ] What `factory-apply` can do via the Paperclip CLI vs the API.
- [ ] Paperclip company export/import as a possible format for the core.
- [ ] How two sequential issues (QA then Developer) share one branch under isolated workspaces.
- [ ] How to block "done" until PR checks pass (old completion-contract behaviour).
- [ ] Per-PR previews stay with CI + homelab (Paperclip previews need Tailscale).

## 10. Reference

- Paperclip Pi adapter: https://docs.paperclip.ing/reference/adapters/pi/
- Paperclip + GitHub: https://docs.paperclip.ing/how-to/connect-agent-to-github/
- Paperclip workspaces: https://docs.paperclip.ing/guides/projects-workflow/workspaces/
- Paperclip company admin: https://docs.paperclip.ing/administration/company/
- Paperclip Runner: https://docs.paperclip.ing/reference/adapters/paperclip-runner/
- Claude.ai docs from 29 Oct (export to Markdown if needed; Claude Code can't open them): Runbook "Software factory" (homelab runbook) https://claude.ai/artifact/RpiVYXBGCq7mYcaWredQgJ · Spec "core and project pack" https://claude.ai/artifact/4LKGunWj7JAYARX3bUWmMX
