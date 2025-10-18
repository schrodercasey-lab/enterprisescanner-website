"""
Enterprise User Management System
Provides role-based access control, SSO integration, and multi-tenant support
for Fortune 500 cybersecurity assessment platform.
"""

import json
import uuid
import hashlib
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
import secrets
import bcrypt
from functools import wraps
import requests
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role definitions for RBAC"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    SECURITY_MANAGER = "security_manager"
    ANALYST = "analyst"
    AUDITOR = "auditor"
    VIEWER = "viewer"

class Permission(Enum):
    """Permission definitions for granular access control"""
    # System Administration
    MANAGE_SYSTEM = "manage_system"
    MANAGE_ORGANIZATIONS = "manage_organizations"
    MANAGE_USERS = "manage_users"
    
    # Security Operations
    RUN_ASSESSMENTS = "run_assessments"
    GENERATE_REPORTS = "generate_reports"
    ACCESS_THREAT_INTEL = "access_threat_intel"
    MANAGE_SECURITY_POLICIES = "manage_security_policies"
    
    # Data Access
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    ACCESS_AUDIT_LOGS = "access_audit_logs"
    
    # Compliance
    MANAGE_COMPLIANCE = "manage_compliance"
    VIEW_COMPLIANCE_REPORTS = "view_compliance_reports"

@dataclass
class Organization:
    """Organization data structure"""
    org_id: str
    name: str
    domain: str
    industry: str
    employee_count: int
    subscription_tier: str
    sso_enabled: bool
    sso_provider: str
    sso_metadata: Dict
    created_at: str
    status: str
    billing_contact: str
    technical_contact: str

@dataclass
class User:
    """User data structure"""
    user_id: str
    org_id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool
    is_sso_user: bool
    last_login: Optional[str]
    created_at: str
    updated_at: str
    password_hash: Optional[str]
    mfa_enabled: bool
    session_timeout: int

@dataclass
class UserSession:
    """User session data structure"""
    session_id: str
    user_id: str
    org_id: str
    created_at: str
    expires_at: str
    ip_address: str
    user_agent: str
    is_active: bool

