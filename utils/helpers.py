"""
helpers.py – Shared utility functions for the Fact-Check Agent.
"""

from typing import Dict, Any


VERDICT_CONFIG: Dict[str, Dict[str, str]] = {
    "Verified": {
        "icon": "✅",
        "badge_class": "badge-verified",
        "color": "#4ade80",
    },
    "Inaccurate": {
        "icon": "⚠️",
        "badge_class": "badge-inaccurate",
        "color": "#fbbf24",
    },
    "False": {
        "icon": "❌",
        "badge_class": "badge-false",
        "color": "#f87171",
    },
    "Not Enough Evidence": {
        "icon": "❓",
        "badge_class": "badge-nee",
        "color": "#60a5fa",
    },
}


def get_verdict_config(status: str) -> Dict[str, str]:
    """
    Return display configuration for a given verdict status.

    Args:
        status: One of "Verified", "Inaccurate", "False", "Not Enough Evidence".

    Returns:
        Dict with keys: icon, badge_class, color.
    """
    return VERDICT_CONFIG.get(status, VERDICT_CONFIG["Not Enough Evidence"])


def truncate_text(text: str, max_length: int = 300) -> str:
    """
    Truncate text to a maximum length, appending ellipsis if truncated.

    Args:
        text: Input text.
        max_length: Maximum character length.

    Returns:
        Truncated (or original) string.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "…"
