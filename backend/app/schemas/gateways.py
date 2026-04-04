"""Schemas for gateway CRUD and template-sync API payloads."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.gateways import GATEWAY_TYPE_OPENCLAW

RUNTIME_ANNOTATION_TYPES = (datetime, UUID)


class GatewayBase(SQLModel):
    """Shared gateway fields used across create/read payloads."""

    name: str
    url: str
    workspace_root: str
    allow_insecure_tls: bool = False
    disable_device_pairing: bool = False


class UiPathFields(SQLModel):
    """UiPath Orchestrator credential fields shared by create/read/update schemas."""

    gateway_type: str = GATEWAY_TYPE_OPENCLAW
    uipath_org_name: str | None = None
    uipath_tenant_name: str | None = None
    uipath_client_id: str | None = None
    uipath_client_secret: str | None = None
    uipath_folder_name: str | None = None
    uipath_process_key: str | None = None
    uipath_webhook_secret: str | None = None


class GatewayCreate(GatewayBase, UiPathFields):
    """Payload for creating a gateway configuration."""

    token: str | None = None

    @field_validator("token", mode="before")
    @classmethod
    def normalize_token(cls, value: object) -> str | None | object:
        """Normalize empty/whitespace tokens to `None`."""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class GatewayUpdate(UiPathFields):
    """Payload for partial gateway updates."""

    name: str | None = None
    url: str | None = None
    token: str | None = None
    workspace_root: str | None = None
    allow_insecure_tls: bool | None = None
    disable_device_pairing: bool | None = None
    gateway_type: str | None = None  # type: ignore[assignment]

    @field_validator("token", mode="before")
    @classmethod
    def normalize_token(cls, value: object) -> str | None | object:
        """Normalize empty/whitespace tokens to `None`."""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class GatewayRead(GatewayBase, UiPathFields):
    """Gateway payload returned from read endpoints."""

    id: UUID
    organization_id: UUID
    token: str | None = None
    created_at: datetime
    updated_at: datetime


class GatewayTemplatesSyncError(SQLModel):
    """Per-agent error entry from a gateway template sync operation."""

    agent_id: UUID | None = None
    agent_name: str | None = None
    board_id: UUID | None = None
    message: str


class GatewayTemplatesSyncResult(SQLModel):
    """Summary payload returned by gateway template sync endpoints."""

    gateway_id: UUID
    include_main: bool
    reset_sessions: bool
    agents_updated: int
    agents_skipped: int
    main_updated: bool
    errors: list[GatewayTemplatesSyncError] = Field(default_factory=list)
