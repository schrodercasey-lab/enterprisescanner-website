"""
Military-Grade Classification & Handling - Part 1 of 3
=======================================================

Automated Classification Marking Engine

Supports:
- CUI (Controlled Unclassified Information)
- CONFIDENTIAL
- SECRET
- TOP SECRET
- Special Access Programs (SAP)

COMPLIANCE:
- EO 13556 (CUI)
- EO 13526 (Classified National Security Information)
- 32 CFR Part 2001 (Classified Information)
- NIST 800-171 (CUI Protection)
- ICD 710 (Classification and Control Markings)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re


class ClassificationLevel(Enum):
    """Classification levels per EO 13526"""
    UNCLASSIFIED = "UNCLASSIFIED"
    CUI = "CONTROLLED UNCLASSIFIED INFORMATION"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    TOP_SECRET = "TOP SECRET"
    TOP_SECRET_SCI = "TOP SECRET//SCI"


class CUICategory(Enum):
    """CUI categories per 32 CFR 2002"""
    PROPIN = "Proprietary Information"
    PRVCY = "Privacy Information"
    CTI = "Controlled Technical Information"
    ITAR = "International Traffic in Arms Regulations"
    EAR = "Export Administration Regulations"
    FOIA = "FOIA Exemption"
    EXPORT_CONTROLLED = "Export Controlled"
    LAW_ENFORCEMENT = "Law Enforcement Sensitive"
    CRITICAL_INFRASTRUCTURE = "Critical Infrastructure"


class SAPType(Enum):
    """Special Access Program types"""
    SAR = "Special Access Required"
    SAP_WAIVED = "Waived SAP"
    SAP_ACKNOWLEDGED = "Acknowledged SAP"
    SAP_UNACKNOWLEDGED = "Unacknowledged SAP"


@dataclass
class ClassificationMarking:
    """Document classification marking"""
    level: ClassificationLevel
    cui_categories: List[CUICategory]
    sap_type: Optional[SAPType]
    declassification_date: Optional[datetime]
    dissemination_controls: List[str]
    portion_markings: Dict[str, str]


@dataclass
class ClassificationDecision:
    """Automated classification decision"""
    document_id: str
    recommended_level: ClassificationLevel
    confidence: float
    rationale: str
    cui_categories: List[CUICategory]
    requires_human_review: bool


class AutomatedClassificationEngine:
    """Automated Classification Marking Engine - Part 1"""
    
    def __init__(self):
        self.classification_patterns = self._load_classification_patterns()
        self.cui_patterns = self._load_cui_patterns()
        self.decisions: List[ClassificationDecision] = []
    
    def classify_document(self, document_id: str, content: str) -> ClassificationDecision:
        """Automatically classify document based on content"""
        print(f"🔍 Classifying document: {document_id}")
        
        # Detect classification indicators
        detected_level = self._detect_classification_level(content)
        
        # Detect CUI categories
        cui_categories = self._detect_cui_categories(content)
        
        # Calculate confidence
        confidence = self._calculate_confidence(content, detected_level)
        
        # Determine if human review required
        requires_review = confidence < 0.85 or detected_level in [
            ClassificationLevel.TOP_SECRET,
            ClassificationLevel.TOP_SECRET_SCI
        ]
        
        decision = ClassificationDecision(
            document_id=document_id,
            recommended_level=detected_level,
            confidence=confidence,
            rationale=self._generate_rationale(detected_level, cui_categories),
            cui_categories=cui_categories,
            requires_human_review=requires_review
        )
        
        self.decisions.append(decision)
        return decision
    
    def apply_banner_markings(self, level: ClassificationLevel, 
                             cui_categories: List[CUICategory] = None,
                             sap_type: Optional[SAPType] = None) -> str:
        """Generate banner marking per ICD 710"""
        
        # Base classification
        marking = level.value
        
        # Add SAP marking if applicable
        if sap_type:
            marking += f"//{sap_type.value}"
        
        # Add CUI categories if applicable
        if cui_categories:
            cui_str = "//CUI//" + "//".join([c.name for c in cui_categories])
            marking += cui_str
        
        return marking
    
    def apply_portion_markings(self, content: str, level: ClassificationLevel) -> str:
        """Apply portion markings to paragraphs"""
        
        # Get portion marking abbreviation
        portion_mark = self._get_portion_marking(level)
        
        # Apply to each paragraph
        lines = content.split('\n')
        marked_lines = []
        
        for line in lines:
            if line.strip():
                marked_lines.append(f"({portion_mark}) {line}")
            else:
                marked_lines.append(line)
        
        return '\n'.join(marked_lines)
    
    def _load_classification_patterns(self) -> Dict[ClassificationLevel, List[str]]:
        """Load classification detection patterns"""
        return {
            ClassificationLevel.TOP_SECRET: [
                r'exceptionally grave damage',
                r'war plans',
                r'intelligence sources and methods',
                r'cryptologic',
                r'special intelligence',
                r'top secret compartmented information'
            ],
            ClassificationLevel.SECRET: [
                r'serious damage to national security',
                r'military operations',
                r'foreign government information',
                r'vulnerabilities or capabilities of systems'
            ],
            ClassificationLevel.CONFIDENTIAL: [
                r'damage to national security',
                r'confidential source',
                r'proprietary information'
            ],
            ClassificationLevel.CUI: [
                r'for official use only',
                r'law enforcement sensitive',
                r'export controlled',
                r'critical infrastructure'
            ]
        }
    
    def _load_cui_patterns(self) -> Dict[CUICategory, List[str]]:
        """Load CUI category detection patterns"""
        return {
            CUICategory.PRVCY: [
                r'social security number',
                r'personally identifiable information',
                r'pii',
                r'date of birth',
                r'medical record'
            ],
            CUICategory.CTI: [
                r'technical data',
                r'engineering drawings',
                r'research and development',
                r'technical specifications'
            ],
            CUICategory.ITAR: [
                r'defense articles',
                r'munitions list',
                r'military equipment',
                r'arms export'
            ],
            CUICategory.CRITICAL_INFRASTRUCTURE: [
                r'scada',
                r'industrial control system',
                r'power grid',
                r'critical infrastructure'
            ]
        }
    
    def _detect_classification_level(self, content: str) -> ClassificationLevel:
        """Detect classification level from content"""
        content_lower = content.lower()
        
        # Check for TOP SECRET indicators
        for pattern in self.classification_patterns[ClassificationLevel.TOP_SECRET]:
            if re.search(pattern, content_lower):
                return ClassificationLevel.TOP_SECRET
        
        # Check for SECRET indicators
        for pattern in self.classification_patterns[ClassificationLevel.SECRET]:
            if re.search(pattern, content_lower):
                return ClassificationLevel.SECRET
        
        # Check for CONFIDENTIAL indicators
        for pattern in self.classification_patterns[ClassificationLevel.CONFIDENTIAL]:
            if re.search(pattern, content_lower):
                return ClassificationLevel.CONFIDENTIAL
        
        # Check for CUI indicators
        for pattern in self.classification_patterns[ClassificationLevel.CUI]:
            if re.search(pattern, content_lower):
                return ClassificationLevel.CUI
        
        return ClassificationLevel.UNCLASSIFIED
    
    def _detect_cui_categories(self, content: str) -> List[CUICategory]:
        """Detect CUI categories in content"""
        content_lower = content.lower()
        detected_categories = []
        
        for category, patterns in self.cui_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    detected_categories.append(category)
                    break
        
        return detected_categories
    
    def _calculate_confidence(self, content: str, level: ClassificationLevel) -> float:
        """Calculate confidence in classification decision"""
        content_lower = content.lower()
        
        # Count matching patterns
        pattern_matches = 0
        total_patterns = len(self.classification_patterns.get(level, []))
        
        if total_patterns > 0:
            for pattern in self.classification_patterns[level]:
                if re.search(pattern, content_lower):
                    pattern_matches += 1
            
            # Base confidence on pattern match ratio
            confidence = min(0.6 + (pattern_matches / total_patterns) * 0.4, 1.0)
        else:
            confidence = 0.5
        
        return confidence
    
    def _generate_rationale(self, level: ClassificationLevel, 
                           cui_categories: List[CUICategory]) -> str:
        """Generate human-readable rationale"""
        if level == ClassificationLevel.UNCLASSIFIED:
            return "No classified or CUI indicators detected"
        
        rationale = f"Classified as {level.value} based on detected indicators. "
        
        if cui_categories:
            cats_str = ", ".join([c.value for c in cui_categories])
            rationale += f"CUI categories detected: {cats_str}."
        
        return rationale
    
    def _get_portion_marking(self, level: ClassificationLevel) -> str:
        """Get portion marking abbreviation"""
        marking_map = {
            ClassificationLevel.UNCLASSIFIED: "U",
            ClassificationLevel.CUI: "CUI",
            ClassificationLevel.CONFIDENTIAL: "C",
            ClassificationLevel.SECRET: "S",
            ClassificationLevel.TOP_SECRET: "TS",
            ClassificationLevel.TOP_SECRET_SCI: "TS//SCI"
        }
        return marking_map.get(level, "U")


def main():
    """Test classification engine"""
    engine = AutomatedClassificationEngine()
    
    # Test document
    test_content = """
    This document contains information about military operations
    that could cause serious damage to national security if disclosed.
    """
    
    decision = engine.classify_document("DOC-001", test_content)
    print(f"Classification: {decision.recommended_level.value}")
    print(f"Confidence: {decision.confidence:.1%}")
    print(f"Human Review: {decision.requires_human_review}")
    
    # Test banner marking
    banner = engine.apply_banner_markings(
        ClassificationLevel.SECRET,
        cui_categories=[CUICategory.CTI]
    )
    print(f"Banner Marking: {banner}")


if __name__ == "__main__":
    main()
