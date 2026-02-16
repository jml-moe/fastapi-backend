from app.models.database import User
from sqlmodel import Session
from app.models.engine import db_session
from app.modules.auth.utils import validate_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()  # fetch({ headers: { Authorization: "Bearer <token>"} })


def get_current_user(token=Depends(security), db: Session = Depends(db_session)):
    current_user = validate_token(token.credentials)
    if not current_user:
        raise HTTPException(401, "Invalid token")

    user = db.get(User, current_user.get("id"))
    if not user:
        raise HTTPException("User not found!")

    return user
