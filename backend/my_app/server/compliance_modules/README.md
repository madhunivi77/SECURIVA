# Compliance Modules - Extensible Compliance Standards

## Overview

This directory contains modular compliance standard definitions. Each file represents a separate compliance standard that can be dynamically loaded by the system.

## ✨ Why Modular?

- **Easy to extend**: Add new standards without modifying core files
- **Maintainable**: Each standard in its own file
- **Scalable**: Load only what you need
- **Organized**: Clear structure for each standard

## 📁 Creating a New Compliance Module

### Step 1: Create a New Python File

Create a new file in this directory: `your_standard.py`

### Step 2: Define the STANDARD Constant

Every module must have a `STANDARD` dictionary:

```python
"""
Your Compliance Standard Module
Brief description of what this standard covers
"""

STANDARD = {
    "name": "Full Name of Your Standard",
    "region": "Geographic region (e.g., 'United States', 'Global')",
    "effective_date": "YYYY-MM-DD",
    "version": "Version or reference number",
    "overview": "Brief description of the standard",
    "official_reference": "Official act/regulation reference",
    "authority": "Governing body or authority",
    
    # Add your requirements structure here
    # Can be any structure - principles, rules, requirements, etc.
    "requirements": [
        {
            "id": "req_001",
            "name": "Requirement Name",
            "description": "What this requirement mandates",
            "implementation": [
                "How to implement point 1",
                "How to implement point 2"
            ]
        }
    ],
    
    # Optional: Add checklist
    "checklist": [
        {
            "id": "check_001",
            "requirement": "Checklist item text",
            "category": "Category name"
        }
    ],
    
    # Optional: Add penalties
    "penalties": {
        "tier_1": {
            "amount": "Fine amount",
            "violations": ["What triggers this"]}
    },
    
    # Add any other relevant fields
}

# Optional: Module metadata
MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "YYYY-MM-DD",
    "maintainer": "Your Name/Team",
    "tags": ["tag1", "tag2"]
}
```

### Step 3: That's It!

The module is automatically discovered and loaded. No need to register it anywhere.

## 📋 Available Modules

Current compliance modules in this directory:

- **gdpr.py** - General Data Protection Regulation (EU)
- **email_compliance.py** - Email marketing compliance (CAN-SPAM, CASL, GDPR email requirements)

## 🎯 Example: Email Compliance Module

See `email_compliance.py` for a comprehensive example that covers:
- Multiple sub-standards (CAN-SPAM, CASL, GDPR email)
- Best practices
- Technical requirements
- Common violations
- Detailed checklists

## 🔧 Using Your Module

Once created, your module is instantly usable:

```python
from my_app.server.compliance_data import get_standard

# Load your new standard
standard = get_standard("your_standard")

# Use it
print(standard["name"])
print(standard["requirements"])
```

Or via the AI tools:
```
getComplianceOverview("your_standard")
getComplianceRequirements("your_standard")
```

## 📝 Flexible Structure

You're not limited to a specific structure! The STANDARD dictionary can contain:

- `requirements` or `key_principles` or `rules` - whatever makes sense
- Custom fields for your standard's unique aspects
- Nested structures as deep as needed
- Lists, dicts, strings - any JSON-serializable data

## 🎨 Naming Conventions

**File names:**
- Use lowercase with underscores: `data_privacy.py`
- Be descriptive: `healthcare_compliance.py` not `hc.py`
- Avoid spaces and special characters

**Module IDs:**
- The file name (without .py) becomes the module ID
- Used in: `get_standard("module_id")`

## 🔍 Listing All Available Modules

```python
from my_app.server.compliance_modules import get_available_modules

modules = get_available_modules()
print(modules)  # ['gdpr', 'email_compliance', 'your_standard']
```

## 🚀 Quick Templates

### Minimal Module Template

```python
"""My Compliance Standard"""

STANDARD = {
    "name": "My Standard Name",
    "region": "Global",
    "effective_date": "2024-01-01",
    "overview": "Quick description",
    "requirements": []
}
```

### Complete Module Template

```python
"""Comprehensive Compliance Standard"""

STANDARD = {
    # Basic info
    "name": "Full Standard Name",
    "region": "Geographic Coverage",
    "effective_date": "YYYY-MM-DD",
    "version": "X.Y",
    "overview": "Detailed description",
    "official_reference": "Act/Regulation reference",
    "authority": "Governing body",
    "website": "https://official-site.com",
    
    # Requirements
    "requirements": [
        {
            "id": "req_001",
            "name": "Requirement Name",
            "description": "What it requires",
            "article": "Article/Section reference",
            "implementation": [
                "Implementation step 1",
                "Implementation step 2"
            ]
        }
    ],
    
    # Penalties
    "penalties": {
        "tier_1": {"amount": "$X", "violations": ["..."]}
    },
    
    # Breach notification
    "breach_notification": {
        "timeline": "When to notify",
        "who": "Who to notify"
    },
    
    # Checklist
    "checklist": [
        {"id": "001", "requirement": "...", "category": "..."}
    ]
}

MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "2024-03-04",
    "maintainer": "Your Team",
    "tags": ["privacy", "security"]
}
```

## 💡 Ideas for New Modules

Potential compliance standards to add:
- **SOC 2** - Service Organization Control
- **ISO 27001** - Information Security Management
- **CCPA** - California Consumer Privacy Act
- **COPPA** - Children's Online Privacy Protection
- **FedRAMP** - Federal Risk and Authorization Management Program
- **NIST Cybersecurity Framework**
- **API Security Standards**
- **Cookie Consent Laws**
- **Accessibility Standards** (WCAG, ADA)
- **Industry-specific**: Finance (GLBA), Healthcare (HITECH), etc.

## 🐛 Troubleshooting

**Module not loading?**
- Check file name (lowercase, underscores only)
- Verify STANDARD constant exists
- Check for Python syntax errors
- Ensure file is in `compliance_modules/` directory

**Import errors?**
- Make sure `__init__.py` exists in this directory
- Check Python path includes parent directory

## 📚 Best Practices

1. **Be comprehensive** - Include all relevant sections
2. **Cite sources** - Reference official articles/sections
3. **Keep updated** - Note version and last_updated date
4. **Document well** - Add docstrings and comments
5. **Test it** - Run `get_standard("your_module")` to verify
6. **Add checklists** - Make it actionable for users
7. **Cross-reference** - Link to related modules

## 🔗 Integration

Modules automatically work with:
- `compliance_data.py` - Data access layer
- `compliance_tools.py` - AI tool functions
- `mcp_server.py` - AI tool endpoints
- Any custom code using `get_standard()`

## 📖 Documentation

After creating a module, consider adding:
- Examples in docstrings
- Usage guide in comments
- Related standards in MODULE_INFO tags
- Links to official documentation

---

**Happy Compliance Coding! 🎉**

Questions? Check the existing modules for examples or consult the team.
