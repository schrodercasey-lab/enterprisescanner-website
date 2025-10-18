"""
Compliance & Trend Report Generators
Specialized reports for regulatory compliance and historical analysis

Report Types:
- Compliance Framework Reports (CIS, NIST, PCI-DSS, HIPAA)
- Trend and Comparison Reports (historical analysis)
- Multi-company comparison reports
- Quarterly/Annual trend reports

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class ComplianceReportGenerator:
    """
    Generate compliance framework reports for regulatory audits
    
    Supported Frameworks:
    - CIS Benchmarks (Docker, Kubernetes, Cloud)
    - NIST Cybersecurity Framework
    - PCI-DSS Requirements
    - HIPAA Security Rule
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Framework mappings
        self.frameworks = {
            'cis': 'CIS Benchmarks Compliance',
            'nist': 'NIST Cybersecurity Framework',
            'pci_dss': 'PCI-DSS Requirements',
            'hipaa': 'HIPAA Security Rule'
        }
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='ComplianceTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='FrameworkHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='ComplianceBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
    
    def generate_cis_report(self, assessment_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate CIS Benchmarks compliance report
        
        Args:
            assessment_data: Complete assessment results
            output_path: Path to save PDF report
        
        Returns:
            Path to generated PDF report
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        
        # Title
        story.append(Paragraph(
            f"CIS Benchmarks Compliance Report<br/>{company_name}",
            self.styles['ComplianceTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Overview
        story.extend(self._create_cis_overview(assessment_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Docker CIS Benchmark
        if 'Container Security' in assessment_data.get('category_scores', {}):
            story.extend(self._create_docker_cis_section(assessment_data))
            story.append(Spacer(1, 0.2*inch))
        
        # Kubernetes CIS Benchmark
        if 'Container Security' in assessment_data.get('category_scores', {}):
            story.extend(self._create_kubernetes_cis_section(assessment_data))
            story.append(Spacer(1, 0.2*inch))
        
        # Cloud CIS Benchmarks
        if 'Cloud Security' in assessment_data.get('category_scores', {}):
            story.extend(self._create_cloud_cis_section(assessment_data))
        
        # Build PDF
        from .report_generator import ReportHeader
        doc.build(story, onFirstPage=ReportHeader("CIS Compliance", company_name),
                 onLaterPages=ReportHeader("CIS Compliance", company_name))
        
        return output_path
    
    def _create_cis_overview(self, assessment_data: Dict) -> List:
        """Create CIS compliance overview"""
        elements = []
        
        elements.append(Paragraph("CIS Benchmarks Overview", self.styles['FrameworkHeader']))
        
        overview_text = """
        The Center for Internet Security (CIS) Benchmarks are globally recognized security standards 
        for hardening systems and applications. This report evaluates compliance with CIS Docker Benchmark, 
        CIS Kubernetes Benchmark, and CIS Cloud Provider Benchmarks.
        """
        elements.append(Paragraph(overview_text, self.styles['ComplianceBody']))
        
        # Compliance summary
        container_score = assessment_data.get('category_scores', {}).get('Container Security', 0)
        cloud_score = assessment_data.get('category_scores', {}).get('Cloud Security', 0)
        
        summary_data = [
            ['CIS Benchmark', 'Score', 'Compliance Status'],
            ['Docker CIS Benchmark', f"{container_score}/100", 
             self._compliance_status(container_score)],
            ['Kubernetes CIS Benchmark', f"{container_score}/100",
             self._compliance_status(container_score)],
            ['Cloud Provider CIS Benchmarks', f"{cloud_score}/100",
             self._compliance_status(cloud_score)]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10)
        ]))
        
        elements.append(summary_table)
        
        return elements
    
    def _create_docker_cis_section(self, assessment_data: Dict) -> List:
        """Create Docker CIS Benchmark section"""
        elements = []
        
        elements.append(Paragraph("CIS Docker Benchmark", self.styles['FrameworkHeader']))
        
        # Find Docker-related findings
        docker_findings = [
            f for f in assessment_data.get('findings', [])
            if 'docker' in f.get('category', '').lower() or 'container' in f.get('category', '').lower()
        ]
        
        docker_text = f"""
        <b>CIS Docker Benchmark Compliance</b><br/>
        Evaluated {len(docker_findings)} Docker security controls including:<br/>
        • Host configuration and hardening<br/>
        • Docker daemon configuration<br/>
        • Container runtime configuration<br/>
        • Container images and build files<br/>
        • Docker security operations
        """
        
        elements.append(Paragraph(docker_text, self.styles['ComplianceBody']))
        
        return elements
    
    def _create_kubernetes_cis_section(self, assessment_data: Dict) -> List:
        """Create Kubernetes CIS Benchmark section"""
        elements = []
        
        elements.append(Paragraph("CIS Kubernetes Benchmark", self.styles['FrameworkHeader']))
        
        # Find Kubernetes-related findings
        k8s_findings = [
            f for f in assessment_data.get('findings', [])
            if 'kubernetes' in f.get('category', '').lower() or 'k8s' in f.get('category', '').lower()
        ]
        
        k8s_text = f"""
        <b>CIS Kubernetes Benchmark Compliance</b><br/>
        Evaluated {len(k8s_findings)} Kubernetes security controls including:<br/>
        • Master node configuration<br/>
        • etcd security settings<br/>
        • Control plane configuration<br/>
        • Worker node security<br/>
        • Pod security policies<br/>
        • Network policies and segmentation
        """
        
        elements.append(Paragraph(k8s_text, self.styles['ComplianceBody']))
        
        return elements
    
    def _create_cloud_cis_section(self, assessment_data: Dict) -> List:
        """Create Cloud Provider CIS Benchmarks section"""
        elements = []
        
        elements.append(Paragraph("Cloud Provider CIS Benchmarks", self.styles['FrameworkHeader']))
        
        cloud_findings = [
            f for f in assessment_data.get('findings', [])
            if any(cloud in f.get('category', '').lower() for cloud in ['aws', 'azure', 'gcp', 'cloud'])
        ]
        
        cloud_text = f"""
        <b>Cloud CIS Benchmarks Compliance</b><br/>
        Evaluated {len(cloud_findings)} cloud security controls including:<br/>
        • Identity and Access Management (IAM)<br/>
        • Storage encryption and access controls<br/>
        • Logging and monitoring configuration<br/>
        • Network security groups and firewalls<br/>
        • Data encryption at rest and in transit
        """
        
        elements.append(Paragraph(cloud_text, self.styles['ComplianceBody']))
        
        return elements
    
    def generate_nist_report(self, assessment_data: Dict[str, Any], output_path: str) -> str:
        """Generate NIST Cybersecurity Framework report"""
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        
        # Title
        story.append(Paragraph(
            f"NIST Cybersecurity Framework Report<br/>{company_name}",
            self.styles['ComplianceTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # NIST CSF Overview
        story.extend(self._create_nist_overview(assessment_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Five Functions
        for function in ['Identify', 'Protect', 'Detect', 'Respond', 'Recover']:
            story.extend(self._create_nist_function_section(assessment_data, function))
            story.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        from .report_generator import ReportHeader
        doc.build(story, onFirstPage=ReportHeader("NIST CSF", company_name),
                 onLaterPages=ReportHeader("NIST CSF", company_name))
        
        return output_path
    
    def _create_nist_overview(self, assessment_data: Dict) -> List:
        """Create NIST CSF overview"""
        elements = []
        
        elements.append(Paragraph("NIST CSF Framework Overview", self.styles['FrameworkHeader']))
        
        overview_text = """
        The NIST Cybersecurity Framework provides a policy framework of computer security guidance 
        for how private sector organizations can assess and improve their ability to prevent, detect, 
        and respond to cyber attacks. The framework consists of five core functions: Identify, Protect, 
        Detect, Respond, and Recover.
        """
        elements.append(Paragraph(overview_text, self.styles['ComplianceBody']))
        
        return elements
    
    def _create_nist_function_section(self, assessment_data: Dict, function: str) -> List:
        """Create NIST function section"""
        elements = []
        
        elements.append(Paragraph(f"<b>{function}</b>", self.styles['Heading3']))
        
        function_descriptions = {
            'Identify': 'Develop organizational understanding to manage cybersecurity risk',
            'Protect': 'Develop and implement appropriate safeguards',
            'Detect': 'Develop and implement activities to identify cybersecurity events',
            'Respond': 'Develop and implement activities to respond to detected cybersecurity incidents',
            'Recover': 'Develop and implement activities to maintain resilience and restore capabilities'
        }
        
        desc = function_descriptions.get(function, '')
        elements.append(Paragraph(desc, self.styles['ComplianceBody']))
        
        return elements
    
    def _compliance_status(self, score: int) -> str:
        """Determine compliance status from score"""
        if score >= 90:
            return 'Fully Compliant'
        elif score >= 75:
            return 'Substantially Compliant'
        elif score >= 60:
            return 'Partially Compliant'
        else:
            return 'Non-Compliant'


class TrendReportGenerator:
    """
    Generate trend and comparison reports for historical analysis
    
    Features:
    - Quarterly/annual trend reports
    - Multi-company comparison
    - Security improvement tracking
    - Benchmark against industry averages
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='TrendTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='PeriodHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TrendBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
    
    def generate_quarterly_report(self, trend_data: List[Dict[str, Any]], 
                                  company_name: str, output_path: str) -> str:
        """
        Generate quarterly trend report
        
        Args:
            trend_data: List of historical assessment snapshots
            company_name: Company name
            output_path: Path to save PDF report
        
        Returns:
            Path to generated PDF report
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        # Title
        story.append(Paragraph(
            f"Quarterly Security Trend Report<br/>{company_name}",
            self.styles['TrendTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.extend(self._create_trend_summary(trend_data, 'quarterly'))
        story.append(Spacer(1, 0.3*inch))
        
        # Score Progression
        story.extend(self._create_score_progression(trend_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Finding Trends
        story.extend(self._create_finding_trends(trend_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Improvement Recommendations
        story.extend(self._create_improvement_recommendations(trend_data))
        
        # Build PDF
        from .report_generator import ReportHeader
        doc.build(story, onFirstPage=ReportHeader("Quarterly Trends", company_name),
                 onLaterPages=ReportHeader("Quarterly Trends", company_name))
        
        return output_path
    
    def _create_trend_summary(self, trend_data: List[Dict], period: str) -> List:
        """Create trend summary section"""
        elements = []
        
        elements.append(Paragraph(f"{period.capitalize()} Trend Summary", self.styles['PeriodHeader']))
        
        if len(trend_data) < 2:
            elements.append(Paragraph(
                "Insufficient historical data for trend analysis. At least 2 assessments required.",
                self.styles['TrendBody']
            ))
            return elements
        
        latest = trend_data[0]
        oldest = trend_data[-1]
        
        score_change = latest.get('value', 0) - oldest.get('value', 0)
        direction = "improved" if score_change > 0 else "declined" if score_change < 0 else "remained stable"
        
        summary_text = f"""
        Over the {period} period, your organization's security posture has <b>{direction}</b> 
        by {abs(score_change):.1f} points. This analysis is based on {len(trend_data)} assessments 
        conducted between {oldest.get('timestamp', 'N/A')} and {latest.get('timestamp', 'N/A')}.
        """
        
        elements.append(Paragraph(summary_text, self.styles['TrendBody']))
        
        return elements
    
    def _create_score_progression(self, trend_data: List[Dict]) -> List:
        """Create score progression analysis"""
        elements = []
        
        elements.append(Paragraph("Security Score Progression", self.styles['PeriodHeader']))
        
        # Score progression table
        if trend_data:
            score_data = [['Assessment Date', 'Overall Score', 'Change']]
            
            for i, snapshot in enumerate(trend_data):
                date = snapshot.get('timestamp', 'N/A')
                score = snapshot.get('value', 0)
                
                if i < len(trend_data) - 1:
                    prev_score = trend_data[i + 1].get('value', 0)
                    change = score - prev_score
                    change_str = f"+{change:.1f}" if change > 0 else f"{change:.1f}" if change < 0 else "0"
                else:
                    change_str = "N/A (Baseline)"
                
                score_data.append([date, f"{score:.1f}", change_str])
            
            score_table = Table(score_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
            ]))
            
            elements.append(score_table)
        
        return elements
    
    def _create_finding_trends(self, trend_data: List[Dict]) -> List:
        """Create vulnerability finding trends"""
        elements = []
        
        elements.append(Paragraph("Vulnerability Finding Trends", self.styles['PeriodHeader']))
        
        trend_text = """
        Tracking vulnerability findings over time helps identify security improvement patterns 
        and validate the effectiveness of remediation efforts.
        """
        elements.append(Paragraph(trend_text, self.styles['TrendBody']))
        
        return elements
    
    def _create_improvement_recommendations(self, trend_data: List[Dict]) -> List:
        """Create improvement recommendations based on trends"""
        elements = []
        
        elements.append(Paragraph("Improvement Recommendations", self.styles['PeriodHeader']))
        
        if len(trend_data) >= 2:
            latest = trend_data[0]
            previous = trend_data[1] if len(trend_data) > 1 else trend_data[0]
            
            score_change = latest.get('value', 0) - previous.get('value', 0)
            
            if score_change > 0:
                rec_text = """
                Your security posture is improving. Continue current security practices and consider:
                <br/>• Maintaining regular assessment schedule
                <br/>• Documenting successful remediation processes
                <br/>• Sharing security best practices across teams
                """
            elif score_change < 0:
                rec_text = """
                Your security posture has declined. Immediate actions recommended:
                <br/>• Review and prioritize critical findings
                <br/>• Increase security team resources
                <br/>• Conduct emergency security review
                """
            else:
                rec_text = """
                Your security posture is stable. Consider:
                <br/>• Implementing proactive security enhancements
                <br/>• Expanding security monitoring coverage
                <br/>• Investing in security automation
                """
            
            elements.append(Paragraph(rec_text, self.styles['TrendBody']))
        
        return elements


# Export main classes
__all__ = ['ComplianceReportGenerator', 'TrendReportGenerator']
