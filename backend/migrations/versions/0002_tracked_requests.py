"""Add private response-tracking requests."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tracked_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("submission_key", sa.String(36), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(160), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("response", sa.Text()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('open', 'completed')", name="ck_tracked_requests_status"),
        sa.CheckConstraint(
            "(status = 'open' AND completed_at IS NULL) OR "
            "(status = 'completed' AND completed_at IS NOT NULL)",
            name="ck_tracked_requests_completion",
        ),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_tracked_requests_title"),
        sa.CheckConstraint("length(trim(owner)) > 0", name="ck_tracked_requests_owner"),
        sa.UniqueConstraint(
            "user_id",
            "submission_key",
            name="uq_tracked_requests_user_submission_key",
        ),
    )
    op.create_index(
        "ix_tracked_requests_user_status_due",
        "tracked_requests",
        ["user_id", "status", "due_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_tracked_requests_user_status_due", table_name="tracked_requests")
    op.drop_table("tracked_requests")
