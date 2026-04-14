import unittest

from my_app.server.guidance_store import DynamoDBGuidanceStore, FallbackGuidanceStore, LocalFileGuidanceStore


class FakeDynamoTable:
    def __init__(self, items_by_type=None, fail=False):
        self.items_by_type = items_by_type or {}
        self.fail = fail

    def query(self, **kwargs):
        if self.fail:
            raise RuntimeError("dynamodb unavailable")

        content_type = kwargs.get("content_type")
        items = [
            {"content_type": content_type, "content_id": content_id, "content": content}
            for content_id, content in self.items_by_type.get(content_type, {}).items()
        ]
        return {"Items": items}


class GuidanceStoreTests(unittest.TestCase):
    def test_dynamodb_store_loads_items_by_content_type(self):
        table = FakeDynamoTable({
            "procedure": {
                "data_deletion": {"title": "Delete data", "applicable_regulations": ["GDPR"], "steps": []}
            }
        })
        store = DynamoDBGuidanceStore(table=table, table_name="SecuriVAGuidanceCatalog")

        procedures = store.get_procedures()

        self.assertIn("data_deletion", procedures)
        self.assertEqual(store.last_backend_name, "dynamodb")
        self.assertEqual(
            store.get_source_reference("procedure", "data_deletion"),
            "dynamodb://SecuriVAGuidanceCatalog/procedure/data_deletion",
        )

    def test_fallback_store_uses_local_when_dynamodb_fails(self):
        primary = DynamoDBGuidanceStore(table=FakeDynamoTable(fail=True), table_name="SecuriVAGuidanceCatalog")
        fallback = LocalFileGuidanceStore()
        store = FallbackGuidanceStore(primary, fallback)

        procedures = store.get_procedures()

        self.assertIn("data_deletion", procedures)
        self.assertEqual(store.last_backend_name, "local_files")


if __name__ == "__main__":
    unittest.main()
