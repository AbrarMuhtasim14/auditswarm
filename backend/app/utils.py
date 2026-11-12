import re
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def repair_json_string(s: str) -> Optional[Any]:
    """Attempt basic repairs on truncated JSON (e.g. unclosed strings/brackets)."""
    s = s.strip()
    if not s:
        return None

    # If string is an array of objects like [ { ... }, { ... incomplete ...
    if s.startswith("["):
        last_brace = s.rfind("}")
        if last_brace != -1:
            candidate = s[:last_brace + 1].strip().rstrip(",") + "]"
            try:
                return json.loads(candidate)
            except Exception:
                pass

    # Check unclosed quotes
    quote_count = 0
    in_escape = False
    for char in s:
        if char == '\\':
            in_escape = not in_escape
            continue
        if char == '"' and not in_escape:
            quote_count += 1
        in_escape = False

    if quote_count % 2 != 0:
        s += '"'

    # Balance brackets and braces
    open_brackets = s.count("[") - s.count("]")
    open_braces = s.count("{") - s.count("}")

    # Remove trailing commas
    s = re.sub(r',\s*$', '', s)

    # Close open braces and brackets
    s += "}" * max(0, open_braces)
    s += "]" * max(0, open_brackets)

    try:
        return json.loads(s)
    except Exception:
        # Try trimming back to last closing brace
        last_brace = s.rfind("}")
        if last_brace > 0:
            truncated = s[:last_brace + 1].strip().rstrip(",")
            if s.startswith("[") and not truncated.endswith("]"):
                truncated += "]"
            try:
                return json.loads(truncated)
            except Exception:
                return None
        return None

def clean_and_extract_json(text: str) -> Optional[Any]:
    """
    Extract and parse JSON from LLM response, stripping reasoning tokens,
    markdown code blocks, or extra text.
    """
    if not text:
        return None

    cleaned = text.strip()

    # Look for ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    else:
        # Look for first { or [ to last } or ]
        first_brace = cleaned.find("{")
        first_bracket = cleaned.find("[")

        start_idx = -1
        if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
            start_idx = first_brace
        elif first_bracket != -1:
            start_idx = first_bracket

        if start_idx != -1:
            cleaned = cleaned[start_idx:]

    try:
        return json.loads(cleaned)
    except Exception as e:
        # Try repairing truncated JSON
        repaired = repair_json_string(cleaned)
        if repaired is not None:
            return repaired
        logger.warning(f"Failed to parse JSON: {e}\nRaw snippet: {cleaned[:200]}")
        return None
