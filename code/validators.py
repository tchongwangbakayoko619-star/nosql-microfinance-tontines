"""
Module de validation de données et gestion d'erreurs conviviales pour le Projet 9.
Toutes les erreurs sont rédigées dans un langage clair et compréhensible par des non-informaticiens.
Des vérifications d'unicité (anti-doublons) sont incluses.
"""

class ValidationError(Exception):
    """Exception personnalisée pour les erreurs de validation de données."""
    pass

def valider_montant(montant, nom_champ="Le montant"):
    """
    Vérifie qu'un montant est un nombre positif et non nul.
    """
    if montant is None or str(montant).strip() == "":
        raise ValidationError(f"{nom_champ} ne peut pas être vide. Veuillez saisir une valeur numérique.")
    try:
        val = float(montant)
        if val <= 0:
            raise ValidationError(f"{nom_champ} doit être une valeur supérieure à zero (ex: 5000).")
        return val
    except (ValueError, TypeError):
        raise ValidationError(f"{nom_champ} n'est pas un nombre valide. N'utilisez pas de lettres ni de symboles.")

def valider_membre(numero, nom, telephone, profession, ville, piece_identite, db=None):
    """
    Valide la création d'un membre et vérifie l'absence de doublon sur le numéro.
    """
    num_str = str(numero).strip() if numero else ""
    if not num_str:
        raise ValidationError("Le numéro du membre est obligatoire. Exemple : MBR-0045.")
    if not nom or len(str(nom).strip()) < 2:
        raise ValidationError("Le nom du membre doit comporter au moins 2 lettres.")
    if not piece_identite or not str(piece_identite).strip():
        raise ValidationError("Le numéro de la pièce d'identité est obligatoire.")
    
    # Vérification anti-doublon si la DB est fournie
    if db is not None:
        existant = db.membres.find_one({"numero": num_str})
        if existant:
            raise ValidationError(f"Le membre avec le numéro '{num_str}' existe déjà dans le système. Choisissez un autre numéro.")
    return True

def valider_compte(numero, membre_numero, type_compte, solde_initial, db=None):
    """
    Valide la création d'un compte, vérifie l'existence du membre et l'absence de doublon sur le compte.
    """
    num_cpt = str(numero).strip() if numero else ""
    num_mbr = str(membre_numero).strip() if membre_numero else ""
    
    if not num_cpt:
        raise ValidationError("Le numéro de compte est obligatoire. Exemple : CPT-10045.")
    if not num_mbr:
        raise ValidationError("Veuillez sélectionner ou indiquer le membre propriétaire du compte.")
    
    types_valides = ["épargne", "courant"]
    type_clean = str(type_compte).lower().strip()
    if type_clean not in types_valides:
        raise ValidationError(f"Le type de compte '{type_compte}' n'est pas reconnu. Choisissez soit 'épargne', soit 'courant'.")
    
    try:
        solde = float(solde_initial)
        if solde < 0:
            raise ValidationError("Le solde initial du compte ne peut pas être négatif.")
    except (ValueError, TypeError):
        raise ValidationError("Le solde initial doit être une somme d'argent valide (ex: 5000).")
    
    if db is not None:
        # 1. Vérifier si le compte existe déjà (doublon)
        compte_existant = db.comptes.find_one({"numero": num_cpt})
        if compte_existant:
            raise ValidationError(f"Le compte numéro '{num_cpt}' existe déjà dans le système. Veuillez utiliser un numéro unique.")
        
        # 2. Vérifier si le membre existe bien
        membre_existant = db.membres.find_one({"numero": num_mbr})
        if not membre_existant:
            raise ValidationError(f"Le membre numéro '{num_mbr}' n'existe pas. Veuillez d'abord inscrire ce membre avant de lui créer un compte.")
            
    return True

