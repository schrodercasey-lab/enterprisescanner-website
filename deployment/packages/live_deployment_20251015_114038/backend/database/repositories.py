"""
Database Repository Pattern Implementation
Data access layer for Enterprise Scanner with business logic separation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import and_, or_, desc, func, text
    from sqlalchemy.exc import IntegrityError
    sqlalchemy_available = True
except ImportError:
    sqlalchemy_available = False
    # Fallback for development
    class Session:
        pass

if sqlalchemy_available:
    from .models import Company, Lead, SecurityAssessment, ChatSession, Partner, PartnerDeal, APIKey, AnalyticsEvent, LeadActivity

class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def commit(self):
        """Commit database transaction"""
        if sqlalchemy_available:
            self.db.commit()
    
    def rollback(self):
        """Rollback database transaction"""
        if sqlalchemy_available:
            self.db.rollback()
    
    def refresh(self, instance):
        """Refresh instance from database"""
        if sqlalchemy_available:
            self.db.refresh(instance)

class CompanyRepository(BaseRepository):
    """Repository for company operations"""
    
    def get_by_domain(self, domain: str) -> Optional[Company]:
        """Get company by domain"""
        if not sqlalchemy_available:
            return None
        return self.db.query(Company).filter(Company.domain == domain).first()
    
    def get_or_create_company(self, domain: str, company_data: Dict[str, Any]) -> Company:
        """Get existing company or create new one"""
        if not sqlalchemy_available:
            return None
            
        company = self.get_by_domain(domain)
        if not company:
            company = Company(**company_data)
            self.db.add(company)
            self.commit()
            self.refresh(company)
        return company
    
    def get_fortune_500_companies(self, limit: int = 100) -> List[Company]:
        """Get Fortune 500 companies"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Company)
                .filter(Company.is_fortune_500 == True)
                .order_by(Company.fortune_rank)
                .limit(limit)
                .all())
    
    def search_companies(self, query: str, limit: int = 50) -> List[Company]:
        """Search companies by name or domain"""
        if not sqlalchemy_available:
            return []
        search_term = f"%{query.lower()}%"
        return (self.db.query(Company)
                .filter(or_(
                    func.lower(Company.name).contains(search_term),
                    func.lower(Company.domain).contains(search_term)
                ))
                .limit(limit)
                .all())
    
    def get_companies_by_industry(self, industry: str) -> List[Company]:
        """Get companies by industry"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Company)
                .filter(Company.industry == industry)
                .all())
    
    def update_fortune_500_status(self, company_id: str, is_fortune_500: bool, rank: int = None):
        """Update Fortune 500 status"""
        if not sqlalchemy_available:
            return
        update_data = {'is_fortune_500': is_fortune_500}
        if rank:
            update_data['fortune_rank'] = rank
        
        self.db.query(Company).filter(Company.id == company_id).update(update_data)
        self.commit()

class LeadRepository(BaseRepository):
    """Repository for lead operations"""
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Lead:
        """Create new lead"""
        if not sqlalchemy_available:
            return None
        db_lead = Lead(**lead_data)
        self.db.add(db_lead)
        self.commit()
        self.refresh(db_lead)
        return db_lead
    
    def get_lead_by_email(self, email: str) -> Optional[Lead]:
        """Get lead by email address"""
        if not sqlalchemy_available:
            return None
        return self.db.query(Lead).filter(Lead.email == email).first()
    
    def get_leads_by_company(self, company_id: str) -> List[Lead]:
        """Get all leads for a specific company"""
        if not sqlalchemy_available:
            return []
        return self.db.query(Lead).filter(Lead.company_id == company_id).all()
    
    def get_high_value_leads(self, min_value: int = 1000000) -> List[Lead]:
        """Get leads with high estimated deal value"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Lead)
                .filter(Lead.estimated_deal_value >= min_value)
                .order_by(desc(Lead.estimated_deal_value))
                .all())
    
    def get_fortune_500_leads(self) -> List[Lead]:
        """Get all leads from Fortune 500 companies"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Lead)
                .join(Company)
                .filter(Company.is_fortune_500 == True)
                .all())
    
    def get_leads_by_status(self, status: str, limit: int = 100) -> List[Lead]:
        """Get leads by status"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Lead)
                .filter(Lead.lead_status == status)
                .order_by(desc(Lead.created_at))
                .limit(limit)
                .all())
    
    def get_leads_for_follow_up(self, days_ahead: int = 7) -> List[Lead]:
        """Get leads requiring follow-up in next N days"""
        if not sqlalchemy_available:
            return []
        target_date = datetime.now() + timedelta(days=days_ahead)
        return (self.db.query(Lead)
                .filter(and_(
                    Lead.next_follow_up_at <= target_date,
                    Lead.next_follow_up_at >= datetime.now(),
                    Lead.lead_status.in_(['new', 'contacted', 'qualified'])
                ))
                .order_by(Lead.next_follow_up_at)
                .all())
    
    def update_lead_score(self, lead_id: str, score: int):
        """Update lead scoring"""
        if not sqlalchemy_available:
            return
        self.db.query(Lead).filter(Lead.id == lead_id).update({
            'lead_score': score,
            'updated_at': datetime.now()
        })
        self.commit()
    
    def update_lead_status(self, lead_id: str, status: str, assigned_to: str = None):
        """Update lead status and assignment"""
        if not sqlalchemy_available:
            return
        update_data = {
            'lead_status': status,
            'updated_at': datetime.now()
        }
        if assigned_to:
            update_data['assigned_to'] = assigned_to
        
        self.db.query(Lead).filter(Lead.id == lead_id).update(update_data)
        self.commit()
    
    def search_leads(self, query: str, limit: int = 50) -> List[Lead]:
        """Search leads by name, email, or company"""
        if not sqlalchemy_available:
            return []
        search_term = f"%{query.lower()}%"
        return (self.db.query(Lead)
                .join(Company)
                .filter(or_(
                    func.lower(Lead.first_name).contains(search_term),
                    func.lower(Lead.last_name).contains(search_term),
                    func.lower(Lead.email).contains(search_term),
                    func.lower(Company.name).contains(search_term)
                ))
                .limit(limit)
                .all())

