"""Typed state objects for the local LangGraph-style meeting workflow.

This project intentionally keeps the state shape lightweight because the
workflow is a single passage from transcript to extracted structured JSON.
"""

from typing import TypedDict, Any


class MeetingState(TypedDict, total=False):
    """State passed between transcript analysis and validation stages."""

    transcript: str
    raw_analysis: dict[str, Any]
    validated_analysis: dict[str, Any]
    model: str
    error: str
