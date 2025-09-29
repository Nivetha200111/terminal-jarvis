"""
Advanced Desktop App with llama.cpp Integration
Uses native llama.cpp for optimal performance
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import os
import sys
from pathlib import Path
import threading
import json
import webbrowser

from .gui import TransparentWindow
from .config import AppConfig
from .rag_system import RAGSystem
from .task_automation import TaskExecutor, TaskSolver
from .enhanced_chat import EnhancedChatSession
from .knowledge_manager import create_knowledge_base_window
from .llama_cpp_integration import (
    AdvancedLlamaCpp, LlamaCppInstaller, 
    get_recommended_models, check_llama_cpp_installation
)


class AdvancedDesktopApp(TransparentWindow):
    """Advanced desktop app with llama.cpp integration"""
    
    def __init__(self):
        super().__init__()
        self.setup_menu()
        self.setup_model_management()
        self.setup_rag_system()
        self.setup_llama_cpp()
        self.load_config()
    
    def setup_menu(self):
        """Add enhanced menu bar"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Model...", command=self.load_model_dialog)
        file_menu.add_command(label="Load Hugging Face Model...", command=self.load_hf_model_dialog)
        file_menu.add_command(label="Load Recent Model", command=self.load_recent_model)
        file_menu.add_separator()
        file_menu.add_command(label="Save Conversation", command=self.save_conversation)
        file_menu.add_command(label="Load Conversation", command=self.load_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close_app)
        
        # Model menu
        model_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Model", menu=model_menu)
        model_menu.add_command(label="Recommended Models", command=self.show_recommended_models)
        model_menu.add_command(label="Install llama.cpp", command=self.install_llama_cpp)
        model_menu.add_command(label="Check Installation", command=self.check_installation)
        model_menu.add_separator()
        model_menu.add_command(label="Model Settings", command=self.model_settings_dialog)
        
        # Knowledge Base menu
        kb_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Knowledge Base", menu=kb_menu)
        kb_menu.add_command(label="Manage Knowledge Base", command=self.open_knowledge_base_manager)
        kb_menu.add_command(label="Add Document", command=self.add_document_dialog)
        kb_menu.add_command(label="Search Knowledge Base", command=self.search_knowledge_base_dialog)
        kb_menu.add_separator()
        kb_menu.add_command(label="Knowledge Base Stats", command=self.show_kb_stats)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Window Settings", command=self.window_settings_dialog)
        settings_menu.add_command(label="Server Settings", command=self.server_settings_dialog)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Open Documentation", command=self.open_documentation)
    
    def setup_llama_cpp(self):
        """Setup llama.cpp integration"""
        try:
            # Check if llama.cpp is installed
            self.llama_cpp_status = check_llama_cpp_installation()
            
            if self.llama_cpp_status["installed"]:
                self.add_message("llama.cpp detected and ready", "system")
            else:
                self.add_message("llama.cpp not found. Use Model → Install llama.cpp", "system")
            
            self.advanced_llm = None
            
        except Exception as e:
            self.add_message(f"Error setting up llama.cpp: {e}", "error")
            self.llama_cpp_status = {"installed": False}
    
    def load_hf_model_dialog(self):
        """Open dialog to load Hugging Face model"""
        if not self.llama_cpp_status["installed"]:
            messagebox.showerror("Error", "llama.cpp not installed. Please install it first.")
            return
        
        # Create model selection window
        model_window = tk.Toplevel(self.root)
        model_window.title("Load Hugging Face Model")
        model_window.geometry("600x400")
        model_window.configure(bg='#1e1e1e')
        model_window.attributes('-topmost', True)
        
        # Title
        title_label = tk.Label(model_window, text="Select a Recommended Model", 
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#1e1e1e')
        title_label.pack(pady=10)
        
        # Models list
        models_frame = ttk.Frame(model_window, style='Main.TFrame')
        models_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox for models
        listbox = tk.Listbox(models_frame, bg='#2d2d2d', fg='white', 
                           font=('Consolas', 10), selectbackground='#404040')
        listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add models to listbox
        models = get_recommended_models()
        for i, model in enumerate(models):
            display_text = f"{model['name']} ({model['size']}) - {model['description']}"
            listbox.insert(tk.END, display_text)
        
        # Custom model input
        custom_frame = ttk.Frame(model_window, style='Main.TFrame')
        custom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(custom_frame, text="Or enter custom model:", 
                bg='#1e1e1e', fg='white').pack(anchor=tk.W)
        
        input_frame = ttk.Frame(custom_frame, style='Main.TFrame')
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Repo:", bg='#1e1e1e', fg='white').pack(side=tk.LEFT)
        repo_var = tk.StringVar()
        repo_entry = tk.Entry(input_frame, textvariable=repo_var, 
                            bg='#2d2d2d', fg='white', font=('Consolas', 10))
        repo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        
        tk.Label(input_frame, text="File:", bg='#1e1e1e', fg='white').pack(side=tk.LEFT)
        file_var = tk.StringVar()
        file_entry = tk.Entry(input_frame, textvariable=file_var, 
                            bg='#2d2d2d', fg='white', font=('Consolas', 10))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        def on_load():
            selection = listbox.curselection()
            if selection:
                # Load selected model
                model = models[selection[0]]
                self.load_hf_model(model['repo'], model['filename'])
                model_window.destroy()
            elif repo_var.get() and file_var.get():
                # Load custom model
                self.load_hf_model(repo_var.get(), file_var.get())
                model_window.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a model or enter custom details.")
        
        # Buttons
        button_frame = ttk.Frame(model_window, style='Main.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Load Model", command=on_load,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="Cancel", command=model_window.destroy,
                 bg='#F44336', fg='white', font=('Segoe UI', 10)).pack(side=tk.RIGHT)
    
    def load_hf_model(self, repo: str, filename: str):
        """Load Hugging Face model"""
        try:
            self.add_message(f"Loading model from {repo}...", "system")
            self.status_label.config(text="Loading model...")
            
            # Create advanced llama.cpp instance
            self.advanced_llm = AdvancedLlamaCpp(hf_repo=repo, hf_filename=filename)
            
            # Setup model in background
            def setup_model():
                try:
                    success = self.advanced_llm.setup_model()
                    if success:
                        self.message_queue.put(("system", f"Model loaded successfully: {repo}"))
                        self.message_queue.put(("status", "Ready - Model loaded"))
                    else:
                        self.message_queue.put(("error", "Failed to load model"))
                        self.message_queue.put(("status", "Ready - No model loaded"))
                except Exception as e:
                    self.message_queue.put(("error", f"Error loading model: {e}"))
                    self.message_queue.put(("status", "Ready - No model loaded"))
            
            threading.Thread(target=setup_model, daemon=True).start()
            
        except Exception as e:
            self.add_message(f"Error loading model: {e}", "error")
    
    def show_recommended_models(self):
        """Show recommended models window"""
        models_window = tk.Toplevel(self.root)
        models_window.title("Recommended GGUF Models")
        models_window.geometry("700x500")
        models_window.configure(bg='#1e1e1e')
        models_window.attributes('-topmost', True)
        
        # Title
        title_label = tk.Label(models_window, text="Recommended GGUF Models", 
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#1e1e1e')
        title_label.pack(pady=10)
        
        # Models list
        models_frame = ttk.Frame(models_window, style='Main.TFrame')
        models_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text widget for models
        text_widget = scrolledtext.ScrolledText(models_frame, 
                                              bg='#2d2d2d', fg='white',
                                              font=('Consolas', 10), state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add models info
        models = get_recommended_models()
        content = "Recommended GGUF Models for Terminal Jarvis:\n\n"
        
        for i, model in enumerate(models, 1):
            content += f"{i}. {model['name']}\n"
            content += f"   Repository: {model['repo']}\n"
            content += f"   Filename: {model['filename']}\n"
            content += f"   Size: {model['size']}\n"
            content += f"   Description: {model['description']}\n\n"
        
        content += "\nTo use these models:\n"
        content += "1. Go to File → Load Hugging Face Model\n"
        content += "2. Select a model from the list\n"
        content += "3. The model will be downloaded automatically\n\n"
        content += "Note: First download may take time depending on model size."
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
    
    def install_llama_cpp(self):
        """Install llama.cpp"""
        install_window = tk.Toplevel(self.root)
        install_window.title("Install llama.cpp")
        install_window.geometry("500x300")
        install_window.configure(bg='#1e1e1e')
        install_window.attributes('-topmost', True)
        
        # Title
        title_label = tk.Label(install_window, text="Install llama.cpp", 
                              font=('Segoe UI', 14, 'bold'), fg='white', bg='#1e1e1e')
        title_label.pack(pady=10)
        
        # Instructions
        instructions = """
Choose your installation method:

1. Windows (winget):
   winget install llama.cpp

2. Mac/Linux (brew):
   brew install llama.cpp

3. Build from source:
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   cmake -B build
   cmake --build build --config Release

4. Download pre-built binaries:
   https://github.com/ggerganov/llama.cpp/releases
        """
        
        text_widget = scrolledtext.ScrolledText(install_window, 
                                              bg='#2d2d2d', fg='white',
                                              font=('Consolas', 10), state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(install_window, style='Main.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def try_install():
            try:
                if sys.platform == "win32":
                    success = LlamaCppInstaller.install_windows()
                else:
                    success = LlamaCppInstaller.install_mac_linux()
                
                if success:
                    messagebox.showinfo("Success", "llama.cpp installed successfully!")
                    install_window.destroy()
                    self.setup_llama_cpp()  # Refresh status
                else:
                    messagebox.showerror("Error", "Failed to install llama.cpp. Please try manual installation.")
            except Exception as e:
                messagebox.showerror("Error", f"Installation failed: {e}")
        
        tk.Button(button_frame, text="Try Auto Install", command=try_install,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(button_frame, text="Open GitHub", 
                 command=lambda: webbrowser.open("https://github.com/ggerganov/llama.cpp"),
                 bg='#2196F3', fg='white', font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(button_frame, text="Close", command=install_window.destroy,
                 bg='#F44336', fg='white', font=('Segoe UI', 10)).pack(side=tk.RIGHT)
    
    def check_installation(self):
        """Check llama.cpp installation status"""
        status = check_llama_cpp_installation()
        
        status_text = "llama.cpp Installation Status:\n\n"
        status_text += f"Installed: {'Yes' if status['installed'] else 'No'}\n"
        status_text += f"Server Path: {status.get('server_path', 'Not found')}\n"
        status_text += f"CLI Path: {status.get('cli_path', 'Not found')}\n\n"
        
        if status['installed']:
            status_text += "✅ llama.cpp is ready to use!"
        else:
            status_text += "❌ llama.cpp not found. Please install it first."
        
        messagebox.showinfo("Installation Status", status_text)
    
    def server_settings_dialog(self):
        """Open server settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Server Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#2d2d2d')
        settings_window.attributes('-topmost', True)
        
        # Port setting
        tk.Label(settings_window, text="Server Port:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        port_var = tk.StringVar(value="8080")
        port_entry = tk.Entry(settings_window, textvariable=port_var, 
                            bg='#1e1e1e', fg='white', font=('Consolas', 10))
        port_entry.pack(pady=5)
        
        # GPU layers
        tk.Label(settings_window, text="GPU Layers:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        gpu_var = tk.StringVar(value="0")
        gpu_entry = tk.Entry(settings_window, textvariable=gpu_var,
                           bg='#1e1e1e', fg='white', font=('Consolas', 10))
        gpu_entry.pack(pady=5)
        
        # Context size
        tk.Label(settings_window, text="Context Size:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        ctx_var = tk.StringVar(value="4096")
        ctx_entry = tk.Entry(settings_window, textvariable=ctx_var,
                           bg='#1e1e1e', fg='white', font=('Consolas', 10))
        ctx_entry.pack(pady=5)
        
        def apply_settings():
            # Apply settings (would need to restart server)
            messagebox.showinfo("Settings", "Settings saved. Restart model to apply changes.")
            settings_window.destroy()
        
        tk.Button(settings_window, text="Apply", command=apply_settings,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10)).pack(pady=20)
    
    def open_documentation(self):
        """Open documentation in browser"""
        webbrowser.open("https://github.com/Nivetha200111/terminal-jarvis")
    
    def process_llm_request(self, message: str):
        """Process LLM request with advanced llama.cpp integration"""
        try:
            if not self.session:
                # Use enhanced session if RAG is available
                if self.rag_system and self.task_solver:
                    self.session = EnhancedChatSession(console=self.console, 
                                                     rag_system=self.rag_system, 
                                                     task_solver=self.task_solver)
                else:
                    self.session = ChatSession(console=self.console)
            
            self.session.add_user(message)
            
            # Use advanced llama.cpp if available
            if self.advanced_llm and self.advanced_llm.server and self.advanced_llm.server.is_running:
                # Advanced streaming response
                response_parts = []
                for piece in self.advanced_llm.stream_chat(self.session.messages):
                    response_parts.append(piece)
                    # Update UI in main thread
                    self.message_queue.put(("stream", piece))
                
                # Complete response
                full_response = "".join(response_parts)
                self.session.add_assistant(full_response)
                self.message_queue.put(("complete", full_response))
            else:
                # Fallback to standard streaming response
                response_parts = []
                for piece in self.llm.stream_chat(self.session.messages):
                    response_parts.append(piece)
                    # Update UI in main thread
                    self.message_queue.put(("stream", piece))
                
                # Complete response
                full_response = "".join(response_parts)
                self.session.add_assistant(full_response)
                self.message_queue.put(("complete", full_response))
            
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def close_app(self):
        """Close application with cleanup"""
        if self.advanced_llm:
            self.advanced_llm.cleanup()
        self.save_config()
        super().close_app()


def main():
    """Main entry point for advanced desktop app"""
    try:
        app = AdvancedDesktopApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
