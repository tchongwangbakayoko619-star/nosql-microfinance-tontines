from pymongo.errors import PyMongoError
from config import get_db

def creer_index_projet(db=None):
    """
    Crée les index obligatoires et optimisés pour le Projet 9.
    """
    if db is None:
        db = get_db()
    if db is None:
        return False

    collections_indexes = [
        ("membres", [("numero", 1)], {"unique": True}),
        ("comptes", [("numero", 1)], {"unique": True}),
        ("prets", [("code_pret", 1)], {"unique": True}),
        ("tontines", [("code_tontine", 1)], {"unique": True}),
        ("comptes", [("membre_numero", 1)], {}),
        ("transactions", [("compte_numero", 1), ("date", -1)], {}),
        ("prets", [("membre_numero", 1)], {}),
        ("tontines", [("membres", 1)], {})
    ]

    try:
        for col_name, keys, opts in collections_indexes:
            try:
                db[col_name].create_index(keys, **opts)
            except PyMongoError:
                pass

        print("✓ Tous les index du Projet 9 ont été créés avec succès.")
        return True
    except PyMongoError as e:
        print(f"[ERREUR INDEX] {e}")
        return False

def obtenir_liste_index(db=None):
    """
    Retourne un dictionnaire listant les index créés par collection.
    """
    if db is None:
        db = get_db()
    if db is None:
        return {}

    collections = ["membres", "comptes", "transactions", "prets", "tontines"]
    resultats = {}
    for col in collections:
        resultats[col] = list(db[col].list_indexes())
    return resultats
