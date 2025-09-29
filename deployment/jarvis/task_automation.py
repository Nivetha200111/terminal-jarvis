"""
Task Automation System for Terminal Jarvis
Handles system tasks, environment setup, and automated actions
"""

import os
import sys
import subprocess
import platform
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import psutil
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemInfo:
    """Get system information and environment details"""
    
    @staticmethod
    def get_os_info() -> Dict[str, str]:
        """Get operating system information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """Get important environment variables"""
        important_vars = [
            "PATH", "PYTHONPATH", "HOME", "USERPROFILE", 
            "APPDATA", "LOCALAPPDATA", "TEMP", "TMP"
        ]
        
        env_vars = {}
        for var in important_vars:
            value = os.environ.get(var, "")
            if value:
                env_vars[var] = value
        
        return env_vars
    
    @staticmethod
    def get_installed_programs() -> List[str]:
        """Get list of installed programs (Windows)"""
        if platform.system() != "Windows":
            return []
        
        try:
            # Get installed programs from registry
            result = subprocess.run([
                "powershell", "-Command",
                "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName | Where-Object {$_.DisplayName -ne $null} | Sort-Object DisplayName"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                programs = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('DisplayName'):
                        programs.append(line.strip())
                return programs
        except Exception as e:
            logger.error(f"Error getting installed programs: {e}")
        
        return []
    
    @staticmethod
    def get_python_installations() -> List[Dict[str, str]]:
        """Find all Python installations on the system"""
        python_installations = []
        
        # Check common Python installation paths
        common_paths = [
            "C:\\Python*",
            "C:\\Program Files\\Python*",
            "C:\\Program Files (x86)\\Python*",
            "C:\\Users\\*\\AppData\\Local\\Programs\\Python\\Python*",
            "C:\\Users\\*\\AppData\\Local\\Microsoft\\WindowsApps\\python*.exe"
        ]
        
        for pattern in common_paths:
            try:
                import glob
                paths = glob.glob(pattern)
                for path in paths:
                    if os.path.isfile(path) and "python" in path.lower():
                        try:
                            # Get Python version
                            result = subprocess.run([path, "--version"], 
                                                  capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                version = result.stdout.strip()
                                python_installations.append({
                                    "path": path,
                                    "version": version,
                                    "executable": path
                                })
                        except:
                            pass
            except Exception as e:
                logger.error(f"Error checking Python path {pattern}: {e}")
        
        return python_installations


class TaskExecutor:
    """Execute system tasks and commands"""
    
    def __init__(self):
        self.system_info = SystemInfo()
        self.os_info = self.system_info.get_os_info()
        self.is_windows = self.os_info["system"] == "Windows"
    
    def add_to_path(self, path_to_add: str, permanent: bool = True) -> Dict[str, Any]:
        """Add a directory to the system PATH"""
        try:
            path_to_add = str(Path(path_to_add).resolve())
            
            if not os.path.exists(path_to_add):
                return {"success": False, "error": f"Path does not exist: {path_to_add}"}
            
            current_path = os.environ.get("PATH", "")
            
            if path_to_add in current_path:
                return {"success": True, "message": "Path already in PATH", "already_exists": True}
            
            if self.is_windows:
                return self._add_to_path_windows(path_to_add, permanent)
            else:
                return self._add_to_path_unix(path_to_add, permanent)
                
        except Exception as e:
            logger.error(f"Error adding to PATH: {e}")
            return {"success": False, "error": str(e)}
    
    def _add_to_path_windows(self, path_to_add: str, permanent: bool) -> Dict[str, Any]:
        """Add to PATH on Windows"""
        try:
            if permanent:
                # Add to system PATH permanently
                result = subprocess.run([
                    "powershell", "-Command",
                    f"[Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';{path_to_add}', 'Machine')"
                ], capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    return {"success": True, "message": f"Added {path_to_add} to system PATH"}
                else:
                    return {"success": False, "error": f"Failed to add to system PATH: {result.stderr}"}
            else:
                # Add to current session only
                os.environ["PATH"] = os.environ.get("PATH", "") + ";" + path_to_add
                return {"success": True, "message": f"Added {path_to_add} to current session PATH"}
                
        except Exception as e:
            return {"success": False, "error": f"Windows PATH error: {e}"}
    
    def _add_to_path_unix(self, path_to_add: str, permanent: bool) -> Dict[str, Any]:
        """Add to PATH on Unix-like systems"""
        try:
            if permanent:
                # Add to shell profile
                home = os.path.expanduser("~")
                shell_profile = os.path.join(home, ".bashrc")
                
                if not os.path.exists(shell_profile):
                    shell_profile = os.path.join(home, ".zshrc")
                
                path_line = f'export PATH="$PATH:{path_to_add}"'
                
                with open(shell_profile, "a") as f:
                    f.write(f"\n# Added by Terminal Jarvis\n{path_line}\n")
                
                return {"success": True, "message": f"Added {path_to_add} to {shell_profile}"}
            else:
                # Add to current session
                os.environ["PATH"] = os.environ.get("PATH", "") + ":" + path_to_add
                return {"success": True, "message": f"Added {path_to_add} to current session PATH"}
                
        except Exception as e:
            return {"success": False, "error": f"Unix PATH error: {e}"}
    
    def install_python_package(self, package_name: str, upgrade: bool = False) -> Dict[str, Any]:
        """Install a Python package using pip"""
        try:
            cmd = [sys.executable, "-m", "pip", "install"]
            if upgrade:
                cmd.append("--upgrade")
            cmd.append(package_name)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {"success": True, "message": f"Successfully installed {package_name}"}
            else:
                return {"success": False, "error": f"Failed to install {package_name}: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Installation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_virtual_environment(self, venv_path: str, python_executable: str = None) -> Dict[str, Any]:
        """Create a Python virtual environment"""
        try:
            venv_path = str(Path(venv_path).resolve())
            
            if python_executable is None:
                python_executable = sys.executable
            
            cmd = [python_executable, "-m", "venv", venv_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {"success": True, "message": f"Created virtual environment at {venv_path}"}
            else:
                return {"success": False, "error": f"Failed to create virtual environment: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Virtual environment creation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_command(self, command: str, shell: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Run a system command"""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "timeout": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "os_info": self.os_info,
                "python_installations": self.system_info.get_python_installations()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}


