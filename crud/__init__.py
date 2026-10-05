"""
Package CRUD pour la gestion de l'application de microfinance.
Regroupe les opérations sur les membres, comptes, transactions, prêts et tontines.
"""

from .membres import (
    creer_membre,
    obtenir_membre,
    lister_membres,
    rechercher_par_ville,
    rechercher_par_profession,
    modifier_membre,
    supprimer_membre,
)
from .comptes import (
    TYPES_AUTORISES,
    STATUTS_AUTORISES,
    creer_compte,
    obtenir_compte,
    lister_comptes_membre,
    lister_comptes_par_type,
    cloture_compte,
    cloturer_compte,
)
from .transactions import (
    CANAUX_AUTORISES,
    effectuer_depot,
    effectuer_retrait,
    effectuer_virement,
    releve_compte,
)
from .prets import (
    STATUTS_PRET,
    calculer_echeancier,
    creer_pret,
    obtenir_pret,
    lister_prets_membre,
    enregistrer_paiement_echeance,
    mettre_a_jour_statut_pret,
    archiver_pret_solde,
    archiver_tous_prets_soldes,
)
from .tontines import (
    PERIODICITES_AUTORISEES,
    creer_tontine,
    ajouter_membre_tontine,
    lister_tontines_membre,
    determiner_prochain_beneficiaire,
    enregistrer_cotisation,
)
from .utils import (
    JSONEncoder,
    format_fcfa,
    clean_doc_for_display,
    creer_index,
    lister_index,
    expliciter_requete,
    expliquer_requete,
    exporter_donnees,
    verifier_projet,
)

__all__ = [
    # Membres
    "creer_membre",
    "obtenir_membre",
    "lister_membres",
    "rechercher_par_ville",
    "rechercher_par_profession",
    "modifier_membre",
    "supprimer_membre",
    # Comptes
    "TYPES_AUTORISES",
    "STATUTS_AUTORISES",
    "creer_compte",
    "obtenir_compte",
    "lister_comptes_membre",
    "lister_comptes_par_type",
    "cloture_compte",
    "cloturer_compte",
    # Transactions
    "CANAUX_AUTORISES",
    "effectuer_depot",
    "effectuer_retrait",
    "effectuer_virement",
    "releve_compte",
    # Prêts
    "STATUTS_PRET",
    "calculer_echeancier",
    "creer_pret",
    "obtenir_pret",
    "lister_prets_membre",
    "enregistrer_paiement_echeance",
    "mettre_a_jour_statut_pret",
    "archiver_pret_solde",
    "archiver_tous_prets_soldes",
    # Tontines
    "PERIODICITES_AUTORISEES",
    "creer_tontine",
    "ajouter_membre_tontine",
    "lister_tontines_membre",
    "determiner_prochain_beneficiaire",
    "enregistrer_cotisation",
    # Utils & Admin
    "JSONEncoder",
    "format_fcfa",
    "clean_doc_for_display",
    "creer_index",
    "lister_index",
    "expliciter_requete",
    "expliquer_requete",
    "exporter_donnees",
    "verifier_projet",
]
