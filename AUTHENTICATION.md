# API Authentication

This document describes how to use the authentication system for the FastAPI Crawler APIs.

## Overview

The authentication system uses API tokens stored in a PostgreSQL database. Two endpoints require authentication:
- `POST /crawl-and-send` - Crawl CoinMarketCap and send to Telegram
- `GET /coins` - Get top coins without sending to Telegram

## Database Setup

The system uses a PostgreSQL database with an `api_tokens` table:

```sql
CREATE TABLE api_tokens (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Default API Tokens

The system comes with these pre-configured tokens:

| Name | Token |
|------|-------|
| admin | admin-token-123456 |
| mobile-app | mobile-app-secret-789 |
| web-dashboard | web-dashboard-token-abc |
| monitoring-service | monitoring-service-xyz-999 |

## Making Authenticated Requests

Include the API token in the `Authorization` header of your HTTP requests.

### Format Options:

1. **Bearer token format** (recommended):
   ```
   Authorization: Bearer admin-token-123456
   ```

2. **Direct token format**:
   ```
   Authorization: admin-token-123456
   ```

### Example Requests:

#### Using curl:
```bash
# Get coins
curl -H "Authorization: Bearer admin-token-123456" \
     http://localhost:8046/coins

# Crawl and send
curl -X POST \
     -H "Authorization: Bearer admin-token-123456" \
     "http://localhost:8046/crawl-and-send?max_coins=10&send_multiple=false"
```

#### Using Python requests:
```python
import requests

headers = {"Authorization": "Bearer admin-token-123456"}

# Get coins
response = requests.get("http://localhost:8046/coins", headers=headers)
print(response.json())

# Crawl and send
response = requests.post(
    "http://localhost:8046/crawl-and-send",
    headers=headers,
    params={"max_coins": 10, "send_multiple": False}
)
print(response.json())
```

## Managing API Tokens

Use the `manage_tokens.py` script to manage API tokens:

### List all tokens:
```bash
python manage_tokens.py list
```

### Create a new token:
```bash
# Create with auto-generated token
python manage_tokens.py create my-new-client

# Create with specific token
python manage_tokens.py create my-client my-custom-token-123
```

### Delete a token:
```bash
python manage_tokens.py delete my-client
```

## Error Responses

### Missing Authorization Header:
```json
{
    "detail": "Authorization header required"
}
```
Status Code: 401

### Invalid Token:
```json
{
    "detail": "Invalid API token"
}
```
Status Code: 401

## Security Notes

1. **Token Security**: Store API tokens securely and never expose them in client-side code or logs
2. **Token Rotation**: Regularly rotate API tokens for better security
3. **Monitoring**: Monitor authentication logs for suspicious activity
4. **Environment Variables**: Consider using environment variables for sensitive tokens

## Docker Setup

The authentication system is automatically configured when using Docker Compose:

```bash
# Start all services including PostgreSQL
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs fastapi-crawler
docker-compose logs postgres
```

The PostgreSQL database will be automatically initialized with the default tokens when first started.