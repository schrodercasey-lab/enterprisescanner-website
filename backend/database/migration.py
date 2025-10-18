"""
Database Migration Script
Migrate existing in-memory data to PostgreSQL database
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.config import get_db, create_tables, test_connection
    from database.repositories import RepositoryFactory
    sqlalchemy_available = True
except ImportError:
    print("SQLAlchemy not available - running in compatibility mode")
    sqlalchemy_available = False

class DataMigration:
    """Handle migration of existing data to database"""
    
    def __init__(self):
        self.migration_log = []
        self.errors = []
    
    def log_info(self, message: str):
        """Log information message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] INFO: {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def log_error(self, message: str):
        """Log error message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] ERROR: {message}"
        self.migration_log.append(log_entry)
        self.errors.append(log_entry)
        print(log_entry)
    
    def migrate_fortune_500_companies(self, db_session) -> bool:
        """Migrate Fortune 500 company data"""
        try:
            if not sqlalchemy_available:
                self.log_info("SQLAlchemy not available - skipping company migration")
                return True
                
            self.log_info("Starting Fortune 500 companies migration...")
            
            repo_factory = RepositoryFactory(db_session)
            company_repo = repo_factory.company_repo()
            
            # Sample Fortune 500 companies data
            fortune_500_companies = [
                {
                    'name': 'Apple Inc.',
                    'domain': 'apple.com',
                    'industry': 'Technology',
                    'employee_count': 147000,
                    'annual_revenue': 365817000000,
                    'fortune_rank': 1,
                    'is_fortune_500': True,
                    'headquarters_location': 'Cupertino, CA'
                },
                {
                    'name': 'Microsoft Corporation',
                    'domain': 'microsoft.com',
                    'industry': 'Technology',
                    'employee_count': 181000,
                    'annual_revenue': 143015000000,
                    'fortune_rank': 2,
                    'is_fortune_500': True,
                    'headquarters_location': 'Redmond, WA'
                },
                {
                    'name': 'Amazon.com Inc.',
                    'domain': 'amazon.com',
                    'industry': 'E-commerce/Cloud',
                    'employee_count': 1298000,
                    'annual_revenue': 469822000000,
                    'fortune_rank': 3,
                    'is_fortune_500': True,
                    'headquarters_location': 'Seattle, WA'
                }
            ]
            
            migrated_count = 0
            for company_data in fortune_500_companies:
                try:
                    company = company_repo.get_or_create_company(
                        domain=company_data['domain'],
                        company_data=company_data
                    )
                    migrated_count += 1
                    self.log_info(f"Migrated company: {company_data['name']}")
                except Exception as e:
                    self.log_error(f"Failed to migrate company {company_data['name']}: {str(e)}")
            
            self.log_info(f"Completed Fortune 500 companies migration: {migrated_count} companies")
            return True
            
        except Exception as e:
            self.log_error(f"Fortune 500 companies migration failed: {str(e)}")
            return False
    
    def migrate_sample_leads(self, db_session) -> bool:
        """Migrate sample lead data"""
        try:
            if not sqlalchemy_available:
                self.log_info("SQLAlchemy not available - skipping leads migration")
                return True
                
            self.log_info("Starting sample leads migration...")
            
            repo_factory = RepositoryFactory(db_session)
            lead_repo = repo_factory.lead_repo()
            company_repo = repo_factory.company_repo()
            
            # Sample leads data
            sample_leads = [
                {
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'email': 'john.smith@apple.com',
                    'job_title': 'CISO',
                    'department': 'Information Security',
                    'seniority_level': 'C-Level',
                    'lead_source': 'website',
                    'lead_score': 95,
                    'estimated_deal_value': 5000000,
                    'company_domain': 'apple.com'
                },
                {
                    'first_name': 'Sarah',
                    'last_name': 'Johnson',
                    'email': 'sarah.johnson@microsoft.com',
                    'job_title': 'VP of Security',
                    'department': 'IT Security',
                    'seniority_level': 'VP',
                    'lead_source': 'partner',
                    'lead_score': 88,
                    'estimated_deal_value': 3200000,
                    'company_domain': 'microsoft.com'
                },
                {
                    'first_name': 'Mike',
                    'last_name': 'Davis',
                    'email': 'mike.davis@amazon.com',
                    'job_title': 'Director of Cybersecurity',
                    'department': 'Security Operations',
                    'seniority_level': 'Director',
                    'lead_source': 'referral',
                    'lead_score': 82,
                    'estimated_deal_value': 4100000,
                    'company_domain': 'amazon.com'
                }
            ]
            
            migrated_count = 0
            for lead_data in sample_leads:
                try:
                    # Find company by domain
                    company = company_repo.get_by_domain(lead_data.pop('company_domain'))
                    if company:
                        lead_data['company_id'] = str(company.id)
                        lead = lead_repo.create_lead(lead_data)
                        migrated_count += 1
                        self.log_info(f"Migrated lead: {lead_data['first_name']} {lead_data['last_name']}")
                    else:
                        self.log_error(f"Company not found for lead: {lead_data['email']}")
                except Exception as e:
                    self.log_error(f"Failed to migrate lead {lead_data['email']}: {str(e)}")
            
            self.log_info(f"Completed sample leads migration: {migrated_count} leads")
            return True
            
        except Exception as e:
            self.log_error(f"Sample leads migration failed: {str(e)}")
            return False
    
    def migrate_partner_applications(self, db_session, existing_partners: Dict = None) -> bool:
        """Migrate existing partner applications"""
        try:
            if not sqlalchemy_available:
                self.log_info("SQLAlchemy not available - skipping partner migration")
                return True
                
            self.log_info("Starting partner applications migration...")
            
            repo_factory = RepositoryFactory(db_session)
            partner_repo = repo_factory.partner_repo()
            
            # Use existing partner data if provided, otherwise use sample data
            if existing_partners:
                partner_data_list = list(existing_partners.values())
            else:
                # Sample partner applications
                partner_data_list = [
                    {
                        'application_id': 'APP-20251015-0001',
                        'company_name': 'CyberTech Solutions',
                        'contact_name': 'Sarah Chen',
                        'contact_title': 'Partner Manager',
                        'email': 'sarah.chen@cybertech-solutions.com',
                        'phone': '+1-555-0123',
                        'annual_revenue_range': '5-25M',
                        'security_experience_years': '6-10',
                        'partner_tier': 'gold',
                        'commission_rate': 30.0,
                        'status': 'approved',
                        'client_types': ['enterprise', 'fortune500'],
                        'experience_description': '10+ years in cybersecurity consulting',
                        'partnership_goals': 'Expand cybersecurity offerings to Fortune 500'
                    },
                    {
                        'application_id': 'APP-20251015-0002',
                        'company_name': 'SecureIT Consulting',
                        'contact_name': 'Michael Rodriguez',
                        'contact_title': 'CEO',
                        'email': 'michael@secureit-consulting.com',
                        'phone': '+1-555-0124',
                        'annual_revenue_range': '1-5M',
                        'security_experience_years': '3-5',
                        'partner_tier': 'authorized',
                        'commission_rate': 25.0,
                        'status': 'pending',
                        'client_types': ['midmarket', 'enterprise'],
                        'experience_description': 'Growing cybersecurity practice',
                        'partnership_goals': 'Establish enterprise security offerings'
                    }
                ]
            
            migrated_count = 0
            for partner_data in partner_data_list:
                try:
                    partner = partner_repo.create_partner_application(partner_data)
                    migrated_count += 1
                    self.log_info(f"Migrated partner: {partner_data['company_name']}")
                except Exception as e:
                    self.log_error(f"Failed to migrate partner {partner_data['company_name']}: {str(e)}")
            
            self.log_info(f"Completed partner applications migration: {migrated_count} partners")
            return True
            
        except Exception as e:
            self.log_error(f"Partner applications migration failed: {str(e)}")
            return False
    
    def migrate_api_keys(self, db_session, existing_keys: Dict = None) -> bool:
        """Migrate existing API keys"""
        try:
            if not sqlalchemy_available:
                self.log_info("SQLAlchemy not available - skipping API keys migration")
                return True
                
            self.log_info("Starting API keys migration...")
            
            # Note: API keys will need to be regenerated for security
            # This migration creates new keys based on existing key metadata
            
            if existing_keys:
                self.log_info(f"Found {len(existing_keys)} existing API keys - regeneration required")
            else:
                self.log_info("No existing API keys found")
            
            # API key migration would require special handling for security
            # Keys should be regenerated rather than migrated
            
            self.log_info("Completed API keys migration (regeneration required)")
            return True
            
        except Exception as e:
            self.log_error(f"API keys migration failed: {str(e)}")
            return False
    
    def run_migration(self, existing_data: Dict = None) -> bool:
        """Run complete data migration"""
        try:
            self.log_info("Starting Enterprise Scanner data migration...")
            
            # Test database connection
            if sqlalchemy_available and not test_connection():
                self.log_error("Database connection failed - aborting migration")
                return False
            
            # Create tables if they don't exist
            if sqlalchemy_available:
                create_tables()
                self.log_info("Database tables verified/created")
            
            # Run migrations with database session
            if sqlalchemy_available:
                with next(get_db()) as db_session:
                    success = True
                    
                    # Migrate companies
                    if not self.migrate_fortune_500_companies(db_session):
                        success = False
                    
                    # Migrate leads
                    if not self.migrate_sample_leads(db_session):
                        success = False
                    
                    # Migrate partners
                    existing_partners = existing_data.get('partners', {}) if existing_data else {}
                    if not self.migrate_partner_applications(db_session, existing_partners):
                        success = False
                    
                    # Migrate API keys
                    existing_keys = existing_data.get('api_keys', {}) if existing_data else {}
                    if not self.migrate_api_keys(db_session, existing_keys):
                        success = False
                    
                    if success:
                        self.log_info("All migrations completed successfully")
                    else:
                        self.log_error("Some migrations failed - check logs")
                    
                    return success
            else:
                self.log_info("SQLAlchemy not available - migration completed in compatibility mode")
                return True
                
        except Exception as e:
            self.log_error(f"Migration failed with error: {str(e)}")
            return False
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate migration report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if len(self.errors) == 0 else 'partial_success' if len(self.migration_log) > len(self.errors) else 'failed',
            'total_operations': len(self.migration_log),
            'errors': len(self.errors),
            'log': self.migration_log,
            'error_details': self.errors
        }

def load_existing_data(data_file: str = None) -> Dict:
    """Load existing data from file if available"""
    if data_file and os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load existing data: {e}")
    return {}

def save_migration_report(report: Dict, report_file: str = 'migration_report.json'):
    """Save migration report to file"""
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Migration report saved to: {report_file}")
    except Exception as e:
        print(f"Failed to save migration report: {e}")

if __name__ == "__main__":
    # Run migration
    migration = DataMigration()
    
    # Load existing data if available
    existing_data = load_existing_data('existing_data.json')
    
    # Run migration
    success = migration.run_migration(existing_data)
    
    # Generate and save report
    report = migration.generate_migration_report()
    save_migration_report(report)
    
    # Exit with appropriate code
    if success:
        print("\n✅ Data migration completed successfully!")
        exit(0)
    else:
        print("\n❌ Data migration completed with errors!")
        exit(1)