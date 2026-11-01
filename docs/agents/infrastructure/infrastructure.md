# Whereabouts — Infrastructure (public-safe)

> v1.0 · 31 October 2026. **This file is safe for the public repo/wiki**: it uses placeholders (`<app-host>`, `<preview-domain>`, `<prod-host>`) instead of real hostnames, IPs or network names. Real values live in `../../private/homelab.md` (keep that in a private repo — e.g. Jamie's Gitea "fleet" repo — never in `SimsJM/whereabouts`).

## 1. Environments

| Environment | Where | Data | Purpose | Who deploys |
|---|---|---|---|---|
| **Local dev** | Developer workspace (factory worktree) | Fresh SQLite + seed fixtures | Build and unit/e2e tests | Developer agent |
| **CI regression** | GitHub-hosted runners | Fresh SQLite per run, seeded fixtures, fakes, test login | Required checks on every PR and merge-queue run | GitHub Actions (`pr.yml`) |
| **Preview** (per PR) | Isolated homelab **preview host**, `pr-<n>.<preview-domain>` | Own SQLite volume, seeded fixtures, test login, no secrets | Jamie clicks through from his phone before merging | `preview.yml` (self-hosted `preview` runner, `main`'s workflow definitions only) |
| **Production** | Homelab **prod host**, `<app-host>` | Real household data on ZFS | Daily use | `deploy.yml` (self-hosted `prod` runner, on push to `main`) |

There is no separate long-lived "QA" environment: QA happens **before merge** in CI and previews (the Oct 6 decision replaced the original "deploy to QA, run regression, then prod" idea).

## 2. Hosting shape

- Homelab: **Proxmox** cluster with **ZFS** storage, segmented network, internal DNS, a VPN for remote access, an existing Caddy reverse proxy and a Whisper (Wyoming) voice pipeline. No GPUs (CPU-only nodes). Specifics: `../../private/homelab.md`.
- **App:** one container from `ghcr.io/simsjm/whereabouts:tree-<hash>`, pinned by digest, running in an LXC (Docker inside), data volume on a ZFS dataset that is snapshotted.
- **TLS:** HTTPS is mandatory (camera/mic). Production cert via Let's Encrypt **DNS challenge** for an internal hostname resolved by the homelab DNS. Previews: Caddy internal CA (root trusted on Jamie's devices) or DNS-challenge certs (O-14).
- **Access:** app reachable only over the VPN by default. MCP (v1.1) exposed only on the AI-agent network segment.
- **Voice:** app → Whisper server on the homelab (audio stays local). Transcript → cloud parser (text only).
- **Backups:** ZFS snapshot before every production deploy; scheduled snapshots of the data dataset; restore drill before launch.

## 3. Hosts and isolation rules

| Host role | Runs | Must never |
|---|---|---|
| **Factory** (one unprivileged LXC) | Paperclip + Pi agents as non-root `factory` user | Hold deploy credentials; host a self-hosted deploy runner |
| **Preview host** (isolated) | `preview` runner, caddy-docker-proxy, preview stacks | Hold production credentials; mount the Docker socket into app containers; reach the rest of the network (firewalled) |
| **Prod host** | `prod` runner, production stack | Run PR or preview workflows |
| **Personal Hermes** | Jamie's personal assistant | Do factory work (D-22) |
| **Website host** | `whereabouts-site` + Watchtower behind existing Caddy | Be the production deploy runner |

Each self-hosted runner sits in its own runner group restricted to its workflows. Repository setting: **require approval before running workflows from fork PRs**.

## 4. Container hardening (preview template, mirror in prod)

```yaml
services:
  app:
    image: ghcr.io/<owner>/whereabouts:${IMAGE_TAG}
    environment:
      APP_ENV: preview
      DATABASE_URL: sqlite:////data/whereabouts.db
      SEED_FIXTURES: demo
      TEST_LOGIN: "on"
    volumes: [data:/data]
    networks: [caddy]
    mem_limit: 512m
    cpus: 1.0
    read_only: true
    tmpfs: [/tmp]
    labels:
      caddy: pr-${PR_NUMBER}.${PREVIEW_DOMAIN}
      caddy.reverse_proxy: "{{upstreams 8000}}"
      caddy.tls: internal
volumes:
  data:
networks:
  caddy:
    external: true
```

Port and variable names are placeholders until the app's configuration is settled (Architect). Production uses `deploy/prod/compose.yml` with `APP_ENV=production`, `TEST_LOGIN` absent, secrets from the `production` environment.

## 5. Observability (proposed)

- `/healthz` endpoint (used by Docker health check and smoke test).
- Structured logs to stdout; `docker logs` / homelab log stack.
- `deploy-failure` GitHub issues on failed deploys; GitHub alerts Jamie.

## 6. Cost

- Models: Ollama Cloud Pro (3 concurrent requests). Analyses on 3–4 Oct concluded it beats buying a GPU or renting a VPS (e.g. Hostinger) at this scale.
- Parser model: low volume (a few calls per voice add).
- Hosting: existing homelab; GHCR for images.
