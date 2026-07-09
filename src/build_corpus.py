"""
Construit data/corpus.csv à partir des pages articles de
code.travail.gouv.fr (Code du travail numérique, licence etalab-2.0).

Usage :
    python src/build_corpus.py

Sortie : data/corpus.csv avec les colonnes id,text,source,category,url
(même schéma que le mini-TP : id/text/source/category, pour pouvoir
réutiliser VectorDB tel quel).

NB : ce script fait de vraies requêtes HTTP. Il ne peut pas tourner dans
le sandbox de la conversation (accès réseau restreint) -- lance-le en
local, dans ton venv.
"""

import csv
import time
import sys

import requests
from bs4 import BeautifulSoup

from article_lists import ARTICLES

BASE_URL = "https://code.travail.gouv.fr/code-du-travail/{}"
OUTPUT_PATH = "data/corpus.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (projet-etudiant-M2-RAG)"}


def article_url(article_id: str) -> str:
    # ex: "L3141-19-1" -> "l3141-19-1"
    return BASE_URL.format(article_id.lower())


def fetch_article(article_id: str) -> dict | None:
    """Récupère et parse une page article. Renvoie None si échec."""
    url = article_url(article_id)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException as e:
        print(f"  [ERREUR réseau] {article_id}: {e}")
        return None

    if resp.status_code != 200:
        print(f"  [HTTP {resp.status_code}] {article_id} -- ignoré")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    main = soup.find("main") or soup

    h1 = main.find("h1")
    if h1 is None:
        print(f"  [PAS DE H1] {article_id} -- structure inattendue, à inspecter")
        return None

    # On parcourt les éléments après le h1 jusqu'au premier h2
    # (qui correspond à "Avez-vous trouvé la réponse à votre question ?").
    paragraphs = []
    for sibling in h1.find_all_next():
        if sibling.name == "h2":
            break
        if sibling.name == "p":
            text = sibling.get_text(" ", strip=True)
            if text and not text.lower().startswith("source"):
                paragraphs.append(text)

    if not paragraphs:
        print(f"  [PAS DE TEXTE] {article_id} -- structure inattendue, à inspecter")
        return None

    return {
        "id": article_id,
        "text": " ".join(paragraphs),
        "source": f"Code du travail, article {article_id}",
        "url": url,
    }


def main():
    rows = []
    for category, article_ids in ARTICLES.items():
        print(f"\n== Thème : {category} ({len(article_ids)} articles) ==")
        for article_id in article_ids:
            result = fetch_article(article_id)
            if result:
                result["category"] = category
                rows.append(result)
                print(f"  OK  {article_id}")
            time.sleep(0.5)  # politesse envers le serveur

    if not rows:
        print("Aucun article récupéré -- vérifie la connexion et la structure HTML.")
        sys.exit(1)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "source", "category", "url"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{len(rows)} articles écrits dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
