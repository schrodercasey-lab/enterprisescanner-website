#!/usr/bin/env python3
import requests
import json

def check_server_status():
    print("ENTERPRISE SCANNER - SERVER STATUS CHECK")
    print("=" * 50)
    
    base_url = "https://enterprisescanner.com"
    
    # Test 1: Website
    try:
        response = requests.get(base_url, timeout=10)
        status = "✓ Online" if response.status_code == 200 else "✗ Error"
        print(f"Website: {response.status_code} - {status}")
    except Exception as e:
        print(f"Website: ✗ Error - {e}")
    
    # Test 2: API Health (might not exist yet)
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        status = "✓ Available" if response.status_code == 200 else "✗ Not Available"
        print(f"API Health: {response.status_code} - {status}")
    except Exception as e:
        print(f"API Health: ✗ Not Available - API not deployed yet")
    
    # Test 3: Security Assessment (our new feature)
    try:
        response = requests.get(f"{base_url}/security-assessment.html", timeout=5)
        status = "✓ Available" if response.status_code == 200 else "✗ Not Available"
        print(f"Security Assessment Page: {response.status_code} - {status}")
    except Exception as e:
        print(f"Security Assessment Page: ✗ Not Available")
        
    print("\nNext step: Deploy Live Security Assessment Tool backend API")

if __name__ == "__main__":
    check_server_status()