# Academia Validator Setup Script
# This script helps set up the certificate verification system

Write-Host "=== Academia Validator Setup ===" -ForegroundColor Green
Write-Host "Setting up Certificate Verification System for Government of Jharkhand" -ForegroundColor Cyan

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if pip is available
Write-Host "`nChecking pip installation..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ Found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ pip not found. Please ensure pip is installed with Python" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies. Check your internet connection and try again." -ForegroundColor Red
    exit 1
}

# Check for Tesseract OCR
Write-Host "`nChecking Tesseract OCR installation..." -ForegroundColor Yellow
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
)

$tesseractFound = $false
foreach ($path in $tesseractPaths) {
    if (Test-Path $path) {
        Write-Host "✓ Found Tesseract at: $path" -ForegroundColor Green
        $tesseractFound = $true
        break
    }
}

if (-not $tesseractFound) {
    Write-Host "⚠️  Tesseract OCR not found in common locations" -ForegroundColor Yellow
    Write-Host "Please install Tesseract OCR:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host "2. Or use Chocolatey: choco install tesseract" -ForegroundColor Cyan
    Write-Host "3. Make sure it's in your PATH environment variable" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The system will still run but OCR functionality may not work without Tesseract." -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "`nCreating necessary directories..." -ForegroundColor Yellow
$directories = @("uploads", "database", "static")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "✓ Directory exists: $dir" -ForegroundColor Green
    }
}

# Test basic imports
Write-Host "`nTesting Python imports..." -ForegroundColor Yellow
$testScript = @"
try:
    import flask
    import pytesseract
    import PIL
    import PyPDF2
    print("✓ All required modules can be imported")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
"@

$testScript | python
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All Python modules imported successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Some Python modules failed to import" -ForegroundColor Red
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser to:" -ForegroundColor Cyan
Write-Host "  http://localhost:5000 - Main verification interface" -ForegroundColor White
Write-Host "  http://localhost:5000/admin - Admin dashboard" -ForegroundColor White
Write-Host ""
Write-Host "Happy validating! 🎓" -ForegroundColor Green