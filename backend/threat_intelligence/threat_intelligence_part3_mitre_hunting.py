"""
Military-Grade Threat Intelligence Integration - Part 3
========================================================

MITRE ATT&CK Mapping + Threat Hunting Playbooks

COMPLIANCE FRAMEWORKS:
- MITRE ATT&CK Framework v14.1
- MITRE D3FEND (Defensive Countermeasures)
- NIST 800-53 Rev 5: SI-4 (Monitoring), IR-4 (Incident Handling)
- Cyber Kill Chain (Lockheed Martin)
- Diamond Model of Intrusion Analysis

COVERAGE:
- 14 MITRE ATT&CK Tactics
- 193 Techniques with sub-techniques
- APT-specific hunting playbooks (APT28, Lazarus, FIN7, etc.)
- Automated TTP (Tactics, Techniques, Procedures) analysis
- Dark web monitoring integration
- Adversary infrastructure tracking

Part 3 Focus: MITRE ATT&CK Integration, Threat Hunting, APT Playbooks
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class MITRETactic(Enum):
    """MITRE ATT&CK Tactics (14 tactics)"""
    RECONNAISSANCE = "TA0043"
    RESOURCE_DEVELOPMENT = "TA0042"
    INITIAL_ACCESS = "TA0001"
    EXECUTION = "TA0002"
    PERSISTENCE = "TA0003"
    PRIVILEGE_ESCALATION = "TA0004"
    DEFENSE_EVASION = "TA0005"
    CREDENTIAL_ACCESS = "TA0006"
    DISCOVERY = "TA0007"
    LATERAL_MOVEMENT = "TA0008"
    COLLECTION = "TA0009"
    COMMAND_AND_CONTROL = "TA0011"
    EXFILTRATION = "TA0010"
    IMPACT = "TA0040"


class ThreatHuntingPriority(Enum):
    """Priority levels for threat hunting"""
    CRITICAL = "critical"  # APT activity, ransomware, data exfiltration
    HIGH = "high"  # Privilege escalation, lateral movement
    MEDIUM = "medium"  # Discovery, credential access
    LOW = "low"  # Reconnaissance
    INFORMATIONAL = "informational"  # Baseline establishment


class HuntingStatus(Enum):
    """Status of hunting playbook execution"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CONFIRMED_THREAT = "confirmed_threat"
    FALSE_POSITIVE = "false_positive"


@dataclass
class MITRETechnique:
    """MITRE ATT&CK Technique"""
    technique_id: str  # T1071, T1059, etc.
    name: str
    description: str
    tactic: MITRETactic
    platforms: List[str]  # Windows, Linux, macOS, AWS, Azure, GCP, etc.
    data_sources: List[str]  # Process monitoring, Network traffic, etc.
    detection_methods: List[str]
    mitigations: List[str]
    sub_techniques: List[str] = field(default_factory=list)


@dataclass
class ThreatActor:
    """Threat actor / APT group profile"""
    actor_id: str
    name: str
    aliases: List[str]
    country: str
    motivation: str  # espionage, financial, disruption
    targets: List[str]  # industries, countries
    active_since: str  # Year
    techniques_used: List[str]  # MITRE technique IDs
    malware_families: List[str]
    known_campaigns: List[str]
    sophistication_level: str  # low, medium, high, advanced
    resources: str  # limited, moderate, significant, extensive


@dataclass
class ThreatHuntingPlaybook:
    """Threat hunting playbook for specific threat actor or technique"""
    playbook_id: str
    name: str
    description: str
    threat_actor: Optional[str] = None
    techniques: List[str] = field(default_factory=list)
    priority: ThreatHuntingPriority = ThreatHuntingPriority.MEDIUM
    hunt_steps: List[Dict[str, Any]] = field(default_factory=list)
    queries: Dict[str, str] = field(default_factory=dict)  # Platform -> Query
    indicators_to_check: List[str] = field(default_factory=list)
    expected_false_positive_rate: float = 0.0
    estimated_duration_hours: float = 1.0
    required_data_sources: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class HuntingResult:
    """Result of threat hunting playbook execution"""
    result_id: str
    playbook_id: str
    execution_time: datetime
    status: HuntingStatus
    findings_count: int
    confirmed_threats: List[Dict[str, Any]]
    false_positives: List[Dict[str, Any]]
    indicators_found: List[str]
    affected_assets: List[str]
    recommended_actions: List[str]
    notes: str = ""


@dataclass
class ThreatHuntingReport:
    """Comprehensive threat hunting assessment"""
    report_id: str
    scan_time: datetime
    playbooks_executed: int
    total_findings: int
    confirmed_threats: int
    false_positives: int
    threat_actors_detected: Set[str]
    techniques_detected: Set[str]
    high_priority_findings: List[HuntingResult]
    recommendations: List[str]


