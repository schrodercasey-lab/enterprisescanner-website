#!/usr/bin/env python3
# Security Configuration Backup System
# Automated backup of security configurations and certificates

import os
import shutil
import tarfile
import gzip
from datetime import datetime
import logging

class SecurityBackup:
    def __init__(self):
        self.backup_dir = 'backups/security'
        self.security_files = [
            '.env.production',
            'deployment/ssl/',
            'deployment/security/',
            'deployment/configs/',
            'logs/security_events.log'
        ]
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Create compressed backup of security configurations"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"security_backup_{timestamp}.tar.gz"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in self.security_files:
                    if os.path.exists(file_path):
                        tar.add(file_path, arcname=os.path.basename(file_path))
                        logging.info(f"Added to backup: {file_path}")
            
            # Verify backup
            backup_size = os.path.getsize(backup_path)
            logging.info(f"Security backup created: {backup_path} ({backup_size} bytes)")
            
            # Cleanup old backups (keep last 30 days)
            self.cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logging.error(f"Security backup failed: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Remove backups older than 30 days"""
        try:
            import glob
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=30)
            backup_pattern = os.path.join(self.backup_dir, 'security_backup_*.tar.gz')
            
            for backup_file in glob.glob(backup_pattern):
                file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
                if file_time < cutoff_date:
                    os.remove(backup_file)
                    logging.info(f"Removed old backup: {backup_file}")
                    
        except Exception as e:
            logging.error(f"Backup cleanup failed: {e}")

def main():
    backup_system = SecurityBackup()
    backup_path = backup_system.create_backup()
    
    if backup_path:
        print(f"Security backup completed: {backup_path}")
        return 0
    else:
        print("❌ Security backup failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
