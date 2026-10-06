# PROJET 9 - Microfinance et Tontines (NoSQL MongoDB)

## Présentation
- **Titre** : Projet 9 - Microfinance et tontines
- **Contexte** : Un établissement de microfinance accompagne des membres qui épargnent, empruntent et participent à des tontines. Chaque membre dispose d'un ou plusieurs comptes, de prêts assortis d'un échéancier, et participe à des tontines où chacun cotise et perçoit la cagnotte à tour de rôle.
- **Objectif** : Concevoir, implémenter et tester une solution complète avec Python et MongoDB pour la gestion des membres, des comptes, des transactions avec atomicité ACID, des prêts, des tontines, des agrégations analytiques, de l'indexation, de l'archivage et des exports.

---

## Technologies Utilisées
- **Langage** : Python 3.8+
- **Base de données** : MongoDB (local ou MongoDB Atlas)
- **Driver Python** : `pymongo`
- **Interface Graphique** : Tkinter (bibliothèque standard Python)

---

## Structure du Projet
```text
code/
├── README.md              <- Documentation complète d'installation et d'utilisation
├── requirements.txt       <- Dépendances Python (pymongo)
├── config.py              <- Configuration unique de la connexion MongoDB
├── generer_donnees.py     <- Script de génération reproductible (random.seed(42))
├── crud.py                <- Modèle NoSQL, opérations CRUD, transactions ACID, archivage
├── validators.py          <- Module de validation métier et contrôle d'unicité
├── utils.py               <- Utilitaires (auto-génération des codes MBR/CPT/PRT/TNT, formatage)
├── indexes.py             <- Création et gestion des index MongoDB
├── exports.py             <- Fonctions d'exportation (JSON & CSV) et vérification globale
├── agregations.py         <- 5 Pipelines d'agrégation analytiques MongoDB
└── main.py                <- Point d'entrée unique (Mode Terminal & Mode Tkinter)
exports/
├── json/                  <- Fichiers d'exportation .json par collection
└── csv/                   <- Fichiers d'exportation .csv par collection principale
```

---

## Configuration MongoDB

La configuration est centralisée exclusivement dans le fichier `code/config.py`.

```python
# code/config.py
MONGODB_URI = "mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER>.mongodb.net/"
DATABASE_NAME = "projet9_microfinance"
```
> **Remarque de sécurité** : Ne mettez jamais de vrai mot de passe ni de fichier `.env`. Remplacez `<USERNAME>`, `<PASSWORD>` et `<CLUSTER>` par vos propres accès.

---

## Installation et Lancement

1. **Création et activation de l'environnement virtuel** :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Linux/macOS
# ou .venv\Scripts\activate sous Windows
```

2. **Installation des dépendances** :
```bash
pip install -r code/requirements.txt
```

3. **Lancement de l'application** :
```bash
python code/main.py
```

Au lancement, l'application propose :
```text
1. Mode Terminal
2. Interface graphique Tkinter
3. Quitter
```

---

## Fonctionnalités Clés et Exigences Réalisées

### 1. Génération de Données Réalistes (`generer_donnees.py`)
- `membres` : 160 documents (exigence >= 150)
- `comptes` : 250 documents (exigence >= 200)
- `transactions` : 3 200 documents (exigence >= 3 000)
- `prets` : 100 documents avec échéancier imbriqué (exigence >= 80)
- `tontines` : 12 documents avec sous-documents de tours et cotisations (exigence >= 10)

### 2. Opérations CRUD & Transactions (`crud.py`, `utils.py`, `validators.py`)
- **GÉNÉRATION AUTOMATIQUE DE CODES** : Génération séquentielle intelligente et anti-doublon des codes lors des créations si le champ est laissé vide : `MBR-0161`, `CPT-00251`, `PRT-0101`, `TNT-013` et `TXN-timestamp`.
- **INSERT** : Création de membres, comptes, transactions, prêts et tontines avec validation stricte des données et unicité.
- **FIND** : Recherche des comptes/soldes d'un membre, relevé des transactions d'un compte sur une période, échéances impayées à ce jour, tontines et prochains bénéficiaires.
- **UPDATE** : Dépôts, retraits (avec refus si solde insuffisant), paiement des échéances et enregistrement des cotisations de tontine.
- **VIREMENT ACID** : Implémentation des virements inter-comptes avec transactions multi-documents MongoDB via `with client.start_session() as s: with s.start_transaction():`.
- **DELETE & ARCHIVAGE** : Clôture des comptes à solde nul et archivage automatique des prêts soldés vers la collection `prets_archives` avec horodatage `date_archivage`.


### 3. Agrégations NoSQL (`agregations.py`)
1. **Encours total des prêts par ville et profession** (`$match`, `$lookup`, `$unwind`, `$group`, `$sort`).
2. **Taux de remboursement à l'échéance** (`$unwind`, `$match`, `$group`, `$project`).
3. **Volume des dépôts et retraits par mois et canal** (`$match`, `$group`, `$sort`).
4. **Membres en retard de +30 jours et montant dû** (`$unwind`, `$match`, `$group`, `$lookup`).
5. **Taux de cotisation du dernier tour de chaque tontine** (`$project`, `$unwind`, `$group`, `$sort`).

### 4. Indexation (`crud.py`)
- Index uniques sur `membres.numero`, `comptes.numero`, `prets.code_pret`, `tontines.code_tontine`.
- Index composés/simples sur `transactions(compte_numero, date)`, `comptes.membre_numero`, `prets.membre_numero` et `tontines.membres`.

### 5. Exports (`exports/`)
- Export automatique au format **JSON** et **CSV** pour chaque collection vers `exports/json/` et `exports/csv/`.

---

## Problèmes Courants & Solutions
- **Erreur de connexion MongoDB (`ServerSelectionTimeoutError`)** : Vérifiez que le service local MongoDB est lancé (`sudo systemctl start mongod`) ou que l'URI Atlas dans `config.py` est correcte et autorise votre adresse IP.
- **Support des Transactions ACID** : Les transactions MongoDB nécessitent un Replica Set (par défaut sur Atlas, ou configuré en local avec `--replSet`). En local standalone, un mécanisme de fallback sécurisé assure la cohérence des opérations.
