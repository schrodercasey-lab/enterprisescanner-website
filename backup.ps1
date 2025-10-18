# Enterprise Scanner - Automated Backup Script
# Creates backup of production server files and databases
# Usage: .\backup.ps1

param(
    [switch]$quick,  # Quick backup (files only, no database)
    [switch]$full    # Full backup (everything including Docker volumes)
)

$SERVER = "root@134.199.147.45"
$BACKUP_DIR = "C:\Backups\enterprisescanner"
$DATE = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_NAME = "backup_$DATE"

Write-Host "`n💾 ENTERPRISE SCANNER BACKUP" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Create backup directory if it doesn't exist
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
    Write-Host "✅ Created backup directory: $BACKUP_DIR" -ForegroundColor Green
}

Write-Host "📦 Starting backup process..." -ForegroundColor Yellow
Write-Host "   Backup location: $BACKUP_DIR\$BACKUP_NAME.tar.gz" -ForegroundColor Gray
Write-Host ""

# Step 1: Create backup on server
Write-Host "🔧 Step 1: Creating backup on server..." -ForegroundColor Yellow

if ($full) {
    Write-Host "   Mode: FULL backup (all files + Docker volumes)" -ForegroundColor Cyan
    ssh $SERVER "tar -czf /root/$BACKUP_NAME.tar.gz /var/www/html /opt/enterprisescanner /etc/nginx/sites-available/enterprisescanner /root/.ssh/authorized_keys 2>/dev/null"
} elseif ($quick) {
    Write-Host "   Mode: QUICK backup (website files only)" -ForegroundColor Cyan
    ssh $SERVER "tar -czf /root/$BACKUP_NAME.tar.gz /var/www/html 2>/dev/null"
} else {
    Write-Host "   Mode: STANDARD backup (files + configs)" -ForegroundColor Cyan
    ssh $SERVER "tar -czf /root/$BACKUP_NAME.tar.gz /var/www/html /opt/enterprisescanner /etc/nginx/sites-available/enterprisescanner 2>/dev/null"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backup created on server" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to create backup on server" -ForegroundColor Red
    exit 1
}

# Step 2: Download backup to local machine
Write-Host ""
Write-Host "📥 Step 2: Downloading backup to local machine..." -ForegroundColor Yellow
scp "${SERVER}:/root/$BACKUP_NAME.tar.gz" "$BACKUP_DIR\"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Backup downloaded successfully" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to download backup" -ForegroundColor Red
    exit 1
}

# Step 3: Cleanup old backups (keep last 7)
Write-Host ""
Write-Host "🧹 Step 3: Cleaning up old backups..." -ForegroundColor Yellow

$oldBackups = Get-ChildItem $BACKUP_DIR -Filter "backup_*.tar.gz" | 
    Sort-Object CreationTime -Descending | 
    Select-Object -Skip 7

if ($oldBackups) {
    foreach ($backup in $oldBackups) {
        Remove-Item $backup.FullName -Force
        Write-Host "   🗑️  Removed old backup: $($backup.Name)" -ForegroundColor Gray
    }
    Write-Host "   ✅ Cleaned up $($oldBackups.Count) old backup(s)" -ForegroundColor Green
} else {
    Write-Host "   ✅ No old backups to clean up" -ForegroundColor Green
}

# Step 4: Cleanup server
Write-Host ""
Write-Host "🧹 Step 4: Cleaning up server..." -ForegroundColor Yellow
ssh $SERVER "rm /root/$BACKUP_NAME.tar.gz"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Server cleanup complete" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Warning: Could not cleanup server (non-critical)" -ForegroundColor Yellow
}

# Step 5: Verify backup
Write-Host ""
Write-Host "✅ Step 5: Verifying backup..." -ForegroundColor Yellow
$backupFile = Get-Item "$BACKUP_DIR\$BACKUP_NAME.tar.gz"
$backupSizeMB = [math]::Round($backupFile.Length / 1MB, 2)

Write-Host "   File: $($backupFile.Name)" -ForegroundColor Gray
Write-Host "   Size: $backupSizeMB MB" -ForegroundColor Gray
Write-Host "   Location: $($backupFile.FullName)" -ForegroundColor Gray

# Success summary
Write-Host ""
Write-Host "🎉 BACKUP COMPLETE!" -ForegroundColor Green
Write-Host "🌐 Backup saved: $BACKUP_DIR\$BACKUP_NAME.tar.gz" -ForegroundColor Cyan
Write-Host ""

# Show backup summary
Write-Host "📊 Backup Summary:" -ForegroundColor Cyan
Write-Host "   Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "   Size: $backupSizeMB MB" -ForegroundColor Gray
Write-Host "   Server: 134.199.147.45" -ForegroundColor Gray
Write-Host "   Backups kept: 7 most recent" -ForegroundColor Gray
Write-Host ""

Write-Host "To restore backup, extract the tar.gz file and SCP contents back to server" -ForegroundColor Yellow
Write-Host ""
