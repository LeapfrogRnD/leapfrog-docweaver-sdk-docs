"""Tests for configuration module."""

import pytest

from leapx.common.types.providers import ParsingMethod
from leapx.services.layout_parser.config import (
    LayoutConservedAdvanceConfig,
    LayoutConservedConfig,
)


class TestParsingMethod:
    """Tests for ParsingMethod enum."""

    def test_enum_values(self):
        """Test enum has expected values."""
        assert ParsingMethod.LAYOUT_CONSERVED.value == "layout_conserved"
        assert (
            ParsingMethod.LAYOUT_CONSERVED_ADVANCE.value == "layout_conserved_advance"
        )

    def test_enum_str(self):
        """Test enum string representation."""
        assert str(ParsingMethod.LAYOUT_CONSERVED) == "layout_conserved"
        assert str(ParsingMethod.LAYOUT_CONSERVED_ADVANCE) == "layout_conserved_advance"


class TestLayoutConservedConfig:
    """Tests for LayoutConservedConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LayoutConservedConfig()
        assert config.reset_lines is True
        assert config.pixel_to_char == 0.2
        assert config.merge_threshold == 0.53
        assert config.max_spaces == 1000

    def test_custom_values(self):
        """Test custom configuration values."""
        config = LayoutConservedConfig(
            reset_lines=False, pixel_to_char=0.15, merge_threshold=0.6, max_spaces=800
        )
        assert config.reset_lines is False
        assert config.pixel_to_char == 0.15
        assert config.merge_threshold == 0.6
        assert config.max_spaces == 800

    def test_validation_pixel_to_char_negative(self):
        """Test validation rejects negative pixel_to_char."""
        with pytest.raises(ValueError, match="pixel_to_char must be positive"):
            LayoutConservedConfig(pixel_to_char=-0.1)

    def test_validation_pixel_to_char_zero(self):
        """Test validation rejects zero pixel_to_char."""
        with pytest.raises(ValueError, match="pixel_to_char must be positive"):
            LayoutConservedConfig(pixel_to_char=0.0)

    def test_validation_merge_threshold_negative(self):
        """Test validation rejects negative merge_threshold."""
        with pytest.raises(ValueError, match="merge_threshold must be positive"):
            LayoutConservedConfig(merge_threshold=-0.5)

    def test_validation_max_spaces_small(self):
        """Test validation rejects small max_spaces."""
        with pytest.raises(ValueError, match="max_spaces must be positive"):
            LayoutConservedConfig(max_spaces=-5)

    def test_validation_max_spaces_zero(self):
        """Test validation rejects zero max_spaces."""
        with pytest.raises(ValueError, match="max_spaces must be positive"):
            LayoutConservedConfig(max_spaces=0)


class TestLayoutConservedAdvanceConfig:
    """Tests for LayoutConservedAdvanceConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LayoutConservedAdvanceConfig()
        assert config.reset_lines is True
        assert config.pixel_to_char == 0.2
        assert config.merge_threshold == 0.53

    def test_custom_values(self):
        """Test custom configuration values."""
        config = LayoutConservedAdvanceConfig(
            reset_lines=False,
            pixel_to_char=0.15,
            merge_threshold=0.6,
        )
        assert config.reset_lines is False
        assert config.pixel_to_char == 0.15
        assert config.merge_threshold == 0.6

    def test_inherits_validation(self):
        """Test that advanced config inherits validation from base."""
        with pytest.raises(ValueError, match="pixel_to_char must be positive"):
            LayoutConservedAdvanceConfig(pixel_to_char=-0.1)

        with pytest.raises(ValueError, match="merge_threshold must be positive"):
            LayoutConservedAdvanceConfig(merge_threshold=0)
