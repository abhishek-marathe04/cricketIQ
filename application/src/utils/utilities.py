import json
import re

def extract_json_from_response(response: str) -> dict | None:
    """
    Extracts the last valid JSON object from a response string, ignoring other explanation text.
    This method ensures no accidental changes to the valid JSON block.
    """
    # Clean up the response by removing explanation text and extra whitespace
    cleaned = re.sub(r"^.*?Query:.*?\n", "", response, flags=re.DOTALL).strip()

    # Match JSON-like blocks without altering them
    json_candidates = re.findall(r'\{[\s\S]*\}', cleaned)

    if not json_candidates:
        print("No JSON found.")
        return None

    # Use the last valid JSON block
    json_data = json_candidates[-1]

    # Print the raw JSON for debugging
    print("Raw extracted JSON:")
    print(json_data)

    # Attempt to parse the cleaned-up JSON string
    try:
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Failed JSON: {json_data}")  # Print the problematic JSON for inspection
        return None
    