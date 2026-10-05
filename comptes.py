from datetime import datetime
from pymongo.errors import PyMongoError, DuplicateKeyError
from database import get_db

TYPES_AUTORISES = ["epargne", "courant"]
STATUTS_AUTORISES = ["actif", "cloture"]

def creer_compte(numero, membre, type_compte, solde=0, date_ouverture=None, statut="actif"):
    """
    Crée un nouveau compte bancaire pour un membre existant.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    if type_compte not in TYPES_AUTORISES:
        print(f"❌ Type de compte invalide. Types autorisés : {TYPES_AUTORISES}")
        return None

    if solde < 0:
        print("❌ Montant invalide (le solde initial ne peut pas être négatif).")
        return None

    # Vérification de l'existence du membre
    membre_doc = db.membres.find_one({"numero": membre})
    if not membre_doc:
        print(f"❌ Membre introuvable ('{membre}').")
        return None

    if date_ouverture is None:
        date_ouverture = datetime.now().strftime("%Y-%m-%d")
    elif isinstance(date_ouverture, datetime):
        date_ouverture = date_ouverture.strftime("%Y-%m-%d")

    doc = {
        "numero": numero,
        "membre": membre,
        "type": type_compte,
        "solde": float(solde),
        "date_ouverture": date_ouverture,
        "statut": statut
    }

    try:
        db.comptes.insert_one(doc)
        print(f"✓ Opération effectuée avec succès. Compte {numero} créé pour le membre {membre}.")
        return doc
    except DuplicateKeyError:
        print(f"❌ Numéro de compte '{numero}' existe déjà.")
        return None
    except PyMongoError:
        print("❌ Erreur lors de la création du compte.")
        return None

def obtenir_compte(numero):
    """
    Recherche un compte par son numéro unique.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    try:
        compte = db.comptes.find_one({"numero": numero})
        if not compte:
            print("❌ Compte introuvable.")
            return None
        return compte
    except PyMongoError:
        print("❌ Erreur lors de la recherche du compte.")
        return None

def lister_comptes_membre(numero_membre):
    """
    Liste tous les comptes associés à un membre donné.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.comptes.find({"membre": numero_membre}, {"_id": 0}))
    except PyMongoError:
        print("❌ Erreur lors de la recherche des comptes du membre.")
        return []

def lister_comptes_par_type(type_compte):
    """
    Liste tous les comptes filtrés par type ('epargne' ou 'courant').
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.comptes.find({"type": type_compte}, {"_id": 0}))
    except PyMongoError:
        print("❌ Erreur lors de la liste des comptes par type.")
        return []

def cloturer_compte(numero_compte):
    """
    Clôture un compte si son solde est exactement égal à zéro.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    try:
        compte = db.comptes.find_one({"numero": numero_compte})
        if not compte:
            print("❌ Compte introuvable.")
            return False

        if compte.get("solde", 0) != 0:
            print("❌ Impossible de clôturer le compte : solde non nul.")
            return False

        res = db.comptes.update_one(
            {"numero": numero_compte},
            {"$set": {"statut": "cloture"}}
        )
        print("✓ Opération effectuée avec succès.")
        return True
    except PyMongoError:
        print("❌ Erreur lors de la clôture du compte.")
        return False
