from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.db.session import get_db
from app.dependencies.auth import create_access_token, hash_password
from app.dependencies.config import AppConfig, get_config
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    config: AppConfig = Depends(get_config),
) -> TokenResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if (
        user is None
        or user.deleted_at is not None
        or user.password != hash_password(payload.password)
    ):
        raise UnauthorizedError("Invalid username or password")
    token = create_access_token(user.id, config)
    return TokenResponse(access_token=token)
