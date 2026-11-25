import threading
import unittest

from glados.pipeline import VoicePipeline, extract_sentences


class FakeSpeech:
    def __init__(self, text):
        self.samples = text
        self.sample_rate = 22050


class FakeTts:
    def __init__(self):
        self.sentences = []

    def synthesize(self, text):
        self.sentences.append(text)
        return FakeSpeech(text)


class PipelineTests(unittest.TestCase):
    def test_sentence_splitter_keeps_partial_text_until_boundary(self):
        self.assertEqual(
            list(extract_sentences(["First sentence. Sec", "ond one! trailing words"])),
            ["First sentence.", "Second one!", "trailing words"],
        )

    def test_synthesizes_and_plays_sentences_in_order_while_streaming_text(self):
        tts = FakeTts()
        played = []
        shown = []

        def llm(history, user_input):
            yield "First thought. "
            yield "Second thought."

        def player(samples, rate, interrupt):
            played.append((samples, rate))

        pipeline = VoicePipeline(tts, llm=llm, player=player)
        full_text = pipeline.run([], "test", on_text=shown.append)

        self.assertEqual(full_text, "First thought. Second thought.")
        self.assertEqual("".join(shown), full_text)
        self.assertEqual(tts.sentences, ["First thought.", "Second thought."])
        self.assertEqual(played, [("First thought.", 22050), ("Second thought.", 22050)])

    def test_interrupt_event_stops_additional_playback(self):
        tts = FakeTts()
        interruption = threading.Event()
        played = []

        def llm(history, user_input):
            yield "First. "
            yield "Second. "
            yield "Third."

        def player(samples, rate, stop):
            played.append(samples)
            stop.set()

        result = VoicePipeline(tts, llm=llm, player=player).run([], "test", interrupt=interruption)
        self.assertTrue(result.startswith("First."))
        self.assertLessEqual(len(played), 1)


if __name__ == "__main__":
    unittest.main()
