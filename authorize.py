import base64
import hashlib
import json
import random
import time
import urllib
import uuid
import webbrowser

import requests
from flask import Flask, request

app = Flask(__name__)
code_verifier = None
state = None


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


@app.get("/callback")
def callback():
    global code_verifier, state

    code = request.args.get("code")
    state_check = request.args.get("state")

    assert state == state_check

    params = {
        "client_id": "divcards2gsheet",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": urllib.parse.quote_plus("http://localhost:8080/callback"),
        "scope": "account:stashes",
        "code_verifier": code_verifier,
    }

    res = requests.post(
        "https://www.pathofexile.com/oauth/token",
        data=params,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
        },
    )

    if res.status_code != 200:
        return f"Error while obtaining token: {res.status_code}"

    data = res.json()

    with open("poe-token.json", "w") as fwrite:
        json.dump(
            {"token": data["access_token"], "expires": int(time.time()) + data["expires_in"]},
            fwrite,
        )

    return "Success"


if __name__ == "__main__":
    code_verifier, state = generate_oath_url()

    app.run(port=8080)
