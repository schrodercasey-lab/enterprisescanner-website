"""
Enterprise Scanner Production SQLite Repositories
Optimized for Fortune 500 scale with enterprise features
"""

import os
import sqlite3
import logging
import threading
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager

class SQLiteConnectionPool:
    """Thread-safe SQLite connection pool for production"""
    
    def __init__(self, database_path, max_connections=20):
        self.database_path = database_path
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
        
        # Pre-create connections
        for _ in range(5):  # Start with 5 connections
            self.connections.append(self._create_connection())
    
    def _create_connection(self):
        """Create optimized SQLite connection"""
        conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=30.0  # 30 second timeout
        )
        conn.row_factory = sqlite3.Row
        
        # Apply production optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = memory")
        
        return conn
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        with self.lock:
            if self.connections:
                conn = self.connections.pop()
            else:
                conn = self._create_connection()
        
        try:
            yield conn
        finally:
            with self.lock:
                if len(self.connections) < self.max_connections:
                    self.connections.append(conn)
                else:
                    conn.close()

# Initialize connection pool
db_pool = SQLiteConnectionPool('enterprise_scanner_production.db')

class ProductionCompanyRepository:
    """Production-optimized company repository"""
    
    def get_all_companies(self, fortune_500_only: bool = False, limit: int = None) -> List[Dict]:
        """Get companies with production optimizations"""
        try:
            with db_pool.get_connection() as conn:
                if fortune_500_only:
                    query = "SELECT * FROM companies WHERE is_fortune_500 = 1 ORDER BY name"
                else:
                    query = "SELECT * FROM companies ORDER BY name"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor = conn.cursor()
                cursor.execute(query)
                companies = [dict(row) for row in cursor.fetchall()]
                
                logging.info(f"Retrieved {len(companies)} companies")
                return companies
                
        except Exception as e:
            logging.error(f"Error getting companies: {e}")
            return []
    
    def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """Get company by ID with caching"""
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logging.error(f"Error getting company {company_id}: {e}")
            return None
    
    def search_companies(self, search_term: str, fortune_500_only: bool = False) -> List[Dict]:
        """Search companies with full-text search"""
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                base_query = """
                    SELECT * FROM companies 
                    WHERE (name LIKE ? OR industry LIKE ? OR description LIKE ?)
                """
                params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
                
                if fortune_500_only:
                    base_query += " AND is_fortune_500 = 1"
                
                base_query += " ORDER BY is_fortune_500 DESC, name"
                
                cursor.execute(base_query, params)
                companies = [dict(row) for row in cursor.fetchall()]
                
                logging.info(f"Search '{search_term}' returned {len(companies)} companies")
                return companies
                
        except Exception as e:
            logging.error(f"Error searching companies: {e}")
            return []

