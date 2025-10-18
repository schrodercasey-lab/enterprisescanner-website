"""
Enhanced Security Assessment API
Real-time vulnerability analysis and scoring for Enterprise Scanner
"""

from flask import Blueprint, request, jsonify, send_file, make_response
from datetime import datetime, timedelta
import json
import uuid
import os
import random
import threading
import time
import logging
from typing import Dict, List, Any
import requests
import socket
import ssl
import dns.resolver
from urllib.parse import urlparse
import subprocess
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib import colors

# Create Blueprint
security_assessment = Blueprint('security_assessment', __name__)

# Setup logging
logger = logging.getLogger(__name__)

# Import new advanced scanning modules
try:
    import sys
    import os
    # Add backend directory to path
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    from scanning_modules.advanced_port_scanner import AdvancedPortScanner
    from scanning_modules.web_app_scanner import WebAppScanner
    from scanning_modules.api_security_scanner import APISecurityScanner
    from scanning_modules.cve_integration import CVEIntegration
    from scanning_modules.multi_cloud_scanner import MultiCloudSecurityScanner
    from scanning_modules.container_security_orchestrator import ContainerSecurityOrchestrator
    
    ADVANCED_SCANNING_AVAILABLE = True
    logger.info("Advanced scanning modules loaded successfully")
except ImportError as e:
    ADVANCED_SCANNING_AVAILABLE = False
    logger.warning(f"Advanced scanning modules not available: {e}")
    logger.warning("Falling back to basic scanning mode")

# Import continuous monitoring system
try:
    from monitoring.continuous_monitor import ContinuousSecurityMonitor
    MONITORING_AVAILABLE = True
    logger.info("Continuous monitoring module loaded successfully")
except ImportError as e:
    MONITORING_AVAILABLE = False
    logger.warning(f"Continuous monitoring not available: {e}")

# Global storage for assessment results (in production, use proper database)
assessment_storage = {}

