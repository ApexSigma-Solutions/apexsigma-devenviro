#!/usr/bin/env python3
"""
DevEnviro + Claude Code Integrated Launcher
Provides flexible launching options for DevEnviro with optional Claude Code integration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import asyncio


class DevEnviroClaudeLauncher:
    """Integrated launcher for DevEnviro with Claude Code"""
    
    def __init__(self):
        self.current_directory = Path.cwd()
        self.startup_script = self.current_directory / "devenviro_startup.py"
        
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="DevEnviro + Claude Code Integrated Launcher",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python launch_claude.py                    # DevEnviro startup + Claude Code
  python launch_claude.py --devenviro-only   # DevEnviro startup only
  python launch_claude.py --claude-only      # Claude Code only (no DevEnviro)
  python launch_claude.py --skip-interactive # Skip DevEnviro interactive menu
  python launch_claude.py --project-path /path/to/project  # Specific project
            """
        )
        
        parser.add_argument(
            "--devenviro-only",
            action="store_true",
            help="Run DevEnviro startup only (no Claude Code)"
        )
        
        parser.add_argument(
            "--claude-only", 
            action="store_true",
            help="Launch Claude Code only (skip DevEnviro startup)"
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
            "--claude-args",
            type=str,
            nargs="*",
            help="Additional arguments to pass to Claude Code"
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
                # Modify the startup script call to skip interactive menu
                # For now, we'll run it normally but could add a --non-interactive flag
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
    
    def launch_claude_code(self, project_path=None, claude_args=None):
        """Launch Claude Code"""
        print("[LAUNCHER] Starting Claude Code...")
        
        # Determine which directory to open
        target_path = project_path or self.current_directory
        
        # Build Claude Code command
        cmd = ["claude-code"]  # Assuming 'claude-code' is in PATH
        
        # Add project path
        cmd.append(str(target_path))
        
        # Add any additional arguments
        if claude_args:
            cmd.extend(claude_args)
            
        try:
            print(f"[INFO] Opening Claude Code in: {target_path}")
            if claude_args:
                print(f"[INFO] Additional args: {' '.join(claude_args)}")
                
            # Launch Claude Code (non-blocking)
            subprocess.Popen(
                cmd,
                cwd=target_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print("[SUCCESS] Claude Code launched")
            return True
            
        except FileNotFoundError:
            print("[ERROR] 'claude-code' command not found")
            print("[INFO] Make sure Claude Code CLI is installed and in your PATH")
            print("[INFO] Alternatively, trying with 'code' command...")
            
            # Fallback to VS Code if Claude Code not found
            try:
                fallback_cmd = ["code"] + cmd[1:]
                subprocess.Popen(
                    fallback_cmd,
                    cwd=target_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("[SUCCESS] VS Code launched as fallback")
                return True
            except FileNotFoundError:
                print("[ERROR] Neither 'claude-code' nor 'code' commands found")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to launch Claude Code: {e}")
            return False
    
    async def run_integrated_launch(self, args):
        """Run the complete integrated launch sequence"""
        print("DevEnviro + Claude Code Integrated Launcher")
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
        
        # Step 1: Run DevEnviro startup (unless claude-only)
        if not args.claude_only:
            devenviro_success = await self.run_devenviro_startup(args.skip_interactive)
            if not devenviro_success:
                print("[WARNING] DevEnviro startup failed, continuing anyway...")
                success = False
        
        # Step 2: Launch Claude Code (unless devenviro-only)
        if not args.devenviro_only:
            claude_success = self.launch_claude_code(
                self.current_directory,
                args.claude_args
            )
            if not claude_success:
                print("[ERROR] Claude Code launch failed")
                success = False
        
        return success


async def main():
    """Main launcher entry point"""
    launcher = DevEnviroClaudeLauncher()
    args = launcher.parse_arguments()
    
    try:
        success = await launcher.run_integrated_launch(args)
        
        if success:
            print("\n[SUCCESS] Launch sequence completed!")
            if not args.devenviro_only and not args.claude_only:
                print("DevEnviro workspace is initialized and Claude Code is starting...")
            elif args.devenviro_only:
                print("DevEnviro workspace is ready for development.")
            elif args.claude_only:
                print("Claude Code is starting...")
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