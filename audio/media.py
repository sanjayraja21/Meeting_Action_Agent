from pathlib import Path
import shutil
import subprocess
import tempfile
import os


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".mpeg", ".mpg"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mpeg", ".mpg"}


def resolve_ffmpeg_path() -> str:
    """Return an ffmpeg executable path from PATH or common Windows installs."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    path_dirs = []
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        if folder:
            path_dirs.append(Path(folder))

    for folder in path_dirs:
        candidate = folder / "ffmpeg.exe"
        if candidate.exists():
            return str(candidate)

    common_dirs = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "ffmpeg" / "bin",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "ffmpeg" / "bin",
        Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages",
    ]

    for base in common_dirs:
        if not base.exists():
            continue
        for match in sorted(base.rglob("ffmpeg.exe")):
            if "bin" in str(match.parent).lower():
                return str(match)

    return ""


def extract_audio(video_path: str) -> str:
    """Extract mono 16kHz WAV audio using FFmpeg.

    The audio file is kept in a safe temporary location and not stored in the
    repository permanently.
    """

    ffmpeg_path = resolve_ffmpeg_path()
    if not ffmpeg_path:
        raise RuntimeError(
            "FFmpeg is not installed or not available in PATH. Install FFmpeg and make sure ffmpeg.exe is in PATH."
        )

    source = Path(video_path)
    if not source.exists():
        raise FileNotFoundError(f"Input media file not found: {video_path}")

    output = Path(tempfile.gettempdir()) / f"meeting_audio_{os.getpid()}_{source.stem}.wav"

    command = [
        ffmpeg_path, "-y",
        "-i", str(source),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        str(output),
    ]

    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("FFmpeg was not found on PATH. Install FFmpeg and try again.") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip()[-1500:] if completed.stderr else completed.stdout.strip()[-1500:]
        raise RuntimeError(
            "FFmpeg could not extract audio. Check that FFmpeg is installed and available in PATH.\n\n" + detail
        )

    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("FFmpeg finished without producing a valid audio file.")

    return str(output)


def prepare_media(file_path: str) -> str:
    """Prepare an uploaded file for transcription.

    Video files are converted to 16kHz mono WAV using FFmpeg. Audio files are
    passed through directly because they are already convertible by Whisper.
    """

    suffix = Path(file_path).suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return extract_audio(file_path)
    if suffix in AUDIO_EXTENSIONS or suffix == ".wav":
        return file_path
    raise ValueError("Unsupported media type. Use a video or audio file such as MP4, MOV, MKV, WAV, MP3, M4A, or MPEG.")
