-- Enterprise Scanner Database Initialization Script
-- This script creates the necessary database schema for all services

-- ============================================
-- Create Extensions
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- Chat System Tables
-- ============================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    visitor_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    lead_score INTEGER DEFAULT 0,
    assigned_agent VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    sender_name VARCHAR(255),
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ============================================
-- Security Assessment Tables
-- ============================================
CREATE TABLE IF NOT EXISTS security_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id VARCHAR(255) UNIQUE NOT NULL,
    company_info JSONB NOT NULL,
    responses JSONB NOT NULL,
    risk_score INTEGER,
    risk_level VARCHAR(50),
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_progress'
);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    weight INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true
);

-- ============================================
-- Analytics Tables
-- ============================================
CREATE TABLE IF NOT EXISTS threat_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    source VARCHAR(255),
    target VARCHAR(255),
    description TEXT,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS security_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(100) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ============================================
-- Partner Portal Tables
-- ============================================
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    tier VARCHAR(50) DEFAULT 'bronze',
    commission_rate NUMERIC(5,2),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS partner_deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id UUID REFERENCES partners(id) ON DELETE CASCADE,
    deal_id VARCHAR(255) UNIQUE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    deal_value NUMERIC(12,2) NOT NULL,
    commission NUMERIC(12,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- ============================================
-- Client Onboarding Tables
-- ============================================
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    company_info JSONB NOT NULL,
    current_phase INTEGER DEFAULT 1,
    phases JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS onboarding_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    task_id VARCHAR(255) NOT NULL,
    phase INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_to VARCHAR(255),
    completed_at TIMESTAMP
);

-- ============================================
-- Performance Monitoring Tables
-- ============================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS sla_compliance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(100) NOT NULL,
    target_value NUMERIC NOT NULL,
    actual_value NUMERIC NOT NULL,
    compliant BOOLEAN NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Users & Authentication Tables
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    company VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    scopes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    active BOOLEAN DEFAULT true
);

-- ============================================
-- Audit Log Table
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Create Indexes for Performance
-- ============================================
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);

CREATE INDEX idx_assessments_assessment_id ON security_assessments(assessment_id);
CREATE INDEX idx_assessments_created_at ON security_assessments(created_at);
CREATE INDEX idx_assessments_status ON security_assessments(status);

CREATE INDEX idx_threat_events_timestamp ON threat_events(timestamp);
CREATE INDEX idx_threat_events_event_type ON threat_events(event_type);
CREATE INDEX idx_threat_events_severity ON threat_events(severity);

CREATE INDEX idx_partners_partner_id ON partners(partner_id);
CREATE INDEX idx_partners_email ON partners(email);
CREATE INDEX idx_partner_deals_partner_id ON partner_deals(partner_id);
CREATE INDEX idx_partner_deals_status ON partner_deals(status);

CREATE INDEX idx_onboarding_session_id ON onboarding_sessions(session_id);
CREATE INDEX idx_onboarding_status ON onboarding_sessions(status);
CREATE INDEX idx_onboarding_tasks_session_id ON onboarding_tasks(session_id);

CREATE INDEX idx_system_metrics_service ON system_metrics(service_name);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_sla_service ON sla_compliance(service_name);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ============================================
-- Create Views for Reporting
-- ============================================
CREATE OR REPLACE VIEW active_chat_sessions AS
SELECT 
    cs.*,
    COUNT(cm.id) as message_count
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.id = cm.session_id
WHERE cs.status = 'active'
GROUP BY cs.id;

CREATE OR REPLACE VIEW partner_performance AS
SELECT 
    p.partner_id,
    p.company_name,
    p.tier,
    COUNT(pd.id) as total_deals,
    SUM(pd.deal_value) as total_revenue,
    SUM(pd.commission) as total_commission,
    AVG(pd.deal_value) as avg_deal_size
FROM partners p
LEFT JOIN partner_deals pd ON p.id = pd.partner_id
WHERE p.status = 'active'
GROUP BY p.id, p.partner_id, p.company_name, p.tier;

-- ============================================
-- Grant Permissions
-- ============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT USAGE ON SCHEMA public TO admin;
