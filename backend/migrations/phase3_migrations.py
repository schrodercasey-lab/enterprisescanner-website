"""
Database Migrations for Phase 3
Schema versioning and migration management for Phase 3 database

Usage:
    python migrations/phase3_migrations.py up      # Apply all pending migrations
    python migrations/phase3_migrations.py status  # Show current schema version
    python migrations/phase3_migrations.py down 1  # Rollback 1 migration
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class"""
    version = 0
    description = ""
    
    def up(self, conn: sqlite3.Connection):
        """Apply migration - must be implemented by subclass"""
        raise NotImplementedError(f"Migration {self.version} must implement up()")
    
    def down(self, conn: sqlite3.Connection):
        """Rollback migration - must be implemented by subclass"""
        raise NotImplementedError(f"Migration {self.version} must implement down()")


class Migration001_InitialSchema(Migration):
    """Create initial Phase 3 schema"""
    version = 1
    description = "Create monitoring sessions and alerts tables"
    
    def up(self, conn):
        cursor = conn.cursor()
        
        # Monitoring sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_sessions (
                session_id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                monitoring_level TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                alerts_generated INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Create index on target and status
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_target 
            ON monitoring_sessions(target)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_status 
            ON monitoring_sessions(status)
        """)
        
        # Security alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                alert_id TEXT PRIMARY KEY,
                session_id TEXT,
                rule_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                metric TEXT NOT NULL,
                current_value REAL NOT NULL,
                threshold_value REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                acknowledged_by TEXT,
                acknowledged_at TEXT,
                resolved_at TEXT,
                resolution_notes TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES monitoring_sessions(session_id)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_session 
            ON security_alerts(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_severity 
            ON security_alerts(severity)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_status 
            ON security_alerts(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
            ON security_alerts(timestamp DESC)
        """)
        
        # Generated scripts log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_scripts (
                script_id TEXT PRIMARY KEY,
                vulnerability_type TEXT NOT NULL,
                language TEXT NOT NULL,
                target_system TEXT NOT NULL,
                cvss_score REAL,
                checksum TEXT NOT NULL UNIQUE,
                file_path TEXT,
                generated_at TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scripts_vuln_type 
            ON generated_scripts(vulnerability_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scripts_language 
            ON generated_scripts(language)
        """)
        
        # Generated configs log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_configs (
                config_id TEXT PRIMARY KEY,
                config_type TEXT NOT NULL,
                hardening_level TEXT NOT NULL,
                target_system TEXT NOT NULL,
                compliance_frameworks TEXT,
                checksum TEXT NOT NULL UNIQUE,
                file_path TEXT,
                generated_at TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_configs_type 
            ON generated_configs(config_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_configs_level 
            ON generated_configs(hardening_level)
        """)
        
        conn.commit()
        logger.info("✅ Migration 001: Initial schema created")
    
    def down(self, conn):
        cursor = conn.cursor()
        
        # Drop indexes first
        indexes = [
            'idx_sessions_target',
            'idx_sessions_status',
            'idx_alerts_session',
            'idx_alerts_severity',
            'idx_alerts_status',
            'idx_alerts_timestamp',
            'idx_scripts_vuln_type',
            'idx_scripts_language',
            'idx_configs_type',
            'idx_configs_level'
        ]
        
        for index in indexes:
            cursor.execute(f"DROP INDEX IF EXISTS {index}")
        
        # Drop tables
        cursor.execute("DROP TABLE IF EXISTS security_alerts")
        cursor.execute("DROP TABLE IF EXISTS monitoring_sessions")
        cursor.execute("DROP TABLE IF EXISTS generated_scripts")
        cursor.execute("DROP TABLE IF EXISTS generated_configs")
        
        conn.commit()
        logger.info("✅ Migration 001: Rolled back")


class Migration002_PerformanceMetrics(Migration):
    """Add performance metrics tracking"""
    version = 2
    description = "Add performance metrics and operation tracking tables"
    
    def up(self, conn):
        cursor = conn.cursor()
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                success BOOLEAN NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_perf_operation 
            ON performance_metrics(operation)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_perf_timestamp 
            ON performance_metrics(timestamp DESC)
        """)
        
        # Alert notification log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (alert_id) REFERENCES security_alerts(alert_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notif_alert 
            ON alert_notifications(alert_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notif_channel 
            ON alert_notifications(channel)
        """)
        
        conn.commit()
        logger.info("✅ Migration 002: Performance metrics tables created")
    
    def down(self, conn):
        cursor = conn.cursor()
        
        cursor.execute("DROP INDEX IF EXISTS idx_perf_operation")
        cursor.execute("DROP INDEX IF EXISTS idx_perf_timestamp")
        cursor.execute("DROP INDEX IF EXISTS idx_notif_alert")
        cursor.execute("DROP INDEX IF EXISTS idx_notif_channel")
        
        cursor.execute("DROP TABLE IF EXISTS alert_notifications")
        cursor.execute("DROP TABLE IF EXISTS performance_metrics")
        
        conn.commit()
        logger.info("✅ Migration 002: Rolled back")


