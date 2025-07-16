"""
Main FastAPI application for devenviro with Sentry integration.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from .sentry_config import init_sentry, capture_exception, capture_message, set_user_context
from .monitoring import ErrorTracker

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize error tracker
error_tracker = ErrorTracker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    """
    # Startup
    environment = os.getenv("ENVIRONMENT", "development")
    init_sentry(
        dsn="https://3f4240883d9c2ac20e4d339d5aed2b6d@o4509669791760384.ingest.de.sentry.io/4509679484272720",
        environment=environment,
        enable_tracing=True,
        enable_profiling=True,
        debug=environment == "development"
    )
    
    capture_message("DevEnviro FastAPI application started", level="info")
    logger.info("DevEnviro FastAPI application started")
    
    yield
    
    # Shutdown
    capture_message("DevEnviro FastAPI application stopped", level="info")
    logger.info("DevEnviro FastAPI application stopped")


# Create FastAPI app
app = FastAPI(
    title="DevEnviro API",
    description="Cognitive Collaboration System - AI-powered memory and knowledge management",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    sentry_enabled: bool


class ErrorTestRequest(BaseModel):
    error_type: str
    message: Optional[str] = "Test error"
    user_id: Optional[str] = None


class MemoryRequest(BaseModel):
    content: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    created_at: str
    user_id: str


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that captures exceptions with Sentry.
    """
    capture_exception(exc, request_url=str(request.url), method=request.method)
    error_tracker.log_error(exc, {"request_url": str(request.url), "method": request.method})
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. It has been logged for investigation."
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP exception handler.
    """
    if exc.status_code >= 500:
        capture_exception(exc, request_url=str(request.url), method=request.method)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """
    Root endpoint with health check.
    """
    return HealthResponse(
        status="healthy",
        environment=os.getenv("ENVIRONMENT", "development"),
        version="0.1.0",
        sentry_enabled=True
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    """
    return HealthResponse(
        status="healthy",
        environment=os.getenv("ENVIRONMENT", "development"),
        version="0.1.0",
        sentry_enabled=True
    )


@app.post("/test-error")
async def test_error(request: ErrorTestRequest):
    """
    Test endpoint for Sentry error reporting.
    """
    if request.user_id:
        set_user_context(request.user_id)
    
    if request.error_type == "exception":
        raise Exception(request.message)
    elif request.error_type == "http":
        raise HTTPException(status_code=400, detail=request.message)
    elif request.error_type == "message":
        capture_message(request.message or "Test error message", level="error")
        return {"message": "Error message captured"}
    else:
        raise HTTPException(status_code=400, detail="Invalid error_type")


@app.post("/memories", response_model=MemoryResponse)
async def create_memory(request: MemoryRequest):
    """
    Create a new memory entry.
    """
    try:
        # Set user context for Sentry
        set_user_context(request.user_id)
        
        # Placeholder for actual memory creation logic
        # In real implementation, this would integrate with mem0ai
        memory_id = f"mem_{hash(request.content)}"
        
        capture_message(f"Memory created for user {request.user_id}", level="info")
        
        return MemoryResponse(
            memory_id=memory_id,
            content=request.content,
            created_at="2025-01-01T00:00:00Z",  # Would be actual timestamp
            user_id=request.user_id
        )
    except Exception as e:
        capture_exception(e, user_id=request.user_id, content_length=len(request.content))
        raise HTTPException(status_code=500, detail="Failed to create memory")


@app.get("/memories/{user_id}")
async def get_user_memories(user_id: str):
    """
    Get memories for a specific user.
    """
    try:
        set_user_context(user_id)
        
        # Placeholder for actual memory retrieval logic
        # In real implementation, this would integrate with mem0ai
        memories = [
            {
                "memory_id": "mem_example",
                "content": "Example memory content",
                "created_at": "2025-01-01T00:00:00Z",
                "user_id": user_id
            }
        ]
        
        return {"memories": memories}
    except Exception as e:
        capture_exception(e, user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve memories")


@app.get("/system/status")
async def system_status():
    """
    Get system status information.
    """
    try:
        status = error_tracker.health_check()
        return status
    except Exception as e:
        capture_exception(e)
        raise HTTPException(status_code=500, detail="Failed to get system status")


@app.get("/sentry-debug")
async def trigger_error():
    """
    Debug endpoint to trigger a division by zero error for Sentry testing.
    """
    raise Exception("Division by zero error for Sentry testing")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )