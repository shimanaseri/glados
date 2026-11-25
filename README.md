# GLaDOS

A small terminal chat assistant using Ollama and an optional sherpa-onnx GLaDOS voice.

All model requests go to a local Ollama server through LangChain's `ChatOllama` integration. `OLLAMA_HOST` is restricted to `localhost` or a loopback IP. LangChain/LangSmith tracing is explicitly disabled, and the project does not configure a paid model provider or API token.

## Run

Install the project with `uv sync`, make sure Ollama is running with the configured model, then run `uv run glados`. The CLI uses voice automatically when the voice files are present; use `uv run glados --text-only` to disable speech.

Download the default voice pack with `uv run glados-download-voice` or `uv run glados --download-voice`. It includes the VITS-Piper model, tokens, and required phonemizer data and is stored in the ignored `models/` directory. Run `uv run glados --tts-demo` to hear a sample and compare synthesis time with its audio duration. After installing the default assets, run `uv run glados-download-voice --fallback` or `uv run glados --download-voice --fallback-voice` to download the alternate model. Start normally with `uv run glados --fallback-voice` to use it.

The retro interface runs with `uv run glados-tui`. Use `uv run glados-tui --text-only` to test it without speech assets. It checks local Ollama and voice setup before opening; `Start GLaDOS.bat` opens the voice TUI in Windows Terminal. Press Esc to interrupt a reply.

## Customize

- Edit `src/glados/persona.py` to change GLaDOS's character prompt.
- Edit the root `memory.md` to add persistent preferences and ongoing context. Memory is read for every request, so edits take effect without restarting.
- Edit `src/glados/config.py` or set its documented environment variables to change the Ollama model, host, history size, generation limits, voice path, or TTS thread count.

Press Ctrl+C during a voice reply to stop playback and discard queued audio. Type `reset` to clear the current chat history or `quit` to exit.

## Tests

Run the unit tests with `uv run python -m unittest discover -s tests -v`. They use fake Ollama, TTS, and playback objects and do not need a running Ollama server or audio device.
