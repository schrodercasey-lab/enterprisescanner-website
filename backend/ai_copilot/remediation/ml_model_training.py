"""
Module G.1.8: ML Model Training
Jupiter v3.0 Enhancement - Autonomous Remediation Engine

Machine learning system for optimizing remediation decisions through
pattern recognition and historical analysis.

Components:
- HistoricalDataCollector: Extract training data from execution history
- PatternRecognizer: Learn from successful/failed patterns
- RiskScoreOptimizer: Calibrate risk scoring accuracy
- StrategyRecommender: Optimize deployment strategy selection
- AnomalyDetector: Identify unusual patterns and outliers
- PredictiveAnalyzer: Forecast remediation success probability

Author: Enterprise Scanner Team
Date: October 17, 2025
Version: 1.0
"""

import sqlite3
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import logging

logger = logging.getLogger(__name__)


# ==================== Data Classes ====================

@dataclass
class TrainingData:
    """Training dataset extracted from execution history"""
    execution_id: str
    vulnerability_id: str
    asset_type: str
    criticality: str
    risk_score: float
    autonomy_level: str
    selected_strategy: str
    test_success_rate: float
    deployment_success: bool
    rollback_occurred: bool
    duration_seconds: float
    error_type: Optional[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'execution_id': self.execution_id,
            'vulnerability_id': self.vulnerability_id,
            'asset_type': self.asset_type,
            'criticality': self.criticality,
            'risk_score': self.risk_score,
            'autonomy_level': self.autonomy_level,
            'selected_strategy': self.selected_strategy,
            'test_success_rate': self.test_success_rate,
            'deployment_success': self.deployment_success,
            'rollback_occurred': self.rollback_occurred,
            'duration_seconds': self.duration_seconds,
            'error_type': self.error_type
        }


@dataclass
class Pattern:
    """Identified pattern from historical data"""
    pattern_id: str
    pattern_type: str  # 'success', 'failure', 'anomaly'
    conditions: Dict  # Conditions that trigger pattern
    outcome: str
    frequency: int
    confidence: float
    identified_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type,
            'conditions': json.dumps(self.conditions),
            'outcome': self.outcome,
            'frequency': self.frequency,
            'confidence': self.confidence,
            'identified_at': self.identified_at.isoformat()
        }


@dataclass
class RiskCalibration:
    """Risk score calibration adjustment"""
    asset_type: str
    criticality: str
    vulnerability_type: str
    current_weight: float
    optimal_weight: float
    adjustment: float
    samples: int
    confidence: float


@dataclass
class StrategyRecommendation:
    """ML-based strategy recommendation"""
    asset_type: str
    risk_score: float
    test_success_rate: float
    recommended_strategy: str
    confidence: float
    reasoning: str
    historical_success_rate: float


@dataclass
class AnomalyReport:
    """Detected anomaly in execution"""
    anomaly_id: str
    execution_id: str
    anomaly_type: str
    severity: str
    description: str
    detected_at: datetime
    metrics: Dict


@dataclass
class SuccessPrediction:
    """Prediction of remediation success"""
    execution_id: str
    predicted_success: bool
    confidence: float
    risk_factors: List[str]
    success_probability: float
    estimated_duration_seconds: float


class MLModelType(Enum):
    """Types of ML models"""
    PATTERN_RECOGNITION = "pattern_recognition"
    RISK_OPTIMIZATION = "risk_optimization"
    STRATEGY_RECOMMENDATION = "strategy_recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    SUCCESS_PREDICTION = "success_prediction"


# ==================== Historical Data Collector ====================

