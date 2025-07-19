#!/usr/bin/env python3
"""
ApexSigma DevEnviro Memory Analytics Dashboard Server
FastAPI backend for responsive memory management and analytics
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our memory engine
from gemini_memory_engine import (
    GeminiMemoryEngine,
    get_gemini_memory_engine,
    extract_and_store_memory,
    search_organizational_memory,
    restore_session_continuity_brief,
    get_chronological_session_context
)

# FastAPI app setup
app = FastAPI(
    title="DevEnviro Memory Analytics Dashboard",
    description="Cognitive collaboration platform with intelligent memory management",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MemoryExtractionRequest(BaseModel):
    content: str
    context: Optional[Dict[str, Any]] = None

class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 10
    category_filter: Optional[str] = None
    importance_threshold: int = 1

class SessionCaptureRequest(BaseModel):
    session_summary: str

# Dashboard routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard interface"""
    return await get_dashboard_html()

@app.get("/api/health")
async def health_check():
    """System health check endpoint"""
    try:
        engine = await get_gemini_memory_engine()
        health = await engine.health_check()
        stats = engine.get_performance_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": health,
            "performance": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/api/memories/stats")
async def get_memory_stats():
    """Get comprehensive memory statistics"""
    try:
        engine = await get_gemini_memory_engine()
        stats = engine.get_performance_stats()
        
        # Get memory distribution by category
        recent_memories = await engine.search_memory(
            query="",
            limit=100,
            importance_threshold=1
        )
        
        category_distribution = {}
        importance_distribution = {}
        
        for memory in recent_memories:
            category = memory.get("category", "unknown")
            importance = memory.get("importance", 0)
            
            category_distribution[category] = category_distribution.get(category, 0) + 1
            importance_range = f"{importance//2*2}-{importance//2*2+1}"
            importance_distribution[importance_range] = importance_distribution.get(importance_range, 0) + 1
        
        return {
            "total_memories": len(recent_memories),
            "category_distribution": category_distribution,
            "importance_distribution": importance_distribution,
            "performance_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.post("/api/memories/extract")
async def extract_memory_endpoint(request: MemoryExtractionRequest):
    """Extract and store memories from content"""
    try:
        result = await extract_and_store_memory(request.content, request.context)
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory extraction failed: {str(e)}")

@app.post("/api/memories/search")
async def search_memory_endpoint(request: MemorySearchRequest):
    """Search memories with filters"""
    try:
        engine = await get_gemini_memory_engine()
        results = await engine.search_memory(
            query=request.query,
            limit=request.limit,
            category_filter=request.category_filter,
            importance_threshold=request.importance_threshold
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {str(e)}")

@app.get("/api/memories/recent")
async def get_recent_memories():
    """Get recent memories for dashboard display"""
    try:
        recent_memories = await search_organizational_memory(
            query="recent important decisions implementations",
            limit=10
        )
        
        return {
            "success": True,
            "memories": recent_memories,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recent memories retrieval failed: {str(e)}")

@app.get("/api/sessions/continuity")
async def get_session_continuity():
    """Get session continuity context"""
    try:
        continuity = await restore_session_continuity_brief()
        chronological = await get_chronological_session_context(hours_back=168)  # 1 week
        
        return {
            "success": True,
            "continuity_brief": continuity,
            "chronological_context": chronological[:10],  # Last 10 episodes
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session continuity retrieval failed: {str(e)}")

@app.post("/api/sessions/capture")
async def capture_session_endpoint(request: SessionCaptureRequest):
    """Capture session for continuity"""
    try:
        from gemini_memory_engine import capture_session_episodic_memory
        result = await capture_session_episodic_memory(request.session_summary)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session capture failed: {str(e)}")

@app.get("/api/analytics/trends")
async def get_analytics_trends():
    """Get trending analytics for the dashboard"""
    try:
        # Get memories from last 7 days
        chronological = await get_chronological_session_context(hours_back=168)
        
        # Create daily activity chart data
        daily_activity = {}
        category_trends = {}
        
        for item in chronological:
            timestamp = item["timestamp"]
            memory = item["memory"]
            
            day_key = timestamp.strftime("%Y-%m-%d")
            daily_activity[day_key] = daily_activity.get(day_key, 0) + 1
            
            category = memory.get("category", "unknown")
            if category not in category_trends:
                category_trends[category] = {}
            category_trends[category][day_key] = category_trends[category].get(day_key, 0) + 1
        
        # Fill missing days with 0
        today = datetime.now()
        for i in range(7):
            day = today - timedelta(days=i)
            day_key = day.strftime("%Y-%m-%d")
            if day_key not in daily_activity:
                daily_activity[day_key] = 0
        
        return {
            "success": True,
            "daily_activity": daily_activity,
            "category_trends": category_trends,
            "total_memories": len(chronological),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics trends retrieval failed: {str(e)}")

async def get_dashboard_html():
    """Generate the responsive dashboard HTML"""
    from dashboard_multi_page import get_multi_page_dashboard_html
    return get_multi_page_dashboard_html()

def start_dashboard_server(host: str = "127.0.0.1", port: int = 8090):
    """Start the dashboard server"""
    print(f"Starting DevEnviro Memory Analytics Dashboard on {host}:{port}")
    print(f"Dashboard URL: http://{host}:{port}")
    
    # Check if we're in an async context
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        print("[INFO] Running in async context, creating server task...")
        # We're in an async context, so we need to run the server differently
        import threading
        
        def run_server():
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info",
                reload=False
            )
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        print(f"[SUCCESS] Dashboard server started on {host}:{port}")
        print("[INFO] Server is running in background thread")
        
        # Keep the main thread alive
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Stopping dashboard server...")
            
    except RuntimeError:
        # No event loop running, can use uvicorn.run directly
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )

if __name__ == "__main__":
    start_dashboard_server()