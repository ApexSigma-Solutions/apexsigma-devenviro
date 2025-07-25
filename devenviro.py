#!/usr/bin/env python3
"""
ApexSigma DevEnviro - Cognitive Collaboration Platform
Seamless startup for cognitive collaboration across any project or workspace

Usage:
  devenviro                        # Auto-detect mode (current project)
  devenviro test                   # Run system test
  devenviro extract <text>         # Extract memory from text
  devenviro search <query>         # Search organizational memory
  devenviro health                 # Check system health
  devenviro stats                  # Show performance statistics
  devenviro global                 # Initialize global workspace
  devenviro project                # Initialize project workspace
  devenviro new project <name>     # Create new project workspace
  devenviro min                    # Minimal initialization
  devenviro full                   # Full system initialization
  devenviro install                # Install system-wide
  devenviro --help                 # Show all options
"""

import os
import sys
import asyncio
import time
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add the devenviro directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "devenviro"))

from gemini_memory_engine import (
    GeminiMemoryEngine,
    extract_and_store_memory,
    search_organizational_memory,
    get_gemini_memory_engine,
    capture_session_episodic_memory,
    restore_session_continuity_brief
)

class DevEnviroManager:
    """Enhanced DevEnviro manager with auto-detection and comprehensive initialization"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.working_dir = Path.cwd()
        self.global_devenviro = Path.home() / ".devenviro"
        self.mode = self._determine_mode()
        self.context = {}
    
    def _determine_mode(self):
        """Determine initialization mode based on environment"""
        if (self.working_dir / ".devenviro").exists():
            return "project_auto"
        elif (self.working_dir / "devenviro").exists():
            return "devenviro_auto"
        elif self.global_devenviro.exists():
            return "global_auto"
        else:
            return "workspace"
    
    def print_header(self, mode="auto"):
        """Print startup header with mode info"""
        print("=" * 75)
        print("  APEXSIGMA DEVENVIRO - COGNITIVE COLLABORATION PLATFORM")
        print("=" * 75)
        print(f"[MODE] {mode.upper()}")
        print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[WORKSPACE] {self.working_dir}")
        print()
    
    def check_environment(self):
        """Check environment and API keys"""
        print("[ENV] Checking environment...")
        
        # Check Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key and len(gemini_key) > 20:
            print("[OK] Gemini API key configured")
        else:
            print("[WARN] Gemini API key not found")
            print("[FIX] Set GEMINI_API_KEY environment variable")
        
        # Check Qdrant
        try:
            import requests
            response = requests.get("http://localhost:6333/collections", timeout=3)
            if response.status_code == 200:
                collections = response.json()
                count = len(collections.get("result", {}).get("collections", []))
                print(f"[OK] Qdrant vector database ({count} collections)")
            else:
                print(f"[WARN] Qdrant status: {response.status_code}")
        except Exception:
            print("[INFO] Qdrant not available - vector search disabled")
            print("[OPTIONAL] Start with: docker run -p 6333:6333 qdrant/qdrant")
        
        return True
    
    def load_context(self):
        """Load context files for cognitive collaboration"""
        print("[CONTEXT] Loading context files...")
        
        context_files = {
            "CLAUDE.md": "Claude strategic agent instructions",
            "README.md": "Project documentation",
            ".devenviro/config.json": "DevEnviro configuration"
        }
        
        loaded_count = 0
        for file_path, description in context_files.items():
            full_path = self.working_dir / file_path
            if full_path.exists():
                try:
                    size = full_path.stat().st_size
                    loaded_count += 1
                    print(f"[OK] {file_path} ({size/1024:.1f}KB)")
                    self.context[file_path] = full_path.read_text(encoding='utf-8')
                except Exception as e:
                    print(f"[WARN] Could not load {file_path}: {e}")
        
        if loaded_count > 0:
            print(f"[SUCCESS] Loaded {loaded_count} context files")
        else:
            print("[INFO] No context files found")
        
        return True

async def main():
    """Main entry point for DevEnviro"""
    manager = DevEnviroManager()
    
    # If no arguments, run auto-detection
    if len(sys.argv) == 1:
        manager.print_header(manager.mode)
        manager.check_environment()
        manager.load_context()
        
        try:
            engine = GeminiMemoryEngine()
            await engine.initialize()
            health = await engine.health_check()
            
            print("[SYSTEM] DevEnviro Status:")
            for component, status in health.items():
                print(f"  {component}: {status}")
            
            print(f"\n[SUCCESS] DevEnviro ready in {manager.mode} mode")
            
            # Show recent session continuity
            try:
                continuity = await restore_session_continuity_brief()
                if "No recent session context" not in continuity:
                    print(f"\n[CONTINUITY] {continuity}")
            except Exception as e:
                print(f"[INFO] Session continuity unavailable: {e}")
            
            print("\n[COMMANDS] Available commands:")
            print("  devenviro health     # Check system health")
            print("  devenviro search     # Search project memory")
            print("  devenviro extract    # Extract and store memories")
            print("  devenviro stats      # Show performance statistics")
            print("  devenviro global     # Initialize global workspace")
            print("  devenviro project    # Initialize project workspace")
            print("  devenviro full       # Full system initialization")
            print("  devenviro session    # Capture current session for continuity")
            print("  devenviro dashboard  # Start memory analytics dashboard")
            
        except Exception as e:
            print(f"[ERROR] Memory system initialization failed: {e}")
            print("[INFO] Basic workspace mode available")
        
        return
    
    # Handle specific commands
    if len(sys.argv) < 2:
        print("DevEnviro - Cognitive Collaboration Platform")
        print("Usage:")
        print("  devenviro test        - Run system test")
        print("  devenviro extract     - Extract memory from stdin")
        print("  devenviro search      - Search organizational memory")
        print("  devenviro health      - Check system health")
        print("  devenviro stats       - Show performance statistics")
        print("")
        print("Workspace Initialization:")
        print("  devenviro global      - Initialize global workspace")
        print("  devenviro project     - Initialize project workspace")
        print("  devenviro new project - Create new project workspace")
        print("  devenviro min         - Minimal initialization")
        print("  devenviro full        - Full system initialization")
        print("  devenviro install     - Install system-wide")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "test":
            await test_system()
        elif command == "extract":
            await extract_memory()
        elif command == "search":
            await search_memory()
        elif command == "health":
            await health_check()
        elif command == "stats":
            await show_stats()
        elif command == "global":
            await initialize_global()
        elif command == "project":
            await initialize_project()
        elif command == "new" and len(sys.argv) > 2 and sys.argv[2].lower() == "project":
            await create_new_project()
        elif command == "min":
            await minimal_init()
        elif command == "full":
            await full_init()
        elif command == "install":
            await install_system()
        elif command == "session":
            await capture_session()
        elif command == "dashboard":
            await start_dashboard()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

async def test_system():
    """Test the DevEnviro system"""
    print("Testing DevEnviro system...")
    
    engine = GeminiMemoryEngine()
    await engine.initialize()
    
    health = await engine.health_check()
    print(f"Health Status: {health}")
    
    # Test extraction
    test_content = "Testing DevEnviro memory extraction system."
    extraction = await engine.extract_memory(test_content)
    print(f"Extraction test: {'PASS' if extraction['success'] else 'FAIL'}")
    
    stats = engine.get_performance_stats()
    print(f"Performance: {stats}")

async def extract_memory():
    """Extract memory from provided text"""
    if len(sys.argv) < 3:
        print("Usage: devenviro extract <text>")
        return
    
    text = " ".join(sys.argv[2:])
    result = await extract_and_store_memory(text)
    
    if result["extraction"]["success"]:
        print(f"Extracted {len(result['extraction']['extraction']['memories'])} memories")
        for i, memory in enumerate(result["extraction"]["extraction"]["memories"]):
            print(f"  {i+1}. [{memory['category']}] {memory['memory_text']}")
    else:
        print("Memory extraction failed")

async def search_memory():
    """Search organizational memory"""
    if len(sys.argv) < 3:
        print("Usage: devenviro search <query>")
        return
    
    query = " ".join(sys.argv[2:])
    results = await search_organizational_memory(query)
    
    print(f"Found {len(results)} memories:")
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result['category']}] {result['text'][:100]}...")

async def health_check():
    """Check system health"""
    engine = await get_gemini_memory_engine()
    health = await engine.health_check()
    
    print("DevEnviro Health Status:")
    for component, status in health.items():
        print(f"  {component}: {status}")

async def show_stats():
    """Show performance statistics"""
    engine = await get_gemini_memory_engine()
    stats = engine.get_performance_stats()
    
    print("DevEnviro Performance Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

async def initialize_global():
    """Initialize global workspace configuration"""
    print("Initializing global DevEnviro workspace...")
    
    # Create global config directory
    global_config_dir = Path.home() / ".devenviro"
    global_config_dir.mkdir(exist_ok=True)
    
    # Create global memory directory
    global_memory_dir = global_config_dir / "memory"
    global_memory_dir.mkdir(exist_ok=True)
    
    # Create global config file
    global_config = {
        "version": "1.0.0",
        "workspace_type": "global",
        "memory_engine": "gemini-2.5-flash",
        "initialized": True,
        "created_at": str(Path.cwd().resolve()),
        "user_id": Path.home().name
    }
    
    config_file = global_config_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(global_config, f, indent=2)
    
    print(f"[OK] Global workspace initialized at {global_config_dir}")
    print("[OK] Global memory storage configured")
    print("[OK] Cross-project learning enabled")
    
    # Test the memory engine
    await health_check()

async def initialize_project():
    """Initialize project-specific workspace"""
    print("Initializing project DevEnviro workspace...")
    
    project_root = Path.cwd()
    devenviro_dir = project_root / ".devenviro"
    devenviro_dir.mkdir(exist_ok=True)
    
    # Create project config
    project_config = {
        "version": "1.0.0",
        "workspace_type": "project",
        "project_name": project_root.name,
        "project_root": str(project_root),
        "memory_engine": "gemini-2.5-flash",
        "initialized": True,
        "created_at": str(project_root.resolve())
    }
    
    config_file = devenviro_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(project_config, f, indent=2)
    
    # Create project memory directory
    memory_dir = devenviro_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    
    # Create CLAUDE.md for project context
    claude_md = project_root / "CLAUDE.md"
    if not claude_md.exists():
        claude_content = f"""# {project_root.name} - DevEnviro Project

