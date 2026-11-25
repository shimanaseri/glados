import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from glados.llm import stream_reply
from glados.persona import SYSTEM_PROMPT


class Chunk:
    def __init__(self, content):
        self.content = content


class FakeClient:
    def __init__(self):
        self.messages = None

    def stream(self, messages):
        self.messages = messages
        yield Chunk("Hello")
        yield Chunk(" there.")
        yield Chunk(12)  # Non-text metadata should not leak into spoken output.


class LlmTests(unittest.TestCase):
    def test_langchain_tracing_is_disabled(self):
        self.assertEqual(os.environ["LANGSMITH_TRACING"].lower(), "false")
        self.assertEqual(os.environ["LANGCHAIN_TRACING_V2"].lower(), "false")

    def test_streams_text_and_passes_persona_history_and_memory(self):
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = Path(temp_dir) / "memory.md"
            memory.write_text("The test subject prefers concise replies.", encoding="utf-8")
            with patch("glados.llm.MEMORY_FILE", memory):
                result = list(stream_reply([("user", "old question"), ("assistant", "old answer")], "Now?", client))

        self.assertEqual(result, ["Hello", " there."])
        self.assertEqual(client.messages[0].content, SYSTEM_PROMPT)
        self.assertIn("concise replies", client.messages[1].content)
        self.assertEqual(client.messages[-3].content, "old question")
        self.assertEqual(client.messages[-2].content, "old answer")
        self.assertEqual(client.messages[-1].content, "Now?")


if __name__ == "__main__":
    unittest.main()
