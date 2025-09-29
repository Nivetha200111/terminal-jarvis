"""
Enhanced Chat System with RAG and Task Automation
Combines knowledge retrieval with automated task execution
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .rag_system import RAGSystem
from .task_automation import TaskSolver, TaskExecutor
from .chat import LocalLlm, ChatSession

logger = logging.getLogger(__name__)


class EnhancedChatSession(ChatSession):
    """Enhanced chat session with RAG and task automation capabilities"""
    
    def __init__(self, console=None, rag_system=None, task_solver=None):
        super().__init__(console)
        self.rag_system = rag_system
        self.task_solver = task_solver
        self.knowledge_base_enabled = rag_system is not None
        self.task_automation_enabled = task_solver is not None
        
        # Track conversation context
        self.conversation_context = {
            "current_topic": None,
            "recent_searches": [],
            "completed_tasks": [],
            "user_preferences": {}
        }
    
    def add_user(self, content: str) -> None:
        """Add user message with context analysis"""
        super().add_user(content)
        
        # Analyze message for context
        self._analyze_user_message(content)
    
    def _analyze_user_message(self, content: str) -> None:
        """Analyze user message for context and intent"""
        content_lower = content.lower()
        
        # Update conversation context
        if any(keyword in content_lower for keyword in ["python", "programming", "code"]):
            self.conversation_context["current_topic"] = "programming"
        elif any(keyword in content_lower for keyword in ["system", "computer", "windows"]):
            self.conversation_context["current_topic"] = "system"
        elif any(keyword in content_lower for keyword in ["help", "how", "what", "why"]):
            self.conversation_context["current_topic"] = "help"
    
    def get_enhanced_response(self, llm: LocalLlm, user_message: str) -> str:
        """Get enhanced response using RAG and task automation"""
        try:
            # Check if this is a task request
            if self._is_task_request(user_message):
                return self._handle_task_request(user_message)
            
            # Get relevant context from knowledge base
            context = ""
            if self.knowledge_base_enabled:
                context = self.rag_system.get_context_for_query(user_message, max_chunks=3)
            
            # Prepare enhanced prompt
            enhanced_prompt = self._create_enhanced_prompt(user_message, context)
            
            # Get response from LLM
            response_parts = []
            for piece in llm.stream_chat([{"role": "user", "content": enhanced_prompt}], 
                                       max_tokens=1024, temperature=0.7):
                response_parts.append(piece)
            
            response = "".join(response_parts)
            
            # Post-process response
            response = self._post_process_response(response, user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting enhanced response: {e}")
            return f"I encountered an error while processing your request: {e}"
    
    def _is_task_request(self, message: str) -> bool:
        """Check if the message is requesting a task to be performed"""
        task_keywords = [
            "add to path", "install", "run command", "execute", "setup python",
            "create virtual environment", "install package", "configure",
            "set up", "fix", "solve", "do this", "help me with"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in task_keywords)
    
    def _handle_task_request(self, user_message: str) -> str:
        """Handle task automation requests"""
        if not self.task_automation_enabled:
            return "Task automation is not available. Please enable it first."
        
        try:
            # Solve the task
            result = self.task_solver.solve_task(user_message)
            
            if result.get("success", False):
                # Task completed successfully
                self.conversation_context["completed_tasks"].append({
                    "task": user_message,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                response = f"✅ **Task Completed Successfully!**\n\n"
                response += f"**Action Taken:** {result.get('action_taken', 'Task completed')}\n\n"
                
                if result.get('message'):
                    response += f"**Details:** {result['message']}\n\n"
                
                if result.get('python_path'):
                    response += f"**Python Path:** {result['python_path']}\n"
                if result.get('python_version'):
                    response += f"**Python Version:** {result['python_version']}\n"
                
                return response
            else:
                # Task failed
                error_msg = result.get('error', 'Unknown error')
                suggestions = result.get('suggestions', [])
                
                response = f"❌ **Task Failed**\n\n"
                response += f"**Error:** {error_msg}\n\n"
                
                if suggestions:
                    response += "**Suggestions:**\n"
                    for suggestion in suggestions:
                        response += f"• {suggestion}\n"
                
                return response
                
        except Exception as e:
            logger.error(f"Error handling task request: {e}")
            return f"❌ **Error processing task:** {e}"
    
    def _create_enhanced_prompt(self, user_message: str, context: str) -> str:
        """Create enhanced prompt with context and instructions"""
        prompt_parts = []
        
        # System instructions
        prompt_parts.append("You are Terminal Jarvis, an AI assistant with access to a knowledge base and task automation capabilities.")
        prompt_parts.append("You can help with programming, system administration, and general questions.")
        
        # Add context if available
        if context:
            prompt_parts.append(f"\n**Relevant Information from Knowledge Base:**\n{context}")
        
        # Add conversation context
        if self.conversation_context["current_topic"]:
            prompt_parts.append(f"\n**Current Topic:** {self.conversation_context['current_topic']}")
        
        # Add user message
        prompt_parts.append(f"\n**User Question:** {user_message}")
        
        # Instructions for response
        prompt_parts.append("\n**Instructions:**")
        prompt_parts.append("- Provide helpful, accurate information")
        prompt_parts.append("- If you can perform a task automatically, mention it")
        prompt_parts.append("- Use the knowledge base information to enhance your response")
        prompt_parts.append("- Be concise but thorough")
        
        return "\n".join(prompt_parts)
    
    def _post_process_response(self, response: str, user_message: str) -> str:
        """Post-process the LLM response"""
        # Add knowledge base attribution if context was used
        if self.knowledge_base_enabled and "knowledge base" in response.lower():
            response += "\n\n*This response was enhanced with information from the knowledge base.*"
        
        # Add task automation hints
        if self.task_automation_enabled and self._is_task_request(user_message):
            response += "\n\n*I can help automate tasks like adding to PATH, installing packages, or running commands. Just ask!*"
        
        return response
    
    def search_knowledge_base(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        if not self.knowledge_base_enabled:
            return []
        
        try:
            results = self.rag_system.search(query, n_results=n_results)
            self.conversation_context["recent_searches"].append({
                "query": query,
                "results_count": len(results),
                "timestamp": datetime.now().isoformat()
            })
            return results
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def add_document_to_knowledge_base(self, file_path: str) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        if not self.knowledge_base_enabled:
            return {"success": False, "error": "Knowledge base not enabled"}
        
        try:
            result = self.rag_system.add_document(file_path)
            return result
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {"success": False, "error": str(e)}
    
    def add_text_to_knowledge_base(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add text to the knowledge base"""
        if not self.knowledge_base_enabled:
            return {"success": False, "error": "Knowledge base not enabled"}
        
        try:
            result = self.rag_system.add_text(text, metadata)
            return result
        except Exception as e:
            logger.error(f"Error adding text: {e}")
            return {"success": False, "error": str(e)}
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        if not self.knowledge_base_enabled:
            return {"error": "Knowledge base not enabled"}
        
        try:
            return self.rag_system.get_knowledge_base_stats()
        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {e}")
            return {"error": str(e)}
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        return {
            "message_count": len(self.messages),
            "current_topic": self.conversation_context["current_topic"],
            "recent_searches": len(self.conversation_context["recent_searches"]),
            "completed_tasks": len(self.conversation_context["completed_tasks"]),
            "knowledge_base_enabled": self.knowledge_base_enabled,
            "task_automation_enabled": self.task_automation_enabled
        }


class EnhancedLocalLlm(LocalLlm):
    """Enhanced LLM with RAG and task automation integration"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rag_system = None
        self.task_solver = None
    
    def enable_rag(self, rag_system: RAGSystem):
        """Enable RAG capabilities"""
        self.rag_system = rag_system
    
    def enable_task_automation(self, task_solver: TaskSolver):
        """Enable task automation capabilities"""
        self.task_solver = task_solver
    
    def stream_enhanced_chat(self, session: EnhancedChatSession, 
                           max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """Stream enhanced chat with RAG and task automation"""
        if not session.messages:
            return ""
        
        user_message = session.messages[-1]["content"]
        
        # Get enhanced response
        response = session.get_enhanced_response(self, user_message)
        
        # Add to session
        session.add_assistant(response)
        
        return response
