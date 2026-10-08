import sys

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = "/"
MONGODB_URI = MONGO_URI

DATABASE_NAME = "projet9_microfinance"

_client = None


def get_client(uri=None):
    """
    Crée et retourne une instance unique du client MongoClient.
    """
    global _client

    target_uri = uri or MONGO_URI

    if _client is None:
        _client = MongoClient(
            target_uri,
            serverSelectionTimeoutMS=3000,
        )

    return _client


def get_database(uri=None, db_name=None):
    """
    Établit la connexion à MongoDB, vérifie avec un ping,
    puis retourne la base de données.
    """
    target_uri = uri or MONGO_URI
    target_db = db_name or DATABASE_NAME

    try:
        client = get_client(target_uri)

        # Vérification de la connexion
        client.admin.command("ping")

        print(f"[OK] Connexion MongoDB réussie.")
        print(f"[OK] Base de données : {target_db}")

        return client[target_db]

    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print(
            f"[ERREUR] Impossible de se connecter à MongoDB "
            f"sur {target_uri}: {e}"
        )
        return None


def get_db():
    """
    Alias de get_database().
    """
    db = get_database()

    if db is None:
        print(
            "[ERREUR CRITIQUE] Connexion MongoDB échouée. "
            "Vérifiez votre URI MongoDB Atlas et votre connexion Internet."
        )

    return db