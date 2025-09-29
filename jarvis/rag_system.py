"""
RAG (Retrieval-Augmented Generation) System for Terminal Jarvis
Handles document ingestion, vector storage, and semantic search
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
import markdown
import psutil
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process various document types and extract text"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_html(file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Error extracting HTML {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_markdown(file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                html = markdown.markdown(md_content)
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()
        except Exception as e:
            logger.error(f"Error extracting Markdown {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting TXT {file_path}: {e}")
            return ""
    
    @classmethod
    def process_file(cls, file_path: str) -> Dict[str, Any]:
        """Process any supported file type and extract text"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": "File not found"}
        
        # Get file info
        file_info = {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "extension": file_path.suffix.lower()
        }
        
        # Extract text based on file type
        text = ""
        if file_path.suffix.lower() == '.pdf':
            text = cls.extract_text_from_pdf(str(file_path))
        elif file_path.suffix.lower() == '.docx':
            text = cls.extract_text_from_docx(str(file_path))
        elif file_path.suffix.lower() in ['.html', '.htm']:
            text = cls.extract_text_from_html(str(file_path))
        elif file_path.suffix.lower() in ['.md', '.markdown']:
            text = cls.extract_text_from_markdown(str(file_path))
        elif file_path.suffix.lower() in ['.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml']:
            text = cls.extract_text_from_txt(str(file_path))
        else:
            return {"error": f"Unsupported file type: {file_path.suffix}"}
        
        if not text.strip():
            return {"error": "No text content found"}
        
        file_info["text"] = text
        file_info["word_count"] = len(text.split())
        file_info["char_count"] = len(text)
        
        return file_info


class TextChunker:
    """Split documents into chunks for better retrieval"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": len(chunks),
                    "chunk_size": len(chunk_words),
                    "start_word": i,
                    "end_word": min(i + self.chunk_size, len(words))
                })
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })
        
        return chunks


class RAGSystem:
    """Main RAG system with vector database and semantic search"""
    
    def __init__(self, db_path: str = "./jarvis_rag_db"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize document processor and chunker
        self.doc_processor = DocumentProcessor()
        self.chunker = TextChunker()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="jarvis_knowledge_base",
            metadata={"description": "Terminal Jarvis Knowledge Base"}
        )
        
        logger.info(f"RAG System initialized with {self.collection.count()} documents")
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        try:
            # Process the document
            doc_info = self.doc_processor.process_file(file_path)
            
            if "error" in doc_info:
                return {"success": False, "error": doc_info["error"]}
            
            # Generate document ID
            doc_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Check if document already exists
            existing = self.collection.get(ids=[doc_id])
            if existing["ids"]:
                return {"success": False, "error": "Document already exists in knowledge base"}
            
            # Chunk the text
            chunks = self.chunker.chunk_text(doc_info["text"], doc_info)
            
            # Prepare data for ChromaDB
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=chunk_metadatas
            )
            
            logger.info(f"Added document {file_path} with {len(chunks)} chunks")
            
            return {
                "success": True,
                "document_id": doc_id,
                "chunks_added": len(chunks),
                "metadata": doc_info
            }
            
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def add_text(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add raw text to the knowledge base"""
        try:
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "source": "manual_input",
                "added_at": datetime.now().isoformat(),
                "type": "text"
            })
            
            # Generate ID
            text_id = hashlib.md5(text.encode()).hexdigest()
            
            # Chunk the text
            chunks = self.chunker.chunk_text(text, metadata)
            
            # Prepare data
            chunk_ids = [f"{text_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=chunk_metadatas
            )
            
            logger.info(f"Added text with {len(chunks)} chunks")
            
            return {
                "success": True,
                "text_id": text_id,
                "chunks_added": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error adding text: {e}")
            return {"success": False, "error": str(e)}
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def get_context_for_query(self, query: str, max_chunks: int = 3) -> str:
        """Get relevant context for a query to use in RAG"""
        results = self.search(query, n_results=max_chunks)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            context_parts.append(f"Source: {result['metadata'].get('name', 'Unknown')}\n{result['text']}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            count = self.collection.count()
            
            # Get all metadata to analyze
            all_data = self.collection.get()
            sources = set()
            file_types = set()
            
            for metadata in all_data["metadatas"]:
                if "name" in metadata:
                    sources.add(metadata["name"])
                if "extension" in metadata:
                    file_types.add(metadata["extension"])
            
            return {
                "total_chunks": count,
                "unique_sources": len(sources),
                "file_types": list(file_types),
                "sources": list(sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {e}")
            return {"error": str(e)}
    
    def delete_document(self, file_path: str) -> Dict[str, Any]:
        """Delete a document from the knowledge base"""
        try:
            doc_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Find all chunks for this document
            all_data = self.collection.get()
            chunk_ids_to_delete = []
            
            for i, metadata in enumerate(all_data["metadatas"]):
                if metadata.get("path") == file_path:
                    chunk_ids_to_delete.append(all_data["ids"][i])
            
            if chunk_ids_to_delete:
                self.collection.delete(ids=chunk_ids_to_delete)
                logger.info(f"Deleted document {file_path} with {len(chunk_ids_to_delete)} chunks")
                return {"success": True, "chunks_deleted": len(chunk_ids_to_delete)}
            else:
                return {"success": False, "error": "Document not found in knowledge base"}
                
        except Exception as e:
            logger.error(f"Error deleting document {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear the entire knowledge base"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("jarvis_knowledge_base")
            self.collection = self.client.create_collection(
                name="jarvis_knowledge_base",
                metadata={"description": "Terminal Jarvis Knowledge Base"}
            )
            
            logger.info("Knowledge base cleared")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {e}")
            return {"success": False, "error": str(e)}
