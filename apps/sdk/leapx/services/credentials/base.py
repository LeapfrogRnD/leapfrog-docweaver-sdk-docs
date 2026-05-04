from pydantic_settings import BaseSettings, SettingsConfigDict


class Credential(BaseSettings):
    """
    Base credential model with environment variable support.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    def validate_for_use(self) -> None:
        """
        Hook you can override in subclasses for custom validation
        Called by the pipeline.

        This checks if the credentials are valid
        """
        return
