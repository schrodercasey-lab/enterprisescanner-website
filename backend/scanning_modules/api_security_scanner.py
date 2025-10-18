"""
API Security Scanner Module
REST, GraphQL, and SOAP API security testing
"""

import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class APIVulnerability:
    """API-specific vulnerability finding"""
    api_type: str  # 'REST', 'GraphQL', 'SOAP'
    vulnerability_type: str
    severity: str
    endpoint: str
    method: Optional[str] = None
    description: str = ""
    recommendation: str = ""


class APISecurityScanner:
    """
    API Security Scanner for Enterprise Scanner
    
    Features:
    - REST API security testing
    - GraphQL introspection and authorization
    - SOAP API security
    - Authentication bypass detection
    - Authorization flaws
    - Rate limiting checks
    - Mass assignment detection
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.vulnerabilities = []
    
    def scan_rest_api(self, api_base_url: str, openapi_spec: Optional[Dict] = None) -> List[APIVulnerability]:
        """
        Scan REST API for security vulnerabilities
        
        Args:
            api_base_url: Base URL of the API
            openapi_spec: Optional OpenAPI/Swagger specification
            
        Returns:
            List of API vulnerabilities
        """
        logger.info(f"Scanning REST API: {api_base_url}")
        self.vulnerabilities = []
        
        # Test authentication
        self._test_authentication(api_base_url)
        
        # Test authorization
        self._test_authorization(api_base_url)
        
        # Test rate limiting
        self._test_rate_limiting(api_base_url)
        
        # Test for exposed sensitive endpoints
        self._test_sensitive_endpoints(api_base_url)
        
        return self.vulnerabilities
    
    def scan_graphql_api(self, graphql_endpoint: str) -> List[APIVulnerability]:
        """
        Scan GraphQL API for security vulnerabilities
        
        Args:
            graphql_endpoint: GraphQL endpoint URL
            
        Returns:
            List of API vulnerabilities
        """
        logger.info(f"Scanning GraphQL API: {graphql_endpoint}")
        self.vulnerabilities = []
        
        # Test introspection
        if self._test_graphql_introspection(graphql_endpoint):
            self.vulnerabilities.append(APIVulnerability(
                api_type='GraphQL',
                vulnerability_type='Introspection Enabled',
                severity='medium',
                endpoint=graphql_endpoint,
                description='GraphQL introspection is enabled, exposing schema details',
                recommendation='Disable introspection in production environments'
            ))
        
        # Test for depth/complexity limits
        self._test_graphql_depth_limit(graphql_endpoint)
        
        return self.vulnerabilities
    
    def _test_authentication(self, api_url: str):
        """Test for authentication bypass vulnerabilities"""
        try:
            # Try accessing without credentials
            response = self.session.get(f"{api_url}/users", timeout=self.timeout)
            if response.status_code == 200:
                self.vulnerabilities.append(APIVulnerability(
                    api_type='REST',
                    vulnerability_type='Missing Authentication',
                    severity='critical',
                    endpoint=f"{api_url}/users",
                    method='GET',
                    description='Sensitive endpoint accessible without authentication',
                    recommendation='Implement proper authentication for all sensitive endpoints'
                ))
        except Exception as e:
            logger.debug(f"Error testing authentication: {e}")
    
    def _test_authorization(self, api_url: str):
        """
        Test for authorization flaws (IDOR, horizontal/vertical privilege escalation)
        
        Tests:
        - IDOR (Insecure Direct Object References)
        - Horizontal privilege escalation (accessing other users' data)
        - Vertical privilege escalation (accessing admin functions)
        - Missing function-level access control
        """
        try:
            # Test 1: IDOR - try accessing resources with different IDs
            test_endpoints = [
                f"{api_url}/users/1",
                f"{api_url}/users/2",
                f"{api_url}/users/admin",
                f"{api_url}/api/v1/account/1",
                f"{api_url}/api/v1/account/999",
            ]
            
            for endpoint in test_endpoints:
                try:
                    # Test without authentication
                    response_unauth = self.session.get(endpoint, timeout=self.timeout)
                    
                    # Test with basic user credentials (simulated)
                    headers_user = {'Authorization': 'Bearer user_token_simulation'}
                    response_user = self.session.get(endpoint, headers=headers_user, timeout=self.timeout)
                    
                    # Check if we can access other users' data
                    if response_user.status_code == 200:
                        self.vulnerabilities.append(APIVulnerability(
                            api_type='REST',
                            vulnerability_type='IDOR - Insecure Direct Object Reference',
                            severity='high',
                            endpoint=endpoint,
                            method='GET',
                            description='API allows access to resources without proper authorization checks',
                            recommendation='Implement object-level authorization checks for all resources'
                        ))
                except:
                    continue
            
            # Test 2: Horizontal Privilege Escalation - accessing peers' data
            peer_test_urls = [
                f"{api_url}/api/profile?userId=123",
                f"{api_url}/api/orders?customerId=456",
                f"{api_url}/api/documents?ownerId=789"
            ]
            
            for test_url in peer_test_urls:
                try:
                    response = self.session.get(test_url, timeout=self.timeout)
                    if response.status_code in [200, 201]:
                        # Check if response contains data (not just empty/error)
                        if response.text and len(response.text) > 50:
                            self.vulnerabilities.append(APIVulnerability(
                                api_type='REST',
                                vulnerability_type='Horizontal Privilege Escalation',
                                severity='high',
                                endpoint=test_url,
                                method='GET',
                                description='User can access data belonging to other users at the same privilege level',
                                recommendation='Implement per-user access controls and validate resource ownership'
                            ))
                except:
                    continue
            
            # Test 3: Vertical Privilege Escalation - accessing admin functions
            admin_endpoints = [
                f"{api_url}/admin",
                f"{api_url}/api/admin/users",
                f"{api_url}/api/admin/settings",
                f"{api_url}/api/v1/admin/dashboard",
                f"{api_url}/management",
                f"{api_url}/api/internal"
            ]
            
            for admin_endpoint in admin_endpoints:
                try:
                    # Try with regular user credentials
                    headers = {'Authorization': 'Bearer regular_user_token'}
                    response = self.session.get(admin_endpoint, headers=headers, timeout=self.timeout)
                    
                    # If accessible, it's a vertical privilege escalation
                    if response.status_code in [200, 201, 204]:
                        self.vulnerabilities.append(APIVulnerability(
                            api_type='REST',
                            vulnerability_type='Vertical Privilege Escalation',
                            severity='critical',
                            endpoint=admin_endpoint,
                            method='GET',
                            description='Regular user can access administrative functions',
                            recommendation='Implement role-based access control (RBAC) and validate user permissions'
                        ))
                except:
                    continue
            
            # Test 4: Mass Assignment vulnerability
            test_mass_assignment_url = f"{api_url}/api/users/update"
            try:
                # Try to update fields that should be restricted (like isAdmin, role)
                malicious_payload = {
                    'username': 'testuser',
                    'isAdmin': True,
                    'role': 'administrator',
                    'permissions': ['*']
                }
                response = self.session.post(test_mass_assignment_url, json=malicious_payload, timeout=self.timeout)
                
                if response.status_code in [200, 201]:
                    self.vulnerabilities.append(APIVulnerability(
                        api_type='REST',
                        vulnerability_type='Mass Assignment',
                        severity='high',
                        endpoint=test_mass_assignment_url,
                        method='POST',
                        description='API accepts unauthorized field updates (mass assignment vulnerability)',
                        recommendation='Use allowlist for acceptable fields, reject unknown properties'
                    ))
            except:
                pass
            
        except Exception as e:
            logger.debug(f"Error testing authorization: {e}")
    
    def _test_rate_limiting(self, api_url: str):
        """Test for rate limiting implementation"""
        try:
            # Make multiple rapid requests
            for i in range(10):
                response = self.session.get(api_url, timeout=self.timeout)
                if i == 9 and response.status_code != 429:  # Not rate limited
                    self.vulnerabilities.append(APIVulnerability(
                        api_type='REST',
                        vulnerability_type='Missing Rate Limiting',
                        severity='medium',
                        endpoint=api_url,
                        description='API does not implement rate limiting',
                        recommendation='Implement rate limiting to prevent abuse'
                    ))
                    break
        except Exception as e:
            logger.debug(f"Error testing rate limiting: {e}")
    
    def _test_sensitive_endpoints(self, api_url: str):
        """Test for exposed sensitive endpoints"""
        sensitive_paths = ['/admin', '/config', '/debug', '/swagger', '/api-docs']
        for path in sensitive_paths:
            try:
                response = self.session.get(f"{api_url}{path}", timeout=self.timeout)
                if response.status_code == 200:
                    self.vulnerabilities.append(APIVulnerability(
                        api_type='REST',
                        vulnerability_type='Sensitive Endpoint Exposed',
                        severity='high',
                        endpoint=f"{api_url}{path}",
                        description=f'Sensitive endpoint {path} is publicly accessible',
                        recommendation='Restrict access to sensitive endpoints'
                    ))
            except Exception as e:
                logger.debug(f"Error testing endpoint {path}: {e}")
    
    def _test_graphql_introspection(self, endpoint: str) -> bool:
        """Test if GraphQL introspection is enabled"""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                }
            }
        }
        """
        try:
            response = self.session.post(
                endpoint,
                json={'query': introspection_query},
                timeout=self.timeout
            )
            return response.status_code == 200 and '__schema' in response.text
        except Exception as e:
            logger.debug(f"Error testing GraphQL introspection: {e}")
            return False
    
    def _test_graphql_depth_limit(self, endpoint: str):
        """
        Test for query depth/complexity limits to prevent DoS attacks
        
        GraphQL APIs without depth limiting are vulnerable to:
        - Deeply nested queries causing excessive CPU/memory usage
        - Query complexity attacks
        - Resource exhaustion DoS
        """
        try:
            # Test 1: Deeply nested query (depth = 20)
            deeply_nested_query = """
            query DeeplyNestedQuery {
                user {
                    posts {
                        comments {
                            author {
                                posts {
                                    comments {
                                        author {
                                            posts {
                                                comments {
                                                    author {
                                                        posts {
                                                            comments {
                                                                author {
                                                                    posts {
                                                                        comments {
                                                                            author {
                                                                                posts {
                                                                                    comments {
                                                                                        author {
                                                                                            id
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            
            response_deep = self.session.post(
                endpoint,
                json={'query': deeply_nested_query},
                timeout=self.timeout * 2  # Allow longer timeout for this test
            )
            
            # If query succeeds without error, depth limiting is not implemented
            if response_deep.status_code == 200 and 'errors' not in response_deep.text:
                self.vulnerabilities.append(APIVulnerability(
                    api_type='GraphQL',
                    vulnerability_type='Missing Query Depth Limit',
                    severity='high',
                    endpoint=endpoint,
                    method='POST',
                    description='GraphQL API accepts deeply nested queries without depth limiting (DoS risk)',
                    recommendation='Implement query depth limiting (max depth: 5-10 levels) and complexity analysis'
                ))
            
            # Test 2: Query with many fields (field complexity attack)
            wide_query = """
            query WideQuery {
                user {
                    id name email username bio website location company
                    avatarUrl coverImage createdAt updatedAt lastLogin
                    profile { age gender country city zip phone }
                    settings { theme language timezone notifications }
                    stats { postCount followerCount followingCount likeCount }
                    permissions { canPost canComment canMessage canShare }
                    posts { id title content createdAt }
                    followers { id name }
                    following { id name }
                    comments { id content }
                    likes { id }
                    bookmarks { id }
                }
            }
            """
            
            response_wide = self.session.post(
                endpoint,
                json={'query': wide_query},
                timeout=self.timeout
            )
            
            if response_wide.status_code == 200 and 'errors' not in response_wide.text:
                self.vulnerabilities.append(APIVulnerability(
                    api_type='GraphQL',
                    vulnerability_type='Missing Query Complexity Limit',
                    severity='medium',
                    endpoint=endpoint,
                    method='POST',
                    description='GraphQL API accepts queries with excessive field selections without complexity analysis',
                    recommendation='Implement query complexity scoring and limits'
                ))
            
            # Test 3: Batch query attack (multiple queries in one request)
            batch_query = """
            query BatchAttack {
                q1: user(id: "1") { id posts { id } }
                q2: user(id: "2") { id posts { id } }
                q3: user(id: "3") { id posts { id } }
                q4: user(id: "4") { id posts { id } }
                q5: user(id: "5") { id posts { id } }
                q6: user(id: "6") { id posts { id } }
                q7: user(id: "7") { id posts { id } }
                q8: user(id: "8") { id posts { id } }
                q9: user(id: "9") { id posts { id } }
                q10: user(id: "10") { id posts { id } }
            }
            """
            
            response_batch = self.session.post(
                endpoint,
                json={'query': batch_query},
                timeout=self.timeout
            )
            
            if response_batch.status_code == 200 and 'errors' not in response_batch.text:
                self.vulnerabilities.append(APIVulnerability(
                    api_type='GraphQL',
                    vulnerability_type='Batch Query Attack Vector',
                    severity='medium',
                    endpoint=endpoint,
                    method='POST',
                    description='GraphQL API allows batched queries without limits (resource exhaustion risk)',
                    recommendation='Limit number of operations per request (max 5-10 queries)'
                ))
            
            # Test 4: Circular reference query (if schema allows)
            circular_query = """
            query CircularQuery {
                user {
                    friends {
                        friends {
                            friends {
                                friends {
                                    friends {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """
            
            response_circular = self.session.post(
                endpoint,
                json={'query': circular_query},
                timeout=self.timeout
            )
            
            if response_circular.status_code == 200 and 'errors' not in response_circular.text:
                self.vulnerabilities.append(APIVulnerability(
                    api_type='GraphQL',
                    vulnerability_type='Circular Reference DoS',
                    severity='high',
                    endpoint=endpoint,
                    method='POST',
                    description='GraphQL schema allows circular references without depth protection',
                    recommendation='Implement depth limits and detect circular relationships'
                ))
                
        except Exception as e:
            logger.debug(f"Error testing GraphQL depth limits: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scanner = APISecurityScanner()
    vulnerabilities = scanner.scan_rest_api("https://api.example.com")
    
    print(f"Found {len(vulnerabilities)} API vulnerabilities")
    for vuln in vulnerabilities:
        print(f"  - {vuln.severity.upper()}: {vuln.vulnerability_type} at {vuln.endpoint}")
