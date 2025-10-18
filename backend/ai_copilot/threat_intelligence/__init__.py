"""
Threat Intelligence Module for Enterprise Scanner
=================================================

Module G.2: Advanced Threat Intelligence Engine

This module provides comprehensive threat intelligence aggregation, analysis,
and distribution capabilities for Fortune 500 enterprises.

Components:
- G.2.1: Multi-Source Intelligence Aggregator (25+ feeds)
- G.2.2: Threat Actor Profiling Engine (100+ APT groups)
- G.2.3: Vulnerability Intelligence Collector (CVE tracking)
- G.2.4: Industry-Specific Intel Gathering
- G.2.5: Threat Correlation Engine
- G.2.6: Predictive Threat Analyzer
- G.2.7: Risk Contextualization Engine
- G.2.8: False Positive Reduction
- G.2.9: Threat Intelligence Feed API
- G.2.10: Executive Threat Briefings
- G.2.11: ARIA Dashboard Integration
- G.2.12: Remediation Engine Integration

Version: 1.0.0
Author: Enterprise Scanner AI Development Team
Created: October 17, 2025
"""

# Version information
__version__ = "1.0.0"
__author__ = "Enterprise Scanner AI Development Team"
__module__ = "G.2: Advanced Threat Intelligence Engine"

# Component exports

# G.2.1: Multi-Source Intelligence Aggregator
from .intelligence_aggregator import (
    MultiSourceIntelligenceAggregator,
    ThreatIntelSource,
    IndicatorOfCompromise,
    IngestionJob,
    SourceType,
    IoC_Type,
    ThreatLevel,
    IngestionStatus,
)

# G.2.2: Threat Actor Profiling Engine
from .actor_profiling import (
    ThreatActorProfilingEngine,
    ThreatActor,
    ThreatCampaign,
    TTP,
    ActorProfile,
    MITREAttackIntegration,
    Motivation,
    SophisticationLevel,
    CampaignStatus,
    AttackVectorType,
)

# G.2.3: Vulnerability Intelligence Collector
from .vulnerability_collector import (
    VulnerabilityIntelligenceCollector,
    Vulnerability,
    ExploitIntelligence,
    VulnerabilityTrend,
    Severity,
    ExploitAvailability,
    TrendingStatus,
)

# G.2.4: Industry-Specific Intelligence Gathering
from .industry_intel import (
    IndustryIntelligenceGatherer,
    IndustryThreat,
    RegulatoryAdvisory,
    IndustryCampaign,
    Industry,
    ComplianceFramework,
    ThreatSeverity,
)

# G.2.5: Threat Correlation Engine
from .correlation_engine import (
    ThreatCorrelationEngine,
    ThreatCorrelation,
    AttackChain,
    ThreatGraph,
    CorrelationType,
    ConfidenceLevel,
    KillChainPhase,
)

# G.2.6: Predictive Threat Analyzer
from .predictive_analyzer import (
    PredictiveThreatAnalyzer,
    ThreatPrediction,
    ThreatForecast,
    EmergingThreat,
    PredictionHorizon,
    ThreatTrend,
    PredictionConfidence,
)

# G.2.7: Risk Contextualization Engine
from .risk_contextualization import (
    RiskContextualizationEngine,
    Asset,
    AssetThreatExposure,
    RemediationRecommendation,
    AssetCriticality,
    BusinessImpact,
    RemediationUrgency
)

# G.2.8: False Positive Reduction
from .false_positive_reducer import (
    FalsePositiveReducer,
    AlertQualityScore,
    WhitelistEntry,
    FeedbackRecord,
    AccuracyMetrics,
    AlertConfidence,
    AlertQuality,
    FilterAction,
    FeedbackType
)

# G.2.9: Threat Intelligence Feed API
from .feed_api import (
    ThreatIntelligenceFeedAPI,
    APIKey,
    FeedSubscription,
    WebhookDelivery,
    QueryFilter,
    APIKeyPermission,
    FeedType,
    DeliveryMethod,
    RateLimitTier
)

# G.2.10: Executive Threat Briefings
from .executive_briefings import (
    ExecutiveBriefingEngine,
    ExecutiveSummary,
    ThreatTrendAnalysis,
    RiskDashboardMetrics,
    ComplianceReport,
    StakeholderAlert,
    ExecutiveBriefing,
    BriefingFrequency,
    BriefingAudience,
    ReportFormat,
    ThreatLevel
)

