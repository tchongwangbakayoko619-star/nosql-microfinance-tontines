# Projet 9 — Microfinance et Tontines (MongoDB & Python)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-MongoDB%20Atlas-green.svg)](https://www.mongodb.com/cloud/atlas)
[![PyMongo](https://img.shields.io/badge/PyMongo-4.0%2B-brightgreen.svg)](https://pymongo.readthedocs.io/)

Application CLI complète de gestion d'un établissement de microfinance et de tontines au Cameroun, développée dans le cadre de l'évaluation finale de NoSQL (Projet 9).

---

## 📋 Table des Matières
1. [Présentation](#-présentation)
2. [Architecture du Projet](#-architecture-du-projet)
3. [Modélisation NoSQL](#-modélisation-nosql)
4. [Installation et Configuration](#-installation-et-configuration)
5. [Génération des Données](#-génération-des-données)
6. [Lancement de l'Application CLI](#-lancement-de-lapplication-cli)
7. [Vérification et Tests](#-vérification-et-tests)
8. [Agrégations MongoDB](#-agrégations-mongodb)
9. [Index et Performances](#-index-et-performances)
10. [Transactions Multi-Documents](#-transactions-multi-documents)
11. [Archivage et Exports](#-archivage-et-exports)

---

## 📖 Présentation

Cet outil permet d'accompagner une institution de microfinance dans la gestion complète de :
- **Ses membres** (profils, coordonnées, pièces d'identité) ;
- **Leurs comptes** (épargne, courant, soldes, clôtures) ;
- **Les transactions financières** (dépôts, retraits, virements inter-comptes) ;
- **Les prêts octroyés** (calcul automatique d'échéancier mensuel, remboursements, statut) ;
- **Les tontines** (gestion des cotisations, tours de table et bénéficiaires).

L'application est exécutable entièrement depuis le terminal (CLI) et est connectable à **MongoDB Atlas**.

---

## 📁 Architecture du Projet

```text
projet9_microfinance/
│
├── README.md                # Documentation complète du projet
├── requirements.txt         # Dépendances Python (PyMongo, python-dotenv)
├── .env.example             # Modèle de variables d'environnement
├── .gitignore               # Fichiers et dossiers exclus du versionnement
│
├── config.py                # Chargement sécurisé de la configuration .env
├── database.py              # Connexion centralisée et ping MongoDB Atlas
├── utils.py                 # Encodeurs JSON et utilitaires de formattage
│
├── membres.py               # Module CRUD Membres
├── comptes.py               # Module CRUD Comptes bancaires
├── transactions.py          # Module Dépôts, Retraits et Virements (Transactions MongoDB)
├── prets.py                 # Module Prêts, Échéanciers et Remboursements
├── tontines.py              # Module Tontines, Cotisations et Tours
│
├── agregations.py           # Pipelines d'agrégations complexes MongoDB
├── index.py                 # Gestion des index uniques, composés et explain()
├── exports.py               # Générateur d'exports JSON et CSV
├── verification.py          # Script d'audit automatique de conformité
├── tests.py                 # Suite de tests unitaires et d'intégration
├── generer_donnees.py       # Générateur reproductible de données réalistes
└── main.py                  # Menu principal CLI interactif
│
├── exports/                 # Fichiers d'exportations générés
│   ├── json/                # Collection .json par entité
│   └── csv/                 # Fichiers .csv plats par entité
└── archives/                # Emplacement des sauvegardes
```

---

## 📐 Modélisation NoSQL

La modélisation respecte les principes fondamentaux du NoSQL orienté document :

### 1. Imbrication (Embedding)
- **Échéancier dans les Prêts (`prets.echeancier`)** : Un échéancier est strictement lié à un prêt spécifique et sa taille est limitée (ex: 6 à 24 mensualités). L'imbrication permet de lire l'état complet du prêt en une seule requête sans jointure.
- **Tours et Cotisations dans les Tontines (`tontines.tours`)** : Les tours de tontine et l'historique des cotisations sont directement intégrés au document tontine pour garantir une cohérence transactionnelle atomique de la tontine.

### 2. Référencement (Referencing)
- **Compte → Membre (`comptes.membre`)** : Un membre peut posséder plusieurs comptes, et les comptes sont interrogés indépendamment.
- **Transaction → Compte (`transactions.compte`)** : La collection des transactions est la plus volumineuse (plusieurs milliers de documents). L'imbriquer dans le compte provoquerait le dépassement de la limite de 16 Mo par document MongoDB.
- **Prêt → Membre (`prets.membre`)** : Permet une recherche rapide des prêts d'un membre sans alourdir le document membre.
- **Tontine → Membres (`tontines.membres`)** : Référence les numéros de membres participants.

---

## 🛠️ Installation et Configuration

### 1. Prérequis
- Python 3.10 ou supérieur
- Accès à un cluster **MongoDB Atlas** (ou une instance local avec réplica set pour les transactions multi-documents).

### 2. Installation de l'environnement virtuel
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration des accès MongoDB Atlas
Créer un fichier `.env` à la racine (basé sur `.env.example`) :
```ini
MONGO_URI=mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER_HOST>/
MONGO_DB=projet9_microfinance
```

> 🔒 **Sécurité** : Les identifiants et mot de passe ne sont jamais inscrits en dur dans le code. Le fichier `.env` est ignoré par Git via `.gitignore`.

---

## 🎲 Génération des Données

Pour générer un jeu de données volumineux, cohérent et reproductible (`random.seed(42)`) au contexte camerounais (villes : Douala, Yaoundé, Bafoussam... ; montants en FCFA) :

```bash
python generer_donnees.py
```

**Volume généré (supérieur au barème minimum) :**
- 👥 **Membres** : 200 (minimum exigé : 150)
- 💳 **Comptes** : 250 (minimum exigé : 200)
- 📊 **Transactions** : >3 500 (minimum exigé : 3 000)
- 🏦 **Prêts** : 100 (minimum exigé : 80)
- 🤝 **Tontines** : 12 (minimum exigé : 10)

---

## 💻 Lancement de l'Application CLI

Pour lancer le menu principal de l'application :

```bash
python main.py
```

Le menu interactif propose :
```text
==================================================
       MICROFINANCE ET TONTINES
==================================================
1. Gestion des membres
2. Gestion des comptes
3. Dépôt
4. Retrait
5. Virement
6. Gestion des prêts
7. Gestion des tontines
8. Recherches
9. Agrégations
10. Index et performances
11. Exports
12. Vérification du projet
13. Exécuter les tests unitaires
14. Régénérer le jeu de données
0. Quitter
```

---

## 🔍 Vérification et Tests

### Script d'audit automatique
Pour valider l'état du projet et les exigences NoSQL :
```bash
python verification.py
```

### Lancement des tests unitaires
Pour exécuter la suite de tests automatisés :
```bash
python tests.py
```

---

## 📈 Agrégations MongoDB

Les calculs statistiques et tableaux de bord sont exécutés nativement par le moteur d'agrégation de MongoDB (`agregations.py`) :

1. **Encours total des prêts par ville et profession** (`$lookup` vers `membres`, `$group`, `$sum`).
2. **Taux de remboursement à l'échéance** (`$unwind` sur `echeancier`, calcul du ratio payé/dû).
3. **Volume des dépôts et retraits par mois et par canal** (`$match`, `$group`, `$dateToString`).
4. **Membres en retard de paiement de plus de 30 jours** (`$unwind`, `$lookup` vers `membres`, filtre et tri par jours de retard).
5. **Taux de cotisation du dernier tour de chaque tontine** (calcul du montant reçu vs attendu).

---

## ⚡ Index et Performances

Pour garantir des performances de requêtes optimales (`index.py`) :

- **Index Uniques** :
  - `membres.numero` (dédoublonnage strict des identifiants membres)
  - `comptes.numero` (dédoublonnage strict des numéros de compte)
- **Index Composés** :
  - `transactions` : `(compte: 1, date: -1)` (accélère l'extraction des relevés de compte ordonnés par date)
  - `prets` : `(membre: 1, statut: 1)` (accélère le suivi des encours et impayés par membre)

L'option **10.3** du menu CLI permet d'afficher le plan d'exécution (`explain()`) pour analyser le fonctionnement de ces index.

---

## 🛡️ Transactions Multi-Documents

Le virement entre deux comptes (`transactions.effectuer_virement`) s'appuie sur les **transactions multi-documents atomiques de MongoDB** (`client.start_session()` et `session.start_transaction()`).

Le processus garantit les propriétés ACID :
1. Vérification des comptes source et destination ;
2. Contrôle du solde disponible sur le compte source ;
3. Débit du compte source et crédit du compte destination ;
4. Création simultanée des pièces justificatives de transaction (débit et crédit) ;
5. Commit global ou Rollback intégral en cas d'erreur.

---

## 🗄️ Archivage et Exports

### Archivage des prêts soldés
Lorsqu'un prêt est intégralement remboursé (`statut == 'solde'`), il est déplacé de manière sécurisée vers la collection `prets_archives` avec horodatage de l'archivage (`date_archivage`).

### Export des données
L'application produit automatiquement des exports ré-importables (`exports.py`) :
- **JSON** : `exports/json/*.json` (conserve les structures imbriquées et types BSON)
- **CSV** : `exports/csv/*.csv` (format plat structuré pour réimport analytique)

---

## 👨‍🎓 Auteur & Évaluation
Projet réalisé dans le cadre du cours NoSQL (Bases de données & MongoDB avec Python).
Enseignant : FOTSO T. Valdez W.
