from sqlmodel import Session, create_engine

engine = create_engine("sqlite:///./database.db")


def db_session():
    with Session(engine) as session:
        yield session