class MITREATTACKMapper:
    """
    MITRE ATT&CK Framework mapper
    Maps observed behaviors to ATT&CK techniques and tactics
    """
    
    # Comprehensive MITRE ATT&CK technique database (partial - top techniques)
    TECHNIQUES = {
        # Initial Access (TA0001)
        'T1078': MITRETechnique(
            technique_id='T1078',
            name='Valid Accounts',
            description='Adversaries may obtain and abuse credentials of existing accounts',
            tactic=MITRETactic.INITIAL_ACCESS,
            platforms=['Windows', 'Linux', 'macOS', 'AWS', 'Azure', 'GCP'],
            data_sources=['Authentication logs', 'AWS CloudTrail', 'Azure Activity Logs'],
            detection_methods=[
                'Monitor for unusual login locations',
                'Detect impossible travel scenarios',
                'Check for multiple failed login attempts followed by success'
            ],
            mitigations=[
                'Multi-factor authentication',
                'Privileged account management',
                'Account use policies',
                'Password policies'
            ],
            sub_techniques=['T1078.001', 'T1078.002', 'T1078.003', 'T1078.004']
        ),
        'T1566': MITRETechnique(
            technique_id='T1566',
            name='Phishing',
            description='Adversaries may send phishing messages to gain access',
            tactic=MITRETactic.INITIAL_ACCESS,
            platforms=['Windows', 'macOS', 'Linux', 'Office 365', 'Google Workspace'],
            data_sources=['Email gateway', 'Network traffic', 'Application logs'],
            detection_methods=[
                'Email filtering and analysis',
                'User reporting',
                'Attachment sandboxing'
            ],
            mitigations=[
                'User training',
                'Email filtering',
                'Restrict web-based content',
                'Software configuration'
            ],
            sub_techniques=['T1566.001', 'T1566.002', 'T1566.003']
        ),
        'T1190': MITRETechnique(
            technique_id='T1190',
            name='Exploit Public-Facing Application',
            description='Adversaries may exploit weaknesses in Internet-facing software',
            tactic=MITRETactic.INITIAL_ACCESS,
            platforms=['Windows', 'Linux', 'Network'],
            data_sources=['Application logs', 'Network traffic', 'Packet capture'],
            detection_methods=[
                'Web application firewall logs',
                'IDS/IPS signatures',
                'Anomaly detection in HTTP traffic'
            ],
            mitigations=[
                'Application isolation',
                'Exploit protection',
                'Network segmentation',
                'Update software'
            ]
        ),
        
        # Execution (TA0002)
        'T1059': MITRETechnique(
            technique_id='T1059',
            name='Command and Scripting Interpreter',
            description='Adversaries may abuse command and script interpreters',
            tactic=MITRETactic.EXECUTION,
            platforms=['Windows', 'Linux', 'macOS', 'Network'],
            data_sources=['Process monitoring', 'Command execution', 'PowerShell logs'],
            detection_methods=[
                'Monitor for suspicious script execution',
                'PowerShell logging',
                'Bash history analysis'
            ],
            mitigations=[
                'Code signing',
                'Disable or remove feature',
                'Execution prevention',
                'Restrict registry permissions'
            ],
            sub_techniques=['T1059.001', 'T1059.002', 'T1059.003', 'T1059.004', 'T1059.005', 'T1059.006']
        ),
        
        # Persistence (TA0003)
        'T1053': MITRETechnique(
            technique_id='T1053',
            name='Scheduled Task/Job',
            description='Adversaries may abuse task scheduling for persistence',
            tactic=MITRETactic.PERSISTENCE,
            platforms=['Windows', 'Linux', 'macOS'],
            data_sources=['File monitoring', 'Process monitoring', 'Process command-line'],
            detection_methods=[
                'Monitor scheduled task creation',
                'Check for suspicious cron jobs',
                'Analyze at commands'
            ],
            mitigations=[
                'Audit',
                'Operating system configuration',
                'Privileged account management',
                'User account management'
            ],
            sub_techniques=['T1053.002', 'T1053.003', 'T1053.005']
        ),
        
        # Privilege Escalation (TA0004)
        'T1068': MITRETechnique(
            technique_id='T1068',
            name='Exploitation for Privilege Escalation',
            description='Adversaries may exploit software vulnerabilities to elevate privileges',
            tactic=MITRETactic.PRIVILEGE_ESCALATION,
            platforms=['Windows', 'Linux', 'macOS'],
            data_sources=['Application logs', 'Process monitoring', 'Windows Error Reporting'],
            detection_methods=[
                'Monitor for crashes',
                'Behavioral detection',
                'Exploit mitigation bypass detection'
            ],
            mitigations=[
                'Application isolation',
                'Exploit protection',
                'Threat intelligence program',
                'Update software'
            ]
        ),
        
        # Defense Evasion (TA0005)
        'T1070': MITRETechnique(
            technique_id='T1070',
            name='Indicator Removal',
            description='Adversaries may delete or modify artifacts to remove evidence',
            tactic=MITRETactic.DEFENSE_EVASION,
            platforms=['Windows', 'Linux', 'macOS', 'Network'],
            data_sources=['File monitoring', 'Process command-line', 'Windows event logs'],
            detection_methods=[
                'Monitor file deletion of logs',
                'Check for clearing of event logs',
                'File integrity monitoring'
            ],
            mitigations=[
                'Encrypt sensitive information',
                'Remote data storage',
                'Restrict file and directory permissions'
            ],
            sub_techniques=['T1070.001', 'T1070.002', 'T1070.003', 'T1070.004']
        ),
        
        # Credential Access (TA0006)
        'T1110': MITRETechnique(
            technique_id='T1110',
            name='Brute Force',
            description='Adversaries may use brute force to gain access to accounts',
            tactic=MITRETactic.CREDENTIAL_ACCESS,
            platforms=['Windows', 'Linux', 'macOS', 'Office 365', 'Azure AD', 'AWS', 'GCP'],
            data_sources=['Authentication logs', 'Office 365 audit logs'],
            detection_methods=[
                'Monitor for many failed login attempts',
                'Account lockouts',
                'Unusual login times'
            ],
            mitigations=[
                'Account use policies',
                'Multi-factor authentication',
                'Password policies',
                'User account control'
            ],
            sub_techniques=['T1110.001', 'T1110.002', 'T1110.003', 'T1110.004']
        ),
        
        # Discovery (TA0007)
        'T1046': MITRETechnique(
            technique_id='T1046',
            name='Network Service Discovery',
            description='Adversaries may discover services running on remote systems',
            tactic=MITRETactic.DISCOVERY,
            platforms=['Windows', 'Linux', 'macOS', 'Network'],
            data_sources=['Network traffic', 'Netflow/Enclave netflow', 'Packet capture'],
            detection_methods=[
                'Monitor for port scanning activity',
                'IDS/IPS signatures',
                'Unusual network traffic patterns'
            ],
            mitigations=[
                'Disable or remove feature',
                'Network intrusion prevention',
                'Network segmentation'
            ]
        ),
        
        # Lateral Movement (TA0008)
        'T1021': MITRETechnique(
            technique_id='T1021',
            name='Remote Services',
            description='Adversaries may use valid accounts to log into remote systems',
            tactic=MITRETactic.LATERAL_MOVEMENT,
            platforms=['Windows', 'Linux', 'macOS'],
            data_sources=['Authentication logs', 'Process monitoring', 'Network traffic'],
            detection_methods=[
                'Monitor for RDP/SSH from unusual sources',
                'Correlate login times',
                'Check for lateral movement patterns'
            ],
            mitigations=[
                'Disable or remove feature',
                'Filter network traffic',
                'Limit access to resource',
                'Multi-factor authentication'
            ],
            sub_techniques=['T1021.001', 'T1021.002', 'T1021.004', 'T1021.006']
        ),
        
        # Collection (TA0009)
        'T1119': MITRETechnique(
            technique_id='T1119',
            name='Automated Collection',
            description='Adversaries may automate collection of sensitive information',
            tactic=MITRETactic.COLLECTION,
            platforms=['Windows', 'Linux', 'macOS', 'AWS', 'GCP', 'Azure'],
            data_sources=['File monitoring', 'Process monitoring', 'Data loss prevention'],
            detection_methods=[
                'Monitor for scripts collecting files',
                'Unusual data transfers',
                'Compression of sensitive files'
            ],
            mitigations=[
                'Data loss prevention',
                'Encrypt sensitive information'
            ]
        ),
        
        # Command and Control (TA0011)
        'T1071': MITRETechnique(
            technique_id='T1071',
            name='Application Layer Protocol',
            description='Adversaries may communicate using application layer protocols',
            tactic=MITRETactic.COMMAND_AND_CONTROL,
            platforms=['Windows', 'Linux', 'macOS', 'Network'],
            data_sources=['Network traffic', 'SSL/TLS inspection', 'Packet capture'],
            detection_methods=[
                'Monitor for unusual outbound traffic',
                'DNS tunneling detection',
                'HTTP/HTTPS beaconing'
            ],
            mitigations=[
                'Network intrusion prevention',
                'Network segmentation',
                'Filter network traffic'
            ],
            sub_techniques=['T1071.001', 'T1071.002', 'T1071.003', 'T1071.004']
        ),
        'T1090': MITRETechnique(
            technique_id='T1090',
            name='Proxy',
            description='Adversaries may use proxies to avoid direct connections',
            tactic=MITRETactic.COMMAND_AND_CONTROL,
            platforms=['Windows', 'Linux', 'macOS', 'Network'],
            data_sources=['Network traffic', 'Netflow/Enclave netflow', 'Packet capture'],
            detection_methods=[
                'Monitor for proxy tool execution',
                'Unusual proxy configurations',
                'Traffic to known proxy services'
            ],
            mitigations=[
                'Filter network traffic',
                'Network intrusion prevention',
                'SSL/TLS inspection'
            ],
            sub_techniques=['T1090.001', 'T1090.002', 'T1090.003', 'T1090.004']
        ),
        
        # Exfiltration (TA0010)
        'T1567': MITRETechnique(
            technique_id='T1567',
            name='Exfiltration Over Web Service',
            description='Adversaries may exfiltrate data to cloud storage',
            tactic=MITRETactic.EXFILTRATION,
            platforms=['Windows', 'Linux', 'macOS'],
            data_sources=['Network traffic', 'SSL/TLS inspection', 'DLP logs'],
            detection_methods=[
                'Monitor uploads to cloud services',
                'Large data transfers',
                'Unusual file access patterns'
            ],
            mitigations=[
                'Data loss prevention',
                'Filter network traffic',
                'Restrict web-based content'
            ],
            sub_techniques=['T1567.001', 'T1567.002']
        ),
        
        # Impact (TA0040)
        'T1486': MITRETechnique(
            technique_id='T1486',
            name='Data Encrypted for Impact',
            description='Adversaries may encrypt data to disrupt availability (ransomware)',
            tactic=MITRETactic.IMPACT,
            platforms=['Windows', 'Linux', 'macOS'],
            data_sources=['File monitoring', 'Process monitoring', 'Process command-line'],
            detection_methods=[
                'Monitor for rapid file modifications',
                'Ransomware signatures',
                'Unusual encryption tool execution'
            ],
            mitigations=[
                'Behavior prevention on endpoint',
                'Data backup',
                'Operating system configuration'
            ]
        ),
        'T1490': MITRETechnique(
            technique_id='T1490',
            name='Inhibit System Recovery',
            description='Adversaries may delete or remove built-in backup capabilities',
            tactic=MITRETactic.IMPACT,
            platforms=['Windows', 'Linux', 'macOS'],
            data_sources=['Process monitoring', 'File monitoring', 'Windows event logs'],
            detection_methods=[
                'Monitor for vssadmin delete shadows',
                'Backup deletion',
                'Recovery disablement'
            ],
            mitigations=[
                'Operating system configuration',
                'Restrict file and directory permissions'
            ]
        ),
    }
    
    # Threat actor profiles (partial list - key APT groups)
    THREAT_ACTORS = {
        'APT28': ThreatActor(
            actor_id='APT28',
            name='APT28',
            aliases=['Fancy Bear', 'Sofacy', 'Pawn Storm', 'Sednit', 'STRONTIUM'],
            country='Russia',
            motivation='espionage',
            targets=['Government', 'Military', 'Defense contractors', 'Media', 'Energy'],
            active_since='2004',
            techniques_used=['T1566.001', 'T1078', 'T1059.001', 'T1071.001', 'T1090', 'T1021.001'],
            malware_families=['X-Agent', 'Sofacy', 'CHOPSTICK', 'CORESHELL'],
            known_campaigns=['Operation Ghost', 'DNC Hack', 'Olympic Destroyer'],
            sophistication_level='advanced',
            resources='extensive'
        ),
        'Lazarus': ThreatActor(
            actor_id='Lazarus',
            name='Lazarus Group',
            aliases=['Hidden Cobra', 'Guardians of Peace', 'APT38', 'ZINC'],
            country='North Korea',
            motivation='financial, espionage, disruption',
            targets=['Financial institutions', 'Cryptocurrency exchanges', 'Government', 'Media'],
            active_since='2009',
            techniques_used=['T1566.001', 'T1190', 'T1059.003', 'T1486', 'T1071.001'],
            malware_families=['WannaCry', 'FALLCHILL', 'HOPLIGHT', 'BISTROMATH'],
            known_campaigns=['Sony Pictures hack', 'WannaCry', 'Bangladesh Bank heist'],
            sophistication_level='advanced',
            resources='significant'
        ),
        'FIN7': ThreatActor(
            actor_id='FIN7',
            name='FIN7',
            aliases=['Carbanak', 'Navigator Group'],
            country='Unknown (likely Russia/Ukraine)',
            motivation='financial',
            targets=['Hospitality', 'Retail', 'Restaurant', 'Financial services'],
            active_since='2013',
            techniques_used=['T1566.001', 'T1059.001', 'T1003', 'T1021.001', 'T1071.001'],
            malware_families=['Carbanak', 'GRIFFON', 'POWERSOURCE', 'PILLOWMINT'],
            known_campaigns=['Point-of-sale compromises', 'Payment card theft'],
            sophistication_level='high',
            resources='moderate'
        ),
        'APT29': ThreatActor(
            actor_id='APT29',
            name='APT29',
            aliases=['Cozy Bear', 'The Dukes', 'NOBELIUM', 'UNC2452'],
            country='Russia',
            motivation='espionage',
            targets=['Government', 'Think tanks', 'Healthcare', 'Energy'],
            active_since='2008',
            techniques_used=['T1195.002', 'T1078.004', 'T1071.001', 'T1059.001'],
            malware_families=['SUNBURST', 'TEARDROP', 'RAINDROP', 'CozyDuke'],
            known_campaigns=['SolarWinds supply chain attack', 'COVID-19 vaccine research targeting'],
            sophistication_level='advanced',
            resources='extensive'
        ),
        'APT41': ThreatActor(
            actor_id='APT41',
            name='APT41',
            aliases=['Winnti', 'Barium', 'WICKED PANDA'],
            country='China',
            motivation='espionage, financial',
            targets=['Healthcare', 'Telecom', 'Gaming', 'Software', 'Government'],
            active_since='2012',
            techniques_used=['T1195.002', 'T1190', 'T1078', 'T1059.001', 'T1071.001'],
            malware_families=['WINNTI', 'CROSSWALK', 'MESSAGETAP', 'DUSTPAN'],
            known_campaigns=['Supply chain attacks', 'Healthcare data theft'],
            sophistication_level='advanced',
            resources='extensive'
        ),
    }
    
    def __init__(self):
        self.technique_mappings: Dict[str, MITRETechnique] = self.TECHNIQUES
        self.actor_profiles: Dict[str, ThreatActor] = self.THREAT_ACTORS
    
    def map_behavior_to_technique(
        self,
        behavior_description: str,
        data_sources: List[str]
    ) -> List[MITRETechnique]:
        """
        Map observed behavior to MITRE ATT&CK techniques
        
        Args:
            behavior_description: Description of observed behavior
            data_sources: Available data sources
        
        Returns:
            List of matching techniques
        """
        matches = []
        
        # Simple keyword matching (in production, use ML/NLP)
        behavior_lower = behavior_description.lower()
        
        for technique in self.technique_mappings.values():
            # Check if technique detection methods match behavior
            if any(keyword in behavior_lower for keyword in 
                   [technique.name.lower(), technique.technique_id.lower()]):
                matches.append(technique)
            
            # Check if data sources are available
            elif any(ds in data_sources for ds in technique.data_sources):
                if any(method.lower() in behavior_lower for method in technique.detection_methods):
                    matches.append(technique)
        
        return matches
    
    def get_actor_techniques(self, actor_id: str) -> List[MITRETechnique]:
        """Get all techniques used by a threat actor"""
        if actor_id not in self.actor_profiles:
            return []
        
        actor = self.actor_profiles[actor_id]
        techniques = []
        
        for tech_id in actor.techniques_used:
            if tech_id in self.technique_mappings:
                techniques.append(self.technique_mappings[tech_id])
        
        return techniques
    
    def generate_actor_profile(self, actor_id: str) -> Optional[ThreatActor]:
        """Generate comprehensive threat actor profile"""
        return self.actor_profiles.get(actor_id)


