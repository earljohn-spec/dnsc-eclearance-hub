"""
Security Primitives for DNSC e-Clearance Hub
Requirements covered: R11 (Auth), R12 (RBAC), R13 (Hashing & Cryptography)
"""

import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
import bcrypt
import jwt
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.schemas import UserRole

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "DEV_ONLY_SECRET_KEY_CHANGE_IN_PRODUCTION_32BYTES")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1

security_bearer = HTTPBearer(auto_error=True)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with cost factor 12."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(
    subject: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed HMAC-SHA256 JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=TOKEN_EXPIRE_HOURS)

    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role.value,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer)
) -> Dict[str, Any]:
    """FastAPI dependency to extract and validate the current authenticated user."""
    token = credentials.credentials
    return decode_access_token(token)


class RoleChecker:
    """FastAPI dependency wrapper for enforcing specific UserRole access."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = [r.value for r in allowed_roles]

    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user
