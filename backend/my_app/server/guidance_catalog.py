import json
import re
from typing import Any

from .guidance_store import build_default_guidance_store

GUIDANCE_TYPE_ALIASES = {
    "procedure": "procedure",
    "procedures": "procedure",
    "process": "procedure",
    "steps": "procedure",
    "decision_tree": "decision_tree",
    "decision tree": "decision_tree",
    "decision": "decision_tree",
    "flowchart": "decision_tree",
    "example": "example",
    "examples": "example",
    "scenario": "example",
    "scenarios": "example",
}

PROCEDURE_HINTS = {
    "data_collection": ["collect", "collection", "signup", "consent", "privacy notice"],
    "data_storage": ["store", "storage", "retain", "retention", "encrypt", "password", "database"],
    "data_sharing": ["share", "sharing", "third party", "vendor", "partner", "processor", "transfer"],
    "data_deletion": ["delete", "deletion", "erase", "erasure", "removal", "purge"],
    "breach_response": ["breach", "incident", "phishing", "leak", "compromise", "notification"],
}

DECISION_TREE_HINTS = {
    "email_compliance": ["email", "phishing", "send data", "attachment", "request by email"],
    "data_sharing": ["share", "vendor", "third party", "processor", "partner"],
    "data_deletion": ["delete", "deletion request", "erasure request", "remove account"],
    "vendor_access": ["vendor access", "database access", "system access", "admin access", "credentials"],
}

EXAMPLE_HINTS = {
    "email_scenarios": ["email", "newsletter", "access request", "vendor request", "deletion request"],
    "technical_scenarios": ["password", "hash", "bcrypt", "logging", "api", "encrypt", "database"],
    "process_scenarios": ["onboarding", "termination", "consent management", "employee process"],
    "data_breach_scenarios": ["breach", "incident", "notification", "leak", "compromise"],
}

REGULATION_PATTERN = re.compile(r"\b(gdpr|ccpa|hipaa|pci[ -]?dss|sox)\b", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"[a-z0-9]{3,}")


