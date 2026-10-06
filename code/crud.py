from datetime import datetime, timedelta
from config import get_db, get_client
from pymongo.errors import PyMongoError, DuplicateKeyError
import validators
from validators import ValidationError
from utils import print_erreur, print_succes, print_info, generer_code_auto

# Ré-exportation des modules d'index pour alléger crud.py
from indexes import creer_index_projet, obtenir_liste_index

# =====================================================================
# 2. OPERATEURS DE CREATION (INSERT)
# =====================================================================

def create_membre(numero=None, nom="", telephone="", profession="", ville="", piece_identite="", db=None):
    if db is None:
        db = get_db()
    if not numero or str(numero).strip() == "":
        numero = generer_code_auto(db.membres, "MBR", champ="numero", largeur=4, db=db)
    try:
        validators.valider_membre(numero, nom, telephone, profession, ville, piece_identite, db=db)
        doc = {
            "numero": str(numero).strip(),
            "nom": str(nom).strip(),
            "telephone": str(telephone).strip(),
            "profession": str(profession).strip(),
            "ville": str(ville).strip(),
            "date_adhesion": datetime.now(),
            "piece_identite": str(piece_identite).strip()
        }
        db.membres.insert_one(doc)
        print_succes(f"[SUCCES] Membre {numero} créé avec succès.")
        return doc
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return None
    except DuplicateKeyError:
        print_erreur(f"[DOUBLON] Un membre avec le numéro {numero} existe déjà dans la base.")
        return None
    except PyMongoError as e:
        print_erreur(f"[MONGODB] {e}")
        return None

def create_compte(numero=None, membre_numero="", type_compte="épargne", solde_initial=0.0, db=None):
    if db is None:
        db = get_db()
    if not numero or str(numero).strip() == "":
        numero = generer_code_auto(db.comptes, "CPT", champ="numero", largeur=5, db=db)
    try:
        validators.valider_compte(numero, membre_numero, type_compte, solde_initial, db=db)
        doc = {
            "numero": str(numero).strip(),
            "membre_numero": str(membre_numero).strip(),
            "type": str(type_compte).lower().strip(),
            "solde": float(solde_initial),
            "date_ouverture": datetime.now()
        }
        db.comptes.insert_one(doc)
        print_succes(f"[SUCCES] Compte {numero} créé pour le membre {membre_numero}.")
        return doc
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return None
    except DuplicateKeyError:
        print_erreur(f"[DOUBLON] Le numéro de compte {numero} existe déjà dans la base.")
        return None

def create_transaction(compte_numero, type_trans, montant, canal="agence", db=None):
    if db is None:
        db = get_db()
    compte = db.comptes.find_one({"numero": compte_numero})
    if not compte:
        print_erreur(f"[ERREUR] Le compte numéro '{compte_numero}' est introuvable.")
        return None

    try:
        validators.valider_montant(montant, "Le montant de la transaction")
        tx_id = f"TXN-{int(datetime.now().timestamp()*1000)}"
        doc = {
            "transaction_id": tx_id,
            "compte_numero": compte_numero,
            "type": type_trans,
            "montant": float(montant),
            "date": datetime.now(),
            "canal": canal
        }
        db.transactions.insert_one(doc)
        print_succes(f"[SUCCES] Transaction {tx_id} créée pour le compte {compte_numero}.")
        return doc
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return None
    except PyMongoError as e:
        print_erreur(f"[MONGODB] {e}")
        return None

def create_pret(code_pret=None, membre_numero="", montant=0, taux=0, duree_mois=1, date_octroi=None, db=None):
    if db is None:
        db = get_db()
    if not code_pret or str(code_pret).strip() == "":
        code_pret = generer_code_auto(db.prets, "PRT", champ="code_pret", largeur=4, db=db)
    try:
        validators.valider_pret(code_pret, membre_numero, montant, taux, duree_mois, db=db)
        date_oct = date_octroi or datetime.now()
        montant_du_par_mois = round(float(montant) / int(duree_mois), 2)
        echeancier = []
        for m in range(1, int(duree_mois) + 1):
            echeancier.append({
                "numero_echeance": m,
                "date_echeance": date_oct + timedelta(days=30 * m),
                "montant_du": montant_du_par_mois,
                "paye": False,
                "date_paiement": None
            })

        doc = {
            "code_pret": str(code_pret).strip(),
            "membre_numero": str(membre_numero).strip(),
            "montant": float(montant),
            "taux": float(taux),
            "duree_mois": int(duree_mois),
            "date_octroi": date_oct,
            "echeancier": echeancier,
            "statut": "en cours"
        }
        db.prets.insert_one(doc)
        print_succes(f"[SUCCES] Prêt {code_pret} octroyé au membre {membre_numero}.")
        return doc
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return None
    except DuplicateKeyError:
        print_erreur(f"[DOUBLON] Le code prêt {code_pret} existe déjà dans la base.")
        return None

