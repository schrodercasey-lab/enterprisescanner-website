"""
Threat Intelligence API Endpoints
Provides real-time threat intelligence data for Enterprise Scanner platform
"""

from flask import Blueprint, jsonify, request
import asyncio
import json
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.threat_intelligence import threat_intel_manager
except ImportError:
    # Mock threat intel manager if not available
    class MockThreatIntelManager:
        def get_threat_intelligence_summary(self):
            return {'status': 'demo', 'threats': []}
        def search_threats(self, **kwargs):
            return []
        def get_threat_by_id(self, threat_id):
            return None
    threat_intel_manager = MockThreatIntelManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
threat_intel_bp = Blueprint('threat_intel', __name__)

@threat_intel_bp.route('/api/threat-intelligence/dashboard', methods=['GET'])
def get_threat_dashboard():
    """
    Get comprehensive threat intelligence dashboard data
    """
    try:
        summary = threat_intel_manager.get_threat_intelligence_summary()
        
        response_data = {
            'status': 'success',
            'data': summary,
            'timestamp': datetime.now().isoformat(),
            'source': 'Enterprise Scanner Threat Intelligence'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating threat dashboard: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve threat intelligence data',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/cves', methods=['GET'])
def get_latest_cves():
    """
    Get latest CVE data with filtering options
    """
    try:
        # Get query parameters
        days_back = request.args.get('days', 7, type=int)
        severity = request.args.get('severity', '')
        limit = request.args.get('limit', 50, type=int)
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        cves = loop.run_until_complete(
            threat_intel_manager.fetch_latest_cves(days_back=days_back, limit=limit)
        )
        loop.close()
        
        # Filter by severity if specified
        if severity:
            cves = [cve for cve in cves if cve.severity.lower() == severity.lower()]
        
        # Convert to dict for JSON serialization
        cves_data = []
        for cve in cves:
            cves_data.append({
                'cve_id': cve.cve_id,
                'description': cve.description,
                'severity': cve.severity,
                'cvss_score': cve.cvss_score,
                'published_date': cve.published_date,
                'modified_date': cve.modified_date,
                'affected_products': cve.affected_products,
                'exploit_availability': cve.exploit_availability,
                'threat_level': cve.threat_level,
                'remediation': cve.remediation,
                'references': cve.references
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'cves': cves_data,
                'total_count': len(cves_data),
                'filters_applied': {
                    'days_back': days_back,
                    'severity': severity if severity else 'all',
                    'limit': limit
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching CVEs: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve CVE data',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/actors', methods=['GET'])
def get_threat_actors():
    """
    Get threat actor intelligence data
    """
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        actors = loop.run_until_complete(threat_intel_manager.fetch_threat_actors())
        loop.close()
        
        # Convert to dict for JSON serialization
        actors_data = []
        for actor in actors:
            actors_data.append({
                'actor_id': actor.actor_id,
                'name': actor.name,
                'aliases': actor.aliases,
                'attribution': actor.attribution,
                'target_sectors': actor.target_sectors,
                'techniques': actor.techniques,
                'last_activity': actor.last_activity,
                'threat_level': actor.threat_level,
                'description': actor.description
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'threat_actors': actors_data,
                'total_count': len(actors_data)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching threat actors: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve threat actor data',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/advisories', methods=['GET'])
def get_security_advisories():
    """
    Get security advisories from various vendors
    """
    try:
        vendor = request.args.get('vendor', '')
        severity = request.args.get('severity', '')
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        advisories = loop.run_until_complete(threat_intel_manager.fetch_security_advisories())
        loop.close()
        
        # Filter if specified
        if vendor:
            advisories = [adv for adv in advisories if adv.vendor.lower() == vendor.lower()]
        if severity:
            advisories = [adv for adv in advisories if adv.severity.lower() == severity.lower()]
        
        # Convert to dict for JSON serialization
        advisories_data = []
        for advisory in advisories:
            advisories_data.append({
                'advisory_id': advisory.advisory_id,
                'title': advisory.title,
                'description': advisory.description,
                'severity': advisory.severity,
                'affected_systems': advisory.affected_systems,
                'published_date': advisory.published_date,
                'vendor': advisory.vendor,
                'solution': advisory.solution,
                'references': advisory.references
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'advisories': advisories_data,
                'total_count': len(advisories_data),
                'filters_applied': {
                    'vendor': vendor if vendor else 'all',
                    'severity': severity if severity else 'all'
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching security advisories: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve security advisory data',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/search', methods=['GET'])
def search_threat_intelligence():
    """
    Search threat intelligence database
    """
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', 'all')
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Search query parameter "q" is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        results = threat_intel_manager.search_threat_intelligence(query, category)
        
        return jsonify({
            'status': 'success',
            'data': {
                'search_query': query,
                'category': category,
                'results': results
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error searching threat intelligence: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Search failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/feed-update', methods=['POST'])
def update_threat_feeds():
    """
    Manually trigger threat intelligence feed updates
    """
    try:
        # Run feed updates
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Update all feeds
        cves = loop.run_until_complete(threat_intel_manager.fetch_latest_cves())
        actors = loop.run_until_complete(threat_intel_manager.fetch_threat_actors())
        advisories = loop.run_until_complete(threat_intel_manager.fetch_security_advisories())
        
        loop.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'updated_feeds': {
                    'cves_updated': len(cves),
                    'threat_actors_updated': len(actors),
                    'advisories_updated': len(advisories)
                },
                'update_timestamp': datetime.now().isoformat()
            },
            'message': 'Threat intelligence feeds updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating threat feeds: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update threat intelligence feeds',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/stats', methods=['GET'])
def get_threat_stats():
    """
    Get threat intelligence statistics and metrics
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect(threat_intel_manager.db_path)
        cursor = conn.cursor()
        
        # Get comprehensive statistics
        stats = {}
        
        # CVE statistics
        cursor.execute("SELECT severity, COUNT(*) FROM cve_data GROUP BY severity")
        stats['cve_by_severity'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM cve_data WHERE cvss_score >= 9.0")
        stats['critical_cves'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cve_data WHERE exploit_availability = 1")
        stats['exploitable_cves'] = cursor.fetchone()[0]
        
        # Threat actor statistics
        cursor.execute("SELECT threat_level, COUNT(*) FROM threat_actors GROUP BY threat_level")
        stats['actors_by_threat_level'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT attribution, COUNT(*) FROM threat_actors GROUP BY attribution")
        stats['actors_by_attribution'] = dict(cursor.fetchall())
        
        # Advisory statistics
        cursor.execute("SELECT vendor, COUNT(*) FROM security_advisories GROUP BY vendor")
        stats['advisories_by_vendor'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT severity, COUNT(*) FROM security_advisories GROUP BY severity")
        stats['advisories_by_severity'] = dict(cursor.fetchall())
        
        # Recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM cve_data 
            WHERE published_date >= date('now', '-7 days')
        """)
        stats['recent_cves'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM security_advisories 
            WHERE published_date >= date('now', '-7 days')
        """)
        stats['recent_advisories'] = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'statistics': stats,
                'last_updated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating threat statistics: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate threat statistics',
            'timestamp': datetime.now().isoformat()
        }), 500

@threat_intel_bp.route('/api/threat-intelligence/industry-report', methods=['GET'])
def get_industry_threat_report():
    """
    Get industry-specific threat intelligence report
    """
    try:
        industry = request.args.get('industry', 'all')
        
        # Industry-specific threat data
        industry_threats = {
            'financial': {
                'primary_threats': ['APT groups', 'Ransomware', 'Fraud', 'Data theft'],
                'threat_actors': ['Lazarus Group', 'FIN7', 'Carbanak'],
                'common_attack_vectors': ['Phishing', 'Business Email Compromise', 'ATM malware'],
                'recent_campaigns': ['Operation Ghost Writer', 'Silence Group activities'],
                'risk_level': 'Critical'
            },
            'healthcare': {
                'primary_threats': ['Ransomware', 'Data breaches', 'IoT vulnerabilities'],
                'threat_actors': ['Conti', 'Ryuk', 'Maze'],
                'common_attack_vectors': ['Phishing', 'RDP exploitation', 'Medical device attacks'],
                'recent_campaigns': ['Healthcare ransomware surge', 'COVID-19 themed attacks'],
                'risk_level': 'High'
            },
            'government': {
                'primary_threats': ['Nation-state actors', 'Espionage', 'Supply chain attacks'],
                'threat_actors': ['APT29', 'APT40', 'APT1'],
                'common_attack_vectors': ['Spear phishing', 'Zero-day exploits', 'Insider threats'],
                'recent_campaigns': ['SolarWinds compromise', 'Exchange Server attacks'],
                'risk_level': 'Critical'
            },
            'technology': {
                'primary_threats': ['IP theft', 'Supply chain attacks', 'Zero-day exploits'],
                'threat_actors': ['APT41', 'APT10', 'Cloud Hopper'],
                'common_attack_vectors': ['Software supply chain', 'Cloud misconfigurations', 'API attacks'],
                'recent_campaigns': ['Codecov supply chain attack', 'npm package attacks'],
                'risk_level': 'High'
            }
        }
        
        if industry.lower() in industry_threats:
            report_data = industry_threats[industry.lower()]
        else:
            # Return aggregated data for all industries
            report_data = {
                'industries_covered': list(industry_threats.keys()),
                'cross_industry_threats': ['Ransomware', 'Phishing', 'Data breaches'],
                'emerging_threats': ['Supply chain attacks', 'Cloud security threats', 'AI/ML attacks'],
                'global_risk_level': 'High'
            }
        
        return jsonify({
            'status': 'success',
            'data': {
                'industry': industry,
                'threat_intelligence': report_data,
                'report_date': datetime.now().isoformat(),
                'recommendations': [
                    'Implement zero-trust architecture',
                    'Regular security awareness training',
                    'Deploy advanced threat detection',
                    'Maintain incident response capabilities',
                    'Regular vulnerability assessments'
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating industry threat report: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate industry threat report',
            'timestamp': datetime.now().isoformat()
        }), 500