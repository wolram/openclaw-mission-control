#!/usr/bin/env python3
"""Minimal Hostinger VPS Docker Manager helper for OpenClaw skills."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "https://developers.hostinger.com/api"


@dataclass(frozen=True)
class HostingerConfig:
    base_url: str
    token: str
    vps_id: str | None
    project_name: str | None


def _fail(message: str, *, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def _read_text_file(path_value: str) -> str:
    return Path(path_value).read_text(encoding="utf-8")


def _resolve_required(
    cli_value: str | None,
    env_name: str,
    *,
    label: str,
) -> str:
    value = cli_value or os.getenv(env_name)
    if value and value.strip():
        return value.strip()
    raise ValueError(f"{label} is required; set --{label.replace(' ', '-')} or {env_name}")


def _resolve_optional(cli_value: str | None, env_name: str) -> str | None:
    value = cli_value or os.getenv(env_name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _build_config(args: argparse.Namespace, *, require_vps: bool, require_project: bool) -> HostingerConfig:
    token = _resolve_required(args.token, "HOSTINGER_API_TOKEN", label="API token")
    vps_id = None
    project_name = None
    if require_vps:
        vps_id = _resolve_required(args.vps_id, "HOSTINGER_VPS_ID", label="VPS id")
    else:
        vps_id = _resolve_optional(args.vps_id, "HOSTINGER_VPS_ID")
    if require_project:
        project_name = _resolve_required(
            args.project_name,
            "HOSTINGER_PROJECT_NAME",
            label="project name",
        )
    else:
        project_name = _resolve_optional(args.project_name, "HOSTINGER_PROJECT_NAME")
    return HostingerConfig(
        base_url=(args.base_url or os.getenv("HOSTINGER_API_BASE_URL") or DEFAULT_BASE_URL).rstrip("/"),
        token=token,
        vps_id=vps_id,
        project_name=project_name,
    )


def _request_json(
    config: HostingerConfig,
    *,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    body = None
    headers = {
        "Authorization": f"Bearer {config.token}",
        "Content-Type": "application/json",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url=f"{config.base_url}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with request.urlopen(req) as response:
            raw = response.read().decode("utf-8")
            if not raw.strip():
                return {"ok": True, "status": response.status}
            return json.loads(raw)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {"error": raw or exc.reason}
        raise RuntimeError(
            f"Hostinger API {method} {path} failed with {exc.code}: {json.dumps(detail, ensure_ascii=True)}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(f"Hostinger API request failed: {exc.reason}") from exc


def _print_json(payload: Any) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


def _payload_for_deploy(args: argparse.Namespace) -> dict[str, Any]:
    sources_selected = sum(
        1
        for value in (
            bool(args.compose_file),
            bool(args.content_url),
            bool(args.content),
        )
        if value
    )
    if sources_selected > 1:
        raise ValueError("choose only one of --compose-file, --content-url, or --content")

    if args.compose_file:
        content = _read_text_file(args.compose_file)
    elif args.content_url:
        content = args.content_url
    elif args.content:
        content = args.content
    else:
        env_content_url = os.getenv("HOSTINGER_PROJECT_CONTENT_URL", "").strip()
        if env_content_url:
            content = env_content_url
        else:
            raise ValueError(
                "deploy requires compose content; pass --compose-file, --content-url, --content, "
                "or set HOSTINGER_PROJECT_CONTENT_URL"
            )

    payload: dict[str, Any] = {
        "project_name": _resolve_required(
            args.project_name,
            "HOSTINGER_PROJECT_NAME",
            label="project name",
        ),
        "content": content,
    }

    if args.environment_file:
        payload["environment"] = _read_text_file(args.environment_file)
    elif args.environment:
        payload["environment"] = args.environment
    else:
        env_value = os.getenv("HOSTINGER_PROJECT_ENV", "").strip()
        if env_value:
            payload["environment"] = env_value

    return payload


def _add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", help="Hostinger API base URL")
    parser.add_argument("--token", help="Hostinger API token")
    parser.add_argument("--vps-id", help="Hostinger VPS id")
    parser.add_argument("--project-name", help="Docker project name")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("list-vms", "list-websites"):
        cmd = subparsers.add_parser(name)
        _add_shared_arguments(cmd)

    for name in (
        "list-projects",
        "get-project",
        "get-logs",
        "update",
        "restart",
        "start",
        "stop",
        "delete",
        "list-actions",
    ):
        cmd = subparsers.add_parser(name)
        _add_shared_arguments(cmd)
        if name == "list-actions":
            cmd.add_argument("--page", type=int, default=1, help="Actions page number")

    action = subparsers.add_parser("get-action")
    _add_shared_arguments(action)
    action.add_argument("--action-id", required=True, help="Hostinger action id")

    deploy = subparsers.add_parser("deploy")
    _add_shared_arguments(deploy)
    deploy.add_argument("--compose-file", help="Path to docker-compose.yaml")
    deploy.add_argument("--content-url", help="Raw URL or GitHub repository URL")
    deploy.add_argument("--content", help="Inline docker-compose.yaml text")
    deploy.add_argument("--environment", help="Inline environment variables")
    deploy.add_argument("--environment-file", help="Path to env file to send as environment")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list-vms":
            config = _build_config(args, require_vps=False, require_project=False)
            return _print_json(
                _request_json(config, method="GET", path="/vps/v1/virtual-machines"),
            )

        if args.command == "list-websites":
            config = _build_config(args, require_vps=False, require_project=False)
            return _print_json(
                _request_json(config, method="GET", path="/hosting/v1/websites"),
            )

        if args.command == "deploy":
            config = _build_config(args, require_vps=True, require_project=False)
            payload = _payload_for_deploy(args)
            return _print_json(
                _request_json(
                    config,
                    method="POST",
                    path=f"/vps/v1/virtual-machines/{config.vps_id}/docker",
                    payload=payload,
                ),
            )

        if args.command == "list-projects":
            config = _build_config(args, require_vps=True, require_project=False)
            return _print_json(
                _request_json(
                    config,
                    method="GET",
                    path=f"/vps/v1/virtual-machines/{config.vps_id}/docker",
                ),
            )

        if args.command == "get-project":
            config = _build_config(args, require_vps=True, require_project=True)
            return _print_json(
                _request_json(
                    config,
                    method="GET",
                    path=f"/vps/v1/virtual-machines/{config.vps_id}/docker/{config.project_name}",
                ),
            )

        if args.command == "get-logs":
            config = _build_config(args, require_vps=True, require_project=True)
            return _print_json(
                _request_json(
                    config,
                    method="GET",
                    path=(
                        f"/vps/v1/virtual-machines/{config.vps_id}/docker/"
                        f"{config.project_name}/logs"
                    ),
                ),
            )

        if args.command == "list-actions":
            config = _build_config(args, require_vps=True, require_project=False)
            return _print_json(
                _request_json(
                    config,
                    method="GET",
                    path=f"/vps/v1/virtual-machines/{config.vps_id}/actions?page={args.page}",
                ),
            )

        if args.command == "get-action":
            config = _build_config(args, require_vps=True, require_project=False)
            return _print_json(
                _request_json(
                    config,
                    method="GET",
                    path=f"/vps/v1/virtual-machines/{config.vps_id}/actions/{args.action_id}",
                ),
            )

        if args.command in {"update", "restart", "start", "stop"}:
            config = _build_config(args, require_vps=True, require_project=True)
            return _print_json(
                _request_json(
                    config,
                    method="POST",
                    path=(
                        f"/vps/v1/virtual-machines/{config.vps_id}/docker/"
                        f"{config.project_name}/{args.command}"
                    ),
                ),
            )

        if args.command == "delete":
            config = _build_config(args, require_vps=True, require_project=True)
            return _print_json(
                _request_json(
                    config,
                    method="DELETE",
                    path=(
                        f"/vps/v1/virtual-machines/{config.vps_id}/docker/"
                        f"{config.project_name}/down"
                    ),
                ),
            )

    except ValueError as exc:
        return _fail(str(exc))
    except FileNotFoundError as exc:
        return _fail(f"file not found: {exc.filename}")
    except RuntimeError as exc:
        return _fail(str(exc), code=1)

    return _fail(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
