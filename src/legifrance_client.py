import os
import time
import json
from typing import Dict, Any, Optional, List
import requests
from dotenv import load_dotenv

from config import OAUTH_TOKEN_URL, API_BASE_URL

load_dotenv()

class LegifranceAPIError(Exception):
    pass


class LegifranceClient:
    def __init__(self) -> None:
        self.client_id: Optional[str] = os.getenv("LEGIFRANCE_CLIENT_ID")
        self.client_secret: Optional[str] = os.getenv("LEGIFRANCE_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Initialisation impossible : Variables d'environnement "
                "LEGIFRANCE_CLIENT_ID ou LEGIFRANCE_CLIENT_SECRET manquantes."
            )

        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self.http_session = requests.Session()

    def _refresh_oauth_token(self) -> str:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid",
        }
        try:
            response = self.http_session.post(OAUTH_TOKEN_URL, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self._token = data["access_token"]
            self._token_expires_at = time.time() + float(data["expires_in"])
            return self._token
        except requests.RequestException as e:
            raise LegifranceAPIError(f"Échec de l'authentification OAuth2 : {e}")

    def _get_valid_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        return self._refresh_oauth_token()

    def _get_default_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_valid_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _extract_id_art_recursive(self, data: Any) -> Optional[str]:
        if isinstance(data, str) and data.startswith("LEGIARTI"):
            return data
        
        if isinstance(data, dict):
            for key in ("id", "cid", "idArticle"):
                val = data.get(key)
                if isinstance(val, str) and val.startswith("LEGIARTI"):
                    return val
            for value in data.values():
                found = self._extract_id_art_recursive(value)
                if found:
                    return found
                    
        elif isinstance(data, list):
            for item in data:
                found = self._extract_id_art_recursive(item)
                if found:
                    return found
                    
        return None

    def search_article(self, num_article: str) -> Optional[str]:
        payload = {
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "ALL",
                        "criteres": [
                            {"typeRecherche": "EXACTE", "valeur": num_article, "operateur": "ET"}
                        ],
                        "operateur": "ET"
                    }
                ],
                "filtres": [
                    {"facette": "NOM_CODE", "valeurs": ["Code du travail"]}
                ],
                "pageNumber": 1,
                "pageSize": 5,
                "sort": "PERTINENCE",
                "typePagination": "DEFAUT",
                "operateur": "ET"
            },
            "fond": "CODE_DATE"
        }
        
        try:
            response = self.http_session.post(
                f"{API_BASE_URL}/search", 
                json=payload, 
                headers=self._get_default_headers(),
                timeout=15
            )
            response.raise_for_status()
            response_data = response.json()
            
            results: List[Dict[str, Any]] = response_data.get("results", [])
            if not results:
                # Fallback : Analyse de la racine si l'API omet le wrapper global
                return self._extract_id_art_recursive(response_data)
                
            return self._extract_id_art_recursive(results[0])

        except requests.RequestException as e:
            raise LegifranceAPIError(f"Anomalie lors de l'appel au service d'indexation: {e}")

    def get_article_content(self, legiarti_id: str) -> Dict[str, Any]:
        if not legiarti_id.startswith("LEGIARTI"):
            raise ValueError(
                f"Contrainte d'intégrité violée : format LEGIARTI requis (reçu: '{legiarti_id}')."
            )

        payload = {"id": legiarti_id}
        
        try:
            response = self.http_session.post(
                f"{API_BASE_URL}/consult/getArticle", 
                json=payload, 
                headers=self._get_default_headers(),
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LegifranceAPIError(f"Impossible de récupérer le contenu de la ressource {legiarti_id}: {e}")


if __name__ == "__main__":
    client = LegifranceClient()