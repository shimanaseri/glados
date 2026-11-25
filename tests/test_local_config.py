import os
import unittest

from glados.config import validate_local_ollama_host


class LocalOllamaConfigTests(unittest.TestCase):
    def test_accepts_localhost_and_loopback_addresses(self):
        for host in ("http://localhost:11434", "http://127.0.0.1:11434", "http://[::1]:11434"):
            with self.subTest(host=host):
                self.assertEqual(validate_local_ollama_host(host), host)

    def test_rejects_remote_hosts_and_credentials(self):
        for host in ("https://api.ollama.ai", "http://192.168.1.5:11434", "http://token@localhost:11434"):
            with self.subTest(host=host):
                with self.assertRaises(ValueError):
                    validate_local_ollama_host(host)

    def test_loopback_bypasses_configured_http_proxies(self):
        for variable in ("NO_PROXY", "no_proxy"):
            entries = os.environ[variable].split(",")
            for host in ("localhost", "127.0.0.1", "::1"):
                self.assertIn(host, entries)


if __name__ == "__main__":
    unittest.main()
