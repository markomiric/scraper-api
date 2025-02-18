import base64
import json


def encode_last_key(last_key: dict) -> str:
    """Encode LastEvaluatedKey as a base64 string."""
    return base64.urlsafe_b64encode(json.dumps(last_key).encode()).decode()


def decode_last_key(token: str) -> dict:
    """Decode the base64 string into a LastEvaluatedKey dict."""
    return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
