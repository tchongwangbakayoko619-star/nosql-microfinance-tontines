import random
from datetime import datetime, timedelta
from config import get_db
from utils import date_aleatoire

VILLES = ["Douala", "Yaoundé", "Bafoussam", "Garoua", "Bamenda", "Kribi", "Maroua"]
PROFESSIONS = ["Commerçant", "Enseignant", "Agriculteur", "Médecin", "Chauffeur", "Artisan", "Comptable", "Ingénieur", "Couturier"]
NOMS = ["Kamga", "Tchoungui", "Fotso", "Nguema", "Mbarga", "Atangana", "Njoya", "Bello", "Abena", "Ewane", "Kengne", "Fosso", "Mvondo", "Ngo Bassa", "Tagne"]
PRENOMS = ["Paul", "Jean", "Marie", "Kevin", "Ibrahim", "Sandra", "Rose", "Moussa", "Alice", "Chantal", "David", "Grace", "Samuel", "Emmanuel"]
TYPES_COMPTE = ["épargne", "courant"]
CANAUX_TRANSACTION = ["agence", "mobile_money"]
PERIODICITES_TONTINE = ["mensuelle", "hebdomadaire", "bimensuelle"]



def generer_donnees(db=None, num_membres=160, num_comptes=250, num_transactions=3200, num_prets=100, num_tontines=12):
    if db is None:
        db = get_db()
    if db is None:
        print("[ERREUR] Connexion à MongoDB indisponible pour la génération.")
        return False

    print("--- DEBUT DE LA GENERATION DES DONNEES PROJET 9 ---")
    random.seed(42)

    # 1. Génération des Membres (>= 150)
    print(f"Génération de {num_membres} membres...")
    membres = []
    for i in range(1, num_membres + 1):
        num_m = f"MBR-{i:04d}"
        nom = random.choice(NOMS)
        prenom = random.choice(PRENOMS)
        piece_id = f"CNI-{random.randint(10000000, 99999999)}"
        date_adh = date_aleatoire(datetime(2020, 1, 1), datetime(2025, 1, 1))
        
        membres.append({
            "numero": num_m,
            "nom": f"{nom} {prenom}",
            "telephone": f"+2376{random.randint(50000000, 99999999)}",
            "profession": random.choice(PROFESSIONS),
            "ville": random.choice(VILLES),
            "date_adhesion": date_adh,
            "piece_identite": piece_id
        })

    db.membres.delete_many({})
    db.membres.insert_many(membres)
    print(f"✓ {len(membres)} membres insérés.")

    # 2. Génération des Comptes (>= 200)
    print(f"Génération de {num_comptes} comptes...")
    comptes = []
    for i in range(1, num_comptes + 1):
        num_c = f"CPT-{i:05d}"
        membre_ref = random.choice(membres)["numero"]
        type_c = random.choice(TYPES_COMPTE)
        solde_initial = round(random.uniform(5000, 500000), 2)
        date_ouv = date_aleatoire(datetime(2021, 1, 1), datetime(2025, 2, 1))

        comptes.append({
            "numero": num_c,
            "membre_numero": membre_ref,
            "type": type_c,
            "solde": solde_initial,
            "date_ouverture": date_ouv
        })

    db.comptes.delete_many({})
    db.comptes.insert_many(comptes)
    print(f"✓ {len(comptes)} comptes insérés.")

    # 3. Génération des Transactions (>= 3000)
    print(f"Génération de {num_transactions} transactions...")
    transactions = []
    types_trans = ["dépôt", "retrait", "virement", "remboursement"]

    for i in range(1, num_transactions + 1):
        cp = random.choice(comptes)
        num_c = cp["numero"]
        t_type = random.choice(types_trans)
        montant = round(random.uniform(1000, 50000), 2)
        date_t = date_aleatoire(datetime(2024, 1, 1), datetime(2026, 3, 1))
        canal = random.choice(CANAUX_TRANSACTION)

        transactions.append({
            "transaction_id": f"TXN-{i:07d}",
            "compte_numero": num_c,
            "type": t_type,
            "montant": montant,
            "date": date_t,
            "canal": canal
        })

    db.transactions.delete_many({})
    db.transactions.insert_many(transactions)
    print(f"✓ {len(transactions)} transactions insérées.")

    # 4. Génération des Prêts avec Échéancier (>= 80)
    print(f"Génération de {num_prets} prêts...")
    prets = []
    for i in range(1, num_prets + 1):
        code_pret = f"PRT-{i:04d}"
        membre_ref = random.choice(membres)["numero"]
        montant = round(random.uniform(50000, 2000000), 2)
        taux = round(random.uniform(2.5, 8.0), 2)
        duree_mois = random.choice([3, 6, 12, 18, 24])
        date_octroi = date_aleatoire(datetime(2024, 1, 1), datetime(2025, 12, 1))

        # Échéancier
        echeancier = []
        montant_du_par_mois = round(montant / duree_mois, 2)
        # Déterminer statut du prêt (en cours, soldé, en retard)
        statut_options = ["en cours", "soldé", "en retard"]
        statut = random.choice(statut_options)

        for m in range(1, duree_mois + 1):
            date_ech = date_octroi + timedelta(days=30 * m)
            if statut == "soldé":
                paye = True
                date_p = date_ech - timedelta(days=random.randint(0, 5))
            elif statut == "en retard" and date_ech < datetime.now() - timedelta(days=30):
                paye = False
                date_p = None
            else:
                paye = random.choice([True, False])
                date_p = date_ech if paye else None

            echeancier.append({
                "numero_echeance": m,
                "date_echeance": date_ech,
                "montant_du": montant_du_par_mois,
                "paye": paye,
                "date_paiement": date_p
            })

        prets.append({
            "code_pret": code_pret,
            "membre_numero": membre_ref,
            "montant": montant,
            "taux": taux,
            "duree_mois": duree_mois,
            "date_octroi": date_octroi,
            "echeancier": echeancier,
            "statut": statut
        })

    db.prets.delete_many({})
    db.prets.insert_many(prets)
    print(f"✓ {len(prets)} prêts insérés.")

    # 5. Génération des Tontines (>= 10)
    print(f"Génération de {num_tontines} tontines...")
    tontines = []
    noms_tontines = [
        "Tontine de la Solidarité", "Tontine Espoir", "Tontine Entreprise & Progrès",
        "Tontine Les Amis du Quartier", "Tontine Famille Réunie", "Tontine Femmes Dynamiques",
        "Tontine des Commerçants", "Tontine Agences", "Tontine Fraternité",
        "Tontine Emergence", "Tontine Succès", "Tontine Progrès"
    ]

    for i in range(1, num_tontines + 1):
        code_tontine = f"TNT-{i:03d}"
        nom_t = noms_tontines[i - 1] if i - 1 < len(noms_tontines) else f"Tontine Groupe {i}"
        cotisation = random.choice([10000, 25000, 50000, 100000])
        period = random.choice(PERIODICITES_TONTINE)

        # Sélectionner entre 5 et 10 membres pour cette tontine
        m_sample = random.sample([m["numero"] for m in membres], k=random.randint(5, 10))
        
        # Ordre de bénéfice
        ordre_benefice = list(m_sample)
        random.shuffle(ordre_benefice)

        # Tours de cotisation
        tours = []
        date_tour_debut = date_aleatoire(datetime(2024, 6, 1), datetime(2025, 1, 1))

        for idx, ben in enumerate(ordre_benefice):
            date_t = date_tour_debut + timedelta(days=30 * idx)
            cotisations_recues = []
            for m_cot in m_sample:
                # 80% à 100% de chance d'avoir cotisé
                paye = random.random() < 0.85
                cotisations_recues.append({
                    "membre_numero": m_cot,
                    "montant": cotisation if paye else 0,
                    "paye": paye,
                    "date_paye": date_t if paye else None
                })
            
            tours.append({
                "tour_numero": idx + 1,
                "date_tour": date_t,
                "beneficiaire_numero": ben,
                "cotisations_recues": cotisations_recues
            })

        tontines.append({
            "code_tontine": code_tontine,
            "nom": nom_t,
            "montant_cotisation": cotisation,
            "periodicite": period,
            "membres": m_sample,
            "ordre_benefice": ordre_benefice,
            "tours": tours
        })

    db.tontines.delete_many({})
    db.tontines.insert_many(tontines)
    print(f"✓ {len(tontines)} tontines insérées.")

    print("==========================================")
    print("GENERATION DES DONNEES PROJET 9 REUSSIE !")
    print("==========================================")
    return True

if __name__ == "__main__":
    generer_donnees()
