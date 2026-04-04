---
name: Home Lab Mission Control Setup
description: Design and operational record for the home lab MC instance — gateways, org structure, skills, and pending connectivity fixes
type: project
date: 2026-03-28
---

# Home Lab Mission Control Setup

## Context

Mission Control running locally on Mac (`localhost:3000 / :8000`), accessible from the home lab via Tailscale. Three OpenClaw gateway containers run on the home lab machine (`100.87.245.64`), each owning a distinct operational domain.

| Host | Role | Tailscale IP |
|------|------|-------------|
| Mac | Mission Control (MC) | `100.118.205.4` |
| Home lab | OpenClaw gateways | `100.87.245.64` |

---

## Network and Auth

### Critical settings (already applied)

| Setting | File | Value |
|---------|------|-------|
| `BASE_URL` | `backend/.env` | `http://100.118.205.4:8000` |
| `DB_AUTO_MIGRATE` | `.env` (root) | `false` (multiple Alembic heads fixed manually) |
| `LOCAL_AUTH_TOKEN` | `.env` (root) | set (≥80 chars) |
| `AUTH_MODE` | `.env` (root) | `local` |

### Auth flow

```
MC backend → gateway WebSocket  : uses Gateway Token (per gateway)
Gateway agent → MC API          : uses X-Agent-Token (per agent, written by MC into gateway files)
Browser → MC API                : uses LOCAL_AUTH_TOKEN as Bearer
```

---

## Org Structure (Personal)

Org ID: `17fabfb6-6441-4057-a0df-495a0d00cc1b`

### Board Groups and Boards

| Group | Gateway | Boards |
|-------|---------|--------|
| Release Ops | openclaw | CI/CD Pipeline, Infrastructure, Security & Compliance, Monitoring & Alerts |
| Marketing | openclaw-clone | Content Creation, Social Media, Campaigns, Analytics |
| AI and ML Engineering | openclaw-clone-2 | Model Training, Data Pipeline, Experiments, Model Deployments |

### Tags (13)

`urgent` · `high-priority` · `medium-priority` · `low-priority` · `bug` · `feature` · `research` · `blocked` · `security` · `infra` · `release-ops` · `marketing` · `ai-ml`

### Custom Fields (6, applied to all 12 boards)

| Key | Label | Visibility |
|-----|-------|-----------|
| `priority` | Priority | always |
| `environment` | Environment | always |
| `effort` | Effort Estimate | always |
| `due_date` | Due Date | always |
| `owner_team` | Owner Team | if_set |
| `external_ref` | External Ref | if_set |

---

## Gateway Reference Table

| Field | openclaw | openclaw-clone | openclaw-clone-2 |
|-------|----------|----------------|-----------------|
| **Domain** | Release Ops | Marketing | AI and ML Eng |
| **Container** | `openclaw` | `openclaw-clone` | `openclaw-clone-2` |
| **Gateway URL** | `ws://100.87.245.64:18789` | `ws://100.87.245.64:18790` | `ws://100.87.245.64:18791` |
| **Gateway Token** | `ded832759a2aaf8b7833fb2d1f3e2052b3f4b7bd71277d7e` | `e9154100996a3220efc97d09391ac6c20d66c3f7e54e9464` | `fab202309600cfe6aa7e97d3d1320e3431f3d9121984168b` |
| **Workspace Root** | `~/.openclaw` | `~/.openclaw` | `~/.openclaw` |
| **MC Access Token** | `LOCAL_AUTH_TOKEN` (see `.env`) | same | same |
| **Telegram Bot Token** | `8754261392:AAERU68Y…` (see env) | TBD | TBD |
| **Telegram Channel** | TBD | TBD | TBD |

> **Note:** Telegram Bot Token is sensitive — keep in container env vars, not in task text or prompts.

---

## Skill Packs Registered

| Pack | Source | Purpose |
|------|--------|---------|
| superpowers | `github.com/obra/superpowers` | Workflow e processo para agentes |
| wolram/skills | `github.com/wolram/skills` | Skills pessoais — home lab e automação |
| antigravity-awesome-skills | `github.com/sickn33/antigravity-awesome-skills` | 800+ skills agenticos |
| ai-marketing-skills | `github.com/BrianRWagner/ai-marketing-skills` | Marketing frameworks |

> **Pending:** "50 do openclaw" — confirmar repo URL. Packs precisam de Sync no MC UI → Skills → Packs.

---

## Open Items

### 1. Gateway agents stuck in PROVISIONING

**Root cause:** Gateway agent process (inside Docker container on home lab) não consegue atingir `http://100.118.205.4:8000`. O `curl` funciona do host mas não foi testado de dentro do container — a interface Tailscale pode não estar acessível via bridge network.

**Fix candidates:**
- Rodar `docker exec openclaw curl -sf http://100.118.205.4:8000/healthz` para confirmar
- Se falhar: mudar os containers do home lab para `--network=host` ou configurar rota Tailscale dentro do container
- Alternativa: expor MC via IP local do Mac na mesma rede do home lab

### 2. OpenClaw official 50 skills

**Status:** URL do repo desconhecida. Pode estar incluída no `antigravity-awesome-skills` ou ser um repo separado.

**Action:** Confirmar com o usuário ou checar `sickn33/antigravity-awesome-skills` após sync para ver se as skills oficiais do OpenClaw estão lá.

### 3. Skill pack sync

**Status:** 4 packs registrados, nenhum sincronizado ainda.

**Action:** MC UI → Skills → Packs → Sync em cada pack (ou via API `POST /api/v1/skills/packs/{id}/sync`).

### 4. Telegram channel IDs

**Status:** Bot token de `openclaw` confirmado. Channels e tokens de `openclaw-clone` e `openclaw-clone-2` pendentes.

### 5. Alembic multiple heads

**Status:** Resolvido manualmente com `alembic upgrade heads`. `DB_AUTO_MIGRATE=false` aplicado no `.env` raiz.

**Long-term:** Criar migration de merge para unificar os heads no repositório.
