#!/bin/bash

# Enterprise Scanner Database Integration Script
# Option C: Complete Database Setup and Service Integration
# Date: October 16, 2025

set -e  # Exit on error

echo "=========================================="
echo "  DATABASE INTEGRATION - OPTION C        "
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Test PostgreSQL connectivity"
echo "  2. Apply database schema"
echo "  3. Verify tables created"
echo "  4. Test database from Python"
echo "  5. Create backup script"
echo ""
read -p "Press Enter to continue or Ctrl+C to abort..."

# ==============================================
# TASK 1: TEST POSTGRESQL CONNECTIVITY
# ==============================================

echo ""
echo "=== Task 1: Testing PostgreSQL Connectivity ==="
echo ""

# Check if PostgreSQL container is running
if docker ps | grep -q enterprisescanner_postgres; then
    echo "✓ PostgreSQL container is running"
else
    echo "✗ PostgreSQL container not running"
    echo "Starting PostgreSQL container..."
    cd /opt/enterprisescanner/docker
    docker-compose -f docker-compose.prod.yml up -d postgres
    sleep 5
fi

# Test connection
echo "Testing database connection..."
docker exec enterprisescanner_postgres psql -U admin -d enterprisescanner -c "SELECT version();" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Database connection successful"
    docker exec enterprisescanner_postgres psql -U admin -d enterprisescanner -c "SELECT version();"
else
    echo "✗ Database connection failed"
    exit 1
fi

# ==============================================
# TASK 2: APPLY DATABASE SCHEMA
# ==============================================

echo ""
echo "=== Task 2: Applying Database Schema ==="
echo ""

# Create schema file on server
cat > /tmp/database_schema.sql << 'SCHEMA_EOF'
-- Enterprise Scanner Database Schema
-- PostgreSQL 15

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    organization_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    max_scans_per_month INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    user_id INTEGER REFERENCES users(id),
    target_url VARCHAR(500) NOT NULL,
    scan_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    vulnerabilities_found INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL,
    vuln_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    metric_type VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(15,2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS performance_logs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    response_time_ms INTEGER,
    status_code INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_scans_organization ON scans(organization_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan ON vulnerabilities(scan_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session ON chat_sessions(session_id);

-- Insert seed data
INSERT INTO organizations (name, domain, subscription_tier, max_scans_per_month)
VALUES ('Enterprise Scanner', 'enterprisescanner.com', 'enterprise', 1000)
ON CONFLICT DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role, organization_id, email_verified)
VALUES (
    'admin@enterprisescanner.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKbw.Jj1u.',
    'System Administrator',
    'admin',
    1,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

SELECT 'Database schema applied successfully!' as status;
SCHEMA_EOF

# Apply schema
echo "Applying database schema..."
docker exec -i enterprisescanner_postgres psql -U admin -d enterprisescanner < /tmp/database_schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Database schema applied successfully"
else
    echo "✗ Failed to apply database schema"
    exit 1
fi

# ==============================================
# TASK 3: VERIFY TABLES CREATED
# ==============================================

echo ""
echo "=== Task 3: Verifying Tables Created ==="
echo ""

# List all tables
echo "Tables in database:"
docker exec enterprisescanner_postgres psql -U admin -d enterprisescanner -c "\dt"

# Count tables
TABLE_COUNT=$(docker exec enterprisescanner_postgres psql -U admin -d enterprisescanner -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

echo ""
echo "✓ Total tables created: $TABLE_COUNT"

# ==============================================
# TASK 4: TEST DATABASE FROM PYTHON
# ==============================================

echo ""
echo "=== Task 4: Testing Database from Python ==="
echo ""

# Create Python test script
cat > /tmp/test_db_connection.py << 'PYTHON_EOF'
import psycopg2
from psycopg2 import pool
import sys

try:
    # Create connection pool
    print("Creating connection pool...")
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 5,
        host='localhost',
        port=5432,
        database='enterprisescanner',
        user='admin',
        password='SecurePass2024!'
    )
    
    # Get connection
    print("Getting connection from pool...")
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    
    # Test query
    print("Executing test query...")
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    print(f"✓ Users in database: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM organizations;")
    org_count = cursor.fetchone()[0]
    print(f"✓ Organizations in database: {org_count}")
    
    # Test insert
    print("Testing INSERT operation...")
    cursor.execute("""
        INSERT INTO audit_logs (action, resource_type, details)
        VALUES ('test_connection', 'database', 'Database integration test')
        RETURNING id;
    """)
    log_id = cursor.fetchone()[0]
    conn.commit()
    print(f"✓ Test audit log created with ID: {log_id}")
    
    # Cleanup
    cursor.close()
    connection_pool.putconn(conn)
    connection_pool.closeall()
    
    print("\n✓ All database tests passed!")
    print("✓ Python can successfully connect to PostgreSQL")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Database test failed: {str(e)}")
    sys.exit(1)
PYTHON_EOF

# Run Python test
cd /opt/enterprisescanner/backend
source venv/bin/activate
python /tmp/test_db_connection.py

if [ $? -eq 0 ]; then
    echo "✓ Python database integration working"
else
    echo "✗ Python database test failed"
    exit 1
fi

# ==============================================
# TASK 5: CREATE BACKUP SCRIPT
# ==============================================

echo ""
echo "=== Task 5: Creating Database Backup Script ==="
echo ""

# Create backup directory
mkdir -p /var/backups/postgres

# Create backup script
cat > /root/backup_database.sh << 'BACKUP_EOF'
#!/bin/bash

# Database backup script
BACKUP_DIR="/var/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/enterprisescanner_$DATE.sql"
RETENTION_DAYS=7

# Create backup
echo "Creating database backup..."
docker exec enterprisescanner_postgres pg_dump -U admin enterprisescanner > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "✓ Backup created: ${BACKUP_FILE}.gz"
    
    # Delete old backups
    find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "✓ Old backups cleaned up (retention: $RETENTION_DAYS days)"
else
    echo "✗ Backup failed"
    exit 1
fi
BACKUP_EOF

chmod +x /root/backup_database.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null | grep -v backup_database.sh; echo "0 2 * * * /root/backup_database.sh >> /var/log/db_backup.log 2>&1") | crontab -

echo "✓ Backup script created: /root/backup_database.sh"
echo "✓ Daily backup scheduled (2:00 AM)"

# Create initial backup
/root/backup_database.sh

# ==============================================
# SUMMARY
# ==============================================

echo ""
echo "=========================================="
echo "  DATABASE INTEGRATION COMPLETE!         "
echo "=========================================="
echo ""
echo "✓ PostgreSQL: Connected and operational"
echo "✓ Database Schema: Applied successfully"
echo "✓ Tables Created: $TABLE_COUNT tables"
echo "✓ Python Integration: Working"
echo "✓ Backup System: Configured (daily at 2 AM)"
echo ""
echo "=== Database Information ==="
echo "Host: localhost"
echo "Port: 5432"
echo "Database: enterprisescanner"
echo "User: admin"
echo "Tables: users, organizations, scans, vulnerabilities,"
echo "        chat_sessions, analytics_metrics, audit_logs,"
echo "        performance_logs"
echo ""
echo "=== Admin Credentials ==="
echo "Email: admin@enterprisescanner.com"
echo "Password: Admin123! (please change immediately)"
echo ""
echo "=== Next Steps ==="
echo "1. Update backend services to use database"
echo "2. Test data persistence"
echo "3. Monitor database performance"
echo ""
echo "Database integration completed successfully!"
echo "=========================================="
