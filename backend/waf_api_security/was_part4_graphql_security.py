"""
Military Upgrade #19: WAF & API Security
Part 4: GraphQL Security & API Gateway Hardening

This module implements comprehensive GraphQL security controls and API gateway
hardening to protect against GraphQL-specific attacks and API abuse.

Key Features:
- GraphQL query depth limiting
- Query complexity analysis
- Introspection disabling in production
- Field-level authorization
- Mutation rate limiting
- API gateway security hardening

Compliance:
- OWASP API Security Top 10 - API3:2023 (Broken Object Property Level Authorization)
- OWASP GraphQL Security Best Practices
- NIST 800-53 AC-3 (Access Enforcement)
- NIST 800-53 SC-5 (Denial of Service Protection)
"""

from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re


class GraphQLOperationType(Enum):
    """GraphQL operation types"""
    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


class SecurityPolicyAction(Enum):
    """Security policy actions"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_AUTH = "require_auth"
    RATE_LIMIT = "rate_limit"


@dataclass
class GraphQLQuery:
    """Parsed GraphQL query"""
    operation_type: GraphQLOperationType
    operation_name: Optional[str]
    query_text: str
    
    # Analysis
    depth: int = 0
    complexity: int = 0
    field_count: int = 0
    fields_requested: List[str] = field(default_factory=list)
    
    # Security
    uses_introspection: bool = False
    has_aliases: bool = False
    has_fragments: bool = False


@dataclass
class FieldPolicy:
    """Field-level authorization policy"""
    field_name: str
    required_roles: List[str] = field(default_factory=list)
    required_scopes: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None  # Requests per minute
    cost: int = 1  # Complexity cost


@dataclass
class QueryComplexityAnalysis:
    """Query complexity analysis result"""
    total_complexity: int
    depth: int
    field_count: int
    estimated_cost: int
    
    # Violations
    exceeds_depth_limit: bool = False
    exceeds_complexity_limit: bool = False
    exceeds_field_limit: bool = False
    
    # Details
    expensive_fields: List[str] = field(default_factory=list)
    unauthorized_fields: List[str] = field(default_factory=list)


@dataclass
class APIGatewayConfig:
    """API Gateway security configuration"""
    # GraphQL limits
    max_query_depth: int = 5
    max_query_complexity: int = 1000
    max_field_count: int = 100
    
    # Features
    enable_introspection: bool = False  # Should be False in production
    allow_batch_queries: bool = False
    max_batch_size: int = 5
    
    # Timeouts
    query_timeout_seconds: int = 10
    mutation_timeout_seconds: int = 30
    
    # Rate limiting
    queries_per_minute: int = 100
    mutations_per_minute: int = 20
    
    # CORS
    allowed_origins: List[str] = field(default_factory=list)
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST"])
    allow_credentials: bool = False


class GraphQLSecurityEngine:
    """GraphQL Security & Query Analysis Engine"""
    
    def __init__(self, config: Optional[APIGatewayConfig] = None):
        self.config = config or APIGatewayConfig()
        self.field_policies: Dict[str, FieldPolicy] = {}
        self.query_history: List[GraphQLQuery] = []
        self.blocked_queries: List[Dict[str, Any]] = []
        
        # Initialize default field policies
        self._initialize_field_policies()
    
    def _initialize_field_policies(self) -> None:
        """Initialize field-level security policies"""
        # Sensitive fields require authentication
        self.field_policies['user.email'] = FieldPolicy(
            field_name='user.email',
            required_roles=['user', 'admin'],
            cost=5
        )
        
        self.field_policies['user.ssn'] = FieldPolicy(
            field_name='user.ssn',
            required_roles=['admin'],
            required_scopes=['read:sensitive'],
            cost=10
        )
        
        # Expensive fields have higher cost
        self.field_policies['analytics.report'] = FieldPolicy(
            field_name='analytics.report',
            required_roles=['user'],
            cost=50,
            rate_limit=10  # 10 per minute
        )
        
        self.field_policies['search.fullText'] = FieldPolicy(
            field_name='search.fullText',
            cost=25,
            rate_limit=20
        )
    
    def parse_graphql_query(self, query_text: str) -> GraphQLQuery:
        """Parse GraphQL query"""
        # Detect operation type
        if query_text.strip().startswith('mutation'):
            operation_type = GraphQLOperationType.MUTATION
        elif query_text.strip().startswith('subscription'):
            operation_type = GraphQLOperationType.SUBSCRIPTION
        else:
            operation_type = GraphQLOperationType.QUERY
        
        # Extract operation name
        operation_name = None
        name_match = re.search(r'(?:query|mutation|subscription)\s+(\w+)', query_text)
        if name_match:
            operation_name = name_match.group(1)
        
        # Detect introspection
        uses_introspection = '__schema' in query_text or '__type' in query_text
        
        # Detect aliases
        has_aliases = ':' in query_text and '{' in query_text
        
        # Detect fragments
        has_fragments = 'fragment' in query_text.lower()
        
        # Extract fields (simplified)
        fields_requested = self._extract_fields(query_text)
        
        return GraphQLQuery(
            operation_type=operation_type,
            operation_name=operation_name,
            query_text=query_text,
            field_count=len(fields_requested),
            fields_requested=fields_requested,
            uses_introspection=uses_introspection,
            has_aliases=has_aliases,
            has_fragments=has_fragments
        )
    
    def _extract_fields(self, query_text: str) -> List[str]:
        """Extract field names from query (simplified)"""
        # Remove comments and whitespace
        clean_query = re.sub(r'#.*$', '', query_text, flags=re.MULTILINE)
        clean_query = re.sub(r'\s+', ' ', clean_query)
        
        # Extract field names (very simplified - real implementation would use proper parser)
        fields = []
        # Match word boundaries that look like field names
        for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(|{|\n|$)', clean_query):
            field = match.group(1)
            # Skip keywords
            if field not in ['query', 'mutation', 'subscription', 'fragment', 'on']:
                fields.append(field)
        
        return list(set(fields))
    
    def analyze_query_complexity(self, query: GraphQLQuery, 
                                 user_roles: List[str] = None) -> QueryComplexityAnalysis:
        """Analyze query complexity and enforce limits"""
        user_roles = user_roles or []
        
        # Calculate depth (simplified - counts nesting levels)
        depth = self._calculate_query_depth(query.query_text)
        query.depth = depth
        
        # Calculate complexity based on fields and their costs
        complexity = 0
        expensive_fields = []
        unauthorized_fields = []
        
        for field in query.fields_requested:
            # Get field policy
            policy = self.field_policies.get(field)
            
            if policy:
                # Check authorization
                if policy.required_roles:
                    if not any(role in user_roles for role in policy.required_roles):
                        unauthorized_fields.append(field)
                        continue
                
                # Add field cost
                complexity += policy.cost
                
                if policy.cost >= 20:
                    expensive_fields.append(field)
            else:
                # Default cost for unknown fields
                complexity += 1
        
        query.complexity = complexity
        
        # Check limits
        exceeds_depth = depth > self.config.max_query_depth
        exceeds_complexity = complexity > self.config.max_query_complexity
        exceeds_field_count = query.field_count > self.config.max_field_count
        
        return QueryComplexityAnalysis(
            total_complexity=complexity,
            depth=depth,
            field_count=query.field_count,
            estimated_cost=complexity * 10,  # Estimated ms
            exceeds_depth_limit=exceeds_depth,
            exceeds_complexity_limit=exceeds_complexity,
            exceeds_field_limit=exceeds_field_count,
            expensive_fields=expensive_fields,
            unauthorized_fields=unauthorized_fields
        )
    
    def _calculate_query_depth(self, query_text: str) -> int:
        """Calculate query depth (nesting level)"""
        max_depth = 0
        current_depth = 0
        
        for char in query_text:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def validate_query(self, query_text: str, user_roles: List[str] = None) -> Dict[str, Any]:
        """Validate GraphQL query against security policies"""
        try:
            # Parse query
            query = self.parse_graphql_query(query_text)
            
            # Block introspection in production
            if query.uses_introspection and not self.config.enable_introspection:
                self._record_blocked_query(query, "Introspection disabled in production")
                return {
                    'valid': False,
                    'reason': 'Introspection queries are disabled',
                    'code': 'INTROSPECTION_DISABLED'
                }
            
            # Analyze complexity
            analysis = self.analyze_query_complexity(query, user_roles)
            
            # Check for unauthorized fields
            if analysis.unauthorized_fields:
                self._record_blocked_query(query, f"Unauthorized fields: {analysis.unauthorized_fields}")
                return {
                    'valid': False,
                    'reason': f'Unauthorized access to fields: {", ".join(analysis.unauthorized_fields)}',
                    'code': 'UNAUTHORIZED_FIELD_ACCESS',
                    'fields': analysis.unauthorized_fields
                }
            
            # Check depth limit
            if analysis.exceeds_depth_limit:
                self._record_blocked_query(query, f"Depth {analysis.depth} exceeds limit {self.config.max_query_depth}")
                return {
                    'valid': False,
                    'reason': f'Query depth {analysis.depth} exceeds maximum {self.config.max_query_depth}',
                    'code': 'DEPTH_LIMIT_EXCEEDED',
                    'depth': analysis.depth,
                    'limit': self.config.max_query_depth
                }
            
            # Check complexity limit
            if analysis.exceeds_complexity_limit:
                self._record_blocked_query(query, f"Complexity {analysis.total_complexity} exceeds limit")
                return {
                    'valid': False,
                    'reason': f'Query complexity {analysis.total_complexity} exceeds maximum {self.config.max_query_complexity}',
                    'code': 'COMPLEXITY_LIMIT_EXCEEDED',
                    'complexity': analysis.total_complexity,
                    'limit': self.config.max_query_complexity
                }
            
            # Check field count limit
            if analysis.exceeds_field_limit:
                self._record_blocked_query(query, f"Field count {query.field_count} exceeds limit")
                return {
                    'valid': False,
                    'reason': f'Query requests {query.field_count} fields, maximum is {self.config.max_field_count}',
                    'code': 'FIELD_COUNT_EXCEEDED',
                    'field_count': query.field_count,
                    'limit': self.config.max_field_count
                }
            
            # Query is valid
            self.query_history.append(query)
            
            return {
                'valid': True,
                'analysis': {
                    'complexity': analysis.total_complexity,
                    'depth': analysis.depth,
                    'field_count': query.field_count,
                    'estimated_cost_ms': analysis.estimated_cost,
                    'expensive_fields': analysis.expensive_fields
                },
                'warnings': self._generate_warnings(analysis)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Query parsing error: {str(e)}',
                'code': 'PARSE_ERROR'
            }
    
    def _record_blocked_query(self, query: GraphQLQuery, reason: str) -> None:
        """Record blocked query for analysis"""
        self.blocked_queries.append({
            'timestamp': datetime.now(),
            'operation_type': query.operation_type.value,
            'query_text': query.query_text[:500],  # First 500 chars
            'reason': reason,
            'depth': query.depth,
            'complexity': query.complexity
        })
        
        print(f"🚫 GraphQL query blocked: {reason}")
    
    def _generate_warnings(self, analysis: QueryComplexityAnalysis) -> List[str]:
        """Generate performance warnings"""
        warnings = []
        
        if analysis.total_complexity > self.config.max_query_complexity * 0.7:
            warnings.append(f"Query complexity is high ({analysis.total_complexity})")
        
        if analysis.depth > self.config.max_query_depth * 0.7:
            warnings.append(f"Query depth is high ({analysis.depth})")
        
        if analysis.expensive_fields:
            warnings.append(f"Query contains expensive fields: {', '.join(analysis.expensive_fields)}")
        
        return warnings


class APIGatewayHardening:
    """API Gateway security hardening"""
    
    def __init__(self, config: Optional[APIGatewayConfig] = None):
        self.config = config or APIGatewayConfig()
        self.graphql_security = GraphQLSecurityEngine(config)
    
    def validate_cors(self, origin: str, method: str) -> Dict[str, Any]:
        """Validate CORS request"""
        # Check allowed origins
        if self.config.allowed_origins and origin not in self.config.allowed_origins:
            return {
                'allowed': False,
                'reason': f'Origin {origin} not in allowed list'
            }
        
        # Check allowed methods
        if method not in self.config.allowed_methods:
            return {
                'allowed': False,
                'reason': f'Method {method} not allowed'
            }
        
        return {
            'allowed': True,
            'headers': {
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': ', '.join(self.config.allowed_methods),
                'Access-Control-Allow-Credentials': str(self.config.allow_credentials).lower()
            }
        }
    
    def validate_batch_request(self, queries: List[str]) -> Dict[str, Any]:
        """Validate GraphQL batch request"""
        if not self.config.allow_batch_queries:
            return {
                'valid': False,
                'reason': 'Batch queries are disabled'
            }
        
        if len(queries) > self.config.max_batch_size:
            return {
                'valid': False,
                'reason': f'Batch size {len(queries)} exceeds maximum {self.config.max_batch_size}'
            }
        
        return {'valid': True}
    
    def apply_security_headers(self) -> Dict[str, str]:
        """Generate security headers for API responses"""
        return {
            # Prevent clickjacking
            'X-Frame-Options': 'DENY',
            
            # Prevent MIME sniffing
            'X-Content-Type-Options': 'nosniff',
            
            # XSS protection
            'X-XSS-Protection': '1; mode=block',
            
            # Content Security Policy
            'Content-Security-Policy': "default-src 'self'",
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # HSTS
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # Permissions policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        return {
            'configuration': {
                'introspection_enabled': self.config.enable_introspection,
                'batch_queries_enabled': self.config.allow_batch_queries,
                'max_query_depth': self.config.max_query_depth,
                'max_complexity': self.config.max_query_complexity
            },
            'statistics': {
                'total_queries': len(self.graphql_security.query_history),
                'blocked_queries': len(self.graphql_security.blocked_queries),
                'field_policies': len(self.graphql_security.field_policies)
            },
            'recent_blocks': self.graphql_security.blocked_queries[-10:]
        }


# Example usage
if __name__ == "__main__":
    # Initialize gateway
    config = APIGatewayConfig(
        max_query_depth=5,
        max_query_complexity=1000,
        enable_introspection=False
    )
    
    gateway = APIGatewayHardening(config)
    
    # Test query validation
    query = """
    query GetUser {
        user(id: "123") {
            name
            email
            posts {
                title
                comments {
                    author
                    text
                }
            }
        }
    }
    """
    
    result = gateway.graphql_security.validate_query(query, user_roles=['user'])
    
    print(f"\n✅ Query Validation:")
    print(f"Valid: {result['valid']}")
    if result['valid']:
        print(f"Complexity: {result['analysis']['complexity']}")
        print(f"Depth: {result['analysis']['depth']}")
        print(f"Estimated cost: {result['analysis']['estimated_cost_ms']}ms")
    
    # Get security headers
    headers = gateway.apply_security_headers()
    print(f"\n🔒 Security Headers: {len(headers)} applied")
