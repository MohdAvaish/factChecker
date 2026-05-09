"""
web_search.py – Live web search using the Tavily Search API.
"""

import streamlit as st
from tavily import TavilyClient
from typing import List, Dict, Any
import functools

# Simple in-memory cache: query → results
_search_cache: Dict[str, List[Dict[str, Any]]] = {}


def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for evidence related to a claim.

    Results are cached in-memory to avoid redundant API calls within a session.

    Args:
        query: The search query (usually the claim text).
        max_results: Number of top results to retrieve.

    Returns:
        A list of result dicts, each containing at minimum:
            - url (str)
            - content (str)
            - title (str)

    Raises:
        ValueError: If the Tavily API key is not configured.
        RuntimeError: If the search API call fails.
    """
    cache_key = f"{query.strip().lower()}::{max_results}"
    if cache_key in _search_cache:
        return _search_cache[cache_key]

    api_key = st.secrets.get("TAVILY_API_KEY", "")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is not set in .streamlit/secrets.toml")

    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
        )

        results: List[Dict[str, Any]] = response.get("results", [])

        # Normalise: ensure required keys exist
        normalised = []
        for r in results:
            normalised.append(
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0.0),
                }
            )

        _search_cache[cache_key] = normalised
        return normalised

    except Exception as e:
        raise RuntimeError(f"Web search failed for query '{query[:60]}…': {e}") from e
