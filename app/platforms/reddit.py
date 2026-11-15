from __future__ import annotations

import base64

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class RedditPlatform(BasePlatform):
    name = "Reddit"

    def __init__(self, settings: Settings):
        super().__init__(settings=settings)
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.username = settings.REDDIT_USERNAME
        self.password = settings.REDDIT_PASSWORD
        self.user_agent = settings.REDDIT_USER_AGENT or "automated-posting:1.0.0 (by /u/unknown)"
        self.subreddit = settings.REDDIT_SUBREDDIT

    async def _get_access_token(self) -> str | None:
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            return None

        auth_bytes = f"{self.client_id}:{self.client_secret}".encode()
        basic_auth = base64.b64encode(auth_bytes).decode("utf-8")

        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        try:
            response = await self.client.post(
                "https://www.reddit.com/api/v1/access_token",
                data=data,
                headers={
                    "User-Agent": self.user_agent,
                    "Authorization": f"Basic {basic_auth}",
                },
            )
            if response.status_code != 200:
                return None
            payload = response.json()
            return payload.get("access_token")
        except (httpx.HTTPError, ValueError):
            return None

    async def publish(self, message: str) -> PlatformResult:
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            return self._failed(
                "Reddit credentials are missing. Configure REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, "
                "REDDIT_USERNAME, REDDIT_PASSWORD, and REDDIT_USER_AGENT."
            )

        token = await self._get_access_token()
        if not token:
            return self._failed("Failed to authenticate with Reddit API.")

        try:
            response = await self.client.post(
                "https://oauth.reddit.com/api/submit",
                data={
                    "sr": self.subreddit,
                    "title": "Automated Post",
                    "kind": "self",
                    "text": message,
                    "resubmit": True,
                    "sendreplies": True,
                },
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            payload = response.json() if response.content else {}
            if response.status_code == 200:
                url = payload.get("json", {}).get("data", {}).get("url")
                return self._success(posted_url=url, public_access=True)
            errors = payload.get("json", {}).get("errors") or payload.get("message") or response.text
            return self._failed(f"Reddit API error {response.status_code}: {errors}")
        except httpx.TimeoutException:
            return self._failed("Reddit API request timed out.")
        except httpx.HTTPError as exc:
            return self._failed(f"Network error while contacting Reddit API: {exc}")
        except ValueError:
            return self._failed("Unexpected Reddit API response format.")
