import json
import os
from pathlib import Path
from typing import Any

from .compliance_modules.procedures.data_handling_procedures import PROCEDURES
from .compliance_modules.procedures.examples_library import EXAMPLES


DECISION_TREE_FILE = Path(__file__).parent / "compliance_modules" / "procedures" / "decision_trees.json"


class BaseGuidanceStore:
    backend_name = "unknown"

    def __init__(self):
        self.last_backend_name = self.backend_name

    def get_procedures(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_decision_trees(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_examples(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_source_reference(self, source_type: str, source_id: str) -> str:
        raise NotImplementedError


class LocalFileGuidanceStore(BaseGuidanceStore):
    backend_name = "local_files"

    def __init__(self, decision_tree_file: Path | None = None):
        super().__init__()
        self.decision_tree_file = decision_tree_file or DECISION_TREE_FILE
        self._decision_trees: dict[str, Any] | None = None

    def get_procedures(self) -> dict[str, Any]:
        self.last_backend_name = self.backend_name
        return PROCEDURES

    def get_decision_trees(self) -> dict[str, Any]:
        self.last_backend_name = self.backend_name
        if self._decision_trees is None:
            with open(self.decision_tree_file, "r", encoding="utf-8") as handle:
                self._decision_trees = json.load(handle)
        return self._decision_trees

    def get_examples(self) -> dict[str, Any]:
        self.last_backend_name = self.backend_name
        return EXAMPLES

    def get_source_reference(self, source_type: str, source_id: str) -> str:
        if source_type == "procedure":
            return str(Path(__file__).parent / "compliance_modules" / "procedures" / "data_handling_procedures.py")
        if source_type == "decision_tree":
            return str(self.decision_tree_file)
        if source_type == "example":
            return str(Path(__file__).parent / "compliance_modules" / "procedures" / "examples_library.py")
        return "local_files"


class DynamoDBGuidanceStore(BaseGuidanceStore):
    backend_name = "dynamodb"

    def __init__(
        self,
        table_name: str | None = None,
        region: str | None = None,
        table: Any | None = None,
    ):
        super().__init__()
        self.table_name = table_name or os.getenv("GUIDANCE_CATALOG_DYNAMODB_TABLE", "SecuriVAGuidanceCatalog")
        self.region = region or os.getenv("AWS_REGION", "us-east-2")
        if table is not None:
            self.table = table
        else:
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError("boto3 is required for DynamoDB guidance storage") from exc

            self.table = boto3.resource("dynamodb", region_name=self.region).Table(self.table_name)
        self._cache: dict[str, dict[str, Any]] = {}

    def _load_content_type(self, content_type: str) -> dict[str, Any]:
        if content_type in self._cache:
            self.last_backend_name = self.backend_name
            return self._cache[content_type]

        items: list[dict[str, Any]] = []
        query_kwargs = {"content_type": content_type}
        try:
            from boto3.dynamodb.conditions import Key

            query_kwargs["KeyConditionExpression"] = Key("content_type").eq(content_type)
        except ImportError:
            pass

        while True:
            response = self.table.query(**query_kwargs)
            items.extend(response.get("Items", []))
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break
            query_kwargs["ExclusiveStartKey"] = last_evaluated_key

        if not items:
            raise LookupError(f"No guidance catalog items found for content_type='{content_type}' in table '{self.table_name}'")

        content = {item["content_id"]: item["content"] for item in items}
        self._cache[content_type] = content
        self.last_backend_name = self.backend_name
        return content

    def get_procedures(self) -> dict[str, Any]:
        return self._load_content_type("procedure")

    def get_decision_trees(self) -> dict[str, Any]:
        return self._load_content_type("decision_tree")

    def get_examples(self) -> dict[str, Any]:
        return self._load_content_type("example")

    def get_source_reference(self, source_type: str, source_id: str) -> str:
        return f"dynamodb://{self.table_name}/{source_type}/{source_id}"


class FallbackGuidanceStore(BaseGuidanceStore):
    backend_name = "fallback"

    def __init__(self, primary: BaseGuidanceStore, fallback: BaseGuidanceStore):
        super().__init__()
        self.primary = primary
        self.fallback = fallback

    def _with_fallback(self, method_name: str) -> dict[str, Any]:
        try:
            result = getattr(self.primary, method_name)()
            if result:
                self.last_backend_name = self.primary.last_backend_name
                return result
        except Exception:
            pass

        result = getattr(self.fallback, method_name)()
        self.last_backend_name = self.fallback.last_backend_name
        return result

    def get_procedures(self) -> dict[str, Any]:
        return self._with_fallback("get_procedures")

    def get_decision_trees(self) -> dict[str, Any]:
        return self._with_fallback("get_decision_trees")

    def get_examples(self) -> dict[str, Any]:
        return self._with_fallback("get_examples")

    def get_source_reference(self, source_type: str, source_id: str) -> str:
        if self.last_backend_name == self.primary.backend_name:
            return self.primary.get_source_reference(source_type, source_id)
        return self.fallback.get_source_reference(source_type, source_id)


def build_default_guidance_store() -> BaseGuidanceStore:
    use_dynamodb_guidance = os.getenv("USE_DYNAMODB_GUIDANCE", "false").lower() == "true"
    local_store = LocalFileGuidanceStore()

    if not use_dynamodb_guidance:
        return local_store

    dynamodb_store = DynamoDBGuidanceStore()
    return FallbackGuidanceStore(dynamodb_store, local_store)
