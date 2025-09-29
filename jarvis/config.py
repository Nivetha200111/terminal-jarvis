import os
from dataclasses import dataclass
from typing import Optional


def _get_int(env_key: str, default: Optional[int]) -> Optional[int]:
	value = os.getenv(env_key)
	if value is None or value == "":
		return default
	try:
		return int(value)
	except ValueError:
		return default


@dataclass
class AppConfig:
	model_path: Optional[str]
	context_length: int
	gpu_layers: int
	threads: Optional[int]

	@staticmethod
	def from_env(
		default_model: Optional[str] = None,
		default_ctx: int = 4096,
		default_gpu_layers: int = 0,
		default_threads: Optional[int] = None,
	) -> "AppConfig":
		return AppConfig(
			model_path=os.getenv("JARVIS_MODEL", default_model),
			context_length=_get_int("JARVIS_CTX", default_ctx) or default_ctx,
			gpu_layers=_get_int("JARVIS_GPU_LAYERS", default_gpu_layers) or default_gpu_layers,
			threads=_get_int("JARVIS_THREADS", default_threads),
		)
