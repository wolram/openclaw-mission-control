"""UiPath Orchestrator webhook receiver endpoint."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import TYPE_CHECKING, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.logging import get_logger
from app.db.session import get_session
from app.models.gateways import Gateway
from app.schemas.common import OkResponse
from app.services.uipath.sync_service import apply_uipath_event

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks/uipath", tags=["uipath-webhooks"])
SESSION_DEP = Depends(get_session)


def _verify_signature(body: bytes, secret: str, header: str) -> bool:
    """Verify UiPath HMAC-SHA256 webhook signature.

    UiPath sends the signature as a raw hex digest in the ``X-UiPath-Signature``
    header (no ``sha256=`` prefix).
    """
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.strip())


@router.post("/{gateway_id}", response_model=OkResponse)
async def receive_uipath_webhook(
    gateway_id: UUID,
    request: Request,
    session: AsyncSession = SESSION_DEP,
) -> OkResponse:
    """Receive a UiPath Orchestrator job event and update the matching OpenClaw task.

    UiPath must be configured to POST to::

        POST /api/v1/webhooks/uipath/{gateway_id}

    If ``uipath_webhook_secret`` is set on the gateway, the ``X-UiPath-Signature``
    header is validated before processing the payload.
    """
    body = await request.body()

    gateway: Gateway | None = await Gateway.objects.by_id(gateway_id).first(session)
    if gateway is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gateway not found.")

    if gateway.uipath_webhook_secret:
        sig_header = request.headers.get("X-UiPath-Signature", "")
        if not sig_header or not _verify_signature(body, gateway.uipath_webhook_secret, sig_header):
            logger.warning(
                "uipath.webhook.invalid_signature",
                extra={"gateway_id": str(gateway_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature.",
            )

    try:
        payload: dict[str, Any] = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be valid JSON.",
        )

    await apply_uipath_event(session, gateway_id=gateway_id, payload=payload)
    return OkResponse()
