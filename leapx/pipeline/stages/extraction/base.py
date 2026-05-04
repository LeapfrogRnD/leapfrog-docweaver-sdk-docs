from abc import ABC
from typing import Any

from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.schemas import StageName, StageType


class BaseExtractionStage(BaseStage[str, dict[str, Any]], ABC):
    """Base for extraction stages.

    This abstract stage defines common properties for extraction stages that
    consume text and produce a key-value dictionary result.

    Returns:
        dict[str, Any]: Structured extraction output.
    """

    @property
    def name(self) -> str:
        """Get stage identifier.

        Returns:
            str: The identifier for extraction stages.
        """
        return StageName.extraction

    @property
    def stage_type(self) -> StageType:
        """Get execution type.

        Returns:
            StageType: IO-bound stage type.
        """
        return StageType.IO
