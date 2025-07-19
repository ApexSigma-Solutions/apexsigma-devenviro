#!/usr/bin/env python3
"""
DevEnviro + Gemini CLI Integrated Launcher
Provides flexible launching options for DevEnviro with optional Gemini CLI integration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import asyncio


class DevEnviroGeminiLauncher:
    """Integrated launcher for DevEnviro with Gemini CLI"""
    
    def __init__(self):
        self.current_directory = Path.cwd()
        self.startup_script = self.current_directory / "devenviro_startup.py"
        
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="DevEnviro + Gemini CLI Integrated Launcher",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python launch_gemini.py                    # DevEnviro startup + Gemini CLI
  python launch_gemini.py --devenviro-only   # DevEnviro startup only
  python launch_gemini.py --gemini-only      # Gemini CLI only (no DevEnviro)
  python launch_gemini.py --skip-interactive # Skip DevEnviro interactive menu
  python launch_gemini.py --project-path /path/to/project  # Specific project
  python launch_gemini.py --gemini-mode chat # Start Gemini in chat mode
            """
        )
        
        parser.add_argument(
            "--devenviro-only",
            action="store_true",
            help="Run DevEnviro startup only (no Gemini CLI)"
        )
        
        parser.add_argument(
            "--gemini-only", 
            action="store_true",
            help="Launch Gemini CLI only (skip DevEnviro startup)"
        )
        
        parser.add_argument(
            "--skip-interactive",
            action="store_true", 
            help="Skip DevEnviro interactive menu"
        )
        
        parser.add_argument(
            "--project-path",
            type=str,
            help="Specific project path to launch in"
        )
        
        parser.add_argument(
            "--gemini-mode",
            type=str,
            choices=["chat", "code", "generate", "analyze"],
            default="chat",
            help="Gemini CLI mode to start in (default: chat)"
        )
        
        parser.add_argument(
            "--gemini-args",
            type=str,
            nargs="*",
            help="Additional arguments to pass to Gemini CLI"
        )
        
        return parser.parse_args()
    
    async def run_devenviro_startup(self, skip_interactive=False):
        """Run DevEnviro startup script"""
        print("[LAUNCHER] Starting DevEnviro initialization...")
        
        if not self.startup_script.exists():
            print(f"[ERROR] DevEnviro startup script not found: {self.startup_script}")
            return False
            
        try:
            if skip_interactive:
                print("[INFO] Running DevEnviro in non-interactive mode")
                
            if skip_interactive:
                # Use environment variable to signal non-interactive mode
                env = os.environ.copy()
                env['DEVENVIRO_NON_INTERACTIVE'] = '1'
                env['DEVENVIRO_AUTO_EXIT'] = '7'
                result = subprocess.run(
                    [sys.executable, str(self.startup_script)],
                    cwd=self.current_directory,
                    text=True,
                    env=env,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    [sys.executable, str(self.startup_script)],
                    cwd=self.current_directory,
                    text=True,
                    capture_output=False
                )
            
            if result.returncode == 0:
                print("[SUCCESS] DevEnviro startup completed")
                return True
            else:
                print(f"[WARNING] DevEnviro startup exited with code: {result.returncode}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"[ERROR] DevEnviro startup failed: {e}")
            return False
    
    def launch_gemini_cli(self, project_path=None, mode="chat", gemini_args=None):
        """Launch Gemini CLI"""
        print("[LAUNCHER] Starting Gemini CLI...")
        
        # Determine which directory to open
        target_path = project_path or self.current_directory
        
        # Build Gemini CLI command
        cmd = []
        
        # Try different possible Gemini CLI commands
        gemini_commands = ["gemini", "gemini-cli", "google-gemini", "gcloud ai gemini"]
        
        gemini_cmd = None
        for cmd_try in gemini_commands:
            try:
                # Check if command exists
                result = subprocess.run(
                    cmd_try.split() + ["--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    gemini_cmd = cmd_try.split()
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue
        
        if not gemini_cmd:
            print("[ERROR] Gemini CLI not found")
            print("[INFO] Tried commands: " + ", ".join(gemini_commands))
            print("[INFO] Please install Gemini CLI:")
            print("       pip install google-generativeai")
            print("       or visit: https://ai.google.dev/gemini-api/docs/quickstart")
            return False
        
        cmd = gemini_cmd.copy()
        
        # Add mode-specific arguments
        if mode == "chat":
            cmd.append("chat")
        elif mode == "code":
            cmd.extend(["generate", "--type", "code"])
        elif mode == "generate":
            cmd.append("generate")
        elif mode == "analyze":
            cmd.extend(["analyze", "--path", str(target_path)])
        
        # Always add project context
        cmd.extend(["--context", str(target_path)])
        
        # Add any additional arguments
        if gemini_args:
            cmd.extend(gemini_args)
            
        try:
            print(f"[INFO] Starting Gemini CLI in {mode} mode")
            print(f"[INFO] Working directory: {target_path}")
            if gemini_args:
                print(f"[INFO] Additional args: {' '.join(gemini_args)}")
                
            # Change to target directory
            os.chdir(target_path)
            
            # Launch Gemini CLI (interactive)
            print(f"[INFO] Running: {' '.join(cmd)}")
            print("[INFO] Starting Gemini CLI session...")
            print("=" * 50)
            
            result = subprocess.run(
                cmd,
                cwd=target_path
            )
            
            print("=" * 50)
            print("[SUCCESS] Gemini CLI session ended")
            return True
            
        except FileNotFoundError:
            print("[ERROR] Gemini CLI command not found")
            print("[INFO] Please install Gemini CLI:")
            print("       pip install google-generativeai")
            print("       or configure gcloud AI platform")
            return False
                
        except Exception as e:
            print(f"[ERROR] Failed to launch Gemini CLI: {e}")
            return False
    
    async def run_integrated_launch(self, args):
        """Run the complete integrated launch sequence"""
        print("DevEnviro + Gemini CLI Integrated Launcher")
        print("=" * 50)
        
        success = True
        
        # Handle project path change
        if args.project_path:
            project_path = Path(args.project_path)
            if project_path.exists() and project_path.is_dir():
                print(f"[INFO] Switching to project: {project_path}")
                os.chdir(project_path)
                self.current_directory = project_path
            else:
                print(f"[ERROR] Project path does not exist: {project_path}")
                return False
        
        # Step 1: Run DevEnviro startup (unless gemini-only)
        if not args.gemini_only:
            devenviro_success = await self.run_devenviro_startup(args.skip_interactive)
            if not devenviro_success:
                print("[WARNING] DevEnviro startup failed, continuing anyway...")
                success = False
        
        # Step 2: Launch Gemini CLI (unless devenviro-only)
        if not args.devenviro_only:
            gemini_success = self.launch_gemini_cli(
                self.current_directory if not args.project_path else None,
                args.gemini_mode,
                args.gemini_args
            )
            if not gemini_success:
                print("[ERROR] Gemini CLI launch failed")
                success = False
        
        return success


async def main():
    """Main launcher entry point"""
    launcher = DevEnviroGeminiLauncher()
    args = launcher.parse_arguments()
    
    try:
        success = await launcher.run_integrated_launch(args)
        
        if success:
            print("\n[SUCCESS] Launch sequence completed!")
            if not args.devenviro_only and not args.gemini_only:
                print("DevEnviro workspace is initialized and Gemini CLI session has ended.")
            elif args.devenviro_only:
                print("DevEnviro workspace is ready for development.")
            elif args.gemini_only:
                print("Gemini CLI session has ended.")
        else:
            print("\n[ERROR] Launch sequence encountered issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n[EXIT] Launch cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())