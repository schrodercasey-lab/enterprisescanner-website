# Debug CSV Import
$contacts = Import-Csv .\fortune500_tracker.csv
$first = $contacts[0]

Write-Host "First Contact Debug:" -ForegroundColor Cyan
Write-Host "Company: '$($first.Company)'" -ForegroundColor White
Write-Host "Industry: '$($first.Industry)'" -ForegroundColor White
Write-Host "Target_Contact: '$($first.Target_Contact)'" -ForegroundColor White
Write-Host "Title: '$($first.Title)'" -ForegroundColor White
Write-Host "Email: '$($first.Email)'" -ForegroundColor White
Write-Host "Phone: '$($first.Phone)'" -ForegroundColor White
Write-Host "LinkedIn: '$($first.LinkedIn)'" -ForegroundColor White
Write-Host "Status: '$($first.Status)'" -ForegroundColor Yellow
Write-Host "Last_Contact: '$($first.Last_Contact)'" -ForegroundColor White
Write-Host "Next_Action: '$($first.Next_Action)'" -ForegroundColor White
Write-Host "Deal_Size: '$($first.Deal_Size)'" -ForegroundColor Green
Write-Host "Priority: '$($first.Priority)'" -ForegroundColor White
Write-Host "Notes: '$($first.Notes)'" -ForegroundColor White

Write-Host "`nAll Properties:" -ForegroundColor Cyan
$first.PSObject.Properties | ForEach-Object {
    Write-Host "  $($_.Name) = '$($_.Value)'" -ForegroundColor Gray
}
