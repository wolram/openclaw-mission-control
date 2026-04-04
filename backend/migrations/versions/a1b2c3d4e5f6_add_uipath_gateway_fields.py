"""add uipath gateway fields

Revision ID: a1b2c3d4e5f6
Revises: f1b2c3d4e5a6
Create Date: 2026-03-27 00:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f1b2c3d4e5a6"
branch_labels = None
depends_on = None

_NULLABLE_UIPATH_COLUMNS = [
    "uipath_org_name",
    "uipath_tenant_name",
    "uipath_client_id",
    "uipath_client_secret",
    "uipath_folder_name",
    "uipath_process_key",
    "uipath_webhook_secret",
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    gateway_columns = {col["name"] for col in inspector.get_columns("gateways")}

    if "gateway_type" not in gateway_columns:
        op.add_column(
            "gateways",
            sa.Column(
                "gateway_type",
                sa.String(),
                nullable=False,
                server_default=sa.text("'openclaw'"),
            ),
        )

    for col_name in _NULLABLE_UIPATH_COLUMNS:
        if col_name not in gateway_columns:
            op.add_column(
                "gateways",
                sa.Column(col_name, sa.String(), nullable=True),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    gateway_columns = {col["name"] for col in inspector.get_columns("gateways")}

    for col_name in reversed(_NULLABLE_UIPATH_COLUMNS):
        if col_name in gateway_columns:
            op.drop_column("gateways", col_name)

    if "gateway_type" in gateway_columns:
        op.drop_column("gateways", "gateway_type")
