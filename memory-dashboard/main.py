#!/usr/bin/env python3
"""
ApexSigma DevEnviro Memory Analytics Dashboard
Modern web interface for memory management and analytics
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

# Add parent directory to path for importing devenviro modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from devenviro.gemini_memory_engine import get_gemini_memory_engine
    from devenviro.memory_bridge import get_memory_bridge
except ImportError as e:
    print(f"Warning: Could not import DevEnviro modules: {e}")
    get_gemini_memory_engine = None
    get_memory_bridge = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DevEnviro Memory Analytics Dashboard",
    description="Cognitive Memory Management and Analytics Interface",
    version="1.0.0"
)

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Pydantic models
class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 10
    category_filter: Optional[str] = None
    importance_threshold: int = 1

class MemoryStoreRequest(BaseModel):
    content: str
    category: str = "general"
    importance: int = 5
    metadata: Optional[Dict[str, Any]] = None

class MemoryExtractionRequest(BaseModel):
    content: str
    context: Optional[Dict[str, Any]] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        if not get_gemini_memory_engine:
            return {"error": "Memory engine not available"}
        
        engine = await get_gemini_memory_engine()
        bridge = await get_memory_bridge()
        
        # Get performance stats
        performance_stats = engine.get_performance_stats()
        
        # Get system health
        system_health = await bridge.health_check()
        
        # Get memory distribution by categories
        categories_data = {}
        for category in ["factual", "procedural", "episodic", "semantic", "organizational", "architectural", "temporal"]:
            results = await engine.search_memory(
                query="",
                limit=1000,
                category_filter=category
            )
            categories_data[category] = len(results)
        
        # Get recent activity
        recent_activity = [
            {"type": "search", "count": performance_stats["searches"], "timestamp": "recent"},
            {"type": "extraction", "count": performance_stats["extractions"], "timestamp": "recent"},
            {"type": "storage", "count": performance_stats["stores"], "timestamp": "recent"}
        ]
        
        return {
            "total_memories": sum(categories_data.values()),
            "categories": categories_data,
            "recent_activity": recent_activity,
            "performance_stats": performance_stats,
            "system_health": system_health
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        return {"error": str(e)}

@app.post("/api/memory/search")
async def search_memory(request: MemorySearchRequest):
    """Search memories with intelligent ranking"""
    try:
        if not get_gemini_memory_engine:
            raise HTTPException(status_code=503, detail="Memory engine not available")
        
        engine = await get_gemini_memory_engine()
        results = await engine.search_memory(
            query=request.query,
            limit=request.limit,
            category_filter=request.category_filter,
            importance_threshold=request.importance_threshold
        )
        
        return {"results": results, "query": request.query, "total": len(results)}
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")

@app.post("/api/memory/extract")
async def extract_memory(request: MemoryExtractionRequest):
    """Extract memories from content using Gemini intelligence"""
    try:
        if not get_gemini_memory_engine:
            raise HTTPException(status_code=503, detail="Memory engine not available")
        
        engine = await get_gemini_memory_engine()
        result = await engine.extract_memory(request.content, request.context)
        
        return result
    except Exception as e:
        logger.error(f"Memory extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Memory extraction failed: {str(e)}")

@app.post("/api/memory/store")
async def store_memory(request: MemoryStoreRequest):
    """Store a memory in the system"""
    try:
        if not get_memory_bridge:
            raise HTTPException(status_code=503, detail="Memory bridge not available")
        
        bridge = await get_memory_bridge()
        result = await bridge.store_memory(
            content=request.content,
            category=request.category,
            metadata=request.metadata
        )
        
        return result
    except Exception as e:
        logger.error(f"Memory storage failed: {e}")
        raise HTTPException(status_code=500, detail=f"Memory storage failed: {str(e)}")

@app.get("/api/dashboard/memories")
async def get_all_memories(limit: int = 100, category: Optional[str] = None, importance: int = 1):
    """Get all memories with filtering options"""
    try:
        if not get_gemini_memory_engine:
            raise HTTPException(status_code=503, detail="Memory engine not available")
        
        engine = await get_gemini_memory_engine()
        
        results = await engine.search_memory(
            query="",  # Empty query to get all
            limit=limit,
            category_filter=category,
            importance_threshold=importance
        )
        
        return {"memories": results, "total": len(results)}
    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memories: {str(e)}")

@app.get("/api/system/health")
async def detailed_health_check():
    """Detailed health check for all system components"""
    try:
        if not get_memory_bridge or not get_gemini_memory_engine:
            return {
                "overall_status": "degraded",
                "error": "Memory modules not available",
                "timestamp": "2025-07-17T11:30:00Z"
            }
        
        bridge = await get_memory_bridge()
        engine = await get_gemini_memory_engine()
        
        bridge_health = await bridge.health_check()
        engine_health = await engine.health_check()
        
        overall_status = "healthy"
        for component_status in list(bridge_health.values()) + list(engine_health.values()):
            if "error" in str(component_status) or component_status == "degraded":
                overall_status = "degraded"
                break
        
        return {
            "overall_status": overall_status,
            "memory_bridge": bridge_health,
            "memory_engine": engine_health,
            "timestamp": "2025-07-17T11:30:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": "2025-07-17T11:30:00Z"
        }

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Memory search interface"""
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Memory analytics and visualization page"""
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/extract", response_class=HTMLResponse)
async def extract_page(request: Request):
    """Memory extraction interface"""
    return templates.TemplateResponse("extract.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8090,
        reload=True,
        log_level="info"
    )