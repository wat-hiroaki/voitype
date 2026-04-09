"""Groq API client initialization."""

from __future__ import annotations

import os
import sys

from groq import Groq

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print(
                "ERROR: GROQ_API_KEY environment variable is not set.\n"
                "Get your free API key at https://console.groq.com/keys\n"
                "Then run: GROQ_API_KEY=your_key voitype",
                file=sys.stderr,
            )
            sys.exit(1)
        _client = Groq(api_key=api_key)
    return _client
