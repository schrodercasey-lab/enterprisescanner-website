-- ============================================================================
-- Privacy Engineering Database Schema
-- For GDPR & CCPA Compliance Automation
-- ============================================================================
-- 
-- This schema supports:
-- - GDPR Article 30 (Records of Processing Activities)
-- - GDPR Articles 15-22 (Data Subject Rights)
-- - CCPA §1798.100-130 (Consumer Rights)
-- - Complete audit trail for regulatory compliance
--
-- Database: PostgreSQL 12+
-- ============================================================================

-- ============================================================================
-- CORE USER TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(2) DEFAULT 'US',
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT NOW(),
    last_modified TIMESTAMP DEFAULT NOW(),
    
    -- Privacy flags
    gdpr_subject BOOLEAN DEFAULT FALSE,
    ccpa_consumer BOOLEAN DEFAULT FALSE,
    ccpa_deleted BOOLEAN DEFAULT FALSE,
    ccpa_deletion_date TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_country (country),
    INDEX idx_created_at (created_at)
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_type VARCHAR(50),
    subscription_tier VARCHAR(50),
    subscription_status VARCHAR(20),
    account_status VARCHAR(20) DEFAULT 'active',
    payment_method VARCHAR(50),
    payment_method_masked VARCHAR(50),
    billing_address TEXT,
    account_balance DECIMAL(10, 2) DEFAULT 0.00,
    loyalty_points INTEGER DEFAULT 0,
    account_tier VARCHAR(20) DEFAULT 'standard',
    account_created TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (account_status)
);

-- ============================================================================
-- TRANSACTION & FINANCIAL DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    transaction_type VARCHAR(50),
    amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_date TIMESTAMP DEFAULT NOW(),
    description TEXT,
    status VARCHAR(20),
    anonymized_at TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    purchase_date TIMESTAMP DEFAULT NOW(),
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    quantity INTEGER,
    total_amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    shipping_address TEXT,
    order_status VARCHAR(20) DEFAULT 'pending',
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    ccpa_deleted_at TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_purchase_date (purchase_date),
    INDEX idx_order_status (order_status)
);

CREATE TABLE IF NOT EXISTS financial_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE RESTRICT,
    record_type VARCHAR(50),
    record_date TIMESTAMP DEFAULT NOW(),
    amount DECIMAL(10, 2),
    description TEXT,
    retention_required_until DATE,
    legal_hold BOOLEAN DEFAULT FALSE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_record_type (record_type),
    INDEX idx_legal_hold (legal_hold)
);

-- ============================================================================
-- BEHAVIORAL & ACTIVITY DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_activity (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type VARCHAR(50),
    activity_timestamp TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    page_visited VARCHAR(500),
    action_taken VARCHAR(100),
    duration_seconds INTEGER,
    
    INDEX idx_user_id (user_id),
    INDEX idx_activity_timestamp (activity_timestamp),
    INDEX idx_activity_type (activity_type)
);

CREATE TABLE IF NOT EXISTS browsing_history (
    browsing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    page_url TEXT,
    page_title VARCHAR(500),
    visit_timestamp TIMESTAMP DEFAULT NOW(),
    duration_seconds INTEGER,
    referrer_url TEXT,
    search_terms TEXT,
    
    INDEX idx_user_id (user_id),
    INDEX idx_visit_timestamp (visit_timestamp)
);

CREATE TABLE IF NOT EXISTS location_history (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(2),
    zip_code VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW(),
    location_source VARCHAR(50),
    accuracy_meters INTEGER,
    
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_location (latitude, longitude)
);

-- ============================================================================
-- DEVICE & TECHNICAL DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    device_type VARCHAR(50),
    operating_system VARCHAR(100),
    browser VARCHAR(100),
    browser_version VARCHAR(50),
    screen_resolution VARCHAR(20),
    language VARCHAR(10),
    timezone VARCHAR(50),
    ip_address INET,
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_device_type (device_type)
);

-- ============================================================================
-- COMMUNICATION DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS communications (
    communication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    communication_type VARCHAR(50),
    subject VARCHAR(255),
    content_summary TEXT,
    sent_date TIMESTAMP DEFAULT NOW(),
    recipient_email VARCHAR(255),
    sender_email VARCHAR(255),
    status VARCHAR(20),
    
    INDEX idx_user_id (user_id),
    INDEX idx_sent_date (sent_date),
    INDEX idx_communication_type (communication_type)
);

