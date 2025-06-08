import asyncio
from .core.database import engine, create_db_and_tables
from sqlmodel import text

async def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        create_db_and_tables()
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())