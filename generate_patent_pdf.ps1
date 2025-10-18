# USPTO Patent Application PDF Generator
# Converts patent_to_pdf.html to professional PDF format
# October 18, 2025

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "USPTO Patent Application - PDF Generator" -ForegroundColor Cyan
Write-Host "JUPITER VR/AR Cybersecurity Platform" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$htmlFile = "$PSScriptRoot\patent_to_pdf.html"
$outputPdf = "$PSScriptRoot\JUPITER_VR_Patent_Application.pdf"

if (-not (Test-Path $htmlFile)) {
    Write-Host "ERROR: HTML file not found!" -ForegroundColor Red
    Write-Host "Expected: $htmlFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "[Step 1] Opening HTML file in default browser..." -ForegroundColor Green
Start-Process $htmlFile

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "MANUAL STEPS - Follow These Instructions:" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Your browser should have opened with the patent document" -ForegroundColor White
Write-Host ""
Write-Host "2. Press CTRL+P (or Cmd+P on Mac) to open Print dialog" -ForegroundColor White
Write-Host ""
Write-Host "3. Select 'Save as PDF' or 'Microsoft Print to PDF' as destination" -ForegroundColor White
Write-Host ""
Write-Host "4. Configure print settings:" -ForegroundColor White
Write-Host "   - Paper size: Letter (8.5 x 11 inches)" -ForegroundColor Cyan
Write-Host "   - Margins: Default" -ForegroundColor Cyan
Write-Host "   - Pages: All" -ForegroundColor Cyan
Write-Host "   - Background graphics: ON" -ForegroundColor Cyan
Write-Host "   - Headers/Footers: OFF" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Save the PDF with this filename:" -ForegroundColor White
Write-Host "   JUPITER_VR_Patent_Application.pdf" -ForegroundColor Green
Write-Host ""
Write-Host "6. Save it to this location:" -ForegroundColor White
Write-Host "   $PSScriptRoot" -ForegroundColor Green
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host ""

Write-Host "ALTERNATIVE METHOD - Using Microsoft Edge (Recommended):" -ForegroundColor Magenta
Write-Host ""
Write-Host "If you have Microsoft Edge, it can generate PDFs automatically:" -ForegroundColor White
Write-Host ""

# Try to use Edge for automatic PDF generation
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (Test-Path $edgePath) {
    Write-Host "Microsoft Edge detected! Generating PDF automatically..." -ForegroundColor Green
    Write-Host ""
    
    # Use Edge to print to PDF
    $arguments = @(
        "--headless"
        "--disable-gpu"
        "--print-to-pdf=`"$outputPdf`""
        "--no-margins"
        "--print-to-pdf-no-header"
        "`"$htmlFile`""
    )
    
    try {
        Start-Process -FilePath $edgePath -ArgumentList $arguments -Wait -NoNewWindow
        
        if (Test-Path $outputPdf) {
            Write-Host "SUCCESS! PDF generated successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Output file: $outputPdf" -ForegroundColor Cyan
            Write-Host "File size: $([math]::Round((Get-Item $outputPdf).Length / 1MB, 2)) MB" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Opening PDF for verification..." -ForegroundColor Green
            Start-Process $outputPdf
            Write-Host ""
            Write-Host "=" * 70 -ForegroundColor Green
            Write-Host "PDF GENERATION COMPLETE!" -ForegroundColor Green
            Write-Host "=" * 70 -ForegroundColor Green
            Write-Host ""
            Write-Host "NEXT STEPS:" -ForegroundColor Yellow
            Write-Host "1. Review the PDF to ensure it looks correct" -ForegroundColor White
            Write-Host "2. Go to https://patentcenter.uspto.gov/" -ForegroundColor White
            Write-Host "3. Log in and complete Patent Center self-enrollment" -ForegroundColor White
            Write-Host "4. Upload JUPITER_VR_Patent_Application.pdf" -ForegroundColor White
            Write-Host "5. Pay $130 (micro) or $260 (small entity) fee" -ForegroundColor White
            Write-Host "6. Submit your application!" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host "PDF generation failed. Please use manual method above." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Automatic generation failed. Please use manual method above." -ForegroundColor Yellow
        Write-Host "Error: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Microsoft Edge not found in default location." -ForegroundColor Yellow
    Write-Host "Please use manual method described above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
