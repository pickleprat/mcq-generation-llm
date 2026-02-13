import re 

def extract_list(raw: str) -> list: 
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON array found in model output.")
    return match.group(0)

