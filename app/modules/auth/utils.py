import logging
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.settings import settings

logger = logging.getLogger(__name__)


def hash_password(plain_password: str):
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def is_password_valid(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def generate_token(data: dict):
    copied_data = data.copy()
    copied_data["exp"] = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(copied_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def validate_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        logger.info("Token expired")
    except InvalidTokenError as e:
        logger.info("Token invalid: %s", e)
    return None
