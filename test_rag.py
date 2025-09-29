#!/usr/bin/env python3
"""
Test script for RAG system functionality
"""

import sys
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_rag_system():
    """Test the RAG system components"""
    print("Testing RAG System Components...")
    
    try:
        from jarvis.rag_system import RAGSystem, DocumentProcessor
        print("[OK] RAG System imports successful")
        
        # Test document processor
        processor = DocumentProcessor()
        print("[OK] Document Processor created")
        
        # Test RAG system initialization
        rag = RAGSystem(db_path="./test_rag_db")
        print("[OK] RAG System initialized")
        
        # Test adding some sample text
        sample_text = """
        Python is a high-level programming language known for its simplicity and readability.
        It's widely used in web development, data science, artificial intelligence, and automation.
        Python has a large standard library and an active community.
        """
        
        result = rag.add_text(sample_text, {"source": "test", "type": "sample"})
        if result.get("success"):
            print("[OK] Sample text added to knowledge base")
        else:
            print(f"[ERROR] Failed to add text: {result.get('error')}")
            return False
        
        # Test search functionality
        search_results = rag.search("Python programming language", n_results=3)
        if search_results:
            print("[OK] Search functionality working")
            print(f"Found {len(search_results)} results")
        else:
            print("[ERROR] Search failed")
            return False
        
        # Test knowledge base stats
        stats = rag.get_knowledge_base_stats()
        print(f"[OK] Knowledge base stats: {stats}")
        
        print("\n[SUCCESS] RAG System test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] RAG System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_automation():
    """Test task automation components"""
    print("\nTesting Task Automation Components...")
    
    try:
        from jarvis.task_automation import TaskExecutor, SystemInfo
        print("[OK] Task Automation imports successful")
        
        # Test system info
        system_info = SystemInfo()
        os_info = system_info.get_os_info()
        print(f"[OK] System info: {os_info['system']} {os_info['release']}")
        
        # Test task executor
        executor = TaskExecutor()
        print("[OK] Task Executor created")
        
        # Test system status
        status = executor.get_system_status()
        if "cpu_percent" in status:
            print("[OK] System status retrieval working")
        else:
            print("[ERROR] System status failed")
            return False
        
        print("[SUCCESS] Task Automation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Task Automation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_chat():
    """Test enhanced chat system"""
    print("\nTesting Enhanced Chat System...")
    
    try:
        from jarvis.enhanced_chat import EnhancedChatSession
        from jarvis.rag_system import RAGSystem
        from jarvis.task_automation import TaskExecutor, TaskSolver
        print("[OK] Enhanced Chat imports successful")
        
        # Create components
        rag = RAGSystem(db_path="./test_rag_db")
        executor = TaskExecutor()
        solver = TaskSolver(rag, executor)
        
        # Create enhanced session
        session = EnhancedChatSession(rag_system=rag, task_solver=solver)
        print("[OK] Enhanced Chat Session created")
        
        # Test conversation summary
        summary = session.get_conversation_summary()
        print(f"[OK] Conversation summary: {summary}")
        
        print("[SUCCESS] Enhanced Chat test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Enhanced Chat test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Terminal Jarvis RAG System Test Suite")
    print("=" * 60)
    
    tests = [
        test_rag_system,
        test_task_automation,
        test_enhanced_chat
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 40)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! RAG system is ready to use.")
        return True
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
