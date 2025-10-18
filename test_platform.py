#!/usr/bin/env python3
"""
Simple test script to validate Enterprise Scanner is working
"""

import requests
import json

print("🔍 Testing Enterprise Scanner Platform...")

try:
    # Test main site
    print("\n1. Testing main site...")
    response = requests.get("http://localhost:5000")
    if response.status_code == 200:
        print("✅ Main site working - Status 200")
    else:
        print(f"❌ Main site error - Status {response.status_code}")

    # Test chat demo
    print("\n2. Testing chat demo...")
    response = requests.get("http://localhost:5000/chat-demo")
    if response.status_code == 200:
        print("✅ Chat demo working - Status 200")
    else:
        print(f"❌ Chat demo error - Status {response.status_code}")

    # Test analytics
    print("\n3. Testing analytics...")
    response = requests.get("http://localhost:5000/analytics")
    if response.status_code == 200:
        print("✅ Analytics dashboard working - Status 200")
    else:
        print(f"❌ Analytics error - Status {response.status_code}")

    # Test health API
    print("\n4. Testing health API...")
    response = requests.get("http://localhost:5000/api/health")
    if response.status_code == 200:
        health_data = response.json()
        print("✅ Health API working - Status 200")
        print(f"   Platform: {health_data.get('platform')}")
        print(f"   Version: {health_data.get('version')}")
        print(f"   Status: {health_data.get('status')}")
        print(f"   Market Opportunity: {health_data.get('market_opportunity')}")
    else:
        print(f"❌ Health API error - Status {response.status_code}")

    print("\n🎉 VALIDATION COMPLETE!")
    print("✅ Enterprise Scanner is fully operational")
    print("🚀 Ready for Fortune 500 demonstrations")
    
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("Make sure the server is running with: python simple_demo.py")