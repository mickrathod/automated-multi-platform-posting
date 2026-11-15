import pytest

from app.config import Settings
from app.platforms.devto import DevToPlatform
from app.platforms.hashnode import HashnodePlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.reddit import RedditPlatform
from app.platforms.x import XPlatform
from app.services.posting_service import PostingService


@pytest.mark.asyncio
async def test_all_platforms_success(monkeypatch):
    async def fake_publish(self, message):
        return self._success(posted_url=f"https://example.com/{self.name.lower()}", public_access=True)

    monkeypatch.setattr(XPlatform, "publish", fake_publish)
    monkeypatch.setattr(RedditPlatform, "publish", fake_publish)
    monkeypatch.setattr(MastodonPlatform, "publish", fake_publish)
    monkeypatch.setattr(DevToPlatform, "publish", fake_publish)
    monkeypatch.setattr(HashnodePlatform, "publish", fake_publish)

    service = PostingService(
        platforms=[
            XPlatform(settings=Settings()),
            RedditPlatform(settings=Settings()),
            MastodonPlatform(settings=Settings()),
            DevToPlatform(settings=Settings()),
            HashnodePlatform(settings=Settings()),
        ]
    )

    response = await service.publish("hello https://example.com")
    assert response.success is True
    assert response.total_platforms == 5
    assert response.successful_platforms == 5
    assert response.failed_platforms == 0


@pytest.mark.asyncio
async def test_one_platform_fails(monkeypatch):
    async def fake_x(self, message):
        return self._success(posted_url="https://x.example/1", public_access=True)

    async def fake_reddit(self, message):
        return self._failed("Authentication failed")

    async def fake_mastodon(self, message):
        return self._success(posted_url="https://mastodon.example/1", public_access=True)

    async def fake_devto(self, message):
        return self._success(posted_url="https://dev.to/1", public_access=True)

    async def fake_hashnode(self, message):
        return self._success(posted_url="https://hashnode.example/1", public_access=True)

    monkeypatch.setattr(XPlatform, "publish", fake_x)
    monkeypatch.setattr(RedditPlatform, "publish", fake_reddit)
    monkeypatch.setattr(MastodonPlatform, "publish", fake_mastodon)
    monkeypatch.setattr(DevToPlatform, "publish", fake_devto)
    monkeypatch.setattr(HashnodePlatform, "publish", fake_hashnode)

    service = PostingService(
        platforms=[
            XPlatform(settings=Settings()),
            RedditPlatform(settings=Settings()),
            MastodonPlatform(settings=Settings()),
            DevToPlatform(settings=Settings()),
            HashnodePlatform(settings=Settings()),
        ]
    )

    response = await service.publish("hello https://example.com")
    assert response.success is False
    assert response.failed_platforms == 1
    assert any(result.platform == "Reddit" and result.status == "failed" for result in response.results)


@pytest.mark.asyncio
async def test_multiple_platform_failures(monkeypatch):
    async def fail_all(self, message):
        return self._failed("API failure")

    monkeypatch.setattr(XPlatform, "publish", fail_all)
    monkeypatch.setattr(RedditPlatform, "publish", fail_all)
    monkeypatch.setattr(MastodonPlatform, "publish", fail_all)
    monkeypatch.setattr(DevToPlatform, "publish", fail_all)
    monkeypatch.setattr(HashnodePlatform, "publish", fail_all)

    service = PostingService(
        platforms=[
            XPlatform(settings=Settings()),
            RedditPlatform(settings=Settings()),
            MastodonPlatform(settings=Settings()),
            DevToPlatform(settings=Settings()),
            HashnodePlatform(settings=Settings()),
        ]
    )

    response = await service.publish("hello https://example.com")
    assert response.success is False
    assert response.failed_platforms == 5
    assert response.successful_platforms == 0


@pytest.mark.asyncio
async def test_auth_failure(monkeypatch):
    async def fake_reddit(self, message):
        return self._failed("Authentication failed")

    monkeypatch.setattr(RedditPlatform, "publish", fake_reddit)
    service = PostingService(platforms=[RedditPlatform(settings=Settings())])
    response = await service.publish("hello https://example.com")
    assert response.success is False
    assert any(result.error and "Authentication failed" in result.error for result in response.results)


@pytest.mark.asyncio
async def test_network_timeout(monkeypatch):
    async def fake_timeout(self, message):
        return self._failed("X API request timed out.")

    monkeypatch.setattr(XPlatform, "publish", fake_timeout)
    service = PostingService(platforms=[XPlatform(settings=Settings(X_ACCESS_TOKEN="token"))])
    response = await service.publish("hello https://example.com")
    assert response.success is False
    assert response.failed_platforms == 1


@pytest.mark.asyncio
async def test_missing_api_credentials(monkeypatch):
    async def fake_missing(self, message):
        return self._failed("X API credentials are missing. Configure X_ACCESS_TOKEN.")

    monkeypatch.setattr(XPlatform, "publish", fake_missing)
    service = PostingService(platforms=[XPlatform(settings=Settings())])
    response = await service.publish("hello https://example.com")
    assert response.success is False
    assert any(result.platform == "X" and result.status == "failed" for result in response.results)


@pytest.mark.asyncio
async def test_unexpected_api_response(monkeypatch):
    async def fake_bad(self, message):
        return self._failed("Unexpected X API response format.")

    monkeypatch.setattr(XPlatform, "publish", fake_bad)
    service = PostingService(platforms=[XPlatform(settings=Settings(X_ACCESS_TOKEN="token"))])
    response = await service.publish("hello https://example.com")
    assert response.success is False
    assert any(result.error and "unexpected" in result.error.lower() for result in response.results)
