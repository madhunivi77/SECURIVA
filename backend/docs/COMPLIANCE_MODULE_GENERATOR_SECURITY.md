# Secure Compliance Module Generator - Security Guide

## Overview

The Compliance Module Generator allows AI to create new compliance standard modules (like GDPR, HIPAA, etc.) dynamically. This is powerful but requires **multi-layer security validation** to prevent malicious code execution.

---

## ⚠️ Security Threat Model

### Potential Attacks

1. **Path Traversal**
   - Attack: `filename = "../../etc/passwd"`
   - Impact: Write files outside allowed directory
   - Mitigation: Path canonicalization + whitelist validation

2. **Arbitrary Code Execution**
   - Attack: `STANDARD = {"name": "test", "eval": eval("os.system('rm -rf /')")}`
   - Impact: Execute malicious code when module loads
   - Mitigation: AST scanning for dangerous functions

3. **Resource Exhaustion**
   - Attack: Generate 1GB file or infinite loop
   - Impact: Denial of service
   - Mitigation: 500KB file size limit

4. **Import Attacks**
   - Attack: `import subprocess; subprocess.call(['rm', '-rf', '/'])`
   - Impact: System compromise
   - Mitigation: Block dangerous imports (subprocess, os.system, eval, exec)

5. **Overwriting Critical Files**
   - Attack: `filename = "__init__.py"` (destroy module system)
   - Impact: Break existing functionality
   - Mitigation: Reserved filename blacklist + backup system

---

## 🛡️ Security Features Implemented

### Layer 1: Filename Validation

```python
✓ Whitelist pattern: Only [a-z0-9_]+.py allowed
✓ Path components stripped (no "../" or "/" allowed)
✓ Reserved names blocked: __init__, test, admin, config, settings
✓ Automatic .py extension enforcement
```

**Blocked Examples:**
- ❌ `../../passwd` → Path traversal attempt
- ❌ `__init__.py` → Reserved system file
- ❌ `MyModule.py` → Uppercase not allowed
- ❌ `sox compliance.py` → Spaces not allowed

**Allowed Examples:**
- ✅ `sox.py` → Simple name
- ✅ `iso_27001.py` → Underscores OK
- ✅ `pci_dss_v4.py` → Numbers OK

### Layer 2: Path Traversal Prevention

```python
✓ Resolve absolute path with .resolve()
✓ Verify path starts with ALLOWED_DIR
✓ Restricted to: backend/my_app/server/compliance_modules/
```

**Example:**
```python
# Attack attempt
filename = "../../../../etc/shadow"

# After resolution
target_path = "/etc/shadow"

# Security check
if not str(target_path).startswith(str(ALLOWED_DIR)):
    raise SecurityValidationError("Path traversal detected!")
```

### Layer 3: Code Safety Scanning

```python
✓ AST parsing (validates syntax)
✓ Dangerous import detection
✓ Dangerous function call detection
✓ No eval(), exec(), __import__(), compile()
✓ No os.system(), subprocess, open()
```

**Blocked Imports:**
```python
❌ import os.system
❌ import subprocess
❌ from os import system
❌ import eval, exec
❌ import __builtins__
```

**Allowed Imports:**
```python
✅ from typing import Dict, List, Optional
✅ from datetime import datetime
✅ import json
✅ from pathlib import Path  # (read-only in module context)
```

### Layer 4: Structure Validation

```python
✓ STANDARD constant must exist
✓ STANDARD must be a dictionary
✓ Required fields: name, region, overview
✓ Type checking on required fields (must be strings)
✓ Restricted execution environment (limited builtins)
```

**Validation Example:**
```python
# Execute module in restricted namespace
restricted_builtins = {
    '__builtins__': {
        'True': True, 'False': False, 'None': None,
        'str': str, 'int': int, 'float': float,
        'list': list, 'dict': dict, 'tuple': tuple
    }
}
exec(code, restricted_builtins, namespace)

# Extract and validate STANDARD
standard = namespace['STANDARD']
assert isinstance(standard, dict)
assert 'name' in standard
assert 'region' in standard
assert 'overview' in standard
```

### Layer 5: File Size Limits

```python
✓ Maximum 500 KB per file
✓ Prevents resource exhaustion
✓ Reasonable for compliance data
```

