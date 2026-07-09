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
            
        # 2. Appel au RAG 
        try:
            reponse, sources, contexte = rag.answer(question)
        except Exception as e:
            print(f"\n[Erreur Système] Détails techniques : {e}") # <--- Ligne modifiée pour débugger
            print("N'hésite pas à réessayer ta question dans quelques instants.\n")
            continue
            
        valide, raison = moderator.check_answer(question, contexte, reponse)
        if not valide:
            print(f"\n[Réponse invalidée par la modération : {raison}]")
            print("Reformule ta question ou consulte un professionnel.\n")
            continue
            
        print(f"\n{reponse}\n")
        
        if sources:
            print("Sources :", ", ".join(h["num"] for h in sources))
        else:
            print("Sources : Aucune source spécifique n'a pu être identifiée.")
        print()

if __name__ == "__main__":
    run()