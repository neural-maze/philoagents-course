import time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """Model for chat request messages."""

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The message content to send to the philosopher",
        examples=["What is the meaning of life?"],
    )
    philosopher_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique identifier for the philosopher",
        examples=["socrates", "plato", "aristotle"],
    )


class ChatResponse(BaseModel):
    """Model for chat response messages."""

    response: str = Field(
        ...,
        description="The philosopher's response",
        examples=["The unexamined life is not worth living."],
    )


class WebSocketMessage(BaseModel):
    """Model for WebSocket message validation."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The message content",
        examples=["Tell me about virtue."],
    )
    philosopher_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique identifier for the philosopher",
        examples=["socrates"],
    )
    client_id: Optional[str] = Field(
        default=None, description="Optional client identifier for connection tracking"
    )


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: str = Field(
        ...,
        description="Error message",
        examples=["Validation Error", "Internal Server Error"],
    )
    detail: Optional[str] = Field(
        None,
        description="Additional error details",
        examples=["Field 'message' is required"],
    )


class ResetResponse(BaseModel):
    """Model for memory reset responses."""

    status: str = Field(
        ..., description="Operation status", examples=["success", "error"]
    )
    message: str = Field(
        ...,
        description="Operation result message",
        examples=["Memory reset successfully", "Failed to reset memory"],
    )


class HealthResponse(BaseModel):
    """Model for health check responses."""

    status: str = Field(
        ..., description="Health status", examples=["healthy", "unhealthy"]
    )
    version: str = Field(..., description="API version", examples=["0.1.0"])
    environment: Optional[str] = Field(
        default=None,
        description="Environment name",
        examples=["development", "production"],
    )
    connections: Optional[int] = Field(
        default=None, description="Active WebSocket connections", examples=[5, 0]
    )


class WebSocketStreamingResponse(BaseModel):
    """Model for WebSocket streaming responses."""

    type: str = Field(
        ...,
        description="Message type",
        examples=["streaming_start", "chunk", "complete", "error"],
    )
    streaming: Optional[bool] = Field(
        default=None, description="Whether streaming is active"
    )
    chunk: Optional[str] = Field(default=None, description="Text chunk for streaming")
    response: Optional[str] = Field(default=None, description="Complete response text")
    philosopher_id: Optional[str] = Field(
        default=None, description="Philosopher identifier"
    )
    error: Optional[str] = Field(default=None, description="Error message if any")
    detail: Optional[str] = Field(default=None, description="Additional error details")


class MetricsResponse(BaseModel):
    """Model for metrics endpoint responses."""

    request_count: int = Field(..., description="Total number of requests processed")
    average_response_time: float = Field(
        ..., description="Average response time in seconds"
    )
    websocket_connections: int = Field(
        ..., description="Current number of active WebSocket connections"
    )
    environment: str = Field(..., description="Current environment")
    version: str = Field(..., description="API version")
    uptime: Optional[float] = Field(
        default=None, description="Server uptime in seconds"
    )
