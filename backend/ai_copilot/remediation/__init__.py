"""
Jupiter v3.0 - Module G.1: Autonomous Remediation Engine
Enterprise-grade vulnerability remediation with AI-powered autonomy

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

__version__ = "1.0.0"
__author__ = "Jupiter Engineering Team"
__email__ = "security@enterprisescanner.com"

# Public API exports
from .risk_analyzer import (
    RiskAnalyzer,
    RiskAssessment,
    RiskFactors,
    AutonomyLevel
)

from .config import (
    RemediationConfig,
    get_config,
    set_config,
    reset_config
)

from .exceptions import (
    RemediationError,
    RemediationDatabaseError,
    ValidationError,
    ConfigurationError,
    ExecutionError,
    RollbackError,
    PatchError,
    SandboxError,
    AutonomyError,
    DeploymentError,
    MLModelError,
    BlockchainError,
    TimeoutError,
    DependencyError,
    PermissionError,
    VerificationError
)

from .patch_engine import (
    PatchEngine,
    PatchMetadata,
    PatchSource,
    PatchStatus,
    VendorPatchRepository,
    OSPackageManager,
    ContainerRegistryClient,
    PatchVerifier
)

from .sandbox_tester import (
    SandboxTester,
    SandboxEnvironment,
    SandboxType,
    TestSuite,
    TestCase,
    TestType,
    TestResult,
    TestRunner,
    KubernetesSandbox,
    DockerSandbox,
    VMSandbox
)

from .rollback_manager import (
    RollbackManager,
    Snapshot,
    SnapshotStatus,
    SnapshotType as RollbackSnapshotType,
    KubernetesRollback,
    DockerRollback,
    VMRollback,
    HealthChecker
)

from .deployment_orchestrator import (
    DeploymentOrchestrator,
    DeploymentPlan,
    DeploymentStage,
    DeploymentStrategy,
    StageStatus,
    CanaryDeployer,
    BlueGreenDeployer,
    RollingUpdateDeployer,
    HealthValidator
)

from .remediation_engine import (
    RemediationEngine,
    RemediationExecution,
    ExecutionState,
    RemediationPriority,
    WorkflowDecision,
    StateTransitionManager,
    DecisionEngine,
    AuditLogger
)
from .ml_model_training import (
    TrainingData,
    Pattern,
    RiskCalibration,
    StrategyRecommendation,
    AnomalyReport,
    SuccessPrediction,
    MLModelType,
    HistoricalDataCollector,
    PatternRecognizer,
    RiskScoreOptimizer,
    StrategyRecommender,
    AnomalyDetector,
    PredictiveAnalyzer
)
from .aria_integration import (
    ExecutionUpdate,
    ApprovalRequest,
    ApprovalResponse,
    ExecutionReport,
    DashboardMetrics,
    Notification,
    NotificationType,
    ARIAConnector,
    ExecutionMonitor,
    ApprovalWorkflow,
    ReportGenerator,
    NotificationSender
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    
    # Risk Analysis
    'RiskAnalyzer',
    'RiskAssessment',
    'RiskFactors',
    'AutonomyLevel',
    
    # Configuration
    'RemediationConfig',
    'get_config',
    'set_config',
    'reset_config',
    
    # Exceptions
    'RemediationError',
    'RemediationDatabaseError',
    'ValidationError',
    'ConfigurationError',
    'ExecutionError',
    'RollbackError',
    'PatchError',
    'SandboxError',
    'AutonomyError',
    'DeploymentError',
    'MLModelError',
    'BlockchainError',
    'TimeoutError',
    'DependencyError',
    'PermissionError',
    'VerificationError',
    
    # Patch Management
    'PatchEngine',
    'PatchMetadata',
    'PatchSource',
    'PatchStatus',
    'VendorPatchRepository',
    'OSPackageManager',
    'ContainerRegistryClient',
    'PatchVerifier',
    
    # Sandbox Testing
    'SandboxTester',
    'SandboxEnvironment',
    'SandboxType',
    'TestSuite',
    'TestCase',
    'TestType',
    'TestResult',
    'TestRunner',
    'KubernetesSandbox',
    'DockerSandbox',
    'VMSandbox',
    
    # Rollback Management
    'RollbackManager',
    'Snapshot',
    'SnapshotStatus',
    'RollbackSnapshotType',
    'KubernetesRollback',
    'DockerRollback',
    'VMRollback',
    'HealthChecker',
    
    # Deployment Orchestration
    'DeploymentOrchestrator',
    'DeploymentPlan',
    'DeploymentStage',
    'DeploymentStrategy',
    'StageStatus',
    'CanaryDeployer',
    'BlueGreenDeployer',
    'RollingUpdateDeployer',
    'HealthValidator',
    
    # Main Remediation Engine
    'RemediationEngine',
    'RemediationExecution',
    'ExecutionState',
    'RemediationPriority',
    'WorkflowDecision',
    'StateTransitionManager',
    'DecisionEngine',
    'AuditLogger',
    # ML Model Training
    'TrainingData',
    'Pattern',
    'RiskCalibration',
    'StrategyRecommendation',
    'AnomalyReport',
    'SuccessPrediction',
    'MLModelType',
    'HistoricalDataCollector',
    'PatternRecognizer',
    'RiskScoreOptimizer',
    'StrategyRecommender',
    'AnomalyDetector',
    'PredictiveAnalyzer',
    # ARIA Integration
    'ExecutionUpdate',
    'ApprovalRequest',
    'ApprovalResponse',
    'ExecutionReport',
    'DashboardMetrics',
    'Notification',
    'NotificationType',
    'ARIAConnector',
    'ExecutionMonitor',
    'ApprovalWorkflow',
    'ReportGenerator',
    'NotificationSender'
]


def get_version() -> str:
    """Get package version"""
    return __version__


def get_info() -> dict:
    """Get package information"""
    return {
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'description': 'AI-powered autonomous vulnerability remediation engine'
    }


# Module-level initialization
def _initialize():
    """Initialize module on import"""
    import logging
    
    # Set up null handler to prevent "No handler found" warnings
    logging.getLogger(__name__).addHandler(logging.NullHandler())


_initialize()
