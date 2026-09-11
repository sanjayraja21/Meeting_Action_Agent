import json
import os
import re
from typing import Any

import ollama
from langgraph.graph import StateGraph, START, END

from agent.prompts import SYSTEM_PROMPT
from agent.state import MeetingState
from utils.validation import validate_analysis, validate_json_text


DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def _extract_json(text: str) -> dict[str, Any]:
    """Safely parse valid JSON from an Ollama response message."""

    data = validate_json_text(text)
    if not isinstance(data, dict):
        raise ValueError("The model did not return a JSON object.")
    return data


def analyze_with_ollama(transcript: str, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Call local Ollama and return a safe structured JSON object.

    If Ollama is unavailable, the exception is raised clearly so the UI can
    show a friendly error rather than crashing the Streamlit process.
    """

    if not transcript.strip():
        raise ValueError("Transcript is empty.")

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            options={"temperature": 0.1},
        )
    except Exception as exc:
        message = str(exc)
        if "connection" in message.lower() or "refused" in message.lower():
            raise RuntimeError("Ollama is not running. Start Ollama and make sure the selected model is installed.") from exc
        raise RuntimeError(f"Ollama failed: {message}") from exc

    content = response.get("message", {}).get("content", "")
    if not content.strip():
        raise ValueError("The local LLM returned an empty response.")
    return _extract_json(content)


def _agent_node(state: MeetingState) -> MeetingState:
    try:
        result = analyze_with_ollama(state["transcript"], state.get("model", DEFAULT_MODEL))
        return {"raw_analysis": result}
    except Exception as exc:
        return {"error": str(exc)}


def _validation_node(state: MeetingState) -> MeetingState:
    if state.get("error"):
        return state
    try:
        return {"validated_analysis": validate_analysis(state["raw_analysis"])}
    except Exception as exc:
        return {"error": str(exc)}


def build_agent():
    """Return a LangGraph workflow object for transcript analysis."""

    graph = StateGraph(MeetingState)
    graph.add_node("analyze", _agent_node)
    graph.add_node("validate", _validation_node)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "validate")
    graph.add_edge("validate", END)
    return graph.compile()


def run_agent(transcript: str, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Run the meeting-analysis graph on a transcript string."""

    agent = build_agent()
    result = agent.invoke({"transcript": transcript, "model": model})
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result["validated_analysis"]


# Public re-export for tests and UI compatibility.
validate_analysis = validate_analysis
