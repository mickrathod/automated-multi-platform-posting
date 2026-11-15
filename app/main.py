from __future__ import annotations

from fastapi import FastAPI

from app.config import settings
from app.platforms.devto import DevToPlatform
from app.platforms.hashnode import HashnodePlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.reddit import RedditPlatform
from app.platforms.x import XPlatform
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import PostingService

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    version="1.0.0",
    description=(
        "Publish a message with a single CTA URL across X, Reddit, Mastodon, DEV.to, and Hashnode. "
        "Platform selection is handled automatically and failures are isolated."
    ),
)

posting_service = PostingService(
    platforms=[
        XPlatform(settings=settings),
        RedditPlatform(settings=settings),
        MastodonPlatform(settings=settings),
        DevToPlatform(settings=settings),
        HashnodePlatform(settings=settings),
    ]
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME}


@app.post(
    "/posting",
    response_model=PostingResponse,
    summary="Publish message to all configured platforms",
    tags=["posting"],
    responses={
        200: {"description": "Posting attempted across all configured platforms."},
        422: {"description": "Validation failed for the input message."},
    },
)
async def create_post(payload: PostingRequest) -> PostingResponse:
    return await posting_service.publish(payload.message)
