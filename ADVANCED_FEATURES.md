# 🚀 Advanced Terminal Jarvis Features

## llama.cpp Integration

Terminal Jarvis now supports **native llama.cpp integration** for optimal performance and compatibility with GGUF models.

### 🎯 **Key Advantages**

- **🚀 Better Performance**: Native llama.cpp is faster than Python bindings
- **🔧 Full Control**: Access to all llama.cpp features and optimizations
- **📦 Easy Model Management**: Direct Hugging Face integration
- **⚡ GPU Acceleration**: Full CUDA/OpenCL support
- **🔄 Streaming**: Real-time response streaming
- **🌐 Server Mode**: REST API compatibility

## 🛠️ **Installation**

### **Option 1: Auto-Install (Recommended)**
```bash
python install_llama_cpp.py
```

### **Option 2: Manual Installation**

#### **Windows (winget)**
```bash
winget install llama.cpp
```

#### **Mac/Linux (brew)**
```bash
brew install llama.cpp
```

#### **Build from Source**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release
```

## 🚀 **Usage**

### **Launch Advanced Version**
```bash
python launch_advanced.py
```

### **Features Available**

#### **1. Hugging Face Model Integration**
- **Load models directly from Hugging Face**
- **Automatic downloading and caching**
- **No manual model management needed**

#### **2. Recommended Models**
- **Llama 3.2 3B Instruct** - Fast, efficient
- **Llama 3.2 1B Instruct** - Ultra-fast
- **Qwen2 7B Instruct** - High-quality
- **Phi-3 Mini 4K** - Microsoft's efficient model
- **CodeLlama 7B** - Specialized for coding

#### **3. Advanced Settings**
- **GPU Layers**: Configure CUDA/OpenCL acceleration
- **Context Size**: Adjust memory usage
- **Server Port**: Customize API endpoint
- **Threading**: Optimize CPU usage

## 🎯 **Model Management**

### **Load Hugging Face Model**
1. Go to **File → Load Hugging Face Model**
2. Select from recommended models
3. Or enter custom repository details
4. Model downloads automatically

### **Custom Model Configuration**
```python
# Example: Load custom model
repo = "microsoft/Phi-3-mini-4k-instruct-gguf"
filename = "Phi-3-mini-4k-instruct-q8.gguf"
```

## 🔧 **Advanced Configuration**

### **Server Settings**
- **Port**: Default 8080 (configurable)
- **Host**: localhost (configurable)
- **GPU Layers**: 0 (CPU) to 99 (full GPU)
- **Context Size**: 4096 (adjustable)

### **Performance Optimization**
```bash
# For GPU acceleration
llama-server -m model.gguf -ngl 35

# For CPU optimization
llama-server -m model.gguf -t 8

# For memory optimization
llama-server -m model.gguf -c 2048
```

## 📊 **Performance Comparison**

| Method | Speed | Memory | GPU Support | Features |
|--------|-------|--------|-------------|----------|
| **llama.cpp** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Python bindings | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

## 🎯 **Use Cases**

### **1. Development & Coding**
- **CodeLlama models** for programming assistance
- **Fast inference** for real-time coding help
- **Context-aware** responses from your codebase

### **2. Document Analysis**
- **Large context windows** for long documents
- **RAG integration** with your knowledge base
- **Semantic search** through your files

### **3. Creative Writing**
- **High-quality models** for creative tasks
- **Streaming responses** for real-time writing
- **Custom prompts** and system messages

## 🔄 **API Integration**

### **REST API Endpoint**
```bash
curl http://localhost:8080/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer no-key" \
-d '{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}'
```

### **Streaming Response**
```python
import requests

response = requests.post(
    "http://localhost:8080/v1/chat/completions",
    json={"messages": [{"role": "user", "content": "Hello!"}], "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8'))
        content = data['choices'][0]['delta'].get('content', '')
        print(content, end='')
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. llama.cpp Not Found**
```bash
# Check installation
llama-server --help

# If not found, reinstall
python install_llama_cpp.py
```

#### **2. Model Download Fails**
```bash
# Check internet connection
# Verify Hugging Face access
# Check disk space
```

#### **3. GPU Not Working**
```bash
# Check CUDA installation
nvidia-smi

# Verify GPU layers setting
# Try with -ngl 0 (CPU only)
```

#### **4. Memory Issues**
```bash
# Reduce context size
# Use smaller model
# Close other applications
```

## 📈 **Performance Tips**

### **1. Model Selection**
- **1B-3B models**: Fast, good for simple tasks
- **7B models**: Balanced performance/quality
- **13B+ models**: High quality, slower

### **2. Hardware Optimization**
- **GPU**: Use CUDA for 7B+ models
- **CPU**: Use 8+ cores for best performance
- **RAM**: 16GB+ recommended for 7B models

### **3. Settings Tuning**
- **Context Size**: Match your use case
- **GPU Layers**: Balance speed/memory
- **Threads**: Match CPU cores

## 🎉 **Getting Started**

1. **Install llama.cpp**:
   ```bash
   python install_llama_cpp.py
   ```

2. **Launch advanced version**:
   ```bash
   python launch_advanced.py
   ```

3. **Load a model**:
   - File → Load Hugging Face Model
   - Select recommended model
   - Wait for download

4. **Start chatting**:
   - Type your message
   - Enjoy fast, high-quality responses!

## 🔗 **Links**

- **llama.cpp GitHub**: https://github.com/ggerganov/llama.cpp
- **Hugging Face Models**: https://huggingface.co/models?library=gguf
- **Terminal Jarvis**: https://github.com/Nivetha200111/terminal-jarvis

---

**Ready to experience the most advanced local AI assistant?** 🚀✨
