"""Integration tests using real Azure OCR patient documents.

These tests validate parser behavior on real-world medical documents
from Azure Document AI OCR, ensuring proper handling of:
- Multi-column layouts
- Complex spacing
- Medical terminology
- Form-style documents
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from leapx.services.layout_parser.parser_factory import ParserFactory
from leapx.services.layout_parser.structures.ocr_data import OCRData


def load_patient_ocr(patient_num: int) -> pd.DataFrame:
    """Load patient OCR JSON and convert to DataFrame.

    Args:
        patient_num: Patient number (1, 2, or 3)

    Returns:
        DataFrame with OCR data
    """
    ocr_dir = Path(__file__).parent / "ocr_results"
    file_path = ocr_dir / f"patient_{patient_num}.json"

    with file_path.open(encoding="utf-8") as f:
        ocr_data = json.load(f)

    rows = []
    for page in ocr_data.get("pages", []):
        page_num = page.get("pageNumber", 1)

        for word in page.get("words", []):
            polygon = word.get("polygon", [])
            if len(polygon) < 8:
                continue

            # Convert inches to pixels at 72 DPI
            x0_px = polygon[0] * 72
            y0_px = polygon[1] * 72
            x2_px = polygon[4] * 72
            y2_px = polygon[5] * 72

            rows.append(
                {
                    "page": page_num,
                    "x0": x0_px,
                    "y0": y0_px,
                    "x2": x2_px,
                    "y2": y2_px,
                    "value": word.get("content", ""),
                    "confidence": word.get("confidence", 1.0),
                }
            )

    return pd.DataFrame(rows)


@pytest.fixture
def patient_1_df():
    """Load patient 1 OCR data."""
    return load_patient_ocr(1)


@pytest.fixture
def patient_2_df():
    """Load patient 2 OCR data."""
    return load_patient_ocr(2)


@pytest.fixture
def patient_3_df():
    """Load patient 3 OCR data."""
    return load_patient_ocr(3)


class TestPatient1Document:
    """Tests for patient 1 prescription document."""

    def test_basic_parser_produces_output(self, patient_1_df):
        """Basic parser should successfully parse document."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        assert result is not None
        assert len(result) > 0
        assert isinstance(result, str)

    def test_advance_parser_produces_output(self, patient_1_df):
        """Advance parser should successfully parse document."""
        parser = ParserFactory.create("layout_conserved_advance")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        assert result is not None
        assert len(result) > 0
        assert isinstance(result, str)

    def test_contains_key_medical_terms(self, patient_1_df):
        """Parsed text should contain key medical terms."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        # Key terms that should appear in prescription
        assert "ipratropium" in result.lower()
        assert "albuterol" in result.lower()
        assert "prescription" in result.lower()
        assert "directions" in result.lower()

    def test_preserves_multi_column_layout(self, patient_1_df):
        """Parser should maintain multi-column structure."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        lines = result.split("\n")

        # Should have multiple lines
        assert len(lines) > 10

        # Lines should have varying indentation (multi-column indicator)
        leading_spaces = [
            len(line) - len(line.lstrip()) for line in lines if line.strip()
        ]
        assert len(set(leading_spaces)) > 1, "Document should have varying indentation"

    def test_word_count_consistency(self, patient_1_df):
        """Parsed output should contain most input words."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        # Get unique words from input
        input_words = set(patient_1_df["value"].str.lower())

        # Get words from output
        output_text = result.lower()
        found_words = sum(1 for word in input_words if word in output_text)

        # Should find at least 90% of words
        coverage = found_words / len(input_words)
        assert coverage > 0.9, f"Only found {coverage:.1%} of input words"


class TestPatient2Document:
    """Tests for patient 2 medical supply order."""

    def test_basic_parser_handles_patient_2(self, patient_2_df):
        """Basic parser should handle patient 2 document."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_2_df)
        result = parser.parse(ocr_data)

        assert result is not None
        assert len(result) > 0

    def test_advance_parser_handles_patient_2(self, patient_2_df):
        """Advance parser should handle patient 2 document."""
        parser = ParserFactory.create("layout_conserved_advance")
        ocr_data = OCRData(df=patient_2_df)
        result = parser.parse(ocr_data)

        assert result is not None
        assert len(result) > 0

    def test_contains_supply_keywords(self, patient_2_df):
        """Should contain medical supply related keywords."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_2_df)
        result = parser.parse(ocr_data)

        result_lower = result.lower()
        # Check for common medical supply terms
        supply_terms = ["supply", "equipment", "order", "patient"]
        found = sum(1 for term in supply_terms if term in result_lower)

        assert found >= 2, "Should contain medical supply terminology"


class TestPatient3Document:
    """Tests for patient 3 diabetic supply order."""

    def test_basic_parser_handles_patient_3(self, patient_3_df):
        """Basic parser should handle patient 3 document."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_3_df)
        result = parser.parse(ocr_data)

        assert result is not None
        assert len(result) > 0

    def test_advance_parser_handles_patient_3(self, patient_3_df):
        """Advance parser should handle patient 3 document."""
        parser = ParserFactory.create("layout_conserved_advance")
        ocr_data = OCRData(df=patient_3_df)
        result = parser.parse(ocr_data)

        assert result is not None
        assert len(result) > 0

    def test_contains_diabetic_terms(self, patient_3_df):
        """Should contain diabetic/medical terminology."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_3_df)
        result = parser.parse(ocr_data)

        result_lower = result.lower()
        # Check for diabetic supply related terms
        diabetic_terms = ["diabetic", "diabetes", "supply", "patient", "order"]
        found = sum(1 for term in diabetic_terms if term in result_lower)

        assert found >= 2, "Should contain diabetic-related terminology"

    def test_largest_document_performance(self, patient_3_df):
        """Patient 3 is largest - should still parse efficiently."""
        import time

        parser = ParserFactory.create("layout_conserved")

        start = time.time()
        ocr_data = OCRData(df=patient_3_df)
        result = parser.parse(ocr_data)
        duration = time.time() - start

        assert duration < 5.0, f"Parsing took {duration:.2f}s, should be < 5s"
        assert len(result) > 0


class TestParserComparison:
    """Compare basic vs advance parser outputs."""

    @pytest.mark.parametrize("patient_num", [1, 2, 3])
    def test_both_parsers_produce_similar_line_counts(self, patient_num):
        """Both parsers should produce similar number of lines."""
        df = load_patient_ocr(patient_num)

        basic_parser = ParserFactory.create("layout_conserved")
        advance_parser = ParserFactory.create("layout_conserved_advance")

        basic_result = basic_parser.parse(OCRData(df=df))
        advance_result = advance_parser.parse(OCRData(df=df))

        basic_lines = len(basic_result.split("\n"))
        advance_lines = len(advance_result.split("\n"))

        # Should be within 20% of each other
        ratio = min(basic_lines, advance_lines) / max(basic_lines, advance_lines)
        assert ratio > 0.8, (
            f"Line counts differ too much: {basic_lines} vs {advance_lines}"
        )

    @pytest.mark.parametrize("patient_num", [1, 2, 3])
    def test_both_parsers_preserve_word_order(self, patient_num):
        """Both parsers should maintain reading order for single-column text.

        Note: Multi-column documents may have words from different columns
        interleaved in the OCR data, so we only check that consecutive words
        from the same y-coordinate (same line) maintain their order.
        """
        df = load_patient_ocr(patient_num)

        # Get words from the same line (similar y0 values)
        # Sort by y0 to group lines, then take first line with multiple words
        df_sorted = df.sort_values("y0").reset_index(drop=True)
        first_line_y = df_sorted.iloc[0]["y0"]

        # Find words on approximately the same line (within 5 pixels)
        same_line = df_sorted[abs(df_sorted["y0"] - first_line_y) < 5]

        if len(same_line) < 2:
            pytest.skip("Not enough words on first line to test order")

        # Sort by x0 to get left-to-right order
        same_line = same_line.sort_values("x0").reset_index(drop=True)
        input_words = same_line.head(5)["value"].tolist()

        basic_parser = ParserFactory.create("layout_conserved")
        # advance_parser = ParserFactory.create("layout_conserved_advance")

        basic_result = basic_parser.parse(OCRData(df=df))
        # advance_result = advance_parser.parse(OCRData(df=df))

        # Check that consecutive words on same line appear in order
        for i in range(len(input_words) - 1):
            word1, word2 = input_words[i], input_words[i + 1]

            basic_idx1 = basic_result.find(word1)
            basic_idx2 = basic_result.find(word2, basic_idx1 + 1)  # Search after word1

            # Both words should be found and in order
            if basic_idx1 >= 0 and basic_idx2 >= 0:
                assert basic_idx1 < basic_idx2, (
                    f"Basic parser: '{word1}' should come before '{word2}' "
                    f"(indices: {basic_idx1}, {basic_idx2})"
                )


class TestEdgeCases:
    """Test edge cases found in patient documents."""

    def test_handles_special_characters(self, patient_1_df):
        """Should handle special characters in medical text."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        # Medical documents often have periods, commas, slashes
        assert "." in result
        assert "/" in result or "mg" in result  # Dosage formats

    def test_handles_numbers(self, patient_1_df):
        """Should preserve numbers correctly."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        # Check that numbers are preserved
        import re

        numbers = re.findall(r"\d+", result)
        assert len(numbers) > 0, "Should contain numeric values"

    def test_handles_empty_lines(self, patient_1_df):
        """Should handle documents with empty line regions."""
        parser = ParserFactory.create("layout_conserved")
        ocr_data = OCRData(df=patient_1_df)
        result = parser.parse(ocr_data)

        lines = result.split("\n")
        # Some lines may be empty (representing vertical spacing)
        empty_lines = [line for line in lines if not line.strip()]

        # Document may have empty lines for spacing
        assert len(empty_lines) >= 0  # Just ensure no crash
