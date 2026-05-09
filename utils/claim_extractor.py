"""
claim_extractor.py – Use DeepSeek via OpenRouter
"""

import json
import re
import streamlit as st
from openai import OpenAI
from typing import List

# OpenRouter DeepSeek model
MODEL = "deepseek/deepseek-chat"

SYSTEM_PROMPT = """You are a precise fact-checking assistant.
Your task is to extract ONLY verifiable factual claims from the provided text.

A verifiable factual claim must contain at least one of:
- Specific percentages
- Exact dates or years
- Financial figures
- Statistical data
- User/customer counts
- Technical measurements

Return ONLY a valid JSON array of strings.
"""


def _parse_json_claims(raw: str) -> List[str]:

    raw = raw.strip()

    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(c) for c in parsed if c]
    except:
        pass

    return []


def extract_claims(text: str, max_chars: int = 12000) -> List[str]:

    api_key = st.secrets.get("OPENROUTER_API_KEY", "")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY missing in secrets.toml"
        )

    # OpenRouter client
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    truncated_text = text[:max_chars]

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content":
                        "Extract all factual claims:\n\n"
                        + truncated_text
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )

        raw_content = response.choices[0].message.content or "[]"

        return _parse_json_claims(raw_content)

    except Exception as e:
        raise RuntimeError(
            f"DeepSeek/OpenRouter extraction failed: {e}"
        ) from e