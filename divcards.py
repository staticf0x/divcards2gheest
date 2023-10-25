import json
import time
import urllib

import requests
from flask import Flask, redirect, render_template, request, send_from_directory

from divcards.api import PoEApi
from divcards.utils import generate_oath_url, token_valid

app = Flask("divcards")
code_verifier = None
state = None


@app.get("/callback")
def callback():
    global code_verifier, state

    if token_valid():
        return redirect("/divcards")

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

    return redirect("/divcards")


@app.route("/static/<path:path>")
def static_files(path: str):
    return send_from_directory("static", path)


@app.get("/divcards")
def list_stashes():
    api = PoEApi()

    stashes = api.stashes()

    return render_template("divcards.html", stashes=stashes)


@app.get("/divcards/<stash_id>")
def show_stash(stash_id: str):
    api = PoEApi()

    stash = api.stash(stash_id)
    items = [(item["typeLine"], item.get("stackSize", 1)) for item in stash["items"]]
    items = sorted(items, key=lambda x: x[1], reverse=True)

    return render_template("stash.html", items=items)


if __name__ == "__main__":
    if not token_valid():
        code_verifier, state = generate_oath_url()

    app.run(port=8080)
