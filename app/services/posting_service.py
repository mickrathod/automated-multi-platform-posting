from __future__ import annotations

import asyncio

from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingResponse


class PostingService:
    def __init__(self, platforms: list[BasePlatform]):
        self.platforms = platforms

    async def publish(self, message: str) -> PostingResponse:
        async def run_single(platform: BasePlatform) -> PlatformResult:
            try:
                return await platform.publish(message)
            except Exception as exc:  # pragma: no cover
                return PlatformResult(
                    platform=platform.name,
                    status="failed",
                    posted_url=None,
                    public_access=False,
                    date=None,
                    time=None,
                    error=f"Unhandled platform error: {exc}",
                )

        results = await asyncio.gather(*(run_single(platform) for platform in self.platforms))
        successful = sum(1 for result in results if result.status == "success")
        failed = len(results) - successful

        return PostingResponse(
            success=(failed == 0),
            total_platforms=len(results),
            successful_platforms=successful,
            failed_platforms=failed,
            results=list(results),
        )
