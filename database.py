import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import MONGO_URI, MONGO_DB

_client = None

def get_client(silent=False):
    """
    Crée ou retourne le singleton MongoClient.
    Vérifie la connexion avec ping.
    """
    global _client
    if _client is None:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            if not silent:
                print("✓ Connexion à MongoDB Atlas réussie.")
            _client = client
        except PyMongoError:
            print("❌ Connexion à MongoDB Atlas impossible.")
            return None
        except Exception:
            print("❌ Connexion à MongoDB Atlas impossible.")
            return None
    return _client

def get_db(silent=True):
    """
    Renvoie l'instance de la base de données MongoDB.
    """
    client = get_client(silent=silent)
    if client is not None:
        return client[MONGO_DB]
    return None

def test_connection():
    """
    Fonction utilitaire pour tester et afficher le statut de connexion.
    """
    db = get_db(silent=False)
    return db is not None
