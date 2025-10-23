#Requires -Version 5.1
<#
.SYNOPSIS
    Ouvre l'interface web de la veille technologique

.DESCRIPTION
    Genere une page d'index et demarre un serveur web local
    Ouvre automatiquement le navigateur sur http://localhost:8000

.EXAMPLE
    .\open_web_view.ps1
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReportsDir = Join-Path $ScriptDir "reports"
$VenvPath = Join-Path $ScriptDir "venv"
$IndexScript = Join-Path $ScriptDir "create_index.py"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Interface Web - Veille Technologique" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verifier si le dossier reports existe
if (-not (Test-Path $ReportsDir)) {
    Write-Host "Aucun rapport trouve. Lancez d'abord:" -ForegroundColor Yellow
    Write-Host "  .\run_tech_watch.ps1 -OpenReport" -ForegroundColor White
    exit 1
}

# Generer la page d'index
Write-Host "Generation de la page d'index..." -ForegroundColor Cyan

if (Test-Path $VenvPath) {
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    & $ActivateScript
    python $IndexScript
} else {
    python $IndexScript
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de la generation de l'index" -ForegroundColor Red
    exit 1
}

Write-Host "Page d'index generee avec succes!" -ForegroundColor Green
Write-Host ""

# Demarrer le serveur web
Write-Host "Demarrage du serveur web local..." -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: http://localhost:8000" -ForegroundColor Yellow -BackgroundColor Black
Write-Host ""
Write-Host "Ouverture du navigateur dans 2 secondes..." -ForegroundColor Green
Write-Host ""
Write-Host "Pour arreter le serveur: Appuyez sur Ctrl+C" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Ouvrir le navigateur apres 2 secondes
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
} | Out-Null

# Demarrer le serveur
Set-Location $ReportsDir
python -m http.server 8000
