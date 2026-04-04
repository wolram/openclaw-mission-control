---
name: hostinger-shared-hosting-recovery
description: Use when a website on Hostinger shared hosting returns the generic Hostinger 404 page, serves the wrong content, or needs manual recovery through SSH, SFTP, FTP, or rsync. Prefer this skill for shared-hosting incidents where the public API can list websites but cannot publish files.
---

# Hostinger Shared Hosting Recovery

Use this skill for recovery and publish work on Hostinger shared-hosting websites.

Do not use it for Hostinger VPS Docker Manager projects. Use `hostinger-vps-deploy` there instead.

Validated against Hostinger public docs and a real shared-hosting incident on `2026-03-26`.

## Before acting

Confirm these values first:

- domain name
- Hostinger username
- SSH host and port, or FTP/SFTP host and port
- one working credential path: SSH private key, SSH password, or FTP password
- publish source: GitHub repository, local directory, or built artifact

Then identify the hosting mode:

- if `/api/vps/v1/virtual-machines` is empty and `/api/hosting/v1/websites` contains the domain, treat it as shared hosting
- if the site is on VPS, stop and switch to `hostinger-vps-deploy`

## Workflow

1. Check the public symptom first with `curl -I -L` and a quick HTML sample.
2. Confirm whether the domain resolves to Hostinger and whether the response is the generic `This Page Does Not Exist` page.
3. SSH into the hosting account and inspect the parent path plus the domain `public_html`.
4. If `public_html` has the expected files but the public site still returns the generic Hostinger 404, inspect `~/domains` permissions before redeploying anything.
5. If `~/domains` is missing execute permission for path traversal, restore the minimal safe mode with `chmod 711 ~/domains`.
6. Re-test the public domain immediately after the permission fix.
7. Only publish files after verification shows content is missing, stale, or wrong.
8. Prefer `rsync` or the repository's existing FTP deploy workflow for shared-hosting publish operations.

## Guardrails

- Do not promise full shared-hosting deploy automation through the Hostinger public API. The public API currently documents inventory and website creation, not file publish endpoints.
- Never run `chmod -R` on the hosting account unless the user explicitly asks for a broad permission reset.
- Prefer `chmod 711 ~/domains` over `755` when the goal is only to restore directory traversal without exposing directory listings.
- Do not use `777`.
- Announce that changing `~/domains` affects every domain under the same shared-hosting account.
- Verify the exact target path before syncing files:
  - `~/domains/<domain>/public_html/`
- If the repository already has a deploy workflow, prefer triggering or fixing that workflow rather than inventing a second publish path.

## What good output looks like

Return:

- whether the issue was DNS, content, or permissions
- which path and permission were corrected
- whether a publish was required
- the final public HTTP status
- the next safe action if the site is still wrong

## Command examples

Check the public symptom:

```bash
curl -I -L --max-time 20 https://example.com
curl -sS https://example.com | rg -n '<title>|This Page Does Not Exist|Hostinger'
```

Inspect the shared-hosting paths:

```bash
ssh -p 65002 user@host 'ls -ld ~ ~/domains ~/domains/example.com ~/domains/example.com/public_html'
ssh -p 65002 user@host 'ls -la ~/domains/example.com/public_html | sed -n "1,80p"'
```

Repair the parent traversal permission:

```bash
ssh -p 65002 user@host 'chmod 711 ~/domains && ls -ld ~/domains'
```

Publish only when needed:

```bash
rsync -avz --delete \
  -e "ssh -p 65002" \
  ./ user@host:~/domains/example.com/public_html/
```

Verify recovery:

```bash
curl -I -L --max-time 20 https://example.com
curl -sS https://example.com | sed -n '1,20p'
```

## References

Load only when needed:

- [`references/shared-hosting-recovery.md`](references/shared-hosting-recovery.md)
