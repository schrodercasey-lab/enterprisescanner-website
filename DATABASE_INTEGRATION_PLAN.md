# Enterprise Scanner - Database Integration Planning
**Planning Date:** October 15, 2025  
**Status:** 📋 IN PROGRESS

## 🎯 Database Architecture Overview

This document outlines the comprehensive database integration plan for Enterprise Scanner's transition from in-memory storage to production-grade PostgreSQL database system supporting Fortune 500 lead management, partner operations, and advanced analytics.

## 🗄️ Current State Analysis

### Existing Data Storage (In-Memory)
- **Leads & Contacts**: Stored in Python dictionaries
- **Chat Sessions**: Memory-based storage with session tracking
- **Security Assessments**: Temporary storage with PDF generation
- **Partner Applications**: Local storage with basic validation
- **API Keys**: In-memory dictionary with usage tracking
- **Analytics Data**: Generated demo data for visualization

### Production Requirements
- **Scalability**: Support for 10,000+ Fortune 500 leads
- **Persistence**: Zero data loss during deployments
- **Performance**: Sub-100ms query response times
- **Compliance**: SOC 2, GDPR, and enterprise security standards
- **Backup & Recovery**: Automated daily backups with point-in-time recovery
- **High Availability**: 99.9% uptime SLA

## 📊 Database Schema Design

### Core Tables

#### 1. Companies Table
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) UNIQUE,
    industry VARCHAR(100),
    employee_count INTEGER,
    annual_revenue BIGINT,
    fortune_rank INTEGER,
    headquarters_location VARCHAR(255),
    is_fortune_500 BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_fortune_500 ON companies(is_fortune_500);
CREATE INDEX idx_companies_industry ON companies(industry);
```

#### 2. Leads Table
```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    job_title VARCHAR(150),
    department VARCHAR(100),
    seniority_level VARCHAR(50), -- C-Level, VP, Director, Manager, Individual
    lead_source VARCHAR(100), -- website, partner, referral, etc.
    lead_status VARCHAR(50) DEFAULT 'new', -- new, qualified, contacted, demo_scheduled, proposal_sent, closed_won, closed_lost
    lead_score INTEGER DEFAULT 0,
    estimated_deal_value BIGINT,
    probability_to_close DECIMAL(5,2),
    assigned_to UUID, -- Reference to sales rep
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP,
    next_follow_up_at TIMESTAMP
);

CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_company ON leads(company_id);
CREATE INDEX idx_leads_status ON leads(lead_status);
CREATE INDEX idx_leads_score ON leads(lead_score DESC);
CREATE INDEX idx_leads_follow_up ON leads(next_follow_up_at);
```

#### 3. Security Assessments Table
```sql
CREATE TABLE security_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    company_id UUID REFERENCES companies(id),
    assessment_type VARCHAR(50) DEFAULT 'comprehensive',
    current_security_score INTEGER,
    risk_level VARCHAR(20), -- low, medium, high, critical
    vulnerabilities_found INTEGER,
    compliance_score INTEGER,
    recommended_budget BIGINT,
    roi_projection BIGINT,
    assessment_data JSONB, -- Detailed assessment results
    pdf_report_path VARCHAR(500),
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_lead ON security_assessments(lead_id);
CREATE INDEX idx_assessments_company ON security_assessments(company_id);
CREATE INDEX idx_assessments_risk ON security_assessments(risk_level);
CREATE INDEX idx_assessments_score ON security_assessments(current_security_score);
```

#### 4. Chat Sessions Table
```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    company_id UUID REFERENCES companies(id),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    escalated_to_human BOOLEAN DEFAULT FALSE,
    escalation_reason VARCHAR(255),
    assigned_consultant VARCHAR(100),
    session_rating INTEGER, -- 1-5 rating from customer
    fortune_500_detected BOOLEAN DEFAULT FALSE,
    high_value_opportunity BOOLEAN DEFAULT FALSE,
    session_data JSONB -- Chat messages and metadata
);

CREATE INDEX idx_chat_lead ON chat_sessions(lead_id);
CREATE INDEX idx_chat_escalated ON chat_sessions(escalated_to_human);
CREATE INDEX idx_chat_fortune_500 ON chat_sessions(fortune_500_detected);
```

#### 5. Partners Table
```sql
CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(150) NOT NULL,
    contact_title VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    annual_revenue_range VARCHAR(50),
    security_experience_years VARCHAR(20),
    partner_tier VARCHAR(50), -- authorized, gold, platinum
    commission_rate DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, active, suspended
    client_types TEXT[], -- Array of client types
    geographic_regions TEXT[],
    specializations TEXT[],
    certification_level VARCHAR(100),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    agreement_signed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partners_email ON partners(email);
