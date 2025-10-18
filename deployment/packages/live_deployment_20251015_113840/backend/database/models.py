"""
Database Models for Enterprise Scanner
SQLAlchemy models for all database tables
"""

from typing import List, Optional
from datetime import datetime
import uuid

try:
    from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, DECIMAL, Text, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET
    from sqlalchemy.orm import relationship
    from sqlalchemy.sql import func
    sqlalchemy_available = True
except ImportError:
    sqlalchemy_available = False
    # Fallback for development without SQLAlchemy
    class Column:
        def __init__(self, *args, **kwargs):
            pass
    
    class String:
        def __init__(self, *args, **kwargs):
            pass
    
    # Add other fallback classes as needed

if sqlalchemy_available:
    from .config import Base
else:
    # Fallback base class
    class Base:
        pass

class Company(Base):
    """Company information including Fortune 500 status"""
    
    if sqlalchemy_available:
        __tablename__ = "companies"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        name = Column(String(255), nullable=False, index=True)
        domain = Column(String(100), unique=True, index=True)
        industry = Column(String(100), index=True)
        employee_count = Column(Integer)
        annual_revenue = Column(BigInteger)
        fortune_rank = Column(Integer)
        headquarters_location = Column(String(255))
        is_fortune_500 = Column(Boolean, default=False, index=True)
        company_size = Column(String(50))  # startup, small, medium, large, enterprise
        website_url = Column(String(500))
        linkedin_url = Column(String(500))
        description = Column(Text)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
        
        # Relationships
        leads = relationship("Lead", back_populates="company", cascade="all, delete-orphan")
        assessments = relationship("SecurityAssessment", back_populates="company")
        chat_sessions = relationship("ChatSession", back_populates="company")
        partner_deals = relationship("PartnerDeal", back_populates="company")

class Lead(Base):
    """Lead and contact information with scoring"""
    
    if sqlalchemy_available:
        __tablename__ = "leads"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True)
        first_name = Column(String(100), nullable=False)
        last_name = Column(String(100), nullable=False)
        email = Column(String(255), unique=True, nullable=False, index=True)
        phone = Column(String(50))
        job_title = Column(String(150))
        department = Column(String(100))
        seniority_level = Column(String(50))  # C-Level, VP, Director, Manager, Individual
        lead_source = Column(String(100))  # website, partner, referral, advertisement
        lead_status = Column(String(50), default='new', index=True)  # new, qualified, contacted, demo_scheduled, proposal_sent, closed_won, closed_lost
        lead_score = Column(Integer, default=0, index=True)
        estimated_deal_value = Column(BigInteger)
        probability_to_close = Column(DECIMAL(5,2))
        assigned_to = Column(UUID(as_uuid=True))  # Sales rep assignment
        priority = Column(String(20), default='medium')  # low, medium, high, urgent
        timezone = Column(String(50))
        preferred_contact_method = Column(String(50))  # email, phone, linkedin
        notes = Column(Text)
        tags = Column(ARRAY(String))  # Array of tags for categorization
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
        last_contacted_at = Column(DateTime(timezone=True))
        next_follow_up_at = Column(DateTime(timezone=True), index=True)
        qualification_date = Column(DateTime(timezone=True))
        
        # Relationships
        company = relationship("Company", back_populates="leads")
        assessments = relationship("SecurityAssessment", back_populates="lead")
        chat_sessions = relationship("ChatSession", back_populates="lead")
        activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")

class SecurityAssessment(Base):
    """Security assessment results and recommendations"""
    
    if sqlalchemy_available:
        __tablename__ = "security_assessments"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), index=True)
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True)
        assessment_type = Column(String(50), default='comprehensive')
        current_security_score = Column(Integer, index=True)
        risk_level = Column(String(20), index=True)  # low, medium, high, critical
        vulnerabilities_found = Column(Integer)
        compliance_score = Column(Integer)
        recommended_budget = Column(BigInteger)
        roi_projection = Column(BigInteger)
        implementation_timeline = Column(Integer)  # Months
        priority_areas = Column(ARRAY(String))
        assessment_data = Column(JSONB)  # Detailed assessment results
        recommendations = Column(JSONB)  # Structured recommendations
        pdf_report_path = Column(String(500))
        report_generated = Column(Boolean, default=False)
        completed_at = Column(DateTime(timezone=True), server_default=func.now())
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        # Relationships
        lead = relationship("Lead", back_populates="assessments")
        company = relationship("Company", back_populates="assessments")

class ChatSession(Base):
    """Chat session tracking and escalation"""
    
    if sqlalchemy_available:
        __tablename__ = "chat_sessions"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
        session_id = Column(String(100), unique=True, nullable=False)
        visitor_ip = Column(INET)
        user_agent = Column(Text)
        session_start = Column(DateTime(timezone=True), server_default=func.now())
        session_end = Column(DateTime(timezone=True))
        duration_seconds = Column(Integer)
        message_count = Column(Integer, default=0)
        escalated_to_human = Column(Boolean, default=False, index=True)
        escalation_reason = Column(String(255))
        assigned_consultant = Column(String(100))
        session_rating = Column(Integer)  # 1-5 rating from customer
        fortune_500_detected = Column(Boolean, default=False, index=True)
        high_value_opportunity = Column(Boolean, default=False, index=True)
        lead_captured = Column(Boolean, default=False)
        contact_info_provided = Column(Boolean, default=False)
        session_data = Column(JSONB)  # Chat messages and metadata
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        # Relationships
        lead = relationship("Lead", back_populates="chat_sessions")
        company = relationship("Company", back_populates="chat_sessions")

