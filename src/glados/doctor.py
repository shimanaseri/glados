"""Pre-flight checks for the local Ollama model and GLaDOS voice."""

from glados.config import MODEL_NAME, OLLAMA_HOST, VOICE_MODEL, VOICE_TOKENS, VOICE_DATA_DIR


def run_checks(require_voice: bool = True) -> list[str]:
    """Return actionable setup errors; an empty list means the TUI can start."""
    errors = []
    try:
        import ollama

        models = ollama.Client(host=OLLAMA_HOST).list().models
        available = {getattr(model, "model", "") for model in models}
        if MODEL_NAME not in available and f"{MODEL_NAME}:latest" not in available:
            errors.append(f"Model {MODEL_NAME!r} is missing. Run: ollama pull {MODEL_NAME}")
    except Exception as exc:
        errors.append(f"Ollama is not reachable at {OLLAMA_HOST}: {exc}")

    if require_voice:
        for path, label in ((VOICE_MODEL, "voice model"), (VOICE_TOKENS, "voice tokens"),
                            (VOICE_DATA_DIR, "voice data")):
            if not path.exists():
                errors.append(f"GLaDOS {label} is missing. Run: uv run glados-download-voice")
    return errors


def main() -> None:
    errors = run_checks()
    if errors:
        print("GLaDOS: The test chamber is not ready. Correct these deficiencies:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("GLaDOS: All local systems are ready. A rare success.")


if __name__ == "__main__":
    main()
