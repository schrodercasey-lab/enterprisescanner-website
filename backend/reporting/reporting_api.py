"""
Reporting API Endpoints
RESTful API for generating and retrieving security reports

Endpoints:
- Executive summary reports
- Technical detailed reports
- Compliance framework reports
- Trend and comparison reports

Author: Enterprise Scanner Security Team
Version: 1.0.0
"""

from flask import Blueprint, jsonify, request, send_file
from typing import Dict, Any, Optional
from datetime import datetime
import os
import tempfile

from .report_generator import ExecutiveReportGenerator, TechnicalReportGenerator
from .compliance_reports import ComplianceReportGenerator, TrendReportGenerator

# Create Flask Blueprint
reporting_bp = Blueprint('reporting', __name__, url_prefix='/api/reports')

# Initialize report generators
executive_generator = ExecutiveReportGenerator()
technical_generator = TechnicalReportGenerator()
compliance_generator = ComplianceReportGenerator()
trend_generator = TrendReportGenerator()

# Report storage directory (use environment variable)
REPORT_DIR = os.getenv('REPORT_STORAGE_PATH', tempfile.gettempdir())


@reporting_bp.route('/executive/<assessment_id>', methods=['POST'])
def generate_executive_report(assessment_id: str):
    """
    Generate executive summary report
    
    Args:
        assessment_id: Assessment ID to generate report for
    
    Request Body:
        {
            "assessment_data": {...},  // Complete assessment results
            "trend_data": [...]  // Optional historical trend data
        }
    
    Returns:
        PDF report file
    
    Example:
        POST /api/reports/executive/abc-123
    """
    try:
        data = request.get_json()
        assessment_data = data.get('assessment_data')
        trend_data = data.get('trend_data')
        
        if not assessment_data:
            return jsonify({
                'success': False,
                'error': 'assessment_data is required'
            }), 400
        
        # Generate report filename
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"executive_report_{company_name}_{timestamp}.pdf"
        output_path = os.path.join(REPORT_DIR, filename)
        
        # Generate report
        executive_generator.generate(assessment_data, output_path, trend_data)
        
        # Return PDF file
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/technical/<assessment_id>', methods=['POST'])
def generate_technical_report(assessment_id: str):
    """
    Generate technical detailed report
    
    Args:
        assessment_id: Assessment ID to generate report for
    
    Request Body:
        {
            "assessment_data": {...}  // Complete assessment results
        }
    
    Returns:
        PDF report file
    
    Example:
        POST /api/reports/technical/abc-123
    """
    try:
        data = request.get_json()
        assessment_data = data.get('assessment_data')
        
        if not assessment_data:
            return jsonify({
                'success': False,
                'error': 'assessment_data is required'
            }), 400
        
        # Generate report filename
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"technical_report_{company_name}_{timestamp}.pdf"
        output_path = os.path.join(REPORT_DIR, filename)
        
        # Generate report
        technical_generator.generate(assessment_data, output_path)
        
        # Return PDF file
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/compliance/<framework>/<assessment_id>', methods=['POST'])
def generate_compliance_report(framework: str, assessment_id: str):
    """
    Generate compliance framework report
    
    Args:
        framework: Compliance framework (cis, nist, pci_dss, hipaa)
        assessment_id: Assessment ID to generate report for
    
    Request Body:
        {
            "assessment_data": {...}  // Complete assessment results
        }
    
    Returns:
        PDF report file
    
    Example:
        POST /api/reports/compliance/cis/abc-123
    """
    try:
        # Validate framework
        valid_frameworks = ['cis', 'nist', 'pci_dss', 'hipaa']
        if framework not in valid_frameworks:
            return jsonify({
                'success': False,
                'error': f'Invalid framework. Valid options: {", ".join(valid_frameworks)}'
            }), 400
        
        data = request.get_json()
        assessment_data = data.get('assessment_data')
        
        if not assessment_data:
            return jsonify({
                'success': False,
                'error': 'assessment_data is required'
            }), 400
        
        # Generate report filename
        company_name = assessment_data.get('assessment_metadata', {}).get('company_name', 'Unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{framework}_compliance_{company_name}_{timestamp}.pdf"
        output_path = os.path.join(REPORT_DIR, filename)
        
        # Generate appropriate compliance report
        if framework == 'cis':
            compliance_generator.generate_cis_report(assessment_data, output_path)
        elif framework == 'nist':
            compliance_generator.generate_nist_report(assessment_data, output_path)
        else:
            # PCI-DSS and HIPAA use similar structure to CIS for now
            compliance_generator.generate_cis_report(assessment_data, output_path)
        
        # Return PDF file
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/trend/quarterly/<company_name>', methods=['POST'])
def generate_quarterly_trend_report(company_name: str):
    """
    Generate quarterly trend report
    
    Args:
        company_name: Company name for trend analysis
    
    Request Body:
        {
            "trend_data": [...]  // List of historical assessment snapshots
        }
    
    Returns:
        PDF report file
    
    Example:
        POST /api/reports/trend/quarterly/AcmeCorp
    """
    try:
        data = request.get_json()
        trend_data = data.get('trend_data')
        
        if not trend_data or len(trend_data) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 assessment snapshots required for trend analysis'
            }), 400
        
        # Generate report filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quarterly_trend_{company_name}_{timestamp}.pdf"
        output_path = os.path.join(REPORT_DIR, filename)
        
        # Generate report
        trend_generator.generate_quarterly_report(trend_data, company_name, output_path)
        
        # Return PDF file
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reporting_bp.route('/available', methods=['GET'])
def get_available_reports():
    """
    Get list of available report types
    
    Returns:
        JSON response with report type definitions
    
    Example:
        GET /api/reports/available
    """
    reports = [
        {
            'type': 'executive',
            'name': 'Executive Summary Report',
            'description': 'Board-ready summary for C-level executives',
            'audience': 'Executive Leadership, Board Members',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/executive/<assessment_id>'
        },
        {
            'type': 'technical',
            'name': 'Technical Detailed Report',
            'description': 'Complete technical findings for security teams',
            'audience': 'Security Teams, IT Managers',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/technical/<assessment_id>'
        },
        {
            'type': 'compliance_cis',
            'name': 'CIS Benchmarks Compliance Report',
            'description': 'CIS Docker, Kubernetes, and Cloud compliance',
            'audience': 'Compliance Officers, Auditors',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/compliance/cis/<assessment_id>'
        },
        {
            'type': 'compliance_nist',
            'name': 'NIST Cybersecurity Framework Report',
            'description': 'NIST CSF five functions compliance',
            'audience': 'Compliance Officers, Auditors',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/compliance/nist/<assessment_id>'
        },
        {
            'type': 'compliance_pci_dss',
            'name': 'PCI-DSS Compliance Report',
            'description': 'Payment card industry compliance',
            'audience': 'Compliance Officers, Finance Teams',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/compliance/pci_dss/<assessment_id>'
        },
        {
            'type': 'compliance_hipaa',
            'name': 'HIPAA Security Rule Report',
            'description': 'Healthcare information security compliance',
            'audience': 'Compliance Officers, Healthcare IT',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/compliance/hipaa/<assessment_id>'
        },
        {
            'type': 'trend_quarterly',
            'name': 'Quarterly Trend Report',
            'description': 'Quarterly security posture trend analysis',
            'audience': 'Executive Leadership, Security Teams',
            'format': 'PDF',
            'endpoint': 'POST /api/reports/trend/quarterly/<company_name>'
        }
    ]
    
    return jsonify({
        'success': True,
        'reports': reports,
        'count': len(reports),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@reporting_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for reporting API
    
    Returns:
        JSON response with service status
    
    Example:
        GET /api/reports/health
    """
    return jsonify({
        'success': True,
        'service': 'reporting_api',
        'status': 'operational',
        'generators': {
            'executive': 'ready',
            'technical': 'ready',
            'compliance': 'ready',
            'trend': 'ready'
        },
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# Error handlers
@reporting_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@reporting_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# Example Flask app integration
def create_reporting_app():
    """
    Create Flask app with reporting blueprint
    
    Returns:
        Configured Flask app
    """
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(reporting_bp)
    
    return app


if __name__ == '__main__':
    # Run standalone for testing
    app = create_reporting_app()
    app.run(debug=True, host='0.0.0.0', port=5002)
