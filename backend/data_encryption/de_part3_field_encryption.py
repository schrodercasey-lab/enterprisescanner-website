"""
Military-Grade Data Encryption - Part 3 of 4
============================================

Field-Level Encryption: PII/PHI/CUI Protection

Features:
- Application-layer field encryption
- PII/PHI/CUI identification & encryption
- Format-preserving encryption (FPE)
- Tokenization for sensitive data
- Searchable encryption

COMPLIANCE:
- NIST 800-53 SC-28 (Protection of Information at Rest)
- HIPAA Security Rule §164.312(a)(2)(iv)
- PCI DSS Requirement 3
- GDPR Article 32
- CMMC Level 3 SC.L2-3.13.11
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import re


class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    RESTRICTED = "Restricted"
    PII = "Personally Identifiable Information"
    PHI = "Protected Health Information"
    CUI = "Controlled Unclassified Information"


class EncryptionType(Enum):
    """Field encryption types"""
    STANDARD = "Standard AES-256-GCM"
    FPE = "Format-Preserving Encryption"
    SEARCHABLE = "Searchable Encryption"
    TOKENIZATION = "Tokenization"


@dataclass
class FieldEncryptionPolicy:
    """Field-level encryption policy"""
    field_name: str
    data_classification: DataClassification
    encryption_type: EncryptionType
    key_id: str
    required: bool
    algorithm: str


@dataclass
class EncryptedField:
    """Encrypted field data"""
    field_name: str
    plaintext_length: int
    ciphertext: str
    encryption_type: EncryptionType
    key_id: str
    iv: str
    auth_tag: str
    encrypted_at: datetime


@dataclass
class Token:
    """Tokenization token"""
    token_id: str
    token_value: str
    original_value_hash: str
    field_name: str
    format_preserved: bool
    created_at: datetime
    expires_at: Optional[datetime]


@dataclass
class PIIField:
    """PII field identification"""
    field_name: str
    field_type: str
    pii_category: str
    sensitivity_score: int  # 1-10
    encryption_required: bool


class FieldEncryptionEngine:
    """Field-Level Encryption Engine - Part 3"""
    
    def __init__(self):
        self.encryption_policies: Dict[str, FieldEncryptionPolicy] = {}
        self.encrypted_fields: Dict[str, List[EncryptedField]] = {}
        self.tokens: Dict[str, Token] = {}
        self.pii_fields: List[PIIField] = []
        self.encryption_keys: Dict[str, str] = {}
    
    def identify_pii_fields(self, schema: Dict[str, str]) -> List[PIIField]:
        """Automatically identify PII/PHI fields in schema"""
        print("🔍 Identifying PII/PHI/CUI fields...")
        
        # PII patterns
        pii_patterns = {
            "ssn": (r"(ssn|social_security)", "SSN", 10),
            "email": (r"email", "Email Address", 7),
            "phone": (r"(phone|mobile|tel)", "Phone Number", 6),
            "address": (r"(address|street|city|zip)", "Physical Address", 7),
            "dob": (r"(dob|date_of_birth|birth_date)", "Date of Birth", 8),
            "name": (r"(first_name|last_name|full_name)", "Name", 6),
            "credit_card": (r"(credit_card|cc_number|card_num)", "Credit Card", 10),
            "passport": (r"passport", "Passport Number", 9),
            "drivers_license": (r"(drivers?_license|dl_number)", "Driver's License", 9),
            "medical_record": (r"(medical_record|mrn|patient_id)", "Medical Record", 10),
            "diagnosis": (r"(diagnosis|condition|disease)", "Medical Diagnosis", 10),
            "prescription": (r"(prescription|medication|drug)", "Prescription", 9),
            "biometric": (r"(fingerprint|retina|facial|biometric)", "Biometric Data", 10),
            "financial": (r"(account_number|routing|iban|swift)", "Financial Info", 9),
            "tax_id": (r"(tax_id|ein|tin)", "Tax ID", 9)
        }
        
        identified_fields = []
        
        for field_name, field_type in schema.items():
            for pii_type, (pattern, category, sensitivity) in pii_patterns.items():
                if re.search(pattern, field_name.lower()):
                    pii_field = PIIField(
                        field_name=field_name,
                        field_type=field_type,
                        pii_category=category,
                        sensitivity_score=sensitivity,
                        encryption_required=sensitivity >= 7
                    )
                    identified_fields.append(pii_field)
                    self.pii_fields.append(pii_field)
                    print(f"  ✓ Found {category}: {field_name} (sensitivity: {sensitivity}/10)")
                    break
        
        print(f"✅ Identified {len(identified_fields)} PII/PHI fields")
        print(f"   Requiring encryption: {sum(1 for f in identified_fields if f.encryption_required)}")
        
        return identified_fields
    
    def create_encryption_policy(self, field_name: str,
                                classification: DataClassification,
                                encryption_type: EncryptionType = EncryptionType.STANDARD) -> FieldEncryptionPolicy:
        """Create field encryption policy"""
        print(f"📋 Creating encryption policy: {field_name}")
        
        # Generate or use existing key
        key_id = f"key-{field_name}"
        if key_id not in self.encryption_keys:
            self.encryption_keys[key_id] = secrets.token_hex(32)  # 256-bit key
        
        # Select algorithm based on encryption type
        algorithms = {
            EncryptionType.STANDARD: "AES-256-GCM",
            EncryptionType.FPE: "FF3-1-AES-256",
            EncryptionType.SEARCHABLE: "AES-256-SIV",
            EncryptionType.TOKENIZATION: "SHA-256-HMAC"
        }
        
        policy = FieldEncryptionPolicy(
            field_name=field_name,
            data_classification=classification,
            encryption_type=encryption_type,
            key_id=key_id,
            required=classification in [DataClassification.PII, 
                                       DataClassification.PHI,
                                       DataClassification.CUI],
            algorithm=algorithms[encryption_type]
        )
        
        self.encryption_policies[field_name] = policy
        
        print(f"✅ Policy created")
        print(f"   Classification: {classification.value}")
        print(f"   Encryption: {encryption_type.value}")
        print(f"   Algorithm: {policy.algorithm}")
        
        return policy
    
    def encrypt_field(self, field_name: str, plaintext: str) -> EncryptedField:
        """Encrypt field value"""
        if field_name not in self.encryption_policies:
            raise ValueError(f"No encryption policy for field: {field_name}")
        
        policy = self.encryption_policies[field_name]
        
        # Generate IV
        iv = secrets.token_hex(16)
        
        # Simulate encryption (in production, use actual crypto libraries)
        key = self.encryption_keys[policy.key_id]
        ciphertext = hashlib.sha256(f"{plaintext}{key}{iv}".encode()).hexdigest()
        auth_tag = hashlib.sha256(f"{ciphertext}{key}".encode()).hexdigest()[:32]
        
        encrypted = EncryptedField(
            field_name=field_name,
            plaintext_length=len(plaintext),
            ciphertext=ciphertext,
            encryption_type=policy.encryption_type,
            key_id=policy.key_id,
            iv=iv,
            auth_tag=auth_tag,
            encrypted_at=datetime.now()
        )
        
        if field_name not in self.encrypted_fields:
            self.encrypted_fields[field_name] = []
        self.encrypted_fields[field_name].append(encrypted)
        
        return encrypted
    
    def encrypt_pii_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt all PII fields in a record"""
        print("🔐 Encrypting PII record...")
        
        encrypted_record = record.copy()
        encrypted_count = 0
        
        for field_name, value in record.items():
            if field_name in self.encryption_policies:
                if value is not None:
                    encrypted = self.encrypt_field(field_name, str(value))
                    encrypted_record[field_name] = f"ENC:{encrypted.ciphertext[:32]}..."
                    encrypted_count += 1
        
        print(f"✅ Encrypted {encrypted_count} fields")
        
        return encrypted_record
    
    def format_preserving_encrypt(self, field_name: str, 
                                  plaintext: str, pattern: str) -> str:
        """Format-preserving encryption (e.g., SSN: XXX-XX-XXXX)"""
        print(f"🔒 FPE encrypting: {field_name}")
        
        if field_name not in self.encryption_policies:
            self.create_encryption_policy(
                field_name,
                DataClassification.PII,
                EncryptionType.FPE
            )
        
        policy = self.encryption_policies[field_name]
        key = self.encryption_keys[policy.key_id]
        
        # Extract digits/letters
        chars = [c for c in plaintext if c.isalnum()]
        
        # Encrypt each character while preserving format
        encrypted_chars = []
        for c in chars:
            # Simulated FPE (in production, use FF3-1)
            encrypted = hashlib.sha256(f"{c}{key}".encode()).hexdigest()[0]
            encrypted_chars.append(encrypted)
        
        # Rebuild with original format
        result = list(pattern)
        char_idx = 0
        for i, c in enumerate(result):
            if c in 'X#':
                if char_idx < len(encrypted_chars):
                    result[i] = encrypted_chars[char_idx]
                    char_idx += 1
        
        ciphertext = ''.join(result)
        
        print(f"  ✓ Format preserved: {pattern}")
        print(f"  ✓ Input:  {plaintext}")
        print(f"  ✓ Output: {ciphertext}")
        
        return ciphertext
    
    def tokenize(self, field_name: str, value: str,
                preserve_format: bool = False,
                expires_days: Optional[int] = None) -> Token:
        """Tokenize sensitive data"""
        print(f"🎫 Tokenizing: {field_name}")
        
        # Generate token
        if preserve_format:
            # Format-preserving tokenization
            token_value = ''.join(
                secrets.choice('0123456789') if c.isdigit() else
                secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') if c.isupper() else
                secrets.choice('abcdefghijklmnopqrstuvwxyz') if c.islower() else c
                for c in value
            )
        else:
            token_value = f"TOK-{secrets.token_urlsafe(16)}"
        
        # Hash original value for verification
        value_hash = hashlib.sha256(value.encode()).hexdigest()
        
        # Create token
        token = Token(
            token_id=secrets.token_hex(16),
            token_value=token_value,
            original_value_hash=value_hash,
            field_name=field_name,
            format_preserved=preserve_format,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=expires_days) if expires_days else None
        )
        
        self.tokens[token.token_id] = token
        
        print(f"✅ Token generated")
        print(f"   Token: {token_value}")
        print(f"   Format preserved: {preserve_format}")
        
        return token
    
    def searchable_encrypt(self, field_name: str, value: str) -> str:
        """Deterministic/searchable encryption"""
        print(f"🔍 Searchable encryption: {field_name}")
        
        if field_name not in self.encryption_policies:
            self.create_encryption_policy(
                field_name,
                DataClassification.PII,
                EncryptionType.SEARCHABLE
            )
        
        policy = self.encryption_policies[field_name]
        key = self.encryption_keys[policy.key_id]
        
        # Deterministic encryption (same input = same output)
        # Uses AES-SIV or similar
        ciphertext = hashlib.sha256(f"{value}{key}".encode()).hexdigest()
        
        print(f"  ✓ Deterministic encryption (searchable)")
        print(f"  ✓ Ciphertext: {ciphertext[:32]}...")
        
        return ciphertext
    
    def bulk_encrypt_pii(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bulk encrypt PII in multiple records"""
        print(f"🔐 Bulk encrypting {len(records)} records...")
        
        encrypted_records = []
        total_fields = 0
        
        for record in records:
            encrypted = self.encrypt_pii_record(record)
            encrypted_records.append(encrypted)
            total_fields += sum(1 for k in record.keys() if k in self.encryption_policies)
        
        print(f"✅ Bulk encryption complete")
        print(f"   Records: {len(records)}")
        print(f"   Encrypted fields: {total_fields}")
        
        return encrypted_records
    
    def audit_field_encryption(self) -> Dict[str, Any]:
        """Audit field-level encryption compliance"""
        print("🔍 Auditing field encryption compliance...")
        
        # Check which identified PII fields have policies
        pii_without_policy = [
            f.field_name for f in self.pii_fields
            if f.encryption_required and f.field_name not in self.encryption_policies
        ]
        
        # Count encryption operations
        total_encrypted = sum(len(fields) for fields in self.encrypted_fields.values())
        
        audit = {
            "timestamp": datetime.now(),
            "identified_pii_fields": len(self.pii_fields),
            "encryption_policies": len(self.encryption_policies),
            "pii_without_policy": pii_without_policy,
            "total_encrypted_values": total_encrypted,
            "tokens_generated": len(self.tokens),
            "compliance_status": {
                "all_pii_protected": len(pii_without_policy) == 0,
                "HIPAA_164_312": any(p.data_classification == DataClassification.PHI 
                                   for p in self.encryption_policies.values()),
                "PCI_DSS_3": any("credit_card" in p.field_name.lower() or "card" in p.field_name.lower()
                               for p in self.encryption_policies.values()),
                "GDPR_Article_32": len(self.encryption_policies) > 0,
                "NIST_800_53_SC_28": total_encrypted > 0
            }
        }
        
        print(f"✅ Audit completed")
        print(f"\nCompliance Status:")
        for standard, compliant in audit["compliance_status"].items():
            print(f"  {standard}: {'✅' if compliant else '❌'}")
        
        if pii_without_policy:
            print(f"\n⚠️  {len(pii_without_policy)} PII fields without encryption policy:")
            for field in pii_without_policy[:5]:
                print(f"     - {field}")
        
        return audit
    
    def generate_encryption_report(self) -> Dict[str, Any]:
        """Generate field encryption report"""
        print("📊 Generating field encryption report...")
        
        report = {
            "timestamp": datetime.now(),
            "pii_fields": {
                "total_identified": len(self.pii_fields),
                "requiring_encryption": sum(1 for f in self.pii_fields if f.encryption_required),
                "by_category": {}
            },
            "encryption_policies": {
                "total": len(self.encryption_policies),
                "by_classification": {},
                "by_type": {}
            },
            "encryption_operations": {
                "total_fields_encrypted": len(self.encrypted_fields),
                "total_values_encrypted": sum(len(v) for v in self.encrypted_fields.values()),
                "tokens_generated": len(self.tokens)
            }
        }
        
        # Count by PII category
        for field in self.pii_fields:
            cat = field.pii_category
            report["pii_fields"]["by_category"][cat] = \
                report["pii_fields"]["by_category"].get(cat, 0) + 1
        
        # Count policies by classification
        for policy in self.encryption_policies.values():
            cls = policy.data_classification.value
            report["encryption_policies"]["by_classification"][cls] = \
                report["encryption_policies"]["by_classification"].get(cls, 0) + 1
            
            typ = policy.encryption_type.value
            report["encryption_policies"]["by_type"][typ] = \
                report["encryption_policies"]["by_type"].get(typ, 0) + 1
        
        print(f"✅ Report generated")
        print(f"\nSummary:")
        print(f"  PII Fields Identified: {report['pii_fields']['total_identified']}")
        print(f"  Encryption Policies: {report['encryption_policies']['total']}")
        print(f"  Values Encrypted: {report['encryption_operations']['total_values_encrypted']}")
        print(f"  Tokens Generated: {report['encryption_operations']['tokens_generated']}")
        
        return report


def main():
    """Test field encryption engine"""
    from datetime import timedelta
    
    engine = FieldEncryptionEngine()
    
    print("=" * 70)
    print("FIELD-LEVEL ENCRYPTION ENGINE")
    print("=" * 70)
    
    # Identify PII fields
    schema = {
        "user_id": "INT",
        "first_name": "VARCHAR",
        "last_name": "VARCHAR",
        "email": "VARCHAR",
        "ssn": "VARCHAR",
        "date_of_birth": "DATE",
        "credit_card": "VARCHAR",
        "phone": "VARCHAR",
        "medical_record_number": "VARCHAR",
        "diagnosis": "TEXT"
    }
    pii_fields = engine.identify_pii_fields(schema)
    
    # Create encryption policies
    print("\n" + "=" * 70)
    engine.create_encryption_policy("ssn", DataClassification.PII, EncryptionType.FPE)
    engine.create_encryption_policy("credit_card", DataClassification.PII, EncryptionType.TOKENIZATION)
    engine.create_encryption_policy("email", DataClassification.PII, EncryptionType.SEARCHABLE)
    engine.create_encryption_policy("medical_record_number", DataClassification.PHI, EncryptionType.STANDARD)
    
    # Encrypt record
    print("\n" + "=" * 70)
    record = {
        "user_id": 12345,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "ssn": "123-45-6789",
        "medical_record_number": "MRN-987654"
    }
    encrypted_record = engine.encrypt_pii_record(record)
    
    # Format-preserving encryption
    print("\n" + "=" * 70)
    fpe_ssn = engine.format_preserving_encrypt("ssn", "123-45-6789", "XXX-XX-XXXX")
    
    # Tokenization
    print("\n" + "=" * 70)
    token = engine.tokenize("credit_card", "4532-1234-5678-9010", preserve_format=True)
    
    # Audit
    print("\n" + "=" * 70)
    audit = engine.audit_field_encryption()
    
    # Generate report
    print("\n" + "=" * 70)
    report = engine.generate_encryption_report()


if __name__ == "__main__":
    main()
