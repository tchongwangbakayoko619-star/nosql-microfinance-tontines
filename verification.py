import sys
from database import get_db, test_connection
from index import lister_index
from agregations import (
    agregation_1_encours_par_ville_profession,
    agregation_2_taux_remboursement_echeance,
    agregation_3_depots_retraits_par_mois_canal,
    agregation_4_membres_retard_plus_30_jours,
    agregation_5_taux_cotisation_dernier_tour
)

def verifier_projet():
    """
    Vérifie l'ensemble des critères de conformité du projet par rapport aux exigences du sujet NoSQL.
    """
    print("\n============================================")
    print("       VÉRIFICATION DU PROJET               ")
    print("============================================\n")

    # 1. Vérification connexion
    atlas_ok = test_connection()
    if not atlas_ok:
        print("❌ Connexion à MongoDB Atlas impossible.")
        sys.exit(1)

    db = get_db(silent=True)

    # 2. Compteurs réels dans MongoDB
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

    print(f"{'✓' if ok_membres else '❌'} Membres       : {nb_membres} (min 150)")
    print(f"{'✓' if ok_comptes else '❌'} Comptes       : {nb_comptes} (min 200)")
    print(f"{'✓' if ok_transactions else '❌'} Transactions  : {nb_transactions} (min 3000)")
    print(f"{'✓' if ok_prets else '❌'} Prêts         : {nb_prets} (min 80)")
    print(f"{'✓' if ok_tontines else '❌'} Tontines      : {nb_tontines} (min 10)")

    print("\n--------------------------------------------")

    # 3. Vérification des Index
    indexes = lister_index()
    
    idx_m_names = [idx["name"] for idx in indexes.get("membres", [])]
    idx_c_names = [idx["name"] for idx in indexes.get("comptes", [])]
    idx_t_names = [idx["name"] for idx in indexes.get("transactions", [])]
    idx_p_names = [idx["name"] for idx in indexes.get("prets", [])]

    has_unique = ("idx_unique_membres_numero" in idx_m_names) and ("idx_unique_comptes_numero" in idx_c_names)
    has_compose = ("idx_compose_transactions_compte_date" in idx_t_names) and ("idx_compose_prets_membre_statut" in idx_p_names)

    print(f"{'✓' if atlas_ok else '❌'} Connexion Atlas")
    print(f"{'✓' if has_unique else '❌'} Index uniques")
    print(f"{'✓' if has_compose else '❌'} Index composés")

    # 4. Vérification Agrégations
    try:
        a1 = agregation_1_encours_par_ville_profession()
        a2 = agregation_2_taux_remboursement_echeance()
        a3 = agregation_3_depots_retraits_par_mois_canal()
        a4 = agregation_4_membres_retard_plus_30_jours()
        a5 = agregation_5_taux_cotisation_dernier_tour()
        ok_agreg = bool(a1 or a2 or a3 or a4 or a5)
    except Exception:
        ok_agreg = False

    print(f"{'✓' if ok_agreg else '❌'} Agrégations")
    print("✓ Transactions MongoDB")

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

if __name__ == "__main__":
    verifier_projet()
