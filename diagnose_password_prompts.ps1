# Deep Diagnostic Script for Password Prompt Issue
# Created: October 16, 2025
# Purpose: Find root cause of password prompts

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   DEEP DIAGNOSTIC - PASSWORD PROMPT ROOT CAUSE   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$results = @()

# SECTION 1: PowerShell Environment
Write-Host "[1/10] Checking PowerShell Environment..." -ForegroundColor Yellow
$results += "=== POWERSHELL ENVIRONMENT ==="
$results += "Version: $($PSVersionTable.PSVersion)"
$results += "Edition: $($PSVersionTable.PSEdition)"
$results += "ExecutionPolicy: $(Get-ExecutionPolicy)"
$results += "Profile Path: $PROFILE"
$results += "Profile Exists: $(Test-Path $PROFILE)"
Write-Host "      ✓ Complete" -ForegroundColor Green

# SECTION 2: Git Configuration
Write-Host "[2/10] Checking Git Configuration..." -ForegroundColor Yellow
$results += "`n=== GIT CONFIGURATION ==="
try {
    $gitVersion = git --version 2>&1
    $results += "Git Version: $gitVersion"
    
    $gitCredHelper = git config --global credential.helper 2>&1
    $results += "Credential Helper: $gitCredHelper"
    
    $gitUser = git config --global user.name 2>&1
    $results += "Git User: $gitUser"
    
    $gitEmail = git config --global user.email 2>&1
    $results += "Git Email: $gitEmail"
    
    Write-Host "      ✓ Complete" -ForegroundColor Green
} catch {
    $results += "Git Error: $_"
    Write-Host "      ⚠ Git check failed" -ForegroundColor Yellow
}

# SECTION 3: SSH Configuration
Write-Host "[3/10] Checking SSH Configuration..." -ForegroundColor Yellow
$results += "`n=== SSH CONFIGURATION ==="
$sshDir = "$env:USERPROFILE\.ssh"
$results += "SSH Directory: $sshDir"
$results += "SSH Dir Exists: $(Test-Path $sshDir)"

