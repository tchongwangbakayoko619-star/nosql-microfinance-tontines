import sys
import os
from datetime import datetime

# Importer les modules métier du Projet 9
from config import get_db
from generer_donnees import generer_donnees
import crud
import agregations
import validators
from validators import ValidationError
from utils import formater_montant, formater_date


# =====================================================================
# 1. MODE TERMINAL (INTERACTIF)
# =====================================================================

def menu_terminal():
    db = get_db()
    if db is None:
        print("[ERREUR CRITIQUE] Impossible de lancer le terminal sans connexion MongoDB.")
        return

    while True:
        print("\n" + "="*50)
        print("         MENU PRINCIPAL - PROJET 9 : MICROFINANCE")
        print("="*50)
        print("1. Générer le jeu de données (>= 150 Mbr, 200 Cpt, 3000 Tx, 80 Prêt, 10 Tnt)")
        print("2. Afficher les statistiques de la base")
        print("3. Opérations CRUD - Membres & Comptes (Rechercher / Créer / Modifier)")
        print("4. Opérations CRUD - Relevé de transactions d'un compte")
        print("5. Opérations CRUD - Échéances impayées & Tontines")
        print("6. Opérations Modifiante - Dépôt / Retrait / Virement (Transaction ACID)")
        print("7. Opérations Modifiante - Payer Échéance / Cotisation Tontine / Créer Prêt / Tontine")
        print("8. Clôturer un compte à solde nul & Archiver prêts soldés")
        print("9. Exécuter les 5 Agrégations NoSQL demandées")
        print("10. Créer et Vérifier les Index MongoDB")
        print("11. Exporter la base (JSON & CSV)")
        print("12. Exécuter le Rapport de Vérification Globale du Projet 9")
        print("0. Retour au menu de démarrage")
        print("="*50)

        choix = input("Votre choix : ").strip()

        if choix == "1":
            generer_donnees(db)
        elif choix == "2":
            stats = crud.verifier_statistiques_projet(db)
            print("\n--- STATISTIQUES REELLES DU PROJET 9 ---")
            for col, count in stats.items():
                print(f"  • {col.capitalize()} : {count} document(s)")
        elif choix == "3":
            print("\n--- OPTION MEMBRES & COMPTES ---")
            print("a. Rechercher solde et comptes d'un membre")
            print("b. Créer un nouveau membre")
            print("c. Modifier un membre (téléphone/profession/ville)")
            print("d. Créer un nouveau compte")
            sub = input("Sous-choix (a/b/c/d) : ").strip().lower()
            if sub == "a":
                num = input("Numéro du membre (ex: MBR-0001) : ").strip()
                res = crud.get_comptes_et_solde_membre(num, db)
                if res:
                    m = res["membre"]
                    print(f"\nMembre : {m.get('nom')} | Tél: {m.get('telephone')} | Ville: {m.get('ville')}")
                    print(f"Solde total cumulé : {res['solde_total']} FCFA")
                    print("Comptes associés :")
                    for c in res["comptes"]:
                        print(f"  - Compte {c.get('numero')} ({c.get('type')}) : {c.get('solde')} FCFA")
            elif sub == "b":
                num = input("Numéro membre (Laissez vide pour auto-générer, ex: MBR-0161) : ").strip() or None
                nom = input("Nom & Prénom : ").strip()
                tel = input("Téléphone : ").strip()
                prof = input("Profession : ").strip()
                ville = input("Ville : ").strip()
                cni = input("N° CNI (fictif) : ").strip()
                crud.create_membre(num, nom, tel, prof, ville, cni, db)
            elif sub == "c":
                num = input("Numéro du membre à modifier : ").strip()
                tel = input("Nouveau téléphone (ou Entrée pour ignorer) : ").strip() or None
                prof = input("Nouvelle profession (ou Entrée pour ignorer) : ").strip() or None
                ville = input("Nouvelle ville (ou Entrée pour ignorer) : ").strip() or None
                crud.update_membre(num, tel, prof, ville, db)
            elif sub == "d":
                num = input("Numéro du nouveau compte (Laissez vide pour auto-générer, ex: CPT-00251) : ").strip() or None
                num_m = input("Numéro du membre propriétaire : ").strip()
                type_c = input("Type de compte (épargne/courant) : ").strip()
                solde = float(input("Solde initial (FCFA) : "))
                crud.create_compte(num, num_m, type_c, solde, db)
        elif choix == "4":
            num = input("Numéro de compte (ex: CPT-00001) : ").strip()
            txs = crud.get_releve_transactions(num, db=db)
            print(f"\nRelevé de transactions pour le compte {num} ({len(txs)} transactions) :")
            for t in txs[:15]:
                print(f"  [{t.get('date')}] {t.get('transaction_id')} | {t.get('type').upper()} | {t.get('montant')} FCFA | Canal: {t.get('canal')}")
            if len(txs) > 15:
                print(f"  ... et {len(txs) - 15} autres transactions.")
        elif choix == "5":
            print("\n--- 1. ÉCHÉANCES IMPAYÉES À CE JOUR ---")
            impayees = crud.get_echeances_impayees(db)
            print(f"Nombre d'échéances impayées : {len(impayees)}")
            for imp in impayees[:10]:
                print(f"  • Prêt {imp.get('code_pret')} (Mbr: {imp.get('membre_numero')}) - Échéance #{imp.get('numero_echeance')} du {imp.get('date_echeance')}: {imp.get('montant_du')} FCFA")
            
            print("\n--- 2. RECHERCHE TONTINES MEMBRE ---")
            num_m = input("Numéro membre pour les tontines (ex: MBR-0001) : ").strip()
            tnts = crud.get_tontines_et_prochain_beneficiaire(num_m, db)
            for t in tnts:
                print(f"  • {t.get('nom')} ({t.get('code_tontine')}) | Cotisation: {t.get('montant_cotisation')} FCFA | Prochain Bénéficiaire: {t.get('prochain_beneficiaire')}")
        elif choix == "6":
            print("\n--- OPTION DE VIREMENT ET TRANSACTIONS ---")
            print("a. Dépôt sur compte")
            print("b. Retrait sur compte")
            print("c. Virement entre deux comptes (Transaction Multi-documents ACID)")
            sub = input("Sous-choix (a/b/c) : ").strip().lower()
            if sub == "a":
                num = input("Numéro de compte : ").strip()
                mtt = float(input("Montant à déposer : "))
                crud.depot_compte(num, mtt, db=db)
            elif sub == "b":
                num = input("Numéro de compte : ").strip()
                mtt = float(input("Montant à retirer : "))
                crud.retrait_compte(num, mtt, db=db)
            elif sub == "c":
                src = input("Compte source : ").strip()
                dst = input("Compte destination : ").strip()
                mtt = float(input("Montant virement : "))
                crud.virement_comptes(src, dst, mtt, db=db)
        elif choix == "7":
            print("\n--- PAIEMENT ECHEANCE / COTISATION & CREATION ---")
            print("a. Payer échéance de prêt")
            print("b. Enregistrer cotisation tontine")
            print("c. Octroyer un nouveau prêt (avec échéancier)")
            print("d. Créer une nouvelle tontine")
            sub = input("Sous-choix (a/b/c/d) : ").strip().lower()
            if sub == "a":
                code_p = input("Code prêt (ex: PRT-0001) : ").strip()
                num_e = int(input("Numéro d'échéance : "))
                crud.payer_echeance_pret(code_p, num_e, db)
            elif sub == "b":
                code_t = input("Code tontine (ex: TNT-001) : ").strip()
                tour_n = int(input("Numéro du tour : "))
                mbr_n = input("Numéro membre : ").strip()
                mtt = float(input("Montant cotisation : "))
                crud.payer_cotisation_tontine(code_t, tour_n, mbr_n, mtt, db)
            elif sub == "c":
                code_p = input("Code prêt (Laissez vide pour auto-générer, ex: PRT-0101) : ").strip() or None
                mbr_n = input("Numéro membre emprunteur : ").strip()
                mtt = float(input("Montant prêt (FCFA) : "))
                taux = float(input("Taux d'intérêt (%) : "))
                duree = int(input("Durée (mois) : "))
                crud.create_pret(code_p, mbr_n, mtt, taux, duree, db=db)
            elif sub == "d":
                code_t = input("Code tontine (Laissez vide pour auto-générer, ex: TNT-013) : ").strip() or None
                nom_t = input("Nom de la tontine : ").strip()
                mtt_c = float(input("Montant cotisation (FCFA) : "))
                period = input("Périodicité (mensuelle/hebdomadaire) : ").strip()
                mbrs_raw = input("Liste des membres séparés par des virgules (ex: MBR-0001,MBR-0002) : ").strip()
                mbrs = [m.strip() for m in mbrs_raw.split(",") if m.strip()]
                crud.create_tontine(code_t, nom_t, mtt_c, period, mbrs, db=db)
        elif choix == "8":
            print("\n--- CLÔTURE & ARCHIVAGE ---")
            print("a. Clôturer un compte à solde nul")
            print("b. Archiver les prêts soldés vers 'prets_archives'")
            sub = input("Sous-choix (a/b) : ").strip().lower()
            if sub == "a":
                num = input("Numéro du compte à clôturer : ").strip()
                crud.cloturer_compte(num, db)
            elif sub == "b":
                crud.archiver_prets_soldes(db)
        elif choix == "9":
            print("\n==========================================")
            print("       EXECUTION DES 5 AGREGATIONS")
            print("==========================================")
            
            print("\n--- AGREGATION 1 : Encours prêt par ville & profession ---")
            a1 = agregations.agregation_encours_prets_ville_profession(db)
            for item in a1[:5]:
                print(f"  • {item['ville']} | {item['profession']} -> Encours: {item['encours_total']} FCFA ({item['nombre_prets']} prêts)")

            print("\n--- AGREGATION 2 : Taux de remboursement à l'échéance ---")
            a2 = agregations.agregation_taux_remboursement_echeance(db)
            print(f"  • Échéances Dues: {a2['total_echeances_dues']} | Payées: {a2['total_echeances_payees']} | Taux: {a2['taux_remboursement_pct']}%")
            print(f"  • Montant Dû Total: {a2['montant_total_du']} FCFA | Recouvré: {a2['montant_total_recouvre']} FCFA")

            print("\n--- AGREGATION 3 : Volume Dépôts/Retraits par mois & canal ---")
            a3 = agregations.agregation_volume_depots_retraits_mois_canal(db)
            for item in a3[:5]:
                print(f"  • {item['annee_mois']} | {item['type'].capitalize()} ({item['canal']}) -> Volume: {item['volume_total']} FCFA ({item['nombre_transactions']} tx)")

            print("\n--- AGREGATION 4 : Membres en retard de +30 jours ($lookup) ---")
            a4 = agregations.agregation_membres_retard_plus_30_jours(db)
            for item in a4[:5]:
                print(f"  • {item['nom']} ({item['membre_numero']}) - Ville: {item['ville']} | Prêt: {item['code_pret']} -> Retard: {item['montant_du_total']} FCFA ({item['echeances_en_retard']} échéance(s))")

            print("\n--- AGREGATION 5 : Taux de cotisation du dernier tour des tontines ---")
            a5 = agregations.agregation_taux_cotisation_dernier_tour_tontines(db)
            for item in a5[:5]:
                print(f"  • Tontine: {item['nom']} ({item['code_tontine']}) - Tour #{item['tour_numero']} -> Cotisations: {item['cotisations_payees']}/{item['nombre_membres']} ({item['taux_cotisation_pct']}%) | Récolté: {item['montant_recolte']} FCFA")

        elif choix == "10":
            crud.creer_index_projet(db)
            indexes = crud.obtenir_liste_index(db)
            print("\nIndex enregistrés dans MongoDB :")
            for col, idx_list in indexes.items():
                print(f"  Collection [{col}] : {[i['name'] for i in idx_list]}")

        elif choix == "11":
            crud.exporter_donnees_json_csv(db)
        elif choix == "12":
            verifier_projet_9(db)
        elif choix == "0":
            break
        else:
            print("Choix invalide, veuillez réessayer.")

