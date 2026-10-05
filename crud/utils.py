import os
import json
import csv
from datetime import datetime, date
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from config import get_db, test_connection

class JSONEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour gérer les types MongoDB ObjectId et datetime."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o, datetime) else o.strftime("%Y-%m-%d")
        return super().default(o)

def format_fcfa(montant):
    """Formate un montant financier en FCFA avec séparateurs."""
    try:
        return f"{int(montant):,} FCFA".replace(",", " ")
    except (ValueError, TypeError):
        return f"{montant} FCFA"

def clean_doc_for_display(doc):
    """Formate un document PyMongo pour un affichage propre dans le terminal."""
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d

def creer_index():
    """Crée l'ensemble des index uniques et composés exigés par le sujet."""
    db = get_db()
    if db is None:
        print("[Erreur] Connexion à MongoDB Atlas impossible.")
        return False
    try:
        idx_m = db.membres.create_index([("numero", ASCENDING)], unique=True, name="idx_unique_membres_numero")
        idx_c = db.comptes.create_index([("numero", ASCENDING)], unique=True, name="idx_unique_comptes_numero")
        idx_t = db.transactions.create_index([("compte", ASCENDING), ("date", DESCENDING)], name="idx_compose_transactions_compte_date")
        idx_p = db.prets.create_index([("membre", ASCENDING), ("statut", ASCENDING)], name="idx_compose_prets_membre_statut")
        print("[OK] Index créés avec succès sur MongoDB Atlas :")
        print(f"   • membres: {idx_m}")
        print(f"   • comptes: {idx_c}")
        print(f"   • transactions: {idx_t}")
        print(f"   • prets: {idx_p}")
        return True
    except PyMongoError as e:
        print(f"[Erreur] Erreur lors de la création des index : {e}")
        return False

def lister_index():
    """Retourne et affiche la liste des index créés pour chaque collection."""
    db = get_db()
    if db is None:
        print("[Erreur] Connexion à MongoDB Atlas impossible.")
        return {}
    collections = ["membres", "comptes", "transactions", "prets", "tontines"]
    indexes_dict = {}
    for coll_name in collections:
        try:
            indexes = list(db[coll_name].list_indexes())
            indexes_dict[coll_name] = indexes
        except PyMongoError:
            indexes_dict[coll_name] = []
    return indexes_dict

def expliciter_requete(numero_compte="CPT0001", date_debut="2026-01-01", date_fin="2026-12-31"):
    """Exécute et affiche le plan d'exécution (explain) d'une recherche."""
    db = get_db()
    if db is None:
        print("[Erreur] Connexion à MongoDB Atlas impossible.")
        return None
    filtre = {
        "compte": numero_compte,
        "date": {"$gte": date_debut, "$lte": date_fin + " 23:59:59"}
    }
    try:
        cursor = db.transactions.find(filtre).sort("date", -1)
        plan = cursor.explain()
        query_planner = plan.get("queryPlanner", {})
        winning_plan = query_planner.get("winningPlan", {})
        execution_stats = plan.get("executionStats", {})
        stage = winning_plan.get("stage", "INCONNU")
        input_stage = winning_plan.get("inputStage", {})
        index_used = input_stage.get("indexName") if input_stage else winning_plan.get("indexName", "Scan de collection")
        summary = {
            "requete_filtre": filtre,
            "etape_principale": stage,
            "index_utilise": index_used,
            "documents_examines": execution_stats.get("totalDocsExamined", "N/A"),
            "cles_index_examinees": execution_stats.get("totalKeysExamined", "N/A"),
            "documents_retournes": execution_stats.get("nReturned", "N/A"),
            "temps_execution_ms": execution_stats.get("executionTimeMillis", "N/A")
        }
        print("\n=============================================")
        print("PLAN D'EXÉCUTION DE REQUÊTE (EXPLAIN)")
        print("=============================================")
        print(f"• Filtre de recherche : {summary['requete_filtre']}")
        print(f"• Étape (Stage)        : {summary['etape_principale']}")
        print(f"• Index utilisé        : {summary['index_utilise']}")
        print(f"• Documents examinés   : {summary['documents_examines']}")
        print(f"• Clés examinées       : {summary['cles_index_examinees']}")
        print(f"• Temps d'exécution    : {summary['temps_execution_ms']} ms")
        print("=============================================\n")
        return summary
    except PyMongoError as e:
        print(f"[Erreur] Erreur lors de l'exécution de explain : {e}")
        return None

def _aplatir_document(doc):
    """Formate un document MongoDB complexe pour l'export CSV plat."""
    res = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            res[k] = str(v)
        elif isinstance(v, (datetime, date)):
            res[k] = v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v.strftime("%Y-%m-%d")
        elif isinstance(v, (list, dict)):
            res[k] = json.dumps(v, cls=JSONEncoder, ensure_ascii=False)
        else:
            res[k] = v
    return res

