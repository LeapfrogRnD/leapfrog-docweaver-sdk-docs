import os
import traceback

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logger import logger

load_dotenv(verbose=False, override=False)


class Settings(BaseSettings):
    mode: str = "staging"

    # Storage configuration
    storage_mode: str = "local"  # "local" or "s3"

    # Queue configuration
    queue_provider: str = "sqs"

    aws_region: str = "us-east-1"
    aws_s3_bucket_name: str = "bucket"
    aws_bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    aws_sqs_queue_name: str = ""

    # CORS configuration
    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    # CSRF configuration
    csrf_secret_key: str = "leapfrog_docweaver_csrf_secret"  # Should be overridden in production with a secure random value  # noqa: S105
    csrf_expiry_seconds: int = 7200  # 2 hours

    # Session configuration
    session_dir: str = "./tmp/sessions"

    #rate limit configuration
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 500
    rate_limit_window_seconds: int = 60
    rate_limit_whitelist: str = ""
    rate_limit_backend: str = "memory"
    rate_limit_redis_url: str | None = None
    rate_limit_redis_prefix: str = "rate_limit:"
    rate_limit_overrides: str = "/api/process-now/:3"

    # JWT configuration
    jwt_secret_key: str = "leapfrog_docweaver_jwt_secret"  # Should be overridden in production with a secure random value  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # Email configuration
    email_provider: str = "ses"
    email_from: str = "noreply@example.com"
    email_from_name: str = "Leapfrog DocWeaver"

    # SMTP configuration
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    # Password reset configuration
    password_reset_token_expire_minutes: int = 30
    frontend_url: str = "http://localhost:5173"

    azure_ocr_endpoint: str | None = None
    azure_ocr_api_key: str | None = None

    local_storage_path: str = "./tmp/uploads"

    langfuse_secret_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_base_url: str | None = None
    langfuse_tracing_enabled: str | None = None

    openai_api_key: str | None = None
    document_page_limit: int = 10

    # Database configuration
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False  # SQL logging for debugging

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def model_post_init(self, __context) -> None:
        """Hook that runs after model initialization to load secrets from AWS."""
        self.load_secrets_from_aws()

        # Validate that required secrets are set
        if not self.jwt_secret_key:
            error_msg = (
                "JWT_SECRET_KEY is required but not set. "
                "Please set it as an environment variable or in AWS Secrets Manager."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

    def load_secrets_from_aws(self):
        """Load secrets from AWS Secrets Manager if running in production/staging."""

        if self.mode.lower() in ("local"):
            logger.info(
                f"Mode is '{self.mode}', skipping AWS Secrets Manager. "
                "Set MODE environment variable to 'production' or 'staging' to load from AWS."
            )
            return

        logger.info(f"Mode is '{self.mode}', attempting to load secrets from AWS Secrets Manager")

        secret_name = os.getenv("AWS_SECRET_NAME")

        if not secret_name:
            logger.warning(
                "AWS_SECRET_NAME environment variable not set, skipping AWS Secrets Manager. "
                "Set AWS_SECRET_NAME to load secrets from AWS."
            )
            return

        try:
            # Lazy import to avoid circular dependency
            from app.providers.secrets.aws_secrets import get_secrets_manager

            logger.info(f"Loading secrets from AWS Secrets Manager: {secret_name}")
            secrets_manager = get_secrets_manager(
                secret_name=secret_name, region_name=self.aws_region
            )
            secrets = secrets_manager.get_secrets()

            secret_mappings = {
                "JWT_SECRET_KEY": ("jwt_secret_key", "JWT_SECRET_KEY"),
                "OPENAI_API_KEY": ("openai_api_key", "OPENAI_API_KEY"),
                "LANGFUSE_PUBLIC_KEY": ("langfuse_public_key", "LANGFUSE_PUBLIC_KEY"),
                "LANGFUSE_SECRET_KEY": ("langfuse_secret_key", "LANGFUSE_SECRET_KEY"),
                "LANGFUSE_BASE_URL": ("langfuse_base_url", "LANGFUSE_BASE_URL"),
                "LANGFUSE_TRACING_ENABLED": (
                    "langfuse_tracing_enabled",
                    "LANGFUSE_TRACING_ENABLED",
                ),
                "AZURE_OCR_ENDPOINT": ("azure_endpoint", "AZURE_OCR_ENDPOINT"),
                "AZURE_OCR_API_KEY": ("azure_key", "AZURE_OCR_API_KEY"),
                "CORS_ORIGINS": ("cors_origins", "CORS_ORIGINS"),
            }

            loaded_secrets = []
            for secret_key, (attr_name, env_var) in secret_mappings.items():
                if secret_key in secrets:
                    value = secrets[secret_key]
                    setattr(self, attr_name, value)
                    os.environ[env_var] = value
                    loaded_secrets.append(secret_key)

            logger.info(
                f"Successfully loaded {len(loaded_secrets)} secrets from AWS: {', '.join(loaded_secrets)}"
            )

        except Exception as e:
            logger.error(
                "Failed to load secrets from AWS Secrets Manager",
                error=str(e),
                traceback=traceback.format_exc(),
            )

    @classmethod
    def initialize(cls) -> "Settings":
        try:
            return Settings()  # type: ignore

        except Exception as e:
            logger.error(
                "Error loading secrets",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            raise e  # noqa: TRY201
