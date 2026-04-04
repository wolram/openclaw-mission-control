"""Bidirectional sync between OpenClaw tasks and UiPath Orchestrator jobs."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from uuid import UUID

from app.core.logging import get_logger
from app.core.time import utcnow
from app.models.gateways import GATEWAY_TYPE_UIPATH, Gateway
from app.services.uipath.orchestrator_client import UiPathConfig, start_job

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.models.tasks import Task

logger = get_logger(__name__)

# Map UiPath job State → OpenClaw task status.
# "Faulted" and "Stopped" map to "done" because OpenClaw has no "failed" status;
# callers can inspect the UiPath dashboard for failure details.
_UIPATH_STATE_TO_TASK_STATUS: dict[str, str] = {
    "Pending": "inbox",
    "Running": "in_progress",
    "Successful": "done",
    "Faulted": "done",
    "Stopped": "done",
}


def uipath_config_from_gateway(gateway: Gateway) -> UiPathConfig | None:
    """Build a ``UiPathConfig`` from a Gateway row.

    Returns ``None`` when the gateway is not UiPath-type or is missing required fields.
    """
    if gateway.gateway_type != GATEWAY_TYPE_UIPATH:
        return None
    missing = [
        f
        for f in (
            "uipath_org_name",
            "uipath_tenant_name",
            "uipath_client_id",
            "uipath_client_secret",
            "uipath_folder_name",
            "uipath_process_key",
        )
        if not getattr(gateway, f, None)
    ]
    if missing:
        logger.warning(
            "uipath.sync.config_incomplete",
            extra={"gateway_id": str(gateway.id), "missing_fields": missing},
        )
        return None

    return UiPathConfig(
        org_name=gateway.uipath_org_name,  # type: ignore[arg-type]
        tenant_name=gateway.uipath_tenant_name,  # type: ignore[arg-type]
        client_id=gateway.uipath_client_id,  # type: ignore[arg-type]
        client_secret=gateway.uipath_client_secret,  # type: ignore[arg-type]
        folder_name=gateway.uipath_folder_name,  # type: ignore[arg-type]
        process_key=gateway.uipath_process_key,  # type: ignore[arg-type]
        webhook_secret=gateway.uipath_webhook_secret,
    )


async def push_task_to_uipath(
    gateway: Gateway,
    *,
    task_id: str,
    task_title: str,
) -> bool:
    """Start a UiPath job representing an OpenClaw task.

    Embeds ``task_id`` in the job's input arguments so that incoming webhooks
    can be matched back to the originating task.

    Returns ``True`` if the job was started successfully, ``False`` otherwise.
    """
    config = uipath_config_from_gateway(gateway)
    if config is None:
        return False

    try:
        job_id = await start_job(config, task_id=task_id, task_title=task_title)
        logger.info(
            "uipath.sync.job_started",
            extra={
                "gateway_id": str(gateway.id),
                "task_id": task_id,
                "uipath_job_id": job_id,
            },
        )
        return True
    except Exception as exc:
        logger.warning(
            "uipath.sync.job_start_failed",
            extra={
                "gateway_id": str(gateway.id),
                "task_id": task_id,
                "error": str(exc),
            },
        )
        return False


async def apply_uipath_event(
    session: AsyncSession,
    *,
    gateway_id: UUID,
    payload: dict[str, Any],
) -> bool:
    """Apply a UiPath webhook job event to the corresponding OpenClaw task.

    Extracts ``in_task_id`` from the job's ``InputArguments`` and updates
    the matching task's status.

    Returns ``True`` if a task was updated.
    """
    from app.models.tasks import Task  # local import to avoid circular deps

    # UiPath webhook body has a top-level "Payload" containing the job object.
    job: dict[str, Any] = payload.get("Payload") or payload
    state: str = str(job.get("State") or "")
    input_args_raw: str | dict[str, Any] | None = job.get("InputArguments")

    if not state or not input_args_raw:
        logger.debug(
            "uipath.sync.event_skipped",
            extra={"gateway_id": str(gateway_id), "reason": "missing state or InputArguments"},
        )
        return False

    if isinstance(input_args_raw, str):
        try:
            input_args: dict[str, Any] = json.loads(input_args_raw)
        except (json.JSONDecodeError, ValueError):
            logger.warning(
                "uipath.sync.invalid_input_args",
                extra={"gateway_id": str(gateway_id)},
            )
            return False
    else:
        input_args = input_args_raw

    task_id_raw = input_args.get("in_task_id")
    if not task_id_raw:
        logger.debug(
            "uipath.sync.no_task_id",
            extra={"gateway_id": str(gateway_id)},
        )
        return False

    try:
        task_id = UUID(str(task_id_raw))
    except ValueError:
        logger.warning(
            "uipath.sync.invalid_task_id",
            extra={"gateway_id": str(gateway_id), "raw": task_id_raw},
        )
        return False

    new_status = _UIPATH_STATE_TO_TASK_STATUS.get(state)
    if new_status is None:
        logger.debug(
            "uipath.sync.unknown_state",
            extra={"gateway_id": str(gateway_id), "state": state},
        )
        return False

    task: Task | None = await Task.objects.by_id(task_id).first(session)
    if task is None:
        logger.warning(
            "uipath.sync.task_not_found",
            extra={"gateway_id": str(gateway_id), "task_id": str(task_id)},
        )
        return False

    if task.status == new_status:
        return False

    old_status = task.status
    task.status = new_status
    task.updated_at = utcnow()
    session.add(task)
    await session.commit()

    logger.info(
        "uipath.sync.task_updated",
        extra={
            "gateway_id": str(gateway_id),
            "task_id": str(task_id),
            "old_status": old_status,
            "new_status": new_status,
            "uipath_state": state,
        },
    )
    return True
