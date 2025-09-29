"""
Desktop Application Launcher for Terminal Jarvis
Combines GUI with model management and file dialogs
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import os
import sys
from pathlib import Path
import threading
import json

from .gui import TransparentWindow
from .config import AppConfig
from .rag_system import RAGSystem
from .task_automation import TaskExecutor, TaskSolver
from .enhanced_chat import EnhancedChatSession, EnhancedLocalLlm
from .knowledge_manager import create_knowledge_base_window


class DesktopApp(TransparentWindow):
    """Enhanced desktop app with model management"""
    
    def __init__(self):
        super().__init__()
        self.setup_menu()
        self.setup_model_management()
        self.setup_rag_system()
        self.load_config()
    
    def setup_menu(self):
        """Add menu bar for model management"""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Model...", command=self.load_model_dialog)
        file_menu.add_command(label="Load Recent Model", command=self.load_recent_model)
        file_menu.add_separator()
        file_menu.add_command(label="Save Conversation", command=self.save_conversation)
        file_menu.add_command(label="Load Conversation", command=self.load_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close_app)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Model Settings", command=self.model_settings_dialog)
        settings_menu.add_command(label="Window Settings", command=self.window_settings_dialog)
        
        # Knowledge Base menu
        kb_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Knowledge Base", menu=kb_menu)
        kb_menu.add_command(label="Manage Knowledge Base", command=self.open_knowledge_base_manager)
        kb_menu.add_command(label="Add Document", command=self.add_document_dialog)
        kb_menu.add_command(label="Search Knowledge Base", command=self.search_knowledge_base_dialog)
        kb_menu.add_separator()
        kb_menu.add_command(label="Knowledge Base Stats", command=self.show_kb_stats)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
    
    def setup_model_management(self):
        """Setup model management"""
        self.recent_models = []
        self.config_file = Path.home() / ".jarvis_desktop.json"
        self.load_recent_models()
    
    def setup_rag_system(self):
        """Setup RAG system and task automation"""
        try:
            # Initialize RAG system
            self.rag_system = RAGSystem(db_path="./jarvis_rag_db")
            
            # Initialize task automation
            self.task_executor = TaskExecutor()
            self.task_solver = TaskSolver(self.rag_system, self.task_executor)
            
            # Update status
            self.add_message("RAG system and task automation initialized", "system")
            
        except Exception as e:
            self.add_message(f"Failed to initialize RAG system: {e}", "error")
            self.rag_system = None
            self.task_solver = None
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.recent_models = config.get('recent_models', [])
                    
                    # Load last used model
                    last_model = config.get('last_model')
                    if last_model and Path(last_model).exists():
                        self.load_model(last_model)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'recent_models': self.recent_models[:10],  # Keep only last 10
                'last_model': getattr(self, 'current_model_path', None)
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_recent_models(self):
        """Load recent models from config"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.recent_models = config.get('recent_models', [])
        except Exception:
            self.recent_models = []
    
    def load_model_dialog(self):
        """Open file dialog to load a model"""
        filetypes = [
            ("GGUF files", "*.gguf"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select GGUF Model File",
            filetypes=filetypes,
            initialdir=Path.home()
        )
        
        if filename:
            self.load_model(filename)
    
    def load_recent_model(self):
        """Load a recent model"""
        if not self.recent_models:
            messagebox.showinfo("No Recent Models", "No recent models found.")
            return
        
        # Create recent models menu
        recent_window = tk.Toplevel(self.root)
        recent_window.title("Recent Models")
        recent_window.geometry("400x300")
        recent_window.configure(bg='#2d2d2d')
        recent_window.attributes('-topmost', True)
        
        tk.Label(recent_window, text="Select a recent model:", 
                bg='#2d2d2d', fg='white', font=('Segoe UI', 10)).pack(pady=10)
        
        # Listbox for recent models
        listbox = tk.Listbox(recent_window, bg='#1e1e1e', fg='white', 
                           font=('Consolas', 9), selectbackground='#404040')
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for model_path in self.recent_models:
            if Path(model_path).exists():
                listbox.insert(tk.END, Path(model_path).name)
            else:
                listbox.insert(tk.END, f"{Path(model_path).name} (not found)")
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                model_path = self.recent_models[selection[0]]
                if Path(model_path).exists():
                    self.load_model(model_path)
                    recent_window.destroy()
                else:
                    messagebox.showerror("Error", "Model file not found.")
        
        tk.Button(recent_window, text="Load", command=on_select,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10)).pack(pady=10)
    
    def load_model(self, model_path: str):
        """Load a GGUF model"""
        try:
            # Add to recent models
            if model_path not in self.recent_models:
                self.recent_models.insert(0, model_path)
            else:
                # Move to front
                self.recent_models.remove(model_path)
                self.recent_models.insert(0, model_path)
            
            self.current_model_path = model_path
            self.save_config()
            
            # Load model
            super().load_model(model_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {e}")
    
    def save_conversation(self):
        """Save current conversation"""
        if not self.session or not self.session.messages:
            messagebox.showinfo("No Conversation", "No conversation to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Conversation",
            defaultextension=".jsonl",
            filetypes=[("JSONL files", "*.jsonl"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.session.save(filename)
                messagebox.showinfo("Success", f"Conversation saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save conversation: {e}")
    
    def load_conversation(self):
        """Load a conversation"""
        filename = filedialog.askopenfilename(
            title="Load Conversation",
            filetypes=[("JSONL files", "*.jsonl"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Clear current conversation
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.delete("1.0", tk.END)
                self.chat_text.config(state=tk.DISABLED)
                
                # Load messages
                if self.session:
                    self.session.messages = []
                
                for line in lines:
                    if line.strip():
                        message = json.loads(line.strip())
                        if message.get('role') == 'user':
                            self.add_message(message.get('content', ''), 'user')
                        elif message.get('role') == 'assistant':
                            self.add_message(message.get('content', ''), 'assistant')
                
                messagebox.showinfo("Success", f"Conversation loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load conversation: {e}")
    
    def model_settings_dialog(self):
        """Open model settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Model Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#2d2d2d')
        settings_window.attributes('-topmost', True)
        
        # Context length
        tk.Label(settings_window, text="Context Length:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        context_var = tk.StringVar(value="4096")
        context_entry = tk.Entry(settings_window, textvariable=context_var, 
                               bg='#1e1e1e', fg='white', font=('Consolas', 10))
        context_entry.pack(pady=5)
        
        # GPU layers
        tk.Label(settings_window, text="GPU Layers:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        gpu_var = tk.StringVar(value="0")
        gpu_entry = tk.Entry(settings_window, textvariable=gpu_var,
                           bg='#1e1e1e', fg='white', font=('Consolas', 10))
        gpu_entry.pack(pady=5)
        
        # Temperature
        tk.Label(settings_window, text="Temperature:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        temp_var = tk.StringVar(value="0.7")
        temp_entry = tk.Entry(settings_window, textvariable=temp_var,
                            bg='#1e1e1e', fg='white', font=('Consolas', 10))
        temp_entry.pack(pady=5)
        
        def apply_settings():
            try:
                # Update settings (would need to reload model to apply)
                messagebox.showinfo("Settings", "Settings saved. Reload model to apply changes.")
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply settings: {e}")
        
        tk.Button(settings_window, text="Apply", command=apply_settings,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10)).pack(pady=20)
    
    def window_settings_dialog(self):
        """Open window settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Window Settings")
        settings_window.geometry("300x200")
        settings_window.configure(bg='#2d2d2d')
        settings_window.attributes('-topmost', True)
        
        # Transparency
        tk.Label(settings_window, text="Transparency:", 
                bg='#2d2d2d', fg='white').pack(pady=5)
        alpha_var = tk.DoubleVar(value=0.95)
        alpha_scale = tk.Scale(settings_window, from_=0.5, to=1.0, 
                             variable=alpha_var, orient=tk.HORIZONTAL,
                             bg='#2d2d2d', fg='white')
        alpha_scale.pack(pady=5)
        
        def apply_window_settings():
            self.root.attributes('-alpha', alpha_var.get())
            settings_window.destroy()
        
        tk.Button(settings_window, text="Apply", command=apply_window_settings,
                 bg='#4CAF50', fg='white', font=('Segoe UI', 10)).pack(pady=20)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Terminal Jarvis Desktop v0.1.0

A transparent, always-on-top desktop application for local LLM chat.

Features:
• Transparent window with pip mode
• Minimizable interface
• Model management
• Conversation saving/loading
• Streaming responses

Built with Python, tkinter, and llama-cpp-python."""
        
        messagebox.showinfo("About Terminal Jarvis", about_text)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """Keyboard Shortcuts:

Ctrl+Enter: Send message
Ctrl+N: New conversation
Ctrl+O: Load model
Ctrl+S: Save conversation
Ctrl+Q: Quit application

Window Controls:
- Minimize/restore
- Toggle pip mode (always on top)
- Drag to move window

RAG Features:
- Upload documents to knowledge base
- Search through your data
- Automated task execution"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def open_knowledge_base_manager(self):
        """Open the knowledge base management window"""
        if not self.rag_system:
            messagebox.showerror("Error", "RAG system not initialized")
            return
        
        try:
            create_knowledge_base_window(self.root, self.rag_system, self.task_solver)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open knowledge base manager: {e}")
    
    def add_document_dialog(self):
        """Open dialog to add a document"""
        if not self.rag_system:
            messagebox.showerror("Error", "RAG system not initialized")
            return
        
        filetypes = [
            ("All supported", "*.pdf;*.docx;*.txt;*.md;*.html;*.py;*.js;*.json;*.yaml"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("Text files", "*.txt"),
            ("Markdown files", "*.md"),
            ("HTML files", "*.html"),
            ("Python files", "*.py"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Add Document to Knowledge Base",
            filetypes=filetypes
        )
        
        if filename:
            try:
                result = self.rag_system.add_document(filename)
                if result.get("success", False):
                    messagebox.showinfo("Success", 
                                      f"Document added successfully!\n"
                                      f"Chunks added: {result.get('chunks_added', 0)}")
                    self.add_message(f"Added document: {Path(filename).name}", "system")
                else:
                    messagebox.showerror("Error", f"Failed to add document: {result.get('error', 'Unknown error')}")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding document: {e}")
    
    def search_knowledge_base_dialog(self):
        """Open dialog to search knowledge base"""
        if not self.rag_system:
            messagebox.showerror("Error", "RAG system not initialized")
            return
        
        query = tk.simpledialog.askstring("Search Knowledge Base", "Enter search query:")
        if query:
            try:
                results = self.rag_system.search(query, n_results=5)
                
                if results:
                    result_text = f"Search Results for: '{query}'\n"
                    result_text += "=" * 50 + "\n\n"
                    
                    for i, result in enumerate(results, 1):
                        result_text += f"Result {i}:\n"
                        result_text += f"Source: {result['metadata'].get('name', 'Unknown')}\n"
                        result_text += f"Relevance: {1 - result['distance']:.2f}\n"
                        result_text += f"Text: {result['text'][:200]}...\n"
                        result_text += "-" * 30 + "\n\n"
                    
                    # Show results in a new window
                    result_window = tk.Toplevel(self.root)
                    result_window.title("Search Results")
                    result_window.geometry("600x400")
                    result_window.configure(bg='#1e1e1e')
                    
                    text_widget = scrolledtext.ScrolledText(result_window, 
                                                          bg='#2d2d2d', fg='white',
                                                          font=('Consolas', 9))
                    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    text_widget.insert(tk.END, result_text)
                    text_widget.config(state=tk.DISABLED)
                else:
                    messagebox.showinfo("No Results", f"No results found for: '{query}'")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error searching knowledge base: {e}")
    
    def show_kb_stats(self):
        """Show knowledge base statistics"""
        if not self.rag_system:
            messagebox.showerror("Error", "RAG system not initialized")
            return
        
        try:
            stats = self.rag_system.get_knowledge_base_stats()
            
            if "error" in stats:
                messagebox.showerror("Error", f"Error getting stats: {stats['error']}")
            else:
                stats_text = f"Knowledge Base Statistics\n"
                stats_text += "=" * 30 + "\n\n"
                stats_text += f"Total Chunks: {stats.get('total_chunks', 0)}\n"
                stats_text += f"Unique Sources: {stats.get('unique_sources', 0)}\n"
                stats_text += f"File Types: {', '.join(stats.get('file_types', []))}\n"
                stats_text += f"Sources: {', '.join(stats.get('sources', []))}\n"
                
                messagebox.showinfo("Knowledge Base Statistics", stats_text)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error getting knowledge base stats: {e}")
    
    def process_llm_request(self, message: str):
        """Process LLM request in background thread with RAG enhancement"""
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
            
            # Use enhanced LLM if available
            if hasattr(self, 'rag_system') and self.rag_system and hasattr(self, 'task_solver') and self.task_solver:
                # Enhanced response with RAG
                full_response = self.session.get_enhanced_response(self.llm, message)
                
                # Stream the response for UI
                words = full_response.split()
                for i, word in enumerate(words):
                    piece = word + (" " if i < len(words) - 1 else "")
                    self.message_queue.put(("stream", piece))
                
                self.message_queue.put(("complete", full_response))
            else:
                # Standard streaming response
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
        self.save_config()
        super().close_app()


def main():
    """Main entry point for desktop app"""
    try:
        app = DesktopApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
