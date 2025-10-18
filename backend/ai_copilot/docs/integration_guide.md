# 🔌 AI Copilot Integration Guide

**Step-by-step guide for integrating AI Copilot into Enterprise Scanner platform.**

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Integration](#architecture-integration)
- [Database Integration](#database-integration)
- [Authentication Integration](#authentication-integration)
- [Scan Pipeline Integration](#scan-pipeline-integration)
- [Frontend Integration](#frontend-integration)
- [Configuration Management](#configuration-management)
- [Testing Integration](#testing-integration)
- [Deployment](#deployment)

---

## ✅ Prerequisites

### **System Requirements**
- Python 3.9+ installed
- PostgreSQL database (existing Enterprise Scanner DB)
- Redis server (for rate limiting)
- Node.js (for frontend build tools)

### **API Keys Required**
- OpenAI API key (GPT-4)
- Anthropic API key (optional, Claude)
- Google AI API key (optional, Gemini)
- Pinecone API key (optional, for production vector DB)

### **Access Requirements**
- Database admin credentials
- Application server access
- Frontend deployment access

---

## 🏗️ Architecture Integration

### **System Overview**

```
┌─────────────────────────────────────────────────────────┐
│            Enterprise Scanner Platform                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐     ┌────────────────┐               │
│  │   Web UI     │────▶│  Flask Backend │               │
│  │  (React/JS)  │     │   (Existing)   │               │
│  └──────────────┘     └────────────────┘               │
│         │                      │                         │
│         │                      ▼                         │
│         │              ┌───────────────┐                │
│         │              │  PostgreSQL   │                │
│         │              │   Database    │                │
│         │              └───────────────┘                │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────┐              │
│  │      AI COPILOT (NEW)                │              │
│  │                                       │              │
│  │  ┌────────────┐   ┌──────────────┐  │              │
│  │  │   Chat     │   │   Analysis   │  │              │
│  │  │    API     │   │   Modules    │  │              │
│  │  └────────────┘   └──────────────┘  │              │
│  │         │                 │          │              │
│  │         ▼                 ▼          │              │
│  │  ┌─────────────────────────────┐   │              │
│  │  │    Knowledge Base (RAG)      │   │              │
│  │  │  ┌──────────┐  ┌──────────┐ │   │              │
│  │  │  │ChromaDB/ │  │ Scan Data│ │   │              │
│  │  │  │ Pinecone │  │  Cache   │ │   │              │
│  │  │  └──────────┘  └──────────┘ │   │              │
│  │  └─────────────────────────────┘   │              │
│  └──────────────────────────────────────┘              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### **Integration Points**

1. **User Authentication** → Access Control module
2. **Scan Results** → Scan Analyzer module
3. **Vulnerability Data** → Knowledge Base
4. **User Queries** → Chat API
5. **Real-time Updates** → WebSocket connections

---

## 🗄️ Database Integration

### **Schema Changes**

Add tables to existing Enterprise Scanner database:

```sql
-- AI Copilot Sessions
CREATE TABLE ai_copilot_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_level VARCHAR(50) NOT NULL,
    context_data JSONB,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_sessions_user ON ai_copilot_sessions(user_id);
CREATE INDEX idx_sessions_activity ON ai_copilot_sessions(last_activity);

-- AI Copilot Queries
CREATE TABLE ai_copilot_queries (
    query_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    query_type VARCHAR(100),
    access_level VARCHAR(50) NOT NULL,
    response_text TEXT,
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_copilot_sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_queries_session ON ai_copilot_queries(session_id);
CREATE INDEX idx_queries_user ON ai_copilot_queries(user_id);
CREATE INDEX idx_queries_type ON ai_copilot_queries(query_type);

-- AI Copilot Rate Limits
CREATE TABLE ai_copilot_rate_limits (
    user_id VARCHAR(255) PRIMARY KEY,
    access_level VARCHAR(50) NOT NULL,
    query_count INTEGER DEFAULT 0,
    reset_at TIMESTAMP,
    last_query_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- AI Copilot Knowledge Base
CREATE TABLE ai_copilot_documents (
    document_id VARCHAR(255) PRIMARY KEY,
    document_type VARCHAR(100) NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_docs_type ON ai_copilot_documents(document_type);
```

### **Run Migrations**

```bash
# Apply schema
psql -U enterprisescanner -d enterprisescanner -f backend/ai_copilot/migrations/001_initial_schema.sql

# Verify tables
psql -U enterprisescanner -d enterprisescanner -c "\dt ai_copilot*"
```

---

## 🔐 Authentication Integration

### **Integrate with Existing Auth**

**Option 1: JWT Token Pass-through**

```python
# backend/api/auth_middleware.py

from backend.ai_copilot import AccessControl, AccessLevel

def get_copilot_access_level(user):
    """Map Enterprise Scanner roles to Copilot access levels."""
    role_mapping = {
        'public': AccessLevel.PUBLIC,
        'sales': AccessLevel.SALES,
        'customer': AccessLevel.CUSTOMER,
        'developer': AccessLevel.DEVELOPER,
        'admin': AccessLevel.ADMIN,
        'military': AccessLevel.MILITARY
    }
    return role_mapping.get(user.role, AccessLevel.PUBLIC)

def copilot_auth_required(f):
    """Decorator for AI Copilot endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verify JWT token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = verify_jwt_token(token)
        
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get copilot access level
        access_level = get_copilot_access_level(user)
        
        # Inject into request context
        g.user = user
        g.copilot_access_level = access_level
        
        return f(*args, **kwargs)
    return decorated_function
```

**Option 2: Session Integration**

```python
# backend/api/session_middleware.py

def init_copilot_session(user_id, session_id):
    """Initialize AI Copilot session from existing user session."""
    from backend.ai_copilot import ContextManager
    
    context_mgr = ContextManager()
    
    # Get user profile
    user = get_user_profile(user_id)
    
    # Create copilot context
    context = {
        'user_id': user_id,
        'access_level': get_copilot_access_level(user),
        'organization_id': user.organization_id,
        'preferences': user.preferences
    }
    
    context_mgr.update_context(session_id, context)
    
    return session_id
```

---

## 🔍 Scan Pipeline Integration

### **Ingest Scan Results**

Connect scan results pipeline to AI Copilot knowledge base:

```python
# backend/services/scan_service.py

from backend.ai_copilot import KnowledgeBase

def process_scan_completion(scan_id):
    """Called when scan completes."""
    # Get scan results
    scan_results = get_scan_results(scan_id)
    
    # Initialize knowledge base
    kb = KnowledgeBase()
    
    # Ingest scan data
    for vulnerability in scan_results.vulnerabilities:
        document = {
            'id': f"vuln_{vulnerability.id}",
            'type': 'vulnerability',
            'scan_id': scan_id,
            'title': vulnerability.name,
            'content': f"""
                Vulnerability: {vulnerability.name}
                Severity: {vulnerability.severity}
                CVSS: {vulnerability.cvss_score}
                Description: {vulnerability.description}
                Affected Asset: {vulnerability.asset_name}
                Location: {vulnerability.location}
                Remediation: {vulnerability.remediation}
            """,
            'metadata': {
                'scan_id': scan_id,
                'vuln_id': vulnerability.id,
                'severity': vulnerability.severity,
                'cvss': vulnerability.cvss_score,
                'asset_id': vulnerability.asset_id
            }
        }
        
        kb.ingest_document(document)
    
    # Ingest scan summary
    summary_doc = {
        'id': f"scan_{scan_id}",
        'type': 'scan_summary',
        'scan_id': scan_id,
        'content': f"""
            Scan Summary
            ID: {scan_id}
            Target: {scan_results.target}
            Total Vulnerabilities: {scan_results.total_count}
            Critical: {scan_results.critical_count}
            High: {scan_results.high_count}
            Medium: {scan_results.medium_count}
            Low: {scan_results.low_count}
            Scan Date: {scan_results.timestamp}
        """,
        'metadata': {
            'scan_id': scan_id,
            'total': scan_results.total_count,
            'critical': scan_results.critical_count
        }
    }
    
    kb.ingest_document(summary_doc)
```

### **Real-time Scan Updates**

Enable AI Copilot to provide real-time scan insights:

```python
# backend/api/websocket_handlers.py

from backend.ai_copilot.interfaces.chat_api import ChatAPI

@socketio.on('scan_progress')
def handle_scan_progress(data):
    """Send scan progress to AI Copilot for real-time commentary."""
    scan_id = data['scan_id']
    progress = data['progress']
    
    # Notify copilot
    copilot = ChatAPI()
    
    if progress['vulnerabilities_found'] > 0:
        # Generate AI summary
        summary = copilot.analyze_partial_scan(scan_id, progress)
        
        # Emit to user
        emit('copilot_insight', {
            'scan_id': scan_id,
            'message': summary['message'],
            'quick_actions': summary['quick_actions']
        })
```

---

## 🖥️ Frontend Integration

### **Add Chat Widget to Dashboard**

```html
<!-- website/dashboard.html -->

<!-- AI Copilot Widget -->
<div id="ai-copilot-widget" class="copilot-widget collapsed">
    <div class="copilot-header">
        <h3>🤖 AI Security Assistant</h3>
        <button class="copilot-toggle">−</button>
    </div>
    
    <div class="copilot-body">
        <div class="copilot-messages" id="copilot-messages"></div>
        
        <div class="copilot-input-group">
            <input 
                type="text" 
                id="copilot-input" 
                placeholder="Ask about your scans..."
                autocomplete="off"
            />
            <button id="copilot-send">Send</button>
        </div>
        
        <div class="copilot-quick-replies" id="copilot-quick-replies"></div>
    </div>
</div>

<script src="/js/ai_copilot.js"></script>
<link rel="stylesheet" href="/css/ai_copilot.css" />
```

### **Initialize Chat Client**

```javascript
// website/js/ai_copilot.js

class AICopilot {
    constructor() {
        this.apiUrl = '/api/copilot';
        this.sessionId = this.generateSessionId();
        this.socket = null;
        this.init();
    }
    
    init() {
        // Connect WebSocket
        this.socket = io(this.apiUrl);
        
        this.socket.on('connect', () => {
            console.log('AI Copilot connected');
        });
        
        this.socket.on('chunk', (data) => {
            this.handleChunk(data);
        });
        
        this.socket.on('complete', (data) => {
            this.handleComplete(data);
        });
        
        // Setup UI
        this.setupEventListeners();
    }
    
    sendMessage(message) {
        this.socket.emit('chat', {
            message: message,
            user_id: getCurrentUserId(),
            session_id: this.sessionId,
            access_level: getUserAccessLevel()
        });
        
        // Show user message
        this.addMessage('user', message);
    }
    
    // ... rest of implementation
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.copilot = new AICopilot();
});
```

---

## ⚙️ Configuration Management

### **Centralized Config**

```python
# backend/config/copilot_config.py

import os
from dataclasses import dataclass

@dataclass
class CopilotConfig:
    # LLM Settings
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    default_provider: str = 'openai'
    default_model: str = 'gpt-4-turbo'
    
    # Database
    database_url: str = os.getenv('DATABASE_URL')
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Vector DB
    use_pinecone: bool = os.getenv('USE_PINECONE', 'false').lower() == 'true'
    pinecone_api_key: str = os.getenv('PINECONE_API_KEY', '')
    pinecone_environment: str = os.getenv('PINECONE_ENVIRONMENT', '')
    
    # API Settings
    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('API_PORT', '5000'))
    enable_cors: bool = os.getenv('ENABLE_CORS', 'true').lower() == 'true'
    enable_websocket: bool = os.getenv('ENABLE_WEBSOCKET', 'true').lower() == 'true'
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    
    # Security
    jwt_secret_key: str = os.getenv('JWT_SECRET_KEY')
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'logs/copilot.log')

# Global config instance
config = CopilotConfig()
```

---

## 🧪 Testing Integration

### **Integration Tests**

```python
# tests/integration/test_copilot_integration.py

import pytest
from backend.ai_copilot import CopilotEngine, AccessLevel

def test_copilot_with_real_scan():
    """Test AI Copilot with actual scan data."""
    # Create test scan
    scan_id = create_test_scan()
    
    # Initialize copilot
    engine = CopilotEngine()
    
    # Query about scan
    query = Query(
        query_id="test_001",
        user_id="test_user",
        session_id="test_session",
        message=f"Analyze scan {scan_id}",
        access_level=AccessLevel.CUSTOMER
    )
    
    # Process
    response = engine.process_query(query)
    
    # Verify
    assert response.success is True
    assert scan_id in response.response_text
    assert response.confidence_score > 0.7
    
def test_authentication_integration():
    """Test auth integration."""
    # ... implementation
    
def test_websocket_connection():
    """Test WebSocket integration."""
    # ... implementation
```

---

## 🚀 Deployment

### **Step-by-Step Deployment**

1. **Install Dependencies**
   ```bash
   cd backend/ai_copilot
   pip install -r requirements.txt
   ```

2. **Apply Database Migrations**
   ```bash
   python backend/ai_copilot/migrations/migrate.py
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start AI Copilot Service**
   ```bash
   python -m backend.ai_copilot.interfaces.chat_api
   ```

5. **Update Frontend**
   ```bash
   # Copy widget files
   cp frontend/ai_copilot_widget.html website/partials/
   cp frontend/ai_copilot.js website/js/
   cp frontend/ai_copilot.css website/css/
   
   # Rebuild frontend
   npm run build
   ```

6. **Verify Integration**
   ```bash
   curl http://localhost:5000/api/copilot/health
   ```

7. **Monitor Logs**
   ```bash
   tail -f logs/copilot.log
   ```

---

## 📊 Monitoring

Add AI Copilot metrics to existing monitoring:

```python
# backend/monitoring/copilot_metrics.py

from prometheus_client import Counter, Histogram

copilot_queries_total = Counter(
    'copilot_queries_total',
    'Total AI Copilot queries',
    ['access_level', 'query_type']
)

copilot_response_time = Histogram(
    'copilot_response_time_seconds',
    'AI Copilot response time'
)

copilot_errors_total = Counter(
    'copilot_errors_total',
    'Total AI Copilot errors',
    ['error_type']
)
```

---

## ✅ Integration Checklist

- [ ] Database tables created
- [ ] Authentication integrated
- [ ] Scan pipeline connected
- [ ] Frontend widget deployed
- [ ] Environment variables configured
- [ ] Rate limiting enabled
- [ ] Monitoring setup
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Team trained on new features

---

**Integration complete! 🎉**

For support: support@enterprisescanner.com
