import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Dev-only fallback; in production set JWT_SECRET via a secret manager.
SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me-in-production-32b")
ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=1)

bearer_scheme = HTTPBearer(auto_error=False)


class TokenRequest(BaseModel):
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def issue_token(subject: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": now, "exp": now + TOKEN_TTL, **(extra or {})}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def require_auth(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    try:
        return jwt.decode(creds.credentials, SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
