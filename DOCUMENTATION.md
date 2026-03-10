# Session documentation

Decisions and changes made during development.

## 2026-03-09: Run at boot and auth token re-sync

### Goal

- Allow Mission Control (local install, no Docker, e.g. in a VM) to run at boot via systemd (Linux) or launchd (macOS).
- Document how to re-sync auth tokens between Mission Control and OpenClaw when they have drifted.

### Implemented

1. **Systemd unit files** (`docs/deployment/systemd/`)
   - Added example units: `openclaw-mission-control-backend.service`, `openclaw-mission-control-frontend.service`, `openclaw-mission-control-rq-worker.service`.
   - Units use placeholders `REPO_ROOT`, `BACKEND_PORT`, `FRONTEND_PORT`; install instructions and a small README explain substitution and install to `~/.config/systemd/user/` or `/etc/systemd/system/`.
   - RQ worker is required for gateway lifecycle and webhooks; it is a separate unit.

2. **Deployment docs** (`docs/deployment/README.md`)
   - Replaced placeholder with a short deployment guide.
   - "Run at boot (local install)": Linux (systemd) with link to `systemd/README.md`; macOS (launchd) with example plist and `launchctl load`; Docker Compose note for `restart: unless-stopped`.

3. **Troubleshooting** (`docs/troubleshooting/gateway-agent-provisioning.md`)
   - New subsection "Re-syncing auth tokens when Mission Control and OpenClaw have drifted": when tokens drift, run template sync with `rotate_tokens=true` via API (curl) or CLI (`scripts/sync_gateway_templates.py --rotate-tokens`); after sync, wake/update gateway if needed.

4. **install.sh** (`install.sh`)
   - New optional flag `--install-service` (local mode only): on Linux, copies the three systemd unit files from `docs/deployment/systemd/`, substitutes `REPO_ROOT`/ports, installs to `$XDG_CONFIG_HOME/systemd/user` (or `~/.config/systemd/user`), runs `systemctl --user daemon-reload` and `systemctl --user enable`. On non-Linux, prints a note pointing to `docs/deployment/README.md` for launchd. Not prompted by default; only when the user passes `--install-service`.

### Rationale

- **No Docker in VM**: User runs local install in a VM and does not want Docker there; run-at-boot is provided by the OS (systemd/launchd).
- **Units as examples**: Units are in `docs/deployment/systemd/` so they can be versioned and copied; install.sh only installs when `--install-service` is given to avoid touching system/LaunchAgents without explicit opt-in.
- **Auth re-sync**: Token drift is a common failure mode; documenting the API and CLI with `rotate_tokens=true` in the provisioning troubleshooting doc makes recovery easy to find.
