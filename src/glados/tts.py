"""Sherpa-ONNX voice synthesis. The model is loaded once per TTS instance."""

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from glados.config import VOICE_MODEL, VOICE_TOKENS, VOICE_DATA_DIR, VOICE_THREADS


@dataclass
class Speech:
    samples: object
    sample_rate: int
    generation_seconds: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return len(self.samples) / self.sample_rate


class TextToSpeech:
    def __init__(self, model: Path = VOICE_MODEL, tokens: Path = VOICE_TOKENS,
                 data_dir: Path = VOICE_DATA_DIR, num_threads: int = VOICE_THREADS):
        missing = [str(path) for path in (model, tokens, data_dir) if not Path(path).exists()]
        if missing:
            raise FileNotFoundError("GLaDOS voice files are missing: " + ", ".join(missing)
                                    + ". Run `glados --download-voice` first.")
        import sherpa_onnx

        self._engine = sherpa_onnx.OfflineTts(
            sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(
                    vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                        model=str(model), tokens=str(tokens), data_dir=str(data_dir)
                    ),
                    num_threads=num_threads,
                )
            )
        )

    def synthesize(self, text: str) -> Speech:
        started = perf_counter()
        audio = self._engine.generate(text)
        return Speech(audio.samples, audio.sample_rate, perf_counter() - started)


def main() -> None:
    """Generate and play a sample, printing synthesis and playback durations."""
    from glados.audio import play_audio

    tts = TextToSpeech()
    sample = tts.synthesize("The test is over. You may stop being useful now.")
    print(f"Generated in {sample.generation_seconds:.2f}s; audio is {sample.duration_seconds:.2f}s.")
    play_audio(sample.samples, sample.sample_rate)


if __name__ == "__main__":
    main()
