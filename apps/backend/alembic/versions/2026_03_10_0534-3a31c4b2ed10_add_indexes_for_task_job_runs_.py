"""add_indexes_for_task_job_runs_performance

Revision ID: 3a31c4b2ed10
Revises: 02603c971446
Create Date: 2026-03-10 05:34:58.745863

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3a31c4b2ed10"
down_revision: str | Sequence[str] | None = "02603c971446"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "idx_task_job_runs_task_created",
        "task_api_workflow_job_runs",
        ["task_id", "created_at"],
        postgresql_using="btree",
    )

    op.create_index(
        "idx_task_job_runs_status",
        "task_api_workflow_job_runs",
        ["status"],
        postgresql_using="btree",
    )

    op.create_index(
        "idx_task_job_runs_status_created",
        "task_api_workflow_job_runs",
        ["status", "created_at"],
        postgresql_using="btree",
    )

    op.create_index(
        "idx_task_job_runs_run_type",
        "task_api_workflow_job_runs",
        ["run_type"],
        postgresql_using="btree",
    )
    op.drop_column("task_api_workflow_job_runs", "job_rank")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_task_job_runs_run_type", table_name="task_api_workflow_job_runs")
    op.drop_index("idx_task_job_runs_status_created", table_name="task_api_workflow_job_runs")
    op.drop_index("idx_task_job_runs_status", table_name="task_api_workflow_job_runs")
    op.drop_index("idx_task_job_runs_task_created", table_name="task_api_workflow_job_runs")
    op.add_column("task_api_workflow_job_runs", "job_rank")
