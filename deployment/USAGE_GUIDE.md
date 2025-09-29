# Terminal Jarvis - Complete Usage Guide

## 🚀 **What is Terminal Jarvis?**

Terminal Jarvis is a **fully local, AI-powered personal assistant** that combines:
- **RAG (Retrieval-Augmented Generation)** - Learn from your documents
- **Task Automation** - Automatically perform system tasks
- **Transparent Desktop GUI** - Always-on-top, minimizable interface
- **Local LLM** - Complete privacy with GGUF models

## 🎯 **Key Features**

### 📚 **Knowledge Base (RAG)**
- Upload PDFs, Word docs, text files, code files
- Semantic search through your documents
- AI learns from your data to give better answers
- Supports: PDF, DOCX, TXT, MD, HTML, PY, JS, JSON, YAML

### 🤖 **Task Automation**
- **Add Python to PATH** - "Add Python to my PATH"
- **Install packages** - "Install numpy package"
- **Run commands** - "Run dir command"
- **System management** - "Show system status"
- **Environment setup** - "Create virtual environment"

### 🖥️ **Desktop Interface**
- **Transparent window** - See through to other apps
- **Pip mode** - Always stays on top
- **Minimizable** - Collapse when not needed
- **Draggable** - Move anywhere on screen
- **Modern dark theme** - Easy on the eyes

## 🚀 **Quick Start**

### 1. **Setup (One-time)**
```powershell
# Run the quickstart script
powershell -ExecutionPolicy Bypass -File quickstart.ps1

# Or manually:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. **Launch the App**
```powershell
# Desktop GUI (Recommended)
python launch_desktop.py

# Or double-click
launch_desktop.bat

# Terminal CLI
python -m jarvis --model "path/to/model.gguf"

# Demo mode (no model needed)
python demo.py
```

### 3. **Get a Model**
Download a GGUF model from Hugging Face:
- [TheBloke/Llama-2-7B-GGUF](https://huggingface.co/TheBloke/Llama-2-7B-GGUF)
- [Qwen/Qwen2-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2-7B-Instruct-GGUF)
- [microsoft/Phi-3-mini-4k-instruct-gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)

## 📖 **How to Use**

### **Desktop GUI Interface**

#### **Main Window**
- **Title Bar**: Drag to move, buttons to minimize/toggle pip mode/close
- **Chat Area**: Your conversation with Jarvis
- **Input Area**: Type messages and press Ctrl+Enter to send
- **Status Bar**: Shows current model and status

#### **Menu Options**
- **File → Load Model**: Select GGUF model file
- **File → Load Recent Model**: Quick access to recent models
- **File → Save Conversation**: Export chat as JSONL
- **File → Load Conversation**: Import previous chat
- **Knowledge Base → Manage Knowledge Base**: Full document management
- **Knowledge Base → Add Document**: Quick document upload
- **Knowledge Base → Search Knowledge Base**: Search your data
- **Settings → Model Settings**: Configure context, GPU layers, temperature
- **Settings → Window Settings**: Adjust transparency

#### **Keyboard Shortcuts**
- `Ctrl+Enter`: Send message
- `Ctrl+N`: New conversation
- `Ctrl+O`: Load model
- `Ctrl+S`: Save conversation
- `Ctrl+Q`: Quit application

### **Knowledge Base Management**

#### **Adding Documents**
1. Go to **Knowledge Base → Manage Knowledge Base**
2. Click **Browse** and select your document
3. Click **Add Document**
4. Or drag and drop files directly

#### **Supported File Types**
- **PDF**: `.pdf`
- **Word**: `.docx`
- **Text**: `.txt`, `.py`, `.js`, `.html`, `.css`, `.json`, `.yaml`, `.yml`
- **Markdown**: `.md`, `.markdown`
- **HTML**: `.html`, `.htm`

#### **Searching Your Data**
1. Go to **Knowledge Base → Search Knowledge Base**
2. Enter your search query
3. View results with relevance scores
4. Or ask Jarvis directly: "What does my document say about Python?"

### **Task Automation Examples**

#### **System Setup**
```
"Add Python to my PATH"
"Install numpy package"
"Create a virtual environment in my project folder"
"Show me my system status"
```

#### **File Management**
```
"Run dir command to list files"
"Show me what's in my Documents folder"
"Check disk space usage"
```

#### **Development Tasks**
```
"Install pandas and matplotlib"
"Set up a Python project structure"
"Check if Python is working correctly"
```

### **Conversation Examples**

#### **Document Questions**
```
User: "What does my manual say about installation?"
Jarvis: [Searches knowledge base] "According to your manual, the installation process involves..."

