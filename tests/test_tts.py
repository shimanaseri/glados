import unittest

from glados.tts import Speech


class TtsTests(unittest.TestCase):
    def test_audio_duration_uses_sample_count_and_rate(self):
        speech = Speech([0.0] * 44100, 22050, 0.5)
        self.assertEqual(speech.duration_seconds, 2.0)
        self.assertEqual(speech.generation_seconds, 0.5)


if __name__ == "__main__":
    unittest.main()
