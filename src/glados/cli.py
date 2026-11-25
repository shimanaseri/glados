"""Command line interface for the GLaDOS assistant."""

import argparse
from threading import Event

from glados.config import VOICE_MODEL, VOICE_TOKENS, VOICE_DATA_DIR, FALLBACK_VOICE_MODEL
from glados.llm import stream_reply
from glados.voice_setup import download_voice


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="glados", description="Chat with GLaDOS in your terminal.")
    parser.add_argument("--text-only", action="store_true", help="Disable speech output")
    parser.add_argument("--download-voice", action="store_true", help="Download the default sherpa-onnx voice")
    parser.add_argument("--fallback-voice", action="store_true", help="Use the alternate VITS-Piper model")
    parser.add_argument("--tts-demo", action="store_true", help="Generate and play one test sentence")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.download_voice:
        download_voice(fallback=args.fallback_voice)
        return

    tts = None
    if not args.text_only:
        model = FALLBACK_VOICE_MODEL if args.fallback_voice else VOICE_MODEL
        if args.fallback_voice and not model.exists():
            download_voice(fallback=True)
        if model.exists() and VOICE_TOKENS.exists() and VOICE_DATA_DIR.exists():
            from glados.tts import TextToSpeech
            tts = TextToSpeech(model=model)
            if args.tts_demo:
                from glados.audio import play_audio
                sample = tts.synthesize("The test is over. You may stop being useful now.")
                print(f"Generated in {sample.generation_seconds:.2f}s; audio is {sample.duration_seconds:.2f}s.")
                play_audio(sample.samples, sample.sample_rate)
                return
            from glados.pipeline import VoicePipeline
            pipeline = VoicePipeline(tts)
        else:
            if args.tts_demo:
                raise FileNotFoundError("Run `glados --download-voice` to install speech files.")
            print("Voice files are missing; using text mode. Run `glados --download-voice` to enable speech.\n")
            pipeline = None
    else:
        pipeline = None

    history = []
    mode = "voice" if pipeline else "text"
    print(f"GLaDOS is online ({mode} mode). Type 'quit' to exit, 'reset' to clear history.")
    if pipeline:
        print("Press Ctrl+C during a reply to stop speech and clear queued audio.\n")
    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("GLaDOS: Leaving so soon? How predictable.")
                break
            if user_input.lower() == "reset":
                history = []
                print("GLaDOS: Conversation history wiped. Not that you were memorable.\n")
                continue

            print("GLaDOS: ", end="", flush=True)
            full_reply = ""
            if pipeline:
                interruption = Event()
                try:
                    full_reply = pipeline.run(
                        history,
                        user_input,
                        on_text=lambda text: print(text, end="", flush=True),
                        interrupt=interruption,
                    )
                except KeyboardInterrupt:
                    interruption.set()
                    print("\nGLaDOS: Playback interrupted. How impatient.")
                    continue
            else:
                for chunk in stream_reply(history, user_input):
                    print(chunk, end="", flush=True)
                    full_reply += chunk
            print("\n")
            history.extend((("user", user_input), ("assistant", full_reply)))
    except (EOFError, KeyboardInterrupt):
        print("\nGLaDOS: Session terminated. Another test subject, gone.")


if __name__ == "__main__":
    main()
