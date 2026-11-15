# Automated Multi-Platform Posting System

A production-oriented Python 3.12 + FastAPI service that accepts a short message containing exactly one CTA URL and publishes it across multiple third-party platforms through their official APIs.

## Overview

This project accepts a `message` via REST API and automatically posts it to:

- X (Twitter)
- Reddit
- Mastodon
- DEV.to
- Hashnode

The caller does not specify which platforms to use. Platform selection is internal and automatic, and each platform is processed independently.

## Features

- FastAPI REST API with Swagger documentation
- Pydantic validation for message and URL rules
- Async HTTP publishing using `httpx`
- Concurrent platform publishing with `asyncio.gather`
- Fail-safe execution: one platform failure does not stop others
- Unified result format for each platform
- Environment-based API credential configuration
- Pytest-based automated testing with mocked responses

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
├── README.md
├── python-post-message.md
└── .env
```

## Official API Documentation

- X API: https://developer.x.com/en/docs/x-api
- Reddit API: https://www.reddit.com/dev/api/
- Mastodon API: https://docs.joinmastodon.org/
- DEV.to API: https://developers.forem.com/api
- Hashnode GraphQL API: https://hashnode.com/

## Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in the required values
3. Never commit `.env` to version control

```bash
cp .env.example .env
```

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

Swagger docs:
- http://localhost:4000/docs

## Example Request

```http
POST /posting
Content-Type: application/json

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
      "error": "Authentication failed"
    }
  ]
}
```

## Run Tests

```bash
pytest -v
```

## Security Notes

- Never commit `.env`
- Do not log API secrets
- Store credentials in environment variables only
- Validate URLs and message content before publishing

## Known Limitations

- Real posting requires valid API keys and platform permissions
- Some platforms impose rate limits and account-level restrictions
- Hashnode requires a valid publication ID
- This environment does not publish to real services unless credentials are configured

## Final Submission Notes

This project matches the practical test specification and demonstrates:

- FastAPI REST structure
- Input validation with Pydantic
- Multi-platform async publishing
- Independent platform failure handling
- API integration patterns
- Test automation with mocked platform responses
