import sys
from config import test_connection, get_db
from generer_donnees import generer_donnees_completes
from crud import (
    creer_membre, obtenir_membre, lister_membres, 
    rechercher_par_ville, rechercher_par_profession, 
    modifier_membre, supprimer_membre,
    creer_compte, obtenir_compte, lister_comptes_membre, 
    lister_comptes_par_type, cloturer_compte,
    effectuer_depot, effectuer_retrait, effectuer_virement, releve_compte,
    creer_pret, obtenir_pret, lister_prets_membre, 
    enregistrer_paiement_echeance, archiver_tous_prets_soldes,
    creer_tontine, ajouter_membre_tontine, lister_tontines_membre, 
    enregistrer_cotisation, determiner_prochain_beneficiaire,
    format_fcfa, clean_doc_for_display,
    creer_index, lister_index, expliciter_requete,
    exporter_donnees, verifier_projet
)
from agregations import (
    agregation_1_encours_par_ville_profession,
    agregation_2_taux_remboursement_echeance,
    agregation_3_depots_retraits_par_mois_canal,
    agregation_4_membres_retard_plus_30_jours,
    agregation_5_taux_cotisation_dernier_tour
)

def afficher_titre():
    print("""
==================================================
       MICROFINANCE ET TONTINES
==================================================
""")

def menu_principal():
    while True:
        afficher_titre()
        print("1. Gestion des membres")
        print("2. Gestion des comptes")
        print("3. Dépôt")
        print("4. Retrait")
        print("5. Virement")
        print("6. Gestion des prêts")
        print("7. Gestion des tontines")
        print("8. Recherches")
        print("9. Agrégations")
        print("10. Index et performances")
        print("11. Exports")
        print("12. Vérification du projet")
        print("13. Exécuter les tests unitaires")
        print("14. Régénérer le jeu de données")
        print("0. Quitter")
        print("==================================================")
        
        choix = input("Faites votre choix (0-14) : ").strip()

        try:
            if choix == "1":
                gerer_membres()
            elif choix == "2":
                gerer_comptes()
            elif choix == "3":
                menu_depot()
            elif choix == "4":
                menu_retrait()
            elif choix == "5":
                menu_virement()
            elif choix == "6":
                gerer_prets()
            elif choix == "7":
                gerer_tontines()
            elif choix == "8":
                menu_recherches()
            elif choix == "9":
                menu_agregations()
            elif choix == "10":
                menu_index_performances()
            elif choix == "11":
                menu_exports()
            elif choix == "12":
                verifier_projet()
            elif choix == "13":
                print("\n Exécution de la suite de tests unitaires...")
                lancer_tests()
            elif choix == "14":
                confirm = input("[Attention] Voulez-vous régénérer les données ? (o/n) : ").lower()
                if confirm == "o":
                    generer_donnees_completes()
            elif choix == "0":
                print("\n Au revoir et merci d'avoir utilisé Microfinance et Tontines !")
                sys.exit(0)
            else:
                print("[Erreur] Choix invalide. Veuillez réessayer.")
        except Exception as e:
            print(f"[Erreur] Une erreur s'est produite : {e}")

        input("\nAppuyez sur Entrée pour continuer...")

# --- SOUS-MENUS CLI ---

def gerer_membres():
    print("\n--- GESTION DES MEMBRES ---")
    print("1. Créer un membre")
    print("2. Consulter un membre")
    print("3. Lister les membres")
    print("4. Rechercher par ville")
    print("5. Rechercher par profession")
    print("6. Modifier les informations d'un membre")
    print("7. Supprimer un membre")
    c = input("Choix : ").strip()

    if c == "1":
        num = input("Numéro de membre (ex: MEM001) : ").strip()
        nom = input("Nom et prénom : ").strip()
        tel = input("Téléphone (ex: 690000000) : ").strip()
        prof = input("Profession : ").strip()
        ville = input("Ville : ").strip()
        pid = input("Pièce d'identité : ").strip()
        creer_membre(num, nom, tel, prof, ville, pid)
    elif c == "2":
        num = input("Numéro du membre : ").strip()
        m = obtenir_membre(num)
        if m:
            print("\n Fiche Membre :")
            for k, v in clean_doc_for_display(m).items():
                print(f"   • {k} : {v}")
    elif c == "3":
        l = lister_membres()
        print(f"\n Liste des {len(l)} premiers membres :")
        for m in l[:15]:
            print(f"   • [{m['numero']}] {m['nom']} - {m['profession']} ({m['ville']})")
    elif c == "4":
        v = input("Ville : ").strip()
        l = rechercher_par_ville(v)
        print(f"\n Membres à {v} ({len(l)}) :")
        for m in l:
            print(f"   • [{m['numero']}] {m['nom']} - {m['telephone']}")
    elif c == "5":
        p = input("Profession : ").strip()
        l = rechercher_par_profession(p)
        print(f"\n Membres exerçant la profession {p} ({len(l)}) :")
        for m in l:
            print(f"   • [{m['numero']}] {m['nom']} - {m['ville']}")
    elif c == "6":
        num = input("Numéro du membre à modifier : ").strip()
        tel = input("Nouveau téléphone (laisser vide si inchangé) : ").strip() or None
        prof = input("Nouvelle profession (laisser vide si inchangé) : ").strip() or None
        ville = input("Nouvelle ville (laisser vide si inchangé) : ").strip() or None
        modifier_membre(num, tel, prof, ville)
    elif c == "7":
        num = input("Numéro du membre à supprimer : ").strip()
        supprimer_membre(num)

