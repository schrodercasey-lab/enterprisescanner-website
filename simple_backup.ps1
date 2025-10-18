# Simple Backup Script
param([switch]$quick)

$SERVER = "root@134.199.147.45"
$BACKUP_DIR = "C:\Backups\enterprisescanner"
$DATE = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "Backup Script" -ForegroundColor Cyan

if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
}

Write-Host "Creating backup on server..." -ForegroundColor Yellow
ssh $SERVER "tar -czf /root/backup_$DATE.tar.gz /var/www/html 2>/dev/null"

Write-Host "Downloading backup..." -ForegroundColor Yellow
scp "${SERVER}:/root/backup_$DATE.tar.gz" "$BACKUP_DIR\"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup complete!" -ForegroundColor Green
    Write-Host "Location: $BACKUP_DIR\backup_$DATE.tar.gz" -ForegroundColor Cyan
    
    # Cleanup server
    ssh $SERVER "rm /root/backup_$DATE.tar.gz"
    
    # Keep only 7 backups
    Get-ChildItem $BACKUP_DIR -Filter "backup_*.tar.gz" | 
        Sort-Object CreationTime -Descending | 
        Select-Object -Skip 7 | 
        Remove-Item -Force
}
