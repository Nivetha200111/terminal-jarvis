"""
Knowledge Base Management Interface
Provides GUI components for managing the RAG knowledge base
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import threading
from datetime import datetime

from .rag_system import RAGSystem
from .task_automation import TaskExecutor, TaskSolver


class KnowledgeBaseManager:
    """GUI manager for the knowledge base"""
    
    def __init__(self, parent_window, rag_system: RAGSystem, task_solver: TaskSolver = None):
        self.parent = parent_window
        self.rag_system = rag_system
        self.task_solver = task_solver
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the knowledge base management UI"""
        # Create main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(self.main_frame, text="Knowledge Base Manager", 
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#1e1e1e')
        title_label.pack(pady=(0, 20))
        
        # Stats frame
        self.create_stats_frame()
        
        # Add documents frame
        self.create_add_documents_frame()
        
        # Search frame
        self.create_search_frame()
        
        # Documents list frame
        self.create_documents_list_frame()
        
        # Refresh stats
        self.refresh_stats()
    
    def create_stats_frame(self):
        """Create statistics display frame"""
        stats_frame = ttk.LabelFrame(self.main_frame, text="Knowledge Base Statistics", 
                                   style='Main.TFrame')
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=4, bg='#2d2d2d', fg='white',
                                font=('Consolas', 9), state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)
    
    def create_add_documents_frame(self):
        """Create document addition frame"""
        add_frame = ttk.LabelFrame(self.main_frame, text="Add Documents", 
                                 style='Main.TFrame')
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(add_frame, style='Main.TFrame')
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, 
                            bg='#2d2d2d', fg='white', font=('Consolas', 10))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = tk.Button(file_frame, text="Browse", command=self.browse_file,
                             bg='#4CAF50', fg='white', font=('Segoe UI', 10))
        browse_btn.pack(side=tk.RIGHT)
        
        # Add button
        add_btn = tk.Button(add_frame, text="Add Document", command=self.add_document,
                          bg='#2196F3', fg='white', font=('Segoe UI', 10, 'bold'))
        add_btn.pack(pady=5)
        
        # Add text frame
        text_frame = ttk.LabelFrame(add_frame, text="Add Text", style='Main.TFrame')
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.text_input = scrolledtext.ScrolledText(text_frame, height=4, 
                                                  bg='#2d2d2d', fg='white',
                                                  font=('Consolas', 10))
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        
        add_text_btn = tk.Button(text_frame, text="Add Text", command=self.add_text,
                               bg='#FF9800', fg='white', font=('Segoe UI', 10))
        add_text_btn.pack(pady=5)
    
    def create_search_frame(self):
        """Create search frame"""
        search_frame = ttk.LabelFrame(self.main_frame, text="Search Knowledge Base", 
                                    style='Main.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search input
        search_input_frame = ttk.Frame(search_frame, style='Main.TFrame')
        search_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_input_frame, textvariable=self.search_var,
                              bg='#2d2d2d', fg='white', font=('Consolas', 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.search_knowledge_base())
        
        search_btn = tk.Button(search_input_frame, text="Search", 
                             command=self.search_knowledge_base,
                             bg='#9C27B0', fg='white', font=('Segoe UI', 10))
        search_btn.pack(side=tk.RIGHT)
        
        # Search results
        self.search_results = scrolledtext.ScrolledText(search_frame, height=6,
                                                      bg='#2d2d2d', fg='white',
                                                      font=('Consolas', 9), state=tk.DISABLED)
        self.search_results.pack(fill=tk.X, padx=5, pady=5)
    
    def create_documents_list_frame(self):
        """Create documents list frame"""
        docs_frame = ttk.LabelFrame(self.main_frame, text="Documents in Knowledge Base", 
                                  style='Main.TFrame')
        docs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(docs_frame, style='Main.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.documents_listbox = tk.Listbox(list_frame, bg='#2d2d2d', fg='white',
                                          font=('Consolas', 9), selectbackground='#404040')
        self.documents_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                               command=self.documents_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.documents_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(docs_frame, style='Main.TFrame')
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = tk.Button(button_frame, text="Refresh", command=self.refresh_documents,
                              bg='#607D8B', fg='white', font=('Segoe UI', 10))
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = tk.Button(button_frame, text="Delete Selected", 
                             command=self.delete_selected_document,
                             bg='#F44336', fg='white', font=('Segoe UI', 10))
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = tk.Button(button_frame, text="Clear All", command=self.clear_knowledge_base,
                            bg='#E91E63', fg='white', font=('Segoe UI', 10))
        clear_btn.pack(side=tk.RIGHT)
    
    def browse_file(self):
        """Browse for file to add"""
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
            title="Select Document to Add",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def add_document(self):
        """Add selected document to knowledge base"""
        file_path = self.file_path_var.get().strip()
        
        if not file_path:
            messagebox.showwarning("No File", "Please select a file to add.")
            return
        
        if not Path(file_path).exists():
            messagebox.showerror("File Not Found", f"File not found: {file_path}")
            return
        
        # Add document in background thread
        def add_doc_thread():
            try:
                result = self.rag_system.add_document(file_path)
                
                # Update UI in main thread
                self.parent.after(0, lambda: self._handle_add_document_result(result))
                
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Error adding document: {e}"))
        
        threading.Thread(target=add_doc_thread, daemon=True).start()
        
        # Show progress
        messagebox.showinfo("Adding Document", "Adding document to knowledge base...")
    
    def _handle_add_document_result(self, result: Dict[str, Any]):
        """Handle the result of adding a document"""
        if result.get("success", False):
            messagebox.showinfo("Success", 
                              f"Document added successfully!\n"
                              f"Chunks added: {result.get('chunks_added', 0)}")
            self.file_path_var.set("")
            self.refresh_stats()
            self.refresh_documents()
        else:
            messagebox.showerror("Error", f"Failed to add document: {result.get('error', 'Unknown error')}")
    
    def add_text(self):
        """Add text to knowledge base"""
        text = self.text_input.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("No Text", "Please enter some text to add.")
            return
        
        # Add text in background thread
        def add_text_thread():
            try:
                metadata = {
                    "source": "manual_input",
                    "added_at": datetime.now().isoformat(),
                    "type": "text"
                }
                result = self.rag_system.add_text(text, metadata)
                
                # Update UI in main thread
                self.parent.after(0, lambda: self._handle_add_text_result(result))
                
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Error adding text: {e}"))
        
        threading.Thread(target=add_text_thread, daemon=True).start()
        
        # Show progress
        messagebox.showinfo("Adding Text", "Adding text to knowledge base...")
    
    def _handle_add_text_result(self, result: Dict[str, Any]):
        """Handle the result of adding text"""
        if result.get("success", False):
            messagebox.showinfo("Success", 
                              f"Text added successfully!\n"
                              f"Chunks added: {result.get('chunks_added', 0)}")
            self.text_input.delete("1.0", tk.END)
            self.refresh_stats()
            self.refresh_documents()
        else:
            messagebox.showerror("Error", f"Failed to add text: {result.get('error', 'Unknown error')}")
    
    def search_knowledge_base(self):
        """Search the knowledge base"""
        query = self.search_var.get().strip()
        
        if not query:
            messagebox.showwarning("No Query", "Please enter a search query.")
            return
        
        try:
            results = self.rag_system.search(query, n_results=5)
            
            # Display results
            self.search_results.config(state=tk.NORMAL)
            self.search_results.delete("1.0", tk.END)
            
            if results:
                self.search_results.insert(tk.END, f"Search Results for: '{query}'\n")
                self.search_results.insert(tk.END, "=" * 50 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    self.search_results.insert(tk.END, f"Result {i}:\n")
                    self.search_results.insert(tk.END, f"Source: {result['metadata'].get('name', 'Unknown')}\n")
                    self.search_results.insert(tk.END, f"Relevance: {1 - result['distance']:.2f}\n")
                    self.search_results.insert(tk.END, f"Text: {result['text'][:200]}...\n")
                    self.search_results.insert(tk.END, "-" * 30 + "\n\n")
            else:
                self.search_results.insert(tk.END, f"No results found for: '{query}'\n")
            
            self.search_results.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Error searching knowledge base: {e}")
    
    def refresh_stats(self):
        """Refresh knowledge base statistics"""
        try:
            stats = self.rag_system.get_knowledge_base_stats()
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete("1.0", tk.END)
            
            if "error" in stats:
                self.stats_text.insert(tk.END, f"Error: {stats['error']}\n")
            else:
                self.stats_text.insert(tk.END, f"Total Chunks: {stats.get('total_chunks', 0)}\n")
                self.stats_text.insert(tk.END, f"Unique Sources: {stats.get('unique_sources', 0)}\n")
                self.stats_text.insert(tk.END, f"File Types: {', '.join(stats.get('file_types', []))}\n")
                self.stats_text.insert(tk.END, f"Sources: {', '.join(stats.get('sources', []))}\n")
            
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(tk.END, f"Error loading stats: {e}\n")
            self.stats_text.config(state=tk.DISABLED)
    
    def refresh_documents(self):
        """Refresh documents list"""
        try:
            stats = self.rag_system.get_knowledge_base_stats()
            
            self.documents_listbox.delete(0, tk.END)
            
            if "error" not in stats:
                sources = stats.get('sources', [])
                for source in sources:
                    self.documents_listbox.insert(tk.END, source)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing documents: {e}")
    
    def delete_selected_document(self):
        """Delete selected document from knowledge base"""
        selection = self.documents_listbox.curselection()
        
        if not selection:
            messagebox.showwarning("No Selection", "Please select a document to delete.")
            return
        
        selected_doc = self.documents_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Delete", f"Delete document '{selected_doc}' from knowledge base?"):
            try:
                # Find the full path for the document
                # This is a simplified approach - in practice, you'd need to track paths
                result = self.rag_system.delete_document(selected_doc)
                
                if result.get("success", False):
                    messagebox.showinfo("Success", f"Deleted {result.get('chunks_deleted', 0)} chunks")
                    self.refresh_stats()
                    self.refresh_documents()
                else:
                    messagebox.showerror("Error", f"Failed to delete document: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting document: {e}")
    
    def clear_knowledge_base(self):
        """Clear the entire knowledge base"""
        if messagebox.askyesno("Confirm Clear", "Clear the entire knowledge base? This cannot be undone."):
            try:
                result = self.rag_system.clear_knowledge_base()
                
                if result.get("success", False):
                    messagebox.showinfo("Success", "Knowledge base cleared successfully")
                    self.refresh_stats()
                    self.refresh_documents()
                else:
                    messagebox.showerror("Error", f"Failed to clear knowledge base: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error clearing knowledge base: {e}")


def create_knowledge_base_window(parent, rag_system: RAGSystem, task_solver: TaskSolver = None):
    """Create a new window for knowledge base management"""
    window = tk.Toplevel(parent)
    window.title("Knowledge Base Manager")
    window.geometry("800x600")
    window.configure(bg='#1e1e1e')
    window.attributes('-topmost', True)
    
    # Create knowledge base manager
    kb_manager = KnowledgeBaseManager(window, rag_system, task_solver)
    
    return window
