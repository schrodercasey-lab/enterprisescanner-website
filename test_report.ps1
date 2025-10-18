# Test Weekly Report - No SSH, No External Dependencies
# This version is 100% local and won't trigger any password prompts

param(
    [string]$WeekEnding = (Get-Date).ToString("yyyy-MM-dd")
)

Write-Host "`n=== Weekly Report Generator (Test Mode) ===" -ForegroundColor Cyan
Write-Host "Week Ending: $WeekEnding`n" -ForegroundColor White

# Check if Fortune 500 tracker exists
$trackerPath = ".\fortune500_tracker.csv"
$hasTracker = Test-Path $trackerPath

if ($hasTracker) {
    Write-Host "[+] Reading Fortune 500 tracker..." -ForegroundColor Green
    
    try {
        $contacts = Import-Csv $trackerPath
        
        # Calculate Fortune 500 metrics (fixed version)
        $totalContacts = $contacts.Count
        $contacted = ($contacts | Where-Object { $_.Status -ne "Not contacted" }).Count
        $meetings = ($contacts | Where-Object { $_.Status -eq "Meeting scheduled" -or $_.Status -eq "In negotiation" }).Count
        
        # Convert Deal_Size to numeric (remove commas, convert to int)
        $totalPipeline = 0
        foreach ($contact in $contacts) {
            if ($contact.Deal_Size) {
                $dealValue = [int]($contact.Deal_Size -replace '[^\d]', '')
                $totalPipeline += $dealValue
            }
        }
        
        $activePipeline = 0
        foreach ($contact in ($contacts | Where-Object { $_.Status -eq "In negotiation" })) {
            if ($contact.Deal_Size) {
                $dealValue = [int]($contact.Deal_Size -replace '[^\d]', '')
                $activePipeline += $dealValue
            }
        }
        
        Write-Host "[+] Fortune 500 Metrics Calculated:" -ForegroundColor Green
        Write-Host "  Total Contacts: $totalContacts" -ForegroundColor White
        Write-Host "  Contacted: $contacted" -ForegroundColor White
        Write-Host "  Meetings: $meetings" -ForegroundColor White
        Write-Host "  Total Pipeline: `$$($totalPipeline.ToString('N0'))" -ForegroundColor Yellow
        Write-Host "  Active Pipeline: `$$($activePipeline.ToString('N0'))" -ForegroundColor Yellow
    }
    catch {
        Write-Host "[!] Error reading tracker: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "[!] Fortune 500 tracker not found at $trackerPath" -ForegroundColor Yellow
}

Write-Host "`n[+] Test Complete - No password prompts!" -ForegroundColor Green
Write-Host "[i] The full weekly_report.ps1 script works the same way`n" -ForegroundColor Cyan
