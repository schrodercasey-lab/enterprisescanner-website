"""
Jupiter v3.0 - Module G.1: Risk Analyzer
Autonomous Remediation Engine - Component 1

Analyzes vulnerability and asset characteristics to determine optimal
autonomy level for remediation (0-5 scale).

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Dict, List, Optional, Tuple
import uuid


class AutonomyLevel(IntEnum):
    """
    Remediation autonomy levels (0-5)
    """
    MANUAL_ONLY = 0       # No automation, human decision required
    AI_ASSISTED = 1       # AI provides recommendations, human executes
    SUPERVISED = 2        # AI can execute with real-time human monitoring
    APPROVAL_REQUIRED = 3 # AI executes after human approval
    HIGH_AUTONOMY = 4     # AI executes autonomously with notification
    FULL_AUTONOMY = 5     # AI executes autonomously without notification


@dataclass
class RiskFactors:
    """Individual risk factor scores (0.0-1.0)"""
    severity: float
    exploitability: float
    asset_criticality: float
    patch_maturity: float
    dependencies: float
    rollback_complexity: float
    compliance_impact: float = 0.5
    business_hours: float = 0.5
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RiskAssessment:
    """Complete risk assessment result"""
    assessment_id: str
    vulnerability_id: str
    asset_id: str
    assessed_at: datetime
    model_version: str
    
    # Individual factors
    factors: RiskFactors
    
    # Overall assessment
    total_risk_score: float
    autonomy_level: AutonomyLevel
    confidence: float
    
    # Recommendations
    reasoning: str
    recommended_strategy: str
    recommended_timing: str
    estimated_risk: str
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['factors'] = self.factors.to_dict()
        result['autonomy_level'] = int(self.autonomy_level)
        result['assessed_at'] = self.assessed_at.isoformat()
        return result


class RiskAnalyzer:
    """
    AI-powered risk analyzer for autonomous remediation decisions
    
    Analyzes multiple factors to determine optimal autonomy level:
    - Vulnerability severity and exploitability
    - Asset criticality and dependencies
    - Patch maturity and rollback complexity
    - Compliance requirements and timing
    
    Returns autonomy level (0-5) with confidence score.
    """
    
    # Scoring weights for risk factors
    WEIGHTS = {
        'severity': 0.25,
        'exploitability': 0.20,
        'asset_criticality': 0.20,
        'patch_maturity': 0.15,
        'dependencies': 0.10,
        'rollback_complexity': 0.10
    }
    
    # Autonomy level thresholds
    THRESHOLDS = {
        AutonomyLevel.FULL_AUTONOMY: 0.85,
        AutonomyLevel.HIGH_AUTONOMY: 0.70,
        AutonomyLevel.APPROVAL_REQUIRED: 0.50,
        AutonomyLevel.SUPERVISED: 0.30,
        AutonomyLevel.AI_ASSISTED: 0.15,
        AutonomyLevel.MANUAL_ONLY: 0.0
    }
    
    def __init__(self, db_path: str = "jupiter_remediation.db", ml_model=None):
        """
        Initialize risk analyzer
        
        Args:
            db_path: Path to remediation database
            ml_model: Optional trained ML model for predictions
        """
        self.db_path = db_path
        self.ml_model = ml_model
        self.model_version = "1.0.0-rule-based" if not ml_model else "1.0.0-ml"
        
    def analyze(self, vulnerability: Dict, asset: Dict) -> RiskAssessment:
        """
        Perform comprehensive risk analysis
        
        Args:
            vulnerability: Vulnerability data dict with keys:
                - vuln_id, cve_id, cvss_score, exploit_available, 
                  patch_age_days, etc.
            asset: Asset data dict with keys:
                - asset_id, asset_name, criticality_tier, has_redundancy,
                  uptime_requirement, etc.
        
        Returns:
            RiskAssessment with autonomy level and confidence
        """
        # Calculate individual risk factors
        factors = RiskFactors(
            severity=self._analyze_severity(vulnerability),
            exploitability=self._analyze_exploitability(vulnerability),
            asset_criticality=self._analyze_asset_criticality(asset),
            patch_maturity=self._analyze_patch_maturity(vulnerability),
            dependencies=self._analyze_dependencies(asset),
            rollback_complexity=self._analyze_rollback_complexity(asset),
            compliance_impact=self._analyze_compliance(asset),
            business_hours=self._check_business_hours()
        )
        
        # Calculate autonomy level
        if self.ml_model:
            autonomy_level, confidence = self._ml_predict(factors, vulnerability, asset)
        else:
            autonomy_level, confidence = self._rule_based_predict(factors)
        
        # Determine deployment strategy
        strategy = self._recommend_strategy(autonomy_level, asset)
        
        # Determine timing
        timing = self._recommend_timing(autonomy_level, factors, asset)
        
        # Estimate overall risk level
        risk_level = self._estimate_risk_level(factors)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(factors, autonomy_level, vulnerability, asset)
        
        # Create assessment
        assessment = RiskAssessment(
            assessment_id=f"ASSESS-{uuid.uuid4().hex[:12].upper()}",
            vulnerability_id=vulnerability['vuln_id'],
            asset_id=asset['asset_id'],
            assessed_at=datetime.utcnow(),
            model_version=self.model_version,
            factors=factors,
            total_risk_score=self._calculate_total_score(factors),
            autonomy_level=AutonomyLevel(autonomy_level),
            confidence=confidence,
            reasoning=reasoning,
            recommended_strategy=strategy,
            recommended_timing=timing,
            estimated_risk=risk_level
        )
        
        # Save to database
        self._save_assessment(assessment)
        
        return assessment
    
    def _analyze_severity(self, vulnerability: Dict) -> float:
        """
        Analyze vulnerability severity (0.0-1.0)
        Higher score = more severe = higher autonomy justified
        """
        cvss = vulnerability.get('cvss_score', 0.0)
        
        if cvss >= 9.0:
            return 1.0  # Critical - immediate autonomous action
        elif cvss >= 7.0:
            return 0.7  # High - autonomous OK with monitoring
        elif cvss >= 4.0:
            return 0.4  # Medium - may require approval
        else:
            return 0.2  # Low - can wait for maintenance window
    
    def _analyze_exploitability(self, vulnerability: Dict) -> float:
        """
        Analyze exploit availability (0.0-1.0)
        Higher score = actively exploited = urgent autonomous action
        """
        # Check various exploit indicators
        if vulnerability.get('exploit_in_wild', False):
            return 1.0  # Active exploitation - URGENT
        elif vulnerability.get('exploit_poc_available', False):
            return 0.7  # PoC exists - HIGH priority
        elif vulnerability.get('exploit_predicted_soon', False):
            return 0.5  # Predicted exploitation - MEDIUM
        elif vulnerability.get('weaponized', False):
            return 0.8  # Weaponized exploit - VERY HIGH
        else:
            return 0.3  # No known exploit - STANDARD
    
    def _analyze_asset_criticality(self, asset: Dict) -> float:
        """
        Analyze asset criticality (0.0-1.0)
        LOWER criticality = HIGHER autonomy OK (inverted scoring)
        """
        tier = asset.get('criticality_tier', 3)
        
        if tier == 1:  # Tier 1: Mission-critical
            return 0.3  # Low autonomy - require careful review
        elif tier == 2:  # Tier 2: Business-critical
            return 0.6  # Medium autonomy - autonomous with notification
        else:  # Tier 3: Standard
            return 1.0  # High autonomy - full autonomous OK
    
    def _analyze_patch_maturity(self, vulnerability: Dict) -> float:
        """
        Analyze patch maturity (0.0-1.0)
        Older patches = more tested = higher autonomy OK
        """
        patch_age_days = vulnerability.get('patch_age_days', 0)
        
        if patch_age_days >= 30:
            return 1.0  # Mature patch - widely tested
        elif patch_age_days >= 14:
            return 0.7  # Moderately mature - reasonably safe
        elif patch_age_days >= 7:
            return 0.5  # New patch - some risk
        elif patch_age_days >= 1:
            return 0.3  # Very new - higher risk
        else:
            return 0.1  # Same-day patch - proceed with caution
    
    def _analyze_dependencies(self, asset: Dict) -> float:
        """
        Analyze dependency complexity (0.0-1.0)
        Fewer dependencies = higher autonomy OK
        """
        dependency_count = asset.get('dependency_count', 0)
        has_dependents = asset.get('has_dependents', False)
        
        if dependency_count == 0 and not has_dependents:
            return 1.0  # Isolated asset - safe to patch
        elif dependency_count <= 3 and not has_dependents:
            return 0.7  # Few dependencies - manageable
        elif dependency_count <= 10:
            return 0.5  # Moderate dependencies - careful testing needed
        else:
            return 0.3  # Complex dependencies - high risk
    
    def _analyze_rollback_complexity(self, asset: Dict) -> float:
        """
        Analyze rollback ease (0.0-1.0)
        Easier rollback = higher autonomy OK
        """
        asset_type = asset.get('asset_type', 'unknown')
        has_backup = asset.get('has_backup', False)
        has_redundancy = asset.get('has_redundancy', False)
        
        # Scoring based on asset type
        type_scores = {
            'container': 1.0,      # Easy rollback (new container)
            'kubernetes': 0.9,     # Very easy (helm rollback)
            'vm': 0.7,             # Moderate (snapshot restore)
            'baremetal': 0.4,      # Harder (physical server)
            'database': 0.3,       # Complex (data consistency)
            'unknown': 0.5
        }
        
        base_score = type_scores.get(asset_type, 0.5)
        
        # Adjust for backup availability
        if has_backup:
            base_score += 0.1
        if has_redundancy:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _analyze_compliance(self, asset: Dict) -> float:
        """
        Analyze compliance impact (0.0-1.0)
        Lower compliance requirements = higher autonomy OK
        """
        compliance_frameworks = asset.get('compliance_frameworks', [])
        
        # High-impact frameworks
        high_impact = ['PCI-DSS', 'HIPAA', 'SOX', 'FISMA']
        
        if any(fw in high_impact for fw in compliance_frameworks):
            return 0.4  # Strict compliance - require audit trail
        elif len(compliance_frameworks) > 0:
            return 0.6  # Some compliance - document well
        else:
            return 1.0  # No special compliance - full autonomy OK
    
    def _check_business_hours(self) -> float:
        """
        Check if current time is business hours (0.0-1.0)
        Outside business hours = higher autonomy OK
        """
        now = datetime.now()
        
        # Business hours: Monday-Friday, 9 AM - 5 PM
        is_weekend = now.weekday() >= 5
        is_business_hours = 9 <= now.hour < 17
        
        if is_weekend or not is_business_hours:
            return 1.0  # Off-hours - safe to patch
        else:
            return 0.5  # Business hours - proceed with caution
    
    def _calculate_total_score(self, factors: RiskFactors) -> float:
        """
        Calculate weighted total risk score (0.0-1.0)
        """
        score = (
            factors.severity * self.WEIGHTS['severity'] +
            factors.exploitability * self.WEIGHTS['exploitability'] +
            factors.asset_criticality * self.WEIGHTS['asset_criticality'] +
            factors.patch_maturity * self.WEIGHTS['patch_maturity'] +
            factors.dependencies * self.WEIGHTS['dependencies'] +
            factors.rollback_complexity * self.WEIGHTS['rollback_complexity']
        )
        
        return round(score, 3)
    
    def _rule_based_predict(self, factors: RiskFactors) -> Tuple[int, float]:
        """
        Rule-based autonomy level prediction
        
        Returns:
            (autonomy_level, confidence)
        """
        total_score = self._calculate_total_score(factors)
        
        # Map score to autonomy level using thresholds
        for level in sorted(self.THRESHOLDS.keys(), reverse=True):
            if total_score >= self.THRESHOLDS[level]:
                # Calculate confidence based on distance from threshold
                if level == AutonomyLevel.FULL_AUTONOMY:
                    confidence = 0.85 + (total_score - self.THRESHOLDS[level]) * 0.5
                else:
                    confidence = 0.75 + (total_score - self.THRESHOLDS[level]) * 0.3
                
                confidence = min(confidence, 0.99)
                return int(level), round(confidence, 3)
        
        # Default to manual if score is very low
        return int(AutonomyLevel.MANUAL_ONLY), 0.60
    
    def _ml_predict(self, factors: RiskFactors, vulnerability: Dict, asset: Dict) -> Tuple[int, float]:
        """
        ML model-based prediction (to be implemented)
        
        Returns:
            (autonomy_level, confidence)
        """
        # TODO: Implement ML prediction
        # For now, fall back to rule-based
        return self._rule_based_predict(factors)
    
    def _recommend_strategy(self, autonomy_level: int, asset: Dict) -> str:
        """
        Recommend deployment strategy based on autonomy level and asset
        """
        asset_type = asset.get('asset_type', 'unknown')
        has_redundancy = asset.get('has_redundancy', False)
        
        if autonomy_level >= AutonomyLevel.HIGH_AUTONOMY:
            if has_redundancy or asset_type == 'kubernetes':
                return 'blue-green'  # Zero downtime
            else:
                return 'canary'  # Gradual rollout
        elif autonomy_level >= AutonomyLevel.APPROVAL_REQUIRED:
            return 'rolling'  # Phased deployment
        else:
            return 'all-at-once'  # Maintenance window
    
    def _recommend_timing(self, autonomy_level: int, factors: RiskFactors, asset: Dict) -> str:
        """
        Recommend when to execute remediation
        """
        if factors.exploitability >= 0.9:
            return 'immediate'  # Active exploitation - NOW
        elif autonomy_level >= AutonomyLevel.HIGH_AUTONOMY:
            if factors.business_hours >= 0.9:
                return 'immediate'  # Off-hours - safe to execute
            else:
                return 'next_off_hours'  # Wait for off-hours
        elif autonomy_level >= AutonomyLevel.APPROVAL_REQUIRED:
            return 'business_hours'  # During business hours with approval
        else:
            return 'maintenance_window'  # Scheduled maintenance
    
    def _estimate_risk_level(self, factors: RiskFactors) -> str:
        """
        Estimate overall risk level
        """
        severity = factors.severity
        exploitability = factors.exploitability
        
        combined_risk = (severity * 0.6) + (exploitability * 0.4)
        
        if combined_risk >= 0.9:
            return 'CRITICAL'
        elif combined_risk >= 0.7:
            return 'HIGH'
        elif combined_risk >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_reasoning(self, factors: RiskFactors, autonomy_level: int, 
                           vulnerability: Dict, asset: Dict) -> str:
        """
        Generate human-readable explanation of decision
        """
        reasons = []
        
        # Severity
        if factors.severity >= 0.9:
            reasons.append(f"Critical vulnerability (CVSS {vulnerability.get('cvss_score', 'N/A')})")
        elif factors.severity >= 0.7:
            reasons.append("High severity vulnerability")
        
        # Exploitability
        if factors.exploitability >= 0.9:
            reasons.append("Active exploitation detected in the wild")
        elif factors.exploitability >= 0.7:
            reasons.append("Proof-of-concept exploit available")
        
        # Asset
        tier = asset.get('criticality_tier', 3)
        if tier == 1:
            reasons.append("Mission-critical asset requires careful handling")
        elif tier == 3:
            reasons.append("Standard asset suitable for autonomous remediation")
        
        # Patch maturity
        if factors.patch_maturity >= 0.9:
            reasons.append("Well-tested patch (30+ days old)")
        elif factors.patch_maturity <= 0.3:
            reasons.append("New patch - proceed with caution")
        
        # Rollback
        if factors.rollback_complexity >= 0.8:
            reasons.append("Easy rollback available")
        elif factors.rollback_complexity <= 0.4:
            reasons.append("Complex rollback - extensive testing required")
        
        # Timing
        if factors.business_hours >= 0.9:
            reasons.append("Off-hours timing favorable for deployment")
        
        # Decision
        level_actions = {
            5: "Full autonomous remediation recommended",
            4: "Autonomous remediation with notification",
            3: "Require human approval before execution",
            2: "Human-supervised autonomous execution",
            1: "AI-assisted manual remediation",
            0: "Manual-only remediation"
        }
        
        action = level_actions.get(autonomy_level, "Manual remediation")
        
        if reasons:
            return f"{action}. Factors: {', '.join(reasons)}."
        else:
            return f"{action}. Standard risk profile."
    
    def _save_assessment(self, assessment: RiskAssessment) -> None:
        """
        Save assessment to database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO risk_assessments (
                    assessment_id, vulnerability_id, asset_id, assessed_at, model_version,
                    severity_score, exploitability_score, asset_criticality_score,
                    patch_maturity_score, dependency_score, rollback_score,
                    compliance_score, business_hours_score,
                    total_risk_score, autonomy_level, confidence,
                    reasoning, factors_json, recommended_strategy, recommended_timing,
                    estimated_risk
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment.assessment_id,
                assessment.vulnerability_id,
                assessment.asset_id,
                assessment.assessed_at.isoformat(),
                assessment.model_version,
                assessment.factors.severity,
                assessment.factors.exploitability,
                assessment.factors.asset_criticality,
                assessment.factors.patch_maturity,
                assessment.factors.dependencies,
                assessment.factors.rollback_complexity,
                assessment.factors.compliance_impact,
                assessment.factors.business_hours,
                assessment.total_risk_score,
                int(assessment.autonomy_level),
                assessment.confidence,
                assessment.reasoning,
                json.dumps(assessment.factors.to_dict()),
                assessment.recommended_strategy,
                assessment.recommended_timing,
                assessment.estimated_risk
            ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to save risk assessment: {str(e)}")
        finally:
            conn.close()
    
    def get_assessment(self, assessment_id: str) -> Optional[RiskAssessment]:
        """
        Retrieve assessment from database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM risk_assessments WHERE assessment_id = ?
            """, (assessment_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Reconstruct RiskAssessment object
            # (Implementation details omitted for brevity)
            return None  # Placeholder
            
        finally:
            conn.close()


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = RiskAnalyzer(db_path="jupiter_remediation.db")
    
    # Example vulnerability
    vulnerability = {
        'vuln_id': 'VULN-12345',
        'cve_id': 'CVE-2024-9823',
        'cvss_score': 9.8,
        'exploit_in_wild': True,
        'patch_age_days': 15
    }
    
    # Example asset
    asset = {
        'asset_id': 'ASSET-67890',
        'asset_name': 'web-server-prod-01',
        'asset_type': 'kubernetes',
        'criticality_tier': 2,
        'has_redundancy': True,
        'has_backup': True,
        'dependency_count': 3,
        'compliance_frameworks': ['SOC2', 'ISO27001']
    }
    
    # Analyze
    assessment = analyzer.analyze(vulnerability, asset)
    
    # Print results
    print(f"Assessment ID: {assessment.assessment_id}")
    print(f"Autonomy Level: {assessment.autonomy_level.name} ({assessment.autonomy_level})")
    print(f"Confidence: {assessment.confidence * 100:.1f}%")
    print(f"Total Risk Score: {assessment.total_risk_score}")
    print(f"Recommended Strategy: {assessment.recommended_strategy}")
    print(f"Recommended Timing: {assessment.recommended_timing}")
    print(f"Estimated Risk: {assessment.estimated_risk}")
    print(f"Reasoning: {assessment.reasoning}")
