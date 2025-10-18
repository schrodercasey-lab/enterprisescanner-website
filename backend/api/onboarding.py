"""
Enterprise Scanner - Client Onboarding API
Handles Fortune 500 client onboarding, trial management, and automated provisioning
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/api')

# In-memory storage for demo (in production, use database)
onboarding_data = {}
trial_accounts = {}

class OnboardingManager:
    """Manages the Fortune 500 client onboarding process"""
    
    def __init__(self):
        self.trial_packages = {
            'enterprise': {
                'name': 'Enterprise',
                'value': 150000,
                'features': [
                    'Basic vulnerability scanning',
                    'Monthly security reports',
                    'Email support',
                    'Standard integrations'
                ],
                'scan_frequency': 'weekly',
                'support_level': 'business'
            },
            'enterprise-plus': {
                'name': 'Enterprise Plus',
                'value': 350000,
                'features': [
                    'Advanced vulnerability scanning',
                    'Real-time threat monitoring',
                    'Weekly security reports',
                    'Phone & email support',
                    'Custom integrations',
                    'Compliance reporting'
                ],
                'scan_frequency': 'daily',
                'support_level': 'priority'
            },
            'enterprise-premium': {
                'name': 'Enterprise Premium',
                'value': 750000,
                'features': [
                    'Comprehensive security suite',
                    '24/7 threat monitoring',
                    'Real-time reporting',
                    'Dedicated security consultant',
                    'Full API access',
                    'SOC integration',
                    'Custom compliance frameworks'
                ],
                'scan_frequency': 'continuous',
                'support_level': 'dedicated'
            }
        }
    
    def validate_company_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate company information step"""
        required_fields = [
            'companyName', 'industry', 'companySize', 'revenue',
            'contactName', 'contactTitle', 'contactEmail'
        ]
        
        errors = []
        for field in required_fields:
            if not data.get(field, '').strip():
                errors.append(f"{field} is required")
        
        # Validate email format
        email = data.get('contactEmail', '')
        if email and '@' not in email:
            errors.append("Invalid email format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data': data
        }
    
    def assess_security_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess client security profile and risk level"""
        # Calculate risk score based on inputs
        risk_score = 0
        risk_factors = []
        
        # Budget assessment
        budget = data.get('securityBudget', '')
        if budget in ['1-5M']:
            risk_score += 3
            risk_factors.append("Limited security budget")
        elif budget in ['5-10M']:
            risk_score += 2
        elif budget in ['10-25M']:
            risk_score += 1
        
        # Incident history
        incidents = data.get('securityIncidents', '')
        if incidents == 'critical':
            risk_score += 5
            risk_factors.append("History of critical security incidents")
        elif incidents == 'major':
            risk_score += 3
            risk_factors.append("History of major security incidents")
        elif incidents == 'minor':
            risk_score += 1
        
        # Timeline urgency
        timeline = data.get('timeline', '')
        if timeline == 'immediate':
            risk_score += 2
            risk_factors.append("Immediate implementation need indicates current vulnerabilities")
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = 'high'
        elif risk_score >= 5:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommended_package': self._recommend_package(risk_score, data),
            'assessment_data': data
        }
    
    def _recommend_package(self, risk_score: int, data: Dict[str, Any]) -> str:
        """Recommend trial package based on risk assessment"""
        company_size = data.get('companySize', '')
        budget = data.get('securityBudget', '')
        
        # High-risk or large companies get premium
        if risk_score >= 8 or company_size == '50000+' or budget == '25M+':
            return 'enterprise-premium'
        
        # Medium companies get plus
        if company_size in ['10000-50000'] or budget in ['10-25M']:
            return 'enterprise-plus'
        
        # Default to enterprise
        return 'enterprise'
    
    def create_trial_account(self, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and provision trial account"""
        trial_id = str(uuid.uuid4())
        
        # Extract data from all steps
        company_info = onboarding_data.get('step1', {})
        security_assessment = onboarding_data.get('step2', {})
        trial_setup = onboarding_data.get('step3', {})
        
        # Get trial package details
        package_type = trial_setup.get('trialPackage', 'enterprise')
        package_details = self.trial_packages.get(package_type, self.trial_packages['enterprise'])
        
        # Calculate trial dates
        start_date = datetime.strptime(trial_setup.get('startDate', ''), '%Y-%m-%d')
        end_date = start_date + timedelta(days=30)
        
        # Create trial account
        trial_account = {
            'trial_id': trial_id,
            'company_name': company_info.get('companyName', ''),
            'contact_email': company_info.get('contactEmail', ''),
            'contact_name': company_info.get('contactName', ''),
            'package_type': package_type,
            'package_details': package_details,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'api_key': self._generate_api_key(),
            'dashboard_url': f'/dashboard/{trial_id}',
            'consultant_assigned': False,
            'initial_scan_completed': False,
            'onboarding_data': onboarding_data
        }
        
        # Store trial account
        trial_accounts[trial_id] = trial_account
        
        # Schedule automated tasks
        self._schedule_onboarding_tasks(trial_id)
        
        return trial_account
    
    def _generate_api_key(self) -> str:
        """Generate secure API key for trial account"""
        return f"es_trial_{uuid.uuid4().hex[:24]}"
    
    def _schedule_onboarding_tasks(self, trial_id: str):
        """Schedule automated onboarding tasks"""
        # In production, this would integrate with task queue (Celery, etc.)
        tasks = [
            {
                'task': 'assign_consultant',
                'schedule': 'immediate',
                'description': 'Assign dedicated security consultant'
            },
            {
                'task': 'initial_scan',
                'schedule': '+24h',
                'description': 'Perform initial vulnerability scan'
            },
            {
                'task': 'setup_monitoring',
                'schedule': '+48h',
                'description': 'Configure real-time monitoring'
            },
            {
                'task': 'executive_report',
                'schedule': '+72h',
                'description': 'Generate executive summary report'
            }
        ]
        
        logger.info(f"Scheduled {len(tasks)} onboarding tasks for trial {trial_id}")
        return tasks

