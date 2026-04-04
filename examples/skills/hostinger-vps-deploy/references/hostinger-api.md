# Hostinger API Reference For VPS Deploys

Use the public Hostinger API base URL:

```bash
BASE_URL="https://developers.hostinger.com/api"
AUTH_HEADER="Authorization: Bearer $HOSTINGER_API_TOKEN"
JSON_HEADER="Content-Type: application/json"
```

Bundled helper:

```bash
python3 scripts/hostinger_vps.py --help
```

Prefer the helper for routine operations. Use the raw API examples below when you need to inspect or debug the exact requests.

## Connectivity and inventory

List VPS instances:

```bash
curl -sS -X GET \
  "$BASE_URL/vps/v1/virtual-machines" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

List shared-hosting websites:

```bash
curl -sS -X GET \
  "$BASE_URL/hosting/v1/websites" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Important:

- `/hosting/v1/websites` is useful for inventory and website creation.
- The public API docs do not currently document file publish endpoints for shared-hosting websites.

## Create or replace a Docker project on VPS

Deploy from raw compose content:

```bash
jq -n \
  --arg project "$HOSTINGER_PROJECT_NAME" \
  --rawfile compose docker-compose.yaml \
  '{project_name: $project, content: $compose}' |
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" \
  --data @- | jq
```

Deploy from a raw compose URL:

```bash
jq -n \
  --arg project "$HOSTINGER_PROJECT_NAME" \
  --arg content "$HOSTINGER_PROJECT_CONTENT_URL" \
  '{project_name: $project, content: $content}' |
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" \
  --data @- | jq
```

Deploy from a GitHub repository URL:

```bash
jq -n \
  --arg project "$HOSTINGER_PROJECT_NAME" \
  --arg content "https://github.com/OWNER/REPO" \
  '{project_name: $project, content: $content}' |
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" \
  --data @- | jq
```

Important:

- Hostinger documents repository URL deploys as resolving `docker-compose.yaml` from the `master` branch.
- If the repository uses `main`, prefer a raw compose URL or inline compose content.

Optional environment payload:

```json
{
  "project_name": "my-project",
  "content": "https://example.com/docker-compose.yaml",
  "environment": "APP_ENV=production\nAPI_BASE_URL=https://api.example.com"
}
```

## Inspect current state

List projects:

```bash
curl -sS -X GET \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Get one project:

```bash
curl -sS -X GET \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Get project logs:

```bash
curl -sS -X GET \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME/logs" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

## Lifecycle operations

Update a project:

```bash
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME/update" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Restart a project:

```bash
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME/restart" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Start a project:

```bash
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME/start" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Stop a project:

```bash
curl -sS -X POST \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME/stop" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Delete a project permanently:

```bash
curl -sS -X DELETE \
  "$BASE_URL/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/docker/$HOSTINGER_PROJECT_NAME/down" \
  -H "$AUTH_HEADER" \
  -H "$JSON_HEADER" | jq
```

Only use the delete operation when the user explicitly asks to remove the project.
