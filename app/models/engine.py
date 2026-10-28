from sqlmodel import Session, create_engine

from app.core.settings import settings

engine = create_engine(
    settings.DB_URL,
    connect_args={"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {},
)


def db_session():
    with Session(engine) as session:
        yield session
