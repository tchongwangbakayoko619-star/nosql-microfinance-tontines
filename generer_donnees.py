import random
from datetime import datetime, timedelta
from config import get_db
from crud import creer_index, calculer_echeancier

# Reproductibilité garantie par la graine 42
random.seed(42)

VILLES = [
    "Douala", "Yaoundé", "Bafoussam", "Bamenda", 
    "Garoua", "Maroua", "Kribi", "Limbe", "Buea"
]

PROFESSIONS = [
    "Commerçant", "Enseignant", "Informaticien", "Comptable", 
    "Entrepreneur", "Infirmier", "Médecin", "Agriculteur", 
    "Chauffeur", "Fonctionnaire", "Étudiant", "Artisan"
]

NOMS = [
    "Mbarga", "Ngo Bassa", "Fotso", "Atangana", "Njoya", "Ekane", 
    "Tchoupo", "Bello", "Kamga", "Abena", "Eto'o", "Moukandjo",
    "Song", "Njitap", "Onana", "Aboubakar", "Zambo", "Mbeumo",
    "Kunde", "Toko", "Bassogog", "Ganago", "Castelletto", "Wooh"
]

PRENOMS = [
    "Aline", "Paul", "Kevin", "Marie", "Ibrahim", "Sandra", "Rose", 
    "Moussa", "Jean", "Grace", "Samuel", "Vincent", "Emmanuel", "Chantal",
    "Patrick", "Eric", "Fabrice", "Vanessa", "Patricia", "Cedric"
]

CANAUX = ["agence", "mobile_money"]
TYPES_COMPTE = ["epargne", "courant"]
TYPES_TRANSACTION = ["depot", "retrait", "virement"]

def date_aleatoire(debut, fin):
    """Génère une date aléatoire au format YYYY-MM-DD HH:MM:SS entre deux dates."""
    ecart = int((fin - debut).total_seconds())
    secondes_alea = random.randint(0, ecart)
    date_res = debut + timedelta(seconds=secondes_alea)
    return date_res.strftime("%Y-%m-%d %H:%M:%S")

