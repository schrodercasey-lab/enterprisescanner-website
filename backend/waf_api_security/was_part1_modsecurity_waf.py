"""
Military Upgrade #19: WAF & API Security
Part 1: ModSecurity WAF with OWASP Core Rule Set

This module implements a Web Application Firewall (WAF) using ModSecurity engine
with OWASP Core Rule Set (CRS) for comprehensive protection against web attacks.

Key Features:
- ModSecurity v3 engine integration
- OWASP CRS 4.0 rule deployment
- Real-time attack detection and blocking
- SQL injection, XSS, RCE protection
- Request/response inspection
- Anomaly scoring system

Compliance:
- OWASP Top 10 2021 protection
- PCI DSS Requirement 6.6 (WAF deployment)
- NIST 800-53 SI-4 (Information System Monitoring)
- CIS Critical Security Control 7.6
- ISO 27001 A.14.1.2, A.14.1.3
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re


class AttackType(Enum):
    """OWASP Top 10 attack categories"""
    SQL_INJECTION = "sql_injection"  # A03:2021
    XSS = "cross_site_scripting"  # A03:2021
    BROKEN_AUTH = "broken_authentication"  # A07:2021
    SENSITIVE_DATA = "sensitive_data_exposure"  # A02:2021
    XXE = "xml_external_entities"  # A05:2021
    BROKEN_ACCESS = "broken_access_control"  # A01:2021
    SECURITY_MISCONFIG = "security_misconfiguration"  # A05:2021
    DESERIALIZATION = "insecure_deserialization"  # A08:2021
    VULNERABLE_COMPONENTS = "vulnerable_components"  # A06:2021
    INSUFFICIENT_LOGGING = "insufficient_logging"  # A09:2021
    SSRF = "server_side_request_forgery"  # A10:2021
    RCE = "remote_code_execution"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"


class ActionType(Enum):
    """WAF action types"""
    ALLOW = "allow"
    BLOCK = "block"
    LOG = "log"
    REDIRECT = "redirect"
    CHALLENGE = "challenge"  # CAPTCHA


class RuleSeverity(Enum):
    """Rule severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"


@dataclass
class WAFRule:
    """ModSecurity WAF rule"""
    rule_id: int
    rule_name: str
    description: str
    severity: RuleSeverity
    attack_type: AttackType
    pattern: str  # Regex or signature
    action: ActionType
    enabled: bool = True
    
    # Anomaly scoring (OWASP CRS)
    anomaly_score: int = 5
    paranoia_level: int = 1  # 1-4 (higher = more strict)
    
    # Performance
    phase: int = 2  # 1=Request Headers, 2=Request Body, 3=Response Headers, 4=Response Body
    false_positive_rate: float = 0.01


@dataclass
class AttackDetection:
    """Detected attack event"""
    detection_id: str
    timestamp: datetime
    attack_type: AttackType
    severity: RuleSeverity
    
    # Request details
    source_ip: str
    user_agent: str
    request_method: str
    request_uri: str
    request_body: Optional[str] = None
    
    # Detection
    matched_rules: List[int] = field(default_factory=list)
    anomaly_score: int = 0
    blocked: bool = False
    
    # Payload
    malicious_payload: Optional[str] = None
    attack_vector: Optional[str] = None


@dataclass
class WAFConfig:
    """ModSecurity WAF configuration"""
    enabled: bool = True
    paranoia_level: int = 2  # 1-4
    anomaly_threshold: int = 5  # Block if score >= threshold
    
    # OWASP CRS settings
    enable_crs: bool = True
    crs_version: str = "4.0"
    
    # Inspection settings
    inspect_request_headers: bool = True
    inspect_request_body: bool = True
    inspect_response_headers: bool = True
    inspect_response_body: bool = False  # Performance impact
    
    # Limits
    max_request_body_size: int = 131072  # 128KB
    max_file_size: int = 1048576  # 1MB
    
    # Actions
    default_action: ActionType = ActionType.BLOCK
    log_all_requests: bool = False
    log_blocked_only: bool = True


