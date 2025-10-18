"""
Module G.1.9: ARIA Integration
Jupiter v3.0 Enhancement - Autonomous Remediation Engine

ARIA dashboard integration providing real-time execution monitoring,
approval workflows, and executive reporting.

Components:
- ARIAConnector: WebSocket + REST API communication
- ExecutionMonitor: Real-time status updates
- ApprovalWorkflow: Manual approval integration
- ReportGenerator: Executive summaries and analytics
- NotificationSender: Alert generation and delivery

Author: Enterprise Scanner Team
Date: October 17, 2025
Version: 1.0
"""

import sqlite3
import json
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ==================== Data Classes ====================

@dataclass
class ExecutionUpdate:
    """Real-time execution status update"""
    execution_id: str
    state: str
    progress_percentage: int
    current_stage: str
    message: str
    timestamp: datetime
    metadata: Dict
    
    def to_json(self) -> str:
        """Convert to JSON for transmission"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)


@dataclass
class ApprovalRequest:
    """Manual approval request"""
    request_id: str
    execution_id: str
    vulnerability_id: str
    asset: Dict
    risk_score: float
    proposed_patch: str
    proposed_strategy: str
    estimated_duration: int
    risk_factors: List[str]
    requested_at: datetime
    requested_by: str
    expires_at: datetime
    
    def to_json(self) -> str:
        """Convert to JSON for transmission"""
        data = asdict(self)
        data['requested_at'] = self.requested_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return json.dumps(data)


@dataclass
class ApprovalResponse:
    """Manual approval response"""
    request_id: str
    execution_id: str
    approved: bool
    approved_by: str
    approved_at: datetime
    comments: Optional[str]
    forced_strategy: Optional[str]


@dataclass
class ExecutionReport:
    """Executive execution report"""
    report_id: str
    execution_id: str
    vulnerability_id: str
    asset_id: str
    success: bool
    duration_seconds: float
    risk_score: float
    strategy_used: str
    stages_completed: int
    tests_passed: int
    rollback_occurred: bool
    completed_at: datetime
    summary: str
    recommendations: List[str]


@dataclass
class DashboardMetrics:
    """Dashboard metrics summary"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    pending_approvals: int
    avg_duration_seconds: float
    success_rate: float
    rollback_rate: float
    high_risk_count: int
    last_updated: datetime


