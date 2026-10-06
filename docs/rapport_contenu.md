# RAPPORT POWERPOINT - PROJET 9 : MICROFINANCE ET TONTINES

## Structure des Diapositives (15-20 slides)

### Diapositive 1 : Page de Garde
- **Titre** : Projet 9 - Système de Gestion NoSQL pour Microfinance et Tontines
- **Matière** : Du SQL au NoSQL (Big Data, MongoDB et Python)
- **Enseignant** : FOTSO T. Valdez W.
- **Membres du Groupe** : Liste des étudiants, matricules et rôles dans le projet.

### Diapositive 2 : Contexte
- Présentation du besoin métier d'un établissement de microfinance.
- Complexité de la gestion combinée des comptes d'épargne/courants, des crédits avec échéancier et des tontines traditionnelles.
- Intérêt de la souplesse du modèle documentaire NoSQL MongoDB par rapport à un SGBDR classique.

### Diapositive 3 : Objectifs du Projet
- Automatiser la gestion des membres, comptes, prêts, tontines et transactions.
- Assurer la cohérence financière grâce aux transactions multi-documents ACID MongoDB.
- Fournir des analyses décisionnelles via le moteur d'agrégation de MongoDB.
- Développer une interface double (Terminal interactif & Interface graphique Tkinter).

### Diapositives 4-6 : Modélisation NoSQL & Justification des Choix
- **Schéma des Collections** : `membres`, `comptes`, `transactions`, `prets`, `tontines`, `prets_archives`.
- **Justification d'Imbrication vs Référence** :
  - *Imbrication* : Les échéanciers sont imbriqués dans les prêts, et les tours/cotisations sont imbriqués dans les tontines (relation 1-to-N à taille bornée, accès atomique).
  - *Référence* : Les transactions font référence aux numéros de comptes, et les prêts/comptes/tontines font référence aux numéros de membres (évite la duplication et garantit la réutilisabilité).

### Diapositive 7 : Données et Volumes Réels
- `membres` : 160 documents
- `comptes` : 250 documents
- `transactions` : 3 200 documents
- `prets` : 100 documents (avec échéancier)
- `tontines` : 12 documents (avec tours & cotisations)
- Génération reproductible via `random.seed(42)`.

### Diapositives 8-12 : Démonstration des Opérations CRUD & Transactions ACID
- **INSERT** : Création de membres, comptes, transactions, prêts et tontines.
- **FIND** : Solde d'un membre, relevé de compte, échéances impayées à ce jour.
- **UPDATE** : Dépôts, retraits avec contrôle de solde, paiement des échéances.
- **Virement Inter-comptes** : Démonstration de `client.start_session()` et `start_transaction()` pour la garantie ACID.
- **DELETE & ARCHIVAGE** : Clôture des comptes nuls et migration des prêts soldés vers `prets_archives`.

### Diapositives 13-16 : Agrégations NoSQL & Interprétation
1. **Encours des prêts par ville et profession** : Identification des zones géographiques et secteurs d'activité les plus engagés en crédit.
2. **Taux de remboursement à l'échéance** : Évaluation du risque crédit et du taux de recouvrement global.
3. **Volume dépôts/retraits par mois & canal** : Analyse de la digitalisation des flux (Mobile Money vs Agence).
4. **Membres en retard > 30 jours ($lookup)** : Ciblage des membres débiteurs pour relance.
5. **Taux de cotisation tontines** : Suivi de la santé financière des tontines au dernier tour.

### Diapositive 17 : Indexation et Performances
- Index uniques sur `numero` / `code_pret` / `code_tontine`.
- Index composés sur `transactions (compte_numero, date)` et index simples sur les clés étrangères.
- Capture de la commande `explain()` démontrant l'utilisation des index.

### Diapositive 18 : Difficultés Rencontrées et Solutions
- *Gestion des transactions ACID en local* : Implémentation d'un mécanisme de fallback sécurisé en l'absence de Replica Set local.
- *Agrégation complexe des sous-documents tontines* : Emploi combiné de `$project`, `$unwind` et `$arrayElemAt`.

### Diapositive 19 : Répartition du Travail
- Présentation détaillée de la contribution de chaque membre du groupe (modélisation, développement Python, UI Tkinter, agrégations, vidéo).

### Diapositive 20 : Bilan et Perspectives
- Application 100% fonctionnelle conforme aux exigences du Projet 9.
- Perspectives : Intégration d'une API REST FastAPI et scoring de crédit prédictif.
