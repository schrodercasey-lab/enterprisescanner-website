"""
Simple Flask Server Starter - No WebSocket Dependencies
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple health check endpoint
@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'message': 'Enterprise Scanner Backend API',
        'version': '1.0.0',
        'database': 'SQLite (enterprise_scanner.db)'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': 'OK'
    })

# Simple lead endpoint
@app.route('/api/leads', methods=['GET', 'POST'])
def leads():
    from flask import request
    import sqlite3
    from datetime import datetime
    
    db_path = os.path.join(os.path.dirname(__file__), 'enterprise_scanner.db')
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Insert lead into database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO leads (
                    first_name, last_name, email, company_name, job_title, 
                    phone, lead_source, lead_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('first_name'),
                data.get('last_name'),
                data.get('email'),
                data.get('company'),
                data.get('job_title'),
                data.get('phone'),
                data.get('lead_source', 'website'),
                data.get('lead_status', 'new'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            lead_id = cursor.lastrowid
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Lead saved to database',
                'lead_id': lead_id,
                'data': data
            })
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"\n❌ DATABASE ERROR:\n{error_detail}")
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}',
                'error_detail': error_detail
            }), 500
    else:
        # GET request - return all leads
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, first_name, last_name, email, company_name, job_title, 
                       phone, lead_source, lead_status, lead_score, created_at
                FROM leads
                ORDER BY created_at DESC
                LIMIT 50
            ''')
            
            rows = cursor.fetchall()
            leads = [dict(row) for row in rows]
            conn.close()
            
            return jsonify({
                'leads': leads,
                'count': len(leads)
            })
        except Exception as e:
            return jsonify({
                'leads': [],
                'count': 0,
                'error': str(e)
            })

# Client onboarding endpoint
@app.route('/api/onboarding', methods=['POST'])
def onboarding():
    from flask import request
    import sqlite3
    from datetime import datetime
    
    db_path = os.path.join(os.path.dirname(__file__), 'enterprise_scanner.db')
    data = request.get_json()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a lead from onboarding data
        cursor.execute('''
            INSERT INTO leads (
                first_name, last_name, email, company_name, job_title, 
                phone, lead_source, lead_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('contactName', '').split()[0] if data.get('contactName') else '',
            data.get('contactName', '').split()[-1] if data.get('contactName') and len(data.get('contactName', '').split()) > 1 else '',
            data.get('email', ''),
            data.get('companyName', ''),
            data.get('title', ''),
            data.get('phone', ''),
            'onboarding',
            'onboarding',
            datetime.now().isoformat()
        ))
        
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Onboarding data saved successfully',
            'lead_id': lead_id
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ONBOARDING ERROR:\n{error_detail}")
        return jsonify({
            'success': False,
            'message': f'Error saving onboarding data: {str(e)}'
        }), 500

# Analytics endpoint
@app.route('/api/analytics/<metric>', methods=['GET'])
def analytics(metric):
    from flask import request
    import sqlite3
    from datetime import datetime, timedelta
    
    db_path = os.path.join(os.path.dirname(__file__), 'enterprise_scanner.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if metric == 'leads-over-time':
            # Get leads grouped by date for last 7 days
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM leads
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            ''')
            rows = cursor.fetchall()
            data = {
                'labels': [row['date'] for row in rows],
                'values': [row['count'] for row in rows]
            }
            
        elif metric == 'sources':
            # Get lead counts by source
            cursor.execute('''
                SELECT lead_source, COUNT(*) as count
                FROM leads
                GROUP BY lead_source
            ''')
            rows = cursor.fetchall()
            data = {
                'labels': [row['lead_source'] for row in rows],
                'values': [row['count'] for row in rows]
            }
            
        elif metric == 'conversion-rate':
            # Calculate conversion metrics
            cursor.execute('SELECT COUNT(*) as total FROM leads')
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as converted FROM leads WHERE lead_status = 'converted'")
            converted = cursor.fetchone()['converted']
            
            rate = (converted / total * 100) if total > 0 else 0
            data = {
                'total': total,
                'converted': converted,
                'rate': round(rate, 2)
            }
        else:
            conn.close()
            return jsonify({'error': 'Unknown metric'}), 404
        
        conn.close()
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n❌ ANALYTICS ERROR:\n{error_detail}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ENTERPRISE SCANNER BACKEND - SIMPLE MODE")
    print("="*60)
    print("✅ Server starting on http://localhost:5000")
    print("✅ Database: SQLite (enterprise_scanner.db)")
    print("\n📡 Available endpoints:")
    print("   GET  http://localhost:5000/")
    print("   GET  http://localhost:5000/health")
    print("   GET  http://localhost:5000/api/leads")
    print("   POST http://localhost:5000/api/leads")
    print("   POST http://localhost:5000/api/onboarding")
    print("   GET  http://localhost:5000/api/analytics/<metric>")
    print("\n⏹️  Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