def gerer_comptes():
    print("\n--- GESTION DES COMPTES ---")
    print("1. Créer un compte")
    print("2. Consulter un compte")
    print("3. Lister les comptes d'un membre")
    print("4. Lister les comptes par type")
    print("5. Clôturer un compte")
    c = input("Choix : ").strip()

    if c == "1":
        num = input("Numéro de compte (ex: CPT0001) : ").strip()
        mem = input("Numéro de membre associé : ").strip()
        typ = input("Type de compte (epargne/courant) : ").strip()
        solde_init = input("Solde initial (FCFA) : ").strip() or "0"
        creer_compte(num, mem, typ, float(solde_init))
    elif c == "2":
        num = input("Numéro du compte : ").strip()
        c_doc = obtenir_compte(num)
        if c_doc:
            print("\n Détails du compte :")
            for k, v in clean_doc_for_display(c_doc).items():
                if k == "solde":
                    v = format_fcfa(v)
                print(f"   • {k} : {v}")
    elif c == "3":
        mem = input("Numéro du membre : ").strip()
        l = lister_comptes_membre(mem)
        print(f"\n Comptes du membre {mem} ({len(l)}) :")
        for cpt in l:
            print(f"   • [{cpt['numero']}] Type: {cpt['type']} | Solde: {format_fcfa(cpt['solde'])} | Statut: {cpt['statut']}")
    elif c == "4":
        typ = input("Type (epargne/courant) : ").strip()
        l = lister_comptes_par_type(typ)
        print(f"\n Comptes de type '{typ}' ({len(l)}) :")
        for cpt in l[:10]:
            print(f"   • [{cpt['numero']}] Membre: {cpt['membre']} | Solde: {format_fcfa(cpt['solde'])}")
    elif c == "5":
        num = input("Numéro du compte à clôturer : ").strip()
        cloturer_compte(num)

def menu_depot():
    print("\n--- EFFECTUER UN DÉPÔT ---")
    cpt = input("Numéro de compte : ").strip()
    montant = input("Montant (FCFA) : ").strip()
    canal = input("Canal (agence/mobile_money) [par défaut agence] : ").strip() or "agence"
    effectuer_depot(cpt, montant, canal)

def menu_retrait():
    print("\n--- EFFECTUER UN RETRAIT ---")
    cpt = input("Numéro de compte : ").strip()
    montant = input("Montant (FCFA) : ").strip()
    canal = input("Canal (agence/mobile_money) [par défaut agence] : ").strip() or "agence"
    effectuer_retrait(cpt, montant, canal)

def menu_virement():
    print("\n--- EFFECTUER UN VIREMENT (TRANSACTION MONGODB) ---")
    src = input("Compte source (débit) : ").strip()
    dst = input("Compte destination (crédit) : ").strip()
    montant = input("Montant (FCFA) : ").strip()
    canal = input("Canal (agence/mobile_money) [par défaut agence] : ").strip() or "agence"
    effectuer_virement(src, dst, montant, canal)

