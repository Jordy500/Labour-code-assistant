import os

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_MODEL_NAME
from vector_db import VectorDB

load_dotenv()

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

with open(os.path.join(PROMPTS_DIR, "rag_system_prompt.txt"), encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read().strip()

class RAG:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.vector_db = VectorDB()

    def answer(self, question, n_results=5):
        hits = self.vector_db.search(question, n_results=n_results)

        contexte = "\n\n".join(f"Article {h['num']} :\n{h['texte']}" for h in hits)
        prompt = PROMPT_TEMPLATE.format(contexte=contexte, question=question)

        response = self.groq_client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content, hits, contexte


if __name__ == "__main__":
    rag = RAG()