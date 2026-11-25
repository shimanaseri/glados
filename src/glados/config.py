"""Runtime configuration, with environment-variable overrides."""

from pathlib import Path
import os


MODEL_NAME = os.getenv("GLADOS_MODEL", "volvi/GLaDOS3.4_3B")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
HISTORY_LIMIT = int(os.getenv("GLADOS_HISTORY_LIMIT", "10"))
OLLAMA_TEMPERATURE = float(os.getenv("GLADOS_TEMPERATURE", "0.7"))
OLLAMA_NUM_PREDICT = int(os.getenv("GLADOS_NUM_PREDICT", "160"))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_DIR = Path(os.getenv("GLADOS_VOICE_DIR", PROJECT_ROOT / "models" / "vits-piper-en_US-glados"))
VOICE_MODEL = VOICE_DIR / "en_US-glados.onnx"
VOICE_TOKENS = VOICE_DIR / "tokens.txt"
VOICE_DATA_DIR = VOICE_DIR / "espeak-ng-data"
FALLBACK_VOICE_MODEL = PROJECT_ROOT / "models" / "rokeya71-glados" / "glados.onnx"
VOICE_THREADS = int(os.getenv("GLADOS_TTS_THREADS", "2"))
MEMORY_FILE = Path(os.getenv("GLADOS_MEMORY_FILE", PROJECT_ROOT / "memory.md"))