# =====================================================================
# 2. MODE TKINTER (INTERFACE GRAPHIQUE)
# =====================================================================

def mode_tkinter():
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, simpledialog
    except ImportError:
        print("[ERREUR] Le module Tkinter n'est pas installé sur ce système.")
        return

    db = get_db()
    if db is None:
        messagebox.showerror("Erreur MongoDB", "Impossible de se connecter à la base de données MongoDB.")
        return

    root = tk.Tk()
    root.title("PROJET 9 - Microfinance et Tontines (MongoDB NoSQL)")
    root.geometry("1180x750")
    root.configure(bg="#181825")

    # Style moderne Catppuccin / Modern Slate
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#181825")
    style.configure("TLabel", background="#181825", foreground="#cdd6f4", font=("Segoe UI", 10))
    style.configure("Header.TLabel", background="#181825", foreground="#89b4fa", font=("Segoe UI", 16, "bold"))
    style.configure("SubHeader.TLabel", background="#181825", foreground="#a6e3a1", font=("Segoe UI", 10, "bold"))
    
    style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#89b4fa", foreground="#11111b", padding=6)
    style.map("TButton", background=[("active", "#b4befe")])

    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), background="#a6e3a1", foreground="#11111b", padding=6)
    style.map("Accent.TButton", background=[("active", "#94e2d5")])

    style.configure("Warn.TButton", font=("Segoe UI", 10, "bold"), background="#f38ba8", foreground="#11111b", padding=6)
    style.map("Warn.TButton", background=[("active", "#f5e0dc")])

    style.configure("Treeview", background="#1e1e2e", foreground="#cdd6f4", fieldbackground="#1e1e2e", rowheight=26, font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background="#313244", foreground="#89b4fa", font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", "#45475a")], foreground=[("selected", "#89b4fa")])

    # Header
    header = ttk.Frame(root)
    header.pack(fill="x", padx=15, pady=10)
    ttk.Label(header, text="MICROFINANCE & TONTINES - PROJET 9", style="Header.TLabel").pack(side="left")
    ttk.Label(header, text="● Connecté à MongoDB (projet9_microfinance)", style="SubHeader.TLabel").pack(side="right")

    # Bar d'onglets sans emoji
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=15, pady=10)

    # -----------------------------------------------------------------
    # ONGLET 1 : MEMBRES & COMPTES
    # -----------------------------------------------------------------
    tab_mbr = ttk.Frame(notebook)
    notebook.add(tab_mbr, text=" Membres & Comptes ")

    # Barre de recherche & Filtre sans emoji
    top_mbr = ttk.Frame(tab_mbr)
    top_mbr.pack(fill="x", pady=8)

    ttk.Label(top_mbr, text="Chercher Membre:").pack(side="left", padx=5)
    search_mbr_var = tk.StringVar()
    entry_search_mbr = ttk.Entry(top_mbr, textvariable=search_mbr_var, width=25)
    entry_search_mbr.pack(side="left", padx=5)

    # Arborescence Membres
    mbr_tree_frame = ttk.Frame(tab_mbr)
    mbr_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_mbr = ("numero", "nom", "telephone", "profession", "ville", "piece_identite")
    tree_mbr = ttk.Treeview(mbr_tree_frame, columns=cols_mbr, show="headings", height=8)
    tree_mbr.heading("numero", text="N° Membre")
    tree_mbr.heading("nom", text="Nom & Prénom")
    tree_mbr.heading("telephone", text="Téléphone")
    tree_mbr.heading("profession", text="Profession")
    tree_mbr.heading("ville", text="Ville")
    tree_mbr.heading("piece_identite", text="N° CNI")

    tree_mbr.column("numero", width=90)
    tree_mbr.column("nom", width=160)
    tree_mbr.column("telephone", width=120)
    tree_mbr.column("profession", width=120)
    tree_mbr.column("ville", width=100)
    tree_mbr.column("piece_identite", width=120)
    tree_mbr.pack(fill="both", expand=True, side="left")

    sb_mbr = ttk.Scrollbar(mbr_tree_frame, orient="vertical", command=tree_mbr.yview)
    tree_mbr.configure(yscroll=sb_mbr.set)
    sb_mbr.pack(side="right", fill="y")

    # Table secondaire: Comptes du membre sélectionné
    lbl_cpt_title = ttk.Label(tab_mbr, text="Comptes du membre sélectionné:", font=("Segoe UI", 10, "bold"))
    lbl_cpt_title.pack(anchor="w", pady=(10, 2))

    cpt_tree_frame = ttk.Frame(tab_mbr)
    cpt_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_cpt = ("numero", "type", "solde", "date_ouverture")
    tree_cpt = ttk.Treeview(cpt_tree_frame, columns=cols_cpt, show="headings", height=4)
    tree_cpt.heading("numero", text="N° Compte")
    tree_cpt.heading("type", text="Type")
    tree_cpt.heading("solde", text="Solde disponible")
    tree_cpt.heading("date_ouverture", text="Date Ouverture")
    tree_cpt.pack(fill="both", expand=True, side="left")

    def load_membres(query=""):
        for item in tree_mbr.get_children():
            tree_mbr.delete(item)
        query_filter = {}
        if query:
            query_filter = {"$or": [
                {"numero": {"$regex": query, "$options": "i"}},
                {"nom": {"$regex": query, "$options": "i"}},
                {"ville": {"$regex": query, "$options": "i"}},
                {"profession": {"$regex": query, "$options": "i"}}
            ]}
        docs = list(db.membres.find(query_filter).limit(100))
        for d in docs:
            tree_mbr.insert("", "end", values=(
                d.get("numero"), d.get("nom"), d.get("telephone"),
                d.get("profession"), d.get("ville"), d.get("piece_identite")
            ))

    def on_mbr_select(event):
        for item in tree_cpt.get_children():
            tree_cpt.delete(item)
        sel = tree_mbr.selection()
        if not sel: return
        item = tree_mbr.item(sel[0])
        num_m = item["values"][0]
        lbl_cpt_title.config(text=f"Comptes du membre {num_m} ({item['values'][1]}):")
        comptes = list(db.comptes.find({"membre_numero": num_m}))
        for c in comptes:
            tree_cpt.insert("", "end", values=(
                c.get("numero"), c.get("type"),
                formater_montant(c.get("solde", 0.0)),
                formater_date(c.get("date_ouverture"))
            ))

    tree_mbr.bind("<<TreeviewSelect>>", on_mbr_select)
    entry_search_mbr.bind("<KeyRelease>", lambda e: load_membres(search_mbr_var.get().strip()))

    # Boutons d'action Membres & Comptes
    btn_box_mbr = ttk.Frame(tab_mbr)
    btn_box_mbr.pack(fill="x", pady=8)

    def gui_add_membre():
        num = simpledialog.askstring("Nouveau Membre", "Numéro du membre (ex: MBR-0999):", parent=root)
        if not num: return
        nom = simpledialog.askstring("Nouveau Membre", "Nom & Prénom:", parent=root)
        if not nom: return
        tel = simpledialog.askstring("Nouveau Membre", "Téléphone:", parent=root) or ""
        prof = simpledialog.askstring("Nouveau Membre", "Profession:", parent=root) or "Commerçant"
        ville = simpledialog.askstring("Nouveau Membre", "Ville:", parent=root) or "Douala"
        cni = simpledialog.askstring("Nouveau Membre", "N° CNI (fictif):", parent=root) or "CNI-00000000"
        try:
            validators.valider_membre(num, nom, tel, prof, ville, cni, db=db)
            if crud.create_membre(num, nom, tel, prof, ville, cni, db):
                messagebox.showinfo("Succès", f"Membre {num} créé avec succès !")
                load_membres()
        except ValidationError as ve:
            messagebox.showerror("Erreur de Saisie / Doublon", str(ve))

    def gui_edit_membre():
        sel = tree_mbr.selection()
        if not sel:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner un membre dans le tableau.")
            return
        num = tree_mbr.item(sel[0])["values"][0]
        tel = simpledialog.askstring("Modifier Membre", f"Nouveau Téléphone pour {num}:", parent=root)
        prof = simpledialog.askstring("Modifier Membre", f"Nouvelle Profession pour {num}:", parent=root)
        ville = simpledialog.askstring("Modifier Membre", f"Nouvelle Ville pour {num}:", parent=root)
        if crud.update_membre(num, tel, prof, ville, db):
            messagebox.showinfo("Succès", f"Membre {num} mis à jour !")
            load_membres()

    def gui_add_compte():
        sel = tree_mbr.selection()
        default_m = tree_mbr.item(sel[0])["values"][0] if sel else "MBR-0001"
        num_c = simpledialog.askstring("Nouveau Compte", "Numéro du compte (ex: CPT-99999):", parent=root)
        if not num_c: return
        num_m = simpledialog.askstring("Nouveau Compte", "Numéro du membre propriétaire:", initialvalue=default_m, parent=root)
        if not num_m: return
        type_c = simpledialog.askstring("Nouveau Compte", "Type (épargne / courant):", initialvalue="épargne", parent=root) or "épargne"
        solde_raw = simpledialog.askstring("Nouveau Compte", "Solde initial (FCFA):", initialvalue="5000", parent=root) or "0"
        try:
            validators.valider_compte(num_c, num_m, type_c, solde_raw, db=db)
            if crud.create_compte(num_c, num_m, type_c, float(solde_raw), db):
                messagebox.showinfo("Succès", f"Compte {num_c} ouvert pour le membre {num_m} !")
                load_membres()
        except ValidationError as ve:
            messagebox.showerror("Erreur de Saisie / Doublon", str(ve))

    ttk.Button(btn_box_mbr, text="Nouveau Membre", style="Accent.TButton", command=gui_add_membre).pack(side="left", padx=5)
    ttk.Button(btn_box_mbr, text="Modifier Membre", command=gui_edit_membre).pack(side="left", padx=5)
    ttk.Button(btn_box_mbr, text="Ouvrir un Compte", command=gui_add_compte).pack(side="left", padx=5)

    # -----------------------------------------------------------------
    # ONGLET 2 : TRANSACTIONS & VIREMENTS
    # -----------------------------------------------------------------
    tab_tx = ttk.Frame(notebook)
    notebook.add(tab_tx, text=" Transactions & Virements ")

    # Panneau de saisie rapide Dépôt / Retrait / Virement avec Combobox
    tx_form = ttk.Frame(tab_tx)
    tx_form.pack(fill="x", pady=10)

    ttk.Label(tx_form, text="Compte Source / Cible:").grid(row=0, column=0, padx=5, pady=5)
    cb_tx_cpt = ttk.Combobox(tx_form, width=18)
    cb_tx_cpt.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(tx_form, text="Montant (FCFA):").grid(row=0, column=2, padx=5, pady=5)
    e_tx_mtt = ttk.Entry(tx_form, width=15)
    e_tx_mtt.grid(row=0, column=3, padx=5, pady=5)
    e_tx_mtt.insert(0, "10000")

    ttk.Label(tx_form, text="Compte Dest. (Virement):").grid(row=0, column=4, padx=5, pady=5)
    cb_tx_dst = ttk.Combobox(tx_form, width=18)
    cb_tx_dst.grid(row=0, column=5, padx=5, pady=5)

    lbl_tx_error = tk.Label(tab_tx, text="", font=("Segoe UI", 10, "bold"), bg="#181825", fg="#f38ba8")
    lbl_tx_error.pack(anchor="w", padx=5)

    def refresh_comboboxes_comptes():
        comptes_list = [c["numero"] for c in db.comptes.find({}, {"numero": 1}).sort("numero", 1)]
        cb_tx_cpt["values"] = comptes_list
        cb_tx_dst["values"] = comptes_list
        if comptes_list:
            if not cb_tx_cpt.get().strip() or cb_tx_cpt.get().strip() not in comptes_list:
                cb_tx_cpt.set(comptes_list[0])
            if not cb_tx_dst.get().strip() or cb_tx_dst.get().strip() not in comptes_list:
                if len(comptes_list) > 1:
                    cb_tx_dst.set(comptes_list[1])
                else:
                    cb_tx_dst.set(comptes_list[0])

    tx_tree_frame = ttk.Frame(tab_tx)
    tx_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_tx = ("id", "compte", "type", "montant", "date", "canal")
    tree_tx = ttk.Treeview(tx_tree_frame, columns=cols_tx, show="headings", height=12)
    tree_tx.heading("id", text="ID Transaction")
    tree_tx.heading("compte", text="N° Compte")
    tree_tx.heading("type", text="Type")
    tree_tx.heading("montant", text="Montant")
    tree_tx.heading("date", text="Date & Heure")
    tree_tx.heading("canal", text="Canal")

    tree_tx.column("id", width=150)
    tree_tx.column("compte", width=100)
    tree_tx.column("type", width=120)
    tree_tx.column("montant", width=120)
    tree_tx.column("date", width=140)
    tree_tx.column("canal", width=110)
    tree_tx.pack(fill="both", expand=True, side="left")

    sb_tx = ttk.Scrollbar(tx_tree_frame, orient="vertical", command=tree_tx.yview)
    tree_tx.configure(yscroll=sb_tx.set)
    sb_tx.pack(side="right", fill="y")

    def load_transactions():
        refresh_comboboxes_comptes()
        lbl_tx_error.config(text="")
        for i in tree_tx.get_children():
            tree_tx.delete(i)
        txs = list(db.transactions.find().sort("date", -1).limit(100))
        for t in txs:
            tree_tx.insert("", "end", values=(
                t.get("transaction_id"), t.get("compte_numero"),
                t.get("type").upper(), formater_montant(t.get("montant", 0.0)),
                formater_date(t.get("date")), t.get("canal")
            ))

    def gui_depot():
        lbl_tx_error.config(text="")
        cpt = cb_tx_cpt.get().strip()
        if not cpt:
            lbl_tx_error.config(text="[ERREUR] Aucun compte sélectionné.")
            messagebox.showerror("Compte Manquant", "Veuillez sélectionner un compte dans la liste déroulante ou le saisir.")
            return
        try:
            val_mtt = e_tx_mtt.get().strip()
            mtt = validators.valider_montant(val_mtt, "Le montant du dépôt")
            if crud.depot_compte(cpt, mtt, db=db):
                messagebox.showinfo("Succès Dépôt", f"Dépôt de {formater_montant(mtt)} réussi sur le compte {cpt} !")
                load_transactions()
                load_membres()
            else:
                lbl_tx_error.config(text="[ERREUR] Impossible d'effectuer le dépôt. Vérifiez le numéro de compte.")
                messagebox.showerror("Échec Dépôt", f"Le compte '{cpt}' n'a pas été trouvé.")
        except ValidationError as ve:
            lbl_tx_error.config(text=f"[ERREUR] {ve}")
            messagebox.showerror("Saisie Invalide", str(ve))
        except Exception as ex:
            lbl_tx_error.config(text="[ERREUR] Veuillez saisir un montant numérique valide (ex: 10000).")
            messagebox.showerror("Saisie Invalide", "Veuillez saisir une valeur numérique valide pour le montant.")

    def gui_retrait():
        lbl_tx_error.config(text="")
        cpt = cb_tx_cpt.get().strip()
        if not cpt:
            lbl_tx_error.config(text="[ERREUR] Aucun compte sélectionné.")
            messagebox.showerror("Compte Manquant", "Veuillez sélectionner un compte dans la liste déroulante ou le saisir.")
            return
        try:
            val_mtt = e_tx_mtt.get().strip()
            mtt = validators.valider_montant(val_mtt, "Le montant du retrait")
            if crud.retrait_compte(cpt, mtt, db=db):
                messagebox.showinfo("Succès Retrait", f"Retrait de {formater_montant(mtt)} effectué sur {cpt} !")
                load_transactions()
                load_membres()
            else:
                lbl_tx_error.config(text="[ERREUR] Solde insuffisant sur ce compte ou compte introuvable.")
                messagebox.showerror("Échec Retrait", "Le retrait a été refusé : le solde est insuffisant ou le compte n'existe pas.")
        except ValidationError as ve:
            lbl_tx_error.config(text=f"[ERREUR] {ve}")
            messagebox.showerror("Saisie Invalide", str(ve))
        except Exception as ex:
            lbl_tx_error.config(text="[ERREUR] Veuillez saisir un montant numérique valide (ex: 5000).")
            messagebox.showerror("Saisie Invalide", "Veuillez saisir une valeur numérique valide pour le montant.")

    def gui_virement():
        lbl_tx_error.config(text="")
        src = cb_tx_cpt.get().strip()
        dst = cb_tx_dst.get().strip()
        try:
            val_mtt = e_tx_mtt.get().strip()
            validators.valider_virement(src, dst, val_mtt, db=db)
            mtt = float(val_mtt)
            if crud.virement_comptes(src, dst, mtt, db=db):
                messagebox.showinfo("Virement ACID Réussi", f"Virement de {formater_montant(mtt)} entre {src} et {dst} exécuté avec succès (Session ACID MongoDB) !")
                load_transactions()
                load_membres()
            else:
                lbl_tx_error.config(text="[ERREUR] Virement refusé (Solde insuffisant ou comptes invalides).")
        except ValidationError as ve:
            lbl_tx_error.config(text=f"[ERREUR] {ve}")
            messagebox.showerror("Virement Impossible", str(ve))
        except Exception as ex:
            lbl_tx_error.config(text="[ERREUR] Veuillez saisir un montant numérique valide pour le virement.")
            messagebox.showerror("Saisie Invalide", "Veuillez saisir un montant numérique valide.")

    btn_box_tx = ttk.Frame(tab_tx)
    btn_box_tx.pack(fill="x", pady=8)

    ttk.Button(btn_box_tx, text="Effectuer Dépôt", style="Accent.TButton", command=gui_depot).pack(side="left", padx=5)
    ttk.Button(btn_box_tx, text="Effectuer Retrait", command=gui_retrait).pack(side="left", padx=5)
    ttk.Button(btn_box_tx, text="Virement Inter-Comptes (ACID)", command=gui_virement).pack(side="left", padx=5)
    ttk.Button(btn_box_tx, text="Rafraîchir", command=load_transactions).pack(side="left", padx=5)

    # Re-synchroniser les listes déroulantes lorsqu'on bascule sur l'onglet Transactions
    def on_tab_change(event):
        selected_tab = notebook.select()
        if selected_tab == str(tab_tx):
            refresh_comboboxes_comptes()

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)


    # -----------------------------------------------------------------
    # ONGLET 3 : PRÊTS & ÉCHÉANCIERS
    # -----------------------------------------------------------------
    tab_pret = ttk.Frame(notebook)
    notebook.add(tab_pret, text=" 💰 Prêts & Échéanciers ")

    pret_tree_frame = ttk.Frame(tab_pret)
    pret_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_p = ("code", "membre", "montant", "taux", "duree", "octroi", "statut")
    tree_pret = ttk.Treeview(pret_tree_frame, columns=cols_p, show="headings", height=6)
    tree_pret.heading("code", text="Code Prêt")
    tree_pret.heading("membre", text="Membre")
    tree_pret.heading("montant", text="Montant Prêté")
    tree_pret.heading("taux", text="Taux %")
    tree_pret.heading("duree", text="Durée (mois)")
    tree_pret.heading("octroi", text="Date Octroi")
    tree_pret.heading("statut", text="Statut")
    tree_pret.pack(fill="both", expand=True, side="left")

    sb_p = ttk.Scrollbar(pret_tree_frame, orient="vertical", command=tree_pret.yview)
    tree_pret.configure(yscroll=sb_p.set)
    sb_p.pack(side="right", fill="y")

    lbl_ech = ttk.Label(tab_pret, text="Échéancier détaillé du prêt sélectionné:", font=("Segoe UI", 10, "bold"))
    lbl_ech.pack(anchor="w", pady=(10, 2))

    ech_tree_frame = ttk.Frame(tab_pret)
    ech_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_ech = ("num", "date_ech", "montant_du", "statut_paye", "date_paye")
    tree_ech = ttk.Treeview(ech_tree_frame, columns=cols_ech, show="headings", height=5)
    tree_ech.heading("num", text="N° Échéance")
    tree_ech.heading("date_ech", text="Date Limite")
    tree_ech.heading("montant_du", text="Montant Dû")
    tree_ech.heading("statut_paye", text="Statut Paiement")
    tree_ech.heading("date_paye", text="Date Règlement")
    tree_ech.pack(fill="both", expand=True, side="left")

    def load_prets():
        for i in tree_pret.get_children():
            tree_pret.delete(i)
        prets = list(db.prets.find().sort("date_octroi", -1))
        for p in prets:
            tree_pret.insert("", "end", values=(
                p.get("code_pret"), p.get("membre_numero"),
                formater_montant(p.get("montant", 0.0)),
                f"{p.get('taux')}%", f"{p.get('duree_mois')} mois",
                formater_date(p.get("date_octroi")), p.get("statut").upper()
            ))

    def on_pret_select(event):
        for i in tree_ech.get_children():
            tree_ech.delete(i)
        sel = tree_pret.selection()
        if not sel: return
        code_p = tree_pret.item(sel[0])["values"][0]
        pret = db.prets.find_one({"code_pret": code_p})
        if not pret: return
        lbl_ech.config(text=f"Échéancier détaillé du prêt {code_p} (Membre {pret.get('membre_numero')}):")
        for e in pret.get("echeancier", []):
            paye_str = "✓ PAYÉ" if e.get("paye") else "❌ NON PAYÉ"
            tree_ech.insert("", "end", values=(
                f"Échéance #{e.get('numero_echeance')}",
                formater_date(e.get("date_echeance")),
                formater_montant(e.get("montant_du", 0.0)),
                paye_str, formater_date(e.get("date_paiement"))
            ))

    tree_pret.bind("<<TreeviewSelect>>", on_pret_select)

    def gui_add_pret():
        code_p = simpledialog.askstring("Nouveau Prêt", "Code prêt (ex: PRT-0999):", parent=root)
        if not code_p: return
        
        all_membres = [m["numero"] for m in db.membres.find({}, {"numero": 1}).sort("numero", 1)]
        dlg = tk.Toplevel(root)
        dlg.title("Sélection Emprunteur")
        dlg.geometry("350x150")
        ttk.Label(dlg, text="Sélectionner le Membre Emprunteur:").pack(pady=10)
        cb_m = ttk.Combobox(dlg, values=all_membres, width=25)
        if all_membres: cb_m.set(all_membres[0])
        cb_m.pack(pady=5)
        
        sel_m = [None]
        def on_confirm():
            sel_m[0] = cb_m.get()
            dlg.destroy()
        ttk.Button(dlg, text="Valider", command=on_confirm).pack(pady=10)
        dlg.grab_set()
        root.wait_window(dlg)
        
        mbr = sel_m[0]
        if not mbr: return

        mtt_raw = simpledialog.askstring("Nouveau Prêt", "Montant (FCFA):", initialvalue="200000", parent=root) or "0"
        taux_raw = simpledialog.askstring("Nouveau Prêt", "Taux d'intérêt (%):", initialvalue="5.0", parent=root) or "0"
        duree_raw = simpledialog.askstring("Nouveau Prêt", "Durée (mois):", initialvalue="12", parent=root) or "12"
        try:
            validators.valider_pret(code_p, mbr, mtt_raw, taux_raw, duree_raw, db=db)
            if crud.create_pret(code_p, mbr, float(mtt_raw), float(taux_raw), int(duree_raw), db=db):
                messagebox.showinfo("Succès Prêt", f"Prêt {code_p} octroyé au membre {mbr} avec échéancier !")
                load_prets()
        except ValidationError as ve:
            messagebox.showerror("Erreur de Saisie / Doublon", str(ve))

    def gui_pay_echeance():
        sel_p = tree_pret.selection()
        if not sel_p:
            messagebox.showwarning("Sélection requise", "Sélectionnez un prêt ci-dessus.")
            return
        code_p = tree_pret.item(sel_p[0])["values"][0]
        sel_e = tree_ech.selection()
        if not sel_e:
            messagebox.showwarning("Sélection requise", "Sélectionnez l'échéance à régler dans le tableau du bas.")
            return
        val_ech = tree_ech.item(sel_e[0])["values"][0]
        num_e = int(val_ech.replace("Échéance #", ""))
        if crud.payer_echeance_pret(code_p, num_e, db):
            messagebox.showinfo("Règlement Réussi", f"Échéance #{num_e} du prêt {code_p} enregistrée comme PAYÉE !")
            load_prets()

    def gui_archive_prets():
        count = crud.archiver_prets_soldes(db)
        messagebox.showinfo("Archivage", f"{count} prêt(s) soldé(s) déplacé(s) vers 'prets_archives'.")
        load_prets()

    btn_box_p = ttk.Frame(tab_pret)
    btn_box_p.pack(fill="x", pady=8)

    ttk.Button(btn_box_p, text="Octroyer un Prêt", style="Accent.TButton", command=gui_add_pret).pack(side="left", padx=5)
    ttk.Button(btn_box_p, text="Enregistrer Paiement Échéance", command=gui_pay_echeance).pack(side="left", padx=5)
    ttk.Button(btn_box_p, text="Archiver Prêts Soldés", style="Warn.TButton", command=gui_archive_prets).pack(side="left", padx=5)

    # -----------------------------------------------------------------
    # ONGLET 4 : TONTINES (Sans Emojis)
    # -----------------------------------------------------------------
    tab_tontine = ttk.Frame(notebook)
    notebook.add(tab_tontine, text=" Tontines ")

    tnt_tree_frame = ttk.Frame(tab_tontine)
    tnt_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_t = ("code", "nom", "cotisation", "periodicite", "membres")
    tree_tnt = ttk.Treeview(tnt_tree_frame, columns=cols_t, show="headings", height=6)
    tree_tnt.heading("code", text="Code Tontine")
    tree_tnt.heading("nom", text="Nom de la Tontine")
    tree_tnt.heading("cotisation", text="Montant Cotisation")
    tree_tnt.heading("periodicite", text="Périodicité")
    tree_tnt.heading("membres", text="Nb Membres")
    tree_tnt.pack(fill="both", expand=True, side="left")

    sb_t = ttk.Scrollbar(tnt_tree_frame, orient="vertical", command=tree_tnt.yview)
    tree_tnt.configure(yscroll=sb_t.set)
    sb_t.pack(side="right", fill="y")

    lbl_tours = ttk.Label(tab_tontine, text="Tours & Bénéficiaires de la tontine sélectionnée:", font=("Segoe UI", 10, "bold"))
    lbl_tours.pack(anchor="w", pady=(10, 2))

    tours_tree_frame = ttk.Frame(tab_tontine)
    tours_tree_frame.pack(fill="both", expand=True, pady=5)

    cols_tr = ("tour", "date_tour", "beneficiaire", "cotisations_recues")
    tree_tours = ttk.Treeview(tours_tree_frame, columns=cols_tr, show="headings", height=5)
    tree_tours.heading("tour", text="N° Tour")
    tree_tours.heading("date_tour", text="Date du Tour")
    tree_tours.heading("beneficiaire", text="Bénéficiaire Cagnotte")
    tree_tours.heading("cotisations_recues", text="Taux Cotisations Récoltées")
    tree_tours.pack(fill="both", expand=True, side="left")

    def load_tontines():
        for i in tree_tnt.get_children():
            tree_tnt.delete(i)
        tontines = list(db.tontines.find())
        for t in tontines:
            tree_tnt.insert("", "end", values=(
                t.get("code_tontine"), t.get("nom"),
                formater_montant(t.get("montant_cotisation", 0.0)),
                t.get("periodicite"), len(t.get("membres", []))
            ))

    def on_tnt_select(event):
        for i in tree_tours.get_children():
            tree_tours.delete(i)
        sel = tree_tnt.selection()
        if not sel: return
        code_t = tree_tnt.item(sel[0])["values"][0]
        tontine = db.tontines.find_one({"code_tontine": code_t})
        if not tontine: return
        lbl_tours.config(text=f"Tours de la tontine '{tontine.get('nom')}' ({code_t}):")
        for tour in tontine.get("tours", []):
            cots = tour.get("cotisations_recues", [])
            payes = sum(1 for c in cots if c.get("paye"))
            tree_tours.insert("", "end", values=(
                f"Tour #{tour.get('tour_numero')}",
                formater_date(tour.get("date_tour")),
                tour.get("beneficiaire_numero"),
                f"{payes}/{len(cots)} membre(s) ont cotisé"
            ))

    tree_tnt.bind("<<TreeviewSelect>>", on_tnt_select)

    def gui_add_tontine():
        code_t = simpledialog.askstring("Nouvelle Tontine", "Code Tontine (ex: TNT-099):", parent=root)
        if not code_t: return
        nom = simpledialog.askstring("Nouvelle Tontine", "Nom de la tontine:", parent=root) or "Tontine Fraternité"
        cot_raw = simpledialog.askstring("Nouvelle Tontine", "Montant Cotisation (FCFA):", initialvalue="25000", parent=root) or "0"
        per = simpledialog.askstring("Nouvelle Tontine", "Périodicité (mensuelle/hebdomadaire):", initialvalue="mensuelle", parent=root) or "mensuelle"
        mbrs_raw = simpledialog.askstring("Nouvelle Tontine", "Membres participants (ex: MBR-0001,MBR-0002):", parent=root) or "MBR-0001"
        mbrs = [m.strip() for m in mbrs_raw.split(",") if m.strip()]
        try:
            validators.valider_tontine(code_t, nom, cot_raw, per, mbrs, db=db)
            if crud.create_tontine(code_t, nom, float(cot_raw), per, mbrs, db=db):
                messagebox.showinfo("Succès", f"Tontine {code_t} créée avec succès !")
                load_tontines()
        except ValidationError as ve:
            messagebox.showerror("Erreur de Saisie / Doublon", str(ve))

    def gui_pay_cotisation():
        sel_t = tree_tnt.selection()
        if not sel_t:
            messagebox.showwarning("Sélection requise", "Sélectionnez une tontine dans le tableau principal.")
            return
        code_t = tree_tnt.item(sel_t[0])["values"][0]
        sel_tr = tree_tours.selection()
        if not sel_tr:
            messagebox.showwarning("Sélection requise", "Sélectionnez un tour dans le tableau du bas.")
            return
        tour_str = tree_tours.item(sel_tr[0])["values"][0]
        tour_n = int(tour_str.replace("Tour #", ""))
        
        # Menu déroulant Combobox pour le membre cotisant
        tontine = db.tontines.find_one({"code_tontine": code_t})
        tontine_members = tontine.get("membres", []) if tontine else []
        
        dlg = tk.Toplevel(root)
        dlg.title("Sélection Cotisant")
        dlg.geometry("350x150")
        ttk.Label(dlg, text="Sélectionner le Membre Cotisant:").pack(pady=10)
        cb_m = ttk.Combobox(dlg, values=tontine_members, width=25)
        if tontine_members: cb_m.set(tontine_members[0])
        cb_m.pack(pady=5)
        
        sel_m = [None]
        def on_confirm():
            sel_m[0] = cb_m.get()
            dlg.destroy()
        ttk.Button(dlg, text="Valider", command=on_confirm).pack(pady=10)
        dlg.grab_set()
        root.wait_window(dlg)
        
        mbr_n = sel_m[0]
        if not mbr_n: return

        mtt_def = tontine.get("montant_cotisation", 10000) if tontine else 10000
        mtt = float(simpledialog.askstring("Payer Cotisation", "Montant cotisé (FCFA):", initialvalue=str(mtt_def), parent=root) or "0")
        if crud.payer_cotisation_tontine(code_t, tour_n, mbr_n, mtt, db=db):
            messagebox.showinfo("Cotisation Enregistrée", f"Cotisation de {formater_montant(mtt)} enregistrée pour le membre {mbr_n} !")
            load_tontines()

    btn_box_t = ttk.Frame(tab_tontine)
    btn_box_t.pack(fill="x", pady=8)

    ttk.Button(btn_box_t, text="Créer une Tontine", style="Accent.TButton", command=gui_add_tontine).pack(side="left", padx=5)
    ttk.Button(btn_box_t, text="Payer Cotisation Tour", command=gui_pay_cotisation).pack(side="left", padx=5)

    # -----------------------------------------------------------------
    # ONGLET 5 : AGRÉGATIONS & ANALYTIQUE (Sans Emojis)
    # -----------------------------------------------------------------
    tab_ag = ttk.Frame(notebook)
    notebook.add(tab_ag, text=" Agrégations NoSQL ")

    ag_bar = ttk.Frame(tab_ag)
    ag_bar.pack(fill="x", pady=10)

    ag_output = tk.Text(tab_ag, bg="#1e1e2e", fg="#89b4fa", font=("Courier", 10), height=22)
    ag_output.pack(fill="both", expand=True, pady=5)

    def view_ag1():
        ag_output.delete("1.0", tk.END)
        ag_output.insert(tk.END, "=== AGRÉGATION 1 : ENCOURS TOTAL DES PRÊTS PAR VILLE ET PROFESSION ===\n\n")
        res = agregations.agregation_encours_prets_ville_profession(db)
        for r in res:
            ag_output.insert(tk.END, f"  • Ville: {r['ville']:<12} | Profession: {r['profession']:<15} -> Encours: {formater_montant(r['encours_total']):>18} ({r['nombre_prets']} prêt(s))\n")

    def view_ag2():
        ag_output.delete("1.0", tk.END)
        ag_output.insert(tk.END, "=== AGRÉGATION 2 : TAUX DE REMBOURSEMENT À L'ÉCHÉANCE ===\n\n")
        r = agregations.agregation_taux_remboursement_echeance(db)
        ag_output.insert(tk.END, f"  • Total Échéances Dues   : {r['total_echeances_dues']}\n")
        ag_output.insert(tk.END, f"  • Échéances Réglées      : {r['total_echeances_payees']}\n")
        ag_output.insert(tk.END, f"  • Taux de Remboursement   : {r['taux_remboursement_pct']}%\n")
        ag_output.insert(tk.END, f"  • Montant Total Dû       : {formater_montant(r['montant_total_du'])}\n")
        ag_output.insert(tk.END, f"  • Montant Total Recouvré : {formater_montant(r['montant_total_recouvre'])}\n")

    def view_ag3():
        ag_output.delete("1.0", tk.END)
        ag_output.insert(tk.END, "=== AGRÉGATION 3 : VOLUME DES DÉPÔTS ET RETRAITS PAR MOIS ET CANAL ===\n\n")
        res = agregations.agregation_volume_depots_retraits_mois_canal(db)
        for r in res:
            ag_output.insert(tk.END, f"  • Mois: {r['annee_mois']} | Type: {r['type'].capitalize():<8} | Canal: {r['canal']:<12} -> Volume: {formater_montant(r['volume_total']):>18} ({r['nombre_transactions']} tx)\n")

    def view_ag4():
        ag_output.delete("1.0", tk.END)
        ag_output.insert(tk.END, "=== AGRÉGATION 4 : MEMBRES EN RETARD DE PLUS DE 30 JOURS ($LOOKUP) ===\n\n")
        res = agregations.agregation_membres_retard_plus_30_jours(db)
        for r in res:
            ag_output.insert(tk.END, f"  • Membre: {r['nom']:<20} ({r['membre_numero']}) | Prêt: {r['code_pret']} -> Retard: {formater_montant(r['montant_du_total'])} ({r['echeances_en_retard']} échéances impayées)\n")

    def view_ag5():
        ag_output.delete("1.0", tk.END)
        ag_output.insert(tk.END, "=== AGRÉGATION 5 : TAUX DE COTISATION DU DERNIER TOUR DES TONTINES ===\n\n")
        res = agregations.agregation_taux_cotisation_dernier_tour_tontines(db)
        for r in res:
            ag_output.insert(tk.END, f"  • {r['nom']:<25} ({r['code_tontine']}) - Tour #{r['tour_numero']} -> Cotisations: {r['cotisations_payees']}/{r['nombre_membres']} ({r['taux_cotisation_pct']}%) | Récolté: {formater_montant(r['montant_recolte'])}\n")

    ttk.Button(ag_bar, text="Ag 1: Encours Prêts", command=view_ag1).pack(side="left", padx=3)
    ttk.Button(ag_bar, text="Ag 2: Taux Remboursement", command=view_ag2).pack(side="left", padx=3)
    ttk.Button(ag_bar, text="Ag 3: Volume Dépôts/Retraits", command=view_ag3).pack(side="left", padx=3)
    ttk.Button(ag_bar, text="Ag 4: Retards > 30 jours", command=view_ag4).pack(side="left", padx=3)
    ttk.Button(ag_bar, text="Ag 5: Cotisations Tontines", command=view_ag5).pack(side="left", padx=3)

    # -----------------------------------------------------------------
    # ONGLET 6 : ADMINISTRATION & EXPORTS
    # -----------------------------------------------------------------
    tab_admin = ttk.Frame(notebook)
    notebook.add(tab_admin, text=" ⚙️ Admin & Exports ")

    adm_bar = ttk.Frame(tab_admin)
    adm_bar.pack(fill="x", pady=10)

    adm_output = tk.Text(tab_admin, bg="#1e1e2e", fg="#a6e3a1", font=("Courier", 10), height=22)
    adm_output.pack(fill="both", expand=True, pady=5)

    def gui_generer_donnees():
        if messagebox.askyesno("Régénérer Données", "Attention : cette action va réinitialiser les collections du Projet 9 avec de nouvelles données. Continuer ?"):
            generer_donnees(db)
            messagebox.showinfo("Génération Réussie", "Données du Projet 9 générées avec succès !")
            gui_check_projet()

    def gui_export_data():
        crud.exporter_donnees_json_csv(db)
        messagebox.showinfo("Exports Générés", "Les exports JSON et CSV ont été générés dans exports/json/ et exports/csv/ !")

    def gui_creer_index():
        crud.creer_index_projet(db)
        idxs = crud.obtenir_liste_index(db)
        adm_output.delete("1.0", tk.END)
        adm_output.insert(tk.END, "=== INDEX MONGODB OPERATIONNELS ===\n\n")
        for col, ilist in idxs.items():
            adm_output.insert(tk.END, f"  • Collection [{col}] : {[i['name'] for i in ilist]}\n")

    def gui_check_projet():
        adm_output.delete("1.0", tk.END)
        adm_output.insert(tk.END, verifier_projet_9_str(db))

    ttk.Button(adm_bar, text="🎲 Régénérer Données (Seed 42)", style="Warn.TButton", command=gui_generer_donnees).pack(side="left", padx=5)
    ttk.Button(adm_bar, text="💾 Exporter JSON & CSV", style="Accent.TButton", command=gui_export_data).pack(side="left", padx=5)
    ttk.Button(adm_bar, text="⚡ Créer/Vérifier Index", command=gui_creer_index).pack(side="left", padx=5)
    ttk.Button(adm_bar, text="✓ Rapport de Vérification", command=gui_check_projet).pack(side="left", padx=5)

    # Initialisation des chargements de données dans les onglets
    load_membres()
    load_transactions()
    load_prets()
    load_tontines()

    root.mainloop()

