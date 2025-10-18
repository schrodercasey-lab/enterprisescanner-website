# Profile Load Tracer - Find What Causes Password Prompts
# Created: October 16, 2025
# Purpose: Trace exactly what happens when profile loads

Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       PROFILE LOAD TRACER - DEBUG MODE          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$trace = @()
$trace += "=== PROFILE LOAD TRACE ==="
$trace += "Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$trace += ""

# Check 1: Profile paths
Write-Host "[1/8] Checking profile paths..." -ForegroundColor Yellow
$trace += "=== PROFILE PATHS ==="
$trace += "`$PROFILE = $PROFILE"
$trace += "`$PROFILE.AllUsersAllHosts = $($PROFILE.AllUsersAllHosts)"
$trace += "`$PROFILE.AllUsersCurrentHost = $($PROFILE.AllUsersCurrentHost)"
$trace += "`$PROFILE.CurrentUserAllHosts = $($PROFILE.CurrentUserAllHosts)"
$trace += "`$PROFILE.CurrentUserCurrentHost = $($PROFILE.CurrentUserCurrentHost)"
$trace += ""

# Check each profile location
$profiles = @(
    $PROFILE.AllUsersAllHosts,
    $PROFILE.AllUsersCurrentHost,
    $PROFILE.CurrentUserAllHosts,
    $PROFILE.CurrentUserCurrentHost
)

