#!/usr/bin/env python3
"""
Terminal Jarvis Demo Script
Demonstrates both CLI and Desktop GUI interfaces
"""

import sys
import os
from pathlib import Path

def show_banner():
    """Display the Terminal Jarvis banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Terminal Jarvis v0.1.0                    ║
║              Local LLM with Desktop GUI & CLI                ║
╚══════════════════════════════════════════════════════════════╝

Choose your interface:

1. 🖥️  Desktop GUI (Transparent, Always-on-Top, Minimizable)
2. 💻  Terminal CLI (Command-line Interface)
3. 🧪  Demo Mode (Mock LLM - No Model Required)
4. ❌  Exit

"""
    print(banner)

def run_desktop_gui():
    """Launch the desktop GUI"""
    print("Launching Desktop GUI...")
    print("Features:")
    print("  • Transparent window with modern dark theme")
    print("  • Pip mode (always on top)")
    print("  • Minimizable and draggable")
    print("  • Model management and conversation saving")
    print("  • Streaming responses")
    print()
    
    try:
        from jarvis.desktop_app import main as desktop_main
        desktop_main()
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Error launching desktop app: {e}")

def run_terminal_cli():
    """Launch the terminal CLI"""
    print("Launching Terminal CLI...")
    print("Usage: python -m jarvis --model path/to/model.gguf")
    print()
    
    try:
        from jarvis.__main__ import main as cli_main
        cli_main()
    except Exception as e:
        print(f"Error launching CLI: {e}")

def run_demo_mode():
    """Run demo mode with mock LLM"""
    print("Running Demo Mode...")
    print("This uses a mock LLM - no real model required!")
    print()
    
    try:
        exec(open('test_demo.py').read())
    except Exception as e:
        print(f"Error running demo: {e}")

def main():
    """Main demo interface"""
    while True:
        show_banner()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                run_desktop_gui()
                break
            elif choice == "2":
                run_terminal_cli()
                break
            elif choice == "3":
                run_demo_mode()
                break
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