def generer_donnees_completes(nb_membres=200, nb_comptes=250, nb_trans=3500, nb_prets=100, nb_tontines=12):
    """
    Génère un jeu de données complet, cohérent et réaliste pour MongoDB Atlas.
    """
    db = get_db()
    if db is None:
        print("[Erreur] Connexion à MongoDB Atlas impossible.")
        return False

    print("Initialisation du nettoyage des collections existantes...")
    db.membres.delete_many({})
    db.comptes.delete_many({})
    db.transactions.delete_many({})
    db.prets.delete_many({})
    db.prets_archives.delete_many({})
    db.tontines.delete_many({})

    print("Création des index obligatoires...")
    creer_index()

    debut_periode = datetime(2025, 1, 1)
    fin_periode = datetime(2026, 10, 1)

    # 1. Génération des Membres (200)
    print(f" Génération de {nb_membres} membres...")
    list_membres = []
    for i in range(1, nb_membres + 1):
        num_mem = f"MEM{i:03d}"
        nom_complet = f"{random.choice(NOMS)} {random.choice(PRENOMS)}"
        tel = f"6{random.randint(50000000, 99999999)}"
        prof = random.choice(PROFESSIONS)
        ville = random.choice(VILLES)
        date_adh = date_aleatoire(debut_periode, datetime(2025, 6, 1))[:10]
        piece_id = f"ID{random.randint(100000, 999999)}"

        list_membres.append({
            "numero": num_mem,
            "nom": nom_complet,
            "telephone": tel,
            "profession": prof,
            "ville": ville,
            "date_adhesion": date_adh,
            "piece_identite": piece_id
        })

    db.membres.insert_many(list_membres)

    # 2. Génération des Comptes (250)
    print(f"Génération de {nb_comptes} comptes...")
    list_comptes = []
    soldes_tracker = {}

    for i in range(1, nb_comptes + 1):
        num_cpt = f"CPT{i:04d}"
        # Chaque compte appartient à un membre existant
        num_mem = list_membres[(i - 1) % nb_membres]["numero"]
        type_cpt = random.choice(TYPES_COMPTE)
        solde_initial = 0.0

        list_comptes.append({
            "numero": num_cpt,
            "membre": num_mem,
            "type": type_cpt,
            "solde": solde_initial,
            "date_ouverture": date_aleatoire(debut_periode, datetime(2025, 6, 1))[:10],
            "statut": "actif"
        })
        soldes_tracker[num_cpt] = solde_initial

    db.comptes.insert_many(list_comptes)

    # 3. Génération des Transactions (3500)
    print(f"Génération de {nb_trans} transactions avec mise à jour des soldes...")
    list_transactions = []
    codes_comptes = [c["numero"] for c in list_comptes]

    for i in range(1, nb_trans + 1):
        cpt = random.choice(codes_comptes)
        type_t = random.choice(TYPES_TRANSACTION)
        canal = random.choice(CANAUX)
        dt = date_aleatoire(debut_periode, fin_periode)

        if type_t == "depot":
            montant = float(random.randint(5, 200) * 5000)  # 25 000 à 1 000 000 FCFA
            soldes_tracker[cpt] += montant
            list_transactions.append({
                "compte": cpt,
                "type": "depot",
                "montant": montant,
                "date": dt,
                "canal": canal,
                "reference": f"DEP-{i:06d}"
            })
        elif type_t == "retrait":
            montant = float(random.randint(2, 50) * 5000)
            if soldes_tracker[cpt] >= montant:
                soldes_tracker[cpt] -= montant
                list_transactions.append({
                    "compte": cpt,
                    "type": "retrait",
                    "montant": montant,
                    "date": dt,
                    "canal": canal,
                    "reference": f"RET-{i:06d}"
                })
            else:
                # Si solde insuffisant, faire un dépôt au lieu du retrait pour maintenir un solde >= 0
                montant_depot = float(random.randint(10, 100) * 5000)
                soldes_tracker[cpt] += montant_depot
                list_transactions.append({
                    "compte": cpt,
                    "type": "depot",
                    "montant": montant_depot,
                    "date": dt,
                    "canal": canal,
                    "reference": f"DEP-{i:06d}"
                })
        else:  # Virement
            cpt_dst = random.choice(codes_comptes)
            while cpt_dst == cpt:
                cpt_dst = random.choice(codes_comptes)

            montant = float(random.randint(2, 30) * 5000)
            if soldes_tracker[cpt] >= montant:
                soldes_tracker[cpt] -= montant
                soldes_tracker[cpt_dst] += montant
                ref_vir = f"VIR-{i:06d}"
                list_transactions.append({
                    "compte": cpt,
                    "type": "virement",
                    "montant": montant,
                    "date": dt,
                    "canal": canal,
                    "compte_source": cpt,
                    "compte_destination": cpt_dst,
                    "reference_virement": ref_vir,
                    "sens": "debit"
                })
                list_transactions.append({
                    "compte": cpt_dst,
                    "type": "virement",
                    "montant": montant,
                    "date": dt,
                    "canal": canal,
                    "compte_source": cpt,
                    "compte_destination": cpt_dst,
                    "reference_virement": ref_vir,
                    "sens": "credit"
                })

    db.transactions.insert_many(list_transactions)

    # Mise à jour des soldes finaux des comptes dans MongoDB
    for num_cpt, solde_final in soldes_tracker.items():
        db.comptes.update_one({"numero": num_cpt}, {"$set": {"solde": round(solde_final, 2)}})

    # 4. Génération des Prêts (100)
    print(f"Génération de {nb_prets} prêts avec leurs échéanciers...")
    list_prets = []
    
    for i in range(1, nb_prets + 1):
        mem = list_membres[(i - 1) % nb_membres]["numero"]
        montant_pret = float(random.randint(10, 100) * 50000)  # 500 000 à 5 000 000 FCFA
        taux_pret = float(random.choice([5.0, 7.5, 10.0, 12.0]))
        duree_mois = random.choice([6, 12, 18, 24])
        dt_octroi = date_aleatoire(datetime(2025, 1, 1), datetime(2025, 12, 1))[:10]

        ech = calculer_echeancier(montant_pret, taux_pret, duree_mois, dt_octroi)

        # Simulation de paiements partiels sur l'échéancier
        statut_pret = "en_cours"
        toutes_payees = True
        a_du_retard = False
        today_str = datetime.now().strftime("%Y-%m-%d")

        for item in ech:
            # Payer aléatoirement certaines échéances antérieures
            if item["date"] < today_str:
                if random.random() < 0.75:  # 75% de chance de paiement à temps
                    item["paye"] = True
                    item["date_paiement"] = item["date"]
                else:
                    item["paye"] = False
                    a_du_retard = True
                    toutes_payees = False
            else:
                toutes_payees = False

        if toutes_payees:
            statut_pret = "solde"
        elif a_du_retard:
            statut_pret = "en_retard"
        else:
            statut_pret = "en_cours"

        list_prets.append({
            "membre": mem,
            "montant": montant_pret,
            "taux": taux_pret,
            "duree": duree_mois,
            "date_octroi": dt_octroi,
            "echeancier": ech,
            "statut": statut_pret
        })

    db.prets.insert_many(list_prets)

    # 5. Génération des Tontines (12)
    print(f" Génération de {nb_tontines} tontines...")
    noms_tontine = [
        "Tontine Solidarité Douala", "Tontine Espoir Yaoundé", "Tontine Mifi Bafoussam",
        "Tontine Dynamique Garoua", "Tontine Phénix Bamenda", "Tontine Fraternité Kribi",
        "Tontine Progrès Maroua", "Tontine Succès Limbe", "Tontine Horizon Buea",
        "Tontine Émergence Douala", "Tontine Union Yaoundé", "Tontine Alliance Bafoussam"
    ]

    list_tontines = []
    for i in range(nb_tontines):
        nom_t = noms_tontine[i]
        cotisation_amt = float(random.choice([10000, 25000, 50000, 100000]))
        # 10 à 20 membres par tontine piochés dans les membres existants
        membres_tontine = random.sample([m["numero"] for m in list_membres], k=random.randint(10, 20))
        ordre_benef = list(membres_tontine)

        # Générer 2 à 5 tours réalisés avec cotisations reçues
        tours = []
        nb_tours = random.randint(2, 5)
        for t_idx in range(nb_tours):
            benef = ordre_benef[t_idx % len(ordre_benef)]
            date_tour = (datetime(2025, 6, 1) + timedelta(days=30 * t_idx)).strftime("%Y-%m-%d")
            
            cots = []
            for m_cot in membres_tontine:
                # 90% des membres ont cotisé
                if random.random() < 0.90:
                    cots.append({
                        "membre": m_cot,
                        "montant": cotisation_amt
                    })

            tours.append({
                "date": date_tour,
                "beneficiaire": benef,
                "cotisations_recues": cots
            })

        list_tontines.append({
            "nom": nom_t,
            "montant_cotisation": cotisation_amt,
            "periodicite": "mensuelle",
            "membres": membres_tontine,
            "ordre_benefice": ordre_benef,
            "tours": tours
        })

    db.tontines.insert_many(list_tontines)

    print("\n Génération des données terminée avec succès !")
    print(f"   • Membres: {db.membres.count_documents({})}")
    print(f"   • Comptes: {db.comptes.count_documents({})}")
    print(f"   • Transactions: {db.transactions.count_documents({})}")
    print(f"   • Prêts: {db.prets.count_documents({})}")
    print(f"   • Tontines: {db.tontines.count_documents({})}")
    return True

if __name__ == "__main__":
    generer_donnees_completes()
