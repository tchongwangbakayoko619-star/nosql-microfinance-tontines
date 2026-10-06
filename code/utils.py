import random
from datetime import datetime, timedelta

# Codes couleur ANSI pour le terminal
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

def print_erreur(msg):
    print(f"{COLOR_RED}[ERREUR] {msg}{COLOR_RESET}")

def print_succes(msg):
    print(f"{COLOR_GREEN}[SUCCES] {msg}{COLOR_RESET}")

def print_info(msg):
    print(f"{COLOR_YELLOW}[INFO] {msg}{COLOR_RESET}")

def date_aleatoire(debut, fin):
    """
    Génère une date aléatoire entre deux objets datetime.
    """
    ecart = (fin - debut).days
    if ecart <= 0:
        return debut
    return debut + timedelta(days=random.randint(0, ecart))

def formater_montant(montant):
    """
    Formate un montant numérique en chaîne lisible FCFA avec séparateurs de milliers.
    """
    try:
        return f"{float(montant):,.2f} FCFA".replace(",", " ")
    except (ValueError, TypeError):
        return f"{montant} FCFA"

def formater_date(dt):
    """
    Formate un objet datetime ou ISO string en format lisible JJ/MM/AAAA.
    """
    if dt is None:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y %H:%M")
    return str(dt)

def valider_numero(prefixe, nombre, largeur=4):
    """
    Formate un identifiant avec un préfixe et un numéro paddé (ex: MBR-0001).
    """
    return f"{prefixe}-{int(nombre):0{largeur}d}"

def generer_code_auto(collection, prefixe, champ="numero", largeur=4, db=None):
    """
    Génère automatiquement un code séquentiel unique (ex: MBR-0161, CPT-00251, PRT-0101, TNT-013).
    S'appuie sur le max existant dans la collection pour éviter tout doublon.
    """
    if db is None:
        from config import get_db
        db = get_db()
    if db is None:
        # Fallback si pas de DB
        return f"{prefixe}-0001"
    
    pipeline = [
        {"$match": {champ: {"$regex": f"^{prefixe}-\\d+$"}}},
        {"$project": {
            "num_str": {"$arrayElemAt": [{"$split": [f"${champ}", "-"]}, 1]}
        }},
        {"$project": {
            "num_int": {"$toInt": "$num_str"}
        }},
        {"$sort": {"num_int": -1}},
        {"$limit": 1}
    ]
    res = list(collection.aggregate(pipeline))
    if res and "num_int" in res[0] and res[0]["num_int"] is not None:
        prochain = res[0]["num_int"] + 1
    else:
        # Si aucun code formaté standard n'existe, on compte le total des documents + 1
        prochain = collection.count_documents({}) + 1

    return f"{prefixe}-{prochain:0{largeur}d}"

