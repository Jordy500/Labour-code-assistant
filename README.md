# Assistant Code du travail — Projet final RAG (M2 MD5)

RAG sur un corpus réel : articles du Code du travail, thèmes congés payés
et durée légale du travail. Architecture héritée du mini-TP guidé
(ChromaDB + sentence-transformers + Groq + agent modérateur), adaptée à
un vrai corpus juridique avec citations d'articles.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # puis remplir GROQ_API_KEY (console.groq.com)
```

## Construire le corpus

```bash
cd src
python build_corpus.py
```

Récupère les articles listés dans `article_lists.py` depuis
code.travail.gouv.fr (licence etalab-2.0) et écrit `data/corpus.csv`
(colonnes : id, text, source, category, url).

## Statut

- [x] Scraper corpus (congés payés + durée du travail)
- [ ] VectorDB (indexation + rechargement)
- [ ] Agent modérateur
- [ ] RAG (prompt à trous + citations)
- [ ] Jeu de questions de test
