import json

import chromadb
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME

CHUNKS_PATH = "chunks_code_travail.json"
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "code_travail"
BATCH_SIZE = 64


class VectorDB:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    def _get_or_none(self):
        try:
            return self.client.get_collection(COLLECTION_NAME)
        except Exception:
            return None

    def build_index(self, chunks_path=CHUNKS_PATH):
        with open(chunks_path, encoding="utf-8") as f:
            chunks = json.load(f)
        print(f"{len(chunks)} chunks à indexer")

        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        collection = self.client.create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

        texts = [c["texte"] for c in chunks]
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [
            {"num": c["num"], "article_id": c["article_id"], "chunk_index": c["chunk_index"]}
            for c in chunks
        ]

        print("Génération des embeddings...")
        embeddings = self.model.encode(
            texts, batch_size=BATCH_SIZE, show_progress_bar=True, convert_to_numpy=True
        )

        print("Indexation dans ChromaDB...")
        for start in range(0, len(ids), BATCH_SIZE):
            end = start + BATCH_SIZE
            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end].tolist(),
                documents=texts[start:end],
                metadatas=metadatas[start:end],
            )

        print(f"Index construit : {collection.count()} chunks indexés")
        return collection

    def search(self, question, n_results=5):
        collection = self._get_or_none()
        if collection is None:
            raise RuntimeError(
            )

        query_embedding = self.model.encode([question], convert_to_numpy=True)
        results = collection.query(
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
    db = VectorDB()
    db.build_index()