from __future__ import annotations

import os
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except Exception as exc:  # pragma: no cover - import error is error surfaced to users
    WhisperModel = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class LocalTranscriber:
    """Reusable local faster-whisper transcriber.

    The same instance of Whisper can be held between calls to avoid
    reloading the model for each transcript. This helps the project stay
    friendly for local desktops and beginners.
    """

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        if WhisperModel is None:
            raise RuntimeError(
                "faster-whisper is not installed. Install dependencies with: pip install -r requirements.txt"
            ) from _IMPORT_ERROR

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, media_path: str) -> str:
        """Transcribe audio or video audio extracted to a WAV path."""

        path = Path(media_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {media_path}")

        if path.stat().st_size == 0:
            raise ValueError("The audio file is empty. Please choose a valid meeting recording.")

        try:
            segments, _ = self.model.transcribe(
                str(path),
                beam_size=5,
                vad_filter=True,
                word_timestamps=False,
            )
            transcript = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
            return transcript.strip()
        except Exception as exc:
            raise RuntimeError(f"Whisper transcription failed: {exc}") from exc
