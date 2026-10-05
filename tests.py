import unittest
from datetime import datetime
from database import get_db, test_connection
from membres import creer_membre, obtenir_membre, modifier_membre, supprimer_membre
from comptes import creer_compte, obtenir_compte, cloturer_compte
from transactions import effectuer_depot, effectuer_retrait, effectuer_virement, releve_compte
from prets import creer_pret, obtenir_pret, enregistrer_paiement_echeance
from tontines import creer_tontine, ajouter_membre_tontine, enregistrer_cotisation
from agregations import (
    agregation_1_encours_par_ville_profession,
    agregation_2_taux_remboursement_echeance,
    agregation_3_depots_retraits_par_mois_canal,
    agregation_4_membres_retard_plus_30_jours,
    agregation_5_taux_cotisation_dernier_tour
)
from index import creer_index, lister_index

class TestMicrofinanceProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialisation de l'environnement de test."""
        cls.db = get_db(silent=True)
        if cls.db is None:
            raise RuntimeError("Impossible de se connecter à la base de test MongoDB.")
        
        # Codes uniques dédiés aux tests
        cls.test_mem1 = "MEM_TEST_001"
        cls.test_mem2 = "MEM_TEST_002"
        cls.test_cpt1 = "CPT_TEST_001"
        cls.test_cpt2 = "CPT_TEST_002"
        cls.test_tontine = "Tontine Test Unitaires"

    def test_01_connexion_atlas(self):
        """Test de la connexion à MongoDB Atlas."""
        self.assertTrue(test_connection())

    def test_02_creation_membre(self):
        """Test de la création d'un membre."""
        # Nettoyage si existant
        self.db.membres.delete_one({"numero": self.test_mem1})
        m = creer_membre(self.test_mem1, "Testeur Unitaire", "690000000", "Informaticien", "Douala", "IDTEST01")
        self.assertIsNotNone(m)
        self.assertEqual(m["numero"], self.test_mem1)

    def test_03_creation_compte(self):
        """Test de la création d'un compte bancaire."""
        self.db.comptes.delete_one({"numero": self.test_cpt1})
        c = creer_compte(self.test_cpt1, self.test_mem1, "epargne", solde=100000)
        self.assertIsNotNone(c)
        self.assertEqual(c["solde"], 100000)

    def test_04_depot(self):
        """Test d'un dépôt d'argent."""
        trans = effectuer_depot(self.test_cpt1, 50000, canal="agence")
        self.assertIsNotNone(trans)
        compte = obtenir_compte(self.test_cpt1)
        self.assertEqual(compte["solde"], 150000)

    def test_05_retrait(self):
        """Test d'un retrait valide."""
        trans = effectuer_retrait(self.test_cpt1, 20000, canal="agence")
        self.assertIsNotNone(trans)
        compte = obtenir_compte(self.test_cpt1)
        self.assertEqual(compte["solde"], 130000)

    def test_06_retrait_solde_insuffisant(self):
        """Test du refus de retrait si le solde est insuffisant."""
        trans = effectuer_retrait(self.test_cpt1, 99999999, canal="agence")
        self.assertIsNone(trans)
        compte = obtenir_compte(self.test_cpt1)
        self.assertEqual(compte["solde"], 130000)

    def test_07_virement_reussi(self):
        """Test d'un virement réussi entre deux comptes."""
        self.db.membres.delete_one({"numero": self.test_mem2})
        self.db.comptes.delete_one({"numero": self.test_cpt2})
        creer_membre(self.test_mem2, "Deuxieme Testeur", "691111111", "Comptable", "Yaoundé", "IDTEST02")
        creer_compte(self.test_cpt2, self.test_mem2, "courant", solde=10000)

        success = effectuer_virement(self.test_cpt1, self.test_cpt2, 30000)
        self.assertTrue(success)

        c1 = obtenir_compte(self.test_cpt1)
        c2 = obtenir_compte(self.test_cpt2)
        self.assertEqual(c1["solde"], 100000)
        self.assertEqual(c2["solde"], 40000)

    def test_08_virement_refuse(self):
        """Test du refus d'un virement avec solde insuffisant."""
        success = effectuer_virement(self.test_cpt1, self.test_cpt2, 99999999)
        self.assertFalse(success)

    def test_09_creation_pret(self):
        """Test de la création d'un prêt avec son échéancier."""
        pret = creer_pret(self.test_mem1, 600000, 10.0, 12)
        self.assertIsNotNone(pret)
        self.assertEqual(len(pret["echeancier"]), 12)
        self.assertEqual(pret["statut"], "en_cours")

    def test_10_paiement_echeance(self):
        """Test du paiement d'une échéance de prêt."""
        pret = self.db.prets.find_one({"membre": self.test_mem1})
        self.assertIsNotNone(pret)
        success = enregistrer_paiement_echeance(pret["_id"], 0)
        self.assertTrue(success)

    def test_11_creation_tontine(self):
        """Test de la création d'une tontine."""
        self.db.tontines.delete_one({"nom": self.test_tontine})
        tontine = creer_tontine(self.test_tontine, 25000, "mensuelle", [self.test_mem1, self.test_mem2])
        self.assertIsNotNone(tontine)
        self.assertIn(self.test_mem1, tontine["membres"])

    def test_12_cotisation_tontine(self):
        """Test de l'enregistrement d'une cotisation tontine."""
        success = enregistrer_cotisation(self.test_tontine, self.test_mem1, 25000)
        self.assertTrue(success)

    def test_13_agregations(self):
        """Test des 5 pipelines d'agrégation MongoDB."""
        a1 = agregation_1_encours_par_ville_profession()
        self.assertIsInstance(a1, list)

        a2 = agregation_2_taux_remboursement_echeance()
        self.assertIsInstance(a2, dict)

        a3 = agregation_3_depots_retraits_par_mois_canal()
        self.assertIsInstance(a3, list)

        a4 = agregation_4_membres_retard_plus_30_jours()
        self.assertIsInstance(a4, list)

        a5 = agregation_5_taux_cotisation_dernier_tour()
        self.assertIsInstance(a5, list)

    def test_14_index(self):
        """Test de la création et vérification des index."""
        res = creer_index()
        self.assertTrue(res)
        indexes = lister_index()
        self.assertIn("membres", indexes)

    @classmethod
    def tearDownClass(cls):
        """Nettoyage des données de test."""
        cls.db.membres.delete_many({"numero": {"$in": [cls.test_mem1, cls.test_mem2]}})
        cls.db.comptes.delete_many({"numero": {"$in": [cls.test_cpt1, cls.test_cpt2]}})
        cls.db.transactions.delete_many({"compte": {"$in": [cls.test_cpt1, cls.test_cpt2]}})
        cls.db.prets.delete_many({"membre": {"$in": [cls.test_mem1, cls.test_mem2]}})
        cls.db.tontines.delete_one({"nom": cls.test_tontine})

def lancer_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMicrofinanceProject)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    unittest.main()
