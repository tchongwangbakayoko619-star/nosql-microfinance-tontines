from datetime import datetime
from pymongo.errors import PyMongoError
from database import get_db
from utils import format_fcfa

def agregation_1_encours_par_ville_profession():
    """
    Agrégation 1 : Encours total des prêts par ville et par profession.
    Effectue un $lookup de 'prets' vers 'membres' sur la référence du membre.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    pipeline = [
        # Jointure avec la collection membres
        {
            "$lookup": {
                "from": "membres",
                "localField": "membre",
                "foreignField": "numero",
                "as": "info_membre"
            }
        },
        {"$unwind": "$info_membre"},
        # Regroupement par ville et profession du membre
        {
            "$group": {
                "_id": {
                    "ville": "$info_membre.ville",
                    "profession": "$info_membre.profession"
                },
                "nombre_prets": {"$sum": 1},
                "encours_total": {"$sum": "$montant"}
            }
        },
        # Tri descendant par encours total
        {"$sort": {"encours_total": -1}},
        # Projection pour sortie lisible
        {
            "$project": {
                "_id": 0,
                "ville": "$_id.ville",
                "profession": "$_id.profession",
                "nombre_prets": 1,
                "encours_total": 1
            }
        }
    ]

    try:
        results = list(db.prets.aggregate(pipeline))
        return results
    except PyMongoError:
        print("❌ Erreur lors de l'exécution de l'Agrégation 1.")
        return []

def agregation_2_taux_remboursement_echeance():
    """
    Agrégation 2 : Taux de remboursement à l'échéance.
    Calculé 100% dans le pipeline MongoDB Aggregation :
    (échéances payées à temps / échéances dues) * 100
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return None

    pipeline = [
        {"$unwind": "$echeancier"},
        {
            "$group": {
                "_id": None,
                "total_echeances_dues": {"$sum": 1},
                "echeances_payees_temps": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$echeancier.paye", True]},
                            1,
                            0
                        ]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_echeances_dues": 1,
                "echeances_payees_temps": 1,
                "taux_remboursement_pct": {
                    "$multiply": [
                        {"$divide": ["$echeances_payees_temps", {"$cond": [{"$eq": ["$total_echeances_dues", 0]}, 1, "$total_echeances_dues"]}]},
                        100
                    ]
                }
            }
        }
    ]

    try:
        res = list(db.prets.aggregate(pipeline))
        return res[0] if res else {"total_echeances_dues": 0, "echeances_payees_temps": 0, "taux_remboursement_pct": 0.0}
    except PyMongoError:
        print("❌ Erreur lors de l'exécution de l'Agrégation 2.")
        return None

def agregation_3_depots_retraits_par_mois_canal():
    """
    Agrégation 3 : Volume des dépôts et retraits par mois et par canal.
    Utilise $match, $group, $sum, $dateToString.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    pipeline = [
        {"$match": {"type": {"$in": ["depot", "retrait"]}}},
        {
            "$project": {
                "canal": 1,
                "type": 1,
                "montant": 1,
                "mois": {"$substr": ["$date", 0, 7]}  # Format YYYY-MM
            }
        },
        {
            "$group": {
                "_id": {
                    "mois": "$mois",
                    "canal": "$canal"
                },
                "total_depots": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "depot"]}, "$montant", 0]
                    }
                },
                "total_retraits": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "retrait"]}, "$montant", 0]
                    }
                }
            }
        },
        {"$sort": {"_id.mois": -1, "_id.canal": 1}},
        {
            "$project": {
                "_id": 0,
                "mois": "$_id.mois",
                "canal": "$_id.canal",
                "total_depots": 1,
                "total_retraits": 1
            }
        }
    ]

    try:
        return list(db.transactions.aggregate(pipeline))
    except PyMongoError:
        print("❌ Erreur lors de l'exécution de l'Agrégation 3.")
        return []

def agregation_4_membres_retard_plus_30_jours():
    """
    Agrégation 4 : Membres en retard de paiement de plus de 30 jours.
    Utilise $lookup et $unwind obligatoire.
    Sort : jours de retard décroissant.
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    date_actuelle_str = datetime.now().strftime("%Y-%m-%d")

    pipeline = [
        {"$unwind": "$echeancier"},
        # Filtre sur les échéances impayées dont la date est dépassée
        {
            "$match": {
                "echeancier.paye": False,
                "echeancier.date": {"$lt": date_actuelle_str}
            }
        },
        # Calcul du nombre de jours de retard en convertissant les dates
        {
            "$project": {
                "membre": 1,
                "montant_du": "$echeancier.num_echeance",
                "montant_echeance": "$echeancier.montant_du",
                "date_due": "$echeancier.date",
                "jours_retard": {
                    "$divide": [
                        {
                            "$subtract": [
                                {"$dateFromString": {"dateString": date_actuelle_str}},
                                {"$dateFromString": {"dateString": "$echeancier.date"}}
                            ]
                        },
                        1000 * 60 * 60 * 24  # conversion ms en jours
                    ]
                }
            }
        },
        # Filtre > 30 jours de retard
        {"$match": {"jours_retard": {"$gt": 30}}},
        # Lookup vers la collection membres
        {
            "$lookup": {
                "from": "membres",
                "localField": "membre",
                "foreignField": "numero",
                "as": "info_membre"
            }
        },
        {"$unwind": "$info_membre"},
        {"$sort": {"jours_retard": -1}},
        {
            "$project": {
                "_id": 0,
                "numero_membre": "$membre",
                "nom_membre": "$info_membre.nom",
                "ville": "$info_membre.ville",
                "profession": "$info_membre.profession",
                "pret_id": "$_id",
                "montant_du": "$montant_echeance",
                "date_due": "$date_due",
                "jours_retard": {"$round": ["$jours_retard", 0]}
            }
        }
    ]

    try:
        return list(db.prets.aggregate(pipeline))
    except PyMongoError:
        print("❌ Erreur lors de l'exécution de l'Agrégation 4.")
        return []

def agregation_5_taux_cotisation_dernier_tour():
    """
    Agrégation 5 : Taux de cotisation du dernier tour de chaque tontine.
    Calcul : (cotisations reçues / cotisations attendues) * 100
    """
    db = get_db()
    if db is None:
        print("❌ Connexion à MongoDB Atlas impossible.")
        return []

    pipeline = [
        {"$match": {"tours": {"$not": {"$size": 0}}}},
        {
            "$project": {
                "nom": 1,
                "montant_cotisation": 1,
                "nombre_membres": {"$size": "$membres"},
                "dernier_tour": {"$arrayElemAt": ["$tours", -1]}
            }
        },
        {
            "$project": {
                "tontine": "$nom",
                "date_dernier_tour": "$dernier_tour.date",
                "beneficiaire": "$dernier_tour.beneficiaire",
                "cotisations_attendues": {
                    "$multiply": ["$montant_cotisation", "$nombre_membres"]
                },
                "cotisations_recues": {
                    "$sum": "$dernier_tour.cotisations_recues.montant"
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "tontine": 1,
                "date_dernier_tour": 1,
                "beneficiaire": 1,
                "cotisations_attendues": 1,
                "cotisations_recues": 1,
                "taux_cotisation_pct": {
                    "$multiply": [
                        {"$divide": ["$cotisations_recues", {"$cond": [{"$eq": ["$cotisations_attendues", 0]}, 1, "$cotisations_attendues"]}]},
                        100
                    ]
                }
            }
        }
    ]

    try:
        return list(db.tontines.aggregate(pipeline))
    except PyMongoError:
        print("❌ Erreur lors de l'exécution de l'Agrégation 5.")
        return []
