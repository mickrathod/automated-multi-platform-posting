from __future__ import annotations

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DevToPlatform(BasePlatform):
    name = "DEV.to"

    def __init__(self, settings: Settings):
        super().__init__(settings=settings)
        self.api_key = settings.DEVTO_API_KEY

    async def publish(self, message: str) -> PlatformResult:
        if not self.api_key:
            return self._failed("DEV.to API key is missing. Configure DEVTO_API_KEY.")

        title = message.strip()[:80].strip() or "Automated Post"

        try:
            response = await self.client.post(
                "https://dev.to/api/articles",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/vnd.forem.api-v1+json",
                    "api-key": self.api_key,
                },
                json={
                    "article": {
                        "title": title,
                        "body_markdown": message,
                        "published": True,
                        "tags": ["api", "automation", "fastapi"],
                    }
                },
            )
            payload = response.json() if response.content else {}
            if response.status_code in (200, 201):
                posted_url = payload.get("url")
                return self._success(posted_url=posted_url, public_access=True)
            error_text = payload.get("error") or payload.get("errors") or response.text
            return self._failed(f"DEV.to API error {response.status_code}: {error_text}")
        except httpx.TimeoutException:
            return self._failed("DEV.to API request timed out.")
        except httpx.HTTPError as exc:
            return self._failed(f"Network error while contacting DEV.to API: {exc}")
        except ValueError:
            return self._failed("Unexpected DEV.to API response format.")
