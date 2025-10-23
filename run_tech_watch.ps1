#Requires -Version 5.1
<#
.SYNOPSIS
    Automation script for mastermaint tech watch

.DESCRIPTION
    Runs the tech watch and automatically opens the generated report in the browser
    Can be used manually or via Windows Task Scheduler

.PARAMETER OpenReport
    Automatically opens the report in the default browser

.EXAMPLE
    .\run_tech_watch.ps1
    Runs the tech watch and displays the result

.EXAMPLE
    .\run_tech_watch.ps1 -OpenReport
    Runs the tech watch and opens the HTML report
#>

[CmdletBinding()]
param(
    [switch]$OpenReport = $false
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ScriptDir "venv"
$PythonScript = Join-Path $ScriptDir "tech_watch.py"
$ConfigFile = Join-Path $ScriptDir "config.yaml"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "Python detected: $pythonVersion" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "Python is not installed or not in PATH" "Red"
        Write-ColorOutput "Install Python from https://www.python.org/downloads/" "Yellow"
        return $false
    }
}

function Initialize-VirtualEnv {
    if (-not (Test-Path $VenvPath)) {
        Write-ColorOutput "Creating Python virtual environment..." "Cyan"
        python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "Error creating virtual environment" "Red"
            exit 1
        }
    }
}

function Install-Dependencies {
    $RequirementsFile = Join-Path $ScriptDir "requirements.txt"
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    Write-ColorOutput "Installing/Verifying dependencies..." "Cyan"
    & $ActivateScript
    python -m pip install --upgrade pip --quiet
    pip install -r $RequirementsFile --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Error installing dependencies" "Red"
        exit 1
    }
}

function Start-TechWatch {
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    Write-ColorOutput "`nStarting tech watch..." "Cyan"
    Write-ColorOutput ("=" * 70) "Gray"
    & $ActivateScript
    $output = python $PythonScript 2>&1
    $exitCode = $LASTEXITCODE
    Write-Output $output
    if ($exitCode -eq 0) {
        Write-ColorOutput "`nTech watch completed successfully!" "Green"
        return $true
    }
    else {
        Write-ColorOutput "`nTech watch failed" "Red"
        return $false
    }
}

function Get-LatestReport {
    $ReportsDir = Join-Path $ScriptDir "reports"
    if (-not (Test-Path $ReportsDir)) { return $null }
    $reports = Get-ChildItem -Path $ReportsDir -Filter "tech_watch_*.html" | 
               Sort-Object LastWriteTime -Descending | Select-Object -First 1
    return $reports
}

function Open-Report {
    param([string]$ReportPath)
    if (Test-Path $ReportPath) {
        Write-ColorOutput "`nOpening report in browser..." "Cyan"
        Start-Process $ReportPath
    }
}

function Main {
    Write-ColorOutput "`n============================================================" "Magenta"
    Write-ColorOutput "  Tech Watch - Infrastructure Monitoring" "Magenta"
    Write-ColorOutput "============================================================`n" "Magenta"
    
    if (-not (Test-PythonInstalled)) { exit 1 }
    if (-not (Test-Path $ConfigFile)) {
        Write-ColorOutput "Configuration file not found: $ConfigFile" "Red"
        exit 1
    }
    
    try {
        Initialize-VirtualEnv
        Install-Dependencies
    }
    catch {
        Write-ColorOutput "Error during preparation: $_" "Red"
        exit 1
    }
    
    $success = Start-TechWatch
    
    if ($success) {
        $latestReport = Get-LatestReport
        if ($latestReport) {
            Write-ColorOutput "`nReport available: $($latestReport.FullName)" "Green"
            if ($OpenReport) {
                Open-Report $latestReport.FullName
            }
            else {
                Write-ColorOutput "To auto-open the report, use: .\run_tech_watch.ps1 -OpenReport" "Yellow"
            }
        }
    }
    Write-ColorOutput "`n" "White"
}

Main
