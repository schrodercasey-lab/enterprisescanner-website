-- Enterprise Scanner Database Schema
-- PostgreSQL 15
-- Created: October 16, 2025

-- ==============================================
-- USERS AND AUTHENTICATION
-- ==============================================

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

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization_id);

-- ==============================================
-- ORGANIZATIONS
-- ==============================================

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    max_scans_per_month INTEGER DEFAULT 10,
    billing_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_organizations_domain ON organizations(domain);

-- ==============================================
-- SECURITY SCANS
-- ==============================================

CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    user_id INTEGER REFERENCES users(id),
    target_url VARCHAR(500) NOT NULL,
    scan_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
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
    info_count INTEGER DEFAULT 0
);

CREATE INDEX idx_scans_organization ON scans(organization_id);
CREATE INDEX idx_scans_user ON scans(user_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_started_at ON scans(started_at);

-- ==============================================
-- VULNERABILITIES
-- ==============================================

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL,
    vuln_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    affected_url VARCHAR(500),
    cvss_score DECIMAL(3,1),
    cwe_id VARCHAR(20),
    remediation TEXT,
    proof_of_concept TEXT,
    false_positive BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vulnerabilities_scan ON vulnerabilities(scan_id);
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulnerabilities_type ON vulnerabilities(vuln_type);

-- ==============================================
-- REPORTS
-- ==============================================

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id),
    report_type VARCHAR(50) NOT NULL,
    format VARCHAR(20) DEFAULT 'pdf',
    file_path VARCHAR(500),
    file_size INTEGER,
    generated_by INTEGER REFERENCES users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_count INTEGER DEFAULT 0
);

CREATE INDEX idx_reports_scan ON reports(scan_id);
CREATE INDEX idx_reports_organization ON reports(organization_id);

-- ==============================================
-- API KEYS
-- ==============================================

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_name VARCHAR(100),
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- ==============================================
-- AUDIT LOGS
-- ==============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);

-- ==============================================
-- CHAT SESSIONS
-- ==============================================

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    context JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_session ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_timestamp ON chat_sessions(timestamp);

-- ==============================================
-- ANALYTICS METRICS
-- ==============================================

CREATE TABLE IF NOT EXISTS analytics_metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    metric_type VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(15,2),
    dimensions JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_organization ON analytics_metrics(organization_id);
CREATE INDEX idx_analytics_type ON analytics_metrics(metric_type);
CREATE INDEX idx_analytics_recorded_at ON analytics_metrics(recorded_at);

-- ==============================================
-- PARTNER DATA
-- ==============================================

CREATE TABLE IF NOT EXISTS partners (
    id SERIAL PRIMARY KEY,
    partner_name VARCHAR(255) NOT NULL,
    partner_type VARCHAR(50),
    contact_email VARCHAR(255),
    api_endpoint VARCHAR(500),
    api_key_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    integration_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partners_active ON partners(is_active);

-- ==============================================
-- CLIENT ONBOARDING
-- ==============================================

CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    user_id INTEGER REFERENCES users(id),
    step VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'in_progress',
    data JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_onboarding_organization ON onboarding_sessions(organization_id);
CREATE INDEX idx_onboarding_status ON onboarding_sessions(status);

-- ==============================================
-- PERFORMANCE MONITORING
-- ==============================================

CREATE TABLE IF NOT EXISTS performance_logs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_service ON performance_logs(service_name);
CREATE INDEX idx_performance_timestamp ON performance_logs(timestamp);

-- ==============================================
-- SYSTEM SETTINGS
-- ==============================================

CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- SEED DATA
-- ==============================================

-- Insert default organization
INSERT INTO organizations (name, domain, subscription_tier, max_scans_per_month)
VALUES ('Enterprise Scanner', 'enterprisescanner.com', 'enterprise', 1000)
ON CONFLICT DO NOTHING;

-- Insert admin user (password: Admin123! - should be changed)
INSERT INTO users (email, password_hash, full_name, role, organization_id, email_verified)
VALUES (
    'admin@enterprisescanner.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKbw.Jj1u.', -- bcrypt hash of 'Admin123!'
    'System Administrator',
    'admin',
    1,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description)
VALUES
    ('max_concurrent_scans', '5', 'Maximum number of concurrent security scans'),
    ('scan_timeout_seconds', '3600', 'Maximum time for a scan to complete'),
    ('rate_limit_per_ip', '100', 'API rate limit per IP per hour'),
    ('data_retention_days', '365', 'Number of days to retain scan data')
ON CONFLICT (setting_key) DO NOTHING;

-- ==============================================
-- FUNCTIONS AND PROCEDURES
-- ==============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_user_id INTEGER,
    p_action VARCHAR,
    p_resource_type VARCHAR,
    p_resource_id INTEGER,
    p_ip_address INET,
    p_details JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_logs (user_id, action, resource_type, resource_id, ip_address, details)
    VALUES (p_user_id, p_action, p_resource_type, p_resource_id, p_ip_address, p_details);
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- VIEWS
-- ==============================================

-- View for scan summary statistics
CREATE OR REPLACE VIEW scan_statistics AS
SELECT 
    s.id,
    s.target_url,
    s.scan_type,
    s.status,
    s.started_at,
    s.completed_at,
    s.vulnerabilities_found,
    o.name as organization_name,
    u.email as user_email
FROM scans s
JOIN organizations o ON s.organization_id = o.id
JOIN users u ON s.user_id = u.id;

-- View for vulnerability summary
CREATE OR REPLACE VIEW vulnerability_summary AS
SELECT 
    scan_id,
    COUNT(*) as total_vulnerabilities,
    SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
    SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
    SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
    SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low,
    AVG(cvss_score) as avg_cvss_score
FROM vulnerabilities
GROUP BY scan_id;

-- ==============================================
-- GRANTS (for future multi-user setup)
-- ==============================================

-- Grant necessary permissions to admin user
-- (In production, create separate users for each service)

-- ==============================================
-- COMPLETION MESSAGE
-- ==============================================

DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Tables: 13';
    RAISE NOTICE 'Indexes: 25+';
    RAISE NOTICE 'Functions: 2';
    RAISE NOTICE 'Views: 2';
    RAISE NOTICE 'Default admin user: admin@enterprisescanner.com';
    RAISE NOTICE 'Database is ready for use!';
END $$;