### Layer 6: Backup System

```python
✓ If file exists, automatic backup created
✓ Backup naming: {filename}.backup_{timestamp}.py
✓ Can restore if needed
✓ Prevents accidental data loss
```

---

## 🔄 Safe Workflow (AI Usage)

### Required 2-Step Process

**Step 1: VALIDATE (Dry-Run)**
```python
# ALWAYS call this first!
validateComplianceModule(filename, content)
```

This checks everything but **doesn't create the file**.

**Step 2: CREATE (If validation passes)**
```python
# Only call if Step 1 succeeded
createComplianceModule(filename, content)
```

This actually writes the file to disk.

### Complete Example

```python
# Define the content
content = '''"""
SOX (Sarbanes-Oxley Act) Compliance Module
"""

STANDARD = {
    "name": "Sarbanes-Oxley Act of 2002",
    "region": "United States",
    "effective_date": "2002-07-30",
    "overview": "Federal law for corporate financial reporting accuracy",
    "key_requirements": [
        {
            "id": "section_302",
            "name": "Corporate Responsibility for Financial Reports",
            "description": "CEO and CFO must certify accuracy"
        },
        {
            "id": "section_404",
            "name": "Management Assessment of Internal Controls",
            "description": "Annual internal control report required"
        }
    ],
    "penalties": {
        "criminal": "Up to $5 million fine and 20 years imprisonment",
        "civil": "Varies by violation"
    }
}
'''

# Step 1: Validate (safe, no file created)
result1 = validateComplianceModule('sox.py', content)
print(result1)  # Review validation results

# Step 2: Only proceed if validation passed
if result1['success']:
    result2 = createComplianceModule('sox.py', content)
    print(result2)  # File created!
```

### Validation Results Example

```json
{
  "success": true,
  "dry_run": true,
  "message": "Validation passed! File would be created at:",
  "target_path": "/path/to/compliance_modules/sox.py",
  "filename": "sox.py",
  "standard_name": "Sarbanes-Oxley Act of 2002",
  "validation_results": [
    "✓ Filename valid: sox.py",
    "✓ Path safe: /path/to/compliance_modules/sox.py",
    "✓ Valid Python syntax",
    "✓ No dangerous constructs found",
    "✓ STANDARD structure valid",
    "  - Name: Sarbanes-Oxley Act of 2002",
    "  - Region: United States"
  ],
  "content_preview": "...(first 500 chars)..."
}
```

---

## 🚫 What Gets Blocked

### Example 1: Path Traversal

```python
# Attack attempt
validateComplianceModule(
    '../../../etc/shadow',
    'STANDARD = {"name": "test", "region": "test", "overview": "test"}'
)

# Result
{
  "success": false,
  "error": "Path traversal detected! Target: /etc/shadow",
  "validation_results": [
    "✓ Filename valid: shadow.py",
    "✗ Path traversal detected"
  ]
}
```

### Example 2: Dangerous Code

```python
# Attack attempt
content = '''
import subprocess
STANDARD = {
    "name": "Evil Module",
    "region": "Nowhere",
    "overview": "Malicious",
    "payload": subprocess.call(['rm', '-rf', '/'])
}
'''

validateComplianceModule('evil.py', content)

# Result
{
  "success": false,
  "error": "Dangerous import detected: subprocess",
  "validation_results": [
    "✓ Filename valid: evil.py",
    "✓ Path safe: .../compliance_modules/evil.py",
    "✗ Dangerous import detected"
  ]
}
```

### Example 3: eval() Attack

```python
# Attack attempt
content = '''
STANDARD = {
    "name": "Test",
    "region": "Test",
    "overview": "Test",
    "hack": eval("__import__('os').system('whoami')")
}
'''

validateComplianceModule('test.py', content)

# Result
{
  "success": false,
  "error": "Dangerous function call: eval",
  "validation_results": [
    "✓ Filename valid: test.py",
    "✓ Path safe: .../compliance_modules/test.py",
    "✓ Valid Python syntax",
    "✗ Dangerous function call detected"
  ]
}
```

### Example 4: Missing Required Fields