def gerer_prets():
    print("\n--- GESTION DES PRÊTS ---")
    print("1. Accorder un prêt")
    print("2. Consulter les prêts d'un membre")
    print("3. Enregistrer le paiement d'une échéance")
    print("4. Archiver les prêts soldés")
    c = input("Choix : ").strip()

    if c == "1":
        mem = input("Numéro du membre emprunteur : ").strip()
        m = input("Montant du prêt (FCFA) : ").strip()
        t = input("Taux d'intérêt annuel (%) : ").strip()
        d = input("Durée (mois) : ").strip()
        creer_pret(mem, float(m), float(t), int(d))
    elif c == "2":
        mem = input("Numéro du membre : ").strip()
        prets = lister_prets_membre(mem)
        print(f"\n Prêts du membre {mem} ({len(prets)}) :")
        for p in prets:
            print(f"   • Prêt ID: {p['_id']} | Montant: {format_fcfa(p['montant'])} | Statut: {p['statut']} | Échéances: {len(p['echeancier'])}")
    elif c == "3":
        pid = input("ID du prêt : ").strip()
        idx = input("Numéro de l'échéance à payer (ex: 1, 2...) : ").strip()
        enregistrer_paiement_echeance(pid, int(idx) - 1)
    elif c == "4":
        archiver_tous_prets_soldes()

def gerer_tontines():
    print("\n--- GESTION DES TONTINES ---")
    print("1. Créer une tontine")
    print("2. Ajouter un membre à une tontine")
    print("3. Consulter les tontines d'un membre")
    print("4. Enregistrer une cotisation")
    print("5. Déterminer le prochain bénéficiaire")
    c = input("Choix : ").strip()

    if c == "1":
        nom = input("Nom de la tontine : ").strip()
        m = input("Montant de cotisation (FCFA) : ").strip()
        p = input("Périodicité (mensuelle/hebdomadaire) [mensuelle] : ").strip() or "mensuelle"
        m_list = input("Liste des numéros de membres séparés par des virgules (ex: MEM001,MEM002) : ").strip().split(",")
        m_list = [x.strip() for x in m_list if x.strip()]
        creer_tontine(nom, float(m), p, m_list)
    elif c == "2":
        nom = input("Nom de la tontine : ").strip()
        mem = input("Numéro du membre à ajouter : ").strip()
        ajouter_membre_tontine(nom, mem)
    elif c == "3":
        mem = input("Numéro du membre : ").strip()
        l = lister_tontines_membre(mem)
        print(f"\n Tontines de {mem} ({len(l)}) :")
        for t in l:
            prochain = determiner_prochain_beneficiaire(t["nom"])
            print(f"   • Tontine '{t['nom']}' | Cotisation: {format_fcfa(t['montant_cotisation'])} | Prochain bénéficiaire: {prochain}")
    elif c == "4":
        nom = input("Nom de la tontine : ").strip()
        mem = input("Numéro du membre cotisant : ").strip()
        m = input("Montant cotisé (FCFA) : ").strip()
        enregistrer_cotisation(nom, mem, float(m))
    elif c == "5":
        nom = input("Nom de la tontine : ").strip()
        b = determiner_prochain_beneficiaire(nom)
        if b:
            print(f" Le prochain bénéficiaire de la tontine '{nom}' est : {b}")

def menu_recherches():
    print("\n--- RECHERCHES FIND OBLIGATOIRES ---")
    print("1. Comptes et solde d'un membre")
    print("2. Relevé des transactions d'un compte sur une période")
    print("3. Échéances de prêt impayées à ce jour")
    print("4. Tontines d'un membre et son prochain bénéficiaire")
    c = input("Choix (1-4) : ").strip()

    if c == "1":
        mem = input("Numéro du membre (ex: MEM001) : ").strip()
        l = lister_comptes_membre(mem)
        print(f"\n Comptes et soldes de {mem} :")
        solde_total = 0
        for cpt in l:
            print(f"   • Compte {cpt['numero']} ({cpt['type']}) : {format_fcfa(cpt['solde'])} [{cpt['statut']}]")
            solde_total += cpt['solde']
        print(f"    Solde global cumulé : {format_fcfa(solde_total)}")
    elif c == "2":
        cpt = input("Numéro de compte (ex: CPT0001) : ").strip()
        d_debut = input("Date début (YYYY-MM-DD) [optionnel] : ").strip() or None
        d_fin = input("Date fin (YYYY-MM-DD) [optionnel] : ").strip() or None
        res = releve_compte(cpt, d_debut, d_fin)
        print(f"\n Relevé de compte {cpt} ({len(res)} transactions) :")
        for t in res[:20]:
            ref = t.get("reference") or t.get("reference_virement") or "N/A"
            print(f"   • [{t['date']}] {t['type'].upper()} | {format_fcfa(t['montant'])} | Canal: {t['canal']} | Réf: {ref}")
    elif c == "3":
        db = get_db()
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        pipeline = [
            {"$unwind": "$echeancier"},
            {"$match": {"echeancier.paye": False, "echeancier.date": {"$lte": today}}},
            {"$project": {"_id": 0, "membre": 1, "date_echeance": "$echeancier.date", "montant_du": "$echeancier.montant_du", "num_echeance": "$echeancier.num_echeance"}}
        ]
        res = list(db.prets.aggregate(pipeline))
        print(f"\n[Attention] Échéances impayées à ce jour ({len(res)}) :")
        for e in res[:15]:
            print(f"   • Membre: {e['membre']} | Échéance n°{e['num_echeance']} | Due le: {e['date_echeance']} | Montant: {format_fcfa(e['montant_du'])}")
    elif c == "4":
        mem = input("Numéro du membre : ").strip()
        l = lister_tontines_membre(mem)
        print(f"\n Tontines de {mem} :")
        for t in l:
            b = determiner_prochain_beneficiaire(t["nom"])
            print(f"   • [{t['nom']}] Cotisation: {format_fcfa(t['montant_cotisation'])} | Prochain bénéficiaire: {b}")

