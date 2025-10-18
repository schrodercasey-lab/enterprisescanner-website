#!/usr/bin/env python3
"""
Live Security Assessment Tool
Interactive Fortune 500 Security Posture Evaluation
Real-Time Risk Analysis & Recommendation Engine
"""

import json
import os
import datetime
import uuid
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import logging
from flask import Flask, render_template_string, jsonify, request, session
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SecurityDomain:
    """Security assessment domain definition"""
    domain_id: str
    domain_name: str
    weight: float
    questions: List[Dict[str, Any]]
    max_score: int
    industry_benchmarks: Dict[str, float]

@dataclass
class AssessmentResult:
    """Security assessment result"""
    assessment_id: str
    company_name: str
    industry: str
    assessment_date: datetime.datetime
    domain_scores: Dict[str, float]
    overall_score: float
    risk_level: str
    recommendations: List[str]
    estimated_roi: float
    contact_info: Dict[str, str]

class LiveSecurityAssessment:
    """Interactive security assessment platform"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        self.assessment_port = 5004
        self.security_domains = {}
        self.assessment_results = {}
        
    def initialize_security_domains(self):
        """Initialize comprehensive security assessment domains"""
        logger.info("Initializing security assessment domains...")
        
        # Identity & Access Management Domain
        iam_domain = SecurityDomain(
            domain_id="iam",
            domain_name="Identity & Access Management",
            weight=0.20,
            max_score=100,
            industry_benchmarks={
                "technology": 85.0,
                "financial": 90.0,
                "healthcare": 88.0,
                "retail": 75.0,
                "manufacturing": 70.0,
                "energy": 72.0
            },
            questions=[
                {
                    "id": "iam_1",
                    "question": "Does your organization implement multi-factor authentication (MFA) for all privileged accounts?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Yes, for all privileged accounts", "score": 25},
                        {"text": "Yes, for most privileged accounts (80%+)", "score": 20},
                        {"text": "Yes, for some privileged accounts (50-80%)", "score": 10},
                        {"text": "Limited implementation (<50%)", "score": 5},
                        {"text": "No MFA implementation", "score": 0}
                    ]
                },
                {
                    "id": "iam_2", 
                    "question": "How frequently do you review and audit user access permissions?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Continuous automated review", "score": 25},
                        {"text": "Monthly reviews", "score": 20},
                        {"text": "Quarterly reviews", "score": 15},
                        {"text": "Annual reviews", "score": 10},
                        {"text": "Ad-hoc or no regular reviews", "score": 0}
                    ]
                },
                {
                    "id": "iam_3",
                    "question": "Do you have automated user provisioning and deprovisioning processes?",
                    "type": "multiple_choice", 
                    "options": [
                        {"text": "Fully automated with real-time sync", "score": 25},
                        {"text": "Mostly automated with manual oversight", "score": 20},
                        {"text": "Semi-automated with manual processes", "score": 10},
                        {"text": "Primarily manual processes", "score": 5},
                        {"text": "Completely manual", "score": 0}
                    ]
                },
                {
                    "id": "iam_4",
                    "question": "What level of privileged access management (PAM) do you have implemented?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Enterprise PAM with session recording and just-in-time access", "score": 25},
                        {"text": "PAM solution with password vaulting", "score": 20},
                        {"text": "Basic privileged account management", "score": 10},
                        {"text": "Shared privileged accounts with basic controls", "score": 5},
                        {"text": "No formal PAM implementation", "score": 0}
                    ]
                }
            ]
        )
        
        # Network Security Domain
        network_domain = SecurityDomain(
            domain_id="network",
            domain_name="Network Security",
            weight=0.18,
            max_score=100,
            industry_benchmarks={
                "technology": 82.0,
                "financial": 88.0,
                "healthcare": 85.0,
                "retail": 78.0,
                "manufacturing": 75.0,
                "energy": 80.0
            },
            questions=[
                {
                    "id": "net_1",
                    "question": "Do you implement network segmentation and micro-segmentation?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Full micro-segmentation with zero-trust architecture", "score": 25},
                        {"text": "Network segmentation with VLANs and subnets", "score": 20},
                        {"text": "Basic network segmentation", "score": 15},
                        {"text": "Limited segmentation", "score": 8},
                        {"text": "Flat network architecture", "score": 0}
                    ]
                },
                {
                    "id": "net_2",
                    "question": "What type of intrusion detection/prevention system (IDS/IPS) do you use?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Next-generation IPS with AI/ML threat detection", "score": 25},
                        {"text": "Advanced IPS with behavioral analysis", "score": 20},
                        {"text": "Traditional signature-based IPS", "score": 15},
                        {"text": "Basic intrusion detection only", "score": 10},
                        {"text": "No IDS/IPS implementation", "score": 0}
                    ]
                },
                {
                    "id": "net_3",
                    "question": "How do you monitor and analyze network traffic?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Real-time network analytics with AI-powered threat hunting", "score": 25},
                        {"text": "Network monitoring with automated alerting", "score": 20},
                        {"text": "Basic network monitoring and logging", "score": 15},
                        {"text": "Limited traffic visibility", "score": 8},
                        {"text": "No comprehensive network monitoring", "score": 0}
                    ]
                },
                {
                    "id": "net_4",
                    "question": "What is your approach to securing remote access and VPN?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Zero-trust network access with device verification", "score": 25},
                        {"text": "VPN with MFA and device management", "score": 20},
                        {"text": "Standard VPN with basic authentication", "score": 15},
                        {"text": "Limited VPN access controls", "score": 8},
                        {"text": "Basic or no remote access security", "score": 0}
                    ]
                }
            ]
        )
        
        # Data Protection Domain
        data_domain = SecurityDomain(
            domain_id="data",
            domain_name="Data Protection & Privacy",
            weight=0.22,
            max_score=100,
            industry_benchmarks={
                "technology": 80.0,
                "financial": 92.0,
                "healthcare": 90.0,
                "retail": 78.0,
                "manufacturing": 73.0,
                "energy": 75.0
            },
            questions=[
                {
                    "id": "data_1",
                    "question": "How do you classify and protect sensitive data?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Automated data classification with DLP and encryption", "score": 25},
                        {"text": "Data classification with manual enforcement", "score": 20},
                        {"text": "Basic data categorization", "score": 15},
                        {"text": "Limited data protection measures", "score": 8},
                        {"text": "No formal data classification", "score": 0}
                    ]
                },
                {
                    "id": "data_2",
                    "question": "What encryption standards do you use for data at rest and in transit?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "AES-256 encryption with key management and perfect forward secrecy", "score": 25},
                        {"text": "Strong encryption (AES-256) with centralized key management", "score": 20},
                        {"text": "Standard encryption with basic key management", "score": 15},
                        {"text": "Limited encryption implementation", "score": 8},
                        {"text": "Minimal or no encryption", "score": 0}
                    ]
                },
                {
                    "id": "data_3",
                    "question": "How do you handle data backup and recovery?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Automated 3-2-1 backup strategy with immutable backups and tested recovery", "score": 25},
                        {"text": "Regular automated backups with documented recovery procedures", "score": 20},
                        {"text": "Scheduled backups with basic recovery testing", "score": 15},
                        {"text": "Irregular backups with limited recovery testing", "score": 8},
                        {"text": "No formal backup and recovery strategy", "score": 0}
                    ]
                },
                {
                    "id": "data_4",
                    "question": "What data privacy compliance frameworks do you follow?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Full compliance with GDPR, CCPA, and industry-specific regulations", "score": 25},
                        {"text": "Compliance with primary applicable regulations", "score": 20},
                        {"text": "Working toward full compliance", "score": 15},
                        {"text": "Basic privacy measures", "score": 8},
                        {"text": "Limited privacy compliance", "score": 0}
                    ]
                }
            ]
        )
        
        # Incident Response Domain
        incident_domain = SecurityDomain(
            domain_id="incident",
            domain_name="Incident Response & Recovery",
            weight=0.20,
            max_score=100,
            industry_benchmarks={
                "technology": 78.0,
                "financial": 85.0,
                "healthcare": 82.0,
                "retail": 72.0,
                "manufacturing": 68.0,
                "energy": 75.0
            },
            questions=[
                {
                    "id": "inc_1",
                    "question": "Do you have a formal incident response plan and team?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Dedicated CSIRT with 24/7 coverage and automated playbooks", "score": 25},
                        {"text": "Formal incident response team with documented procedures", "score": 20},
                        {"text": "Basic incident response plan with assigned roles", "score": 15},
                        {"text": "Informal incident handling procedures", "score": 8},
                        {"text": "No formal incident response capability", "score": 0}
                    ]
                },
                {
                    "id": "inc_2",
                    "question": "How frequently do you test and update your incident response procedures?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Quarterly tabletop exercises and annual full-scale simulations", "score": 25},
                        {"text": "Semi-annual testing and regular plan updates", "score": 20},
                        {"text": "Annual testing with periodic updates", "score": 15},
                        {"text": "Infrequent or ad-hoc testing", "score": 8},
                        {"text": "No regular testing or updates", "score": 0}
                    ]
                },
                {
                    "id": "inc_3",
                    "question": "What is your mean time to detection (MTTD) for security incidents?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Less than 1 hour with automated detection", "score": 25},
                        {"text": "1-24 hours", "score": 20},
                        {"text": "1-7 days", "score": 15},
                        {"text": "1-30 days", "score": 8},
                        {"text": "More than 30 days or unknown", "score": 0}
                    ]
                },
                {
                    "id": "inc_4",
                    "question": "How do you handle forensic analysis and evidence preservation?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Automated forensic tools with legal-grade evidence preservation", "score": 25},
                        {"text": "Formal forensic procedures with trained personnel", "score": 20},
                        {"text": "Basic evidence collection and analysis", "score": 15},
                        {"text": "Limited forensic capabilities", "score": 8},
                        {"text": "No formal forensic analysis", "score": 0}
                    ]
                }
            ]
        )
        
        # Governance & Compliance Domain
        governance_domain = SecurityDomain(
            domain_id="governance",
            domain_name="Security Governance & Compliance",
            weight=0.20,
            max_score=100,
            industry_benchmarks={
                "technology": 75.0,
                "financial": 88.0,
                "healthcare": 85.0,
                "retail": 70.0,
                "manufacturing": 65.0,
                "energy": 78.0
            },
            questions=[
                {
                    "id": "gov_1",
                    "question": "Do you have a formal cybersecurity governance structure?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Board-level cybersecurity committee with regular reporting", "score": 25},
                        {"text": "Executive-level security governance with C-suite oversight", "score": 20},
                        {"text": "Formal security policies with management oversight", "score": 15},
                        {"text": "Basic security policies and procedures", "score": 8},
                        {"text": "No formal governance structure", "score": 0}
                    ]
                },
                {
                    "id": "gov_2",
                    "question": "How do you manage third-party and vendor cybersecurity risk?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Comprehensive vendor risk management with continuous monitoring", "score": 25},
                        {"text": "Formal vendor assessments and contractual security requirements", "score": 20},
                        {"text": "Basic vendor security evaluations", "score": 15},
                        {"text": "Limited vendor risk management", "score": 8},
                        {"text": "No formal vendor risk assessment", "score": 0}
                    ]
                },
                {
                    "id": "gov_3",
                    "question": "What cybersecurity training and awareness programs do you have?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Comprehensive training with phishing simulations and role-specific content", "score": 25},
                        {"text": "Regular security awareness training for all employees", "score": 20},
                        {"text": "Basic annual security training", "score": 15},
                        {"text": "Limited or ad-hoc training", "score": 8},
                        {"text": "No formal security training program", "score": 0}
                    ]
                },
                {
                    "id": "gov_4",
                    "question": "How do you measure and report on cybersecurity metrics?",
                    "type": "multiple_choice",
                    "options": [
                        {"text": "Comprehensive KPIs with executive dashboards and board reporting", "score": 25},
                        {"text": "Regular security metrics reporting to management", "score": 20},
                        {"text": "Basic security metrics tracking", "score": 15},
                        {"text": "Limited metrics collection", "score": 8},
                        {"text": "No formal security metrics program", "score": 0}
                    ]
                }
            ]
        )
        
        # Store domains
        self.security_domains = {
            "iam": iam_domain,
            "network": network_domain, 
            "data": data_domain,
            "incident": incident_domain,
            "governance": governance_domain
        }
        
        logger.info(f"✅ Initialized {len(self.security_domains)} security assessment domains")
    
    def calculate_assessment_score(self, responses: Dict[str, Any], company_info: Dict[str, str]) -> AssessmentResult:
        """Calculate comprehensive assessment score and recommendations"""
        
        domain_scores = {}
        total_weighted_score = 0
        
        # Calculate scores for each domain
        for domain_id, domain in self.security_domains.items():
            domain_score = 0
            domain_responses = [r for r in responses if r.get('question_id', '').startswith(domain_id)]
            
            for response in domain_responses:
                domain_score += response.get('score', 0)
            
            # Convert to percentage
            domain_percentage = (domain_score / domain.max_score) * 100
            domain_scores[domain_id] = domain_percentage
            total_weighted_score += domain_percentage * domain.weight
        
        # Determine risk level
        if total_weighted_score >= 85:
            risk_level = "Low"
        elif total_weighted_score >= 70:
            risk_level = "Medium"
        elif total_weighted_score >= 50:
            risk_level = "High"
        else:
            risk_level = "Critical"
        
        # Generate recommendations based on lowest scoring domains
        recommendations = self.generate_recommendations(domain_scores, company_info.get('industry', 'technology'))
        
        # Calculate estimated ROI
        estimated_roi = self.calculate_estimated_roi(total_weighted_score, company_info)
        
        # Create assessment result
        assessment_result = AssessmentResult(
            assessment_id=str(uuid.uuid4()),
            company_name=company_info.get('company_name', 'Unknown'),
            industry=company_info.get('industry', 'technology'),
            assessment_date=datetime.datetime.now(),
            domain_scores=domain_scores,
            overall_score=total_weighted_score,
            risk_level=risk_level,
            recommendations=recommendations,
            estimated_roi=estimated_roi,
            contact_info=company_info
        )
        
        return assessment_result
    
    def generate_recommendations(self, domain_scores: Dict[str, float], industry: str) -> List[str]:
        """Generate targeted recommendations based on assessment results"""
        
        recommendations = []
        industry_benchmarks = {}
        
        # Get industry benchmarks
        for domain_id, domain in self.security_domains.items():
            industry_benchmarks[domain_id] = domain.industry_benchmarks.get(industry, 75.0)
        
        # Identify improvement areas
        for domain_id, score in domain_scores.items():
            benchmark = industry_benchmarks[domain_id]
            domain_name = self.security_domains[domain_id].domain_name
            
            if score < benchmark - 15:
                if domain_id == "iam":
                    recommendations.append(f"🔐 Critical: Implement comprehensive Identity & Access Management with MFA, PAM, and automated provisioning. Current score ({score:.0f}%) significantly below industry benchmark ({benchmark:.0f}%)")
                elif domain_id == "network":
                    recommendations.append(f"🛡️ Priority: Deploy advanced network security with micro-segmentation, next-gen IPS, and zero-trust architecture. Current gap: {benchmark-score:.0f} points")
                elif domain_id == "data":
                    recommendations.append(f"🔒 Urgent: Strengthen data protection with automated classification, encryption, and privacy compliance. Industry gap: {benchmark-score:.0f} points")
                elif domain_id == "incident":
                    recommendations.append(f"🚨 Critical: Establish 24/7 incident response capabilities with automated detection and response playbooks. Below benchmark by {benchmark-score:.0f} points")
                elif domain_id == "governance":
                    recommendations.append(f"📋 Essential: Implement executive-level security governance with board oversight and comprehensive metrics. Gap: {benchmark-score:.0f} points")
            
            elif score < benchmark:
                recommendations.append(f"✨ Optimize {domain_name}: Enhance existing controls to meet industry standards. Potential improvement: {benchmark-score:.0f} points")
        
        # Add Enterprise Scanner value propositions
        if len(recommendations) > 0:
            recommendations.append("🏢 Enterprise Scanner can address these gaps with our AI-powered cybersecurity platform, providing automated threat detection, compliance reporting, and executive dashboards.")
            recommendations.append("📊 Our platform integrates with 11+ enterprise security systems and provides real-time business impact analysis for C-suite reporting.")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def calculate_estimated_roi(self, overall_score: float, company_info: Dict[str, str]) -> float:
        """Calculate estimated ROI from security improvements"""
        
        # Base ROI calculation based on security maturity gap
        security_gap = max(0, 85 - overall_score)  # Target: 85% security maturity
        
        # Industry-specific risk multipliers
        industry_multipliers = {
            "financial": 2.5,
            "healthcare": 2.2,
            "technology": 1.8,
            "retail": 1.6,
            "manufacturing": 1.4,
            "energy": 2.0
        }
        
        industry = company_info.get('industry', 'technology')
        multiplier = industry_multipliers.get(industry, 1.5)
        
        # Estimate potential cost savings (in millions)
        # Based on: breach cost avoidance, compliance efficiency, operational savings
        base_savings = (security_gap / 10) * multiplier
        
        # Add Enterprise Scanner specific value
        platform_value = base_savings * 0.4  # 40% additional value from platform capabilities
        
        total_estimated_roi = base_savings + platform_value
        
        return round(total_estimated_roi, 1)
    
    def create_assessment_template(self):
        """Create interactive assessment HTML template"""
        
        assessment_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Security Assessment - Enterprise Scanner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .assessment-container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.5;
        }
        
        .progress-container {
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            margin-top: 10px;
            text-align: center;
            font-weight: 600;
            color: #495057;
        }
        
        .content {
            padding: 40px;
        }
        
        .step {
            display: none;
        }
        
        .step.active {
            display: block;
        }
        
        .step h2 {
            color: #1e3c72;
            margin-bottom: 25px;
            font-size: 1.8em;
            border-bottom: 3px solid #2a5298;
            padding-bottom: 10px;
        }
        
        .question-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 5px solid #2a5298;
        }
        
        .question-text {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #495057;
        }
        
        .option {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
        }
        
        .option:hover {
            border-color: #2a5298;
            background: #f8f9fa;
        }
        
        .option.selected {
            border-color: #28a745;
            background: #d4edda;
        }
        
        .option input[type="radio"] {
            margin-right: 15px;
            transform: scale(1.2);
        }
        
        .company-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .input-group {
            display: flex;
            flex-direction: column;
        }
        
        .input-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #495057;
        }
        
        .input-group input,
        .input-group select {
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .input-group input:focus,
        .input-group select:focus {
            outline: none;
            border-color: #2a5298;
        }
        
        .navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
            padding-top: 25px;
            border-top: 1px solid #e9ecef;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #2a5298, #1e3c72);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(42, 82, 152, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .results-container {
            text-align: center;
        }
        
        .score-circle {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient(#28a745 0% var(--score-percentage), #e9ecef var(--score-percentage) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 30px;
            position: relative;
        }
        
        .score-inner {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .score-value {
            font-size: 3em;
            font-weight: bold;
            color: #1e3c72;
        }
        
        .score-label {
            font-size: 1em;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .risk-low { background: #d4edda; color: #155724; }
        .risk-medium { background: #fff3cd; color: #856404; }
        .risk-high { background: #f8d7da; color: #721c24; }
        .risk-critical { background: #f5c6cb; color: #721c24; }
        
        .recommendations {
            text-align: left;
            margin-top: 30px;
        }
        
        .recommendation {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #2a5298;
        }
        
        .domain-scores {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .domain-score {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .domain-name {
            font-weight: 600;
            margin-bottom: 10px;
            color: #495057;
        }
        
        .domain-percentage {
            font-size: 2em;
            font-weight: bold;
            color: #1e3c72;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-top: 30px;
            text-align: center;
        }
        
        .cta-section h3 {
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .cta-section p {
            margin-bottom: 20px;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            .assessment-container {
                margin: 10px;
                border-radius: 15px;
            }
            
            .header {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .content {
                padding: 20px;
            }
            
            .company-info {
                grid-template-columns: 1fr;
            }
            
            .navigation {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="assessment-container">
        <div class="header">
            <h1>🔒 Live Security Assessment</h1>
            <p>Evaluate your organization's cybersecurity posture with our comprehensive Fortune 500-grade assessment tool. Get instant insights, benchmarking, and personalized recommendations.</p>
        </div>
        
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Step 1 of 6</div>
        </div>
        
        <div class="content">
            <!-- Company Information Step -->
            <div class="step active" id="step0">
                <h2>📋 Company Information</h2>
                <div class="company-info">
                    <div class="input-group">
                        <label for="companyName">Company Name *</label>
                        <input type="text" id="companyName" required>
                    </div>
                    <div class="input-group">
                        <label for="industry">Industry *</label>
                        <select id="industry" required>
                            <option value="">Select Industry</option>
                            <option value="technology">Technology</option>
                            <option value="financial">Financial Services</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="retail">Retail</option>
                            <option value="manufacturing">Manufacturing</option>
                            <option value="energy">Energy</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label for="contactName">Contact Name *</label>
                        <input type="text" id="contactName" required>
                    </div>
                    <div class="input-group">
                        <label for="contactEmail">Email Address *</label>
                        <input type="email" id="contactEmail" required>
                    </div>
                    <div class="input-group">
                        <label for="contactTitle">Job Title</label>
                        <input type="text" id="contactTitle" placeholder="e.g., CISO, IT Director">
                    </div>
                    <div class="input-group">
                        <label for="companySize">Company Size</label>
                        <select id="companySize">
                            <option value="">Select Size</option>
                            <option value="small">1-500 employees</option>
                            <option value="medium">501-5,000 employees</option>
                            <option value="large">5,001-50,000 employees</option>
                            <option value="enterprise">50,000+ employees</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Assessment Questions will be populated here -->
            <div id="questionSteps"></div>
            
            <!-- Results Step -->
            <div class="step" id="resultsStep">
                <div class="results-container">
                    <h2>🎯 Your Security Assessment Results</h2>
                    <div class="score-circle" id="scoreCircle">
                        <div class="score-inner">
                            <div class="score-value" id="scoreValue">--</div>
                            <div class="score-label">Security Score</div>
                        </div>
                    </div>
                    
                    <div class="risk-badge" id="riskBadge">Calculating...</div>
                    
                    <div class="domain-scores" id="domainScores"></div>
                    
                    <div class="recommendations">
                        <h3>🚀 Recommended Improvements</h3>
                        <div id="recommendationsList"></div>
                    </div>
                    
                    <div class="cta-section">
                        <h3>💼 Ready to Strengthen Your Security?</h3>
                        <p>Enterprise Scanner can help you address these security gaps with our AI-powered cybersecurity platform.</p>
                        <a href="mailto:sales@enterprisescanner.com?subject=Security Assessment Follow-up" class="btn btn-primary">Schedule a Demo</a>
                    </div>
                </div>
            </div>
            
            <div class="navigation">
                <button class="btn btn-secondary" id="prevBtn" onclick="previousStep()" style="display: none;">Previous</button>
                <div id="stepIndicator"></div>
                <button class="btn btn-primary" id="nextBtn" onclick="nextStep()">Get Started</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentStep = 0;
        let totalSteps = 6;
        let assessmentData = {
            company_info: {},
            responses: []
        };
        let assessmentQuestions = {};
        
        // Initialize assessment
        document.addEventListener('DOMContentLoaded', function() {
            loadAssessmentQuestions();
            updateProgress();
            updateStepIndicator();
        });
        
        function loadAssessmentQuestions() {
            fetch('/api/assessment-questions')
                .then(response => response.json())
                .then(data => {
                    assessmentQuestions = data;
                    createQuestionSteps();
                    totalSteps = Object.keys(assessmentQuestions).length + 2; // +2 for info and results
                })
                .catch(error => console.error('Error loading questions:', error));
        }
        
        function createQuestionSteps() {
            const questionContainer = document.getElementById('questionSteps');
            let stepIndex = 1;
            
            Object.entries(assessmentQuestions).forEach(([domainId, domain]) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'step';
                stepDiv.id = `step${stepIndex}`;
                
                let questionsHtml = '';
                domain.questions.forEach(question => {
                    questionsHtml += `
                        <div class="question-card">
                            <div class="question-text">${question.question}</div>
                            <div class="options">
                                ${question.options.map((option, index) => `
                                    <div class="option" onclick="selectOption('${question.id}', ${option.score}, this)">
                                        <input type="radio" name="${question.id}" value="${option.score}">
                                        <span>${option.text}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                });
                
                stepDiv.innerHTML = `
                    <h2>🔒 ${domain.domain_name}</h2>
                    ${questionsHtml}
                `;
                
                questionContainer.appendChild(stepDiv);
                stepIndex++;
            });
        }
        
        function selectOption(questionId, score, element) {
            // Remove previous selections
            const options = element.parentNode.querySelectorAll('.option');
            options.forEach(opt => opt.classList.remove('selected'));
            
            // Select current option
            element.classList.add('selected');
            element.querySelector('input').checked = true;
            
            // Store response
            const existingIndex = assessmentData.responses.findIndex(r => r.question_id === questionId);
            if (existingIndex >= 0) {
                assessmentData.responses[existingIndex].score = score;
            } else {
                assessmentData.responses.push({
                    question_id: questionId,
                    score: score
                });
            }
        }
        
        function nextStep() {
            if (currentStep === 0) {
                // Validate company information
                if (!validateCompanyInfo()) {
                    return;
                }
                document.getElementById('nextBtn').textContent = 'Next';
            }
            
            if (currentStep === totalSteps - 2) {
                // Last question step, submit assessment
                submitAssessment();
                return;
            }
            
            if (currentStep < totalSteps - 1) {
                document.getElementById(`step${currentStep}`).classList.remove('active');
                currentStep++;
                document.getElementById(`step${currentStep}` || 'resultsStep').classList.add('active');
                updateProgress();
                updateNavigation();
                updateStepIndicator();
            }
        }
        
        function previousStep() {
            if (currentStep > 0) {
                document.getElementById(`step${currentStep}` === null ? 'resultsStep' : `step${currentStep}`).classList.remove('active');
                currentStep--;
                document.getElementById(`step${currentStep}`).classList.add('active');
                updateProgress();
                updateNavigation();
                updateStepIndicator();
            }
        }
        
        function validateCompanyInfo() {
            const requiredFields = ['companyName', 'industry', 'contactName', 'contactEmail'];
            let isValid = true;
            
            requiredFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (!field.value.trim()) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                } else {
                    field.style.borderColor = '#e9ecef';
                    assessmentData.company_info[fieldId] = field.value;
                }
            });
            
            // Store optional fields
            ['contactTitle', 'companySize'].forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field.value) {
                    assessmentData.company_info[fieldId] = field.value;
                }
            });
            
            return isValid;
        }
        
        function updateProgress() {
            const progress = (currentStep / (totalSteps - 1)) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = `Step ${currentStep + 1} of ${totalSteps}`;
        }
        
        function updateNavigation() {
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            prevBtn.style.display = currentStep > 0 ? 'block' : 'none';
            
            if (currentStep === totalSteps - 1) {
                nextBtn.style.display = 'none';
            } else if (currentStep === totalSteps - 2) {
                nextBtn.textContent = 'Complete Assessment';
            } else {
                nextBtn.textContent = currentStep === 0 ? 'Get Started' : 'Next';
            }
        }
        
        function updateStepIndicator() {
            const indicator = document.getElementById('stepIndicator');
            let dots = '';
            for (let i = 0; i < totalSteps; i++) {
                const active = i === currentStep ? 'active' : '';
                dots += `<span class="step-dot ${active}"></span>`;
            }
            indicator.innerHTML = dots;
        }
        
        function submitAssessment() {
            document.getElementById('nextBtn').disabled = true;
            document.getElementById('nextBtn').textContent = 'Processing...';
            
            fetch('/api/submit-assessment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(assessmentData)
            })
            .then(response => response.json())
            .then(result => {
                displayResults(result);
                nextStep(); // Move to results step
            })
            .catch(error => {
                console.error('Error submitting assessment:', error);
                alert('There was an error processing your assessment. Please try again.');
                document.getElementById('nextBtn').disabled = false;
                document.getElementById('nextBtn').textContent = 'Complete Assessment';
            });
        }
        
        function displayResults(result) {
            // Update overall score
            const scoreValue = Math.round(result.overall_score);
            document.getElementById('scoreValue').textContent = scoreValue;
            
            // Update score circle
            const scoreCircle = document.getElementById('scoreCircle');
            scoreCircle.style.setProperty('--score-percentage', scoreValue + '%');
            
            // Update risk badge
            const riskBadge = document.getElementById('riskBadge');
            riskBadge.textContent = `Risk Level: ${result.risk_level}`;
            riskBadge.className = `risk-badge risk-${result.risk_level.toLowerCase()}`;
            
            // Update domain scores
            const domainScores = document.getElementById('domainScores');
            domainScores.innerHTML = '';
            Object.entries(result.domain_scores).forEach(([domain, score]) => {
                const domainDiv = document.createElement('div');
                domainDiv.className = 'domain-score';
                const domainName = assessmentQuestions[domain].domain_name;
                domainDiv.innerHTML = `
                    <div class="domain-name">${domainName}</div>
                    <div class="domain-percentage">${Math.round(score)}%</div>
                `;
                domainScores.appendChild(domainDiv);
            });
            
            // Update recommendations
            const recommendationsList = document.getElementById('recommendationsList');
            recommendationsList.innerHTML = '';
            result.recommendations.forEach(recommendation => {
                const recDiv = document.createElement('div');
                recDiv.className = 'recommendation';
                recDiv.textContent = recommendation;
                recommendationsList.appendChild(recDiv);
            });
        }
    </script>
    
    <style>
        .step-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #e9ecef;
            display: inline-block;
            margin: 0 5px;
            transition: background 0.3s ease;
        }
        
        .step-dot.active {
            background: #2a5298;
        }
    </style>
</body>
</html>
        """
        
        return assessment_html
    
    def setup_assessment_routes(self):
        """Setup Flask routes for the assessment"""
        
        @self.app.route('/')
        def assessment_home():
            return self.create_assessment_template()
        
        @self.app.route('/api/assessment-questions')
        def get_assessment_questions():
            questions_data = {}
            for domain_id, domain in self.security_domains.items():
                questions_data[domain_id] = {
                    'domain_name': domain.domain_name,
                    'questions': domain.questions
                }
            return jsonify(questions_data)
        
        @self.app.route('/api/submit-assessment', methods=['POST'])
        def submit_assessment():
            try:
                data = request.get_json()
                
                # Calculate assessment results
                result = self.calculate_assessment_score(
                    data.get('responses', []),
                    data.get('company_info', {})
                )
                
                # Store assessment result
                self.assessment_results[result.assessment_id] = result
                
                # Save to file for follow-up
                os.makedirs("assessments", exist_ok=True)
                with open(f"assessments/{result.assessment_id}.json", "w") as f:
                    result_dict = asdict(result)
                    result_dict['assessment_date'] = result_dict['assessment_date'].isoformat()
                    json.dump(result_dict, f, indent=2)
                
                logger.info(f"Assessment completed for {result.company_name}: {result.overall_score:.1f}% score")
                
                return jsonify({
                    'assessment_id': result.assessment_id,
                    'overall_score': result.overall_score,
                    'risk_level': result.risk_level,
                    'domain_scores': result.domain_scores,
                    'recommendations': result.recommendations,
                    'estimated_roi': result.estimated_roi
                })
                
            except Exception as e:
                logger.error(f"Assessment submission error: {e}")
                return jsonify({'error': 'Assessment processing failed'}), 500
        
        @self.app.route('/api/assessment-results/<assessment_id>')
        def get_assessment_results(assessment_id):
            if assessment_id in self.assessment_results:
                result = self.assessment_results[assessment_id]
                return jsonify(asdict(result))
            else:
                return jsonify({'error': 'Assessment not found'}), 404
    
    def run_assessment_platform(self):
        """Run the live security assessment platform"""
        self.initialize_security_domains()
        self.setup_assessment_routes()
        
        logger.info(f"🚀 Starting Live Security Assessment Platform...")
        logger.info(f"🔒 Assessment URL: http://localhost:{self.assessment_port}")
        logger.info(f"📊 Interactive security evaluation for Fortune 500 prospects")
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.assessment_port,
                debug=False
            )
        except Exception as e:
            logger.error(f"Assessment platform startup failed: {e}")

