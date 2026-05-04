"""drop_unwanted_columns_from_tasks

Revision ID: 61f7925317a4
Revises: a2ea5b12b880
Create Date: 2026-03-01 16:43:20.598659

"""

from collections.abc import Sequence

from sqlalchemy import JSON, Boolean, Column, Integer, String, Text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "61f7925317a4"
down_revision: str | Sequence[str] | None = "a2ea5b12b880"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("tasks", "status")
    op.drop_column("tasks", "task_rank")
    op.drop_column("tasks", "result")
    op.drop_column("tasks", "failed_remarks")
    op.drop_column("tasks", "is_integrated_api_task")
    op.drop_column("tasks", "api_key_id")
    op.drop_column("tasks", "api_job_id")
    op.add_column("tasks", Column("is_duplicated", Boolean, default=False, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("tasks", Column("status", String(255), nullable=True))
    op.add_column("tasks", Column("task_rank", Integer, nullable=True))
    op.add_column("tasks", Column("result", JSON, nullable=True))
    op.add_column("tasks", Column("failed_remarks", Text, nullable=True))
    op.add_column("tasks", Column("is_integrated_api_task", Boolean, nullable=True))
    op.add_column("tasks", Column("api_key_id", Integer, nullable=True))
    op.add_column("tasks", Column("api_job_id", String(255), nullable=True))
    op.drop_column("tasks", "is_duplicated")
