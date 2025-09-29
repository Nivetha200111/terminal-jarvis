#!/usr/bin/env python3
"""
Demo script to test Terminal Jarvis without requiring a real model.
This creates a mock LLM for testing the CLI interface.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.chat import LocalLlm, ChatSession
from rich.console import Console

class MockLlm:
    """Mock LLM for testing the interface without requiring a real model."""
    
    def __init__(self, *args, **kwargs):
        self.model_path = kwargs.get('model_path', 'mock-model.gguf')
        self.context_length = kwargs.get('context_length', 4096)
        self.gpu_layers = kwargs.get('gpu_layers', 0)
        self.threads = kwargs.get('threads', None)
    
    def stream_chat(self, messages, max_tokens=1024, temperature=0.7):
        """Generate a mock response."""
        last_message = messages[-1]['content'] if messages else "Hello!"
        
        # Simple mock responses based on input
        if "hello" in last_message.lower():
            response = "Hello! I'm Terminal Jarvis, your local LLM assistant. How can I help you today?"
        elif "help" in last_message.lower():
            response = "I can help you with various tasks like:\n- Answering questions\n- Writing code\n- Explaining concepts\n- Creative writing\n\nWhat would you like to know?"
        elif "test" in last_message.lower():
            response = "Great! The test is working. Terminal Jarvis is running locally and ready to assist you."
        else:
            response = f"I understand you said: '{last_message}'\n\nThis is a mock response. In a real setup, you would need a GGUF model file to get actual LLM responses."
        
        # Stream the response word by word
        words = response.split()
        for i, word in enumerate(words):
            if i == 0:
                yield word
            else:
                yield " " + word

def main():
    """Run a demo of Terminal Jarvis with mock LLM."""
    console = Console()
    session = ChatSession(console=console)
    session.render_system_banner("mock-model.gguf (DEMO MODE)")
    
    console.print("\n[bold green]Demo Mode:[/bold green] This is a mock LLM for testing. In real usage, provide a GGUF model with --model")
    
    # Create mock LLM
    llm = MockLlm()
    
    # Simple demo conversation
    demo_messages = [
        "Hello!",
        "Can you help me test this?",
        "What can you do?"
    ]
    
    for message in demo_messages:
        session.add_user(message)
        console.print(f"\n[bold blue]You>[/bold blue] {message}")
        console.print("[bold green]Assistant>[/bold green] ", end="")
        
        generated = []
        for piece in llm.stream_chat(session.messages, max_tokens=100, temperature=0.7):
            generated.append(piece)
            console.print(piece, end="", soft_wrap=True)
        console.print()
        
        assistant_text = "".join(generated)
        session.add_assistant(assistant_text)
    
    console.print(f"\n[bold cyan]Demo completed![/bold cyan] To use with a real model:")
    console.print("1. Download a GGUF model (e.g., from Hugging Face)")
    console.print("2. Run: python -m jarvis --model path/to/model.gguf")
    console.print("3. Or set JARVIS_MODEL environment variable")

if __name__ == "__main__":
    main()
