# Meeting Action Agent

Meeting Action Agent is a beginner-friendly, zero-cost local Streamlit application that analyzes recorded meeting audio/video and local microphone audio. It extracts a transcript using Faster-Whisper, sends the transcript to a local Ollama Llama 3.2 workflow built with a simple LangGraph-style graph, then validates and exports the meeting result as JSON, TXT, and CSV files.

## Features

- Upload a recorded meeting video or audio file.
- Convert video files to WAV audio with FFmpeg.
- Transcribe audio locally with Faster-Whisper.
- Analyze the transcript locally with Ollama + Llama 3.2.
- Validate the response and normalize missing evidence into safe defaults.
- Export a meeting result as JSON, TXT, and CSV files in the outputs folder.
- Use a live microphone demo mode that records a short local segment.

## Architecture

Recorded Meeting or Live Audio
? FFmpeg media preparation
? Faster-Whisper transcription
? LangGraph-style single-agent workflow
? Ollama + Llama 3.2 analysis
? Validation and normalization
? Local file exports in outputs/

## Technology stack

- Python
- Streamlit
- Faster-Whisper
- Ollama
- Llama 3.2
- LangGraph
- FFmpeg
- Local JSON/TXT/CSV exports

## Folder structure

```text
Meeting_Action_Agent/
├── app/
├── agent/
├── audio/
├── utils/
├── screenshots/
│   ├── recorded_meeting.png
│   └── meeting_transcript.png
├── README.md
├── requirements.txt
└── .gitignore
```

## Windows installation

Install Python 3.11+ and then create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Python virtual environment setup

Use the project virtual environment for all local commands:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

## Requirements installation

```powershell
pip install -r requirements.txt
```

## Ollama installation and setup

Install Ollama locally from the Ollama website or official installer, then pull the default model used by the project:

```powershell
ollama --version
ollama pull llama3.2
ollama list
```

## Llama 3.2 setup

The default model name in the app is `llama3.2`.

```powershell
ollama run llama3.2
```

## FFmpeg setup

Install FFmpeg and add it to PATH, then verify it:

```powershell
ffmpeg -version
```

## How to run the Streamlit website

Run the Streamlit app from the project root:

```powershell
python -m streamlit run app/main.py
```

## Recorded meeting workflow

1. Open the Streamlit app.
2. Choose Recorded Meeting.
3. Upload a video or audio file.
4. Click Analyze Meeting.
5. The app prepares audio, transcribes it locally, and sends the transcript to Ollama.
6. The structured result is displayed in the UI and exported locally.

## Live microphone workflow

1. Open the Streamlit app.
2. Choose Live Meeting.
3. Record a short microphone segment.
4. Click Analyze Recorded Segment.
5. The segment is transcribed locally and analyzed by the same workflow.

This is a near-real-time demonstration and is not a direct Zoom, Google Meet, or Microsoft Teams bot.

## Output formats

The app exports the same meeting analysis into these local files:

- JSON
- TXT
- CSV

Files are stored in the outputs/ folder.

## Limitations

- Speaker identification and diarization are not guaranteed.
- Local microphone mode is a near-real-time demonstration only.
- Accuracy depends on audio quality and local model performance.
- The project uses local files only and does not write to a database.
- This project does not directly join external meeting platforms.

## Future improvements

- Better speaker labels and speaker diarization
- Stronger transcript cleanup
- More export formatting
- Better UI for results and exports
- Additional local validation rules
