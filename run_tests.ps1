# Quick Test Runner for Multi-Tenant System
# Run with: .\run_tests.ps1

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Multi-Tenant Credential System Test Runner" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if PostgreSQL is running
Write-Host "`n[1/6] Checking PostgreSQL..." -ForegroundColor Yellow
$pgStatus = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgStatus -and $pgStatus.Status -eq "Running") {
    Write-Host "  ✓ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "  ✗ PostgreSQL is not running" -ForegroundColor Red
    Write-Host "  Start it with: net start postgresql-x64-14" -ForegroundColor Yellow
    exit 1
}

# Check environment variables
Write-Host "`n[2/6] Checking environment variables..." -ForegroundColor Yellow

if (-not $env:DATABASE_URL) {
    Write-Host "  ⚠ DATABASE_URL not set, using default: postgresql://localhost/securiva_test" -ForegroundColor Yellow
    $env:DATABASE_URL = "postgresql://localhost/securiva_test"
}
Write-Host "  DATABASE_URL: $env:DATABASE_URL" -ForegroundColor Gray

if (-not $env:ENCRYPTION_KEY) {
    Write-Host "  ⚠ ENCRYPTION_KEY not set, generating temporary key..." -ForegroundColor Yellow
    $env:ENCRYPTION_KEY = [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
    Write-Host "  Generated key: $($env:ENCRYPTION_KEY.Substring(0, 20))..." -ForegroundColor Gray
}

if (-not $env:JWT_SECRET_KEY) {
    Write-Host "  ⚠ JWT_SECRET_KEY not set, using test key" -ForegroundColor Yellow
    $env:JWT_SECRET_KEY = "test-jwt-secret-key-for-development"
}

# Check if database exists
Write-Host "`n[3/6] Checking test database..." -ForegroundColor Yellow
$dbExists = psql -lqt | Select-String -Pattern "securiva_test"
if (-not $dbExists) {
    Write-Host "  Creating test database..." -ForegroundColor Yellow
    createdb securiva_test
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database created" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to create database" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✓ Test database exists" -ForegroundColor Green
}

# Run migrations
Write-Host "`n[4/6] Running migrations..." -ForegroundColor Yellow
$migrationFile = "backend\my_app\server\migrations\001_multitenant_credentials_schema.sql"
if (Test-Path $migrationFile) {
    psql securiva_test -f $migrationFile 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Migrations applied" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Migrations may have already been applied" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Migration file not found: $migrationFile" -ForegroundColor Red
    exit 1
}

# Check Python and dependencies
Write-Host "`n[5/6] Checking Python dependencies..." -ForegroundColor Yellow
python --version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python is available" -ForegroundColor Green

# Check key dependencies
$requiredModules = @("psycopg2", "cryptography", "google-auth")
foreach ($module in $requiredModules) {
    python -c "import $($module.Replace('-', '_'))" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $module installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $module not installed" -ForegroundColor Red
        Write-Host "    Install with: pip install $module" -ForegroundColor Yellow
    }
}

# Run tests
Write-Host "`n[6/6] Running tests..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

# Test 1: Credential Manager
Write-Host "`n[TEST SET 1] Credential Manager Tests" -ForegroundColor Cyan
Write-Host "--------------------------------------" -ForegroundColor Cyan
Set-Location "backend\my_app\server"
python test_multitenant_credentials.py
$test1Result = $LASTEXITCODE

# Test 2: MCP Adapter
Write-Host "`n[TEST SET 2] MCP Adapter Tests" -ForegroundColor Cyan
Write-Host "--------------------------------------" -ForegroundColor Cyan
python test_mcp_adapter.py
$test2Result = $LASTEXITCODE

Set-Location "..\..\..\"

# Summary
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($test1Result -eq 0) {
    Write-Host "  ✓ Credential Manager Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "  ✗ Credential Manager Tests: FAILED" -ForegroundColor Red
}

if ($test2Result -eq 0) {
    Write-Host "  ✓ MCP Adapter Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "  ✗ MCP Adapter Tests: FAILED" -ForegroundColor Red
}

if ($test1Result -eq 0 -and $test2Result -eq 0) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠ Some tests failed. Check output above for details." -ForegroundColor Yellow
    exit 1
}
