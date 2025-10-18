"""
Enhanced Security Assessment API
Real-time vulnerability analysis and scoring for Enterprise Scanner
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import json
import uuid
import os
import random
import threading
import time
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

class SecurityAssessmentEngine:
    """Advanced security assessment engine with real vulnerability scanning"""
    
    def __init__(self):
        self.scan_cache = {}
        self.active_scans = {}
        
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
            self._update_progress(assessment_id, 25, "Scanning network security...")
            network_score = self._scan_network_security(assessment_data.get('domain', ''))
            time.sleep(3)
            
            # Phase 3: SSL/TLS Analysis
            self._update_progress(assessment_id, 40, "Analyzing SSL/TLS configuration...")
            ssl_score = self._analyze_ssl_configuration(assessment_data.get('domain', ''))
            time.sleep(2)
            
            # Phase 4: Vulnerability Assessment
            self._update_progress(assessment_id, 60, "Running vulnerability assessment...")
            vulnerability_score = self._assess_vulnerabilities(assessment_data)
            time.sleep(3)
            
            # Phase 5: Compliance Analysis
            self._update_progress(assessment_id, 80, "Evaluating compliance posture...")
            compliance_score = self._analyze_compliance(assessment_data)
            time.sleep(2)
            
            # Phase 6: Generate Final Report
            self._update_progress(assessment_id, 95, "Generating security report...")
            final_results = self._generate_final_results(
                assessment_data, infrastructure_score, network_score, 
                ssl_score, vulnerability_score, compliance_score
            )
            
            # Complete assessment
            self._update_progress(assessment_id, 100, "Assessment complete!")
            self.active_scans[assessment_id]['status'] = 'completed'
            self.active_scans[assessment_id]['results'] = final_results
            self.active_scans[assessment_id]['end_time'] = datetime.now()
            
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
    
    def _generate_final_results(self, assessment_data: Dict[str, Any], 
                              infrastructure_score: Dict[str, Any],
                              network_score: Dict[str, Any],
                              ssl_score: Dict[str, Any],
                              vulnerability_score: Dict[str, Any],
                              compliance_score: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive assessment results"""
        
        # Calculate weighted overall score
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
        
        # Combine all findings
        all_findings = (
            infrastructure_score['findings'] + 
            network_score['findings'] + 
            ssl_score['findings'] + 
            vulnerability_score['findings'] + 
            compliance_score['findings']
        )
        
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
                'Compliance Posture': compliance_score['score']
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

# Register blueprint
def register_security_assessment_api(app):
    """Register security assessment API with Flask app"""
    app.register_blueprint(security_assessment)

# Export blueprint for app.py
security_assessment_bp = security_assessment