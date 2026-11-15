from __future__ import annotations

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class XPlatform(BasePlatform):
    name = "X"

    def __init__(self, settings: Settings):
        super().__init__(settings=settings)
        self.access_token = settings.X_ACCESS_TOKEN

    async def publish(self, message: str) -> PlatformResult:
        if not self.access_token:
            return self._failed("X API credentials are missing. Configure X_ACCESS_TOKEN.")

        try:
            response = await self.client.post(
                "https://api.twitter.com/2/tweets",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                json={"text": message},
            )
            payload = response.json() if response.content else {}
            if response.status_code in (200, 201):
                tweet_id = payload.get("data", {}).get("id")
                posted_url = f"https://x.com/i/web/status/{tweet_id}" if tweet_id else None
                return self._success(posted_url=posted_url, public_access=True)
            error_text = payload.get("errors") or payload.get("detail") or response.text
            return self._failed(f"X API error {response.status_code}: {error_text}")
        except httpx.TimeoutException:
            return self._failed("X API request timed out.")
        except httpx.HTTPError as exc:
            return self._failed(f"Network error while contacting X API: {exc}")
        except ValueError:
            return self._failed("Unexpected X API response format.")
