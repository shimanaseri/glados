"""Amber-on-black Textual interface for local GLaDOS chat and voice."""

from pathlib import Path
import argparse
import threading

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Input, RichLog, Static

from glados.art import ANNOYED, IDLE, TALKING
from glados.config import VOICE_MODEL, VOICE_TOKENS, VOICE_DATA_DIR
from glados.doctor import run_checks
from glados.pipeline import VoicePipeline
from glados.llm import stream_reply
from glados.tts import TextToSpeech


class GladosTui(App):
    TITLE = "GLaDOS // APERTURE TEST CONSOLE"
    CSS_PATH = Path(__file__).with_name("tui.tcss")
    BINDINGS = [("escape", "interrupt", "Interrupt"), ("ctrl+c", "quit", "Quit")]

    def __init__(self, voice: bool = True) -> None:
        super().__init__()
        self.voice = voice
        self.history = []
        self.interruption: threading.Event | None = None
        self.completed_reply = ""
        self.pending_sentence = ""
        self.sentence_chars = 0
        self.typing_timer = None
        self.portrait_pulse = None
        self.pulse_on = False
        self.patience = 100
        self.turns = 0
        self.pipeline = VoicePipeline(TextToSpeech(VOICE_MODEL, VOICE_TOKENS, VOICE_DATA_DIR)) if voice else None
        self.streamed_text = ""

    def compose(self) -> ComposeResult:
        yield Static("A P E R T U R E   S C I E N C E   //   G L A D O S   T E S T   C O N S O L E", id="masthead")
        with Horizontal(id="body"):
            with Vertical(id="chat-panel"):
                yield RichLog(id="transcript", wrap=True, markup=False, highlight=False)
                yield Static("", id="current-line", markup=False)
                yield Static("SUBTITLE // awaiting vocal output", id="subtitle", markup=False)
                yield Input(placeholder="Enter a test response, human...", id="prompt")
                yield Static("PATIENCE  [██████████]  100%", id="patience", markup=False)
            with Vertical(id="side-panel"):
                yield Static("SYSTEM LOG // SUBJECT INDEX", id="side-title")
                yield RichLog(id="system-log", wrap=True, markup=False, highlight=False)
                yield Static(IDLE, id="portrait", markup=False)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#prompt", Input).focus()
        self.query_one("#system-log", RichLog).write("BOOT // local Ollama link verified")
        self.query_one("#system-log", RichLog).write("BOOT // sherpa-onnx voice core loaded")
        self.query_one("#system-log", RichLog).write("NOTICE // all tests are involuntary")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt:
            return
        event.input.value = ""
        if self.interruption and not self.interruption.is_set():
            self.query_one("#system-log", RichLog).write("BUSY // interrupt current test with Esc")
            return
        self.turns += 1
        self.history.append(("user", prompt))
        event.input.disabled = True
        self.query_one("#transcript", RichLog).write(f"> {prompt}")
        penalty = min(24, max(0, len(prompt.split()) - 4) + (8 if "please" in prompt.lower() else 0))
        self.patience = max(0, self.patience - penalty)
        self._update_patience()
        self.interruption = threading.Event()
        self.completed_reply = ""
        self.streamed_text = ""
        self._write_log(f"SUBJECT {self.turns:03d} // response requested")
        self.run_reply(prompt, self.interruption)

    @work(thread=True, exclusive=True)
    def run_reply(self, prompt: str, stop: threading.Event) -> None:
        try:
            if self.pipeline:
                reply = self.pipeline.run(
                    self.history[:-1],
                    prompt,
                    interrupt=stop,
                    on_sentence=lambda sentence, seconds: self.call_from_thread(
                        self._begin_sentence, sentence, seconds
                    ),
                )
            else:
                parts = []
                for chunk in stream_reply(self.history[:-1], prompt):
                    if stop.is_set():
                        break
                    parts.append(chunk)
                    self.call_from_thread(self._append_stream_text, chunk)
                reply = "".join(parts)
            self.call_from_thread(self._finish_reply, reply, stop.is_set())
        except Exception as exc:
            self.call_from_thread(self._reply_error, str(exc))

    def _begin_sentence(self, sentence: str, seconds: float) -> None:
        if self.typing_timer is not None:
            self.typing_timer.stop()
        self.pending_sentence = sentence
        self.sentence_chars = 0
        self.query_one("#subtitle", Static).update(f"SUBTITLE // {sentence}")
        portrait = self.query_one("#portrait", Static)
        portrait.update(TALKING)
        portrait.set_class(True, "talking")
        portrait.set_class(False, "annoyed")
        portrait.set_class(False, "pulse-on")
        self.pulse_on = False
        if self.portrait_pulse is not None:
            self.portrait_pulse.stop()
        self.portrait_pulse = self.set_interval(0.35, self._pulse_portrait)
        self.query_one("#current-line", Static).update("GLaDOS: ")
        interval = max(0.015, seconds / max(1, len(sentence)))

        def type_character() -> None:
            if self.sentence_chars >= len(self.pending_sentence):
                return
            self.sentence_chars += 1
            shown = self.pending_sentence[:self.sentence_chars]
            self.query_one("#current-line", Static).update(f"GLaDOS: {shown}")
            if self.sentence_chars >= len(self.pending_sentence):
                self.completed_reply += shown + " "
                self.query_one("#transcript", RichLog).write(f"GLaDOS: {shown}")

        self.typing_timer = self.set_interval(interval, type_character, repeat=len(sentence))

    def _append_stream_text(self, text: str) -> None:
        self.streamed_text += text
        self.query_one("#current-line", Static).update("GLaDOS: " + self.streamed_text)

    def _finish_reply(self, reply: str, interrupted: bool) -> None:
        if self.typing_timer is not None:
            self.typing_timer.stop()
            self.typing_timer = None
        self.query_one("#current-line", Static).update("")
        self.query_one("#subtitle", Static).update("SUBTITLE // " + ("playback interrupted" if interrupted else "end of response"))
        if self.portrait_pulse is not None:
            self.portrait_pulse.stop()
            self.portrait_pulse = None
        portrait = self.query_one("#portrait", Static)
        portrait.update(ANNOYED if self.patience < 40 else IDLE)
        portrait.set_class(False, "talking")
        portrait.set_class(self.patience < 40, "annoyed")
        portrait.set_class(False, "pulse-on")
        self.pulse_on = False
        if reply and not interrupted:
            self.history.append(("assistant", reply))
            if not self.voice:
                self.query_one("#transcript", RichLog).write(f"GLaDOS: {reply}")
            self._write_log("TEST COMPLETE // response archived")
        self.interruption = None
        prompt = self.query_one("#prompt", Input)
        prompt.disabled = False
        prompt.focus()

    def _reply_error(self, message: str) -> None:
        if self.typing_timer is not None:
            self.typing_timer.stop()
            self.typing_timer = None
        self._write_log("ERROR // local response failed")
        self.query_one("#subtitle", Static).update(f"SUBTITLE // {message[:100]}")
        if self.portrait_pulse is not None:
            self.portrait_pulse.stop()
            self.portrait_pulse = None
        portrait = self.query_one("#portrait", Static)
        portrait.update(ANNOYED)
        portrait.set_class(False, "talking")
        portrait.set_class(True, "annoyed")
        portrait.set_class(False, "pulse-on")
        self.pulse_on = False
        self.interruption = None
        prompt = self.query_one("#prompt", Input)
        prompt.disabled = False
        prompt.focus()

    def _write_log(self, message: str) -> None:
        self.query_one("#system-log", RichLog).write(message)

    def _update_patience(self) -> None:
        filled = round(self.patience / 10)
        meter = "█" * filled + "░" * (10 - filled)
        self.query_one("#patience", Static).update(f"PATIENCE  [{meter}]  {self.patience}%")

    def _pulse_portrait(self) -> None:
        self.pulse_on = not self.pulse_on
        self.query_one("#portrait", Static).set_class(self.pulse_on, "pulse-on")

    def action_interrupt(self) -> None:
        if self.interruption is not None:
            self.interruption.set()
            if self.typing_timer is not None:
                self.typing_timer.stop()
                self.typing_timer = None
            if self.portrait_pulse is not None:
                self.portrait_pulse.stop()
                self.portrait_pulse = None
            self._write_log("INTERRUPT // subject halted playback")
            portrait = self.query_one("#portrait", Static)
            portrait.update(ANNOYED)
            portrait.set_class(False, "talking")
            portrait.set_class(True, "annoyed")
            portrait.set_class(False, "pulse-on")
            self.pulse_on = False


def main() -> None:
    parser = argparse.ArgumentParser(description="Local retro GLaDOS terminal UI")
    parser.add_argument("--text-only", action="store_true", help="Run without voice assets")
    args = parser.parse_args()
    errors = run_checks(require_voice=not args.text_only)
    if errors:
        print("GLaDOS: The console cannot start. Fix these local test chamber faults:")
        for error in errors:
            print(f"  - {error}")
        return
    try:
        GladosTui(voice=not args.text_only).run()
    except Exception as exc:
        print("GLaDOS: The local console failed to initialize. A disappointing result.")
        print(f"  - {exc}")


if __name__ == "__main__":
    main()