def create_tontine(code_tontine=None, nom="", montant_cotisation=0, periodicite="mensuelle", membres_liste=None, db=None):
    if db is None:
        db = get_db()
    if membres_liste is None:
        membres_liste = []
    if not code_tontine or str(code_tontine).strip() == "":
        code_tontine = generer_code_auto(db.tontines, "TNT", champ="code_tontine", largeur=3, db=db)
    try:
        validators.valider_tontine(code_tontine, nom, montant_cotisation, periodicite, membres_liste, db=db)
        import random
        ordre_b = list(membres_liste)
        random.shuffle(ordre_b)

        tours = []
        date_tour_debut = datetime.now()
        for idx, ben in enumerate(ordre_b):
            cotisations_recues = []
            for m_cot in membres_liste:
                cotisations_recues.append({
                    "membre_numero": m_cot,
                    "montant": 0.0,
                    "paye": False,
                    "date_paye": None
                })
            tours.append({
                "tour_numero": idx + 1,
                "date_tour": date_tour_debut + timedelta(days=30 * idx),
                "beneficiaire_numero": ben,
                "cotisations_recues": cotisations_recues
            })

        doc = {
            "code_tontine": str(code_tontine).strip(),
            "nom": str(nom).strip(),
            "montant_cotisation": float(montant_cotisation),
            "periodicite": str(periodicite).lower().strip(),
            "membres": membres_liste,
            "ordre_benefice": ordre_b,
            "tours": tours
        }
        db.tontines.insert_one(doc)
        print_succes(f"[SUCCES] Tontine {code_tontine} ('{nom}') créée avec succès.")
        return doc
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return None
    except DuplicateKeyError:
        print_erreur(f"[DOUBLON] La tontine {code_tontine} existe déjà dans la base.")
        return None

# =====================================================================
# MODIFICATION GENERIQUE D'ENTITES (UPDATE)
# =====================================================================

def update_membre(numero, telephone=None, profession=None, ville=None, db=None):
    if db is None:
        db = get_db()
    updates = {}
    if telephone: updates["telephone"] = telephone
    if profession: updates["profession"] = profession
    if ville: updates["ville"] = ville

    if not updates:
        print("[INFORMATION] Aucun champ à modifier fourni.")
        return False

    res = db.membres.update_one({"numero": numero}, {"$set": updates})
    if res.matched_count > 0:
        print(f"✓ Informations du membre {numero} mises à jour.")
        return True
    else:
        print(f"[ERREUR] Membre {numero} introuvable.")
        return False

def update_compte(numero, type_compte=None, db=None):
    if db is None:
        db = get_db()
    if not type_compte:
        return False
    res = db.comptes.update_one({"numero": numero}, {"$set": {"type": type_compte}})
    if res.matched_count > 0:
        print(f"✓ Compte {numero} mis à jour (Nouveau type: {type_compte}).")
        return True
    else:
        print(f"[ERREUR] Compte {numero} introuvable.")
        return False

def update_pret(code_pret, statut=None, taux=None, db=None):
    if db is None:
        db = get_db()
    updates = {}
    if statut: updates["statut"] = statut
    if taux is not None: updates["taux"] = float(taux)

    if not updates:
        return False

    res = db.prets.update_one({"code_pret": code_pret}, {"$set": updates})
    if res.matched_count > 0:
        print(f"✓ Prêt {code_pret} mis à jour.")
        return True
    else:
        print(f"[ERREUR] Prêt {code_pret} introuvable.")
        return False

def update_tontine(code_tontine, nom=None, montant_cotisation=None, periodicite=None, db=None):
    if db is None:
        db = get_db()
    updates = {}
    if nom: updates["nom"] = nom
    if montant_cotisation is not None: updates["montant_cotisation"] = float(montant_cotisation)
    if periodicite: updates["periodicite"] = periodicite

    if not updates:
        return False

    res = db.tontines.update_one({"code_tontine": code_tontine}, {"$set": updates})
    if res.matched_count > 0:
        print(f"✓ Tontine {code_tontine} mise à jour.")
        return True
    else:
        print(f"[ERREUR] Tontine {code_tontine} introuvable.")
        return False

