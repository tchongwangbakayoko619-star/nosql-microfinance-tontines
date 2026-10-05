from datetime import datetime
from pymongo.errors import PyMongoError, DuplicateKeyError
from database import get_db

def creer_membre(numero, nom, telephone, profession, ville, piece_identite, date_adhesion=None):
    """
    Crée un nouveau membre dans la collection 'membres'.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    if date_adhesion is None:
        date_adhesion = datetime.now().strftime("%Y-%m-%d")
    elif isinstance(date_adhesion, datetime):
        date_adhesion = date_adhesion.strftime("%Y-%m-%d")

    doc = {
        "numero": numero,
        "nom": nom,
        "telephone": telephone,
        "profession": profession,
        "ville": ville,
        "date_adhesion": date_adhesion,
        "piece_identite": piece_identite
    }

    try:
        res = db.membres.insert_one(doc)
        print(f"✓ Opération effectuée avec succès. Membre {numero} créé.")
        return doc
    except DuplicateKeyError:
        print(f"❌ Numéro de membre '{numero}' existe déjà.")
        return None
    except PyMongoError as e:
        print("❌ Erreur lors de la création du membre.")
        return None

def obtenir_membre(numero):
    """
    Recherche un membre par son numéro unique.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    try:
        membre = db.membres.find_one({"numero": numero})
        if not membre:
            print("❌ Membre introuvable.")
            return None
        return membre
    except PyMongoError:
        print("❌ Erreur lors de la recherche du membre.")
        return None

def lister_membres(limite=50):
    """
    Liste les membres inscrits avec une limite par défaut.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.membres.find({}, {"_id": 0}).limit(limite))
    except PyMongoError:
        print("❌ Erreur lors de la récupération de la liste des membres.")
        return []

def rechercher_par_ville(ville):
    """
    Recherche tous les membres résidant dans une ville donnée.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.membres.find({"ville": ville}, {"_id": 0}))
    except PyMongoError:
        print("❌ Erreur lors de la recherche par ville.")
        return []

def rechercher_par_profession(profession):
    """
    Recherche tous les membres ayant une profession donnée.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.membres.find({"profession": profession}, {"_id": 0}))
    except PyMongoError:
        print("❌ Erreur lors de la recherche par profession.")
        return []

def modifier_membre(numero, telephone=None, profession=None, ville=None):
    """
    Modifie les informations autorisées d'un membre (téléphone, profession, ville).
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    update_fields = {}
    if telephone:
        update_fields["telephone"] = telephone
    if profession:
        update_fields["profession"] = profession
    if ville:
        update_fields["ville"] = ville

    if not update_fields:
        print("❌ Aucune modification spécifiée.")
        return False

    try:
        res = db.membres.update_one({"numero": numero}, {"$set": update_fields})
        if res.matched_count == 0:
            print("❌ Membre introuvable.")
            return False
        print("✓ Opération effectuée avec succès.")
        return True
    except PyMongoError:
        print("❌ Erreur lors de la modification du membre.")
        return False

def supprimer_membre(numero):
    """
    Supprime un membre si et seulement s'il ne possède ni comptes ni prêts.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    try:
        membre = db.membres.find_one({"numero": numero})
        if not membre:
            print("❌ Membre introuvable.")
            return False

        comptes_count = db.comptes.count_documents({"membre": numero})
        prets_count = db.prets.count_documents({"membre": numero})

        if comptes_count > 0 or prets_count > 0:
            print(f"❌ Impossible de supprimer le membre {numero} : possède {comptes_count} compte(s) et {prets_count} prêt(s).")
            return False

        db.membres.delete_one({"numero": numero})
        print("✓ Opération effectuée avec succès.")
        return True
    except PyMongoError:
        print("❌ Erreur lors de la suppression du membre.")
        return False
