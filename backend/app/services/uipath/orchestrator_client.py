"""UiPath Orchestrator REST API client with OAuth2 authentication."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)

_CLOUD_TOKEN_URL = "https://cloud.uipath.com/identity_/connect/token"


@dataclass
class UiPathConfig:
    """Connection configuration for a UiPath Orchestrator instance."""

    org_name: str
    tenant_name: str
    client_id: str
    client_secret: str
    folder_name: str
    process_key: str
    webhook_secret: str | None = None
    # Override base/token URLs for on-premise Orchestrator instances.
    base_url: str | None = None
    token_url: str | None = None

    @property
    def api_base(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        return f"https://cloud.uipath.com/{self.org_name}/{self.tenant_name}/orchestrator_"

    @property
    def resolved_token_url(self) -> str:
        return self.token_url or _CLOUD_TOKEN_URL


# Module-level token cache: cache_key → (token, expiry_monotonic)
_token_cache: dict[str, tuple[str, float]] = {}
_cache_lock: asyncio.Lock | None = None


def _get_cache_lock() -> asyncio.Lock:
    global _cache_lock
    if _cache_lock is None:
        _cache_lock = asyncio.Lock()
    return _cache_lock


async def get_access_token(config: UiPathConfig) -> str:
    """Acquire and cache an OAuth2 access token using client credentials flow."""
    cache_key = f"{config.client_id}@{config.resolved_token_url}"
    lock = _get_cache_lock()
    async with lock:
        cached = _token_cache.get(cache_key)
        if cached and time.monotonic() < cached[1]:
            return cached[0]

        async with httpx.AsyncClient(timeout=15) as http:
            response = await http.post(
                config.resolved_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                    "scope": "OR.Jobs OR.Queues OR.Webhooks.Write",
                },
            )
            response.raise_for_status()
            body = response.json()

        token: str = body["access_token"]
        expires_in = int(body.get("expires_in", 3600))
        _token_cache[cache_key] = (token, time.monotonic() + expires_in - 60)
        logger.debug(
            "uipath.auth.token_refreshed",
            extra={"client_id": config.client_id, "expires_in": expires_in},
        )
        return token


async def start_job(
    config: UiPathConfig,
    *,
    task_id: str,
    task_title: str,
    extra_input: dict[str, Any] | None = None,
) -> int:
    """Start a UiPath job for the configured process.

    Embeds ``task_id`` in the job's InputArguments so webhook callbacks can
    match the job back to the originating OpenClaw task.

    Returns the UiPath integer job ID.
    """
    token = await get_access_token(config)
    input_args: dict[str, Any] = {
        "in_task_id": task_id,
        "in_task_title": task_title,
        **(extra_input or {}),
    }
    url = (
        f"{config.api_base}/odata/Jobs"
        "/UiPath.Server.Configuration.OData.StartJobs"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitName": config.folder_name,
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "startInfo": {
            "ReleaseKey": config.process_key,
            "Strategy": "ModernJobsCount",
            "JobsCount": 1,
            "InputArguments": json.dumps(input_args),
        }
    }
    async with httpx.AsyncClient(timeout=30) as http:
        response = await http.post(url, json=body, headers=headers)
        response.raise_for_status()
        result = response.json()

    jobs: list[dict[str, Any]] = result.get("value", [])
    if not jobs:
        raise RuntimeError("UiPath returned no job records from StartJobs")

    job_id: int = jobs[0]["Id"]
    logger.info(
        "uipath.job.started",
        extra={
            "task_id": task_id,
            "uipath_job_id": job_id,
            "process_key": config.process_key,
        },
    )
    return job_id


async def register_webhook(
    config: UiPathConfig,
    *,
    callback_url: str,
    secret: str,
) -> int:
    """Register a webhook subscription in UiPath Orchestrator.

    Subscribes to ``job.completed``, ``job.faulted``, and ``job.stopped``
    events so OpenClaw receives status updates.

    Returns the UiPath webhook subscription ID.
    """
    token = await get_access_token(config)
    url = f"{config.api_base}/odata/Webhooks"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-UIPATH-OrganizationUnitName": config.folder_name,
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "Url": callback_url,
        "Enabled": True,
        "Secret": secret,
        "SubscribeToAllEvents": False,
        "AllowInsecureSsl": False,
        "Events": [
            {"EventType": "job.completed"},
            {"EventType": "job.faulted"},
            {"EventType": "job.stopped"},
            {"EventType": "job.started"},
        ],
    }
    async with httpx.AsyncClient(timeout=15) as http:
        response = await http.post(url, json=body, headers=headers)
        response.raise_for_status()
        result = response.json()

    webhook_id: int = result["Id"]
    logger.info(
        "uipath.webhook.registered",
        extra={
            "webhook_id": webhook_id,
            "callback_url": callback_url,
        },
    )
    return webhook_id
