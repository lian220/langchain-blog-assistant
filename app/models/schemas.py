from pydantic import BaseModel, Field
from typing import Optional


class BlogRequest(BaseModel):
    """Request model for blog generation."""

    topic: str = Field(..., description="The topic for the blog post")
    additional_instructions: Optional[str] = Field(
        None, description="Any additional instructions for the blog generation"
    )


class BlogResponse(BaseModel):
    """Response model for blog generation."""

    success: bool
    message: str
    file_name: Optional[str] = None
    content_preview: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    message: str
