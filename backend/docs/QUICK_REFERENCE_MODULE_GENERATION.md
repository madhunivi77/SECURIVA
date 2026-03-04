# 🚀 Quick Reference: Secure AI Module Generation

## 📋 TL;DR

**Problem:** AI needs to create compliance module files, but this is dangerous (arbitrary code execution risk)

**Solution:** 6-layer security validation + 2-step process (validate → create)

**Result:** ✅ AI can safely generate modules | ❌ Malicious code blocked

---

## 🎯 3 MCP Tools Available

### 1. listComplianceModules()
**Purpose:** See what modules exist  
**Safe:** ✅ Read-only, always safe  
**Returns:** List of all .py files in compliance_modules/

```python
result = listComplianceModules()
# {"modules": [{"filename": "gdpr.py", ...}, ...]}
```

---

### 2. validateComplianceModule(filename, content)
**Purpose:** Validate module WITHOUT creating file (dry-run)  
**Safe:** ✅ No file created, validation only  
**Use:** ALWAYS call this first!

```python
result = validateComplianceModule('sox.py', module_content)
# Returns validation results or security errors
```

**Checks:**
- ✓ Filename safety (path traversal prevention)
- ✓ Python syntax validity
- ✓ Dangerous code detection (eval, exec, subprocess, etc.)
- ✓ STANDARD structure validation
- ✓ Required fields present
- ✓ File size limits

---

### 3. createComplianceModule(filename, content, allow_overwrite=False)
**Purpose:** Actually create the file (WRITES TO DISK)  
**Dangerous:** ⚠️ Writes files - validate first!  
**Use:** Only after validateComplianceModule() passes

```python
# Step 1: Validate
validate_result = validateComplianceModule('sox.py', content)

# Step 2: Only proceed if valid
if validate_result['success']:
    create_result = createComplianceModule('sox.py', content)
    # File created in compliance_modules/sox.py
```

---

## 🔄 Workflow (AI or Manual)

```
┌─────────────────────────────────────────────────────────┐
│ 1. AI GENERATES CONTENT                                 │
│    content = '''STANDARD = {...}'''                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. VALIDATE (Dry Run)                                   │
│    result = validateComplianceModule(filename, content) │
│    ✓ No file created                                    │
│    ✓ Security checks run                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ╔═════════════╗
              ║  Valid?     ║
              ╚══════╤══════╝
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
     ✅ YES                    ❌ NO
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌────────────────────┐
│ 3. CREATE        │    │ REJECT             │
│    create...()   │    │ Show error message │
│    ✓ File saved  │    │ Don't create file  │
└──────────────────┘    └────────────────────┘
```

---

## 🛡️ Security: 6 Layers

| Layer | What It Does | Example Attack Blocked |
|-------|--------------|------------------------|
| **1. Filename** | Only `[a-z0-9_]+.py` | `../../../etc/passwd` ❌ |
| **2. Path** | Must be in `compliance_modules/` | `/etc/shadow` ❌ |
| **3. Code Scan** | Block dangerous imports | `import subprocess` ❌ |
| **4. Function Scan** | Block dangerous calls | `eval()`, `exec()` ❌ |
| **5. Structure** | STANDARD dict required | Missing fields ❌ |
| **6. Size** | 500KB max | 1GB file ❌ |

---

## ✅ What AI Can Do

```python
✅ Generate compliance data
✅ Create .py files in compliance_modules/ only
✅ Use: dict, list, str, int, float, bool
✅ Define STANDARD constant
✅ Add MODULE_INFO metadata
```

## ❌ What AI Cannot Do

```python
❌ Write files outside compliance_modules/
❌ Import: subprocess, os.system, eval, exec
❌ Call: eval(), exec(), __import__(), compile()
❌ Read arbitrary files
❌ Make network requests
❌ Execute system commands
❌ Overwrite __init__.py or reserved files
```

---

## 📝 Module Template

