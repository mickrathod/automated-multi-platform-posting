from __future__ import annotations

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    def __init__(self, settings: Settings):
        super().__init__(settings=settings)
        self.instance_url = (settings.MASTODON_INSTANCE_URL or "").rstrip("/")
        self.token = settings.MASTODON_ACCESS_TOKEN

    async def publish(self, message: str) -> PlatformResult:
        if not self.instance_url or not self.token:
            return self._failed(
                "Mastodon credentials are missing. Configure MASTODON_INSTANCE_URL and MASTODON_ACCESS_TOKEN."
            )

        try:
            response = await self.client.post(
                f"{self.instance_url}/api/v1/statuses",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={"status": message, "visibility": "unlisted"},
            )
            payload = response.json() if response.content else {}
            if response.status_code in (200, 201):
                posted_url = payload.get("url")
                return self._success(posted_url=posted_url, public_access=True)
            error_text = payload.get("error") or payload.get("detail") or response.text
            return self._failed(f"Mastodon API error {response.status_code}: {error_text}")
        except httpx.TimeoutException:
            return self._failed("Mastodon API request timed out.")
        except httpx.HTTPError as exc:
            return self._failed(f"Network error while contacting Mastodon API: {exc}")
        except ValueError:
            return self._failed("Unexpected Mastodon API response format.")
