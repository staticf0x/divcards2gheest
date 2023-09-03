import json

import requests


class BearerAuth(requests.auth.AuthBase):
    def __init__(self):
        with open("poe-token.json") as fread:
            data = json.load(fread)
            self.token = data["token"]

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r