CREATE TABLE IF NOT EXISTS marketing_communications (
    marketing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    campaign_name VARCHAR(255),
    sent_date TIMESTAMP DEFAULT NOW(),
    opened BOOLEAN DEFAULT FALSE,
    clicked BOOLEAN DEFAULT FALSE,
    opt_out BOOLEAN DEFAULT FALSE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_opt_out (opt_out)
);

-- ============================================================================
-- SECURITY DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    event_type VARCHAR(100),
    event_timestamp TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    location VARCHAR(255),
    device_info TEXT,
    risk_score INTEGER,
    action_taken VARCHAR(100),
    
    INDEX idx_user_id (user_id),
    INDEX idx_event_timestamp (event_timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_risk_score (risk_score)
);

-- ============================================================================
-- CONSENT & PREFERENCES
-- ============================================================================

CREATE TABLE IF NOT EXISTS consent_log (
    consent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    consent_type VARCHAR(100),
    consent_given BOOLEAN,
    consent_timestamp TIMESTAMP DEFAULT NOW(),
    consent_version VARCHAR(20),
    consent_method VARCHAR(50),
    consent_text TEXT,
    withdrawn_at TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_consent_type (consent_type),
    INDEX idx_consent_timestamp (consent_timestamp)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    preference_key VARCHAR(100),
    preference_value TEXT,
    last_updated TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (user_id, preference_key),
    INDEX idx_user_id (user_id)
);

-- ============================================================================
-- INFERENCES & DERIVED DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_inferences (
    inference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    inference_type VARCHAR(100),
    inference_value TEXT,
    confidence_score DECIMAL(5, 2),
    created_date TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    data_source VARCHAR(255),
    
    INDEX idx_user_id (user_id),
    INDEX idx_inference_type (inference_type)
);

-- ============================================================================
-- THIRD-PARTY SHARING
-- ============================================================================

CREATE TABLE IF NOT EXISTS third_party_sharing (
    sharing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    third_party_name VARCHAR(255),
    third_party_category VARCHAR(100),
    data_category_shared VARCHAR(255),
    sharing_date TIMESTAMP DEFAULT NOW(),
    sharing_purpose TEXT,
    legal_basis VARCHAR(100),
    opt_out_available BOOLEAN DEFAULT TRUE,
    opt_out_requested BOOLEAN DEFAULT FALSE,
    opt_out_date TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_sharing_date (sharing_date),
    INDEX idx_opt_out_requested (opt_out_requested)
);

-- ============================================================================
-- GDPR COMPLIANCE TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS gdpr_data_subject_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_subject_id VARCHAR(255) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    request_date TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP,
    verification_method VARCHAR(100),
    status VARCHAR(20) DEFAULT 'received',
    response_deadline TIMESTAMP,
    fulfilled_at TIMESTAMP,
    response_sent_at TIMESTAMP,
    notes TEXT,
    
    INDEX idx_data_subject_id (data_subject_id),
    INDEX idx_request_type (request_type),
    INDEX idx_status (status),
    INDEX idx_response_deadline (response_deadline)
);

CREATE TABLE IF NOT EXISTS gdpr_erasure_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_subject_id VARCHAR(255) NOT NULL,
    user_id UUID,
    erasure_timestamp TIMESTAMP DEFAULT NOW(),
    tables_affected TEXT,
    total_records_deleted INTEGER,
    request_verified BOOLEAN,
    erased_by VARCHAR(255),
    verification_method VARCHAR(100),
    
    INDEX idx_data_subject_id (data_subject_id),
    INDEX idx_erasure_timestamp (erasure_timestamp)
);

CREATE TABLE IF NOT EXISTS gdpr_processing_activities (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_name VARCHAR(255) NOT NULL,
    controller_name VARCHAR(255),
    dpo_contact VARCHAR(255),
    purposes TEXT,
    legal_basis VARCHAR(100),
    data_categories TEXT,
    data_subjects TEXT,
    recipients TEXT,
    third_country_transfers BOOLEAN DEFAULT FALSE,
    safeguards TEXT,
    retention_period VARCHAR(255),
    security_measures TEXT,
    last_reviewed TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_activity_name (activity_name),
    INDEX idx_last_reviewed (last_reviewed)
);

-- ============================================================================
-- CCPA COMPLIANCE TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS ccpa_consumer_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id VARCHAR(255) NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    request_date TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP,
    verification_method VARCHAR(100),
    status VARCHAR(20) DEFAULT 'received',
    response_deadline TIMESTAMP,
    fulfilled_at TIMESTAMP,
    response_method VARCHAR(50),
    notes TEXT,
    
    INDEX idx_consumer_id (consumer_id),
    INDEX idx_request_type (request_type),
    INDEX idx_status (status),
    INDEX idx_response_deadline (response_deadline)
);

