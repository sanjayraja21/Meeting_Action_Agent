import os
import tempfile
from pathlib import Path
import streamlit as st

from agent.meeting_agent import run_agent
from audio.media import prepare_media
from audio.transcription import LocalTranscriber
from utils.exports import analysis_to_json, analysis_to_txt, analysis_to_csv


st.set_page_config(
    page_title="Meeting Action Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Meeting Action Agent")
st.caption("Zero-cost local Agentic AI for recorded meetings and near-real-time microphone analysis.")

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Input mode", ["Recorded Meeting", "Live Meeting"])
    model = st.text_input("Ollama model", "llama3.2")
    whisper_size = st.selectbox("Whisper model", ["tiny", "base", "small"], index=1)

if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None

if mode == "Recorded Meeting":
    st.subheader("🎥 Recorded Meeting Analysis")

    uploaded = st.file_uploader(
        "Upload a meeting video or audio file",
        type=["mp4", "mov", "mkv", "avi", "webm", "wav", "mp3", "m4a", "mpeg", "mpg"],
    )

    if uploaded:
        if st.button("Analyze Meeting", type="primary"):
            suffix = Path(uploaded.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.getbuffer())
                source_path = tmp.name

            try:
                with st.spinner("Loading local Whisper model..."):
                    transcriber = LocalTranscriber(whisper_size)

                with st.spinner("Preparing audio..."):
                    audio_path = prepare_media(source_path)

                with st.spinner("Transcribing meeting locally..."):
                    transcript = transcriber.transcribe(audio_path)

                if not transcript:
                    st.error("No speech was detected.")
                    st.stop()

                st.session_state.transcript = transcript

                with st.spinner("Meeting Agent is analyzing the transcript..."):
                    analysis = run_agent(transcript, model)

                st.session_state.analysis = analysis
                st.success("Meeting analysis completed.")

            except Exception as exc:
                st.error(f"Error: {exc}")

    if st.session_state.transcript:
        with st.expander("View transcript", expanded=False):
            st.write(st.session_state.transcript)

else:
    st.subheader("🎙 Live Meeting")
    st.info(
        "This free local demo processes microphone audio in chunks. "
        "For a stable first demo, record the meeting and use Recorded Meeting mode. "
        "Direct Zoom/Meet/Teams bot integration is a later extension."
    )

    audio = st.audio_input("Record a short meeting segment")

    if audio is not None and st.button("Analyze Recorded Segment", type="primary"):
        suffix = ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio.getbuffer())
            source_path = tmp.name

        try:
            with st.spinner("Transcribing the microphone segment..."):
                transcriber = LocalTranscriber(whisper_size)
                transcript = transcriber.transcribe(source_path)

            if transcript:
                st.session_state.transcript = transcript
                with st.spinner("Agent analyzing segment..."):
                    st.session_state.analysis = run_agent(transcript, model)
                st.success("Segment analyzed.")
            else:
                st.warning("No speech detected in this segment.")
        except Exception as exc:
            st.error(f"Error: {exc}")

analysis = st.session_state.analysis

if analysis:
    st.divider()
    st.header("📊 Meeting Results")

    st.subheader("📝 Summary")
    st.write(analysis.get("summary", ""))

    c1, c2, c3 = st.columns(3)
    c1.metric("Participants", len(analysis.get("participants", [])))
    c2.metric("Action Items", len(analysis.get("action_items", [])))
    c3.metric("Decisions", len(analysis.get("decisions", [])))

    st.subheader("👥 Participants")
    st.write(", ".join(analysis.get("participants", [])) or "None identified")

    st.subheader("✅ Action Items")
    actions = analysis.get("action_items", [])
    if actions:
        st.dataframe(actions, use_container_width=True)
    else:
        st.info("No action items detected.")

    st.subheader("📌 Decisions")
    for item in analysis.get("decisions", []):
        st.write(f"- {item}")

    st.subheader("🔄 Follow-up Items")
    for item in analysis.get("follow_up_items", []):
        st.write(f"- {item}")

    st.subheader("⬇️ Export")
    col1, col2, col3 = st.columns(3)
    col1.download_button(
        "Download JSON",
        analysis_to_json(analysis),
        "meeting_analysis.json",
        "application/json",
    )
    col2.download_button(
        "Download TXT",
        analysis_to_txt(analysis),
        "meeting_report.txt",
        "text/plain",
    )
    col3.download_button(
        "Download CSV",
        analysis_to_csv(analysis),
        "meeting_action_items.csv",
        "text/csv",
    )
