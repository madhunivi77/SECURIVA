"""
Secure Compliance Module Generator
Allows AI to generate new compliance modules with safety validation
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import shutil


class SecurityValidationError(Exception):
    """Raised when security validation fails"""
    pass


class ComplianceModuleGenerator:
    """
    Secure generator for compliance modules with multi-layer validation
    """
    
    # Only allow writing to this directory
    ALLOWED_DIR = Path(__file__).parent / "compliance_modules"
    
    # Dangerous Python constructs to block
    DANGEROUS_IMPORTS = [
        'os.system', 'subprocess', 'eval', 'exec', '__import__',
        'compile', 'open', 'input', 'raw_input', 'file',
        'execfile', 'reload', '__builtins__', 'globals', 'locals',
        'vars', 'dir', 'delattr', 'setattr', 'getattr'
    ]
    
    # Required fields in STANDARD constant
    REQUIRED_FIELDS = ['name', 'region', 'overview']
    
    # Maximum file size (500 KB)
    MAX_FILE_SIZE = 500 * 1024
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize generator
        
        Args:
            dry_run: If True, only validate without writing files
        """
        self.dry_run = dry_run
        self.validation_results = []
        
    def validate_filename(self, filename: str) -> str:
        """
        Validate and sanitize filename
        
        Args:
            filename: Proposed filename
            
        Returns:
            Sanitized filename
            
        Raises:
            SecurityValidationError: If filename is invalid
        """
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Must end with .py
        if not filename.endswith('.py'):
            filename += '.py'
        
        # Only allow lowercase alphanumeric and underscore
        base_name = filename[:-3]  # Remove .py
        if not re.match(r'^[a-z0-9_]+$', base_name):
            raise SecurityValidationError(
                f"Invalid filename: {filename}. Only lowercase letters, numbers, and underscores allowed."
            )
        
        # Prevent reserved names
        reserved = ['__init__', 'test', 'admin', 'config', 'settings']
        if base_name in reserved:
            raise SecurityValidationError(f"Reserved filename: {filename}")
        
        self.validation_results.append(f"✓ Filename valid: {filename}")
        return filename
    
    def validate_path(self, filename: str) -> Path:
        """
        Validate target path is within allowed directory
        
        Args:
            filename: Sanitized filename
            
        Returns:
            Resolved absolute path
            
        Raises:
            SecurityValidationError: If path escapes allowed directory
        """
        target_path = (self.ALLOWED_DIR / filename).resolve()
        
        # Ensure path is within allowed directory (prevent path traversal)
        if not str(target_path).startswith(str(self.ALLOWED_DIR.resolve())):
            raise SecurityValidationError(
                f"Path traversal detected! Target: {target_path}"
            )
        
        self.validation_results.append(f"✓ Path safe: {target_path}")
        return target_path
    
    def validate_python_syntax(self, content: str) -> ast.Module:
        """
        Validate Python syntax and check for dangerous constructs
        
        Args:
            content: Python code to validate
            
        Returns:
            AST module
            
        Raises:
            SecurityValidationError: If syntax invalid or dangerous code detected
        """
        # Check file size
        if len(content.encode('utf-8')) > self.MAX_FILE_SIZE:
            raise SecurityValidationError(
                f"File too large: {len(content)} bytes (max {self.MAX_FILE_SIZE})"
            )
        
        # Parse as Python AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise SecurityValidationError(f"Invalid Python syntax: {e}")
        
        self.validation_results.append("✓ Valid Python syntax")
        
        # Check for dangerous constructs
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(danger in alias.name for danger in self.DANGEROUS_IMPORTS):
                        raise SecurityValidationError(
                            f"Dangerous import detected: {alias.name}"
                        )
            
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    if any(danger in full_name for danger in self.DANGEROUS_IMPORTS):
                        raise SecurityValidationError(
                            f"Dangerous import detected: {full_name}"
                        )
            
            # Block dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', '__import__', 'compile']:
                        raise SecurityValidationError(
                            f"Dangerous function call: {node.func.id}"
                        )
        
        self.validation_results.append("✓ No dangerous constructs found")
        return tree
    
    def validate_standard_structure(self, content: str) -> Dict[str, Any]:
        """
        Validate STANDARD constant exists and has required structure
        
        Args:
            content: Python module content
            
        Returns:
            STANDARD dictionary
            
        Raises:
            SecurityValidationError: If STANDARD is invalid
        """
        # Execute in restricted namespace to extract STANDARD
        namespace = {}
        try:
            # Use compile + exec with restricted builtins
            code = compile(content, '<string>', 'exec')
            restricted_builtins = {
                '__builtins__': {
                    'True': True, 'False': False, 'None': None,
                    'str': str, 'int': int, 'float': float, 'bool': bool,
                    'list': list, 'dict': dict, 'tuple': tuple
                }
            }
            exec(code, restricted_builtins, namespace)
        except Exception as e:
            raise SecurityValidationError(f"Failed to execute module: {e}")
        
        # Check STANDARD exists
        if 'STANDARD' not in namespace:
            raise SecurityValidationError("STANDARD constant not found")
        
        standard = namespace['STANDARD']
        
        # Validate it's a dictionary
        if not isinstance(standard, dict):
            raise SecurityValidationError("STANDARD must be a dictionary")
        
        # Check required fields
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in standard]
        if missing_fields:
            raise SecurityValidationError(
                f"STANDARD missing required fields: {missing_fields}"
            )
        
        # Validate field types
        if not isinstance(standard.get('name'), str):
            raise SecurityValidationError("STANDARD['name'] must be a string")
        
        if not isinstance(standard.get('region'), str):
            raise SecurityValidationError("STANDARD['region'] must be a string")
        
        if not isinstance(standard.get('overview'), str):
            raise SecurityValidationError("STANDARD['overview'] must be a string")
        
        self.validation_results.append(f"✓ STANDARD structure valid")
        self.validation_results.append(f"  - Name: {standard['name'][:50]}")
        self.validation_results.append(f"  - Region: {standard['region']}")
        
        return standard
    
    def backup_existing_file(self, target_path: Path) -> Optional[Path]:
        """
        Backup existing file if it exists
        
        Args:
            target_path: Path to file
            
        Returns:
            Backup path if created, None otherwise
        """
        if not target_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = target_path.with_suffix(f'.backup_{timestamp}.py')
        
        shutil.copy2(target_path, backup_path)
        self.validation_results.append(f"✓ Backup created: {backup_path.name}")
        
        return backup_path
    
    def generate_module(
        self,
        filename: str,
        content: str,
        allow_overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Generate and validate a compliance module
        
        Args:
            filename: Module filename (e.g., 'sox.py')
            content: Python module content with STANDARD constant
            allow_overwrite: Whether to allow overwriting existing files
            
        Returns:
            dict with status, path, validation results, and warnings
        """
        self.validation_results = []
        
        try:
            # Step 1: Validate filename
            safe_filename = self.validate_filename(filename)
            
            # Step 2: Validate path
            target_path = self.validate_path(safe_filename)
            
            # Step 3: Check if file exists
            if target_path.exists() and not allow_overwrite:
                return {
                    "success": False,
                    "error": f"File already exists: {safe_filename}. Set allow_overwrite=True to replace.",
                    "validation_results": self.validation_results
                }
            
            # Step 4: Validate Python syntax
            self.validate_python_syntax(content)
            
            # Step 5: Validate STANDARD structure
            standard = self.validate_standard_structure(content)
            
            # Step 6: Backup existing file
            backup_path = None
            if target_path.exists():
                backup_path = self.backup_existing_file(target_path)
            
            # Step 7: Write file (or dry-run)
            if self.dry_run:
                result = {
                    "success": True,
                    "dry_run": True,
                    "message": "Validation passed! File would be created at:",
                    "target_path": str(target_path),
                    "filename": safe_filename,
                    "standard_name": standard.get('name'),
                    "validation_results": self.validation_results,
                    "content_preview": content[:500] + "..." if len(content) > 500 else content
                }
            else:
                # Actually write the file
                target_path.write_text(content, encoding='utf-8')
                
                result = {
                    "success": True,
                    "dry_run": False,
                    "message": "Compliance module created successfully!",
                    "target_path": str(target_path),
                    "filename": safe_filename,
                    "standard_name": standard.get('name'),
                    "backup_path": str(backup_path) if backup_path else None,
                    "validation_results": self.validation_results
                }
            
            return result
            
        except SecurityValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "validation_results": self.validation_results
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {type(e).__name__}: {e}",
                "validation_results": self.validation_results
            }


# MCP Tool Functions

def create_compliance_module_dry_run(filename: str, content: str) -> Dict[str, Any]:
    """
    Validate a compliance module without writing to disk (dry-run mode)
    
    This is the safe first step - validates everything but doesn't create files.
    Always call this first before create_compliance_module().
    
    Args:
        filename: Module filename (e.g., 'sox.py' or 'iso_27001.py')
        content: Complete Python module content with STANDARD constant
        
    Returns:
        dict with validation results and preview
    """
    generator = ComplianceModuleGenerator(dry_run=True)
    return generator.generate_module(filename, content)


def create_compliance_module(
    filename: str,
    content: str,
    allow_overwrite: bool = False
) -> Dict[str, Any]:
    """
    Create a new compliance module file (WRITES TO DISK)
    
    ⚠️ IMPORTANT: Always call create_compliance_module_dry_run() first!
    Only call this after reviewing dry-run results.
    
    Args:
        filename: Module filename (e.g., 'sox.py')
        content: Complete Python module content with STANDARD constant
        allow_overwrite: If True, allows overwriting existing files (backup created)
        
    Returns:
        dict with creation status and file path
        
    Security Features:
    - Path traversal prevention
    - Dangerous code detection
    - Syntax validation
    - Structure validation
    - Automatic backups
    - File size limits
    """
    generator = ComplianceModuleGenerator(dry_run=False)
    return generator.generate_module(filename, content, allow_overwrite)


def list_compliance_modules() -> Dict[str, Any]:
    """
    List all available compliance modules in the system
    
    Returns:
        dict with list of module files and metadata
    """
    modules_dir = Path(__file__).parent / "compliance_modules"
    
    if not modules_dir.exists():
        return {
            "success": False,
            "error": "Compliance modules directory not found"
        }
    
    modules = []
    for file_path in modules_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
        
        stat = file_path.stat()
        modules.append({
            "filename": file_path.name,
            "module_id": file_path.stem,
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    return {
        "success": True,
        "total_modules": len(modules),
        "modules": sorted(modules, key=lambda x: x['filename'])
    }


# Example usage template
EXAMPLE_MODULE_TEMPLATE = '''"""
{description}
"""

STANDARD = {{
    "name": "{full_name}",
    "region": "{region}",
    "effective_date": "{date}",
    "version": "{version}",
    "overview": "{overview}",
    "official_reference": "{reference}",
    "authority": "{authority}",
    "website": "{website}",
    
    "key_requirements": [
        {{
            "id": "req_001",
            "name": "Requirement Name",
            "description": "Description of requirement",
            "requirements": [
                "Specific requirement 1",
                "Specific requirement 2"
            ]
        }}
    ],
    
    "penalties": {{
        "description": "Penalty structure",
        "tiers": []
    }},
    
    "checklist": [
        {{"id": "check_001", "requirement": "Check this", "category": "Category"}}
    ]
}}

MODULE_INFO = {{
    "module_type": "compliance_standard",
    "last_updated": "{today}",
    "maintainer": "Compliance Team",
    "tags": {tags},
    "industry": "{industry}"
}}
'''
