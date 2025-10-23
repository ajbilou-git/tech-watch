#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Configure Windows Task Scheduler pour exécuter la veille technologique quotidiennement

.DESCRIPTION
    Crée une tâche planifiée Windows qui exécute la veille technologique tous les jours
    à l'heure spécifiée et ouvre automatiquement le rapport

.PARAMETER TaskTime
    Heure d'exécution quotidienne (format HH:mm, par défaut 09:00)

.PARAMETER TaskName
    Nom de la tâche dans le planificateur (par défaut "MastermaintTechWatch")

.EXAMPLE
    .\setup_task_scheduler.ps1
    Configure la tâche pour s'exécuter à 09:00

.EXAMPLE
    .\setup_task_scheduler.ps1 -TaskTime "08:30"
    Configure la tâche pour s'exécuter à 08:30
#>

[CmdletBinding()]
param(
    [string]$TaskTime = "09:00",
    [string]$TaskName = "MastermaintTechWatch"
)

# Vérifier les privilèges administrateur
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunScript = Join-Path $ScriptDir "run_tech_watch.ps1"

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Configuration du Planificateur de Tâches Windows                ║" -ForegroundColor Cyan
Write-Host "║   Veille Technologique mastermaint                                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Vérification des privilèges
if (-not (Test-Administrator)) {
    Write-Host "⚠️  Ce script nécessite des privilèges administrateur" -ForegroundColor Yellow
    Write-Host "   Relancez PowerShell en tant qu'administrateur et réessayez" -ForegroundColor Yellow
    exit 1
}

# Vérifier que le script existe
if (-not (Test-Path $RunScript)) {
    Write-Host "❌ Script introuvable: $RunScript" -ForegroundColor Red
    exit 1
}

try {
    # Supprimer la tâche existante si elle existe
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "🗑️  Suppression de la tâche existante..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # Configuration de l'action
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$RunScript`" -OpenReport" `
        -WorkingDirectory $ScriptDir
    
    # Configuration du déclencheur (quotidien)
    $trigger = New-ScheduledTaskTrigger -Daily -At $TaskTime
    
    # Configuration des paramètres
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable
    
    # Principal (utilisateur actuel)
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -RunLevel Limited
    
    # Description
    $description = "Veille technologique quotidienne pour l'infrastructure mastermaint. Agrège les flux RSS des technologies utilisées et génère un rapport HTML."
    
    # Créer la tâche
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description $description | Out-Null
    
    Write-Host "✅ Tâche planifiée créée avec succès!" -ForegroundColor Green
    Write-Host "`n📋 Détails de la tâche:" -ForegroundColor Cyan
    Write-Host "   Nom          : $TaskName" -ForegroundColor White
    Write-Host "   Heure        : $TaskTime (quotidien)" -ForegroundColor White
    Write-Host "   Script       : $RunScript" -ForegroundColor White
    Write-Host "   Utilisateur  : $env:USERNAME" -ForegroundColor White
    
    Write-Host "`n💡 Conseils:" -ForegroundColor Yellow
    Write-Host "   • La tâche s'exécutera tous les jours à $TaskTime" -ForegroundColor White
    Write-Host "   • Le rapport s'ouvrira automatiquement dans votre navigateur" -ForegroundColor White
    Write-Host "   • Pour modifier l'heure, relancez ce script avec -TaskTime" -ForegroundColor White
    Write-Host "   • Pour gérer la tâche: Planificateur de tâches > Bibliothèque" -ForegroundColor White
    
    Write-Host "`n🧪 Voulez-vous tester la tâche maintenant? (O/N)" -ForegroundColor Cyan -NoNewline
    $response = Read-Host " "
    
    if ($response -eq "O" -or $response -eq "o") {
        Write-Host "`n▶️  Lancement de la tâche..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "✅ Tâche lancée! Vérifiez la sortie dans une nouvelle fenêtre." -ForegroundColor Green
    }
    
    Write-Host ""
}
catch {
    Write-Host "❌ Erreur lors de la création de la tâche: $_" -ForegroundColor Red
    exit 1
}