class TaskSolver:
    """High-level task solver that combines RAG with task execution"""
    
    def __init__(self, rag_system, task_executor):
        self.rag = rag_system
        self.executor = task_executor
    
    def solve_task(self, task_description: str) -> Dict[str, Any]:
        """Solve a task using RAG knowledge and task execution"""
        try:
            # Search knowledge base for relevant information
            context = self.rag.get_context_for_query(task_description, max_chunks=5)
            
            # Analyze the task
            task_analysis = self._analyze_task(task_description, context)
            
            if task_analysis["task_type"] == "path_addition":
                return self._solve_path_addition_task(task_description, context)
            elif task_analysis["task_type"] == "python_setup":
                return self._solve_python_setup_task(task_description, context)
            elif task_analysis["task_type"] == "package_installation":
                return self._solve_package_installation_task(task_description, context)
            elif task_analysis["task_type"] == "system_command":
                return self._solve_system_command_task(task_description, context)
            else:
                return {
                    "success": False,
                    "error": "Task type not recognized",
                    "suggestions": self._get_general_suggestions(task_description, context)
                }
                
        except Exception as e:
            logger.error(f"Error solving task: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_task(self, task_description: str, context: str) -> Dict[str, Any]:
        """Analyze the task to determine its type and requirements"""
        task_lower = task_description.lower()
        
        # Check for path-related tasks
        if any(keyword in task_lower for keyword in ["add to path", "path", "environment variable", "env"]):
            return {"task_type": "path_addition", "confidence": 0.9}
        
        # Check for Python setup tasks
        if any(keyword in task_lower for keyword in ["python", "pip", "virtual environment", "venv"]):
            return {"task_type": "python_setup", "confidence": 0.8}
        
        # Check for package installation
        if any(keyword in task_lower for keyword in ["install", "package", "pip install"]):
            return {"task_type": "package_installation", "confidence": 0.8}
        
        # Check for system commands
        if any(keyword in task_lower for keyword in ["run", "execute", "command", "cmd", "powershell"]):
            return {"task_type": "system_command", "confidence": 0.7}
        
        return {"task_type": "unknown", "confidence": 0.0}
    
    def _solve_path_addition_task(self, task_description: str, context: str) -> Dict[str, Any]:
        """Solve path addition tasks"""
        # Extract path from task description
        words = task_description.split()
        path_candidates = []
        
        for i, word in enumerate(words):
            if word.lower() in ["add", "to", "path"] and i + 1 < len(words):
                # Look for path-like strings
                for j in range(i + 1, min(i + 3, len(words))):
                    candidate = words[j]
                    if os.path.exists(candidate) or ":" in candidate:
                        path_candidates.append(candidate)
        
        if not path_candidates:
            return {
                "success": False,
                "error": "Could not identify path to add",
                "suggestions": ["Please specify the exact path you want to add to PATH"]
            }
        
        path_to_add = path_candidates[0]
        result = self.executor.add_to_path(path_to_add, permanent=True)
        
        if result["success"]:
            result["task_solved"] = True
            result["action_taken"] = f"Added {path_to_add} to system PATH"
        
        return result
    
    def _solve_python_setup_task(self, task_description: str, context: str) -> Dict[str, Any]:
        """Solve Python setup tasks"""
        # Get current Python installations
        python_installations = self.executor.system_info.get_python_installations()
        
        if not python_installations:
            return {
                "success": False,
                "error": "No Python installations found",
                "suggestions": ["Please install Python first", "Download from python.org"]
            }
        
        # Find the best Python installation
        best_python = python_installations[0]
        for py_install in python_installations:
            if "python" in py_install["path"].lower() and "python" in best_python["path"].lower():
                if py_install["version"] > best_python["version"]:
                    best_python = py_install
        
        # Add Python to PATH if not already there
        python_dir = os.path.dirname(best_python["path"])
        path_result = self.executor.add_to_path(python_dir, permanent=True)
        
        # Add Scripts directory if it exists
        scripts_dir = os.path.join(python_dir, "Scripts")
        if os.path.exists(scripts_dir):
            scripts_result = self.executor.add_to_path(scripts_dir, permanent=True)
        
        return {
            "success": True,
            "task_solved": True,
            "action_taken": f"Configured Python {best_python['version']} and added to PATH",
            "python_path": best_python["path"],
            "python_version": best_python["version"],
            "path_added": path_result["success"]
        }
    
    def _solve_package_installation_task(self, task_description: str, context: str) -> Dict[str, Any]:
        """Solve package installation tasks"""
        # Extract package name from task description
        words = task_description.split()
        package_candidates = []
        
        for i, word in enumerate(words):
            if word.lower() in ["install", "pip", "install"] and i + 1 < len(words):
                package_candidates.append(words[i + 1])
        
        if not package_candidates:
            return {
                "success": False,
                "error": "Could not identify package to install",
                "suggestions": ["Please specify the package name", "Example: install numpy"]
            }
        
        package_name = package_candidates[0]
        result = self.executor.install_python_package(package_name)
        
        if result["success"]:
            result["task_solved"] = True
            result["action_taken"] = f"Installed Python package: {package_name}"
        
        return result
    
    def _solve_system_command_task(self, task_description: str, context: str) -> Dict[str, Any]:
        """Solve system command tasks"""
        # Extract command from task description
        words = task_description.split()
        command_candidates = []
        
        for i, word in enumerate(words):
            if word.lower() in ["run", "execute", "command"] and i + 1 < len(words):
                # Get the rest of the words as command
                command = " ".join(words[i + 1:])
                command_candidates.append(command)
                break
        
        if not command_candidates:
            return {
                "success": False,
                "error": "Could not identify command to run",
                "suggestions": ["Please specify the command to execute", "Example: run dir"]
            }
        
        command = command_candidates[0]
        result = self.executor.run_command(command)
        
        if result["success"]:
            result["task_solved"] = True
            result["action_taken"] = f"Executed command: {command}"
        
        return result
    
    def _get_general_suggestions(self, task_description: str, context: str) -> List[str]:
        """Get general suggestions for unrecognized tasks"""
        suggestions = [
            "Try rephrasing your request more specifically",
            "Check if the task involves adding something to PATH",
            "Consider if you need to install a Python package",
            "Think about whether you need to run a system command"
        ]
        
        if context:
            suggestions.append("I found some relevant information in the knowledge base that might help")
        
        return suggestions
