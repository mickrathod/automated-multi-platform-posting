import pytest
import httpx

from app.config import Settings
from app.platforms.devto import DevToPlatform
from app.platforms.hashnode import HashnodePlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.reddit import RedditPlatform
from app.platforms.x import XPlatform


@pytest.mark.asyncio
async def test_x_success(monkeypatch):
    async def fake_post(*args, **kwargs):
        class Response:
            status_code = 201
            content = b'{"data":{"id":"123","text":"hello"}}'
            text = '{"data":{"id":"123","text":"hello"}}'

            def json(self):
                return {"data": {"id": "123", "text": "hello"}}

        return Response()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    platform = XPlatform(settings=Settings(X_ACCESS_TOKEN="token"))
    result = await platform.publish("hello https://example.com")
    assert result.status == "success"
    assert result.posted_url == "https://x.com/i/web/status/123"


@pytest.mark.asyncio
async def test_reddit_missing_credentials():
    platform = RedditPlatform(settings=Settings())
    result = await platform.publish("hello https://example.com")
    assert result.status == "failed"
    assert "missing" in result.error.lower()


@pytest.mark.asyncio
async def test_mastodon_success(monkeypatch):
    async def fake_post(*args, **kwargs):
        class Response:
            status_code = 200
            content = b'{"url":"https://mastodon.example/@user/1"}'
            text = '{"url":"https://mastodon.example/@user/1"}'

            def json(self):
                return {"url": "https://mastodon.example/@user/1"}

        return Response()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    platform = MastodonPlatform(
        settings=Settings(MASTODON_INSTANCE_URL="https://mastodon.example", MASTODON_ACCESS_TOKEN="abc")
    )
    result = await platform.publish("hello https://example.com")
    assert result.status == "success"
    assert result.posted_url == "https://mastodon.example/@user/1"


@pytest.mark.asyncio
async def test_devto_success(monkeypatch):
    async def fake_post(*args, **kwargs):
        class Response:
            status_code = 201
            content = b'{"url":"https://dev.to/user/post-title"}'
            text = '{"url":"https://dev.to/user/post-title"}'

            def json(self):
                return {"url": "https://dev.to/user/post-title"}

        return Response()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    platform = DevToPlatform(settings=Settings(DEVTO_API_KEY="k"))
    result = await platform.publish("hello https://example.com")
    assert result.status == "success"
    assert result.posted_url == "https://dev.to/user/post-title"


@pytest.mark.asyncio
async def test_hashnode_missing_credentials():
    platform = HashnodePlatform(settings=Settings())
    result = await platform.publish("hello https://example.com")
    assert result.status == "failed"
