from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Automated Posting System"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 4000

    X_API_KEY: str | None = None
    X_API_SECRET: str | None = None
    X_ACCESS_TOKEN: str | None = None
    X_ACCESS_TOKEN_SECRET: str | None = None

    REDDIT_CLIENT_ID: str | None = None
    REDDIT_CLIENT_SECRET: str | None = None
    REDDIT_USERNAME: str | None = None
    REDDIT_PASSWORD: str | None = None
    REDDIT_USER_AGENT: str | None = None
    REDDIT_SUBREDDIT: str = "test"

    MASTODON_INSTANCE_URL: str | None = None
    MASTODON_ACCESS_TOKEN: str | None = None

    DEVTO_API_KEY: str | None = None

    HASHNODE_API_KEY: str | None = None
    HASHNODE_PUBLICATION_ID: str | None = None
    HASHNODE_ENDPOINT: str = "https://gql.hashnode.com"

    REQUEST_TIMEOUT_SECONDS: float = 20.0


settings = Settings()
