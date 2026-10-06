import os
import json
import csv
from datetime import datetime
from config import get_db

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def exporter_donnees_json_csv(db=None, base_dir=None):
    """
    Exporte les collections de la base de données au format JSON et CSV.
    """
    if db is None:
        db = get_db()
    if db is None:
        return False

    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    dir_json = os.path.join(base_dir, "exports", "json")
    dir_csv = os.path.join(base_dir, "exports", "csv")
    os.makedirs(dir_json, exist_ok=True)
    os.makedirs(dir_csv, exist_ok=True)

    collections = ["membres", "comptes", "transactions", "prets", "tontines"]

    for col_name in collections:
        docs = list(db[col_name].find())
        
        # 1. Export JSON
        file_json = os.path.join(dir_json, f"{col_name}.json")
        with open(file_json, "w", encoding="utf-8") as f:
            json.dump(docs, f, default=json_serializer, indent=2, ensure_ascii=False)
        
        # 2. Export CSV
        file_csv = os.path.join(dir_csv, f"{col_name}.csv")
        if docs:
            all_keys = set()
            for d in docs:
                all_keys.update(d.keys())
            if "_id" in all_keys:
                all_keys.remove("_id")
            fieldnames = sorted(list(all_keys))

            with open(file_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for d in docs:
                    row = {}
                    for k in fieldnames:
                        val = d.get(k)
                        if isinstance(val, (dict, list)):
                            row[k] = json.dumps(val, default=json_serializer, ensure_ascii=False)
                        elif isinstance(val, datetime):
                            row[k] = val.isoformat()
                        else:
                            row[k] = val
                    writer.writerow(row)

    print("✓ Exports JSON et CSV générés avec succès dans exports/json/ et exports/csv/.")
    return True

def verifier_statistiques_projet(db=None):
    """
    Récupère les statistiques réelles des collections MongoDB du Projet 9.
    """
    if db is None:
        db = get_db()
    if db is None:
        return {}

    stats = {
        "membres": db.membres.count_documents({}),
        "comptes": db.comptes.count_documents({}),
        "transactions": db.transactions.count_documents({}),
        "prets": db.prets.count_documents({}),
        "tontines": db.tontines.count_documents({}),
        "prets_archives": db.prets_archives.count_documents({})
    }
    return stats