```python
"""
Module Description
"""

STANDARD = {
    # === REQUIRED (will fail without these) ===
    "name": "Full Standard Name",
    "region": "Geographic Scope",
    "overview": "What this standard covers",
    
    # === RECOMMENDED ===
    "effective_date": "YYYY-MM-DD",
    "version": "1.0",
    
    # === YOUR COMPLIANCE DATA ===
    "key_requirements": [...],
    "penalties": {...},
    "checklist": [...]
}

# Optional
MODULE_INFO = {
    "last_updated": "2024-03-04",
    "tags": ["finance", "sox"],
    "industry": "Finance"
}
```

---

## 🧪 Quick Test Commands

```bash
# Test security (13 tests - should all pass)
python test_generator_security.py

# Demo workflow (creates SOX module)
python demo_generator_workflow.py

# Verify modules work with AI tools
python test_sox_module.py
```

---

## 🚨 Common Issues

### Issue 1: Validation Fails - "Dangerous import"
**Cause:** Module tries to import blocked package  
**Fix:** Remove dangerous imports (subprocess, os.system, etc.)

### Issue 2: "STANDARD constant not found"
**Cause:** Missing or misspelled STANDARD  
**Fix:** Ensure `STANDARD = {` exists at module level

### Issue 3: "Missing required fields"
**Cause:** STANDARD missing name, region, or overview  
**Fix:** Add all three required fields

### Issue 4: "Path traversal detected"
**Cause:** Filename contains `../` or absolute path  
**Fix:** Use simple filename like `sox.py`

### Issue 5: "Reserved filename"
**Cause:** Trying to name file `__init__.py`, `test.py`, etc.  
**Fix:** Use descriptive name like `sox_compliance.py`

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [SECURE_AI_MODULE_GENERATION_SUMMARY.md](./SECURE_AI_MODULE_GENERATION_SUMMARY.md) | Complete overview (this doc's big brother) |
| [COMPLIANCE_MODULE_GENERATOR_SECURITY.md](./COMPLIANCE_MODULE_GENERATOR_SECURITY.md) | Deep dive into security (700+ lines) |
| [HIPAA_MODULE_WALKTHROUGH.md](./HIPAA_MODULE_WALKTHROUGH.md) | Manual module creation guide |

---

## 🎯 Example: Create SOX Module

```python
# AI generates content
sox = '''"""SOX Compliance"""
STANDARD = {
    "name": "Sarbanes-Oxley Act",
    "region": "United States",
    "overview": "Corporate financial reporting",
    "key_sections": [...],
    "checklist": [...]
}
'''

# Step 1: Validate
v = validateComplianceModule('sox.py', sox)
print(v['validation_results'])
# ✓ Filename valid
# ✓ Path safe
# ✓ Valid Python
# ✓ No dangerous code
# ✓ Structure valid

# Step 2: Create (only if valid!)
if v['success']:
    c = createComplianceModule('sox.py', sox)
    print(c['target_path'])
    # compliance_modules/sox.py created!
```

---

## 📊 Current Modules (4)

1. **gdpr.py** - European data protection
2. **hipaa.py** - US healthcare privacy
3. **email_compliance.py** - Email marketing rules
4. **sox.py** - Corporate financial reporting ← AI generated!

---

## 🎉 Success Criteria

✅ All 13 security tests pass  
✅ SOX module generated by AI  
✅ SOX queryable via AI tools  
✅ No security vulnerabilities found  
✅ Backward compatible with existing modules

---

## 💡 Pro Tips

1. **Always dry-run first:** Validate before creating
2. **Review validation results:** Check what security caught
3. **Use descriptive names:** `iso_27001.py` not `module1.py`
4. **Follow template:** Use existing modules as reference
5. **Test after creation:** Verify AI can query your module

---

## 🔗 Quick Links

- **Generator Code:** [compliance_module_generator.py](../my_app/server/compliance_module_generator.py)
- **MCP Tools:** [mcp_server.py](../my_app/server/mcp_server.py) (lines 2342+)
- **Security Tests:** [test_generator_security.py](../../test_generator_security.py)
- **Demo:** [demo_generator_workflow.py](../../demo_generator_workflow.py)

---

**Remember:** Validation is cheap, recovery from malicious code is expensive. Always validate first! 🛡️
