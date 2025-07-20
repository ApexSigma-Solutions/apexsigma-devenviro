#!/usr/bin/env python3
"""
Multi-page dashboard HTML content for DevEnviro Memory Analytics
"""

def get_multi_page_dashboard_html():
    """Generate the complete multi-page dashboard HTML"""
    return """
    <!DOCTYPE html>
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
                background: rgba(237, 238, 237, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(237, 238, 237, 0.2);
            }
            .gradient-bg {
                background: #161f27;
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
                border-left: 3px solid rgba(255, 255, 255, 0.8);
            }
            .page-transition {
                transition: all 0.3s ease;
            }
            
            /* Navigation Drawer Styles */
            .nav-drawer {
                position: fixed;
                top: 0;
                left: 0;
                height: 100vh;
                width: 280px;
                background: rgba(0, 0, 0, 0.9);
                backdrop-filter: blur(20px);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                transform: translateX(-100%);
                transition: transform 0.3s ease;
                z-index: 1000;
            }
            
            .nav-drawer.open {
                transform: translateX(0);
            }
            
            .nav-trigger {
                position: fixed;
                top: 20px;
                left: 20px;
                width: 50px;
                height: 50px;
                background: rgba(74, 144, 226, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 1001;
            }
            
            .nav-trigger:hover {
                background: rgba(74, 144, 226, 0.3);
                transform: scale(1.05);
            }
            
            .nav-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.5);
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                z-index: 999;
            }
            
            .nav-overlay.active {
                opacity: 1;
                visibility: visible;
            }
            
            /* Loading Spinner */
            .spinner {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-top: 2px solid #fff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Progress Bar */
            .progress-bar {
                width: 100%;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                overflow: hidden;
                margin: 8px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4A90E2, #E74C3C);
                border-radius: 2px;
                transition: width 0.3s ease;
            }
            
            /* Button Loading State */
            .btn-loading {
                opacity: 0.7;
                cursor: not-allowed;
                pointer-events: none;
            }
            
            .btn-loading .spinner {
                margin-right: 8px;
            }
        </style>
    </head>
    <body class="min-h-screen gradient-bg">
        <!-- Dashboard App -->
        <div x-data="dashboardApp()" x-init="init()" class="min-h-screen">
            
            <!-- Navigation Trigger -->
            <div class="nav-trigger" @click="toggleNav()" @mouseenter="showNav()" @mouseleave="hideNav()">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
            </div>
            
            <!-- Navigation Overlay -->
            <div class="nav-overlay" :class="{ 'active': navOpen }" @click="closeNav()"></div>
            
            <!-- Navigation Drawer -->
            <nav class="nav-drawer" :class="{ 'open': navOpen }" @mouseenter="showNav()" @mouseleave="hideNav()">
                <div class="p-6">
                    <!-- Header -->
                    <div class="flex items-center space-x-3 mb-8">
                        <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                            </svg>
                        </div>
                        <div>
                            <h1 class="text-lg font-bold" style="color: #edeeed;">DevEnviro</h1>
                            <p class="text-sm" style="color: rgba(237, 238, 237, 0.6);">Cognitive Platform</p>
                        </div>
                    </div>
                    
                    <!-- System Status -->
                    <div class="mb-6 p-3 bg-white/5 rounded-lg">
                        <div class="flex items-center space-x-2">
                            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span class="text-white text-sm">System Healthy</span>
                        </div>
                        <button 
                            @click="refreshData()" 
                            :class="{ 'btn-loading': isLoading }"
                            class="w-full mt-2 px-3 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
                        >
                            <span x-show="isLoading" class="spinner"></span>
                            <span x-text="isLoading ? 'Refreshing...' : 'Refresh Data'"></span>
                        </button>
                    </div>
                    
                    <!-- Navigation Menu -->
                    <div class="space-y-2">
                        <button 
                            @click="navigateTo('dashboard')" 
                            :class="{ 'active': currentPage === 'dashboard' }"
                            class="nav-item w-full px-4 py-3 rounded-lg text-white text-sm font-medium flex items-center space-x-3"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                            </svg>
                            <span>Dashboard</span>
                        </button>
                        
                        <button 
                            @click="navigateTo('search')" 
                            :class="{ 'active': currentPage === 'search' }"
                            class="nav-item w-full px-4 py-3 rounded-lg text-white text-sm font-medium flex items-center space-x-3"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                            <span>Search Memory</span>
                        </button>
                        
                        <button 
                            @click="navigateTo('knowledge')" 
                            :class="{ 'active': currentPage === 'knowledge' }"
                            class="nav-item w-full px-4 py-3 rounded-lg text-white text-sm font-medium flex items-center space-x-3"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                            </svg>
                            <span>Knowledge Ingestion</span>
                        </button>
                        
                        <button 
                            @click="navigateTo('analytics')" 
                            :class="{ 'active': currentPage === 'analytics' }"
                            class="nav-item w-full px-4 py-3 rounded-lg text-white text-sm font-medium flex items-center space-x-3"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                            <span>Deep Analytics</span>
                        </button>
                        
                        <button 
                            @click="navigateTo('explorer')" 
                            :class="{ 'active': currentPage === 'explorer' }"
                            class="nav-item w-full px-4 py-3 rounded-lg text-white text-sm font-medium flex items-center space-x-3"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                            </svg>
                            <span>Data Explorer</span>
                        </button>
                    </div>
                </div>
            </nav>
            
            <!-- Main Header -->
            <div class="glass-morphism rounded-lg m-4 mb-0 ml-20">
                <div class="px-6 py-4">
                    <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                        <div>
                            <h1 class="text-2xl font-bold mb-1" style="color: #edeeed;">DevEnviro Memory Analytics</h1>
                            <p class="text-sm" style="color: rgba(237, 238, 237, 0.8);">Cognitive Collaboration Platform Dashboard</p>
                        </div>
                        
                        <div class="flex items-center space-x-4 mt-4 md:mt-0">
                            <div class="text-right">
                                <p class="text-white font-medium text-sm" x-text="getPageTitle()"></p>
                                <p class="text-white/60 text-xs" x-text="new Date().toLocaleString()"></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Page Content -->
            <div class="p-4 pt-2 ml-16">
                
                <!-- Dashboard Landing Page -->
                <div x-show="currentPage === 'dashboard'" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform scale-95" x-transition:enter-end="opacity-100 transform scale-100">
                    
                    <!-- Loading Progress -->
                    <div x-show="isLoading" class="mb-4">
                        <div class="progress-bar">
                            <div class="progress-fill" :style="'width: ' + loadingProgress + '%'"></div>
                        </div>
                        <p class="text-white/80 text-sm mt-2">Loading dashboard data...</p>
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

                    <!-- Quick Actions & Recent Activity -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Quick Actions -->
                        <div class="glass-morphism rounded-lg p-6 card-hover">
                            <h3 class="text-lg font-bold text-white mb-4">Quick Actions</h3>
                            <div class="space-y-3">
                                <button @click="currentPage = 'search'" class="w-full p-3 bg-white/10 rounded-lg text-white hover:bg-white/20 transition-colors text-left">
                                    <div class="flex items-center space-x-3">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                                        </svg>
                                        <span>Search organizational memory</span>
                                    </div>
                                </button>
                                <button @click="currentPage = 'knowledge'" class="w-full p-3 bg-white/10 rounded-lg text-white hover:bg-white/20 transition-colors text-left">
                                    <div class="flex items-center space-x-3">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                        </svg>
                                        <span>Add knowledge to organizational brain</span>
                                    </div>
                                </button>
                                <button @click="currentPage = 'analytics'" class="w-full p-3 bg-white/10 rounded-lg text-white hover:bg-white/20 transition-colors text-left">
                                    <div class="flex items-center space-x-3">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                        </svg>
                                        <span>View deep analytics and insights</span>
                                    </div>
                                </button>
                                <button @click="currentPage = 'explorer'" class="w-full p-3 bg-white/10 rounded-lg text-white hover:bg-white/20 transition-colors text-left">
                                    <div class="flex items-center space-x-3">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                        </svg>
                                        <span>Explore data objects and relationships</span>
                                    </div>
                                </button>
                            </div>
                        </div>

                        <!-- Recent Activity -->
                        <div class="glass-morphism rounded-lg p-6 card-hover">
                            <h3 class="text-lg font-bold text-white mb-4">Recent Activity</h3>
                            <div class="space-y-3 max-h-80 overflow-y-auto">
                                <template x-for="memory in recentMemories.slice(0, 5)" :key="memory.id">
                                    <div class="p-3 bg-white/5 rounded-lg border border-white/10">
                                        <div class="flex items-center justify-between mb-1">
                                            <span class="text-xs text-blue-300 font-medium" x-text="memory.category.toUpperCase()"></span>
                                            <span class="text-xs text-white/60" x-text="new Date(memory.timestamp).toLocaleString()"></span>
                                        </div>
                                        <p class="text-white text-sm" x-text="memory.text.substring(0, 80) + '...'"></p>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Search Memory Page -->
                <div x-show="currentPage === 'search'" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform scale-95" x-transition:enter-end="opacity-100 transform scale-100">
                    <div class="glass-morphism rounded-lg p-6 mb-6 card-hover">
                        <h2 class="text-2xl font-bold text-white mb-4">Search Organizational Memory</h2>
                        
                        <div class="space-y-4">
                            <div class="flex space-x-2">
                                <input 
                                    x-model="searchQuery" 
                                    @keydown.enter="searchMemories()"
                                    class="flex-1 px-4 py-3 rounded-lg bg-white/10 text-white placeholder-white/60 border border-white/20 focus:border-white/40 outline-none"
                                    placeholder="Search memories, decisions, implementations..."
                                />
                                <button 
                                    @click="searchMemories()"
                                    :class="{ 'btn-loading': isSearching }"
                                    class="px-6 py-3 rounded-lg transition-colors"
                                    style="background-color: #4A90E2; color: #edeeed;"
                                    onmouseover="this.style.backgroundColor='#357ABD'"
                                    onmouseout="this.style.backgroundColor='#4A90E2'"
                                >
                                    <span x-show="isSearching" class="spinner"></span>
                                    <span x-text="isSearching ? 'Searching...' : 'Search'"></span>
                                </button>
                            </div>
                            
                            <div class="flex flex-wrap gap-2">
                                <span class="text-white/80 text-sm">Filter by category:</span>
                                <template x-for="category in ['factual', 'procedural', 'episodic', 'semantic', 'organizational', 'architectural', 'temporal']">
                                    <button 
                                        @click="searchCategory = searchCategory === category ? '' : category; searchMemories()"
                                        :class="searchCategory === category ? 'bg-blue-500 text-white' : 'bg-white/10 text-white/80 hover:bg-white/20'"
                                        class="px-3 py-1 rounded-full text-sm transition-colors"
                                        x-text="category"
                                    ></button>
                                </template>
                            </div>

                            <div class="flex items-center space-x-4">
                                <label class="text-white/80 text-sm">Importance threshold:</label>
                                <input 
                                    x-model="importanceThreshold" 
                                    type="range" 
                                    min="1" 
                                    max="10" 
                                    class="flex-1 max-w-xs"
                                    @change="searchMemories()"
                                />
                                <span class="text-white text-sm" x-text="importanceThreshold"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Search Results -->
                    <div class="glass-morphism rounded-lg p-6 card-hover">
                        <h3 class="text-lg font-bold text-white mb-4">Search Results</h3>
                        <div class="space-y-3 max-h-96 overflow-y-auto">
                            <template x-for="result in searchResults" :key="result.id">
                                <div class="p-4 bg-white/5 rounded-lg border border-white/10">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-xs text-blue-300 font-medium" x-text="result.category.toUpperCase()"></span>
                                        <span class="text-xs text-white/60" x-text="'Score: ' + result.score.toFixed(3)"></span>
                                    </div>
                                    <p class="text-white text-sm mb-2" x-text="result.text"></p>
                                    <div class="flex items-center justify-between">
                                        <div class="flex space-x-2">
                                            <template x-for="tag in result.tags.slice(0, 3)">
                                                <span class="px-2 py-1 bg-white/10 text-white/80 rounded text-xs" x-text="tag"></span>
                                            </template>
                                        </div>
                                        <span class="text-xs text-white/60" x-text="'Importance: ' + result.importance"></span>
                                    </div>
                                </div>
                            </template>
                            <div x-show="searchResults.length === 0" class="text-center text-white/60 py-8">
                                No results found. Try adjusting your search terms or filters.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Knowledge Ingestion Page -->
                <div x-show="currentPage === 'knowledge'" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform scale-95" x-transition:enter-end="opacity-100 transform scale-100">
                    <div class="glass-morphism rounded-lg p-6 mb-6 card-hover">
                        <h2 class="text-2xl font-bold text-white mb-4">Knowledge Ingestion</h2>
                        <p class="text-white/80 mb-6">Add knowledge to your organizational brain for instant training and recall</p>
                        
                        <div class="space-y-6">
                            <!-- Text Input -->
                            <div>
                                <label class="block text-white font-medium mb-2">Knowledge Content</label>
                                <textarea 
                                    x-model="knowledgeContent" 
                                    rows="6"
                                    class="w-full px-4 py-3 rounded-lg bg-white/10 text-white placeholder-white/60 border border-white/20 focus:border-white/40 outline-none"
                                    placeholder="Enter knowledge content, documentation, decisions, or datasets..."
                                ></textarea>
                            </div>
                            
                            <!-- Context Input -->
                            <div>
                                <label class="block text-white font-medium mb-2">Context (Optional)</label>
                                <input 
                                    x-model="knowledgeContext" 
                                    class="w-full px-4 py-3 rounded-lg bg-white/10 text-white placeholder-white/60 border border-white/20 focus:border-white/40 outline-none"
                                    placeholder="Project name, source, or additional context..."
                                />
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="flex space-x-4">
                                <button 
                                    @click="extractKnowledge()"
                                    :class="{ 'btn-loading': isExtracting }"
                                    class="px-6 py-3 rounded-lg transition-colors"
                                    style="background-color: #4A90E2; color: #edeeed;"
                                    onmouseover="this.style.backgroundColor='#357ABD'"
                                    onmouseout="this.style.backgroundColor='#4A90E2'"
                                    :disabled="!knowledgeContent.trim() || isExtracting"
                                >
                                    <span x-show="isExtracting" class="spinner"></span>
                                    <span x-text="isExtracting ? 'Processing...' : 'Extract & Store Knowledge'"></span>
                                </button>
                                <button 
                                    @click="knowledgeContent = ''; knowledgeContext = ''; extractionResult = null"
                                    class="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Extraction Results -->
                    <div x-show="extractionResult" class="glass-morphism rounded-lg p-6 card-hover">
                        <h3 class="text-lg font-bold text-white mb-4">Extraction Results</h3>
                        <div class="space-y-3">
                            <template x-for="memory in extractionResult?.extraction?.extraction?.memories || []" :key="memory.memory_text">
                                <div class="p-4 bg-white/5 rounded-lg border border-white/10">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-xs text-green-300 font-medium" x-text="memory.category.toUpperCase()"></span>
                                        <span class="text-xs text-white/60" x-text="'Importance: ' + memory.importance"></span>
                                    </div>
                                    <p class="text-white text-sm mb-2" x-text="memory.memory_text"></p>
                                    <div class="flex space-x-2">
                                        <template x-for="tag in memory.tags">
                                            <span class="px-2 py-1 bg-white/10 text-white/80 rounded text-xs" x-text="tag"></span>
                                        </template>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>

                <!-- Deep Analytics Page -->
                <div x-show="currentPage === 'analytics'" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform scale-95" x-transition:enter-end="opacity-100 transform scale-100">
                    <div class="glass-morphism rounded-lg p-6 mb-6 card-hover">
                        <h2 class="text-2xl font-bold text-white mb-4">Deep Analytics & Insights</h2>
                        <p class="text-white/80 mb-6">Comprehensive analysis of your organizational memory patterns</p>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                        <!-- Memory Categories Chart -->
                        <div class="glass-morphism rounded-lg p-6 card-hover">
                            <h3 class="text-lg font-bold text-white mb-4">Memory Distribution</h3>
                            <div class="relative">
                                <canvas id="categoriesChart" width="400" height="300"></canvas>
                            </div>
                        </div>

                        <!-- Importance Distribution -->
                        <div class="glass-morphism rounded-lg p-6 card-hover">
                            <h3 class="text-lg font-bold text-white mb-4">Importance Levels</h3>
                            <div class="relative">
                                <canvas id="importanceChart" width="400" height="300"></canvas>
                            </div>
                        </div>
                    </div>

                    <!-- Analytics Metrics -->
                    <div class="glass-morphism rounded-lg p-6 card-hover">
                        <h3 class="text-lg font-bold text-white mb-4">Performance Metrics</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div class="text-center">
                                <p class="text-3xl font-bold text-blue-300" x-text="stats.performance_stats?.extractions || 0"></p>
                                <p class="text-white/80 text-sm">Extractions</p>
                            </div>
                            <div class="text-center">
                                <p class="text-3xl font-bold text-green-300" x-text="stats.performance_stats?.searches || 0"></p>
                                <p class="text-white/80 text-sm">Searches</p>
                            </div>
                            <div class="text-center">
                                <p class="text-3xl font-bold text-purple-300" x-text="stats.performance_stats?.stores || 0"></p>
                                <p class="text-white/80 text-sm">Stores</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Data Explorer Page -->
                <div x-show="currentPage === 'explorer'" x-transition:enter="transition ease-out duration-300" x-transition:enter-start="opacity-0 transform scale-95" x-transition:enter-end="opacity-100 transform scale-100">
                    <div class="glass-morphism rounded-lg p-6 mb-6 card-hover">
                        <h2 class="text-2xl font-bold text-white mb-4">Data Explorer</h2>
                        <p class="text-white/80 mb-6">Explore objects, organizations, and users in your knowledge base</p>
                        
                        <div class="flex space-x-4">
                            <button 
                                @click="explorerView = 'objects'" 
                                :class="explorerView === 'objects' ? 'bg-blue-500' : 'bg-white/20'"
                                class="px-4 py-2 text-white rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                Objects
                            </button>
                            <button 
                                @click="explorerView = 'organizations'" 
                                :class="explorerView === 'organizations' ? 'bg-blue-500' : 'bg-white/20'"
                                class="px-4 py-2 text-white rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                Organizations
                            </button>
                            <button 
                                @click="explorerView = 'users'" 
                                :class="explorerView === 'users' ? 'bg-blue-500' : 'bg-white/20'"
                                class="px-4 py-2 text-white rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                Users
                            </button>
                        </div>
                    </div>

                    <!-- Explorer Content -->
                    <div class="glass-morphism rounded-lg p-6 card-hover">
                        <div x-show="explorerView === 'objects'">
                            <h3 class="text-lg font-bold text-white mb-4">Data Objects</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <template x-for="category in Object.keys(stats.category_distribution || {})" :key="category">
                                    <div class="p-4 bg-white/5 rounded-lg border border-white/10 cursor-pointer hover:bg-white/10 transition-colors">
                                        <div class="flex items-center justify-between mb-2">
                                            <span class="text-white font-medium" x-text="category.charAt(0).toUpperCase() + category.slice(1)"></span>
                                            <span class="text-white/60 text-sm" x-text="stats.category_distribution[category]"></span>
                                        </div>
                                        <p class="text-white/80 text-sm">Click to explore memories</p>
                                    </div>
                                </template>
                            </div>
                        </div>

                        <div x-show="explorerView === 'organizations'">
                            <h3 class="text-lg font-bold text-white mb-4">Organizations</h3>
                            <div class="p-4 bg-white/5 rounded-lg border border-white/10">
                                <div class="flex items-center space-x-3 mb-2">
                                    <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                        <span class="text-white font-bold text-sm">AS</span>
                                    </div>
                                    <div>
                                        <p class="text-white font-medium">ApexSigma Solutions</p>
                                        <p class="text-white/60 text-sm">Primary organization</p>
                                    </div>
                                </div>
                                <div class="grid grid-cols-2 gap-4 mt-4">
                                    <div>
                                        <p class="text-white/80 text-sm">Total Memories</p>
                                        <p class="text-white font-bold" x-text="stats.total_memories || 0"></p>
                                    </div>
                                    <div>
                                        <p class="text-white/80 text-sm">Active Users</p>
                                        <p class="text-white font-bold">1</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div x-show="explorerView === 'users'">
                            <h3 class="text-lg font-bold text-white mb-4">Users</h3>
                            <div class="p-4 bg-white/5 rounded-lg border border-white/10">
                                <div class="flex items-center space-x-3 mb-2">
                                    <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                        <span class="text-white font-bold text-sm">U</span>
                                    </div>
                                    <div>
                                        <p class="text-white font-medium">Current User</p>
                                        <p class="text-white/60 text-sm">System administrator</p>
                                    </div>
                                </div>
                                <div class="grid grid-cols-2 gap-4 mt-4">
                                    <div>
                                        <p class="text-white/80 text-sm">Sessions</p>
                                        <p class="text-white font-bold" x-text="sessionContinuity.length || 0"></p>
                                    </div>
                                    <div>
                                        <p class="text-white/80 text-sm">Contributions</p>
                                        <p class="text-white font-bold" x-text="stats.performance_stats?.extractions || 0"></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function dashboardApp() {
                return {
                    currentPage: 'dashboard',
                    navOpen: false,
                    isLoading: false,
                    isSearching: false,
                    isExtracting: false,
                    loadingProgress: 0,
                    stats: {},
                    recentMemories: [],
                    sessionContinuity: [],
                    searchQuery: '',
                    searchCategory: '',
                    searchResults: [],
                    importanceThreshold: 1,
                    knowledgeContent: '',
                    knowledgeContext: '',
                    extractionResult: null,
                    explorerView: 'objects',
                    categoriesChart: null,
                    importanceChart: null,

                    async init() {
                        await this.refreshData();
                        this.initCharts();
                    },

                    // Navigation functions
                    toggleNav() {
                        this.navOpen = !this.navOpen;
                    },

                    showNav() {
                        this.navOpen = true;
                    },

                    hideNav() {
                        setTimeout(() => {
                            if (!this.navOpen) return;
                            this.navOpen = false;
                        }, 300);
                    },

                    closeNav() {
                        this.navOpen = false;
                    },

                    navigateTo(page) {
                        this.currentPage = page;
                        this.navOpen = false;
                    },

                    getPageTitle() {
                        const titles = {
                            dashboard: 'Dashboard Overview',
                            search: 'Memory Search',
                            knowledge: 'Knowledge Ingestion',
                            analytics: 'Deep Analytics',
                            explorer: 'Data Explorer'
                        };
                        return titles[this.currentPage] || 'Dashboard';
                    },

                    async refreshData() {
                        this.isLoading = true;
                        this.loadingProgress = 0;
                        
                        try {
                            // Simulate progressive loading
                            this.loadingProgress = 20;
                            
                            // Load stats
                            const statsResponse = await fetch('/api/memories/stats');
                            this.stats = await statsResponse.json();
                            this.loadingProgress = 40;

                            // Load recent memories
                            const recentResponse = await fetch('/api/memories/recent');
                            const recentData = await recentResponse.json();
                            this.recentMemories = recentData.memories || [];
                            this.loadingProgress = 70;

                            // Load session continuity
                            const sessionResponse = await fetch('/api/sessions/continuity');
                            const sessionData = await sessionResponse.json();
                            this.sessionContinuity = sessionData.chronological_context || [];
                            this.loadingProgress = 90;

                            // Update charts
                            this.updateCharts();
                            this.loadingProgress = 100;
                            
                            // Hide loading after brief delay
                            setTimeout(() => {
                                this.isLoading = false;
                                this.loadingProgress = 0;
                            }, 500);
                        } catch (error) {
                            console.error('Error refreshing data:', error);
                            this.isLoading = false;
                            this.loadingProgress = 0;
                        }
                    },

                    async searchMemories() {
                        if (!this.searchQuery.trim() && !this.searchCategory) return;

                        this.isSearching = true;
                        this.searchResults = [];
                        
                        try {
                            const response = await fetch('/api/memories/search', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    query: this.searchQuery,
                                    category_filter: this.searchCategory || null,
                                    importance_threshold: this.importanceThreshold,
                                    limit: 20
                                })
                            });

                            const data = await response.json();
                            this.searchResults = data.results || [];
                        } catch (error) {
                            console.error('Error searching memories:', error);
                        } finally {
                            this.isSearching = false;
                        }
                    },

                    async extractKnowledge() {
                        if (!this.knowledgeContent.trim()) return;

                        this.isExtracting = true;
                        this.extractionResult = null;
                        
                        try {
                            const response = await fetch('/api/memories/extract', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    content: this.knowledgeContent,
                                    context: this.knowledgeContext ? { source: this.knowledgeContext } : null
                                })
                            });

                            const data = await response.json();
                            this.extractionResult = data.result;
                            
                            // Refresh data after extraction
                            await this.refreshData();
                        } catch (error) {
                            console.error('Error extracting knowledge:', error);
                        } finally {
                            this.isExtracting = false;
                        }
                    },

                    initCharts() {
                        // Categories chart
                        const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
                        this.categoriesChart = new Chart(categoriesCtx, {
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
                                            font: { size: 12 }
                                        }
                                    }
                                }
                            }
                        });

                        // Importance chart
                        const importanceCtx = document.getElementById('importanceChart').getContext('2d');
                        this.importanceChart = new Chart(importanceCtx, {
                            type: 'bar',
                            data: {
                                labels: [],
                                datasets: [{
                                    label: 'Memories',
                                    data: [],
                                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                                    borderColor: 'rgba(59, 130, 246, 1)',
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        labels: {
                                            color: 'white',
                                            font: { size: 12 }
                                        }
                                    }
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: { color: 'white' },
                                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                                    },
                                    x: {
                                        ticks: { color: 'white' },
                                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                                    }
                                }
                            }
                        });
                    },

                    updateCharts() {
                        if (!this.categoriesChart || !this.importanceChart) return;

                        // Update categories chart
                        if (this.stats.category_distribution) {
                            const labels = Object.keys(this.stats.category_distribution);
                            const data = Object.values(this.stats.category_distribution);
                            
                            this.categoriesChart.data.labels = labels;
                            this.categoriesChart.data.datasets[0].data = data;
                            this.categoriesChart.update();
                        }

                        // Update importance chart
                        if (this.stats.importance_distribution) {
                            const labels = Object.keys(this.stats.importance_distribution);
                            const data = Object.values(this.stats.importance_distribution);
                            
                            this.importanceChart.data.labels = labels;
                            this.importanceChart.data.datasets[0].data = data;
                            this.importanceChart.update();
                        }
                    }
                }
            }
        </script>
    </body>
    </html>
    """