class Partner(Base):
    """Partner information and tier management"""
    
    if sqlalchemy_available:
        __tablename__ = "partners"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        application_id = Column(String(50), unique=True)  # APP-YYYYMMDD-NNNN format
        company_name = Column(String(255), nullable=False, index=True)
        contact_name = Column(String(150), nullable=False)
        contact_title = Column(String(100))
        email = Column(String(255), unique=True, nullable=False, index=True)
        phone = Column(String(50))
        annual_revenue_range = Column(String(50))
        security_experience_years = Column(String(20))
        partner_tier = Column(String(50), index=True)  # authorized, gold, platinum
        commission_rate = Column(DECIMAL(5,2))
        status = Column(String(50), default='pending', index=True)  # pending, approved, active, suspended, terminated
        client_types = Column(ARRAY(String))  # Array of client types
        geographic_regions = Column(ARRAY(String))
        specializations = Column(ARRAY(String))
        certification_level = Column(String(100))
        certifications = Column(ARRAY(String))
        experience_description = Column(Text)
        partnership_goals = Column(Text)
        onboarding_completed = Column(Boolean, default=False)
        training_completed = Column(Boolean, default=False)
        agreement_signed_at = Column(DateTime(timezone=True))
        last_login_at = Column(DateTime(timezone=True))
        total_deal_value = Column(BigInteger, default=0)
        total_commission_earned = Column(BigInteger, default=0)
        deals_closed = Column(Integer, default=0)
        performance_rating = Column(DECIMAL(3,2))  # 1.00 to 5.00
        notes = Column(Text)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
        
        # Relationships
        deals = relationship("PartnerDeal", back_populates="partner")

class PartnerDeal(Base):
    """Partner deal tracking and commission calculation"""
    
    if sqlalchemy_available:
        __tablename__ = "partner_deals"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), index=True)
        lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True)
        deal_name = Column(String(255))
        deal_value = Column(BigInteger, nullable=False)
        commission_rate = Column(DECIMAL(5,2))
        commission_amount = Column(BigInteger)
        deal_status = Column(String(50), index=True)  # pipeline, proposal, negotiation, closed_won, closed_lost
        deal_stage = Column(String(100))
        close_probability = Column(DECIMAL(5,2))
        expected_close_date = Column(DateTime(timezone=True))
        actual_close_date = Column(DateTime(timezone=True))
        deal_source = Column(String(100))  # partner_lead, shared_lead, joint_opportunity
        sales_cycle_days = Column(Integer)
        competitive_situation = Column(String(255))
        decision_makers = Column(ARRAY(String))
        deal_notes = Column(Text)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
        
        # Relationships
        partner = relationship("Partner", back_populates="deals")
        company = relationship("Company", back_populates="partner_deals")

class APIKey(Base):
    """API key management with usage tracking"""
    
    if sqlalchemy_available:
        __tablename__ = "api_keys"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        key_hash = Column(String(255), unique=True, nullable=False, index=True)
        key_name = Column(String(100))
        key_prefix = Column(String(20))  # First few characters for identification
        created_by = Column(UUID(as_uuid=True))  # User who created the key
        permissions = Column(ARRAY(String))  # Array of allowed permissions
        rate_limit_per_hour = Column(Integer, default=1000)
        usage_count = Column(BigInteger, default=0)
        last_used_at = Column(DateTime(timezone=True))
        last_used_ip = Column(INET)
        expires_at = Column(DateTime(timezone=True))
        is_active = Column(Boolean, default=True, index=True)
        revoked_at = Column(DateTime(timezone=True))
        revoked_reason = Column(String(255))
        created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalyticsEvent(Base):
    """Analytics and tracking events"""
    
    if sqlalchemy_available:
        __tablename__ = "analytics_events"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        event_type = Column(String(100), nullable=False, index=True)
        event_category = Column(String(50))  # engagement, conversion, error
        event_data = Column(JSONB)
        lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
        company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
        session_id = Column(String(100))
        user_agent = Column(Text)
        ip_address = Column(INET)
        referrer_url = Column(Text)
        page_url = Column(Text)
        utm_source = Column(String(100))
        utm_medium = Column(String(100))
        utm_campaign = Column(String(100))
        device_type = Column(String(50))  # desktop, mobile, tablet
        browser = Column(String(100))
        operating_system = Column(String(100))
        created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class LeadActivity(Base):
    """Lead activity tracking and timeline"""
    
    if sqlalchemy_available:
        __tablename__ = "lead_activities"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), index=True)
        activity_type = Column(String(100), nullable=False)  # email, call, meeting, demo, proposal
        activity_subject = Column(String(255))
        activity_description = Column(Text)
        activity_outcome = Column(String(100))  # completed, scheduled, cancelled, no_response
        performed_by = Column(UUID(as_uuid=True))  # User who performed the activity
        scheduled_at = Column(DateTime(timezone=True))
        completed_at = Column(DateTime(timezone=True))
        next_action = Column(String(255))
        next_action_date = Column(DateTime(timezone=True))
        activity_data = Column(JSONB)  # Additional activity-specific data
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        # Relationships
        lead = relationship("Lead", back_populates="activities")

# Model registry for easy access
MODEL_REGISTRY = {
    'Company': Company,
    'Lead': Lead,
    'SecurityAssessment': SecurityAssessment,
    'ChatSession': ChatSession,
    'Partner': Partner,
    'PartnerDeal': PartnerDeal,
    'APIKey': APIKey,
    'AnalyticsEvent': AnalyticsEvent,
    'LeadActivity': LeadActivity
}

def get_model(model_name: str):
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name)

def get_all_models():
    """Get all model classes"""
    return list(MODEL_REGISTRY.values())