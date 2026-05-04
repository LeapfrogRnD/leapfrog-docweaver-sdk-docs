from typing import Any

from pydantic import model_validator

from leapx.common.types.providers import ParsingMethod
from leapx.pipeline.stages.configs.base import BlockConfig
from leapx.services.layout_parser.config import (
    LayoutConservedAdvanceConfig,
    LayoutConservedConfig,
)


class ParserConfig(BlockConfig):
    """Configuration for the layout parser stage.

    Args:
        subconfig: Optional parser-specific configuration.
        method: Parsing method identifier (enum or string).
    """

    method: ParsingMethod | None = None
    subconfig: dict[str, Any] = {}
    instance: Any | None = None

    @model_validator(mode="after")
    def get_parser_config_object(
        self,
    ) -> LayoutConservedConfig | LayoutConservedAdvanceConfig:
        """Build the parser configuration object from the selected method.

        Returns:
            An instance of the parser configuration for the chosen method.

        Raises:
            ValueError: If the parser method is unrecognized.
        """
        methods = {
            ParsingMethod.LAYOUT_CONSERVED: LayoutConservedConfig,
            ParsingMethod.LAYOUT_CONSERVED_ADVANCE: LayoutConservedAdvanceConfig,
        }
        self.instance = (
            methods.get(self.method)(**self.subconfig) if self.method else None
        )
        if self.instance:
            return self

        message = f"Unknown parser method: {self.method}"
        raise ValueError(message)