foreach ($p in $profiles) {
    if (Test-Path $p) {
        $trace += "EXISTS: $p"
        Write-Host "   Found: $p" -ForegroundColor Green
    } else {
        $trace += "NOT FOUND: $p"
    }
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 2: Workspace profile
Write-Host "[2/8] Checking workspace profile..." -ForegroundColor Yellow
$workspaceProfile = "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\PowerShell_Profile.ps1"
$trace += ""
$trace += "=== WORKSPACE PROFILE ==="
$trace += "Path: $workspaceProfile"
$trace += "Exists: $(Test-Path $workspaceProfile)"
if (Test-Path $workspaceProfile) {
    $content = Get-Content $workspaceProfile -Raw
    $trace += "Size: $($content.Length) characters"
    $trace += "Lines: $(($content -split "`n").Count)"
    Write-Host "   ✓ Workspace profile found" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Workspace profile not found" -ForegroundColor Yellow
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 3: OneDrive interference
Write-Host "[3/8] Checking OneDrive status..." -ForegroundColor Yellow
$trace += ""
$trace += "=== ONEDRIVE STATUS ==="
$onedrive = Get-Process OneDrive -ErrorAction SilentlyContinue
if ($onedrive) {
    $trace += "OneDrive Process: Running (PID $($onedrive.Id))"
    $trace += "Current Path: $PWD"
    $trace += "In OneDrive: $($PWD.Path -match 'OneDrive')"
    Write-Host "   OneDrive is running" -ForegroundColor Yellow
} else {
    $trace += "OneDrive Process: Not running"
    Write-Host "   OneDrive not running" -ForegroundColor Green
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 4: Git processes
Write-Host "[4/8] Checking Git processes..." -ForegroundColor Yellow
$trace += ""
$trace += "=== GIT PROCESSES ==="
$gitProcesses = Get-Process | Where-Object { $_.Name -match "git" }
if ($gitProcesses) {
    foreach ($proc in $gitProcesses) {
        $trace += "Git Process: $($proc.Name) (PID $($proc.Id))"
        Write-Host "   Git process found: $($proc.Name)" -ForegroundColor Yellow
    }
} else {
    $trace += "No Git processes running"
    Write-Host "   No Git processes" -ForegroundColor Green
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 5: VS Code processes
Write-Host "[5/8] Checking VS Code processes..." -ForegroundColor Yellow
$trace += ""
$trace += "=== VS CODE PROCESSES ==="
$vscodeProcesses = Get-Process | Where-Object { $_.Name -match "code|vscode" }
if ($vscodeProcesses) {
    $trace += "VS Code Processes: $($vscodeProcesses.Count)"
    Write-Host "   VS Code is running ($($vscodeProcesses.Count) processes)" -ForegroundColor Yellow
} else {
    $trace += "No VS Code processes running"
    Write-Host "   VS Code not running" -ForegroundColor Green
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 6: SSH processes
Write-Host "[6/8] Checking SSH processes..." -ForegroundColor Yellow
$trace += ""
$trace += "=== SSH PROCESSES ==="
$sshProcesses = Get-Process | Where-Object { $_.Name -match "ssh|plink|putty" }
if ($sshProcesses) {
    foreach ($proc in $sshProcesses) {
        $trace += "SSH Process: $($proc.Name) (PID $($proc.Id))"
        Write-Host "   SSH process found: $($proc.Name)" -ForegroundColor Red
    }
} else {
    $trace += "No SSH processes running"
    Write-Host "   No SSH processes" -ForegroundColor Green
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 7: Loaded modules
Write-Host "[7/8] Checking loaded modules..." -ForegroundColor Yellow
$trace += ""
$trace += "=== LOADED MODULES ==="
$modules = Get-Module | Select-Object Name, Version
if ($modules) {
    foreach ($mod in $modules) {
        $trace += "Module: $($mod.Name) v$($mod.Version)"
    }
    Write-Host "   $($modules.Count) modules loaded" -ForegroundColor White
} else {
    $trace += "No modules loaded"
    Write-Host "   No modules loaded" -ForegroundColor Green
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Check 8: Simulated profile load
Write-Host "[8/8] Simulating profile load..." -ForegroundColor Yellow
$trace += ""
$trace += "=== PROFILE LOAD SIMULATION ==="
Write-Host "   This will attempt to load the profile and see what happens..." -ForegroundColor White
Write-Host "   (If you see a password prompt here, we found the cause!)" -ForegroundColor Yellow
Write-Host ""

# Try to load the workspace profile in a controlled way
if (Test-Path $workspaceProfile) {
    Write-Host "   Loading workspace profile..." -ForegroundColor White
    $trace += "Attempting to load: $workspaceProfile"
    
    try {
        # Parse the profile content without executing it
        $content = Get-Content $workspaceProfile -Raw
        $ast = [System.Management.Automation.Language.Parser]::ParseInput($content, [ref]$null, [ref]$null)
        
        $trace += "Profile parsed successfully"
        $trace += "AST Elements: $($ast.EndBlock.Statements.Count)"
        
        Write-Host "   ✓ Profile parsed without errors" -ForegroundColor Green
        Write-Host "   ✓ Profile contains $($ast.EndBlock.Statements.Count) statements" -ForegroundColor Green
        
        # Check for suspicious commands
        $suspiciousCommands = @()
        foreach ($statement in $ast.EndBlock.Statements) {
            $statementText = $statement.Extent.Text
            if ($statementText -match "ssh |scp |Get-Credential|Read-Host.*password") {
                $suspiciousCommands += $statementText
            }
        }
        
        if ($suspiciousCommands.Count -gt 0) {
            $trace += ""
            $trace += "⚠️  SUSPICIOUS COMMANDS FOUND IN PROFILE:"
            foreach ($cmd in $suspiciousCommands) {
                $trace += "  - $cmd"
            }
            Write-Host "   ⚠️  WARNING: Profile contains commands that might prompt!" -ForegroundColor Red
        } else {
            $trace += "No suspicious commands found in profile"
            Write-Host "   ✓ No suspicious commands in profile" -ForegroundColor Green
        }
        
    } catch {
        $trace += "Profile parsing error: $_"
        Write-Host "   ⚠️  Profile parsing error: $_" -ForegroundColor Red
    }
} else {
    $trace += "Workspace profile not found - cannot simulate"
    Write-Host "   ⚠️  Workspace profile not found" -ForegroundColor Yellow
}
Write-Host "      ✓ Complete" -ForegroundColor Green

# Save trace
Write-Host ""
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$traceFile = "profile_load_trace_$timestamp.txt"
$trace | Out-File $traceFile -Encoding UTF8

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  TRACE COMPLETE                  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📄 Trace saved to: $traceFile" -ForegroundColor Green
Write-Host ""

# Analysis
Write-Host "🔍 ANALYSIS:" -ForegroundColor Yellow
Write-Host ""

$issues = @()

if ($onedrive) {
    $issues += "OneDrive is running and workspace is in OneDrive folder"
}

if ($gitProcesses) {
    $issues += "Git processes are running in background"
}

if ($vscodeProcesses) {
    $issues += "VS Code is running (extensions may be active)"
}

if ($sshProcesses) {
    $issues += "SSH processes detected - may be causing prompts"
}

if ($issues.Count -eq 0) {
    Write-Host "   ✓ No obvious issues detected" -ForegroundColor Green
    Write-Host ""
    Write-Host "   The password prompt may be caused by:" -ForegroundColor White
    Write-Host "   • VS Code extension background activity" -ForegroundColor Gray
    Write-Host "   • Windows Credential Manager" -ForegroundColor Gray
    Write-Host "   • Git credential helper" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  POTENTIAL ISSUES FOUND:" -ForegroundColor Red
    Write-Host ""
    foreach ($issue in $issues) {
        Write-Host "   • $issue" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📋 RECOMMENDED ACTIONS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Run the diagnostic script:" -ForegroundColor White
Write-Host "   .\diagnose_password_prompts.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Then run the fix script:" -ForegroundColor White
Write-Host "   .\fix_password_prompts.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. If still having issues, review:" -ForegroundColor White
Write-Host "   • This trace: $traceFile" -ForegroundColor Gray
Write-Host "   • Diagnostic report (from step 1)" -ForegroundColor Gray
Write-Host ""
Write-Host "═════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
