"""
Desktop GUI for Terminal Jarvis - Transparent, pip mode, minimizable
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from typing import Optional, Callable
import json
from pathlib import Path

try:
    from jarvis.chat import LocalLlm, ChatSession
    from jarvis.config import AppConfig
except ImportError:
    # Fallback for when running as standalone
    LocalLlm = None
    ChatSession = None
    AppConfig = None


class TransparentWindow:
    """A transparent, always-on-top window with modern styling"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_ui()
        self.setup_bindings()
        
        # State management
        self.is_minimized = False
        self.is_pip_mode = True
        self.llm = None
        self.session = None
        self.message_queue = queue.Queue()
        
        # Start message processing
        self.process_messages()
    
    def setup_window(self):
        """Configure the main window properties"""
        self.root.title("Terminal Jarvis")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Make window transparent
        self.root.attributes('-alpha', 0.95)
        
        # Always on top (pip mode)
        self.root.attributes('-topmost', True)
        
        # Remove window decorations for modern look
        self.root.overrideredirect(True)
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        
        # Configure dark theme
        style.theme_use('clam')
        
        # Main frame style
        style.configure('Main.TFrame', 
                       background='#1e1e1e',
                       borderwidth=0)
        
        # Title bar style
        style.configure('Title.TFrame',
                       background='#2d2d2d',
                       borderwidth=0)
        
        # Button styles
        style.configure('Control.TButton',
                       background='#404040',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 5))
        
        style.map('Control.TButton',
                 background=[('active', '#505050'),
                           ('pressed', '#606060')])
        
        # Text area style
        style.configure('Chat.TFrame',
                       background='#1e1e1e',
                       borderwidth=0)
    
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title bar
        self.create_title_bar()
        
        # Chat area
        self.create_chat_area()
        
        # Input area
        self.create_input_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_title_bar(self):
        """Create the title bar with controls"""
        title_frame = ttk.Frame(self.main_frame, style='Title.TFrame')
        title_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        
        # Title
        title_label = tk.Label(title_frame, 
                              text="Terminal Jarvis",
                              fg='white',
                              bg='#2d2d2d',
                              font=('Segoe UI', 10, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(title_frame, style='Title.TFrame')
        button_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Minimize button
        self.minimize_btn = tk.Button(button_frame,
                                    text="−",
                                    command=self.toggle_minimize,
                                    bg='#404040',
                                    fg='white',
                                    font=('Segoe UI', 12, 'bold'),
                                    borderwidth=0,
                                    width=3,
                                    height=1)
        self.minimize_btn.pack(side=tk.LEFT, padx=2)
        
        # Pip mode toggle
        self.pip_btn = tk.Button(button_frame,
                               text="📌",
                               command=self.toggle_pip_mode,
                               bg='#404040',
                               fg='white',
                               font=('Segoe UI', 10),
                               borderwidth=0,
                               width=3,
                               height=1)
        self.pip_btn.pack(side=tk.LEFT, padx=2)
        
        # Close button
        self.close_btn = tk.Button(button_frame,
                                 text="×",
                                 command=self.close_app,
                                 bg='#e74c3c',
                                 fg='white',
                                 font=('Segoe UI', 12, 'bold'),
                                 borderwidth=0,
                                 width=3,
                                 height=1)
        self.close_btn.pack(side=tk.LEFT, padx=2)
    
    def create_chat_area(self):
        """Create the chat display area"""
        chat_frame = ttk.Frame(self.main_frame, style='Chat.TFrame')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Chat text area
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg='#1e1e1e',
            fg='white',
            font=('Consolas', 10),
            borderwidth=0,
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        self.chat_text.tag_configure("user", foreground="#4CAF50", font=('Consolas', 10, 'bold'))
        self.chat_text.tag_configure("assistant", foreground="#2196F3", font=('Consolas', 10))
        self.chat_text.tag_configure("system", foreground="#FF9800", font=('Consolas', 9, 'italic'))
        self.chat_text.tag_configure("error", foreground="#F44336", font=('Consolas', 9))
    
    def create_input_area(self):
        """Create the input area"""
        input_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        input_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        # Input text box
        self.input_text = tk.Text(input_frame,
                                height=3,
                                bg='#2d2d2d',
                                fg='white',
                                font=('Consolas', 10),
                                borderwidth=1,
                                relief=tk.SOLID,
                                wrap=tk.WORD,
                                padx=10,
                                pady=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Send button
        self.send_btn = tk.Button(input_frame,
                                text="Send",
                                command=self.send_message,
                                bg='#4CAF50',
                                fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                borderwidth=0,
                                width=8,
                                height=2)
        self.send_btn.pack(side=tk.RIGHT, pady=2)
        
        # Bind Enter key to send
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
        self.input_text.bind('<KeyPress>', self.on_input_key)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.status_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        # Status label
        self.status_label = tk.Label(self.status_frame,
                                   text="Ready - No model loaded",
                                   fg='#888888',
                                   bg='#1e1e1e',
                                   font=('Segoe UI', 8),
                                   anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Model info
        self.model_label = tk.Label(self.status_frame,
                                  text="",
                                  fg='#888888',
                                  bg='#1e1e1e',
                                  font=('Segoe UI', 8),
                                  anchor=tk.E)
        self.model_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_bindings(self):
        """Set up window bindings"""
        # Make window draggable
        self.main_frame.bind('<Button-1>', self.start_drag)
        self.main_frame.bind('<B1-Motion>', self.drag_window)
        
        # Focus handling
        self.root.bind('<FocusIn>', self.on_focus_in)
        self.root.bind('<FocusOut>', self.on_focus_out)
    
    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def drag_window(self, event):
        """Drag the window"""
        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")
    
    def on_focus_in(self, event):
        """Handle focus in"""
        self.root.attributes('-alpha', 0.95)
    
    def on_focus_out(self, event):
        """Handle focus out"""
        if not self.is_pip_mode:
            self.root.attributes('-alpha', 0.8)
    
    def toggle_minimize(self):
        """Toggle minimize/restore"""
        if self.is_minimized:
            self.root.deiconify()
            self.minimize_btn.config(text="−")
            self.is_minimized = False
        else:
            self.root.iconify()
            self.minimize_btn.config(text="+")
            self.is_minimized = True
    
    def toggle_pip_mode(self):
        """Toggle pip mode (always on top)"""
        self.is_pip_mode = not self.is_pip_mode
        self.root.attributes('-topmost', self.is_pip_mode)
        
        if self.is_pip_mode:
            self.pip_btn.config(text="📌", bg='#4CAF50')
        else:
            self.pip_btn.config(text="📌", bg='#404040')
    
    def close_app(self):
        """Close the application"""
        self.root.quit()
        self.root.destroy()
    
    def on_input_key(self, event):
        """Handle input key events"""
        # Auto-resize input area
        self.root.after(10, self.auto_resize_input)
    
    def auto_resize_input(self):
        """Auto-resize input text area"""
        self.input_text.update_idletasks()
        lines = int(self.input_text.index('end-1c').split('.')[0])
        if lines <= 3:
            self.input_text.config(height=3)
        elif lines <= 6:
            self.input_text.config(height=lines)
        else:
            self.input_text.config(height=6)
    
    def add_message(self, message: str, msg_type: str = "assistant"):
        """Add a message to the chat area"""
        self.chat_text.config(state=tk.NORMAL)
        
        if msg_type == "user":
            self.chat_text.insert(tk.END, "You: ", "user")
        elif msg_type == "assistant":
            self.chat_text.insert(tk.END, "Jarvis: ", "assistant")
        elif msg_type == "system":
            self.chat_text.insert(tk.END, "System: ", "system")
        elif msg_type == "error":
            self.chat_text.insert(tk.END, "Error: ", "error")
        
        self.chat_text.insert(tk.END, message + "\n\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def send_message(self):
        """Send a message to the LLM"""
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_message(message, "user")
        
        # Update status
        self.status_label.config(text="Thinking...")
        self.send_btn.config(state=tk.DISABLED)
        
        # Send to LLM in background thread
        if self.llm and self.session:
            threading.Thread(target=self.process_llm_request, args=(message,), daemon=True).start()
        else:
            self.add_message("No model loaded. Please load a model first.", "error")
            self.status_label.config(text="Ready - No model loaded")
            self.send_btn.config(state=tk.NORMAL)
    
    def process_llm_request(self, message: str):
        """Process LLM request in background thread"""
        try:
            if not self.session:
                self.session = ChatSession()
            
            self.session.add_user(message)
            
            # Stream response
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
    
    def process_messages(self):
        """Process messages from background threads"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()
                
                if msg_type == "stream":
                    # Update streaming response
                    if not hasattr(self, 'current_response'):
                        self.current_response = ""
                        self.add_message("", "assistant")
                        self.response_start = self.chat_text.index("end-2c")
                    
                    self.current_response += content
                    self.update_streaming_response()
                
                elif msg_type == "complete":
                    # Complete the response
                    if hasattr(self, 'current_response'):
                        delattr(self, 'current_response')
                    self.status_label.config(text="Ready")
                    self.send_btn.config(state=tk.NORMAL)
                
                elif msg_type == "error":
                    self.add_message(content, "error")
                    self.status_label.config(text="Error occurred")
                    self.send_btn.config(state=tk.NORMAL)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def update_streaming_response(self):
        """Update the streaming response in the chat"""
        if not hasattr(self, 'current_response'):
            return
        
        self.chat_text.config(state=tk.NORMAL)
        # Replace the last message with updated content
        self.chat_text.delete(self.response_start, tk.END)
        self.chat_text.insert(tk.END, "Jarvis: ", "assistant")
        self.chat_text.insert(tk.END, self.current_response + "▌")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def load_model(self, model_path: str):
        """Load a GGUF model"""
        try:
            self.status_label.config(text="Loading model...")
            self.add_message(f"Loading model: {model_path}", "system")
            
            # Load model in background
            threading.Thread(target=self._load_model_background, args=(model_path,), daemon=True).start()
            
        except Exception as e:
            self.add_message(f"Failed to load model: {e}", "error")
            self.status_label.config(text="Ready - No model loaded")
    
    def _load_model_background(self, model_path: str):
        """Load model in background thread"""
        try:
            if LocalLlm is None:
                raise ImportError("llama-cpp-python not available")
            
            self.llm = LocalLlm(model_path=model_path)
            self.session = ChatSession()
            
            self.message_queue.put(("system", f"Model loaded successfully: {Path(model_path).name}"))
            self.message_queue.put(("status", "Ready - Model loaded"))
            self.message_queue.put(("model", Path(model_path).name))
            
        except Exception as e:
            self.message_queue.put(("error", f"Failed to load model: {e}"))
            self.message_queue.put(("status", "Ready - No model loaded"))
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()


def main():
    """Main entry point for the GUI"""
    app = TransparentWindow()
    
    # Add welcome message
    app.add_message("Welcome to Terminal Jarvis Desktop!", "system")
    app.add_message("Load a GGUF model to start chatting. Use the menu to load a model file.", "system")
    
    app.run()


if __name__ == "__main__":
    main()
