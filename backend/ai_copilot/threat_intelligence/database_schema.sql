-- =============================================================================
-- Module G.2: Advanced Threat Intelligence Engine - Database Schema
-- =============================================================================
-- Purpose: Store and manage threat intelligence data from 25+ sources
-- Database: SQLite (development) / PostgreSQL (production)
-- Version: 1.0.0
-- Created: October 17, 2025
-- =============================================================================

-- Enable WAL mode for better concurrent access (SQLite)
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- =============================================================================
-- THREAT INTELLIGENCE SOURCES
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_intel_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL, -- 'commercial', 'osint', 'government', 'proprietary', 'dark_web'
    source_url VARCHAR(500),
    api_endpoint VARCHAR(500),
    api_key_encrypted TEXT,
    is_active BOOLEAN DEFAULT 1,
    reliability_score DECIMAL(3,2) DEFAULT 0.50, -- 0.0 to 1.0
    last_sync_timestamp DATETIME,
    sync_frequency_minutes INTEGER DEFAULT 60,
    total_indicators_imported INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_active ON threat_intel_sources(is_active);
CREATE INDEX idx_sources_type ON threat_intel_sources(source_type);

-- =============================================================================
-- THREAT ACTORS (APT GROUPS)
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_actors (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_name VARCHAR(200) NOT NULL,
    actor_aliases TEXT, -- JSON array of alternative names
    attribution_confidence DECIMAL(3,2) DEFAULT 0.50, -- 0.0 to 1.0
    suspected_nation_state VARCHAR(100),
    motivation VARCHAR(100), -- 'financial', 'espionage', 'sabotage', 'hacktivism'
    sophistication_level VARCHAR(50), -- 'low', 'medium', 'high', 'advanced'
    first_observed_date DATE,
    last_activity_date DATE,
    is_active BOOLEAN DEFAULT 1,
    target_industries TEXT, -- JSON array
    target_regions TEXT, -- JSON array
    mitre_attck_techniques TEXT, -- JSON array of technique IDs
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actors_active ON threat_actors(is_active);
CREATE INDEX idx_actors_nation ON threat_actors(suspected_nation_state);
CREATE INDEX idx_actors_sophistication ON threat_actors(sophistication_level);

-- =============================================================================
-- THREAT CAMPAIGNS
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name VARCHAR(200) NOT NULL,
    actor_id INTEGER,
    campaign_start_date DATE,
    campaign_end_date DATE,
    is_ongoing BOOLEAN DEFAULT 1,
    target_industries TEXT, -- JSON array
    target_regions TEXT, -- JSON array
    attack_vectors TEXT, -- JSON array
    malware_families TEXT, -- JSON array
    objectives TEXT,
    description TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_id) REFERENCES threat_actors(actor_id) ON DELETE SET NULL
);

CREATE INDEX idx_campaigns_ongoing ON threat_campaigns(is_ongoing);
CREATE INDEX idx_campaigns_actor ON threat_campaigns(actor_id);
CREATE INDEX idx_campaigns_dates ON threat_campaigns(campaign_start_date, campaign_end_date);

