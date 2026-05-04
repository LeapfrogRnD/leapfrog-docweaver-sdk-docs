from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from leapx.services.extractor import (
    ExtractionRequest,
    ExtractorService,
    ModelConfig,
    SystemPrompt,
    UserPrompt,
    create_extractor_service,
)
from leapx.services.extractor.constants import (
    EMPTY_SYSTEM_PROMPT_CONTENT,
    EMPTY_USER_PROMPT_CONTENT,
)
from leapx.services.extractor.exceptions.extractor_exceptions import (
    ExtractorError,
)


# Test models for extraction
class PersonInfo(BaseModel):
    name: str
    age: int
    email: str | None = None


class CompanyInfo(BaseModel):
    company_name: str
    industry: str
    employees: int


class TestExtractorService:
    """Test the ExtractorService implementation"""

    @pytest.fixture
    def mock_instructor_client(self):
        """Create a mock async instructor client"""
        mock_client = Mock()
        mock_completion = Mock()

        async def async_create(*args, **kwargs):
            return mock_completion

        mock_client.chat.completions.create = Mock(side_effect=async_create)
        return mock_client

    @pytest.fixture
    def extractor_service(self, mock_instructor_client):
        """Create an ExtractorService with mocked client"""
        return ExtractorService(instructor_client=mock_instructor_client)

    @pytest.fixture
    def async_extractor_service(self, mock_instructor_client):
        """Create an ExtractorService with mocked async client"""
        return ExtractorService(instructor_client=mock_instructor_client)

    @pytest.fixture
    def valid_request(self):
        """Create a valid extraction request"""
        return ExtractionRequest(
            system_prompt=SystemPrompt(content="You are a data extractor"),
            user_prompt=UserPrompt(
                content="Extract person info: John Doe, 30 years old"
            ),
            config=ModelConfig(),
            response_model=PersonInfo,
        )

    def test_validate_request_valid(self, extractor_service, valid_request):
        """Test validation of a valid request"""
        is_valid, error_message = extractor_service.validate_request(valid_request)
        assert is_valid is True
        assert error_message is None

    def test_validate_request_empty_system_prompt(self, extractor_service):
        """Test validation fails with empty system prompt"""
        request = ExtractionRequest(
            system_prompt=SystemPrompt(content=""),
            user_prompt=UserPrompt(content="Extract data"),
            config=ModelConfig(),
            response_model=PersonInfo,
        )
        is_valid, error_message = extractor_service.validate_request(request)
        assert is_valid is False
        assert error_message == EMPTY_SYSTEM_PROMPT_CONTENT

    def test_validate_request_empty_user_prompt(self, extractor_service):
        """Test validation fails with empty user prompt"""
        request = ExtractionRequest(
            system_prompt=SystemPrompt(content="System prompt"),
            user_prompt=UserPrompt(content=""),
            config=ModelConfig(),
            response_model=PersonInfo,
        )
        is_valid, error_message = extractor_service.validate_request(request)
        assert is_valid is False
        assert error_message == EMPTY_USER_PROMPT_CONTENT

    def test_build_user_content_without_context(self, extractor_service):
        """Test building user content without context"""
        user_prompt = UserPrompt(content="Extract data")
        content = extractor_service._build_user_content(user_prompt)
        assert content == "Extract data"

    def test_build_user_content_with_context(self, extractor_service):
        """Test building user content with context"""
        user_prompt = UserPrompt(content="Extract data", context="This is a resume")
        content = extractor_service._build_user_content(user_prompt)
        expected = "Context: This is a resume\nocr_text:\n```Extract data```"
        assert content == expected

    @pytest.mark.asyncio
    async def test_extract_success(
        self, async_extractor_service, valid_request, mock_instructor_client
    ):
        """Test successful extraction"""
        # Mock the response
        mock_result = PersonInfo(name="John Doe", age=30, email="john@example.com")

        async def async_create(*args, **kwargs):
            return mock_result

        mock_instructor_client.chat.completions.create = Mock(side_effect=async_create)

        response = await async_extractor_service.extract(valid_request)

        assert response.data == mock_result
        assert "model" in response.metadata

    @pytest.mark.asyncio
    async def test_extract_validation_failure(self, extractor_service):
        """Test extraction returns error response with invalid request"""
        invalid_request = ExtractionRequest(
            system_prompt=SystemPrompt(content=""),  # Empty content
            user_prompt=UserPrompt(content="Extract data"),
            config=ModelConfig(),
            response_model=PersonInfo,
        )

        response = await extractor_service.extract(invalid_request)

        assert response.data is None
        assert response.metadata["status"] == "validation_failed"
        assert "system_prompt.content cannot be empty" in response.metadata["error"]

    @pytest.mark.asyncio
    async def test_extract_api_error(
        self, extractor_service, valid_request, mock_instructor_client
    ):
        """Test extraction returns error response on API errors"""

        # Mock an exception
        async def async_create_error(*args, **kwargs):
            raise Exception("API Error")

        mock_instructor_client.chat.completions.create = Mock(
            side_effect=async_create_error
        )

        response = await extractor_service.extract(valid_request)

        assert response.data is None
        assert response.metadata["status"] == "extraction_failed"
        assert "API Error" in response.metadata["error"]

    @pytest.mark.asyncio
    async def test_extract_async_success(
        self, async_extractor_service, valid_request, mock_instructor_client
    ):
        """Test successful async extraction"""
        # Mock the response
        mock_result = PersonInfo(name="John Doe", age=30, email="john@example.com")

        async def async_create(*args, **kwargs):
            return mock_result

        mock_instructor_client.chat.completions.create = Mock(side_effect=async_create)

        response = await async_extractor_service.extract(valid_request)

        assert response.data == mock_result
        assert "model" in response.metadata

    @pytest.mark.asyncio
    async def test_extract_async_validation_failure(self, async_extractor_service):
        """Test async extraction returns error response with invalid request"""
        invalid_request = ExtractionRequest(
            system_prompt=SystemPrompt(content=""),  # Empty content
            user_prompt=UserPrompt(content="Extract data"),
            config=ModelConfig(),
            response_model=PersonInfo,
        )

        response = await async_extractor_service.extract(invalid_request)

        assert response.data is None
        assert response.metadata["status"] == "validation_failed"
        assert "system_prompt.content cannot be empty" in response.metadata["error"]

    @pytest.mark.asyncio
    async def test_extract_async_api_error(
        self, extractor_service, valid_request, mock_instructor_client
    ):
        """Test async extraction returns error response on API errors"""

        # Mock an exception
        async def async_create_error(*args, **kwargs):
            raise ExtractorError("API Error")

        mock_instructor_client.chat.completions.create = Mock(
            side_effect=async_create_error
        )

        response = await extractor_service.extract(valid_request)

        assert response.data is None
        assert response.metadata["status"] == "extraction_failed"
        assert "API Error" in response.metadata["error"]

    def test_create_extractor_service_default(self):
        """Test factory function creates service with default client"""
        service = create_extractor_service()
        assert isinstance(service, ExtractorService)
        assert service.instructor_client is not None

    def test_create_extractor_service_custom_client(self, mock_instructor_client):
        """Test factory function creates service with custom client"""
        service = create_extractor_service(mock_instructor_client)
        assert isinstance(service, ExtractorService)
        assert service.instructor_client == mock_instructor_client


