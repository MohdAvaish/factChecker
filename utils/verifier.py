"""
verifier.py – Compare claims against live web evidence using DeepSeek R1 via OpenRouter.
"""

import json
import re
import streamlit as st
from openai import OpenAI
from typing import List, Dict, Any

# Recommended reasoning model
MODEL = "deepseek/deepseek-r1"

VALID_STATUSES = {
    "Verified",
    "Inaccurate",
    "False",
    "Not Enough Evidence"
}

SYSTEM_PROMPT = """You are an expert fact-checker with access to web evidence.

Given a factual claim and a set of web search results, your job is to:

1. Carefully read the evidence.
2. Determine whether the claim is correct, inaccurate, false, or unverifiable.
3. Provide the corrected fact if the claim is wrong.
4. Cite the relevant source URLs from the evidence.

Classification rules:

- "Verified":
  The claim is confirmed by credible sources.

- "Inaccurate":
  The claim is partially correct but contains errors.

- "False":
  The claim is contradicted by credible sources.

- "Not Enough Evidence":
  The evidence is insufficient or contradictory.

You MUST respond ONLY with a valid JSON object.

Format:

{
  "status": "Verified | Inaccurate | False | Not Enough Evidence",
  "correct_fact": "Corrected fact",
  "explanation": "Short explanation",
  "sources": ["url1", "url2"]
}
"""


def _build_evidence_block(
    search_results: List[Dict[str, Any]]
) -> str:
    """
    Convert search results into readable evidence text.
    """

    if not search_results:
        return "No web evidence available."

    parts = []

    for i, r in enumerate(search_results, 1):

        snippet = r.get("content", "")[:800]

        parts.append(
            f"[Source {i}]\n"
            f"Title: {r.get('title', 'Untitled')}\n"
            f"URL: {r.get('url', '')}\n"
            f"Excerpt: {snippet}"
        )

    return "\n\n".join(parts)


def _parse_verification(
    raw: str,
    source_urls: List[str]
) -> Dict[str, Any]:
    """
    Parse model JSON safely.
    """

    raw = raw.strip()

    # Remove markdown fences
    raw = re.sub(
        r"^```(?:json)?\s*",
        "",
        raw,
        flags=re.IGNORECASE
    )

    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)

    except json.JSONDecodeError:

        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if match:
            try:
                parsed = json.loads(match.group())
            except:
                parsed = {}
        else:
            parsed = {}

    status = parsed.get(
        "status",
        "Not Enough Evidence"
    )

    if status not in VALID_STATUSES:
        status = "Not Enough Evidence"

    correct_fact = parsed.get(
        "correct_fact",
        "Unable to determine."
    )

    explanation = parsed.get(
        "explanation",
        "Verification failed."
    )

    raw_sources = parsed.get("sources", [])

    if isinstance(raw_sources, list):
        sources = [
            s for s in raw_sources
            if isinstance(s, str)
            and s.startswith("http")
        ]
    else:
        sources = []

    # Fallback sources
    if not sources:
        sources = source_urls[:3]

    return {
        "status": status,
        "correct_fact": correct_fact,
        "explanation": explanation,
        "sources": sources,
    }


def verify_claim(
    claim: str,
    search_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Verify a claim using DeepSeek R1 via OpenRouter.
    """

    api_key = st.secrets.get(
        "OPENROUTER_API_KEY",
        ""
    )

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY missing in secrets.toml"
        )

    # OpenRouter client
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    evidence_block = _build_evidence_block(
        search_results
    )

    source_urls = [
        r.get("url", "")
        for r in search_results
        if r.get("url")
    ]

    user_message = (
        f"Claim:\n{claim}\n\n"
        f"Evidence:\n{evidence_block}"
    )

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
                    "content": user_message
                }
            ],
            temperature=0.1,
            max_tokens=800
        )

        raw_content = (
            response.choices[0]
            .message.content
            or "{}"
        )

        return _parse_verification(
            raw_content,
            source_urls
        )

    except Exception as e:

        return {
            "status": "Not Enough Evidence",
            "correct_fact": "Verification failed.",
            "explanation": (
                f"Verification error: {e}"
            ),
            "sources": source_urls[:2],
        }