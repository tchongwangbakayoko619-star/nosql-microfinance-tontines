import math
from datetime import datetime, timedelta
from pymongo.errors import PyMongoError
from database import get_db

STATUTS_PRET = ["en_cours", "solde", "en_retard"]

def calculer_echeancier(montant, taux, duree, date_octroi=None):
    """
    Calcule l'échéancier mensuel d'un prêt bancaire.
    Formule de la mensualité constante :
    M = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
    où :
      - P = montant du prêt (capital)
      - r = taux d'intérêt mensuel (taux annuel / 100 / 12)
      - n = durée en mois
    Si le taux est 0, M = P / n.
    """
    if date_octroi is None:
        start_date = datetime.now()
    elif isinstance(date_octroi, str):
        start_date = datetime.strptime(date_octroi, "%Y-%m-%d")
    else:
        start_date = date_octroi

    montant = float(montant)
    taux = float(taux)
    duree = int(duree)

    if duree <= 0:
        return []

    if taux > 0:
        r = (taux / 100.0) / 12.0
        mensualite = montant * (r * (1 + r)**duree) / ((1 + r)**duree - 1)
    else:
        mensualite = montant / duree

    mensualite = round(mensualite, 2)
    echeancier = []

    current_date = start_date
    for i in range(1, duree + 1):
        # Ajout d'un mois approximatif (30 jours)
        current_date += timedelta(days=30)
        echeancier.append({
            "num_echeance": i,
            "date": current_date.strftime("%Y-%m-%d"),
            "montant_du": mensualite,
            "paye": False,
            "date_paiement": None
        })

    return echeancier

def creer_pret(membre, montant, taux, duree, date_octroi=None):
    """
    Crée un prêt avec son échéancier embarqué pour un membre donné.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    # Vérification membre
    membre_doc = db.membres.find_one({"numero": membre})
    if not membre_doc:
        print(f"❌ Membre introuvable ('{membre}').")
        return None

    if date_octroi is None:
        date_octroi = datetime.now().strftime("%Y-%m-%d")

    echeancier = calculer_echeancier(montant, taux, duree, date_octroi)

    doc = {
        "membre": membre,
        "montant": float(montant),
        "taux": float(taux),
        "duree": int(duree),
        "date_octroi": date_octroi,
        "echeancier": echeancier,
        "statut": "en_cours"
    }

    try:
        res = db.prets.insert_one(doc)
        doc["_id"] = res.inserted_id
        print(f"✓ Opération effectuée avec succès. Prêt de {montant:,.0f} FCFA accordé au membre {membre}.")
        return doc
    except PyMongoError:
        print("❌ Erreur lors de la création du prêt.")
        return None

def obtenir_pret(pret_id):
    """
    Récupère un document prêt par son _id.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    try:
        from bson import ObjectId
        if isinstance(pret_id, str):
            pret_id = ObjectId(pret_id)
        pret = db.prets.find_one({"_id": pret_id})
        if not pret:
            print("❌ Prêt introuvable.")
            return None
        return pret
    except Exception:
        print("❌ Prêt introuvable.")
        return None

def lister_prets_membre(numero_membre):
    """
    Liste tous les prêts (actifs ou archives) d'un membre.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    try:
        return list(db.prets.find({"membre": numero_membre}))
    except PyMongoError:
        print("❌ Erreur lors de la recherche des prêts du membre.")
        return []

def enregistrer_paiement_echeance(pret_id, index_echeance, date_paiement=None):
    """
    Enregistre le paiement d'une échéance spécifique d'un prêt.
    Met à jour automatiquement le statut du prêt.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    if date_paiement is None:
        date_paiement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pret = obtenir_pret(pret_id)
    if not pret:
        return False

    echeancier = pret.get("echeancier", [])
    if index_echeance < 0 or index_echeance >= len(echeancier):
        print("❌ Numéro d'échéance invalide.")
        return False

    if echeancier[index_echeance]["paye"]:
        print("⚠️ Cette échéance est déjà payée.")
        return False

    echeancier[index_echeance]["paye"] = True
    echeancier[index_echeance]["date_paiement"] = date_paiement

    try:
        db.prets.update_one(
            {"_id": pret["_id"]},
            {"$set": {"echeancier": echeancier}}
        )
        print("✓ Opération effectuée avec succès. Échéance enregistrée comme payée.")
        mettre_a_jour_statut_pret(pret["_id"])
        return True
    except PyMongoError:
        print("❌ Erreur lors du paiement de l'échéance.")
        return False

def mettre_a_jour_statut_pret(pret_id):
    """
    Re-calcule et met à jour le statut du prêt :
      - 'solde' : toutes les échéances sont payées
      - 'en_retard' : au moins une échéance impayée est dépassée par rapport à aujourd'hui
      - 'en_cours' : sinon
    Si le prêt est 'solde', déclenche automatiquement son archivage.
    """
    db = get_db()
    if db is None:
        return False

    pret = obtenir_pret(pret_id)
    if not pret:
        return False

    echeancier = pret.get("echeancier", [])
    if not echeancier:
        return False

    toutes_payees = all(ech.get("paye") for ech in echeancier)
    aujourdhui = datetime.now().strftime("%Y-%m-%d")

    en_retard = any(
        (not ech.get("paye")) and (ech.get("date") < aujourdhui)
        for ech in echeancier
    )

    if toutes_payees:
        nouveau_statut = "solde"
    elif en_retard:
        nouveau_statut = "en_retard"
    else:
        nouveau_statut = "en_cours"

    try:
        db.prets.update_one(
            {"_id": pret["_id"]},
            {"$set": {"statut": nouveau_statut}}
        )
        if nouveau_statut == "solde":
            archiver_pret_solde(pret["_id"])
        return True
    except PyMongoError:
        return False

def archiver_pret_solde(pret_id):
    """
    Copie le prêt soldé dans 'prets_archives' puis le supprime de 'prets'.
    """
    db = get_db()
    if db is None:
        return False

    try:
        from bson import ObjectId
        if isinstance(pret_id, str):
            pret_id = ObjectId(pret_id)

        pret = db.prets.find_one({"_id": pret_id, "statut": "solde"})
        if not pret:
            return False

        pret_archive = dict(pret)
        pret_archive["date_archivage"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.prets_archives.insert_one(pret_archive)
        db.prets.delete_one({"_id": pret_id})
        print(f"✓ Prêt {pret_id} archivé avec succès vers 'prets_archives'.")
        return True
    except PyMongoError:
        print("❌ Erreur lors de l'archivage du prêt.")
        return False

def archiver_tous_prets_soldes():
    """
    Parcourt et archive l'ensemble des prêts ayant le statut 'solde'.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return 0

    try:
        prets_soldes = list(db.prets.find({"statut": "solde"}))
        count = 0
        for pret in prets_soldes:
            if archiver_pret_solde(pret["_id"]):
                count += 1
        print(f"✓ {count} prêt(s) soldé(s) archivé(s).")
        return count
    except PyMongoError:
        print("❌ Erreur lors de l'archivage global des prêts.")
        return 0
