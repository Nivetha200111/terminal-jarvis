#!/usr/bin/env python3
"""
Install llama.cpp for Terminal Jarvis
Supports Windows, Mac, and Linux
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path

def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "mac"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def check_winget():
    """Check if winget is available on Windows"""
    try:
        result = subprocess.run(["winget", "--version"], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_brew():
    """Check if brew is available on Mac/Linux"""
    try:
        result = subprocess.run(["brew", "--version"], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_windows():
    """Install llama.cpp on Windows"""
    print("Installing llama.cpp on Windows...")
    
    if check_winget():
        print("Using winget to install llama.cpp...")
        try:
            result = subprocess.run(["winget", "install", "llama.cpp"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ llama.cpp installed successfully via winget!")
                return True
            else:
                print(f"❌ winget installation failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    else:
        print("❌ winget not found. Please install winget first.")
        print("Download from: https://github.com/microsoft/winget-cli")
        return False

def install_mac_linux():
    """Install llama.cpp on Mac/Linux"""
    print("Installing llama.cpp on Mac/Linux...")
    
    if check_brew():
        print("Using brew to install llama.cpp...")
        try:
            result = subprocess.run(["brew", "install", "llama.cpp"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ llama.cpp installed successfully via brew!")
                return True
            else:
                print(f"❌ brew installation failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    else:
        print("❌ brew not found. Please install Homebrew first.")
        print("Install from: https://brew.sh")
        return False

def build_from_source():
    """Build llama.cpp from source"""
    print("Building llama.cpp from source...")
    
    try:
        # Clone repository
        if not Path("llama.cpp").exists():
            print("Cloning llama.cpp repository...")
            result = subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"❌ Failed to clone repository: {result.stderr}")
                return False
        
        # Change to llama.cpp directory
        os.chdir("llama.cpp")
        
        # Build
        print("Building llama.cpp...")
        result = subprocess.run(["cmake", "-B", "build"], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"❌ CMake configuration failed: {result.stderr}")
            return False
        
        result = subprocess.run(["cmake", "--build", "build", "--config", "Release"], 
                              capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False
        
        print("✅ llama.cpp built successfully from source!")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Build timed out")
        return False
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

def download_prebuilt():
    """Download pre-built binaries"""
    print("Downloading pre-built binaries...")
    
    os_name = detect_os()
    if os_name == "windows":
        url = "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b2308-bin-win-avx2-x64.zip"
    elif os_name == "mac":
        url = "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b2308-bin-macos-arm64.zip"
    elif os_name == "linux":
        url = "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b2308-bin-ubuntu-22.04-avx2-x64.zip"
    else:
        print("❌ Unsupported operating system for pre-built binaries")
        return False
    
    print(f"Please download from: {url}")
    print("Extract the files and add them to your PATH")
    webbrowser.open(url)
    return True

def verify_installation():
    """Verify llama.cpp installation"""
    print("\nVerifying installation...")
    
    try:
        # Check llama-server
        result = subprocess.run(["llama-server", "--help"], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ llama-server found")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    try:
        # Check llama-cli
        result = subprocess.run(["llama-cli", "--help"], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ llama-cli found")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ llama.cpp not found in PATH")
    return False

def main():
    """Main installation function"""
    print("Terminal Jarvis - llama.cpp Installer")
    print("="*40)
    
    os_name = detect_os()
    print(f"Detected OS: {os_name}")
    
    # Check if already installed
    if verify_installation():
        print("✅ llama.cpp is already installed!")
        return 0
    
    print("\nInstallation options:")
    print("1. Auto-install (winget/brew)")
    print("2. Build from source")
    print("3. Download pre-built binaries")
    print("4. Manual installation guide")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    success = False
    
    if choice == "1":
        if os_name == "windows":
            success = install_windows()
        elif os_name in ["mac", "linux"]:
            success = install_mac_linux()
        else:
            print("❌ Auto-install not supported on this OS")
    
    elif choice == "2":
        success = build_from_source()
    
    elif choice == "3":
        success = download_prebuilt()
    
    elif choice == "4":
        print("\nManual Installation Guide:")
        print("1. Visit: https://github.com/ggerganov/llama.cpp")
        print("2. Download the latest release for your OS")
        print("3. Extract the files")
        print("4. Add the directory to your PATH")
        print("5. Verify with: llama-server --help")
        return 0
    
    else:
        print("❌ Invalid option")
        return 1
    
    if success:
        print("\n" + "="*40)
        print("Installation completed!")
        
        if verify_installation():
            print("✅ llama.cpp is ready to use!")
            print("\nYou can now run: python launch_advanced.py")
        else:
            print("⚠️  Installation completed but llama.cpp not found in PATH")
            print("You may need to restart your terminal or add to PATH manually")
    else:
        print("\n❌ Installation failed")
        print("Please try manual installation or check the error messages above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
