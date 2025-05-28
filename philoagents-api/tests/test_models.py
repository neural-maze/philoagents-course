import pytest
from pydantic import ValidationError

from philoagents.infrastructure.models import (
    ChatMessage,
    ChatResponse,
    ErrorResponse,
    MetricsResponse,
    ResetResponse,
    WebSocketMessage,
    WebSocketStreamingResponse,
)


class TestChatMessage:
    """Tests for ChatMessage model."""

    def test_valid_chat_message(self):
        """Test creating a valid chat message."""
        message = ChatMessage(message="Hello, Socrates!", philosopher_id="socrates")
        assert message.message == "Hello, Socrates!"
        assert message.philosopher_id == "socrates"

    def test_message_strip_whitespace(self):
        """Test that whitespace is stripped from message."""
        message = ChatMessage(message="  Hello, Socrates!  ", philosopher_id="socrates")
        assert message.message == "Hello, Socrates!"

    def test_empty_message_validation(self):
        """Test that empty message raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(message="")

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_short" for error in errors)

    def test_message_too_long_validation(self):
        """Test that message too long raises validation error."""
        long_message = "x" * 10001
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(message=long_message)

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(message="Hello", extra_field="not_allowed")

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)


class TestChatResponse:
    """Tests for ChatResponse model."""

    def test_valid_chat_response(self):
        """Test creating a valid chat response."""
        response = ChatResponse(
            response="The unexamined life is not worth living.",
        )
        assert response.response == "The unexamined life is not worth living."


class TestWebSocketMessage:
    """Tests for WebSocketMessage model."""

    def test_valid_websocket_message(self):
        """Test creating a valid WebSocket message."""
        message = WebSocketMessage(
            message="Tell me about virtue", philosopher_id="socrates"
        )
        assert message.message == "Tell me about virtue"
        assert message.philosopher_id == "socrates"
        assert message.client_id is None

    def test_websocket_message_with_client_id(self):
        """Test WebSocket message with client ID."""
        message = WebSocketMessage(
            message="Tell me about virtue",
            philosopher_id="socrates",
            client_id="client_123",
        )
        assert message.client_id == "client_123"

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            WebSocketMessage(
                message="Hello", philosopher_id="socrates", extra_field="not_allowed"
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_valid_error_response(self):
        """Test creating a valid error response."""
        error = ErrorResponse(
            error="Validation Error", detail="Field 'message' is required"
        )
        assert error.error == "Validation Error"
        assert error.detail == "Field 'message' is required"

    def test_error_response_without_detail(self):
        """Test error response without detail."""
        error = ErrorResponse(error="Internal Server Error")
        assert error.error == "Internal Server Error"
        assert error.detail is None


class TestResetResponse:
    """Tests for ResetResponse model."""

    def test_valid_reset_response(self):
        """Test creating a valid reset response."""
        response = ResetResponse(status="success", message="Memory reset successfully")
        assert response.status == "success"
        assert response.message == "Memory reset successfully"


class TestWebSocketStreamingResponse:
    """Tests for WebSocketStreamingResponse model."""

    def test_streaming_start_response(self):
        """Test streaming start response."""
        response = WebSocketStreamingResponse(type="streaming_start", streaming=True)
        assert response.type == "streaming_start"
        assert response.streaming is True
        assert response.chunk is None
        assert response.response is None

    def test_chunk_response(self):
        """Test chunk response."""
        response = WebSocketStreamingResponse(type="chunk", chunk="Hello, ")
        assert response.type == "chunk"
        assert response.chunk == "Hello, "

    def test_error_response(self):
        """Test error response."""
        response = WebSocketStreamingResponse(
            type="error", error="Processing error", detail="Something went wrong"
        )
        assert response.type == "error"
        assert response.error == "Processing error"
        assert response.detail == "Something went wrong"


class TestMetricsResponse:
    """Tests for MetricsResponse model."""

    def test_metrics_response_with_uptime(self):
        """Test metrics response with uptime."""
        metrics = MetricsResponse(
            request_count=100,
            average_response_time=0.25,
            websocket_connections=5,
            environment="development",
            version="0.1.0",
            uptime=3600.0,
        )
        assert metrics.uptime == 3600.0


class TestModelSerialization:
    """Tests for model serialization."""

    def test_chat_message_serialization(self):
        """Test ChatMessage serialization."""
        message = ChatMessage(message="Hello, Socrates!", philosopher_id="socrates")
        data = message.model_dump()
        assert data["message"] == "Hello, Socrates!"
        assert data["philosopher_id"] == "socrates"

    def test_error_response_serialization(self):
        """Test ErrorResponse serialization."""
        error = ErrorResponse(error="Test error", detail="Test detail")
        data = error.model_dump()
        assert data["error"] == "Test error"
        assert data["detail"] == "Test detail"

    def test_model_deserialization(self):
        """Test model deserialization from dict."""
        data = {"message": "Hello, Socrates!", "philosopher_id": "socrates"}
        message = ChatMessage(**data)
        assert message.message == "Hello, Socrates!"
        assert message.philosopher_id == "socrates"