# =====================================================================
# 3. OPERATEURS DE LECTURE (FIND)
# =====================================================================

def get_comptes_et_solde_membre(membre_numero, db=None):
    """
    Exigence PDF: Comptes et solde d'un membre.
    """
    if db is None:
        db = get_db()
    membre = db.membres.find_one({"numero": membre_numero})
    if not membre:
        print(f"[ERREUR] Membre {membre_numero} introuvable.")
        return None

    comptes = list(db.comptes.find({"membre_numero": membre_numero}))
    solde_total = sum(c.get("solde", 0.0) for c in comptes)

    return {
        "membre": membre,
        "comptes": comptes,
        "solde_total": solde_total
    }

def get_releve_transactions(compte_numero, date_debut=None, date_fin=None, db=None):
    """
    Exigence PDF: Relevé des transactions d'un compte sur une période.
    """
    if db is None:
        db = get_db()
    compte = db.comptes.find_one({"numero": compte_numero})
    if not compte:
        print(f"[ERREUR] Compte {compte_numero} introuvable.")
        return []

    query = {"compte_numero": compte_numero}
    if date_debut or date_fin:
        query["date"] = {}
        if date_debut:
            query["date"]["$gte"] = date_debut
        if date_fin:
            query["date"]["$lte"] = date_fin

    transactions = list(db.transactions.find(query).sort("date", -1))
    return transactions

def get_echeances_impayees(db=None):
    """
    Exigence PDF: Échéances impayées à ce jour.
    """
    if db is None:
        db = get_db()
    maintenant = datetime.now()

    pipeline = [
        {"$unwind": "$echeancier"},
        {
            "$match": {
                "echeancier.paye": False,
                "echeancier.date_echeance": {"$lte": maintenant}
            }
        },
        {
            "$project": {
                "code_pret": 1,
                "membre_numero": 1,
                "statut": 1,
                "numero_echeance": "$echeancier.numero_echeance",
                "date_echeance": "$echeancier.date_echeance",
                "montant_du": "$echeancier.montant_du"
            }
        },
        {"$sort": {"date_echeance": 1}}
    ]

    impayees = list(db.prets.aggregate(pipeline))
    return impayees

def get_tontines_et_prochain_beneficiaire(membre_numero, db=None):
    """
    Exigence PDF: Tontines d'un membre et prochain bénéficiaire.
    """
    if db is None:
        db = get_db()
    tontines = list(db.tontines.find({"membres": membre_numero}))
    resultats = []

    for t in tontines:
        # Chercher le prochain tour non encore complété ou le dernier tour
        prochain_ben = "Aucun"
        prochain_date = "N/A"
        for tour in t.get("tours", []):
            # Si toutes les cotisations du tour ne sont pas payées ou si date_tour est future
            cotisations = tour.get("cotisations_recues", [])
            total_paye = sum(1 for c in cotisations if c.get("paye"))
            if total_paye < len(t.get("membres", [])):
                prochain_ben = tour.get("beneficiaire_numero")
                prochain_date = tour.get("date_tour")
                break
        
        resultats.append({
            "code_tontine": t.get("code_tontine"),
            "nom": t.get("nom"),
            "montant_cotisation": t.get("montant_cotisation"),
            "periodicite": t.get("periodicite"),
            "prochain_beneficiaire": prochain_ben,
            "date_prochain_tour": prochain_date
        })

    return resultats

# =====================================================================
# 4. OPERATEURS DE MODIFICATION (UPDATE) & TRANSACTIONS
# =====================================================================

def depot_compte(compte_numero, montant, canal="agence", db=None):
    """
    Exigence PDF: Dépôt sur un compte.
    """
    if db is None:
        db = get_db()
    try:
        validators.valider_depot(compte_numero, montant, canal=canal, db=db)
        canal_clean = validators.valider_canal(canal)
        mtt = float(montant)
        compte_numero = str(compte_numero).strip()

        # Mettre à jour le solde
        db.comptes.update_one({"numero": compte_numero}, {"$inc": {"solde": mtt}})

        # Enregistrer la transaction
        db.transactions.insert_one({
            "transaction_id": f"TXN-{int(datetime.now().timestamp()*1000)}",
            "compte_numero": compte_numero,
            "type": "dépôt",
            "montant": mtt,
            "date": datetime.now(),
            "canal": canal_clean
        })

        print_succes(f"Dépôt de {mtt} FCFA réussi sur le compte {compte_numero} (Canal: {canal_clean}).")
        return True
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return False
    except PyMongoError as e:
        print_erreur(f"[MONGODB] {e}")
        return False

