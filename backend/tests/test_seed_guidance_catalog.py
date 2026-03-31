import unittest

from tests.seed_guidance_catalog_table import build_seed_items


class SeedGuidanceCatalogTests(unittest.TestCase):
    def test_build_seed_items_contains_all_content_types(self):
        items = build_seed_items()

        self.assertTrue(len(items) > 0)
        content_types = {item["content_type"] for item in items}
        self.assertEqual(content_types, {"procedure", "decision_tree", "example"})

    def test_build_seed_items_have_required_fields(self):
        items = build_seed_items()

        sample = items[0]
        self.assertIn("content_type", sample)
        self.assertIn("content_id", sample)
        self.assertIn("content", sample)
        self.assertIn("updated_at", sample)


if __name__ == "__main__":
    unittest.main()
