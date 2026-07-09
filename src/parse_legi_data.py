import json

from config import CODE_TRAVAIL_ID

LEGI_DATA_PATH = "data/LEGITEXT000006072050.json"


def extract_articles(path=LEGI_DATA_PATH):
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
    if len(texte) <= size:
        return [texte]

    words = texte.split(" ")
    chunks = []
    current = []
    current_len = 0

    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= size:
            chunks.append(" ".join(current))
            overlap_words = max(1, overlap // 6) 
            current = current[-overlap_words:]
            current_len = sum(len(w) + 1 for w in current)

    if current:
        chunks.append(" ".join(current))

    return chunks
if __name__ == "__main__":
    articles = extract_articles()
    print(f"{len(articles)} articles extraits")

    with open("articles_code_travail.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print("articles_code_travail.json stocké")