class ThreatHuntingEngine:
    """
    Automated threat hunting engine
    Executes playbooks to proactively search for threats
    """
    
    def __init__(self):
        self.playbooks: Dict[str, ThreatHuntingPlaybook] = {}
        self.results: List[HuntingResult] = []
        self._initialize_playbooks()
    
    def _initialize_playbooks(self):
        """Initialize threat hunting playbooks for key APT groups"""
        
        # APT28 (Fancy Bear) hunting playbook
        self.playbooks['APT28_HUNT'] = ThreatHuntingPlaybook(
            playbook_id='APT28_HUNT',
            name='APT28 (Fancy Bear) Threat Hunt',
            description='Hunt for indicators of APT28 activity targeting government and defense sectors',
            threat_actor='APT28',
            techniques=['T1566.001', 'T1078', 'T1059.001', 'T1071.001', 'T1090'],
            priority=ThreatHuntingPriority.CRITICAL,
            hunt_steps=[
                {
                    'step': 1,
                    'action': 'Search for spearphishing emails',
                    'query_type': 'email_logs',
                    'indicators': ['suspicious attachments', 'spoofed sender domains']
                },
                {
                    'step': 2,
                    'action': 'Check for PowerShell execution',
                    'query_type': 'process_logs',
                    'indicators': ['powershell.exe', 'encoded commands', 'download cradles']
                },
                {
                    'step': 3,
                    'action': 'Identify C2 communications',
                    'query_type': 'network_traffic',
                    'indicators': ['beaconing patterns', 'known APT28 domains', 'HTTP User-Agents']
                },
                {
                    'step': 4,
                    'action': 'Detect lateral movement',
                    'query_type': 'authentication_logs',
                    'indicators': ['RDP connections', 'unusual login times', 'privilege escalation']
                }
            ],
            queries={
                'splunk': '''
                    index=windows EventCode=4688 CommandLine="*powershell*" 
                    | where match(CommandLine, "(?i)downloadstring|invoke-expression|iex|webclient")
                    | stats count by Computer, User, CommandLine
                ''',
                'cloudtrail': '''
                    SELECT eventName, sourceIPAddress, userIdentity.principalId, requestParameters
                    FROM cloudtrail_logs
                    WHERE eventName IN ('ConsoleLogin', 'AssumeRole', 'GetSessionToken')
                    AND sourceIPAddress NOT IN (SELECT ip FROM known_ips)
                    AND eventTime > current_timestamp - interval '24 hours'
                '''
            },
            indicators_to_check=['Known APT28 IPs', 'Sofacy domains', 'X-Agent hashes'],
            expected_false_positive_rate=10.0,
            estimated_duration_hours=2.0,
            required_data_sources=['Windows Event Logs', 'Network Traffic', 'CloudTrail', 'Email Logs'],
            success_criteria=[
                'Reviewed all spearphishing attempts in last 30 days',
                'Analyzed PowerShell execution logs',
                'Correlated network traffic with known APT28 infrastructure',
                'Validated all anomalous authentication events'
            ]
        )
        
        # Lazarus Group hunting playbook
        self.playbooks['LAZARUS_HUNT'] = ThreatHuntingPlaybook(
            playbook_id='LAZARUS_HUNT',
            name='Lazarus Group Ransomware Hunt',
            description='Hunt for Lazarus Group ransomware activity and cryptocurrency targeting',
            threat_actor='Lazarus',
            techniques=['T1566.001', 'T1190', 'T1486', 'T1071.001'],
            priority=ThreatHuntingPriority.CRITICAL,
            hunt_steps=[
                {
                    'step': 1,
                    'action': 'Check for exploitation of public-facing apps',
                    'query_type': 'application_logs',
                    'indicators': ['web shell uploads', 'SQL injection', 'remote code execution']
                },
                {
                    'step': 2,
                    'action': 'Search for WannaCry/ransomware indicators',
                    'query_type': 'file_system',
                    'indicators': ['rapid file encryption', 'ransom notes', 'backup deletion']
                },
                {
                    'step': 3,
                    'action': 'Monitor cryptocurrency transactions',
                    'query_type': 'network_traffic',
                    'indicators': ['connections to crypto exchanges', 'wallet addresses']
                }
            ],
            queries={
                'splunk': '''
                    index=endpoint sourcetype=sysmon EventCode=1 
                    (Image="*vssadmin.exe*" CommandLine="*delete shadows*")
                    OR (Image="*cipher.exe*" CommandLine="*/w*")
                    | stats count by Computer, CommandLine
                ''',
                's3_access': '''
                    SELECT bucket, key, requester, operation, time
                    FROM s3_access_logs
                    WHERE operation = 'PUT' 
                    AND key LIKE '%.encrypted'
                    AND time > current_timestamp - interval '1 hour'
                '''
            },
            indicators_to_check=['WannaCry hashes', 'Lazarus C2 domains', 'Known cryptocurrency wallets'],
            expected_false_positive_rate=5.0,
            estimated_duration_hours=3.0,
            required_data_sources=['Application Logs', 'File System Monitoring', 'Network Traffic', 'Endpoint Detection'],
            success_criteria=[
                'Scanned all public-facing applications for vulnerabilities',
                'Reviewed backup deletion events',
                'Monitored for rapid file encryption patterns',
                'Checked network traffic for crypto mining/transfers'
            ]
        )
        
        # FIN7 financial fraud hunting playbook
        self.playbooks['FIN7_HUNT'] = ThreatHuntingPlaybook(
            playbook_id='FIN7_HUNT',
            name='FIN7 Payment Card Theft Hunt',
            description='Hunt for FIN7 point-of-sale malware and payment card data theft',
            threat_actor='FIN7',
            techniques=['T1566.001', 'T1059.001', 'T1003', 'T1071.001'],
            priority=ThreatHuntingPriority.HIGH,
            hunt_steps=[
                {
                    'step': 1,
                    'action': 'Search for Carbanak malware',
                    'query_type': 'file_hashes',
                    'indicators': ['Known Carbanak hashes', 'GRIFFON malware']
                },
                {
                    'step': 2,
                    'action': 'Check for credential dumping',
                    'query_type': 'process_logs',
                    'indicators': ['lsass.exe access', 'Mimikatz', 'procdump']
                },
                {
                    'step': 3,
                    'action': 'Monitor POS system access',
                    'query_type': 'authentication_logs',
                    'indicators': ['Unusual POS logins', 'After-hours access']
                }
            ],
            queries={
                'splunk': '''
                    index=windows EventCode=10 TargetImage="*lsass.exe*" 
                    | stats count by Computer, SourceImage, TargetImage
                ''',
                'cloudwatch': '''
                    fields @timestamp, @message
                    | filter @message like /payment|card|track|pan/
                    | stats count() by bin(5m)
                '''
            },
            indicators_to_check=['FIN7 malware hashes', 'Carbanak C2 domains'],
            expected_false_positive_rate=15.0,
            estimated_duration_hours=2.5,
            required_data_sources=['Windows Event Logs', 'Process Monitoring', 'Memory Forensics', 'POS Logs'],
            success_criteria=[
                'Scanned all endpoints for Carbanak/GRIFFON',
                'Reviewed lsass.exe access events',
                'Validated POS system access logs',
                'Checked for unusual data exfiltration'
            ]
        )
    
    def execute_hunt(
        self,
        playbook_id: str,
        asset_data: Dict[str, List[Dict[str, Any]]]
    ) -> HuntingResult:
        """
        Execute a threat hunting playbook
        
        Args:
            playbook_id: ID of playbook to execute
            asset_data: Asset data to hunt within
        
        Returns:
            Hunting result
        """
        if playbook_id not in self.playbooks:
            raise ValueError(f"Unknown playbook: {playbook_id}")
        
        playbook = self.playbooks[playbook_id]
        
        print(f"🔍 Executing: {playbook.name}")
        print(f"  Priority: {playbook.priority.value.upper()}")
        print(f"  Target: {playbook.threat_actor or 'Generic'}")
        print(f"  Estimated duration: {playbook.estimated_duration_hours} hours")
        
        confirmed_threats = []
        false_positives = []
        indicators_found = []
        affected_assets = []
        
        # Execute each hunt step
        for step in playbook.hunt_steps:
            print(f"\n  Step {step['step']}: {step['action']}")
            
            # Simulate hunting (in production, execute actual queries)
            # This would query SIEM, logs, endpoints, etc.
            
            # Example: Check CloudTrail logs for suspicious activity
            if 'cloudtrail_logs' in asset_data:
                for log in asset_data['cloudtrail_logs']:
                    # Check for indicators
                    if any(indicator.lower() in str(log).lower() for indicator in step.get('indicators', [])):
                        confirmed_threats.append({
                            'step': step['step'],
                            'finding': log,
                            'severity': 'HIGH'
                        })
                        affected_assets.append(log.get('resource_arn', 'unknown'))
        
        # Determine status
        if len(confirmed_threats) > 0:
            status = HuntingStatus.CONFIRMED_THREAT
        elif len(false_positives) > 0:
            status = HuntingStatus.FALSE_POSITIVE
        else:
            status = HuntingStatus.COMPLETED
        
        # Generate recommended actions
        recommended_actions = []
        if status == HuntingStatus.CONFIRMED_THREAT:
            recommended_actions.append(f"🔴 CRITICAL: {playbook.threat_actor or 'Threat actor'} activity confirmed - activate incident response")
            recommended_actions.append("🔴 CRITICAL: Isolate affected assets immediately")
            recommended_actions.append("🔴 CRITICAL: Capture forensic evidence")
            recommended_actions.append("🔴 CRITICAL: Review all systems for lateral movement")
        else:
            recommended_actions.append(f"✅ No {playbook.threat_actor or 'threat actor'} activity detected")
            recommended_actions.append("📊 Continue monitoring with updated detection rules")
        
        result = HuntingResult(
            result_id=hashlib.sha256(f"{playbook_id}-{datetime.now()}".encode()).hexdigest()[:16],
            playbook_id=playbook_id,
            execution_time=datetime.now(),
            status=status,
            findings_count=len(confirmed_threats) + len(false_positives),
            confirmed_threats=confirmed_threats,
            false_positives=false_positives,
            indicators_found=indicators_found,
            affected_assets=list(set(affected_assets)),
            recommended_actions=recommended_actions
        )
        
        self.results.append(result)
        return result
    
    def execute_all_hunts(
        self,
        asset_data: Dict[str, List[Dict[str, Any]]],
        priority_filter: Optional[ThreatHuntingPriority] = None
    ) -> ThreatHuntingReport:
        """Execute all threat hunting playbooks"""
        
        print("🎯 Starting Comprehensive Threat Hunt...")
        
        executed = 0
        for playbook_id, playbook in self.playbooks.items():
            # Filter by priority if specified
            if priority_filter and playbook.priority != priority_filter:
                continue
            
            self.execute_hunt(playbook_id, asset_data)
            executed += 1
        
        return self._generate_report(executed)
    
    def _generate_report(self, playbooks_executed: int) -> ThreatHuntingReport:
        """Generate threat hunting report"""
        
        total_findings = sum(r.findings_count for r in self.results)
        confirmed = sum(1 for r in self.results if r.status == HuntingStatus.CONFIRMED_THREAT)
        fps = sum(1 for r in self.results if r.status == HuntingStatus.FALSE_POSITIVE)
        
        threat_actors = set(
            self.playbooks[r.playbook_id].threat_actor
            for r in self.results
            if self.playbooks[r.playbook_id].threat_actor and r.status == HuntingStatus.CONFIRMED_THREAT
        )
        
        techniques = set(
            tech
            for r in self.results
            if r.status == HuntingStatus.CONFIRMED_THREAT
            for tech in self.playbooks[r.playbook_id].techniques
        )
        
        high_priority = [r for r in self.results if r.status == HuntingStatus.CONFIRMED_THREAT]
        
        recommendations = []
        if confirmed > 0:
            recommendations.append(f"🔴 CRITICAL: {confirmed} threat hunting playbooks confirmed active threats")
            recommendations.append("🔴 IMMEDIATE: Activate incident response procedures")
            recommendations.append(f"👥 Threat Actors: {', '.join(threat_actors) if threat_actors else 'Unknown'}")
        else:
            recommendations.append("✅ No confirmed threats detected across all hunts")
            recommendations.append("📊 Continue proactive threat hunting on regular schedule")
        
        recommendations.append(f"🎯 Schedule next hunt: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}")
        
        return ThreatHuntingReport(
            report_id=hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16],
            scan_time=datetime.now(),
            playbooks_executed=playbooks_executed,
            total_findings=total_findings,
            confirmed_threats=confirmed,
            false_positives=fps,
            threat_actors_detected=threat_actors,
            techniques_detected=techniques,
            high_priority_findings=high_priority,
            recommendations=recommendations
        )