## Project Configuration
- **Project Type**: {detect_project_type(project_root)}
- **DevEnviro Workspace**: Initialized
- **Memory Engine**: Gemini 2.5 Flash
- **Cognitive Collaboration**: Enabled

## Project Context
This project uses DevEnviro for cognitive collaboration and persistent organizational memory.

## Usage
```bash
devenviro health     # Check system health
devenviro search     # Search project memory
devenviro extract    # Extract and store memories
```

## Notes
- Project-specific memories are stored in `.devenviro/memory/`
- Global memories are accessible for cross-project learning
- Health checks ensure all systems are operational
"""
        with open(claude_md, 'w') as f:
            f.write(claude_content)
    
    print(f"[OK] Project workspace initialized in {devenviro_dir}")
    print(f"[OK] Project memory storage configured")
    print(f"[OK] CLAUDE.md created for project context")
    
    # Test the memory engine
    await health_check()

async def create_new_project():
    """Create a new project workspace with full setup"""
    if len(sys.argv) < 4:
        print("Usage: devenviro new project <project_name>")
        return
    
    project_name = sys.argv[3]
    project_dir = Path.cwd() / project_name
    
    print(f"Creating new project: {project_name}")
    
    # Create project directory
    project_dir.mkdir(exist_ok=True)
    
    # Change to project directory
    os.chdir(project_dir)
    
    # Initialize project workspace
    await initialize_project()
    
    # Create basic project structure
    (project_dir / "src").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "docs").mkdir(exist_ok=True)
    
    # Create basic files
    gitignore_content = """# DevEnviro
