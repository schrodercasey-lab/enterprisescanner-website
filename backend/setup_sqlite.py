"""
SQLite Database Setup for Enterprise Scanner
Quick start development database with all tables
"""

import sqlite3
import os
from datetime import datetime
import hashlib

# Get the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, 'enterprise_scanner.db')

def create_database():
    """Create SQLite database with all tables"""
    
    print("🗄️  Creating Enterprise Scanner Database...")
    print(f"📁 Database location: {DB_PATH}")
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        print("⚠️  Existing database found - backing up...")
        backup_path = DB_PATH + f".backup.{int(datetime.now().timestamp())}"
        os.rename(DB_PATH, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📊 Creating tables...")
    
    # 1. Organizations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            domain TEXT,
            industry TEXT,
            employee_count INTEGER,
            annual_revenue INTEGER,
            fortune_rank INTEGER,
            headquarters_location TEXT,
            is_fortune_500 BOOLEAN DEFAULT 0,
            subscription_tier TEXT DEFAULT 'free',
            max_scans_per_month INTEGER DEFAULT 10,
            billing_email TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ organizations")
    
    # 2. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            organization_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    print("✅ users")
    
    # 3. Companies Table (for lead tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            domain TEXT UNIQUE,
            industry TEXT,
            employee_count INTEGER,
            annual_revenue INTEGER,
            fortune_rank INTEGER,
            headquarters_location TEXT,
            is_fortune_500 BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ companies")
    
    # 4. Leads Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            job_title TEXT,
            department TEXT,
            seniority_level TEXT,
            lead_source TEXT,
            lead_status TEXT DEFAULT 'new',
            lead_score INTEGER DEFAULT 0,
            estimated_deal_value INTEGER,
            probability_to_close REAL,
            assigned_to INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_contacted_at TIMESTAMP,
            next_follow_up_at TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)
    print("✅ leads")
    
    # 5. Security Scans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER,
            user_id INTEGER,
            lead_id INTEGER,
            target_url TEXT NOT NULL,
            scan_type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            duration_seconds INTEGER,
            total_checks INTEGER DEFAULT 0,
            vulnerabilities_found INTEGER DEFAULT 0,
            critical_count INTEGER DEFAULT 0,
            high_count INTEGER DEFAULT 0,
            medium_count INTEGER DEFAULT 0,
            low_count INTEGER DEFAULT 0,
            info_count INTEGER DEFAULT 0,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    print("✅ scans")
    
    # 6. Vulnerabilities Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            severity TEXT NOT NULL,
            vuln_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            affected_url TEXT,
            cvss_score REAL,
            cwe_id TEXT,
            remediation TEXT,
            proof_of_concept TEXT,
            false_positive BOOLEAN DEFAULT 0,
            verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
        )
    """)
    print("✅ vulnerabilities")
    
    # 7. Security Assessments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            company_id INTEGER,
            scan_id INTEGER,
            assessment_type TEXT DEFAULT 'comprehensive',
            current_security_score INTEGER,
            risk_level TEXT,
            vulnerabilities_found INTEGER,
            compliance_score INTEGER,
            recommended_budget INTEGER,
            roi_projection INTEGER,
            assessment_data TEXT,
            pdf_report_path TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id),
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    """)
    print("✅ security_assessments")
    
    # 8. Chat Sessions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            lead_id INTEGER,
            company_id INTEGER,
            user_id INTEGER,
            message TEXT NOT NULL,
            response TEXT,
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP,
            escalated_to_human BOOLEAN DEFAULT 0,
            escalation_reason TEXT,
            assigned_consultant TEXT,
            session_rating INTEGER,
            fortune_500_detected BOOLEAN DEFAULT 0,
            high_value_opportunity BOOLEAN DEFAULT 0,
            context TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id),
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("✅ chat_sessions")
    
    # 9. Partners Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_title TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            annual_revenue_range TEXT,
            security_experience_years TEXT,
            partner_tier TEXT,
            partner_type TEXT,
            commission_rate REAL,
            status TEXT DEFAULT 'pending',
            client_types TEXT,
            geographic_regions TEXT,
            specializations TEXT,
            certification_level TEXT,
            onboarding_completed BOOLEAN DEFAULT 0,
            agreement_signed_at TIMESTAMP,
            api_endpoint TEXT,
            api_key_hash TEXT,
            is_active BOOLEAN DEFAULT 1,
            integration_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ partners")
    
    # 10. API Keys Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            key_hash TEXT UNIQUE NOT NULL,
            key_name TEXT,
            key_prefix TEXT,
            created_by INTEGER,
            permissions TEXT,
            rate_limit_per_hour INTEGER DEFAULT 1000,
            usage_count INTEGER DEFAULT 0,
            last_used_at TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)
    print("✅ api_keys")
    
    # 11. Analytics Events Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            lead_id INTEGER,
            company_id INTEGER,
            session_id TEXT,
            user_agent TEXT,
            ip_address TEXT,
            referrer_url TEXT,
            page_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    print("✅ analytics_events")
    
    # 12. Reports Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            organization_id INTEGER,
            report_type TEXT NOT NULL,
            format TEXT DEFAULT 'pdf',
            file_path TEXT,
            file_size INTEGER,
            generated_by INTEGER,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            download_count INTEGER DEFAULT 0,
            FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (generated_by) REFERENCES users(id)
        )
    """)
    print("✅ reports")
    
    # 13. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("✅ audit_logs")
    
    # Create indexes for performance
    print("\n🔍 Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(lead_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_lead ON chat_sessions(lead_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type)")
    print("✅ 8 indexes created")
    
    # Insert seed data
    print("\n🌱 Inserting seed data...")
    
    # Default organization
    cursor.execute("""
        INSERT INTO organizations (name, domain, subscription_tier, max_scans_per_month, is_active)
        VALUES ('Enterprise Scanner', 'enterprisescanner.com', 'enterprise', 1000, 1)
    """)
    
    # Admin user (password: Admin123!)
    admin_password_hash = hashlib.sha256('Admin123!'.encode()).hexdigest()
    cursor.execute("""
        INSERT INTO users (email, password_hash, full_name, role, organization_id, email_verified)
        VALUES ('admin@enterprisescanner.com', ?, 'System Administrator', 'admin', 1, 1)
    """, (admin_password_hash,))
    
    # Sample Fortune 500 companies
    fortune_500_companies = [
        ('Microsoft Corporation', 'microsoft.com', 'Technology', 181000, 198270000000, 3),
        ('Apple Inc.', 'apple.com', 'Technology', 164000, 394328000000, 2),
        ('JPMorgan Chase', 'jpmorgan.com', 'Financial Services', 293723, 141422000000, 7),
        ('Amazon.com Inc.', 'amazon.com', 'Technology', 1608000, 574785000000, 1),
        ('Alphabet Inc.', 'google.com', 'Technology', 190711, 307394000000, 4),
    ]
    
    for company_data in fortune_500_companies:
        cursor.execute("""
            INSERT INTO companies (name, domain, industry, employee_count, annual_revenue, fortune_rank, is_fortune_500)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, company_data)
    
    print("✅ Seed data inserted")
    
    # Commit changes
    conn.commit()
    print("\n💾 Database committed successfully")
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
    index_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM companies WHERE is_fortune_500=1")
    fortune_count = cursor.fetchone()[0]
    
    # Close connection
    conn.close()
    
    # Print summary
    print("\n" + "="*60)
    print("✅ DATABASE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"📊 Tables created: {table_count}")
    print(f"🔍 Indexes created: {index_count}")
    print(f"🏢 Fortune 500 companies: {fortune_count}")
    print(f"👤 Admin user: admin@enterprisescanner.com")
    print(f"🔑 Admin password: Admin123!")
    print(f"📁 Database file: {DB_PATH}")
    print("="*60)
    print("\n🚀 Next steps:")
    print("1. Run: python backend/app.py")
    print("2. Visit: http://localhost:5000")
    print("3. API endpoint: http://localhost:5000/api/leads")
    print("\n✅ Ready for development!")
    
    return DB_PATH

if __name__ == "__main__":
    try:
        db_path = create_database()
        print(f"\n✅ Success! Database ready at: {db_path}")
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