class SecurityAssessmentRepository(BaseRepository):
    """Repository for security assessment operations"""
    
    def create_assessment(self, assessment_data: Dict[str, Any]) -> SecurityAssessment:
        """Create new security assessment"""
        if not sqlalchemy_available:
            return None
        assessment = SecurityAssessment(**assessment_data)
        self.db.add(assessment)
        self.commit()
        self.refresh(assessment)
        return assessment
    
    def get_assessments_by_lead(self, lead_id: str) -> List[SecurityAssessment]:
        """Get all assessments for a lead"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(SecurityAssessment)
                .filter(SecurityAssessment.lead_id == lead_id)
                .order_by(desc(SecurityAssessment.completed_at))
                .all())
    
    def get_assessments_by_company(self, company_id: str) -> List[SecurityAssessment]:
        """Get all assessments for a company"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(SecurityAssessment)
                .filter(SecurityAssessment.company_id == company_id)
                .order_by(desc(SecurityAssessment.completed_at))
                .all())
    
    def get_high_risk_assessments(self) -> List[SecurityAssessment]:
        """Get assessments with high or critical risk levels"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(SecurityAssessment)
                .filter(SecurityAssessment.risk_level.in_(['high', 'critical']))
                .order_by(desc(SecurityAssessment.completed_at))
                .all())
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """Get assessment statistics"""
        if not sqlalchemy_available:
            return {}
        
        stats = {}
        total_assessments = self.db.query(SecurityAssessment).count()
        
        # Risk level distribution
        risk_levels = self.db.query(
            SecurityAssessment.risk_level,
            func.count(SecurityAssessment.id).label('count')
        ).group_by(SecurityAssessment.risk_level).all()
        
        # Average security score
        avg_score = self.db.query(
            func.avg(SecurityAssessment.current_security_score)
        ).scalar()
        
        stats.update({
            'total_assessments': total_assessments,
            'risk_distribution': {level: count for level, count in risk_levels},
            'average_security_score': float(avg_score) if avg_score else 0
        })
        
        return stats

class PartnerRepository(BaseRepository):
    """Repository for partner operations"""
    
    def create_partner_application(self, partner_data: Dict[str, Any]) -> Partner:
        """Create new partner application"""
        if not sqlalchemy_available:
            return None
        partner = Partner(**partner_data)
        self.db.add(partner)
        self.commit()
        self.refresh(partner)
        return partner
    
    def get_partner_by_email(self, email: str) -> Optional[Partner]:
        """Get partner by email"""
        if not sqlalchemy_available:
            return None
        return self.db.query(Partner).filter(Partner.email == email).first()
    
    def get_partners_by_status(self, status: str) -> List[Partner]:
        """Get partners by status"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Partner)
                .filter(Partner.status == status)
                .order_by(desc(Partner.created_at))
                .all())
    
    def get_partners_by_tier(self, tier: str) -> List[Partner]:
        """Get partners by tier"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(Partner)
                .filter(Partner.partner_tier == tier)
                .all())
    
    def approve_partner(self, partner_id: str, commission_rate: float) -> bool:
        """Approve partner application"""
        if not sqlalchemy_available:
            return False
        try:
            self.db.query(Partner).filter(Partner.id == partner_id).update({
                'status': 'approved',
                'commission_rate': commission_rate,
                'updated_at': datetime.now()
            })
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            return False
    
    def get_partner_performance(self, partner_id: str) -> Dict[str, Any]:
        """Get partner performance metrics"""
        if not sqlalchemy_available:
            return {}
        
        partner = self.db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            return {}
        
        deals = self.db.query(PartnerDeal).filter(PartnerDeal.partner_id == partner_id).all()
        
        return {
            'total_deals': len(deals),
            'total_value': sum(deal.deal_value for deal in deals),
            'total_commission': sum(deal.commission_amount or 0 for deal in deals),
            'won_deals': len([d for d in deals if d.deal_status == 'closed_won']),
            'pipeline_value': sum(d.deal_value for d in deals if d.deal_status in ['pipeline', 'proposal', 'negotiation'])
        }

class ChatSessionRepository(BaseRepository):
    """Repository for chat session operations"""
    
    def create_chat_session(self, session_data: Dict[str, Any]) -> ChatSession:
        """Create new chat session"""
        if not sqlalchemy_available:
            return None
        session = ChatSession(**session_data)
        self.db.add(session)
        self.commit()
        self.refresh(session)
        return session
    
    def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        if not sqlalchemy_available:
            return None
        return self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    def get_escalated_sessions(self) -> List[ChatSession]:
        """Get sessions escalated to human"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(ChatSession)
                .filter(ChatSession.escalated_to_human == True)
                .order_by(desc(ChatSession.session_start))
                .all())
    
    def get_fortune_500_sessions(self) -> List[ChatSession]:
        """Get sessions from Fortune 500 companies"""
        if not sqlalchemy_available:
            return []
        return (self.db.query(ChatSession)
                .filter(ChatSession.fortune_500_detected == True)
                .order_by(desc(ChatSession.session_start))
                .all())
    
    def update_session_outcome(self, session_id: str, lead_captured: bool, rating: int = None):
        """Update session outcome"""
        if not sqlalchemy_available:
            return
        update_data = {
            'lead_captured': lead_captured,
            'session_end': datetime.now()
        }
        if rating:
            update_data['session_rating'] = rating
            
        self.db.query(ChatSession).filter(ChatSession.session_id == session_id).update(update_data)
        self.commit()

