# Automated Multi-Platform Posting System

A FastAPI-based service that accepts a short marketing or announcement message with exactly one CTA URL and publishes it across multiple social platforms using official APIs.

## Features

- REST API for posting a message with a single URL
- Pydantic validation for request rules
- Async HTTP publishing to five platforms
- Isolated platform failure handling
- UTC timestamps stored in results
- Modular platform adapters and service layer
- Swagger documentation via FastAPI

## Supported Platforms

- X (Twitter)
- Reddit
- Mastodon
- DEV.to
- Hashnode

## Technology Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- httpx
- pydantic-settings
- Pytest
- pytest-asyncio

## Project Structure

```text
automated-posting/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   ├── dependencies.py
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── x.py
│   │   ├── reddit.py
│   │   ├── mastodon.py
│   │   ├── devto.py
│   │   └── hashnode.py
│   └── services/
│       ├── __init__.py
│       └── posting_service.py
├── tests/
│   ├── __init__.py
│   ├── test_validation.py
│   ├── test_platforms.py
│   └── test_posting.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Official API Docs

- X API: https://developer.x.com/en/docs/x-api
- Reddit API: https://www.reddit.com/dev/api/
- Mastodon API: https://docs.joinmastodon.org/
- DEV.to API: https://developers.forem.com/api
- Hashnode GraphQL API: https://hashnode.com/

## Environment Setup

Copy `.env.example` to `.env` and fill in required values.

## Install

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

Swagger docs: http://localhost:4000/docs

## Example Request

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

## Example Response

```json
{
  "success": false,
  "total_platforms": 5,
  "successful_platforms": 4,
  "failed_platforms": 1,
  "results": [
    {
      "platform": "X",
      "status": "success",
      "posted_url": "https://x.com/i/web/status/123",
      "public_access": true,
      "date": "2026-11-15",
      "time": "10:30:00",
      "error": null
    },
    {
      "platform": "Reddit",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Reddit credentials are missing."
    }
  ]
}
```

## Run Tests

```bash
pytest -v
```

## Security Notes

- Never commit `.env` files.
- Keep tokens in environment variables.
- Do not log secrets.
- Validate URLs and input strings tightly.

## Known Limitations

- Real posting requires valid credentials and platform-specific permissions.
- Some APIs enforce rate limits or scoped tokens.
- Hashnode requires a publication ID and GraphQL API access.
- No live posts are performed in this environment.