if (Test-Path $sshDir) {
    $sshFiles = Get-ChildItem $sshDir -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    $results += "SSH Files: $($sshFiles -join ', ')"
} else {
    $results += "SSH Files: None (directory doesn't exist)"
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# SECTION 4: SSH Agent Service
Write-Host "[4/10] Checking SSH Agent Service..." -ForegroundColor Yellow
$results += "`n=== SSH AGENT SERVICE ==="
try {
    $sshAgent = Get-Service ssh-agent -ErrorAction SilentlyContinue
    if ($sshAgent) {
        $results += "SSH Agent Status: $($sshAgent.Status)"
        $results += "SSH Agent StartType: $($sshAgent.StartType)"
    } else {
        $results += "SSH Agent: Not installed"
    }
    Write-Host "      ✓ Complete" -ForegroundColor Green
} catch {
    $results += "SSH Agent Error: $_"
    Write-Host "      ⚠ SSH Agent check failed" -ForegroundColor Yellow
}

# SECTION 5: Running Processes
Write-Host "[5/10] Checking Running Processes..." -ForegroundColor Yellow
$results += "`n=== RUNNING PROCESSES (SSH/GIT RELATED) ==="
$processes = Get-Process | Where-Object {
    $_.Name -match "ssh|git|plink|putty|wsl|bash"
} | Select-Object Name, Id, Path -First 20
$results += $processes | ForEach-Object { "$($_.Name) (PID: $($_.Id))" }
Write-Host "      ✓ Complete" -ForegroundColor Green

# SECTION 6: VS Code Extensions
Write-Host "[6/10] Checking VS Code Extensions..." -ForegroundColor Yellow
$results += "`n=== VS CODE EXTENSIONS ==="
try {
    $extensions = code --list-extensions 2>&1 | Where-Object {
        $_ -match "git|ssh|remote|azure"
    }
    if ($extensions) {
        $results += $extensions
    } else {
        $results += "No Git/SSH/Remote extensions found"
    }
    Write-Host "      ✓ Complete" -ForegroundColor Green
} catch {
    $results += "VS Code check failed: $_"
    Write-Host "      ⚠ VS Code check failed" -ForegroundColor Yellow
}

# SECTION 7: Environment Variables
Write-Host "[7/10] Checking Environment Variables..." -ForegroundColor Yellow
$results += "`n=== ENVIRONMENT VARIABLES (AUTH RELATED) ==="
$authVars = Get-ChildItem Env: | Where-Object {
    $_.Name -match "SSH|GIT|CREDENTIAL|AUTH|PASSWORD|TOKEN"
} | Select-Object Name, Value
if ($authVars) {
    $results += $authVars | ForEach-Object { "$($_.Name) = $($_.Value)" }
} else {
    $results += "No authentication-related environment variables found"
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# SECTION 8: OneDrive Status
Write-Host "[8/10] Checking OneDrive..." -ForegroundColor Yellow
$results += "`n=== ONEDRIVE STATUS ==="
$oneDriveProcess = Get-Process OneDrive -ErrorAction SilentlyContinue
if ($oneDriveProcess) {
    $results += "OneDrive Running: Yes (PID: $($oneDriveProcess.Id))"
    $results += "Workspace in OneDrive: $($PWD.Path -match 'OneDrive')"
} else {
    $results += "OneDrive Running: No"
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# SECTION 9: Windows Credential Manager
Write-Host "[9/10] Checking Windows Credential Manager..." -ForegroundColor Yellow
$results += "`n=== WINDOWS CREDENTIAL MANAGER ==="
try {
    # Check for stored credentials
    $creds = cmdkey /list 2>&1 | Select-String -Pattern "git|github|ssh|digitalocean"
    if ($creds) {
        $results += "Stored Credentials Found:"
        $results += $creds
    } else {
        $results += "No Git/SSH credentials in Windows Credential Manager"
    }
    Write-Host "      ✓ Complete" -ForegroundColor Green
} catch {
    $results += "Credential Manager check failed: $_"
    Write-Host "      ⚠ Credential check failed" -ForegroundColor Yellow
}

# SECTION 10: Profile Content Analysis
Write-Host "[10/10] Analyzing Profile Content..." -ForegroundColor Yellow
$results += "`n=== PROFILE CONTENT ANALYSIS ==="
$profilePath = "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\PowerShell_Profile.ps1"
if (Test-Path $profilePath) {
    $profileContent = Get-Content $profilePath -Raw
    
    # Check for suspicious patterns
    $hasSSH = $profileContent -match "ssh "
    $hasSCP = $profileContent -match "scp "
    $hasPassword = $profileContent -match "password|credential"
    $hasImportModule = $profileContent -match "Import-Module"
    $hasInvokeCommand = $profileContent -match "Invoke-Command|Invoke-Expression"
    
    $results += "Contains 'ssh ' command: $hasSSH"
    $results += "Contains 'scp ' command: $hasSCP"
    $results += "Contains password/credential: $hasPassword"
    $results += "Contains Import-Module: $hasImportModule"
    $results += "Contains Invoke-Command/Expression: $hasInvokeCommand"
    
    # Count functions
    $functionCount = ([regex]::Matches($profileContent, "function ")).Count
    $results += "Function count: $functionCount"
    
    Write-Host "      ✓ Complete" -ForegroundColor Green
} else {
    $results += "Profile not found at: $profilePath"
    Write-Host "      ⚠ Profile not found" -ForegroundColor Yellow
}

# ANALYSIS SUMMARY
Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  ANALYSIS COMPLETE                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Save results
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$outputFile = "diagnostic_report_$timestamp.txt"
$results | Out-File $outputFile -Encoding UTF8

Write-Host "📄 Full diagnostic report saved to:" -ForegroundColor Green
Write-Host "   $outputFile" -ForegroundColor White
Write-Host ""

# Display summary
Write-Host "🔍 KEY FINDINGS:" -ForegroundColor Yellow
Write-Host ""

# Determine likely causes
$likelyCauses = @()

# Check Git credential helper
$gitCredHelperResult = $results | Where-Object { $_ -match "Credential Helper:" }
if ($gitCredHelperResult -and $gitCredHelperResult -notmatch "Credential Helper: $" -and $gitCredHelperResult -notmatch "not configured") {
    $likelyCauses += "Git Credential Helper is configured: $gitCredHelperResult"
}

# Check SSH Agent
$sshAgentResult = $results | Where-Object { $_ -match "SSH Agent Status:" }
if ($sshAgentResult -and $sshAgentResult -match "Running|Started") {
    $likelyCauses += "SSH Agent is running: $sshAgentResult"
}

# Check OneDrive
$oneDriveResult = $results | Where-Object { $_ -match "OneDrive Running: Yes" }
if ($oneDriveResult) {
    $workspaceInOneDrive = $results | Where-Object { $_ -match "Workspace in OneDrive: True" }
    if ($workspaceInOneDrive) {
        $likelyCauses += "Workspace is in OneDrive folder (may cause file access prompts)"
    }
}

# Check VS Code extensions
$vsCodeGitExt = $results | Where-Object { $_ -match "git" -and $_ -match "vscode" }
if ($vsCodeGitExt) {
    $likelyCauses += "VS Code Git-related extensions detected: May prompt for auth"
}

# Check for profile issues
$profileSSH = $results | Where-Object { $_ -match "Contains 'ssh ' command: True" }
if ($profileSSH) {
    $likelyCauses += "⚠️  CRITICAL: Profile contains SSH commands!"
}

if ($likelyCauses.Count -eq 0) {
    Write-Host "   No obvious authentication triggers found." -ForegroundColor Green
    Write-Host "   The password prompts may be coming from:" -ForegroundColor Yellow
    Write-Host "   • Windows Credential Manager prompts" -ForegroundColor Gray
    Write-Host "   • VS Code extension background operations" -ForegroundColor Gray
    Write-Host "   • Git background fetch operations" -ForegroundColor Gray
} else {
    Write-Host "   POTENTIAL CAUSES IDENTIFIED:" -ForegroundColor Red
    Write-Host ""
    foreach ($cause in $likelyCauses) {
        Write-Host "   • $cause" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📋 RECOMMENDED ACTIONS:" -ForegroundColor Cyan
Write-Host ""

# Generate recommendations
if ($results -match "Credential Helper:.*manager") {
    Write-Host "1. Git Credential Manager is active" -ForegroundColor White
    Write-Host "   Run: git config --global --unset credential.helper" -ForegroundColor Gray
    Write-Host ""
}

if ($results -match "SSH Dir Exists: False") {
    Write-Host "2. Set up SSH keys for passwordless access" -ForegroundColor White
    Write-Host "   Run: ssh-keygen -t ed25519" -ForegroundColor Gray
    Write-Host ""
}

if ($results -match "OneDrive Running: Yes") {
    Write-Host "3. Consider moving .ssh folder outside OneDrive" -ForegroundColor White
    Write-Host "   OneDrive may interfere with SSH key access" -ForegroundColor Gray
    Write-Host ""
}

if ($results -match "Contains 'ssh ' command: True") {
    Write-Host "4. CRITICAL: Remove SSH commands from profile!" -ForegroundColor Red
    Write-Host "   Your profile should only contain function definitions" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "🔧 NEXT STEPS:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Review the full report: $outputFile" -ForegroundColor White
Write-Host "2. Apply recommended fixes above" -ForegroundColor White
Write-Host "3. Test profile reload: . `$PROFILE" -ForegroundColor White
Write-Host "4. If still having issues, share the diagnostic report" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
