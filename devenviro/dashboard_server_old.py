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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DevEnviro Memory Analytics Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
        <style>
            .glass-morphism {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .card-hover {
                transition: all 0.3s ease;
            }
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .nav-item {
                transition: all 0.3s ease;
            }
            .nav-item:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            .nav-item.active {
                background: rgba(255, 255, 255, 0.2);
                border-bottom: 2px solid rgba(255, 255, 255, 0.8);
            }
        </style>
    </head>
    <body class="min-h-screen gradient-bg">
        <!-- Dashboard App -->
        <div x-data="dashboardApp()" x-init="init()" class="min-h-screen">
            
            <!-- Navigation Header -->
            <nav class="glass-morphism rounded-lg m-4 mb-0">
                <div class="px-6 py-4">
                    <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div class="flex items-center space-x-4">
                            <div class="flex items-center space-x-2">
                                <div class="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h1 class="text-xl font-bold text-white">DevEnviro</h1>
                                    <p class="text-white/60 text-sm">Cognitive Collaboration Platform</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex items-center space-x-4 mt-4 md:mt-0">
                            <div class="flex items-center space-x-2">
                                <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                                <span class="text-white text-sm">System Healthy</span>
                            </div>
                            <button 
                                @click="refreshData()" 
                                class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors"
                            >
                                Refresh
                            </button>
                        </div>
                    </div>
                    
                    <!-- Navigation Menu -->
                    <div class="mt-4 flex flex-wrap gap-2">
                        <button 
                            @click="currentPage = 'dashboard'" 
                            :class="currentPage === 'dashboard' ? 'active' : ''"
                            class="nav-item px-4 py-2 rounded-lg text-white text-sm font-medium"
                        >
                            Dashboard
                        </button>
                        <button 
                            @click="currentPage = 'search'" 
                            :class="currentPage === 'search' ? 'active' : ''"
                            class="nav-item px-4 py-2 rounded-lg text-white text-sm font-medium"
                        >
                            Search Memory
                        </button>
                        <button 
                            @click="currentPage = 'knowledge'" 
                            :class="currentPage === 'knowledge' ? 'active' : ''"
                            class="nav-item px-4 py-2 rounded-lg text-white text-sm font-medium"
                        >
                            Knowledge Ingestion
                        </button>
                        <button 
                            @click="currentPage = 'analytics'" 
                            :class="currentPage === 'analytics' ? 'active' : ''"
                            class="nav-item px-4 py-2 rounded-lg text-white text-sm font-medium"
                        >
                            Deep Analytics
                        </button>
                        <button 
                            @click="currentPage = 'explorer'" 
                            :class="currentPage === 'explorer' ? 'active' : ''"
                            class="nav-item px-4 py-2 rounded-lg text-white text-sm font-medium"
                        >
                            Data Explorer
                        </button>
                    </div>
                </div>
            </nav>
            
            <!-- Page Content -->
            <div class="p-4 pt-2">
                
                <!-- Dashboard Landing Page -->
                <div x-show="currentPage === 'dashboard'" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform scale-95" x-transition:enter-end="opacity-100 transform scale-100">
                    
                    <!-- Welcome Header -->
                    <div class="glass-morphism rounded-lg p-6 mb-6 card-hover">
                        <div class="text-center">
                            <h2 class="text-2xl font-bold text-white mb-2">Welcome to DevEnviro Memory Analytics</h2>
                            <p class="text-white/80 mb-4">Your cognitive collaboration platform dashboard</p>
                            <div class="flex justify-center space-x-4">
                                <button @click="currentPage = 'search'" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                    Search Memory
                                </button>
                                <button @click="currentPage = 'knowledge'" class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                                    Add Knowledge
                                </button>
                                <button @click="currentPage = 'analytics'" class="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
                                    View Analytics
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Stats Cards -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                        <div class="glass-morphism rounded-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white/80 text-sm">Total Memories</p>
                            <p class="text-2xl font-bold text-white" x-text="stats.total_memories || 0"></p>
                        </div>
                        <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white/80 text-sm">Operations</p>
                            <p class="text-2xl font-bold text-white" x-text="stats.performance_stats?.total_operations || 0"></p>
                        </div>
                        <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white/80 text-sm">Avg Response</p>
                            <p class="text-2xl font-bold text-white" x-text="(stats.performance_stats?.average_response_time_ms || 0).toFixed(0) + 'ms'"></p>
                        </div>
                        <div class="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-white/80 text-sm">Success Rate</p>
                            <p class="text-2xl font-bold text-white" x-text="((1 - (stats.performance_stats?.error_rate || 0)) * 100).toFixed(1) + '%'"></p>
                        </div>
                        <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <!-- Memory Search -->
                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <h2 class="text-xl font-bold text-white mb-4">Memory Search</h2>
                    <div class="space-y-4">
                        <div class="flex space-x-2">
                            <input 
                                x-model="searchQuery" 
                                @keydown.enter="searchMemories()"
                                class="flex-1 px-4 py-2 rounded-lg bg-white/10 text-white placeholder-white/60 border border-white/20 focus:border-white/40 outline-none"
                                placeholder="Search memories..."
                            />
                            <button 
                                @click="searchMemories()"
                                class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                Search
                            </button>
                        </div>
                        
                        <div class="flex flex-wrap gap-2">
                            <template x-for="category in ['factual', 'procedural', 'episodic', 'semantic', 'organizational', 'architectural', 'temporal']">
                                <button 
                                    @click="searchCategory = searchCategory === category ? '' : category; searchMemories()"
                                    :class="searchCategory === category ? 'bg-blue-500 text-white' : 'bg-white/10 text-white/80 hover:bg-white/20'"
                                    class="px-3 py-1 rounded-full text-sm transition-colors"
                                    x-text="category"
                                ></button>
                            </template>
                        </div>

                        <div class="space-y-2 max-h-64 overflow-y-auto">
                            <template x-for="result in searchResults" :key="result.id">
                                <div class="p-3 bg-white/5 rounded-lg border border-white/10">
                                    <div class="flex items-center justify-between mb-1">
                                        <span class="text-xs text-blue-300 font-medium" x-text="result.category.toUpperCase()"></span>
                                        <span class="text-xs text-white/60" x-text="'Score: ' + result.score.toFixed(3)"></span>
                                    </div>
                                    <p class="text-white text-sm" x-text="result.text"></p>
                                    <div class="flex items-center justify-between mt-2">
                                        <div class="flex space-x-2">
                                            <template x-for="tag in result.tags">
                                                <span class="px-2 py-1 bg-white/10 text-white/80 rounded text-xs" x-text="tag"></span>
                                            </template>
                                        </div>
                                        <span class="text-xs text-white/60" x-text="'Importance: ' + result.importance"></span>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>

                <!-- Memory Categories Chart -->
                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <h2 class="text-xl font-bold text-white mb-4">Memory Categories</h2>
                    <div class="relative">
                        <canvas id="categoriesChart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>

            <!-- Recent Memories & Session Continuity -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Recent Memories -->
                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <h2 class="text-xl font-bold text-white mb-4">Recent Memories</h2>
                    <div class="space-y-3 max-h-96 overflow-y-auto">
                        <template x-for="memory in recentMemories" :key="memory.id">
                            <div class="p-4 bg-white/5 rounded-lg border border-white/10">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-xs text-blue-300 font-medium" x-text="memory.category.toUpperCase()"></span>
                                    <span class="text-xs text-white/60" x-text="new Date(memory.timestamp).toLocaleString()"></span>
                                </div>
                                <p class="text-white text-sm mb-2" x-text="memory.text"></p>
                                <div class="flex items-center justify-between">
                                    <div class="flex space-x-1">
                                        <template x-for="tag in memory.tags.slice(0, 3)">
                                            <span class="px-2 py-1 bg-white/10 text-white/80 rounded text-xs" x-text="tag"></span>
                                        </template>
                                    </div>
                                    <span class="text-xs text-white/60" x-text="'Importance: ' + memory.importance"></span>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Session Continuity -->
                <div class="glass-morphism rounded-lg p-6 card-hover">
                    <h2 class="text-xl font-bold text-white mb-4">Session Continuity</h2>
                    <div class="space-y-3 max-h-96 overflow-y-auto">
                        <template x-for="session in sessionContinuity" :key="session.timestamp">
                            <div class="p-4 bg-white/5 rounded-lg border border-white/10">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-xs text-green-300 font-medium">SESSION</span>
                                    <span class="text-xs text-white/60" x-text="Math.round(session.hours_ago) + 'h ago'"></span>
                                </div>
                                <p class="text-white text-sm" x-text="session.memory.text"></p>
                                <div class="mt-2">
                                    <span class="text-xs text-blue-300" x-text="session.memory.category.toUpperCase()"></span>
                                    <span class="text-xs text-white/60 ml-2" x-text="'Score: ' + session.memory.score.toFixed(3)"></span>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function dashboardApp() {
                return {
                    stats: {},
                    recentMemories: [],
                    sessionContinuity: [],
                    searchQuery: '',
                    searchCategory: '',
                    searchResults: [],
                    categoriesChart: null,

                    async init() {
                        await this.refreshData();
                        this.initCharts();
                    },

                    async refreshData() {
                        try {
                            // Load stats
                            const statsResponse = await fetch('/api/memories/stats');
                            this.stats = await statsResponse.json();

                            // Load recent memories
                            const recentResponse = await fetch('/api/memories/recent');
                            const recentData = await recentResponse.json();
                            this.recentMemories = recentData.memories || [];

                            // Load session continuity
                            const sessionResponse = await fetch('/api/sessions/continuity');
                            const sessionData = await sessionResponse.json();
                            this.sessionContinuity = sessionData.chronological_context || [];

                            // Update charts
                            this.updateCategoriesChart();
                        } catch (error) {
                            console.error('Error refreshing data:', error);
                        }
                    },

                    async searchMemories() {
                        if (!this.searchQuery.trim() && !this.searchCategory) return;

                        try {
                            const response = await fetch('/api/memories/search', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    query: this.searchQuery,
                                    category_filter: this.searchCategory || null,
                                    limit: 10
                                })
                            });

                            const data = await response.json();
                            this.searchResults = data.results || [];
                        } catch (error) {
                            console.error('Error searching memories:', error);
                        }
                    },

                    initCharts() {
                        const ctx = document.getElementById('categoriesChart').getContext('2d');
                        this.categoriesChart = new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                                labels: [],
                                datasets: [{
                                    data: [],
                                    backgroundColor: [
                                        '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
                                        '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
                                    ],
                                    borderColor: 'rgba(255, 255, 255, 0.1)',
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            color: 'white',
                                            font: {
                                                size: 12
                                            }
                                        }
                                    }
                                }
                            }
                        });
                    },

                    updateCategoriesChart() {
                        if (!this.categoriesChart || !this.stats.category_distribution) return;

                        const labels = Object.keys(this.stats.category_distribution);
                        const data = Object.values(this.stats.category_distribution);

                        this.categoriesChart.data.labels = labels;
                        this.categoriesChart.data.datasets[0].data = data;
                        this.categoriesChart.update();
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

# Server startup
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