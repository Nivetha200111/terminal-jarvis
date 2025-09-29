from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel

from .config import AppConfig
from .chat import LocalLlm, ChatSession


console = Console()


@click.command()
@click.option("--model", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to GGUF model file")
@click.option("--ctx", "context_length", type=int, default=4096, show_default=True, help="Context window tokens")
@click.option("--gpu-layers", "gpu_layers", type=int, default=0, show_default=True, help="Number of layers offloaded to GPU")
@click.option("--n-gpu-layers", "gpu_layers_alias", type=int, default=None, help="Alias for --gpu-layers")
@click.option("--threads", type=int, default=None, help="CPU threads to use")
@click.option("--save", "save_path", type=click.Path(dir_okay=False, path_type=Path), default=None, help="Path to save transcript JSONL")
@click.option("--temperature", type=float, default=0.7, show_default=True, help="Sampling temperature")
@click.option("--max-tokens", type=int, default=1024, show_default=True, help="Max new tokens per response")
def main(
	model: Optional[Path],
	context_length: int,
	gpu_layers: int,
	gpu_layers_alias: Optional[int],
	threads: Optional[int],
	save_path: Optional[Path],
	temperature: float,
	max_tokens: int,
):
	gpu_layers = gpu_layers_alias if gpu_layers_alias is not None else gpu_layers

	cfg = AppConfig.from_env(
		default_model=str(model) if model else None,
		default_ctx=context_length,
		default_gpu_layers=gpu_layers,
		default_threads=threads,
	)

	session = ChatSession(console=console)
	session.render_system_banner(cfg.model_path)

	if not cfg.model_path:
		console.print(Panel("No model specified. Use --model or set JARVIS_MODEL.", border_style="red"))
		raise SystemExit(2)

	# Load model
	try:
		llm = LocalLlm(
			model_path=cfg.model_path,
			context_length=cfg.context_length,
			gpu_layers=cfg.gpu_layers,
			threads=cfg.threads,
		)
	except Exception as exc:
		console.print(Panel(f"Failed to load model: {exc}", border_style="red"))
		raise SystemExit(1)

	prompt = PromptSession("You> ", history=InMemoryHistory())

	def handle_command(line: str) -> bool:
		parts = line.strip().split()
		cmd = parts[0].lower()
		if cmd == ":help":
			console.print(
				Panel(
					"\n".join(
						[
							":help — show this help",
							":model <path> — switch model (reload)",
							":save <path> — save transcript JSONL",
							":exit — quit",
						]
					),
					border_style="cyan",
				)
			)
			return True
		if cmd == ":exit":
			return False
		if cmd == ":save":
			path = parts[1] if len(parts) > 1 else (str(save_path) if save_path else "transcript.jsonl")
			p = session.save(path)
			console.print(Panel(f"Saved to {p}", border_style="green"))
			return True
		if cmd == ":model":
			new_path = parts[1] if len(parts) > 1 else None
			if not new_path:
				console.print(Panel("Usage: :model <path>", border_style="yellow"))
				return True
			try:
				new_llm = LocalLlm(
					model_path=new_path,
					context_length=cfg.context_length,
					gpu_layers=cfg.gpu_layers,
					threads=cfg.threads,
				)
			except Exception as exc:
				console.print(Panel(f"Failed to load model: {exc}", border_style="red"))
				return True
			console.print(Panel(f"Switched model to {new_path}", border_style="green"))
			nonlocal llm
			llm = new_llm
			return True
		return True

	while True:
		try:
			line = prompt.prompt()
		except (EOFError, KeyboardInterrupt):
			console.print()
			break

		line = line.strip()
		if not line:
			continue

		if line.startswith(":"):
			keep = handle_command(line)
			if not keep:
				break
			continue

		session.add_user(line)
		console.print("Assistant> ", end="")
		generated = []
		for piece in llm.stream_chat(session.messages, max_tokens=max_tokens, temperature=temperature):
			generated.append(piece)
			console.print(piece, end="", soft_wrap=True)
		console.print()
		assistant_text = "".join(generated)
		session.add_assistant(assistant_text)

	if save_path:
		p = session.save(str(save_path))
		console.print(Panel(f"Saved to {p}", border_style="green"))


if __name__ == "__main__":
	main()
