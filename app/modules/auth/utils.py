import bcrypt


def hash_password(plain_password: str):
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def is_password_valid(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
