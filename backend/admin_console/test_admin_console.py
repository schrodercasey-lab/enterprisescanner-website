"""
Admin Console Test Suite
=========================

Comprehensive tests for Admin Console functionality:
- API endpoints
- WebSocket connections
- System metrics
- Threat intelligence
- AI assistant
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
TIMEOUT = 5

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")


# Test 1: Health Check
def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed - Status: {data.get('status')}")
            
            components = data.get('components', {})
            print_info(f"Grok Intel: {'✓' if components.get('grok_intel') else '✗'}")
            print_info(f"Grok Assistant: {'✓' if components.get('grok_assistant') else '✗'}")
            print_info(f"Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Health check failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


# Test 2: Dashboard Stats
def test_dashboard_stats():
    """Test dashboard statistics endpoint"""
    print_header("TEST 2: Dashboard Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Stats endpoint working")
            
            # Users
            users = data.get('users', {})
            print_info(f"Users - Total: {users.get('total')}, Active: {users.get('active')}, Trend: {users.get('trend')}")
            
            # Trials
            trials = data.get('trials', {})
            print_info(f"Trials - Active: {trials.get('active')}, Hot Leads: {trials.get('hot_leads')}, Conversion: {trials.get('conversion_rate')}%")
            
            # Revenue
            revenue = data.get('revenue', {})
            mrr = revenue.get('mrr', 0) / 1000
            arr = revenue.get('arr', 0) / 1000000
            print_info(f"Revenue - MRR: ${mrr:.0f}K, ARR: ${arr:.2f}M, Trend: {revenue.get('trend')}")
            
            # Alerts
            alerts = data.get('alerts', {})
            print_info(f"Alerts - Critical: {alerts.get('critical')}, High: {alerts.get('high')}, Total: {alerts.get('total')}")
            
            return True
        else:
            print_error(f"Stats failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Stats error: {e}")
        return False


# Test 3: System Metrics
def test_system_metrics():
    """Test system metrics endpoint"""
    print_header("TEST 3: System Metrics")
    
    try:
        response = requests.get(f"{BASE_URL}/api/system/metrics", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("System metrics working")
            
            # CPU
            cpu = data.get('cpu', {})
            print_info(f"CPU: {cpu.get('percent')}% - Status: {cpu.get('status')}")
            
            # Memory
            memory = data.get('memory', {})
            print_info(f"Memory: {memory.get('percent')}% ({memory.get('used_gb')}GB / {memory.get('total_gb')}GB) - Status: {memory.get('status')}")
            
            # Disk
            disk = data.get('disk', {})
            print_info(f"Disk: {disk.get('percent')}% ({disk.get('used_gb')}GB / {disk.get('total_gb')}GB) - Status: {disk.get('status')}")
            
            return True
        else:
            print_error(f"Metrics failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Metrics error: {e}")
        return False


# Test 4: Threat Intelligence Feed
def test_threat_feed():
    """Test threat intelligence feed"""
    print_header("TEST 4: Threat Intelligence Feed")
    
    try:
        response = requests.get(f"{BASE_URL}/api/threats?hours=24", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            threats = data.get('threats', [])
            
            print_success(f"Threat feed working - Found {len(threats)} threats")
            
            if threats:
                for i, threat in enumerate(threats[:3], 1):
                    print_info(f"Threat {i}: {threat.get('title')} [{threat.get('severity')}]")
                    if threat.get('cve_id'):
                        print_info(f"  CVE: {threat.get('cve_id')}")
            else:
                print_warning("No threats found in last 24 hours")
            
            return True
        else:
            print_error(f"Threat feed failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Threat feed error: {e}")
        return False


# Test 5: Main Dashboard Page
def test_dashboard_page():
    """Test main dashboard HTML page"""
    print_header("TEST 5: Dashboard Page")
    
    try:
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        
        if response.status_code == 200:
            html = response.text
            
            # Check for key elements
            checks = {
                'Title': 'Admin Console - Enterprise Scanner' in html,
                'Tailwind CSS': 'tailwindcss.com' in html,
                'Socket.IO': 'socket.io' in html,
                'Chart.js': 'chart.js' in html,
                'WebSocket': 'socket = io(' in html
            }
            
            print_success("Dashboard page loaded")
            for check, passed in checks.items():
                if passed:
                    print_success(f"{check} present")
                else:
                    print_warning(f"{check} missing")
            
            return all(checks.values())
        else:
            print_error(f"Dashboard page failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Dashboard page error: {e}")
        return False


# Run all tests
def run_all_tests():
    """Run complete test suite"""
    print(f"\n{BLUE}{'='*60}")
    print("ENTERPRISE SCANNER ADMIN CONSOLE - TEST SUITE")
    print(f"{'='*60}{RESET}")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Dashboard Stats", test_dashboard_stats),
        ("System Metrics", test_system_metrics),
        ("Threat Feed", test_threat_feed),
        ("Dashboard Page", test_dashboard_page)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print_header("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        if passed:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
    
    print(f"\n{BLUE}{'='*60}")
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print(f"{GREEN}✅ ALL TESTS PASSED!{RESET}")
    elif passed_count > 0:
        print(f"{YELLOW}⚠️  SOME TESTS FAILED{RESET}")
    else:
        print(f"{RED}❌ ALL TESTS FAILED{RESET}")
    
    print(f"{'='*60}{RESET}\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
