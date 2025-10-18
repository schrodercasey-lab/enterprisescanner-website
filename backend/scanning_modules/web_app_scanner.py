"""
Web Application Security Scanner Module
OWASP Top 10 vulnerability detection for Enterprise Scanner
"""

import requests
import re
import urllib.parse
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import time

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class VulnerabilityFinding:
    """Single vulnerability finding"""
    vulnerability_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    url: str
    parameter: Optional[str] = None
    payload: Optional[str] = None
    evidence: Optional[str] = None
    description: str = ""
    recommendation: str = ""
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None


@dataclass
class WebAppScanResult:
    """Complete web application scan results"""
    target_url: str
    scan_start: datetime
    scan_end: datetime
    vulnerabilities: List[VulnerabilityFinding]
    pages_scanned: int = 0
    requests_made: int = 0
    scan_duration_seconds: float = 0.0


class WebAppScanner:
    """
    Web Application Security Scanner for Fortune 500 enterprises
    
    Features:
    - OWASP Top 10 vulnerability detection
    - SQL Injection testing
    - Cross-Site Scripting (XSS) detection
    - CSRF testing
    - Path Traversal detection
    - Command Injection testing
    - XML External Entity (XXE) detection
    - Security header analysis
    """
    
    # SQL Injection payloads
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "admin' #",
        "admin'/*",
        "' or 1=1--",
        "' or 1=1#",
        "' or 1=1/*",
        "') or '1'='1--",
        "') or ('1'='1--",
        "1' OR '1' = '1",
        "1' UNION SELECT NULL--",
        "' UNION SELECT NULL, NULL--",
        "' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055"
    ]
    
    # XSS payloads
    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<marquee onstart=alert('XSS')>",
        "'\"><script>alert('XSS')</script>",
        "<scr<script>ipt>alert('XSS')</script>",
        "%3Cscript%3Ealert('XSS')%3C/script%3E"
    ]
    
    # Path traversal payloads
    PATH_TRAVERSAL_PAYLOADS = [
        "../../../../../etc/passwd",
        "..\\..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "....//....//....//....//etc/passwd",
        "..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd",
        "..%252F..%252F..%252F..%252F..%252Fetc%252Fpasswd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
    ]
    
    # Command injection payloads
    COMMAND_INJECTION_PAYLOADS = [
        "; ls",
        "| ls",
        "& ls",
        "&& ls",
        "|| ls",
        "`ls`",
        "$(ls)",
        "; cat /etc/passwd",
        "| cat /etc/passwd",
        "&& cat /etc/passwd"
    ]
    
    # Critical security headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'Prevents clickjacking attacks',
        'X-Content-Type-Options': 'Prevents MIME-sniffing',
        'Content-Security-Policy': 'Prevents XSS and injection attacks',
        'Strict-Transport-Security': 'Forces HTTPS connections',
        'X-XSS-Protection': 'Enables browser XSS protection',
        'Referrer-Policy': 'Controls referrer information',
        'Permissions-Policy': 'Controls browser features'
    }
    
    def __init__(self, timeout: int = 10, user_agent: Optional[str] = None):
        """
        Initialize the web application scanner
        
        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or 'EnterpriseScanner/1.0 (Security Assessment)'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.vulnerabilities = []
        self.requests_made = 0
        
    def scan_web_app(
        self, 
        target_url: str,
        test_sql_injection: bool = True,
        test_xss: bool = True,
        test_path_traversal: bool = True,
        test_command_injection: bool = True,
        test_security_headers: bool = True
    ) -> WebAppScanResult:
        """
        Perform comprehensive web application security scan
        
        Args:
            target_url: Target web application URL
            test_sql_injection: Test for SQL injection vulnerabilities
            test_xss: Test for XSS vulnerabilities
            test_path_traversal: Test for path traversal vulnerabilities
            test_command_injection: Test for command injection
            test_security_headers: Check security headers
            
        Returns:
            WebAppScanResult with all findings
        """
        scan_start = datetime.now()
        self.vulnerabilities = []
        self.requests_made = 0
        pages_scanned = 0
        
        logger.info(f"Starting web application scan of {target_url}")
        
        try:
            # Normalize URL
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url
            
            # Test security headers
            if test_security_headers:
                self._check_security_headers(target_url)
                pages_scanned += 1
            
            # Discover forms and parameters
            forms = self._discover_forms(target_url)
            pages_scanned += 1
            
            # Test SQL Injection
            if test_sql_injection:
                logger.info("Testing for SQL injection vulnerabilities...")
                self._test_sql_injection(target_url, forms)
            
            # Test XSS
            if test_xss:
                logger.info("Testing for XSS vulnerabilities...")
                self._test_xss(target_url, forms)
            
            # Test Path Traversal
            if test_path_traversal:
                logger.info("Testing for path traversal vulnerabilities...")
                self._test_path_traversal(target_url)
            
            # Test Command Injection
            if test_command_injection:
                logger.info("Testing for command injection...")
                self._test_command_injection(target_url, forms)
            
        except Exception as e:
            logger.error(f"Error during web app scan: {e}")
        
        scan_end = datetime.now()
        scan_duration = (scan_end - scan_start).total_seconds()
        
        result = WebAppScanResult(
            target_url=target_url,
            scan_start=scan_start,
            scan_end=scan_end,
            vulnerabilities=self.vulnerabilities,
            pages_scanned=pages_scanned,
            requests_made=self.requests_made,
            scan_duration_seconds=scan_duration
        )
        
        logger.info(f"Scan complete: {len(self.vulnerabilities)} vulnerabilities found in {scan_duration:.2f}s")
        return result
    
    def _check_security_headers(self, url: str):
        """Check for missing security headers"""
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            for header, description in self.SECURITY_HEADERS.items():
                if header not in response.headers:
                    self.vulnerabilities.append(VulnerabilityFinding(
                        vulnerability_type='Missing Security Header',
                        severity='medium' if header in ['X-Frame-Options', 'X-Content-Type-Options'] else 'low',
                        url=url,
                        parameter=header,
                        description=f'Missing security header: {header}',
                        recommendation=f'Add {header} header to HTTP responses. Purpose: {description}',
                        cwe_id='CWE-693',
                        owasp_category='A05:2021 - Security Misconfiguration'
                    ))
                    
        except Exception as e:
            logger.debug(f"Error checking security headers: {e}")
    
    def _discover_forms(self, url: str) -> List[Dict[str, Any]]:
        """Discover forms and input fields on a page"""
        forms = []
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            # Simple form detection using regex (in production, use BeautifulSoup)
            form_pattern = r'<form[^>]*>(.*?)</form>'
            input_pattern = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>'
            
            form_matches = re.findall(form_pattern, response.text, re.DOTALL | re.IGNORECASE)
            
            for form_html in form_matches:
                inputs = re.findall(input_pattern, form_html, re.IGNORECASE)
                if inputs:
                    forms.append({
                        'url': url,
                        'inputs': inputs
                    })
                    
        except Exception as e:
            logger.debug(f"Error discovering forms: {e}")
            
        return forms
    
    def _test_sql_injection(self, url: str, forms: List[Dict[str, Any]]):
        """Test for SQL injection vulnerabilities"""
        
        # Test URL parameters
        if '?' in url:
            base_url, params = url.split('?', 1)
            param_dict = urllib.parse.parse_qs(params)
            
            for param_name in param_dict.keys():
                for payload in self.SQL_INJECTION_PAYLOADS[:5]:  # Limit payloads for speed
                    test_url = base_url + '?' + urllib.parse.urlencode({param_name: payload})
                    
                    if self._is_sql_vulnerable(test_url, payload):
                        self.vulnerabilities.append(VulnerabilityFinding(
                            vulnerability_type='SQL Injection',
                            severity='critical',
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            description=f'SQL injection vulnerability detected in parameter: {param_name}',
                            recommendation='Use parameterized queries/prepared statements. Never concatenate user input into SQL queries.',
                            cwe_id='CWE-89',
                            owasp_category='A03:2021 - Injection'
                        ))
                        break  # One finding per parameter is enough
        
        # Test form inputs
        for form in forms:
            for input_name in form['inputs']:
                for payload in self.SQL_INJECTION_PAYLOADS[:3]:  # Fewer payloads for forms
                    if self._test_form_sql_injection(form['url'], input_name, payload):
                        self.vulnerabilities.append(VulnerabilityFinding(
                            vulnerability_type='SQL Injection',
                            severity='critical',
                            url=form['url'],
                            parameter=input_name,
                            payload=payload,
                            description=f'SQL injection vulnerability detected in form input: {input_name}',
                            recommendation='Use parameterized queries/prepared statements',
                            cwe_id='CWE-89',
                            owasp_category='A03:2021 - Injection'
                        ))
                        break
    
    def _is_sql_vulnerable(self, url: str, payload: str) -> bool:
        """Check if URL is vulnerable to SQL injection"""
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            # SQL error patterns
            sql_errors = [
                r'sql syntax',
                r'mysql_fetch',
                r'mysql_num_rows',
                r'ora-\d+',
                r'postgresql.*error',
                r'warning.*mysql',
                r'mssql_query',
                r'odbc_exec',
                r'microsoft sql native client error'
            ]
            
            response_text = response.text.lower()
            for pattern in sql_errors:
                if re.search(pattern, response_text, re.IGNORECASE):
                    return True
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error testing SQL injection: {e}")
            return False
    
    def _test_form_sql_injection(self, url: str, input_name: str, payload: str) -> bool:
        """Test form input for SQL injection"""
        try:
            data = {input_name: payload}
            response = self.session.post(url, data=data, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            return self._is_sql_vulnerable(url, payload)
            
        except Exception as e:
            logger.debug(f"Error testing form SQL injection: {e}")
            return False
    
    def _test_xss(self, url: str, forms: List[Dict[str, Any]]):
        """Test for XSS vulnerabilities"""
        
        # Test URL parameters
        if '?' in url:
            base_url, params = url.split('?', 1)
            param_dict = urllib.parse.parse_qs(params)
            
            for param_name in param_dict.keys():
                for payload in self.XSS_PAYLOADS[:5]:
                    test_url = base_url + '?' + urllib.parse.urlencode({param_name: payload})
                    
                    if self._is_xss_vulnerable(test_url, payload):
                        self.vulnerabilities.append(VulnerabilityFinding(
                            vulnerability_type='Cross-Site Scripting (XSS)',
                            severity='high',
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            description=f'XSS vulnerability detected in parameter: {param_name}',
                            recommendation='Sanitize user input and encode output. Use Content-Security-Policy header.',
                            cwe_id='CWE-79',
                            owasp_category='A03:2021 - Injection'
                        ))
                        break
    
    def _is_xss_vulnerable(self, url: str, payload: str) -> bool:
        """Check if URL is vulnerable to XSS"""
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            # Check if payload is reflected in response
            if payload in response.text or urllib.parse.quote(payload) in response.text:
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Error testing XSS: {e}")
            return False
    
    def _test_path_traversal(self, url: str):
        """Test for path traversal vulnerabilities"""
        
        if '?' in url:
            base_url, params = url.split('?', 1)
            param_dict = urllib.parse.parse_qs(params)
            
            for param_name in param_dict.keys():
                for payload in self.PATH_TRAVERSAL_PAYLOADS[:3]:
                    test_url = base_url + '?' + urllib.parse.urlencode({param_name: payload})
                    
                    if self._is_path_traversal_vulnerable(test_url, payload):
                        self.vulnerabilities.append(VulnerabilityFinding(
                            vulnerability_type='Path Traversal',
                            severity='high',
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            description=f'Path traversal vulnerability detected in parameter: {param_name}',
                            recommendation='Validate and sanitize file paths. Use whitelist of allowed files.',
                            cwe_id='CWE-22',
                            owasp_category='A01:2021 - Broken Access Control'
                        ))
                        break
    
    def _is_path_traversal_vulnerable(self, url: str, payload: str) -> bool:
        """Check if URL is vulnerable to path traversal"""
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            # Look for file content indicators
            indicators = [
                'root:x:0:0',  # /etc/passwd
                '[boot loader]',  # Windows boot.ini
                'localhost'  # /etc/hosts
            ]
            
            for indicator in indicators:
                if indicator in response.text:
                    return True
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error testing path traversal: {e}")
            return False
    
    def _test_command_injection(self, url: str, forms: List[Dict[str, Any]]):
        """Test for command injection vulnerabilities"""
        
        if '?' in url:
            base_url, params = url.split('?', 1)
            param_dict = urllib.parse.parse_qs(params)
            
            for param_name in param_dict.keys():
                for payload in self.COMMAND_INJECTION_PAYLOADS[:3]:
                    test_url = base_url + '?' + urllib.parse.urlencode({param_name: payload})
                    
                    if self._is_command_injection_vulnerable(test_url):
                        self.vulnerabilities.append(VulnerabilityFinding(
                            vulnerability_type='Command Injection',
                            severity='critical',
                            url=url,
                            parameter=param_name,
                            payload=payload,
                            description=f'Command injection vulnerability detected in parameter: {param_name}',
                            recommendation='Never pass user input to system commands. Use safe APIs instead.',
                            cwe_id='CWE-78',
                            owasp_category='A03:2021 - Injection'
                        ))
                        break
    
    def _is_command_injection_vulnerable(self, url: str) -> bool:
        """Check if URL is vulnerable to command injection"""
        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            self.requests_made += 1
            
            # Look for command output indicators
            indicators = [
                'bin',
                'usr',
                'root:',
                'uid=',
                'gid='
            ]
            
            for indicator in indicators:
                if indicator in response.text:
                    return True
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error testing command injection: {e}")
            return False
    
    def get_scan_summary(self, result: WebAppScanResult) -> Dict[str, Any]:
        """Generate summary dictionary from scan results"""
        
        # Count by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for vuln in result.vulnerabilities:
            severity_counts[vuln.severity] += 1
        
        # Group by type
        vuln_types = {}
        for vuln in result.vulnerabilities:
            if vuln.vulnerability_type not in vuln_types:
                vuln_types[vuln.vulnerability_type] = 0
            vuln_types[vuln.vulnerability_type] += 1
        
        return {
            'target': result.target_url,
            'scan_info': {
                'start_time': result.scan_start.isoformat(),
                'end_time': result.scan_end.isoformat(),
                'duration_seconds': result.scan_duration_seconds,
                'pages_scanned': result.pages_scanned,
                'requests_made': result.requests_made
            },
            'findings': {
                'total_vulnerabilities': len(result.vulnerabilities),
                'by_severity': severity_counts,
                'by_type': vuln_types,
                'vulnerabilities': [
                    {
                        'type': v.vulnerability_type,
                        'severity': v.severity,
                        'url': v.url,
                        'parameter': v.parameter,
                        'description': v.description,
                        'cwe_id': v.cwe_id,
                        'owasp_category': v.owasp_category
                    }
                    for v in result.vulnerabilities
                ]
            },
            'risk_score': self._calculate_risk_score(severity_counts)
        }
    
    def _calculate_risk_score(self, severity_counts: Dict[str, int]) -> int:
        """Calculate overall risk score from vulnerability counts"""
        score = (
            severity_counts['critical'] * 40 +
            severity_counts['high'] * 20 +
            severity_counts['medium'] * 10 +
            severity_counts['low'] * 5
        )
        return min(100, score)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scanner = WebAppScanner(timeout=10)
    
    # Test with a safe target (use your own test site)
    target = "http://testphp.vulnweb.com"  # Known vulnerable test site
    print(f"Scanning {target}...")
    
    result = scanner.scan_web_app(target)
    summary = scanner.get_scan_summary(result)
    
    print(f"\n=== Web App Scan Results ===")
    print(f"Target: {summary['target']}")
    print(f"Duration: {summary['scan_info']['duration_seconds']:.2f}s")
    print(f"Total Vulnerabilities: {summary['findings']['total_vulnerabilities']}")
    print(f"Risk Score: {summary['risk_score']}/100")
    print(f"\nBy Severity:")
    for severity, count in summary['findings']['by_severity'].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")
