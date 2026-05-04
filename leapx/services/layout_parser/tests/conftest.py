"""Test fixtures and sample data for layout parser tests."""

import pandas as pd
import pytest


@pytest.fixture
def sample_ocr_dataframe():
    """Create sample OCR DataFrame for testing."""
    return pd.DataFrame(
        {
            "x0": [10.0, 50.0, 10.0, 60.0],
            "y0": [10.0, 10.0, 30.0, 30.0],
            "x2": [40.0, 80.0, 50.0, 100.0],
            "y2": [20.0, 20.0, 40.0, 40.0],
            "value": ["Hello", "World", "Test", "Document"],
            "page": [0, 0, 0, 0],
            "block": [0, 0, 0, 0],
            "line": [0, 0, 1, 1],
            "confidence": [0.95, 0.97, 0.92, 0.94],
            "space_type": [1, 2, 1, 2],
        }
    )


@pytest.fixture
def minimal_ocr_dataframe():
    """Create minimal OCR DataFrame with only required columns."""
    return pd.DataFrame(
        {
            "x0": [0.0, 50.0],
            "y0": [0.0, 0.0],
            "x2": [40.0, 90.0],
            "y2": [10.0, 10.0],
            "value": ["Hello", "World"],
        }
    )


@pytest.fixture
def empty_ocr_dataframe():
    """Create empty OCR DataFrame."""
    return pd.DataFrame(columns=["x0", "y0", "x2", "y2", "value"])


@pytest.fixture
def multi_page_dataframe():
    """Create multi-page OCR DataFrame."""
    return pd.DataFrame(
        {
            "x0": [10.0, 50.0, 10.0, 50.0],
            "y0": [10.0, 10.0, 10.0, 10.0],
            "x2": [40.0, 80.0, 40.0, 80.0],
            "y2": [20.0, 20.0, 20.0, 20.0],
            "value": ["Page", "One", "Page", "Two"],
            "page": [0, 0, 1, 1],
            "line": [0, 0, 0, 0],
            "confidence": [0.95, 0.96, 0.94, 0.93],
        }
    )


@pytest.fixture
def sample_layout_conserved_config():
    """Create sample LayoutConservedConfig."""
    from leapx.services.layout_parser.config import LayoutConservedConfig

    return LayoutConservedConfig(
        reset_lines=True, pixel_to_char=0.2, merge_threshold=0.53, max_spaces=1000
    )


@pytest.fixture
def sample_layout_conserved_advance_config():
    """Create sample LayoutConservedAdvanceConfig."""
    from leapx.services.layout_parser.config import LayoutConservedAdvanceConfig

    return LayoutConservedAdvanceConfig(
        reset_lines=True,
        pixel_to_char=0.2,
        merge_threshold=0.53,
    )