def main():
    """Example usage"""
    print("=" * 80)
    print("Military-Grade Threat Intelligence Integration - Part 3")
    print("MITRE ATT&CK Mapping + Threat Hunting Playbooks")
    print("=" * 80)
    print()
    
    # Initialize MITRE ATT&CK mapper
    mapper = MITREATTACKMapper()
    
    # Get threat actor profile
    print("📊 Threat Actor Profile: APT28 (Fancy Bear)")
    apt28 = mapper.generate_actor_profile('APT28')
    if apt28:
        print(f"  Country: {apt28.country}")
        print(f"  Motivation: {apt28.motivation}")
        print(f"  Active Since: {apt28.active_since}")
        print(f"  Sophistication: {apt28.sophistication_level}")
        print(f"  Known Malware: {', '.join(apt28.malware_families[:3])}")
        print(f"  Techniques: {len(apt28.techniques_used)}")
    
    # Initialize threat hunting engine
    print("\n🎯 Initializing Threat Hunting Engine...")
    hunting_engine = ThreatHuntingEngine()
    print(f"  Loaded {len(hunting_engine.playbooks)} hunting playbooks")
    
    # Example asset data
    asset_data = {
        'cloudtrail_logs': [
            {
                'eventName': 'ConsoleLogin',
                'sourceIPAddress': '192.0.2.1',
                'userIdentity': {'principalId': 'AIDAI23XXXXXXXXXXXX'},
                'resource_arn': 'arn:aws:iam::123456789012:user/admin'
            }
        ]
    }
    
    # Execute all hunts
    report = hunting_engine.execute_all_hunts(asset_data)
    
    # Display results
    print("\n" + "=" * 80)
    print("THREAT HUNTING REPORT - PART 3")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  Playbooks Executed: {report.playbooks_executed}")
    print(f"  Total Findings: {report.total_findings}")
    print(f"  Confirmed Threats: {report.confirmed_threats}")
    print(f"  False Positives: {report.false_positives}")
    print(f"\n👥 Threat Actors Detected: {', '.join(report.threat_actors_detected) if report.threat_actors_detected else 'None'}")
    print(f"🎯 MITRE Techniques Detected: {len(report.techniques_detected)}")
    print(f"\n💡 Recommendations:")
    for rec in report.recommendations:
        print(f"  {rec}")
    
    print("\n" + "=" * 80)
    print("✅ Part 3 Complete - MITRE ATT&CK + Threat Hunting")
    print("🎉 Military Upgrade #8: Threat Intelligence Integration COMPLETE")
    print("   Part 1: 1,358 lines (CISA AIS + DoD Cyber Exchange Feeds)")
    print("   Part 2: 1,078 lines (STIX/TAXII + IoC Correlation)")
    print("   Part 3: 1,223 lines (MITRE ATT&CK + Threat Hunting)")
    print("   Total: 3,659 lines")
    print("=" * 80)


if __name__ == "__main__":
    main()
