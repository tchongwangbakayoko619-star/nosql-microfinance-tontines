import uuid
from datetime import datetime
from pymongo.errors import PyMongoError
from database import get_client, get_db
from config import MONGO_DB

CANAUX_AUTORISES = ["agence", "mobile_money"]

def effectuer_depot(numero_compte, montant, canal="agence"):
    """
    Effectue un dépôt sur un compte actif et enregistre la transaction.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    if canal not in CANAUX_AUTORISES:
        print(f"❌ Canal invalide. Canaux autorisés : {CANAUX_AUTORISES}")
        return None

    try:
        montant = float(montant)
        if montant <= 0:
            print("❌ Montant invalide.")
            return None
    except (ValueError, TypeError):
        print("❌ Montant invalide.")
        return None

    compte = db.comptes.find_one({"numero": numero_compte})
    if not compte:
        print("❌ Compte introuvable.")
        return None

    if compte.get("statut") != "actif":
        print("❌ Compte inactif ou clôturé.")
        return None

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Mise à jour atomique du solde
        db.comptes.update_one(
            {"numero": numero_compte},
            {"$inc": {"solde": montant}}
        )

        trans_doc = {
            "compte": numero_compte,
            "type": "depot",
            "montant": montant,
            "date": date_str,
            "canal": canal,
            "reference": f"DEP-{uuid.uuid4().hex[:8].upper()}"
        }
        db.transactions.insert_one(trans_doc)

        print(f"✓ Opération effectuée avec succès. Dépôt de {montant:,.0f} FCFA réalisé sur le compte {numero_compte}.")
        return trans_doc
    except PyMongoError:
        print("❌ Erreur lors de l'exécution du dépôt.")
        return None

def effectuer_retrait(numero_compte, montant, canal="agence"):
    """
    Effectue un retrait sur un compte actif si le solde est suffisant.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    if canal not in CANAUX_AUTORISES:
        print(f"❌ Canal invalide. Canaux autorisés : {CANAUX_AUTORISES}")
        return None

    try:
        montant = float(montant)
        if montant <= 0:
            print("❌ Montant invalide.")
            return None
    except (ValueError, TypeError):
        print("❌ Montant invalide.")
        return None

    compte = db.comptes.find_one({"numero": numero_compte})
    if not compte:
        print("❌ Compte introuvable.")
        return None

    if compte.get("statut") != "actif":
        print("❌ Compte inactif ou clôturé.")
        return None

    if compte.get("solde", 0) < montant:
        print("❌ Solde insuffisant.")
        return None

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Mise à jour conditionnelle avec vérification de solde >= montant
        res = db.comptes.update_one(
            {"numero": numero_compte, "solde": {"$gte": montant}},
            {"$inc": {"solde": -montant}}
        )

        if res.modified_count == 0:
            print("❌ Solde insuffisant.")
            return None

        trans_doc = {
            "compte": numero_compte,
            "type": "retrait",
            "montant": montant,
            "date": date_str,
            "canal": canal,
            "reference": f"RET-{uuid.uuid4().hex[:8].upper()}"
        }
        db.transactions.insert_one(trans_doc)

        print(f"✓ Opération effectuée avec succès. Retrait de {montant:,.0f} FCFA effectué sur le compte {numero_compte}.")
        return trans_doc
    except PyMongoError:
        print("❌ Erreur lors de l'exécution du retrait.")
        return None

