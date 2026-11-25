"""Runtime configuration, with environment-variable overrides."""

from pathlib import Path
import ipaddress
import os
from urllib.parse import urlsplit


def validate_local_ollama_host(host: str) -> str:
    """Accept only loopback Ollama endpoints; refuse remote LLM servers."""
    parsed = urlsplit(host)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("OLLAMA_HOST must be an HTTP(S) URL on localhost or a loopback IP.")
    if parsed.username or parsed.password:
        raise ValueError("OLLAMA_HOST must not contain credentials or API tokens.")
    hostname = parsed.hostname.lower()
    is_loopback = hostname in ("localhost", "localhost.localdomain")
    if not is_loopback:
        try:
            is_loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            is_loopback = False
    if not is_loopback:
        raise ValueError("Remote Ollama hosts are disabled; use localhost or a loopback IP address.")
    return host


MODEL_NAME = os.getenv("GLADOS_MODEL", "volvi/GLaDOS3.4_3B")
OLLAMA_HOST = validate_local_ollama_host(os.getenv("OLLAMA_HOST", "http://localhost:11434"))
# Keep proxy environment settings from rerouting loopback model requests off-device.
for _proxy_bypass_var in ("NO_PROXY", "no_proxy"):
    _existing_bypasses = [item.strip() for item in os.getenv(_proxy_bypass_var, "").split(",") if item.strip()]
    os.environ[_proxy_bypass_var] = ",".join(dict.fromkeys(_existing_bypasses + ["localhost", "127.0.0.1", "::1"]))
HISTORY_LIMIT = int(os.getenv("GLADOS_HISTORY_LIMIT", "10"))
OLLAMA_TEMPERATURE = float(os.getenv("GLADOS_TEMPERATURE", "0.7"))
OLLAMA_NUM_PREDICT = int(os.getenv("GLADOS_NUM_PREDICT", "96"))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VOICE_DIR = Path(os.getenv("GLADOS_VOICE_DIR", PROJECT_ROOT / "models" / "vits-piper-en_US-glados"))
VOICE_MODEL = VOICE_DIR / "en_US-glados.onnx"
VOICE_TOKENS = VOICE_DIR / "tokens.txt"
VOICE_DATA_DIR = VOICE_DIR / "espeak-ng-data"
FALLBACK_VOICE_MODEL = PROJECT_ROOT / "models" / "rokeya71-glados" / "glados.onnx"
VOICE_THREADS = int(os.getenv("GLADOS_TTS_THREADS", "2"))
MEMORY_FILE = Path(os.getenv("GLADOS_MEMORY_FILE", PROJECT_ROOT / "memory.md"))
