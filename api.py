import json
import tomllib

import requests


class BearerAuth(requests.auth.AuthBase):
    def __init__(self):
        with open("poe-token.json") as fread:
            data = json.load(fread)
            self.token = data["token"]

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class PoEApi:
    def __init__(self):
        self.auth = BearerAuth()
        self.url = "https://api.pathofexile.com"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
        }

    def get(self, url: str):
        if not url.startswith("/"):
            url = f"/{url}"

        url = url.removesuffix("/")

        return requests.get(f"{self.url}{url}", headers=self.headers, auth=self.auth)

    def stashes(self):
        res = api.get("/stash/standard")
        stashes = res.json()["stashes"]

        return stashes

    def stash(self, stash_id: str):
        res = api.get(f"/stash/standard/{stash_id}")

        return res.json()["stash"]


api = PoEApi()

with open("config.toml", "rb") as fread:
    config = tomllib.load(fread)

print("Fetching account stashes...")

for stash in api.stashes():
    if stash["name"] == config["stash"]["name"]:
        stash_id = stash["id"]
        print(f"Found stash '{stash['name']}' (ID: {stash_id})")
        break

stash = api.stash(stash_id)

cards = []

for item in stash["items"]:
    name = item["typeLine"]
    count = item["stackSize"]

    cards.append((name, count))

for card, count in sorted(cards, key=lambda x: x[1], reverse=True):
    print(f"{card:30s} {count:4d}")