CREATE TABLE IF NOT EXISTS ccpa_deletion_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id VARCHAR(255) NOT NULL,
    user_id UUID,
    deletion_timestamp TIMESTAMP DEFAULT NOW(),
    tables_processed TEXT,
    records_deleted INTEGER,
    records_retained INTEGER,
    retention_reasons TEXT,
    verified BOOLEAN,
    deleted_by VARCHAR(255),
    
    INDEX idx_consumer_id (consumer_id),
    INDEX idx_deletion_timestamp (deletion_timestamp)
);

CREATE TABLE IF NOT EXISTS ccpa_sale_opt_out (
    opt_out_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    opt_out_date TIMESTAMP DEFAULT NOW(),
    opt_out_method VARCHAR(50),
    third_parties_notified TEXT,
    notification_sent_at TIMESTAMP,
    
    UNIQUE (consumer_id),
    INDEX idx_consumer_id (consumer_id),
    INDEX idx_opt_out_date (opt_out_date)
);

CREATE TABLE IF NOT EXISTS ccpa_disclosure_log (
    disclosure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id VARCHAR(255) NOT NULL,
    disclosure_date TIMESTAMP DEFAULT NOW(),
    disclosure_period_start DATE,
    disclosure_period_end DATE,
    categories_collected TEXT,
    categories_sold TEXT,
    categories_disclosed TEXT,
    business_purposes TEXT,
    third_parties TEXT,
    
    INDEX idx_consumer_id (consumer_id),
    INDEX idx_disclosure_date (disclosure_date)
);

-- ============================================================================
-- AUDIT & COMPLIANCE TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS privacy_audit_trail (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100),
    event_timestamp TIMESTAMP DEFAULT NOW(),
    user_id UUID,
    consumer_id VARCHAR(255),
    action_performed VARCHAR(255),
    action_details TEXT,
    performed_by VARCHAR(255),
    ip_address INET,
    regulation VARCHAR(20),
    
    INDEX idx_event_timestamp (event_timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_regulation (regulation)
);

CREATE TABLE IF NOT EXISTS compliance_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type VARCHAR(100),
    report_period_start DATE,
    report_period_end DATE,
    generated_at TIMESTAMP DEFAULT NOW(),
    generated_by VARCHAR(255),
    total_requests INTEGER,
    requests_fulfilled INTEGER,
    average_response_time_days DECIMAL(5, 2),
    report_data JSONB,
    
    INDEX idx_report_type (report_type),
    INDEX idx_generated_at (generated_at)
);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

CREATE OR REPLACE VIEW v_gdpr_request_summary AS
SELECT 
    request_type,
    status,
    COUNT(*) as request_count,
    AVG(EXTRACT(DAY FROM (fulfilled_at - request_date))) as avg_days_to_fulfill,
    COUNT(CASE WHEN fulfilled_at > response_deadline THEN 1 END) as overdue_count
FROM gdpr_data_subject_requests
GROUP BY request_type, status;

CREATE OR REPLACE VIEW v_ccpa_request_summary AS
SELECT 
    request_type,
    status,
    COUNT(*) as request_count,
    AVG(EXTRACT(DAY FROM (fulfilled_at - request_date))) as avg_days_to_fulfill,
    COUNT(CASE WHEN fulfilled_at > response_deadline THEN 1 END) as overdue_count
FROM ccpa_consumer_requests
GROUP BY request_type, status;

CREATE OR REPLACE VIEW v_active_users_privacy_status AS
SELECT 
    u.user_id,
    u.email,
    u.gdpr_subject,
    u.ccpa_consumer,
    u.ccpa_deleted,
    COUNT(DISTINCT c.consent_id) as total_consents,
    COUNT(DISTINCT CASE WHEN c.consent_given = TRUE AND c.withdrawn_at IS NULL THEN c.consent_id END) as active_consents,
    o.opt_out_date as sale_opt_out_date
FROM users u
LEFT JOIN consent_log c ON u.user_id = c.user_id
LEFT JOIN ccpa_sale_opt_out o ON u.email = o.consumer_id
WHERE u.ccpa_deleted = FALSE
GROUP BY u.user_id, u.email, u.gdpr_subject, u.ccpa_consumer, u.ccpa_deleted, o.opt_out_date;

-- ============================================================================
-- FUNCTIONS FOR PRIVACY AUTOMATION
-- ============================================================================

