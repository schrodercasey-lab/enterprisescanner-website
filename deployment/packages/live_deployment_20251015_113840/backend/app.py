"""
Enterprise Scanner - Flask Application Entry Point
Premium cybersecurity platform for Fortune 500 companies
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Security imports - simplified for demo
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'deployment', 'security'))
    from security_middleware import SecurityMiddleware, require_api_key, require_csrf_token, generate_csrf_token_for_session
    from monitoring.security_monitor import security_monitor, log_failed_login, log_successful_login
    SECURITY_AVAILABLE = True
except ImportError:
    print("Security middleware not available - using simplified security")
    SECURITY_AVAILABLE = False
    class SecurityMiddleware:
        def __init__(self, app): pass
    def require_api_key(f): return f
    def require_csrf_token(f): return f
    def generate_csrf_token_for_session(): return "demo-token"

# Import security assessment blueprint
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.security_assessment import security_assessment_bp


# Try to import database repositories, use mock if not available
try:
    # First try SQLite repositories (for development)
    from database.sqlite_repositories import LeadRepository, LeadActivityRepository, CompanyRepository, SecurityAssessmentRepository
    DATABASE_AVAILABLE = True
    DATABASE_TYPE = "SQLite"
    print("SQLite database repositories loaded successfully")
except ImportError:
    try:
        # Fallback to PostgreSQL repositories (for production)
        from database.repositories import CompanyRepository, LeadRepository, SecurityAssessmentRepository, LeadActivityRepository
        from database.config import DatabaseConfig
        DATABASE_AVAILABLE = True
        DATABASE_TYPE = "PostgreSQL"
        print("PostgreSQL database repositories loaded successfully")
    except ImportError as e:
        print(f"Database repositories not available: {e}")
        print("Using mock data - run setup_sqlite_dev.py or setup_postgresql.py to enable database")
        DATABASE_AVAILABLE = False
        DATABASE_TYPE = "Mock"

# Load environment variables based on environment
env_file = '.env.production' if os.environ.get('FLASK_ENV') == 'production' else '.env.development'
load_dotenv(env_file)

app = Flask(__name__)
CORS(app)

# Register security assessment blueprint
app.register_blueprint(security_assessment_bp, url_prefix='/api')

# Initialize security middleware if available
if SECURITY_AVAILABLE:
    security = SecurityMiddleware(app)
else:
    print("Running in demo mode - security middleware disabled")

# Configure session security
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)


# Mock repositories for when database is not available
class MockLeadRepository:
    def get_filtered_leads(self, **kwargs):
        return []
    
    def count_filtered_leads(self, *args):
        return 0
    
    def create_lead(self, data):
        return 1
    
    def get_lead_by_id(self, lead_id):
        return None
    
    def update_lead(self, lead_id, data):
        pass
    
    def update_lead_status(self, lead_id, status):
        pass
    
    def count_total_leads(self):
        return 0
    
    def count_qualified_leads(self):
        return 0
    
    def count_closed_deals(self):
        return 0
    
    def get_total_revenue(self):
        return 0
    
    def get_average_sales_cycle(self):
        return 0
    
    def get_pipeline_counts(self):
        return {}
    
    def get_top_opportunities(self, limit=5):
        return []
    
    def get_revenue_forecast(self, forecast_type, months):
        return []

class MockActivityRepository:
    def log_activity(self, lead_id, activity_type, description):
        pass
    
    def get_lead_activities(self, lead_id):
        return []
    
    def get_recent_activities(self, limit=10):
        return []

# Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'enterprise-scanner-dev-key')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')

# Email Configuration for Google Workspace
EMAIL_CONFIG = {
    'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'port': int(os.environ.get('EMAIL_PORT', 587)),
    'use_tls': os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true',
    'username': os.environ.get('EMAIL_USERNAME', 'info@enterprisescanner.com'),
    'password': os.environ.get('EMAIL_PASSWORD', ''),
    'testing_mode': os.environ.get('EMAIL_TESTING_MODE', 'False').lower() == 'true'
}

# Domain Configuration
DOMAIN_CONFIG = {
    'name': os.environ.get('DOMAIN_NAME', 'localhost:5000'),
    'url': os.environ.get('DOMAIN_URL', 'http://localhost:5000'),
    'api_base': os.environ.get('API_BASE_URL', 'http://localhost:5000/api')
}

# Feature Flags
FEATURES = {
    'fortune_500_detection': os.environ.get('ENABLE_FORTUNE_500_DETECTION', 'True').lower() == 'true',
    'high_value_notifications': os.environ.get('HIGH_VALUE_LEAD_NOTIFICATION', 'True').lower() == 'true',
    'executive_escalation': os.environ.get('EXECUTIVE_ESCALATION_ENABLED', 'True').lower() == 'true',
    'pdf_generation': os.environ.get('PDF_GENERATION_ENABLED', 'True').lower() == 'true',
    'email_delivery': os.environ.get('ASSESSMENT_EMAIL_DELIVERY', 'True').lower() == 'true',
    'lead_routing': os.environ.get('LEAD_ROUTING_ENABLED', 'True').lower() == 'true',
    'real_time_metrics': os.environ.get('REAL_TIME_METRICS', 'True').lower() == 'true'
}

# Legacy configuration for backwards compatibility
app.config['MAIL_SERVER'] = EMAIL_CONFIG['host']
app.config['MAIL_PORT'] = EMAIL_CONFIG['port']
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'info@enterprisescanner.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')

# Enterprise Scanner Business Email Addresses
BUSINESS_EMAILS = {
    'info': 'info@enterprisescanner.com',
    'sales': 'sales@enterprisescanner.com', 
    'support': 'support@enterprisescanner.com',
    'security': 'security@enterprisescanner.com',
    'partnerships': 'partnerships@enterprisescanner.com'
}

# Storage for partner applications and data (in production, use PostgreSQL)
partners = {}
partner_applications = {}

# API key storage (in production, use database)
api_keys = {
    "es_bootstrap_test_key_12345": {
        "name": "Bootstrap Test Key",
        "permissions": "read_write",
        "created": "2025-10-15T11:00:00.000000",
        "last_used": None,
        "usage_count": 0
    }
}

def validate_api_key(api_key):
    """Validate API key and track usage"""
    if api_key in api_keys:
        # Update last used timestamp
        api_keys[api_key]['last_used'] = datetime.now().isoformat()
        api_keys[api_key]['usage_count'] = api_keys[api_key].get('usage_count', 0) + 1
        return True
    return False

def require_api_key(f):
    """Decorator to require API key authentication"""
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Valid API key required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Main homepage - Fortune 500 optimized"""
    return send_from_directory('../website', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from website directory"""
    return send_from_directory('../website', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.1.0',
        'environment': os.environ.get('ENVIRONMENT', 'development'),
        'database': DATABASE_TYPE if DATABASE_AVAILABLE else 'Mock',
        'database_available': DATABASE_AVAILABLE,
        'features': ['live_chat', 'security_assessment', 'analytics_dashboard', 'crm_system'],
        'email_system': 'google_workspace_enabled'
    })

@app.route('/api/roi-calculator', methods=['POST'])
def roi_calculator():
    """Advanced ROI calculator for Fortune 500 prospects"""
    data = request.get_json()
    
    # Extract parameters
    company_size = data.get('company_size', 'large')
    annual_revenue = float(data.get('annual_revenue', 1000000000))  # Default 1B
    current_security_spend = float(data.get('current_security_spend', annual_revenue * 0.03))
    
    # Calculate potential savings (industry benchmarks)
    breach_cost_reduction = annual_revenue * 0.025  # 2.5% of revenue average breach cost
    compliance_savings = current_security_spend * 0.15  # 15% compliance efficiency
    operational_savings = current_security_spend * 0.20  # 20% operational efficiency
    
    total_annual_savings = breach_cost_reduction + compliance_savings + operational_savings
    
    # Enterprise Scanner cost (premium pricing)
    platform_cost = 150000 if company_size == 'enterprise' else 75000
    
    roi_percentage = ((total_annual_savings - platform_cost) / platform_cost) * 100
    payback_months = (platform_cost / (total_annual_savings / 12))
    
    return jsonify({
        'annual_savings': round(total_annual_savings),
        'platform_cost': platform_cost,
        'net_savings': round(total_annual_savings - platform_cost),
        'roi_percentage': round(roi_percentage, 1),
        'payback_months': round(payback_months, 1),
        'breach_cost_reduction': round(breach_cost_reduction),
        'compliance_savings': round(compliance_savings),
        'operational_savings': round(operational_savings)
    })

@app.route('/api/demo-request', methods=['POST'])
def demo_request():
    """Handle Fortune 500 demo requests"""
    data = request.get_json()
    
    # Log high-value lead
    print(f"FORTUNE 500 DEMO REQUEST: {data.get('company')} - {data.get('email')}")
    
    # TODO: Integrate with CRM and email automation
    
    return jsonify({
        'status': 'success',
        'message': 'Demo request received. Our enterprise team will contact you within 24 hours.',
        'reference_id': f"ES-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    })

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Handle live chat messages with enterprise-level responses"""
    data = request.get_json()
    message = data.get('message', '').lower()
    chat_id = data.get('chatId')
    user_info = data.get('userInfo', {})
    
    # Log chat interaction for Fortune 500 lead tracking
    print(f"ENTERPRISE CHAT: {chat_id} - {message[:100]}...")
    
    # Intelligent response routing
    response = generate_enterprise_response(message, user_info)
    escalate = should_escalate_to_human(message, user_info)
    
    return jsonify({
        'response': response,
        'escalate': escalate,
        'reason': get_escalation_reason(message) if escalate else None,
        'chat_id': chat_id,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/chat/escalate', methods=['POST'])
def chat_escalate():
    """Escalate chat to human consultant and notify sales team"""
    data = request.get_json()
    chat_id = data.get('chatId')
    reason = data.get('reason')
    messages = data.get('messages', [])
    user_info = data.get('userInfo', {})
    
    # High-priority notification for Fortune 500 prospects
    print(f"ESCALATION ALERT: {chat_id} - {reason}")
    
    # Send real-time notification to sales@enterprisescanner.com
    send_chat_escalation_notification(chat_id, reason, messages, user_info)
    
    return jsonify({
        'status': 'escalated',
        'message': 'Enterprise consultant will respond within 2 hours',
        'reference_id': f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    })

def send_chat_escalation_notification(chat_id, reason, messages, user_info):
    """Send immediate notification for chat escalations"""
    
    subject = f"🚨 LIVE CHAT ESCALATION: {reason.replace('_', ' ').title()}"
    
    # Extract user information
    user_email = user_info.get('email', 'Unknown')
    user_company = user_info.get('company', 'Unknown Company')
    
    # Format chat messages for email
    chat_history = ""
    for msg in messages[-5:]:  # Last 5 messages
        sender = "Prospect" if msg.get('sender') == 'user' else "System"
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', datetime.utcnow().isoformat())
        chat_history += f"<p><strong>{sender} ({timestamp}):</strong> {content}</p>"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; }}
            .urgent {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .chat-history {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .cta {{ background: #007bff; color: white; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0; }}
            .cta a {{ color: white; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚨 Live Chat Escalation Alert</h1>
            <p>Immediate Response Required</p>
        </div>
        
        <div style="padding: 20px;">
            <div class="urgent">
                <strong>ESCALATION REASON:</strong> {reason.replace('_', ' ').title()}<br>
                <strong>RESPONSE TIME TARGET:</strong> Within 2 hours
            </div>
            
            <h2>Prospect Information</h2>
            <p><strong>Company:</strong> {user_company}</p>
            <p><strong>Email:</strong> {user_email}</p>
            <p><strong>Chat ID:</strong> {chat_id}</p>
            <p><strong>Escalation Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
            
            <h2>Recent Chat History</h2>
            <div class="chat-history">
                {chat_history if chat_history else "<p>No recent messages available</p>"}
            </div>
            
            <div class="cta">
                <h3>Immediate Actions Required</h3>
                <p>
                    <a href="mailto:{user_email}?subject=Enterprise Scanner Consultation">Respond to Prospect</a> | 
                    <a href="https://enterprisescanner.com/admin/chat/{chat_id}">View Full Chat</a>
                </p>
            </div>
            
            <h3>Escalation Guidelines:</h3>
            <ul>
                <li><strong>Executive Level:</strong> Route to senior consultant, prepare executive briefing materials</li>
                <li><strong>Technical Discussion:</strong> Connect with technical architect, prepare technical documentation</li>
                <li><strong>Procurement Inquiry:</strong> Involve sales director, prepare pricing and contract information</li>
                <li><strong>Urgent Matter:</strong> Immediate response required, escalate to management if needed</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Send to sales team with high priority
    send_email(
        to_email=BUSINESS_EMAILS['sales'],
        subject=subject,
        html_content=html_content,
        cc_emails=[BUSINESS_EMAILS['support'], BUSINESS_EMAILS['security']]
    )

@app.route('/api/security-assessment', methods=['POST'])
def security_assessment():
    """Process enterprise security assessment submissions"""
    data = request.get_json()
    form_data = data.get('formData', {})
    risk_score = data.get('riskScore', 0)
    recommendations = data.get('recommendations', [])
    
    # Extract key information for lead scoring
    company_name = form_data.get('companyName', 'Unknown')
    email = form_data.get('email', '')
    industry = form_data.get('industry', '')
    company_size = form_data.get('companySize', '')
    job_title = form_data.get('jobTitle', '')
    
    # High-value lead detection
    high_value_indicators = [
        'cio', 'ciso', 'cto', 'vp', 'director', 'chief', 'head of security',
        'security manager', 'it director', 'risk manager'
    ]
    
    is_high_value = (
        company_size in ['large', 'enterprise'] or
        any(indicator in job_title.lower() for indicator in high_value_indicators) or
        risk_score < 60  # Poor security posture = urgent need
    )
    
    # Generate assessment ID
    assessment_id = f"SA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Log assessment completion
    print(f"SECURITY ASSESSMENT COMPLETED: {assessment_id}")
    print(f"Company: {company_name} ({company_size})")
    print(f"Contact: {form_data.get('contactName')} - {email}")
    print(f"Industry: {industry}")
    print(f"Risk Score: {risk_score}/100")
    print(f"High Value Lead: {'YES' if is_high_value else 'NO'}")
    
    # Calculate potential business value
    business_value = calculate_business_value(form_data, risk_score)
    
    # Generate follow-up recommendations
    follow_up_actions = generate_follow_up_actions(form_data, risk_score, is_high_value)
    
    # TODO: Integrate with CRM system
    # TODO: Send assessment results to sales@enterprisescanner.com
    # TODO: Schedule automated follow-up emails
    # TODO: Add to Fortune 500 prospect pipeline if applicable
    
    # Send email notifications for high-value leads
    if is_high_value:
        send_high_value_lead_notification(form_data, risk_score, assessment_id)
    
    # Send assessment results to prospect
    send_assessment_results_email(form_data, risk_score, recommendations, assessment_id)
    
    response_data = {
        'status': 'success',
        'assessment_id': assessment_id,
        'risk_score': risk_score,
        'business_value': business_value,
        'high_value_lead': is_high_value,
        'follow_up_actions': follow_up_actions,
        'message': 'Security assessment completed successfully',
        'next_steps': {
            'consultation_available': True,
            'demo_recommended': risk_score < 70,
            'urgent_follow_up': risk_score < 50,
            'contact_info': {
                'sales_email': 'sales@enterprisescanner.com',
                'phone': '+1-800-SCANNER',
                'demo_calendar': 'https://enterprisescanner.com/demo'
            }
        }
    }
    
    return jsonify(response_data)

def send_email(to_email, subject, html_content, cc_emails=None, attachments=None):
    """Send email using Google Workspace SMTP with environment configuration"""
    
    # Check if email is configured
    if not EMAIL_CONFIG['password'] and not EMAIL_CONFIG['testing_mode']:
        print(f"⚠️ Email not configured - would send: {subject} to {to_email}")
        return False
    
    # In testing mode, just log the email
    if EMAIL_CONFIG['testing_mode']:
        print(f"📧 TEST MODE - Email: {subject}")
        print(f"   From: {EMAIL_CONFIG['username']}")
        print(f"   To: {to_email}")
        if cc_emails:
            print(f"   CC: {', '.join(cc_emails)}")
        print(f"   Content preview: {html_content[:100]}...")
        if attachments:
            print(f"   Attachments: {len(attachments)} files")
        return True
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_CONFIG['username']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                with open(attachment['file_path'], 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype=attachment['type'])
                    attach.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
                    msg.attach(attach)
        
        # Send email using configured SMTP settings
        server = smtplib.SMTP(EMAIL_CONFIG['host'], EMAIL_CONFIG['port'])
        
        if EMAIL_CONFIG['use_tls']:
            server.starttls()
            
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        
        recipients = [to_email]
        if cc_emails:
            recipients.extend(cc_emails)
            
        server.sendmail(app.config['MAIL_USERNAME'], recipients, msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def send_high_value_lead_notification(form_data, risk_score, assessment_id):
    """Send immediate notification to sales team for high-value leads"""
    
    company_name = form_data.get('companyName', 'Unknown Company')
    contact_name = form_data.get('contactName', 'Unknown Contact')
    email = form_data.get('email', '')
    job_title = form_data.get('jobTitle', '')
    company_size = form_data.get('companySize', '')
    industry = form_data.get('industry', '')
    
    subject = f"🚨 HIGH-VALUE LEAD ALERT: {company_name} - Security Assessment Completed"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .alert {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .info-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
            .info-item {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            .cta {{ background: #28a745; color: white; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0; }}
            .cta a {{ color: white; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 High-Value Lead Alert</h1>
            <p>Enterprise Scanner Security Assessment</p>
        </div>
        
        <div class="content">
            <div class="alert">
                <strong>IMMEDIATE ACTION REQUIRED:</strong> High-value Fortune 500 prospect has completed security assessment
            </div>
            
            <h2>Lead Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Company:</strong> {company_name}<br>
                    <strong>Industry:</strong> {industry}<br>
                    <strong>Size:</strong> {company_size}
                </div>
                <div class="info-item">
                    <strong>Contact:</strong> {contact_name}<br>
                    <strong>Title:</strong> {job_title}<br>
                    <strong>Email:</strong> {email}
                </div>
            </div>
            
            <h2>Assessment Results</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Security Score:</strong> {risk_score}/100<br>
                    <strong>Risk Level:</strong> {"Critical" if risk_score < 40 else "Poor" if risk_score < 55 else "Fair" if risk_score < 70 else "Good"}
                </div>
                <div class="info-item">
                    <strong>Assessment ID:</strong> {assessment_id}<br>
                    <strong>Completed:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
                </div>
            </div>
            
            <div class="cta">
                <h3>Recommended Actions</h3>
                <p>
                    {"🚨 URGENT: Schedule consultation within 24 hours" if risk_score < 50 else "📞 Contact within 48 hours for demo and consultation"}<br>
                    <a href="mailto:{email}?subject=Enterprise Scanner Consultation - {company_name}">Send Follow-up Email</a> | 
                    <a href="tel:+1-800-SCANNER">Call Prospect</a>
                </p>
            </div>
            
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Add to CRM as high-priority lead</li>
                <li>Schedule executive briefing within 48 hours</li>
                <li>Prepare custom ROI analysis for {industry} industry</li>
                <li>{"Emphasize urgent security gaps requiring immediate attention" if risk_score < 60 else "Focus on competitive advantages and industry benchmarking"}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Send to sales team with high priority
    send_email(
        to_email=BUSINESS_EMAILS['sales'],
        subject=subject,
        html_content=html_content,
        cc_emails=[BUSINESS_EMAILS['info'], BUSINESS_EMAILS['security']]
    )

def send_assessment_results_email(form_data, risk_score, recommendations, assessment_id):
    """Send assessment results and next steps to the prospect"""
    
    prospect_email = form_data.get('email', '')
    if not prospect_email:
        return
    
    company_name = form_data.get('companyName', 'your organization')
    contact_name = form_data.get('contactName', 'there')
    risk_level = get_risk_level_from_score(risk_score)
    
    subject = f"Your Enterprise Security Assessment Results - {company_name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; max-width: 800px; margin: 0 auto; }}
            .score-card {{ background: #f8f9fa; border-left: 5px solid #1e3c72; padding: 20px; margin: 20px 0; }}
            .recommendations {{ background: #fff; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px; margin: 20px 0; }}
            .cta {{ background: #28a745; color: white; padding: 20px; text-align: center; border-radius: 10px; margin: 30px 0; }}
            .cta a {{ color: white; text-decoration: none; font-weight: bold; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ Enterprise Security Assessment Results</h1>
            <p>Comprehensive Cybersecurity Analysis for {company_name}</p>
        </div>
        
        <div class="content">
            <p>Dear {contact_name},</p>
            
            <p>Thank you for completing the Enterprise Scanner security assessment. We've analyzed your organization's cybersecurity posture and prepared a comprehensive report with actionable insights.</p>
            
            <div class="score-card">
                <h2>Your Security Score: {risk_score}/100</h2>
                <p><strong>Risk Level:</strong> {risk_level}</p>
                <p>{get_score_summary_for_email(risk_score)}</p>
            </div>
            
            <div class="recommendations">
                <h3>🎯 Priority Recommendations</h3>
                {"".join([f"<p><strong>{rec.get('title', 'Security Enhancement')}:</strong> {rec.get('description', 'Improve security posture')}</p>" for rec in recommendations[:3]])}
            </div>
            
            <div class="cta">
                <h3>Ready to Strengthen Your Security Posture?</h3>
                <p>Our enterprise security experts are ready to help you implement these recommendations and achieve industry-leading protection.</p>
                <p>
                    <a href="mailto:sales@enterprisescanner.com?subject=Consultation Request - {company_name}">Schedule Free Consultation</a> | 
                    <a href="https://enterprisescanner.com/demo">Request Demo</a>
                </p>
            </div>
            
            <h3>What's Next?</h3>
            <ul>
                <li>📞 <strong>Expert Consultation:</strong> Schedule a 30-minute call with our security specialists</li>
                <li>🎯 <strong>Custom Demo:</strong> See how Enterprise Scanner addresses your specific security gaps</li>
                <li>📊 <strong>ROI Analysis:</strong> Get detailed cost-benefit analysis for your organization</li>
                <li>📋 <strong>Implementation Plan:</strong> Receive step-by-step security improvement roadmap</li>
            </ul>
            
            <p>Questions? Reply to this email or contact our enterprise team at <a href="mailto:sales@enterprisescanner.com">sales@enterprisescanner.com</a> or call +1-800-SCANNER.</p>
            
            <p>Best regards,<br>
            The Enterprise Scanner Team</p>
        </div>
        
        <div class="footer">
            <p><strong>Enterprise Scanner</strong> | Premium Cybersecurity for Fortune 500 Companies</p>
            <p>🌐 <a href="https://enterprisescanner.com">enterprisescanner.com</a> | 📧 <a href="mailto:info@enterprisescanner.com">info@enterprisescanner.com</a></p>
            <p>Assessment ID: {assessment_id} | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
        </div>
    </body>
    </html>
    """
    
    # Send results to prospect
    send_email(
        to_email=prospect_email,
        subject=subject,
        html_content=html_content
    )

def get_risk_level_from_score(score):
    """Convert numeric score to risk level description"""
    if score >= 85:
        return 'Excellent'
    elif score >= 70:
        return 'Good'
    elif score >= 55:
        return 'Fair'
    elif score >= 40:
        return 'Poor'
    else:
        return 'Critical'

def get_score_summary_for_email(score):
    """Get email-appropriate score summary"""
    if score >= 85:
        return 'Your organization demonstrates strong security practices with comprehensive controls in place.'
    elif score >= 70:
        return 'Your security posture is solid with some areas for improvement to achieve enterprise-grade protection.'
    elif score >= 55:
        return 'Your security program has basic protections but requires significant enhancements to meet enterprise standards.'
    elif score >= 40:
        return 'Your organization faces considerable security risks that require immediate attention and investment.'
    else:
        return 'Your current security posture presents critical vulnerabilities that could result in significant business impact.'

def calculate_business_value(form_data, risk_score):
    """Calculate potential business value and ROI for prospect"""
    
    # Revenue-based calculations
    revenue_multipliers = {
        'under-10m': 10000000,
        '10m-100m': 50000000,
        '100m-1b': 500000000,
        '1b-10b': 5000000000,
        'over-10b': 15000000000
    }
    
    annual_revenue = revenue_multipliers.get(form_data.get('annualRevenue', 'under-10m'), 50000000)
    
    # Industry risk factors
    industry_risk = {
        'financial': 0.04,      # 4% of revenue at risk
        'healthcare': 0.035,    # 3.5% of revenue at risk
        'technology': 0.025,    # 2.5% of revenue at risk
        'retail': 0.03,         # 3% of revenue at risk
        'government': 0.02,     # 2% of revenue at risk
        'manufacturing': 0.025, # 2.5% of revenue at risk
        'energy': 0.035,        # 3.5% of revenue at risk
        'education': 0.015      # 1.5% of revenue at risk
    }.get(form_data.get('industry', 'technology'), 0.025)
    
    # Calculate potential losses based on risk score
    risk_multiplier = (100 - risk_score) / 100  # Higher risk = higher potential loss
    potential_annual_loss = annual_revenue * industry_risk * risk_multiplier
    
    # Enterprise Scanner platform cost (based on company size)
    platform_costs = {
        'startup': 50000,
        'small': 75000,
        'medium': 150000,
        'large': 300000,
        'enterprise': 500000
    }
    
    platform_cost = platform_costs.get(form_data.get('companySize', 'medium'), 150000)
    
    # Calculate ROI
    annual_savings = potential_annual_loss * 0.75  # 75% risk reduction
    roi_percentage = ((annual_savings - platform_cost) / platform_cost) * 100
    
    return {
        'potential_annual_loss': round(potential_annual_loss),
        'annual_savings': round(annual_savings),
        'platform_cost': platform_cost,
        'roi_percentage': round(roi_percentage, 1),
        'payback_months': round((platform_cost / (annual_savings / 12)), 1),
        'three_year_value': round((annual_savings * 3) - platform_cost)
    }

def generate_follow_up_actions(form_data, risk_score, is_high_value):
    """Generate specific follow-up actions based on assessment results"""
    
    actions = []
    
    if is_high_value:
        actions.append({
            'action': 'immediate_executive_outreach',
            'priority': 'high',
            'timeframe': '24 hours',
            'description': 'Schedule executive briefing with senior security consultant'
        })
    
    if risk_score < 50:
        actions.append({
            'action': 'urgent_security_consultation',
            'priority': 'critical',
            'timeframe': '12 hours',
            'description': 'Critical security gaps identified - urgent consultation recommended'
        })
    
    if risk_score < 70:
        actions.append({
            'action': 'demo_presentation',
            'priority': 'high',
            'timeframe': '48 hours',
            'description': 'Platform demonstration focusing on identified security gaps'
        })
    
    # Industry-specific actions
    industry = form_data.get('industry', '')
    if industry == 'financial':
        actions.append({
            'action': 'compliance_consultation',
            'priority': 'high',
            'timeframe': '72 hours',
            'description': 'Financial services compliance and risk management consultation'
        })
    elif industry == 'healthcare':
        actions.append({
            'action': 'hipaa_compliance_review',
            'priority': 'high',
            'timeframe': '72 hours',
            'description': 'HIPAA compliance gap analysis and remediation planning'
        })
    
    # Company size-specific actions
    if form_data.get('companySize') == 'enterprise':
        actions.append({
            'action': 'enterprise_assessment',
            'priority': 'medium',
            'timeframe': '1 week',
            'description': 'Comprehensive enterprise security architecture review'
        })
    
    return actions

def generate_enterprise_response(message, user_info):
    """Generate intelligent responses for Fortune 500 prospects"""
    
    # Executive-level templates for different topics
    templates = {
        'demo': "I'd be delighted to arrange a personalized demo of our enterprise platform. Our Fortune 500 clients typically see 300-800% ROI within the first year. What's your preferred time for a 30-minute executive briefing?",
        
        'pricing': "Enterprise Scanner offers flexible licensing designed for organizations of your scale. Our Fortune 500 partnerships typically range from $150K-$500K annually, with most clients seeing $2-5M in annual savings. Would you like me to prepare a custom ROI analysis?",
        
        'security': "Security is paramount in our enterprise platform. We maintain SOC 2 Type II compliance, offer end-to-end encryption, and have helped organizations achieve NIST Cybersecurity Framework compliance. What specific security standards does your organization require?",
        
        'roi': "Our ROI calculator shows enterprises of your size typically save $2-5M annually through breach prevention, compliance efficiency, and operational optimization. Based on industry benchmarks, what's your current annual cybersecurity budget?",
        
        'compliance': "We specialize in helping Fortune 500 companies achieve and maintain compliance with NIST, ISO 27001, SOX, GDPR, and industry-specific regulations. Our automated compliance reporting has reduced audit preparation time by 75% for major enterprises.",
        
        'integration': "Our platform integrates seamlessly with existing enterprise infrastructure including SIEM, SOAR, and major cloud platforms. We offer dedicated technical consultants and white-glove onboarding for Fortune 500 implementations.",
        
        'support': "Enterprise clients receive 24/7 priority support, dedicated customer success managers, and direct access to our security researchers. Our average response time for critical issues is under 15 minutes."
    }
    
    # Keyword matching for intelligent responses
    if any(word in message for word in ['demo', 'demonstration', 'show me', 'see it']):
        return templates['demo']
    elif any(word in message for word in ['price', 'cost', 'budget', 'expensive']):
        return templates['pricing']
    elif any(word in message for word in ['security', 'secure', 'safe', 'protection']):
        return templates['security']
    elif any(word in message for word in ['roi', 'return', 'savings', 'value']):
        return templates['roi']
    elif any(word in message for word in ['compliance', 'regulate', 'audit', 'standard']):
        return templates['compliance']
    elif any(word in message for word in ['integrate', 'api', 'connect', 'existing']):
        return templates['integration']
    elif any(word in message for word in ['support', 'help', 'assistance', 'service']):
        return templates['support']
    else:
        return "Thank you for your interest in Enterprise Scanner. As a platform designed specifically for Fortune 500 organizations, we focus on enterprise-grade vulnerability management and compliance automation. How can I help you evaluate our solution for your security needs?"

def should_escalate_to_human(message, user_info):
    """Determine if chat should be escalated to human consultant"""
    
    # High-value escalation triggers
    escalation_keywords = [
        'ceo', 'cio', 'ciso', 'chief', 'director', 'vp', 'vice president',
        'urgent', 'critical', 'breach', 'incident', 'emergency',
        'contract', 'procurement', 'purchase', 'budget approval',
        'technical', 'architecture', 'detailed', 'complex'
    ]
    
    # Fortune 500 company domains
    enterprise_domains = [
        'jpmorgan', 'microsoft', 'unitedhealth', 'berkshire', 'amazon',
        'apple', 'walmart', 'google', 'exxon', 'cvs'
    ]
    
    # Check for high-value indicators
    if any(keyword in message.lower() for keyword in escalation_keywords):
        return True
    
    # Check user email domain for Fortune 500 companies
    user_email = user_info.get('email', '')
    if any(domain in user_email.lower() for domain in enterprise_domains):
        return True
    
    return False

def get_escalation_reason(message):
    """Get specific reason for escalation"""
    if any(word in message.lower() for word in ['ceo', 'cio', 'ciso', 'chief']):
        return 'executive_level'
    elif any(word in message.lower() for word in ['technical', 'architecture', 'integration']):
        return 'technical_discussion'
    elif any(word in message.lower() for word in ['contract', 'procurement', 'purchase']):
        return 'procurement_inquiry'
    elif any(word in message.lower() for word in ['urgent', 'critical', 'emergency']):
        return 'urgent_matter'
    else:
        return 'general_inquiry'

# API Key Management Storage (In production, use database)
api_keys_storage = {}

@app.route('/api/keys/generate', methods=['POST'])
def generate_api_key():
    """Generate a new API key for authentication"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    key_name = data.get('name', '').strip()
    permissions = data.get('permissions', 'read')
    
    if not key_name:
        return jsonify({'error': 'Key name is required'}), 400
    
    # Generate unique API key
    import secrets
    api_key = f"es_{secrets.token_urlsafe(32)}"
    
    # Store key information
    key_data = {
        'id': str(len(api_keys_storage) + 1),
        'name': key_name,
        'key': api_key,
        'permissions': permissions,
        'created': datetime.utcnow().isoformat(),
        'last_used': None,
        'requests_count': 0
    }
    
    api_keys_storage[api_key] = key_data
    
    return jsonify({
        'status': 'success',
        'message': 'API key generated successfully',
        'key_data': {
            'id': key_data['id'],
            'name': key_data['name'],
            'key': api_key,
            'permissions': key_data['permissions'],
            'created': key_data['created']
        }
    })

@app.route('/api/keys', methods=['GET'])
def list_api_keys():
    """List all API keys (without showing the actual key values)"""
    keys_list = []
    for key, data in api_keys_storage.items():
        keys_list.append({
            'id': data['id'],
            'name': data['name'],
            'permissions': data['permissions'],
            'created': data['created'],
            'last_used': data['last_used'],
            'requests_count': data['requests_count'],
            'key_preview': f"{key[:8]}...{key[-4:]}"
        })
    
    return jsonify({
        'status': 'success',
        'keys': keys_list,
        'total_keys': len(keys_list)
    })

@app.route('/api/keys/<key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    """Delete an API key"""
    # Find and delete key by ID
    key_to_delete = None
    for key, data in api_keys_storage.items():
        if data['id'] == key_id:
            key_to_delete = key
            break
    
    if key_to_delete:
        del api_keys_storage[key_to_delete]
        return jsonify({
            'status': 'success',
            'message': 'API key deleted successfully'
        })
    else:
        return jsonify({'error': 'API key not found'}), 404

def validate_api_key(api_key):
    """Validate API key and update usage statistics"""
    if api_key in api_keys_storage:
        # Update last used timestamp and request count
        api_keys_storage[api_key]['last_used'] = datetime.utcnow().isoformat()
        api_keys_storage[api_key]['requests_count'] += 1
        return True
    return False

def require_api_key(f):
    """Decorator to require API key authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required in X-API-Key header'}), 401
        
        if not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/documentation', methods=['GET'])
def api_documentation():
    """Serve API documentation metadata"""
    return jsonify({
        'api_version': '1.0.0',
        'base_url': 'https://api.enterprisescanner.com/v1',
        'documentation_url': 'https://enterprisescanner.com/api-docs',
        'endpoints': [
            {
                'path': '/health',
                'method': 'GET',
                'description': 'Health check endpoint',
                'authentication': False,
                'parameters': []
            },
            {
                'path': '/security-assessment',
                'method': 'POST',
                'description': 'Submit security assessment',
                'authentication': True,
                'parameters': [
                    {'name': 'contactName', 'type': 'string', 'required': True},
                    {'name': 'email', 'type': 'string', 'required': True},
                    {'name': 'companyName', 'type': 'string', 'required': True},
                    {'name': 'jobTitle', 'type': 'string', 'required': False},
                    {'name': 'companySize', 'type': 'string', 'required': False},
                    {'name': 'industry', 'type': 'string', 'required': False}
                ]
            },
            {
                'path': '/chat/send',
                'method': 'POST',
                'description': 'Send chat message',
                'authentication': True,
                'parameters': [
                    {'name': 'message', 'type': 'string', 'required': True},
                    {'name': 'userInfo', 'type': 'object', 'required': False}
                ]
            },
            {
                'path': '/chat/escalate',
                'method': 'POST',
                'description': 'Escalate chat to human consultant',
                'authentication': True,
                'parameters': [
                    {'name': 'chatId', 'type': 'string', 'required': True},
                    {'name': 'reason', 'type': 'string', 'required': True},
                    {'name': 'messages', 'type': 'array', 'required': False},
                    {'name': 'userInfo', 'type': 'object', 'required': False}
                ]
            },
            {
                'path': '/analytics/metrics',
                'method': 'GET',
                'description': 'Get analytics metrics',
                'authentication': True,
                'parameters': [
                    {'name': 'timeframe', 'type': 'string', 'required': False},
                    {'name': 'metric_type', 'type': 'string', 'required': False}
                ]
            },
            {
                'path': '/contact/submit',
                'method': 'POST',
                'description': 'Submit contact form',
                'authentication': True,
                'parameters': [
                    {'name': 'name', 'type': 'string', 'required': True},
                    {'name': 'email', 'type': 'string', 'required': True},
                    {'name': 'company', 'type': 'string', 'required': False},
                    {'name': 'message', 'type': 'string', 'required': True}
                ]
            }
        ],
        'authentication': {
            'type': 'API Key',
            'header': 'X-API-Key',
            'description': 'Include your API key in the X-API-Key header'
        },
        'rate_limits': {
            'standard': '1,000 requests/hour',
            'enterprise': '10,000 requests/hour',
            'partner': 'Unlimited'
        }
    })

@app.route('/api/deployment/verify', methods=['GET'])
def verify_deployment():
    """Comprehensive deployment verification with system health checks"""
    
    verification_results = {
        'deployment_status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {},
        'services': {},
        'warnings': [],
        'errors': []
    }
    
    try:
        # Email System Verification
        try:
            # Test SMTP connection
            import smtplib
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            verification_results['checks']['email_smtp'] = {
                'status': 'connected',
                'message': 'SMTP server accessible'
            }
            server.quit()
        except Exception as e:
            verification_results['checks']['email_smtp'] = {
                'status': 'warning',
                'message': f'SMTP connection issue: {str(e)}'
            }
            verification_results['warnings'].append('Email system may need configuration')
        
        # Database Connectivity (if applicable)
        verification_results['checks']['database'] = {
            'status': 'not_configured',
            'message': 'Database not yet implemented - using in-memory storage'
        }
        
        # File System Permissions
        import os
        try:
            test_file = 'temp_deployment_test.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            verification_results['checks']['file_system'] = {
                'status': 'healthy',
                'message': 'File system read/write access confirmed'
            }
        except Exception as e:
            verification_results['checks']['file_system'] = {
                'status': 'error',
                'message': f'File system access error: {str(e)}'
            }
            verification_results['errors'].append('File system permissions issue')
        
        # Memory Usage
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            verification_results['checks']['memory'] = {
                'status': 'healthy' if memory_percent < 80 else 'warning',
                'usage_percent': memory_percent,
                'message': f'Memory usage: {memory_percent}%'
            }
        except ImportError:
            verification_results['checks']['memory'] = {
                'status': 'not_available',
                'message': 'psutil not installed - memory monitoring unavailable'
            }
        
        # Service Status
        verification_results['services'] = {
            'live_chat': {
                'status': 'active',
                'endpoint': '/api/chat/send',
                'features': ['Fortune 500 detection', 'Auto-escalation', 'Email notifications']
            },
            'security_assessment': {
                'status': 'active',
                'endpoint': '/api/assessment/submit',
                'features': ['Risk scoring', 'PDF generation', 'Lead routing']
            },
            'analytics_dashboard': {
                'status': 'active',
                'endpoint': '/api/analytics/metrics',
                'features': ['Real-time metrics', 'Industry benchmarking', 'Threat intelligence']
            },
            'email_automation': {
                'status': 'configured',
                'endpoints': ['/api/contact/submit', '/api/chat/escalate'],
                'features': ['Lead notifications', 'Assessment results', 'Chat escalations']
            }
        }
        
        # Environment Configuration
        verification_results['environment'] = {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'flask_version': '2.3.0+',
            'business_emails_configured': len(BUSINESS_EMAILS),
            'email_addresses': list(BUSINESS_EMAILS.keys())
        }
        
        # Determine overall status
        if verification_results['errors']:
            verification_results['deployment_status'] = 'error'
        elif verification_results['warnings']:
            verification_results['deployment_status'] = 'warning'
        else:
            verification_results['deployment_status'] = 'healthy'
        
        # Next Steps Recommendations
        verification_results['recommendations'] = []
        
        if verification_results['checks']['email_smtp']['status'] != 'connected':
            verification_results['recommendations'].append({
                'priority': 'high',
                'action': 'Configure Google Workspace email credentials in environment variables',
                'details': 'Set EMAIL_PASSWORD for automated notifications'
            })
        
        if verification_results['checks']['database']['status'] == 'not_configured':
            verification_results['recommendations'].append({
                'priority': 'medium',
                'action': 'Consider implementing persistent database storage',
                'details': 'PostgreSQL recommended for production Fortune 500 lead management'
            })
        
        verification_results['recommendations'].append({
            'priority': 'medium',
            'action': 'Deploy Phase 2 Week 2 frontend features to production',
            'details': 'Upload live chat, security assessment, and analytics dashboard to https://enterprisescanner.com'
        })
        
    except Exception as e:
        verification_results['deployment_status'] = 'error'
        verification_results['errors'].append(f'Verification failed: {str(e)}')
    
    return jsonify(verification_results)

@app.route('/api/partners/apply', methods=['POST'])
def submit_partner_application():
    """Submit partner application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['companyName', 'partnerTier', 'contactName', 'contactTitle', 'email', 'phone', 'annualRevenue', 'securityFocus']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check for duplicate applications
        if data['email'] in partner_applications:
            return jsonify({'error': 'Application with this email already exists'}), 409
        
        # Generate application ID
        application_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{len(partner_applications) + 1:04d}"
        
        # Store application
        application_data = {
            **data,
            'id': application_id,
            'status': 'pending',
            'submitted_at': datetime.now().isoformat(),
            'reviewed_by': None,
            'reviewed_at': None,
            'notes': ''
        }
        
        partner_applications[data['email']] = application_data
        
        # Send notification emails
        send_partner_application_notification(application_data)
        
        return jsonify({
            'success': True,
            'application_id': application_id,
            'message': 'Application submitted successfully',
            'next_steps': 'We will review your application and contact you within 48 hours'
        })
        
    except Exception as e:
        print(f"Partner application error: {e}")
        return jsonify({'error': 'Failed to process application'}), 500

@app.route('/api/partners/login', methods=['POST'])
def partner_login():
    """Partner authentication"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if partner exists and is approved
        if email in partner_applications:
            application = partner_applications[email]
            if application['status'] == 'approved':
                # In production, verify password hash
                partner_data = {
                    'id': application['id'],
                    'companyName': application['companyName'],
                    'contactName': application['contactName'],
                    'email': application['email'],
                    'partnerTier': application['partnerTier'],
                    'status': application['status']
                }
                return jsonify({
                    'success': True,
                    'partner': partner_data,
                    'message': 'Login successful'
                })
            else:
                return jsonify({'error': 'Application still pending approval'}), 403
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Partner login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500

@app.route('/api/partners', methods=['GET'])
@require_api_key
def get_partners():
    """Get all partners (admin only)"""
    try:
        # Filter sensitive data
        partner_list = []
        for email, application in partner_applications.items():
            partner_list.append({
                'id': application['id'],
                'companyName': application['companyName'],
                'contactName': application['contactName'],
                'email': application['email'],
                'partnerTier': application['partnerTier'],
                'status': application['status'],
                'submitted_at': application['submitted_at'],
                'reviewed_at': application.get('reviewed_at'),
                'annualRevenue': application['annualRevenue']
            })
        
        return jsonify({
            'partners': partner_list,
            'total': len(partner_list),
            'by_status': {
                'pending': len([p for p in partner_list if p['status'] == 'pending']),
                'approved': len([p for p in partner_list if p['status'] == 'approved']),
                'rejected': len([p for p in partner_list if p['status'] == 'rejected'])
            }
        })
        
    except Exception as e:
        print(f"Get partners error: {e}")
        return jsonify({'error': 'Failed to retrieve partners'}), 500

@app.route('/api/partners/<application_id>/approve', methods=['POST'])
@require_api_key
def approve_partner(application_id):
    """Approve partner application"""
    try:
        # Find application by ID
        application = None
        for email, app in partner_applications.items():
            if app['id'] == application_id:
                application = app
                break
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Update status
        application['status'] = 'approved'
        application['reviewed_at'] = datetime.now().isoformat()
        application['reviewed_by'] = 'admin'  # In production, use authenticated user
        
        # Add to partners list
        partners[application['email']] = application
        
        # Send approval notification
        send_partner_approval_notification(application)
        
        return jsonify({
            'success': True,
            'message': 'Partner application approved',
            'partner_id': application['id']
        })
        
    except Exception as e:
        print(f"Approve partner error: {e}")
        return jsonify({'error': 'Failed to approve application'}), 500

def send_partner_application_notification(application_data):
    """Send notification email for new partner application"""
    try:
        # Email to partnerships team
        subject = f"New Partner Application: {application_data['companyName']}"
        
        body = f"""
        New Partner Application Received
        
        Company: {application_data['companyName']}
        Contact: {application_data['contactName']} ({application_data['contactTitle']})
        Email: {application_data['email']}
        Phone: {application_data['phone']}
        Desired Tier: {application_data['partnerTier']}
        Annual Revenue: {application_data['annualRevenue']}
        Security Experience: {application_data['securityFocus']}
        
        Client Types: {', '.join(application_data.get('clientTypes', []))}
        
        Experience: {application_data.get('experience', 'Not provided')}
        
        Partnership Goals: {application_data.get('expectations', 'Not provided')}
        
        Application ID: {application_data['id']}
        Submitted: {application_data['submitted_at']}
        
        Review application at: {DOMAIN_CONFIG['url']}/admin/partners/{application_data['id']}
        """
        
        send_email('partnerships@enterprisescanner.com', subject, body)
        
        # Confirmation email to applicant
        confirmation_subject = "Partner Application Received - Enterprise Scanner"
        confirmation_body = f"""
        Dear {application_data['contactName']},
        
        Thank you for your interest in joining the Enterprise Scanner Partner Network.
        
        We have received your application for the {application_data['partnerTier']} tier and will review it within 48 hours.
        
        Application Details:
        - Company: {application_data['companyName']}
        - Application ID: {application_data['id']}
        - Submitted: {application_data['submitted_at']}
        
        Our partnership team will contact you shortly with next steps.
        
        Best regards,
        Enterprise Scanner Partnership Team
        partnerships@enterprisescanner.com
        """
        
        send_email(application_data['email'], confirmation_subject, confirmation_body)
        
    except Exception as e:
        print(f"Partner notification email error: {e}")

def send_partner_approval_notification(partner_data):
    """Send approval notification to partner"""
    try:
        subject = f"Welcome to Enterprise Scanner Partner Network - {partner_data['partnerTier'].title()} Partner"
        
        commission_rates = {
            'authorized': '25%',
            'gold': '30%',
            'platinum': '35%'
        }
        
        commission_rate = commission_rates.get(partner_data['partnerTier'], '25%')
        
        body = f"""
        Congratulations {partner_data['contactName']}!
        
        Your application to join the Enterprise Scanner Partner Network has been approved.
        
        Partner Details:
        - Company: {partner_data['companyName']}
        - Partner Tier: {partner_data['partnerTier'].title()}
        - Commission Rate: {commission_rate}
        - Partner ID: {partner_data['id']}
        
        Next Steps:
        1. Access your partner portal: {DOMAIN_CONFIG['url']}/partner-portal.html
        2. Complete partner training program
        3. Download sales and marketing materials
        4. Schedule your partner onboarding call
        
        Your dedicated partner manager will contact you within 24 hours to begin the onboarding process.
        
        Welcome to the team!
        
        Enterprise Scanner Partnership Team
        partnerships@enterprisescanner.com
        """
        
        send_email(partner_data['email'], subject, body)
        
    except Exception as e:
        print(f"Partner approval notification error: {e}")

# CRM API Endpoints
@app.route('/api/crm/leads', methods=['GET'])
def get_leads():
    """Get all leads with filtering and pagination"""
    try:
        # Get query parameters
        status = request.args.get('status', '')
        company_type = request.args.get('company_type', '')
        deal_value_range = request.args.get('deal_value_range', '')
        assigned_to = request.args.get('assigned_to', '')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        lead_repo = LeadRepository() if DATABASE_AVAILABLE else MockLeadRepository()
        leads = lead_repo.get_filtered_leads(
            status=status,
            company_type=company_type,
            deal_value_range=deal_value_range,
            assigned_to=assigned_to,
            search=search,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'status': 'success',
            'data': leads,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': lead_repo.count_filtered_leads(status, company_type, deal_value_range, assigned_to, search)
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/crm/leads', methods=['POST'])
def create_lead():
    """Create a new lead"""
    try:
        data = request.json
        lead_repo = LeadRepository() if DATABASE_AVAILABLE else MockLeadRepository()
        
        # Calculate lead score
        lead_score = calculate_lead_score(data)
        
        lead_data = {
            'first_name': data.get('firstName'),
            'last_name': data.get('lastName'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'company': data.get('company'),
            'title': data.get('title'),
            'status': data.get('status', 'new'),
            'source': data.get('source'),
            'deal_value': data.get('dealValue', 0),
            'lead_score': lead_score,
            'notes': data.get('notes'),
            'assigned_to': data.get('assignedTo'),
            'created_at': datetime.utcnow(),
            'next_follow_up': datetime.utcnow() + datetime.timedelta(days=1)
        }
        
        lead_id = lead_repo.create_lead(lead_data)
        
        # Log activity
        activity_repo = LeadActivityRepository() if DATABASE_AVAILABLE else MockActivityRepository()
        activity_repo.log_activity(lead_id, 'lead_created', f"New lead created: {data.get('firstName')} {data.get('lastName')}")
        
        # Schedule follow-up
        schedule_automated_follow_up(lead_id, lead_data['status'])
        
        return jsonify({
            'status': 'success',
            'data': {'id': lead_id, 'score': lead_score},
            'message': 'Lead created successfully'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/crm/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead information"""
    try:
        data = request.json
        lead_repo = LeadRepository() if DATABASE_AVAILABLE else MockLeadRepository()
        
        # Update lead score if relevant fields changed
        if any(field in data for field in ['company', 'title', 'dealValue', 'status']):
            current_lead = lead_repo.get_lead_by_id(lead_id)
            if current_lead:
                updated_data = {**current_lead, **data}
                data['lead_score'] = calculate_lead_score(updated_data)
        
        lead_repo.update_lead(lead_id, data)
        
        # Log activity
        activity_repo = LeadActivityRepository() if DATABASE_AVAILABLE else MockActivityRepository()
        activity_repo.log_activity(lead_id, 'lead_updated', f"Lead information updated")
        
        return jsonify({
            'status': 'success',
            'message': 'Lead updated successfully'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/crm/leads/<int:lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    """Update lead status (for pipeline drag-and-drop)"""
    try:
        data = request.json
        new_status = data.get('status')
        
        lead_repo = LeadRepository() if DATABASE_AVAILABLE else MockLeadRepository()
        lead_repo.update_lead_status(lead_id, new_status)
        
        # Log activity
        activity_repo = LeadActivityRepository() if DATABASE_AVAILABLE else MockActivityRepository()
        activity_repo.log_activity(lead_id, 'status_changed', f"Status changed to {new_status}")
        
        # Schedule appropriate follow-up
        schedule_automated_follow_up(lead_id, new_status)
        
        return jsonify({
            'status': 'success',
            'message': f'Lead status updated to {new_status}'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/crm/leads/<int:lead_id>/activities', methods=['GET'])
def get_lead_activities(lead_id):
    """Get lead activity history"""
    try:
        activity_repo = LeadActivityRepository() if DATABASE_AVAILABLE else MockActivityRepository()
        activities = activity_repo.get_lead_activities(lead_id)
        
        return jsonify({
            'status': 'success',
            'data': activities
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/crm/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Get CRM dashboard metrics"""
    try:
        lead_repo = LeadRepository() if DATABASE_AVAILABLE else MockLeadRepository()
        
        # Calculate key metrics
        total_leads = lead_repo.count_total_leads()
        qualified_leads = lead_repo.count_qualified_leads()
        closed_deals = lead_repo.count_closed_deals()
        total_revenue = lead_repo.get_total_revenue()
        
        # Conversion metrics
        conversion_rate = (closed_deals / total_leads * 100) if total_leads > 0 else 0
        avg_deal_size = (total_revenue / closed_deals) if closed_deals > 0 else 0
        avg_sales_cycle = lead_repo.get_average_sales_cycle()
        
        # Pipeline data
        pipeline_data = lead_repo.get_pipeline_counts()
        
        # Recent activity
        activity_repo = LeadActivityRepository() if DATABASE_AVAILABLE else MockActivityRepository()
        recent_activities = activity_repo.get_recent_activities(limit=10)
        
        # Top opportunities
        top_opportunities = lead_repo.get_top_opportunities(limit=5)
        
        return jsonify({
            'status': 'success',
            'data': {
                'metrics': {
                    'total_leads': total_leads,
                    'qualified_leads': qualified_leads,
                    'closed_deals': closed_deals,
                    'total_revenue': total_revenue,
                    'conversion_rate': round(conversion_rate, 1),
                    'avg_deal_size': round(avg_deal_size, 0),
                    'avg_sales_cycle': avg_sales_cycle
                },
                'pipeline': pipeline_data,
                'recent_activities': recent_activities,
                'top_opportunities': top_opportunities
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/crm/analytics/forecast', methods=['GET'])
def get_revenue_forecast():
    """Get revenue forecast data"""
    try:
        forecast_type = request.args.get('type', 'likely')  # conservative, likely, optimistic
        months = int(request.args.get('months', 12))
        
        lead_repo = LeadRepository() if DATABASE_AVAILABLE else MockLeadRepository()
        forecast_data = lead_repo.get_revenue_forecast(forecast_type, months)
        
        return jsonify({
            'status': 'success',
            'data': forecast_data
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def calculate_lead_score(lead_data):
    """Calculate lead score based on various factors"""
    score = 0
    
    # Company scoring (40 points max)
    company = lead_data.get('company', '')
    deal_value = float(lead_data.get('dealValue', 0))
    
    if is_fortune_500_company(company):
        score += 40
    elif deal_value > 500000:
        score += 30
    elif deal_value > 100000:
        score += 20
    else:
        score += 10
    
    # Title scoring (25 points max)
    title = lead_data.get('title', '').lower()
    if 'ciso' in title or 'chief information security' in title:
        score += 25
    elif 'cto' in title or 'chief technology' in title:
        score += 20
    elif 'director' in title or 'manager' in title:
        score += 15
    else:
        score += 10
    
    # Engagement scoring (20 points max)
    status = lead_data.get('status', 'new')
    status_scores = {
        'demo_scheduled': 20,
        'qualified': 15,
        'contacted': 10,
        'new': 5
    }
    score += status_scores.get(status, 5)
    
    # Source scoring (15 points max)
    source = lead_data.get('source', '')
    source_scores = {
        'referral': 15,
        'partner': 10,
        'website': 5,
        'advertisement': 3,
        'cold_outreach': 1
    }
    score += source_scores.get(source, 1)
    
    return min(score, 100)

def is_fortune_500_company(company):
    """Check if company is Fortune 500"""
    fortune_companies = [
        'Microsoft', 'Apple', 'Amazon', 'Alphabet', 'Google', 'Meta', 'Tesla',
        'Berkshire Hathaway', 'NVIDIA', 'JPMorgan Chase', 'Johnson & Johnson',
        'Visa', 'Procter & Gamble', 'Mastercard', 'UnitedHealth', 'Home Depot',
        'Bank of America', 'Pfizer', 'Coca-Cola', 'PepsiCo', 'Walt Disney'
    ]
    
    return any(fc.lower() in company.lower() for fc in fortune_companies)

def schedule_automated_follow_up(lead_id, status):
    """Schedule automated follow-up based on lead status"""
    follow_up_templates = {
        'new': {
            'days': 1,
            'template': 'welcome_email',
            'subject': 'Welcome to Enterprise Scanner - Next Steps'
        },
        'contacted': {
            'days': 3,
            'template': 'follow_up_email',
            'subject': 'Following up on your cybersecurity needs'
        },
        'qualified': {
            'days': 2,
            'template': 'demo_invitation',
            'subject': 'Schedule Your Personal Security Assessment Demo'
        },
        'demo_scheduled': {
            'days': 1,
            'template': 'demo_reminder',
            'subject': 'Reminder: Your Enterprise Scanner Demo Tomorrow'
        },
        'proposal_sent': {
            'days': 5,
            'template': 'proposal_follow_up',
            'subject': 'Following up on your Enterprise Scanner proposal'
        }
    }
    
    if status in follow_up_templates:
        template_data = follow_up_templates[status]
        follow_up_date = datetime.utcnow() + datetime.timedelta(days=template_data['days'])
        
        # In a real implementation, this would schedule an actual email
        print(f"Scheduled {template_data['template']} for lead {lead_id} on {follow_up_date}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])