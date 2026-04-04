# Hostinger Shared Hosting Recovery

This runbook covers manual recovery for websites hosted on Hostinger shared hosting.

Use it when a domain resolves to Hostinger but serves the generic `This Page Does Not Exist` page, serves stale content, or needs a direct shared-hosting publish path.

## What this runbook is for

Validated on `2026-03-26`:

- Hostinger public API documents shared-hosting website inventory at `/api/hosting/v1/websites`
- Hostinger public API does not document file publish endpoints for shared hosting
- recovery work therefore happens through SSH, SFTP, FTP, rsync, or hPanel

## Typical incident pattern

1. Domain resolves and responds from Hostinger CDN.
2. Public response is the generic Hostinger 404 page.
3. The domain `public_html` already contains valid site files.
4. The parent `~/domains` directory has the wrong permissions and blocks traversal.

Minimal fix:

```bash
ssh -p 65002 user@host
chmod 711 ~/domains
```

Then verify:

```bash
curl -I -L --max-time 20 https://example.com
```

## Recommended OpenClaw skill

Use the example skill at [`examples/skills/hostinger-shared-hosting-recovery/SKILL.md`](../../examples/skills/hostinger-shared-hosting-recovery/SKILL.md).

That skill is meant to:

- distinguish shared hosting from VPS
- diagnose DNS vs content vs permissions
- repair the `~/domains` traversal problem safely
- publish with `rsync` only when a publish is actually needed

## Guardrails

- Do not use `chmod -R` unless there is a specific, approved repair plan.
- Prefer `711` on `~/domains` when the issue is path traversal.
- Do not use `777`.
- Remember that `~/domains` is shared by every domain under that hosting account.
