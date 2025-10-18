"""
JUPITER VR/AR Platform - VR Training System (Module G.3.11)

Comprehensive training and certification system for security analysts.
Provides guided scenarios, skill assessment, and safe practice environment.

Training Scenarios:
1. Phishing Attack Investigation
2. Ransomware Response
3. DDoS Mitigation
4. SQL Injection Detection
5. Zero-Day Vulnerability Assessment
6. Insider Threat Detection
7. Advanced Persistent Threat (APT) Hunting
8. Cloud Security Incident Response
9. IoT Botnet Investigation
10. Supply Chain Attack Analysis

Features:
- Guided step-by-step tutorials
- Skill scoring and assessment
- Progress tracking and analytics
- Certification upon completion
- Practice mode with no consequences
- Performance metrics and feedback

Enterprise Scanner - JUPITER Platform
October 2025
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime, timedelta
import json
import random


# ============================================================================
# Enums and Constants
# ============================================================================

class TrainingScenario(Enum):
    """Available training scenarios"""
    PHISHING_INVESTIGATION = "phishing_investigation"
    RANSOMWARE_RESPONSE = "ransomware_response"
    DDOS_MITIGATION = "ddos_mitigation"
    SQL_INJECTION_DETECTION = "sql_injection_detection"
    ZERO_DAY_ASSESSMENT = "zero_day_assessment"
    INSIDER_THREAT_DETECTION = "insider_threat_detection"
    APT_HUNTING = "apt_hunting"
    CLOUD_INCIDENT_RESPONSE = "cloud_incident_response"
    IOT_BOTNET_INVESTIGATION = "iot_botnet_investigation"
    SUPPLY_CHAIN_ATTACK = "supply_chain_attack"


class SkillLevel(Enum):
    """Analyst skill levels"""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TrainingStepType(Enum):
    """Types of training steps"""
    INTRODUCTION = "introduction"
    OBSERVATION = "observation"
    ANALYSIS = "analysis"
    DECISION = "decision"
    ACTION = "action"
    VALIDATION = "validation"
    SUMMARY = "summary"


class CertificationLevel(Enum):
    """Certification levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TrainingStep:
    """Individual step in a training scenario"""
    step_id: str
    step_type: TrainingStepType
    title: str
    description: str
    instructions: List[str]
    expected_actions: List[str]
    hints: List[str]
    time_limit_seconds: Optional[int] = None
    points: int = 10
    required: bool = True


@dataclass
class ScenarioDefinition:
    """Complete training scenario definition"""
    scenario_id: str
    scenario_type: TrainingScenario
    title: str
    description: str
    difficulty: SkillLevel
    estimated_duration_minutes: int
    steps: List[TrainingStep]
    learning_objectives: List[str]
    prerequisites: List[str]
    total_points: int
    pass_threshold_percent: int = 70


@dataclass
class TrainingProgress:
    """User progress through a training scenario"""
    user_id: str
    scenario_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_step_index: int = 0
    completed_steps: List[str] = field(default_factory=list)
    skipped_steps: List[str] = field(default_factory=list)
    step_scores: Dict[str, int] = field(default_factory=dict)
    total_score: int = 0
    hints_used: int = 0
    time_spent_seconds: int = 0
    passed: bool = False


@dataclass
class SkillAssessmentResult:
    """Results of skill assessment"""
    user_id: str
    assessed_at: datetime
    skill_level: SkillLevel
    strengths: List[str]
    weaknesses: List[str]
    recommended_scenarios: List[TrainingScenario]
    overall_score: int
    category_scores: Dict[str, int]


@dataclass
class Certification:
    """Training certification"""
    certification_id: str
    user_id: str
    level: CertificationLevel
    scenarios_completed: List[str]
    total_score: int
    issued_at: datetime
    expires_at: datetime
    badge_url: str


# ============================================================================
# Training Scenario Manager
# ============================================================================

