# SQLite Development Database Setup
# Enterprise Scanner - Quick Development Database

"""
SQLite development database setup for immediate testing
This provides a working database without requiring PostgreSQL installation
"""

import os
import sqlite3
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteSetup:
    def __init__(self):
        self.db_path = 'enterprise_scanner_dev.db'
        self.schema_file = 'backend/database/schema.sql'
        
    def create_sqlite_database(self):
        """Create SQLite database with Enterprise Scanner schema"""
        try:
            # Convert PostgreSQL schema to SQLite compatible
            sqlite_schema = self.convert_postgresql_to_sqlite()
            
            # Create database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute schema
            cursor.executescript(sqlite_schema)
            conn.commit()
            
            logging.info(f"SQLite database created: {self.db_path}")
            
            # Seed with sample data
            self.seed_sample_data(conn)
            
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Failed to create SQLite database: {e}")
            return False
    
    def convert_postgresql_to_sqlite(self):
        """Convert PostgreSQL schema to SQLite compatible format"""
        sqlite_schema = """
        -- Enterprise Scanner SQLite Schema
        -- Development database for immediate testing
        
        -- Companies table
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            domain TEXT,
            industry TEXT,
            size TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Leads table
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            company_id INTEGER,
            title TEXT,
            status TEXT DEFAULT 'new',
            source TEXT,
            deal_value REAL DEFAULT 0,
            lead_score INTEGER DEFAULT 0,
            notes TEXT,
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_contact TIMESTAMP,
            next_follow_up TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );
        
        -- Security Assessments table
        CREATE TABLE IF NOT EXISTS security_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            assessment_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            vulnerability_count INTEGER DEFAULT 0,
            critical_issues INTEGER DEFAULT 0,
            risk_score REAL DEFAULT 0,
            report_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );
        
        -- Chat Sessions table
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            visitor_id TEXT,
            company_name TEXT,
            email TEXT,
            status TEXT DEFAULT 'active',
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        );
        
        -- Partners table
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            partner_tier TEXT DEFAULT 'bronze',
            commission_rate REAL DEFAULT 25.0,
            status TEXT DEFAULT 'pending',
            specializations TEXT,
            geographic_regions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP
        );
        
        -- Partner Deals table
        CREATE TABLE IF NOT EXISTS partner_deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            lead_id INTEGER,
            deal_value REAL,
            commission_amount REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES partners (id),
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        );
        
        -- API Keys table
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            partner_id INTEGER,
            permissions TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES partners (id)
        );
        
        -- Analytics Events table
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id TEXT,
            session_id TEXT,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Lead Activities table
        CREATE TABLE IF NOT EXISTS lead_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            activity_type TEXT NOT NULL,
            description TEXT,
            user_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company_id);
        CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score);
        CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
        CREATE INDEX IF NOT EXISTS idx_partners_email ON partners(email);
        CREATE INDEX IF NOT EXISTS idx_activities_lead ON lead_activities(lead_id);
        """
        
        return sqlite_schema
    
    def seed_sample_data(self, conn):
        """Seed database with sample Fortune 500 data"""
        cursor = conn.cursor()
        
        # Sample companies
        companies = [
            ('Microsoft Corporation', 'microsoft.com', 'Technology', 'Enterprise', 'Redmond, WA'),
            ('Apple Inc.', 'apple.com', 'Technology', 'Enterprise', 'Cupertino, CA'),
            ('Amazon.com Inc.', 'amazon.com', 'E-commerce', 'Enterprise', 'Seattle, WA'),
            ('Alphabet Inc.', 'google.com', 'Technology', 'Enterprise', 'Mountain View, CA'),
            ('Meta Platforms Inc.', 'meta.com', 'Technology', 'Enterprise', 'Menlo Park, CA')
        ]
        
        for company in companies:
            cursor.execute("""
                INSERT OR IGNORE INTO companies (name, domain, industry, size, location)
                VALUES (?, ?, ?, ?, ?)
            """, company)
        
        # Sample leads
        leads = [
            ('John', 'Smith', 'john.smith@microsoft.com', '+1 (425) 882-8080', 1, 'CISO', 'qualified', 'website', 850000, 92),
            ('Sarah', 'Johnson', 'sarah.johnson@apple.com', '+1 (408) 996-1010', 2, 'IT Director', 'demo_scheduled', 'referral', 650000, 88),
            ('Michael', 'Brown', 'michael.brown@amazon.com', '+1 (206) 266-1000', 3, 'Security Manager', 'contacted', 'partner', 420000, 75),
            ('Lisa', 'Davis', 'lisa.davis@google.com', '+1 (650) 253-0000', 4, 'CTO', 'proposal_sent', 'website', 1200000, 95),
            ('Robert', 'Wilson', 'robert.wilson@meta.com', '+1 (650) 543-4800', 5, 'VP Information Security', 'new', 'advertisement', 780000, 82)
        ]
        
        for lead in leads:
            cursor.execute("""
                INSERT OR IGNORE INTO leads 
                (first_name, last_name, email, phone, company_id, title, status, source, deal_value, lead_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, lead)
        
        # Sample activities
        activities = [
            (1, 'lead_created', 'New lead created from website form submission'),
            (1, 'email_sent', 'Welcome email sent to lead'),
            (1, 'status_changed', 'Status changed to qualified'),
            (2, 'lead_created', 'New lead created from referral'),
            (2, 'meeting_scheduled', 'Demo meeting scheduled'),
            (3, 'lead_created', 'New lead created from partner referral'),
            (3, 'email_sent', 'Follow-up email sent')
        ]
        
        for activity in activities:
            cursor.execute("""
                INSERT INTO lead_activities (lead_id, activity_type, description)
                VALUES (?, ?, ?)
            """, activity)
        
        conn.commit()
        logging.info("Sample data seeded successfully")
    
    def create_development_config(self):
        """Create development configuration for SQLite"""
        config_content = f"""# Enterprise Scanner Development Configuration (SQLite)
# Generated on {datetime.now().isoformat()}

# Database Configuration (SQLite)
DATABASE_URL=sqlite:///{self.db_path}
DB_TYPE=sqlite

# Application Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev_secret_key_change_in_production

# Email Configuration (Development)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=info@enterprisescanner.com
EMAIL_PASSWORD=your_email_password
EMAIL_TESTING_MODE=True

# Domain Configuration
DOMAIN_URL=http://localhost:5000

# Partner Configuration
PARTNER_COMMISSION_BRONZE=25
PARTNER_COMMISSION_SILVER=30
PARTNER_COMMISSION_GOLD=35

# Security Configuration
SECURITY_HEADERS=True
SESSION_TIMEOUT=3600

# API Configuration
API_RATE_LIMIT=1000
API_RATE_LIMIT_WINDOW=3600

# Development Features
LOG_LEVEL=DEBUG
METRICS_ENABLED=True
HEALTH_CHECK_ENABLED=True
"""
        
        with open('.env.development', 'w') as f:
            f.write(config_content)
        
        logging.info("Development configuration updated for SQLite")

def main():
    """Main setup function"""
    print("🗄️  Enterprise Scanner SQLite Development Setup")
    print("=" * 60)
    print("This will create a SQLite database for immediate development and testing.")
    print("For production, use PostgreSQL setup later.")
    
    setup = SQLiteSetup()
    
    if setup.create_sqlite_database():
        setup.create_development_config()
        print(f"\n✅ SQLite database setup completed successfully!")
        print(f"Database file: {setup.db_path}")
        print("\nNext steps:")
        print("1. Database is ready with sample Fortune 500 data")
        print("2. Run: python backend/app.py")
        print("3. Open: http://localhost:5000/crm-dashboard.html")
        print("4. The CRM will now use live database instead of mock data")
        print("\n💡 For production PostgreSQL setup, install PostgreSQL first:")
        print("   - Download: https://www.postgresql.org/download/windows/")
        print("   - Then run: python deployment/scripts/setup_postgresql.py")
        return 0
    else:
        print("\n❌ SQLite setup failed.")
        return 1

if __name__ == "__main__":
    exit(main())