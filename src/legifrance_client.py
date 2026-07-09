import os
import time

import requests
from dotenv import load_dotenv

from config import OAUTH_TOKEN_URL

load_dotenv()


class LegifranceClient:
    def __init__(self):
        self.client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
        self.client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "LEGIFRANCE_CLIENT_ID / LEGIFRANCE_CLIENT_SECRET manquants dans .env"
            )

        self._token = None
        self._token_expires_at = 0  # timestamp unix

    def _get_token(self):
        """Renvoie un token valide, en le renouvelant si besoin.

        Le token PISTE dure 1h (expires_in dans la réponse). On garde
        une marge de 60s pour ne pas se faire surprendre par l'expiration
        pile au milieu d'une requête.
        """
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        response = requests.post(
            OAUTH_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "openid",
            },
        )
        response.raise_for_status()
        data = response.json()

        self._token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"]
        return self._token


if __name__ == "__main__":
    # test rapide : si ça affiche un token, l'auth fonctionne
    client = LegifranceClient()
    print(client._get_token()[:20] + "...")