class TrainingScenarioManager:
    """Manages training scenarios and progression"""
    
    def __init__(self):
        self.scenarios: Dict[str, ScenarioDefinition] = {}
        self.user_progress: Dict[str, Dict[str, TrainingProgress]] = {}
        self._initialize_scenarios()
    
    def _initialize_scenarios(self):
        """Initialize all training scenarios"""
        
        # Scenario 1: Phishing Investigation
        phishing_steps = [
            TrainingStep(
                step_id="phishing_intro",
                step_type=TrainingStepType.INTRODUCTION,
                title="Phishing Investigation Introduction",
                description="Learn to identify and investigate phishing attacks",
                instructions=[
                    "Review the email that triggered the alert",
                    "Look for suspicious sender addresses",
                    "Check for urgency tactics and spelling errors",
                    "Examine any embedded links or attachments"
                ],
                expected_actions=["view_email", "check_sender"],
                hints=["Hover over links without clicking to see the real URL"],
                time_limit_seconds=300,
                points=10
            ),
            TrainingStep(
                step_id="phishing_analysis",
                step_type=TrainingStepType.ANALYSIS,
                title="Analyze Email Headers",
                description="Deep dive into email headers to find indicators of compromise",
                instructions=[
                    "Examine the 'From' and 'Return-Path' headers",
                    "Check SPF, DKIM, and DMARC authentication results",
                    "Look for mismatched sender domains",
                    "Identify the originating IP address"
                ],
                expected_actions=["view_headers", "check_spf", "check_dkim"],
                hints=[
                    "SPF failures often indicate spoofed emails",
                    "Check if the IP is from an unexpected country"
                ],
                time_limit_seconds=600,
                points=20
            ),
            TrainingStep(
                step_id="phishing_decision",
                step_type=TrainingStepType.DECISION,
                title="Make Your Assessment",
                description="Decide if this is a legitimate phishing attack",
                instructions=[
                    "Review all evidence collected",
                    "Determine the threat level (low/medium/high/critical)",
                    "Identify affected users",
                    "Choose appropriate response actions"
                ],
                expected_actions=["set_threat_level", "identify_victims"],
                hints=["Consider the potential impact if users clicked the link"],
                time_limit_seconds=300,
                points=30
            ),
            TrainingStep(
                step_id="phishing_action",
                step_type=TrainingStepType.ACTION,
                title="Take Remediation Actions",
                description="Execute the appropriate response to contain the threat",
                instructions=[
                    "Quarantine the malicious email",
                    "Block the sender domain",
                    "Alert affected users",
                    "Update email filters",
                    "Document the incident"
                ],
                expected_actions=[
                    "quarantine_email",
                    "block_sender",
                    "notify_users",
                    "update_filters"
                ],
                hints=["Don't forget to document your actions for compliance"],
                time_limit_seconds=600,
                points=30
            ),
            TrainingStep(
                step_id="phishing_summary",
                step_type=TrainingStepType.SUMMARY,
                title="Incident Summary",
                description="Review your performance and learn from the scenario",
                instructions=[
                    "Review the correct identification markers",
                    "Understand what you did well",
                    "Learn from any mistakes",
                    "Apply knowledge to future investigations"
                ],
                expected_actions=["review_summary"],
                hints=[],
                time_limit_seconds=None,
                points=10
            )
        ]
        
        self.scenarios["phishing_investigation"] = ScenarioDefinition(
            scenario_id="phishing_investigation",
            scenario_type=TrainingScenario.PHISHING_INVESTIGATION,
            title="Phishing Attack Investigation",
            description="Learn to identify, analyze, and respond to phishing attacks",
            difficulty=SkillLevel.BEGINNER,
            estimated_duration_minutes=30,
            steps=phishing_steps,
            learning_objectives=[
                "Identify phishing email indicators",
                "Analyze email headers for authentication failures",
                "Assess threat severity",
                "Execute appropriate remediation actions"
            ],
            prerequisites=[],
            total_points=100,
            pass_threshold_percent=70
        )
        
        # Scenario 2: Ransomware Response
        ransomware_steps = [
            TrainingStep(
                step_id="ransomware_intro",
                step_type=TrainingStepType.INTRODUCTION,
                title="Ransomware Detection",
                description="Identify the signs of a ransomware infection",
                instructions=[
                    "Review alerts for file encryption activity",
                    "Check for ransom notes on affected systems",
                    "Identify the ransomware variant",
                    "Assess the scope of infection"
                ],
                expected_actions=["view_alerts", "identify_variant"],
                hints=["Look for file extension changes (.encrypted, .locked, etc.)"],
                time_limit_seconds=300,
                points=15
            ),
            TrainingStep(
                step_id="ransomware_containment",
                step_type=TrainingStepType.ACTION,
                title="Contain the Outbreak",
                description="Immediately contain the ransomware to prevent spread",
                instructions=[
                    "Isolate infected systems from the network",
                    "Disable network shares",
                    "Block command and control IPs",
                    "Preserve evidence for forensics"
                ],
                expected_actions=[
                    "isolate_systems",
                    "disable_shares",
                    "block_c2",
                    "preserve_evidence"
                ],
                hints=["Speed is critical - isolate first, investigate later"],
                time_limit_seconds=600,
                points=35
            ),
            TrainingStep(
                step_id="ransomware_recovery",
                step_type=TrainingStepType.ACTION,
                title="Recovery Planning",
                description="Plan and execute recovery from ransomware",
                instructions=[
                    "Verify backup integrity",
                    "Identify decryption tools if available",
                    "Prioritize systems for restoration",
                    "Coordinate with stakeholders",
                    "Execute recovery plan"
                ],
                expected_actions=[
                    "check_backups",
                    "search_decryptors",
                    "restore_systems"
                ],
                hints=["Never pay the ransom - use backups or decryption tools"],
                time_limit_seconds=900,
                points=40
            ),
            TrainingStep(
                step_id="ransomware_summary",
                step_type=TrainingStepType.SUMMARY,
                title="Post-Incident Review",
                description="Learn from the incident and improve defenses",
                instructions=[
                    "Document lessons learned",
                    "Identify security gaps",
                    "Recommend preventive measures",
                    "Update incident response plan"
                ],
                expected_actions=["document_lessons"],
                hints=[],
                time_limit_seconds=None,
                points=10
            )
        ]
        
        self.scenarios["ransomware_response"] = ScenarioDefinition(
            scenario_id="ransomware_response",
            scenario_type=TrainingScenario.RANSOMWARE_RESPONSE,
            title="Ransomware Incident Response",
            description="Learn to detect, contain, and recover from ransomware attacks",
            difficulty=SkillLevel.INTERMEDIATE,
            estimated_duration_minutes=45,
            steps=ransomware_steps,
            learning_objectives=[
                "Recognize ransomware infection indicators",
                "Execute rapid containment procedures",
                "Plan and execute recovery operations",
                "Document post-incident improvements"
            ],
            prerequisites=["phishing_investigation"],
            total_points=100,
            pass_threshold_percent=75
        )
        
        # Scenario 3: DDoS Mitigation
        ddos_steps = [
            TrainingStep(
                step_id="ddos_detection",
                step_type=TrainingStepType.OBSERVATION,
                title="DDoS Attack Detection",
                description="Identify a distributed denial of service attack in progress",
                instructions=[
                    "Monitor network traffic patterns",
                    "Identify abnormal traffic spikes",
                    "Determine attack vector (SYN flood, UDP flood, HTTP flood)",
                    "Assess impact on services"
                ],
                expected_actions=["view_traffic", "identify_attack_type"],
                hints=["Look for high volume of requests from many different IPs"],
                time_limit_seconds=300,
                points=15
            ),
            TrainingStep(
                step_id="ddos_mitigation",
                step_type=TrainingStepType.ACTION,
                title="Activate DDoS Mitigation",
                description="Deploy countermeasures to mitigate the attack",
                instructions=[
                    "Enable rate limiting",
                    "Activate scrubbing center",
                    "Implement geo-blocking if appropriate",
                    "Scale infrastructure if possible",
                    "Contact ISP/CDN for assistance"
                ],
                expected_actions=[
                    "enable_rate_limiting",
                    "activate_scrubbing",
                    "scale_resources"
                ],
                hints=["Use CDN and DDoS protection services for large attacks"],
                time_limit_seconds=600,
                points=40
            ),
            TrainingStep(
                step_id="ddos_analysis",
                step_type=TrainingStepType.ANALYSIS,
                title="Attack Analysis",
                description="Analyze the attack characteristics and source",
                instructions=[
                    "Identify source countries and ASNs",
                    "Determine if botnet is involved",
                    "Look for patterns in attack traffic",
                    "Assess attacker sophistication"
                ],
                expected_actions=["analyze_sources", "identify_botnet"],
                hints=["Botnet attacks show coordinated timing patterns"],
                time_limit_seconds=600,
                points=30
            ),
            TrainingStep(
                step_id="ddos_summary",
                step_type=TrainingStepType.SUMMARY,
                title="DDoS Response Summary",
                description="Review mitigation effectiveness and plan improvements",
                instructions=[
                    "Measure mitigation effectiveness",
                    "Document attack characteristics",
                    "Update DDoS playbook",
                    "Recommend infrastructure improvements"
                ],
                expected_actions=["review_effectiveness"],
                hints=[],
                time_limit_seconds=None,
                points=15
            )
        ]
        
        self.scenarios["ddos_mitigation"] = ScenarioDefinition(
            scenario_id="ddos_mitigation",
            scenario_type=TrainingScenario.DDOS_MITIGATION,
            title="DDoS Attack Mitigation",
            description="Learn to detect and mitigate distributed denial of service attacks",
            difficulty=SkillLevel.INTERMEDIATE,
            estimated_duration_minutes=40,
            steps=ddos_steps,
            learning_objectives=[
                "Detect DDoS attacks in real-time",
                "Deploy effective mitigation measures",
                "Analyze attack patterns and sources",
                "Optimize DDoS defense strategy"
            ],
            prerequisites=[],
            total_points=100,
            pass_threshold_percent=70
        )
        
        # Add more scenarios (abbreviated for brevity)
        self._add_sql_injection_scenario()
        self._add_zero_day_scenario()
        self._add_insider_threat_scenario()
        self._add_apt_hunting_scenario()
        self._add_cloud_incident_scenario()
        self._add_iot_botnet_scenario()
        self._add_supply_chain_scenario()
    
    def _add_sql_injection_scenario(self):
        """Add SQL injection detection scenario"""
        steps = [
            TrainingStep(
                step_id="sql_intro",
                step_type=TrainingStepType.INTRODUCTION,
                title="SQL Injection Basics",
                description="Learn to identify SQL injection attempts",
                instructions=[
                    "Review web application logs",
                    "Look for SQL syntax in inputs",
                    "Identify common injection patterns"
                ],
                expected_actions=["review_logs"],
                hints=["Common patterns: ' OR '1'='1, UNION SELECT, DROP TABLE"],
                points=15
            ),
            TrainingStep(
                step_id="sql_action",
                step_type=TrainingStepType.ACTION,
                title="Block and Remediate",
                description="Stop the attack and fix vulnerabilities",
                instructions=[
                    "Block malicious IPs",
                    "Enable WAF rules",
                    "Alert development team",
                    "Test for other injection points"
                ],
                expected_actions=["block_ip", "enable_waf"],
                hints=["Use prepared statements to prevent SQL injection"],
                points=35
            )
        ]
        
        self.scenarios["sql_injection_detection"] = ScenarioDefinition(
            scenario_id="sql_injection_detection",
            scenario_type=TrainingScenario.SQL_INJECTION_DETECTION,
            title="SQL Injection Detection",
            description="Identify and respond to SQL injection attacks",
            difficulty=SkillLevel.INTERMEDIATE,
            estimated_duration_minutes=25,
            steps=steps,
            learning_objectives=[
                "Recognize SQL injection patterns",
                "Block attacks effectively",
                "Work with developers to fix vulnerabilities"
            ],
            prerequisites=[],
            total_points=100,
            pass_threshold_percent=70
        )
    
    def _add_zero_day_scenario(self):
        """Add zero-day vulnerability assessment scenario"""
        self.scenarios["zero_day_assessment"] = ScenarioDefinition(
            scenario_id="zero_day_assessment",
            scenario_type=TrainingScenario.ZERO_DAY_ASSESSMENT,
            title="Zero-Day Vulnerability Assessment",
            description="Assess and respond to zero-day exploits",
            difficulty=SkillLevel.ADVANCED,
            estimated_duration_minutes=60,
            steps=[],  # Abbreviated
            learning_objectives=[
                "Identify zero-day indicators",
                "Assess risk and impact",
                "Deploy temporary mitigations"
            ],
            prerequisites=["phishing_investigation", "ransomware_response"],
            total_points=100,
            pass_threshold_percent=80
        )
    
    def _add_insider_threat_scenario(self):
        """Add insider threat detection scenario"""
        self.scenarios["insider_threat_detection"] = ScenarioDefinition(
            scenario_id="insider_threat_detection",
            scenario_type=TrainingScenario.INSIDER_THREAT_DETECTION,
            title="Insider Threat Detection",
            description="Identify and investigate insider threats",
            difficulty=SkillLevel.ADVANCED,
            estimated_duration_minutes=50,
            steps=[],  # Abbreviated
            learning_objectives=[
                "Detect anomalous user behavior",
                "Conduct discrete investigations",
                "Coordinate with HR and legal"
            ],
            prerequisites=["phishing_investigation"],
            total_points=100,
            pass_threshold_percent=75
        )
    
    def _add_apt_hunting_scenario(self):
        """Add APT hunting scenario"""
        self.scenarios["apt_hunting"] = ScenarioDefinition(
            scenario_id="apt_hunting",
            scenario_type=TrainingScenario.APT_HUNTING,
            title="Advanced Persistent Threat Hunting",
            description="Hunt for and eradicate APT groups",
            difficulty=SkillLevel.EXPERT,
            estimated_duration_minutes=90,
            steps=[],  # Abbreviated
            learning_objectives=[
                "Identify APT tactics, techniques, and procedures",
                "Track lateral movement",
                "Eradicate persistent access"
            ],
            prerequisites=["ransomware_response", "insider_threat_detection"],
            total_points=100,
            pass_threshold_percent=85
        )
    
    def _add_cloud_incident_scenario(self):
        """Add cloud security incident response scenario"""
        self.scenarios["cloud_incident_response"] = ScenarioDefinition(
            scenario_id="cloud_incident_response",
            scenario_type=TrainingScenario.CLOUD_INCIDENT_RESPONSE,
            title="Cloud Security Incident Response",
            description="Respond to incidents in cloud environments",
            difficulty=SkillLevel.ADVANCED,
            estimated_duration_minutes=55,
            steps=[],  # Abbreviated
            learning_objectives=[
                "Understand cloud-specific threats",
                "Use cloud-native security tools",
                "Coordinate with cloud providers"
            ],
            prerequisites=["phishing_investigation"],
            total_points=100,
            pass_threshold_percent=75
        )
    
    def _add_iot_botnet_scenario(self):
        """Add IoT botnet investigation scenario"""
        self.scenarios["iot_botnet_investigation"] = ScenarioDefinition(
            scenario_id="iot_botnet_investigation",
            scenario_type=TrainingScenario.IOT_BOTNET_INVESTIGATION,
            title="IoT Botnet Investigation",
            description="Investigate and disrupt IoT botnets",
            difficulty=SkillLevel.ADVANCED,
            estimated_duration_minutes=45,
            steps=[],  # Abbreviated
            learning_objectives=[
                "Identify compromised IoT devices",
                "Analyze botnet command and control",
                "Coordinate IoT device remediation"
            ],
            prerequisites=["ddos_mitigation"],
            total_points=100,
            pass_threshold_percent=75
        )
    
    def _add_supply_chain_scenario(self):
        """Add supply chain attack analysis scenario"""
        self.scenarios["supply_chain_attack"] = ScenarioDefinition(
            scenario_id="supply_chain_attack",
            scenario_type=TrainingScenario.SUPPLY_CHAIN_ATTACK,
            title="Supply Chain Attack Analysis",
            description="Detect and respond to supply chain compromises",
            difficulty=SkillLevel.EXPERT,
            estimated_duration_minutes=75,
            steps=[],  # Abbreviated
            learning_objectives=[
                "Identify supply chain compromises",
                "Assess vendor security posture",
                "Coordinate multi-organization response"
            ],
            prerequisites=["apt_hunting"],
            total_points=100,
            pass_threshold_percent=80
        )
    
    def get_scenario(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        """Get scenario definition by ID"""
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(
        self,
        difficulty: Optional[SkillLevel] = None
    ) -> List[ScenarioDefinition]:
        """List available scenarios, optionally filtered by difficulty"""
        scenarios = list(self.scenarios.values())
        
        if difficulty:
            scenarios = [s for s in scenarios if s.difficulty == difficulty]
        
        return sorted(scenarios, key=lambda x: x.difficulty.value)
    
    def start_scenario(self, user_id: str, scenario_id: str) -> TrainingProgress:
        """Start a new training scenario for a user"""
        if scenario_id not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        progress = TrainingProgress(
            user_id=user_id,
            scenario_id=scenario_id,
            started_at=datetime.now()
        )
        
        self.user_progress[user_id][scenario_id] = progress
        return progress
    
    def get_current_step(
        self,
        user_id: str,
        scenario_id: str
    ) -> Optional[TrainingStep]:
        """Get the current step for a user's scenario"""
        progress = self.user_progress.get(user_id, {}).get(scenario_id)
        if not progress:
            return None
        
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return None
        
        if progress.current_step_index >= len(scenario.steps):
            return None
        
        return scenario.steps[progress.current_step_index]
    
    def complete_step(
        self,
        user_id: str,
        scenario_id: str,
        step_id: str,
        score: int,
        actions_taken: List[str]
    ) -> Dict:
        """Mark a step as complete and record score"""
        progress = self.user_progress.get(user_id, {}).get(scenario_id)
        if not progress:
            return {'success': False, 'error': 'No active scenario'}
        
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return {'success': False, 'error': 'Unknown scenario'}
        
        current_step = self.get_current_step(user_id, scenario_id)
        if not current_step or current_step.step_id != step_id:
            return {'success': False, 'error': 'Step mismatch'}
        
        # Record step completion
        progress.completed_steps.append(step_id)
        progress.step_scores[step_id] = score
        progress.total_score += score
        progress.current_step_index += 1
        
        # Check if scenario is complete
        if progress.current_step_index >= len(scenario.steps):
            progress.completed_at = datetime.now()
            progress.time_spent_seconds = int(
                (progress.completed_at - progress.started_at).total_seconds()
            )
            
            # Determine if passed
            pass_score = (scenario.pass_threshold_percent / 100) * scenario.total_points
            progress.passed = progress.total_score >= pass_score
        
        return {
            'success': True,
            'step_completed': step_id,
            'score': score,
            'total_score': progress.total_score,
            'scenario_complete': progress.completed_at is not None,
            'passed': progress.passed
        }
    
    def use_hint(self, user_id: str, scenario_id: str) -> Optional[str]:
        """Use a hint for the current step"""
        progress = self.user_progress.get(user_id, {}).get(scenario_id)
        if not progress:
            return None
        
        current_step = self.get_current_step(user_id, scenario_id)
        if not current_step or not current_step.hints:
            return None
        
        progress.hints_used += 1
        hint_index = min(progress.hints_used - 1, len(current_step.hints) - 1)
        return current_step.hints[hint_index]
    
    def skip_step(self, user_id: str, scenario_id: str, step_id: str) -> Dict:
        """Skip a non-required step"""
        progress = self.user_progress.get(user_id, {}).get(scenario_id)
        if not progress:
            return {'success': False, 'error': 'No active scenario'}
        
        current_step = self.get_current_step(user_id, scenario_id)
        if not current_step or current_step.step_id != step_id:
            return {'success': False, 'error': 'Step mismatch'}
        
        if current_step.required:
            return {'success': False, 'error': 'Cannot skip required step'}
        
        progress.skipped_steps.append(step_id)
        progress.current_step_index += 1
        
        return {'success': True, 'step_skipped': step_id}
    
    def get_progress(self, user_id: str, scenario_id: str) -> Optional[TrainingProgress]:
        """Get user's progress for a scenario"""
        return self.user_progress.get(user_id, {}).get(scenario_id)


# ============================================================================
# Skill Assessment System
# ============================================================================

class SkillAssessment:
    """Assess analyst skills and recommend training"""
    
    def __init__(self):
        self.assessment_history: Dict[str, List[SkillAssessmentResult]] = {}
    
    def assess_user(
        self,
        user_id: str,
        completed_scenarios: List[TrainingProgress]
    ) -> SkillAssessmentResult:
        """Assess user skill level based on completed scenarios"""
        
        if not completed_scenarios:
            return SkillAssessmentResult(
                user_id=user_id,
                assessed_at=datetime.now(),
                skill_level=SkillLevel.NOVICE,
                strengths=[],
                weaknesses=["No training completed yet"],
                recommended_scenarios=[TrainingScenario.PHISHING_INVESTIGATION],
                overall_score=0,
                category_scores={}
            )
        
        # Calculate category scores
        category_scores = {
            'detection': 0,
            'analysis': 0,
            'response': 0,
            'remediation': 0
        }
        
        total_score = 0
        passed_count = 0
        
        for progress in completed_scenarios:
            if progress.passed:
                passed_count += 1
            total_score += progress.total_score
            
            # Categorize scores (simplified)
            for step_id, score in progress.step_scores.items():
                if 'detection' in step_id or 'intro' in step_id:
                    category_scores['detection'] += score
                elif 'analysis' in step_id:
                    category_scores['analysis'] += score
                elif 'action' in step_id or 'mitigation' in step_id:
                    category_scores['response'] += score
                elif 'remediation' in step_id or 'recovery' in step_id:
                    category_scores['remediation'] += score
        
        # Normalize category scores
        for category in category_scores:
            category_scores[category] = min(100, category_scores[category])
        
        overall_score = total_score // len(completed_scenarios) if completed_scenarios else 0
        
        # Determine skill level
        if overall_score >= 90 and passed_count >= 8:
            skill_level = SkillLevel.EXPERT
        elif overall_score >= 80 and passed_count >= 6:
            skill_level = SkillLevel.ADVANCED
        elif overall_score >= 70 and passed_count >= 4:
            skill_level = SkillLevel.INTERMEDIATE
        elif overall_score >= 60 and passed_count >= 2:
            skill_level = SkillLevel.BEGINNER
        else:
            skill_level = SkillLevel.NOVICE
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for category, score in category_scores.items():
            if score >= 80:
                strengths.append(f"Strong {category} skills")
            elif score < 60:
                weaknesses.append(f"Need improvement in {category}")
        
        # Recommend scenarios
        recommended = self._recommend_scenarios(skill_level, category_scores)
        
        result = SkillAssessmentResult(
            user_id=user_id,
            assessed_at=datetime.now(),
            skill_level=skill_level,
            strengths=strengths,
            weaknesses=weaknesses,
            recommended_scenarios=recommended,
            overall_score=overall_score,
            category_scores=category_scores
        )
        
        # Store assessment
        if user_id not in self.assessment_history:
            self.assessment_history[user_id] = []
        self.assessment_history[user_id].append(result)
        
        return result
    
    def _recommend_scenarios(
        self,
        skill_level: SkillLevel,
        category_scores: Dict[str, int]
    ) -> List[TrainingScenario]:
        """Recommend training scenarios based on skill level and weaknesses"""
        recommendations = []
        
        # Find weakest categories
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1]
        )
        
        # Map categories to scenarios
        category_to_scenarios = {
            'detection': [
                TrainingScenario.PHISHING_INVESTIGATION,
                TrainingScenario.SQL_INJECTION_DETECTION
            ],
            'analysis': [
                TrainingScenario.APT_HUNTING,
                TrainingScenario.INSIDER_THREAT_DETECTION
            ],
            'response': [
                TrainingScenario.RANSOMWARE_RESPONSE,
                TrainingScenario.DDOS_MITIGATION
            ],
            'remediation': [
                TrainingScenario.ZERO_DAY_ASSESSMENT,
                TrainingScenario.CLOUD_INCIDENT_RESPONSE
            ]
        }
        
        # Recommend scenarios for weakest categories
        for category, score in sorted_categories[:2]:
            scenarios = category_to_scenarios.get(category, [])
            recommendations.extend(scenarios)
        
        # Add advanced scenarios for higher skill levels
        if skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
            recommendations.extend([
                TrainingScenario.APT_HUNTING,
                TrainingScenario.SUPPLY_CHAIN_ATTACK
            ])
        
        return recommendations[:5]  # Return top 5
    
    def get_assessment_history(
        self,
        user_id: str
    ) -> List[SkillAssessmentResult]:
        """Get user's assessment history"""
        return self.assessment_history.get(user_id, [])


