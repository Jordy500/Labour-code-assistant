import json

import chromadb
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME

CHUNKS_PATH = "chunks_code_travail.json"
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "code_travail"

BATCH_SIZE = 64


def load_chunks(path=CHUNKS_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_index():
    chunks = load_chunks()
    print(f"{len(chunks)} chunks à indexer")

    print(f"Chargement du modèle {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
    COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
)

    texts = [c["texte"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {"num": c["num"], "article_id": c["article_id"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    print("Génération des embeddings ...")
    embeddings = model.encode(
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

    print(f"Index construit : {collection.count()} chunks indexés dans '{COLLECTION_NAME}'")


if __name__ == "__main__":
    build_index()