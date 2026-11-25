"""Concurrent LLM -> sentence TTS -> ordered audio playback pipeline."""

from __future__ import annotations

import queue
import re
import threading
from collections.abc import Callable, Iterable

from glados.audio import play_audio
from glados.llm import stream_reply
from glados.tts import Speech, TextToSpeech

_END = object()
_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")


def extract_sentences(chunks: Iterable[str]):
    """Yield sentences as soon as punctuation and following whitespace arrive."""
    pending = ""
    for chunk in chunks:
        pending += chunk
        parts = _BOUNDARY.split(pending)
        pending = parts.pop()
        for part in parts:
            sentence = part.strip()
            if sentence:
                yield sentence
    if pending.strip():
        yield pending.strip()


class VoicePipeline:
    def __init__(self, tts: TextToSpeech, llm: Callable = stream_reply,
                 player: Callable = play_audio, queue_size: int = 4):
        self.tts = tts
        self.llm = llm
        self.player = player
        self.queue_size = queue_size

    def run(self, history, user_input: str, on_text: Callable[[str], None] | None = None,
            interrupt: threading.Event | None = None) -> str:
        stop = interrupt or threading.Event()
        sentence_queue: queue.Queue = queue.Queue(self.queue_size)
        audio_queue: queue.Queue = queue.Queue(self.queue_size)
        errors: queue.Queue = queue.Queue()
        response: list[str] = []

        def put_until_stopped(q, value):
            while not stop.is_set():
                try:
                    q.put(value, timeout=0.1)
                    return True
                except queue.Full:
                    continue
            return False

        def produce_text():
            try:
                def chunks():
                    for chunk in self.llm(history, user_input):
                        if stop.is_set():
                            break
                        response.append(chunk)
                        if on_text:
                            on_text(chunk)
                        yield chunk
                for sentence in extract_sentences(chunks()):
                    if not put_until_stopped(sentence_queue, sentence):
                        break
            except BaseException as exc:
                errors.put(exc)
                stop.set()
            finally:
                put_until_stopped(sentence_queue, _END)

        def synthesize():
            try:
                while not stop.is_set():
                    try:
                        sentence = sentence_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    if sentence is _END:
                        put_until_stopped(audio_queue, _END)
                        return
                    speech = self.tts.synthesize(sentence)
                    if not stop.is_set():
                        put_until_stopped(audio_queue, (speech.samples, speech.sample_rate))
            except BaseException as exc:
                errors.put(exc)
                stop.set()
            finally:
                put_until_stopped(audio_queue, _END)

        def play_in_order():
            try:
                while not stop.is_set():
                    try:
                        item = audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    if item is _END:
                        return
                    self.player(item[0], item[1], stop)
            except BaseException as exc:
                errors.put(exc)
                stop.set()

        workers = [
            threading.Thread(target=play_in_order, daemon=True, name="glados-playback"),
            threading.Thread(target=synthesize, daemon=True, name="glados-tts"),
            threading.Thread(target=produce_text, daemon=True, name="glados-llm"),
        ]
        for worker in workers:
            worker.start()
        try:
            for worker in workers:
                worker.join()
        except KeyboardInterrupt:
            stop.set()
            for worker in workers:
                worker.join()
            raise
        if not errors.empty():
            raise errors.get()
        return "".join(response)
