# Hostinger Shared Hosting Recovery Reference

## Scope

Use this reference only for Hostinger shared-hosting incidents.

Validated on `2026-03-26`:

- Hostinger public API documents `/api/hosting/v1/websites` for website inventory and creation.
- Hostinger public API does not document shared-hosting file publish endpoints.
- SSH, SFTP, FTP, or hPanel file actions remain the practical publish paths for shared hosting.

## Fast diagnosis

1. Confirm the site is actually on shared hosting.
2. Check public DNS and HTTP behavior.
3. Compare the public response with the files already present in `public_html`.
4. If files are present but the public site serves Hostinger's generic 404 page, inspect `~/domains` permissions before redeploying.

## Incident signature

This pattern was observed on `marlow.dev.br` and `cltxpj.app.br` on `2026-03-26`:

- Hostinger API showed both websites as enabled.
- `public_html` already contained valid site files.
- Public requests returned Hostinger's generic `This Page Does Not Exist` page.
- The parent directory had the wrong mode:

```text
drw-r--r-- /home/<user>/domains
```

- Restoring traversal on the parent directory fixed both sites:

```bash
chmod 711 ~/domains
```

- After the fix, both domains returned `HTTP/2 200` without republishing.

## Safe permission model

Recommended for the shared-hosting parent path:

```text
~/domains -> 711
```

Why:

- owner keeps full access
- webserver or hosting runtime can traverse the path
- directory listings are not broadly exposed

Avoid:

- `644` on directories: breaks traversal
- `777`: unnecessary and unsafe
- `chmod -R` across the whole hosting tree unless you are doing a deliberate repair with a full backup and a precise reason

## Minimal command set

Inspect:

```bash
ssh -p 65002 user@host 'ls -ld ~ ~/domains ~/domains/example.com ~/domains/example.com/public_html'
ssh -p 65002 user@host 'ls -la ~/domains/example.com/public_html | sed -n "1,80p"'
```

Fix:

```bash
ssh -p 65002 user@host 'chmod 711 ~/domains && ls -ld ~/domains'
```

Verify:

```bash
curl -I -L --max-time 20 https://example.com
curl -sS https://example.com | rg -n '<title>|This Page Does Not Exist|Hostinger'
```

Publish with rsync:

```bash
rsync -avz --delete \
  -e "ssh -p 65002" \
  ./ user@host:~/domains/example.com/public_html/
```

## Recovery choices

If permissions are wrong:

- fix permissions first
- re-test before republishing

If files are missing or stale:

- publish from the repository or built artifact
- prefer the repo's existing deploy workflow if one already exists

If SSH shell is restricted:

- try SFTP/FTP
- use hPanel File Manager if needed

## Notes for OpenClaw

- Treat shared-hosting recovery as a shell-driven workflow, not an API deploy workflow.
- Prefer short, high-signal summaries:
  - root cause
  - command used
  - final HTTP status
  - whether files were changed
