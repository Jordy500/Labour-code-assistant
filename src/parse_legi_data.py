"""
Parse l'arbre unist de legi-data pour en extraire une liste plate
d'articles du Code du travail (numéro + texte), utilisable pour
l'indexation dans ChromaDB.
"""

import json

from config import CODE_TRAVAIL_ID

LEGI_DATA_PATH = "data/LEGITEXT000006072050.json"


def extract_articles(path=LEGI_DATA_PATH):
    """Renvoie une liste de dicts {num, id, texte} pour chaque article en vigueur."""
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)

    articles = []

    def walk(node):
        if node.get("type") == "article":
            data = node["data"]
            if data.get("etat") == "VIGUEUR" and data.get("texte"):
                articles.append(
                    {
                        "num": data.get("num"),
                        "id": data.get("id"),
                        "texte": data.get("texte"),
                    }
                )
        for child in node.get("children", []):
            walk(child)

    walk(tree)
    return articles

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def chunk_text(texte, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Découpe un texte long en morceaux avec chevauchement.

    Si le texte est plus court que `size`, renvoie une liste à un seul élément.
    """
    if len(texte) <= size:
        return [texte]

    chunks = []
    start = 0
    while start < len(texte):
        end = start + size
        chunks.append(texte[start:end])
        start += size - overlap
    return chunks


def build_chunks(articles):
    """Transforme la liste d'articles en liste de chunks indexables.

    Chaque chunk garde une trace de l'article d'origine (num, id) et
    de sa position (chunk_index / total_chunks) pour reconstituer le
    contexte complet si besoin.
    """
    chunks = []
    for article in articles:
        pieces = chunk_text(article["texte"])
        for i, piece in enumerate(pieces):
            chunks.append(
                {
                    "chunk_id": f"{article['id']}_{i}",
                    "article_id": article["id"],
                    "num": article["num"],
                    "chunk_index": i,
                    "total_chunks": len(pieces),
                    "texte": piece,
                }
            )
    return chunks
if __name__ == "__main__":
    articles = extract_articles()
    print(f"{len(articles)} articles extraits")

    chunks = build_chunks(articles)
    print(f"{len(chunks)} chunks générés")

    with open("chunks_code_travail.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print("Sauvegardé dans chunks_code_travail.json")