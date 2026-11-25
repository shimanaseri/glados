"""Download the GLaDOS VITS-Piper weights and their sherpa-onnx assets."""

import argparse
import sys
import tarfile
import urllib.request
from pathlib import Path

from glados.config import VOICE_DIR, VOICE_TOKENS, VOICE_DATA_DIR, FALLBACK_VOICE_MODEL


VOICE_ARCHIVE_URL = (
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/"
    "vits-piper-en_US-glados.tar.bz2"
)
FALLBACK_MODEL_URL = (
    "https://huggingface.co/rokeya71/VITS-Piper-GlaDOS-en-onnx/resolve/main/glados.onnx"
)


def _safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    root = destination.resolve()
    for member in archive.getmembers():
        if member.issym() or member.islnk():
            raise ValueError(f"Links are not allowed in voice archive: {member.name}")
        target = (destination / member.name).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"Unsafe path in voice archive: {member.name}")
    archive.extractall(destination)


def _download_resumable(url: str, destination: Path) -> None:
    """Download with byte progress and resume a partial archive after interruption."""
    offset = destination.stat().st_size if destination.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        if offset and response.status != 206:
            offset = 0
        total_header = response.headers.get("Content-Range", "").rsplit("/", 1)[-1]
        total = int(total_header) if total_header.isdigit() else offset + int(response.headers.get("Content-Length", 0))
        mode = "ab" if offset else "wb"
        downloaded = offset
        last_percent = -1
        with destination.open(mode) as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                downloaded += len(chunk)
                percent = int(downloaded * 100 / total) if total else 0
                if percent != last_percent:
                    print(f"\rVoice download: {downloaded / (1024 * 1024):.1f} MB ({percent}%)", end="", flush=True)
                    last_percent = percent
    print(file=sys.stdout, flush=True)
    if total and downloaded != total:
        raise OSError(f"Incomplete voice archive: downloaded {downloaded} of {total} bytes; run setup again to resume.")


def download_voice(fallback: bool = False) -> None:
    if fallback:
        if not VOICE_TOKENS.exists() or not VOICE_DATA_DIR.exists():
            raise FileNotFoundError("Download the default voice first; fallback uses its tokens and eSpeak data.")
        FALLBACK_VOICE_MODEL.parent.mkdir(parents=True, exist_ok=True)
        print("Downloading alternate GLaDOS voice model (~64 MB)...")
        urllib.request.urlretrieve(FALLBACK_MODEL_URL, FALLBACK_VOICE_MODEL)
        return

    VOICE_DIR.parent.mkdir(parents=True, exist_ok=True)
    print("Downloading GLaDOS voice files (~80 MB)...")
    archive_path = VOICE_DIR.parent / ".vits-piper-en_US-glados.tar.bz2.partial"
    _download_resumable(VOICE_ARCHIVE_URL, archive_path)
    with tarfile.open(archive_path, "r:bz2") as archive:
        _safe_extract(archive, VOICE_DIR.parent)
    archive_path.unlink(missing_ok=True)
    print(f"Voice files installed in {VOICE_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the GLaDOS sherpa-onnx voice files.")
    parser.add_argument("--fallback", action="store_true", help="Download the alternate VITS-Piper model")
    args = parser.parse_args()
    download_voice(fallback=args.fallback)


if __name__ == "__main__":
    main()