def menu_agregations():
    print("\n--- AGRÉGATIONS MONGODB PIPELINES ---")
    print("1. Encours total des prêts par ville et profession")
    print("2. Taux de remboursement à l'échéance")
    print("3. Volume des dépôts et retraits par mois et canal")
    print("4. Membres en retard de plus de 30 jours ($lookup + $unwind)")
    print("5. Taux de cotisation du dernier tour de chaque tontine")
    c = input("Choix (1-5) : ").strip()

    if c == "1":
        res = agregation_1_encours_par_ville_profession()
        print("\n Encours total des prêts par ville et profession :")
        for r in res[:15]:
            print(f"   • {r['ville']} | {r['profession']} : {r['nombre_prets']} prêt(s) | Total encours: {format_fcfa(r['encours_total'])}")
    elif c == "2":
        res = agregation_2_taux_remboursement_echeance()
        print("\n Taux de remboursement à l'échéance :")
        print(f"   • Total échéances dues : {res.get('total_echeances_dues')}")
        print(f"   • Échéances payées à temps : {res.get('echeances_payees_temps')}")
        print(f"    Taux de remboursement : {res.get('taux_remboursement_pct', 0):.2f} %")
    elif c == "3":
        res = agregation_3_depots_retraits_par_mois_canal()
        print("\n Dépôts et retraits par mois et canal :")
        for r in res[:15]:
            print(f"   • Mois: {r['mois']} | Canal: {r['canal']} | Dépôts: {format_fcfa(r['total_depots'])} | Retraits: {format_fcfa(r['total_retraits'])}")
    elif c == "4":
        res = agregation_4_membres_retard_plus_30_jours()
        print(f"\n Membres en retard > 30 jours ({len(res)}) :")
        for r in res[:15]:
            print(f"   • [{r['numero_membre']}] {r['nom_membre']} ({r['ville']} - {r['profession']}) | Retard: {int(r['jours_retard'])} jours | Dû: {format_fcfa(r['montant_du'])}")
    elif c == "5":
        res = agregation_5_taux_cotisation_dernier_tour()
        print("\n Taux de cotisation du dernier tour des tontines :")
        for r in res:
            print(f"   • [{r['tontine']}] Tour du {r['date_dernier_tour']} | Bénéficiaire: {r['beneficiaire']} | Reçu: {format_fcfa(r['cotisations_recues'])} / Attendus: {format_fcfa(r['cotisations_attendues'])} ({r['taux_cotisation_pct']:.1f}%)")

def menu_index_performances():
    print("\n--- INDEX ET PERFORMANCES ---")
    print("1. Créer les index sur MongoDB Atlas")
    print("2. Lister les index existants par collection")
    print("3. Exécuter un Explain sur les transactions d'un compte sur une période")
    c = input("Choix (1-3) : ").strip()

    if c == "1":
        creer_index()
    elif c == "2":
        idxs = lister_index()
        for coll, list_i in idxs.items():
            print(f"\n Collection '{coll}' ({len(list_i)} index) :")
            for idx in list_i:
                print(f"   • Nom: {idx.get('name')} | Clés: {idx.get('key')}")
    elif c == "3":
        cpt = input("Numéro de compte (défaut CPT0001) : ").strip() or "CPT0001"
        expliquer_requete(cpt)

def menu_exports():
    print("\n--- EXPORTS DES DONNÉES ---")
    exporter_donnees()

if __name__ == "__main__":
    menu_principal()
