from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional, Dict

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


try:
	from llama_cpp import Llama
except Exception as exc:  # pragma: no cover
	Llama = None  # type: ignore


Message = Dict[str, str]


class LocalLlm:
	def __init__(
		self,
		model_path: str,
		context_length: int = 4096,
		gpu_layers: int = 0,
		threads: Optional[int] = None,
	):
		if Llama is None:
			raise RuntimeError("llama-cpp-python is not installed or failed to import")

		self.model_path = model_path
		self.context_length = context_length
		self.gpu_layers = gpu_layers
		self.threads = threads

		self.llm = Llama(
			model_path=model_path,
			n_ctx=context_length,
			n_gpu_layers=gpu_layers,
			n_threads=threads or None,
			verbose=False,
		)

	def stream_chat(
		self,
		messages: List[Message],
		max_tokens: int = 1024,
		temperature: float = 0.7,
	) -> Iterable[str]:
		stream = self.llm.create_chat_completion(
			messages=messages,
			max_tokens=max_tokens,
			temperature=temperature,
			stream=True,
		)
		for chunk in stream:
			# Handle both OpenAI-compatible and text stream shapes
			try:
				delta = chunk["choices"][0].get("delta") or {}
				piece = delta.get("content")
			except Exception:
				piece = None
			if not piece:
				piece = chunk["choices"][0].get("text")
			if piece:
				yield piece


class ChatSession:
	def __init__(self, console: Optional[Console] = None):
		self.console = console or Console()
		self.messages: List[Message] = []

	def add_user(self, content: str) -> None:
		self.messages.append({"role": "user", "content": content})

	def add_assistant(self, content: str) -> None:
		self.messages.append({"role": "assistant", "content": content})

	def transcript_as_jsonl(self) -> str:
		return "\n".join(json.dumps(m, ensure_ascii=False) for m in self.messages) + "\n"

	def save(self, path: str) -> Path:
		p = Path(path)
		p.parent.mkdir(parents=True, exist_ok=True)
		p.write_text(self.transcript_as_jsonl(), encoding="utf-8")
		return p

	def render_system_banner(self, model_path: Optional[str]) -> None:
		banner = Text()
		banner.append("Terminal Jarvis — Local LLM\n", style="bold cyan")
		if model_path:
			banner.append(f"Model: {model_path}\n", style="magenta")
		banner.append("Type :help for commands. :exit to quit.\n", style="dim")
		self.console.print(Panel(banner, border_style="cyan"))

	def render_assistant(self, text: str) -> None:
		if text.strip().startswith(("#", "- ", "1. ")):
			self.console.print(Markdown(text))
		else:
			self.console.print(text)


def iter_stream_to_text(stream: Iterable[str]) -> str:
	chunks: List[str] = []
	for piece in stream:
		chunks.append(piece)
		yield piece
	return "".join(chunks)
