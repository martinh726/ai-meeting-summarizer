from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

settings.data_dir.mkdir(parents=True, exist_ok=True)

# check_same_thread=False lets background tasks (which run in other threads) use SQLite.
engine = create_engine(
    f"sqlite:///{settings.data_dir / 'app.db'}",
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one database session per request."""
    with Session(engine) as session:
        yield session
