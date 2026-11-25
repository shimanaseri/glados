"""Sounddevice playback helpers."""

import threading
import time


def play_audio(samples, sample_rate: int, interrupt: threading.Event | None = None) -> None:
    import sounddevice as sd

    sd.play(samples, sample_rate)
    try:
        while sd.get_stream().active:
            if interrupt is not None and interrupt.is_set():
                sd.stop()
                return
            time.sleep(0.03)
    finally:
        if interrupt is not None and interrupt.is_set():
            sd.stop()
