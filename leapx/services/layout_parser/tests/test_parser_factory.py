"""Tests for ParserFactory."""

import pytest

from leapx.common.types.providers import ParsingMethod
from leapx.services.layout_parser.exceptions.layout_parser_exceptions import (
    ParserNotRegisteredError,
    ParserRegistrationError,
)
from leapx.services.layout_parser.parser_factory import ParserFactory
from leapx.services.layout_parser.parsers.base_parser import BaseLayoutParser
from leapx.services.layout_parser.parsers.layout_conserved import LayoutConservedParser
from leapx.services.layout_parser.parsers.layout_conserved_advance import (
    LayoutConservedAdvanceParser,
)


class TestParserFactory:
    """Tests for ParserFactory."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Clear registry before and after each test."""
        ParserFactory.clear_registry()
        yield
        ParserFactory.clear_registry()

    def test_register_parser(self):
        """Test registering a parser."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        assert ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED)

    def test_register_parser_twice_raises_error(self):
        """Test registering same parser twice raises error."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)

        with pytest.raises(ParserRegistrationError, match="already registered"):
            ParserFactory.register(
                ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser
            )

    def test_register_parser_with_override(self):
        """Test registering parser with override=True."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        ParserFactory.register(
            ParsingMethod.LAYOUT_CONSERVED, LayoutConservedAdvanceParser, override=True
        )

        parser_class = ParserFactory.get_parser_class(ParsingMethod.LAYOUT_CONSERVED)
        assert parser_class == LayoutConservedAdvanceParser

    def test_register_invalid_parser_raises_error(self):
        """Test registering non-parser class raises error."""

        class NotAParser:
            pass

        with pytest.raises(
            ParserRegistrationError, match="must extend BaseLayoutParser"
        ):
            ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, NotAParser)

    def test_unregister_parser(self):
        """Test unregistering a parser."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        assert ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED)

        ParserFactory.unregister(ParsingMethod.LAYOUT_CONSERVED)
        assert not ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED)

    def test_unregister_nonexistent_parser_raises_error(self):
        """Test unregistering non-registered parser raises error."""
        with pytest.raises(ParserNotRegisteredError, match="No parser registered"):
            ParserFactory.unregister(ParsingMethod.LAYOUT_CONSERVED)

    def test_create_parser(self):
        """Test creating parser instance."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        parser = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED)

        assert isinstance(parser, LayoutConservedParser)
        assert isinstance(parser, BaseLayoutParser)

    def test_create_parser_with_config(self, sample_layout_conserved_config):
        """Test creating parser with configuration."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        parser = ParserFactory.create(
            ParsingMethod.LAYOUT_CONSERVED, config=sample_layout_conserved_config
        )

        assert parser.config == sample_layout_conserved_config

    def test_create_unregistered_parser_raises_error(self):
        """Test creating unregistered parser raises error."""
        with pytest.raises(ParserNotRegisteredError, match="No parser registered"):
            ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED)

    def test_list_available_empty(self):
        """Test listing available parsers when none registered."""
        available = ParserFactory.list_available()
        assert available == []

    def test_list_available_with_parsers(self):
        """Test listing available parsers."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        ParserFactory.register(
            ParsingMethod.LAYOUT_CONSERVED_ADVANCE, LayoutConservedAdvanceParser
        )

        available = ParserFactory.list_available()
        assert len(available) == 2
        assert ParsingMethod.LAYOUT_CONSERVED in available
        assert ParsingMethod.LAYOUT_CONSERVED_ADVANCE in available

    def test_is_registered_true(self):
        """Test is_registered returns True for registered parser."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        assert ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED) is True

    def test_is_registered_false(self):
        """Test is_registered returns False for non-registered parser."""
        assert ParserFactory.is_registered(ParsingMethod.LAYOUT_CONSERVED) is False

    def test_get_parser_class(self):
        """Test getting parser class."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        parser_class = ParserFactory.get_parser_class(ParsingMethod.LAYOUT_CONSERVED)

        assert parser_class == LayoutConservedParser

    def test_get_parser_class_unregistered_raises_error(self):
        """Test getting unregistered parser class raises error."""
        with pytest.raises(ParserNotRegisteredError, match="No parser registered"):
            ParserFactory.get_parser_class(ParsingMethod.LAYOUT_CONSERVED)

    def test_clear_registry(self):
        """Test clearing registry."""
        ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
        ParserFactory.register(
            ParsingMethod.LAYOUT_CONSERVED_ADVANCE, LayoutConservedAdvanceParser
        )

        ParserFactory.clear_registry()
        assert ParserFactory.list_available() == []
