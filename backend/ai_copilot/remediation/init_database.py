"""
Jupiter v3.0 - Module G.1: Database Initialization
CLI tool to initialize and verify remediation database

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

import sqlite3
import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    from config import get_config
    from exceptions import RemediationDatabaseError
except ImportError:
    # Fallback for standalone execution
    class RemediationDatabaseError(Exception):
        pass
    
    class MockConfig:
        database_path = "jupiter_remediation.db"
    
    def get_config():
        return MockConfig()


def read_schema_file(schema_path: str = None) -> str:
    """
    Read SQL schema from file
    
    Args:
        schema_path: Path to schema file (default: database_schema.sql)
        
    Returns:
        SQL schema as string
    """
    if schema_path is None:
        schema_path = Path(__file__).parent / "database_schema.sql"
    
    if not Path(schema_path).exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r') as f:
        return f.read()


def initialize_database(db_path: str, schema_path: str = None, force: bool = False) -> bool:
    """
    Initialize remediation database with schema
    
    Args:
        db_path: Path to database file
        schema_path: Path to schema SQL file
        force: If True, drop existing tables before initialization
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if database already exists
        db_exists = Path(db_path).exists()
        
        if db_exists and not force:
            print(f"⚠️  Database already exists: {db_path}")
            print(f"   Use --force to reinitialize")
            return False
        
        # Read schema
        print(f"📖 Reading schema...")
        schema_sql = read_schema_file(schema_path)
        
        # Connect to database
        print(f"🔌 Connecting to {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing tables if force mode
        if force and db_exists:
            print(f"🗑️  Dropping existing tables...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                if table != 'sqlite_sequence':
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"   Dropped {len(tables)} tables")
        
        # Execute schema
        print(f"🔨 Creating schema...")
        cursor.executescript(schema_sql)
        conn.commit()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database initialized successfully!")
        print(f"   Database: {db_path}")
        print(f"   Tables: {len(tables)}")
        for table in tables:
            print(f"      - {table}")
        
        # Close connection
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def verify_database(db_path: str) -> bool:
    """
    Verify database schema is correct
    
    Args:
        db_path: Path to database file
        
    Returns:
        True if schema is valid, False otherwise
    """
    try:
        print(f"🔍 Verifying database schema...")
        
        if not Path(db_path).exists():
            print(f"❌ Database not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Expected tables
        expected_tables = [
            'remediation_plans',
            'remediation_executions',
            'system_snapshots',
            'risk_assessments',
            'patches',
            'remediation_audit_log',
            'autonomous_decisions',
            'remediation_metrics',
            'deployment_stages',
            'schema_version'
        ]
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        actual_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = set(expected_tables) - set(actual_tables)
        extra_tables = set(actual_tables) - set(expected_tables) - {'sqlite_sequence'}
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        
        if extra_tables:
            print(f"⚠️  Extra tables: {', '.join(extra_tables)}")
        
        print(f"✅ All required tables present ({len(expected_tables)})")
        
        # Check views exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        views = [row[0] for row in cursor.fetchall()]
        
        expected_views = [
            'v_active_remediations',
            'v_remediation_stats_daily',
            'v_autonomy_distribution',
            'v_patch_success_rates'
        ]
        
        missing_views = set(expected_views) - set(views)
        if missing_views:
            print(f"⚠️  Missing views: {', '.join(missing_views)}")
        else:
            print(f"✅ All views present ({len(views)})")
        
        # Check triggers exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")
        triggers = [row[0] for row in cursor.fetchall()]
        
        expected_triggers = [
            'update_patch_stats',
            'update_patch_stats_on_failure',
            'expire_old_snapshots'
        ]
        
        missing_triggers = set(expected_triggers) - set(triggers)
        if missing_triggers:
            print(f"⚠️  Missing triggers: {', '.join(missing_triggers)}")
        else:
            print(f"✅ All triggers present ({len(triggers)})")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"✅ {len(indexes)} indexes defined")
        
        # Check schema version
        cursor.execute("SELECT version, applied_at FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            version, applied_at = row
            print(f"✅ Schema version: {version} (applied {applied_at})")
        else:
            print(f"⚠️  No schema version recorded")
        
        # Check foreign keys enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        if fk_enabled:
            print(f"✅ Foreign keys: ENABLED")
        else:
            print(f"❌ Foreign keys: DISABLED (run PRAGMA foreign_keys = ON)")
        
        # Check journal mode
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        print(f"✅ Journal mode: {journal_mode}")
        
        conn.close()
        
        print(f"\n✅ Database schema verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False


def show_stats(db_path: str) -> bool:
    """
    Show database statistics
    
    Args:
        db_path: Path to database file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📊 Database Statistics\n")
        
        if not Path(db_path).exists():
            print(f"❌ Database not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Row counts for each table
        tables = [
            'remediation_plans',
            'remediation_executions',
            'system_snapshots',
            'risk_assessments',
            'patches',
            'remediation_audit_log',
            'autonomous_decisions',
            'deployment_stages'
        ]
        
        print("Row Counts:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:30} {count:>8} rows")
        
        # Database file size
        db_size = Path(db_path).stat().st_size
        print(f"\nDatabase Size: {db_size:,} bytes ({db_size / 1024 / 1024:.2f} MB)")
        
        # Recent activity
        print(f"\nRecent Activity:")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM remediation_executions 
            WHERE created_at >= datetime('now', '-24 hours')
        """)
        recent_executions = cursor.fetchone()[0]
        print(f"  Executions (24h): {recent_executions}")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM remediation_audit_log 
            WHERE timestamp >= datetime('now', '-24 hours')
        """)
        recent_audit = cursor.fetchone()[0]
        print(f"  Audit entries (24h): {recent_audit}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Jupiter v3.0 - Remediation Database Initialization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database with default location
  python init_database.py --init
  
  # Initialize with custom path
  python init_database.py --init --database /path/to/db.sqlite
  
  # Force reinitialize (drops existing tables)
  python init_database.py --init --force
  
  # Verify database schema
  python init_database.py --verify
  
  # Show database statistics
  python init_database.py --stats
        """
    )
    
    parser.add_argument('--init', action='store_true',
                       help='Initialize database with schema')
    parser.add_argument('--verify', action='store_true',
                       help='Verify database schema')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    parser.add_argument('--database', type=str,
                       help='Database file path (default from config)')
    parser.add_argument('--schema', type=str,
                       help='Schema SQL file path (default: database_schema.sql)')
    parser.add_argument('--force', action='store_true',
                       help='Force reinitialize (drops existing tables)')
    
    args = parser.parse_args()
    
    # Get database path
    if args.database:
        db_path = args.database
    else:
        config = get_config()
        db_path = config.database_path
    
    # Execute requested operation
    if args.init:
        success = initialize_database(db_path, args.schema, args.force)
        sys.exit(0 if success else 1)
    
    elif args.verify:
        success = verify_database(db_path)
        sys.exit(0 if success else 1)
    
    elif args.stats:
        success = show_stats(db_path)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