def retrait_compte(compte_numero, montant, canal="agence", db=None):
    """
    Exigence PDF: Retrait (refus si le solde est insuffisant).
    """
    if db is None:
        db = get_db()
    try:
        validators.valider_retrait(compte_numero, montant, canal=canal, db=db)
        canal_clean = validators.valider_canal(canal)
        mtt = float(montant)
        compte_numero = str(compte_numero).strip()

        db.comptes.update_one({"numero": compte_numero}, {"$inc": {"solde": -mtt}})

        db.transactions.insert_one({
            "transaction_id": f"TXN-{int(datetime.now().timestamp()*1000)}",
            "compte_numero": compte_numero,
            "type": "retrait",
            "montant": mtt,
            "date": datetime.now(),
            "canal": canal_clean
        })

        print_succes(f"Retrait de {mtt} FCFA effectué sur le compte {compte_numero} (Canal: {canal_clean}).")
        return True
    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return False
    except PyMongoError as e:
        print_erreur(f"[MONGODB] {e}")
        return False

def virement_comptes(compte_src, compte_dest, montant, canal="agence", db=None):
    """
    Exigence PDF: Virement entre deux comptes avec Transaction MongoDB (session)
    """
    if db is None:
        db = get_db()
    client = get_client()

    try:
        validators.valider_virement(compte_src, compte_dest, montant, canal=canal, db=db)
        canal_clean = validators.valider_canal(canal)
        mtt = float(montant)
        compte_src = str(compte_src).strip()
        compte_dest = str(compte_dest).strip()

        # Utilisation d'une transaction ACID MongoDB
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    # Retrait source
                    db.comptes.update_one({"numero": compte_src}, {"$inc": {"solde": -mtt}}, session=session)
                    # Dépôt destination
                    db.comptes.update_one({"numero": compte_dest}, {"$inc": {"solde": mtt}}, session=session)

                    # Transactions enregistrées
                    now = datetime.now()
                    db.transactions.insert_one({
                        "transaction_id": f"TXN-VIR-OUT-{int(now.timestamp()*1000)}",
                        "compte_numero": compte_src,
                        "type": "virement (débit)",
                        "montant": mtt,
                        "date": now,
                        "canal": canal_clean
                    }, session=session)

                    db.transactions.insert_one({
                        "transaction_id": f"TXN-VIR-IN-{int(now.timestamp()*1000)}",
                        "compte_numero": compte_dest,
                        "type": "virement (crédit)",
                        "montant": mtt,
                        "date": now,
                        "canal": canal_clean
                    }, session=session)

            print_succes(f"Virement de {mtt} FCFA entre {compte_src} et {compte_dest} effectué avec succès (Canal: {canal_clean}, Transaction ACID).")
            return True

        except Exception as e:
            # Fallback pour MongoDB Standalone sans replica set
            print_info(f"[AVERTISSEMENT TRANSACTION SESSION] Exécution fallback sans session replica set...")
            db.comptes.update_one({"numero": compte_src}, {"$inc": {"solde": -mtt}})
            db.comptes.update_one({"numero": compte_dest}, {"$inc": {"solde": mtt}})
            now = datetime.now()
            db.transactions.insert_one({
                "transaction_id": f"TXN-VIR-OUT-{int(now.timestamp()*1000)}",
                "compte_numero": compte_src,
                "type": "virement (débit)",
                "montant": mtt,
                "date": now,
                "canal": canal_clean
            })
            db.transactions.insert_one({
                "transaction_id": f"TXN-VIR-IN-{int(now.timestamp()*1000)}",
                "compte_numero": compte_dest,
                "type": "virement (crédit)",
                "montant": mtt,
                "date": now,
                "canal": canal_clean
            })
            print_succes(f"Virement de {mtt} FCFA entre {compte_src} et {compte_dest} effectué (Canal: {canal_clean}, Fallback).")
            return True

    except ValidationError as ve:
        print_erreur(f"[VALIDATION] {ve}")
        return False
    except PyMongoError as e:
        print_erreur(f"[MONGODB] {e}")
        return False

