#!/usr/bin/env python3
"""
Enterprise Scanner - Comprehensive Validation Script
Validates all Phase 3 features and production readiness
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

class EnterpriseValidator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'start_time': datetime.now(),
            'tests': []
        }
    
    def log_test(self, test_name, status, message="", response_time=None):
        """Log test result"""
        self.results['total_tests'] += 1
        if status == 'PASS':
            self.results['passed'] += 1
            icon = "✅"
        elif status == 'FAIL':
            self.results['failed'] += 1
            icon = "❌"
        else:  # WARNING
            self.results['warnings'] += 1
            icon = "⚠️"
        
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results['tests'].append(result)
        
        print(f"{icon} {test_name}: {status}")
        if message:
            print(f"   {message}")
        if response_time:
            print(f"   Response time: {response_time:.3f}s")
    
    def test_server_health(self):
        """Test basic server connectivity"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Server Health", "PASS", 
                            "Server is responding", response_time)
                return True
            else:
                self.log_test("Server Health", "FAIL", 
                            f"HTTP {response.status_code}", response_time)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Health", "FAIL", str(e))
            return False
    
    def test_phase3_pages(self):
        """Test all Phase 3 feature pages"""
        pages = {
            '/chat-demo': 'Enterprise Chat Demo',
            '/analytics': 'Analytics Dashboard',
            '/reports': 'PDF Reports',
            '/threat-intel': 'Threat Intelligence',
            '/user-mgmt': 'User Management',
            '/api-security': 'API Security'
        }
        
        for path, name in pages.items():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{path}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Check for key content indicators
                    content_checks = {
                        '/chat-demo': ['enterprise-chat', 'WebSocket', 'real-time'],
                        '/analytics': ['analytics', 'dashboard', 'metrics'],
                        '/reports': ['PDF', 'reports', 'generate'],
                        '/threat-intel': ['threat', 'intelligence', 'security'],
                        '/user-mgmt': ['user', 'management', 'access'],
                        '/api-security': ['API', 'security', 'rate']
                    }
                    
                    if path in content_checks:
                        content = response.text.lower()
                        missing_content = [term for term in content_checks[path] 
                                         if term not in content]
                        if missing_content:
                            self.log_test(f"{name} Content", "WARNING", 
                                        f"Missing keywords: {missing_content}", response_time)
                        else:
                            self.log_test(f"{name} Page", "PASS", 
                                        "Page loaded with expected content", response_time)
                    else:
                        self.log_test(f"{name} Page", "PASS", 
                                    "Page accessible", response_time)
                else:
                    self.log_test(f"{name} Page", "FAIL", 
                                f"HTTP {response.status_code}", response_time)
            except requests.exceptions.RequestException as e:
                self.log_test(f"{name} Page", "FAIL", str(e))
    
    def test_chat_api(self):
        """Test chat API endpoints"""
        # Test chat start endpoint
        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/api/chat/start", 
                                   json={
                                       'name': 'Test User',
                                       'email': 'test@example.com',
                                       'company': 'Test Company'
                                   }, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if 'chat_id' in data and 'success' in data:
                    self.log_test("Chat API - Start", "PASS", 
                                "Chat session started successfully", response_time)
                    
                    # Test message endpoint
                    chat_id = data.get('chat_id')
                    if chat_id:
                        try:
                            start_time = time.time()
                            msg_response = requests.post(f"{self.base_url}/api/chat/message",
                                                       json={
                                                           'chat_id': chat_id,
                                                           'message': 'Test message'
                                                       }, timeout=10)
                            response_time = time.time() - start_time
                            
                            if msg_response.status_code == 200:
                                self.log_test("Chat API - Message", "PASS", 
                                            "Message sent successfully", response_time)
                            else:
                                self.log_test("Chat API - Message", "FAIL", 
                                            f"HTTP {msg_response.status_code}")
                        except requests.exceptions.RequestException as e:
                            self.log_test("Chat API - Message", "FAIL", str(e))
                else:
                    self.log_test("Chat API - Start", "FAIL", 
                                "Invalid response format")
            else:
                self.log_test("Chat API - Start", "FAIL", 
                            f"HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log_test("Chat API - Start", "FAIL", str(e))
    
    def test_static_assets(self):
        """Test critical static assets"""
        assets = [
            '/css/enterprise-chat.css',
            '/js/enterprise-chat.js'
        ]
        
        for asset in assets:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{asset}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    # Check file size (should not be empty)
                    if len(response.content) > 100:
                        self.log_test(f"Asset: {asset}", "PASS", 
                                    f"Size: {len(response.content)} bytes", response_time)
                    else:
                        self.log_test(f"Asset: {asset}", "WARNING", 
                                    "File seems too small")
                else:
                    self.log_test(f"Asset: {asset}", "FAIL", 
                                f"HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"Asset: {asset}", "FAIL", str(e))
    
    def test_performance(self):
        """Test basic performance metrics"""
        try:
            # Test multiple requests to check consistency
            response_times = []
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{self.base_url}/", timeout=10)
                response_time = time.time() - start_time
                response_times.append(response_time)
                time.sleep(0.1)  # Small delay between requests
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            if avg_response_time < 1.0:
                self.log_test("Performance - Average Response", "PASS", 
                            f"Avg: {avg_response_time:.3f}s")
            elif avg_response_time < 2.0:
                self.log_test("Performance - Average Response", "WARNING", 
                            f"Avg: {avg_response_time:.3f}s (>1s)")
            else:
                self.log_test("Performance - Average Response", "FAIL", 
                            f"Avg: {avg_response_time:.3f}s (>2s)")
            
            if max_response_time < 2.0:
                self.log_test("Performance - Max Response", "PASS", 
                            f"Max: {max_response_time:.3f}s")
            else:
                self.log_test("Performance - Max Response", "WARNING", 
                            f"Max: {max_response_time:.3f}s (>2s)")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Performance Test", "FAIL", str(e))
    
    def test_security_headers(self):
        """Test security headers"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            for header, expected in security_headers.items():
                if header in headers:
                    self.log_test(f"Security Header: {header}", "PASS", 
                                f"Value: {headers[header]}")
                else:
                    self.log_test(f"Security Header: {header}", "WARNING", 
                                "Header not present")
                    
        except requests.exceptions.RequestException as e:
            self.log_test("Security Headers", "FAIL", str(e))
    
    def run_validation(self):
        """Run complete validation suite"""
        print("🚀 Enterprise Scanner - Comprehensive Validation")
        print("=" * 60)
        print(f"Testing server: {self.base_url}")
        print(f"Start time: {self.results['start_time']}")
        print()
        
        # Core functionality tests
        print("📊 Core Functionality Tests:")
        if not self.test_server_health():
            print("❌ Server not responding - aborting remaining tests")
            return self.generate_report()
        
        print("\n🎯 Phase 3 Feature Tests:")
        self.test_phase3_pages()
        
        print("\n💬 Chat System Tests:")
        self.test_chat_api()
        
        print("\n📁 Static Asset Tests:")
        self.test_static_assets()
        
        print("\n⚡ Performance Tests:")
        self.test_performance()
        
        print("\n🔒 Security Tests:")
        self.test_security_headers()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate final validation report"""
        end_time = datetime.now()
        duration = end_time - self.results['start_time']
        
        print("\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        # Overall status
        if self.results['failed'] == 0:
            if self.results['warnings'] == 0:
                status = "✅ EXCELLENT"
                color = "green"
            else:
                status = "⚠️ GOOD (with warnings)"
                color = "yellow"
        else:
            status = "❌ NEEDS ATTENTION"
            color = "red"
        
        print(f"Overall Status: {status}")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Warnings: {self.results['warnings']} ⚠️")
        print(f"Failed: {self.results['failed']} ❌")
        print(f"Duration: {duration.total_seconds():.2f} seconds")
        print(f"Success Rate: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        
        # Recommendations
        print("\n📝 RECOMMENDATIONS:")
        if self.results['failed'] == 0 and self.results['warnings'] == 0:
            print("🎉 Platform is production-ready!")
            print("✅ All tests passed - ready for stakeholder demo")
            print("🚀 Proceed with Fortune 500 deployment")
        elif self.results['failed'] == 0:
            print("✅ Core functionality is working")
            print("⚠️ Address warnings for optimal performance")
            print("📊 Platform ready for demo with minor optimizations")
        else:
            print("❌ Critical issues need to be resolved")
            print("🔧 Fix failed tests before production deployment")
            print("⏱️ Re-run validation after fixes")
        
        # Save detailed report
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
        return self.results

def main():
    """Main validation function"""
    # Check if server URL is provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # Check if server is running
    try:
        requests.get(base_url, timeout=5)
    except requests.exceptions.RequestException:
        print(f"❌ Server not accessible at {base_url}")
        print("🔧 Please start the server with: python start_production.py")
        sys.exit(1)
    
    # Run validation
    validator = EnterpriseValidator(base_url)
    results = validator.run_validation()
    
    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    elif results['warnings'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()