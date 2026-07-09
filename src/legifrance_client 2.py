import os
import time
import json

import requests
from dotenv import load_dotenv

from config import CODE_TRAVAIL_ID, OAUTH_TOKEN_URL, API_BASE_URL

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
        """Renvoie un token valide, en le renouvelant si besoin."""
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

    def _headers(self):
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    def search_article(self, num_article):
        """Cherche un article par son numéro (ex: 'L1221-1') dans le Code du travail.

        Renvoie l'id LEGIARTI du premier résultat, ou None si rien trouvé.
        """
        payload = {
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "NUM_ARTICLE",
                        "criteres": [
                            {"typeRecherche": "EXACTE", "valeur": num_article, "operateur": "ET"}
                        ],
                        "operateur": "ET",
                    }
                ],
                "filtres": [{"facette": "NOM_CODE", "valeurs": ["Code du travail"]}],
                "pageNumber": 1,
                "pageSize": 5,
                "operateur": "ET",
                "sort": "PERTINENCE",
                "typePagination": "DEFAUT",
            },
            "fond": "CODE_DATE",
        }
        response = requests.post(f"{API_BASE_URL}/search", json=payload, headers=self._headers())
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return None
        return results[0]["titles"][0]["id"]

    def get_article_content(self, legiarti_id):
        """Récupère le contenu complet d'un article via son id LEGIARTI."""
        payload = {"id": legiarti_id}
        response = requests.post(
            f"{API_BASE_URL}/consult/getArticle", json=payload, headers=self._headers()
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    client = LegifranceClient()
    legiarti_id = client.search_article("L1221-1")
    print("LEGIARTI ID:", legiarti_id)

    if legiarti_id:
        article = client.get_article_content(legiarti_id)
        with open("test_article.json", "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        print("Article sauvegardé dans test_article.json")