from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES

security = HTTPBearer(auto_error=False)

USERS = {
    settings.ADMIN_USERNAME: settings.ADMIN_PASSWORD,
}


def verify_password(plain: str, expected: str) -> bool:
    return plain == expected


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    return payload.get("sub")


async def require_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    user = await get_current_user(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