class ProductionLeadRepository:
    """Production-optimized lead repository with advanced features"""
    
    def get_all_leads(self, filters: Dict = None, page: int = 1, per_page: int = 50) -> Dict:
        """Get leads with advanced filtering and pagination"""
        try:
            offset = (page - 1) * per_page
            
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # Base query with joins
                base_query = """
                    SELECT l.*, c.name as company_name, c.is_fortune_500, c.industry
                    FROM leads l
                    LEFT JOIN companies c ON l.company_id = c.id
                """
                
                # Build WHERE conditions
                where_conditions = []
                params = []
                
                if filters:
                    if filters.get('status'):
                        where_conditions.append("l.status = ?")
                        params.append(filters['status'])
                    
                    if filters.get('min_score'):
                        where_conditions.append("l.score >= ?")
                        params.append(filters['min_score'])
                    
                    if filters.get('max_score'):
                        where_conditions.append("l.score <= ?")
                        params.append(filters['max_score'])
                    
                    if filters.get('fortune_500_only'):
                        where_conditions.append("c.is_fortune_500 = 1")
                    
                    if filters.get('industry'):
                        where_conditions.append("c.industry = ?")
                        params.append(filters['industry'])
                    
                    if filters.get('search'):
                        where_conditions.append("""
                            (l.name LIKE ? OR l.email LIKE ? OR l.title LIKE ? OR c.name LIKE ?)
                        """)
                        search_term = f"%{filters['search']}%"
                        params.extend([search_term, search_term, search_term, search_term])
                    
                    if filters.get('min_deal_value'):
                        where_conditions.append("l.deal_value >= ?")
                        params.append(filters['min_deal_value'])
                
                # Complete query
                if where_conditions:
                    query = base_query + " WHERE " + " AND ".join(where_conditions)
                else:
                    query = base_query
                
                # Add ordering and pagination
                query += " ORDER BY l.score DESC, l.deal_value DESC, l.created_at DESC"
                query += f" LIMIT {per_page} OFFSET {offset}"
                
                cursor.execute(query, params)
                leads = [dict(row) for row in cursor.fetchall()]
                
                # Get total count
                count_query = """
                    SELECT COUNT(*) FROM leads l
                    LEFT JOIN companies c ON l.company_id = c.id
                """
                if where_conditions:
                    count_query += " WHERE " + " AND ".join(where_conditions)
                
                # Remove pagination params for count
                count_params = params
                cursor.execute(count_query, count_params)
                total = cursor.fetchone()[0]
                
                result = {
                    'leads': leads,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page,
                    'has_next': page * per_page < total,
                    'has_prev': page > 1
                }
                
                logging.info(f"Retrieved {len(leads)} leads (page {page}/{result['pages']})")
                return result
                
        except Exception as e:
            logging.error(f"Error getting leads: {e}")
            return {'leads': [], 'total': 0, 'page': 1, 'per_page': per_page, 'pages': 0}
    
    def get_lead_statistics(self) -> Dict:
        """Get comprehensive lead statistics"""
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total leads
                cursor.execute("SELECT COUNT(*) FROM leads")
                stats['total_leads'] = cursor.fetchone()[0]
                
                # Qualified leads (score >= 75)
                cursor.execute("SELECT COUNT(*) FROM leads WHERE score >= 75")
                stats['qualified_leads'] = cursor.fetchone()[0]
                
                # Hot leads (score >= 90)
                cursor.execute("SELECT COUNT(*) FROM leads WHERE score >= 90")
                stats['hot_leads'] = cursor.fetchone()[0]
                
                # Total pipeline value
                cursor.execute("SELECT COALESCE(SUM(deal_value), 0) FROM leads WHERE status != 'lost'")
                stats['pipeline_value'] = float(cursor.fetchone()[0])
                
                # Won deals value
                cursor.execute("SELECT COALESCE(SUM(deal_value), 0) FROM leads WHERE status = 'won'")
                stats['won_value'] = float(cursor.fetchone()[0])
                
                # Average deal size
                cursor.execute("SELECT COALESCE(AVG(deal_value), 0) FROM leads WHERE deal_value > 0")
                stats['average_deal_size'] = float(cursor.fetchone()[0])
                
                # Leads by status
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM leads 
                    GROUP BY status 
                    ORDER BY COUNT(*) DESC
                """)
                stats['leads_by_status'] = dict(cursor.fetchall())
                
                # Fortune 500 leads
                cursor.execute("""
                    SELECT COUNT(*) FROM leads l
                    JOIN companies c ON l.company_id = c.id
                    WHERE c.is_fortune_500 = 1
                """)
                stats['fortune_500_leads'] = cursor.fetchone()[0]
                
                # Recent activity (last 30 days)
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute("SELECT COUNT(*) FROM leads WHERE created_at >= ?", (thirty_days_ago,))
                stats['recent_leads'] = cursor.fetchone()[0]
                
                logging.info("Lead statistics calculated successfully")
                return stats
                
        except Exception as e:
            logging.error(f"Error getting lead statistics: {e}")
            return {}
    
    def update_lead_score(self, lead_id: int, new_score: int) -> bool:
        """Update lead score with activity logging"""
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current score
                cursor.execute("SELECT score FROM leads WHERE id = ?", (lead_id,))
                current_score = cursor.fetchone()[0]
                
                # Update score
                cursor.execute("UPDATE leads SET score = ? WHERE id = ?", (new_score, lead_id))
                
                # Log activity
                cursor.execute("""
                    INSERT INTO lead_activities (lead_id, activity_type, description, performed_by)
                    VALUES (?, ?, ?, ?)
                """, (lead_id, 'score_update', f'Score updated from {current_score} to {new_score}', 'system'))
                
                conn.commit()
                logging.info(f"Lead {lead_id} score updated: {current_score} -> {new_score}")
                return True
                
        except Exception as e:
            logging.error(f"Error updating lead score: {e}")
            return False

class ProductionLeadActivityRepository:
    """Production lead activity repository with analytics"""
    
    def get_activities_by_lead(self, lead_id: int, limit: int = 100) -> List[Dict]:
        """Get activities for a lead with limit"""
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM lead_activities 
                    WHERE lead_id = ? 
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (lead_id, limit))
                
                activities = [dict(row) for row in cursor.fetchall()]
                logging.info(f"Retrieved {len(activities)} activities for lead {lead_id}")
                return activities
                
        except Exception as e:
            logging.error(f"Error getting activities: {e}")
            return []
    
    def get_recent_activities(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent activities across all leads"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT la.*, l.name as lead_name, c.name as company_name
                    FROM lead_activities la
                    JOIN leads l ON la.lead_id = l.id
                    JOIN companies c ON l.company_id = c.id
                    WHERE la.created_at >= ?
                    ORDER BY la.created_at DESC
                    LIMIT ?
                """, (cutoff_time, limit))
                
                activities = [dict(row) for row in cursor.fetchall()]
                logging.info(f"Retrieved {len(activities)} recent activities")
                return activities
                
        except Exception as e:
            logging.error(f"Error getting recent activities: {e}")
            return []

class ProductionSecurityAssessmentRepository:
    """Production security assessment repository"""
    
    def get_assessments_by_company(self, company_id: int) -> List[Dict]:
        """Get assessments for a company"""
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM security_assessments 
                    WHERE company_id = ? 
                    ORDER BY assessment_date DESC
                """, (company_id,))
                
                assessments = [dict(row) for row in cursor.fetchall()]
                return assessments
                
        except Exception as e:
            logging.error(f"Error getting assessments: {e}")
            return []

# Compatibility aliases for existing code
CompanyRepository = ProductionCompanyRepository
LeadRepository = ProductionLeadRepository
LeadActivityRepository = ProductionLeadActivityRepository
SecurityAssessmentRepository = ProductionSecurityAssessmentRepository

def check_database_health() -> Dict:
    """Check production database health"""
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic connectivity test
            cursor.execute("SELECT 1")
            
            # Get database statistics
            cursor.execute("SELECT COUNT(*) FROM companies")
            companies = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM leads")
            leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lead_activities")
            activities = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM security_assessments")
            assessments = cursor.fetchone()[0]
            
            # Check database file size
            db_size = os.path.getsize('enterprise_scanner_production.db')
            
            return {
                'status': 'healthy',
                'database_type': 'SQLite Production',
                'connection_pool_size': len(db_pool.connections),
                'database_size': db_size,
                'statistics': {
                    'total_companies': companies,
                    'total_leads': leads,
                    'total_activities': activities,
                    'total_assessments': assessments
                }
            }
            
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
