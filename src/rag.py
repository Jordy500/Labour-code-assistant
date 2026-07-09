import os

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_MODEL_NAME
from vector_db import VectorDB

load_dotenv()


PROMPT_TEMPLATE = """Tu es un assistant juridique spécialisé dans le droit du travail français.
Réponds à la question en te basant UNIQUEMENT sur les extraits du Code du travail fournis ci-dessous.
Si les extraits ne permettent pas de répondre, dis-le clairement plutôt que d'inventer une réponse.
Cite toujours le(s) numéro(s) d'article sur lesquels tu t'appuies.

Extraits du Code du travail :
{contexte}

Question : {question}

Réponse :"""


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
        return response.choices[0].message.content, hits


if __name__ == "__main__":
    rag = RAG()
    question = "Quelle est la durée légale de la période d'essai ?"
    reponse, sources = rag.answer(question)

    print(f"Question : {question}\n")
    print(f"Réponse :\n{reponse}\n")
    print("Sources utilisées :", ", ".join(h["num"] for h in sources))