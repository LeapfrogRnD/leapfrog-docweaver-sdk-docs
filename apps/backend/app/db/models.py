from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    JSON,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    event,
    func,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import (
    Mapped,
    Session,
    mapped_column,
    relationship,
    with_loader_criteria,
)

from app.db.database import Base
from app.db.utils.columns import UTCDateTime
from app.shared.constants.app_constants import FileUploadStatus, TaskStatus, TaskTypes


class TimestampMixin(Base):
    """Mixin class to add created_at and updated_at timestamps to tables."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = UTCDateTime(server_default=func.now())
    updated_at: Mapped[datetime | None] = UTCDateTime(
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        server_onupdate=func.now(),
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = UTCDateTime(nullable=True)
    deleted_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    def soft_delete(self, user_id: int | None = None) -> None:
        self.deleted_at = datetime.now(UTC)
        self.deleted_by = user_id

    def restore(self) -> None:
        self.deleted_at = None
        self.deleted_by = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    if (
        not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )


class UserStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING = "pending"


class User(TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=True)
    verification_token: Mapped[str] = mapped_column(String(100), nullable=True)
    is_profile_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    forget_password_token: Mapped[str] = mapped_column(String(100), nullable=True)
    forget_password_token_expiry: Mapped[datetime] = UTCDateTime(nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name="user_status"),
        default=UserStatus.BLOCKED,
        nullable=False,
    )

    # Relationship to refresh tokens
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    # Relationship to tasks
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="user", foreign_keys="Task.created_by"
    )
    pipelines: Mapped[list["Pipeline"]] = relationship(
        "Pipeline", back_populates="user", foreign_keys="Pipeline.created_by"
    )

    # Relationship to api_keys
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="ApiKey.created_by",
    )

    # __table_args__ = (
    #     Index(
    #         "uq_user_active_email",
    #         "email",
    #         unique=True,
    #             postgresql_where=text(
    #                 "is_active IS TRUE AND deleted_at IS NULL"
    #             ),
    #     ),
    # )

    @property
    def full_name(self) -> str:
        first = (self.first_name or "").strip()
        last = (self.last_name or "").strip()
        if not first and not last:
            return "User"
        return f"{first} {last}".strip()


class RefreshToken(TimestampMixin):
    """Model for storing refresh tokens."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = UTCDateTime(nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship to user
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class Pipeline(TimestampMixin, SoftDeleteMixin):
    """Model for storing pipeline information."""

    __tablename__ = "pipelines"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ocr_provider: Mapped[str] = mapped_column(String(100), nullable=True)
    parsing_method: Mapped[str] = mapped_column(String(100), nullable=True)
    vlm_model: Mapped[str] = mapped_column(String(100), nullable=True)
    vlm_model_provider: Mapped[str] = mapped_column(String(100), nullable=True)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=True)
    llm_model_provider: Mapped[str] = mapped_column(String(100), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    task_metadata: Mapped[JSON] = mapped_column(JSON, default={}, nullable=True)
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="pipeline")
    user: Mapped["User"] = relationship(
        "User", back_populates="pipelines", foreign_keys=[created_by]
    )


class Task(TimestampMixin, SoftDeleteMixin):
    """Model for storing task information."""

    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    additional_instruction: Mapped[str] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskTypes] = mapped_column(String(255), nullable=True)
    file_key: Mapped[str] = mapped_column(String(255), nullable=True)
    file_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    file_status: Mapped[FileUploadStatus] = mapped_column(String(255), nullable=True)
    json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    formatted_json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    pipeline_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pipelines.id"), nullable=True
    )
    task_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    is_duplicated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    # Relationship to user and pipeline
    user: Mapped["User"] = relationship(
        "User", back_populates="tasks", foreign_keys=[created_by]
    )
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="tasks")
    task_job_runs: Mapped[list["TaskApiWorkFlowJobRun"]] = relationship(
        "TaskApiWorkFlowJobRun", back_populates="task"
    )

    @property
    def lastest_job_run(self) -> "TaskApiWorkFlowJobRun | None":
        if not self.task_job_runs:
            return None
        return max(self.task_job_runs, key=lambda run: run.created_at)


class ApiKey(TimestampMixin, SoftDeleteMixin):
    """Model for storing api keys."""

    __tablename__ = "api_keys"

    secret_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime] = UTCDateTime(nullable=True)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    webhook_url: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index(
            "uq_api_key_secret_name_not_deleted",
            "secret_name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="api_keys",
        foreign_keys=[created_by],
    )
    api_key_secrets: Mapped[list["ApiKeySecrets"]] = relationship(
        "ApiKeySecrets", back_populates="api_key"
    )
    api_workflows: Mapped[list["ApiWorkFlow"]] = relationship(
        "ApiWorkFlow", back_populates="api_key"
    )


class ApiKeySecrets(TimestampMixin):
    """Model for storing api keys."""

    __tablename__ = "api_key_secrets"

    api_key_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_keys.id"), nullable=False
    )
    secret_value: Mapped[str] = mapped_column(String, nullable=False)
    generated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    revoked_at: Mapped[datetime] = UTCDateTime(nullable=True)
    revoked_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    # Relationships
    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="api_key_secrets")


class ApiWorkFlow(TimestampMixin, SoftDeleteMixin):
    """Model for storing api workflows."""

    __tablename__ = "api_workflows"

    name: Mapped[str] = mapped_column(String, nullable=False)
    workflow_type: Mapped[str] = mapped_column(String, nullable=False)
    pipeline_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    additional_instruction: Mapped[str] = mapped_column(Text, nullable=True)
    json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    formatted_json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    file_status: Mapped[FileUploadStatus] = mapped_column(String(255), nullable=True)
    api_key_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_keys.id"), nullable=False
    )

    __table_args__ = (
        Index(
            "uq_workflow_name_not_deleted",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    # Relationships
    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="api_workflows")


class ApiWorkFlowJob(TimestampMixin):
    """Model for storing api workflow jobs."""

    __tablename__ = "api_workflow_jobs"

    api_workflow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_workflows.id"), nullable=False
    )
    api_job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    api_secret_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_key_secrets.id"), nullable=False
    )
    file_key: Mapped[str] = mapped_column(String(255), nullable=True)
    file_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    job_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    # Relationships
    api_workflow: Mapped["ApiWorkFlow"] = relationship("ApiWorkFlow")
    api_key_secret: Mapped["ApiKeySecrets"] = relationship("ApiKeySecrets")
    api_workflow_job_runs: Mapped[list["TaskApiWorkFlowJobRun"]] = relationship(
        "TaskApiWorkFlowJobRun", back_populates="api_workflow_job"
    )

    @property
    def lastest_job_run(self) -> "TaskApiWorkFlowJobRun | None":
        if not self.api_workflow_job_runs:
            return None
        return max(self.api_workflow_job_runs, key=lambda run: run.created_at)


class TaskApiWorkFlowJobRun(TimestampMixin):
    """Model for storing task api workflow job runs."""

    __tablename__ = "task_api_workflow_job_runs"
    run_type: Mapped[str] = mapped_column(String(255), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)
    api_workflow_job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_workflow_jobs.id"), nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(String(255), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=True)
    failed_remarks: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    api_workflow_job: Mapped["ApiWorkFlowJob"] = relationship(
        "ApiWorkFlowJob", back_populates="api_workflow_job_runs"
    )
    task: Mapped["Task"] = relationship("Task", back_populates="task_job_runs")
