from datetime import datetime
from pymongo.errors import PyMongoError
from database import get_db

PERIODICITES_AUTORISEES = ["mensuelle", "hebdomadaire", "bimensuelle"]

def creer_tontine(nom, montant_cotisation, periodicite, membres_liste, ordre_benefice=None):
    """
    Crée une nouvelle tontine avec une liste initiale de membres.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    if periodicite not in PERIODICITES_AUTORISEES:
        print(f"❌ Périodicité invalide. Valeurs autorisées : {PERIODICITES_AUTORISEES}")
        return None

    # Suppression des doublons de membres
    membres_uniques = list(set(membres_liste))

    # Vérification présence des membres en BDD
    membres_existants = list(db.membres.find({"numero": {"$in": membres_uniques}}, {"numero": 1}))
    numeros_valides = [m["numero"] for m in membres_existants]

    if len(numeros_valides) == 0:
        print("❌ Aucun membre valide fourni pour la tontine.")
        return None

    if ordre_benefice is None:
        ordre_benefice = list(numeros_valides)
    else:
        # Filtrer l'ordre fourni pour ne garder que les membres valides
        ordre_benefice = [m for m in ordre_benefice if m in numeros_valides]

    doc = {
        "nom": nom,
        "montant_cotisation": float(montant_cotisation),
        "periodicite": periodicite,
        "membres": numeros_valides,
        "ordre_benefice": ordre_benefice,
        "tours": []
    }

    try:
        res = db.tontines.insert_one(doc)
        print(f"✓ Opération effectuée avec succès. Tontine '{nom}' créée.")
        return doc
    except PyMongoError:
        print("❌ Erreur lors de la création de la tontine.")
        return None

def ajouter_membre_tontine(nom_tontine, numero_membre):
    """
    Ajoute un membre à une tontine existante (vérifie les doublons).
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    tontine = db.tontines.find_one({"nom": nom_tontine})
    if not tontine:
        print("❌ Tontine introuvable.")
        return False

    if numero_membre in tontine.get("membres", []):
        print(f"❌ Le membre {numero_membre} appartient déjà à la tontine '{nom_tontine}'.")
        return False

    membre_doc = db.membres.find_one({"numero": numero_membre})
    if not membre_doc:
        print(f"❌ Membre '{numero_membre}' introuvable.")
        return False

    try:
        db.tontines.update_one(
            {"nom": nom_tontine},
            {
                "$push": {
                    "membres": numero_membre,
                    "ordre_benefice": numero_membre
                }
            }
        )
        print(f"✓ Membre {numero_membre} ajouté à la tontine '{nom_tontine}'.")
        return True
    except PyMongoError:
        print("❌ Erreur lors de l'ajout du membre à la tontine.")
        return False

def lister_tontines_membre(numero_membre):
    """
    Liste toutes les tontines auxquelles participe un membre.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.tontines.find({"membres": numero_membre}, {"_id": 0}))
    except PyMongoError:
        print("❌ Erreur lors de la récupération des tontines du membre.")
        return []

def determiner_prochain_beneficiaire(nom_tontine):
    """
    Détermine le prochain bénéficiaire de la tontine selon 'ordre_benefice' et les tours déjà réalisés.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    tontine = db.tontines.find_one({"nom": nom_tontine})
    if not tontine:
        print("❌ Tontine introuvable.")
        return None

    ordre = tontine.get("ordre_benefice", [])
    tours = tontine.get("tours", [])

    beneficiaires_passes = [t.get("beneficiaire") for t in tours if t.get("beneficiaire")]

    for membre in ordre:
        if membre not in beneficiaires_passes:
            return membre

    # Si tout le monde a déjà bénéficié d'un tour, le cycle recommence
    if ordre:
        return ordre[0]
    return None

def enregistrer_cotisation(nom_tontine, numero_membre, montant, date_tour=None):
    """
    Enregistre la cotisation d'un membre pour le tour courant (ou crée un tour s'il n'existe pas).
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    tontine = db.tontines.find_one({"nom": nom_tontine})
    if not tontine:
        print("❌ Tontine introuvable.")
        return False

    if numero_membre not in tontine.get("membres", []):
        print(f"❌ Le membre {numero_membre} ne fait pas partie de cette tontine.")
        return False

    if date_tour is None:
        date_tour = datetime.now().strftime("%Y-%m-%d")

    tours = tontine.get("tours", [])

    # Trouver ou créer le tour actif
    if not tours or (tours and len(tours[-1].get("cotisations_recues", [])) >= len(tontine.get("membres", []))):
        prochain_benef = determiner_prochain_beneficiaire(nom_tontine)
        nouveau_tour = {
            "date": date_tour,
            "beneficiaire": prochain_benef,
            "cotisations_recues": []
        }
        tours.append(nouveau_tour)

    tour_actuel = tours[-1]

    # Vérifier si le membre a déjà cotisé pour ce tour
    deja_cotise = any(c.get("membre") == numero_membre for c.get in tour_actuel.get("cotisations_recues", []))
    if deja_cotise:
        print(f"⚠️ Le membre {numero_membre} a déjà cotisé pour ce tour.")
        return False

    tour_actuel.get("cotisations_recues", []).append({
        "membre": numero_membre,
        "montant": float(montant)
    })

    try:
        db.tontines.update_one(
            {"nom": nom_tontine},
            {"$set": {"tours": tours}}
        )
        print(f"✓ Cotisation de {montant:,.0f} FCFA enregistrée pour {numero_membre} (Tontine: '{nom_tontine}').")
        return True
    except PyMongoError:
        print("❌ Erreur lors de l'enregistrement de la cotisation.")
        return False
