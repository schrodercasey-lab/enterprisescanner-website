# CSV Diagnostic and Fix Tool
# Run this to see what's wrong with the CSV parsing

Write-Host "`n=== CSV Diagnostic Tool ===" -ForegroundColor Cyan

$csvPath = ".\fortune500_tracker.csv"
if (-not (Test-Path $csvPath)) {
    Write-Host "[!] CSV file not found: $csvPath" -ForegroundColor Red
    exit 1
}

# Read raw CSV
Write-Host "`n[1] Reading CSV file..." -ForegroundColor Yellow
$contacts = Import-Csv $csvPath

Write-Host "[+] Total records: $($contacts.Count)" -ForegroundColor Green

# Check first record
Write-Host "`n[2] First Record Analysis:" -ForegroundColor Yellow
$first = $contacts[0]

Write-Host "Company: '$($first.Company)'" -ForegroundColor White
Write-Host "Industry: '$($first.Industry)'" -ForegroundColor White
Write-Host "Deal_Size: '$($first.Deal_Size)'" -ForegroundColor $(if($first.Deal_Size){'Green'}else{'Red'})
Write-Host "Priority: '$($first.Priority)'" -ForegroundColor $(if($first.Priority){'Green'}else{'Red'})
Write-Host "Status: '$($first.Status)'" -ForegroundColor $(if($first.Status){'Green'}else{'Red'})

# Try to convert Deal_Size
Write-Host "`n[3] Testing Deal_Size Conversion:" -ForegroundColor Yellow
if ($first.Deal_Size) {
    try {
        $cleanValue = $first.Deal_Size -replace '[^\d]', ''
        $numericValue = [int]$cleanValue
        Write-Host "[+] Deal_Size '$($first.Deal_Size)' converts to: $numericValue" -ForegroundColor Green
    } catch {
        Write-Host "[!] Failed to convert: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[!] Deal_Size is empty or null" -ForegroundColor Red
}

# Calculate total pipeline with detailed output
Write-Host "`n[4] Calculating Total Pipeline:" -ForegroundColor Yellow
$totalPipeline = 0
$successCount = 0
$failCount = 0

foreach ($contact in $contacts) {
    if ($contact.Deal_Size) {
        try {
            $cleanValue = $contact.Deal_Size -replace '[^\d]', ''
            if ($cleanValue) {
                $dealValue = [int]$cleanValue
                $totalPipeline += $dealValue
                $successCount++
            } else {
                Write-Host "  [!] Empty after cleaning: $($contact.Company)" -ForegroundColor Red
                $failCount++
            }
        } catch {
            Write-Host "  [!] Failed to convert $($contact.Company): '$($contact.Deal_Size)'" -ForegroundColor Red
            $failCount++
        }
    } else {
        Write-Host "  [!] No Deal_Size for: $($contact.Company)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host "`n[5] Results:" -ForegroundColor Yellow
Write-Host "Successfully converted: $successCount" -ForegroundColor Green
Write-Host "Failed conversions: $failCount" -ForegroundColor $(if($failCount -gt 0){'Red'}else{'Green'})
Write-Host "Total Pipeline: `$$($totalPipeline.ToString('N0'))" -ForegroundColor $(if($totalPipeline -gt 0){'Green'}else{'Red'})

# Show all column headers
Write-Host "`n[6] CSV Column Headers:" -ForegroundColor Yellow
$first.PSObject.Properties.Name | ForEach-Object {
    Write-Host "  - $_" -ForegroundColor Gray
}

Write-Host "`n=== Diagnostic Complete ===" -ForegroundColor Cyan
