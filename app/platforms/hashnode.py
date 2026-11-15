from __future__ import annotations

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class HashnodePlatform(BasePlatform):
    name = "Hashnode"

    def __init__(self, settings: Settings):
        super().__init__(settings=settings)
        self.api_key = settings.HASHNODE_API_KEY
        self.publication_id = settings.HASHNODE_PUBLICATION_ID
        self.endpoint = settings.HASHNODE_ENDPOINT

    async def _create_draft(self, title: str, content: str) -> str | None:
        mutation = """
        mutation CreateDraft($input: CreateDraftInput!) {
          createDraft(input: $input) {
            draft {
              id
            }
          }
        }
        """

        variables = {
            "input": {
                "publicationId": self.publication_id,
                "title": title,
                "contentMarkdown": content,
                "tags": [{"name": "api", "slug": "api"}],
                "enableToc": True,
            }
        }

        response = await self.client.post(
            self.endpoint,
            json={"query": mutation, "variables": variables},
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        payload = response.json() if response.content else {}
        if response.status_code != 200:
            return None
        if payload.get("errors"):
            return None
        return payload.get("data", {}).get("createDraft", {}).get("draft", {}).get("id")

    async def _publish_draft(self, draft_id: str) -> str | None:
        mutation = """
        mutation PublishDraft($input: PublishDraftInput!) {
          publishDraft(input: $input) {
            post {
              url
            }
          }
        }
        """

        variables = {"input": {"draftId": draft_id}}

        response = await self.client.post(
            self.endpoint,
            json={"query": mutation, "variables": variables},
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        payload = response.json() if response.content else {}
        if response.status_code != 200:
            return None
        if payload.get("errors"):
            return None
        return payload.get("data", {}).get("publishDraft", {}).get("post", {}).get("url")

    async def publish(self, message: str) -> PlatformResult:
        if not self.api_key or not self.publication_id:
            return self._failed(
                "Hashnode credentials are missing. Configure HASHNODE_API_KEY and HASHNODE_PUBLICATION_ID."
            )

        title = message.strip()[:80].strip() or "Automated Post"
        try:
            draft_id = await self._create_draft(title, message)
            if not draft_id:
                return self._failed("Hashnode draft creation failed or credentials are invalid.")
            posted_url = await self._publish_draft(draft_id)
            if not posted_url:
                return self._failed("Hashnode publishDraft failed or API returned no URL.")
            return self._success(posted_url=posted_url, public_access=True)
        except httpx.TimeoutException:
            return self._failed("Hashnode API request timed out.")
        except httpx.HTTPError as exc:
            return self._failed(f"Network error while contacting Hashnode API: {exc}")
        except ValueError:
            return self._failed("Unexpected Hashnode API response format.")