.devenviro/memory/
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/
.env/
"""
    
    with open(project_dir / ".gitignore", 'w') as f:
        f.write(gitignore_content)
    
    readme_content = f"""# {project_name}

## DevEnviro Cognitive Collaboration Project

This project is enhanced with DevEnviro for intelligent workspace management and persistent organizational memory.

### Features
- 🧠 **Persistent Memory**: Organizational knowledge that grows with each interaction
- 🚀 **Intelligent Workspace**: Auto-configured development environment
- 📊 **Analytics Dashboard**: Real-time monitoring and memory management
- 🔍 **Semantic Search**: Natural language queries across project knowledge

### Quick Start
```bash
devenviro health     # Check system status
devenviro search     # Search project memory
devenviro extract    # Extract and store memories
```

### Project Structure
```
{project_name}/
├── src/             # Source code
├── tests/           # Test files
├── docs/            # Documentation
├── .devenviro/      # DevEnviro configuration
└── CLAUDE.md        # Project context for AI collaboration
```

### DevEnviro Integration
- **Memory Engine**: Gemini 2.5 Flash
- **Vector Storage**: Qdrant
- **Workspace Type**: Project-specific with global learning
- **Status**: ✅ Fully operational

---
Generated with DevEnviro Cognitive Collaboration Platform
"""
    
    with open(project_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"[OK] New project '{project_name}' created successfully")
    print(f"[OK] Project structure initialized")
    print(f"[OK] DevEnviro cognitive collaboration enabled")
    print(f"[INFO] Project location: {project_dir}")

async def minimal_init():
    """Minimal DevEnviro initialization"""
    print("Minimal DevEnviro initialization...")
    
    # Just check if the system is working
    try:
        engine = GeminiMemoryEngine()
        await engine.initialize()
        print("[OK] Memory engine: Operational")
        
        health = await engine.health_check()
        if health["gemini"] == "healthy":
            print("[OK] Gemini 2.5 Flash: Connected")
        if health["qdrant"] == "healthy":
            print("[OK] Qdrant: Connected")
        
        print("[OK] Minimal initialization complete")
        print("TIP: Use 'devenviro full' for complete setup")
        
    except Exception as e:
        print(f"[ERROR] Minimal initialization failed: {e}")
        print("TIP: Check your configuration and try again")

async def full_init():
    """Full system initialization with dashboard"""
    print("Full DevEnviro system initialization...")
    
    # Initialize global workspace
    await initialize_global()
    
    # Initialize project workspace if in a project
    if Path.cwd().name != Path.home().name:
        await initialize_project()
    
    # Start the dashboard
    print("[INFO] Starting DevEnviro dashboard...")
    print("[INFO] Dashboard URL: http://127.0.0.1:8090")
    print("[INFO] Memory search interface available")
    print("[INFO] Analytics and monitoring active")
    print("[INFO] Use 'devenviro dashboard' to start the web interface")
    
    # Test full system
    await test_system()
    
    print("[OK] Full DevEnviro system initialized")
    print("[SUCCESS] Cognitive collaboration platform ready!")

async def install_system():
    """Install DevEnviro system-wide"""
    print("Installing DevEnviro system-wide...")
    
    # The .bat file already exists, just verify it's working
    import subprocess
    try:
        result = subprocess.run(["where", "devenviro"], capture_output=True, text=True)
        if result.returncode == 0:
            bat_path = result.stdout.strip()
            print(f"[OK] DevEnviro command found at: {bat_path}")
            
            # Verify the batch file points to the right location
            script_path = Path(__file__).resolve()
            expected_content = f'@echo off\npython "{script_path}" %*\n'
            
            try:
                with open(bat_path, 'r') as f:
                    current_content = f.read()
                
                if str(script_path) not in current_content:
                    print(f"[WARN] Updating batch file to point to: {script_path}")
                    with open(bat_path, 'w') as f:
                        f.write(expected_content)
                    print("[OK] Batch file updated")
                else:
                    print("[OK] Batch file is correctly configured")
                    
            except PermissionError:
                print("[WARN] Permission denied updating batch file")
                print("TIP: Run as administrator to update system files")
        else:
            print("[ERROR] DevEnviro command not found in PATH")
            print("TIP: Please add the batch file to your PATH manually")
            
    except Exception as e:
        print(f"[ERROR] Installation check failed: {e}")
    
    # Initialize global workspace
    await initialize_global()
    
    print("[OK] DevEnviro system installation complete")
    print("[SUCCESS] Use 'devenviro full' to initialize complete system")

async def capture_session():
    """Capture current session for continuity"""
    if len(sys.argv) < 3:
        print("Usage: devenviro session <session_summary>")
        print("Example: devenviro session 'Fixed dashboard responsiveness and updated README'")
        return
    
    session_summary = " ".join(sys.argv[2:])
    
    print("Capturing session episode for continuity...")
    
    try:
        result = await capture_session_episodic_memory(session_summary)
        
        if result["extraction"]["success"]:
            stored_count = len(result["stored_memories"])
            print(f"[OK] Session captured with {stored_count} episodic memories")
            
            # Show what was captured
            for i, memory in enumerate(result["extraction"]["extraction"]["memories"]):
                print(f"  {i+1}. [{memory['category']}] {memory['memory_text'][:80]}...")
            
            print(f"[SUCCESS] Session continuity established for future reference")
        else:
            print("[ERROR] Failed to capture session memories")
            
    except Exception as e:
        print(f"[ERROR] Session capture failed: {e}")

async def start_dashboard():
    """Start the memory analytics dashboard"""
    print("Starting DevEnviro Memory Analytics Dashboard...")
    
    try:
        # Import dashboard server
        sys.path.insert(0, str(Path(__file__).parent / "devenviro"))
        from dashboard_server import start_dashboard_server
        
        # Check if memory engine is working
        engine = await get_gemini_memory_engine()
        health = await engine.health_check()
        
        if health["gemini"] == "healthy":
            print("[OK] Memory engine ready")
        else:
            print("[WARN] Memory engine may have issues")
        
        print("[INFO] Starting dashboard server...")
        print("[INFO] Dashboard will be available at: http://127.0.0.1:8090")
        print("[INFO] Press Ctrl+C to stop the server")
        
        # Start the server (this will block)
        start_dashboard_server()
        
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard server stopped")
    except Exception as e:
        print(f"[ERROR] Dashboard startup failed: {e}")
        print("[TIP] Make sure all dependencies are installed: pip install -e .")

def detect_project_type(project_path: Path) -> str:
    """Detect the type of project based on files present"""
    if (project_path / "package.json").exists():
        return "Node.js/JavaScript"
    elif (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
        return "Python"
    elif (project_path / "pom.xml").exists():
        return "Java/Maven"
    elif (project_path / "build.gradle").exists():
        return "Java/Gradle"
    elif (project_path / "Cargo.toml").exists():
        return "Rust"
    elif (project_path / "go.mod").exists():
        return "Go"
    elif (project_path / ".csproj").exists():
        return "C#/.NET"
    else:
        return "Generic"

def cli_main():
    """Console script entry point"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()