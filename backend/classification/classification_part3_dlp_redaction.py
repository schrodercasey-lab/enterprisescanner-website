"""
Military-Grade Classification & Handling - Part 3 of 3
=======================================================

Data Loss Prevention (DLP) & Automated Redaction

Features:
- Real-time DLP policy enforcement
- PII/PHI detection and redaction
- Content inspection for classified data
- Transmission controls
- Automated redaction for FOIA requests

COMPLIANCE:
- NIST 800-171 (CUI Protection)
- HIPAA (PHI Protection)
- GDPR (PII Protection)
- Privacy Act of 1974
- FOIA (Redaction Requirements)
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


class DLPViolationType(Enum):
    """DLP violation types"""
    CLASSIFIED_DATA_LEAK = "Classified Data Leak"
    PII_EXPOSURE = "PII Exposure"
    PHI_EXPOSURE = "PHI Exposure"
    FINANCIAL_DATA = "Financial Data Exposure"
    INTELLECTUAL_PROPERTY = "IP Leak"
    UNAUTHORIZED_TRANSMISSION = "Unauthorized Transmission"


class RedactionReason(Enum):
    """Redaction reasons per FOIA"""
    EXEMPTION_1 = "National Security (b)(1)"
    EXEMPTION_2 = "Internal Personnel Rules (b)(2)"
    EXEMPTION_3 = "Statutory Exemption (b)(3)"
    EXEMPTION_4 = "Trade Secrets (b)(4)"
    EXEMPTION_5 = "Privileged Communications (b)(5)"
    EXEMPTION_6 = "Personal Privacy (b)(6)"
    EXEMPTION_7 = "Law Enforcement (b)(7)"


@dataclass
class PIIPattern:
    """PII detection pattern"""
    pattern_type: str
    regex: str
    description: str
    severity: str


@dataclass
class DLPViolation:
    """DLP policy violation"""
    violation_id: str
    violation_type: DLPViolationType
    severity: str
    detected_at: datetime
    content_snippet: str
    policy_violated: str
    action_taken: str


@dataclass
class RedactedDocument:
    """Redacted document"""
    document_id: str
    original_content: str
    redacted_content: str
    redaction_count: int
    redaction_reasons: List[RedactionReason]
    redacted_at: datetime


class DLPEngine:
    """Data Loss Prevention & Redaction Engine - Part 3"""
    
    def __init__(self):
        self.pii_patterns = self._load_pii_patterns()
        self.phi_patterns = self._load_phi_patterns()
        self.violations: List[DLPViolation] = []
        self.redacted_docs: Dict[str, RedactedDocument] = {}
    
    def scan_for_pii(self, content: str) -> List[Tuple[str, str, int, int]]:
        """Scan content for PII"""
        print("🔍 Scanning for PII...")
        
        detections = []
        
        for pattern in self.pii_patterns:
            matches = re.finditer(pattern.regex, content, re.IGNORECASE)
            for match in matches:
                detections.append((
                    pattern.pattern_type,
                    match.group(),
                    match.start(),
                    match.end()
                ))
        
        return detections
    
    def scan_for_phi(self, content: str) -> List[Tuple[str, str, int, int]]:
        """Scan content for PHI (HIPAA)"""
        print("🔍 Scanning for PHI...")
        
        detections = []
        
        for pattern in self.phi_patterns:
            matches = re.finditer(pattern.regex, content, re.IGNORECASE)
            for match in matches:
                detections.append((
                    pattern.pattern_type,
                    match.group(),
                    match.start(),
                    match.end()
                ))
        
        return detections
    
    def enforce_dlp_policy(self, content: str, transmission_type: str) -> Dict[str, Any]:
        """Enforce DLP policy on content transmission"""
        print(f"🛡️ Enforcing DLP policy for {transmission_type}...")
        
        violations_found = []
        
        # Check for PII
        pii_detections = self.scan_for_pii(content)
        if pii_detections and transmission_type == "EXTERNAL":
            violation = DLPViolation(
                violation_id=f"DLP-{datetime.now().timestamp()}",
                violation_type=DLPViolationType.PII_EXPOSURE,
                severity="HIGH",
                detected_at=datetime.now(),
                content_snippet=pii_detections[0][1][:50],
                policy_violated="PII External Transmission",
                action_taken="BLOCKED"
            )
            violations_found.append(violation)
            self.violations.append(violation)
        
        # Check for PHI
        phi_detections = self.scan_for_phi(content)
        if phi_detections:
            violation = DLPViolation(
                violation_id=f"DLP-{datetime.now().timestamp()}",
                violation_type=DLPViolationType.PHI_EXPOSURE,
                severity="CRITICAL",
                detected_at=datetime.now(),
                content_snippet=phi_detections[0][1][:50],
                policy_violated="PHI HIPAA Protection",
                action_taken="BLOCKED"
            )
            violations_found.append(violation)
            self.violations.append(violation)
        
        # Check for classified markings
        classified_patterns = [
            r'//SECRET//',
            r'//TOP SECRET//',
            r'//CONFIDENTIAL//'
        ]
        
        for pattern in classified_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violation = DLPViolation(
                    violation_id=f"DLP-{datetime.now().timestamp()}",
                    violation_type=DLPViolationType.CLASSIFIED_DATA_LEAK,
                    severity="CRITICAL",
                    detected_at=datetime.now(),
                    content_snippet="<classified content redacted>",
                    policy_violated="Classified Information Protection",
                    action_taken="BLOCKED"
                )
                violations_found.append(violation)
                self.violations.append(violation)
                break
        
        return {
            "allowed": len(violations_found) == 0,
            "violations_count": len(violations_found),
            "violations": violations_found,
            "action": "ALLOWED" if len(violations_found) == 0 else "BLOCKED"
        }
    
    def auto_redact_document(self, document_id: str, content: str,
                            redaction_reason: RedactionReason) -> RedactedDocument:
        """Automatically redact sensitive information"""
        print(f"✂️ Auto-redacting document: {document_id}")
        
        redacted_content = content
        redaction_count = 0
        
        # Redact PII
        pii_detections = self.scan_for_pii(content)
        for detection in pii_detections:
            pattern_type, matched_text, start, end = detection
            redacted_content = redacted_content.replace(
                matched_text,
                f"[REDACTED - {redaction_reason.value}]"
            )
            redaction_count += 1
        
        # Redact PHI
        phi_detections = self.scan_for_phi(content)
        for detection in phi_detections:
            pattern_type, matched_text, start, end = detection
            redacted_content = redacted_content.replace(
                matched_text,
                f"[REDACTED - {redaction_reason.value}]"
            )
            redaction_count += 1
        
        # Create redacted document
        redacted_doc = RedactedDocument(
            document_id=document_id,
            original_content=content,
            redacted_content=redacted_content,
            redaction_count=redaction_count,
            redaction_reasons=[redaction_reason],
            redacted_at=datetime.now()
        )
        
        self.redacted_docs[document_id] = redacted_doc
        
        print(f"✅ Redacted {redaction_count} items from document")
        return redacted_doc
    
    def _load_pii_patterns(self) -> List[PIIPattern]:
        """Load PII detection patterns"""
        return [
            PIIPattern(
                pattern_type="SSN",
                regex=r'\b\d{3}-\d{2}-\d{4}\b',
                description="Social Security Number",
                severity="HIGH"
            ),
            PIIPattern(
                pattern_type="EMAIL",
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                description="Email Address",
                severity="MEDIUM"
            ),
            PIIPattern(
                pattern_type="PHONE",
                regex=r'\b(\+1-?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                description="Phone Number",
                severity="MEDIUM"
            ),
            PIIPattern(
                pattern_type="CREDIT_CARD",
                regex=r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                description="Credit Card Number",
                severity="HIGH"
            ),
            PIIPattern(
                pattern_type="DATE_OF_BIRTH",
                regex=r'\b(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/\d{4}\b',
                description="Date of Birth",
                severity="MEDIUM"
            )
        ]
    
    def _load_phi_patterns(self) -> List[PIIPattern]:
        """Load PHI detection patterns (HIPAA)"""
        return [
            PIIPattern(
                pattern_type="MRN",
                regex=r'\bMRN[:\s]?\d{6,10}\b',
                description="Medical Record Number",
                severity="HIGH"
            ),
            PIIPattern(
                pattern_type="DIAGNOSIS_CODE",
                regex=r'\b[A-Z]\d{2}\.\d{1,2}\b',
                description="ICD-10 Diagnosis Code",
                severity="MEDIUM"
            ),
            PIIPattern(
                pattern_type="PRESCRIPTION",
                regex=r'\b(Rx|prescription)[:\s][\w\s]+\d+mg\b',
                description="Prescription Information",
                severity="HIGH"
            )
        ]


def main():
    """Test DLP engine"""
    engine = DLPEngine()
    
    # Test content with PII
    test_content = """
    Patient John Doe (SSN: 123-45-6789) was seen on 05/15/2024.
    Contact: john.doe@example.com or call 555-123-4567.
    MRN: 1234567
    """
    
    # Scan for PII
    pii = engine.scan_for_pii(test_content)
    print(f"PII Detected: {len(pii)} items")
    
    # Enforce DLP policy
    result = engine.enforce_dlp_policy(test_content, "EXTERNAL")
    print(f"DLP Action: {result['action']}")
    print(f"Violations: {result['violations_count']}")
    
    # Auto-redact
    redacted = engine.auto_redact_document(
        "DOC-001",
        test_content,
        RedactionReason.EXEMPTION_6
    )
    print(f"Redactions: {redacted.redaction_count}")


if __name__ == "__main__":
    main()