@dataclass
class Notification:
    """System notification"""
    notification_id: str
    notification_type: str  # 'execution_complete', 'approval_required', 'anomaly_detected', etc.
    severity: str  # 'info', 'warning', 'error', 'critical'
    title: str
    message: str
    execution_id: Optional[str]
    created_at: datetime
    sent_to: List[str]
    
    def to_json(self) -> str:
        """Convert to JSON for transmission"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return json.dumps(data)


class NotificationType(Enum):
    """Notification types"""
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETE = "execution_complete"
    EXECUTION_FAILED = "execution_failed"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_TIMEOUT = "approval_timeout"
    ROLLBACK_OCCURRED = "rollback_occurred"
    ANOMALY_DETECTED = "anomaly_detected"
    HIGH_RISK_DETECTED = "high_risk_detected"


# ==================== ARIA Connector ====================

class ARIAConnector:
    """
    WebSocket + REST API connector to ARIA dashboard
    
    Manages bidirectional communication with dashboard UI
    """
    
    def __init__(
        self,
        aria_url: str = "ws://localhost:8080/aria/ws",
        api_url: str = "http://localhost:8080/api/v1",
        api_key: Optional[str] = None
    ):
        self.aria_url = aria_url
        self.api_url = api_url
        self.api_key = api_key
        self.websocket = None
        self.connected = False
        self.listeners: Dict[str, List[Callable]] = {}
    
    async def connect(self) -> bool:
        """
        Establish WebSocket connection to ARIA
        
        Returns:
            True if connected successfully
        """
        try:
            # In production, use websockets library
            # For now, simulate connection
            logger.info(f"Connecting to ARIA dashboard at {self.aria_url}")
            
            # Simulated connection
            self.connected = True
            logger.info("✅ Connected to ARIA dashboard")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ARIA: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from ARIA dashboard"""
        if self.websocket:
            # await self.websocket.close()
            pass
        
        self.connected = False
        logger.info("Disconnected from ARIA dashboard")
    
    async def send_update(self, update: ExecutionUpdate) -> bool:
        """
        Send execution update to dashboard
        
        Args:
            update: Execution status update
            
        Returns:
            True if sent successfully
        """
        if not self.connected:
            logger.warning("Not connected to ARIA - cannot send update")
            return False
        
        try:
            message = {
                'type': 'execution_update',
                'data': json.loads(update.to_json())
            }
            
            # In production: await self.websocket.send(json.dumps(message))
            logger.debug(f"📤 Sent update: {update.execution_id} - {update.message}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send update: {e}")
            return False
    
    async def send_approval_request(self, request: ApprovalRequest) -> bool:
        """
        Send approval request to dashboard
        
        Args:
            request: Approval request
            
        Returns:
            True if sent successfully
        """
        if not self.connected:
            logger.warning("Not connected to ARIA - cannot send approval request")
            return False
        
        try:
            message = {
                'type': 'approval_request',
                'data': json.loads(request.to_json())
            }
            
            # In production: await self.websocket.send(json.dumps(message))
            logger.info(f"📤 Sent approval request: {request.request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send approval request: {e}")
            return False
    
    async def send_notification(self, notification: Notification) -> bool:
        """
        Send notification to dashboard
        
        Args:
            notification: Notification to send
            
        Returns:
            True if sent successfully
        """
        if not self.connected:
            logger.warning("Not connected to ARIA - cannot send notification")
            return False
        
        try:
            message = {
                'type': 'notification',
                'data': json.loads(notification.to_json())
            }
            
            # In production: await self.websocket.send(json.dumps(message))
            logger.info(f"📤 Sent notification: {notification.title}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def register_listener(self, event_type: str, callback: Callable) -> None:
        """
        Register event listener
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(callback)
        logger.debug(f"Registered listener for {event_type}")
    
    async def _handle_message(self, message: str) -> None:
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            event_type = data.get('type')
            
            if event_type in self.listeners:
                for callback in self.listeners[event_type]:
                    await callback(data.get('data', {}))
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")


# ==================== Execution Monitor ====================

class ExecutionMonitor:
    """
    Real-time execution monitoring
    
    Streams execution status to ARIA dashboard
    """
    
    def __init__(self, connector: ARIAConnector, db_path: str = 'remediation.db'):
        self.connector = connector
        self.db_path = db_path
        self.active_monitors: Dict[str, bool] = {}
    
    async def start_monitoring(self, execution_id: str) -> None:
        """
        Start monitoring execution
        
        Args:
            execution_id: Execution to monitor
        """
        self.active_monitors[execution_id] = True
        logger.info(f"Started monitoring execution {execution_id}")
        
        # Start monitoring loop
        asyncio.create_task(self._monitor_loop(execution_id))
    
    async def stop_monitoring(self, execution_id: str) -> None:
        """
        Stop monitoring execution
        
        Args:
            execution_id: Execution to stop monitoring
        """
        self.active_monitors[execution_id] = False
        logger.info(f"Stopped monitoring execution {execution_id}")
    
    async def _monitor_loop(self, execution_id: str) -> None:
        """Monitor execution status loop"""
        last_state = None
        
        while self.active_monitors.get(execution_id, False):
            try:
                # Get current execution state
                execution = self._get_execution_status(execution_id)
                
                if execution and execution['state'] != last_state:
                    # State changed - send update
                    update = ExecutionUpdate(
                        execution_id=execution_id,
                        state=execution['state'],
                        progress_percentage=self._calculate_progress(execution['state']),
                        current_stage=execution['state'],
                        message=f"Execution in {execution['state']} state",
                        timestamp=datetime.now(),
                        metadata={
                            'risk_score': execution.get('risk_score', 0.0),
                            'autonomy_level': execution.get('autonomy_level', 'unknown')
                        }
                    )
                    
                    await self.connector.send_update(update)
                    last_state = execution['state']
                
                # Check if execution complete
                if execution and execution['state'] in ['completed', 'failed', 'rolled_back']:
                    self.active_monitors[execution_id] = False
                    break
                
                # Wait before next check
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)
    
    def _get_execution_status(self, execution_id: str) -> Optional[Dict]:
        """Get current execution status from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    execution_id,
                    state,
                    autonomy_level,
                    success,
                    rolled_back
                FROM remediation_executions
                WHERE execution_id = ?
            """, (execution_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        finally:
            conn.close()
    
    def _calculate_progress(self, state: str) -> int:
        """Calculate progress percentage from state"""
        state_progress = {
            'pending': 0,
            'risk_analysis': 10,
            'patch_search': 20,
            'snapshot_creation': 30,
            'sandbox_testing': 50,
            'deployment': 70,
            'validation': 90,
            'completed': 100,
            'failed': 100,
            'rolled_back': 100
        }
        
        return state_progress.get(state, 0)
    
    async def send_stage_update(
        self,
        execution_id: str,
        stage: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Send manual stage update
        
        Args:
            execution_id: Execution ID
            stage: Current stage name
            message: Status message
            metadata: Additional metadata
        """
        update = ExecutionUpdate(
            execution_id=execution_id,
            state=stage,
            progress_percentage=self._calculate_progress(stage),
            current_stage=stage,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        await self.connector.send_update(update)


# ==================== Approval Workflow ====================

class ApprovalWorkflow:
    """
    Manual approval workflow integration
    
    Handles approval requests and responses
    """
    
    def __init__(self, connector: ARIAConnector, db_path: str = 'remediation.db'):
        self.connector = connector
        self.db_path = db_path
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        
        # Register approval response listener
        connector.register_listener('approval_response', self._handle_approval_response)
    
    async def request_approval(
        self,
        execution_id: str,
        vulnerability_id: str,
        asset: Dict,
        risk_score: float,
        proposed_patch: str,
        proposed_strategy: str,
        estimated_duration: int,
        risk_factors: List[str],
        timeout_minutes: int = 30
    ) -> str:
        """
        Request manual approval
        
        Args:
            execution_id: Execution ID
            vulnerability_id: Vulnerability being remediated
            asset: Asset information
            risk_score: Calculated risk score
            proposed_patch: Patch to be applied
            proposed_strategy: Deployment strategy
            estimated_duration: Estimated duration in seconds
            risk_factors: List of risk factors
            timeout_minutes: Approval timeout
            
        Returns:
            Request ID
        """
        request_id = f"APPR-{execution_id}-{int(datetime.now().timestamp())}"
        
        request = ApprovalRequest(
            request_id=request_id,
            execution_id=execution_id,
            vulnerability_id=vulnerability_id,
            asset=asset,
            risk_score=risk_score,
            proposed_patch=proposed_patch,
            proposed_strategy=proposed_strategy,
            estimated_duration=estimated_duration,
            risk_factors=risk_factors,
            requested_at=datetime.now(),
            requested_by='remediation_engine',
            expires_at=datetime.now() + timedelta(minutes=timeout_minutes)
        )
        
        # Save to database
        self._save_approval_request(request)
        
        # Store pending
        self.pending_requests[request_id] = request
        
        # Send to dashboard
        await self.connector.send_approval_request(request)
        
        logger.info(f"📋 Approval requested: {request_id} (expires in {timeout_minutes} min)")
        
        return request_id
    
    async def wait_for_approval(
        self,
        request_id: str,
        timeout_seconds: int = 1800
    ) -> Optional[ApprovalResponse]:
        """
        Wait for approval response
        
        Args:
            request_id: Request ID to wait for
            timeout_seconds: Timeout in seconds
            
        Returns:
            Approval response or None if timeout
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            # Check database for response
            response = self._get_approval_response(request_id)
            
            if response:
                # Remove from pending
                self.pending_requests.pop(request_id, None)
                return response
            
            # Wait before checking again
            await asyncio.sleep(2)
        
        logger.warning(f"⏱️ Approval request {request_id} timed out")
        return None
    
    async def _handle_approval_response(self, data: Dict) -> None:
        """Handle approval response from dashboard"""
        try:
            response = ApprovalResponse(
                request_id=data['request_id'],
                execution_id=data['execution_id'],
                approved=data['approved'],
                approved_by=data['approved_by'],
                approved_at=datetime.fromisoformat(data['approved_at']),
                comments=data.get('comments'),
                forced_strategy=data.get('forced_strategy')
            )
            
            # Save to database
            self._save_approval_response(response)
            
            logger.info(f"✅ Approval response received: {response.request_id} - {'APPROVED' if response.approved else 'REJECTED'}")
            
        except Exception as e:
            logger.error(f"Error handling approval response: {e}")
    
    def _save_approval_request(self, request: ApprovalRequest) -> None:
        """Save approval request to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS approval_requests (
                    request_id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    vulnerability_id TEXT NOT NULL,
                    asset TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    proposed_patch TEXT NOT NULL,
                    proposed_strategy TEXT NOT NULL,
                    estimated_duration INTEGER NOT NULL,
                    risk_factors TEXT NOT NULL,
                    requested_at TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO approval_requests
                (request_id, execution_id, vulnerability_id, asset, risk_score, 
                 proposed_patch, proposed_strategy, estimated_duration, risk_factors,
                 requested_at, requested_by, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.request_id,
                request.execution_id,
                request.vulnerability_id,
                json.dumps(request.asset),
                request.risk_score,
                request.proposed_patch,
                request.proposed_strategy,
                request.estimated_duration,
                json.dumps(request.risk_factors),
                request.requested_at.isoformat(),
                request.requested_by,
                request.expires_at.isoformat()
            ))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def _save_approval_response(self, response: ApprovalResponse) -> None:
        """Save approval response to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS approval_responses (
                    request_id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    approved INTEGER NOT NULL,
                    approved_by TEXT NOT NULL,
                    approved_at TEXT NOT NULL,
                    comments TEXT,
                    forced_strategy TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO approval_responses
                (request_id, execution_id, approved, approved_by, approved_at, comments, forced_strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                response.request_id,
                response.execution_id,
                1 if response.approved else 0,
                response.approved_by,
                response.approved_at.isoformat(),
                response.comments,
                response.forced_strategy
            ))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def _get_approval_response(self, request_id: str) -> Optional[ApprovalResponse]:
        """Get approval response from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM approval_responses
                WHERE request_id = ?
            """, (request_id,))
            
            row = cursor.fetchone()
            if row:
                return ApprovalResponse(
                    request_id=row['request_id'],
                    execution_id=row['execution_id'],
                    approved=bool(row['approved']),
                    approved_by=row['approved_by'],
                    approved_at=datetime.fromisoformat(row['approved_at']),
                    comments=row['comments'],
                    forced_strategy=row['forced_strategy']
                )
            return None
            
        finally:
            conn.close()


# ==================== Report Generator ====================

class ReportGenerator:
    """
    Executive report generation
    
    Creates summaries and analytics for dashboard
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
    
    def generate_execution_report(self, execution_id: str) -> Optional[ExecutionReport]:
        """
        Generate execution report
        
        Args:
            execution_id: Execution to report on
            
        Returns:
            Execution report or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get execution details
            cursor.execute("""
                SELECT 
                    re.execution_id,
                    re.vulnerability_id,
                    re.asset_id,
                    re.success,
                    re.duration_seconds,
                    re.rolled_back,
                    re.completed_at,
                    ra.risk_score,
                    dp.strategy,
                    COUNT(DISTINCT ds.stage_id) as stages_completed
                FROM remediation_executions re
                LEFT JOIN risk_assessments ra ON re.execution_id = ra.execution_id
                LEFT JOIN deployment_plans dp ON re.execution_id = dp.execution_id
                LEFT JOIN deployment_stages ds ON dp.plan_id = ds.plan_id AND ds.status = 'completed'
                WHERE re.execution_id = ?
                GROUP BY re.execution_id
            """, (execution_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Generate summary
            if row['success']:
                summary = f"Successfully remediated vulnerability {row['vulnerability_id']} using {row['strategy']} strategy"
            else:
                summary = f"Failed to remediate vulnerability {row['vulnerability_id']}"
                if row['rolled_back']:
                    summary += " - system rolled back"
            
            # Generate recommendations
            recommendations = []
            if row['duration_seconds'] > 1800:
                recommendations.append("Consider optimizing deployment process - duration exceeded 30 minutes")
            if row['rolled_back']:
                recommendations.append("Review rollback cause - implement preventive measures")
            if row['risk_score'] > 0.8:
                recommendations.append("High risk vulnerability - schedule follow-up validation")
            
            report_id = f"RPT-{execution_id}-{int(datetime.now().timestamp())}"
            
            return ExecutionReport(
                report_id=report_id,
                execution_id=execution_id,
                vulnerability_id=row['vulnerability_id'],
                asset_id=row['asset_id'],
                success=bool(row['success']),
                duration_seconds=row['duration_seconds'] or 0.0,
                risk_score=row['risk_score'] or 0.0,
                strategy_used=row['strategy'] or 'unknown',
                stages_completed=row['stages_completed'] or 0,
                tests_passed=0,  # Would query test results
                rollback_occurred=bool(row['rolled_back']),
                completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else datetime.now(),
                summary=summary,
                recommendations=recommendations
            )
            
        finally:
            conn.close()
    
    def generate_dashboard_metrics(self, days_back: int = 30) -> DashboardMetrics:
        """
        Generate dashboard metrics
        
        Args:
            days_back: Days of history to include
            
        Returns:
            Dashboard metrics summary
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                    AVG(duration_seconds) as avg_duration,
                    SUM(CASE WHEN rolled_back = 1 THEN 1 ELSE 0 END) as rollbacks
                FROM remediation_executions
                WHERE started_at >= ?
            """, (cutoff_date.isoformat(),))
            
            row = cursor.fetchone()
            
            total = row['total'] or 0
            successful = row['successful'] or 0
            failed = row['failed'] or 0
            
            # Pending approvals
            cursor.execute("""
                SELECT COUNT(*) as pending
                FROM approval_requests
                WHERE request_id NOT IN (SELECT request_id FROM approval_responses)
                  AND expires_at > ?
            """, (datetime.now().isoformat(),))
            
            pending_approvals = cursor.fetchone()['pending'] or 0
            
            # High risk count
            cursor.execute("""
                SELECT COUNT(*) as high_risk
                FROM remediation_executions re
                JOIN risk_assessments ra ON re.execution_id = ra.execution_id
                WHERE re.started_at >= ?
                  AND ra.risk_score >= 0.7
            """, (cutoff_date.isoformat(),))
            
            high_risk = cursor.fetchone()['high_risk'] or 0
            
            return DashboardMetrics(
                total_executions=total,
                successful_executions=successful,
                failed_executions=failed,
                pending_approvals=pending_approvals,
                avg_duration_seconds=row['avg_duration'] or 0.0,
                success_rate=successful / total if total > 0 else 0.0,
                rollback_rate=(row['rollbacks'] or 0) / total if total > 0 else 0.0,
                high_risk_count=high_risk,
                last_updated=datetime.now()
            )
            
        finally:
            conn.close()


# ==================== Notification Sender ====================

class NotificationSender:
    """
    Alert generation and delivery
    
    Sends notifications for key events
    """
    
    def __init__(self, connector: ARIAConnector):
        self.connector = connector
    
    async def send_execution_started(self, execution_id: str, vulnerability_id: str, asset_id: str) -> None:
        """Send execution started notification"""
        notification = Notification(
            notification_id=f"NOTIF-{execution_id}-START",
            notification_type=NotificationType.EXECUTION_STARTED.value,
            severity='info',
            title='Remediation Started',
            message=f'Started remediating {vulnerability_id} on asset {asset_id}',
            execution_id=execution_id,
            created_at=datetime.now(),
            sent_to=['dashboard']
        )
        
        await self.connector.send_notification(notification)
    
    async def send_execution_complete(self, execution_id: str, success: bool, duration: float) -> None:
        """Send execution complete notification"""
        notification = Notification(
            notification_id=f"NOTIF-{execution_id}-COMPLETE",
            notification_type=NotificationType.EXECUTION_COMPLETE.value,
            severity='info' if success else 'warning',
            title='Remediation Complete',
            message=f"Remediation {'succeeded' if success else 'failed'} in {duration:.1f}s",
            execution_id=execution_id,
            created_at=datetime.now(),
            sent_to=['dashboard']
        )
        
        await self.connector.send_notification(notification)
    
    async def send_approval_required(self, request_id: str, execution_id: str, risk_score: float) -> None:
        """Send approval required notification"""
        notification = Notification(
            notification_id=f"NOTIF-{request_id}",
            notification_type=NotificationType.APPROVAL_REQUIRED.value,
            severity='warning',
            title='Manual Approval Required',
            message=f'High risk remediation (score: {risk_score:.2f}) requires approval',
            execution_id=execution_id,
            created_at=datetime.now(),
            sent_to=['dashboard', 'security_team']
        )
        
        await self.connector.send_notification(notification)
    
    async def send_rollback_occurred(self, execution_id: str, reason: str) -> None:
        """Send rollback notification"""
        notification = Notification(
            notification_id=f"NOTIF-{execution_id}-ROLLBACK",
            notification_type=NotificationType.ROLLBACK_OCCURRED.value,
            severity='error',
            title='Automatic Rollback Triggered',
            message=f'Deployment failed - system rolled back: {reason}',
            execution_id=execution_id,
            created_at=datetime.now(),
            sent_to=['dashboard', 'security_team', 'ops_team']
        )
        
        await self.connector.send_notification(notification)
    
    async def send_anomaly_detected(self, execution_id: str, anomaly_type: str, severity: str) -> None:
        """Send anomaly detection notification"""
        notification = Notification(
            notification_id=f"NOTIF-{execution_id}-ANOM",
            notification_type=NotificationType.ANOMALY_DETECTED.value,
            severity=severity,
            title='Anomaly Detected',
            message=f'Unusual pattern detected: {anomaly_type}',
            execution_id=execution_id,
            created_at=datetime.now(),
            sent_to=['dashboard', 'security_team']
        )
        
        await self.connector.send_notification(notification)


# ==================== Exports ====================

__all__ = [
    # Data classes
    'ExecutionUpdate',
    'ApprovalRequest',
    'ApprovalResponse',
    'ExecutionReport',
    'DashboardMetrics',
    'Notification',
    # Enums
    'NotificationType',
    # Components
    'ARIAConnector',
    'ExecutionMonitor',
    'ApprovalWorkflow',
    'ReportGenerator',
    'NotificationSender'
]
