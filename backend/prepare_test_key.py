import requests
import json
from services.api_security import security_manager

# Get the test API key we just created
test_key_id = "esk_d3502fb05a114576"

# Try to get the key details (we need the secret)
import sqlite3
conn = sqlite3.connect(security_manager.db_path)
cursor = conn.cursor()

cursor.execute('SELECT key_secret_hash FROM api_keys WHERE key_id = ?', (test_key_id,))
result = cursor.fetchone()
conn.close()

if result:
    print(f"Found API key in database: {test_key_id}")
    
    # For testing, let's create a fresh key
    api_key = security_manager.generate_api_key(
        organization_id='test-org-002',
        user_id='test-user-002',
        name='Flask Test Key',
        permissions=['api_access', 'security_monitoring']
    )
    
    print(f"Created test API key: {api_key.key_id}")
    print(f"Key secret for testing: {api_key.key_secret}")
    
    # Add test IP to whitelist
    security_manager.add_ip_to_whitelist('127.0.0.1', 'test-org-002', 'Local testing IP')
    
    print("\nAPI key and whitelist configured for Flask testing")
    print(f"Use these headers in your requests:")
    print(f"X-API-Key: {api_key.key_id}")
    print(f"X-API-Secret: {api_key.key_secret}")
    
else:
    print("API key not found in database")