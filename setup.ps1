# Quick Setup Script for AI Study Buddy

Write-Host "🎓 Setting up AI Study Buddy..." -ForegroundColor Cyan

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
Write-Host "`nSetting up environment variables..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env and add your OpenAI or Anthropic API key!" -ForegroundColor Red
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create necessary folders
Write-Host "`nCreating folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path uploads | Out-Null
New-Item -ItemType Directory -Force -Path processed | Out-Null

Write-Host "`n✨ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file and add your API key" -ForegroundColor White
Write-Host "2. Run: python app.py" -ForegroundColor White
Write-Host "3. Open browser to http://localhost:8000" -ForegroundColor White
Write-Host "`nHappy Learning! 🎓" -ForegroundColor Magenta
