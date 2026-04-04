# Hostinger Deploy Agent

This runbook explains how to operate Hostinger deployments through OpenClaw Mission Control.

## What is supported today

Validated against Hostinger public API docs and OpenAPI `0.11.7` on `2026-03-26`:

- `Hosting: Websites` supports listing and creating websites with `/api/hosting/v1/websites`.
- The public API does not document file publish or deploy endpoints for shared-hosting websites.
- `VPS: Docker Manager` supports deploying and operating Docker Compose projects on VPS instances through `/api/vps/v1/virtual-machines/{virtualMachineId}/docker`.

Practical consequence:

- For Hostinger shared hosting, Mission Control can help with planning, build prep, and inventory, but the final publish step must use some other flow such as FTP, Git deploy, or manual hPanel actions.
- For Hostinger VPS, Mission Control can drive real deploy workflows through the public API.

## Recommended architecture

Use this layout when you want OpenClaw to own the deploy loop:

1. Run Mission Control as your control plane.
2. Connect one OpenClaw gateway that has network access to the Hostinger API.
3. Store Hostinger credentials in the gateway runtime environment, not in Mission Control prompts.
4. Install a Hostinger VPS deploy skill onto that gateway.
5. Create one board per site or service so approvals, logs, and operator prompts stay isolated.

## Gateway prerequisites

On the machine that runs the OpenClaw gateway:

- `curl`
- `jq`
- `python3`
- `HOSTINGER_API_TOKEN`
- `HOSTINGER_VPS_ID`
- `HOSTINGER_PROJECT_NAME`

Optional but useful:

- `HOSTINGER_PROJECT_CONTENT_URL`
- `HOSTINGER_PROJECT_ENV`

Notes:

- Mission Control installs gateway skills into `<workspace_root>/skills`.
- `workspace_root` should match the OpenClaw runtime workspace root when possible.
- Do not put the Hostinger token directly into task text. Keep it in environment variables and let the gateway use shell environment resolution.

## Mission Control setup

1. Start Mission Control and sign in as an org admin.
2. Create a gateway with the correct WebSocket URL, token, and workspace root.
3. Verify connectivity on the gateway status screen before creating boards.
4. Add a board for the site or service you want to operate.
5. Install the example skill in [`examples/skills/hostinger-vps-deploy/SKILL.md`](../../examples/skills/hostinger-vps-deploy/SKILL.md) by publishing that folder in a GitHub repository and registering its tree URL in the marketplace.
6. Use the bundled helper at [`examples/skills/hostinger-vps-deploy/scripts/hostinger_vps.py`](../../examples/skills/hostinger-vps-deploy/scripts/hostinger_vps.py) for deterministic API calls from the gateway.

## Deploy workflow

Use Hostinger VPS for automated deploys.

### First deploy or redeploy

- Create or replace the project with `POST /api/vps/v1/virtual-machines/{virtualMachineId}/docker`.
- Send `project_name` plus `content`.
- `content` may be raw compose YAML, a raw URL, or a GitHub repository URL.

Important:

- Hostinger documents repository URL deploys as resolving `docker-compose.yaml` from the `master` branch.
- If your repository uses `main`, prefer a raw file URL or inline compose content instead of the bare repository URL.

### Routine update

- Use `POST /api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/update`.
- After the action is accepted, inspect logs and current project state.

### Verification

- List projects with `GET /api/vps/v1/virtual-machines/{virtualMachineId}/docker`.
- Inspect one project with `GET /api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}`.
- Fetch recent logs with `GET /api/vps/v1/virtual-machines/{virtualMachineId}/docker/{projectName}/logs`.

### Rollback

Use one of these safe patterns:

- redeploy a previous compose file revision
- redeploy a previous image tag
- keep immutable tags per release and point the compose content back to the last known good version

Avoid relying on `latest` if you want predictable rollbacks.

## Shared-hosting fallback

If your site is on Hostinger shared hosting instead of VPS:

- use OpenClaw to prepare the build, artifact, checklist, and DNS/domain verification
- use `/api/hosting/v1/websites` only for inventory or website creation
- finish publishing through whatever non-public-API path you already use
- for incident recovery and permission-related 404s, use [`examples/skills/hostinger-shared-hosting-recovery/SKILL.md`](../../examples/skills/hostinger-shared-hosting-recovery/SKILL.md) and the runbook at [`docs/operations/hostinger-shared-hosting-recovery.md`](./hostinger-shared-hosting-recovery.md)

Do not promise full deploy automation for shared hosting through the current public API surface.

## Example operator prompts

- `Deploy the current compose project to Hostinger VPS, then show me the action id and current project state.`
- `List current Hostinger VPS projects and tell me which one maps to the production site.`
- `Update the Hostinger project, inspect the last logs, and summarize any errors.`
- `Prepare a rollback to the previous image tag but do not execute it until I approve.`
