from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.models.database import User
from app.models.engine import db_session
from app.modules.auth.utils import validate_token

security = HTTPBearer()  # fetch({ headers: { Authorization: "Bearer <token>"} })


def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(db_session)],
):
    current_user = validate_token(token.credentials)
    if not current_user:
        raise HTTPException(401, "Invalid token")

    user = db.get(User, current_user.get("id"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found!")

    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Hanya Admin yang boleh mengakses ini")
    return user
