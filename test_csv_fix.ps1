# Quick CSV Test - Verify Fix
Write-Host "`n=== Testing Fixed CSV ===" -ForegroundColor Cyan

$contacts = Import-Csv .\fortune500_tracker.csv
$first = $contacts[0]

Write-Host "`nFirst Record:" -ForegroundColor Yellow
Write-Host "Company: $($first.Company)" -ForegroundColor White
Write-Host "Industry: $($first.Industry)" -ForegroundColor White
Write-Host "Status: $($first.Status)" -ForegroundColor $(if($first.Status -eq 'Not contacted'){'Green'}else{'Red'})
Write-Host "Deal_Size: $($first.Deal_Size)" -ForegroundColor $(if($first.Deal_Size -eq '150000'){'Green'}else{'Red'})
Write-Host "Priority: $($first.Priority)" -ForegroundColor $(if($first.Priority -eq 'High'){'Green'}else{'Red'})

# Calculate total
$totalPipeline = 0
foreach ($contact in $contacts) {
    if ($contact.Deal_Size) {
        $dealValue = [int]($contact.Deal_Size -replace '[^\d]', '')
        $totalPipeline += $dealValue
    }
}

Write-Host "`nTotal Pipeline: `$$($totalPipeline.ToString('N0'))" -ForegroundColor $(if($totalPipeline -gt 0){'Green'}else{'Red'})
Write-Host "Expected: `$6,500,000" -ForegroundColor Cyan

if ($totalPipeline -eq 6500000) {
    Write-Host "`n✅ CSV IS FIXED! All columns aligned correctly!" -ForegroundColor Green
} elseif ($totalPipeline -gt 0) {
    Write-Host "`n⚠️ CSV is working but total is off. Expected $6.5M, got `$$($totalPipeline.ToString('N0'))" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ CSV still has issues - pipeline is $0" -ForegroundColor Red
}

Write-Host ""