CREATE OR REPLACE FUNCTION check_gdpr_response_deadline()
RETURNS TABLE (
    request_id UUID,
    data_subject_id VARCHAR,
    request_type VARCHAR,
    days_until_deadline INTEGER,
    overdue BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.request_id,
        r.data_subject_id,
        r.request_type,
        EXTRACT(DAY FROM (r.response_deadline - NOW()))::INTEGER as days_until_deadline,
        (NOW() > r.response_deadline) as overdue
    FROM gdpr_data_subject_requests r
    WHERE r.status IN ('received', 'verifying', 'processing')
    ORDER BY r.response_deadline ASC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_ccpa_response_deadline()
RETURNS TABLE (
    request_id UUID,
    consumer_id VARCHAR,
    request_type VARCHAR,
    days_until_deadline INTEGER,
    overdue BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.request_id,
        r.consumer_id,
        r.request_type,
        EXTRACT(DAY FROM (r.response_deadline - NOW()))::INTEGER as days_until_deadline,
        (NOW() > r.response_deadline) as overdue
    FROM ccpa_consumer_requests r
    WHERE r.status IN ('received', 'verifying', 'processing')
    ORDER BY r.response_deadline ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional indexes for common query patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_privacy_flags 
ON users(gdpr_subject, ccpa_consumer, ccpa_deleted);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_consent_active 
ON consent_log(user_id, consent_given) WHERE withdrawn_at IS NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_third_party_opt_out 
ON third_party_sharing(user_id, opt_out_requested);

-- ============================================================================
-- TRIGGERS FOR AUDIT TRAIL
-- ============================================================================

CREATE OR REPLACE FUNCTION log_privacy_event()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO privacy_audit_trail (
        event_type,
        user_id,
        action_performed,
        action_details,
        regulation
    ) VALUES (
        TG_TABLE_NAME || '_' || TG_OP,
        NEW.user_id,
        TG_OP,
        row_to_json(NEW)::TEXT,
        CASE 
            WHEN NEW.gdpr_subject THEN 'GDPR'
            WHEN NEW.ccpa_consumer THEN 'CCPA'
            ELSE 'GENERAL'
        END
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to key tables
CREATE TRIGGER gdpr_request_audit
AFTER INSERT OR UPDATE ON gdpr_data_subject_requests
FOR EACH ROW EXECUTE FUNCTION log_privacy_event();

CREATE TRIGGER ccpa_request_audit
AFTER INSERT OR UPDATE ON ccpa_consumer_requests
FOR EACH ROW EXECUTE FUNCTION log_privacy_event();

-- ============================================================================
-- GRANTS (Adjust based on your user roles)
-- ============================================================================

-- Example: Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO privacy_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO privacy_app_user;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'Core user identity data with privacy flags';
COMMENT ON TABLE gdpr_data_subject_requests IS 'GDPR Article 15-22 data subject rights requests';
COMMENT ON TABLE ccpa_consumer_requests IS 'CCPA §1798.100-130 consumer rights requests';
COMMENT ON TABLE gdpr_erasure_log IS 'GDPR Article 17 right to erasure audit trail';
COMMENT ON TABLE ccpa_deletion_log IS 'CCPA §1798.105 right to delete audit trail';
COMMENT ON TABLE privacy_audit_trail IS 'Comprehensive audit trail for all privacy operations';

COMMENT ON FUNCTION check_gdpr_response_deadline() IS 'Returns GDPR requests approaching or past 30-day deadline';
COMMENT ON FUNCTION check_ccpa_response_deadline() IS 'Returns CCPA requests approaching or past 45-day deadline';

-- ============================================================================
-- SAMPLE DATA FOR TESTING (Optional - remove in production)
-- ============================================================================

-- Example: Insert test user
-- INSERT INTO users (email, first_name, last_name, country, gdpr_subject, ccpa_consumer)
-- VALUES ('test@example.com', 'Test', 'User', 'US', TRUE, TRUE);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Deployment Notes:
-- 1. Review and adjust table names/columns based on your existing schema
-- 2. Configure appropriate user permissions (GRANT statements)
-- 3. Set up regular backups of privacy data
-- 4. Implement encryption at rest for sensitive tables
-- 5. Configure automated monitoring for deadline tracking
-- 6. Test all privacy functions in staging before production deployment

-- Compliance Notes:
-- - GDPR requires 30-day response time (1 month, extendable to 3 months)
-- - CCPA requires 45-day response time (extendable to 90 days)
-- - Audit trails must be maintained for regulatory inspection
-- - Regular compliance reports should be generated
-- - Data retention policies should be configured per table
