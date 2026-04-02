"""
Security Test Suite for Compliance Module Generator
Tests both valid usage and attack prevention
"""
import sys
sys.path.insert(0, 'backend')

from my_app.server.compliance_module_generator import ComplianceModuleGenerator, SecurityValidationError
from pathlib import Path

print("=" * 80)
print("COMPLIANCE MODULE GENERATOR - SECURITY TEST SUITE")
print("=" * 80)

# Test counter
tests_passed = 0
tests_failed = 0

def test(name, func):
    """Run a test and track results"""
    global tests_passed, tests_failed
    print(f"\n[TEST] {name}")
    try:
        func()
        print("  ✅ PASS")
        tests_passed += 1
    except AssertionError as e:
        print(f"  ❌ FAIL: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        tests_failed += 1


# ====================
# VALID USAGE TESTS
# ====================

def test_valid_module():
    """Valid compliance module should pass all validation"""
    content = '''"""Test Module"""
STANDARD = {
    "name": "Test Standard",
    "region": "Test Region",
    "overview": "Test Overview",
    "key_requirements": []
}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('test_valid.py', content)
    
    assert result['success'] == True, f"Should succeed: {result.get('error')}"
    assert result['dry_run'] == True
    assert result['filename'] == 'test_valid.py'
    assert 'validation_results' in result
    print(f"    Validation passed: {len(result['validation_results'])} checks")


def test_filename_normalization():
    """Filename should be normalized correctly"""
    content = '''"""Test"""
STANDARD = {"name": "Test", "region": "Test", "overview": "Test"}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    
    # Test adding .py extension
    result = gen.generate_module('test_file', content)
    assert result['filename'] == 'test_file.py'
    
    # Test with .py already
    result = gen.generate_module('test_file.py', content)
    assert result['filename'] == 'test_file.py'
    
    print("    ✓ .py extension added when missing")
    print("    ✓ .py extension preserved when present")


def test_backup_system():
    """Backup should be created when overwriting"""
    content = '''"""Test"""
STANDARD = {"name": "Test", "region": "Test", "overview": "Test"}
'''
    
    # Create a temporary test file
    gen = ComplianceModuleGenerator(dry_run=False)
    modules_dir = Path(__file__).parent / "my_app" / "server" / "compliance_modules"
    test_file = modules_dir / "test_backup.py"
    
    # Create initial file
    test_file.write_text(content)
    
    # Overwrite with allow_overwrite=True
    result = gen.generate_module('test_backup.py', content, allow_overwrite=True)
    
    assert result['success'] == True
    assert result['backup_path'] is not None
    
    # Cleanup
    test_file.unlink()
    if result['backup_path']:
        Path(result['backup_path']).unlink(missing_ok=True)
    
    print(f"    ✓ Backup created: {Path(result['backup_path']).name}")


# ====================
# SECURITY ATTACK TESTS
# ====================

def test_path_traversal_attack():
    """Path traversal should be blocked"""
    content = '''"""Evil"""
STANDARD = {"name": "Evil", "region": "Evil", "overview": "Evil"}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    
    # Test various path traversal attempts
    attacks = [
        '../../etc/passwd',
        '../../../etc/shadow',
        '..\\..\\..\\windows\\system32\\config\\sam',
        '/etc/passwd',
        'C:\\Windows\\System32\\config\\sam'
    ]
    
    for attack in attacks:
        try:
            result = gen.generate_module(attack, content)
            # Should either fail or sanitize to safe filename
            if result['success']:
                # Check path is still within allowed directory
                assert 'compliance_modules' in result['target_path'].lower()
        except SecurityValidationError:
            pass  # Expected - attack blocked
    
    print("    ✓ Path traversal attacks blocked")


def test_dangerous_imports():
    """Dangerous imports should be blocked"""
    dangerous_imports = [
        "import subprocess",
        "import os.system",
        "from os import system",
        "import eval",
        "import __builtins__",
        "from subprocess import call"
    ]
    
    gen = ComplianceModuleGenerator(dry_run=True)
    
    for imp in dangerous_imports:
        content = f'''
{imp}
STANDARD = {{"name": "Evil", "region": "Evil", "overview": "Evil"}}
'''
        result = gen.generate_module('evil.py', content)
        assert result['success'] == False, f"Should block: {imp}"
        assert 'dangerous' in result['error'].lower()
    
    print(f"    ✓ {len(dangerous_imports)} dangerous imports blocked")


def test_dangerous_functions():
    """Dangerous function calls should be blocked"""
    dangerous_funcs = [
        "eval('print(1)')",
        "exec('print(1)')",
        "__import__('os')",
        "compile('1+1', '<string>', 'eval')"
    ]
    
    gen = ComplianceModuleGenerator(dry_run=True)
    
    for func in dangerous_funcs:
        content = f'''
STANDARD = {{
    "name": "Evil",
    "region": "Evil",
    "overview": "Evil",
    "payload": {func}
}}
'''
        result = gen.generate_module('evil.py', content)
        assert result['success'] == False, f"Should block: {func}"
        assert 'dangerous' in result['error'].lower()
    
    print(f"    ✓ {len(dangerous_funcs)} dangerous functions blocked")


def test_file_size_limit():
    """Large files should be blocked"""
    # Create content larger than 500KB
    large_content = '''"""Large File"""
STANDARD = {
    "name": "Large Standard",
    "region": "Test",
    "overview": "Test",
    "data": "''' + ("X" * 600000) + '''"
}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('large.py', large_content)
    
    assert result['success'] == False
    assert 'too large' in result['error'].lower()
    print("    ✓ 600KB file blocked (limit: 500KB)")


def test_invalid_python_syntax():
    """Invalid Python syntax should be blocked"""
    invalid_code = '''
STANDARD = {
    "name": "Broken"
    "region": "Missing comma here"
}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('broken.py', invalid_code)
    
    assert result['success'] == False
    assert 'syntax' in result['error'].lower()
    print("    ✓ Invalid Python syntax blocked")


def test_missing_standard_constant():
    """Module without STANDARD should be blocked"""
    content = '''"""No STANDARD here"""
SOME_OTHER_DICT = {"name": "Test"}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('no_standard.py', content)
    
    assert result['success'] == False
    assert 'STANDARD' in result['error']
    print("    ✓ Missing STANDARD constant blocked")


def test_missing_required_fields():
    """STANDARD without required fields should be blocked"""
    # Missing 'overview'
    content = '''"""Incomplete"""
STANDARD = {"name": "Test", "region": "Test"}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('incomplete.py', content)
    
    assert result['success'] == False
    assert 'missing required fields' in result['error'].lower()
    print("    ✓ Missing required fields blocked")


def test_invalid_field_types():
    """STANDARD with wrong field types should be blocked"""
    # 'name' should be string, not int
    content = '''"""Bad Types"""
STANDARD = {
    "name": 123,
    "region": "Test",
    "overview": "Test"
}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('bad_types.py', content)
    
    assert result['success'] == False
    assert 'must be a string' in result['error'].lower()
    print("    ✓ Invalid field types blocked")


def test_reserved_filenames():
    """Reserved filenames should be blocked"""
    content = '''"""Test"""
STANDARD = {"name": "Test", "region": "Test", "overview": "Test"}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    
    reserved = ['__init__.py', 'test.py', 'admin.py', 'config.py']
    
    for filename in reserved:
        try:
            result = gen.generate_module(filename, content)
            assert result['success'] == False, f"Should block reserved name: {filename}"
        except SecurityValidationError:
            pass  # Expected
    
    print(f"    ✓ {len(reserved)} reserved filenames blocked")


def test_uppercase_filename():
    """Uppercase filenames should be blocked"""
    content = '''"""Test"""
STANDARD = {"name": "Test", "region": "Test", "overview": "Test"}
'''
    
    gen = ComplianceModuleGenerator(dry_run=True)
    result = gen.generate_module('MyModule.py', content)
    
    assert result['success'] == False
    assert 'only lowercase' in result['error'].lower()
    print("    ✓ Uppercase filenames blocked")


# ====================
# RUN ALL TESTS
# ====================

print("\n" + "=" * 80)
print("VALID USAGE TESTS")
print("=" * 80)

test("Valid module passes all validation", test_valid_module)
test("Filename normalization works", test_filename_normalization)
test("Backup system creates backups", test_backup_system)

print("\n" + "=" * 80)
print("SECURITY ATTACK PREVENTION TESTS")
print("=" * 80)

test("Path traversal attacks blocked", test_path_traversal_attack)
test("Dangerous imports blocked", test_dangerous_imports)
test("Dangerous functions blocked", test_dangerous_functions)
test("File size limits enforced", test_file_size_limit)
test("Invalid Python syntax blocked", test_invalid_python_syntax)
test("Missing STANDARD constant blocked", test_missing_standard_constant)
test("Missing required fields blocked", test_missing_required_fields)
test("Invalid field types blocked", test_invalid_field_types)
test("Reserved filenames blocked", test_reserved_filenames)
test("Uppercase filenames blocked", test_uppercase_filename)

# ====================
# SUMMARY
# ====================

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"📊 Total:  {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n🎉 ALL SECURITY TESTS PASSED!")
    print("The system is secure against known attack vectors.")
else:
    print(f"\n⚠️  {tests_failed} tests failed - review security measures!")

print("=" * 80)