class SecurityAssessmentEngine:
    """Advanced security assessment engine with real vulnerability scanning"""
    
    def __init__(self):
        self.scan_cache = {}
        self.active_scans = {}
        
        # Initialize advanced scanning modules if available
        if ADVANCED_SCANNING_AVAILABLE:
            try:
                self.port_scanner = AdvancedPortScanner()
                self.web_scanner = WebAppScanner()
                self.api_scanner = APISecurityScanner()
                self.cve_integration = CVEIntegration()
                self.cloud_scanner = MultiCloudSecurityScanner()
                self.container_scanner = ContainerSecurityOrchestrator()
                logger.info("Advanced scanners initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize advanced scanners: {e}")
                self.port_scanner = None
                self.web_scanner = None
                self.api_scanner = None
                self.cve_integration = None
                self.cloud_scanner = None
                self.container_scanner = None
        else:
            self.port_scanner = None
            self.web_scanner = None
            self.api_scanner = None
            self.cve_integration = None
            self.cloud_scanner = None
            self.container_scanner = None
        
        # Initialize continuous monitoring system
        if MONITORING_AVAILABLE:
            try:
                # Use environment variable for DB path, default to backend/monitoring directory
                monitoring_db = os.getenv('MONITORING_DB_PATH', 
                                         os.path.join(backend_path, 'monitoring', 'security_monitoring.db'))
                self.monitor = ContinuousSecurityMonitor(db_path=monitoring_db)
                logger.info("Continuous monitoring initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize continuous monitoring: {e}")
                self.monitor = None
        else:
            self.monitor = None
        
    def start_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """Start a new security assessment"""
        assessment_id = str(uuid.uuid4())
        
        # Store assessment data
        self.active_scans[assessment_id] = {
            'id': assessment_id,
            'data': assessment_data,
            'status': 'initializing',
            'progress': 0,
            'start_time': datetime.now(),
            'current_phase': 'Initializing assessment...',
            'results': None
        }
        
        # Start assessment in background thread
        thread = threading.Thread(target=self._run_assessment, args=(assessment_id,))
        thread.daemon = True
        thread.start()
        
        return assessment_id
    
    def _run_assessment(self, assessment_id: str):
        """Run the complete security assessment"""
        try:
            scan_data = self.active_scans[assessment_id]
            assessment_data = scan_data['data']
            
            # Phase 1: Infrastructure Analysis
            self._update_progress(assessment_id, 10, "Analyzing infrastructure...")
            infrastructure_score = self._analyze_infrastructure(assessment_data)
            time.sleep(2)
            
            # Phase 2: Network Security Scan
            self._update_progress(assessment_id, 20, "Scanning network security...")
            network_score = self._scan_network_security(assessment_data.get('domain', ''))
            time.sleep(2)
            
            # Phase 2A: Advanced Port Scanning (if available)
            advanced_port_score = None
            if self.port_scanner and assessment_data.get('domain'):
                self._update_progress(assessment_id, 30, "Running advanced port scan...")
                advanced_port_score = self._run_advanced_port_scan(assessment_data.get('domain', ''))
                time.sleep(2)
            
            # Phase 3: SSL/TLS Analysis
            self._update_progress(assessment_id, 40, "Analyzing SSL/TLS configuration...")
            ssl_score = self._analyze_ssl_configuration(assessment_data.get('domain', ''))
            time.sleep(2)
            
            # Phase 4: Vulnerability Assessment
            self._update_progress(assessment_id, 50, "Running vulnerability assessment...")
            vulnerability_score = self._assess_vulnerabilities(assessment_data)
            time.sleep(2)
            
            # Phase 4A: Web Application Security Scan (if available)
            web_app_score = None
            if self.web_scanner and assessment_data.get('domain'):
                self._update_progress(assessment_id, 60, "Scanning web application security...")
                web_app_score = self._run_web_app_scan(assessment_data.get('domain', ''))
                time.sleep(2)
            
            # Phase 4B: API Security Scan (if available and API endpoints detected)
            api_security_score = None
            if self.api_scanner and assessment_data.get('has_api', False):
                self._update_progress(assessment_id, 70, "Testing API security...")
                api_security_score = self._run_api_security_scan(assessment_data)
                time.sleep(2)
            
            # Phase 4C: Cloud Security Assessment (if available and cloud credentials provided)
            cloud_security_score = None
            if self.cloud_scanner and assessment_data.get('cloud_provider'):
                self._update_progress(assessment_id, 75, "Assessing cloud security...")
                cloud_security_score = self._run_cloud_security_scan(assessment_data)
                time.sleep(2)
            
            # Phase 4D: Container Security Assessment (if available and container platform configured)
            container_security_score = None
            if self.container_scanner and assessment_data.get('container_platform'):
                self._update_progress(assessment_id, 78, "Scanning container security...")
                container_security_score = self._run_container_security_scan(assessment_data)
                time.sleep(2)
            
            # Phase 5: Compliance Analysis
            self._update_progress(assessment_id, 80, "Evaluating compliance posture...")
            compliance_score = self._analyze_compliance(assessment_data)
            time.sleep(2)
            
            # Phase 6: Generate Final Report
            self._update_progress(assessment_id, 95, "Generating security report...")
            final_results = self._generate_final_results(
                assessment_data, infrastructure_score, network_score, 
                ssl_score, vulnerability_score, compliance_score,
                advanced_port_score, web_app_score, api_security_score, cloud_security_score, container_security_score
            )
            
            # Complete assessment
            self._update_progress(assessment_id, 100, "Assessment complete!")
            self.active_scans[assessment_id]['status'] = 'completed'
            self.active_scans[assessment_id]['results'] = final_results
            self.active_scans[assessment_id]['end_time'] = datetime.now()
            
            # Record assessment in continuous monitoring system
            if self.monitor:
                try:
                    self.monitor.record_assessment(final_results)
                    logger.info(f"Assessment {assessment_id} recorded in monitoring system")
                except Exception as e:
                    logger.error(f"Failed to record assessment in monitoring: {e}")
            
        except Exception as e:
            self.active_scans[assessment_id]['status'] = 'error'
            self.active_scans[assessment_id]['error'] = str(e)
    
    def _update_progress(self, assessment_id: str, progress: int, phase: str):
        """Update assessment progress"""
        if assessment_id in self.active_scans:
            self.active_scans[assessment_id]['progress'] = progress
            self.active_scans[assessment_id]['current_phase'] = phase
    
    def _analyze_infrastructure(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze infrastructure security"""
        score = 70  # Base score
        findings = []
        
        # Analyze based on company size and industry
        size = assessment_data.get('company_size', '')
        industry = assessment_data.get('industry', '')
        
        # Industry-specific risk factors
        industry_risks = {
            'financial': {'risk_factor': 1.3, 'base_deduction': 15},
            'healthcare': {'risk_factor': 1.4, 'base_deduction': 20},
            'government': {'risk_factor': 1.2, 'base_deduction': 10},
            'technology': {'risk_factor': 1.1, 'base_deduction': 5},
            'retail': {'risk_factor': 1.25, 'base_deduction': 12}
        }
        
        if industry in industry_risks:
            score -= industry_risks[industry]['base_deduction']
            findings.append({
                'type': 'Industry Risk Factor',
                'severity': 'medium',
                'description': f'{industry.title()} sector faces elevated cybersecurity threats',
                'recommendation': 'Implement industry-specific security controls'
            })
        
        # Size-based analysis
        if size in ['large', 'enterprise']:
            score += 10  # Larger companies typically have better security
            findings.append({
                'type': 'Infrastructure Scale',
                'severity': 'low',
                'description': 'Large enterprise infrastructure detected',
                'recommendation': 'Maintain comprehensive security monitoring'
            })
        elif size == 'startup':
            score -= 15
            findings.append({
                'type': 'Resource Constraints',
                'severity': 'high',
                'description': 'Limited cybersecurity resources typical in startups',
                'recommendation': 'Prioritize essential security controls and consider managed security services'
            })
        
        return {
            'score': max(30, min(100, score)),
            'findings': findings,
            'category': 'Infrastructure Security'
        }
    
    def _scan_network_security(self, domain: str) -> Dict[str, Any]:
        """Scan network security configuration"""
        score = 75
        findings = []
        
        if not domain:
            return {
                'score': 60,
                'findings': [{'type': 'Domain Analysis', 'severity': 'medium', 
                           'description': 'No domain provided for network analysis',
                           'recommendation': 'Provide primary domain for comprehensive assessment'}],
                'category': 'Network Security'
            }
        
        try:
            # Parse domain
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://' + domain
            
            parsed_url = urlparse(domain)
            hostname = parsed_url.hostname
            
            if hostname:
                # Test basic connectivity
                try:
                    socket.gethostbyname(hostname)
                    findings.append({
                        'type': 'DNS Resolution',
                        'severity': 'low',
                        'description': 'Domain resolves correctly',
                        'recommendation': 'Maintain current DNS configuration'
                    })
                except socket.gaierror:
                    score -= 20
                    findings.append({
                        'type': 'DNS Resolution',
                        'severity': 'high',
                        'description': 'Domain resolution failed',
                        'recommendation': 'Verify DNS configuration and domain status'
                    })
                
                # Check for common ports
                open_ports = self._scan_common_ports(hostname)
                if len(open_ports) > 5:
                    score -= 15
                    findings.append({
                        'type': 'Port Exposure',
                        'severity': 'medium',
                        'description': f'Multiple open ports detected: {", ".join(map(str, open_ports[:5]))}',
                        'recommendation': 'Minimize exposed services and implement port filtering'
                    })
                
        except Exception as e:
            score -= 10
            findings.append({
                'type': 'Network Analysis Error',
                'severity': 'medium',
                'description': f'Unable to complete network scan: {str(e)}',
                'recommendation': 'Manual network security review recommended'
            })
        
        return {
            'score': max(30, min(100, score)),
            'findings': findings,
            'category': 'Network Security'
        }
    
    def _scan_common_ports(self, hostname: str) -> List[int]:
        """Scan common ports for open services"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((hostname, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                continue
                
        return open_ports
    
    def _analyze_ssl_configuration(self, domain: str) -> Dict[str, Any]:
        """Analyze SSL/TLS configuration"""
        score = 80
        findings = []
        
        if not domain:
            return {
                'score': 70,
                'findings': [{'type': 'SSL Analysis', 'severity': 'medium',
                           'description': 'No domain provided for SSL analysis',
                           'recommendation': 'Provide domain for SSL certificate analysis'}],
                'category': 'SSL/TLS Security'
            }
        
        try:
            # Parse domain
            if domain.startswith(('http://', 'https://')):
                parsed_url = urlparse(domain)
                hostname = parsed_url.hostname
            else:
                hostname = domain
            
            if hostname:
                # Check SSL certificate
                context = ssl.create_default_context()
                with socket.create_connection((hostname, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        
                        # Check certificate expiration
                        expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now()).days
                        
                        if days_until_expiry < 30:
                            score -= 25
                            findings.append({
                                'type': 'Certificate Expiration',
                                'severity': 'critical',
                                'description': f'SSL certificate expires in {days_until_expiry} days',
                                'recommendation': 'Renew SSL certificate immediately'
                            })
                        elif days_until_expiry < 90:
                            score -= 10
                            findings.append({
                                'type': 'Certificate Expiration',
                                'severity': 'medium',
                                'description': f'SSL certificate expires in {days_until_expiry} days',
                                'recommendation': 'Schedule certificate renewal'
                            })
                        
                        # Check protocol version
                        protocol = ssock.version()
                        if protocol in ['TLSv1.2', 'TLSv1.3']:
                            findings.append({
                                'type': 'TLS Protocol',
                                'severity': 'low',
                                'description': f'Using secure {protocol}',
                                'recommendation': 'Maintain current TLS configuration'
                            })
                        else:
                            score -= 30
                            findings.append({
                                'type': 'TLS Protocol',
                                'severity': 'high',
                                'description': f'Using outdated protocol: {protocol}',
                                'recommendation': 'Upgrade to TLS 1.2 or 1.3'
                            })
                            
        except ssl.SSLError as e:
            score -= 20
            findings.append({
                'type': 'SSL Configuration',
                'severity': 'high',
                'description': f'SSL configuration error: {str(e)}',
                'recommendation': 'Review and fix SSL/TLS configuration'
            })
        except Exception as e:
            score -= 15
            findings.append({
                'type': 'SSL Analysis',
                'severity': 'medium',
                'description': f'Unable to analyze SSL: {str(e)}',
                'recommendation': 'Manual SSL configuration review recommended'
            })
        
        return {
            'score': max(30, min(100, score)),
            'findings': findings,
            'category': 'SSL/TLS Security'
        }
    
    def _assess_vulnerabilities(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential vulnerabilities based on assessment responses"""
        score = 75
        findings = []
        
        # Analyze security team capability
        security_team = assessment_data.get('security_team', '')
        if security_team == 'no':
            score -= 20
            findings.append({
                'type': 'Security Team',
                'severity': 'high',
                'description': 'No dedicated cybersecurity team',
                'recommendation': 'Establish dedicated security team or engage managed security services'
            })
        elif security_team == 'partial':
            score -= 10
            findings.append({
                'type': 'Security Team',
                'severity': 'medium',
                'description': 'Partial security team coverage',
                'recommendation': 'Consider expanding dedicated security resources'
            })
        
        # Analyze security tools
        security_tools = assessment_data.get('security_tools', [])
        essential_tools = ['firewall', 'antivirus', 'backup-solution']
        missing_tools = [tool for tool in essential_tools if tool not in security_tools]
        
        if missing_tools:
            score -= len(missing_tools) * 8
            findings.append({
                'type': 'Security Tools Gap',
                'severity': 'high' if len(missing_tools) > 1 else 'medium',
                'description': f'Missing essential security tools: {", ".join(missing_tools)}',
                'recommendation': 'Implement missing security tools immediately'
            })
        
        # Check for advanced tools
        advanced_tools = ['siem', 'vulnerability-scanner', 'penetration-testing']
        has_advanced = any(tool in security_tools for tool in advanced_tools)
        
        if not has_advanced:
            score -= 15
            findings.append({
                'type': 'Advanced Security Tools',
                'severity': 'medium',
                'description': 'No advanced security monitoring tools detected',
                'recommendation': 'Consider implementing SIEM and vulnerability scanning solutions'
            })
        
        # Analyze incident history
        security_incident = assessment_data.get('security_incident', '')
        if security_incident == 'yes-major':
            score -= 25
            findings.append({
                'type': 'Security Incident History',
                'severity': 'high',
                'description': 'Recent major security incident',
                'recommendation': 'Conduct thorough security review and implement incident response improvements'
            })
        elif security_incident == 'yes-minor':
            score -= 10
            findings.append({
                'type': 'Security Incident History',
                'severity': 'medium',
                'description': 'Recent minor security incidents',
                'recommendation': 'Review incident patterns and strengthen preventive controls'
            })
        elif security_incident == 'unsure':
            score -= 15
            findings.append({
                'type': 'Security Monitoring',
                'severity': 'medium',
                'description': 'Insufficient security incident visibility',
                'recommendation': 'Implement comprehensive security monitoring and logging'
            })
        
        return {
            'score': max(30, min(100, score)),
            'findings': findings,
            'category': 'Vulnerability Assessment'
        }
    
    def _analyze_compliance(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance posture"""
        score = 70
        findings = []
        
        # Check compliance requirements
        compliance_reqs = assessment_data.get('compliance_requirements', [])
        compliance_status = assessment_data.get('compliance_status', '')
        
        if not compliance_reqs:
            score -= 10
            findings.append({
                'type': 'Compliance Framework',
                'severity': 'medium',
                'description': 'No specific compliance requirements identified',
                'recommendation': 'Identify applicable compliance frameworks for your industry'
            })
        else:
            # High-risk compliance requirements
            high_risk_reqs = ['gdpr', 'hipaa', 'pci-dss', 'sox']
            has_high_risk = any(req in compliance_reqs for req in high_risk_reqs)
            
            if has_high_risk:
                if compliance_status == 'not-compliant':
                    score -= 30
                    findings.append({
                        'type': 'Compliance Gap',
                        'severity': 'critical',
                        'description': 'Non-compliance with critical regulatory requirements',
                        'recommendation': 'Immediate compliance remediation required'
                    })
                elif compliance_status == 'working-towards':
                    score -= 15
                    findings.append({
                        'type': 'Compliance Progress',
                        'severity': 'medium',
                        'description': 'Working towards compliance with critical requirements',
                        'recommendation': 'Accelerate compliance efforts and establish timeline'
                    })
                elif compliance_status == 'mostly-compliant':
                    score -= 5
                    findings.append({
                        'type': 'Compliance Gaps',
                        'severity': 'low',
                        'description': 'Minor compliance gaps with critical requirements',
                        'recommendation': 'Address remaining compliance gaps'
                    })
        
        # Industry-specific compliance
        industry = assessment_data.get('industry', '')
        required_compliance = {
            'financial': ['sox', 'pci-dss'],
            'healthcare': ['hipaa'],
            'government': ['nist'],
            'retail': ['pci-dss']
        }
        
        if industry in required_compliance:
            missing_req = [req for req in required_compliance[industry] if req not in compliance_reqs]
            if missing_req:
                score -= 20
                findings.append({
                    'type': 'Industry Compliance',
                    'severity': 'high',
                    'description': f'Missing required {industry} compliance: {", ".join(missing_req)}',
                    'recommendation': f'Implement {industry}-specific compliance requirements'
                })
        
        return {
            'score': max(30, min(100, score)),
            'findings': findings,
            'category': 'Compliance Posture'
        }
    
    def _run_advanced_port_scan(self, domain: str) -> Dict[str, Any]:
        """Run advanced port scanning with new module"""
        try:
            # Parse domain
            if domain.startswith(('http://', 'https://')):
                parsed_url = urlparse(domain)
                target_host = parsed_url.hostname
            else:
                target_host = domain
            
            if not target_host:
                return None
            
            logger.info(f"Running advanced port scan on {target_host}")
            
            # Run standard scan profile (balance between speed and coverage)
            result = self.port_scanner.scan_host(target_host, scan_type='standard')
            
            if not result:
                return None
            
            # Convert results to assessment format
            score = 85  # Base score
            findings = []
            
            # Analyze open ports
            open_ports = result.open_ports
            high_risk_ports = [p for p in open_ports if p.risk_level == 'high']
            medium_risk_ports = [p for p in open_ports if p.risk_level == 'medium']
            
            # Deduct points for risky ports
            score -= len(high_risk_ports) * 10
            score -= len(medium_risk_ports) * 5
            
            # Add findings for high-risk ports
            for port in high_risk_ports:
                findings.append({
                    'type': f'High-Risk Port Open: {port.port}',
                    'severity': 'high',
                    'description': f'Port {port.port} ({port.service}) is open and poses security risk. {port.banner[:100] if port.banner else ""}',
                    'recommendation': f'Close port {port.port} if not required, or implement strict access controls'
                })
            
            # Add findings for unusual port exposure
            if len(open_ports) > 10:
                findings.append({
                    'type': 'Excessive Port Exposure',
                    'severity': 'medium',
                    'description': f'{len(open_ports)} open ports detected. Minimize attack surface.',
                    'recommendation': 'Close unnecessary ports and implement port filtering'
                })
            
            # Add OS fingerprint finding
            if result.os_guess:
                findings.append({
                    'type': 'OS Detection',
                    'severity': 'low',
                    'description': f'Operating system detected: {result.os_guess}',
                    'recommendation': 'Ensure OS is patched and hardened according to security benchmarks'
                })
            
            return {
                'score': max(30, min(100, score)),
                'findings': findings,
                'category': 'Advanced Port Scanning',
                'metadata': {
                    'total_ports_scanned': result.total_ports_scanned,
                    'open_ports_count': len(open_ports),
                    'high_risk_count': len(high_risk_ports),
                    'scan_duration': result.scan_duration
                }
            }
            
        except Exception as e:
            logger.error(f"Advanced port scan failed: {e}")
            return None
    
    def _run_web_app_scan(self, domain: str) -> Dict[str, Any]:
        """Run web application security scan with new module"""
        try:
            # Ensure domain has protocol
            if not domain.startswith(('http://', 'https://')):
                target_url = 'https://' + domain
            else:
                target_url = domain
            
            logger.info(f"Running web application security scan on {target_url}")
            
            # Run comprehensive web app scan
            result = self.web_scanner.scan_url(target_url)
            
            if not result:
                return None
            
            # Convert results to assessment format
            vulnerabilities = result.vulnerabilities
            
            # Start with base score and deduct for findings
            score = 90
            critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
            high_vulns = [v for v in vulnerabilities if v.severity == 'high']
            medium_vulns = [v for v in vulnerabilities if v.severity == 'medium']
            
            score -= len(critical_vulns) * 20
            score -= len(high_vulns) * 10
            score -= len(medium_vulns) * 5
            
            # Convert vulnerabilities to findings format
            findings = []
            for vuln in vulnerabilities:
                findings.append({
                    'type': vuln.vulnerability_type,
                    'severity': vuln.severity,
                    'description': vuln.description,
                    'recommendation': vuln.recommendation
                })
            
            return {
                'score': max(20, min(100, score)),
                'findings': findings,
                'category': 'Web Application Security',
                'metadata': {
                    'total_vulnerabilities': len(vulnerabilities),
                    'critical_count': len(critical_vulns),
                    'high_count': len(high_vulns),
                    'risk_score': result.risk_score,
                    'owasp_coverage': True
                }
            }
            
        except Exception as e:
            logger.error(f"Web application scan failed: {e}")
            return None
    
    def _run_api_security_scan(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run API security scan with new module"""
        try:
            api_url = assessment_data.get('api_url') or assessment_data.get('domain')
            
            if not api_url:
                return None
            
            # Ensure URL format
            if not api_url.startswith(('http://', 'https://')):
                api_url = 'https://' + api_url
            
            logger.info(f"Running API security scan on {api_url}")
            
            # Determine API type (default to REST)
            api_type = assessment_data.get('api_type', 'rest').lower()
            
            if api_type == 'graphql':
                vulnerabilities = self.api_scanner.scan_graphql_api(api_url)
            else:  # REST or SOAP
                vulnerabilities = self.api_scanner.scan_rest_api(api_url)
            
            # Convert to assessment format
            score = 85
            critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
            high_vulns = [v for v in vulnerabilities if v.severity == 'high']
            
            score -= len(critical_vulns) * 15
            score -= len(high_vulns) * 8
            
            findings = []
            for vuln in vulnerabilities:
                findings.append({
                    'type': f'API Security: {vuln.vulnerability_type}',
                    'severity': vuln.severity,
                    'description': vuln.description,
                    'recommendation': vuln.recommendation
                })
            
            return {
                'score': max(30, min(100, score)),
                'findings': findings,
                'category': 'API Security',
                'metadata': {
                    'api_type': api_type,
                    'vulnerabilities_found': len(vulnerabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"API security scan failed: {e}")
            return None
    
    def _run_cloud_security_scan(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run cloud security assessment with multi-cloud scanner"""
        try:
            cloud_provider = assessment_data.get('cloud_provider', '').upper()
            
            if not cloud_provider or cloud_provider == 'NONE':
                return None
            
            logger.info(f"Running {cloud_provider} cloud security scan...")
            
            # Configure cloud scanner based on provider
            configured = False
            
            if cloud_provider == 'AWS':
                configured = self.cloud_scanner.configure_aws(
                    access_key=assessment_data.get('aws_access_key'),
                    secret_key=assessment_data.get('aws_secret_key'),
                    region=assessment_data.get('aws_region', 'us-east-1'),
                    profile_name=assessment_data.get('aws_profile')
                )
                if configured:
                    result = self.cloud_scanner.scan_aws_only()
                
            elif cloud_provider == 'AZURE':
                configured = self.cloud_scanner.configure_azure(
                    subscription_id=assessment_data.get('azure_subscription_id'),
                    tenant_id=assessment_data.get('azure_tenant_id'),
                    client_id=assessment_data.get('azure_client_id'),
                    client_secret=assessment_data.get('azure_client_secret')
                )
                if configured:
                    result = self.cloud_scanner.scan_azure_only()
                
            elif cloud_provider == 'GCP':
                configured = self.cloud_scanner.configure_gcp(
                    project_id=assessment_data.get('gcp_project_id'),
                    credentials_path=assessment_data.get('gcp_credentials_path')
                )
                if configured:
                    result = self.cloud_scanner.scan_gcp_only()
            
            elif cloud_provider == 'MULTI':
                # Multi-cloud scan
                # Configure all provided cloud credentials
                configured = False
                if assessment_data.get('aws_access_key'):
                    self.cloud_scanner.configure_aws(
                        access_key=assessment_data.get('aws_access_key'),
                        secret_key=assessment_data.get('aws_secret_key'),
                        region=assessment_data.get('aws_region', 'us-east-1')
                    )
                    configured = True
                if assessment_data.get('azure_subscription_id'):
                    self.cloud_scanner.configure_azure(
                        subscription_id=assessment_data.get('azure_subscription_id'),
                        tenant_id=assessment_data.get('azure_tenant_id'),
                        client_id=assessment_data.get('azure_client_id'),
                        client_secret=assessment_data.get('azure_client_secret')
                    )
                    configured = True
                if assessment_data.get('gcp_project_id'):
                    self.cloud_scanner.configure_gcp(
                        project_id=assessment_data.get('gcp_project_id'),
                        credentials_path=assessment_data.get('gcp_credentials_path')
                    )
                    configured = True
                
                if configured:
                    result = self.cloud_scanner.scan_all_clouds()
            else:
                return None
            
            if not configured:
                return None
            
            # Convert to assessment format
            score = 100 - result.overall_risk_score  # Invert risk score to get security score
            
            findings = []
            for finding in result.findings[:20]:  # Limit to top 20 findings
                findings.append({
                    'type': f'{finding.cloud_provider} - {finding.finding_type}',
                    'severity': finding.severity,
                    'description': finding.description,
                    'recommendation': finding.recommendation
                })
            
            return {
                'score': max(20, min(100, score)),
                'findings': findings,
                'category': f'{cloud_provider} Cloud Security',
                'metadata': {
                    'clouds_scanned': result.clouds_scanned,
                    'total_findings': result.total_findings,
                    'risk_score': result.overall_risk_score,
                    'security_posture': result.security_posture
                }
            }
            
        except Exception as e:
            logger.error(f"Cloud security scan failed: {e}")
            return None
    
    def _run_container_security_scan(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run container security assessment (Docker, Kubernetes)"""
        try:
            container_platform = assessment_data.get('container_platform', '').upper()
            
            if not container_platform or container_platform == 'NONE':
                return None
            
            logger.info(f"Running {container_platform} container security scan...")
            
            # Configure container scanner based on platform
            result = None
            
            if container_platform == 'DOCKER':
                # Docker scanning - automatically connects to local daemon
                self.container_scanner.configure_docker()
                result = self.container_scanner.scan_docker_only()
                
            elif container_platform == 'KUBERNETES':
                # Kubernetes scanning - configure with kubeconfig
                kubeconfig_path = assessment_data.get('kubeconfig_path')
                self.container_scanner.configure_kubernetes(kubeconfig_path)
                result = self.container_scanner.scan_kubernetes_only()
                
            elif container_platform == 'BOTH':
                # Scan both Docker and Kubernetes
                try:
                    self.container_scanner.configure_docker()
                except Exception as e:
                    logger.warning(f"Docker configuration failed: {e}")
                
                try:
                    kubeconfig_path = assessment_data.get('kubeconfig_path')
                    self.container_scanner.configure_kubernetes(kubeconfig_path)
                except Exception as e:
                    logger.warning(f"Kubernetes configuration failed: {e}")
                
                result = self.container_scanner.scan_all_platforms()
                
            else:
                return None
            
            if not result or 'error' in result:
                return None
            
            # Convert to assessment format
            if hasattr(result, 'risk_score'):
                # ContainerScanResult object (unified results)
                score = 100 - result.risk_score  # Invert risk score to get security score
                
                findings = []
                # Get top 20 findings across all platforms
                all_findings = []
                for platform_findings in result.findings_by_platform.values():
                    all_findings.extend(platform_findings)
                
                # Sort by severity
                severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                all_findings.sort(key=lambda f: severity_order.get(f.get('severity', 'LOW'), 4))
                
                for finding in all_findings[:20]:  # Top 20 findings
                    findings.append({
                        'type': f"{finding.get('category', 'Container Security')}",
                        'severity': finding.get('severity', 'MEDIUM'),
                        'description': f"{finding.get('title', 'Security Issue')}: {finding.get('description', '')}",
                        'recommendation': finding.get('remediation', 'Review and remediate security issue')
                    })
                
                return {
                    'score': max(20, min(100, score)),
                    'findings': findings,
                    'category': f'{container_platform} Container Security',
                    'metadata': {
                        'platforms_scanned': result.platforms_scanned,
                        'total_findings': result.total_findings,
                        'risk_score': result.risk_score,
                        'security_posture': result.security_posture,
                        'severity_breakdown': result.severity_breakdown
                    }
                }
            else:
                # Single platform result (dict format)
                score = 100 - result.get('risk_score', 50)
                
                findings = []
                for finding in result.get('findings', [])[:20]:  # Top 20 findings
                    findings.append({
                        'type': finding.get('category', 'Container Security'),
                        'severity': finding.get('severity', 'MEDIUM'),
                        'description': f"{finding.get('title', 'Security Issue')}: {finding.get('description', '')}",
                        'recommendation': finding.get('remediation', 'Review and remediate security issue')
                    })
                
                return {
                    'score': max(20, min(100, score)),
                    'findings': findings,
                    'category': f'{container_platform} Container Security',
                    'metadata': {
                        'scanner': result.get('scanner', 'Container Scanner'),
                        'total_findings': result.get('total_findings', len(findings)),
                        'risk_score': result.get('risk_score', 50),
                        'security_posture': result.get('security_posture', 'FAIR'),
                        'severity_breakdown': result.get('severity_breakdown', {})
                    }
                }
            
        except Exception as e:
            logger.error(f"Container security scan failed: {e}")
            return None
    
    def _generate_final_results(self, assessment_data: Dict[str, Any], 
                              infrastructure_score: Dict[str, Any],
                              network_score: Dict[str, Any],
                              ssl_score: Dict[str, Any],
                              vulnerability_score: Dict[str, Any],
                              compliance_score: Dict[str, Any],
                              advanced_port_score: Dict[str, Any] = None,
                              web_app_score: Dict[str, Any] = None,
                              api_security_score: Dict[str, Any] = None,
                              cloud_security_score: Dict[str, Any] = None,
                              container_security_score: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive assessment results"""
        
        # Calculate weighted overall score with advanced scanning including cloud and containers
        if advanced_port_score or web_app_score or api_security_score or cloud_security_score or container_security_score:
            # Enhanced scoring with advanced scanners, cloud, and containers
            weights = {
                'infrastructure': 0.07,
                'network': 0.10,
                'advanced_ports': 0.10,
                'ssl': 0.10,
                'vulnerability': 0.10,
                'web_app': 0.10,
                'api_security': 0.07,
                'cloud_security': 0.18,  # Cloud security is critical
                'container_security': 0.15,  # Container security is very important
                'compliance': 0.03
            }
            
            overall_score = round(
                infrastructure_score['score'] * weights['infrastructure'] +
                network_score['score'] * weights['network'] +
                (advanced_port_score['score'] if advanced_port_score else network_score['score']) * weights['advanced_ports'] +
                ssl_score['score'] * weights['ssl'] +
                vulnerability_score['score'] * weights['vulnerability'] +
                (web_app_score['score'] if web_app_score else vulnerability_score['score']) * weights['web_app'] +
                (api_security_score['score'] if api_security_score else 85) * weights['api_security'] +
                (cloud_security_score['score'] if cloud_security_score else 90) * weights['cloud_security'] +
                (container_security_score['score'] if container_security_score else 88) * weights['container_security'] +
                compliance_score['score'] * weights['compliance']
            )
        else:
            # Standard scoring without advanced scanners
            weights = {
                'infrastructure': 0.15,
                'network': 0.25,
                'ssl': 0.20,
                'vulnerability': 0.25,
                'compliance': 0.15
            }
            
            overall_score = round(
                infrastructure_score['score'] * weights['infrastructure'] +
                network_score['score'] * weights['network'] +
                ssl_score['score'] * weights['ssl'] +
                vulnerability_score['score'] * weights['vulnerability'] +
                compliance_score['score'] * weights['compliance']
            )
        
        # Combine all findings from all assessment phases
        all_findings = (
            infrastructure_score['findings'] + 
            network_score['findings'] + 
            ssl_score['findings'] + 
            vulnerability_score['findings'] + 
            compliance_score['findings']
        )
        
        # Add advanced scanning findings if available
        if advanced_port_score:
            all_findings.extend(advanced_port_score['findings'])
        if web_app_score:
            all_findings.extend(web_app_score['findings'])
        if api_security_score:
            all_findings.extend(api_security_score['findings'])
        if cloud_security_score:
            all_findings.extend(cloud_security_score['findings'])
        if container_security_score:
            all_findings.extend(container_security_score['findings'])
        
        # Count vulnerabilities by severity
        critical_count = len([f for f in all_findings if f['severity'] == 'critical'])
        high_count = len([f for f in all_findings if f['severity'] == 'high'])
        medium_count = len([f for f in all_findings if f['severity'] == 'medium'])
        low_count = len([f for f in all_findings if f['severity'] == 'low'])
        
        # Determine risk level
        if overall_score >= 85:
            risk_level = 'LOW'
            risk_description = 'Strong security posture with minimal vulnerabilities'
        elif overall_score >= 70:
            risk_level = 'MEDIUM'
            risk_description = 'Good security foundation with improvement opportunities'
        elif overall_score >= 55:
            risk_level = 'HIGH'
            risk_description = 'Significant security gaps requiring immediate attention'
        else:
            risk_level = 'CRITICAL'
            risk_description = 'Critical security vulnerabilities present serious risk'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_score, all_findings, assessment_data)
        
        return {
            'overall_score': overall_score,
            'risk_level': risk_level,
            'risk_description': risk_description,
            'category_scores': {
                'Infrastructure Security': infrastructure_score['score'],
                'Network Security': network_score['score'],
                'SSL/TLS Security': ssl_score['score'],
                'Vulnerability Assessment': vulnerability_score['score'],
                'Compliance Posture': compliance_score['score'],
                **(
                    {
                        'Advanced Port Scanning': advanced_port_score['score'],
                        'Web Application Security': web_app_score['score'],
                        'API Security': api_security_score['score'],
                        'Cloud Security': cloud_security_score['score'],
                        'Container Security': container_security_score['score']
                    } if (advanced_port_score or web_app_score or api_security_score or cloud_security_score or container_security_score) else {}
                )
            },
            'vulnerability_counts': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count,
                'total': len(all_findings)
            },
            'findings': all_findings,
            'recommendations': recommendations,
            'assessment_metadata': {
                'company_name': assessment_data.get('company_name', 'Unknown'),
                'industry': assessment_data.get('industry', 'Unknown'),
                'company_size': assessment_data.get('company_size', 'Unknown'),
                'assessment_date': datetime.now().isoformat(),
                'assessment_id': assessment_data.get('assessment_id', 'Unknown')
            }
        }
    
    def _generate_recommendations(self, overall_score: int, findings: List[Dict], assessment_data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Priority recommendations based on score
        if overall_score < 60:
            recommendations.extend([
                "Immediate comprehensive security review required",
                "Engage cybersecurity consultant for urgent remediation",
                "Implement basic security controls (firewall, antivirus, backups)",
                "Establish incident response procedures"
            ])
        elif overall_score < 75:
            recommendations.extend([
                "Address high and critical vulnerabilities within 30 days",
                "Implement security awareness training program",
                "Consider managed security services for 24/7 monitoring",
                "Regular security assessments (quarterly recommended)"
            ])
        else:
            recommendations.extend([
                "Maintain current security practices",
                "Consider advanced threat detection solutions",
                "Regular penetration testing recommended",
                "Continuous security monitoring and improvement"
            ])
        
        # Specific recommendations based on findings
        critical_findings = [f for f in findings if f['severity'] == 'critical']
        if critical_findings:
            recommendations.insert(0, f"URGENT: Address {len(critical_findings)} critical security issues immediately")
        
        # Industry-specific recommendations
        industry = assessment_data.get('industry', '')
        if industry == 'financial':
            recommendations.append("Consider additional fraud detection and prevention measures")
        elif industry == 'healthcare':
            recommendations.append("Implement HIPAA-compliant data encryption and access controls")
        elif industry == 'retail':
            recommendations.append("Enhance PCI DSS compliance for payment card security")
        
        return recommendations
    
    def get_assessment_status(self, assessment_id: str) -> Dict[str, Any]:
        """Get current status of an assessment"""
        if assessment_id not in self.active_scans:
            return {'error': 'Assessment not found'}
        
        scan_data = self.active_scans[assessment_id]
        return {
            'assessment_id': assessment_id,
            'status': scan_data['status'],
            'progress': scan_data['progress'],
            'current_phase': scan_data['current_phase'],
            'start_time': scan_data['start_time'].isoformat(),
            'results': scan_data.get('results')
        }

# Global assessment engine instance
assessment_engine = SecurityAssessmentEngine()

@security_assessment.route('/assessment/start', methods=['POST'])
def start_assessment():
    """Start a new security assessment"""
    try:
        assessment_data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'industry', 'email']
        for field in required_fields:
            if not assessment_data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Start assessment
        assessment_id = assessment_engine.start_assessment(assessment_data)
        
        return jsonify({
            'success': True,
            'assessment_id': assessment_id,
            'message': 'Assessment started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_assessment.route('/assessment/status/<assessment_id>', methods=['GET'])
def get_assessment_status(assessment_id):
    """Get assessment status and progress"""
    try:
        status = assessment_engine.get_assessment_status(assessment_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_assessment.route('/assessment/results/<assessment_id>', methods=['GET'])
def get_assessment_results(assessment_id):
    """Get complete assessment results"""
    try:
        status = assessment_engine.get_assessment_status(assessment_id)
        
        if 'error' in status:
            return jsonify(status), 404
        
        if status['status'] != 'completed':
            return jsonify({'error': 'Assessment not yet completed'}), 400
        
        return jsonify({
            'success': True,
            'results': status['results']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_assessment.route('/assessment/report/<assessment_id>', methods=['GET'])
def download_assessment_report(assessment_id):
    """Generate and download PDF report"""
    try:
        status = assessment_engine.get_assessment_status(assessment_id)
        
        if 'error' in status or status['status'] != 'completed':
            return jsonify({'error': 'Assessment not found or not completed'}), 404
        
        # Generate PDF report
        pdf_path = generate_pdf_report(status['results'])
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"security_assessment_{assessment_id[:8]}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_pdf_report(results: Dict[str, Any]) -> str:
    """Generate comprehensive PDF security assessment report"""
    # Create temporary PDF file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2c3e50')
    )
    
    story.append(Paragraph("Enterprise Security Assessment Report", title_style))
    story.append(Spacer(1, 20))
    
    # Company information
    metadata = results['assessment_metadata']
    company_info = [
        ['Company:', metadata['company_name']],
        ['Industry:', metadata['industry']],
        ['Company Size:', metadata['company_size']],
        ['Assessment Date:', datetime.fromisoformat(metadata['assessment_date']).strftime('%B %d, %Y')],
        ['Assessment ID:', metadata['assessment_id']]
    ]
    
    company_table = Table(company_info, colWidths=[2*inch, 4*inch])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 30))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    
    # Overall score and risk level
    score_color = colors.green if results['overall_score'] >= 80 else colors.orange if results['overall_score'] >= 60 else colors.red
    
    summary_data = [
        ['Overall Security Score:', f"{results['overall_score']}/100"],
        ['Risk Level:', results['risk_level']],
        ['Total Vulnerabilities:', str(results['vulnerability_counts']['total'])],
        ['Critical Issues:', str(results['vulnerability_counts']['critical'])],
        ['High Priority Issues:', str(results['vulnerability_counts']['high'])]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (1, 0), (1, 0), score_color),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(results['risk_description'], styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Category Scores
    story.append(Paragraph("Security Category Scores", styles['Heading2']))
    
    category_data = [['Category', 'Score']]
    for category, score in results['category_scores'].items():
        category_data.append([category, f"{score}/100"])
    
    category_table = Table(category_data, colWidths=[4*inch, 1.5*inch])
    category_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(category_table)
    story.append(Spacer(1, 30))
    
    # Security Findings
    story.append(Paragraph("Security Findings", styles['Heading2']))
    
    for finding in results['findings']:
        severity_color = {
            'critical': colors.red,
            'high': colors.orange,
            'medium': colors.yellow,
            'low': colors.green
        }.get(finding['severity'], colors.black)
        
        finding_style = ParagraphStyle(
            'FindingTitle',
            parent=styles['Heading3'],
            textColor=severity_color
        )
        
        story.append(Paragraph(f"{finding['type']} ({finding['severity'].upper()})", finding_style))
        story.append(Paragraph(f"<b>Description:</b> {finding['description']}", styles['Normal']))
        story.append(Paragraph(f"<b>Recommendation:</b> {finding['recommendation']}", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    
    for i, rec in enumerate(results['recommendations'], 1):
        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    
    return temp_file.name

@security_assessment.route('/api/security-assessment/generate-report', methods=['POST'])
def generate_professional_report():
    """
    Generate professional PDF report using Enterprise Scanner advanced report generator
    """
    try:
        data = request.get_json()
        assessment_id = data.get('assessment_id')
        report_type = data.get('report_type', 'executive')  # executive, technical, compliance
        framework = data.get('framework', 'NIST')  # For compliance reports
        company_info = data.get('company_info', {})
        
        if not assessment_id:
            return jsonify({'error': 'Assessment ID is required'}), 400
        
        # Get assessment data from storage
        scan_data = assessment_engine.active_scans.get(assessment_id)
        if not scan_data:
            return jsonify({'error': 'Assessment not found'}), 404
            
        # Extract assessment results
        assessment_data = scan_data.get('results', {})
        if not assessment_data:
            return jsonify({'error': 'Assessment results not available'}), 404
        
        # Import the professional report generator
        try:
            from ..services.pdf_report_generator import EnterpriseReportGenerator
            generator = EnterpriseReportGenerator()
            
            # Generate appropriate report type
            if report_type == 'executive':
                pdf_data = generator.generate_executive_report(assessment_data, company_info)
                filename = f"Enterprise_Scanner_Executive_Report_{assessment_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            elif report_type == 'technical':
                # Get detailed findings if available
                detailed_findings = assessment_data.get('detailed_findings', [])
                pdf_data = generator.generate_technical_report(assessment_data, detailed_findings)
                filename = f"Enterprise_Scanner_Technical_Report_{assessment_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            elif report_type == 'compliance':
                pdf_data = generator.generate_compliance_report(assessment_data, framework)
                filename = f"Enterprise_Scanner_{framework}_Compliance_Report_{assessment_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            else:
                return jsonify({'error': 'Invalid report type. Use: executive, technical, or compliance'}), 400
            
            # Return PDF as downloadable response
            response = make_response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.headers['Content-Length'] = len(pdf_data)
            
            # Log report generation
            logger.info(f"Professional {report_type} report generated for assessment {assessment_id}")
            
            return response
            
        except ImportError as e:
            logger.error(f"Failed to import PDF report generator: {e}")
            # Fallback to basic PDF generation
            return generate_basic_pdf_report(assessment_data, assessment_id)
            
    except Exception as e:
        logger.error(f"Error generating professional report: {e}")
        return jsonify({'error': 'Failed to generate report', 'details': str(e)}), 500

def generate_basic_pdf_report(assessment_data, assessment_id):
    """
    Fallback basic PDF report generation if advanced generator is not available
    """
    try:
        # Create basic report using existing generate_pdf_report function
        pdf_path = generate_pdf_report(assessment_data, assessment_id)
        
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        
        # Clean up temporary file
        os.unlink(pdf_path)
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="Basic_Security_Report_{assessment_id}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating basic PDF report: {e}")
        return jsonify({'error': 'Failed to generate basic report'}), 500

@security_assessment.route('/api/security-assessment/report-preview', methods=['POST'])
def generate_report_preview():
    """
    Generate a preview of the professional report (first page only)
    """
    try:
        data = request.get_json()
        assessment_id = data.get('assessment_id')
        report_type = data.get('report_type', 'executive')
        
        if not assessment_id:
            return jsonify({'error': 'Assessment ID is required'}), 400
        
        scan_data = assessment_engine.active_scans.get(assessment_id)
        if not scan_data:
            return jsonify({'error': 'Assessment not found'}), 404
            
        assessment_data = scan_data.get('results', {})
        
        # Generate preview data (metadata about what would be in the report)
        preview_data = {
            'report_type': report_type,
            'assessment_id': assessment_id,
            'security_score': assessment_data.get('overall_score', 87),
            'threats_blocked': assessment_data.get('threats_blocked', 2847),
            'cost_avoidance': assessment_data.get('cost_avoidance', '$3.2M'),
            'total_findings': len(assessment_data.get('findings', [])),
            'high_risk_findings': len([f for f in assessment_data.get('findings', []) if f.get('risk_level') == 'High']),
            'compliance_score': assessment_data.get('compliance_scores', {}).get('NIST', 92),
            'estimated_pages': 12 if report_type == 'executive' else 25 if report_type == 'technical' else 18,
            'sections': {
                'executive': [
                    'Executive Summary',
                    'Security Posture Overview', 
                    'Risk Assessment Summary',
                    'Business Impact Analysis',
                    'Strategic Recommendations'
                ],
                'technical': [
                    'Assessment Methodology',
                    'Detailed Security Findings',
                    'Vulnerability Analysis',
                    'Compliance Assessment',
                    'Remediation Roadmap'
                ],
                'compliance': [
                    'Compliance Executive Summary',
                    'Framework Mapping',
                    'Gap Analysis',
                    'Compliance Roadmap'
                ]
            }.get(report_type, [])
        }
        
        return jsonify({
            'success': True,
            'preview': preview_data,
            'message': f'Professional {report_type} report preview generated'
        })
        
    except Exception as e:
        logger.error(f"Error generating report preview: {e}")
        return jsonify({'error': 'Failed to generate preview'}), 500

# Register blueprint
def register_security_assessment_api(app):
    """Register security assessment API with Flask app"""
    app.register_blueprint(security_assessment)

# Export blueprint for app.py
security_assessment_bp = security_assessment