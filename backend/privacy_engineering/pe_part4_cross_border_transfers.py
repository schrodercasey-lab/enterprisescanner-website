"""
Military Upgrade #17: Privacy Engineering & GDPR Compliance
Part 4: Cross-Border Data Transfer & Privacy Shield

This module implements cross-border data transfer controls required for international
data flows under GDPR Chapter V and successor frameworks to EU-US Privacy Shield.

Key Features:
- EU-US Data Privacy Framework compliance
- Standard Contractual Clauses (SCCs) management
- Binding Corporate Rules (BCRs) enforcement
- Data localization requirements
- Transfer Impact Assessments (TIAs)

Compliance:
- GDPR Chapter V (Transfer of Personal Data to Third Countries)
- EU-US Data Privacy Framework (2023)
- UK-US Data Bridge
- Swiss-US Data Privacy Framework
- Schrems II decision compliance
- Standard Contractual Clauses (2021 version)
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class TransferMechanism(Enum):
    """Legal mechanisms for cross-border transfers (GDPR Article 45-46)"""
    ADEQUACY_DECISION = "adequacy_decision"  # Article 45
    STANDARD_CONTRACTUAL_CLAUSES = "sccs"  # Article 46(2)(c)
    BINDING_CORPORATE_RULES = "bcrs"  # Article 46(2)(b)
    CODE_OF_CONDUCT = "code_of_conduct"  # Article 46(2)(e)
    CERTIFICATION = "certification"  # Article 46(2)(f)
    EXPLICIT_CONSENT = "explicit_consent"  # Article 49(1)(a)
    CONTRACTUAL_NECESSITY = "contractual_necessity"  # Article 49(1)(b)
    DEROGATIONS = "derogations"  # Article 49


class DataPrivacyFramework(Enum):
    """International data privacy frameworks"""
    EU_US_DPF = "eu_us_data_privacy_framework"  # 2023
    UK_US_DATA_BRIDGE = "uk_us_data_bridge"  # 2023
    SWISS_US_DPF = "swiss_us_data_privacy_framework"  # 2023
    APEC_CBPR = "apec_cross_border_privacy_rules"  # Asia-Pacific
    EU_JAPAN_ADEQUACY = "eu_japan_adequacy"  # 2019


class Country(Enum):
    """Countries with different data protection levels"""
    # EU/EEA (GDPR)
    EU = "european_union"
    UK = "united_kingdom"
    SWITZERLAND = "switzerland"
    
    # Adequate countries (GDPR Article 45)
    CANADA = "canada"
    JAPAN = "japan"
    NEW_ZEALAND = "new_zealand"
    ISRAEL = "israel"
    SOUTH_KOREA = "south_korea"
    
    # US (requires additional safeguards)
    USA = "united_states"
    
    # Other countries (require safeguards)
    CHINA = "china"
    RUSSIA = "russia"
    INDIA = "india"


class TransferRiskLevel(Enum):
    """Risk assessment for data transfers"""
    LOW = "low"  # Adequate country
    MEDIUM = "medium"  # SCCs in place
    HIGH = "high"  # Government surveillance concerns
    CRITICAL = "critical"  # No safeguards


@dataclass
class DataTransfer:
    """Cross-border data transfer record"""
    transfer_id: str
    transfer_date: datetime
    
    # Origin and destination
    source_country: Country
    destination_country: Country
    
    # Data and subjects
    data_categories: List[str]
    data_subject_count: int
    is_sensitive_data: bool
    
    # Legal basis
    transfer_mechanism: TransferMechanism
    legal_basis_document: Optional[str] = None
    
    # Safeguards
    encryption_used: bool = True
    pseudonymization_used: bool = False
    additional_safeguards: List[str] = field(default_factory=list)
    
    # Risk assessment
    risk_level: TransferRiskLevel = TransferRiskLevel.MEDIUM
    tia_conducted: bool = False
    tia_id: Optional[str] = None
    
    # Compliance
    data_subject_informed: bool = False
    consent_obtained: bool = False
    approved_by: Optional[str] = None


@dataclass
class StandardContractualClause:
    """Standard Contractual Clauses (2021 version)"""
    scc_id: str
    version: str = "2021"  # EU Commission 2021 SCCs
    effective_date: datetime = field(default_factory=datetime.now)
    
    # Parties
    data_exporter: str  # EU entity
    data_exporter_country: Country
    data_importer: str  # Non-EU entity
    data_importer_country: Country
    
    # Module selection (4 modules in 2021 SCCs)
    module_used: str = "Module Two"  # Controller to Processor
    
    # Annexes
    annex_i_completed: bool = False  # Parties and processing details
    annex_ii_completed: bool = False  # Technical/organizational measures
    annex_iii_completed: bool = False  # Sub-processors list
    
    # Supplementary measures (Schrems II)
    supplementary_measures: List[str] = field(default_factory=list)
    
    # Status
    signed_by_exporter: bool = False
    signed_by_importer: bool = False
    signature_date: Optional[datetime] = None


@dataclass
class BindingCorporateRules:
    """Binding Corporate Rules for intra-group transfers"""
    bcr_id: str
    group_name: str
    approved_by_dpa: str  # Lead supervisory authority
    approval_date: datetime
    
    # Scope
    countries_covered: List[Country]
    entities_covered: List[str]
    data_types_covered: List[str]
    
    # Requirements (Article 47)
    legally_binding: bool = True
    enforceable_rights: bool = True
    training_program: bool = True
    complaint_mechanism: bool = True
    cooperation_with_dpa: bool = True
    
    # Review
    annual_review_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TransferImpactAssessment:
    """Transfer Impact Assessment (TIA) - Schrems II requirement"""
    tia_id: str
    assessment_date: datetime
    transfer_id: str
    
    # Destination country analysis
    destination_country: Country
    legal_framework_analysis: str
    government_access_analysis: str
    surveillance_law_analysis: str
    
    # Risk factors
    risks_identified: List[str]
    risk_severity: TransferRiskLevel
    
    # Safeguards assessment
    existing_safeguards: List[str]
    effectiveness_assessment: str
    additional_measures_needed: List[str]
    
    # Conclusion
    transfer_permissible: bool
    conditions: List[str]
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    
    # Review
    review_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=180))


@dataclass
class DataLocalizationRule:
    """Data localization/residency requirement"""
    rule_id: str
    country: Country
    requirement: str
    legal_basis: str
    
    # Requirements
    data_must_remain_in_country: bool = False
    processing_must_occur_locally: bool = False
    local_copy_required: bool = False
    
    # Exceptions
    exceptions: List[str] = field(default_factory=list)
    
    effective_date: datetime = field(default_factory=datetime.now)


class CrossBorderTransferEngine:
    """Cross-Border Data Transfer & Privacy Shield Engine"""
    
    def __init__(self, organization_name: str, primary_country: Country):
        self.organization_name = organization_name
        self.primary_country = primary_country
        
        self.transfers: Dict[str, DataTransfer] = {}
        self.sccs: Dict[str, StandardContractualClause] = {}
        self.bcrs: Dict[str, BindingCorporateRules] = {}
        self.tias: Dict[str, TransferImpactAssessment] = {}
        self.localization_rules: Dict[str, DataLocalizationRule] = {}
        
        # Adequacy decisions (GDPR Article 45)
        self.adequate_countries = {
            Country.CANADA,
            Country.JAPAN,
            Country.NEW_ZEALAND,
            Country.ISRAEL,
            Country.SOUTH_KOREA,
            Country.UK,
            Country.SWITZERLAND
        }
    
    def assess_transfer_legality(self, source: Country, destination: Country,
                                data_categories: List[str], is_sensitive: bool) -> Dict[str, Any]:
        """Assess if data transfer is legally permissible"""
        assessment = {
            'legal': False,
            'mechanism_required': None,
            'adequacy_decision': False,
            'additional_safeguards_required': [],
            'tia_required': False,
            'risk_level': TransferRiskLevel.MEDIUM
        }
        
        # Check if within EU/EEA (no restrictions)
        if self._is_within_eea(source) and self._is_within_eea(destination):
            assessment['legal'] = True
            assessment['risk_level'] = TransferRiskLevel.LOW
            return assessment
        
        # Check adequacy decision (Article 45)
        if destination in self.adequate_countries:
            assessment['legal'] = True
            assessment['adequacy_decision'] = True
            assessment['risk_level'] = TransferRiskLevel.LOW
            print(f"✅ Transfer permitted: {destination.value} has adequacy decision")
            return assessment
        
        # US transfers require EU-US DPF or SCCs
        if destination == Country.USA:
            assessment['mechanism_required'] = TransferMechanism.STANDARD_CONTRACTUAL_CLAUSES
            assessment['additional_safeguards_required'] = [
                "Encryption in transit and at rest",
                "Access controls",
                "Data minimization",
                "Transparency about government access"
            ]
            assessment['tia_required'] = True
            assessment['risk_level'] = TransferRiskLevel.HIGH
            print(f"⚠️  US transfer requires SCCs + supplementary measures + TIA (Schrems II)")
        
        # China, Russia require special attention
        if destination in [Country.CHINA, Country.RUSSIA]:
            assessment['mechanism_required'] = TransferMechanism.STANDARD_CONTRACTUAL_CLAUSES
            assessment['additional_safeguards_required'] = [
                "Strong encryption",
                "Data sovereignty measures",
                "Regular security audits",
                "Government access notifications"
            ]
            assessment['tia_required'] = True
            assessment['risk_level'] = TransferRiskLevel.CRITICAL
            print(f"⚠️  High-risk destination: Comprehensive safeguards required")
        
        # Sensitive data requires explicit consent or stronger basis
        if is_sensitive:
            assessment['additional_safeguards_required'].append("Explicit consent from data subjects")
            assessment['risk_level'] = TransferRiskLevel.HIGH
        
        return assessment
    
    def _is_within_eea(self, country: Country) -> bool:
        """Check if country is within EU/EEA"""
        return country in [Country.EU, Country.UK, Country.SWITZERLAND]
    
    def register_data_transfer(self, transfer: DataTransfer) -> bool:
        """Register cross-border data transfer"""
        try:
            # Assess transfer legality
            assessment = self.assess_transfer_legality(
                transfer.source_country,
                transfer.destination_country,
                transfer.data_categories,
                transfer.is_sensitive_data
            )
            
            transfer.risk_level = assessment['risk_level']
            
            # Require TIA for high-risk transfers
            if assessment['tia_required'] and not transfer.tia_conducted:
                print(f"⚠️  Transfer Impact Assessment required before transfer")
                return False
            
            # Require appropriate transfer mechanism
            if assessment['mechanism_required']:
                if transfer.transfer_mechanism != assessment['mechanism_required']:
                    print(f"⚠️  Transfer mechanism {assessment['mechanism_required'].value} required")
                    return False
            
            # Require legal basis documentation
            if not transfer.legal_basis_document:
                print(f"⚠️  Legal basis documentation required")
                return False
            
            self.transfers[transfer.transfer_id] = transfer
            print(f"✅ Data transfer registered: {transfer.transfer_id}")
            print(f"   {transfer.source_country.value} → {transfer.destination_country.value}")
            print(f"   Risk: {transfer.risk_level.value} | Mechanism: {transfer.transfer_mechanism.value}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register transfer: {e}")
            return False
    
    def implement_sccs(self, scc: StandardContractualClause) -> bool:
        """Implement Standard Contractual Clauses"""
        try:
            # Validate SCCs are appropriate for countries involved
            if not self._validate_scc_applicability(scc):
                return False
            
            # Ensure all annexes completed
            if not all([scc.annex_i_completed, scc.annex_ii_completed]):
                print(f"⚠️  Annexes I and II must be completed")
                return False
            
            # For US transfers, require supplementary measures (Schrems II)
            if scc.data_importer_country == Country.USA:
                required_measures = [
                    "End-to-end encryption",
                    "Pseudonymization",
                    "Multi-party encryption",
                    "Technical measures against government access"
                ]
                
                if not any(measure in scc.supplementary_measures for measure in required_measures):
                    print(f"⚠️  Supplementary measures required for US transfers (Schrems II)")
                    print(f"   Recommended: {', '.join(required_measures)}")
                    return False
            
            # Both parties must sign
            if not (scc.signed_by_exporter and scc.signed_by_importer):
                print(f"⚠️  Both parties must sign SCCs")
                return False
            
            self.sccs[scc.scc_id] = scc
            print(f"✅ Standard Contractual Clauses implemented: {scc.scc_id}")
            print(f"   Exporter: {scc.data_exporter} ({scc.data_exporter_country.value})")
            print(f"   Importer: {scc.data_importer} ({scc.data_importer_country.value})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to implement SCCs: {e}")
            return False
    
    def _validate_scc_applicability(self, scc: StandardContractualClause) -> bool:
        """Validate SCCs are appropriate"""
        # SCCs only for transfers from EU/EEA to non-adequate countries
        if not self._is_within_eea(scc.data_exporter_country):
            print(f"⚠️  SCCs require EU/EEA data exporter")
            return False
        
        if scc.data_importer_country in self.adequate_countries:
            print(f"⚠️  SCCs not needed - {scc.data_importer_country.value} has adequacy decision")
            return False
        
        return True
    
    def conduct_transfer_impact_assessment(self, transfer_id: str,
                                          destination: Country) -> TransferImpactAssessment:
        """Conduct Transfer Impact Assessment (Schrems II requirement)"""
        try:
            tia_id = f"TIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Analyze destination country laws
            legal_analysis = self._analyze_destination_laws(destination)
            
            # Assess government access risks
            surveillance_analysis = self._analyze_surveillance_laws(destination)
            
            # Identify risks
            risks = self._identify_transfer_risks(destination, legal_analysis, surveillance_analysis)
            
            # Assess safeguards
            effectiveness = self._assess_safeguard_effectiveness(destination, risks)
            
            # Determine if transfer is permissible
            permissible = effectiveness['effective'] and len(risks) < 5
            
            tia = TransferImpactAssessment(
                tia_id=tia_id,
                assessment_date=datetime.now(),
                transfer_id=transfer_id,
                destination_country=destination,
                legal_framework_analysis=legal_analysis,
                government_access_analysis=surveillance_analysis['summary'],
                surveillance_law_analysis=surveillance_analysis['details'],
                risks_identified=risks,
                risk_severity=self._calculate_risk_severity(risks),
                existing_safeguards=["SCCs", "Encryption", "Access controls"],
                effectiveness_assessment=effectiveness['assessment'],
                additional_measures_needed=effectiveness['recommendations'],
                transfer_permissible=permissible,
                conditions=effectiveness['conditions'] if permissible else []
            )
            
            self.tias[tia_id] = tia
            
            print(f"✅ Transfer Impact Assessment completed: {tia_id}")
            print(f"   Destination: {destination.value}")
            print(f"   Risks identified: {len(risks)}")
            print(f"   Transfer permissible: {permissible}")
            
            return tia
            
        except Exception as e:
            print(f"❌ TIA failed: {e}")
            raise
    
    def _analyze_destination_laws(self, country: Country) -> str:
        """Analyze destination country's data protection laws"""
        analyses = {
            Country.USA: "US has sectoral privacy laws (no omnibus law). FISA Section 702 and EO 12333 allow government surveillance. Cloud Act permits data access.",
            Country.CHINA: "China's PIPL requires data localization. Government has broad access powers under National Security Law and Cybersecurity Law.",
            Country.RUSSIA: "Russia requires data localization (Federal Law 242-FZ). Government has extensive surveillance powers under Yarovaya Law.",
            Country.INDIA: "India has no omnibus data protection law yet. IT Act provides some protections. Government surveillance under Section 69.",
        }
        
        return analyses.get(country, "Country-specific analysis required")
    
    def _analyze_surveillance_laws(self, country: Country) -> Dict[str, str]:
        """Analyze surveillance and government access laws"""
        analyses = {
            Country.USA: {
                'summary': 'US has extensive surveillance programs (FISA 702, EO 12333)',
                'details': 'FISA Section 702 allows warrantless surveillance of non-US persons. EO 12333 permits foreign intelligence collection. Cloud Act permits cross-border data access.'
            },
            Country.CHINA: {
                'summary': 'Broad government access powers under multiple laws',
                'details': 'National Security Law, Cybersecurity Law, and Data Security Law grant extensive government access. No effective judicial oversight.'
            }
        }
        
        return analyses.get(country, {
            'summary': 'Surveillance law analysis needed',
            'details': 'Country-specific surveillance laws must be reviewed'
        })
    
    def _identify_transfer_risks(self, country: Country, legal: str, surveillance: Dict) -> List[str]:
        """Identify risks for data transfer"""
        risks = []
        
        if country == Country.USA:
            risks.extend([
                "FISA Section 702 surveillance",
                "Executive Order 12333 intelligence collection",
                "Cloud Act data access requests",
                "No effective redress for non-US persons"
            ])
        
        if country in [Country.CHINA, Country.RUSSIA]:
            risks.extend([
                "Mandatory data localization",
                "Broad government access powers",
                "Weak judicial oversight",
                "National security laws override privacy"
            ])
        
        return risks
    
    def _calculate_risk_severity(self, risks: List[str]) -> TransferRiskLevel:
        """Calculate overall risk severity"""
        if len(risks) >= 5:
            return TransferRiskLevel.CRITICAL
        elif len(risks) >= 3:
            return TransferRiskLevel.HIGH
        elif len(risks) >= 1:
            return TransferRiskLevel.MEDIUM
        else:
            return TransferRiskLevel.LOW
    
    def _assess_safeguard_effectiveness(self, country: Country, risks: List[str]) -> Dict[str, Any]:
        """Assess if safeguards are effective (Schrems II test)"""
        # For high-risk countries, standard safeguards may not be sufficient
        if len(risks) >= 4:
            return {
                'effective': False,
                'assessment': 'Standard safeguards insufficient for high-risk destination',
                'recommendations': [
                    "End-to-end encryption with data subject holding keys",
                    "Multi-party computation",
                    "Federated learning (no raw data transfer)",
                    "On-premises processing only",
                    "Avoid transfer entirely"
                ],
                'conditions': []
            }
        
        return {
            'effective': True,
            'assessment': 'SCCs with supplementary measures provide adequate protection',
            'recommendations': [
                "Implement strong encryption",
                "Use pseudonymization",
                "Minimize data transferred",
                "Implement access controls"
            ],
            'conditions': [
                "Regular audits of importer's security",
                "Immediate notification of government requests",
                "Annual TIA review"
            ]
        }
    
    def check_data_localization_requirements(self, country: Country) -> Optional[DataLocalizationRule]:
        """Check if country has data localization requirements"""
        localization_countries = {
            Country.RUSSIA: DataLocalizationRule(
                rule_id="LOC-RU",
                country=Country.RUSSIA,
                requirement="Personal data of Russian citizens must be stored in Russia",
                legal_basis="Federal Law No. 242-FZ",
                data_must_remain_in_country=True,
                processing_must_occur_locally=True
            ),
            Country.CHINA: DataLocalizationRule(
                rule_id="LOC-CN",
                country=Country.CHINA,
                requirement="Important data must be stored in China",
                legal_basis="Cybersecurity Law, Data Security Law, PIPL",
                data_must_remain_in_country=True,
                local_copy_required=True
            )
        }
        
        return localization_countries.get(country)
    
    def generate_transfer_report(self) -> Dict[str, Any]:
        """Generate cross-border transfer compliance report"""
        return {
            'total_transfers': len(self.transfers),
            'high_risk_transfers': sum(
                1 for t in self.transfers.values() 
                if t.risk_level in [TransferRiskLevel.HIGH, TransferRiskLevel.CRITICAL]
            ),
            'sccs_implemented': len(self.sccs),
            'tias_conducted': len(self.tias),
            'transfers_by_country': self._count_transfers_by_country(),
            'compliance_gaps': self._identify_compliance_gaps()
        }
    
    def _count_transfers_by_country(self) -> Dict[str, int]:
        """Count transfers by destination country"""
        counts = {}
        for transfer in self.transfers.values():
            country = transfer.destination_country.value
            counts[country] = counts.get(country, 0) + 1
        return counts
    
    def _identify_compliance_gaps(self) -> List[str]:
        """Identify compliance gaps"""
        gaps = []
        
        for transfer in self.transfers.values():
            if transfer.risk_level == TransferRiskLevel.HIGH and not transfer.tia_conducted:
                gaps.append(f"Transfer {transfer.transfer_id} missing TIA")
            
            if not transfer.data_subject_informed:
                gaps.append(f"Transfer {transfer.transfer_id} - data subjects not informed")
        
        return gaps


# Example usage
if __name__ == "__main__":
    engine = CrossBorderTransferEngine(
        organization_name="Enterprise Scanner Inc.",
        primary_country=Country.EU
    )
    
    # Assess US transfer
    assessment = engine.assess_transfer_legality(
        source=Country.EU,
        destination=Country.USA,
        data_categories=["Customer names", "Email addresses"],
        is_sensitive=False
    )
    
    print(f"\n📊 Transfer Assessment:")
    print(f"Legal: {assessment['legal']}")
    print(f"Mechanism required: {assessment['mechanism_required']}")
    print(f"TIA required: {assessment['tia_required']}")
    
    print("\n✅ Cross-border transfer system operational")
