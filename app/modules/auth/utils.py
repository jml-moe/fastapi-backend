from jose.exceptions import ExpiredSignatureError
from app.core.settings import settings
import bcrypt
from jose import jwt
from datetime import datetime, timedelta


def hash_password(plain_password: str):
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def is_password_valid(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def generate_token(data: dict):
    copied_data = data.copy()
    copied_data["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    return jwt.encode(copied_data, settings.SECRET_KEY, algorithm="HS256")


def validate_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError as e:
        print(e, "Token Expired")
        return None
    except Exception as e:
        print(e)
        return None
