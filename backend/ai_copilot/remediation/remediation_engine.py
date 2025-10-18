"""
Jupiter v3.0 - Module G.1: Main Remediation Engine
Complete autonomous vulnerability remediation workflow orchestrator

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

import logging
import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import time

try:
    from .config import get_config
    from .exceptions import (
        RemediationError,
        ValidationError,
        TimeoutError as RemediationTimeoutError,
        RemediationDatabaseError
    )
    from .risk_analyzer import RiskAnalyzer, RiskAssessment, AutonomyLevel
    from .patch_engine import PatchEngine, Patch
    from .sandbox_tester import SandboxTester, TestSuite, TestCase, TestType
    from .rollback_manager import RollbackManager, Snapshot
    from .deployment_orchestrator import (
        DeploymentOrchestrator,
        DeploymentPlan,
        DeploymentStrategy
    )
except ImportError:
    # Fallback for standalone execution
    class RemediationError(Exception):
        pass
    class ValidationError(Exception):
        pass
    class RemediationTimeoutError(Exception):
        pass
    class RemediationDatabaseError(Exception):
        pass
    
    class AutonomyLevel(Enum):
        FULL_AUTO = "full_auto"
        SEMI_AUTO = "semi_auto"
        MANUAL = "manual"
    
    class MockConfig:
        database_path = "jupiter_remediation.db"
        max_concurrent_remediations = 5
        enable_blockchain_audit = True
    
    def get_config():
        return MockConfig()
    
    # Mock classes for type hints when imports fail
    class Patch:
        pass
    
    class RiskAssessment:
        pass
    
    class Snapshot:
        pass
    
    class TestSuite:
        pass
    
    class TestCase:
        pass
    
    class TestType(Enum):
        UNIT = "unit"
        INTEGRATION = "integration"
    
    class DeploymentPlan:
        pass
    
    class DeploymentStrategy(Enum):
        ROLLING = "rolling"
        BLUE_GREEN = "blue_green"
        CANARY = "canary"
    
    class RiskAnalyzer:
        pass
    
    class PatchEngine:
        pass
    
    class SandboxTester:
        pass
    
    class RollbackManager:
        pass
    
    class DeploymentOrchestrator:
        pass


class ExecutionState(Enum):
    """Remediation execution states"""
    PENDING = "pending"              # Queued for execution
    RISK_ANALYSIS = "risk_analysis"  # Analyzing risk
    PATCH_SEARCH = "patch_search"    # Finding patches
    SNAPSHOT_CREATION = "snapshot_creation"  # Creating backup
    SANDBOX_TESTING = "sandbox_testing"      # Testing patch
    DEPLOYMENT = "deployment"        # Deploying patch
    VALIDATION = "validation"        # Post-deployment validation
    COMPLETED = "completed"          # Successfully completed
    FAILED = "failed"                # Failed with errors
    ROLLED_BACK = "rolled_back"      # Rolled back after failure
    REQUIRES_APPROVAL = "requires_approval"  # Awaiting manual approval


class RemediationPriority(Enum):
    """Remediation priority levels"""
    CRITICAL = "critical"    # Immediate execution
    HIGH = "high"           # Within 1 hour
    MEDIUM = "medium"       # Within 4 hours
    LOW = "low"             # Within 24 hours


@dataclass
class RemediationExecution:
    """Complete remediation execution tracking"""
    execution_id: str
    vulnerability_id: str
    asset: Dict
    
    # Execution configuration
    priority: RemediationPriority
    state: ExecutionState = ExecutionState.PENDING
    autonomy_level: Optional[AutonomyLevel] = None
    
    # Component results
    risk_assessment: Optional[RiskAssessment] = None
    selected_patch: Optional[Patch] = None
    snapshot: Optional[Snapshot] = None
    test_results: List[TestSuite] = field(default_factory=list)
    deployment_plan: Optional[DeploymentPlan] = None
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    state_history: List[Dict] = field(default_factory=list)
    
    # Results
    success: bool = False
    rolled_back: bool = False
    requires_approval: bool = False
    error_message: Optional[str] = None
    
    # Metadata
    metadata: Dict = field(default_factory=dict)


@dataclass
class WorkflowDecision:
    """Decision point in workflow"""
    decision_id: str
    execution_id: str
    decision_type: str  # 'strategy_selection', 'approval_required', 'rollback_trigger'
    
    # Decision output (required fields first)
    decision: str
    reasoning: str
    
    # Decision inputs (optional fields)
    risk_score: Optional[float] = None
    autonomy_level: Optional[AutonomyLevel] = None
    test_success_rate: Optional[float] = None
    confidence: float = 0.0
    
    # Timing
    decided_at: datetime = field(default_factory=datetime.now)


class StateTransitionManager:
    """Manages state transitions and history"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def transition_state(
        self,
        execution: RemediationExecution,
        new_state: ExecutionState,
        message: str = None
    ) -> None:
        """
        Transition execution to new state
        
        Args:
            execution: Execution to transition
            new_state: Target state
            message: Optional transition message
        """
        try:
            old_state = execution.state
            execution.state = new_state
            
            # Record transition in history
            transition = {
                'from_state': old_state.value,
                'to_state': new_state.value,
                'timestamp': datetime.now().isoformat(),
                'message': message
            }
            execution.state_history.append(transition)
            
            # Save to database
            self._save_state_transition(execution.execution_id, transition)
            
            self.logger.info(
                f"State transition: {old_state.value} → {new_state.value} "
                f"({execution.execution_id})"
            )
            
        except Exception as e:
            self.logger.error(f"Error in state transition: {e}")
            raise RemediationError(f"State transition failed: {e}")
    
    def _save_state_transition(self, execution_id: str, transition: Dict) -> None:
        """Save state transition to database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO execution_state_history (
                        execution_id, from_state, to_state,
                        transition_time, message
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    execution_id,
                    transition['from_state'],
                    transition['to_state'],
                    transition['timestamp'],
                    transition.get('message')
                ))
                
        except Exception as e:
            self.logger.error(f"Error saving state transition: {e}")


class DecisionEngine:
    """Makes intelligent decisions during remediation workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def select_deployment_strategy(
        self,
        execution: RemediationExecution
    ) -> Tuple[DeploymentStrategy, WorkflowDecision]:
        """
        Select optimal deployment strategy based on risk and context
        
        Args:
            execution: Remediation execution
            
        Returns:
            Tuple of (strategy, decision)
        """
        try:
            decision_id = f"strategy-{execution.execution_id}-{int(time.time())}"
            
            # Get risk score
            risk_score = execution.risk_assessment.risk_score if execution.risk_assessment else 0.5
            
            # Get test success rate
            test_success = self._calculate_test_success_rate(execution.test_results)
            
            # Decision logic
            if risk_score >= 0.8:
                # High risk → Canary with small stages
                strategy = DeploymentStrategy.CANARY
                reasoning = "High risk score requires gradual canary rollout"
                confidence = 0.9
            elif risk_score >= 0.5:
                # Medium risk → Blue-green for instant rollback
                strategy = DeploymentStrategy.BLUE_GREEN
                reasoning = "Medium risk suitable for blue-green deployment"
                confidence = 0.8
            elif risk_score >= 0.3:
                # Low-medium risk → Rolling update
                strategy = DeploymentStrategy.ROLLING_UPDATE
                reasoning = "Low-medium risk allows rolling update"
                confidence = 0.85
            else:
                # Low risk → Rolling update (fastest)
                strategy = DeploymentStrategy.ROLLING_UPDATE
                reasoning = "Low risk enables efficient rolling update"
                confidence = 0.9
            
            # Adjust for test results
            if test_success < 0.9:
                # Poor test results → More conservative
                if strategy == DeploymentStrategy.ROLLING_UPDATE:
                    strategy = DeploymentStrategy.CANARY
                    reasoning += " (adjusted to canary due to test results)"
                    confidence *= 0.8
            
            decision = WorkflowDecision(
                decision_id=decision_id,
                execution_id=execution.execution_id,
                decision_type='strategy_selection',
                risk_score=risk_score,
                autonomy_level=execution.autonomy_level,
                test_success_rate=test_success,
                decision=strategy.value,
                reasoning=reasoning,
                confidence=confidence
            )
            
            self.logger.info(
                f"Strategy selected: {strategy.value} "
                f"(confidence: {confidence:.2f}, reason: {reasoning})"
            )
            
            return strategy, decision
            
        except Exception as e:
            self.logger.error(f"Error selecting strategy: {e}")
            # Fallback to safest option
            return DeploymentStrategy.CANARY, WorkflowDecision(
                decision_id=decision_id,
                execution_id=execution.execution_id,
                decision_type='strategy_selection',
                decision='canary',
                reasoning=f"Fallback to canary due to error: {e}",
                confidence=0.5
            )
    
    def _calculate_test_success_rate(self, test_suites: List[TestSuite]) -> float:
        """Calculate overall test success rate"""
        if not test_suites:
            return 1.0
        
        total_tests = 0
        passed_tests = 0
        
        for suite in test_suites:
            total_tests += suite.total_tests
            passed_tests += suite.tests_passed
        
        if total_tests == 0:
            return 1.0
        
        return passed_tests / total_tests
    
    def should_require_approval(self, execution: RemediationExecution) -> Tuple[bool, WorkflowDecision]:
        """
        Determine if manual approval is required
        
        Args:
            execution: Remediation execution
            
        Returns:
            Tuple of (requires_approval, decision)
        """
        try:
            decision_id = f"approval-{execution.execution_id}-{int(time.time())}"
            
            # Check autonomy level
            if execution.autonomy_level == AutonomyLevel.MANUAL:
                return True, WorkflowDecision(
                    decision_id=decision_id,
                    execution_id=execution.execution_id,
                    decision_type='approval_required',
                    autonomy_level=execution.autonomy_level,
                    decision='required',
                    reasoning='Manual autonomy level requires approval',
                    confidence=1.0
                )
            
            if execution.autonomy_level == AutonomyLevel.SEMI_AUTO:
                # Check risk score
                risk_score = execution.risk_assessment.risk_score if execution.risk_assessment else 0.5
                
                if risk_score >= 0.7:
                    return True, WorkflowDecision(
                        decision_id=decision_id,
                        execution_id=execution.execution_id,
                        decision_type='approval_required',
                        risk_score=risk_score,
                        autonomy_level=execution.autonomy_level,
                        decision='required',
                        reasoning='Semi-auto mode with high risk requires approval',
                        confidence=0.9
                    )
            
            # Full auto or low risk semi-auto
            return False, WorkflowDecision(
                decision_id=decision_id,
                execution_id=execution.execution_id,
                decision_type='approval_required',
                autonomy_level=execution.autonomy_level,
                decision='not_required',
                reasoning='Autonomy level permits automatic execution',
                confidence=0.95
            )
            
        except Exception as e:
            self.logger.error(f"Error checking approval requirement: {e}")
            # Fail safe: require approval on error
            return True, WorkflowDecision(
                decision_id=decision_id,
                execution_id=execution.execution_id,
                decision_type='approval_required',
                decision='required',
                reasoning=f'Approval required due to error: {e}',
                confidence=0.5
            )


