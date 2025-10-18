-- Enterprise Scanner Database Schema
-- PostgreSQL DDL script for production deployment

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) UNIQUE,
    industry VARCHAR(100),
    employee_count INTEGER,
    annual_revenue BIGINT,
    fortune_rank INTEGER,
    headquarters_location VARCHAR(255),
    is_fortune_500 BOOLEAN DEFAULT FALSE,
    company_size VARCHAR(50),
    website_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Companies indexes
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_fortune_500 ON companies(is_fortune_500);
CREATE INDEX idx_companies_created_at ON companies(created_at);

-- Leads table
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    job_title VARCHAR(150),
    department VARCHAR(100),
    seniority_level VARCHAR(50),
    lead_source VARCHAR(100),
    lead_status VARCHAR(50) DEFAULT 'new',
    lead_score INTEGER DEFAULT 0,
    estimated_deal_value BIGINT,
    probability_to_close DECIMAL(5,2),
    assigned_to UUID,
    priority VARCHAR(20) DEFAULT 'medium',
    timezone VARCHAR(50),
    preferred_contact_method VARCHAR(50),
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    next_follow_up_at TIMESTAMP WITH TIME ZONE,
    qualification_date TIMESTAMP WITH TIME ZONE
);

-- Leads indexes
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_company_id ON leads(company_id);
CREATE INDEX idx_leads_status ON leads(lead_status);
CREATE INDEX idx_leads_score ON leads(lead_score DESC);
CREATE INDEX idx_leads_follow_up ON leads(next_follow_up_at);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_leads_assigned_to ON leads(assigned_to);

-- Security assessments table
CREATE TABLE security_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) DEFAULT 'comprehensive',
    current_security_score INTEGER,
    risk_level VARCHAR(20),
    vulnerabilities_found INTEGER,
    compliance_score INTEGER,
    recommended_budget BIGINT,
    roi_projection BIGINT,
    implementation_timeline INTEGER,
    priority_areas TEXT[],
    assessment_data JSONB,
    recommendations JSONB,
    pdf_report_path VARCHAR(500),
    report_generated BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Security assessments indexes
CREATE INDEX idx_assessments_lead_id ON security_assessments(lead_id);
CREATE INDEX idx_assessments_company_id ON security_assessments(company_id);
CREATE INDEX idx_assessments_risk_level ON security_assessments(risk_level);
CREATE INDEX idx_assessments_score ON security_assessments(current_security_score);
CREATE INDEX idx_assessments_completed_at ON security_assessments(completed_at);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    visitor_ip INET,
    user_agent TEXT,
    session_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    message_count INTEGER DEFAULT 0,
    escalated_to_human BOOLEAN DEFAULT FALSE,
    escalation_reason VARCHAR(255),
    assigned_consultant VARCHAR(100),
    session_rating INTEGER CHECK (session_rating >= 1 AND session_rating <= 5),
    fortune_500_detected BOOLEAN DEFAULT FALSE,
    high_value_opportunity BOOLEAN DEFAULT FALSE,
    lead_captured BOOLEAN DEFAULT FALSE,
    contact_info_provided BOOLEAN DEFAULT FALSE,
    session_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions indexes
CREATE INDEX idx_chat_sessions_lead_id ON chat_sessions(lead_id);
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_escalated ON chat_sessions(escalated_to_human);
CREATE INDEX idx_chat_sessions_fortune_500 ON chat_sessions(fortune_500_detected);
CREATE INDEX idx_chat_sessions_start ON chat_sessions(session_start);

