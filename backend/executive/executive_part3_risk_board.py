"""
Military-Grade Executive & Strategic Reporting - Part 3 of 3
=============================================================

Risk Acceptance Matrix & Board-Level Presentations

Features:
- Risk acceptance workflow
- Board presentation generation
- Risk register management
- Executive decision support
- Compliance reporting for Board

COMPLIANCE:
- COSO ERM Framework
- ISO 31000 (Risk Management)
- NIST 800-39 (Risk Management Framework)
- SOX Section 404 (Internal Controls)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class RiskAppetite(Enum):
    """Organizational risk appetite"""
    AVERSE = "Risk Averse"
    MINIMAL = "Minimal Risk"
    CAUTIOUS = "Cautious"
    OPEN = "Open to Risk"
    AGGRESSIVE = "Risk Seeking"


class RiskDecision(Enum):
    """Risk treatment decisions"""
    MITIGATE = "Mitigate"
    ACCEPT = "Accept"
    TRANSFER = "Transfer"
    AVOID = "Avoid"


class BoardMemberRole(Enum):
    """Board member roles"""
    CHAIRMAN = "Board Chairman"
    AUDIT_COMMITTEE = "Audit Committee Chair"
    RISK_COMMITTEE = "Risk Committee Chair"
    CISO = "Chief Information Security Officer"
    CIO = "Chief Information Officer"
    CEO = "Chief Executive Officer"


@dataclass
class RiskItem:
    """Enterprise risk register item"""
    risk_id: str
    title: str
    description: str
    likelihood: float  # 0-100
    impact: float  # 0-100
    inherent_risk_score: float
    residual_risk_score: float
    risk_owner: str
    decision: RiskDecision
    rationale: str


@dataclass
class RiskAcceptance:
    """Formal risk acceptance"""
    acceptance_id: str
    risk_id: str
    accepted_by: str
    accepted_by_role: BoardMemberRole
    acceptance_date: datetime
    expiration_date: datetime
    conditions: List[str]
    compensating_controls: List[str]


@dataclass
class BoardPresentation:
    """Board-level presentation"""
    presentation_id: str
    meeting_date: datetime
    presentation_title: str
    executive_summary: str
    key_risks: List[str]
    risk_heatmap: Dict[str, Any]
    financial_impact: float
    recommendations: List[str]
    vote_required: bool


class RiskGovernanceEngine:
    """Risk Acceptance & Board Presentation Engine - Part 3"""
    
    def __init__(self):
        self.risk_register: List[RiskItem] = []
        self.risk_acceptances: List[RiskAcceptance] = []
        self.board_presentations: List[BoardPresentation] = []
        self.risk_appetite = RiskAppetite.CAUTIOUS
    
    def add_risk_to_register(self, title: str, description: str,
                            likelihood: float, impact: float,
                            risk_owner: str) -> RiskItem:
        """Add risk to enterprise risk register"""
        print(f"📊 Adding risk to register: {title}")
        
        # Calculate inherent risk score
        inherent_risk = self._calculate_risk_score(likelihood, impact)
        
        # Determine recommended decision
        decision = self._recommend_decision(inherent_risk)
        
        risk = RiskItem(
            risk_id=f"RISK-{len(self.risk_register) + 1:04d}",
            title=title,
            description=description,
            likelihood=likelihood,
            impact=impact,
            inherent_risk_score=inherent_risk,
            residual_risk_score=inherent_risk * 0.5,  # Assume 50% reduction with controls
            risk_owner=risk_owner,
            decision=decision,
            rationale=self._generate_rationale(inherent_risk, decision)
        )
        
        self.risk_register.append(risk)
        
        print(f"✅ Risk Added: {risk.risk_id} (Score: {inherent_risk:.1f})")
        return risk
    
    def accept_risk(self, risk_id: str, accepted_by: str,
                   accepted_by_role: BoardMemberRole,
                   duration_days: int = 90) -> RiskAcceptance:
        """Formally accept a risk"""
        print(f"⚠️ Creating risk acceptance for: {risk_id}")
        
        risk = self._get_risk(risk_id)
        if not risk:
            raise ValueError(f"Risk not found: {risk_id}")
        
        # Validate acceptance authority
        if not self._validate_acceptance_authority(risk, accepted_by_role):
            print(f"⚠️ Warning: {accepted_by_role.value} may not have authority for this risk level")
        
        acceptance = RiskAcceptance(
            acceptance_id=f"RA-{len(self.risk_acceptances) + 1:04d}",
            risk_id=risk_id,
            accepted_by=accepted_by,
            accepted_by_role=accepted_by_role,
            acceptance_date=datetime.now(),
            expiration_date=datetime.now() + timedelta(days=duration_days),
            conditions=self._generate_acceptance_conditions(risk),
            compensating_controls=self._identify_compensating_controls(risk)
        )
        
        self.risk_acceptances.append(acceptance)
        risk.decision = RiskDecision.ACCEPT
        
        print(f"✅ Risk Accepted: {acceptance.acceptance_id}")
        return acceptance
    
    def generate_board_presentation(self, meeting_date: datetime,
                                    title: str) -> BoardPresentation:
        """Generate board-level cybersecurity presentation"""
        print(f"📊 Generating Board Presentation: {title}")
        
        # Create executive summary
        exec_summary = self._create_executive_summary()
        
        # Identify top risks
        top_risks = self._identify_top_risks(limit=5)
        
        # Generate risk heatmap data
        heatmap = self._generate_risk_heatmap()
        
        # Calculate financial impact
        financial_impact = self._estimate_financial_impact()
        
        # Generate recommendations
        recommendations = self._generate_board_recommendations()
        
        # Determine if vote required
        vote_required = self._requires_board_vote()
        
        presentation = BoardPresentation(
            presentation_id=f"BOARD-{datetime.now().timestamp()}",
            meeting_date=meeting_date,
            presentation_title=title,
            executive_summary=exec_summary,
            key_risks=top_risks,
            risk_heatmap=heatmap,
            financial_impact=financial_impact,
            recommendations=recommendations,
            vote_required=vote_required
        )
        
        self.board_presentations.append(presentation)
        
        print(f"✅ Board Presentation Generated")
        return presentation
    
    def generate_risk_acceptance_report(self) -> Dict[str, Any]:
        """Generate risk acceptance report"""
        print("📋 Generating Risk Acceptance Report...")
        
        # Count acceptances
        total_acceptances = len(self.risk_acceptances)
        active_acceptances = sum(1 for a in self.risk_acceptances 
                                if a.expiration_date > datetime.now())
        expired_acceptances = total_acceptances - active_acceptances
        
        # Group by role
        by_role = {}
        for acceptance in self.risk_acceptances:
            role = acceptance.accepted_by_role.value
            by_role[role] = by_role.get(role, 0) + 1
        
        return {
            "total_acceptances": total_acceptances,
            "active_acceptances": active_acceptances,
            "expired_acceptances": expired_acceptances,
            "acceptances_by_role": by_role,
            "risks_requiring_renewal": self._identify_expiring_acceptances()
        }
    
    def _calculate_risk_score(self, likelihood: float, impact: float) -> float:
        """Calculate risk score (likelihood × impact)"""
        return (likelihood * impact) / 100
    
    def _recommend_decision(self, risk_score: float) -> RiskDecision:
        """Recommend risk treatment decision"""
        if risk_score >= 75:
            return RiskDecision.MITIGATE
        elif risk_score >= 50:
            return RiskDecision.TRANSFER
        elif risk_score >= 25:
            return RiskDecision.ACCEPT
        else:
            return RiskDecision.ACCEPT
    
    def _generate_rationale(self, risk_score: float, decision: RiskDecision) -> str:
        """Generate decision rationale"""
        return f"Risk score of {risk_score:.1f} warrants {decision.value} strategy"
    
    def _get_risk(self, risk_id: str) -> Optional[RiskItem]:
        """Get risk by ID"""
        for risk in self.risk_register:
            if risk.risk_id == risk_id:
                return risk
        return None
    
    def _validate_acceptance_authority(self, risk: RiskItem, 
                                      role: BoardMemberRole) -> bool:
        """Validate acceptance authority based on risk level"""
        if risk.inherent_risk_score >= 75:
            # High risks require Board approval
            return role in [BoardMemberRole.CHAIRMAN, BoardMemberRole.AUDIT_COMMITTEE]
        elif risk.inherent_risk_score >= 50:
            # Medium risks require executive approval
            return role in [BoardMemberRole.CISO, BoardMemberRole.CIO, BoardMemberRole.CEO]
        else:
            # Low risks can be accepted by CISO
            return role == BoardMemberRole.CISO
    
    def _generate_acceptance_conditions(self, risk: RiskItem) -> List[str]:
        """Generate risk acceptance conditions"""
        return [
            f"Risk must be reviewed quarterly by {risk.risk_owner}",
            "Compensating controls must remain in place",
            "Risk must be re-evaluated if threat landscape changes"
        ]
    
    def _identify_compensating_controls(self, risk: RiskItem) -> List[str]:
        """Identify compensating controls"""
        return [
            "Enhanced monitoring and alerting",
            "Regular vulnerability scanning",
            "Incident response plan activation"
        ]
    
    def _create_executive_summary(self) -> str:
        """Create executive summary for Board"""
        total_risks = len(self.risk_register)
        high_risks = sum(1 for r in self.risk_register if r.inherent_risk_score >= 75)
        
        return f"Current risk posture: {total_risks} active risks identified, " \
               f"{high_risks} rated as high priority requiring immediate attention. " \
               f"Risk appetite: {self.risk_appetite.value}."
    
    def _identify_top_risks(self, limit: int = 5) -> List[str]:
        """Identify top risks by score"""
        sorted_risks = sorted(self.risk_register, 
                            key=lambda r: r.inherent_risk_score, 
                            reverse=True)
        return [r.title for r in sorted_risks[:limit]]
    
    def _generate_risk_heatmap(self) -> Dict[str, Any]:
        """Generate risk heatmap data"""
        heatmap = {
            "high_likelihood_high_impact": 0,
            "high_likelihood_low_impact": 0,
            "low_likelihood_high_impact": 0,
            "low_likelihood_low_impact": 0
        }
        
        for risk in self.risk_register:
            if risk.likelihood >= 50 and risk.impact >= 50:
                heatmap["high_likelihood_high_impact"] += 1
            elif risk.likelihood >= 50 and risk.impact < 50:
                heatmap["high_likelihood_low_impact"] += 1
            elif risk.likelihood < 50 and risk.impact >= 50:
                heatmap["low_likelihood_high_impact"] += 1
            else:
                heatmap["low_likelihood_low_impact"] += 1
        
        return heatmap
    
    def _estimate_financial_impact(self) -> float:
        """Estimate total financial impact"""
        # Simplified calculation: $100k per risk point
        total_risk_score = sum(r.inherent_risk_score for r in self.risk_register)
        return total_risk_score * 100000
    
    def _generate_board_recommendations(self) -> List[str]:
        """Generate recommendations for Board"""
        return [
            "Approve $2.5M cybersecurity budget increase",
            "Authorize hiring of 5 additional security analysts",
            "Approve third-party risk assessment program"
        ]
    
    def _requires_board_vote(self) -> bool:
        """Determine if Board vote required"""
        # Vote required if any high-severity risks being accepted
        return any(r.inherent_risk_score >= 75 and r.decision == RiskDecision.ACCEPT 
                  for r in self.risk_register)
    
    def _identify_expiring_acceptances(self) -> List[str]:
        """Identify acceptances expiring within 30 days"""
        threshold = datetime.now() + timedelta(days=30)
        expiring = []
        
        for acceptance in self.risk_acceptances:
            if datetime.now() < acceptance.expiration_date <= threshold:
                expiring.append(acceptance.acceptance_id)
        
        return expiring


def main():
    """Test risk governance engine"""
    engine = RiskGovernanceEngine()
    
    # Add risk to register
    risk = engine.add_risk_to_register(
        title="Unpatched Critical Vulnerabilities",
        description="Production systems have 15 critical vulnerabilities",
        likelihood=80.0,
        impact=90.0,
        risk_owner="CISO"
    )
    print(f"Risk Score: {risk.inherent_risk_score:.1f}")
    
    # Accept risk
    acceptance = engine.accept_risk(
        risk_id=risk.risk_id,
        accepted_by="John Smith",
        accepted_by_role=BoardMemberRole.CHAIRMAN,
        duration_days=90
    )
    print(f"Risk Acceptance: {acceptance.acceptance_id}")
    
    # Generate board presentation
    presentation = engine.generate_board_presentation(
        meeting_date=datetime.now() + timedelta(days=7),
        title="Q1 Cybersecurity Risk Review"
    )
    print(f"Financial Impact: ${presentation.financial_impact:,.2f}")
    print(f"Vote Required: {presentation.vote_required}")
    
    # Generate acceptance report
    report = engine.generate_risk_acceptance_report()
    print(f"Active Acceptances: {report['active_acceptances']}")


if __name__ == "__main__":
    main()
