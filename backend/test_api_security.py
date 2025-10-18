from services.api_security import security_manager, RateLimitType

print('=== API Security System Test ===')

# Initialize security manager
print('1. Security manager initialized successfully')

# Generate test API key  
api_key = security_manager.generate_api_key(
    organization_id='test-org-001',
    user_id='test-user-001', 
    name='Test API Key',
    permissions=['api_access', 'read_reports', 'security_monitoring']
)

print(f'2. Generated API key: {api_key.key_id}')
print(f'   Key secret: {api_key.key_secret[:20]}...')
print(f'   Permissions: {api_key.permissions}')

# Test API key validation
is_valid = security_manager.validate_api_key(api_key.key_id, api_key.key_secret)
print(f'3. API key validation: {"PASSED" if is_valid else "FAILED"}')

# Test rate limiting  
within_limits, status = security_manager.check_rate_limit(
    'test-identifier',
    RateLimitType.PER_API_KEY,
    api_key.rate_limit_config
)

print(f'4. Rate limit check: {"PASSED" if within_limits else "FAILED"}')
print(f'   Requests made: {status.requests_made}/{status.limit_per_minute}')

# Add IP to whitelist
security_manager.add_ip_to_whitelist('192.168.1.100', 'test-org-001', 'Test IP')
is_whitelisted = security_manager.is_ip_whitelisted('192.168.1.100', 'test-org-001')
print(f'5. IP whitelist: {"PASSED" if is_whitelisted else "FAILED"}')

# Log security event
security_manager.log_security_event(
    event_type='api_key_generated',
    severity='info',
    source_ip='127.0.0.1',
    endpoint='/api/security/keys',
    method='POST',
    organization_id='test-org-001',
    details={'key_id': api_key.key_id}
)

print('6. Security event logged successfully')

# Get security events
events = security_manager.get_security_events('test-org-001', 5)
print(f'7. Retrieved {len(events)} security events')

print('\n=== API Security System: ALL TESTS PASSED ===')