User: "Summarize the key points from my research paper"
Jarvis: [Finds relevant sections] "Based on your research paper, the main findings are..."
```

#### **Task Requests**
```
User: "Add Python to my PATH"
Jarvis: ✅ Task Completed Successfully!
       Action Taken: Added C:\Python311 to system PATH
       Python Path: C:\Python311\python.exe
       Python Version: Python 3.11.0

User: "Install the requests package"
Jarvis: ✅ Task Completed Successfully!
       Action Taken: Installed Python package: requests
```

#### **General Questions**
```
User: "How do I create a virtual environment?"
Jarvis: "To create a virtual environment, you can use the 'venv' module..."

User: "What's the difference between lists and tuples in Python?"
Jarvis: "Lists and tuples are both sequence types in Python, but they differ in..."
```

## 🔧 **Advanced Configuration**

### **Model Settings**
- **Context Length**: How much conversation history to remember
- **GPU Layers**: How many layers to run on GPU (if available)
- **Temperature**: Response creativity (0.0 = focused, 1.0 = creative)
- **Max Tokens**: Maximum response length

### **Window Settings**
- **Transparency**: Adjust window opacity (0.5 = 50%, 1.0 = 100%)
- **Pip Mode**: Toggle always-on-top behavior
- **Minimize**: Collapse to taskbar

### **Knowledge Base Settings**
- **Chunk Size**: How documents are split for search
- **Overlap**: Overlap between chunks for better context
- **Embedding Model**: Sentence transformer model for search

## 🐛 **Troubleshooting**

### **Common Issues**

#### **"No model loaded"**
- Download a GGUF model from Hugging Face
- Use **File → Load Model** to select it
- Or set `JARVIS_MODEL` environment variable

#### **"RAG system not initialized"**
- Check that all dependencies are installed
- Run `python test_rag.py` to test the system
- Restart the application

#### **"Task automation failed"**
- Check that you have the necessary permissions
- Some tasks require administrator privileges
- Try running as administrator

#### **"Document upload failed"**
- Check file format is supported
- Ensure file is not corrupted
- Try with a smaller file first

### **Performance Tips**

#### **For Better Speed**
- Use smaller models (7B parameters or less)
- Reduce context length if memory is limited
- Use GPU acceleration if available

#### **For Better Quality**
- Use larger models (13B+ parameters)
- Increase context length
- Add more documents to knowledge base

## 📁 **File Structure**

```
terminal-jarvis/
├── jarvis/                    # Main package
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── desktop_app.py        # Desktop GUI
│   ├── gui.py               # Base GUI components
│   ├── chat.py              # Chat functionality
│   ├── enhanced_chat.py     # RAG-enhanced chat
│   ├── rag_system.py        # RAG and vector database
│   ├── task_automation.py   # Task execution
│   ├── knowledge_manager.py # Knowledge base GUI
│   └── config.py            # Configuration
├── models/                   # Place GGUF models here
├── data/                    # Knowledge base data
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
├── launch_desktop.py       # Desktop launcher
├── launch_desktop.bat      # Windows batch launcher
├── launch_desktop.ps1      # PowerShell launcher
├── demo.py                 # Demo chooser
├── test_rag.py            # RAG system tests
├── quickstart.ps1         # Setup script
├── deploy.bat             # Deployment script
└── README.md              # This file
```

## 🎉 **Success!**

You now have a fully functional, local AI assistant that can:
- ✅ Learn from your documents
- ✅ Automate system tasks
- ✅ Run completely offline
- ✅ Keep your data private
- ✅ Stay always available (pip mode)
- ✅ Work with any GGUF model

**Happy chatting with Jarvis!** 🤖✨
