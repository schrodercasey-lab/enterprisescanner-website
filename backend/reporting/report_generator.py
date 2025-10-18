"""
Advanced Reporting Engine
Professional security assessment reports for Enterprise Scanner

Generates multiple report types:
- Executive Summary Reports (C-level, board-ready)
- Technical Detailed Reports (security team format)
- Compliance Framework Reports (CIS, NIST, PCI-DSS, HIPAA)
- Trend and Comparison Reports (historical analysis)

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import io
import os

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ReportHeader:
    """Custom header/footer for professional reports"""
    
    def __init__(self, title: str, company_name: str):
        self.title = title
        self.company_name = company_name
    
    def __call__(self, canvas, doc):
        """Draw header and footer"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(inch, letter[1] - 0.5*inch, "Enterprise Scanner")
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(letter[0] - inch, letter[1] - 0.5*inch, 
                              datetime.now().strftime('%B %d, %Y'))
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.drawString(inch, 0.5*inch, f"CONFIDENTIAL - {self.company_name}")
        canvas.drawRightString(letter[0] - inch, 0.5*inch, 
                              f"Page {doc.page}")
        
        canvas.restoreState()


class ExecutiveReportGenerator:
    """
    Generate executive summary reports for C-level executives and board members
    
    Features:
    - High-level risk overview
    - Visual scoring with trend indicators
    - Top critical findings with business impact
    - Compliance posture summary
    - Board-ready formatting
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='ExecutiveTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExecutiveBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLabel',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def generate(self, assessment_data: Dict[str, Any], output_path: str,
                 trend_data: Optional[List[Dict]] = None) -> str:
        """
        Generate executive summary report
        
        Args:
            assessment_data: Complete assessment results
            output_path: Path to save PDF report
            trend_data: Optional historical trend data
        
        Returns:
            Path to generated PDF report
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        story = []
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        
        # Title Page
        story.extend(self._create_title_page(assessment_data, company_name))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(assessment_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Overview
        story.extend(self._create_risk_overview(assessment_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Key Findings
        story.extend(self._create_key_findings(assessment_data))
        story.append(PageBreak())
        
        # Strategic Recommendations
        story.extend(self._create_strategic_recommendations(assessment_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Compliance Posture
        story.extend(self._create_compliance_summary(assessment_data))
        
        # Trend Analysis (if available)
        if trend_data:
            story.append(PageBreak())
            story.extend(self._create_trend_analysis(trend_data))
        
        # Build PDF with custom header/footer
        doc.build(story, onFirstPage=ReportHeader("Executive Summary", company_name),
                 onLaterPages=ReportHeader("Executive Summary", company_name))
        
        return output_path
    
    def _create_title_page(self, assessment_data: Dict, company_name: str) -> List:
        """Create professional title page"""
        elements = []
        
        # Spacer to center content
        elements.append(Spacer(1, 2*inch))
        
        # Main Title
        title = Paragraph(
            "SECURITY ASSESSMENT<br/>EXECUTIVE SUMMARY",
            self.styles['ExecutiveTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Company Name
        company = Paragraph(
            f"<b>{company_name}</b>",
            ParagraphStyle('CompanyName', parent=self.styles['Normal'],
                         fontSize=18, alignment=TA_CENTER)
        )
        elements.append(company)
        elements.append(Spacer(1, inch))
        
        # Assessment Info
        assessment_date = assessment_data.get('assessment_metadata', {}).get(
            'assessment_date', datetime.now().isoformat()
        )
        date_str = datetime.fromisoformat(assessment_date.replace('Z', '+00:00')).strftime('%B %d, %Y')
        
        info_style = ParagraphStyle('InfoStyle', parent=self.styles['Normal'],
                                   fontSize=12, alignment=TA_CENTER, textColor=HexColor('#666666'))
        
        elements.append(Paragraph(f"Assessment Date: {date_str}", info_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            f"Assessment ID: {assessment_data.get('assessment_metadata', {}).get('assessment_id', 'N/A')}",
            info_style
        ))
        
        # Confidentiality Notice
        elements.append(Spacer(1, 1.5*inch))
        notice = Paragraph(
            "<b>CONFIDENTIAL</b><br/>This document contains sensitive security information and is "
            "intended solely for the use of executive leadership and board members. "
            "Unauthorized distribution is prohibited.",
            ParagraphStyle('Notice', parent=self.styles['Normal'],
                         fontSize=9, alignment=TA_CENTER, textColor=HexColor('#cc0000'))
        )
        elements.append(notice)
        
        return elements
    
    def _create_executive_summary(self, assessment_data: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        overall_score = assessment_data.get('overall_score', 0)
        risk_level = assessment_data.get('risk_level', 'UNKNOWN')
        risk_description = assessment_data.get('risk_description', '')
        
        # Summary text
        summary_text = f"""
        Enterprise Scanner has completed a comprehensive security assessment of your organization's 
        infrastructure, applications, and security posture. The assessment evaluated 
        {len(assessment_data.get('category_scores', {}))} critical security domains including 
        infrastructure security, network security, cloud security, container security, and compliance posture.
        <br/><br/>
        <b>Overall Security Score: {overall_score}/100</b>
        <br/>
        <b>Risk Level: {risk_level}</b>
        <br/><br/>
        {risk_description}
        """
        
        elements.append(Paragraph(summary_text, self.styles['ExecutiveBody']))
        
        return elements
    
    def _create_risk_overview(self, assessment_data: Dict) -> List:
        """Create risk overview with visual indicators"""
        elements = []
        
        elements.append(Paragraph("Risk Overview", self.styles['SectionHeader']))
        
        overall_score = assessment_data.get('overall_score', 0)
        vuln_counts = assessment_data.get('vulnerability_counts', {})
        
        # Score interpretation
        if overall_score >= 85:
            score_color = HexColor('#28a745')
            score_text = "STRONG SECURITY POSTURE"
        elif overall_score >= 70:
            score_color = HexColor('#ffc107')
            score_text = "MODERATE SECURITY POSTURE"
        elif overall_score >= 55:
            score_color = HexColor('#fd7e14')
            score_text = "ELEVATED SECURITY RISK"
        else:
            score_color = HexColor('#dc3545')
            score_text = "CRITICAL SECURITY RISK"
        
        # Risk summary table
        risk_data = [
            ['Security Metric', 'Value', 'Status'],
            ['Overall Security Score', f"{overall_score}/100", score_text],
            ['Critical Vulnerabilities', str(vuln_counts.get('critical', 0)), 
             'Immediate Action Required' if vuln_counts.get('critical', 0) > 0 else 'Good'],
            ['High Vulnerabilities', str(vuln_counts.get('high', 0)),
             'Review Required' if vuln_counts.get('high', 0) > 5 else 'Acceptable'],
            ['Total Findings', str(vuln_counts.get('total', 0)), 'See Details Below']
        ]
        
        risk_table = Table(risk_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
        ]))
        
        elements.append(risk_table)
        
        return elements
    
    def _create_key_findings(self, assessment_data: Dict) -> List:
        """Create key findings section with top critical issues"""
        elements = []
        
        elements.append(Paragraph("Critical Findings Requiring Attention", self.styles['SectionHeader']))
        
        # Get top 5 critical/high findings
        all_findings = assessment_data.get('findings', [])
        critical_findings = [f for f in all_findings if f.get('severity') == 'critical'][:5]
        high_findings = [f for f in all_findings if f.get('severity') == 'high'][:3]
        
        top_findings = critical_findings + high_findings[:8 - len(critical_findings)]
        
        if not top_findings:
            elements.append(Paragraph(
                "No critical or high-severity findings identified. Your security posture is strong.",
                self.styles['ExecutiveBody']
            ))
        else:
            for i, finding in enumerate(top_findings, 1):
                severity = finding.get('severity', 'unknown').upper()
                category = finding.get('category', 'Unknown')
                description = finding.get('description', 'No description available')
                
                # Severity color
                if severity == 'CRITICAL':
                    sev_color = HexColor('#dc3545')
                elif severity == 'HIGH':
                    sev_color = HexColor('#fd7e14')
                else:
                    sev_color = HexColor('#ffc107')
                
                finding_text = f"""
                <b>{i}. [{severity}] {category}</b><br/>
                {description}
                """
                
                elements.append(Paragraph(finding_text, self.styles['ExecutiveBody']))
                elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_strategic_recommendations(self, assessment_data: Dict) -> List:
        """Create strategic recommendations for executive action"""
        elements = []
        
        elements.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))
        
        recommendations = assessment_data.get('recommendations', [])[:5]
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_text = f"<b>{i}.</b> {rec}"
                elements.append(Paragraph(rec_text, self.styles['ExecutiveBody']))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph(
                "Continue current security practices and conduct regular assessments.",
                self.styles['ExecutiveBody']
            ))
        
        return elements
    
    def _create_compliance_summary(self, assessment_data: Dict) -> List:
        """Create compliance posture summary"""
        elements = []
        
        elements.append(Paragraph("Compliance Posture", self.styles['SectionHeader']))
        
        compliance_score = assessment_data.get('category_scores', {}).get('Compliance Posture', 0)
        
        compliance_text = f"""
        Your organization's compliance posture score is <b>{compliance_score}/100</b>. 
        This assessment evaluates alignment with major regulatory frameworks including 
        CIS Benchmarks, NIST Cybersecurity Framework, PCI-DSS, and HIPAA security requirements.
        <br/><br/>
        Regular compliance assessments are recommended to maintain regulatory alignment and 
        demonstrate due diligence to auditors and stakeholders.
        """
        
        elements.append(Paragraph(compliance_text, self.styles['ExecutiveBody']))
        
        return elements
    
    def _create_trend_analysis(self, trend_data: List[Dict]) -> List:
        """Create trend analysis section"""
        elements = []
        
        elements.append(Paragraph("Security Posture Trends", self.styles['SectionHeader']))
        
        if len(trend_data) >= 2:
            latest = trend_data[0]
            previous = trend_data[-1]
            
            score_change = latest.get('value', 0) - previous.get('value', 0)
            direction = "improved" if score_change > 0 else "declined" if score_change < 0 else "remained stable"
            
            trend_text = f"""
            Over the past {len(trend_data)} assessment(s), your security posture has <b>{direction}</b> 
            by {abs(score_change)} points. This trend analysis helps identify patterns and validate 
            the effectiveness of security investments.
            """
            
            elements.append(Paragraph(trend_text, self.styles['ExecutiveBody']))
        else:
            elements.append(Paragraph(
                "Insufficient historical data for trend analysis. Continue regular assessments to track progress.",
                self.styles['ExecutiveBody']
            ))
        
        return elements


class TechnicalReportGenerator:
    """
    Generate detailed technical reports for security teams
    
    Features:
    - Complete finding details with CVE IDs
    - Category-by-category breakdown
    - Remediation steps with priority rankings
    - Technical vulnerability details
    - Network/architecture analysis
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for technical reports"""
        self.styles.add(ParagraphStyle(
            name='TechnicalTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='CategoryHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=15,
            backColor=HexColor('#e9ecef'),
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='TechnicalBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            backColor=HexColor('#f8f9fa'),
            borderPadding=5
        ))
    
    def generate(self, assessment_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate technical detailed report
        
        Args:
            assessment_data: Complete assessment results
            output_path: Path to save PDF report
        
        Returns:
            Path to generated PDF report
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        
        # Title
        story.extend(self._create_tech_title(assessment_data, company_name))
        story.append(Spacer(1, 0.3*inch))
        
        # Assessment Overview
        story.extend(self._create_assessment_overview(assessment_data))
        story.append(PageBreak())
        
        # Category Breakdown
        story.extend(self._create_category_breakdown(assessment_data))
        story.append(PageBreak())
        
        # Detailed Findings
        story.extend(self._create_detailed_findings(assessment_data))
        story.append(PageBreak())
        
        # Remediation Guide
        story.extend(self._create_remediation_guide(assessment_data))
        
        # Build PDF
        doc.build(story, onFirstPage=ReportHeader("Technical Report", company_name),
                 onLaterPages=ReportHeader("Technical Report", company_name))
        
        return output_path
    
    def _create_tech_title(self, assessment_data: Dict, company_name: str) -> List:
        """Create technical report title"""
        elements = []
        
        title = Paragraph(
            f"Security Assessment - Technical Report<br/>{company_name}",
            self.styles['TechnicalTitle']
        )
        elements.append(title)
        
        assessment_date = assessment_data.get('assessment_metadata', {}).get(
            'assessment_date', datetime.now().isoformat()
        )
        date_str = datetime.fromisoformat(assessment_date.replace('Z', '+00:00')).strftime('%B %d, %Y')
        
        subtitle = Paragraph(
            f"Assessment Date: {date_str} | "
            f"ID: {assessment_data.get('assessment_metadata', {}).get('assessment_id', 'N/A')}",
            ParagraphStyle('Subtitle', parent=self.styles['Normal'], fontSize=10, textColor=HexColor('#666666'))
        )
        elements.append(subtitle)
        
        return elements
    
    def _create_assessment_overview(self, assessment_data: Dict) -> List:
        """Create technical assessment overview"""
        elements = []
        
        elements.append(Paragraph("Assessment Overview", self.styles['CategoryHeader']))
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Overall Security Score', f"{assessment_data.get('overall_score', 0)}/100"],
            ['Risk Level', assessment_data.get('risk_level', 'UNKNOWN')],
            ['Total Findings', str(assessment_data.get('vulnerability_counts', {}).get('total', 0))],
            ['Critical Findings', str(assessment_data.get('vulnerability_counts', {}).get('critical', 0))],
            ['High Findings', str(assessment_data.get('vulnerability_counts', {}).get('high', 0))],
            ['Medium Findings', str(assessment_data.get('vulnerability_counts', {}).get('medium', 0))],
            ['Low Findings', str(assessment_data.get('vulnerability_counts', {}).get('low', 0))]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#343a40')),
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
    
    def _create_category_breakdown(self, assessment_data: Dict) -> List:
        """Create category-by-category security breakdown"""
        elements = []
        
        elements.append(Paragraph("Security Category Breakdown", self.styles['CategoryHeader']))
        
        category_scores = assessment_data.get('category_scores', {})
        
        # Category scores table
        category_data = [['Security Category', 'Score', 'Grade']]
        
        for category, score in category_scores.items():
            grade = self._score_to_grade(score)
            category_data.append([category, f"{score}/100", grade])
        
        category_table = Table(category_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#343a40')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
        ]))
        
        elements.append(category_table)
        
        return elements
    
    def _create_detailed_findings(self, assessment_data: Dict) -> List:
        """Create detailed findings section with all vulnerabilities"""
        elements = []
        
        elements.append(Paragraph("Detailed Security Findings", self.styles['CategoryHeader']))
        
        findings = assessment_data.get('findings', [])
        
        # Group findings by severity
        by_severity = {
            'critical': [f for f in findings if f.get('severity') == 'critical'],
            'high': [f for f in findings if f.get('severity') == 'high'],
            'medium': [f for f in findings if f.get('severity') == 'medium'],
            'low': [f for f in findings if f.get('severity') == 'low']
        }
        
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_findings = by_severity[severity]
            
            if severity_findings:
                elements.append(Paragraph(
                    f"{severity.upper()} Severity Findings ({len(severity_findings)})",
                    self.styles['Heading3']
                ))
                elements.append(Spacer(1, 0.1*inch))
                
                for i, finding in enumerate(severity_findings, 1):
                    finding_text = f"""
                    <b>{i}. {finding.get('category', 'Unknown Category')}</b><br/>
                    <b>Description:</b> {finding.get('description', 'No description')}<br/>
                    <b>Impact:</b> {finding.get('impact', 'Unknown impact')}<br/>
                    <b>Remediation:</b> {finding.get('remediation', 'Contact security team')}
                    """
                    
                    elements.append(Paragraph(finding_text, self.styles['TechnicalBody']))
                    elements.append(Spacer(1, 0.15*inch))
                
                elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_remediation_guide(self, assessment_data: Dict) -> List:
        """Create prioritized remediation guide"""
        elements = []
        
        elements.append(Paragraph("Remediation Priority Guide", self.styles['CategoryHeader']))
        
        recommendations = assessment_data.get('recommendations', [])
        
        priority_text = """
        <b>Priority 1 (Immediate - 0-7 days):</b> Critical vulnerabilities requiring immediate action<br/>
        <b>Priority 2 (High - 7-30 days):</b> High-severity issues requiring prompt remediation<br/>
        <b>Priority 3 (Medium - 30-90 days):</b> Medium-severity issues for scheduled remediation<br/>
        <b>Priority 4 (Low - 90+ days):</b> Low-severity issues and security enhancements
        """
        elements.append(Paragraph(priority_text, self.styles['TechnicalBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        for i, rec in enumerate(recommendations[:10], 1):
            rec_text = f"<b>{i}.</b> {rec}"
            elements.append(Paragraph(rec_text, self.styles['TechnicalBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _score_to_grade(self, score: int) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Fair)'
        elif score >= 60:
            return 'D (Poor)'
        else:
            return 'F (Critical)'


# Export main classes
__all__ = ['ExecutiveReportGenerator', 'TechnicalReportGenerator']