# Initialize onboarding manager
onboarding_manager = OnboardingManager()

@onboarding_bp.route('/onboarding', methods=['POST'])
def submit_onboarding():
    """Handle complete onboarding form submission"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate all steps
        validation_results = {}
        
        # Validate company info (step 1)
        if 'step1' in data:
            validation_results['step1'] = onboarding_manager.validate_company_info(data['step1'])
        
        # Perform security assessment (step 2)
        if 'step2' in data:
            validation_results['step2'] = onboarding_manager.assess_security_profile(data['step2'])
        
        # Check for validation errors
        errors = []
        for step, result in validation_results.items():
            if not result.get('valid', True):
                errors.extend(result.get('errors', []))
        
        if errors:
            return jsonify({
                'success': False,
                'errors': errors,
                'validation_results': validation_results
            }), 400
        
        # Create trial account
        trial_account = onboarding_manager.create_trial_account(data)
        
        # Store complete onboarding data
        onboarding_id = str(uuid.uuid4())
        onboarding_data[onboarding_id] = {
            'id': onboarding_id,
            'trial_id': trial_account['trial_id'],
            'submitted_at': datetime.now().isoformat(),
            'data': data,
            'validation_results': validation_results,
            'status': 'completed'
        }
        
        logger.info(f"Onboarding completed for {trial_account['company_name']} - Trial ID: {trial_account['trial_id']}")
        
        return jsonify({
            'success': True,
            'onboarding_id': onboarding_id,
            'trial_account': {
                'trial_id': trial_account['trial_id'],
                'company_name': trial_account['company_name'],
                'package_type': trial_account['package_type'],
                'start_date': trial_account['start_date'],
                'end_date': trial_account['end_date'],
                'dashboard_url': trial_account['dashboard_url'],
                'api_key': trial_account['api_key'][:12] + '...'  # Partial key for security
            },
            'next_steps': [
                'Security consultant will contact you within 2 hours',
                'Initial vulnerability scan will be completed within 24 hours',
                'Executive dashboard will be configured within 48 hours'
            ]
        })
        
    except Exception as e:
        logger.error(f"Error processing onboarding: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@onboarding_bp.route('/onboarding/validate', methods=['POST'])
def validate_step():
    """Validate individual onboarding step"""
    try:
        data = request.get_json()
        step = data.get('step')
        step_data = data.get('data', {})
        
        if step == 1:
            result = onboarding_manager.validate_company_info(step_data)
        elif step == 2:
            result = onboarding_manager.assess_security_profile(step_data)
        else:
            result = {'valid': True, 'data': step_data}
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error validating step: {str(e)}")
        return jsonify({
            'valid': False,
            'error': 'Validation error'
        }), 500

@onboarding_bp.route('/trial/<trial_id>', methods=['GET'])
def get_trial_status(trial_id):
    """Get trial account status and details"""
    try:
        trial_account = trial_accounts.get(trial_id)
        
        if not trial_account:
            return jsonify({
                'success': False,
                'error': 'Trial not found'
            }), 404
        
        # Calculate trial progress
        start_date = datetime.fromisoformat(trial_account['start_date'])
        end_date = datetime.fromisoformat(trial_account['end_date'])
        now = datetime.now()
        
        if now < start_date:
            progress = 0
            status = 'pending'
        elif now > end_date:
            progress = 100
            status = 'expired'
        else:
            total_days = (end_date - start_date).days
            elapsed_days = (now - start_date).days
            progress = min(100, (elapsed_days / total_days) * 100)
            status = 'active'
        
        return jsonify({
            'success': True,
            'trial': {
                'trial_id': trial_id,
                'company_name': trial_account['company_name'],
                'status': status,
                'progress': round(progress, 1),
                'days_remaining': max(0, (end_date - now).days),
                'package_type': trial_account['package_type'],
                'package_details': trial_account['package_details'],
                'dashboard_url': trial_account['dashboard_url']
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving trial status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@onboarding_bp.route('/trial/<trial_id>/extend', methods=['POST'])
def extend_trial(trial_id):
    """Extend trial period (admin function)"""
    try:
        data = request.get_json()
        extension_days = data.get('days', 7)
        
        trial_account = trial_accounts.get(trial_id)
        if not trial_account:
            return jsonify({
                'success': False,
                'error': 'Trial not found'
            }), 404
        
        # Extend trial end date
        current_end = datetime.fromisoformat(trial_account['end_date'])
        new_end = current_end + timedelta(days=extension_days)
        trial_account['end_date'] = new_end.isoformat()
        
        logger.info(f"Extended trial {trial_id} by {extension_days} days")
        
        return jsonify({
            'success': True,
            'message': f'Trial extended by {extension_days} days',
            'new_end_date': trial_account['end_date']
        })
        
    except Exception as e:
        logger.error(f"Error extending trial: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@onboarding_bp.route('/trials', methods=['GET'])
def list_trials():
    """List all trial accounts (admin function)"""
    try:
        trials_summary = []
        
        for trial_id, trial_data in trial_accounts.items():
            trials_summary.append({
                'trial_id': trial_id,
                'company_name': trial_data['company_name'],
                'contact_email': trial_data['contact_email'],
                'package_type': trial_data['package_type'],
                'status': trial_data['status'],
                'start_date': trial_data['start_date'],
                'end_date': trial_data['end_date'],
                'created_at': trial_data['created_at']
            })
        
        return jsonify({
            'success': True,
            'trials': trials_summary,
            'total_count': len(trials_summary)
        })
        
    except Exception as e:
        logger.error(f"Error listing trials: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

def register_onboarding_routes(app):
    """Register onboarding routes with Flask app"""
    app.register_blueprint(onboarding_bp)
    logger.info("Onboarding API routes registered")