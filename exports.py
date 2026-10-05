import os
import csv
import json
from datetime import datetime, date
from bson import ObjectId
from database import get_db
from utils import JSONEncoder

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
JSON_DIR = os.path.join(EXPORTS_DIR, "json")
CSV_DIR = os.path.join(EXPORTS_DIR, "csv")

def assurer_dossiers_exports():
    """
    Crée les dossiers exports/json/ et exports/csv/ s'ils n'existent pas.
    """
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)

def exporter_donnees():
    """
    Exporte l'ensemble des 5 collections principales MongoDB en formats JSON et CSV.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return False

    assurer_dossiers_exports()
    collections = ["membres", "comptes", "transactions", "prets", "tontines"]

    res_json = []
    res_csv = []

    for coll_name in collections:
        try:
            docs = list(db[coll_name].find())
            
            # 1. Export JSON
            json_file = os.path.join(JSON_DIR, f"{coll_name}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(docs, f, cls=JSONEncoder, ensure_ascii=False, indent=2)
            res_json.append(json_file)

            # 2. Export CSV
            csv_file = os.path.join(CSV_DIR, f"{coll_name}.csv")
            if docs:
                # Obtenir la liste de toutes les clés de manière aplatie pour le header CSV
                fieldnames = set()
                flat_docs = []
                for d in docs:
                    flat_d = _aplatir_document(d)
                    fieldnames.update(flat_d.keys())
                    flat_docs.append(flat_d)

                fieldnames = sorted(list(fieldnames))
                # S'assurer que 'numero' ou 'nom' vient en premier s'il existe
                if "numero" in fieldnames:
                    fieldnames.remove("numero")
                    fieldnames.insert(0, "numero")

                with open(csv_file, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(flat_docs)
            else:
                with open(csv_file, "w", encoding="utf-8") as f:
                    f.write("")
            res_csv.append(csv_file)

            print(f"✓ Collection '{coll_name}' exportée : {len(docs)} document(s).")
        except Exception as e:
            print(f"❌ Erreur lors de l'export de {coll_name} : {e}")
            return False

    print("\n✓ Tous les exports ont été générés avec succès dans 'exports/json/' et 'exports/csv/'.")
    return True

def _aplatir_document(doc):
    """
    Formate un document MongoDB complexe pour l'export CSV plat.
    """
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
