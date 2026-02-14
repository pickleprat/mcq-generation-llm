import json
import re

def extract_list(raw: str) -> list:
    match = re.search(r'\[.*?\]', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in model output.")

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON array: {e}")

    if not isinstance(parsed, list):
        raise ValueError("Parsed JSON is not a list.")

    return parsed

def extract_json(raw: str):
    match = re.search(r'(\{.*\}|\[.*\])', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output.")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")