from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Optional
import datetime
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    str(settings.DATABASE_URL),
    echo = settings.DEBUG,
    pool_pre_ping = True,
    pool_size = 10,
    max_overflow = 20
)

SessionLocal = sessionmaker(
    autocommit = False,
    Autoflush = False,
    bind = engine,
    class_ = Session,
    expire_on_commit = False
)

class BaseModel(SQLModel):
    """Base model witn common fields"""
    id: Optional[int] = Field(default = None, primary_key = True)
    created_at: datetime.datetime = Field(
        default_factory = datetime.datetime.utcnow,
        nullable = False
    )

    updated_at: datetime.datetime = Field(
        default_factory = datetime.datetime.utcnow,
        nullable = False,
        sa_column_kwargs = {"onupdate": datetime.datetime.utcnow}
    )

    class Config:
        validate_assignment = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)