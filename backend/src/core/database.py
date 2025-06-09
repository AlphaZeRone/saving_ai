from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/saving_db"
)

engine = create_engine(DATABASE_URL, echo = True)

def create_table():
    """ สร้าง Table ทั้งหมด """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# Testing 
if  __name__ == "__main__":
    print(f"Testing database connection to: {DATABASE_URL}")
    try:
        with Session(engine) as session:
            result = session.exec("SELECT 1 as test")
            print(f"✅ Database connection successful: {result.first()}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")