#!/usr/bin/env python3
"""
ApexSigma DevEnviro - Cognitive Collaboration Initialization System
Seamless startup for cognitive collaboration across any project or workspace

Usage:
  devenviro                        # Auto-detect mode (current project)
  devenviro --global               # Global organizational context only
  devenviro --project=myapp        # Specific project context
  devenviro --workspace=path       # Initialize in different workspace
  devenviro --minimal              # Minimal init (memory only)
  devenviro --full                 # Full system with all checks
  devenviro --install              # Add to system PATH
  devenviro --help                 # Show all options
"""

import os
import sys
import asyncio
import time
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# Determine project root dynamically
if hasattr(sys, '_MEIPASS'):  # If running as compiled executable
    script_dir = Path(sys.executable).parent
else:
    script_dir = Path(__file__).parent

class DevEnviroInitializer:
    def __init__(self, args):
        self.args = args
        self.script_dir = script_dir
        self.working_dir = Path(args.workspace) if args.workspace else Path.cwd()
        self.global_apexsigma = Path.home() / ".apexsigma"
        self.mode = self._determine_mode()
        self.context = {}
        
        # Add working directory to Python path for imports
        sys.path.insert(0, str(self.working_dir))
        
    def _determine_mode(self):
        """Determine initialization mode"""
        if self.args.global_only:
            return "global"
        elif self.args.project:
            return "project"
        elif self.args.workspace:
            return "workspace"
        elif self.args.minimal:
            return "minimal"
        elif self.args.full:
            return "full"
        else:
            # Auto-detect
            if (self.working_dir / ".apexsigma").exists():
                return "project_auto"
            elif (self.working_dir / "devenviro").exists():
                return "devenviro_auto"
            elif self.global_apexsigma.exists():
                return "global_auto"
            else:
                return "workspace"
    
    def print_header(self):
        """Print startup header with mode info"""
        print("=" * 75)
        print("  APEXSIGMA DEVENVIRO - COGNITIVE COLLABORATION INITIALIZATION")
        print("=" * 75)
        print(f"[INIT] Mode: {self.mode.upper()}")
        print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[WORKSPACE] {self.working_dir}")
        if self.args.project:
            print(f"[PROJECT] {self.args.project}")
        print()
    
    def install_to_path(self):
        """Install devenviro to system PATH"""
        print("[INSTALL] Installing DevEnviro to system PATH...")
        
        try:
            # Windows installation
            if os.name == 'nt':
                # Create batch wrapper
                batch_content = f'''@echo off
python "{self.script_dir / "devenviro.py"}" %*
'''
                
                # Try to install to a directory in PATH
                install_dirs = [
                    Path.home() / "AppData" / "Local" / "Programs" / "ApexSigma",
                    Path("C:") / "ApexSigma" / "bin",
                    Path.home() / "bin"
                ]
                
                installed = False
                for install_dir in install_dirs:
                    try:
                        install_dir.mkdir(parents=True, exist_ok=True)
                        batch_file = install_dir / "devenviro.bat"
                        batch_file.write_text(batch_content)
                        
                        print(f"[OK] Installed to: {batch_file}")
                        print(f"[INFO] Add to PATH: {install_dir}")
                        print("[CMD] Add to PATH with:")
                        print(f'       setx PATH "%PATH%;{install_dir}"')
                        installed = True
                        break
                    except PermissionError:
                        continue
                
                if not installed:
                    print("[ERROR] Could not install to system directories")
                    print("[ALT] Manual setup:")
                    print(f"1. Copy devenviro.py to a directory in your PATH")
                    print(f"2. Create devenviro.bat with: python path\\to\\devenviro.py %*")
            
            else:
                # Unix/Linux installation
                install_dirs = [
                    Path.home() / ".local" / "bin",
                    Path("/usr/local/bin"),
                    Path.home() / "bin"
                ]
                
                for install_dir in install_dirs:
                    try:
                        install_dir.mkdir(parents=True, exist_ok=True)
                        target = install_dir / "devenviro"
                        
                        # Create symlink or copy
                        if target.exists():
                            target.unlink()
                        
                        # Make executable wrapper
                        wrapper_content = f'''#!/bin/bash
python3 "{self.script_dir / "devenviro.py"}" "$@"
'''
                        target.write_text(wrapper_content)
                        target.chmod(0o755)
                        
                        print(f"[OK] Installed to: {target}")
                        print("[TEST] Try: devenviro --help")
                        break
                        
                    except PermissionError:
                        continue
                        
        except Exception as e:
            print(f"[ERROR] Installation failed: {e}")
            print("[ALT] Manual installation:")
            print(f"1. Add alias: alias devenviro='python {self.script_dir / 'devenviro.py'}'")
            print("2. Add to ~/.bashrc or ~/.zshrc for persistence")
    
    def check_environment(self):
        """Check environment based on mode"""
        print(f"[ENV] Checking environment for {self.mode} mode...")
        
        # Always check API keys
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and len(gemini_key) > 20:
            print("[OK] Gemini API key configured")
        else:
            print("[WARN] Gemini API key not found")
            print("[FIX] Set GEMINI_API_KEY environment variable")
        
        # Check working directory
        print(f"[OK] Working directory: {self.working_dir}")
        
        # Mode-specific checks
        if self.mode in ["global", "global_auto"]:
            return self._check_global_environment()
        elif self.mode in ["project", "project_auto", "devenviro_auto"]:
            return self._check_project_environment()
        elif self.mode in ["workspace"]:
            return self._check_workspace_environment()
        else:  # minimal or full
            return self._check_basic_environment()
    
    def _check_global_environment(self):
        """Check global ApexSigma environment"""
        print("[GLOBAL] Checking global ApexSigma environment...")
        
        if not self.global_apexsigma.exists():
            print(f"[INFO] Global directory not found: {self.global_apexsigma}")
            print("[INFO] This is normal for first-time setup")
            return True
        
        global_files = [
            "config/infrastructure.yml",
            "context/security.md",
            "context/globalrules.md",
            "tools/unified-memory-bridge.py"
        ]
        
        found = 0
        for file in global_files:
            full_path = self.global_apexsigma / file
            if full_path.exists():
                print(f"[OK] ~/.apexsigma/{file}")
                found += 1
            else:
                print(f"[TODO] ~/.apexsigma/{file}")
        
        print(f"[INFO] Global setup: {found}/{len(global_files)} files found")
        return True
    
    def _check_project_environment(self):
        """Check project-specific environment"""
        project_name = self.args.project or "detected"
        print(f"[PROJECT] Checking project environment: {project_name}")
        
        # Look for DevEnviro files
        devenviro_files = [
            "devenviro/gemini_memory_engine.py",
            "devenviro/memory_bridge.py",
            "CLAUDE.md",
            "GEMINI.md"
        ]
        
        found = 0
        for file in devenviro_files:
            if (self.working_dir / file).exists():
                print(f"[OK] {file}")
                found += 1
            else:
                print(f"[MISSING] {file}")
        
        if found == 0:
            print("[INFO] No DevEnviro files found - workspace mode")
            return self._check_workspace_environment()
        elif found < len(devenviro_files):
            print(f"[WARN] Partial DevEnviro setup ({found}/{len(devenviro_files)})")
        else:
            print("[SUCCESS] Complete DevEnviro project detected")
        
        return True
    
    def _check_workspace_environment(self):
        """Check workspace environment"""
        print("[WORKSPACE] Analyzing workspace for cognitive capabilities...")
        
        # Look for any cognitive-related files
        patterns = [
            "**/*memory*.py",
            "**/CLAUDE.md",
            "**/GEMINI.md",
            "**/.apexsigma/**",
            "**/devenviro/**"
        ]
        
        found_files = []
        for pattern in patterns:
            found_files.extend(list(self.working_dir.glob(pattern)))
        
        if found_files:
            print(f"[DETECT] Found {len(found_files)} cognitive-related files:")
            for file in found_files[:10]:  # Show first 10
                rel_path = file.relative_to(self.working_dir)
                print(f"  [FILE] {rel_path}")
            if len(found_files) > 10:
                print(f"  [+] ... and {len(found_files) - 10} more")
        else:
            print("[INFO] No cognitive files detected - basic workspace")
        
        return True
    
    def _check_basic_environment(self):
        """Basic environment check"""
        print("[BASIC] Basic environment check...")
        print(f"[OK] Python {sys.version.split()[0]}")
        print(f"[OK] Platform: {sys.platform}")
        print(f"[OK] Working directory accessible")
        return True
    
    async def initialize_memory_system(self):
        """Initialize memory system if available"""
        if self.mode == "minimal":
            print("[MINIMAL] Skipping memory system initialization")
            return None, None
        
        print("\n[MEMORY] Initializing cognitive memory system...")
        
        try:
            # Try to import from current workspace
            try:
                from devenviro.gemini_memory_engine import get_gemini_memory_engine
                from devenviro.memory_bridge import get_memory_bridge
                print("[OK] DevEnviro memory modules found in workspace")
                memory_available = True
            except ImportError:
                # Try to import from script directory
                sys.path.insert(0, str(self.script_dir))
                try:
                    from devenviro.gemini_memory_engine import get_gemini_memory_engine
                    from devenviro.memory_bridge import get_memory_bridge
                    print("[OK] DevEnviro memory modules found in script directory")
                    memory_available = True
                except ImportError as e:
                    print(f"[INFO] Memory system not available: {e}")
                    print("[INFO] Working in basic mode")
                    return None, None
            
            if memory_available:
                # Initialize Gemini engine
                print("[GEMINI] Starting Gemini 2.5 Flash memory engine...")
                engine = await get_gemini_memory_engine()
                
                # Health check
                health = await engine.health_check()
                all_healthy = True
                for component, status in health.items():
                    if status == "healthy":
                        print(f"[OK] {component}: {status}")
                    else:
                        print(f"[WARN] {component}: {status}")
                        all_healthy = False
                
                if all_healthy:
                    print("[SUCCESS] All memory systems healthy")
                else:
                    print("[WARN] Some memory systems degraded")
                
                # Initialize memory bridge
                print("[BRIDGE] Initializing memory bridge...")
                bridge = await get_memory_bridge()
                
                return engine, bridge
        
        except Exception as e:
            print(f"[ERROR] Memory system initialization failed: {e}")
            return None, None
    
    def check_services(self):
        """Check external services"""
        if self.mode == "minimal":
            return True
            
        print("\n[SERVICES] Checking external services...")
        
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
        
        # Check for other common services
        services = [
            ("PostgreSQL", "localhost", 5432),
            ("Redis", "localhost", 6379),
        ]
        
        for service, host, port in services:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    print(f"[OK] {service} available on {host}:{port}")
                else:
                    print(f"[INFO] {service} not available on {host}:{port}")
            except Exception:
                print(f"[INFO] Could not check {service}")
        
        return True
    
    def load_context(self):
        """Load context based on mode and location"""
        print(f"\n[CONTEXT] Loading context for {self.mode} mode...")
        
        context_files = {}
        
        # Global context (if available)
        if self.mode in ["global", "global_auto", "project", "project_auto", "full"]:
            global_context = self.global_apexsigma / "context"
            if global_context.exists():
                for file in global_context.glob("*.md"):
                    context_files[f"global/{file.name}"] = f"Global {file.stem}"
        
        # Local context files to look for
        local_files = {
            "CLAUDE.md": "Claude strategic agent instructions",
            "GEMINI.md": "Gemini integration agent instructions",
            "contexts/project-overview.md": "Project state and vision",
            "LEARNED_KNOWLEDGE.md": "Organizational knowledge",
            "contexts/implementation-roadmap.md": "Implementation timeline",
            "contexts/technical-architecture.md": "Technical specifications",
            ".apexsigma/plan.md": "Project plan",
            ".apexsigma/tasks.md": "Project tasks",
            "README.md": "Project documentation"
        }
        
        # Add local files based on mode
        if self.mode not in ["global", "global_auto"]:
            context_files.update(local_files)
        
        # Load and display
        loaded_count = 0
        total_size = 0
        
        for file_path, description in context_files.items():
            if file_path.startswith("global/"):
                full_path = self.global_apexsigma / "context" / file_path[7:]
            else:
                full_path = self.working_dir / file_path
            
            if full_path.exists():
                try:
                    size = full_path.stat().st_size
                    total_size += size
                    loaded_count += 1
                    print(f"[OK] {file_path} ({size/1024:.1f}KB)")
                    
                    # Store in context for potential use
                    self.context[file_path] = full_path.read_text(encoding='utf-8')
                except Exception as e:
                    print(f"[WARN] Could not load {file_path}: {e}")
        
        if loaded_count > 0:
            print(f"[SUCCESS] Loaded {loaded_count} context files ({total_size/1024:.1f}KB total)")
        else:
            print("[INFO] No context files found - basic workspace mode")
        
        return loaded_count > 0
    
    def display_capabilities(self):
        """Display current system capabilities"""
        print(f"\n[CAPABILITIES] DevEnviro {self.mode.upper()} mode ready:")
        
        base_caps = [
            "• Flexible multi-workspace initialization",
            "• Context-aware environment detection",
            "• Cross-project capability support"
        ]
        
        if self.mode in ["project_auto", "devenviro_auto", "full"]:
            base_caps.extend([
                "• Gemini 2.5 Flash memory engine",
                "• Intelligent memory extraction & categorization",
                "• Vector search with semantic understanding",
                "• Hierarchical context loading system",
                "• Organizational pattern recognition",
                "• Cross-project learning capabilities"
            ])
        elif self.mode in ["global", "global_auto"]:
            base_caps.extend([
                "• Global organizational context access",
                "• Cross-project standards enforcement",
                "• Organizational DNA baseline"
            ])
        elif self.mode == "workspace":
            base_caps.extend([
                "• Workspace-specific environment setup",
                "• Cognitive file detection and analysis",
                "• Flexible project structure support"
            ])
        
        for cap in base_caps:
            print(f"  {cap}")
    
    def show_next_steps(self):
        """Show available next steps based on mode"""
        print(f"\n[COMMANDS] Available commands from {self.working_dir}:")
        
        # Universal commands
        print("  • Re-initialize: devenviro")
        print("  • Different mode: devenviro --global | --minimal | --full")
        print("  • Other workspace: devenviro --workspace=/path/to/project")
        print("  • Help: devenviro --help")
        
        # Mode-specific commands
        if self.mode in ["project_auto", "devenviro_auto", "full"]:
            if (self.working_dir / "devenviro" / "memory_bridge.py").exists():
                print("  • Test memory: python devenviro/memory_bridge.py")
            if (self.working_dir / "test_gemini_clean.py").exists():
                print("  • Run tests: python test_gemini_clean.py")
            if (self.working_dir / "devenviro" / "main.py").exists():
                print("  • Start app: python devenviro/main.py")
        
        # Git commands if in git repo
        if (self.working_dir / ".git").exists():
            print("  • Git status: git status")
            print("  • Git log: git log --oneline -5")
        
        # Project-specific suggestions
        if (self.working_dir / "package.json").exists():
            print("  • NPM install: npm install")
            print("  • NPM start: npm start")
        elif (self.working_dir / "requirements.txt").exists():
            print("  • Install deps: pip install -r requirements.txt")
        elif (self.working_dir / "Cargo.toml").exists():
            print("  • Cargo build: cargo build")
        
    async def store_session_start(self, engine):
        """Store session start in memory"""
        if not engine or self.mode == "minimal":
            return
            
        try:
            session_info = f"""
            DevEnviro {self.mode} session initialized
            
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Mode: {self.mode}
            Workspace: {self.working_dir}
            Context Files: {len(self.context)} loaded
            Memory System: Available
            
            Cognitive collaboration environment ready.
            """
            
            await engine.store_memory(
                memory_text=session_info.strip(),
                category="episodic",
                importance=4,
                tags=["devenviro", "session_start", self.mode, "initialization"],
                metadata={
                    "mode": self.mode,
                    "workspace": str(self.working_dir),
                    "context_count": len(self.context)
                }
            )
            print("[MEMORY] Session initialization recorded")
            
        except Exception as e:
            print(f"[INFO] Session recording skipped: {e}")
    
    async def run(self):
        """Main initialization sequence"""
        start_time = time.time()
        
        # Handle special commands
        if self.args.install:
            self.install_to_path()
            return True
        
        # Header
        self.print_header()
        
        # Environment check
        if not self.check_environment():
            print(f"\n[FAILED] Environment check failed for {self.mode} mode")
            return False
        
        # Services check
        if not self.check_services():
            print(f"\n[WARN] Some services unavailable (continuing anyway)")
        
        # Load context
        self.load_context()
        
        # Initialize memory system
        engine, bridge = await self.initialize_memory_system()
        
        # Store session start
        if engine:
            await self.store_session_start(engine)
        
        # Display capabilities
        self.display_capabilities()
        
        # Show next steps
        self.show_next_steps()
        
        # Success
        elapsed = time.time() - start_time
        print(f"\n[SUCCESS] DevEnviro initialization complete in {elapsed:.2f}s")
        print(f"[READY] Cognitive workspace ready ({self.mode} mode)")
        print("=" * 75)
        
        return True

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="ApexSigma DevEnviro - Cognitive Collaboration Initialization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devenviro                          # Auto-detect current workspace
  devenviro --global                 # Global organizational context
  devenviro --project=myapp          # Specific project mode
  devenviro --workspace=/path/to/dir # Different workspace
  devenviro --minimal                # Memory system only
  devenviro --full                   # Full system check
  devenviro --install                # Add to system PATH
        """
    )
    
    parser.add_argument("--global", dest="global_only", action="store_true",
                       help="Initialize with global organizational context only")
    parser.add_argument("--project", type=str, metavar="NAME",
                       help="Initialize for specific project")
    parser.add_argument("--workspace", type=str, metavar="PATH",
                       help="Initialize in different workspace directory")
    parser.add_argument("--minimal", action="store_true",
                       help="Minimal initialization (memory system only)")
    parser.add_argument("--full", action="store_true",
                       help="Full initialization with comprehensive checks")
    parser.add_argument("--install", action="store_true",
                       help="Install devenviro command to system PATH")
    
    return parser

async def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    initializer = DevEnviroInitializer(args)
    
    try:
        success = await initializer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] DevEnviro initialization cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAILED] DevEnviro initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())