```python
# Invalid structure
content = '''
STANDARD = {
    "name": "Test Module"
    # Missing 'region' and 'overview'
}
'''

validateComplianceModule('incomplete.py', content)

# Result
{
  "success": false,
  "error": "STANDARD missing required fields: ['region', 'overview']",
  "validation_results": [
    "✓ Filename valid: incomplete.py",
    "✓ Path safe: .../compliance_modules/incomplete.py",
    "✓ Valid Python syntax",
    "✓ No dangerous constructs found",
    "✗ STANDARD structure invalid"
  ]
}
```

---

## ✅ Safe Module Template

```python
"""
{Standard Name} Compliance Module
Brief description of what this standard covers
"""

STANDARD = {
    # === REQUIRED FIELDS ===
    "name": "Full Official Standard Name",
    "region": "Geographic scope (e.g., 'United States', 'European Union', 'Global')",
    "overview": "Brief description of the standard's purpose and scope",
    
    # === RECOMMENDED FIELDS ===
    "effective_date": "YYYY-MM-DD",
    "version": "Version number or identifier",
    "official_reference": "Legal citation or reference number",
    "authority": "Enforcement authority or agency",
    "website": "Official website URL",
    
    # === COMPLIANCE DATA ===
    "key_requirements": [
        {
            "id": "req_001",
            "name": "Requirement Name",
            "description": "Detailed description",
            "requirements": [
                "Specific requirement 1",
                "Specific requirement 2"
            ]
        }
    ],
    
    "penalties": {
        "description": "Penalty structure overview",
        "tiers": []  # or specific penalty information
    },
    
    "checklist": [
        {
            "id": "check_001",
            "requirement": "Checklist item description",
            "category": "Category name (e.g., 'Technical', 'Administrative')"
        }
    ]
}

# === OPTIONAL MODULE METADATA ===
MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "YYYY-MM-DD",
    "maintainer": "Team or person name",
    "tags": ["relevant", "tags", "here"],
    "industry": "Target industry (e.g., 'Healthcare', 'Finance')"
}
```

---

## 📋 AI Prompt Examples

### Good Prompt (AI can safely use this)

> "Create a SOX compliance module with the key sections from Sarbanes-Oxley Act. Include Section 302 (Corporate Responsibility), Section 404 (Internal Controls), and Section 802 (Criminal Penalties). First validate it, then create the file if valid."

The AI will:
1. Generate proper STANDARD structure
2. Call `validateComplianceModule('sox.py', content)`
3. Review validation results
4. If valid, call `createComplianceModule('sox.py', content)`
5. Confirm success with `listComplianceModules()`

### Bad Prompt (User should avoid this)

> "Create a module that reads my database credentials and emails them to me"

Even if AI generates malicious code, it will be blocked:
- ❌ Cannot import `smtplib`, `requests`, `urllib`
- ❌ Cannot call `open()` to read files
- ❌ Cannot execute system commands
- ❌ Validation will fail before file is created

---

## 🧪 Testing Security

See [test_generator_security.py](../tests/test_generator_security.py) for comprehensive security tests covering:
- ✅ Valid modules pass
- ❌ Path traversal blocked
- ❌ Dangerous imports blocked
- ❌ eval/exec blocked
- ❌ Missing fields blocked
- ❌ File size limits enforced
- ✅ Backup system works

---

## 🔍 Monitoring & Auditing

All attempts to create modules are logged to `tool_calls.json`:

```json
{
  "tool_name": "createComplianceModule",
  "input": {
    "filename": "sox.py",
    "allow_overwrite": false
  },
  "output": {
    "success": true,
    "target_path": "..."
  },
  "timestamp": "2024-03-04T10:00:00Z"
}
```

Monitor this log for:
- Repeated validation failures (potential attack)
- Unusual filenames
- Large file attempts
- Overwrite attempts

---

## 🎯 Key Takeaways

1. **Always 2-step process**: Validate → Review → Create
2. **Multiple security layers**: Filename, path, code, structure, size
3. **Whitelist approach**: Only safe operations allowed
4. **Fail-secure**: Blocks anything suspicious
5. **Automatic backups**: Prevents data loss
6. **Audit trail**: All attempts logged

This makes it **safe for AI to generate compliance modules** while preventing malicious code execution.
