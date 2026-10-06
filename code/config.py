import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "projet9_microfinance"

_client = None

def get_client(uri=None):
    """
    Crée et retourne une instance unique du client MongoClient.
    """
    global _client
    target_uri = uri or MONGODB_URI
    if _client is None:
        _client = MongoClient(target_uri, serverSelectionTimeoutMS=3000)
    return _client

def get_database(uri=None, db_name=None):
    """
    Etablit la connexion à MongoDB, vérifie avec un ping, et retourne la base de données.
    """
    client = get_client(uri)
    target_db = db_name or DATABASE_NAME
    try:
        # Vérification de la connexion
        client.admin.command('ping')
        return client[target_db]
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print(f"[ERREUR] Impossible de se connecter à MongoDB sur {target_uri}: {e}")
        return None

def get_db():
    """
    Alias pour get_database() pour la comptabilité du projet.
    """
    db = get_database()
    if db is None:
        print("[ERREUR CRITIQUE] Connexion MongoDB échouée. Vérifiez que MongoDB est démarré.")
    return db
