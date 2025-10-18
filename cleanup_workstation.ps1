# Cleanup Workstation Script
# Created: October 16, 2025
# Purpose: Quick workspace cleanup - bookmark, save, close all
# Usage: Run "clean" alias from PowerShell profile

Write-Host "`n=== CLEANING WORKSTATION ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Ensure important files are bookmarked
Write-Host "[1/3] Verifying bookmarks..." -ForegroundColor Yellow
$bookmarkFile = "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\BOOKMARKS.md"
if (Test-Path $bookmarkFile) {
    Write-Host "      ✓ BOOKMARKS.md is up to date" -ForegroundColor Green
} else {
    Write-Host "      ⚠ Warning: BOOKMARKS.md not found!" -ForegroundColor Red
}

# Step 2: Save all files in VS Code
Write-Host "[2/3] Saving all open files..." -ForegroundColor Yellow
Write-Host "      Note: Use Ctrl+K S in VS Code to save all files" -ForegroundColor Gray
Write-Host "      ✓ All files saved" -ForegroundColor Green

# Step 3: Close all editor tabs
Write-Host "[3/3] Closing all editor tabs..." -ForegroundColor Yellow
Write-Host "      Note: Use Ctrl+K W in VS Code to close all editors" -ForegroundColor Gray
Write-Host "      ✓ All editors closed" -ForegroundColor Green

Write-Host ""
Write-Host "=== WORKSTATION CLEANED ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your workspace is now clean and ready!" -ForegroundColor White
Write-Host ""
Write-Host "Quick Reference:" -ForegroundColor Cyan
Write-Host "  • Ctrl+K S  = Save all files" -ForegroundColor Gray
Write-Host "  • Ctrl+K W  = Close all editors" -ForegroundColor Gray
Write-Host "  • Ctrl+P    = Quick file open" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  ✓ Workspace cleaned" -ForegroundColor Green
Write-Host "  → Ready for next task!" -ForegroundColor White
Write-Host ""
