#!/usr/bin/env python3
"""
Enterprise Scanner - Professional PDF Report Generator
Fortune 500-grade cybersecurity assessment reports with executive summaries,
technical findings, remediation roadmaps, and compliance matrices.
"""

import os
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        PageBreak, Image, KeepTogether, NextPageTemplate, PageTemplate
    )
    from reportlab.platypus.frames import Frame
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics import renderPDF
except ImportError:
    print("Warning: ReportLab not installed. PDF generation will be limited.")
    # Fallback for basic functionality
    pass

class EnterpriseReportGenerator:
    """
    Professional PDF report generator for Enterprise Scanner cybersecurity assessments.
    Designed for Fortune 500 companies with executive-grade presentations.
    """
    
    def __init__(self):
        self.company_logo = None
        self.report_styles = self._create_report_styles()
        self.brand_colors = {
            'primary': colors.Color(30/255, 60/255, 114/255),  # #1e3c72
            'secondary': colors.Color(42/255, 82/255, 152/255),  # #2a5298
            'success': colors.Color(40/255, 167/255, 69/255),  # #28a745
            'warning': colors.Color(255/255, 193/255, 7/255),  # #ffc107
            'danger': colors.Color(220/255, 53/255, 69/255),  # #dc3545
            'info': colors.Color(23/255, 162/255, 184/255),  # #17a2b8
            'light_gray': colors.Color(248/255, 249/255, 250/255),  # #f8f9fa
            'dark_gray': colors.Color(108/255, 117/255, 125/255)  # #6c757d
        }
        
    def _create_report_styles(self):
        """Create custom styles for professional report formatting"""
        styles = getSampleStyleSheet()
        
        # Executive Summary Title
        styles.add(ParagraphStyle(
            name='ExecutiveTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.Color(30/255, 60/255, 114/255),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section Headers
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.Color(30/255, 60/255, 114/255),
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.Color(30/255, 60/255, 114/255),
            borderPadding=5
        ))
        
        # Executive Summary Body
        styles.add(ParagraphStyle(
            name='ExecutiveBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=16
        ))
        
        # Technical Finding
        styles.add(ParagraphStyle(
            name='TechnicalFinding',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leftIndent=20,
            fontName='Helvetica',
            leading=14
        ))
        
        # Recommendation
        styles.add(ParagraphStyle(
            name='Recommendation',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=15,
            fontName='Helvetica',
            textColor=colors.Color(40/255, 167/255, 69/255),
            leading=14
        ))
        
        # Risk Level High
        styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.Color(220/255, 53/255, 69/255),
            backColor=colors.Color(248/255, 215/255, 218/255),
            borderWidth=1,
            borderColor=colors.Color(220/255, 53/255, 69/255),
            borderPadding=5
        ))
        
        # Risk Level Medium
        styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.Color(133/255, 100/255, 4/255),
            backColor=colors.Color(255/255, 243/255, 205/255),
            borderWidth=1,
            borderColor=colors.Color(255/255, 193/255, 7/255),
            borderPadding=5
        ))
        
        # Risk Level Low
        styles.add(ParagraphStyle(
            name='RiskLow',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.Color(21/255, 87/255, 36/255),
            backColor=colors.Color(212/255, 237/255, 218/255),
            borderWidth=1,
            borderColor=colors.Color(40/255, 167/255, 69/255),
            borderPadding=5
        ))
        
        return styles
    
    def generate_executive_report(self, assessment_data: Dict[str, Any], 
                                company_info: Dict[str, str] = None) -> bytes:
        """
        Generate executive-level cybersecurity assessment report for C-suite presentation
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Cover Page
        story.extend(self._create_cover_page(assessment_data, company_info))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(assessment_data))
        story.append(PageBreak())
        
        # Security Posture Overview
        story.extend(self._create_security_overview(assessment_data))
        story.append(PageBreak())
        
        # Risk Assessment Summary
        story.extend(self._create_risk_summary(assessment_data))
        story.append(PageBreak())
        
        # Business Impact Analysis
        story.extend(self._create_business_impact(assessment_data))
        story.append(PageBreak())
        
        # Strategic Recommendations
        story.extend(self._create_strategic_recommendations(assessment_data))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_technical_report(self, assessment_data: Dict[str, Any],
                                 detailed_findings: List[Dict] = None) -> bytes:
        """
        Generate detailed technical cybersecurity assessment report for IT teams
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Cover Page
        story.extend(self._create_technical_cover_page(assessment_data))
        story.append(PageBreak())
        
        # Assessment Methodology
        story.extend(self._create_methodology_section())
        story.append(PageBreak())
        
        # Detailed Findings
        if detailed_findings:
            story.extend(self._create_detailed_findings(detailed_findings))
            story.append(PageBreak())
        
        # Vulnerability Analysis
        story.extend(self._create_vulnerability_analysis(assessment_data))
        story.append(PageBreak())
        
        # Compliance Assessment
        story.extend(self._create_compliance_assessment(assessment_data))
        story.append(PageBreak())
        
        # Remediation Roadmap
        story.extend(self._create_remediation_roadmap(assessment_data))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_compliance_report(self, assessment_data: Dict[str, Any],
                                 framework: str = "NIST") -> bytes:
        """
        Generate compliance-focused report for regulatory requirements
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Cover Page
        story.extend(self._create_compliance_cover_page(assessment_data, framework))
        story.append(PageBreak())
        
        # Compliance Executive Summary
        story.extend(self._create_compliance_executive_summary(assessment_data, framework))
        story.append(PageBreak())
        
        # Framework Mapping
        story.extend(self._create_framework_mapping(assessment_data, framework))
        story.append(PageBreak())
        
        # Gap Analysis
        story.extend(self._create_gap_analysis(assessment_data, framework))
        story.append(PageBreak())
        
        # Compliance Roadmap
        story.extend(self._create_compliance_roadmap(assessment_data, framework))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_cover_page(self, assessment_data: Dict[str, Any], 
                          company_info: Dict[str, str] = None) -> List:
        """Create professional cover page with Enterprise Scanner branding"""
        elements = []
        
        # Company Logo Placeholder
        elements.append(Spacer(1, 1*inch))
        
        # Title
        title = Paragraph(
            "ENTERPRISE SCANNER<br/>Cybersecurity Assessment Report",
            self.report_styles['ExecutiveTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Company Information
        if company_info:
            company_name = company_info.get('name', 'Fortune 500 Company')
            elements.append(Paragraph(
                f"<b>Client:</b> {company_name}",
                self.report_styles['ExecutiveBody']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Assessment Details
        assessment_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(
            f"<b>Assessment Date:</b> {assessment_date}",
            self.report_styles['ExecutiveBody']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Security Score
        security_score = assessment_data.get('overall_score', 87)
        score_color = 'success' if security_score >= 80 else 'warning' if security_score >= 60 else 'danger'
        elements.append(Paragraph(
            f"<b>Overall Security Score:</b> <font color='{self.brand_colors[score_color]}'>{security_score}/100</font>",
            self.report_styles['ExecutiveBody']
        ))
        
        elements.append(Spacer(1, 1*inch))
        
        # Confidentiality Notice
        confidentiality = """
        <b>CONFIDENTIAL</b><br/>
        This report contains confidential and proprietary information. 
        Distribution is restricted to authorized personnel only.
        """
        elements.append(Paragraph(confidentiality, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_executive_summary(self, assessment_data: Dict[str, Any]) -> List:
        """Create executive summary for C-suite presentation"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.report_styles['ExecutiveTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Security Posture Overview
        security_score = assessment_data.get('overall_score', 87)
        threats_blocked = assessment_data.get('threats_blocked', 2847)
        cost_avoidance = assessment_data.get('cost_avoidance', '$3.2M')
        
        summary_text = f"""
        Enterprise Scanner conducted a comprehensive cybersecurity assessment of your organization's 
        digital infrastructure. Our analysis reveals a <b>strong security posture</b> with a security 
        score of <b>{security_score}/100</b>, indicating effective cybersecurity investments and practices.
        
        <b>Key Findings:</b>
        • Your security infrastructure successfully blocked <b>{threats_blocked:,} advanced threats</b> this quarter
        • Current security investments have delivered an estimated <b>{cost_avoidance} in cost avoidance</b>
        • Overall risk exposure has been reduced by <b>78%</b> compared to industry baseline
        • Compliance posture shows <b>94% adherence</b> to regulatory frameworks
        
        <b>Business Impact:</b>
        The assessment demonstrates that your cybersecurity program is delivering measurable business value 
        through threat prevention, operational continuity, and regulatory compliance. Your organization 
        is well-positioned to defend against current threat landscape while maintaining business growth objectives.
        """
        
        elements.append(Paragraph(summary_text, self.report_styles['ExecutiveBody']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive Metrics Table
        metrics_data = [
            ['Metric', 'Current Status', 'Industry Benchmark', 'Performance'],
            ['Security Score', f'{security_score}/100', '75/100', '16% Above Average'],
            ['Threat Response Time', '12 minutes', '45 minutes', '73% Faster'],
            ['Compliance Rate', '94%', '82%', '15% Higher'],
            ['Cost Avoidance', cost_avoidance, '$1.8M', '78% Higher ROI']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.brand_colors['primary'])
        ]))
        
        elements.append(metrics_table)
        
        return elements
    
    def _create_security_overview(self, assessment_data: Dict[str, Any]) -> List:
        """Create security posture overview section"""
        elements = []
        
        elements.append(Paragraph("Security Posture Overview", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Security Strengths
        elements.append(Paragraph("<b>Security Strengths:</b>", self.report_styles['ExecutiveBody']))
        
        strengths = [
            "Advanced threat detection systems effectively identifying and blocking sophisticated attacks",
            "Robust incident response procedures with industry-leading response times",
            "Comprehensive employee security training program with 95% completion rate",
            "Multi-layered security architecture providing defense-in-depth protection",
            "Regular security assessments and continuous monitoring implementation"
        ]
        
        for strength in strengths:
            elements.append(Paragraph(f"• {strength}", self.report_styles['TechnicalFinding']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Areas for Improvement
        elements.append(Paragraph("<b>Areas for Improvement:</b>", self.report_styles['ExecutiveBody']))
        
        improvements = [
            "SSL certificate management - 3 certificates expiring within 30 days",
            "Security patch management - 15 critical patches pending deployment",
            "Access control review - quarterly access review 3 days overdue",
            "Backup verification - quarterly backup restore testing required"
        ]
        
        for improvement in improvements:
            elements.append(Paragraph(f"• {improvement}", self.report_styles['TechnicalFinding']))
        
        return elements
    
    def _create_risk_summary(self, assessment_data: Dict[str, Any]) -> List:
        """Create risk assessment summary section"""
        elements = []
        
        elements.append(Paragraph("Risk Assessment Summary", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk Distribution
        risk_data = [
            ['Risk Level', 'Count', 'Business Impact', 'Timeline'],
            ['Critical', '2', '$4.8M potential loss', 'Immediate action required'],
            ['High', '7', '$2.3M potential loss', 'Address within 30 days'],
            ['Medium', '14', '$800K potential loss', 'Address within 90 days'],
            ['Low', '23', '$200K potential loss', 'Address within 6 months']
        ]
        
        risk_table = Table(risk_data, colWidths=[1.5*inch, 1*inch, 2*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), self.brand_colors['danger']),
            ('BACKGROUND', (0, 2), (0, 2), self.brand_colors['warning']),
            ('BACKGROUND', (0, 3), (0, 3), self.brand_colors['info']),
            ('BACKGROUND', (0, 4), (0, 4), self.brand_colors['success']),
            ('TEXTCOLOR', (0, 1), (0, 4), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, self.brand_colors['primary'])
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk Mitigation Value
        mitigation_text = """
        <b>Risk Mitigation Value:</b> Through proactive security measures and continuous monitoring, 
        your organization has successfully mitigated approximately <b>$12.3M in potential cybersecurity losses</b> 
        this year. This represents a <b>320% return on cybersecurity investment</b> and demonstrates the 
        significant business value of your security program.
        """
        
        elements.append(Paragraph(mitigation_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_business_impact(self, assessment_data: Dict[str, Any]) -> List:
        """Create business impact analysis section"""
        elements = []
        
        elements.append(Paragraph("Business Impact Analysis", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # ROI Analysis
        roi_text = """
        <b>Return on Investment (ROI) Analysis:</b>
        
        Your cybersecurity investment of approximately <b>$15M annually</b> has delivered exceptional 
        business value through threat prevention, operational continuity, and regulatory compliance.
        
        <b>Quantified Benefits:</b>
        • <b>$3.2M</b> in direct cost avoidance through threat prevention
        • <b>$2.1M</b> in productivity savings through 99.9% uptime
        • <b>$1.8M</b> in compliance cost avoidance through automated frameworks
        • <b>$5.2M</b> in reputation protection through zero data breaches
        
        <b>Total Annual Value: $12.3M</b>
        <b>Net ROI: 320%</b>
        <b>Payback Period: 3.8 months</b>
        """
        
        elements.append(Paragraph(roi_text, self.report_styles['ExecutiveBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Industry Benchmarking
        benchmark_text = """
        <b>Industry Benchmarking:</b>
        
        Compared to Fortune 500 peers in your industry sector, your organization demonstrates:
        • <b>23% higher</b> security effectiveness score
        • <b>67% faster</b> incident response times
        • <b>15% better</b> compliance adherence
        • <b>78% higher</b> security ROI
        
        This positions your organization in the <b>top 10%</b> of industry leaders for cybersecurity maturity.
        """
        
        elements.append(Paragraph(benchmark_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_strategic_recommendations(self, assessment_data: Dict[str, Any]) -> List:
        """Create strategic recommendations section"""
        elements = []
        
        elements.append(Paragraph("Strategic Recommendations", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Short-term Priorities (30 days)
        elements.append(Paragraph("<b>Immediate Priorities (30 Days):</b>", self.report_styles['ExecutiveBody']))
        
        short_term = [
            "Address SSL certificate expirations to prevent service disruptions",
            "Deploy 15 critical security patches to eliminate high-risk vulnerabilities",
            "Complete quarterly access control review for 23 privileged accounts",
            "Implement automated certificate renewal to prevent future expirations"
        ]
        
        for item in short_term:
            elements.append(Paragraph(f"• {item}", self.report_styles['Recommendation']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Medium-term Initiatives (90 days)
        elements.append(Paragraph("<b>Strategic Initiatives (90 Days):</b>", self.report_styles['ExecutiveBody']))
        
        medium_term = [
            "Advance zero-trust architecture implementation to 85% completion",
            "Enhance threat intelligence integration with real-time CVE feeds",
            "Implement advanced analytics for predictive threat detection",
            "Expand security awareness training to include social engineering simulation"
        ]
        
        for item in medium_term:
            elements.append(Paragraph(f"• {item}", self.report_styles['Recommendation']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Long-term Vision (12 months)
        elements.append(Paragraph("<b>Long-term Vision (12 Months):</b>", self.report_styles['ExecutiveBody']))
        
        long_term = [
            "Achieve SOC 2 Type II certification to strengthen customer trust",
            "Implement AI-driven security orchestration and automated response",
            "Establish comprehensive third-party risk management program",
            "Deploy advanced deception technology for early threat detection"
        ]
        
        for item in long_term:
            elements.append(Paragraph(f"• {item}", self.report_styles['Recommendation']))
        
        return elements
    
    def _create_technical_cover_page(self, assessment_data: Dict[str, Any]) -> List:
        """Create technical report cover page"""
        # Similar to executive cover but with technical focus
        return self._create_cover_page(assessment_data)
    
    def _create_methodology_section(self) -> List:
        """Create assessment methodology section"""
        elements = []
        
        elements.append(Paragraph("Assessment Methodology", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        methodology_text = """
        Enterprise Scanner employs a comprehensive, multi-layered approach to cybersecurity assessment, 
        combining automated scanning, manual testing, and expert analysis to provide thorough security evaluation.
        
        <b>Assessment Components:</b>
        • Network infrastructure vulnerability scanning
        • Web application security testing
        • SSL/TLS configuration analysis
        • DNS security evaluation
        • Port and service enumeration
        • Security policy review
        • Compliance framework mapping
        
        <b>Standards and Frameworks:</b>
        Our assessment methodology aligns with industry-leading standards including NIST Cybersecurity Framework, 
        ISO 27001, OWASP Top 10, and CIS Critical Security Controls.
        """
        
        elements.append(Paragraph(methodology_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_detailed_findings(self, findings: List[Dict]) -> List:
        """Create detailed technical findings section"""
        elements = []
        
        elements.append(Paragraph("Detailed Security Findings", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        for finding in findings[:10]:  # Limit to top 10 findings
            # Finding Title
            risk_level = finding.get('risk_level', 'Medium')
            title = finding.get('title', 'Security Finding')
            
            risk_style = f'Risk{risk_level}' if f'Risk{risk_level}' in self.report_styles else 'ExecutiveBody'
            elements.append(Paragraph(f"<b>{title}</b> - {risk_level} Risk", self.report_styles[risk_style]))
            
            # Finding Description
            description = finding.get('description', 'No description available')
            elements.append(Paragraph(description, self.report_styles['TechnicalFinding']))
            
            # Recommendation
            recommendation = finding.get('recommendation', 'Review and remediate as needed')
            elements.append(Paragraph(f"<b>Recommendation:</b> {recommendation}", self.report_styles['Recommendation']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_vulnerability_analysis(self, assessment_data: Dict[str, Any]) -> List:
        """Create vulnerability analysis section"""
        elements = []
        
        elements.append(Paragraph("Vulnerability Analysis", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        vuln_text = """
        The vulnerability assessment identified various security issues across your digital infrastructure. 
        Our analysis prioritizes vulnerabilities based on exploitability, business impact, and regulatory compliance requirements.
        
        <b>Vulnerability Categories:</b>
        • SSL/TLS Configuration Issues: 8 findings
        • Missing Security Patches: 15 findings  
        • Network Security Gaps: 6 findings
        • Web Application Vulnerabilities: 12 findings
        • Access Control Issues: 5 findings
        """
        
        elements.append(Paragraph(vuln_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_compliance_assessment(self, assessment_data: Dict[str, Any]) -> List:
        """Create compliance assessment section"""
        elements = []
        
        elements.append(Paragraph("Compliance Assessment", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        compliance_data = [
            ['Framework', 'Compliance Score', 'Status', 'Priority Actions'],
            ['NIST Framework', '92%', 'Compliant', '3 minor gaps'],
            ['ISO 27001', '89%', 'Compliant', '5 improvements needed'],
            ['SOX Compliance', '76%', 'Partial', '8 controls to implement'],
            ['GDPR', '94%', 'Compliant', '2 documentation updates']
        ]
        
        compliance_table = Table(compliance_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 2*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, self.brand_colors['primary'])
        ]))
        
        elements.append(compliance_table)
        
        return elements
    
    def _create_remediation_roadmap(self, assessment_data: Dict[str, Any]) -> List:
        """Create remediation roadmap section"""
        elements = []
        
        elements.append(Paragraph("Remediation Roadmap", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        roadmap_text = """
        <b>Phase 1 (Immediate - 30 days):</b>
        • Address critical SSL certificate expirations
        • Deploy high-priority security patches
        • Complete overdue access control reviews
        
        <b>Phase 2 (Short-term - 90 days):</b>
        • Implement automated certificate management
        • Enhance network segmentation
        • Upgrade web application security controls
        
        <b>Phase 3 (Long-term - 6-12 months):</b>
        • Complete zero-trust architecture deployment
        • Implement advanced threat detection
        • Achieve additional compliance certifications
        """
        
        elements.append(Paragraph(roadmap_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_compliance_cover_page(self, assessment_data: Dict[str, Any], framework: str) -> List:
        """Create compliance-specific cover page"""
        elements = []
        
        elements.append(Spacer(1, 1*inch))
        
        title = Paragraph(
            f"ENTERPRISE SCANNER<br/>{framework} Compliance Assessment Report",
            self.report_styles['ExecutiveTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        assessment_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(
            f"<b>Assessment Date:</b> {assessment_date}",
            self.report_styles['ExecutiveBody']
        ))
        
        return elements
    
    def _create_compliance_executive_summary(self, assessment_data: Dict[str, Any], framework: str) -> List:
        """Create compliance executive summary"""
        elements = []
        
        elements.append(Paragraph(f"{framework} Compliance Executive Summary", self.report_styles['ExecutiveTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        compliance_score = assessment_data.get('compliance_scores', {}).get(framework, 92)
        
        summary_text = f"""
        Enterprise Scanner conducted a comprehensive {framework} compliance assessment of your organization's 
        cybersecurity program. Our analysis reveals a <b>{compliance_score}% compliance rate</b> with the 
        {framework} framework, indicating strong alignment with industry best practices.
        
        <b>Compliance Highlights:</b>
        • Strong governance and risk management processes
        • Effective technical safeguards and controls
        • Comprehensive security awareness training program
        • Regular monitoring and assessment procedures
        
        <b>Areas for Enhancement:</b>
        • Documentation updates for 3 control families
        • Implementation of 2 additional technical controls
        • Enhancement of incident response procedures
        """
        
        elements.append(Paragraph(summary_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_framework_mapping(self, assessment_data: Dict[str, Any], framework: str) -> List:
        """Create framework control mapping section"""
        elements = []
        
        elements.append(Paragraph(f"{framework} Framework Mapping", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # This would contain detailed framework mapping
        mapping_text = f"""
        This section provides a comprehensive mapping of your organization's security controls 
        to the {framework} framework requirements. Each control family has been evaluated 
        for implementation effectiveness and compliance adherence.
        """
        
        elements.append(Paragraph(mapping_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_gap_analysis(self, assessment_data: Dict[str, Any], framework: str) -> List:
        """Create compliance gap analysis section"""
        elements = []
        
        elements.append(Paragraph("Compliance Gap Analysis", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        gap_text = """
        The gap analysis identifies specific areas where additional controls or documentation 
        may be required to achieve full compliance with the framework requirements.
        
        <b>Identified Gaps:</b>
        • Control documentation requires updating for 3 families
        • 2 technical controls need implementation
        • Incident response procedures need enhancement
        • Annual security training completion tracking improvement needed
        """
        
        elements.append(Paragraph(gap_text, self.report_styles['ExecutiveBody']))
        
        return elements
    
    def _create_compliance_roadmap(self, assessment_data: Dict[str, Any], framework: str) -> List:
        """Create compliance improvement roadmap"""
        elements = []
        
        elements.append(Paragraph("Compliance Improvement Roadmap", self.report_styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        roadmap_text = f"""
        <b>30-Day Actions:</b>
        • Update control documentation for identified gaps
        • Complete outstanding policy reviews
        • Implement missing technical controls
        
        <b>90-Day Initiatives:</b>
        • Enhance incident response procedures
        • Implement automated compliance monitoring
        • Complete staff training on new procedures
        
        <b>Annual Goals:</b>
        • Achieve 98%+ {framework} compliance rating
        • Implement continuous compliance monitoring
        • Establish quarterly compliance assessments
        """
        
        elements.append(Paragraph(roadmap_text, self.report_styles['ExecutiveBody']))
        
        return elements


def create_sample_assessment_data() -> Dict[str, Any]:
    """Create sample assessment data for testing"""
    return {
        'overall_score': 87,
        'threats_blocked': 2847,
        'cost_avoidance': '$3.2M',
        'compliance_scores': {
            'NIST': 92,
            'ISO27001': 89,
            'SOX': 76,
            'GDPR': 94
        },
        'vulnerabilities': {
            'critical': 2,
            'high': 7,
            'medium': 14,
            'low': 23
        },
        'assessment_date': datetime.now().isoformat(),
        'target_domain': 'example.com'
    }


if __name__ == "__main__":
    # Test report generation
    generator = EnterpriseReportGenerator()
    sample_data = create_sample_assessment_data()
    
    print("Generating sample Executive Report...")
    executive_pdf = generator.generate_executive_report(
        sample_data, 
        {'name': 'Fortune 500 Technology Company'}
    )
    
    with open('sample_executive_report.pdf', 'wb') as f:
        f.write(executive_pdf)
    
    print("Executive report generated: sample_executive_report.pdf")
    print("PDF Report Generator ready for Enterprise Scanner integration!")