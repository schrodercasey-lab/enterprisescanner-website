"""
Enterprise User Management API Endpoints
Provides REST API for user management, authentication, and authorization
"""

from flask import Blueprint, jsonify, request, session
import json
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.user_management import (
        user_manager, UserRole, Permission, require_permission, require_role
    )
except ImportError:
    # Mock user management if not available
    class MockUserManager:
        def authenticate(self, *args): return None
        def create_user(self, *args): return None
        def get_user(self, *args): return None
    user_manager = MockUserManager()
    class UserRole: ADMIN = 'admin'; USER = 'user'
    class Permission: READ = 'read'; WRITE = 'write'
    def require_permission(*args): 
        def decorator(f): return f
        return decorator
    def require_role(*args):
        def decorator(f): return f
        return decorator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
user_mgmt_bp = Blueprint('user_mgmt', __name__)

@user_mgmt_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and create session
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Authenticate user
        auth_result = user_manager.authenticate_user(email, password, ip_address, user_agent)
        
        if auth_result:
            user, session_token = auth_result
            
            # Store session info
            session['user_id'] = user.user_id
            session['org_id'] = user.org_id
            session['role'] = user.role.value
            
            return jsonify({
                'status': 'success',
                'data': {
                    'user': {
                        'user_id': user.user_id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role.value,
                        'permissions': [p.value for p in user.permissions],
                        'org_id': user.org_id
                    },
                    'session_token': session_token,
                    'expires_in': user.session_timeout
                },
                'message': 'Login successful',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials',
                'timestamp': datetime.now().isoformat()
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Authentication failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Logout user and invalidate session
    """
    try:
        session.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Logout successful',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Logout failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/auth/validate', methods=['GET'])
def validate_session():
    """
    Validate current session
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'status': 'error',
                'message': 'Invalid authorization header',
                'timestamp': datetime.now().isoformat()
            }), 401
        
        token = auth_header.split(' ')[1]
        session_data = user_manager.validate_session(token)
        
        if session_data:
            return jsonify({
                'status': 'success',
                'data': {
                    'valid': True,
                    'user_id': session_data['user_id'],
                    'org_id': session_data['org_id'],
                    'role': session_data['role'],
                    'permissions': session_data['permissions']
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired session',
                'timestamp': datetime.now().isoformat()
            }), 401
            
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Session validation failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/organizations', methods=['POST'])
def create_organization():
    """
    Create a new organization (Super Admin only)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'domain', 'industry', 'employee_count', 'billing_contact', 'technical_contact']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        org = user_manager.create_organization(
            name=data['name'],
            domain=data['domain'],
            industry=data['industry'],
            employee_count=data['employee_count'],
            billing_contact=data['billing_contact'],
            technical_contact=data['technical_contact']
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'organization': {
                    'org_id': org.org_id,
                    'name': org.name,
                    'domain': org.domain,
                    'industry': org.industry,
                    'employee_count': org.employee_count,
                    'subscription_tier': org.subscription_tier,
                    'created_at': org.created_at
                }
            },
            'message': 'Organization created successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Organization creation error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to create organization',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/users', methods=['POST'])
def create_user():
    """
    Create a new user
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['org_id', 'email', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role specified',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        user = user_manager.create_user(
            org_id=data['org_id'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            password=data.get('password'),
            is_sso_user=data.get('is_sso_user', False)
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.value,
                    'permissions': [p.value for p in user.permissions],
                    'org_id': user.org_id,
                    'is_sso_user': user.is_sso_user,
                    'created_at': user.created_at
                }
            },
            'message': 'User created successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"User creation error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to create user',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/organizations/<org_id>/users', methods=['GET'])
def get_organization_users(org_id):
    """
    Get all users for an organization
    """
    try:
        users = user_manager.get_organization_users(org_id)
        
        users_data = []
        for user in users:
            users_data.append({
                'user_id': user.user_id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.value,
                'is_active': user.is_active,
                'is_sso_user': user.is_sso_user,
                'last_login': user.last_login,
                'created_at': user.created_at,
                'mfa_enabled': user.mfa_enabled
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'users': users_data,
                'total_count': len(users_data)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting organization users: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve users',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/users/<user_id>/role', methods=['PUT'])
def update_user_role(user_id):
    """
    Update user role
    """
    try:
        data = request.get_json()
        new_role_str = data.get('role')
        
        if not new_role_str:
            return jsonify({
                'status': 'error',
                'message': 'Role is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        try:
            new_role = UserRole(new_role_str)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role specified',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Get current user from session for audit
        updated_by = session.get('user_id', '')
        
        success = user_manager.update_user_role(user_id, new_role, updated_by)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'User role updated successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update user role',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update user role',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/organizations/<org_id>/sso', methods=['POST'])
def setup_sso(org_id):
    """
    Setup SSO integration for organization
    """
    try:
        data = request.get_json()
        provider = data.get('provider')
        metadata = data.get('metadata', {})
        
        if not provider:
            return jsonify({
                'status': 'error',
                'message': 'SSO provider is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        success = user_manager.setup_sso_integration(org_id, provider, metadata)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'SSO integration configured successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to configure SSO integration',
                'timestamp': datetime.now().isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"SSO setup error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to configure SSO',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/organizations/<org_id>/audit-logs', methods=['GET'])
def get_audit_logs(org_id):
    """
    Get audit logs for organization
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = user_manager.get_audit_logs(org_id, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'audit_logs': logs,
                'total_count': len(logs)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve audit logs',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/permissions/check', methods=['POST'])
def check_permission():
    """
    Check if user has specific permission
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        permission_str = data.get('permission')
        
        if not user_id or not permission_str:
            return jsonify({
                'status': 'error',
                'message': 'User ID and permission are required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        try:
            permission = Permission(permission_str)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid permission specified',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        has_permission = user_manager.check_permission(user_id, permission)
        
        return jsonify({
            'status': 'success',
            'data': {
                'has_permission': has_permission,
                'user_id': user_id,
                'permission': permission_str
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Permission check error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Permission check failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/roles', methods=['GET'])
def get_available_roles():
    """
    Get available user roles and their permissions
    """
    try:
        roles_data = {}
        
        for role in UserRole:
            permissions = user_manager.role_permissions.get(role, [])
            roles_data[role.value] = {
                'name': role.value,
                'permissions': [p.value for p in permissions],
                'description': get_role_description(role)
            }
        
        return jsonify({
            'status': 'success',
            'data': {
                'roles': roles_data
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting roles: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve roles',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_mgmt_bp.route('/api/permissions', methods=['GET'])
def get_available_permissions():
    """
    Get available permissions
    """
    try:
        permissions_data = {}
        
        for permission in Permission:
            permissions_data[permission.value] = {
                'name': permission.value,
                'description': get_permission_description(permission)
            }
        
        return jsonify({
            'status': 'success',
            'data': {
                'permissions': permissions_data
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve permissions',
            'timestamp': datetime.now().isoformat()
        }), 500

def get_role_description(role: UserRole) -> str:
    """Get role description"""
    descriptions = {
        UserRole.SUPER_ADMIN: "Complete system administration access across all organizations",
        UserRole.ORG_ADMIN: "Full administrative access within organization",
        UserRole.SECURITY_MANAGER: "Security operations and policy management",
        UserRole.ANALYST: "Security analysis and assessment capabilities",
        UserRole.AUDITOR: "Audit and compliance review access",
        UserRole.VIEWER: "Read-only access to reports and analytics"
    }
    return descriptions.get(role, "")

def get_permission_description(permission: Permission) -> str:
    """Get permission description"""
    descriptions = {
        Permission.MANAGE_SYSTEM: "Manage system-wide settings and configurations",
        Permission.MANAGE_ORGANIZATIONS: "Create and manage organizations",
        Permission.MANAGE_USERS: "Create, update, and manage user accounts",
        Permission.RUN_ASSESSMENTS: "Execute security assessments and scans",
        Permission.GENERATE_REPORTS: "Generate and export security reports",
        Permission.ACCESS_THREAT_INTEL: "Access threat intelligence feeds and data",
        Permission.MANAGE_SECURITY_POLICIES: "Configure security policies and rules",
        Permission.VIEW_ANALYTICS: "View security analytics and dashboards",
        Permission.EXPORT_DATA: "Export data and reports",
        Permission.ACCESS_AUDIT_LOGS: "View audit logs and system activity",
        Permission.MANAGE_COMPLIANCE: "Manage compliance frameworks and requirements",
        Permission.VIEW_COMPLIANCE_REPORTS: "View compliance status and reports"
    }
    return descriptions.get(permission, "")