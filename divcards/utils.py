import base64
import hashlib
import json
import os
import random
import time
import urllib
import uuid
import webbrowser


def token_valid() -> bool:
    """Return True if there is a valid OAuth token."""
    if not os.path.exists("poe-token.json"):
        return False

    with open("poe-token.json") as fread:
        data = json.load(fread)

    return time.time() <= data["expires"]


def base64_url_encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii").replace("+", "-").replace("/", "_").rstrip("=")


def generate_oath_url():
    secret = random.randbytes(32)
    code_verifier = base64_url_encode(secret)
    code_challenge = base64_url_encode(hashlib.sha256(code_verifier.encode("ascii")).digest())
    state = str(uuid.uuid4())

    params = {
        "client_id": "divcards2gsheet",
        "response_type": "code",
        "scope": "account:stashes",
        "state": state,
        "redirect_uri": urllib.parse.quote_plus("http://localhost:8080/callback"),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    params_str = "&".join(f"{k}={v}" for k, v in params.items())

    oauth_url = f"https://www.pathofexile.com/oauth/authorize?{params_str}"

    webbrowser.open_new_tab(oauth_url)

    return code_verifier, state
