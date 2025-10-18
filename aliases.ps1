# Quick Alias Loader
# Run this anytime: . .\aliases.ps1

# Navigation shortcuts
function ws { Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace }
function web { Set-Location C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website }

# Deployment shortcuts
function dt { .\simple_deploy.ps1 -test }
function deploy { .\simple_deploy.ps1 -all }
function backup { .\simple_backup.ps1 }

# Fortune 500 CRM shortcuts
function crm { .\update_crm.ps1 }
function contacts { Import-Csv .\fortune500_tracker.csv | Format-Table Company, Industry, Deal_Size, Priority, Status -AutoSize }
function hot { Import-Csv .\fortune500_tracker.csv | Where-Object {$_.Priority -eq "High"} | Format-Table Company, Industry, Deal_Size, Status -AutoSize }

# Reporting shortcuts
function report { .\weekly_report.ps1 }
function perf { .\perf_report.ps1 }

# Documentation shortcuts
function prompts { notepad AI_PROMPT_TEMPLATES.md }
function snippets { notepad CODE_SNIPPETS.md }
function shortcuts { notepad KEYBOARD_SHORTCUTS.md }

# Quick commands
function ll { Get-ChildItem | Format-Table -AutoSize }

Write-Host "Aliases loaded! Try: hot, crm, deploy, contacts" -ForegroundColor Green