# G.2.11: ARIA Dashboard Integration
from .aria_dashboard import (
    ARIADashboardIntegration,
    DashboardWidget,
    ChartData,
    ThreatFeedItem,
    AlertNotification,
    WidgetType,
    ChartType,
    UpdateFrequency,
    AlertPriority
)

# G.2.12: Remediation Engine Integration
from .remediation_integration import (
    RemediationEngineIntegration,
    ThreatRemediationMapping,
    RemediationTask,
    RemediationFeedback,
    CrossSystemOrchestration,
    RemediationTrigger,
    RemediationAction,
    IntegrationStatus
)

# Public API
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__module__',
    
    # G.2.1: Intelligence Aggregator
    'MultiSourceIntelligenceAggregator',
    'ThreatIntelSource',
    'IndicatorOfCompromise',
    'IngestionJob',
    'SourceType',
    'IoC_Type',
    'ThreatLevel',
    'IngestionStatus',
    
    # G.2.2: Threat Actor Profiling
    'ThreatActorProfilingEngine',
    'ThreatActor',
    'ThreatCampaign',
    'TTP',
    'ActorProfile',
    'MITREAttackIntegration',
    'Motivation',
    'SophisticationLevel',
    'CampaignStatus',
    'AttackVectorType',
    
    # G.2.3: Vulnerability Intelligence
    'VulnerabilityIntelligenceCollector',
    'Vulnerability',
    'ExploitIntelligence',
    'VulnerabilityTrend',
    'Severity',
    'ExploitAvailability',
    'TrendingStatus',
    
    # G.2.4: Industry-Specific Intelligence
    'IndustryIntelligenceGatherer',
    'IndustryThreat',
    'RegulatoryAdvisory',
    'IndustryCampaign',
    'Industry',
    'ComplianceFramework',
    'ThreatSeverity',
    
    # G.2.5: Threat Correlation
    'ThreatCorrelationEngine',
    'ThreatCorrelation',
    'AttackChain',
    'ThreatGraph',
    'CorrelationType',
    'ConfidenceLevel',
    'KillChainPhase',
    
    # G.2.6: Predictive Analysis
    'PredictiveThreatAnalyzer',
    'ThreatPrediction',
    'ThreatForecast',
    'EmergingThreat',
    'PredictionHorizon',
    'ThreatTrend',
    'PredictionConfidence',
    
    # G.2.7: Risk Contextualization
    'RiskContextualizationEngine',
    'Asset',
    'AssetThreatExposure',
    'RemediationRecommendation',
    'AssetCriticality',
    'BusinessImpact',
    'RemediationUrgency',
    
    # G.2.8: False Positive Reduction
    'FalsePositiveReducer',
    'AlertQualityScore',
    'WhitelistEntry',
    'FeedbackRecord',
    'AccuracyMetrics',
    'AlertConfidence',
    'AlertQuality',
    'FilterAction',
    'FeedbackType',
    
    # G.2.9: Threat Intelligence Feed API
    'ThreatIntelligenceFeedAPI',
    'APIKey',
    'FeedSubscription',
    'WebhookDelivery',
    'QueryFilter',
    'APIKeyPermission',
    'FeedType',
    'DeliveryMethod',
    'RateLimitTier',
    
    # G.2.10: Executive Threat Briefings
    'ExecutiveBriefingEngine',
    'ExecutiveSummary',
    'ThreatTrendAnalysis',
    'RiskDashboardMetrics',
    'ComplianceReport',
    'StakeholderAlert',
    'ExecutiveBriefing',
    'BriefingFrequency',
    'BriefingAudience',
    'ReportFormat',
    'ThreatLevel',
    
    # G.2.11: ARIA Dashboard Integration
    'ARIADashboardIntegration',
    'DashboardWidget',
    'ChartData',
    'ThreatFeedItem',
    'AlertNotification',
    'WidgetType',
    'ChartType',
    'UpdateFrequency',
    'AlertPriority',
    
    # G.2.12: Remediation Engine Integration
    'RemediationEngineIntegration',
    'ThreatRemediationMapping',
    'RemediationTask',
    'RemediationFeedback',
    'CrossSystemOrchestration',
    'RemediationTrigger',
    'RemediationAction',
    'IntegrationStatus',
]
