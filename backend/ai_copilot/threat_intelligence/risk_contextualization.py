"""
Module G.2.7: Risk Contextualization Engine
============================================

Purpose: Contextualize threat intelligence with business impact, asset criticality,
         and organizational priorities to enable risk-based decision making.

Features:
- Asset-threat correlation and exposure analysis
- Business impact scoring (financial, operational, reputational)
- Remediation priority ranking (risk-based)
- Risk decay modeling (urgency over time)
- Attack surface analysis and mapping
- Criticality-weighted risk scoring
- Exploitability vs. impact matrix
- Crown jewel asset protection

Author: Enterprise Scanner AI Development Team
Version: 1.0.0
Created: October 17, 2025
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import math


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetCriticality(Enum):
    """Asset criticality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CROWN_JEWEL = "crown_jewel"


class BusinessImpact(Enum):
    """Business impact categories"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    REPUTATIONAL = "reputational"
    COMPLIANCE = "compliance"
    STRATEGIC = "strategic"


class RemediationUrgency(Enum):
    """Remediation urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Asset:
    """Represents an organizational asset"""
    asset_id: str
    asset_name: str
    asset_type: str  # server, application, database, endpoint, network_device
    criticality: AssetCriticality = AssetCriticality.MEDIUM
    business_value: float = 0.0  # 0.0-1.0
    exposure_score: float = 0.0  # 0.0-1.0 (internet-facing, etc.)
    owner: str = ""
    department: str = ""
    data_classification: str = ""  # public, internal, confidential, restricted
    dependencies: List[str] = field(default_factory=list)  # Dependent asset IDs
    
    def get_criticality_multiplier(self) -> float:
        """Get risk multiplier based on criticality"""
        multipliers = {
            AssetCriticality.LOW: 0.5,
            AssetCriticality.MEDIUM: 1.0,
            AssetCriticality.HIGH: 1.5,
            AssetCriticality.CRITICAL: 2.0,
            AssetCriticality.CROWN_JEWEL: 3.0
        }
        return multipliers.get(self.criticality, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'asset_id': self.asset_id,
            'asset_name': self.asset_name,
            'asset_type': self.asset_type,
            'criticality': self.criticality.value,
            'business_value': self.business_value,
            'exposure_score': self.exposure_score,
            'data_classification': self.data_classification
        }


@dataclass
class AssetThreatExposure:
    """Represents threat exposure for an asset"""
    exposure_id: Optional[int] = None
    asset_id: str = ""
    threat_type: str = ""  # vulnerability, campaign, actor, technique
    threat_id: str = ""
    threat_name: str = ""
    base_risk_score: float = 0.0  # Raw threat risk (0-100)
    contextualized_risk_score: float = 0.0  # With business context (0-100)
    exploitability: float = 0.5  # 0.0-1.0
    impact_score: float = 0.5  # 0.0-1.0
    urgency: RemediationUrgency = RemediationUrgency.MEDIUM
    estimated_remediation_hours: int = 0
    remediation_cost: float = 0.0
    potential_loss: float = 0.0  # Financial impact if exploited
    first_detected: Optional[datetime] = None
    days_exposed: int = 0
    
    def calculate_priority_score(self) -> float:
        """Calculate remediation priority (0-100)"""
        # Factors: risk, exploitability, days exposed, urgency
        priority = 0.0
        
        # Base risk (40 points)
        priority += (self.contextualized_risk_score / 100) * 40
        
        # Exploitability (20 points)
        priority += self.exploitability * 20
        
        # Time urgency (20 points)
        urgency_scores = {
            RemediationUrgency.LOW: 4,
            RemediationUrgency.MEDIUM: 8,
            RemediationUrgency.HIGH: 12,
            RemediationUrgency.CRITICAL: 16,
            RemediationUrgency.EMERGENCY: 20
        }
        priority += urgency_scores.get(self.urgency, 8)
        
        # Days exposed (20 points, logarithmic)
        if self.days_exposed > 0:
            time_factor = min(20, math.log(self.days_exposed + 1) * 5)
            priority += time_factor
        
        return min(100.0, priority)
    
    def get_roi(self) -> float:
        """Calculate ROI of remediation (potential loss / cost)"""
        if self.remediation_cost > 0:
            return self.potential_loss / self.remediation_cost
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'exposure_id': self.exposure_id,
            'asset_id': self.asset_id,
            'threat_name': self.threat_name,
            'base_risk_score': self.base_risk_score,
            'contextualized_risk_score': self.contextualized_risk_score,
            'priority_score': self.calculate_priority_score(),
            'urgency': self.urgency.value,
            'days_exposed': self.days_exposed,
            'estimated_hours': self.estimated_remediation_hours,
            'roi': self.get_roi()
        }