class TestIntegration:
    """Integration tests for the complete extraction flow"""

    @pytest.mark.asyncio
    async def test_complete_extraction_flow(self):
        """Test the complete extraction flow with mocked dependencies"""
        # Create mock client
        mock_client = Mock()
        mock_result = CompanyInfo(
            company_name="Tech Corp", industry="Technology", employees=500
        )

        async def async_create(*args, **kwargs):
            return mock_result

        mock_client.chat.completions.create = Mock(side_effect=async_create)

        # Create service
        service = ExtractorService(instructor_client=mock_client)

        # Create request
        request = ExtractionRequest(
            system_prompt=SystemPrompt(
                content="Extract company information from the given text"
            ),
            user_prompt=UserPrompt(
                content="Tech Corp is a technology company with 500 employees",
                context="Company profile document",
            ),
            config=ModelConfig(temperature=0.2, model="gpt-4"),
            response_model=CompanyInfo,
        )

        # Perform extraction
        response = await service.extract(request)

        # Verify results
        assert response.data.company_name == "Tech Corp"
        assert response.data.industry == "Technology"
        assert response.data.employees == 500

        # Verify client was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args

        assert call_args.kwargs["model"] == "gpt-4"
        assert call_args.kwargs["temperature"] == 0.2
        assert call_args.kwargs["response_model"] == CompanyInfo
        assert len(call_args.kwargs["messages"]) == 2
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert call_args.kwargs["messages"][1]["role"] == "user"


if __name__ == "__main__":
    pytest.main([__file__])
