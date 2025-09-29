# Terminal Jarvis (Local LLM)

A fully local, personal LLM that runs offline using `llama.cpp` models (`.gguf`).

**Two interfaces available:**
- 🖥️ **Desktop GUI** - Transparent, always-on-top, minimizable desktop app
- 💻 **Terminal CLI** - Command-line interface for terminal users

Works on Windows PowerShell (also macOS/Linux). No cloud required.

## Features

### Desktop GUI
- **Transparent window** with modern dark theme
- **Pip mode** - Always stays on top of other windows
- **Minimizable** - Collapse to taskbar or minimize to system tray
- **Draggable** - Move window by dragging the title bar
- **Model management** - Load, switch, and manage GGUF models
- **Conversation saving** - Export/import chat history
- **Streaming responses** - Real-time token generation
- **Keyboard shortcuts** - Quick access to common functions

### Terminal CLI
- Offline, private, local inference
- Uses `llama.cpp` via `llama-cpp-python`
- Streaming tokens in a simple REPL shell
- Configurable model, context window, GPU layers
- Saves conversation transcripts locally

## Quickstart (Windows PowerShell)

1) Install Python 3.10+ and pip.

2) (Optional for GPU) Install CUDA 12.x if you have an NVIDIA GPU and want acceleration.

3) Create and activate a venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4) Install dependencies:

```powershell
pip install -r requirements.txt
```

5) Download a GGUF model (examples):

- `TheBloke/Llama-2-7B-GGUF` on Hugging Face
- `Qwen/Qwen2-7B-Instruct-GGUF`

Place the `.gguf` file somewhere on disk, e.g. `models\qwen2-7b-instruct.Q4_K_M.gguf`.

6) Run the application:

**Desktop GUI (Recommended):**
```powershell
python launch_desktop.py
# Or double-click: launch_desktop.bat
```

**Terminal CLI:**
```powershell
python -m jarvis --model "C:\\path\\to\\model.gguf" --gpu-layers 20 --ctx 4096
```

## Desktop GUI Usage

### Launching
- **Windows**: Double-click `launch_desktop.bat` or run `python launch_desktop.py`
- **PowerShell**: Run `.\launch_desktop.ps1`

### Interface
- **Title Bar**: Drag to move window, buttons to minimize/toggle pip mode/close
- **Chat Area**: Displays conversation with color-coded messages
- **Input Area**: Type messages and press Ctrl+Enter to send
- **Status Bar**: Shows current model and status

### Controls
- **Minimize** (─): Collapse window to taskbar
- **Pip Mode** (📌): Toggle always-on-top (green = enabled)
- **Close** (×): Exit application

### Menu Options
- **File → Load Model**: Select GGUF model file
- **File → Load Recent Model**: Quick access to recently used models
- **File → Save Conversation**: Export chat as JSONL
- **File → Load Conversation**: Import previous chat
- **Settings → Model Settings**: Configure context, GPU layers, temperature
- **Settings → Window Settings**: Adjust transparency

### Keyboard Shortcuts
- `Ctrl+Enter`: Send message
- `Ctrl+N`: New conversation
- `Ctrl+O`: Load model
- `Ctrl+S`: Save conversation
- `Ctrl+Q`: Quit application

## Terminal CLI Usage

Type messages. Press Enter to send. Use `:help` for commands.

## Commands inside REPL

- `:help` — show help
- `:model <path>` — switch model path
- `:save <path>` — save transcript (JSONL)
- `:exit` — quit

## Configuration

You can set defaults via CLI flags or environment variables:

- `--model` or `JARVIS_MODEL`
- `--ctx` or `JARVIS_CTX`
- `--gpu-layers` or `JARVIS_GPU_LAYERS`
- `--n-gpu-layers` (alias)
- `--threads` or `JARVIS_THREADS`

## Notes

- First load may take time to build the context. Subsequent prompts are faster.
- For best results, use an instruct-tuned model in GGUF format.
- If you encounter AVX/AVX2 issues, ensure your CPU supports required instruction sets or use a compatible wheel.

## License

MIT
