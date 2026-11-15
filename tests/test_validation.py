import pytest
from pydantic import ValidationError

from app.schemas import PostingRequest


def test_valid_message_with_one_url():
    payload = PostingRequest(message="Check out our product https://example.com")
    assert payload.message == "Check out our product https://example.com"


def test_empty_message():
    with pytest.raises(ValidationError):
        PostingRequest(message="   ")


def test_missing_message():
    with pytest.raises(ValidationError):
        PostingRequest(message=None)  # type: ignore[arg-type]


def test_message_exceeding_200_chars():
    long_message = "x" * 201
    with pytest.raises(ValidationError):
        PostingRequest(message=f"{long_message} https://example.com")


def test_message_without_url():
    with pytest.raises(ValidationError):
        PostingRequest(message="This is a message without a URL")


def test_message_with_multiple_urls():
    with pytest.raises(ValidationError):
        PostingRequest(message="A https://a.com and https://b.com")


def test_invalid_url():
    with pytest.raises(ValidationError):
        PostingRequest(message="Bad url ftp://example.com")


def test_http_and_https_allowed():
    req_http = PostingRequest(message="HTTP test http://example.com")
    req_https = PostingRequest(message="HTTPS test https://example.com")
    assert req_http.message == "HTTP test http://example.com"
    assert req_https.message == "HTTPS test https://example.com"
