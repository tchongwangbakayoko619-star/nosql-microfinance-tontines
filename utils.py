import json
from datetime import datetime, date
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    """
    Encodeur JSON personnalisé pour gérer les types MongoDB ObjectId et datetime.
    """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o, datetime) else o.strftime("%Y-%m-%d")
        return super().default(o)

def format_fcfa(montant):
    """
    Formate un montant financier en FCFA avec séparateurs.
    """
    try:
        return f"{int(montant):,} FCFA".replace(",", " ")
    except (ValueError, TypeError):
        return f"{montant} FCFA"

def clean_doc_for_display(doc):
    """
    Formate un document PyMongo pour un affichage propre dans le terminal sans l'ObjectId brut.
    """
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d
