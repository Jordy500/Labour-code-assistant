from moderator import Moderator
from rag import RAG


def run():
    print("=== Assistant juridique - Code du travail ===")
    print("Pose ta question (ou tape 'quit' pour arrêter)\n")

    moderator = Moderator()
    rag = RAG()

    while True:
        question = input("> ").strip()
        if question.lower() in ("quit", "exit"):
            print("À bientôt.")
            break
        if not question:
            continue

        autorisee, raison = moderator.check_question(question)
        if not autorisee:
            print(f"\n[Question refusée] {raison}\n")
            continue

        reponse, sources = rag.answer(question)
        contexte = "\n\n".join(f"Article {h['num']} :\n{h['texte']}" for h in sources)

        valide, raison = moderator.check_answer(question, contexte, reponse)
        if not valide:
            print(f"\n[Réponse invalidée par la modération : {raison}]")
            print("Reformule ta question ou consulte un professionnel.\n")
            continue

        print(f"\n{reponse}\n")
        print("Sources :", ", ".join(h["num"] for h in sources))
        print()


if __name__ == "__main__":
    run()