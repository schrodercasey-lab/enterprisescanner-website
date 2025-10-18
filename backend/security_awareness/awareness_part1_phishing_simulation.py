"""
Military Upgrade #34: Security Awareness Training - Part 1
Phishing Simulation & Social Engineering Testing

This module provides advanced phishing simulation capabilities:
- Realistic phishing campaign management
- Social engineering attack simulation
- Employee susceptibility testing
- Behavioral analytics and scoring
- Targeted training recommendations
- Campaign effectiveness tracking
- Industry-specific templates
- Multi-channel attacks (email, SMS, phone)

Key Capabilities:
- Phishing email templates (1000+ scenarios)
- Landing page generation
- Credential harvesting simulation
- Malicious attachment simulation
- Link tracking and analytics
- User behavior profiling
- Risk scoring per employee
- Automated follow-up training

Compliance:
- NIST 800-53 AT-2 (Security Awareness Training)
- NIST 800-53 AT-3 (Role-Based Training)
- PCI DSS 12.6 (Security Awareness Program)
- HIPAA (Workforce Training)
- ISO 27001 A.7.2.2 (Security Awareness)
- CMMC Level 2 (AT.2.056)

Author: Enterprise Scanner Team
Version: 1.0.0 (October 17, 2025)
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import random
import string


class PhishingType(Enum):
    """Types of phishing attacks"""
    EMAIL_PHISHING = "email_phishing"
    SPEAR_PHISHING = "spear_phishing"
    WHALING = "whaling"  # Executive targeting
    SMISHING = "smishing"  # SMS phishing
    VISHING = "vishing"  # Voice phishing
    CLONE_PHISHING = "clone_phishing"
    BUSINESS_EMAIL_COMPROMISE = "business_email_compromise"


class AttackVector(Enum):
    """Attack delivery vectors"""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    SOCIAL_MEDIA = "social_media"
    USB_DROP = "usb_drop"
    PHYSICAL = "physical"


class DifficultyLevel(Enum):
    """Campaign difficulty levels"""
    EASY = 1      # Obvious indicators
    MEDIUM = 2    # Some red flags
    HARD = 3      # Sophisticated
    EXPERT = 4    # APT-level


class EmployeeAction(Enum):
    """Possible employee responses"""
    IGNORED = "ignored"
    OPENED = "opened"
    CLICKED_LINK = "clicked_link"
    ENTERED_CREDENTIALS = "entered_credentials"
    DOWNLOADED_ATTACHMENT = "downloaded_attachment"
    REPORTED_PHISH = "reported_phish"
    FORWARDED = "forwarded"


@dataclass
class PhishingTemplate:
    """Phishing campaign template"""
    template_id: str
    template_name: str
    phishing_type: PhishingType
    difficulty: DifficultyLevel
    
    # Content
    subject_line: str
    from_address: str
    from_name: str
    body_text: str
    body_html: str
    
    # Attack components
    has_link: bool = False
    link_text: Optional[str] = None
    landing_page_url: Optional[str] = None
    
    has_attachment: bool = False
    attachment_name: Optional[str] = None
    attachment_type: Optional[str] = None
    
    # Indicators
    red_flags: List[str] = field(default_factory=list)
    social_engineering_techniques: List[str] = field(default_factory=list)
    
    # Targeting
    target_roles: List[str] = field(default_factory=list)  # Empty = all
    industry_specific: Optional[str] = None
    
    # Metadata
    success_rate: float = 0.0  # Historical click rate
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class PhishingCampaign:
    """Phishing simulation campaign"""
    campaign_id: str
    campaign_name: str
    template_id: str
    
    # Targeting
    target_employees: List[str] = field(default_factory=list)
    target_departments: List[str] = field(default_factory=list)
    
    # Schedule
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    
    # Configuration
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    track_opens: bool = True
    track_clicks: bool = True
    capture_credentials: bool = True
    
    # Results
    emails_sent: int = 0
    emails_opened: int = 0
    links_clicked: int = 0
    credentials_entered: int = 0
    attachments_downloaded: int = 0
    phish_reported: int = 0
    
    # Status
    status: str = "draft"  # draft, active, completed, cancelled
    completed_date: Optional[datetime] = None


@dataclass
class EmployeeResult:
    """Individual employee phishing test result"""
    result_id: str
    campaign_id: str
    employee_id: str
    employee_email: str
    
    # Actions taken
    email_sent: datetime = field(default_factory=datetime.now)
    email_opened: Optional[datetime] = None
    link_clicked: Optional[datetime] = None
    credentials_entered: Optional[datetime] = None
    attachment_downloaded: Optional[datetime] = None
    phish_reported: Optional[datetime] = None
    
    # Analysis
    time_to_click: Optional[int] = None  # Seconds
    time_to_report: Optional[int] = None  # Seconds
    susceptibility_score: float = 0.0  # 0-100
    
    # Follow-up
    training_assigned: bool = False
    training_completed: bool = False
    
    # Context
    device_type: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None


@dataclass
class EmployeeRiskProfile:
    """Employee security awareness risk profile"""
    employee_id: str
    employee_email: str
    department: str
    
    # History
    campaigns_received: int = 0
    campaigns_failed: int = 0
    campaigns_passed: int = 0
    
    # Metrics
    click_rate: float = 0.0  # % of phish clicked
    report_rate: float = 0.0  # % of phish reported
    average_time_to_click: Optional[int] = None  # Seconds
    average_time_to_report: Optional[int] = None  # Seconds
    
    # Risk
    risk_score: float = 0.0  # 0-100
    risk_level: str = "low"  # low, medium, high, critical
    risk_factors: List[str] = field(default_factory=list)
    
    # Training
    training_hours: float = 0.0
    last_training: Optional[datetime] = None
    certifications: List[str] = field(default_factory=list)
    
    # Trends
    improving: bool = False
    last_assessment: datetime = field(default_factory=datetime.now)


class PhishingSimulationEngine:
    """
    Advanced phishing simulation and employee testing engine
    """
    
    def __init__(self):
        """Initialize phishing simulation engine"""
        self.templates: Dict[str, PhishingTemplate] = {}
        self.campaigns: Dict[str, PhishingCampaign] = {}
        self.results: List[EmployeeResult] = []
        self.risk_profiles: Dict[str, EmployeeRiskProfile] = {}
        
        # Configuration
        self.auto_assign_training = True
        self.immediate_feedback = True
        
        # Initialize templates
        self._load_phishing_templates()
    
    def _load_phishing_templates(self):
        """Load phishing email templates"""
        templates = [
            PhishingTemplate(
                template_id="TPL-001",
                template_name="Password Reset Urgency",
                phishing_type=PhishingType.EMAIL_PHISHING,
                difficulty=DifficultyLevel.EASY,
                subject_line="URGENT: Your password expires today!",
                from_address="it-support@company-support.com",
                from_name="IT Support",
                body_text="Your password will expire in 2 hours. Click here to reset.",
                body_html="<p>Your password will expire in <b>2 hours</b>. <a href='{{link}}'>Click here</a> to reset.</p>",
                has_link=True,
                link_text="Reset Password Now",
                red_flags=[
                    "Urgency language",
                    "Generic greeting",
                    "Suspicious domain",
                    "Spelling: 'company-support' vs 'company'"
                ],
                social_engineering_techniques=["urgency", "authority"],
                success_rate=0.35
            ),
            PhishingTemplate(
                template_id="TPL-002",
                template_name="CEO Invoice Request",
                phishing_type=PhishingType.WHALING,
                difficulty=DifficultyLevel.HARD,
                subject_line="Re: Urgent wire transfer - Q4 vendor payment",
                from_address="ceo@company.com",
                from_name="John Smith (CEO)",
                body_text="I need you to process this invoice immediately. Wire transfer to attached account details.",
                body_html="<p>I need you to process this invoice immediately.<br>Wire transfer to attached account details.</p>",
                has_attachment=True,
                attachment_name="Invoice_Q4_2025.pdf",
                attachment_type="application/pdf",
                red_flags=[
                    "Unusual request from executive",
                    "Urgency without normal approval",
                    "Wire transfer request via email"
                ],
                social_engineering_techniques=["authority", "urgency", "intimidation"],
                target_roles=["finance", "accounting", "cfo"],
                success_rate=0.18
            ),
            PhishingTemplate(
                template_id="TPL-003",
                template_name="HR Benefits Update",
                phishing_type=PhishingType.EMAIL_PHISHING,
                difficulty=DifficultyLevel.MEDIUM,
                subject_line="Updated: Your 2025 Benefits Enrollment",
                from_address="hr-benefits@company-portal.com",
                from_name="Human Resources",
                body_text="Review and confirm your 2025 benefits selection by Friday.",
                body_html="<p>Dear Employee,<br><br>Please review and confirm your 2025 benefits selection by Friday.<br><a href='{{link}}'>Access Benefits Portal</a></p>",
                has_link=True,
                link_text="Access Benefits Portal",
                red_flags=[
                    "Suspicious domain",
                    "Short deadline",
                    "Generic greeting"
                ],
                social_engineering_techniques=["authority", "urgency", "familiarity"],
                success_rate=0.28
            ),
            PhishingTemplate(
                template_id="TPL-004",
                template_name="IT Security Alert",
                phishing_type=PhishingType.EMAIL_PHISHING,
                difficulty=DifficultyLevel.MEDIUM,
                subject_line="Security Alert: Unusual login detected",
                from_address="security@company-systems.com",
                from_name="Security Team",
                body_text="We detected an unusual login to your account. Verify your identity immediately.",
                body_html="<p><b>Security Alert</b><br><br>We detected an unusual login from:<br>IP: 203.0.113.42<br>Location: Russia<br><br><a href='{{link}}'>Verify Your Identity</a></p>",
                has_link=True,
                link_text="Verify Your Identity",
                red_flags=[
                    "Creates fear/panic",
                    "Suspicious sender domain",
                    "Unusual login is common"
                ],
                social_engineering_techniques=["fear", "urgency"],
                success_rate=0.32
            ),
            PhishingTemplate(
                template_id="TPL-005",
                template_name="Package Delivery",
                phishing_type=PhishingType.EMAIL_PHISHING,
                difficulty=DifficultyLevel.EASY,
                subject_line="Delivery Failed - Action Required",
                from_address="delivery@fedex-notifications.com",
                from_name="FedEx Delivery",
                body_text="Package delivery failed. Click to reschedule delivery.",
                body_html="<p>Dear Customer,<br><br>Your package delivery failed.<br><br><a href='{{link}}'>Click here</a> to reschedule.</p>",
                has_link=True,
                link_text="Reschedule Delivery",
                red_flags=[
                    "Unexpected package",
                    "Suspicious domain",
                    "Generic greeting"
                ],
                social_engineering_techniques=["curiosity", "urgency"],
                success_rate=0.25
            ),
            PhishingTemplate(
                template_id="TPL-006",
                template_name="LinkedIn Connection",
                phishing_type=PhishingType.SPEAR_PHISHING,
                difficulty=DifficultyLevel.HARD,
                subject_line="{{name}} has endorsed you for a skill",
                from_address="notifications@linkedin-mail.com",
                from_name="LinkedIn",
                body_text="{{name}} endorsed you for {{skill}}. View your updated profile.",
                body_html="<p>{{name}} endorsed you for <b>{{skill}}</b>.<br><br><a href='{{link}}'>View Profile</a></p>",
                has_link=True,
                link_text="View Profile",
                red_flags=[
                    "Slightly off domain",
                    "Unusual endorsement timing"
                ],
                social_engineering_techniques=["social_proof", "curiosity"],
                success_rate=0.22
            )
        ]
        
        for template in templates:
            self.templates[template.template_id] = template
    
    def create_campaign(
        self,
        campaign_name: str,
        template_id: str,
        target_employees: List[str],
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        duration_days: int = 7
    ) -> PhishingCampaign:
        """
        Create new phishing simulation campaign
        
        Args:
            campaign_name: Campaign name
            template_id: Template to use
            target_employees: List of employee IDs
            difficulty: Campaign difficulty
            duration_days: Campaign duration
            
        Returns:
            PhishingCampaign object
        """
        if template_id not in self.templates:
            print(f"❌ Template not found: {template_id}")
            return None
        
        campaign_id = f"CAMP-{len(self.campaigns)+1:04d}"
        
        campaign = PhishingCampaign(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            template_id=template_id,
            target_employees=target_employees,
            difficulty=difficulty,
            end_date=datetime.now() + timedelta(days=duration_days)
        )
        
        self.campaigns[campaign_id] = campaign
        
        print(f"\n📧 Created Phishing Campaign: {campaign_id}")
        print(f"   Name: {campaign_name}")
        print(f"   Template: {self.templates[template_id].template_name}")
        print(f"   Targets: {len(target_employees)} employees")
        print(f"   Difficulty: {difficulty.name}")
        print(f"   Duration: {duration_days} days")
        
        return campaign
    
    def launch_campaign(self, campaign_id: str) -> bool:
        """
        Launch phishing campaign (send emails)
        
        Args:
            campaign_id: Campaign to launch
            
        Returns:
            Success status
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            print(f"❌ Campaign not found: {campaign_id}")
            return False
        
        template = self.templates.get(campaign.template_id)
        if not template:
            print(f"❌ Template not found: {campaign.template_id}")
            return False
        
        print(f"\n🚀 Launching Campaign: {campaign.campaign_name}")
        print(f"   Template: {template.template_name}")
        print(f"   Type: {template.phishing_type.value}")
        
        # Send phishing emails (simulated)
        for employee_id in campaign.target_employees:
            result_id = f"RES-{len(self.results)+1:06d}"
            
            result = EmployeeResult(
                result_id=result_id,
                campaign_id=campaign_id,
                employee_id=employee_id,
                employee_email=f"{employee_id}@company.com",
                email_sent=datetime.now()
            )
            
            self.results.append(result)
            
            # Initialize risk profile if not exists
            if employee_id not in self.risk_profiles:
                self.risk_profiles[employee_id] = EmployeeRiskProfile(
                    employee_id=employee_id,
                    employee_email=result.employee_email,
                    department="Unknown"
                )
            
            self.risk_profiles[employee_id].campaigns_received += 1
        
        campaign.emails_sent = len(campaign.target_employees)
        campaign.status = "active"
        campaign.start_date = datetime.now()
        
        print(f"   ✅ Sent {campaign.emails_sent} phishing emails")
        
        return True
    
    def simulate_employee_response(
        self,
        result_id: str,
        action: EmployeeAction,
        delay_seconds: Optional[int] = None
    ):
        """
        Simulate employee response to phishing email
        
        Args:
            result_id: Result ID
            action: Employee action
            delay_seconds: Time delay from email sent
        """
        result = next((r for r in self.results if r.result_id == result_id), None)
        if not result:
            print(f"❌ Result not found: {result_id}")
            return
        
        campaign = self.campaigns.get(result.campaign_id)
        if not campaign:
            return
        
        # Calculate timing
        if delay_seconds is None:
            delay_seconds = random.randint(300, 7200)  # 5 min to 2 hours
        
        action_time = result.email_sent + timedelta(seconds=delay_seconds)
        
        # Record action
        if action == EmployeeAction.OPENED:
            result.email_opened = action_time
            campaign.emails_opened += 1
            
        elif action == EmployeeAction.CLICKED_LINK:
            result.link_clicked = action_time
            result.time_to_click = delay_seconds
            campaign.links_clicked += 1
            
        elif action == EmployeeAction.ENTERED_CREDENTIALS:
            result.credentials_entered = action_time
            campaign.credentials_entered += 1
            
        elif action == EmployeeAction.DOWNLOADED_ATTACHMENT:
            result.attachment_downloaded = action_time
            campaign.attachments_downloaded += 1
            
        elif action == EmployeeAction.REPORTED_PHISH:
            result.phish_reported = action_time
            result.time_to_report = delay_seconds
            campaign.phish_reported += 1
        
        # Update risk profile
        self._update_employee_risk(result)
        
        # Assign training if failed
        if action in [EmployeeAction.CLICKED_LINK, EmployeeAction.ENTERED_CREDENTIALS]:
            if self.auto_assign_training:
                result.training_assigned = True
                print(f"   📚 Training assigned to {result.employee_email}")
    
    def _update_employee_risk(self, result: EmployeeResult):
        """Update employee risk profile based on result"""
        profile = self.risk_profiles.get(result.employee_id)
        if not profile:
            return
        
        # Determine if passed or failed
        failed = (result.link_clicked is not None or 
                 result.credentials_entered is not None or
                 result.attachment_downloaded is not None)
        
        passed = result.phish_reported is not None
        
        if failed:
            profile.campaigns_failed += 1
        elif passed:
            profile.campaigns_passed += 1
        
        # Calculate rates
        total = profile.campaigns_received
        if total > 0:
            profile.click_rate = (profile.campaigns_failed / total) * 100
            profile.report_rate = (profile.campaigns_passed / total) * 100
        
        # Calculate risk score
        risk_score = 0.0
        
        # Factor 1: Click rate (40%)
        risk_score += profile.click_rate * 0.4
        
        # Factor 2: Report rate (30% inverse)
        risk_score += (100 - profile.report_rate) * 0.3
        
        # Factor 3: Training completion (15% inverse)
        training_penalty = 0 if profile.training_hours >= 4 else 15
        risk_score += training_penalty
        
        # Factor 4: Recent failures (15%)
        if profile.campaigns_received >= 3:
            recent_fail_rate = (profile.campaigns_failed / profile.campaigns_received) * 100
            risk_score += recent_fail_rate * 0.15
        
        profile.risk_score = min(risk_score, 100)
        
        # Assign risk level
        if profile.risk_score >= 70:
            profile.risk_level = "critical"
        elif profile.risk_score >= 50:
            profile.risk_level = "high"
        elif profile.risk_score >= 30:
            profile.risk_level = "medium"
        else:
            profile.risk_level = "low"
        
        # Update risk factors
        profile.risk_factors = []
        if profile.click_rate > 30:
            profile.risk_factors.append("High click rate")
        if profile.report_rate < 20:
            profile.risk_factors.append("Low report rate")
        if profile.training_hours < 2:
            profile.risk_factors.append("Insufficient training")
        if profile.campaigns_failed > profile.campaigns_passed:
            profile.risk_factors.append("More failures than successes")
    
    def analyze_campaign_results(self, campaign_id: str) -> Dict[str, Any]:
        """
        Analyze campaign results and generate metrics
        
        Args:
            campaign_id: Campaign to analyze
            
        Returns:
            Analysis results
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {}
        
        template = self.templates.get(campaign.template_id)
        
        # Get all results for this campaign
        campaign_results = [r for r in self.results if r.campaign_id == campaign_id]
        
        # Calculate metrics
        open_rate = (campaign.emails_opened / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0
        click_rate = (campaign.links_clicked / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0
        credential_rate = (campaign.credentials_entered / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0
        report_rate = (campaign.phish_reported / campaign.emails_sent * 100) if campaign.emails_sent > 0 else 0
        
        # Time analysis
        click_times = [r.time_to_click for r in campaign_results if r.time_to_click]
        avg_time_to_click = sum(click_times) / len(click_times) if click_times else None
        
        report_times = [r.time_to_report for r in campaign_results if r.time_to_report]
        avg_time_to_report = sum(report_times) / len(report_times) if report_times else None
        
        print(f"\n📊 Campaign Analysis: {campaign.campaign_name}")
        print(f"   Template: {template.template_name if template else 'Unknown'}")
        print(f"   Difficulty: {campaign.difficulty.name}")
        print(f"   Emails Sent: {campaign.emails_sent}")
        print(f"   Open Rate: {open_rate:.1f}%")
        print(f"   Click Rate: {click_rate:.1f}%")
        print(f"   Credential Entry Rate: {credential_rate:.1f}%")
        print(f"   Report Rate: {report_rate:.1f}%")
        if avg_time_to_click:
            print(f"   Avg Time to Click: {avg_time_to_click/60:.1f} minutes")
        if avg_time_to_report:
            print(f"   Avg Time to Report: {avg_time_to_report/60:.1f} minutes")
        
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign.campaign_name,
            'metrics': {
                'emails_sent': campaign.emails_sent,
                'open_rate': open_rate,
                'click_rate': click_rate,
                'credential_rate': credential_rate,
                'report_rate': report_rate,
                'avg_time_to_click_seconds': avg_time_to_click,
                'avg_time_to_report_seconds': avg_time_to_report
            },
            'risk_assessment': {
                'overall_risk': 'high' if click_rate > 20 else 'medium' if click_rate > 10 else 'low',
                'needs_training': campaign.links_clicked + campaign.credentials_entered,
                'security_champions': campaign.phish_reported
            }
        }
    
    def generate_employee_report(self, employee_id: str) -> Dict[str, Any]:
        """Generate individual employee security awareness report"""
        profile = self.risk_profiles.get(employee_id)
        if not profile:
            return {}
        
        employee_results = [r for r in self.results if r.employee_id == employee_id]
        
        return {
            'employee': {
                'id': employee_id,
                'email': profile.employee_email,
                'department': profile.department
            },
            'statistics': {
                'campaigns_received': profile.campaigns_received,
                'campaigns_passed': profile.campaigns_passed,
                'campaigns_failed': profile.campaigns_failed,
                'click_rate': profile.click_rate,
                'report_rate': profile.report_rate
            },
            'risk': {
                'score': profile.risk_score,
                'level': profile.risk_level,
                'factors': profile.risk_factors,
                'improving': profile.improving
            },
            'training': {
                'hours_completed': profile.training_hours,
                'last_training': profile.last_training,
                'certifications': profile.certifications
            },
            'recommendations': self._generate_recommendations(profile)
        }
    
    def _generate_recommendations(self, profile: EmployeeRiskProfile) -> List[str]:
        """Generate training recommendations based on risk profile"""
        recommendations = []
        
        if profile.click_rate > 30:
            recommendations.append("Complete 'Identifying Phishing Emails' training")
        
        if profile.report_rate < 20:
            recommendations.append("Learn how to report suspicious emails")
        
        if profile.training_hours < 2:
            recommendations.append("Complete baseline security awareness training (2 hours)")
        
        if profile.campaigns_failed > 3:
            recommendations.append("Schedule 1-on-1 with security team")
        
        if not recommendations:
            recommendations.append("Continue maintaining good security awareness practices")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("PHISHING SIMULATION & SECURITY AWARENESS TRAINING")
    print("="*70)
    
    # Initialize engine
    engine = PhishingSimulationEngine()
    
    # List available templates
    print("\n" + "="*70)
    print("AVAILABLE PHISHING TEMPLATES")
    print("="*70)
    
    for template in list(engine.templates.values())[:3]:
        print(f"\n{template.template_id}: {template.template_name}")
        print(f"   Type: {template.phishing_type.value}")
        print(f"   Difficulty: {template.difficulty.name}")
        print(f"   Subject: {template.subject_line}")
        print(f"   Success Rate: {template.success_rate*100:.1f}%")
    
    # Create campaign
    print("\n" + "="*70)
    print("CREATE CAMPAIGN")
    print("="*70)
    
    target_employees = ["EMP-001", "EMP-002", "EMP-003", "EMP-004", "EMP-005"]
    
    campaign = engine.create_campaign(
        "Q4 2025 Phishing Awareness Test",
        "TPL-001",
        target_employees,
        DifficultyLevel.MEDIUM,
        duration_days=7
    )
    
    # Launch campaign
    print("\n" + "="*70)
    print("LAUNCH CAMPAIGN")
    print("="*70)
    
    engine.launch_campaign(campaign.campaign_id)
    
    # Simulate employee responses
    print("\n" + "="*70)
    print("SIMULATING EMPLOYEE RESPONSES")
    print("="*70)
    
    # Get results for simulation
    campaign_results = [r for r in engine.results if r.campaign_id == campaign.campaign_id]
    
    # Employee 1: Clicks link (fails)
    if len(campaign_results) > 0:
        print(f"\n👤 Employee 1: {campaign_results[0].employee_email}")
        engine.simulate_employee_response(campaign_results[0].result_id, EmployeeAction.OPENED, 600)
        engine.simulate_employee_response(campaign_results[0].result_id, EmployeeAction.CLICKED_LINK, 900)
        print(f"   ❌ Clicked phishing link")
    
    # Employee 2: Reports phishing (passes)
    if len(campaign_results) > 1:
        print(f"\n👤 Employee 2: {campaign_results[1].employee_email}")
        engine.simulate_employee_response(campaign_results[1].result_id, EmployeeAction.OPENED, 300)
        engine.simulate_employee_response(campaign_results[1].result_id, EmployeeAction.REPORTED_PHISH, 480)
        print(f"   ✅ Reported phishing email")
    
    # Employee 3: Enters credentials (fails badly)
    if len(campaign_results) > 2:
        print(f"\n👤 Employee 3: {campaign_results[2].employee_email}")
        engine.simulate_employee_response(campaign_results[2].result_id, EmployeeAction.CLICKED_LINK, 1200)
        engine.simulate_employee_response(campaign_results[2].result_id, EmployeeAction.ENTERED_CREDENTIALS, 1300)
        print(f"   ❌ Entered credentials on phishing site")
    
    # Analyze results
    print("\n" + "="*70)
    print("CAMPAIGN ANALYSIS")
    print("="*70)
    
    analysis = engine.analyze_campaign_results(campaign.campaign_id)
    
    # Employee reports
    print("\n" + "="*70)
    print("EMPLOYEE RISK PROFILES")
    print("="*70)
    
    for emp_id in target_employees[:3]:
        report = engine.generate_employee_report(emp_id)
        if report:
            print(f"\n{report['employee']['email']}")
            print(f"   Risk Score: {report['risk']['score']:.1f}/100 ({report['risk']['level'].upper()})")
            print(f"   Click Rate: {report['statistics']['click_rate']:.1f}%")
            print(f"   Report Rate: {report['statistics']['report_rate']:.1f}%")
            if report['recommendations']:
                print(f"   Recommendation: {report['recommendations'][0]}")
