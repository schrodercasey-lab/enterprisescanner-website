# Enterprise Scanner - PowerShell Profile
# Efficiency aliases for daily workflow
# Created: October 16, 2025

# Navigation shortcuts
function ws { Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace }
function web { Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website }

# Deployment shortcuts
function dt { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\simple_deploy.ps1 -test 
}

function deploy { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\simple_deploy.ps1 -all 
}

function backup { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\simple_backup.ps1 
}

# Fortune 500 CRM shortcuts
function crm { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\update_crm.ps1 
}

function contacts { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    Import-Csv .\fortune500_tracker.csv | Format-Table Company, Industry, Deal_Size, Priority, Status -AutoSize 
}

function hot { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    Import-Csv .\fortune500_tracker.csv | Where-Object {$_.Priority -eq "High"} | Format-Table Company, Industry, Deal_Size, Status -AutoSize 
}

# Reporting shortcuts
function report { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\weekly_report.ps1 
}

function perf { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\perf_report.ps1 
}

# Documentation shortcuts
function prompts { 
    notepad C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\AI_PROMPT_TEMPLATES.md 
}

function snippets { 
    notepad C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\CODE_SNIPPETS.md 
}

function shortcuts { 
    notepad C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\KEYBOARD_SHORTCUTS.md 
}

# Quick commands
function ll { Get-ChildItem | Format-Table -AutoSize }
function clean { 
    Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace
    .\cleanup_workstation.ps1 
}

# Success message
Write-Host ""
Write-Host "=== Enterprise Scanner Aliases Loaded ===" -ForegroundColor Green
Write-Host "Navigation:  ws, web" -ForegroundColor Cyan
Write-Host "Deployment:  dt, deploy, backup" -ForegroundColor Cyan
Write-Host "CRM:         crm, contacts, hot" -ForegroundColor Cyan
Write-Host "Reports:     report, perf" -ForegroundColor Cyan
Write-Host "Docs:        prompts, snippets, shortcuts" -ForegroundColor Cyan
Write-Host "Quick:       ll (list files)" -ForegroundColor Cyan
Write-Host ""
