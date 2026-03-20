import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.db.session import get_db
from app.dependencies.config import AppConfig, get_config
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def create_access_token(user_id: int, config: AppConfig) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    config: AppConfig = Depends(get_config),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials, config.jwt_secret, algorithms=[config.jwt_algorithm]
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise UnauthorizedError("Invalid or expired token")

    user = db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise UnauthorizedError("User not found or inactive")
    return user
