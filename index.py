from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from database import get_db

def creer_index():
    """
    Crée l'ensemble des index uniques et composés exigés par le sujet.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    try:
        # Index uniques
        idx_m = db.membres.create_index([("numero", ASCENDING)], unique=True, name="idx_unique_membres_numero")
        idx_c = db.comptes.create_index([("numero", ASCENDING)], unique=True, name="idx_unique_comptes_numero")

        # Index composés
        idx_t = db.transactions.create_index([("compte", ASCENDING), ("date", DESCENDING)], name="idx_compose_transactions_compte_date")
        idx_p = db.prets.create_index([("membre", ASCENDING), ("statut", ASCENDING)], name="idx_compose_prets_membre_statut")

        print("✓ Index créés avec succès sur MongoDB Atlas :")
        print(f"   • membres: {idx_m}")
        print(f"   • comptes: {idx_c}")
        print(f"   • transactions: {idx_t}")
        print(f"   • prets: {idx_p}")
        return True
    except PyMongoError as e:
        print(f"❌ Erreur lors de la création des index : {e}")
        return False

def lister_index():
    """
    Retourne et affiche la liste des index créés pour chaque collection.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
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

def expliquer_requete(numero_compte="CPT0001", date_debut="2026-01-01", date_fin="2026-12-31"):
    """
    Exécute et affiche de manière synthétique le plan d'exécution (explain)
    d'une recherche de transactions sur une période pour mesurer l'impact de l'index composé.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    filtre = {
        "compte": numero_compte,
        "date": {"$gte": date_debut, "$lte": date_fin + " 23:59:59"}
    }

    try:
        cursor = db.transactions.find(filtre).sort("date", -1)
        plan = cursor.explain()

        # Extraction synthétique et propre des informations d'exécution
        query_planner = plan.get("queryPlanner", {})
        winning_plan = query_planner.get("winningPlan", {})
        execution_stats = plan.get("executionStats", {})

        stage = winning_plan.get("stage", "INCONNU")
        input_stage = winning_plan.get("inputStage", {})
        index_used = input_stage.get("indexName") if input_stage else winning_plan.get("indexName", "Aucun (Scan de collection)")

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
        print("     PLAN D'EXÉCUTION DE REQUÊTE (EXPLAIN)   ")
        print("=============================================")
        print(f"• Filtre de recherche : {summary['requete_filtre']}")
        print(f"• Étape (Stage)        : {summary['etape_principale']}")
        print(f"• Index utilisé        : {summary['index_utilise']}")
        print(f"• Documents examinés   : {summary['documents_examines']}")
        print(f"• Clés examinées       : {summary['cles_index_examinees']}")
        print(f"• Documents retournés   : {summary['documents_retournes']}")
        print(f"• Temps d'exécution    : {summary['temps_execution_ms']} ms")
        print("=============================================\n")

        return summary
    except PyMongoError as e:
        print(f"❌ Erreur lors de l'exécution de explain : {e}")
        return None
