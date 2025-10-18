"""
Military Upgrade #35: Forensics & E-Discovery - Part 2
E-Discovery & Legal Hold Management

This module provides enterprise e-discovery capabilities:
- Legal hold management
- Data preservation
- Document review and production
- Custodian management
- Search and collection
- Privilege review
- Production formatting
- Compliance reporting

Key Capabilities:
- Automated legal hold notifications
- Custodian acknowledgment tracking
- Data preservation across systems
- Keyword and concept search
- Document deduplication
- Metadata extraction and preservation
- Privilege log generation
- Production set management

Compliance:
- Federal Rules of Civil Procedure (FRCP)
- Electronic Discovery Reference Model (EDRM)
- ISO/IEC 27050 (E-Discovery)
- General Data Protection Regulation (GDPR)
- Sarbanes-Oxley Act (SOX)
- Health Insurance Portability (HIPAA)

Author: Enterprise Scanner Team
Version: 1.0.0 (October 17, 2025)
"""

import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class LegalHoldStatus(Enum):
    """Legal hold status"""
    DRAFT = "draft"
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"


class CustodianStatus(Enum):
    """Custodian acknowledgment status"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    DECLINED = "declined"
    ESCALATED = "escalated"


class DocumentStatus(Enum):
    """Document review status"""
    UNREVIEWED = "unreviewed"
    UNDER_REVIEW = "under_review"
    RELEVANT = "relevant"
    NOT_RELEVANT = "not_relevant"
    PRIVILEGED = "privileged"
    PRODUCED = "produced"


class ProductionFormat(Enum):
    """Production output formats"""
    NATIVE = "native"
    TIFF = "tiff"
    PDF = "pdf"
    CSV = "csv"
    LOAD_FILE = "load_file"


@dataclass
class LegalHold:
    """Legal hold notice"""
    hold_id: str
    hold_name: str
    
    # Legal details
    matter_name: str
    case_number: Optional[str] = None
    issuing_attorney: str = ""
    law_firm: Optional[str] = None
    
    # Scope
    description: str = ""
    scope_keywords: List[str] = field(default_factory=list)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    
    # Custodians
    custodians: List[str] = field(default_factory=list)
    
    # Status
    status: LegalHoldStatus = LegalHoldStatus.DRAFT
    issued_date: Optional[datetime] = None
    release_date: Optional[datetime] = None
    
    # Notifications
    reminder_frequency_days: int = 30
    last_reminder: Optional[datetime] = None
    
    # Systems to preserve
    systems: List[str] = field(default_factory=list)  # email, file_share, etc.


@dataclass
class Custodian:
    """Data custodian subject to legal hold"""
    custodian_id: str
    hold_id: str
    
    # Identity
    name: str
    email: str
    department: Optional[str] = None
    title: Optional[str] = None
    
    # Status
    status: CustodianStatus = CustodianStatus.PENDING
    notified_date: Optional[datetime] = None
    acknowledged_date: Optional[datetime] = None
    
    # Data locations
    email_accounts: List[str] = field(default_factory=list)
    file_locations: List[str] = field(default_factory=list)
    devices: List[str] = field(default_factory=list)
    
    # Notifications
    notifications_sent: int = 0
    last_notification: Optional[datetime] = None
    
    # Notes
    notes: str = ""


@dataclass
class Document:
    """Document in e-discovery collection"""
    document_id: str
    collection_id: str
    
    # Identification
    file_name: str
    file_path: str
    file_type: str
    file_size_bytes: int = 0
    
    # Hashes
    hash_md5: Optional[str] = None
    hash_sha256: Optional[str] = None
    
    # Metadata
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    custodian: Optional[str] = None
    
    # Content
    text_content: Optional[str] = None
    page_count: int = 0
    
    # Review
    status: DocumentStatus = DocumentStatus.UNREVIEWED
    reviewed_by: Optional[str] = None
    reviewed_date: Optional[datetime] = None
    
    # Coding
    tags: List[str] = field(default_factory=list)
    relevance_score: float = 0.0  # 0-100
    privilege: bool = False
    confidential: bool = False
    
    # Production
    produced: bool = False
    production_id: Optional[str] = None
    bates_number: Optional[str] = None  # Sequential numbering
    
    # Deduplication
    duplicate_of: Optional[str] = None
    duplicate_count: int = 0


@dataclass
class Collection:
    """E-discovery document collection"""
    collection_id: str
    hold_id: str
    collection_name: str
    
    # Scope
    custodians: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    
    # Execution
    collected_date: datetime = field(default_factory=datetime.now)
    collected_by: str = ""
    
    # Statistics
    total_documents: int = 0
    total_size_gb: float = 0.0
    duplicates_removed: int = 0
    
    # Status
    status: str = "in_progress"  # in_progress, completed, failed


@dataclass
class ProductionSet:
    """Document production set"""
    production_id: str
    production_name: str
    
    # Recipient
    recipient: str = ""
    recipient_email: Optional[str] = None
    
    # Documents
    document_ids: List[str] = field(default_factory=list)
    
    # Format
    format: ProductionFormat = ProductionFormat.PDF
    
    # Numbering
    bates_prefix: str = ""
    bates_start: int = 1
    
    # Status
    produced_date: Optional[datetime] = None
    produced_by: Optional[str] = None
    
    # Delivery
    delivery_method: str = "secure_transfer"
    delivered: bool = False


@dataclass
class PrivilegeLog:
    """Attorney-client privilege log"""
    log_id: str
    production_id: str
    
    # Document
    document_id: str
    date: Optional[datetime] = None
    author: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Privilege
    privilege_type: str = "attorney-client"  # attorney-client, work-product
    privilege_reason: str = ""
    
    # Status
    withheld: bool = True


class EDiscoveryEngine:
    """
    E-Discovery and legal hold management engine
    """
    
    def __init__(self):
        """Initialize e-discovery engine"""
        self.legal_holds: Dict[str, LegalHold] = {}
        self.custodians: List[Custodian] = []
        self.collections: Dict[str, Collection] = {}
        self.documents: Dict[str, Document] = {}
        self.productions: Dict[str, ProductionSet] = {}
        self.privilege_logs: List[PrivilegeLog] = []
        
        # Configuration
        self.auto_preserve = True
        self.deduplication_enabled = True
        
        # Statistics
        self.stats = {
            'active_holds': 0,
            'total_custodians': 0,
            'documents_collected': 0,
            'documents_produced': 0
        }
    
    def create_legal_hold(
        self,
        hold_name: str,
        matter_name: str,
        issuing_attorney: str,
        scope_keywords: List[str],
        custodians: List[str],
        systems: List[str]
    ) -> LegalHold:
        """
        Create new legal hold
        
        Args:
            hold_name: Hold name
            matter_name: Legal matter name
            issuing_attorney: Attorney name
            scope_keywords: Keywords defining scope
            custodians: List of custodian names
            systems: Systems to preserve (email, files, etc.)
            
        Returns:
            LegalHold object
        """
        hold_id = f"HOLD-{len(self.legal_holds)+1:05d}"
        
        hold = LegalHold(
            hold_id=hold_id,
            hold_name=hold_name,
            matter_name=matter_name,
            issuing_attorney=issuing_attorney,
            scope_keywords=scope_keywords,
            custodians=custodians,
            systems=systems,
            status=LegalHoldStatus.DRAFT
        )
        
        self.legal_holds[hold_id] = hold
        
        print(f"\n⚖️  Created Legal Hold: {hold_id}")
        print(f"   Matter: {matter_name}")
        print(f"   Attorney: {issuing_attorney}")
        print(f"   Custodians: {len(custodians)}")
        print(f"   Systems: {', '.join(systems)}")
        
        return hold
    
    def issue_legal_hold(
        self,
        hold_id: str
    ) -> bool:
        """
        Issue legal hold and notify custodians
        
        Args:
            hold_id: Hold to issue
            
        Returns:
            Success status
        """
        hold = self.legal_holds.get(hold_id)
        if not hold:
            print(f"❌ Legal hold not found: {hold_id}")
            return False
        
        hold.status = LegalHoldStatus.ACTIVE
        hold.issued_date = datetime.now()
        self.stats['active_holds'] += 1
        
        # Create custodian records and send notifications
        for custodian_name in hold.custodians:
            custodian_id = f"CUST-{len(self.custodians)+1:06d}"
            
            custodian = Custodian(
                custodian_id=custodian_id,
                hold_id=hold_id,
                name=custodian_name,
                email=f"{custodian_name.lower().replace(' ', '.')}@company.com",
                status=CustodianStatus.PENDING,
                notified_date=datetime.now(),
                notifications_sent=1,
                last_notification=datetime.now()
            )
            
            self.custodians.append(custodian)
            self.stats['total_custodians'] += 1
        
        # Preserve data (simulated)
        if self.auto_preserve:
            print(f"   🔒 Preserving data in systems: {', '.join(hold.systems)}")
        
        print(f"\n📨 Legal Hold Issued: {hold_id}")
        print(f"   Status: {hold.status.value.upper()}")
        print(f"   Notifications Sent: {len(hold.custodians)}")
        print(f"   ⚠️  Data preservation active")
        
        return True
    
    def acknowledge_hold(
        self,
        custodian_id: str
    ) -> bool:
        """
        Record custodian acknowledgment of legal hold
        
        Args:
            custodian_id: Custodian acknowledging
            
        Returns:
            Success status
        """
        custodian = next(
            (c for c in self.custodians if c.custodian_id == custodian_id),
            None
        )
        if not custodian:
            print(f"❌ Custodian not found: {custodian_id}")
            return False
        
        custodian.status = CustodianStatus.ACKNOWLEDGED
        custodian.acknowledged_date = datetime.now()
        
        print(f"\n✅ Hold Acknowledged: {custodian.name}")
        print(f"   Custodian ID: {custodian_id}")
        print(f"   Hold ID: {custodian.hold_id}")
        
        return True
    
    def create_collection(
        self,
        hold_id: str,
        collection_name: str,
        custodians: List[str],
        keywords: List[str],
        collected_by: str,
        date_range_start: Optional[datetime] = None,
        date_range_end: Optional[datetime] = None
    ) -> Collection:
        """
        Create document collection for legal hold
        
        Args:
            hold_id: Legal hold
            collection_name: Collection name
            custodians: Custodians to collect from
            keywords: Search keywords
            collected_by: Collector name
            date_range_start: Start date filter
            date_range_end: End date filter
            
        Returns:
            Collection object
        """
        hold = self.legal_holds.get(hold_id)
        if not hold:
            print(f"❌ Legal hold not found: {hold_id}")
            return None
        
        collection_id = f"COLL-{len(self.collections)+1:06d}"
        
        collection = Collection(
            collection_id=collection_id,
            hold_id=hold_id,
            collection_name=collection_name,
            custodians=custodians,
            keywords=keywords,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            collected_by=collected_by,
            status="in_progress"
        )
        
        self.collections[collection_id] = collection
        
        print(f"\n📂 Created Collection: {collection_id}")
        print(f"   Name: {collection_name}")
        print(f"   Hold: {hold_id}")
        print(f"   Custodians: {len(custodians)}")
        print(f"   Keywords: {', '.join(keywords[:3])}...")
        
        # Simulate document collection
        self._collect_documents(collection)
        
        return collection
    
    def _collect_documents(self, collection: Collection):
        """Collect documents matching criteria (simulated)"""
        # Simulate finding documents
        num_documents = 150  # Simulated
        
        for i in range(num_documents):
            doc_id = f"DOC-{len(self.documents)+1:08d}"
            
            document = Document(
                document_id=doc_id,
                collection_id=collection.collection_id,
                file_name=f"document_{i+1}.pdf",
                file_path=f"/collections/{collection.collection_id}/doc_{i+1}.pdf",
                file_type="pdf",
                file_size_bytes=1024 * 500,  # 500KB
                created_date=datetime.now() - timedelta(days=365-i),
                custodian=collection.custodians[i % len(collection.custodians)] if collection.custodians else None
            )
            
            self.documents[doc_id] = document
            collection.total_documents += 1
            self.stats['documents_collected'] += 1
        
        collection.status = "completed"
        collection.total_size_gb = num_documents * 0.0005  # Rough calculation
        
        print(f"   ✅ Collected {num_documents} documents")
        print(f"   Total Size: {collection.total_size_gb:.2f} GB")
    
    def review_document(
        self,
        document_id: str,
        reviewer: str,
        status: DocumentStatus,
        tags: Optional[List[str]] = None,
        privilege: bool = False
    ) -> bool:
        """
        Review and code document
        
        Args:
            document_id: Document to review
            reviewer: Reviewer name
            status: Review status
            tags: Document tags
            privilege: Privileged document flag
            
        Returns:
            Success status
        """
        document = self.documents.get(document_id)
        if not document:
            print(f"❌ Document not found: {document_id}")
            return False
        
        document.status = status
        document.reviewed_by = reviewer
        document.reviewed_date = datetime.now()
        document.privilege = privilege
        
        if tags:
            document.tags.extend(tags)
        
        print(f"\n📄 Document Reviewed: {document_id}")
        print(f"   Status: {status.value}")
        print(f"   Reviewer: {reviewer}")
        if privilege:
            print(f"   ⚠️  PRIVILEGED")
        
        return True
    
    def create_production(
        self,
        production_name: str,
        recipient: str,
        document_ids: List[str],
        format: ProductionFormat = ProductionFormat.PDF,
        bates_prefix: str = "PROD"
    ) -> ProductionSet:
        """
        Create production set for delivery
        
        Args:
            production_name: Production name
            recipient: Recipient name
            document_ids: Documents to produce
            format: Production format
            bates_prefix: Bates numbering prefix
            
        Returns:
            ProductionSet object
        """
        production_id = f"PROD-{len(self.productions)+1:05d}"
        
        production = ProductionSet(
            production_id=production_id,
            production_name=production_name,
            recipient=recipient,
            document_ids=document_ids,
            format=format,
            bates_prefix=bates_prefix
        )
        
        self.productions[production_id] = production
        
        # Assign bates numbers
        bates_num = production.bates_start
        privileged_docs = []
        
        for doc_id in document_ids:
            document = self.documents.get(doc_id)
            if document:
                if document.privilege:
                    # Create privilege log entry
                    privileged_docs.append(document)
                else:
                    # Assign bates number
                    document.bates_number = f"{bates_prefix}{bates_num:06d}"
                    document.produced = True
                    document.production_id = production_id
                    bates_num += 1
                    self.stats['documents_produced'] += 1
        
        # Create privilege log for withheld documents
        for doc in privileged_docs:
            log_id = f"PRIV-{len(self.privilege_logs)+1:06d}"
            
            priv_log = PrivilegeLog(
                log_id=log_id,
                production_id=production_id,
                document_id=doc.document_id,
                date=doc.created_date,
                author=doc.author,
                description=f"Privileged document withheld: {doc.file_name}",
                privilege_type="attorney-client"
            )
            
            self.privilege_logs.append(priv_log)
        
        print(f"\n📦 Created Production: {production_id}")
        print(f"   Name: {production_name}")
        print(f"   Recipient: {recipient}")
        print(f"   Documents: {len(document_ids)}")
        print(f"   Produced: {bates_num - production.bates_start}")
        print(f"   Privileged: {len(privileged_docs)}")
        print(f"   Format: {format.value}")
        
        return production
    
    def release_legal_hold(
        self,
        hold_id: str,
        reason: str
    ) -> bool:
        """
        Release legal hold and end preservation
        
        Args:
            hold_id: Hold to release
            reason: Release reason
            
        Returns:
            Success status
        """
        hold = self.legal_holds.get(hold_id)
        if not hold:
            print(f"❌ Legal hold not found: {hold_id}")
            return False
        
        hold.status = LegalHoldStatus.RELEASED
        hold.release_date = datetime.now()
        self.stats['active_holds'] -= 1
        
        # Update custodian statuses
        hold_custodians = [
            c for c in self.custodians
            if c.hold_id == hold_id
        ]
        
        print(f"\n🔓 Legal Hold Released: {hold_id}")
        print(f"   Reason: {reason}")
        print(f"   Duration: {(hold.release_date - hold.issued_date).days if hold.issued_date else 0} days")
        print(f"   Custodians: {len(hold_custodians)}")
        print(f"   ℹ️  Data preservation ended")
        
        return True
    
    def generate_hold_report(
        self,
        hold_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive legal hold report"""
        hold = self.legal_holds.get(hold_id)
        if not hold:
            return {}
        
        # Get custodians
        hold_custodians = [
            c for c in self.custodians
            if c.hold_id == hold_id
        ]
        
        acknowledged = [
            c for c in hold_custodians
            if c.status == CustodianStatus.ACKNOWLEDGED
        ]
        
        pending = [
            c for c in hold_custodians
            if c.status == CustodianStatus.PENDING
        ]
        
        # Get collections
        hold_collections = [
            c for c in self.collections.values()
            if c.hold_id == hold_id
        ]
        
        total_docs = sum(c.total_documents for c in hold_collections)
        
        return {
            'hold_info': {
                'hold_id': hold_id,
                'hold_name': hold.hold_name,
                'matter_name': hold.matter_name,
                'status': hold.status.value,
                'issued_date': hold.issued_date,
                'release_date': hold.release_date
            },
            'custodians': {
                'total': len(hold_custodians),
                'acknowledged': len(acknowledged),
                'pending': len(pending),
                'compliance_rate': (len(acknowledged) / len(hold_custodians) * 100) if hold_custodians else 0
            },
            'collections': {
                'total_collections': len(hold_collections),
                'documents_collected': total_docs
            },
            'preservation': {
                'systems': hold.systems,
                'active': hold.status == LegalHoldStatus.ACTIVE
            }
        }


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("E-DISCOVERY & LEGAL HOLD MANAGEMENT")
    print("="*70)
    
    # Initialize engine
    ediscovery = EDiscoveryEngine()
    
    # Create legal hold
    print("\n" + "="*70)
    print("CREATE LEGAL HOLD")
    print("="*70)
    
    hold = ediscovery.create_legal_hold(
        hold_name="Smith v. Corporation Litigation",
        matter_name="Employment Dispute Case #2025-12345",
        issuing_attorney="Sarah Johnson, Esq.",
        scope_keywords=["employment", "termination", "HR", "performance review"],
        custodians=["John Smith", "Jane Doe", "HR Manager"],
        systems=["email", "file_share", "hr_system"]
    )
    
    # Issue hold
    print("\n" + "="*70)
    print("ISSUE LEGAL HOLD")
    print("="*70)
    
    ediscovery.issue_legal_hold(hold.hold_id)
    
    # Custodian acknowledges
    print("\n" + "="*70)
    print("CUSTODIAN ACKNOWLEDGMENT")
    print("="*70)
    
    if ediscovery.custodians:
        ediscovery.acknowledge_hold(ediscovery.custodians[0].custodian_id)
    
    # Create collection
    print("\n" + "="*70)
    print("CREATE COLLECTION")
    print("="*70)
    
    collection = ediscovery.create_collection(
        hold.hold_id,
        "Initial Collection - Email",
        ["John Smith", "Jane Doe"],
        ["termination", "performance"],
        "Discovery Team",
        date_range_start=datetime.now() - timedelta(days=365),
        date_range_end=datetime.now()
    )
    
    # Review documents
    print("\n" + "="*70)
    print("DOCUMENT REVIEW")
    print("="*70)
    
    if ediscovery.documents:
        sample_docs = list(ediscovery.documents.keys())[:3]
        
        ediscovery.review_document(
            sample_docs[0],
            "Reviewer 1",
            DocumentStatus.RELEVANT,
            tags=["key_evidence"]
        )
        
        ediscovery.review_document(
            sample_docs[1],
            "Reviewer 1",
            DocumentStatus.PRIVILEGED,
            privilege=True
        )
    
    # Create production
    print("\n" + "="*70)
    print("CREATE PRODUCTION")
    print("="*70)
    
    relevant_docs = [
        doc_id for doc_id, doc in ediscovery.documents.items()
        if doc.status == DocumentStatus.RELEVANT
    ][:50]  # First 50 relevant
    
    if relevant_docs:
        production = ediscovery.create_production(
            "Production 001 - Initial Production",
            "Opposing Counsel",
            relevant_docs,
            ProductionFormat.PDF,
            bates_prefix="CORP"
        )
    
    # Generate report
    print("\n" + "="*70)
    print("LEGAL HOLD REPORT")
    print("="*70)
    
    report = ediscovery.generate_hold_report(hold.hold_id)
    print(json.dumps(report, indent=2, default=str))