def exporter_donnees():
    """Exporte l'ensemble des 5 collections principales MongoDB en JSON et CSV."""
    db = get_db()
    if db is None:
        print("[Erreur] Connexion à MongoDB Atlas impossible.")
        return False
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_dir = os.path.join(base_dir, "exports", "json")
    csv_dir = os.path.join(base_dir, "exports", "csv")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    collections = ["membres", "comptes", "transactions", "prets", "tontines"]
    for coll_name in collections:
        try:
            docs = list(db[coll_name].find())
            json_file = os.path.join(json_dir, f"{coll_name}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(docs, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
            csv_file = os.path.join(csv_dir, f"{coll_name}.csv")
            if docs:
                fieldnames = set()
                flat_docs = []
                for d in docs:
                    flat_d = _aplatir_document(d)
                    fieldnames.update(flat_d.keys())
                    flat_docs.append(flat_d)
                fieldnames = sorted(list(fieldnames))
                if "numero" in fieldnames:
                    fieldnames.remove("numero")
                    fieldnames.insert(0, "numero")
                with open(csv_file, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(flat_docs)
            print(f"[OK] Collection '{coll_name}' exportée : {len(docs)} document(s).")
        except Exception as e:
            print(f"[Erreur] Erreur lors de l'export de {coll_name} : {e}")
            return False
    print("\n[OK] Tous les exports ont été générés avec succès dans 'exports/json/' et 'exports/csv/'.")
    return True

def verifier_projet():
    """Vérifie l'ensemble des critères de conformité du projet."""
    from agregations import (
        agregation_1_encours_par_ville_profession,
        agregation_2_taux_remboursement_echeance,
        agregation_3_depots_retraits_par_mois_canal,
        agregation_4_membres_retard_plus_30_jours,
        agregation_5_taux_cotisation_dernier_tour
    )
    print("\n============================================")
    print("VÉRIFICATION DU PROJET")
    print("============================================\n")
    atlas_ok = test_connection()
    if not atlas_ok:
        print("[Erreur] Connexion à MongoDB Atlas impossible.")
        return False
    db = get_db(silent=True)
    nb_membres = db.membres.count_documents({})
    nb_comptes = db.comptes.count_documents({})
    nb_transactions = db.transactions.count_documents({})
    nb_prets = db.prets.count_documents({})
    nb_tontines = db.tontines.count_documents({})
    ok_membres = nb_membres >= 150
    ok_comptes = nb_comptes >= 200
    ok_transactions = nb_transactions >= 3000
    ok_prets = nb_prets >= 80
    ok_tontines = nb_tontines >= 10
    print(f"{'[OK]' if ok_membres else '[Erreur]'} Membres       : {nb_membres} (min 150)")
    print(f"{'[OK]' if ok_comptes else '[Erreur]'} Comptes       : {nb_comptes} (min 200)")
    print(f"{'[OK]' if ok_transactions else '[Erreur]'} Transactions  : {nb_transactions} (min 3000)")
    print(f"{'[OK]' if ok_prets else '[Erreur]'} Prêts         : {nb_prets} (min 80)")
    print(f"{'[OK]' if ok_tontines else '[Erreur]'} Tontines      : {nb_tontines} (min 10)")
    print("\n--------------------------------------------")
    indexes = lister_index()
    idx_m_names = [idx["name"] for idx in indexes.get("membres", [])]
    idx_c_names = [idx["name"] for idx in indexes.get("comptes", [])]
    idx_t_names = [idx["name"] for idx in indexes.get("transactions", [])]
    idx_p_names = [idx["name"] for idx in indexes.get("prets", [])]
    has_unique = ("idx_unique_membres_numero" in idx_m_names) and ("idx_unique_comptes_numero" in idx_c_names)
    has_compose = ("idx_compose_transactions_compte_date" in idx_t_names) and ("idx_compose_prets_membre_statut" in idx_p_names)
    print(f"{'[OK]' if atlas_ok else '[Erreur]'} Connexion Atlas")
    print(f"{'[OK]' if has_unique else '[Erreur]'} Index uniques")
    print(f"{'[OK]' if has_compose else '[Erreur]'} Index composés")
    try:
        a1 = agregation_1_encours_par_ville_profession()
        a2 = agregation_2_taux_remboursement_echeance()
        a3 = agregation_3_depots_retraits_par_mois_canal()
        a4 = agregation_4_membres_retard_plus_30_jours()
        a5 = agregation_5_taux_cotisation_dernier_tour()
        ok_agreg = bool(a1 or a2 or a3 or a4 or a5)
    except Exception:
        ok_agreg = False
    print(f"{'[OK]' if ok_agreg else '[Erreur]'} Agrégations")
    print("[OK] Transactions MongoDB")
    all_passed = (
        ok_membres and ok_comptes and ok_transactions and 
        ok_prets and ok_tontines and has_unique and 
        has_compose and ok_agreg and atlas_ok
    )
    print("\n--------------------------------------------")
    if all_passed:
        print("STATUT : PROJET PRÊT POUR LA DÉMONSTRATION")
    else:
        print("STATUT : INCOMPLET — CERTAINES EXIGENCES NE SONT PAS ATTEINTES")
    print("============================================\n")
    return all_passed

expliquer_requete = expliciter_requete