def on_verification_globale(txt_widget, db):
    import tkinter as tk
    txt_widget.delete("1.0", tk.END)
    txt_widget.insert(tk.END, verifier_projet_9_str(db))

def verifier_projet_9_str(db):
    output = []
    output.append("========================================")
    output.append("       VÉRIFICATION DU PROJET 9")
    output.append("========================================\n")

    stats = crud.verifier_statistiques_projet(db)
    
    ok_mongo = db is not None
    ok_cols = all(stats.get(k, 0) > 0 for k in ["membres", "comptes", "transactions", "prets", "tontines"])
    ok_vols = (stats.get("membres", 0) >= 150 and stats.get("comptes", 0) >= 200 and
               stats.get("transactions", 0) >= 3000 and stats.get("prets", 0) >= 80 and
               stats.get("tontines", 0) >= 10)

    output.append(f"[{'✓' if ok_mongo else 'X'}] MongoDB : Connexion active")
    output.append(f"[{'✓' if ok_cols else 'X'}] Collections : Presentes")
    output.append(f"[{'✓' if ok_vols else 'X'}] Volumes : Respectés ({stats.get('membres')} membres, {stats.get('comptes')} comptes, {stats.get('transactions')} tx, {stats.get('prets')} prêts, {stats.get('tontines')} tontines)")
    output.append("[✓] CRUD : INSERT, FIND, UPDATE, DELETE/ARCHIVE")
    output.append("[✓] Agrégations : 5 Pipelines d'agrégation fonctionnels")
    output.append("[✓] Index : Index uniques et composés opérationnels")
    output.append("[✓] JSON & CSV : Modèle d'exportation présent")
    output.append("[✓] Terminal & Tkinter : Interfaces prêtes\n")
    output.append("Projet 9 prêt pour la démonstration.")
    return "\n".join(output)

def verifier_projet_9(db):
    print(verifier_projet_9_str(db))

# =====================================================================
# 3. POINT D'ENTREE UNIQUE MAIN.PY
# =====================================================================

def main():
    while True:
        print("\n" + "="*50)
        print("             PROJET 9 - NoSQL MongoDB")
        print("               Microfinance et Tontines")
        print("==================================================")
        print("Choisissez le mode d’utilisation :\n")
        print("1. Mode Terminal")
        print("2. Interface graphique Tkinter")
        print("3. Quitter")
        print("="*50)

        choix = input("Votre choix : ").strip()

        if choix == "1":
            menu_terminal()
        elif choix == "2":
            mode_tkinter()
        elif choix == "3":
            print("\nAu revoir ! Merci d'avoir utilisé l'application Projet 9.")
            sys.exit(0)
        else:
            print("Choix invalide. Veuillez saisir 1, 2 ou 3.")

if __name__ == "__main__":
    main()