class EnterpriseUserManager:
    """
    Enterprise-grade user management system with RBAC and SSO support
    """
    
    def __init__(self, db_path: str = "enterprise_users.db", jwt_secret: str = None):
        self.db_path = db_path
        self.jwt_secret = jwt_secret or secrets.token_hex(32)
        self.setup_database()
        self.setup_role_permissions()
        
    def setup_database(self):
        """Initialize user management database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Organizations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS organizations (
                    org_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT UNIQUE NOT NULL,
                    industry TEXT,
                    employee_count INTEGER,
                    subscription_tier TEXT DEFAULT 'standard',
                    sso_enabled INTEGER DEFAULT 0,
                    sso_provider TEXT,
                    sso_metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    billing_contact TEXT,
                    technical_contact TEXT
                )
            ''')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    org_id TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    permissions TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_sso_user INTEGER DEFAULT 0,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    password_hash TEXT,
                    mfa_enabled INTEGER DEFAULT 0,
                    session_timeout INTEGER DEFAULT 3600,
                    FOREIGN KEY (org_id) REFERENCES organizations (org_id)
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    org_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (org_id) REFERENCES organizations (org_id)
                )
            ''')
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    org_id TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 1
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    org_id TEXT NOT NULL,
                    user_id TEXT,
                    key_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    permissions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (org_id) REFERENCES organizations (org_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Enterprise user management database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")
            raise
    
    def setup_role_permissions(self):
        """Define role-based permission mappings"""
        self.role_permissions = {
            UserRole.SUPER_ADMIN: [
                Permission.MANAGE_SYSTEM,
                Permission.MANAGE_ORGANIZATIONS,
                Permission.MANAGE_USERS,
                Permission.RUN_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_THREAT_INTEL,
                Permission.MANAGE_SECURITY_POLICIES,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.ACCESS_AUDIT_LOGS,
                Permission.MANAGE_COMPLIANCE,
                Permission.VIEW_COMPLIANCE_REPORTS
            ],
            UserRole.ORG_ADMIN: [
                Permission.MANAGE_USERS,
                Permission.RUN_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_THREAT_INTEL,
                Permission.MANAGE_SECURITY_POLICIES,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.ACCESS_AUDIT_LOGS,
                Permission.MANAGE_COMPLIANCE,
                Permission.VIEW_COMPLIANCE_REPORTS
            ],
            UserRole.SECURITY_MANAGER: [
                Permission.RUN_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_THREAT_INTEL,
                Permission.MANAGE_SECURITY_POLICIES,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.MANAGE_COMPLIANCE,
                Permission.VIEW_COMPLIANCE_REPORTS
            ],
            UserRole.ANALYST: [
                Permission.RUN_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.ACCESS_THREAT_INTEL,
                Permission.VIEW_ANALYTICS,
                Permission.VIEW_COMPLIANCE_REPORTS
            ],
            UserRole.AUDITOR: [
                Permission.VIEW_ANALYTICS,
                Permission.ACCESS_AUDIT_LOGS,
                Permission.VIEW_COMPLIANCE_REPORTS,
                Permission.EXPORT_DATA
            ],
            UserRole.VIEWER: [
                Permission.VIEW_ANALYTICS,
                Permission.VIEW_COMPLIANCE_REPORTS
            ]
        }
    
    def create_organization(self, name: str, domain: str, industry: str, 
                          employee_count: int, billing_contact: str, 
                          technical_contact: str) -> Organization:
        """Create a new organization"""
        try:
            org_id = str(uuid.uuid4())
            org = Organization(
                org_id=org_id,
                name=name,
                domain=domain,
                industry=industry,
                employee_count=employee_count,
                subscription_tier="standard",
                sso_enabled=False,
                sso_provider="",
                sso_metadata={},
                created_at=datetime.now().isoformat(),
                status="active",
                billing_contact=billing_contact,
                technical_contact=technical_contact
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO organizations 
                (org_id, name, domain, industry, employee_count, subscription_tier,
                 sso_enabled, sso_provider, sso_metadata, status, billing_contact, technical_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                org.org_id, org.name, org.domain, org.industry, org.employee_count,
                org.subscription_tier, int(org.sso_enabled), org.sso_provider,
                json.dumps(org.sso_metadata), org.status, org.billing_contact, org.technical_contact
            ))
            
            conn.commit()
            conn.close()
            
            self.log_audit_event("", org_id, "CREATE_ORGANIZATION", "organization", org_id, 
                               f"Created organization: {name}")
            
            logger.info(f"Organization created: {name} ({org_id})")
            return org
            
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            raise
    
    def create_user(self, org_id: str, email: str, first_name: str, last_name: str,
                   role: UserRole, password: str = None, is_sso_user: bool = False) -> User:
        """Create a new user"""
        try:
            user_id = str(uuid.uuid4())
            permissions = self.role_permissions.get(role, [])
            password_hash = None
            
            if password and not is_sso_user:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user = User(
                user_id=user_id,
                org_id=org_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                permissions=permissions,
                is_active=True,
                is_sso_user=is_sso_user,
                last_login=None,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                password_hash=password_hash,
                mfa_enabled=False,
                session_timeout=3600
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users 
                (user_id, org_id, email, first_name, last_name, role, permissions,
                 is_active, is_sso_user, created_at, updated_at, password_hash, mfa_enabled, session_timeout)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id, user.org_id, user.email, user.first_name, user.last_name,
                user.role.value, json.dumps([p.value for p in user.permissions]),
                int(user.is_active), int(user.is_sso_user), user.created_at, user.updated_at,
                user.password_hash, int(user.mfa_enabled), user.session_timeout
            ))
            
            conn.commit()
            conn.close()
            
            self.log_audit_event("", org_id, "CREATE_USER", "user", user_id, 
                               f"Created user: {email} with role {role.value}")
            
            logger.info(f"User created: {email} ({user_id}) with role {role.value}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def authenticate_user(self, email: str, password: str, ip_address: str = "", 
                         user_agent: str = "") -> Optional[Tuple[User, str]]:
        """Authenticate user with email/password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users WHERE email = ? AND is_active = 1
            """, (email,))
            
            user_data = cursor.fetchone()
            if not user_data:
                self.log_audit_event("", "", "LOGIN_FAILED", "user", "", 
                                   f"Failed login attempt for {email}", ip_address, False)
                conn.close()
                return None
            
            # Convert to User object
            user = self._row_to_user(user_data)
            
            # Check password for non-SSO users
            if not user.is_sso_user:
                if not user.password_hash or not bcrypt.checkpw(password.encode('utf-8'), 
                                                               user.password_hash.encode('utf-8')):
                    self.log_audit_event(user.user_id, user.org_id, "LOGIN_FAILED", "user", user.user_id, 
                                       f"Invalid password for {email}", ip_address, False)
                    conn.close()
                    return None
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
            """, (user.user_id,))
            
            conn.commit()
            conn.close()
            
            # Create session
            session_token = self.create_user_session(user, ip_address, user_agent)
            
            self.log_audit_event(user.user_id, user.org_id, "LOGIN_SUCCESS", "user", user.user_id, 
                               f"Successful login for {email}", ip_address)
            
            logger.info(f"User authenticated: {email}")
            return user, session_token
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_user_session(self, user: User, ip_address: str = "", user_agent: str = "") -> str:
        """Create a new user session"""
        try:
            session_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(seconds=user.session_timeout)
            
            session = UserSession(
                session_id=session_id,
                user_id=user.user_id,
                org_id=user.org_id,
                created_at=datetime.now().isoformat(),
                expires_at=expires_at.isoformat(),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_sessions 
                (session_id, user_id, org_id, created_at, expires_at, ip_address, user_agent, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.user_id, session.org_id, session.created_at,
                session.expires_at, session.ip_address, session.user_agent, int(session.is_active)
            ))
            
            conn.commit()
            conn.close()
            
            # Generate JWT token
            token_payload = {
                'session_id': session_id,
                'user_id': user.user_id,
                'org_id': user.org_id,
                'role': user.role.value,
                'permissions': [p.value for p in user.permissions],
                'exp': int(expires_at.timestamp())
            }
            
            token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
            
            logger.info(f"Session created for user: {user.email}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            raise
    
    def validate_session(self, token: str) -> Optional[Dict]:
        """Validate user session token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM user_sessions 
                WHERE session_id = ? AND is_active = 1 AND expires_at > CURRENT_TIMESTAMP
            """, (payload['session_id'],))
            
            session_data = cursor.fetchone()
            conn.close()
            
            if session_data:
                return payload
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("Session token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid session token")
            return None
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT permissions FROM users WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_permissions = json.loads(result[0])
                return permission.value in user_permissions
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return False
    
    def setup_sso_integration(self, org_id: str, provider: str, metadata: Dict) -> bool:
        """Setup SSO integration for organization"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE organizations 
                SET sso_enabled = 1, sso_provider = ?, sso_metadata = ?
                WHERE org_id = ?
            """, (provider, json.dumps(metadata), org_id))
            
            conn.commit()
            conn.close()
            
            self.log_audit_event("", org_id, "SETUP_SSO", "organization", org_id, 
                               f"Configured SSO with provider: {provider}")
            
            logger.info(f"SSO configured for organization: {org_id} with provider: {provider}")
            return True
            
        except Exception as e:
            logger.error(f"SSO setup error: {e}")
            return False
    
    def get_organization_users(self, org_id: str) -> List[User]:
        """Get all users for an organization"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users WHERE org_id = ? ORDER BY created_at DESC
            """, (org_id,))
            
            users = []
            for row in cursor.fetchall():
                users.append(self._row_to_user(row))
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Error getting organization users: {e}")
            return []
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_role(self, user_id: str, new_role: UserRole, updated_by: str) -> bool:
        """Update user role and permissions"""
        try:
            new_permissions = self.role_permissions.get(new_role, [])
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET role = ?, permissions = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (new_role.value, json.dumps([p.value for p in new_permissions]), user_id))
            
            conn.commit()
            conn.close()
            
            # Get user info for audit log
            user = self.get_user_by_id(user_id)
            if user:
                self.log_audit_event(updated_by, user.org_id, "UPDATE_USER_ROLE", "user", user_id, 
                                   f"Updated role to {new_role.value} for {user.email}")
            
            logger.info(f"User role updated: {user_id} to {new_role.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False
    
    def log_audit_event(self, user_id: str, org_id: str, action: str, resource_type: str, 
                       resource_id: str, details: str, ip_address: str = "", success: bool = True):
        """Log audit event"""
        try:
            log_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_logs 
                (log_id, user_id, org_id, action, resource_type, resource_id, details, ip_address, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (log_id, user_id, org_id, action, resource_type, resource_id, details, ip_address, int(success)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Audit logging error: {e}")
    
    def get_audit_logs(self, org_id: str, limit: int = 100) -> List[Dict]:
        """Get audit logs for organization"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM audit_logs 
                WHERE org_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (org_id, limit))
            
            logs = []
            columns = [description[0] for description in cursor.description]
            for row in cursor.fetchall():
                logs.append(dict(zip(columns, row)))
            
            conn.close()
            return logs
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        return User(
            user_id=row[0],
            org_id=row[1],
            email=row[2],
            first_name=row[3],
            last_name=row[4],
            role=UserRole(row[5]),
            permissions=[Permission(p) for p in json.loads(row[6]) if p],
            is_active=bool(row[7]),
            is_sso_user=bool(row[8]),
            last_login=row[9],
            created_at=row[10],
            updated_at=row[11],
            password_hash=row[12],
            mfa_enabled=bool(row[13]),
            session_timeout=row[14]
        )

# Decorators for permission checking
def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would integrate with Flask request context
            # For now, we'll pass the validation through
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role: UserRole):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would integrate with Flask request context
            # For now, we'll pass the validation through
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Global user manager instance
user_manager = EnterpriseUserManager()