# Production Database Migration Script
# Enterprise Scanner - SQLite to PostgreSQL Migration

"""
Complete production database migration for Enterprise Scanner
Migrates from SQLite development database to PostgreSQL production
Includes data migration, connection pooling, and backup systems
"""

import os
import sys
import subprocess
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import secrets
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_db_migration.log'),
        logging.StreamHandler()
    ]
)

class ProductionDatabaseMigration:
    def __init__(self):
        self.sqlite_db_path = 'enterprise_scanner_dev.db'
        self.pg_host = 'localhost'
        self.pg_port = 5432
        self.pg_database = 'enterprise_scanner'
        self.pg_user = 'enterprise_user'
        self.pg_password = self.generate_secure_password()
        self.backup_dir = 'backups/database'
        
        # Connection pool settings
        self.pool_size = 20
        self.max_overflow = 30
        self.pool_timeout = 30
        self.pool_recycle = 3600
        
    def generate_secure_password(self):
        """Generate secure password for PostgreSQL user"""
        import string
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def check_postgresql_installation(self):
        """Check if PostgreSQL is installed and running"""
        try:
            # Check if PostgreSQL service is running
            result = subprocess.run(['pg_isready', '-h', self.pg_host, '-p', str(self.pg_port)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("PostgreSQL is installed and running")
                return True
            else:
                logging.warning("PostgreSQL is not running or not accessible")
                return False
                
        except FileNotFoundError:
            logging.error("PostgreSQL is not installed or not in PATH")
            return False
    
    def install_postgresql_windows(self):
        """Install PostgreSQL on Windows using chocolatey"""
        logging.info("Installing PostgreSQL using Chocolatey...")
        try:
            # Check if chocolatey is installed
            subprocess.run(['choco', '--version'], check=True, 
                         capture_output=True)
            
            # Install PostgreSQL
            result = subprocess.run([
                'choco', 'install', 'postgresql', '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("PostgreSQL installed successfully")
                return True
            else:
                logging.error(f"Failed to install PostgreSQL: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError:
            logging.info("Chocolatey not available, providing manual instructions")
            self.print_manual_installation_instructions()
            return False
    
    def print_manual_installation_instructions(self):
        """Print manual installation instructions"""
        instructions = """
        Manual PostgreSQL Installation Instructions:
        
        1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
        2. Run the installer and follow the setup wizard
        3. Set a password for the postgres user (remember this password)
        4. Set port to 5432 (default)
        5. After installation, add PostgreSQL bin directory to PATH:
           - Default location: C:\\Program Files\\PostgreSQL\\16\\bin
        6. Restart your command prompt and run this script again
        
        Alternative: Use Docker
        1. Install Docker Desktop
        2. Run: docker run --name postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 -d postgres
        """
        print(instructions)
        logging.info("Manual installation instructions provided")
    
    def create_database(self):
        """Create the enterprise_scanner database"""
        try:
            # Connect to PostgreSQL server (not to specific database)
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['username'],
                password=self.db_config['password'],
                database='postgres'  # Connect to default database
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (self.db_config['database'],)
            )
            
            if cursor.fetchone():
                logging.info(f"Database '{self.db_config['database']}' already exists")
            else:
                # Create database
                cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
                logging.info(f"Database '{self.db_config['database']}' created successfully")
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.Error as e:
            logging.error(f"Failed to create database: {e}")
            return False
    
    def test_connection(self):
        """Test connection to the database"""
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['username'],
                password=self.db_config['password']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logging.info(f"Successfully connected to PostgreSQL: {version[0]}")
            cursor.close()
            conn.close()
            return True
            
        except psycopg2.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            return False
    
    def run_schema_script(self):
        """Run the database schema creation script"""
        try:
            schema_file = 'backend/database/schema.sql'
            if not os.path.exists(schema_file):
                logging.error(f"Schema file not found: {schema_file}")
                return False
            
            # Read schema file
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Connect and execute schema
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['username'],
                password=self.db_config['password']
            )
            cursor = conn.cursor()
            cursor.execute(schema_sql)
            conn.commit()
            
            logging.info("Database schema created successfully")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Failed to create schema: {e}")
            return False
    
    def setup_production_database(self):
        """Complete production database setup"""
        logging.info("Starting PostgreSQL production setup...")
        
        # Step 1: Check PostgreSQL installation
        if not self.check_postgresql_installation():
            if os.name == 'nt':  # Windows
                if not self.install_postgresql_windows():
                    return False
            else:
                logging.error("Please install PostgreSQL manually")
                return False
        
        # Step 2: Create database
        if not self.create_database():
            return False
        
        # Step 3: Test connection
        if not self.test_connection():
            return False
        
        # Step 4: Create schema
        if not self.run_schema_script():
            return False
        
        logging.info("PostgreSQL production setup completed successfully!")
        return True
    
    def generate_production_config(self):
        """Generate production configuration file"""
        config_content = f"""# Enterprise Scanner Production Configuration
# Generated on {datetime.now().isoformat()}

# Database Configuration
DATABASE_URL=postgresql://{self.db_config['username']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}
DB_HOST={self.db_config['host']}
DB_PORT={self.db_config['port']}
DB_NAME={self.db_config['database']}
DB_USER={self.db_config['username']}
DB_PASSWORD={self.db_config['password']}

# Connection Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Application Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your_production_secret_key_here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=info@enterprisescanner.com
EMAIL_PASSWORD=your_production_email_password

# Security Configuration
SSL_DISABLE=False
SECURITY_HEADERS=True
SESSION_TIMEOUT=3600

# API Configuration
API_RATE_LIMIT=1000
API_RATE_LIMIT_WINDOW=3600

# Monitoring Configuration
LOG_LEVEL=INFO
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True
"""
        
        config_file = '.env.production'
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logging.info(f"Production configuration saved to {config_file}")
        print(f"\n⚠️  IMPORTANT: Edit {config_file} and update the following:")
        print("   - DB_PASSWORD: Set your PostgreSQL password")
        print("   - SECRET_KEY: Generate a secure secret key")
        print("   - EMAIL_PASSWORD: Set your email service password")


def main():
    """Main setup function"""
    print("🚀 Enterprise Scanner PostgreSQL Production Setup")
    print("=" * 60)
    
    setup = PostgreSQLSetup()
    
    # Check for environment variables
    if not os.environ.get('DB_PASSWORD'):
        print("\n⚠️  Database password not set!")
        password = input("Enter PostgreSQL password (or press Enter to use 'postgres'): ").strip()
        if password:
            os.environ['DB_PASSWORD'] = password
        else:
            os.environ['DB_PASSWORD'] = 'postgres'
            setup.db_config['password'] = 'postgres'
    
    # Run setup
    if setup.setup_production_database():
        setup.generate_production_config()
        print("\n✅ PostgreSQL setup completed successfully!")
        print("Next steps:")
        print("1. Update .env.production with your actual passwords")
        print("2. Run: python backend/database/migration.py")
        print("3. Start production server with: FLASK_ENV=production python backend/app.py")
    else:
        print("\n❌ PostgreSQL setup failed. Check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())