-- Jupiter v3.0 - Module G.1: Autonomous Remediation Engine
-- Database Schema for jupiter_remediation.db
-- Created: October 17, 2025
-- Version: 1.0

-- ============================================================================
-- PRAGMA SETTINGS
-- Enable foreign key constraints and optimize for performance
-- ============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;

-- ============================================================================
-- REMEDIATION PLANS
-- Stores planned remediation activities with autonomy level
-- ============================================================================

CREATE TABLE IF NOT EXISTS remediation_plans (
    plan_id TEXT PRIMARY KEY,
    vulnerability_id TEXT NOT NULL,
    cve_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    asset_name TEXT NOT NULL,
    
    -- Risk assessment
    autonomy_level INTEGER NOT NULL CHECK(autonomy_level BETWEEN 0 AND 5),
    risk_score REAL NOT NULL CHECK(risk_score BETWEEN 0.0 AND 1.0),
    confidence REAL NOT NULL CHECK(confidence BETWEEN 0.0 AND 1.0),
    
    -- Patch information
    patch_id TEXT,
    patch_source TEXT, -- vendor, os_package, container, custom
    
    -- Deployment strategy
    strategy TEXT NOT NULL CHECK(strategy IN ('blue-green', 'canary', 'rolling', 'all-at-once')),
    
    -- Status tracking
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'IN_PROGRESS', 'SUCCESS', 'FAILED', 'ROLLED_BACK', 'CANCELLED')),
    
    -- Approval tracking (for Level 3)
    requires_approval BOOLEAN NOT NULL DEFAULT 0,
    approved_by TEXT,
    approved_at TIMESTAMP,
    approval_code TEXT,
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_for TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metadata
    created_by TEXT DEFAULT 'SYSTEM',
    priority INTEGER DEFAULT 5 CHECK(priority BETWEEN 1 AND 10),
    notes TEXT
    
    -- Note: vulnerability_id and asset_id reference main jupiter database
    -- Referential integrity enforced at application level
    -- FOREIGN KEY (patch_id) REFERENCES patches(patch_id) ON DELETE SET NULL
);

CREATE INDEX idx_remediation_plans_vuln ON remediation_plans(vulnerability_id);
CREATE INDEX idx_remediation_plans_asset ON remediation_plans(asset_id);
CREATE INDEX idx_remediation_plans_status ON remediation_plans(status);
CREATE INDEX idx_remediation_plans_created ON remediation_plans(created_at DESC);

-- ============================================================================
-- REMEDIATION EXECUTIONS
-- Tracks actual execution of remediation plans
-- ============================================================================

CREATE TABLE IF NOT EXISTS remediation_executions (
    execution_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    
    -- Execution status
    status TEXT NOT NULL CHECK(status IN ('QUEUED', 'RUNNING', 'SUCCESS', 'FAILED', 'ROLLED_BACK', 'TIMEOUT')),
    
    -- Timing metrics (all in seconds)
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    risk_analysis_duration INTEGER DEFAULT 0,
    sandbox_duration INTEGER DEFAULT 0,
    deployment_duration INTEGER DEFAULT 0,
    monitoring_duration INTEGER DEFAULT 0,
    total_duration INTEGER,
    
    -- Test results
    sandbox_passed BOOLEAN,
    tests_run INTEGER DEFAULT 0,
    tests_passed INTEGER DEFAULT 0,
    tests_failed INTEGER DEFAULT 0,
    test_pass_rate REAL,
    
    -- Performance metrics
    sandbox_performance_score REAL,
    production_performance_score REAL,
    
    -- Rollback tracking
    rollback_performed BOOLEAN DEFAULT 0,
    rollback_reason TEXT,
    rollback_duration INTEGER,
    rollback_success BOOLEAN,
    
    -- Error tracking
    error_message TEXT,
    error_stack_trace TEXT,
    
    -- Metadata
    worker_id TEXT, -- Identifies which remediation worker handled this
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    FOREIGN KEY (plan_id) REFERENCES remediation_plans(plan_id) ON DELETE CASCADE
);

