#!/usr/bin/env python3
"""
Launch Advanced Terminal Jarvis with llama.cpp Integration
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import tkinter
        import requests
        import chromadb
        import sentence_transformers
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install missing dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def check_llama_cpp():
    """Check if llama.cpp is available"""
    try:
        result = subprocess.run(["llama-server", "--help"], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def show_llama_cpp_help():
    """Show llama.cpp installation help"""
    print("\n" + "="*60)
    print("llama.cpp Installation Required")
    print("="*60)
    print("\nTo use the advanced features, you need to install llama.cpp:")
    print("\n1. Windows (winget):")
    print("   winget install llama.cpp")
    print("\n2. Mac/Linux (brew):")
    print("   brew install llama.cpp")
    print("\n3. Build from source:")
    print("   git clone https://github.com/ggerganov/llama.cpp")
    print("   cd llama.cpp")
    print("   cmake -B build")
    print("   cmake --build build --config Release")
    print("\n4. Download pre-built binaries:")
    print("   https://github.com/ggerganov/llama.cpp/releases")
    print("\n" + "="*60)

def main():
    """Main launcher function"""
    print("Terminal Jarvis - Advanced Launcher")
    print("="*40)
    
    # Check if we're in the right directory
    if not Path("jarvis").exists():
        print("Error: Please run this script from the terminal-jarvis directory")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("Installing missing dependencies...")
        if not install_dependencies():
            print("Failed to install dependencies. Please run: pip install -r requirements.txt")
            return 1
    
    # Check llama.cpp
    llama_cpp_available = check_llama_cpp()
    
    if not llama_cpp_available:
        print("⚠️  llama.cpp not found")
        show_llama_cpp_help()
        
        choice = input("\nDo you want to continue without llama.cpp? (y/n): ").lower()
        if choice != 'y':
            return 1
    
    # Launch the appropriate version
    try:
        if llama_cpp_available:
            print("🚀 Launching Advanced Terminal Jarvis with llama.cpp...")
            from jarvis.advanced_desktop_app import main as advanced_main
            advanced_main()
        else:
            print("🚀 Launching Standard Terminal Jarvis...")
            from jarvis.desktop_app import main as standard_main
            standard_main()
    except ImportError as e:
        print(f"Error importing desktop app: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error launching application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
