from datetime import datetime
from functools import partial

from shared.constants.app_constants import TaskStatus, TaskTypes
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


def orm_to_dict(obj, include: set[str]) -> dict:
    if isinstance(obj, dict):
        return {k: obj.get(k) for k in include if k in obj}
    return {c: getattr(obj, c) for c in include}


Base = declarative_base()

UTCDateTime = partial(
    mapped_column,
    DateTime(timezone=True),
)


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


class Pipeline(TimestampMixin):
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
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship to tasks
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="pipeline")


class Task(TimestampMixin):
    """Model for storing task information."""

    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    additional_instruction: Mapped[str] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskTypes] = mapped_column(String(255), nullable=True)
    file_key: Mapped[str] = mapped_column(String(255), nullable=True)
    file_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    formatted_json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    pipeline_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pipelines.id"), nullable=True
    )
    task_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    is_duplicated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="tasks")
    task_job_runs: Mapped[list["TaskApiWorkFlowJobRun"]] = relationship(
        "TaskApiWorkFlowJobRun", back_populates="task"
    )

    @property
    def lastest_job_run(self) -> "TaskApiWorkFlowJobRun | None":
        if not self.task_job_runs:
            return None
        return max(self.task_job_runs, key=lambda run: run.created_at)

    @property
    def execution_config(self) -> dict:
        config = {
            **orm_to_dict(
                self,
                {
                    "formatted_json_schema",
                    "additional_instruction",
                    "task_type",
                    "task_metadata",
                },
            )
        }

        if self.pipeline is not None:
            config.update(
                orm_to_dict(
                    self.pipeline,
                    {
                        "ocr_provider",
                        "parsing_method",
                        "vlm_model",
                        "vlm_model_provider",
                        "llm_model",
                        "llm_model_provider",
                    },
                )
            )

        return config


class ApiKey(TimestampMixin):
    """Model for storing api keys."""

    __tablename__ = "api_keys"

    secret_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    webhook_url: Mapped[str] = mapped_column(String, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    api_key_secrets: Mapped[list["ApiKeySecrets"]] = relationship(
        "ApiKeySecrets", back_populates="api_key"
    )
    api_workflows: Mapped[list["ApiWorkFlow"]] = relationship(
        "ApiWorkFlow", back_populates="api_key"
    )


class ApiKeySecrets(TimestampMixin):
    """Model for storing api key secrets."""

    __tablename__ = "api_key_secrets"

    api_key_id: Mapped[int] = mapped_column(Integer, ForeignKey("api_keys.id"), nullable=False)
    secret_value: Mapped[str] = mapped_column(String, nullable=False)
    generated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="api_key_secrets")


class ApiWorkFlow(TimestampMixin):
    """Model for storing api workflows."""

    __tablename__ = "api_workflows"

    name: Mapped[str] = mapped_column(String, nullable=False)
    workflow_type: Mapped[str] = mapped_column(String, nullable=False)
    pipeline_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    additional_instruction: Mapped[str] = mapped_column(Text, nullable=True)
    json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    formatted_json_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    api_key_id: Mapped[int] = mapped_column(Integer, ForeignKey("api_keys.id"), nullable=False)

    # Relationships
    api_key: Mapped["ApiKey"] = relationship("ApiKey", back_populates="api_workflows")
    api_workflow_jobs: Mapped[list["ApiWorkFlowJob"]] = relationship(
        "ApiWorkFlowJob", back_populates="api_workflow"
    )


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

    @property
    def execution_config(self) -> dict:
        config = {
            **orm_to_dict(
                self.api_workflow,
                {
                    "formatted_json_schema",
                    "additional_instruction",
                    "workflow_type",
                },
            )
        }

        if self.api_workflow is not None and self.api_workflow.pipeline_config is not None:
            config.update(
                orm_to_dict(
                    self.api_workflow.pipeline_config,
                    {
                        "ocr_provider",
                        "parsing_method",
                        "vlm_model",
                        "vlm_model_provider",
                        "llm_model",
                        "llm_model_provider",
                        "task_metadata",
                    },
                )
            )

        return config


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
