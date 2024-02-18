import logging
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Header

from database import get_db, ApiToken


logger = logging.getLogger(__name__)


async def verify_api_token(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    """
    Verify API token from Authorization header.
    Expected format: Bearer <token> or just <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    # Extract token from Authorization header
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix

    # Query database for token
    api_token = db.query(ApiToken).filter(ApiToken.token == token).first()

    if not api_token:
        logger.warning(f"Invalid API token attempted: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid API token")

    logger.info(f"Authenticated request for client: {api_token.name}")
    return api_token