class HistoricalDataCollector:
    """
    Extracts training data from execution history
    
    Collects complete execution records for ML training
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
    
    def collect_training_data(
        self,
        days_back: int = 90,
        min_samples: int = 10
    ) -> List[TrainingData]:
        """
        Collect historical data for training
        
        Args:
            days_back: How many days of history to collect
            min_samples: Minimum samples required
            
        Returns:
            List of training data samples
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    re.execution_id,
                    re.vulnerability_id,
                    re.asset_type,
                    re.asset_criticality,
                    ra.risk_score,
                    re.autonomy_level,
                    dp.strategy,
                    re.test_success_rate,
                    re.success,
                    re.rolled_back,
                    re.duration_seconds,
                    re.error_message
                FROM remediation_executions re
                LEFT JOIN risk_assessments ra ON re.execution_id = ra.execution_id
                LEFT JOIN deployment_plans dp ON re.execution_id = dp.execution_id
                WHERE re.started_at >= ?
                  AND re.state = 'completed' OR re.state = 'failed'
                ORDER BY re.started_at DESC
            """, (cutoff_date.isoformat(),))
            
            training_data = []
            for row in cursor.fetchall():
                # Extract error type if present
                error_type = None
                if row['error_message']:
                    error_type = self._classify_error(row['error_message'])
                
                training_data.append(TrainingData(
                    execution_id=row['execution_id'],
                    vulnerability_id=row['vulnerability_id'],
                    asset_type=row['asset_type'],
                    criticality=row['asset_criticality'],
                    risk_score=row['risk_score'] or 0.5,
                    autonomy_level=row['autonomy_level'],
                    selected_strategy=row['strategy'] or 'unknown',
                    test_success_rate=row['test_success_rate'] or 0.0,
                    deployment_success=bool(row['success']),
                    rollback_occurred=bool(row['rolled_back']),
                    duration_seconds=row['duration_seconds'] or 0.0,
                    error_type=error_type
                ))
            
            logger.info(f"Collected {len(training_data)} training samples from last {days_back} days")
            
            if len(training_data) < min_samples:
                logger.warning(f"Only {len(training_data)} samples collected, minimum is {min_samples}")
            
            return training_data
            
        finally:
            conn.close()
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type from error message"""
        error_lower = error_message.lower()
        
        if 'timeout' in error_lower:
            return 'timeout'
        elif 'connection' in error_lower:
            return 'connection'
        elif 'authentication' in error_lower or 'permission' in error_lower:
            return 'authentication'
        elif 'not found' in error_lower:
            return 'not_found'
        elif 'health' in error_lower or 'validation' in error_lower:
            return 'health_check'
        else:
            return 'unknown'


# ==================== Pattern Recognizer ====================