# ============================================================================
# Practice Simulator
# ============================================================================

class PracticeSimulator:
    """Safe environment for practicing security operations"""
    
    def __init__(self):
        self.practice_sessions: Dict[str, Dict] = {}
    
    def create_practice_environment(
        self,
        user_id: str,
        scenario_type: TrainingScenario
    ) -> Dict:
        """Create a practice environment for a scenario"""
        session_id = f"{user_id}_{scenario_type.value}_{datetime.now().timestamp()}"
        
        # Generate synthetic threats based on scenario
        synthetic_threats = self._generate_synthetic_threats(scenario_type)
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'scenario_type': scenario_type.value,
            'created_at': datetime.now(),
            'threats': synthetic_threats,
            'actions_taken': [],
            'mistakes': 0,
            'practice_mode': True
        }
        
        self.practice_sessions[session_id] = session
        return session
    
    def _generate_synthetic_threats(
        self,
        scenario_type: TrainingScenario
    ) -> List[Dict]:
        """Generate realistic but synthetic threats for practice"""
        threats = []
        
        if scenario_type == TrainingScenario.PHISHING_INVESTIGATION:
            threats = [
                {
                    'type': 'email',
                    'sender': 'support@paypa1-security.com',  # Typosquatting
                    'subject': 'URGENT: Verify your account now!',
                    'body': 'Your account will be suspended in 24 hours...',
                    'indicators': ['typosquatting', 'urgency', 'suspicious_link']
                },
                {
                    'type': 'email',
                    'sender': 'ceo@company.com',  # Spoofed
                    'subject': 'Wire Transfer Request',
                    'body': 'Please send $50,000 to this account immediately',
                    'indicators': ['spoofed_sender', 'financial_request']
                }
            ]
        
        elif scenario_type == TrainingScenario.RANSOMWARE_RESPONSE:
            threats = [
                {
                    'type': 'ransomware',
                    'variant': 'Lockbit 3.0',
                    'affected_systems': 15,
                    'file_types_encrypted': ['.docx', '.xlsx', '.pdf'],
                    'ransom_amount': '$100,000 in Bitcoin',
                    'indicators': ['file_encryption', 'ransom_note', 'c2_communication']
                }
            ]
        
        elif scenario_type == TrainingScenario.DDOS_MITIGATION:
            threats = [
                {
                    'type': 'ddos',
                    'attack_type': 'SYN Flood',
                    'traffic_volume': '50 Gbps',
                    'source_ips': random.randint(10000, 50000),
                    'target': 'web_server',
                    'indicators': ['high_syn_packets', 'multiple_sources']
                }
            ]
        
        return threats
    
    def execute_practice_action(
        self,
        session_id: str,
        action: str,
        parameters: Dict
    ) -> Dict:
        """Execute an action in the practice environment"""
        session = self.practice_sessions.get(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        # Simulate action results
        result = {
            'success': True,
            'action': action,
            'timestamp': datetime.now(),
            'outcome': self._simulate_action_outcome(action, parameters, session),
            'feedback': self._generate_feedback(action, parameters, session)
        }
        
        session['actions_taken'].append(result)
        
        # Track mistakes
        if not result['outcome'].get('correct', True):
            session['mistakes'] += 1
        
        return result
    
    def _simulate_action_outcome(
        self,
        action: str,
        parameters: Dict,
        session: Dict
    ) -> Dict:
        """Simulate the outcome of an action"""
        # This would contain complex simulation logic
        # For now, simplified version
        
        if action == 'quarantine_email':
            return {
                'correct': True,
                'impact': 'Email successfully quarantined',
                'threat_contained': True
            }
        
        elif action == 'isolate_systems':
            return {
                'correct': True,
                'impact': 'Systems isolated from network',
                'spread_prevented': True
            }
        
        elif action == 'enable_rate_limiting':
            return {
                'correct': True,
                'impact': 'Rate limiting enabled',
                'attack_mitigated': True
            }
        
        return {
            'correct': True,
            'impact': 'Action executed',
            'result': 'Success'
        }
    
    def _generate_feedback(
        self,
        action: str,
        parameters: Dict,
        session: Dict
    ) -> str:
        """Generate educational feedback for the action"""
        feedback_templates = {
            'quarantine_email': "Good job! Quarantining suspicious emails prevents users from interacting with them.",
            'isolate_systems': "Excellent! Isolating infected systems is critical to prevent lateral movement.",
            'enable_rate_limiting': "Smart choice! Rate limiting helps reduce the impact of flood attacks."
        }
        
        return feedback_templates.get(
            action,
            "Action completed. Review the outcome to learn more."
        )
    
    def end_practice_session(self, session_id: str) -> Dict:
        """End a practice session and provide summary"""
        session = self.practice_sessions.get(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        duration = (datetime.now() - session['created_at']).total_seconds()
        
        summary = {
            'session_id': session_id,
            'duration_seconds': int(duration),
            'actions_taken': len(session['actions_taken']),
            'mistakes': session['mistakes'],
            'accuracy': (len(session['actions_taken']) - session['mistakes']) / 
                       max(1, len(session['actions_taken'])) * 100,
            'completed': True
        }
        
        return summary


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("JUPITER VR Training System - Module G.3.11")
    print("=" * 70)
    
    # Initialize components
    scenario_manager = TrainingScenarioManager()
    skill_assessment = SkillAssessment()
    practice_sim = PracticeSimulator()
    
    # List available scenarios
    print("\nAvailable Training Scenarios:")
    for scenario in scenario_manager.list_scenarios():
        print(f"  - {scenario.title}")
        print(f"    Difficulty: {scenario.difficulty.value}")
        print(f"    Duration: {scenario.estimated_duration_minutes} minutes")
        print(f"    Steps: {len(scenario.steps)}")
        print()
    
    # Start a scenario
    user_id = "analyst_001"
    progress = scenario_manager.start_scenario(user_id, "phishing_investigation")
    print(f"\nStarted scenario: {progress.scenario_id}")
    
    # Get current step
    current_step = scenario_manager.get_current_step(user_id, "phishing_investigation")
    if current_step:
        print(f"Current step: {current_step.title}")
        print(f"Description: {current_step.description}")
        print(f"Points available: {current_step.points}")
    
    # Create practice environment
    practice_session = practice_sim.create_practice_environment(
        user_id,
        TrainingScenario.PHISHING_INVESTIGATION
    )
    print(f"\nCreated practice session: {practice_session['session_id']}")
    print(f"Synthetic threats generated: {len(practice_session['threats'])}")
    
    print("\n" + "=" * 70)
    print("Training System Ready!")
    print("=" * 70)