@dataclass
class RemediationRecommendation:
    """Remediation recommendation with prioritization"""
    recommendation_id: Optional[int] = None
    asset_id: str = ""
    threat_id: str = ""
    recommendation: str = ""
    priority_score: float = 0.0
    urgency: RemediationUrgency = RemediationUrgency.MEDIUM
    estimated_effort: str = ""  # Low, Medium, High
    estimated_hours: int = 0
    estimated_cost: float = 0.0
    risk_reduction: float = 0.0  # 0.0-100.0
    dependencies: List[str] = field(default_factory=list)
    sla_deadline: Optional[datetime] = None
    
    def is_overdue(self) -> bool:
        """Check if recommendation is past SLA"""
        if self.sla_deadline:
            return datetime.now() > self.sla_deadline
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'recommendation_id': self.recommendation_id,
            'asset_id': self.asset_id,
            'recommendation': self.recommendation,
            'priority_score': self.priority_score,
            'urgency': self.urgency.value,
            'estimated_effort': self.estimated_effort,
            'risk_reduction': self.risk_reduction,
            'is_overdue': self.is_overdue()
        }


# =============================================================================
# Risk Contextualization Engine
# =============================================================================

class RiskContextualizationEngine:
    """
    Contextualize threat intelligence with business impact
    
    Capabilities:
    - Asset-threat correlation
    - Business impact scoring
    - Remediation priority ranking
    - Risk decay modeling
    - Attack surface analysis
    - Criticality weighting
    - Exploitability vs. impact matrix
    - ROI-based prioritization
    """
    
    # Business impact weights by data classification
    DATA_CLASSIFICATION_WEIGHTS = {
        'public': 0.2,
        'internal': 0.5,
        'confidential': 0.8,
        'restricted': 1.0
    }
    
    # Remediation effort estimates (hours) by threat type
    EFFORT_ESTIMATES = {
        'patch': 2,
        'configuration': 4,
        'architectural': 40,
        'process': 20,
        'monitoring': 8
    }
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        """
        Initialize risk contextualization engine
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.assets: Dict[str, Asset] = {}
        self.exposures: List[AssetThreatExposure] = []
        
        # Load assets
        self._load_assets()
        
        logger.info(f"RiskContextualizationEngine initialized with {len(self.assets)} assets")
    
    def _load_assets(self) -> None:
        """Load assets from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Note: This assumes an assets table exists
            # In production, integrate with CMDB/asset management system
            cursor.execute("""
                SELECT asset_id, asset_name, asset_type, criticality,
                       business_value, exposure_score, owner, department,
                       data_classification
                FROM assets
                WHERE is_active = 1
            """)
            
            for row in cursor.fetchall():
                try:
                    asset = Asset(
                        asset_id=row[0],
                        asset_name=row[1],
                        asset_type=row[2],
                        criticality=AssetCriticality(row[3]) if row[3] else AssetCriticality.MEDIUM,
                        business_value=row[4] if row[4] else 0.5,
                        exposure_score=row[5] if row[5] else 0.0,
                        owner=row[6] if row[6] else "",
                        department=row[7] if row[7] else "",
                        data_classification=row[8] if row[8] else "internal"
                    )
                    self.assets[asset.asset_id] = asset
                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping invalid asset: {e}")
            
            conn.close()
            logger.info(f"Loaded {len(self.assets)} assets")
            
        except sqlite3.OperationalError:
            # Assets table doesn't exist - create sample assets
            logger.warning("Assets table not found, using sample data")
            self._create_sample_assets()
    
    def _create_sample_assets(self) -> None:
        """Create sample assets for demonstration"""
        sample_assets = [
            Asset("ASSET-001", "Production Database", "database", 
                  AssetCriticality.CRITICAL, 0.95, 0.2, "DBA Team", "IT", "restricted"),
            Asset("ASSET-002", "Web Application Server", "server",
                  AssetCriticality.HIGH, 0.8, 0.9, "DevOps", "Engineering", "confidential"),
            Asset("ASSET-003", "Customer Portal", "application",
                  AssetCriticality.CROWN_JEWEL, 1.0, 1.0, "Product", "Engineering", "restricted"),
            Asset("ASSET-004", "Employee Workstation", "endpoint",
                  AssetCriticality.MEDIUM, 0.5, 0.3, "IT", "IT", "internal"),
            Asset("ASSET-005", "Development Server", "server",
                  AssetCriticality.LOW, 0.3, 0.5, "DevOps", "Engineering", "internal")
        ]
        
        for asset in sample_assets:
            self.assets[asset.asset_id] = asset
    
    def correlate_asset_threats(self, asset_id: str) -> List[AssetThreatExposure]:
        """
        Correlate threats affecting specific asset
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            List of threat exposures
        """
        exposures = []
        
        if asset_id not in self.assets:
            logger.warning(f"Asset {asset_id} not found")
            return exposures
        
        asset = self.assets[asset_id]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get vulnerabilities affecting asset
            cursor.execute("""
                SELECT v.vulnerability_id, v.cve_id, v.cvss_score, v.epss_score,
                       v.has_exploit, v.exploited_in_wild, v.published_date,
                       ate.exposure_level, ate.is_exploitable
                FROM threat_vulnerabilities v
                JOIN asset_threat_exposure ate ON v.vulnerability_id = ate.threat_id
                WHERE ate.asset_id = ?
                  AND ate.threat_type = 'vulnerability'
                  AND ate.is_mitigated = 0
            """, (asset_id,))
            
            for row in cursor.fetchall():
                vuln_id = row[0]
                cve_id = row[1]
                cvss_score = row[2] if row[2] else 0.0
                epss_score = row[3] if row[3] else 0.0
                has_exploit = bool(row[4])
                exploited_wild = bool(row[5])
                published_date_str = row[6]
                exposure_level = row[7] if row[7] else 0.5
                is_exploitable = bool(row[8])
                
                # Calculate base risk
                base_risk = cvss_score * 10  # CVSS is 0-10, scale to 0-100
                
                # Calculate exploitability
                exploitability = 0.3  # Base
                if is_exploitable:
                    exploitability += 0.2
                if has_exploit:
                    exploitability += 0.2
                if exploited_wild:
                    exploitability += 0.3
                exploitability = min(1.0, exploitability + (epss_score * 0.3))
                
                # Calculate impact based on asset criticality
                impact_score = asset.business_value * asset.get_criticality_multiplier() / 3.0
                impact_score = min(1.0, impact_score)
                
                # Contextualized risk = base risk * criticality multiplier * exposure
                contextualized_risk = base_risk * asset.get_criticality_multiplier() * (1 + exposure_level)
                contextualized_risk = min(100.0, contextualized_risk)
                
                # Calculate days exposed
                if published_date_str:
                    published_date = datetime.fromisoformat(published_date_str)
                    days_exposed = (datetime.now() - published_date).days
                else:
                    days_exposed = 0
                
                # Determine urgency
                urgency = self._calculate_urgency(contextualized_risk, exploitability, days_exposed)
                
                # Estimate remediation effort
                estimated_hours = self.EFFORT_ESTIMATES.get('patch', 2)
                remediation_cost = estimated_hours * 150  # $150/hour rate
                
                # Potential loss (rough estimate)
                potential_loss = asset.business_value * 1000000 * (contextualized_risk / 100)
                
                exposure = AssetThreatExposure(
                    asset_id=asset_id,
                    threat_type="vulnerability",
                    threat_id=str(vuln_id),
                    threat_name=cve_id,
                    base_risk_score=base_risk,
                    contextualized_risk_score=contextualized_risk,
                    exploitability=exploitability,
                    impact_score=impact_score,
                    urgency=urgency,
                    estimated_remediation_hours=estimated_hours,
                    remediation_cost=remediation_cost,
                    potential_loss=potential_loss,
                    first_detected=published_date if published_date_str else datetime.now(),
                    days_exposed=days_exposed
                )
                
                exposures.append(exposure)
                self._save_exposure(exposure)
            
            conn.close()
            logger.info(f"Found {len(exposures)} threat exposures for asset {asset_id}")
            
        except Exception as e:
            logger.error(f"Error correlating asset threats: {e}")
        
        return exposures
    
    def _calculate_urgency(
        self,
        risk_score: float,
        exploitability: float,
        days_exposed: int
    ) -> RemediationUrgency:
        """Calculate remediation urgency"""
        
        # Emergency: Critical risk + exploited in wild
        if risk_score >= 90 and exploitability >= 0.8:
            return RemediationUrgency.EMERGENCY
        
        # Critical: High risk + exploitable
        if risk_score >= 70 and exploitability >= 0.6:
            return RemediationUrgency.CRITICAL
        
        # High: Medium-high risk or long exposure
        if risk_score >= 50 or days_exposed > 90:
            return RemediationUrgency.HIGH
        
        # Medium: Moderate risk
        if risk_score >= 30:
            return RemediationUrgency.MEDIUM
        
        # Low: Everything else
        return RemediationUrgency.LOW
    
    def prioritize_remediation(
        self,
        exposures: Optional[List[AssetThreatExposure]] = None,
        max_results: int = 50
    ) -> List[AssetThreatExposure]:
        """
        Prioritize threat remediation across all assets
        
        Args:
            exposures: Optional specific exposures, or all if None
            max_results: Maximum results to return
            
        Returns:
            Sorted list by priority
        """
        if exposures is None:
            exposures = self.exposures
        
        # Sort by priority score
        prioritized = sorted(
            exposures,
            key=lambda e: e.calculate_priority_score(),
            reverse=True
        )
        
        return prioritized[:max_results]
    
    def analyze_attack_surface(self) -> Dict[str, Any]:
        """
        Analyze organizational attack surface
        
        Returns:
            Attack surface analysis
        """
        analysis = {
            'total_assets': len(self.assets),
            'by_criticality': {},
            'by_exposure': {},
            'internet_facing': 0,
            'crown_jewels': 0,
            'high_value_exposed': 0,
            'attack_surface_score': 0.0
        }
        
        # Count by criticality
        for asset in self.assets.values():
            crit = asset.criticality.value
            analysis['by_criticality'][crit] = analysis['by_criticality'].get(crit, 0) + 1
            
            if asset.criticality == AssetCriticality.CROWN_JEWEL:
                analysis['crown_jewels'] += 1
            
            if asset.exposure_score > 0.7:
                analysis['internet_facing'] += 1
                
                if asset.business_value > 0.7:
                    analysis['high_value_exposed'] += 1
        
        # Calculate attack surface score (0-100)
        surface_score = 0.0
        
        # Internet-facing assets (40 points)
        surface_score += min(40, analysis['internet_facing'] * 4)
        
        # High-value exposed (30 points)
        surface_score += min(30, analysis['high_value_exposed'] * 6)
        
        # Crown jewels (30 points if exposed)
        for asset in self.assets.values():
            if asset.criticality == AssetCriticality.CROWN_JEWEL and asset.exposure_score > 0.5:
                surface_score += 10
        
        analysis['attack_surface_score'] = min(100, surface_score)
        
        return analysis
    
    def model_risk_decay(
        self,
        exposure: AssetThreatExposure,
        days_forward: int = 30
    ) -> Dict[int, float]:
        """
        Model risk decay/escalation over time
        
        Args:
            exposure: Threat exposure
            days_forward: Days to project
            
        Returns:
            Dict of day -> risk score
        """
        decay_model = {}
        
        current_risk = exposure.contextualized_risk_score
        exploitability = exposure.exploitability
        
        for day in range(days_forward + 1):
            # Risk increases over time for exploitable vulnerabilities
            if exploitability > 0.5:
                # Exponential growth for highly exploitable
                growth_factor = 1 + (day * 0.02 * exploitability)
                risk = current_risk * growth_factor
            else:
                # Slow linear growth for less exploitable
                risk = current_risk + (day * 0.1)
            
            decay_model[day] = min(100.0, risk)
        
        return decay_model
    
    def generate_remediation_recommendations(
        self,
        asset_id: str
    ) -> List[RemediationRecommendation]:
        """
        Generate remediation recommendations for asset
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Get exposures for asset
        exposures = self.correlate_asset_threats(asset_id)
        
        for exposure in exposures:
            # Determine effort level
            if exposure.estimated_remediation_hours <= 4:
                effort = "Low"
            elif exposure.estimated_remediation_hours <= 20:
                effort = "Medium"
            else:
                effort = "High"
            
            # Calculate SLA deadline based on urgency
            sla_days = {
                RemediationUrgency.EMERGENCY: 1,
                RemediationUrgency.CRITICAL: 7,
                RemediationUrgency.HIGH: 30,
                RemediationUrgency.MEDIUM: 90,
                RemediationUrgency.LOW: 180
            }
            
            deadline = datetime.now() + timedelta(days=sla_days.get(exposure.urgency, 90))
            
            # Risk reduction (percentage of contextualized risk)
            risk_reduction = exposure.contextualized_risk_score * 0.9  # 90% reduction
            
            recommendation = RemediationRecommendation(
                asset_id=asset_id,
                threat_id=exposure.threat_id,
                recommendation=f"Remediate {exposure.threat_name} on {asset_id}",
                priority_score=exposure.calculate_priority_score(),
                urgency=exposure.urgency,
                estimated_effort=effort,
                estimated_hours=exposure.estimated_remediation_hours,
                estimated_cost=exposure.remediation_cost,
                risk_reduction=risk_reduction,
                sla_deadline=deadline
            )
            
            recommendations.append(recommendation)
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority_score, reverse=True)
        
        return recommendations
    
    def calculate_business_impact(
        self,
        asset: Asset,
        threat_type: str
    ) -> Dict[str, float]:
        """
        Calculate multi-dimensional business impact
        
        Args:
            asset: Asset object
            threat_type: Type of threat
            
        Returns:
            Dict of impact categories
        """
        impact = {
            'financial': 0.0,
            'operational': 0.0,
            'reputational': 0.0,
            'compliance': 0.0,
            'strategic': 0.0
        }
        
        # Base impact from asset value
        base_impact = asset.business_value * asset.get_criticality_multiplier()
        
        # Financial impact
        impact['financial'] = base_impact * 0.3
        
        # Operational impact (higher for critical systems)
        if asset.criticality in [AssetCriticality.CRITICAL, AssetCriticality.CROWN_JEWEL]:
            impact['operational'] = base_impact * 0.4
        else:
            impact['operational'] = base_impact * 0.2
        
        # Reputational impact (higher for customer-facing)
        if asset.exposure_score > 0.7:
            impact['reputational'] = base_impact * 0.3
        
        # Compliance impact (higher for regulated data)
        data_weight = self.DATA_CLASSIFICATION_WEIGHTS.get(asset.data_classification, 0.5)
        impact['compliance'] = base_impact * data_weight * 0.25
        
        # Strategic impact (higher for crown jewels)
        if asset.criticality == AssetCriticality.CROWN_JEWEL:
            impact['strategic'] = base_impact * 0.5
        
        return impact
    
    def _save_exposure(self, exposure: AssetThreatExposure) -> None:
        """Save exposure to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO asset_threat_exposure (
                    asset_id, threat_type, threat_id,
                    base_risk_score, contextualized_risk_score,
                    exploitability_score, impact_score,
                    remediation_urgency, estimated_effort_hours,
                    potential_loss_amount, first_detected_date,
                    days_exposed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                exposure.asset_id,
                exposure.threat_type,
                exposure.threat_id,
                exposure.base_risk_score,
                exposure.contextualized_risk_score,
                exposure.exploitability,
                exposure.impact_score,
                exposure.urgency.value,
                exposure.estimated_remediation_hours,
                exposure.potential_loss,
                exposure.first_detected.isoformat() if exposure.first_detected else None,
                exposure.days_exposed
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.debug(f"Error saving exposure: {e}")
    
    def get_contextualization_summary(self) -> Dict[str, Any]:
        """Get summary of risk contextualization"""
        return {
            'total_assets': len(self.assets),
            'total_exposures': len(self.exposures),
            'crown_jewels': sum(1 for a in self.assets.values() if a.criticality == AssetCriticality.CROWN_JEWEL),
            'high_priority_items': sum(1 for e in self.exposures if e.urgency in [RemediationUrgency.CRITICAL, RemediationUrgency.EMERGENCY]),
            'attack_surface': self.analyze_attack_surface(),
            'timestamp': datetime.now().isoformat()
        }


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize engine
    engine = RiskContextualizationEngine()
    
    # Analyze attack surface
    print("\n=== Attack Surface Analysis ===")
    surface = engine.analyze_attack_surface()
    print(f"Total Assets: {surface['total_assets']}")
    print(f"Crown Jewels: {surface['crown_jewels']}")
    print(f"Internet-Facing: {surface['internet_facing']}")
    print(f"High-Value Exposed: {surface['high_value_exposed']}")
    print(f"Attack Surface Score: {surface['attack_surface_score']:.1f}/100")
    
    # Correlate threats for sample asset
    if engine.assets:
        sample_asset_id = list(engine.assets.keys())[0]
        print(f"\n=== Threat Exposure for {sample_asset_id} ===")
        
        exposures = engine.correlate_asset_threats(sample_asset_id)
        for exposure in exposures[:5]:
            print(f"\n{exposure.threat_name}:")
            print(f"  Base Risk: {exposure.base_risk_score:.1f}")
            print(f"  Contextualized Risk: {exposure.contextualized_risk_score:.1f}")
            print(f"  Priority Score: {exposure.calculate_priority_score():.1f}")
            print(f"  Urgency: {exposure.urgency.value}")
            print(f"  ROI: {exposure.get_roi():.1f}x")
        
        # Generate recommendations
        print(f"\n=== Remediation Recommendations ===")
        recommendations = engine.generate_remediation_recommendations(sample_asset_id)
        for rec in recommendations[:3]:
            print(f"\n{rec.recommendation}:")
            print(f"  Priority: {rec.priority_score:.1f}")
            print(f"  Effort: {rec.estimated_effort} ({rec.estimated_hours}h)")
            print(f"  Risk Reduction: {rec.risk_reduction:.1f}%")
            print(f"  SLA: {rec.sla_deadline.strftime('%Y-%m-%d') if rec.sla_deadline else 'N/A'}")
