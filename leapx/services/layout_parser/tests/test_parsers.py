"""Integration tests for parsers."""

import pandas as pd
import pytest

from leapx.common.types.providers import ParsingMethod
from leapx.services.layout_parser import ParserFactory
from leapx.services.layout_parser.config import (
    LayoutConservedConfig,
)
from leapx.services.layout_parser.exceptions.layout_parser_exceptions import (
    DataFrameColumnMissingError,
    DataFrameEmptyError,
)
from leapx.services.layout_parser.parsers.layout_conserved import LayoutConservedParser
from leapx.services.layout_parser.parsers.layout_conserved_advance import (
    LayoutConservedAdvanceParser,
)
from leapx.services.layout_parser.structures.ocr_data import OCRData


class TestLayoutConservedParser:
    """Integration tests for LayoutConservedParser."""

    def test_parser_creation(self):
        """Test creating parser instance."""
        parser = LayoutConservedParser()
        assert parser is not None
        assert parser.config is not None

    def test_parser_with_config(self, sample_layout_conserved_config):
        """Test creating parser with custom config."""
        parser = LayoutConservedParser(config=sample_layout_conserved_config)
        assert parser.config == sample_layout_conserved_config

    def test_parse_simple_dataframe(self, minimal_ocr_dataframe):
        """Test parsing minimal DataFrame."""
        parser = LayoutConservedParser()
        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result = parser.parse(ocr_data)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Hello" in result
        assert "World" in result

    def test_parse_with_lines(self, sample_ocr_dataframe):
        """Test parsing DataFrame with multiple lines."""
        parser = LayoutConservedParser()
        ocr_data = OCRData(df=sample_ocr_dataframe)
        result = parser.parse(ocr_data)

        assert isinstance(result, str)
        lines = result.split("\n")
        assert len(lines) >= 1  # At least one line

    def test_parse_empty_dataframe_raises_error(self, empty_ocr_dataframe):
        """Test parsing empty DataFrame raises error."""
        LayoutConservedParser()

        with pytest.raises(DataFrameEmptyError):
            OCRData(df=empty_ocr_dataframe)

    def test_parse_missing_columns_raises_error(self):
        """Test parsing DataFrame with missing required columns raises error."""
        df = pd.DataFrame({"x0": [0], "y0": [0]})  # Missing x2, y2, value
        LayoutConservedParser()

        with pytest.raises(DataFrameColumnMissingError):
            OCRData(df=df)

    def test_parse_with_kwargs_override(self, minimal_ocr_dataframe):
        """Test parsing with kwargs overriding config."""
        config = LayoutConservedConfig(pixel_to_char=0.2)
        parser = LayoutConservedParser(config=config)

        # Override with kwargs
        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result = parser.parse(ocr_data, pixel_to_char=0.15, reset_lines=False)
        assert isinstance(result, str)

    def test_parse_preserves_layout(self):
        """Test that parser preserves horizontal spacing."""
        df = pd.DataFrame(
            {
                "x0": [0.0, 100.0],  # Words far apart
                "y0": [0.0, 0.0],
                "x2": [30.0, 130.0],
                "y2": [10.0, 10.0],
                "value": ["Left", "Right"],
                "line": [0, 0],
            }
        )

        parser = LayoutConservedParser()
        ocr_data = OCRData(df=df)
        result = parser.parse(ocr_data)
        # Should have spaces between words
        assert "Left" in result
        assert "Right" in result
        # Calculate approximate position (pixel_to_char=0.2 default)
        # "Right" at x0=100 should be around char position 20
        assert len(result) > 10  # Should have spacing


class TestLayoutConservedAdvanceParser:
    """Integration tests for LayoutConservedAdvanceParser."""

    def test_parser_creation(self):
        """Test creating parser instance."""
        parser = LayoutConservedAdvanceParser()
        assert parser is not None
        assert parser.config is not None

    def test_parser_with_config(self, sample_layout_conserved_advance_config):
        """Test creating parser with custom config."""
        parser = LayoutConservedAdvanceParser(
            config=sample_layout_conserved_advance_config
        )
        assert parser.config == sample_layout_conserved_advance_config

    def test_parse_simple_dataframe(self, minimal_ocr_dataframe):
        """Test parsing minimal DataFrame."""
        parser = LayoutConservedAdvanceParser()
        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result = parser.parse(ocr_data)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Hello" in result
        assert "World" in result

    def test_parse_with_auto_adjust(self, minimal_ocr_dataframe):
        """Test parsing with auto-adjust ratio enabled (default)."""
        parser = LayoutConservedAdvanceParser()
        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result = parser.parse(ocr_data, auto_adjust_ratio=True)
        assert isinstance(result, str)

    def test_parse_without_auto_adjust(self, minimal_ocr_dataframe):
        """Test parsing with auto-adjust ratio disabled."""
        parser = LayoutConservedAdvanceParser()
        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result = parser.parse(ocr_data, auto_adjust_ratio=False)
        assert isinstance(result, str)

    def test_parse_empty_dataframe_raises_error(self, empty_ocr_dataframe):
        """Test parsing empty DataFrame raises error."""
        with pytest.raises(DataFrameEmptyError):
            OCRData(df=empty_ocr_dataframe)


class TestParserFactoryIntegration:
    """Integration tests using ParserFactory."""

    @pytest.fixture(autouse=True)
    def setup_parsers(self):
        """Ensure parsers are registered."""
        # Explicitly register parsers in case registry was cleared
        from leapx.services.layout_parser import ParserFactory, ParsingMethod
        from leapx.services.layout_parser.parsers.layout_conserved import (
            LayoutConservedParser,
        )
        from leapx.services.layout_parser.parsers.layout_conserved_advance import (
            LayoutConservedAdvanceParser,
        )

        if not ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED):
            ParserFactory.register(
                ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser
            )
        if not ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED_ADVANCE):
            ParserFactory.register(
                ParsingMethod.LAYOUT_CONSERVED_ADVANCE, LayoutConservedAdvanceParser
            )

    def test_create_layout_conserved_parser(self):
        """Test creating LayoutConservedParser via factory."""
        parser = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED)
        assert isinstance(parser, LayoutConservedParser)

    def test_create_layout_conserved_advance_parser(self):
        """Test creating LayoutConservedAdvanceParser via factory."""
        parser = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED_ADVANCE)
        assert isinstance(parser, LayoutConservedAdvanceParser)

    def test_parse_via_factory(self, minimal_ocr_dataframe):
        """Test full parsing workflow via factory."""
        parser = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED)
        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result = parser.parse(ocr_data)

        assert isinstance(result, str)
        assert "Hello" in result
        assert "World" in result

    def test_compare_parsers(self, minimal_ocr_dataframe):
        """Test that both parsers produce valid output."""
        parser1 = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED)
        parser2 = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED_ADVANCE)

        ocr_data = OCRData(df=minimal_ocr_dataframe)
        result1 = parser1.parse(ocr_data)
        result2 = parser2.parse(ocr_data)

        # Both should produce string output
        assert isinstance(result1, str)
        assert isinstance(result2, str)

        # Both should contain the words
        assert "Hello" in result1 and "World" in result1
        assert "Hello" in result2 and "World" in result2
