import chromadb
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME

CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "code_travail"


class LegalSearch:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = client.get_collection(COLLECTION_NAME)

    def search(self, question, n_results=3):
        query_embedding = self.model.encode([question], convert_to_numpy=True)
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
        )

        hits = []
        for i in range(len(results["ids"][0])):
            hits.append(
                {
                    "num": results["metadatas"][0][i]["num"],
                    "texte": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                }
            )
        return hits


if __name__ == "__main__":
    search = LegalSearch()
    question = "Quelle est la durée légale de la période d'essai ?"
    results = search.search(question)

    print(f"Question : {question}\n")
    for r in results:
        print(f"Article {r['num']} (distance: {r['distance']:.3f})")
        print(r["texte"][:300] + "...\n")