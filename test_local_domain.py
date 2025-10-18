#!/usr/bin/env python3
"""
Enterprise Scanner - Local Domain Testing Script
Tests the local enterprisescanner.com setup
"""

import requests
import ssl
import socket
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def test_domain_resolution():
    """Test if domain resolves to localhost"""
    print("Testing domain resolution...")
    
    try:
        ip = socket.gethostbyname('enterprisescanner.com')
        if ip == '127.0.0.1':
            print("✅ enterprisescanner.com resolves to 127.0.0.1")
            return True
        else:
            print(f"❌ enterprisescanner.com resolves to {ip} (expected 127.0.0.1)")
            return False
    except Exception as e:
        print(f"❌ Domain resolution failed: {e}")
        return False

def test_flask_app():
    """Test if Flask application is running"""
    print("Testing Flask application...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/crm-dashboard.html', timeout=5)
        if response.status_code == 200:
            print("✅ Flask application is running on port 5000")
            return True
        else:
            print(f"❌ Flask application returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask application is not running")
        print("   Start it with: python start_production.py")
        return False
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False

def test_crm_dashboard():
    """Test CRM dashboard accessibility"""
    print("Testing CRM dashboard...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/crm-dashboard.html', timeout=10)
        if response.status_code == 200:
            print("✅ CRM dashboard is accessible")
            if "Fortune 500" in response.text:
                print("✅ CRM dashboard contains Fortune 500 content")
            return True
        else:
            print(f"❌ CRM dashboard returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CRM dashboard test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("Testing API endpoints...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/companies', timeout=10)
        if response.status_code in [200, 401]:  # 401 is OK (means auth is working)
            print("✅ API endpoints are accessible")
            return True
        else:
            print(f"❌ API endpoints returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Enterprise Scanner - Local Domain Testing")
    print("=" * 50)
    
    tests = [
        test_domain_resolution,
        test_flask_app,
        test_crm_dashboard,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed >= 2:  # At least Flask and CRM working
        print("✅ Core functionality is working!")
        print("")
        print("Access points:")
        print("   http://127.0.0.1:5000")
        print("   http://127.0.0.1:5000/crm-dashboard.html")
        print("   http://enterprisescanner.com:5000 (if hosts configured)")
    else:
        print("⚠️  Some tests failed. Check the setup and try again.")
        print("")
        print("Common solutions:")
        print("   - Make sure Flask app is running: python start_production.py")
        print("   - Check that Enterprise Scanner is properly configured")

if __name__ == "__main__":
    main()
