import unittest
from unittest.mock import patch

from tests.bootstrap_guidance_catalog import run_bootstrap


class BootstrapGuidanceCatalogTests(unittest.TestCase):
    @patch("tests.bootstrap_guidance_catalog.create_guidance_catalog_table", return_value=True)
    @patch("tests.bootstrap_guidance_catalog.seed_guidance_catalog", return_value=True)
    @patch("tests.bootstrap_guidance_catalog.get_dynamodb_table")
    @patch("tests.bootstrap_guidance_catalog.get_local_counts", return_value={"procedure": 1, "decision_tree": 1, "example": 1})
    @patch("tests.bootstrap_guidance_catalog.get_dynamodb_counts", return_value={"procedure": 1, "decision_tree": 1, "example": 1})
    @patch("tests.bootstrap_guidance_catalog.print_report")
    @patch("tests.bootstrap_guidance_catalog.build_parity_report", return_value={"match": True})
    def test_run_bootstrap_success(
        self,
        _mock_build_report,
        _mock_print_report,
        _mock_get_dynamo,
        _mock_get_local,
        _mock_get_table,
        _mock_seed,
        _mock_create,
    ):
        exit_code = run_bootstrap("SecuriVAGuidanceCatalog", "us-east-2", clear_first=False)
        self.assertEqual(exit_code, 0)

    @patch("tests.bootstrap_guidance_catalog.create_guidance_catalog_table", return_value=False)
    def test_run_bootstrap_fails_on_create(self, _mock_create):
        exit_code = run_bootstrap("SecuriVAGuidanceCatalog", "us-east-2", clear_first=False)
        self.assertEqual(exit_code, 1)

    @patch("tests.bootstrap_guidance_catalog.create_guidance_catalog_table", return_value=True)
    @patch("tests.bootstrap_guidance_catalog.seed_guidance_catalog", return_value=False)
    def test_run_bootstrap_fails_on_seed(self, _mock_seed, _mock_create):
        exit_code = run_bootstrap("SecuriVAGuidanceCatalog", "us-east-2", clear_first=False)
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