CREATE INDEX idx_partners_tier ON partners(partner_tier);
CREATE INDEX idx_partners_status ON partners(status);
```

#### 6. Partner Deals Table
```sql
CREATE TABLE partner_deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID REFERENCES partners(id),
    lead_id UUID REFERENCES leads(id),
    company_id UUID REFERENCES companies(id),
    deal_value BIGINT NOT NULL,
    commission_rate DECIMAL(5,2),
    commission_amount BIGINT,
    deal_status VARCHAR(50), -- pipeline, proposal, negotiation, closed_won, closed_lost
    deal_stage VARCHAR(100),
    close_probability DECIMAL(5,2),
    expected_close_date DATE,
    actual_close_date DATE,
    deal_source VARCHAR(100), -- partner_lead, shared_lead, joint_opportunity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partner_deals_partner ON partner_deals(partner_id);
CREATE INDEX idx_partner_deals_status ON partner_deals(deal_status);
CREATE INDEX idx_partner_deals_value ON partner_deals(deal_value DESC);
```

#### 7. API Keys Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(255) UNIQUE NOT NULL, -- Hashed API key
    key_name VARCHAR(100),
    key_prefix VARCHAR(20), -- First few characters for identification
    created_by UUID, -- User who created the key
    permissions TEXT[], -- Array of allowed permissions
    rate_limit_per_hour INTEGER DEFAULT 1000,
    usage_count BIGINT DEFAULT 0,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

#### 8. Analytics Events Table
```sql
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL, -- page_view, form_submit, chat_start, assessment_complete
    event_data JSONB,
    lead_id UUID REFERENCES leads(id),
    company_id UUID REFERENCES companies(id),
    session_id VARCHAR(100),
    user_agent TEXT,
    ip_address INET,
    referrer_url TEXT,
    page_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created ON analytics_events(created_at);
CREATE INDEX idx_analytics_lead ON analytics_events(lead_id);
CREATE INDEX idx_analytics_company ON analytics_events(company_id);
```

## 🔄 Data Migration Strategy

### Phase 1: Database Setup (Week 1)
1. **PostgreSQL Instance Setup**
   - AWS RDS PostgreSQL 14+ instance
   - Multi-AZ deployment for high availability
   - Automated backups with 7-day retention
   - Security groups and VPC configuration

2. **Schema Implementation**
   - Execute DDL scripts for all tables
   - Create indexes for performance optimization
   - Set up database roles and permissions
   - Configure connection pooling

3. **Development Environment**
   - Local PostgreSQL setup for development
   - Database migration scripts using Alembic
   - Environment-specific configuration
   - Connection string management

### Phase 2: Application Integration (Week 2)
1. **ORM Implementation**
   - SQLAlchemy models for all tables
   - Database connection management
   - Query optimization and caching
   - Error handling and retry logic

2. **API Endpoint Updates**
   - Modify existing endpoints to use database
   - Implement proper transaction handling
   - Add database health checks
   - Update error responses

3. **Data Access Layer**
   - Repository pattern implementation
   - Business logic separation
   - Query builders for complex operations
   - Bulk operations for performance

### Phase 3: Data Migration (Week 3)
1. **Migration Scripts**
   - Import existing Fortune 500 company data
   - Migrate sample lead data for testing
   - Partner application data transfer
   - API key recreation with proper hashing

2. **Data Validation**
   - Integrity checks and foreign key validation
   - Performance testing with realistic data volumes
   - Backup and recovery testing
   - Data quality verification

## 🏗️ Technical Implementation

### Database Configuration
```python
# database/config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://username:password@localhost:5432/enterprise_scanner'
)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    pool_pre_ping=True,
    echo=False  # Set to True for development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Model Implementation
```python
# database/models.py
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, DECIMAL, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .config import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(100), unique=True)
    industry = Column(String(100))
    employee_count = Column(Integer)
    annual_revenue = Column(BigInteger)
    fortune_rank = Column(Integer)
    headquarters_location = Column(String(255))
    is_fortune_500 = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    leads = relationship("Lead", back_populates="company")
    assessments = relationship("SecurityAssessment", back_populates="company")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    job_title = Column(String(150))
    department = Column(String(100))
    seniority_level = Column(String(50))
    lead_source = Column(String(100))
    lead_status = Column(String(50), default='new')
    lead_score = Column(Integer, default=0)
    estimated_deal_value = Column(BigInteger)
    probability_to_close = Column(DECIMAL(5,2))
    assigned_to = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_contacted_at = Column(DateTime(timezone=True))
    next_follow_up_at = Column(DateTime(timezone=True))
    
    # Relationships
    company = relationship("Company", back_populates="leads")
    assessments = relationship("SecurityAssessment", back_populates="lead")
```

