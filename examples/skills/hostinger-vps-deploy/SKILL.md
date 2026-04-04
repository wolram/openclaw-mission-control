---
name: hostinger-vps-deploy
description: Use when the task is to deploy, update, restart, inspect, or troubleshoot a website or application running on Hostinger VPS Docker Manager. Prefer this skill for Hostinger VPS projects deployed from docker-compose content, raw URLs, or GitHub repository sources. Do not use it for Hostinger shared-hosting website publishing because the public API currently documents website list and create operations, but not file publish endpoints.
---

# Hostinger VPS Deploy

Use this skill for Hostinger VPS deploy operations through the public API.

## Before acting

Confirm these values first:

- `HOSTINGER_API_TOKEN`
- `HOSTINGER_VPS_ID`
- `HOSTINGER_PROJECT_NAME` or an explicit project name from the user

Then identify the deploy source:

- raw `docker-compose.yaml` content
- raw URL to a compose file
- GitHub repository URL

If the request is about Hostinger shared hosting, stop and explain that the public API does not document file publish endpoints there. You may still help with planning, builds, inventory, or handoff steps.

## Workflow

1. Prefer the bundled helper script at [`scripts/hostinger_vps.py`](scripts/hostinger_vps.py) for all API operations.
2. Read [`references/hostinger-api.md`](references/hostinger-api.md) only when you need endpoint details or to debug request shapes.
3. Validate API access before changing anything.
4. For a new deploy or full redeploy, create the project with the Docker Manager `POST /docker` endpoint.
5. For a routine refresh, use the project `update` endpoint.
6. After every change, verify project state and inspect logs if anything looks off.
7. Report the action id and current state back to the user.

## Guardrails

- Treat Hostinger Docker Manager endpoints as experimental because the official docs mark them that way.
- Prefer immutable image tags or a pinned compose revision for production deploys.
- Never print the API token.
- Do not delete a project with the `down` endpoint unless the user explicitly asks for removal.
- If the repository uses `main` instead of `master`, do not assume Hostinger's bare GitHub repository URL import will work. Use a raw compose URL or inline compose content instead.

## What good output looks like

Return:

- what changed
- which Hostinger endpoint was used
- the action id and action state
- the current project status
- the next safe action if verification fails

## Script examples

Validate access:

```bash
python3 scripts/hostinger_vps.py list-vms
```

Deploy from a compose file:

```bash
python3 scripts/hostinger_vps.py deploy --compose-file docker-compose.yaml
```

Refresh an existing project:

```bash
python3 scripts/hostinger_vps.py update
python3 scripts/hostinger_vps.py get-project
python3 scripts/hostinger_vps.py get-logs
```
