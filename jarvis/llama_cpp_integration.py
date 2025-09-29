"""
Advanced llama.cpp Integration for Terminal Jarvis
Uses native llama.cpp for optimal performance and compatibility
"""

import os
import subprocess
import json
import requests
import threading
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Generator
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class LlamaCppServer:
    """Manages llama.cpp server for optimal performance"""
    
    def __init__(self, model_path: str, port: int = 8080, host: str = "localhost"):
        self.model_path = model_path
        self.port = port
        self.host = host
        self.server_process = None
        self.server_url = f"http://{host}:{port}"
        self.is_running = False
        
    def start_server(self, gpu_layers: int = 0, context_size: int = 4096, 
                    threads: Optional[int] = None) -> bool:
        """Start the llama.cpp server"""
        try:
            # Check if llama-server is available
            llama_server_path = self._find_llama_server()
            if not llama_server_path:
                logger.error("llama-server not found. Please install llama.cpp")
                return False
            
            # Build command
            cmd = [
                llama_server_path,
                "-m", self.model_path,
                "--port", str(self.port),
                "--host", self.host,
                "-c", str(context_size),
                "-ngl", str(gpu_layers)
            ]
            
            if threads:
                cmd.extend(["-t", str(threads)])
            
            # Start server
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            if self._wait_for_server():
                self.is_running = True
                logger.info(f"llama.cpp server started on {self.server_url}")
                return True
            else:
                logger.error("Failed to start llama.cpp server")
                return False
                
        except Exception as e:
            logger.error(f"Error starting llama.cpp server: {e}")
            return False
    
    def stop_server(self):
        """Stop the llama.cpp server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.is_running = False
            logger.info("llama.cpp server stopped")
    
    def _find_llama_server(self) -> Optional[str]:
        """Find llama-server executable"""
        # Check common locations
        possible_paths = [
            "llama-server",
            "llama-server.exe",
            "./llama-server",
            "./llama-server.exe",
            "C:\\Program Files\\llama.cpp\\llama-server.exe",
            "/usr/local/bin/llama-server",
            "/opt/homebrew/bin/llama-server"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--help"], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def _wait_for_server(self, timeout: int = 30) -> bool:
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.server_url}/health", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       max_tokens: int = 1024, temperature: float = 0.7,
                       stream: bool = True) -> Generator[str, None, None]:
        """Send chat completion request to llama.cpp server"""
        if not self.is_running:
            raise RuntimeError("Server is not running")
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            if stream:
                response = requests.post(
                    f"{self.server_url}/v1/chat/completions",
                    json=payload,
                    stream=True,
                    timeout=30
                )
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                else:
                    logger.error(f"Server error: {response.status_code}")
            else:
                response = requests.post(
                    f"{self.server_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        yield content
                else:
                    logger.error(f"Server error: {response.status_code}")
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise


class AdvancedLlamaCpp:
    """Advanced llama.cpp integration with Hugging Face support"""
    
    def __init__(self, model_path: str = None, hf_repo: str = None, 
                 hf_filename: str = None, port: int = 8080):
        self.model_path = model_path
        self.hf_repo = hf_repo
        self.hf_filename = hf_filename
        self.port = port
        self.server = None
        self.cache_dir = os.getenv("LLAMA_CACHE", os.path.expanduser("~/.cache/llama.cpp"))
        
    def setup_model(self) -> bool:
        """Setup model for use"""
        try:
            if self.hf_repo and self.hf_filename:
                # Use Hugging Face model
                model_path = self._download_hf_model()
                if not model_path:
                    return False
            elif self.model_path and os.path.exists(self.model_path):
                # Use local model
                model_path = self.model_path
            else:
                logger.error("No valid model path provided")
                return False
            
            # Start server
            self.server = LlamaCppServer(model_path, self.port)
            return self.server.start_server()
            
        except Exception as e:
            logger.error(f"Error setting up model: {e}")
            return False
    
    def _download_hf_model(self) -> Optional[str]:
        """Download model from Hugging Face"""
        try:
            # Create cache directory
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # Use huggingface-hub to download
            from huggingface_hub import hf_hub_download
            
            model_path = hf_hub_download(
                repo_id=self.hf_repo,
                filename=self.hf_filename,
                cache_dir=self.cache_dir
            )
            
            logger.info(f"Downloaded model to: {model_path}")
            return model_path
            
        except ImportError:
            logger.error("huggingface-hub not installed. Install with: pip install huggingface-hub")
            return None
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return None
    
    def stream_chat(self, messages: List[Dict[str, str]], 
                   max_tokens: int = 1024, temperature: float = 0.7) -> Generator[str, None, None]:
        """Stream chat completion"""
        if not self.server or not self.server.is_running:
            raise RuntimeError("Model not set up or server not running")
        
        try:
            for content in self.server.chat_completion(messages, max_tokens, temperature, stream=True):
                yield content
        except Exception as e:
            logger.error(f"Error in stream_chat: {e}")
            raise
    
    def cleanup(self):
        """Cleanup resources"""
        if self.server:
            self.server.stop_server()


class LlamaCppInstaller:
    """Helper class to install llama.cpp"""
    
    @staticmethod
    def install_windows() -> bool:
        """Install llama.cpp on Windows using winget"""
        try:
            result = subprocess.run(
                ["winget", "install", "llama.cpp"],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error installing llama.cpp: {e}")
            return False
    
    @staticmethod
    def install_mac_linux() -> bool:
        """Install llama.cpp on Mac/Linux using brew"""
        try:
            result = subprocess.run(
                ["brew", "install", "llama.cpp"],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error installing llama.cpp: {e}")
            return False
    
    @staticmethod
    def build_from_source() -> bool:
        """Build llama.cpp from source"""
        try:
            # Clone repository
            if not os.path.exists("llama.cpp"):
                subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"])
            
            os.chdir("llama.cpp")
            
            # Build
            subprocess.run(["cmake", "-B", "build"])
            subprocess.run(["cmake", "--build", "build", "--config", "Release"])
            
            return True
        except Exception as e:
            logger.error(f"Error building from source: {e}")
            return False


def get_recommended_models() -> List[Dict[str, str]]:
    """Get list of recommended GGUF models"""
    return [
        {
            "name": "Llama 3.2 3B Instruct",
            "repo": "bartowski/Llama-3.2-3B-Instruct-GGUF",
            "filename": "Llama-3.2-3B-Instruct-Q8_0.gguf",
            "size": "3B",
            "description": "Fast, efficient 3B parameter model"
        },
        {
            "name": "Llama 3.2 1B Instruct",
            "repo": "bartowski/Llama-3.2-1B-Instruct-GGUF",
            "filename": "Llama-3.2-1B-Instruct-Q8_0.gguf",
            "size": "1B",
            "description": "Ultra-fast 1B parameter model"
        },
        {
            "name": "Qwen2 7B Instruct",
            "repo": "Qwen/Qwen2-7B-Instruct-GGUF",
            "filename": "qwen2-7b-instruct-q8_0.gguf",
            "size": "7B",
            "description": "High-quality 7B parameter model"
        },
        {
            "name": "Phi-3 Mini 4K Instruct",
            "repo": "microsoft/Phi-3-mini-4k-instruct-gguf",
            "filename": "Phi-3-mini-4k-instruct-q8.gguf",
            "size": "3.8B",
            "description": "Microsoft's efficient 3.8B model"
        },
        {
            "name": "CodeLlama 7B Instruct",
            "repo": "TheBloke/CodeLlama-7B-Instruct-GGUF",
            "filename": "codellama-7b-instruct.Q8_0.gguf",
            "size": "7B",
            "description": "Specialized for coding tasks"
        }
    ]


def check_llama_cpp_installation() -> Dict[str, Any]:
    """Check if llama.cpp is installed and working"""
    result = {
        "installed": False,
        "version": None,
        "server_path": None,
        "cli_path": None
    }
    
    # Check for llama-server
    try:
        server_result = subprocess.run(
            ["llama-server", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if server_result.returncode == 0:
            result["installed"] = True
            result["server_path"] = "llama-server"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check for llama-cli
    try:
        cli_result = subprocess.run(
            ["llama-cli", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if cli_result.returncode == 0:
            result["installed"] = True
            result["cli_path"] = "llama-cli"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return result