def main():
    """Deploy and run Live Security Assessment Platform"""
    print("=" * 80)
    print("🔒 LIVE SECURITY ASSESSMENT PLATFORM")
    print("Interactive Fortune 500 Security Evaluation Tool")
    print("=" * 80)
    
    assessment_platform = LiveSecurityAssessment()
    
    print(f"\n🎯 ASSESSMENT CAPABILITIES:")
    print(f"   📋 5 Security Domains: IAM, Network, Data Protection, Incident Response, Governance")
    print(f"   📊 20 Comprehensive Questions with industry benchmarking")
    print(f"   🏢 Fortune 500 industry-specific scoring and recommendations")
    print(f"   💰 ROI analysis and business impact assessment")
    print(f"   📈 Real-time results with personalized improvement roadmap")
    
    print(f"\n🚀 BUSINESS VALUE:")
    print(f"   🎯 Lead Generation: Interactive prospect engagement tool")
    print(f"   📊 Needs Assessment: Identify specific security gaps and opportunities")
    print(f"   💼 Value Demonstration: Show potential ROI from Enterprise Scanner platform")
    print(f"   🤝 Sales Enablement: Qualified leads with detailed security profiles")
    
    print(f"\n🔒 STARTING LIVE SECURITY ASSESSMENT...")
    print(f"📱 Interactive Platform: http://localhost:5004")
    print(f"🎯 Ready for Fortune 500 prospect engagement!")
    
    # Run assessment platform
    assessment_platform.run_assessment_platform()

if __name__ == "__main__":
    main()