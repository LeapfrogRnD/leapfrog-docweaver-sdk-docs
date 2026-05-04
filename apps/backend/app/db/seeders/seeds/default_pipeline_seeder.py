"""Super admin seeder."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Pipeline
from app.db.seeders import BaseSeeder, register_seeder
from app.logger import logger
from app.shared.constants.app_constants import (
    BedrockModel,
    LLMProviderType,
    OCRProviderType,
    ParsingMethod,
)


@register_seeder(order=2)
class DefaultPipelineSeeder(BaseSeeder):
    """Seeder for creating default pipeline."""

    @property
    def name(self) -> str:
        return "DefaultPipelineSeeder"

    async def seed(self, session: AsyncSession) -> None:
        """Create super admin user if it doesn't exist."""

        result = await session.scalar(
            select(func.count()).select_from(Pipeline).where(Pipeline.is_default.is_(True))
        )

        if result and result > 0:
            logger.info(f"{self.name}: Default Pipeline already exists. Skipping.")
            return

        default_pipeline = Pipeline(
            name="Default Pipeline",
            description="This is the default pipeline.",
            ocr_provider=OCRProviderType.AWS_TEXTRACT,
            parsing_method=ParsingMethod.LAYOUT_CONSERVED,
            llm_model=BedrockModel.claude_4_5,
            llm_model_provider=LLMProviderType.BEDROCK,
            is_default=True,
        )

        session.add(default_pipeline)
        await session.flush()
