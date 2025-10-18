"""
Simple Database Repository Implementation for SQLite
Compatible with Enterprise Scanner CRM system
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

class SQLiteRepository:
    def __init__(self, db_path='enterprise_scanner_dev.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

class LeadRepository(SQLiteRepository):
    def get_filtered_leads(self, status='', company_type='', deal_value_range='', 
                          assigned_to='', search='', page=1, per_page=20):
        """Get filtered leads with pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT l.*, c.name as company_name 
        FROM leads l 
        LEFT JOIN companies c ON l.company_id = c.id 
        WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND l.status = ?"
            params.append(status)
        
        if search:
            query += " AND (l.first_name LIKE ? OR l.last_name LIKE ? OR l.email LIKE ? OR c.name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        query += " ORDER BY l.lead_score DESC, l.created_at DESC"
        query += f" LIMIT {per_page} OFFSET {(page-1)*per_page}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        leads = []
        for row in rows:
            lead = dict(row)
            lead['company'] = lead.get('company_name', '')
            leads.append(lead)
        
        conn.close()
        return leads
    
    def count_filtered_leads(self, status='', company_type='', deal_value_range='', 
                           assigned_to='', search=''):
        """Count filtered leads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) 
        FROM leads l 
        LEFT JOIN companies c ON l.company_id = c.id 
        WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND l.status = ?"
            params.append(status)
        
        if search:
            query += " AND (l.first_name LIKE ? OR l.last_name LIKE ? OR l.email LIKE ? OR c.name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def create_lead(self, data):
        """Create a new lead"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find or create company
        company_id = self.find_or_create_company(data.get('company', ''), conn)
        
        cursor.execute("""
            INSERT INTO leads 
            (first_name, last_name, email, phone, company_id, title, status, source, 
             deal_value, lead_score, notes, assigned_to, next_follow_up)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('email', ''),
            data.get('phone', ''),
            company_id,
            data.get('title', ''),
            data.get('status', 'new'),
            data.get('source', ''),
            data.get('deal_value', 0),
            data.get('lead_score', 0),
            data.get('notes', ''),
            data.get('assigned_to', ''),
            data.get('next_follow_up')
        ))
        
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lead_id
    
    def find_or_create_company(self, company_name, conn):
        """Find existing company or create new one"""
        if not company_name:
            return None
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        else:
            cursor.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
            return cursor.lastrowid
    
    def get_lead_by_id(self, lead_id):
        """Get lead by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.*, c.name as company_name 
            FROM leads l 
            LEFT JOIN companies c ON l.company_id = c.id 
            WHERE l.id = ?
        """, (lead_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            lead = dict(row)
            lead['company'] = lead.get('company_name', '')
            return lead
        return None
    
    def update_lead(self, lead_id, data):
        """Update lead"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        set_clauses = []
        params = []
        
        for field in ['first_name', 'last_name', 'email', 'phone', 'title', 'status', 
                     'source', 'deal_value', 'lead_score', 'notes', 'assigned_to']:
            if field in data:
                set_clauses.append(f"{field} = ?")
                params.append(data[field])
        
        if 'company' in data:
            company_id = self.find_or_create_company(data['company'], conn)
            set_clauses.append("company_id = ?")
            params.append(company_id)
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(lead_id)
        
        query = f"UPDATE leads SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def update_lead_status(self, lead_id, status):
        """Update lead status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE leads 
            SET status = ?, updated_at = CURRENT_TIMESTAMP, last_contact = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, lead_id))
        
        conn.commit()
        conn.close()
    
    def count_total_leads(self):
        """Count total leads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_qualified_leads(self):
        """Count qualified leads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE status IN ('qualified', 'demo_scheduled', 'proposal_sent')
        """)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def count_closed_deals(self):
        """Count closed deals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'closed_won'")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_total_revenue(self):
        """Get total revenue from closed deals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(deal_value), 0) 
            FROM leads 
            WHERE status = 'closed_won'
        """)
        revenue = cursor.fetchone()[0]
        conn.close()
        return revenue
    
    def get_average_sales_cycle(self):
        """Get average sales cycle in days"""
        # Simplified calculation - return mock value for now
        return 45
    
    def get_pipeline_counts(self):
        """Get pipeline stage counts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM leads 
            GROUP BY status
        """)
        
        rows = cursor.fetchall()
        pipeline = {}
        for row in rows:
            pipeline[row[0]] = row[1]
        
        conn.close()
        return pipeline
    
    def get_top_opportunities(self, limit=5):
        """Get top opportunities by deal value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.*, c.name as company_name
            FROM leads l
            LEFT JOIN companies c ON l.company_id = c.id
            WHERE l.status IN ('qualified', 'demo_scheduled', 'proposal_sent')
            ORDER BY l.deal_value DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        opportunities = []
        for row in rows:
            opp = dict(row)
            opp['company'] = opp.get('company_name', '')
            opportunities.append(opp)
        
        conn.close()
        return opportunities
    
    def get_revenue_forecast(self, forecast_type, months):
        """Get revenue forecast data"""
        # Simplified forecast - generate mock data based on current pipeline
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(deal_value) 
            FROM leads 
            WHERE status IN ('qualified', 'demo_scheduled', 'proposal_sent')
        """)
        
        pipeline_value = cursor.fetchone()[0] or 0
        conn.close()
        
        # Generate forecast based on type
        multipliers = {
            'conservative': 0.15,
            'likely': 0.25,
            'optimistic': 0.40
        }
        
        multiplier = multipliers.get(forecast_type, 0.25)
        monthly_revenue = pipeline_value * multiplier / months
        
        forecast = []
        for i in range(months):
            forecast.append({
                'month': i + 1,
                'revenue': monthly_revenue * (i + 1),
                'deals': int(monthly_revenue / 150000) if monthly_revenue > 0 else 0
            })
        
        return forecast

class LeadActivityRepository(SQLiteRepository):
    def log_activity(self, lead_id, activity_type, description):
        """Log lead activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO lead_activities (lead_id, activity_type, description)
            VALUES (?, ?, ?)
        """, (lead_id, activity_type, description))
        
        conn.commit()
        conn.close()
    
    def get_lead_activities(self, lead_id):
        """Get activities for a specific lead"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM lead_activities
            WHERE lead_id = ?
            ORDER BY timestamp DESC
        """, (lead_id,))
        
        rows = cursor.fetchall()
        activities = [dict(row) for row in rows]
        conn.close()
        return activities
    
    def get_recent_activities(self, limit=10):
        """Get recent activities across all leads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT la.*, l.first_name, l.last_name, c.name as company_name
            FROM lead_activities la
            JOIN leads l ON la.lead_id = l.id
            LEFT JOIN companies c ON l.company_id = c.id
            ORDER BY la.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        activities = []
        for row in rows:
            activity = dict(row)
            activity['lead_name'] = f"{activity['first_name']} {activity['last_name']}"
            activity['company'] = activity.get('company_name', '')
            activities.append(activity)
        
        conn.close()
        return activities

# Mock classes for backwards compatibility
class CompanyRepository(SQLiteRepository):
    pass

class SecurityAssessmentRepository(SQLiteRepository):
    pass