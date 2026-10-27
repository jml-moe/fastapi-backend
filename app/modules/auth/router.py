from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.database import User
from app.models.engine import db_session
from app.modules.auth.schema import LoginUser, RegisterUser
from app.modules.auth.utils import generate_token, hash_password, is_password_valid

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(body: RegisterUser, db: Annotated[Session, Depends(db_session)]):

    try:
        hashed_password = hash_password(body.password)
        new_user = User(name=body.name, email=body.email, password=hashed_password)
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="User already exist!"
        ) from e

    return {"message": "User register success!"}


@auth_router.post("/login")
def login_user(body: LoginUser, db: Annotated[Session, Depends(db_session)]):

    user = db.exec(select(User).where(User.email == body.email)).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")

    if not is_password_valid(body.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")

    # Give token / access -> ID
    token = generate_token({"id": user.id})

    return {"token": token}
