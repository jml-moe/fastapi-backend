from sqlalchemy.exc import IntegrityError
from app.modules.auth.utils import hash_password, is_password_valid
from app.models.database import User
from app.models.engine import db_session
from sqlmodel import Session, select
from app.modules.auth.schema import RegisterUser, LoginUser
from fastapi import APIRouter, Depends, HTTPException, status

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(body: RegisterUser, db: Session = Depends(db_session)):

    try:
        hashed_password = hash_password(body.password)
        new_user = User(name=body.name, email=body.email, password=hashed_password)
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        print(e)
        raise HTTPException(status.HTTP_409_CONFLICT, detail="User already exist!")
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Bad Request")

    return {"message": "User register success!"}


@auth_router.post("/login")
def login_user(body: LoginUser, db: Session = Depends(db_session)):

    user = db.exec(select(User).where(User.email == body.email)).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")

    if not is_password_valid(body.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")

    # Give token / access

    return {"message": "User login success!!"}
