from sqlmodel import Session, SQLModel, create_engine

from .settings import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


def get_session():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
