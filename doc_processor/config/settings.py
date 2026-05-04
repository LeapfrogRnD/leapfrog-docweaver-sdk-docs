"""Configuration settings for the document processor worker."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the path to the parent directory's .env file
# ENV_FILE_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
ENV_FILE_PATH = ".env"


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH), env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )

    # Application
    APP_NAME: str = "doc-processor"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    # Database Configuration (shared with main app)
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"  # localhost for local
    DB_PORT: str = "5434"  # 5434

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False  # SQL logging for debugging
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Worker Configuration
    WORKER_ID: str = "worker-1"  # Will be overridden by ECS task ID
    POLLING_INTERVAL: int = 5  # Seconds between polling cycles
    BATCH_SIZE: int = 5  # Number of tasks to fetch per poll
    MAX_CONCURRENT_TASKS: int = 3  # Max tasks processing simultaneously

    TASK_TIMEOUT: int = 300  # 5 minutes per task
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 60  # Seconds before retry

    STORAGE_BACKEND: Literal["s3", "local"] = "local"
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "leapx-documents"
    LOCAL_STORAGE_PATH: str = "/tmp/documents"

    # SQS Configuration
    SQS_QUEUE_URL: str = ""
    # Optional explicit DLQ URL. If empty, worker will derive from SQS_QUEUE_URL redrive policy.
    SQS_DLQ_URL: str = ""
    SQS_DLQ_SUFFIX: str = "-dlq"
    SQS_ENDPOINT_URL: str | None = None
    SQS_MAX_MESSAGES: int = 10
    SQS_WAIT_TIME_SECONDS: int = 20
    SQS_VISIBILITY_TIMEOUT: int = 300

    # Health Check
    HEALTH_CHECK_PORT: int = 8050

    # Graceful Shutdown
    SHUTDOWN_TIMEOUT: int = 30  # Seconds to wait for graceful shutdown

    # Metrics & Monitoring
    ENABLE_METRICS: bool = True
    MEMORY_THRESHOLD_PERCENT: float = 50.0  # For auto-scaling alerts
    CPU_THRESHOLD_PERCENT: float = 60.0

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Global settings instance
settings = Settings()
