import unittest
from unittest.mock import patch

from textual.widgets import Input, RichLog, Static

from glados.art import IDLE
from glados.tui import GladosTui


class TuiTests(unittest.IsolatedAsyncioTestCase):
    async def test_retro_layout_mounts_without_voice_model(self):
        async with GladosTui(voice=False).run_test(size=(110, 38)) as pilot:
            app = pilot.app
            self.assertIsInstance(app.query_one("#transcript"), RichLog)
            self.assertIsInstance(app.query_one("#system-log"), RichLog)
            self.assertIsInstance(app.query_one("#prompt"), Input)
            self.assertIsInstance(app.query_one("#portrait"), Static)
            self.assertEqual(str(app.query_one("#portrait").render()).strip(), IDLE.strip())

    async def test_text_only_chat_archives_background_reply(self):
        with patch("glados.tui.stream_reply", return_value=iter(["Test complete."])):
            async with GladosTui(voice=False).run_test(size=(110, 40)) as pilot:
                app = pilot.app
                prompt = app.query_one("#prompt", Input)
                prompt.value = "Run a test"
                await pilot.press("enter")
                for _ in range(20):
                    if len(app.history) > 1:
                        break
                    await pilot.pause(0.05)
                self.assertEqual(app.history[-1], ("assistant", "Test complete."))


if __name__ == "__main__":
    unittest.main()
