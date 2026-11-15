from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod

import httpx

from app.config import Settings
from app.schemas import PlatformResult


class BasePlatform(ABC):
    name: str

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS)

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        raise NotImplementedError

    def _success(self, posted_url: str | None = None, public_access: bool = True) -> PlatformResult:
        now_utc = dt.datetime.now(dt.timezone.utc)
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=now_utc.strftime("%Y-%m-%d"),
            time=now_utc.strftime("%H:%M:%S"),
            error=None,
        )

    def _failed(
        self,
        error: str,
        posted_url: str | None = None,
        public_access: bool = False,
    ) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="failed",
            posted_url=posted_url,
            public_access=public_access,
            date=None,
            time=None,
            error=error,
        )