-- Partners table
CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id VARCHAR(50) UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(150) NOT NULL,
    contact_title VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    annual_revenue_range VARCHAR(50),
    security_experience_years VARCHAR(20),
    partner_tier VARCHAR(50),
    commission_rate DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'pending',
    client_types TEXT[],
    geographic_regions TEXT[],
    specializations TEXT[],
    certification_level VARCHAR(100),
    certifications TEXT[],
    experience_description TEXT,
    partnership_goals TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    training_completed BOOLEAN DEFAULT FALSE,
    agreement_signed_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    total_deal_value BIGINT DEFAULT 0,
    total_commission_earned BIGINT DEFAULT 0,
    deals_closed INTEGER DEFAULT 0,
    performance_rating DECIMAL(3,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Partners indexes
CREATE INDEX idx_partners_email ON partners(email);
CREATE INDEX idx_partners_tier ON partners(partner_tier);
CREATE INDEX idx_partners_status ON partners(status);
CREATE INDEX idx_partners_created_at ON partners(created_at);
CREATE INDEX idx_partners_application_id ON partners(application_id);

-- Partner deals table
CREATE TABLE partner_deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id UUID REFERENCES partners(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    deal_name VARCHAR(255),
    deal_value BIGINT NOT NULL,
    commission_rate DECIMAL(5,2),
    commission_amount BIGINT,
    deal_status VARCHAR(50),
    deal_stage VARCHAR(100),
    close_probability DECIMAL(5,2),
    expected_close_date DATE,
    actual_close_date DATE,
    deal_source VARCHAR(100),
    sales_cycle_days INTEGER,
    competitive_situation VARCHAR(255),
    decision_makers TEXT[],
    deal_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Partner deals indexes
CREATE INDEX idx_partner_deals_partner_id ON partner_deals(partner_id);
CREATE INDEX idx_partner_deals_status ON partner_deals(deal_status);
CREATE INDEX idx_partner_deals_value ON partner_deals(deal_value DESC);
CREATE INDEX idx_partner_deals_expected_close ON partner_deals(expected_close_date);
CREATE INDEX idx_partner_deals_created_at ON partner_deals(created_at);

-- API keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_name VARCHAR(100),
    key_prefix VARCHAR(20),
    created_by UUID,
    permissions TEXT[],
    rate_limit_per_hour INTEGER DEFAULT 1000,
    usage_count BIGINT DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    last_used_ip INET,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API keys indexes
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_api_keys_created_by ON api_keys(created_by);

-- Analytics events table
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50),
    event_data JSONB,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    session_id VARCHAR(100),
    user_agent TEXT,
    ip_address INET,
    referrer_url TEXT,
    page_url TEXT,
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    device_type VARCHAR(50),
    browser VARCHAR(100),
    operating_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analytics events indexes
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_events_lead_id ON analytics_events(lead_id);
CREATE INDEX idx_analytics_events_company_id ON analytics_events(company_id);
CREATE INDEX idx_analytics_events_session_id ON analytics_events(session_id);

-- Lead activities table
CREATE TABLE lead_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    activity_subject VARCHAR(255),
    activity_description TEXT,
    activity_outcome VARCHAR(100),
    performed_by UUID,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    next_action VARCHAR(255),
    next_action_date TIMESTAMP WITH TIME ZONE,
    activity_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Lead activities indexes
CREATE INDEX idx_lead_activities_lead_id ON lead_activities(lead_id);
CREATE INDEX idx_lead_activities_type ON lead_activities(activity_type);
CREATE INDEX idx_lead_activities_created_at ON lead_activities(created_at);
CREATE INDEX idx_lead_activities_scheduled_at ON lead_activities(scheduled_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partners_updated_at BEFORE UPDATE ON partners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_partner_deals_updated_at BEFORE UPDATE ON partner_deals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial Fortune 500 companies data
INSERT INTO companies (name, domain, industry, employee_count, annual_revenue, fortune_rank, is_fortune_500, company_size) VALUES
('Apple Inc.', 'apple.com', 'Technology', 147000, 365817000000, 1, TRUE, 'enterprise'),
('Microsoft Corporation', 'microsoft.com', 'Technology', 181000, 143015000000, 2, TRUE, 'enterprise'),
('Amazon.com Inc.', 'amazon.com', 'E-commerce/Cloud', 1298000, 469822000000, 3, TRUE, 'enterprise'),
('Alphabet Inc.', 'google.com', 'Technology', 139995, 257637000000, 4, TRUE, 'enterprise'),
('Tesla Inc.', 'tesla.com', 'Automotive/Energy', 99290, 53823000000, 5, TRUE, 'enterprise'),
('Berkshire Hathaway Inc.', 'berkshirehathaway.com', 'Financial Services', 372000, 245510000000, 6, TRUE, 'enterprise'),
('Meta Platforms Inc.', 'meta.com', 'Technology', 67317, 85965000000, 7, TRUE, 'enterprise'),
('UnitedHealth Group Incorporated', 'unitedhealthgroup.com', 'Healthcare', 350000, 287597000000, 8, TRUE, 'enterprise'),
('Johnson & Johnson', 'jnj.com', 'Healthcare', 134500, 93775000000, 9, TRUE, 'enterprise'),
('JPMorgan Chase & Co.', 'jpmorganchase.com', 'Financial Services', 271025, 119543000000, 10, TRUE, 'enterprise');

-- Insert sample lead statuses and types for reference
COMMENT ON COLUMN leads.lead_status IS 'Valid values: new, qualified, contacted, demo_scheduled, proposal_sent, closed_won, closed_lost';
COMMENT ON COLUMN leads.seniority_level IS 'Valid values: C-Level, VP, Director, Manager, Individual';
COMMENT ON COLUMN leads.priority IS 'Valid values: low, medium, high, urgent';

COMMENT ON COLUMN partners.partner_tier IS 'Valid values: authorized, gold, platinum';
COMMENT ON COLUMN partners.status IS 'Valid values: pending, approved, active, suspended, terminated';

COMMENT ON COLUMN partner_deals.deal_status IS 'Valid values: pipeline, proposal, negotiation, closed_won, closed_lost';

COMMENT ON COLUMN security_assessments.risk_level IS 'Valid values: low, medium, high, critical';

-- Create database views for common queries
CREATE VIEW fortune_500_leads AS
SELECT l.*, c.name as company_name, c.fortune_rank
FROM leads l
JOIN companies c ON l.company_id = c.id
WHERE c.is_fortune_500 = TRUE;

CREATE VIEW high_value_opportunities AS
SELECT l.*, c.name as company_name, c.is_fortune_500
FROM leads l
JOIN companies c ON l.company_id = c.id
WHERE l.estimated_deal_value >= 1000000
ORDER BY l.estimated_deal_value DESC;

CREATE VIEW partner_performance AS
SELECT 
    p.id,
    p.company_name,
    p.partner_tier,
    p.commission_rate,
    COUNT(pd.id) as total_deals,
    SUM(CASE WHEN pd.deal_status = 'closed_won' THEN pd.deal_value ELSE 0 END) as won_value,
    SUM(CASE WHEN pd.deal_status = 'closed_won' THEN pd.commission_amount ELSE 0 END) as total_commission
FROM partners p
LEFT JOIN partner_deals pd ON p.id = pd.partner_id
WHERE p.status = 'active'
GROUP BY p.id, p.company_name, p.partner_tier, p.commission_rate;

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO enterprise_scanner_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO enterprise_scanner_app;