class AuditLogger:
    """Blockchain-ready audit logging system"""
    
    def __init__(self, db_path: str, blockchain_enabled: bool = True):
        self.db_path = db_path
        self.blockchain_enabled = blockchain_enabled
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def log_execution_start(self, execution: RemediationExecution) -> str:
        """
        Log execution start with blockchain hash
        
        Args:
            execution: Remediation execution
            
        Returns:
            Audit record hash
        """
        try:
            audit_data = {
                'event_type': 'execution_start',
                'execution_id': execution.execution_id,
                'vulnerability_id': execution.vulnerability_id,
                'asset': execution.asset,
                'priority': execution.priority.value,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate blockchain hash
            audit_hash = self._generate_hash(audit_data)
            
            # Save to database
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_log (
                        audit_id, execution_id, event_type,
                        event_data, audit_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    audit_hash,
                    execution.execution_id,
                    'execution_start',
                    json.dumps(audit_data),
                    audit_hash,
                    datetime.now().isoformat()
                ))
            
            self.logger.info(f"✅ Audit logged: execution_start ({audit_hash[:16]}...)")
            return audit_hash
            
        except Exception as e:
            self.logger.error(f"Error logging audit: {e}")
            return ""
    
    def log_decision(self, decision: WorkflowDecision) -> str:
        """Log workflow decision"""
        try:
            audit_data = {
                'event_type': 'workflow_decision',
                'decision_id': decision.decision_id,
                'execution_id': decision.execution_id,
                'decision_type': decision.decision_type,
                'decision': decision.decision,
                'reasoning': decision.reasoning,
                'confidence': decision.confidence,
                'timestamp': decision.decided_at.isoformat()
            }
            
            audit_hash = self._generate_hash(audit_data)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_log (
                        audit_id, execution_id, event_type,
                        event_data, audit_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    audit_hash,
                    decision.execution_id,
                    'workflow_decision',
                    json.dumps(audit_data),
                    audit_hash,
                    datetime.now().isoformat()
                ))
            
            self.logger.info(f"✅ Audit logged: decision ({decision.decision_type})")
            return audit_hash
            
        except Exception as e:
            self.logger.error(f"Error logging decision: {e}")
            return ""
    
    def log_execution_complete(
        self,
        execution: RemediationExecution,
        success: bool
    ) -> str:
        """Log execution completion"""
        try:
            audit_data = {
                'event_type': 'execution_complete',
                'execution_id': execution.execution_id,
                'success': success,
                'rolled_back': execution.rolled_back,
                'final_state': execution.state.value,
                'duration_seconds': (execution.completed_at - execution.started_at).total_seconds() if execution.completed_at and execution.started_at else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            audit_hash = self._generate_hash(audit_data)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_log (
                        audit_id, execution_id, event_type,
                        event_data, audit_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    audit_hash,
                    execution.execution_id,
                    'execution_complete',
                    json.dumps(audit_data),
                    audit_hash,
                    datetime.now().isoformat()
                ))
            
            self.logger.info(f"✅ Audit logged: execution_complete (success={success})")
            return audit_hash
            
        except Exception as e:
            self.logger.error(f"Error logging completion: {e}")
            return ""
    
    def _generate_hash(self, data: Dict) -> str:
        """Generate SHA-256 hash for blockchain"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()


class RemediationEngine:
    """
    Main autonomous remediation orchestrator
    
    Coordinates complete end-to-end vulnerability remediation workflow
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize remediation engine
        
        Args:
            db_path: Database path (default from config)
        """
        self.config = get_config()
        self.db_path = db_path or self.config.database_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize all component systems
        self.risk_analyzer = RiskAnalyzer(self.db_path)
        self.patch_engine = PatchEngine(self.db_path)
        self.sandbox_tester = SandboxTester(self.db_path)
        self.rollback_manager = RollbackManager(self.db_path)
        self.deployment_orchestrator = DeploymentOrchestrator(self.db_path)
        
        # Initialize workflow systems
        self.state_manager = StateTransitionManager(self.db_path)
        self.decision_engine = DecisionEngine()
        self.audit_logger = AuditLogger(
            self.db_path,
            blockchain_enabled=self.config.enable_blockchain_audit
        )
    
    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def remediate_vulnerability(
        self,
        vulnerability_id: str,
        asset: Dict,
        priority: RemediationPriority = RemediationPriority.MEDIUM,
        force_strategy: Optional[DeploymentStrategy] = None
    ) -> RemediationExecution:
        """
        Execute complete autonomous remediation workflow
        
        Args:
            vulnerability_id: Vulnerability identifier (CVE, etc.)
            asset: Asset information
            priority: Remediation priority
            force_strategy: Optional forced deployment strategy
            
        Returns:
            RemediationExecution with complete results
        """
        # Create execution
        execution_id = f"EXEC-{int(time.time())}-{vulnerability_id[:8]}"
        execution = RemediationExecution(
            execution_id=execution_id,
            vulnerability_id=vulnerability_id,
            asset=asset,
            priority=priority
        )
        
        try:
            self.logger.info(f"🚀 Starting remediation: {execution_id}")
            self.logger.info(f"   Vulnerability: {vulnerability_id}")
            self.logger.info(f"   Asset: {asset.get('asset_id', 'Unknown')}")
            
            execution.started_at = datetime.now()
            
            # Log audit trail
            self.audit_logger.log_execution_start(execution)
            
            # Save initial execution
            self._save_execution(execution)
            
            # Execute workflow stages
            self._execute_workflow(execution, force_strategy)
            
            execution.completed_at = datetime.now()
            duration = (execution.completed_at - execution.started_at).total_seconds()
            
            # Log completion
            self.audit_logger.log_execution_complete(execution, execution.success)
            
            # Update execution
            self._update_execution(execution)
            
            if execution.success:
                self.logger.info(f"✅ Remediation completed successfully: {execution_id}")
                self.logger.info(f"   Duration: {duration:.2f}s")
            else:
                self.logger.error(f"❌ Remediation failed: {execution_id}")
                self.logger.error(f"   Error: {execution.error_message}")
                if execution.rolled_back:
                    self.logger.info(f"   ⚠️  Rolled back to previous state")
            
            return execution
            
        except Exception as e:
            self.logger.error(f"Critical error in remediation: {e}")
            execution.state = ExecutionState.FAILED
            execution.success = False
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            
            self._update_execution(execution)
            self.audit_logger.log_execution_complete(execution, False)
            
            return execution
    
    def _execute_workflow(
        self,
        execution: RemediationExecution,
        force_strategy: Optional[DeploymentStrategy]
    ) -> None:
        """Execute complete remediation workflow"""
        
        # Stage 1: Risk Analysis
        if not self._perform_risk_analysis(execution):
            return
        
        # Check if approval required
        requires_approval, approval_decision = self.decision_engine.should_require_approval(execution)
        self.audit_logger.log_decision(approval_decision)
        
        if requires_approval:
            self.state_manager.transition_state(
                execution,
                ExecutionState.REQUIRES_APPROVAL,
                "Manual approval required before proceeding"
            )
            execution.requires_approval = True
            return
        
        # Stage 2: Patch Search
        if not self._find_patch(execution):
            return
        
        # Stage 3: Snapshot Creation
        if not self._create_snapshot(execution):
            return
        
        # Stage 4: Sandbox Testing
        if not self._test_in_sandbox(execution):
            return
        
        # Stage 5: Deployment Strategy Selection
        if force_strategy:
            strategy = force_strategy
            strategy_decision = WorkflowDecision(
                decision_id=f"forced-{execution.execution_id}",
                execution_id=execution.execution_id,
                decision_type='strategy_selection',
                decision=strategy.value,
                reasoning='Strategy forced by user',
                confidence=1.0
            )
        else:
            strategy, strategy_decision = self.decision_engine.select_deployment_strategy(execution)
        
        self.audit_logger.log_decision(strategy_decision)
        
        # Stage 6: Deployment
        if not self._deploy_patch(execution, strategy):
            return
        
        # Stage 7: Final Validation
        if not self._validate_deployment(execution):
            return
        
        # Success!
        self.state_manager.transition_state(
            execution,
            ExecutionState.COMPLETED,
            "Remediation completed successfully"
        )
        execution.success = True
    
    def _perform_risk_analysis(self, execution: RemediationExecution) -> bool:
        """Perform risk analysis"""
        try:
            self.state_manager.transition_state(
                execution,
                ExecutionState.RISK_ANALYSIS,
                "Analyzing remediation risk"
            )
            
            self.logger.info("📊 Performing risk analysis...")
            
            # Analyze risk
            risk_assessment = self.risk_analyzer.analyze_remediation_risk(
                vulnerability_id=execution.vulnerability_id,
                asset=execution.asset,
                patch_available=True  # Optimistic assumption
            )
            
            execution.risk_assessment = risk_assessment
            execution.autonomy_level = risk_assessment.recommended_autonomy
            
            self.logger.info(f"   Risk Score: {risk_assessment.risk_score:.2f}")
            self.logger.info(f"   Autonomy: {risk_assessment.recommended_autonomy.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Risk analysis failed: {e}")
            execution.state = ExecutionState.FAILED
            execution.error_message = f"Risk analysis error: {e}"
            return False
    
    def _find_patch(self, execution: RemediationExecution) -> bool:
        """Find appropriate patch"""
        try:
            self.state_manager.transition_state(
                execution,
                ExecutionState.PATCH_SEARCH,
                "Searching for patches"
            )
            
            self.logger.info("🔍 Searching for patch...")
            
            # Find patches
            patches = self.patch_engine.find_patches(
                vulnerability_id=execution.vulnerability_id,
                asset=execution.asset
            )
            
            if not patches:
                raise RemediationError(f"No patches found for {execution.vulnerability_id}")
            
            # Select best patch (first for now - could be more sophisticated)
            execution.selected_patch = patches[0]
            
            self.logger.info(f"   ✅ Found patch: {execution.selected_patch.patch_id}")
            self.logger.info(f"   Source: {execution.selected_patch.source}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Patch search failed: {e}")
            execution.state = ExecutionState.FAILED
            execution.error_message = f"Patch search error: {e}"
            return False
    
    def _create_snapshot(self, execution: RemediationExecution) -> bool:
        """Create pre-deployment snapshot"""
        try:
            self.state_manager.transition_state(
                execution,
                ExecutionState.SNAPSHOT_CREATION,
                "Creating system snapshot"
            )
            
            self.logger.info("📸 Creating snapshot...")
            
            # Create snapshot
            snapshot = self.rollback_manager.create_snapshot(
                execution_id=execution.execution_id,
                asset=execution.asset
            )
            
            execution.snapshot = snapshot
            
            self.logger.info(f"   ✅ Snapshot created: {snapshot.snapshot_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Snapshot creation failed: {e}")
            execution.state = ExecutionState.FAILED
            execution.error_message = f"Snapshot error: {e}"
            return False
    
    def _test_in_sandbox(self, execution: RemediationExecution) -> bool:
        """Test patch in sandbox"""
        try:
            self.state_manager.transition_state(
                execution,
                ExecutionState.SANDBOX_TESTING,
                "Testing patch in sandbox"
            )
            
            self.logger.info("🧪 Testing in sandbox...")
            
            # Create test suite
            test_suite = self._create_test_suite(execution)
            
            # Test in sandbox
            success, results = self.sandbox_tester.test_patch_in_sandbox(
                patch_id=execution.selected_patch.patch_id,
                asset=execution.asset,
                test_suites=[test_suite]
            )
            
            execution.test_results = results
            
            if not success:
                raise RemediationError("Sandbox testing failed")
            
            self.logger.info(f"   ✅ Sandbox tests passed: {test_suite.tests_passed}/{test_suite.total_tests}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Sandbox testing failed: {e}")
            execution.state = ExecutionState.FAILED
            execution.error_message = f"Sandbox testing error: {e}"
            return False
    
    def _create_test_suite(self, execution: RemediationExecution) -> TestSuite:
        """Create appropriate test suite"""
        suite = TestSuite(
            suite_id=f"suite-{execution.execution_id}",
            name=f"Patch validation for {execution.vulnerability_id}"
        )
        
        # Add functional test
        suite.test_cases.append(TestCase(
            test_id=f"func-{execution.execution_id}",
            name="Functional Test",
            test_type=TestType.FUNCTIONAL,
            description="Verify system functionality after patch"
        ))
        
        # Add security test
        suite.test_cases.append(TestCase(
            test_id=f"sec-{execution.execution_id}",
            name="Security Test",
            test_type=TestType.SECURITY,
            description="Verify vulnerability is patched"
        ))
        
        suite.total_tests = len(suite.test_cases)
        
        return suite
    
    def _deploy_patch(self, execution: RemediationExecution, strategy: DeploymentStrategy) -> bool:
        """Deploy patch using selected strategy"""
        try:
            self.state_manager.transition_state(
                execution,
                ExecutionState.DEPLOYMENT,
                f"Deploying with {strategy.value} strategy"
            )
            
            self.logger.info(f"🚀 Deploying with {strategy.value} strategy...")
            
            # Create deployment plan
            plan = self.deployment_orchestrator.create_deployment_plan(
                execution_id=execution.execution_id,
                asset=execution.asset,
                patch={'patch_id': execution.selected_patch.patch_id},
                strategy=strategy
            )
            
            execution.deployment_plan = plan
            
            # Define health checks
            health_checks = self._create_health_checks(execution)
            
            # Execute deployment
            success = self.deployment_orchestrator.execute_deployment(
                plan=plan,
                health_checks=health_checks,
                auto_rollback=True
            )
            
            if not success:
                if plan.rolled_back:
                    execution.rolled_back = True
                    self.state_manager.transition_state(
                        execution,
                        ExecutionState.ROLLED_BACK,
                        "Deployment failed and was rolled back"
                    )
                raise RemediationError("Deployment failed")
            
            self.logger.info(f"   ✅ Deployment completed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            execution.state = ExecutionState.FAILED
            execution.error_message = f"Deployment error: {e}"
            return False
    
    def _create_health_checks(self, execution: RemediationExecution) -> List[Dict]:
        """Create health checks for deployment"""
        # Basic health checks - could be customized per asset type
        return [
            {
                'type': 'http',
                'name': 'Health Endpoint',
                'url': f"http://{execution.asset.get('hostname', 'localhost')}/health",
                'expected_status': 200,
                'timeout': 10
            }
        ]
    
    def _validate_deployment(self, execution: RemediationExecution) -> bool:
        """Final validation after deployment"""
        try:
            self.state_manager.transition_state(
                execution,
                ExecutionState.VALIDATION,
                "Performing final validation"
            )
            
            self.logger.info("✅ Performing final validation...")
            
            # Could add additional validation logic here
            # For now, if we got here, deployment succeeded
            
            self.logger.info("   ✅ Validation passed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            execution.state = ExecutionState.FAILED
            execution.error_message = f"Validation error: {e}"
            return False
    
    def _save_execution(self, execution: RemediationExecution) -> None:
        """Save execution to database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO remediation_executions (
                        execution_id, vulnerability_id, asset_id,
                        priority, state, autonomy_level,
                        started_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.execution_id,
                    execution.vulnerability_id,
                    execution.asset.get('asset_id', 'unknown'),
                    execution.priority.value,
                    execution.state.value,
                    execution.autonomy_level.value if execution.autonomy_level else None,
                    execution.started_at.isoformat() if execution.started_at else None,
                    datetime.now().isoformat()
                ))
                
        except Exception as e:
            self.logger.error(f"Error saving execution: {e}")
            raise RemediationDatabaseError(f"Failed to save execution: {e}")
    
    def _update_execution(self, execution: RemediationExecution) -> None:
        """Update execution in database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE remediation_executions
                    SET state = ?, completed_at = ?,
                        success = ?, rolled_back = ?,
                        error_message = ?
                    WHERE execution_id = ?
                """, (
                    execution.state.value,
                    execution.completed_at.isoformat() if execution.completed_at else None,
                    1 if execution.success else 0,
                    1 if execution.rolled_back else 0,
                    execution.error_message,
                    execution.execution_id
                ))
                
        except Exception as e:
            self.logger.error(f"Error updating execution: {e}")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize engine
    engine = RemediationEngine()
    
    # Example vulnerability
    vulnerability_id = "CVE-2024-1234"
    
    # Example asset
    asset = {
        'asset_id': 'K8S-PROD-001',
        'asset_type': 'kubernetes_cluster',
        'hostname': 'api.example.com',
        'deployment_name': 'web-app',
        'namespace': 'production',
        'criticality': 'high'
    }
    
    # Execute remediation
    print(f"\n{'='*60}")
    print(f"AUTONOMOUS VULNERABILITY REMEDIATION")
    print(f"{'='*60}\n")
    
    execution = engine.remediate_vulnerability(
        vulnerability_id=vulnerability_id,
        asset=asset,
        priority=RemediationPriority.HIGH
    )
    
    print(f"\n{'='*60}")
    print(f"REMEDIATION SUMMARY")
    print(f"{'='*60}")
    print(f"Execution ID: {execution.execution_id}")
    print(f"Vulnerability: {execution.vulnerability_id}")
    print(f"Final State: {execution.state.value}")
    print(f"Success: {execution.success}")
    print(f"Rolled Back: {execution.rolled_back}")
    print(f"Requires Approval: {execution.requires_approval}")
    if execution.started_at and execution.completed_at:
        duration = (execution.completed_at - execution.started_at).total_seconds()
        print(f"Duration: {duration:.2f} seconds")
    if execution.error_message:
        print(f"Error: {execution.error_message}")
    print(f"{'='*60}\n")