### Repository Pattern
```python
# database/repositories.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from .models import Company, Lead, SecurityAssessment, Partner
from .schemas import LeadCreate, LeadUpdate, CompanyCreate

class LeadRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_lead(self, lead_data: LeadCreate) -> Lead:
        """Create new lead with company association"""
        db_lead = Lead(**lead_data.dict())
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead
    
    def get_leads_by_company(self, company_id: str) -> List[Lead]:
        """Get all leads for a specific company"""
        return self.db.query(Lead).filter(Lead.company_id == company_id).all()
    
    def get_high_value_leads(self, min_value: int = 1000000) -> List[Lead]:
        """Get leads with high estimated deal value"""
        return (self.db.query(Lead)
                .filter(Lead.estimated_deal_value >= min_value)
                .order_by(desc(Lead.estimated_deal_value))
                .all())
    
    def get_fortune_500_leads(self) -> List[Lead]:
        """Get all leads from Fortune 500 companies"""
        return (self.db.query(Lead)
                .join(Company)
                .filter(Company.is_fortune_500 == True)
                .all())
    
    def update_lead_score(self, lead_id: str, score: int):
        """Update lead scoring"""
        self.db.query(Lead).filter(Lead.id == lead_id).update({"lead_score": score})
        self.db.commit()

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_company(self, domain: str, company_data: dict) -> Company:
        """Get existing company or create new one"""
        company = self.db.query(Company).filter(Company.domain == domain).first()
        if not company:
            company = Company(**company_data)
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
        return company
    
    def get_fortune_500_companies(self) -> List[Company]:
        """Get all Fortune 500 companies"""
        return (self.db.query(Company)
                .filter(Company.is_fortune_500 == True)
                .order_by(Company.fortune_rank)
                .all())
```

## 📈 Performance Optimization

### Indexing Strategy
- **Primary Keys**: UUID with B-tree indexes
- **Foreign Keys**: Automatic indexing for join performance
- **Search Fields**: Email, domain, phone number indexing
- **Status Fields**: Lead status, partner tier, deal status
- **Time-based**: Created_at, updated_at for analytics queries
- **Composite Indexes**: Multi-column indexes for common query patterns

### Query Optimization
- **Connection Pooling**: 20 connections with proper lifecycle management
- **Query Caching**: Redis cache for frequently accessed data
- **Bulk Operations**: Batch inserts and updates for large datasets
- **Pagination**: Cursor-based pagination for large result sets
- **Read Replicas**: Separate read instances for analytics queries

### Monitoring & Alerting
- **Database Performance**: Query execution time monitoring
- **Connection Health**: Pool utilization and connection failures
- **Storage Usage**: Disk space and growth rate tracking
- **Backup Status**: Automated backup success/failure alerts

## 🔒 Security & Compliance

### Data Protection
- **Encryption at Rest**: AES-256 encryption for all stored data
- **Encryption in Transit**: TLS 1.3 for all database connections
- **Access Control**: Role-based permissions with principle of least privilege
- **Audit Logging**: Comprehensive logging of all data access and modifications

### Compliance Requirements
- **GDPR**: Data retention policies and right to deletion
- **SOC 2**: Access controls and audit trail requirements
- **Enterprise Security**: Customer data isolation and security scanning
- **Data Backup**: Automated daily backups with geographic distribution

## 📊 Analytics & Reporting

### Real-time Analytics
- **Lead Pipeline Metrics**: Conversion rates by source and stage
- **Partner Performance**: Deal volume and commission tracking
- **Security Assessment Trends**: Risk scoring and compliance metrics
- **Customer Engagement**: Chat session analysis and satisfaction scores

### Business Intelligence
- **Executive Dashboards**: High-level KPIs and trends
- **Sales Performance**: Individual and team performance metrics
- **Partner Analytics**: Commission payments and deal attribution
- **Competitive Analysis**: Market positioning and win/loss ratios

## 🚀 Implementation Timeline

### Week 1: Database Foundation
- [ ] PostgreSQL instance setup and configuration
- [ ] Schema creation and index optimization
- [ ] Development environment setup
- [ ] Initial testing and validation

### Week 2: Application Integration
- [ ] SQLAlchemy models and repository implementation
- [ ] API endpoint database integration
- [ ] Connection pooling and error handling
- [ ] Unit tests for database operations

### Week 3: Data Migration & Testing
- [ ] Production data migration scripts
- [ ] Performance testing with realistic data volumes
- [ ] Backup and recovery testing
- [ ] Production deployment preparation

### Week 4: Advanced Features
- [ ] Analytics query optimization
- [ ] Real-time metrics implementation
- [ ] Advanced CRM feature preparation
- [ ] Production monitoring setup

## 💡 Success Criteria

### Performance Metrics
- **Query Response Time**: < 100ms for 95% of queries
- **Throughput**: Support 1000+ concurrent users
- **Availability**: 99.9% uptime SLA
- **Data Integrity**: Zero data loss during migrations

### Business Metrics
- **Lead Management**: 10,000+ Fortune 500 leads tracked
- **Partner Operations**: 500+ partner applications managed
- **Assessment Storage**: 1,000+ security assessments archived
- **API Usage**: 100,000+ API calls per day supported

This database integration plan provides the foundation for Enterprise Scanner's evolution into a enterprise-grade cybersecurity platform capable of supporting Fortune 500 operations at scale.

---

*Enterprise Scanner - Database Integration Planning*  
*Scaling to Support Fortune 500 Enterprise Operations*