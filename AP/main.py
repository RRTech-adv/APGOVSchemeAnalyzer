from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import upload, chat, extract, districts, categories, history, auth
from services.db_service import DatabaseService
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    db_service = DatabaseService()
    print(f"Database initialized at: {settings.DATABASE_PATH}")
    yield
    # Shutdown: Cleanup if needed
    pass

app = FastAPI(
    title="Arunachal Schemes Backend",
    description="Backend API for managing district-wise Arunachal Pradesh scheme data with Gemini LLM",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(extract.router)
app.include_router(districts.router)
app.include_router(categories.router)
app.include_router(history.router)

@app.get("/")
async def root():
    return {
        "message": "Arunachal Schemes Backend API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "login": "POST /auth/login",
                "verify": "GET /auth/verify"
            },
            "upload": "/upload",
            "chat": "/chat",
            "extract": "/extract/{document_id}",
            "districts": "/districts",
            "create_district": "POST /districts",
            "district_data": "/districts/{district_name}",
            "district_analytics": "/districts/{district_name}/analytics",
            "delete_district": "DELETE /districts/{district_name}",
            "categories": "/categories",
            "history": "/history/{district_name}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": settings.DATABASE_PATH}

if __name__ == "__main__":
    import uvicorn
    # Configure timeouts for large file uploads and processing
    # timeout_keep_alive keeps connections alive, timeout_graceful_shutdown for cleanup
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=600,  # 10 minutes - allow long uploads to complete
        timeout_graceful_shutdown=30
    )