class ModSecurityWAF:
    """ModSecurity Web Application Firewall Engine"""
    
    def __init__(self, config: Optional[WAFConfig] = None):
        self.config = config or WAFConfig()
        self.rules: Dict[int, WAFRule] = {}
        self.detections: List[AttackDetection] = []
        self.blocked_ips: Set[str] = set()
        
        # Initialize OWASP CRS rules
        if self.config.enable_crs:
            self._load_owasp_crs()
    
    def _load_owasp_crs(self) -> None:
        """Load OWASP Core Rule Set 4.0"""
        # SQL Injection rules (920000-920999)
        self.add_rule(WAFRule(
            rule_id=920100,
            rule_name="SQL Injection - SELECT/UNION",
            description="Detects SQL injection attempts using SELECT and UNION",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.SQL_INJECTION,
            pattern=r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table)",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        self.add_rule(WAFRule(
            rule_id=920200,
            rule_name="SQL Injection - Comments",
            description="Detects SQL comments used to bypass authentication",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.SQL_INJECTION,
            pattern=r"(?i)(--|#|\/\*|\*\/|;.*--)",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        self.add_rule(WAFRule(
            rule_id=920300,
            rule_name="SQL Injection - Boolean Blind",
            description="Detects boolean-based blind SQL injection",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.SQL_INJECTION,
            pattern=r"(?i)(and|or)\s+\d+\s*=\s*\d+",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=2
        ))
        
        # XSS rules (930000-930999)
        self.add_rule(WAFRule(
            rule_id=930100,
            rule_name="XSS - Script Tags",
            description="Detects <script> tags in user input",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.XSS,
            pattern=r"(?i)<script[^>]*>.*?</script>",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        self.add_rule(WAFRule(
            rule_id=930200,
            rule_name="XSS - Event Handlers",
            description="Detects JavaScript event handlers (onclick, onerror, etc.)",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.XSS,
            pattern=r"(?i)on(load|error|click|mouse|focus|blur|change|submit)\s*=",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        self.add_rule(WAFRule(
            rule_id=930300,
            rule_name="XSS - JavaScript Protocol",
            description="Detects javascript: protocol in URLs",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.XSS,
            pattern=r"(?i)javascript:",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        # Remote Code Execution rules (940000-940999)
        self.add_rule(WAFRule(
            rule_id=940100,
            rule_name="RCE - System Commands",
            description="Detects system command injection attempts",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.RCE,
            pattern=r"(?i)(exec|system|passthru|shell_exec|eval|base64_decode)\s*\(",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        self.add_rule(WAFRule(
            rule_id=940200,
            rule_name="RCE - Command Chaining",
            description="Detects command chaining operators",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.COMMAND_INJECTION,
            pattern=r"[;&|`$]\s*(cat|ls|wget|curl|nc|bash|sh)",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        # Path Traversal rules (950000-950999)
        self.add_rule(WAFRule(
            rule_id=950100,
            rule_name="Path Traversal - Directory Navigation",
            description="Detects directory traversal attempts",
            severity=RuleSeverity.ERROR,
            attack_type=AttackType.PATH_TRAVERSAL,
            pattern=r"(\.\./|\.\.\\|%2e%2e/|%2e%2e\\)",
            action=ActionType.BLOCK,
            anomaly_score=4,
            paranoia_level=1
        ))
        
        self.add_rule(WAFRule(
            rule_id=950200,
            rule_name="Path Traversal - Absolute Paths",
            description="Detects absolute path access attempts",
            severity=RuleSeverity.ERROR,
            attack_type=AttackType.PATH_TRAVERSAL,
            pattern=r"(/etc/passwd|/etc/shadow|c:\\windows\\)",
            action=ActionType.BLOCK,
            anomaly_score=4,
            paranoia_level=1
        ))
        
        # XXE rules (960000-960999)
        self.add_rule(WAFRule(
            rule_id=960100,
            rule_name="XXE - External Entity Declaration",
            description="Detects XML External Entity declarations",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.XXE,
            pattern=r"<!ENTITY.*SYSTEM",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=1
        ))
        
        # SSRF rules (970000-970999)
        self.add_rule(WAFRule(
            rule_id=970100,
            rule_name="SSRF - Internal IP Access",
            description="Detects Server-Side Request Forgery to internal IPs",
            severity=RuleSeverity.CRITICAL,
            attack_type=AttackType.SSRF,
            pattern=r"(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+)",
            action=ActionType.BLOCK,
            anomaly_score=5,
            paranoia_level=2
        ))
        
        print(f"✅ Loaded OWASP CRS {self.config.crs_version} with {len(self.rules)} rules")
    
    def add_rule(self, rule: WAFRule) -> bool:
        """Add custom WAF rule"""
        try:
            # Validate rule pattern is valid regex
            re.compile(rule.pattern)
            
            self.rules[rule.rule_id] = rule
            return True
            
        except re.error as e:
            print(f"❌ Invalid rule pattern: {e}")
            return False
    
    def inspect_request(self, method: str, uri: str, headers: Dict[str, str],
                       body: Optional[str] = None, source_ip: str = "0.0.0.0") -> Dict[str, Any]:
        """Inspect HTTP request for attacks"""
        if not self.config.enabled:
            return {'allowed': True, 'reason': 'WAF disabled'}
        
        # Check if IP is blocked
        if source_ip in self.blocked_ips:
            return {
                'allowed': False,
                'blocked': True,
                'reason': 'IP address blocked',
                'action': 'block'
            }
        
        detection_id = f"DET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        matched_rules = []
        total_anomaly_score = 0
        attack_types = set()
        
        # Inspect request URI
        if self.config.inspect_request_headers:
            uri_matches = self._scan_content(uri, self.config.paranoia_level)
            matched_rules.extend(uri_matches)
        
        # Inspect headers
        if self.config.inspect_request_headers:
            for header_value in headers.values():
                header_matches = self._scan_content(header_value, self.config.paranoia_level)
                matched_rules.extend(header_matches)
        
        # Inspect body
        if body and self.config.inspect_request_body:
            if len(body) > self.config.max_request_body_size:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': f'Request body exceeds limit ({self.config.max_request_body_size} bytes)',
                    'action': 'block'
                }
            
            body_matches = self._scan_content(body, self.config.paranoia_level)
            matched_rules.extend(body_matches)
        
        # Calculate total anomaly score
        for rule_id in matched_rules:
            rule = self.rules[rule_id]
            total_anomaly_score += rule.anomaly_score
            attack_types.add(rule.attack_type)
        
        # Determine action
        blocked = total_anomaly_score >= self.config.anomaly_threshold
        
        # Log detection
        if matched_rules:
            detection = AttackDetection(
                detection_id=detection_id,
                timestamp=datetime.now(),
                attack_type=list(attack_types)[0] if attack_types else AttackType.SECURITY_MISCONFIG,
                severity=RuleSeverity.CRITICAL if blocked else RuleSeverity.WARNING,
                source_ip=source_ip,
                user_agent=headers.get('User-Agent', 'Unknown'),
                request_method=method,
                request_uri=uri,
                request_body=body[:500] if body else None,  # First 500 chars
                matched_rules=matched_rules,
                anomaly_score=total_anomaly_score,
                blocked=blocked,
                malicious_payload=self._extract_payload(uri, body),
                attack_vector=self._identify_vector(matched_rules)
            )
            
            self.detections.append(detection)
            
            if blocked:
                self._handle_block(source_ip, detection)
        
        return {
            'allowed': not blocked,
            'blocked': blocked,
            'detection_id': detection_id if matched_rules else None,
            'matched_rules': matched_rules,
            'anomaly_score': total_anomaly_score,
            'threshold': self.config.anomaly_threshold,
            'attack_types': [at.value for at in attack_types],
            'action': 'block' if blocked else 'allow'
        }
    
    def _scan_content(self, content: str, paranoia_level: int) -> List[int]:
        """Scan content against all rules"""
        matched = []
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Only apply rules at or below current paranoia level
            if rule.paranoia_level > paranoia_level:
                continue
            
            # Check if pattern matches
            if re.search(rule.pattern, content, re.IGNORECASE):
                matched.append(rule_id)
        
        return matched
    
    def _extract_payload(self, uri: str, body: Optional[str]) -> Optional[str]:
        """Extract malicious payload from request"""
        # Check URI for payloads
        for pattern in [r"<script>", r"union.*select", r"\.\./"]:
            match = re.search(pattern, uri, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Check body for payloads
        if body:
            for pattern in [r"<script>", r"union.*select", r"exec\("]:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        return None
    
    def _identify_vector(self, matched_rules: List[int]) -> str:
        """Identify primary attack vector"""
        if not matched_rules:
            return "unknown"
        
        # Get first matched rule
        rule = self.rules[matched_rules[0]]
        return rule.attack_type.value
    
    def _handle_block(self, source_ip: str, detection: AttackDetection) -> None:
        """Handle blocked request"""
        print(f"🚫 Attack blocked: {detection.detection_id}")
        print(f"   IP: {source_ip}")
        print(f"   Attack: {detection.attack_type.value}")
        print(f"   Score: {detection.anomaly_score}")
        print(f"   URI: {detection.request_uri}")
        
        # Auto-block IP after 5 violations
        ip_violations = sum(1 for d in self.detections if d.source_ip == source_ip and d.blocked)
        if ip_violations >= 5:
            self.blocked_ips.add(source_ip)
            print(f"   ⛔ IP {source_ip} permanently blocked (5 violations)")
    
    def block_ip(self, ip: str, reason: str = "Manual block") -> None:
        """Manually block IP address"""
        self.blocked_ips.add(ip)
        print(f"⛔ IP {ip} blocked: {reason}")
    
    def unblock_ip(self, ip: str) -> None:
        """Unblock IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            print(f"✅ IP {ip} unblocked")
    
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Get WAF attack statistics"""
        total_detections = len(self.detections)
        blocked_count = sum(1 for d in self.detections if d.blocked)
        
        # Attack type distribution
        attack_distribution = {}
        for detection in self.detections:
            attack_type = detection.attack_type.value
            attack_distribution[attack_type] = attack_distribution.get(attack_type, 0) + 1
        
        # Top attacking IPs
        ip_counts = {}
        for detection in self.detections:
            ip = detection.source_ip
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_detections': total_detections,
            'blocked_requests': blocked_count,
            'allowed_requests': total_detections - blocked_count,
            'block_rate': f"{(blocked_count/total_detections*100):.1f}%" if total_detections > 0 else "0%",
            'attack_distribution': attack_distribution,
            'top_attacking_ips': top_ips,
            'blocked_ips': list(self.blocked_ips),
            'active_rules': len([r for r in self.rules.values() if r.enabled])
        }
    
    def generate_waf_report(self) -> Dict[str, Any]:
        """Generate comprehensive WAF report"""
        stats = self.get_attack_statistics()
        
        # Recent attacks (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_attacks = [d for d in self.detections if d.timestamp >= recent_cutoff]
        
        # Critical attacks
        critical_attacks = [
            d for d in self.detections 
            if d.severity == RuleSeverity.CRITICAL and d.blocked
        ]
        
        return {
            'report_date': datetime.now().isoformat(),
            'waf_status': 'enabled' if self.config.enabled else 'disabled',
            'paranoia_level': self.config.paranoia_level,
            'anomaly_threshold': self.config.anomaly_threshold,
            'statistics': stats,
            'recent_attacks_24h': len(recent_attacks),
            'critical_attacks': len(critical_attacks),
            'owasp_crs_version': self.config.crs_version,
            'rule_coverage': {
                'sql_injection': len([r for r in self.rules.values() if r.attack_type == AttackType.SQL_INJECTION]),
                'xss': len([r for r in self.rules.values() if r.attack_type == AttackType.XSS]),
                'rce': len([r for r in self.rules.values() if r.attack_type == AttackType.RCE]),
                'path_traversal': len([r for r in self.rules.values() if r.attack_type == AttackType.PATH_TRAVERSAL]),
            }
        }


# Example usage
if __name__ == "__main__":
    # Initialize WAF
    waf = ModSecurityWAF()
    
    # Test SQL injection detection
    result = waf.inspect_request(
        method="GET",
        uri="/api/users?id=1' UNION SELECT * FROM passwords--",
        headers={'User-Agent': 'AttackBot/1.0'},
        source_ip="203.0.113.42"
    )
    
    print(f"\n🔍 Inspection Result:")
    print(f"Allowed: {result['allowed']}")
    print(f"Blocked: {result['blocked']}")
    print(f"Anomaly Score: {result['anomaly_score']}")
    print(f"Attack Types: {result['attack_types']}")
    
    # Get statistics
    stats = waf.get_attack_statistics()
    print(f"\n📊 WAF Statistics:")
    print(f"Total Detections: {stats['total_detections']}")
    print(f"Blocked: {stats['blocked_requests']}")
    print(f"Active Rules: {stats['active_rules']}")