CREATE INDEX idx_executions_plan ON remediation_executions(plan_id);
CREATE INDEX idx_executions_status ON remediation_executions(status);
CREATE INDEX idx_executions_started ON remediation_executions(started_at DESC);

-- ============================================================================
-- SYSTEM SNAPSHOTS
-- Stores system state before patching for rollback
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    
    -- Snapshot metadata
    snapshot_type TEXT NOT NULL CHECK(snapshot_type IN ('vm', 'container', 'kubernetes', 'database', 'configuration')),
    snapshot_method TEXT NOT NULL, -- hypervisor, docker, helm, pg_dump, etc.
    
    -- Snapshot data (JSON blob or reference)
    snapshot_data TEXT NOT NULL, -- JSON blob with snapshot details
    storage_location TEXT, -- S3, local path, etc.
    storage_size_mb REAL,
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    retention_days INTEGER DEFAULT 30,
    
    -- Status
    status TEXT NOT NULL CHECK(status IN ('CREATING', 'READY', 'RESTORING', 'EXPIRED', 'DELETED')),
    verified BOOLEAN DEFAULT 0,
    verified_at TIMESTAMP,
    
    -- Restore tracking
    restored_at TIMESTAMP,
    restore_duration INTEGER,
    restore_success BOOLEAN,
    
    FOREIGN KEY (execution_id) REFERENCES remediation_executions(execution_id) ON DELETE CASCADE
    -- Note: asset_id references main jupiter database
);

CREATE INDEX idx_snapshots_asset ON system_snapshots(asset_id);
CREATE INDEX idx_snapshots_execution ON system_snapshots(execution_id);
CREATE INDEX idx_snapshots_expires ON system_snapshots(expires_at);
CREATE INDEX idx_snapshots_status ON system_snapshots(status);

-- ============================================================================
-- RISK ASSESSMENTS
-- Stores AI-powered risk analysis results
-- ============================================================================

CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id TEXT PRIMARY KEY,
    vulnerability_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    
    -- Assessment metadata
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version TEXT NOT NULL,
    
    -- Individual risk factor scores (0.0 - 1.0)
    severity_score REAL NOT NULL CHECK(severity_score BETWEEN 0.0 AND 1.0),
    exploitability_score REAL NOT NULL CHECK(exploitability_score BETWEEN 0.0 AND 1.0),
    asset_criticality_score REAL NOT NULL CHECK(asset_criticality_score BETWEEN 0.0 AND 1.0),
    patch_maturity_score REAL NOT NULL CHECK(patch_maturity_score BETWEEN 0.0 AND 1.0),
    dependency_score REAL NOT NULL CHECK(dependency_score BETWEEN 0.0 AND 1.0),
    rollback_score REAL NOT NULL CHECK(rollback_score BETWEEN 0.0 AND 1.0),
    compliance_score REAL CHECK(compliance_score BETWEEN 0.0 AND 1.0),
    business_hours_score REAL CHECK(business_hours_score BETWEEN 0.0 AND 1.0),
    
    -- Overall assessment
    total_risk_score REAL NOT NULL CHECK(total_risk_score BETWEEN 0.0 AND 1.0),
    autonomy_level INTEGER NOT NULL CHECK(autonomy_level BETWEEN 0 AND 5),
    confidence REAL NOT NULL CHECK(confidence BETWEEN 0.0 AND 1.0),
    
    -- AI reasoning
    reasoning TEXT NOT NULL,
    factors_json TEXT, -- Detailed JSON with all analyzed factors
    
    -- Recommendations
    recommended_strategy TEXT,
    recommended_timing TEXT, -- immediate, business_hours, maintenance_window
    estimated_risk TEXT CHECK(estimated_risk IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    
    -- Override tracking
    human_reviewed BOOLEAN DEFAULT 0,
    human_override BOOLEAN DEFAULT 0,
    human_decision INTEGER, -- If human overrode, what level did they choose
    human_feedback TEXT,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP
    
    -- Note: vulnerability_id and asset_id reference main jupiter database
);