class AnalyticsRepository(BaseRepository):
    """Repository for analytics and reporting"""
    
    def track_event(self, event_data: Dict[str, Any]) -> AnalyticsEvent:
        """Track analytics event"""
        if not sqlalchemy_available:
            return None
        event = AnalyticsEvent(**event_data)
        self.db.add(event)
        self.commit()
        return event
    
    def get_conversion_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion metrics for last N days"""
        if not sqlalchemy_available:
            return {}
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Website visitors
        visitors = self.db.query(AnalyticsEvent).filter(
            and_(
                AnalyticsEvent.event_type == 'page_view',
                AnalyticsEvent.created_at >= start_date
            )
        ).count()
        
        # Leads generated
        leads = self.db.query(Lead).filter(Lead.created_at >= start_date).count()
        
        # Assessments completed
        assessments = self.db.query(SecurityAssessment).filter(
            SecurityAssessment.completed_at >= start_date
        ).count()
        
        # Chat sessions
        chats = self.db.query(ChatSession).filter(
            ChatSession.session_start >= start_date
        ).count()
        
        return {
            'visitors': visitors,
            'leads': leads,
            'assessments': assessments,
            'chat_sessions': chats,
            'visitor_to_lead_rate': (leads / visitors * 100) if visitors > 0 else 0,
            'lead_to_assessment_rate': (assessments / leads * 100) if leads > 0 else 0
        }
    
    def get_lead_source_performance(self) -> List[Dict[str, Any]]:
        """Get performance by lead source"""
        if not sqlalchemy_available:
            return []
        
        results = self.db.query(
            Lead.lead_source,
            func.count(Lead.id).label('count'),
            func.avg(Lead.lead_score).label('avg_score'),
            func.sum(Lead.estimated_deal_value).label('total_value')
        ).group_by(Lead.lead_source).all()
        
        return [
            {
                'source': source,
                'lead_count': count,
                'average_score': float(avg_score) if avg_score else 0,
                'total_value': int(total_value) if total_value else 0
            }
            for source, count, avg_score, total_value in results
        ]

# Repository factory for dependency injection
class RepositoryFactory:
    """Factory for creating repository instances"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def company_repo(self) -> CompanyRepository:
        return CompanyRepository(self.db)
    
    def lead_repo(self) -> LeadRepository:
        return LeadRepository(self.db)
    
    def assessment_repo(self) -> SecurityAssessmentRepository:
        return SecurityAssessmentRepository(self.db)
    
    def partner_repo(self) -> PartnerRepository:
        return PartnerRepository(self.db)
    
    def chat_repo(self) -> ChatSessionRepository:
        return ChatSessionRepository(self.db)
    
    def analytics_repo(self) -> AnalyticsRepository:
        return AnalyticsRepository(self.db)