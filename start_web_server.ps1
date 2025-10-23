# Script pour demarrer un serveur web local
# Affiche le rapport de veille technologique sur http://localhost:8000

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReportsDir = Join-Path $ScriptDir "reports"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Serveur Web - Veille Technologique" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demarrage du serveur web local..." -ForegroundColor Green
Write-Host "URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pour arreter le serveur, appuyez sur Ctrl+C" -ForegroundColor Red
Write-Host ""

# Demarrer le serveur Python
Set-Location $ReportsDir
python -m http.server 8000

# Retourner au dossier initial
Set-Location $ScriptDir