-- =============================================================================
-- INDICATORS OF COMPROMISE (IoCs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS indicators_of_compromise (
    ioc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ioc_type VARCHAR(50) NOT NULL, -- 'ip', 'domain', 'url', 'file_hash', 'email', 'registry_key', 'mutex'
    ioc_value TEXT NOT NULL,
    ioc_hash VARCHAR(64), -- SHA-256 hash of ioc_value for deduplication
    first_seen_date DATETIME,
    last_seen_date DATETIME,
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    threat_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    is_active BOOLEAN DEFAULT 1,
    false_positive_flag BOOLEAN DEFAULT 0,
    validation_status VARCHAR(20) DEFAULT 'unvalidated', -- 'unvalidated', 'validated', 'false_positive'
    source_count INTEGER DEFAULT 1, -- Number of sources reporting this IoC
    tags TEXT, -- JSON array
    context TEXT, -- Additional context about the IoC
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_ioc_hash ON indicators_of_compromise(ioc_hash);
CREATE INDEX idx_ioc_type ON indicators_of_compromise(ioc_type);
CREATE INDEX idx_ioc_active ON indicators_of_compromise(is_active);
CREATE INDEX idx_ioc_threat_level ON indicators_of_compromise(threat_level);
CREATE INDEX idx_ioc_validation ON indicators_of_compromise(validation_status);

-- =============================================================================
-- IoC SOURCE MAPPING (Many-to-Many)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ioc_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ioc_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    reported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    FOREIGN KEY (ioc_id) REFERENCES indicators_of_compromise(ioc_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES threat_intel_sources(source_id) ON DELETE CASCADE,
    UNIQUE(ioc_id, source_id)
);

CREATE INDEX idx_ioc_sources_ioc ON ioc_sources(ioc_id);
CREATE INDEX idx_ioc_sources_source ON ioc_sources(source_id);

-- =============================================================================
-- IoC CAMPAIGN ASSOCIATION (Many-to-Many)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ioc_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ioc_id INTEGER NOT NULL,
    campaign_id INTEGER NOT NULL,
    role VARCHAR(100), -- 'c2_server', 'malware_hash', 'phishing_domain', etc.
    FOREIGN KEY (ioc_id) REFERENCES indicators_of_compromise(ioc_id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES threat_campaigns(campaign_id) ON DELETE CASCADE,
    UNIQUE(ioc_id, campaign_id)
);

CREATE INDEX idx_ioc_campaigns_ioc ON ioc_campaigns(ioc_id);
CREATE INDEX idx_ioc_campaigns_campaign ON ioc_campaigns(campaign_id);

-- =============================================================================
-- VULNERABILITIES (CVEs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_vulnerabilities (
    vulnerability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cve_id VARCHAR(20) UNIQUE,
    cvss_score DECIMAL(3,1),
    cvss_vector VARCHAR(100),
    severity VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    published_date DATE,
    last_modified_date DATE,
    description TEXT,
    affected_products TEXT, -- JSON array
    vendor VARCHAR(200),
    has_exploit BOOLEAN DEFAULT 0,
    has_poc BOOLEAN DEFAULT 0,
    exploited_in_wild BOOLEAN DEFAULT 0,
    exploit_availability_date DATE,
    weaponization_timeline_days INTEGER, -- Days from publish to exploit
    patch_available BOOLEAN DEFAULT 0,
    patch_release_date DATE,
    epss_score DECIMAL(5,4), -- Exploit Prediction Scoring System (0.0 to 1.0)
    trending BOOLEAN DEFAULT 0,
    social_media_mentions INTEGER DEFAULT 0,
    dark_web_mentions INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vuln_cve ON threat_vulnerabilities(cve_id);
CREATE INDEX idx_vuln_severity ON threat_vulnerabilities(severity);
CREATE INDEX idx_vuln_exploit ON threat_vulnerabilities(has_exploit);
CREATE INDEX idx_vuln_wild ON threat_vulnerabilities(exploited_in_wild);
CREATE INDEX idx_vuln_trending ON threat_vulnerabilities(trending);
CREATE INDEX idx_vuln_epss ON threat_vulnerabilities(epss_score);

-- =============================================================================
-- VULNERABILITY CAMPAIGN ASSOCIATION
-- =============================================================================

CREATE TABLE IF NOT EXISTS vulnerability_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vulnerability_id INTEGER NOT NULL,
    campaign_id INTEGER NOT NULL,
    exploitation_observed BOOLEAN DEFAULT 0,
    first_exploitation_date DATE,
    FOREIGN KEY (vulnerability_id) REFERENCES threat_vulnerabilities(vulnerability_id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES threat_campaigns(campaign_id) ON DELETE CASCADE,
    UNIQUE(vulnerability_id, campaign_id)
);

CREATE INDEX idx_vuln_campaigns_vuln ON vulnerability_campaigns(vulnerability_id);
CREATE INDEX idx_vuln_campaigns_campaign ON vulnerability_campaigns(campaign_id);

-- =============================================================================
-- MALWARE FAMILIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS malware_families (
    malware_id INTEGER PRIMARY KEY AUTOINCREMENT,
    malware_name VARCHAR(200) NOT NULL UNIQUE,
    malware_type VARCHAR(50), -- 'trojan', 'ransomware', 'backdoor', 'rootkit', 'worm', 'spyware'
    first_observed_date DATE,
    last_activity_date DATE,
    is_active BOOLEAN DEFAULT 1,
    capabilities TEXT, -- JSON array
    infection_vectors TEXT, -- JSON array
    file_hashes TEXT, -- JSON array of known hashes
    c2_infrastructure TEXT, -- JSON array of C2 servers
    associated_actors TEXT, -- JSON array of actor IDs
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_malware_type ON malware_families(malware_type);
CREATE INDEX idx_malware_active ON malware_families(is_active);

-- =============================================================================
-- THREAT INTELLIGENCE REPORTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_intelligence_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_title VARCHAR(500) NOT NULL,
    report_type VARCHAR(50), -- 'tactical', 'operational', 'strategic'
    source_id INTEGER,
    publish_date DATE,
    report_url VARCHAR(1000),
    report_content TEXT,
    report_summary TEXT,
    tlp_level VARCHAR(20) DEFAULT 'amber', -- 'white', 'green', 'amber', 'red'
    industries_affected TEXT, -- JSON array
    regions_affected TEXT, -- JSON array
    iocs_extracted INTEGER DEFAULT 0,
    cves_mentioned TEXT, -- JSON array
    actors_mentioned TEXT, -- JSON array
    campaigns_mentioned TEXT, -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES threat_intel_sources(source_id) ON DELETE SET NULL
);

CREATE INDEX idx_reports_source ON threat_intelligence_reports(source_id);
CREATE INDEX idx_reports_date ON threat_intelligence_reports(publish_date);
CREATE INDEX idx_reports_type ON threat_intelligence_reports(report_type);
CREATE INDEX idx_reports_tlp ON threat_intelligence_reports(tlp_level);

-- =============================================================================
-- THREAT PREDICTIONS (ML-Generated)
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_type VARCHAR(50), -- 'zero_day_likelihood', 'weaponization_timeline', 'target_industry', 'attack_volume'
    subject_id INTEGER, -- CVE ID, Actor ID, etc.
    subject_type VARCHAR(50), -- 'vulnerability', 'actor', 'campaign'
    prediction_date DATE NOT NULL,
    prediction_horizon_days INTEGER, -- 30, 60, or 90 days
    prediction_value DECIMAL(10,4),
    confidence_score DECIMAL(3,2),
    prediction_rationale TEXT,
    actual_outcome DECIMAL(10,4), -- Filled in after horizon passes
    accuracy_score DECIMAL(3,2), -- How accurate was the prediction
    model_version VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_type ON threat_predictions(prediction_type);
CREATE INDEX idx_predictions_date ON threat_predictions(prediction_date);
CREATE INDEX idx_predictions_subject ON threat_predictions(subject_type, subject_id);

-- =============================================================================
-- INDUSTRY THREAT INTELLIGENCE
-- =============================================================================

CREATE TABLE IF NOT EXISTS industry_threat_intel (
    intel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_sector VARCHAR(100) NOT NULL, -- 'financial', 'healthcare', 'energy', 'retail', 'technology'
    threat_category VARCHAR(100), -- 'ransomware', 'data_breach', 'ddos', 'insider_threat'
    severity VARCHAR(20),
    incident_count INTEGER DEFAULT 0,
    average_impact_cost DECIMAL(15,2),
    trend VARCHAR(20), -- 'increasing', 'stable', 'decreasing'
    reporting_period_start DATE,
    reporting_period_end DATE,
    top_threat_actors TEXT, -- JSON array
    top_malware_families TEXT, -- JSON array
    common_attack_vectors TEXT, -- JSON array
    recommendations TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_industry_sector ON industry_threat_intel(industry_sector);
CREATE INDEX idx_industry_period ON industry_threat_intel(reporting_period_start, reporting_period_end);

-- =============================================================================
-- ASSET THREAT CORRELATION (Links to assets from other modules)
-- =============================================================================

CREATE TABLE IF NOT EXISTS asset_threat_exposure (
    exposure_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL, -- From asset discovery module
    ioc_id INTEGER,
    vulnerability_id INTEGER,
    campaign_id INTEGER,
    exposure_type VARCHAR(50), -- 'vulnerable', 'ioc_match', 'targeted'
    risk_score DECIMAL(5,2),
    exposure_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    remediated BOOLEAN DEFAULT 0,
    remediation_date DATETIME,
    FOREIGN KEY (ioc_id) REFERENCES indicators_of_compromise(ioc_id) ON DELETE CASCADE,
    FOREIGN KEY (vulnerability_id) REFERENCES threat_vulnerabilities(vulnerability_id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES threat_campaigns(campaign_id) ON DELETE CASCADE
);

CREATE INDEX idx_exposure_asset ON asset_threat_exposure(asset_id);
CREATE INDEX idx_exposure_remediated ON asset_threat_exposure(remediated);
CREATE INDEX idx_exposure_risk ON asset_threat_exposure(risk_score);

-- =============================================================================
-- THREAT INTELLIGENCE ALERTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_intel_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type VARCHAR(50), -- 'zero_day', 'apt_campaign', 'ioc_match', 'trending_threat'
    severity VARCHAR(20),
    title VARCHAR(500),
    description TEXT,
    affected_assets_count INTEGER DEFAULT 0,
    recommended_actions TEXT,
    alert_status VARCHAR(20) DEFAULT 'open', -- 'open', 'acknowledged', 'resolved'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at DATETIME,
    resolved_at DATETIME,
    acknowledged_by VARCHAR(100),
    resolved_by VARCHAR(100)
);

CREATE INDEX idx_alerts_status ON threat_intel_alerts(alert_status);
CREATE INDEX idx_alerts_severity ON threat_intel_alerts(severity);
CREATE INDEX idx_alerts_created ON threat_intel_alerts(created_at);

-- =============================================================================
-- THREAT ACTOR TTPs (MITRE ATT&CK Mapping)
-- =============================================================================

CREATE TABLE IF NOT EXISTS threat_actor_ttps (
    ttp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER NOT NULL,
    mitre_technique_id VARCHAR(20) NOT NULL, -- e.g., "T1566.001"
    mitre_technique_name VARCHAR(200),
    mitre_tactic VARCHAR(100),
    observed_count INTEGER DEFAULT 1,
    first_observed_date DATE,
    last_observed_date DATE,
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    FOREIGN KEY (actor_id) REFERENCES threat_actors(actor_id) ON DELETE CASCADE
);

CREATE INDEX idx_ttps_actor ON threat_actor_ttps(actor_id);
CREATE INDEX idx_ttps_technique ON threat_actor_ttps(mitre_technique_id);
CREATE INDEX idx_ttps_tactic ON threat_actor_ttps(mitre_tactic);

-- =============================================================================
-- DARK WEB MONITORING
-- =============================================================================

CREATE TABLE IF NOT EXISTS dark_web_mentions (
    mention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mention_type VARCHAR(50), -- 'credential_dump', 'exploit_sale', 'vulnerability_discussion', 'data_leak'
    forum_name VARCHAR(200),
    post_url TEXT,
    post_content TEXT,
    post_author VARCHAR(200),
    post_date DATETIME,
    relevance_score DECIMAL(3,2),
    keywords_matched TEXT, -- JSON array
    related_assets TEXT, -- JSON array of asset IDs if matched
    severity VARCHAR(20),
    investigated BOOLEAN DEFAULT 0,
    investigation_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_darkweb_type ON dark_web_mentions(mention_type);
CREATE INDEX idx_darkweb_investigated ON dark_web_mentions(investigated);
CREATE INDEX idx_darkweb_severity ON dark_web_mentions(severity);
CREATE INDEX idx_darkweb_date ON dark_web_mentions(post_date);

-- =============================================================================
-- INTELLIGENCE CORRELATION SCORES
-- =============================================================================

CREATE TABLE IF NOT EXISTS correlation_scores (
    correlation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity1_type VARCHAR(50), -- 'actor', 'campaign', 'malware', 'ioc'
    entity1_id INTEGER,
    entity2_type VARCHAR(50),
    entity2_id INTEGER,
    correlation_strength DECIMAL(3,2), -- 0.0 to 1.0
    correlation_type VARCHAR(100), -- 'infrastructure_overlap', 'ttp_similarity', 'temporal_proximity'
    evidence_count INTEGER DEFAULT 1,
    first_correlated_date DATE,
    last_correlated_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_correlation_entity1 ON correlation_scores(entity1_type, entity1_id);
CREATE INDEX idx_correlation_entity2 ON correlation_scores(entity2_type, entity2_id);
CREATE INDEX idx_correlation_strength ON correlation_scores(correlation_strength);

-- =============================================================================
-- INITIAL DATA: Threat Intelligence Sources
-- =============================================================================

INSERT INTO threat_intel_sources (source_name, source_type, source_url, reliability_score) VALUES
-- Commercial Sources
('CrowdStrike Falcon Intelligence', 'commercial', 'https://api.crowdstrike.com', 0.95),
('Recorded Future', 'commercial', 'https://api.recordedfuture.com', 0.95),
('Mandiant Threat Intelligence', 'commercial', 'https://api.mandiant.com', 0.95),
('Palo Alto Networks Unit 42', 'commercial', 'https://autofocus.paloaltonetworks.com', 0.90),
('Anomali ThreatStream', 'commercial', 'https://api.anomali.com', 0.90),

-- OSINT Sources
('AlienVault OTX', 'osint', 'https://otx.alienvault.com', 0.75),
('Abuse.ch', 'osint', 'https://abuse.ch', 0.85),
('MISP Threat Sharing', 'osint', 'https://www.misp-project.org', 0.80),
('ThreatFox', 'osint', 'https://threatfox.abuse.ch', 0.80),
('URLhaus', 'osint', 'https://urlhaus.abuse.ch', 0.80),

-- Government Sources
('CISA Known Exploited Vulnerabilities', 'government', 'https://www.cisa.gov/known-exploited-vulnerabilities', 0.95),
('US-CERT', 'government', 'https://www.cisa.gov/uscert', 0.90),
('FBI InfraGard', 'government', 'https://www.infragard.org', 0.90),
('DHS AIS', 'government', 'https://www.cisa.gov/ais', 0.90),

-- Proprietary Sources
('Enterprise Scanner Honeypot Network', 'proprietary', 'internal', 1.00),
('Enterprise Scanner Customer Telemetry', 'proprietary', 'internal', 1.00),

-- Dark Web Monitoring
('Dark Web Forum Monitor', 'dark_web', 'tor://', 0.70),
('Paste Site Monitor', 'dark_web', 'https://', 0.65);

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
