"""Text formatting via Groq LLM."""

from __future__ import annotations

from voitype.config import CFG
from voitype.groq_client import get_client


def format_dictation(raw_text: str) -> str:
    prompt = CFG.PROMPT_DICTATION.format(text=raw_text)
    try:
        response = get_client().chat.completions.create(
            model=CFG.MODEL_LLM,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )
        result = response.choices[0].message.content
        return result.strip() if result else raw_text
    except Exception as e:
        print(f"Formatting error: {e}")
        return raw_text


def format_rewrite(instruction: str, original: str) -> str:
    prompt = CFG.PROMPT_REWRITE.format(instruction=instruction, original=original)
    try:
        response = get_client().chat.completions.create(
            model=CFG.MODEL_LLM,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )
        result = response.choices[0].message.content
        return result.strip() if result else original
    except Exception as e:
        print(f"Rewrite error: {e}")
        return original