def valider_virement(compte_src, compte_dest, montant, db=None):
    """
    Valide une opération de virement entre deux comptes.
    """
    c_src = str(compte_src).strip() if compte_src else ""
    c_dst = str(compte_dest).strip() if compte_dest else ""
    
    if not c_src:
        raise ValidationError("Veuillez sélectionner ou saisir le compte source (expéditeur).")
    if not c_dst:
        raise ValidationError("Veuillez sélectionner ou saisir le compte destinataire.")
    if c_src == c_dst:
        raise ValidationError("Le compte expéditeur et le compte destinataire doivent être deux comptes différents.")
    
    mtt = valider_montant(montant, "Le montant du virement")
    
    if db is not None:
        compte_source_doc = db.comptes.find_one({"numero": c_src})
        if not compte_source_doc:
            raise ValidationError(f"Le compte source '{c_src}' n'existe pas dans la base de données.")
        compte_dest_doc = db.comptes.find_one({"numero": c_dst})
        if not compte_dest_doc:
            raise ValidationError(f"Le compte destinataire '{c_dst}' n'existe pas dans la base de données.")
        
        solde_dispo = compte_source_doc.get("solde", 0.0)
        if solde_dispo < mtt:
            raise ValidationError(f"Solde insuffisant sur le compte '{c_src}'. Solde actuel : {solde_dispo:,.0f} FCFA, montant demandé : {mtt:,.0f} FCFA.")
            
    return True

def valider_pret(code_pret, membre_numero, montant, taux, duree_mois, db=None):
    """
    Valide les paramètres d'un prêt et contrôle l'absence de doublons.
    """
    code_p = str(code_pret).strip() if code_pret else ""
    num_m = str(membre_numero).strip() if membre_numero else ""
    
    if not code_p:
        raise ValidationError("Le code du prêt est obligatoire. Exemple : PRT-0045.")
    if not num_m:
        raise ValidationError("Veuillez sélectionner ou saisir le membre emprunteur.")
    
    valider_montant(montant, "Le montant du prêt")
    
    try:
        t = float(taux)
        if t <= 0 or t > 100:
            raise ValidationError("Le taux d'intérêt doit être un pourcentage valide compris entre 0,1% et 100%.")
    except (ValueError, TypeError):
        raise ValidationError("Le taux d'intérêt doit être une valeur numérique (ex: 5 pour 5%).")
        
    try:
        d = int(duree_mois)
        if d <= 0 or d > 120:
            raise ValidationError("La durée du remboursement doit être comprise entre 1 et 120 mois.")
    except (ValueError, TypeError):
        raise ValidationError("La durée du prêt doit être exprimée en nombre entier de mois (ex: 12).")

    if db is not None:
        pret_existant = db.prets.find_one({"code_pret": code_p})
        if pret_existant:
            raise ValidationError(f"Un prêt avec le code '{code_p}' a déjà été enregistré. Veuillez saisir un autre code.")
        membre_doc = db.membres.find_one({"numero": num_m})
        if not membre_doc:
            raise ValidationError(f"Le membre '{num_m}' n'a pas été trouvé dans le système.")

    return True

def valider_tontine(code_tontine, nom, montant_cotisation, periodicite, membres_liste, db=None):
    """
    Valide la création d'une tontine et garantit l'absence de doublons.
    """
    code_t = str(code_tontine).strip() if code_tontine else ""
    nom_t = str(nom).strip() if nom else ""
    
    if not code_t:
        raise ValidationError("Le code de la tontine est obligatoire. Exemple : TON-0012.")
    if not nom_t:
        raise ValidationError("Veuillez donner un nom à la tontine. Exemple : Tontine des Commerçants.")
    
    valider_montant(montant_cotisation, "Le montant de la cotisation")
    
    periodicites = ["mensuelle", "hebdomadaire", "bimensuelle"]
    if str(periodicite).lower().strip() not in periodicites:
        raise ValidationError(f"La périodicité '{periodicite}' n'est pas valide. Choisissez parmi : mensuelle, hebdomadaire, ou bimensuelle.")
        
    if not membres_liste or not isinstance(membres_liste, list) or len(membres_liste) < 1:
        raise ValidationError("Une tontine nécessite au moins un membre inscrit pour fonctionner.")
        
    if db is not None:
        tontine_existante = db.tontines.find_one({"code_tontine": code_t})
        if tontine_existante:
            raise ValidationError(f"La tontine avec le code '{code_t}' existe déjà. Choisissez un autre code.")
            
    return True
