from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutConservedConstants:
    MERGE_THRESHOLD: float = 0.1
    CALCULATED_RATIO_MINIMUM: float = 0.05
    CALCULATED_RATIO_MAXIMUM: float = 0.5


constants = LayoutConservedConstants()