CREATE INDEX idx_risk_vuln ON risk_assessments(vulnerability_id);
CREATE INDEX idx_risk_asset ON risk_assessments(asset_id);
CREATE INDEX idx_risk_assessed ON risk_assessments(assessed_at DESC);
CREATE INDEX idx_risk_autonomy ON risk_assessments(autonomy_level);

-- ============================================================================
-- PATCHES
-- Catalog of available patches
-- ============================================================================

CREATE TABLE IF NOT EXISTS patches (
    patch_id TEXT PRIMARY KEY,
    cve_id TEXT NOT NULL,
    
    -- Vendor information
    vendor TEXT NOT NULL,
    product TEXT NOT NULL,
    patch_version TEXT NOT NULL,
    patch_name TEXT,
    
    -- Release information
    release_date DATE,
    source_url TEXT,
    advisory_url TEXT,
    
    -- Verification
    signature TEXT, -- Digital signature for verification
    signature_algorithm TEXT,
    checksum_sha256 TEXT,
    verified BOOLEAN DEFAULT 0,
    verified_at TIMESTAMP,
    
    -- Compatibility
    os_type TEXT, -- linux, windows, macos, container
    os_versions TEXT, -- JSON array: ["ubuntu-20.04", "ubuntu-22.04"]
    architecture TEXT, -- x86_64, arm64, etc.
    
    -- Requirements
    size_mb REAL,
    requires_reboot BOOLEAN DEFAULT 0,
    requires_downtime BOOLEAN DEFAULT 0,
    estimated_downtime_minutes INTEGER,
    prerequisites TEXT, -- JSON array of prerequisite patches
    dependencies TEXT, -- JSON array of required packages
    conflicts TEXT, -- JSON array of conflicting packages
    
    -- Maturity tracking
    installations_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    rollback_count INTEGER DEFAULT 0,
    success_rate REAL,
    
    -- Metadata
    severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patches_cve ON patches(cve_id);
CREATE INDEX idx_patches_vendor ON patches(vendor);
CREATE INDEX idx_patches_os_type ON patches(os_type);
CREATE INDEX idx_patches_release_date ON patches(release_date DESC);
CREATE INDEX idx_patches_success_rate ON patches(success_rate DESC);

-- ============================================================================
-- REMEDIATION AUDIT LOG (Blockchain-backed)
-- Immutable audit trail of all remediation activities
-- ============================================================================

CREATE TABLE IF NOT EXISTS remediation_audit_log (
    log_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    
    -- Event information
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL, -- PLANNED, STARTED, SNAPSHOT_CREATED, SANDBOX_TESTED, DEPLOYED, MONITORED, SUCCESS, FAILED, ROLLED_BACK
    event_category TEXT NOT NULL CHECK(event_category IN ('PLANNING', 'EXECUTION', 'TESTING', 'DEPLOYMENT', 'MONITORING', 'ROLLBACK', 'COMPLETION')),
    
    -- Actor information
    actor TEXT NOT NULL, -- SYSTEM, USER_<user_id>, ARIA, ML_MODEL
    actor_type TEXT NOT NULL CHECK(actor_type IN ('SYSTEM', 'HUMAN', 'AI', 'ML_MODEL')),
    
    -- Event details
    action TEXT NOT NULL,
    details TEXT, -- JSON blob with event-specific details
    prev_status TEXT,
    new_status TEXT,
    
    -- Blockchain proof (for compliance and immutability)
    blockchain_hash TEXT, -- Hash of this record stored on blockchain
    blockchain_block INTEGER,
    blockchain_confirmed BOOLEAN DEFAULT 0,
    blockchain_confirmation_time TIMESTAMP,
    blockchain_network TEXT, -- ethereum, hyperledger, etc.
    
    -- Metadata
    correlation_id TEXT, -- Links related events together
    severity TEXT CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    
    FOREIGN KEY (execution_id) REFERENCES remediation_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_audit_execution ON remediation_audit_log(execution_id);
CREATE INDEX idx_audit_timestamp ON remediation_audit_log(timestamp DESC);
CREATE INDEX idx_audit_event_type ON remediation_audit_log(event_type);
CREATE INDEX idx_audit_actor ON remediation_audit_log(actor);
CREATE INDEX idx_audit_correlation ON remediation_audit_log(correlation_id);

-- ============================================================================
-- AUTONOMOUS DECISIONS
-- Tracks AI/ML decision-making for auditing and improvement
-- ============================================================================

CREATE TABLE IF NOT EXISTS autonomous_decisions (
    decision_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    
    -- Decision metadata
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decision_type TEXT NOT NULL CHECK(decision_type IN ('AUTONOMY_LEVEL', 'DEPLOY_STRATEGY', 'REMEDIATE', 'ROLLBACK', 'ESCALATE', 'RETRY', 'CANCEL')),
    decision_outcome TEXT NOT NULL,
    
    -- Model information
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    confidence REAL NOT NULL CHECK(confidence BETWEEN 0.0 AND 1.0),
    
    -- Decision factors
    input_features TEXT NOT NULL, -- JSON blob with all input features
    model_output TEXT NOT NULL, -- JSON blob with raw model output
    reasoning TEXT NOT NULL, -- Human-readable explanation
    alternative_options TEXT, -- JSON array of other options considered
    
    -- Outcome tracking
    decision_correct BOOLEAN, -- Was the decision correct in hindsight?
    actual_outcome TEXT, -- What actually happened
    feedback_score REAL CHECK(feedback_score BETWEEN 0.0 AND 1.0), -- Quality of decision (0=bad, 1=excellent)
    
    -- Human oversight
    human_reviewed BOOLEAN DEFAULT 0,
    human_decision TEXT CHECK(human_decision IN ('APPROVED', 'REJECTED', 'MODIFIED')),
    human_feedback TEXT,
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    
    -- Learning
    used_for_training BOOLEAN DEFAULT 0,
    training_label TEXT, -- Correct label for ML training
    
    FOREIGN KEY (execution_id) REFERENCES remediation_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_decisions_execution ON autonomous_decisions(execution_id);
CREATE INDEX idx_decisions_timestamp ON autonomous_decisions(timestamp DESC);
CREATE INDEX idx_decisions_type ON autonomous_decisions(decision_type);
CREATE INDEX idx_decisions_confidence ON autonomous_decisions(confidence);
CREATE INDEX idx_decisions_correct ON autonomous_decisions(decision_correct);

-- ============================================================================
-- REMEDIATION METRICS (Aggregated statistics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS remediation_metrics (
    metric_id TEXT PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_hour INTEGER CHECK(metric_hour BETWEEN 0 AND 23),
    
    -- Volume metrics
    plans_created INTEGER DEFAULT 0,
    executions_started INTEGER DEFAULT 0,
    executions_completed INTEGER DEFAULT 0,
    
    -- Success metrics
    successes INTEGER DEFAULT 0,
    failures INTEGER DEFAULT 0,
    rollbacks INTEGER DEFAULT 0,
    timeouts INTEGER DEFAULT 0,
    
    -- Autonomy metrics
    level_0_count INTEGER DEFAULT 0,
    level_1_count INTEGER DEFAULT 0,
    level_2_count INTEGER DEFAULT 0,
    level_3_count INTEGER DEFAULT 0,
    level_4_count INTEGER DEFAULT 0,
    level_5_count INTEGER DEFAULT 0,
    
    -- Timing metrics (in seconds)
    avg_total_duration REAL,
    avg_sandbox_duration REAL,
    avg_deployment_duration REAL,
    min_duration INTEGER,
    max_duration INTEGER,
    
    -- Quality metrics
    avg_test_pass_rate REAL,
    avg_confidence REAL,
    human_override_count INTEGER DEFAULT 0,
    
    -- Business metrics
    labor_hours_saved REAL,
    estimated_breach_prevention_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(metric_date, metric_hour)
);

CREATE INDEX idx_metrics_date ON remediation_metrics(metric_date DESC);

-- ============================================================================
-- DEPLOYMENT STAGES (For canary and rolling deployments)
-- ============================================================================

CREATE TABLE IF NOT EXISTS deployment_stages (
    stage_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    
    -- Stage information
    stage_number INTEGER NOT NULL,
    stage_name TEXT NOT NULL, -- canary-5, canary-25, canary-50, full-deployment
    traffic_percentage INTEGER NOT NULL CHECK(traffic_percentage BETWEEN 0 AND 100),
    
    -- Assets in this stage
    assets_count INTEGER NOT NULL,
    assets_json TEXT, -- JSON array of asset IDs in this stage
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration INTEGER,
    
    -- Status
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED')),
    
    -- Health metrics
    error_rate REAL,
    response_time_ms REAL,
    success_rate REAL,
    health_check_passed BOOLEAN,
    
    -- Decision
    proceed_to_next_stage BOOLEAN,
    abort_reason TEXT,
    
    FOREIGN KEY (execution_id) REFERENCES remediation_executions(execution_id) ON DELETE CASCADE
);

CREATE INDEX idx_stages_execution ON deployment_stages(execution_id);
CREATE INDEX idx_stages_number ON deployment_stages(execution_id, stage_number);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Active remediations view
CREATE VIEW IF NOT EXISTS v_active_remediations AS
SELECT 
    rp.plan_id,
    rp.cve_id,
    rp.asset_name,
    rp.autonomy_level,
    rp.status AS plan_status,
    re.execution_id,
    re.status AS execution_status,
    re.started_at,
    CAST((julianday('now') - julianday(re.started_at)) * 24 * 60 AS INTEGER) AS elapsed_minutes,
    re.sandbox_passed,
    re.rollback_performed
FROM remediation_plans rp
JOIN remediation_executions re ON rp.plan_id = re.plan_id
WHERE re.status IN ('QUEUED', 'RUNNING')
ORDER BY re.started_at DESC;

-- Daily statistics view
CREATE VIEW IF NOT EXISTS v_daily_remediation_stats AS
SELECT 
    DATE(started_at) AS remediation_date,
    COUNT(*) AS total_executions,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS successes,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failures,
    SUM(CASE WHEN rollback_performed = 1 THEN 1 ELSE 0 END) AS rollbacks,
    ROUND(AVG(total_duration) / 60.0, 2) AS avg_duration_minutes,
    ROUND(AVG(test_pass_rate) * 100, 2) AS avg_test_pass_rate_pct
FROM remediation_executions
WHERE started_at IS NOT NULL
GROUP BY DATE(started_at)
ORDER BY remediation_date DESC;

-- Autonomy level distribution view
CREATE VIEW IF NOT EXISTS v_autonomy_distribution AS
SELECT 
    ra.autonomy_level,
    COUNT(*) AS assessment_count,
    ROUND(AVG(ra.confidence) * 100, 2) AS avg_confidence_pct,
    SUM(CASE WHEN ra.human_override = 1 THEN 1 ELSE 0 END) AS override_count,
    ROUND(AVG(ra.total_risk_score), 3) AS avg_risk_score
FROM risk_assessments ra
GROUP BY ra.autonomy_level
ORDER BY ra.autonomy_level DESC;

-- Patch success rates view
CREATE VIEW IF NOT EXISTS v_patch_success_rates AS
SELECT 
    p.patch_id,
    p.cve_id,
    p.vendor,
    p.patch_version,
    p.installations_count,
    p.success_count,
    p.failure_count,
    p.rollback_count,
    ROUND(CAST(p.success_count AS REAL) / NULLIF(p.installations_count, 0) * 100, 2) AS success_rate_pct,
    ROUND((julianday('now') - julianday(p.release_date)), 0) AS patch_age_days
FROM patches p
WHERE p.installations_count > 0
ORDER BY p.success_rate_pct DESC, p.installations_count DESC;

-- ============================================================================
-- TRIGGERS FOR AUTOMATION
-- ============================================================================

-- Auto-update patch statistics when execution completes
CREATE TRIGGER IF NOT EXISTS update_patch_stats_on_success
AFTER UPDATE OF status ON remediation_executions
WHEN NEW.status = 'SUCCESS' AND OLD.status != 'SUCCESS'
BEGIN
    UPDATE patches 
    SET 
        installations_count = installations_count + 1,
        success_count = success_count + 1,
        success_rate = CAST(success_count + 1 AS REAL) / CAST(installations_count + 1 AS REAL),
        updated_at = CURRENT_TIMESTAMP
    WHERE patch_id = (
        SELECT patch_id FROM remediation_plans WHERE plan_id = NEW.plan_id
    );
END;

-- Auto-update patch statistics on failure
CREATE TRIGGER IF NOT EXISTS update_patch_stats_on_failure
AFTER UPDATE OF status ON remediation_executions
WHEN NEW.status = 'FAILED' AND OLD.status != 'FAILED'
BEGIN
    UPDATE patches 
    SET 
        installations_count = installations_count + 1,
        failure_count = failure_count + 1,
        success_rate = CAST(success_count AS REAL) / CAST(installations_count + 1 AS REAL),
        updated_at = CURRENT_TIMESTAMP
    WHERE patch_id = (
        SELECT patch_id FROM remediation_plans WHERE plan_id = NEW.plan_id
    );
END;

-- Auto-update patch statistics on rollback
CREATE TRIGGER IF NOT EXISTS update_patch_stats_on_rollback
AFTER UPDATE OF rollback_performed ON remediation_executions
WHEN NEW.rollback_performed = 1 AND OLD.rollback_performed = 0
BEGIN
    UPDATE patches 
    SET 
        rollback_count = rollback_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE patch_id = (
        SELECT patch_id FROM remediation_plans WHERE plan_id = NEW.plan_id
    );
END;

-- Auto-expire old snapshots (optimized to only check related execution)
CREATE TRIGGER IF NOT EXISTS expire_old_snapshots
AFTER INSERT ON system_snapshots
BEGIN
    UPDATE system_snapshots
    SET status = 'EXPIRED'
    WHERE status = 'READY' 
    AND datetime(expires_at) < datetime('now')
    AND execution_id = NEW.execution_id
    AND snapshot_id != NEW.snapshot_id;
END;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default patch sources
INSERT OR IGNORE INTO patches (patch_id, cve_id, vendor, product, patch_version, os_type, verified)
VALUES 
    ('PATCH-DEFAULT-001', 'CVE-0000-0000', 'SYSTEM', 'DEFAULT', '1.0.0', 'linux', 1);

-- ============================================================================
-- DATABASE METADATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) 
VALUES ('1.0.0', 'Initial schema for Module G.1 Autonomous Remediation Engine');

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_plans_status_priority ON remediation_plans(status, priority DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_status_started ON remediation_executions(status, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_execution_timestamp ON remediation_audit_log(execution_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_execution_type ON autonomous_decisions(execution_id, decision_type);

-- Additional optimized indexes
CREATE INDEX IF NOT EXISTS idx_plans_requires_approval 
ON remediation_plans(requires_approval, status) 
WHERE requires_approval = 1 AND status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_snapshots_cleanup
ON system_snapshots(status, expires_at)
WHERE status = 'READY';

CREATE INDEX IF NOT EXISTS idx_audit_actor_timestamp
ON remediation_audit_log(actor_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_executions_completed_date
ON remediation_executions(DATE(completed_at))
WHERE status IN ('SUCCESS', 'FAILED');

-- ============================================================================
-- SCHEMA COMPLETE
-- ============================================================================

-- Total tables: 10
-- Total views: 4  
-- Total triggers: 4
-- Total indexes: 39+
-- Version: 1.0.1 (Optimized)
