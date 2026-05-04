"""Tests for BBox structure."""

import pytest

from leapx.services.layout_parser.structures.bbox import BBox


class TestBBox:
    """Tests for BBox dataclass."""

    def test_creation(self):
        """Test creating a BBox."""
        bbox = BBox(x0=0, y0=0, x2=10, y2=10)
        assert bbox.x0 == 0
        assert bbox.y0 == 0
        assert bbox.x2 == 10
        assert bbox.y2 == 10

    def test_width_property(self):
        """Test width calculation."""
        bbox = BBox(x0=5, y0=5, x2=15, y2=20)
        assert bbox.width == 10

    def test_height_property(self):
        """Test height calculation."""
        bbox = BBox(x0=5, y0=5, x2=15, y2=20)
        assert bbox.height == 15

    def test_is_empty_true(self):
        """Test is_empty returns True for None values."""
        bbox = BBox.default_empty_bbox()
        assert bbox.is_empty() is True

    def test_is_empty_false(self):
        """Test is_empty returns False for valid bbox."""
        bbox = BBox(x0=0, y0=0, x2=10, y2=10)
        assert bbox.is_empty() is False

    def test_is_invalid_true(self):
        """Test is_invalid returns True for negative dimensions."""
        bbox = BBox(x0=10, y0=10, x2=5, y2=5)
        assert bbox.is_invalid() is True

    def test_is_invalid_false(self):
        """Test is_invalid returns False for valid dimensions."""
        bbox = BBox(x0=0, y0=0, x2=10, y2=10)
        assert bbox.is_invalid() is False

    def test_copy(self):
        """Test copying a BBox."""
        bbox1 = BBox(x0=0, y0=0, x2=10, y2=10)
        bbox2 = bbox1.copy()
        assert bbox1.x0 == bbox2.x0
        assert bbox1.y0 == bbox2.y0
        assert bbox1.x2 == bbox2.x2
        assert bbox1.y2 == bbox2.y2
        assert bbox1 is not bbox2

    def test_from_iterator_tuple(self):
        """Test creating from tuple."""
        bbox = BBox.from_iterator((0, 5, 10, 15))
        assert bbox.x0 == 0
        assert bbox.y0 == 5
        assert bbox.x2 == 10
        assert bbox.y2 == 15

    def test_from_iterator_list(self):
        """Test creating from list."""
        bbox = BBox.from_iterator([2, 4, 6, 8])
        assert bbox.x0 == 2
        assert bbox.y0 == 4
        assert bbox.x2 == 6
        assert bbox.y2 == 8

    def test_from_iterator_invalid_length(self):
        """Test creating from iterator with wrong length raises ValueError."""
        with pytest.raises(ValueError, match="Invalid length of iterator for BBox"):
            BBox.from_iterator([1, 2, 3])

    def test_repr(self):
        """Test string representation."""
        bbox = BBox(x0=0, y0=0, x2=10, y2=10)
        assert "BBox" in repr(bbox)
        assert "0" in repr(bbox)
        assert "10" in repr(bbox)

    def test_equality(self):
        """Test BBox equality."""
        bbox1 = BBox(x0=0, y0=0, x2=10, y2=10)
        bbox2 = BBox(x0=0, y0=0, x2=10, y2=10)
        bbox3 = BBox(x0=0, y0=0, x2=5, y2=5)
        assert bbox1 == bbox2
        assert bbox1 != bbox3

    def test_negative_dimensions(self):
        """Test BBox with inverted coordinates."""
        bbox = BBox(x0=10, y0=10, x2=0, y2=0)
        assert bbox.width == -10
        assert bbox.height == -10
        assert bbox.is_invalid() is True
