# PowerShell script to install ER707 WAN Monitor as a Windows Service
# Requires NSSM (Non-Sucking Service Manager)
#
# Usage:
#   1. Download NSSM from https://nssm.cc/download
#   2. Extract nssm.exe to a folder in your PATH or to this directory
#   3. Edit the variables below to match your environment
#   4. Run this script as Administrator: .\install_windows_service.ps1

# Configuration - UPDATE THESE VALUES
$ServiceName = "ER707WANMonitor"
$DisplayName = "ER707 WAN IP Monitor"
$Description = "Monitors ER707 WAN IP and performs automatic remediation when private IP is detected"
$PythonPath = "C:\Python\python.exe"  # Update to your Python installation path
$ScriptPath = "$PSScriptRoot\er707_wan_monitor.py"
$WorkingDirectory = $PSScriptRoot

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check if NSSM is available
$nssmPath = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssmPath) {
    Write-Host "ERROR: NSSM not found in PATH" -ForegroundColor Red
    Write-Host "Please download NSSM from https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "Extract nssm.exe to a folder in your PATH or to this directory" -ForegroundColor Yellow
    exit 1
}

# Check if Python exists
if (-not (Test-Path $PythonPath)) {
    Write-Host "ERROR: Python not found at $PythonPath" -ForegroundColor Red
    Write-Host "Please update the PythonPath variable in this script" -ForegroundColor Yellow
    exit 1
}

# Check if script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script not found at $ScriptPath" -ForegroundColor Red
    exit 1
}

# Check if service already exists
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Service '$ServiceName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove and reinstall? (y/n)"
    if ($response -eq 'y') {
        Write-Host "Stopping service..." -ForegroundColor Cyan
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        
        Write-Host "Removing service..." -ForegroundColor Cyan
        nssm remove $ServiceName confirm
    } else {
        Write-Host "Installation cancelled" -ForegroundColor Yellow
        exit 0
    }
}

# Install service
Write-Host "Installing service '$ServiceName'..." -ForegroundColor Cyan
nssm install $ServiceName $PythonPath $ScriptPath

# Configure service
Write-Host "Configuring service..." -ForegroundColor Cyan
nssm set $ServiceName AppDirectory $WorkingDirectory
nssm set $ServiceName DisplayName $DisplayName
nssm set $ServiceName Description $Description
nssm set $ServiceName Start SERVICE_AUTO_START

# Configure stdout/stderr logging
$logDir = Join-Path $WorkingDirectory "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
nssm set $ServiceName AppStdout (Join-Path $logDir "service_output.log")
nssm set $ServiceName AppStderr (Join-Path $logDir "service_error.log")

# Configure restart behavior
nssm set $ServiceName AppExit Default Restart
nssm set $ServiceName AppRestartDelay 5000

Write-Host ""
Write-Host "Service installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit config.yaml with your Omada Controller details"
Write-Host "2. Start the service: nssm start $ServiceName"
Write-Host "3. Check status: nssm status $ServiceName"
Write-Host "4. View logs in: $logDir"
Write-Host ""
Write-Host "Service management commands:" -ForegroundColor Cyan
Write-Host "  Start:   nssm start $ServiceName"
Write-Host "  Stop:    nssm stop $ServiceName"
Write-Host "  Restart: nssm restart $ServiceName"
Write-Host "  Status:  nssm status $ServiceName"
Write-Host "  Remove:  nssm remove $ServiceName"
Write-Host ""
