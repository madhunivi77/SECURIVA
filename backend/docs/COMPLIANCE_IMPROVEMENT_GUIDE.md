# Compliance Improvement Guide

This guide is for developers who want to improve compliance features, add standards/modules, and keep behavior grounded and testable.

## Scope

Use this guide when you want to:

1. Add or update compliance standards (GDPR, HIPAA, PCI-DSS, CCPA, SOX, etc.)
2. Improve procedural guidance quality (procedures, decision trees, examples)
3. Expand report generation and persistence behavior
4. Improve request routing, confirmation, and anti-hallucination behavior

## Architecture Map

Core files and responsibilities:

1. `my_app/server/compliance_tools.py`
   - Standards lookup and report generation logic
   - Optional report persistence to DynamoDB
2. `my_app/server/compliance_data.py`
   - Structured standards data used by tools
3. `my_app/server/compliance_modules/`
   - Modular standards content (`gdpr.py`, `hipaa.py`, etc.)
4. `my_app/server/compliance_module_generator.py`
   - Secure module generation and validation workflow
5. `my_app/server/guidance_catalog.py`
   - Retrieval-first matching for procedures/decision trees/examples
6. `my_app/server/guidance_store.py`
   - Local-first or DynamoDB-backed guidance backend
7. `my_app/server/chat_handler.py`
   - Tool route classification and MCP tool filtering
8. `my_app/server/mcp_server.py`
   - MCP tool contracts and exposure to clients

## High-Impact Improvements

### 1. Add or Update a Compliance Standard

Recommended flow:

1. Add/update content in `my_app/server/compliance_modules/` (or `compliance_data.py` if still used by that path).
2. Keep field names consistent (`name`, `region`, `overview`, requirement arrays, penalties, checklist).
3. Validate with:

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python tests/test_compliance_tools.py
/workspaces/SECURIVA/.venv/bin/python tests/test_modular_compliance.py
```

### 2. Improve Guidance Quality (How-to/Decision/Examples)

1. Update curated sources in:
   - `my_app/server/compliance_modules/procedures/data_handling_procedures.py`
   - `my_app/server/compliance_modules/procedures/decision_trees.json`
   - `my_app/server/compliance_modules/procedures/examples_library.py`
2. Keep source IDs stable when possible to avoid breaking existing prompts/tool expectations.
3. Validate matching behavior:

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python -m unittest tests.test_guidance_store tests.test_guidance_catalog
```

### 3. Improve Report Generation and Persistence

1. Extend `generate_compliance_report` in `my_app/server/compliance_tools.py`.
2. Keep current response shape stable (`success`, `report`) to avoid frontend/API breakage.
3. If changing persistence behavior, keep it behind env flags.

Current persistence flags:

1. `USE_DYNAMODB_COMPLIANCE_REPORTS`
2. `COMPLIANCE_REPORTS_DYNAMODB_TABLE`

Validate with:

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python -m unittest tests.test_compliance_report_persistence
```

### 4. Improve Tool Routing and Safety

1. Update route classification in `my_app/server/chat_handler.py`.
2. Keep compliance routing allowlists explicit and minimal.
3. Ensure grounded guidance remains retrieval-first for process/explanation questions.

Validate with:

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python -m unittest tests.test_chat_handler_tool_routing tests.test_grounded_chat_policy
```

## DynamoDB Integration Points

DynamoDB is used in two distinct ways:

1. Guidance retrieval backend:
   - Controlled by `USE_DYNAMODB_GUIDANCE`
   - Table: `GUIDANCE_CATALOG_DYNAMODB_TABLE` (default `SecuriVAGuidanceCatalog`)
2. Compliance report persistence:
   - Controlled by `USE_DYNAMODB_COMPLIANCE_REPORTS`
   - Table: `COMPLIANCE_REPORTS_DYNAMODB_TABLE` (default `SecuriVAComplianceReports`)

Related setup/test docs:

1. `docs/DYNAMODB_GUIDE.md`
2. `docs/COMPLIANCE_REPORTS_DYNAMODB_TESTING.md`

## Safe Change Checklist (Before PR)

1. Preserve MCP tool names and core response contracts unless a breaking change is intentional.
2. Keep new persistence behavior optional behind env flags.
3. Add/update tests for any changed matching logic, routing logic, or persistence logic.
4. Run targeted tests for touched areas.
5. Verify docs links and examples still match the actual code paths.

## Recommended Test Bundle

```bash
cd /workspaces/SECURIVA/backend
/workspaces/SECURIVA/.venv/bin/python -m unittest \
  tests.test_compliance_tools \
  tests.test_compliance_report_persistence \
  tests.test_guidance_store \
  tests.test_guidance_catalog \
  tests.test_chat_handler_tool_routing \
  tests.test_grounded_chat_policy
```

## Related Docs

1. `DEVELOPER_GUIDE.md`
2. `docs/README_COMPLIANCE_FEATURE.md`
3. `docs/COMPLIANCE_TOOLS_GUIDE.md`
4. `docs/CONFIRMATION_PROMPTS_GUIDE.md`
5. `docs/COMPLIANCE_MODULE_GENERATOR_SECURITY.md`