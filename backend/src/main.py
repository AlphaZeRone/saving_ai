from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, SQLModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from api.auth import router as auth_router
from api.transaction import router as transaction_router

load_dotenv()

# =========== Database Setup =================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/saving_ai_dev"
)

engine = create_engine(DATABASE_URL, echo = True)

def create_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# ========= Aplication Lifespan ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting AI Saving Assistant MVP")
    create_tables()
    print("✅ Database Table Create")

    yield

    print("👋 Shutting down...")

# ============ FastAPI ===============
app = FastAPI(
    title = "AI Saving Assistant - MVP", 
    version = "0.1.0",
    description = "MVP Version for academic submiossion",
    lifespan = lifespan
)

# ===== CORS Configuration ============
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# ===== Basic Routes ========
@app.get("/")
async def root():
    return {
        "message": "AI Saving Assistant MVP",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-06-10"
    }

# ======== Include Router ========

app.include_router(auth_router, prefix = "/api/auth", tags = ["Authetication"])
app.include_router(transaction_router, prefix = "/api/transactions", tags = ["Transactions"])

# ====== Testing Database Connection =========
@app.get("/test-db")
async def test_database(session: Session = Depends(get_session)):
    try:
        from sqlmodel import text
        result = session.exec(text("SELECT 1 as test")).first()

        test_value = result[0] if result else None

        return {
            "database": "connected",
            "result": test_value,
            "message": "Database Connection Successful"
        }
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"Database connection failed: {str(e)}"
        )
    
if __name__ == "__main__":
    import uvicorn

    print("Starting development server....")
    uvicorn.run(
        "main:app",
        host = "0.0.0.0",
        port = 8000,
        reload = True,
        log_level = "info"
    )
