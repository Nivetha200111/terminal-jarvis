#!/usr/bin/env python3
"""
Desktop Launcher for Terminal Jarvis
Launches the transparent desktop GUI application
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the desktop application"""
    try:
        from jarvis.desktop_app import main as desktop_main
        desktop_main()
    except ImportError as e:
        print(f"Error importing desktop app: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting desktop app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
