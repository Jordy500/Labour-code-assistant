"""
Listes d'articles du Code du travail à récupérer, par thème.

Ces IDs viennent des tables des matières Légifrance (LEGITEXT000006072050).
On commence volontairement petit (2 thèmes) pour garder un corpus qu'on
peut lire et vérifier à la main -- cf. le principe du cours : "lisez vos
chunks avant de brancher le LLM".

Pour étendre le corpus plus tard : parcourir la page thème sur
https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072050/...
et ajouter les IDs manquants ici.
"""

ARTICLES = {
    "conges_payes": [
        "L3141-1", "L3141-2",
        "L3141-3", "L3141-4", "L3141-5", "L3141-6", "L3141-7", "L3141-8", "L3141-9",
        "L3141-10", "L3141-11",
        "L3141-12", "L3141-13", "L3141-14",
        "L3141-19-1",
        "L3141-24", "L3141-25", "L3141-26", "L3141-27",
        "L3141-30", "L3141-31",
    ],
    "duree_travail": [
        "L3121-27", "L3121-28", "L3121-29", "L3121-30", "L3121-31",
        "L3121-32", "L3121-33", "L3121-34",
        "L3121-35", "L3121-36", "L3121-37", "L3121-38", "L3121-39", "L3121-40",
        "L3121-48", "L3121-49", "L3121-50",
    ],
}
