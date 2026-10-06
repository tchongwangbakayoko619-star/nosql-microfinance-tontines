from datetime import datetime, timedelta
from config import get_db

def agregation_encours_prets_ville_profession(db=None):
    """
    Agrégation 1: Encours total des prêts par ville et par profession (avec $lookup).
    """
    if db is None:
        db = get_db()

    pipeline = [
        {"$match": {"statut": {"$in": ["en cours", "en retard"]}}},
        {
            "$lookup": {
                "from": "membres",
                "localField": "membre_numero",
                "foreignField": "numero",
                "as": "info_membre"
            }
        },
        {"$unwind": "$info_membre"},
        {
            "$group": {
                "_id": {
                    "ville": "$info_membre.ville",
                    "profession": "$info_membre.profession"
                },
                "encours_total": {"$sum": "$montant"},
                "nombre_prets": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "ville": "$_id.ville",
                "profession": "$_id.profession",
                "encours_total": {"$round": ["$encours_total", 2]},
                "nombre_prets": 1
            }
        },
        {"$sort": {"encours_total": -1}}
    ]

    return list(db.prets.aggregate(pipeline))

def agregation_taux_remboursement_echeance(db=None):
    """
    Agrégation 2: Taux de remboursement à l'échéance (échéances payées à temps / échéances dues).
    """
    if db is None:
        db = get_db()
    maintenant = datetime.now()

    pipeline = [
        {"$unwind": "$echeancier"},
        {
            "$match": {
                "echeancier.date_echeance": {"$lte": maintenant}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_echeances_dues": {"$sum": 1},
                "total_echeances_payees": {
                    "$sum": {
                        "$cond": ["$echeancier.paye", 1, 0]
                    }
                },
                "montant_total_du": {"$sum": "$echeancier.montant_du"},
                "montant_total_recouvre": {
                    "$sum": {
                        "$cond": ["$echeancier.paye", "$echeancier.montant_du", 0]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_echeances_dues": 1,
                "total_echeances_payees": 1,
                "taux_remboursement_pct": {
                    "$round": [
                        {
                            "$multiply": [
                                {"$divide": ["$total_echeances_payees", {"$cond": [{"$eq": ["$total_echeances_dues", 0]}, 1, "$total_echeances_dues"]}]},
                                100
                            ]
                        },
                        2
                    ]
                },
                "montant_total_du": {"$round": ["$montant_total_du", 2]},
                "montant_total_recouvre": {"$round": ["$montant_total_recouvre", 2]}
            }
        }
    ]

    res = list(db.prets.aggregate(pipeline))
    return res[0] if res else {
        "total_echeances_dues": 0,
        "total_echeances_payees": 0,
        "taux_remboursement_pct": 0.0,
        "montant_total_du": 0.0,
        "montant_total_recouvre": 0.0
    }

def agregation_volume_depots_retraits_mois_canal(db=None):
    """
    Agrégation 3: Volume des dépôts et retraits par mois et par canal.
    """
    if db is None:
        db = get_db()

    pipeline = [
        {"$match": {"type": {"$in": ["dépôt", "retrait"]}}},
        {
            "$group": {
                "_id": {
                    "annee_mois": {"$dateToString": {"format": "%Y-%m", "date": "$date"}},
                    "type": "$type",
                    "canal": "$canal"
                },
                "volume_total": {"$sum": "$montant"},
                "nombre_transactions": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "annee_mois": "$_id.annee_mois",
                "type": "$_id.type",
                "canal": "$_id.canal",
                "volume_total": {"$round": ["$volume_total", 2]},
                "nombre_transactions": 1
            }
        },
        {"$sort": {"annee_mois": -1, "type": 1}}
    ]

    return list(db.transactions.aggregate(pipeline))

def agregation_membres_retard_plus_30_jours(db=None):
    """
    Agrégation 4: Membres en retard de plus de 30 jours, avec le montant dû (avec $lookup).
    """
    if db is None:
        db = get_db()
    seuil_date = datetime.now() - timedelta(days=30)

    pipeline = [
        {"$unwind": "$echeancier"},
        {
            "$match": {
                "echeancier.paye": False,
                "echeancier.date_echeance": {"$lt": seuil_date}
            }
        },
        {
            "$group": {
                "_id": "$membre_numero",
                "code_pret": {"$first": "$code_pret"},
                "montant_du_total": {"$sum": "$echeancier.montant_du"},
                "echeances_en_retard": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "membres",
                "localField": "_id",
                "foreignField": "numero",
                "as": "membre_info"
            }
        },
        {"$unwind": "$membre_info"},
        {
            "$project": {
                "_id": 0,
                "membre_numero": "$_id",
                "nom": "$membre_info.nom",
                "telephone": "$membre_info.telephone",
                "ville": "$membre_info.ville",
                "code_pret": 1,
                "montant_du_total": {"$round": ["$montant_du_total", 2]},
                "echeances_en_retard": 1
            }
        },
        {"$sort": {"montant_du_total": -1}}
    ]

    return list(db.prets.aggregate(pipeline))

def agregation_taux_cotisation_dernier_tour_tontines(db=None):
    """
    Agrégation 5: Pour chaque tontine, le taux de cotisation du dernier tour.
    """
    if db is None:
        db = get_db()

    pipeline = [
        {
            "$project": {
                "code_tontine": 1,
                "nom": 1,
                "montant_cotisation": 1,
                "periodicite": 1,
                "nombre_membres": {"$size": "$membres"},
                "dernier_tour": {"$arrayElemAt": ["$tours", -1]}
            }
        },
        {"$unwind": "$dernier_tour.cotisations_recues"},
        {
            "$group": {
                "_id": {
                    "code_tontine": "$code_tontine",
                    "nom": "$nom",
                    "tour_numero": "$dernier_tour.tour_numero",
                    "beneficiaire": "$dernier_tour.beneficiaire_numero",
                    "nombre_membres": "$nombre_membres"
                },
                "cotisations_payees": {
                    "$sum": {
                        "$cond": ["$dernier_tour.cotisations_recues.paye", 1, 0]
                    }
                },
                "montant_recolte": {
                    "$sum": "$dernier_tour.cotisations_recues.montant"
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "code_tontine": "$_id.code_tontine",
                "nom": "$_id.nom",
                "tour_numero": "$_id.tour_numero",
                "beneficiaire": "$_id.beneficiaire",
                "cotisations_payees": 1,
                "nombre_membres": "$_id.nombre_membres",
                "taux_cotisation_pct": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        "$cotisations_payees",
                                        {"$cond": [{"$eq": ["$_id.nombre_membres", 0]}, 1, "$_id.nombre_membres"]}
                                    ]
                                },
                                100
                            ]
                        },
                        2
                    ]
                },
                "montant_recolte": {"$round": ["$montant_recolte", 2]}
            }
        },
        {"$sort": {"code_tontine": 1}}
    ]

    return list(db.tontines.aggregate(pipeline))