def effectuer_virement(compte_source, compte_destination, montant, canal="agence"):
    """
    Effectue un virement entre deux comptes en utilisant une transaction MongoDB multi-documents.
    """
    client = get_client(silent=True)
    if client is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    try:
        montant = float(montant)
        if montant <= 0:
            print("❌ Montant invalide.")
            return False
    except (ValueError, TypeError):
        print("❌ Montant invalide.")
        return False

    if compte_source == compte_destination:
        print("❌ Virement impossible : les comptes source et destination doivent être différents.")
        return False

    ref_virement = f"VIR-{uuid.uuid4().hex[:8].upper()}"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def execution_virement(session):
        db = client[MONGO_DB]

        # 1 & 2. Vérifier les comptes
        src = db.comptes.find_one({"numero": compte_source}, session=session)
        dst = db.comptes.find_one({"numero": compte_destination}, session=session)

        if not src:
            raise ValueError(f"Compte source '{compte_source}' introuvable.")
        if not dst:
            raise ValueError(f"Compte destination '{compte_destination}' introuvable.")

        # 3. Vérifier statuts
        if src.get("statut") != "actif":
            raise ValueError(f"Compte source '{compte_source}' inactif ou clôturé.")
        if dst.get("statut") != "actif":
            raise ValueError(f"Compte destination '{compte_destination}' inactif ou clôturé.")

        # 6. Vérifier le solde disponible
        if src.get("solde", 0) < montant:
            raise ValueError("Solde insuffisant sur le compte source.")

        # 7. Débiter le compte source avec contrôle de concurrence
        res_src = db.comptes.update_one(
            {"numero": compte_source, "solde": {"$gte": montant}},
            {"$inc": {"solde": -montant}},
            session=session
        )
        if res_src.modified_count == 0:
            raise ValueError("Solde insuffisant sur le compte source.")

        # 8. Créditer le compte destination
        db.comptes.update_one(
            {"numero": compte_destination},
            {"$inc": {"solde": montant}},
            session=session
        )

        # 9. Créer les documents de transactions
        t_src = {
            "compte": compte_source,
            "type": "virement",
            "montant": montant,
            "date": date_str,
            "canal": canal,
            "compte_source": compte_source,
            "compte_destination": compte_destination,
            "reference_virement": ref_virement,
            "sens": "debit"
        }
        t_dst = {
            "compte": compte_destination,
            "type": "virement",
            "montant": montant,
            "date": date_str,
            "canal": canal,
            "compte_source": compte_source,
            "compte_destination": compte_destination,
            "reference_virement": ref_virement,
            "sens": "credit"
        }
        db.transactions.insert_many([t_src, t_dst], session=session)

    try:
        # Vraie transaction multi-documents MongoDB
        with client.start_session() as session:
            session.with_transaction(execution_virement)
        print(f"✓ Opération effectuée avec succès. Virement de {montant:,.0f} FCFA exécuté (Réf: {ref_virement}).")
        return True
    except ValueError as ve:
        print(f"❌ Virement impossible : {ve}")
        return False
    except PyMongoError as pme:
        # En cas d'environnement mono-nœud sans réplica set (fallback gracieux documenté)
        if "Transaction numbers are only allowed on a replica set" in str(pme) or "standalone" in str(pme):
            print("⚠️ Remarque: Les transactions multi-documents nécessitent un réplica set (comme sur MongoDB Atlas). Mode de secours sans session exécuté.")
            return _effectuer_virement_sans_session(compte_source, compte_destination, montant, canal, ref_virement, date_str)
        print("❌ Virement impossible : erreur de transaction MongoDB.")
        return False

def _effectuer_virement_sans_session(compte_source, compte_destination, montant, canal, ref_virement, date_str):
    """
    Fallback secours si exécuté sur un serveur MongoDB local sans réplica set activé.
    """
    db = get_db()
    src = db.comptes.find_one({"numero": compte_source})
    dst = db.comptes.find_one({"numero": compte_destination})
    if not src or not dst:
        print("❌ Compte introuvable.")
        return False
    if src.get("statut") != "actif" or dst.get("statut") != "actif":
        print("❌ Compte inactif.")
        return False
    if src.get("solde", 0) < montant:
        print("❌ Solde insuffisant.")
        return False

    res = db.comptes.update_one({"numero": compte_source, "solde": {"$gte": montant}}, {"$inc": {"solde": -montant}})
    if res.modified_count == 0:
        print("❌ Solde insuffisant.")
        return False

    db.comptes.update_one({"numero": compte_destination}, {"$inc": {"solde": montant}})
    db.transactions.insert_many([
        {
            "compte": compte_source,
            "type": "virement",
            "montant": montant,
            "date": date_str,
            "canal": canal,
            "compte_source": compte_source,
            "compte_destination": compte_destination,
            "reference_virement": ref_virement,
            "sens": "debit"
        },
        {
            "compte": compte_destination,
            "type": "virement",
            "montant": montant,
            "date": date_str,
            "canal": canal,
            "compte_source": compte_source,
            "compte_destination": compte_destination,
            "reference_virement": ref_virement,
            "sens": "credit"
        }
    ])
    print(f"✓ Opération effectuée avec succès. Virement de {montant:,.0f} FCFA exécuté (Réf: {ref_virement}).")
    return True

def releve_compte(numero_compte, date_debut=None, date_fin=None):
    """
    Affiche le relevé de compte filtré par période et trié par date.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    filtre = {"compte": numero_compte}

    if date_debut or date_fin:
        date_query = {}
        if date_debut:
            date_query["$gte"] = date_debut
        if date_fin:
            date_query["$lte"] = date_fin + " 23:59:59"
        filtre["date"] = date_query

    try:
        results = list(db.transactions.find(filtre, {"_id": 0}).sort("date", 1))
        return results
    except PyMongoError:
        print("❌ Erreur lors de la récupération du relevé de compte.")
        return []