def payer_echeance_pret(code_pret, numero_echeance, db=None):
    """
    Exigence PDF: Enregistrer le paiement d'une échéance.
    """
    if db is None:
        db = get_db()
    pret = db.prets.find_one({"code_pret": code_pret})
    if not pret:
        print(f"[ERREUR] Prêt {code_pret} introuvable.")
        return False

    echeancier = pret.get("echeancier", [])
    trouve = False
    now = datetime.now()

    for ech in echeancier:
        if ech.get("numero_echeance") == numero_echeance:
            if ech.get("paye"):
                print(f"[INFORMATION] L'échéance {numero_echeance} du prêt {code_pret} a déjà été payée.")
                return True
            ech["paye"] = True
            ech["date_paiement"] = now
            trouve = True
            break

    if not trouve:
        print(f"[ERREUR] Échéance numéro {numero_echeance} introuvable pour le prêt {code_pret}.")
        return False

    # Vérifier si toutes les échéances sont payées pour solder le prêt
    toutes_payees = all(e.get("paye") for e in echeancier)
    nouveau_statut = "soldé" if toutes_payees else pret.get("statut")

    db.prets.update_one(
        {"code_pret": code_pret},
        {
            "$set": {
                "echeancier": echeancier,
                "statut": nouveau_statut
            }
        }
    )

    print(f"✓ Échéance {numero_echeance} du prêt {code_pret} marquée comme PAYÉE. (Statut du prêt: {nouveau_statut})")
    return True

def payer_cotisation_tontine(code_tontine, tour_numero, membre_numero, montant, db=None):
    """
    Exigence PDF: Enregistrer la cotisation d'un membre à une tontine.
    """
    if db is None:
        db = get_db()
    tontine = db.tontines.find_one({"code_tontine": code_tontine})
    if not tontine:
        print(f"[ERREUR] Tontine {code_tontine} introuvable.")
        return False

    tours = tontine.get("tours", [])
    tour_cible = None
    for t in tours:
        if t.get("tour_numero") == tour_numero:
            tour_cible = t
            break

    if not tour_cible:
        print(f"[ERREUR] Tour {tour_numero} introuvable dans la tontine {code_tontine}.")
        return False

    cotisations = tour_cible.get("cotisations_recues", [])
    membre_trouve = False

    for c in cotisations:
        if c.get("membre_numero") == membre_numero:
            c["montant"] = float(montant)
            c["paye"] = True
            c["date_paye"] = datetime.now()
            membre_trouve = True
            break

    if not membre_trouve:
        cotisations.append({
            "membre_numero": membre_numero,
            "montant": float(montant),
            "paye": True,
            "date_paye": datetime.now()
        })

    db.tontines.update_one(
        {"code_tontine": code_tontine},
        {"$set": {"tours": tours}}
    )

    print(f"✓ Cotisation de {montant} FCFA du membre {membre_numero} pour le tour {tour_numero} de la tontine {code_tontine} enregistrée.")
    return True

# =====================================================================
# 5. OPERATEURS DE SUPPRESSION / ARCHIVAGE (DELETE / ARCHIVE)
# =====================================================================

def cloturer_compte(compte_numero, db=None):
    """
    Exigence PDF: Clôturer un compte à solde nul.
    """
    if db is None:
        db = get_db()
    compte = db.comptes.find_one({"numero": compte_numero})
    if not compte:
        print(f"[ERREUR] Compte {compte_numero} introuvable.")
        return False

    if compte.get("solde", 0.0) != 0:
        print(f"[ERREUR CLOTURE REFUSEE] Le solde du compte {compte_numero} n'est pas nul ({compte.get('solde')} FCFA).")
        return False

    db.comptes.delete_one({"numero": compte_numero})
    print(f"✓ Compte {compte_numero} à solde nul clôturé et supprimé avec succès.")
    return True

def archiver_prets_soldes(db=None):
    """
    Exigence PDF: Archiver les prêts soldés.
    Déplace les documents concernés vers prets_archives avec date_archivage puis les supprime de prets.
    """
    if db is None:
        db = get_db()
    prets_soldes = list(db.prets.find({"statut": "soldé"}))
    if not prets_soldes:
        print("[INFORMATION] Aucun prêt soldé à archiver.")
        return 0

    now = datetime.now()
    for p in prets_soldes:
        p["date_archivage"] = now

    db.prets_archives.insert_many(prets_soldes)
    ids_a_supprimer = [p["_id"] for p in prets_soldes]
    res = db.prets.delete_many({"_id": {"$in": ids_a_supprimer}})

    print(f"✓ {res.deleted_count} prêt(s) soldé(s) archivé(s) dans 'prets_archives'.")
    return res.deleted_count

# Ré-exportation des modules d'exportation et vérification pour alléger crud.py
from exports import exporter_donnees_json_csv, verifier_statistiques_projet, json_serializer