class Migration003_AuditLog(Migration):
    """Add audit log for compliance"""
    version = 3
    description = "Add audit log table for compliance tracking"
    
    def up(self, conn):
        cursor = conn.cursor()
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_user 
            ON audit_log(user)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_action 
            ON audit_log(action)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
            ON audit_log(timestamp DESC)
        """)
        
        conn.commit()
        logger.info("✅ Migration 003: Audit log table created")
    
    def down(self, conn):
        cursor = conn.cursor()
        
        cursor.execute("DROP INDEX IF EXISTS idx_audit_user")
        cursor.execute("DROP INDEX IF EXISTS idx_audit_action")
        cursor.execute("DROP INDEX IF EXISTS idx_audit_timestamp")
        cursor.execute("DROP TABLE IF EXISTS audit_log")
        
        conn.commit()
        logger.info("✅ Migration 003: Rolled back")


class MigrationManager:
    """Manage database migrations"""
    
    def __init__(self, db_path: str = "phase3.db"):
        """
        Initialize migration manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.migrations: List[Migration] = [
            Migration001_InitialSchema(),
            Migration002_PerformanceMetrics(),
            Migration003_AuditLog(),
        ]
        
        # Ensure database directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    def init_migrations_table(self):
        """Create migrations tracking table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                applied_by TEXT,
                execution_time_ms REAL
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Migrations table initialized")
    
    def get_current_version(self) -> int:
        """
        Get current schema version
        
        Returns:
            Current version number (0 if no migrations applied)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT MAX(version) FROM schema_migrations")
            result = cursor.fetchone()
            version = result[0] if result[0] else 0
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            version = 0
        finally:
            conn.close()
        
        return version
    
    def get_pending_migrations(self) -> List[Migration]:
        """
        Get list of pending migrations
        
        Returns:
            List of pending Migration objects
        """
        current = self.get_current_version()
        return [m for m in self.migrations if m.version > current]
    
    def get_applied_migrations(self) -> List[dict]:
        """
        Get list of applied migrations
        
        Returns:
            List of dicts with migration info
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT version, description, applied_at, execution_time_ms
                FROM schema_migrations
                ORDER BY version
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'version': row[0],
                    'description': row[1],
                    'applied_at': row[2],
                    'execution_time_ms': row[3]
                })
            
            return results
            
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()
    
    def migrate_up(self, target_version: Optional[int] = None):
        """
        Apply migrations up to target version
        
        Args:
            target_version: Target version to migrate to (None for latest)
        """
        self.init_migrations_table()
        current = self.get_current_version()
        
        if target_version is None:
            target = max(m.version for m in self.migrations)
        else:
            target = target_version
        
        print(f"\n{'='*80}")
        print(f"PHASE 3 DATABASE MIGRATION")
        print(f"{'='*80}")
        print(f"Database:        {self.db_path}")
        print(f"Current Version: {current}")
        print(f"Target Version:  {target}")
        print(f"{'='*80}\n")
        
        if current >= target:
            print("✅ Database is already at target version")
            return
        
        migrations_to_apply = [
            m for m in sorted(self.migrations, key=lambda x: x.version)
            if current < m.version <= target
        ]
        
        if not migrations_to_apply:
            print("No migrations to apply")
            return
        
        print(f"Migrations to apply: {len(migrations_to_apply)}\n")
        
        for migration in migrations_to_apply:
            start_time = datetime.now()
            print(f"Applying migration {migration.version}: {migration.description}...")
            
            conn = sqlite3.connect(self.db_path)
            try:
                # Apply migration
                migration.up(conn)
                
                # Record migration
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO schema_migrations 
                    (version, description, applied_at, execution_time_ms)
                    VALUES (?, ?, ?, ?)
                """, (
                    migration.version,
                    migration.description,
                    datetime.utcnow().isoformat(),
                    execution_time
                ))
                conn.commit()
                
                print(f"✅ Migration {migration.version} applied successfully ({execution_time:.2f}ms)\n")
                
            except Exception as e:
                conn.rollback()
                print(f"❌ Migration {migration.version} failed: {e}\n")
                logger.error(f"Migration {migration.version} failed: {e}")
                raise
            finally:
                conn.close()
        
        new_version = self.get_current_version()
        print(f"{'='*80}")
        print(f"✅ Migrations complete!")
        print(f"Database version: {current} → {new_version}")
        print(f"{'='*80}\n")
    
    def migrate_down(self, steps: int = 1):
        """
        Rollback migrations
        
        Args:
            steps: Number of migrations to rollback
        """
        current = self.get_current_version()
        target = max(0, current - steps)
        
        print(f"\n{'='*80}")
        print(f"PHASE 3 DATABASE ROLLBACK")
        print(f"{'='*80}")
        print(f"Database:        {self.db_path}")
        print(f"Current Version: {current}")
        print(f"Target Version:  {target}")
        print(f"Steps to rollback: {steps}")
        print(f"{'='*80}\n")
        
        if current == 0:
            print("No migrations to rollback")
            return
        
        migrations_to_rollback = [
            m for m in sorted(self.migrations, key=lambda x: x.version, reverse=True)
            if target < m.version <= current
        ]
        
        if not migrations_to_rollback:
            print("No migrations to rollback")
            return
        
        print(f"⚠️  WARNING: About to rollback {len(migrations_to_rollback)} migration(s)")
        print(f"This will DESTROY DATA. Type 'yes' to confirm: ", end='')
        
        if input().strip().lower() != 'yes':
            print("Rollback cancelled")
            return
        
        print()
        
        for migration in migrations_to_rollback:
            print(f"Rolling back migration {migration.version}: {migration.description}...")
            
            conn = sqlite3.connect(self.db_path)
            try:
                # Rollback migration
                migration.down(conn)
                
                # Remove from migrations table
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,)
                )
                conn.commit()
                
                print(f"✅ Migration {migration.version} rolled back successfully\n")
                
            except Exception as e:
                conn.rollback()
                print(f"❌ Rollback {migration.version} failed: {e}\n")
                logger.error(f"Rollback {migration.version} failed: {e}")
                raise
            finally:
                conn.close()
        
        new_version = self.get_current_version()
        print(f"{'='*80}")
        print(f"✅ Rollback complete!")
        print(f"Database version: {current} → {new_version}")
        print(f"{'='*80}\n")
    
    def status(self):
        """Print migration status"""
        current = self.get_current_version()
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print(f"\n{'='*80}")
        print(f"PHASE 3 MIGRATION STATUS")
        print(f"{'='*80}")
        print(f"Database:        {self.db_path}")
        print(f"Current Version: {current}")
        print(f"Latest Version:  {max(m.version for m in self.migrations)}")
        print(f"{'='*80}\n")
        
        if applied:
            print(f"Applied Migrations ({len(applied)}):")
            for m in applied:
                exec_time = f" ({m['execution_time_ms']:.2f}ms)" if m['execution_time_ms'] else ""
                print(f"  ✅ {m['version']}: {m['description']}{exec_time}")
                print(f"     Applied: {m['applied_at']}")
        else:
            print("No migrations applied yet")
        
        print()
        
        if pending:
            print(f"Pending Migrations ({len(pending)}):")
            for m in pending:
                print(f"  ⏳ {m.version}: {m.description}")
        else:
            print("✅ Database is up to date")
        
        print(f"\n{'='*80}\n")


def main():
    """CLI entry point for migrations"""
    import argparse
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from modules.config import get_config
    
    # Get database path from config
    try:
        config = get_config()
        default_db = config.db_path
    except:
        default_db = "phase3.db"
    
    parser = argparse.ArgumentParser(
        description="Phase 3 Database Migration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command',
                       choices=['up', 'down', 'status', 'init'],
                       help='Migration command')
    parser.add_argument('--version', type=int,
                       help='Target version (for up command)')
    parser.add_argument('--steps', type=int, default=1,
                       help='Number of steps to rollback (for down command)')
    parser.add_argument('--db', default=default_db,
                       help=f'Database path (default: {default_db})')
    
    args = parser.parse_args()
    
    manager = MigrationManager(args.db)
    
    if args.command == 'init':
        manager.init_migrations_table()
        print("✅ Migrations table initialized")
    elif args.command == 'up':
        manager.migrate_up(args.version)
    elif args.command == 'down':
        manager.migrate_down(args.steps)
    elif args.command == 'status':
        manager.status()


if __name__ == "__main__":
    main()