class PatternRecognizer:
    """
    Learn patterns from successful/failed deployments
    
    Identifies common conditions leading to success or failure
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
        self.patterns: List[Pattern] = []
    
    def recognize_patterns(
        self,
        training_data: List[TrainingData],
        min_frequency: int = 3,
        min_confidence: float = 0.7
    ) -> List[Pattern]:
        """
        Identify patterns in training data
        
        Args:
            training_data: Historical execution data
            min_frequency: Minimum occurrences for pattern
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of identified patterns
        """
        patterns = []
        
        # Pattern 1: Strategy success by risk score ranges
        strategy_patterns = self._analyze_strategy_success(training_data)
        patterns.extend([p for p in strategy_patterns if p.frequency >= min_frequency and p.confidence >= min_confidence])
        
        # Pattern 2: Asset type specific issues
        asset_patterns = self._analyze_asset_type_patterns(training_data)
        patterns.extend([p for p in asset_patterns if p.frequency >= min_frequency and p.confidence >= min_confidence])
        
        # Pattern 3: Test success rate correlation
        test_patterns = self._analyze_test_correlation(training_data)
        patterns.extend([p for p in test_patterns if p.frequency >= min_frequency and p.confidence >= min_confidence])
        
        # Pattern 4: Failure patterns
        failure_patterns = self._analyze_failure_patterns(training_data)
        patterns.extend([p for p in failure_patterns if p.frequency >= min_frequency and p.confidence >= min_confidence])
        
        self.patterns = patterns
        self._save_patterns(patterns)
        
        logger.info(f"Identified {len(patterns)} patterns with min_frequency={min_frequency}, min_confidence={min_confidence}")
        
        return patterns
    
    def _analyze_strategy_success(self, training_data: List[TrainingData]) -> List[Pattern]:
        """Analyze which strategies work best for different risk levels"""
        patterns = []
        
        # Group by strategy and risk range
        risk_ranges = [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)]
        strategies = set(td.selected_strategy for td in training_data)
        
        for strategy in strategies:
            for risk_min, risk_max in risk_ranges:
                # Filter data
                filtered = [
                    td for td in training_data
                    if td.selected_strategy == strategy
                    and risk_min <= td.risk_score < risk_max
                ]
                
                if not filtered:
                    continue
                
                success_count = sum(1 for td in filtered if td.deployment_success)
                frequency = len(filtered)
                confidence = success_count / frequency if frequency > 0 else 0.0
                
                pattern_id = f"STRAT-{strategy}-{risk_min}-{risk_max}-{int(datetime.now().timestamp())}"
                
                patterns.append(Pattern(
                    pattern_id=pattern_id,
                    pattern_type='success' if confidence > 0.7 else 'failure',
                    conditions={
                        'strategy': strategy,
                        'risk_min': risk_min,
                        'risk_max': risk_max
                    },
                    outcome=f"{confidence*100:.1f}% success rate",
                    frequency=frequency,
                    confidence=confidence,
                    identified_at=datetime.now()
                ))
        
        return patterns
    
    def _analyze_asset_type_patterns(self, training_data: List[TrainingData]) -> List[Pattern]:
        """Analyze success patterns by asset type"""
        patterns = []
        
        asset_types = set(td.asset_type for td in training_data)
        
        for asset_type in asset_types:
            filtered = [td for td in training_data if td.asset_type == asset_type]
            
            if not filtered:
                continue
            
            success_count = sum(1 for td in filtered if td.deployment_success)
            frequency = len(filtered)
            confidence = success_count / frequency if frequency > 0 else 0.0
            
            # Check if specific strategies work better for this asset type
            strategy_success = {}
            for strategy in set(td.selected_strategy for td in filtered):
                strat_filtered = [td for td in filtered if td.selected_strategy == strategy]
                strat_success = sum(1 for td in strat_filtered if td.deployment_success)
                strategy_success[strategy] = strat_success / len(strat_filtered) if strat_filtered else 0.0
            
            best_strategy = max(strategy_success, key=strategy_success.get) if strategy_success else 'unknown'
            
            pattern_id = f"ASSET-{asset_type}-{int(datetime.now().timestamp())}"
            
            patterns.append(Pattern(
                pattern_id=pattern_id,
                pattern_type='success' if confidence > 0.7 else 'failure',
                conditions={
                    'asset_type': asset_type,
                    'best_strategy': best_strategy
                },
                outcome=f"{confidence*100:.1f}% success, best strategy: {best_strategy}",
                frequency=frequency,
                confidence=confidence,
                identified_at=datetime.now()
            ))
        
        return patterns
    
    def _analyze_test_correlation(self, training_data: List[TrainingData]) -> List[Pattern]:
        """Analyze correlation between test success and deployment success"""
        patterns = []
        
        test_ranges = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0)]
        
        for test_min, test_max in test_ranges:
            filtered = [
                td for td in training_data
                if test_min <= td.test_success_rate < test_max
            ]
            
            if not filtered:
                continue
            
            success_count = sum(1 for td in filtered if td.deployment_success)
            frequency = len(filtered)
            confidence = success_count / frequency if frequency > 0 else 0.0
            
            pattern_id = f"TEST-{test_min}-{test_max}-{int(datetime.now().timestamp())}"
            
            patterns.append(Pattern(
                pattern_id=pattern_id,
                pattern_type='success' if confidence > 0.7 else 'failure',
                conditions={
                    'test_success_min': test_min,
                    'test_success_max': test_max
                },
                outcome=f"{confidence*100:.1f}% deployment success",
                frequency=frequency,
                confidence=confidence,
                identified_at=datetime.now()
            ))
        
        return patterns
    
    def _analyze_failure_patterns(self, training_data: List[TrainingData]) -> List[Pattern]:
        """Analyze common failure patterns"""
        patterns = []
        
        failures = [td for td in training_data if not td.deployment_success]
        
        if not failures:
            return patterns
        
        # Group by error type
        error_types = set(td.error_type for td in failures if td.error_type)
        
        for error_type in error_types:
            filtered = [td for td in failures if td.error_type == error_type]
            frequency = len(filtered)
            
            # Analyze common conditions
            strategies = [td.selected_strategy for td in filtered]
            most_common_strategy = max(set(strategies), key=strategies.count) if strategies else 'unknown'
            
            avg_risk = statistics.mean([td.risk_score for td in filtered])
            
            pattern_id = f"FAIL-{error_type}-{int(datetime.now().timestamp())}"
            
            patterns.append(Pattern(
                pattern_id=pattern_id,
                pattern_type='failure',
                conditions={
                    'error_type': error_type,
                    'common_strategy': most_common_strategy,
                    'avg_risk_score': avg_risk
                },
                outcome=f"Failure: {error_type}",
                frequency=frequency,
                confidence=frequency / len(failures),
                identified_at=datetime.now()
            ))
        
        return patterns
    
    def _save_patterns(self, patterns: List[Pattern]) -> None:
        """Save identified patterns to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    frequency INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    identified_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            for pattern in patterns:
                cursor.execute("""
                    INSERT OR REPLACE INTO ml_patterns
                    (pattern_id, pattern_type, conditions, outcome, frequency, confidence, identified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.pattern_type,
                    json.dumps(pattern.conditions),
                    pattern.outcome,
                    pattern.frequency,
                    pattern.confidence,
                    pattern.identified_at.isoformat()
                ))
            
            conn.commit()
            logger.info(f"Saved {len(patterns)} patterns to database")
            
        finally:
            conn.close()


# ==================== Risk Score Optimizer ====================

class RiskScoreOptimizer:
    """
    Calibrate risk scoring accuracy based on outcomes
    
    Adjusts risk calculation weights to improve predictions
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
    
    def optimize_risk_weights(
        self,
        training_data: List[TrainingData]
    ) -> List[RiskCalibration]:
        """
        Calculate optimal risk score weights
        
        Args:
            training_data: Historical execution data
            
        Returns:
            List of calibration adjustments
        """
        calibrations = []
        
        # Group by asset type and criticality
        groups = {}
        for td in training_data:
            key = (td.asset_type, td.criticality)
            if key not in groups:
                groups[key] = []
            groups[key].append(td)
        
        for (asset_type, criticality), data in groups.items():
            if len(data) < 5:  # Need minimum samples
                continue
            
            # Calculate actual vs predicted success
            successes = [td for td in data if td.deployment_success]
            failures = [td for td in data if not td.deployment_success]
            
            actual_success_rate = len(successes) / len(data)
            
            # Average risk scores
            avg_risk_success = statistics.mean([td.risk_score for td in successes]) if successes else 0.5
            avg_risk_failure = statistics.mean([td.risk_score for td in failures]) if failures else 0.5
            
            # Calculate optimal adjustment
            # If high risk but high success, reduce risk weight
            # If low risk but many failures, increase risk weight
            current_weight = 1.0
            
            if actual_success_rate > 0.8 and avg_risk_success > 0.6:
                # High success despite high risk - reduce weight
                optimal_weight = current_weight * 0.8
            elif actual_success_rate < 0.5 and avg_risk_failure < 0.5:
                # Low success despite low risk - increase weight
                optimal_weight = current_weight * 1.2
            else:
                optimal_weight = current_weight
            
            adjustment = optimal_weight - current_weight
            confidence = min(len(data) / 20.0, 1.0)  # More samples = higher confidence
            
            calibrations.append(RiskCalibration(
                asset_type=asset_type,
                criticality=criticality,
                vulnerability_type='all',  # Can be refined further
                current_weight=current_weight,
                optimal_weight=optimal_weight,
                adjustment=adjustment,
                samples=len(data),
                confidence=confidence
            ))
        
        logger.info(f"Generated {len(calibrations)} risk calibrations")
        
        return calibrations


# ==================== Strategy Recommender ====================

class StrategyRecommender:
    """
    Recommend optimal deployment strategy based on ML
    
    Uses historical success rates to optimize strategy selection
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
    
    def recommend_strategy(
        self,
        asset_type: str,
        risk_score: float,
        test_success_rate: float,
        training_data: List[TrainingData]
    ) -> StrategyRecommendation:
        """
        Recommend deployment strategy using ML
        
        Args:
            asset_type: Type of asset
            risk_score: Calculated risk score
            test_success_rate: Sandbox test success rate
            training_data: Historical data
            
        Returns:
            Strategy recommendation with confidence
        """
        # Filter similar historical cases
        similar = [
            td for td in training_data
            if td.asset_type == asset_type
            and abs(td.risk_score - risk_score) < 0.2
            and abs(td.test_success_rate - test_success_rate) < 0.2
        ]
        
        if not similar:
            # Fallback to risk-based selection
            return self._fallback_recommendation(risk_score)
        
        # Calculate success rate by strategy
        strategy_stats = {}
        for strategy in set(td.selected_strategy for td in similar):
            strat_data = [td for td in similar if td.selected_strategy == strategy]
            success_count = sum(1 for td in strat_data if td.deployment_success)
            success_rate = success_count / len(strat_data)
            
            strategy_stats[strategy] = {
                'success_rate': success_rate,
                'samples': len(strat_data),
                'avg_duration': statistics.mean([td.duration_seconds for td in strat_data])
            }
        
        # Select best strategy
        best_strategy = max(strategy_stats, key=lambda s: strategy_stats[s]['success_rate'])
        best_stats = strategy_stats[best_strategy]
        
        confidence = min(best_stats['samples'] / 10.0, 1.0)  # More samples = higher confidence
        
        reasoning = (
            f"Based on {best_stats['samples']} similar cases with "
            f"{best_stats['success_rate']*100:.1f}% success rate"
        )
        
        return StrategyRecommendation(
            asset_type=asset_type,
            risk_score=risk_score,
            test_success_rate=test_success_rate,
            recommended_strategy=best_strategy,
            confidence=confidence,
            reasoning=reasoning,
            historical_success_rate=best_stats['success_rate']
        )
    
    def _fallback_recommendation(self, risk_score: float) -> StrategyRecommendation:
        """Fallback to risk-based recommendation when no similar cases exist"""
        if risk_score >= 0.8:
            strategy = 'canary'
            reasoning = "High risk score - no historical data, using conservative canary"
        elif risk_score >= 0.5:
            strategy = 'blue_green'
            reasoning = "Medium risk score - no historical data, using blue-green"
        else:
            strategy = 'rolling_update'
            reasoning = "Low risk score - no historical data, using rolling update"
        
        return StrategyRecommendation(
            asset_type='unknown',
            risk_score=risk_score,
            test_success_rate=0.0,
            recommended_strategy=strategy,
            confidence=0.5,  # Low confidence without data
            reasoning=reasoning,
            historical_success_rate=0.0
        )


# ==================== Anomaly Detector ====================

class AnomalyDetector:
    """
    Detect unusual patterns and outliers
    
    Identifies executions that deviate from normal patterns
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
    
    def detect_anomalies(
        self,
        current_execution: TrainingData,
        training_data: List[TrainingData]
    ) -> List[AnomalyReport]:
        """
        Detect anomalies in current execution
        
        Args:
            current_execution: Current execution to check
            training_data: Historical baseline data
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Similar executions for baseline
        similar = [
            td for td in training_data
            if td.asset_type == current_execution.asset_type
        ]
        
        if len(similar) < 5:
            return anomalies  # Need baseline
        
        # Anomaly 1: Duration outlier
        durations = [td.duration_seconds for td in similar]
        avg_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0
        
        if std_duration > 0:
            z_score = (current_execution.duration_seconds - avg_duration) / std_duration
            
            if abs(z_score) > 2.5:  # 2.5 standard deviations
                anomalies.append(AnomalyReport(
                    anomaly_id=f"ANOM-DUR-{current_execution.execution_id}",
                    execution_id=current_execution.execution_id,
                    anomaly_type='duration_outlier',
                    severity='medium' if abs(z_score) < 3.5 else 'high',
                    description=f"Duration {current_execution.duration_seconds:.0f}s is {z_score:.1f} std devs from mean {avg_duration:.0f}s",
                    detected_at=datetime.now(),
                    metrics={
                        'z_score': z_score,
                        'current_duration': current_execution.duration_seconds,
                        'avg_duration': avg_duration,
                        'std_duration': std_duration
                    }
                ))
        
        # Anomaly 2: Unexpected rollback
        rollback_rate = sum(1 for td in similar if td.rollback_occurred) / len(similar)
        
        if current_execution.rollback_occurred and rollback_rate < 0.1:
            anomalies.append(AnomalyReport(
                anomaly_id=f"ANOM-ROLL-{current_execution.execution_id}",
                execution_id=current_execution.execution_id,
                anomaly_type='unexpected_rollback',
                severity='high',
                description=f"Rollback occurred despite low historical rollback rate ({rollback_rate*100:.1f}%)",
                detected_at=datetime.now(),
                metrics={
                    'historical_rollback_rate': rollback_rate,
                    'similar_executions': len(similar)
                }
            ))
        
        # Anomaly 3: Risk score vs outcome mismatch
        if current_execution.risk_score < 0.3 and not current_execution.deployment_success:
            anomalies.append(AnomalyReport(
                anomaly_id=f"ANOM-RISK-{current_execution.execution_id}",
                execution_id=current_execution.execution_id,
                anomaly_type='risk_mismatch',
                severity='medium',
                description=f"Low risk score ({current_execution.risk_score:.2f}) but deployment failed",
                detected_at=datetime.now(),
                metrics={
                    'risk_score': current_execution.risk_score,
                    'deployment_success': current_execution.deployment_success
                }
            ))
        
        if anomalies:
            logger.warning(f"Detected {len(anomalies)} anomalies in execution {current_execution.execution_id}")
        
        return anomalies


# ==================== Predictive Analyzer ====================

class PredictiveAnalyzer:
    """
    Forecast remediation success probability
    
    Predicts likelihood of success before deployment
    """
    
    def __init__(self, db_path: str = 'remediation.db'):
        self.db_path = db_path
    
    def predict_success(
        self,
        execution_id: str,
        asset_type: str,
        risk_score: float,
        test_success_rate: float,
        selected_strategy: str,
        training_data: List[TrainingData]
    ) -> SuccessPrediction:
        """
        Predict remediation success probability
        
        Args:
            execution_id: Current execution ID
            asset_type: Type of asset
            risk_score: Calculated risk score
            test_success_rate: Sandbox test success
            selected_strategy: Chosen deployment strategy
            training_data: Historical data
            
        Returns:
            Success prediction with confidence
        """
        # Find similar historical cases
        similar = [
            td for td in training_data
            if td.asset_type == asset_type
            and abs(td.risk_score - risk_score) < 0.15
            and td.selected_strategy == selected_strategy
        ]
        
        if not similar:
            return self._fallback_prediction(execution_id, risk_score, test_success_rate)
        
        # Calculate success probability
        success_count = sum(1 for td in similar if td.deployment_success)
        success_probability = success_count / len(similar)
        
        # Adjust based on test success rate
        if test_success_rate < 0.8:
            success_probability *= 0.8  # Reduce confidence
        elif test_success_rate > 0.95:
            success_probability = min(success_probability * 1.1, 1.0)  # Increase confidence
        
        # Identify risk factors
        risk_factors = []
        if risk_score > 0.7:
            risk_factors.append("High risk score")
        if test_success_rate < 0.9:
            risk_factors.append("Test success rate below threshold")
        
        rollback_rate = sum(1 for td in similar if td.rollback_occurred) / len(similar)
        if rollback_rate > 0.2:
            risk_factors.append(f"High historical rollback rate ({rollback_rate*100:.1f}%)")
        
        # Estimate duration
        durations = [td.duration_seconds for td in similar]
        estimated_duration = statistics.median(durations)
        
        confidence = min(len(similar) / 15.0, 1.0)
        
        return SuccessPrediction(
            execution_id=execution_id,
            predicted_success=success_probability > 0.7,
            confidence=confidence,
            risk_factors=risk_factors,
            success_probability=success_probability,
            estimated_duration_seconds=estimated_duration
        )
    
    def _fallback_prediction(
        self,
        execution_id: str,
        risk_score: float,
        test_success_rate: float
    ) -> SuccessPrediction:
        """Fallback prediction when no similar cases exist"""
        # Simple heuristic
        base_probability = 1.0 - risk_score
        adjusted_probability = base_probability * test_success_rate
        
        risk_factors = ["No historical data - prediction based on heuristics"]
        if risk_score > 0.7:
            risk_factors.append("High risk score")
        if test_success_rate < 0.9:
            risk_factors.append("Low test success rate")
        
        return SuccessPrediction(
            execution_id=execution_id,
            predicted_success=adjusted_probability > 0.7,
            confidence=0.4,  # Low confidence without data
            risk_factors=risk_factors,
            success_probability=adjusted_probability,
            estimated_duration_seconds=1200.0  # 20 minutes default
        )


# ==================== Exports ====================

__all__ = [
    # Data classes
    'TrainingData',
    'Pattern',
    'RiskCalibration',
    'StrategyRecommendation',
    'AnomalyReport',
    'SuccessPrediction',
    # Enums
    'MLModelType',
    # Components
    'HistoricalDataCollector',
    'PatternRecognizer',
    'RiskScoreOptimizer',
    'StrategyRecommender',
    'AnomalyDetector',
    'PredictiveAnalyzer'
]