def _normalize(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _tokenize(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(_normalize(text)))


def _keyword_score(question: str, keywords: list[str]) -> int:
    normalized_question = _normalize(question)
    return sum(1 for keyword in keywords if keyword in normalized_question)


def _token_overlap_score(question: str, *texts: str) -> int:
    question_tokens = _tokenize(question)
    if not question_tokens:
        return 0

    candidate_tokens: set[str] = set()
    for text in texts:
        candidate_tokens.update(_tokenize(text))
    return len(question_tokens.intersection(candidate_tokens))


def _serialize_content(content: Any) -> str:
    return json.dumps(content, sort_keys=True) if isinstance(content, (dict, list)) else str(content)


class GuidanceCatalog:
    """Retrieval-first guidance catalog backed by a configurable guidance store."""

    def __init__(self, store=None):
        self.store = store or build_default_guidance_store()

    def get_guidance(
        self,
        user_question: str,
        regulation: str | None = None,
        guidance_type: str | None = None,
    ) -> dict[str, Any]:
        resolved_type = self._resolve_guidance_type(user_question, guidance_type)
        resolved_regulation = self._resolve_regulation(user_question, regulation)

        if resolved_type == "decision_tree":
            return self._match_decision_tree(user_question, resolved_regulation)
        if resolved_type == "example":
            return self._match_example(user_question, resolved_regulation)
        return self._match_procedure(user_question, resolved_regulation)

    def _resolve_guidance_type(self, user_question: str, guidance_type: str | None) -> str:
        if guidance_type:
            resolved = GUIDANCE_TYPE_ALIASES.get(_normalize(guidance_type))
            if resolved:
                return resolved

        normalized_question = _normalize(user_question)
        if any(phrase in normalized_question for phrase in ["can i", "should i", "is it ok", "is it okay"]):
            return "decision_tree"
        if any(phrase in normalized_question for phrase in ["example", "show me", "sample", "code example"]):
            return "example"
        return "procedure"

    def _resolve_regulation(self, user_question: str, regulation: str | None) -> str | None:
        if regulation:
            return regulation.upper()

        match = REGULATION_PATTERN.search(user_question or "")
        if not match:
            return None

        regulation_name = match.group(1).upper()
        if regulation_name in {"PCI DSS", "PCI-DSS"}:
            return "PCI-DSS"
        return regulation_name.replace("  ", " ")

    def _build_metadata(
        self,
        source_type: str,
        source_id: str,
        regulation: str | None,
        source_reference: str,
        matched_terms: list[str],
    ) -> dict[str, Any]:
        return {
            "success": True,
            "source": {
                "backend": self.store.last_backend_name,
                "source_type": source_type,
                "source_id": source_id,
                "regulation": regulation,
                "path": source_reference,
            },
            "matched_terms": matched_terms,
            "response_rules": [
                "Answer only from the returned source content.",
                "If the user asks for reasoning, explain using the cited steps, guidance, or legal basis in the source.",
                "Do not invent additional requirements, penalties, or procedures.",
                "If the source is incomplete for the user's case, say what is missing instead of guessing.",
            ],
        }

    def _match_procedure(self, user_question: str, regulation: str | None) -> dict[str, Any]:
        procedures = self.store.get_procedures()
        best_id = None
        best_score = -1

        for procedure_id, procedure in procedures.items():
            score = _keyword_score(user_question, PROCEDURE_HINTS.get(procedure_id, [])) * 4
            score += _token_overlap_score(
                user_question,
                procedure_id.replace("_", " "),
                procedure.get("title", ""),
                procedure.get("description", ""),
                _serialize_content(procedure),
            )
            if regulation and regulation in procedure.get("applicable_regulations", []):
                score += 3
            if score > best_score:
                best_id = procedure_id
                best_score = score

        if not best_id:
            return {
                "success": False,
                "error": "No matching procedure found.",
                "available_procedures": sorted(procedures.keys()),
            }

        procedure = procedures[best_id]
        matched_terms = [
            keyword for keyword in PROCEDURE_HINTS.get(best_id, []) if keyword in _normalize(user_question)
        ]
        result = self._build_metadata(
            source_type="procedure",
            source_id=best_id,
            regulation=regulation,
            source_reference=self.store.get_source_reference("procedure", best_id),
            matched_terms=matched_terms,
        )
        result["guidance"] = procedure
        return result

    def _match_decision_tree(self, user_question: str, regulation: str | None) -> dict[str, Any]:
        trees = self.store.get_decision_trees()
        tree_map = {
            "email_compliance": "email_compliance_decision",
            "data_sharing": "data_sharing_decision",
            "data_deletion": "data_deletion_decision",
            "vendor_access": "vendor_access_decision",
        }

        best_id = None
        best_score = -1
        for scenario_id, tree_key in tree_map.items():
            tree = trees.get(tree_key, {})
            score = _keyword_score(user_question, DECISION_TREE_HINTS.get(scenario_id, [])) * 4
            score += _token_overlap_score(
                user_question,
                scenario_id.replace("_", " "),
                tree.get("title", ""),
                tree.get("description", ""),
                _serialize_content(tree),
            )
            if score > best_score:
                best_id = scenario_id
                best_score = score

        if not best_id:
            return {
                "success": False,
                "error": "No matching decision tree found.",
                "available_scenarios": sorted(tree_map.keys()),
            }

        tree_key = tree_map[best_id]
        matched_terms = [
            keyword for keyword in DECISION_TREE_HINTS.get(best_id, []) if keyword in _normalize(user_question)
        ]
        result = self._build_metadata(
            source_type="decision_tree",
            source_id=best_id,
            regulation=regulation,
            source_reference=self.store.get_source_reference("decision_tree", best_id),
            matched_terms=matched_terms,
        )
        result["guidance"] = trees[tree_key]
        return result

    def _match_example(self, user_question: str, regulation: str | None) -> dict[str, Any]:
        examples = self.store.get_examples()
        best_topic = None
        best_entry = None
        best_score = -1

        for topic, entries in examples.items():
            topic_bonus = _keyword_score(user_question, EXAMPLE_HINTS.get(topic, [])) * 4
            for entry in entries:
                score = topic_bonus
                score += _token_overlap_score(
                    user_question,
                    topic.replace("_", " "),
                    entry.get("scenario", ""),
                    entry.get("situation", ""),
                    _serialize_content(entry),
                )
                if regulation and regulation in entry.get("applicable_regulations", []):
                    score += 3
                if score > best_score:
                    best_topic = topic
                    best_entry = entry
                    best_score = score

        if not best_topic or not best_entry:
            return {
                "success": False,
                "error": "No matching example found.",
                "available_topics": sorted(examples.keys()),
            }

        matched_terms = [
            keyword for keyword in EXAMPLE_HINTS.get(best_topic, []) if keyword in _normalize(user_question)
        ]
        result = self._build_metadata(
            source_type="example",
            source_id=best_topic,
            regulation=regulation,
            source_reference=self.store.get_source_reference("example", best_topic),
            matched_terms=matched_terms,
        )
        result["guidance"] = best_entry
        return result
