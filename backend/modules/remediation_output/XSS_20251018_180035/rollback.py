#!/usr/bin/env python3
"""Rollback script - restores from backup"""
import sys
import shutil
import glob

def rollback():
    # Find most recent backup
    backups = sorted(glob.glob("*.backup.*"), reverse=True)
    if not backups:
        print("❌ No backup found")
        sys.exit(1)
    
    latest_backup = backups[0]
    original_file = latest_backup.split('.backup.')[0]
    
    print(f"Rolling back from {latest_backup} to {original_file}")
    shutil.copy2(latest_backup, original_file)
    print("✅ Rollback complete")

if __name__ == "__main__":
    rollback()
