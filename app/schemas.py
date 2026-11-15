from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

URL_PATTERN = r"https?://[^\s]+"


class PostingRequest(BaseModel):
    message: str = Field(..., description="The message to publish with exactly one CTA URL.")

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if value is None:
            raise ValueError("Message is required.")

        normalized = value.strip()
        if not normalized:
            raise ValueError("Message cannot be empty.")
        if len(normalized) > 200:
            raise ValueError("Message must not exceed 200 characters.")

        import re
        from urllib.parse import urlparse

        matches = re.findall(URL_PATTERN, normalized)
        if len(matches) != 1:
            raise ValueError("Message must contain exactly one valid HTTP or HTTPS URL.")

        url = matches[0].strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL must be a valid HTTP or HTTPS URL.")

        return normalized

    @model_validator(mode="after")
    def ensure_exactly_one_url(self):
        import re
        from urllib.parse import urlparse

        normalized = self.message.strip()
        matches = re.findall(URL_PATTERN, normalized)
        if len(matches) != 1:
            raise ValueError("Message must contain exactly one valid HTTP or HTTPS URL.")

        url = matches[0].strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL must be a valid HTTP or HTTPS URL.")

        self.message = normalized
        return self


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    total_platforms: int
    successful_platforms: int
    failed_platforms: int
    results: list[PlatformResult]
