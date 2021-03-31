import requests
import json
import base64


# Configuration for using Dining Hall API
class Configs:
    def __init__(self):
        self.CONSUMER_KEY = "KPYMe2FTDdpk9Lo3Q0FLWPWCjwsa"
        self.CONSUMER_SECRET = "ONBGvpgskS6EKutumvlTf_kh56Ua"
        self.BASE_URL = "https://api.princeton.edu:443/mobile-app/1.0.0"
        self.DINING_MENU = "/dining/menu"
        self.REFRESH_TOKEN_URL = "https://api.princeton.edu:443/token"
        self._refreshToken(grant_type="client_credentials")

    def _refreshToken(self, **kwargs):
        req = requests.post(
            self.REFRESH_TOKEN_URL,
            data=kwargs,
            headers={
                "Authorization": "Basic " + base64.b64encode(bytes(self.CONSUMER_KEY + ":" + self.CONSUMER_SECRET, "utf-8")).decode("utf-8")
            },
        )
        text = req.text
        response = json.loads(text)
        self.ACCESS_TOKEN = response["access_token"]
