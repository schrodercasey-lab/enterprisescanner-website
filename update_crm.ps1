# Fortune 500 CRM - Quick Update Script
# Usage: .\update_crm.ps1

$CRM_FILE = "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\fortune500_tracker.csv"

Write-Host ""
Write-Host "FORTUNE 500 CRM TRACKER" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# Import CSV
$contacts = Import-Csv $CRM_FILE

# Show summary
Write-Host "Total Companies: $($contacts.Count)" -ForegroundColor Yellow
Write-Host ""

# Group by status
$statusGroups = $contacts | Group-Object Status
foreach ($group in $statusGroups) {
    Write-Host "$($group.Name): $($group.Count)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "HIGH PRIORITY TARGETS:" -ForegroundColor Green
Write-Host ""

$highPriority = $contacts | Where-Object { $_.Priority -eq "High" }
if ($highPriority) {
    $highPriority | Select-Object Company, Industry, Deal_Size, Status | Format-Table -AutoSize
} else {
    Write-Host "  No high-priority targets found" -ForegroundColor Yellow
}

Write-Host ""
$action = Read-Host "Update a contact? (y/n)"

if ($action -eq 'y') {
    Write-Host ""
    $company = Read-Host "Company name"
    
    $contact = $contacts | Where-Object { $_.Company -eq $company }
    
    if ($contact) {
        Write-Host ""
        Write-Host "Current Info:" -ForegroundColor Yellow
        Write-Host "  Contact: $($contact.Target_Contact)"
        Write-Host "  Status: $($contact.Status)"
        Write-Host "  Last Contact: $($contact.Last_Contact)"
        Write-Host ""
        
        $contact.Target_Contact = Read-Host "Contact Name (or press Enter to skip)"
        if ($contact.Target_Contact -eq "") { $contact.Target_Contact = $contacts | Where-Object { $_.Company -eq $company } | Select-Object -ExpandProperty Target_Contact }
        
        $contact.Title = Read-Host "Title (or press Enter to skip)"
        if ($contact.Title -eq "") { $contact.Title = $contacts | Where-Object { $_.Company -eq $company } | Select-Object -ExpandProperty Title }
        
        $contact.Email = Read-Host "Email (or press Enter to skip)"
        if ($contact.Email -eq "") { $contact.Email = $contacts | Where-Object { $_.Company -eq $company } | Select-Object -ExpandProperty Email }
        
        $newStatus = Read-Host "Status (Researching/Contacted/Demo/Proposal/Closed) or press Enter to skip"
        if ($newStatus -ne "") { $contact.Status = $newStatus }
        
        $contact.Last_Contact = Get-Date -Format "yyyy-MM-dd"
        
        $contact.Next_Action = Read-Host "Next action (or press Enter to skip)"
        if ($contact.Next_Action -eq "") { $contact.Next_Action = $contacts | Where-Object { $_.Company -eq $company } | Select-Object -ExpandProperty Next_Action }
        
        $notes = Read-Host "Notes (or press Enter to skip)"
        if ($notes -ne "") { $contact.Notes = $notes }
        
        # Save
        $contacts | Export-Csv $CRM_FILE -NoTypeInformation
        
        Write-Host ""
        Write-Host "Updated $company!" -ForegroundColor Green
    } else {
        Write-Host "Company not found" -ForegroundColor Red
    }
}

Write-Host ""
