#!/usr/bin/env python3
# SQLite Production Backup System
# Enterprise Scanner Database Backup

import os
import shutil
import gzip
import sqlite3
from datetime import datetime, timedelta
import logging

class SQLiteBackupSystem:
    def __init__(self):
        self.prod_db = "enterprise_scanner_production.db"
        self.backup_dir = "backups/database"
        self.retention_days = 30
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.backup_dir, 'backup.log')),
                logging.StreamHandler()
            ]
        )
    
    def create_backup(self):
        """Create compressed backup of production database"""
        try:
            if not os.path.exists(self.prod_db):
                logging.error(f"Production database not found: {self.prod_db}")
                return False
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"enterprise_scanner_prod_{timestamp}.db")
            compressed_file = f"{backup_file}.gz"
            
            logging.info(f"Creating backup: {compressed_file}")
            
            # Create database backup using SQLite backup API
            source_conn = sqlite3.connect(self.prod_db)
            backup_conn = sqlite3.connect(backup_file)
            
            # Use SQLite's online backup API
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            # Compress backup
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            os.remove(backup_file)
            
            # Verify backup
            if os.path.exists(compressed_file):
                backup_size = os.path.getsize(compressed_file)
                logging.info(f"Backup completed: {backup_size} bytes")
                
                # Cleanup old backups
                self.cleanup_old_backups()
                return True
            else:
                logging.error("Backup file was not created")
                return False
                
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('enterprise_scanner_prod_') and filename.endswith('.db.gz'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        removed_count += 1
                        logging.info(f"Removed old backup: {filename}")
            
            # Count remaining backups
            remaining = len([f for f in os.listdir(self.backup_dir) 
                           if f.startswith('enterprise_scanner_prod_') and f.endswith('.db.gz')])
            
            logging.info(f"Cleanup completed: {removed_count} removed, {remaining} retained")
            
        except Exception as e:
            logging.error(f"Backup cleanup failed: {e}")
    
    def verify_backup(self, backup_file):
        """Verify backup integrity"""
        try:
            # Extract and test compressed backup
            test_db = backup_file.replace('.gz', '_test')
            
            with gzip.open(backup_file, 'rb') as f_in:
                with open(test_db, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Test database integrity
            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            conn.close()
            os.remove(test_db)
            
            if result == 'ok':
                logging.info(f"Backup verified successfully: {backup_file}")
                return True
            else:
                logging.error(f"Backup verification failed: {result}")
                return False
                
        except Exception as e:
            logging.error(f"Backup verification error: {e}")
            return False

def main():
    backup_system = SQLiteBackupSystem()
    success = backup_system.create_backup()
    
    if success:
        print("SQLite backup completed successfully!")
        return 0
    else:
        print("SQLite backup failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
