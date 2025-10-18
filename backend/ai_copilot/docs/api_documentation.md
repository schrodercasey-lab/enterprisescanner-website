# 📡 AI Copilot API Documentation

**Complete REST API and WebSocket reference for AI Copilot integration.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [REST Endpoints](#rest-endpoints)
- [WebSocket Events](#websocket-events)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Code Examples](#code-examples)

---

## 🌐 Overview

The AI Copilot API provides both REST and WebSocket interfaces for real-time AI-powered security assistance. It supports:

- **Natural language queries** about security vulnerabilities
- **Real-time response streaming** via WebSocket
- **Role-based access control** with 6 levels
- **Rate limiting** to prevent abuse
- **Session management** for conversation context

---

## 🔗 Base URL

```
Production:  https://enterprisescanner.com/api/copilot
Development: http://localhost:5000/api/copilot
```

---

## 🔐 Authentication

All endpoints require authentication via JWT token in the `Authorization` header:

```http
Authorization: Bearer <your-jwt-token>
```

### **Get JWT Token**

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": "user_123",
  "access_level": "customer"
}
```

---

## 🎯 REST Endpoints

### **1. Health Check**

Check API availability and status.

```http
GET /api/copilot/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T12:00:00Z",
  "copilot_engine": "available",
  "websocket": "enabled",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is down

---

### **2. Send Message**

Send a chat message and receive AI response.

```http
POST /api/copilot/chat
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "message": "What is SQL injection?",
  "user_id": "user_123",
  "session_id": "session_456",
  "access_level": "customer",
  "include_sources": true,
  "format": "markdown",
  "stream": false,
  "metadata": {
    "scan_id": "scan_789",
    "context": "analyzing recent scan"
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | ✅ Yes | User query (max 2000 chars) |
| `user_id` | string | ✅ Yes | Unique user identifier |
| `session_id` | string | ❌ No | Session ID for context (auto-generated if omitted) |
| `access_level` | string | ❌ No | Access level: public, sales, customer, developer, admin, military |
| `include_sources` | boolean | ❌ No | Include source citations (default: true) |
| `format` | string | ❌ No | Response format: text, markdown, json, html (default: markdown) |
| `stream` | boolean | ❌ No | Enable streaming (use SSE endpoint instead) |
| `metadata` | object | ❌ No | Additional context data |

**Response:**
```json
{
  "success": true,
  "response": "SQL injection is a code injection technique that exploits vulnerabilities...",
  "session_id": "session_456",
  "query_id": "query_789",
  "query_type": "vulnerability_explanation",
  "sources": [
    {
      "title": "OWASP Top 10",
      "url": "https://owasp.org/www-project-top-ten/",
      "relevance": 0.95
    }
  ],
  "citations": [
    "OWASP defines SQL injection as..."
  ],
  "quick_replies": [
    "How do I prevent SQL injection?",
    "Show me code examples",
    "Is my application vulnerable?"
  ],
  "confidence_score": 0.92,
  "processing_time_ms": 1234,
  "tokens_used": 567
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Access denied
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

### **3. Stream Response (SSE)**

Stream AI response in real-time using Server-Sent Events.

```http
POST /api/copilot/stream
Content-Type: application/json
Authorization: Bearer <token>
Accept: text/event-stream
```

**Request Body:** Same as `/chat` endpoint

**Response (SSE Stream):**
```
data: {"type": "start", "session_id": "session_456"}

data: {"type": "chunk", "content": "SQL injection is "}

data: {"type": "chunk", "content": "a code injection "}

data: {"type": "chunk", "content": "technique..."}

data: {"type": "complete", "response": "SQL injection is a code injection technique...", "confidence_score": 0.92}
```

**SSE Event Types:**
- `start` - Stream started
- `chunk` - Content chunk
- `complete` - Stream complete with full response
- `error` - Error occurred

---

### **4. Get Context**

Retrieve conversation context for a session.

```http
GET /api/copilot/context/:session_id
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "session_456",
  "user_id": "user_123",
  "access_level": "customer",
  "created_at": "2025-10-17T10:00:00Z",
  "last_activity": "2025-10-17T12:00:00Z",
  "message_count": 15,
  "context": {
    "scan_id": "scan_789",
    "current_topic": "SQL injection",
    "recent_queries": [
      "What is SQL injection?",
      "How do I prevent it?"
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Session not found

---

### **5. Clear Context**

Clear conversation history for a session.

```http
DELETE /api/copilot/context/:session_id
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Context cleared successfully",
  "session_id": "session_456"
}
```

---

### **6. System Status**

Get detailed system status and statistics.

```http
GET /api/copilot/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "operational",
  "uptime_seconds": 86400,
  "statistics": {
    "total_queries": 12345,
    "active_sessions": 42,
    "average_response_time_ms": 1234,
    "success_rate": 0.98
  },
  "llm_providers": {
    "openai": "available",
    "anthropic": "available",
    "google": "unavailable"
  },
  "vector_db": {
    "type": "chromadb",
    "status": "healthy",
    "document_count": 5678
  },
  "rate_limits": {
    "public": 10,
    "customer": 1000,
    "admin": 2000
  }
}
```

---

## 🔌 WebSocket Events

Connect to WebSocket for real-time streaming:

```javascript
const socket = io('http://localhost:5000', {
  path: '/socket.io',
  transports: ['websocket', 'polling']
});
```

### **Client → Server Events**

#### **`chat`**
Send a chat message.

```javascript
socket.emit('chat', {
  message: "What is SQL injection?",
  user_id: "user_123",
  session_id: "session_456",
  access_level: "customer",
  stream: true
});
```

#### **`disconnect`**
Disconnect from server.

```javascript
socket.disconnect();
```

---

### **Server → Client Events**

#### **`connect`**
Connection established.

```javascript
socket.on('connect', () => {
  console.log('Connected to AI Copilot');
});
```

#### **`chunk`**
Response chunk received (streaming).

```javascript
socket.on('chunk', (data) => {
  console.log('Chunk:', data.content);
  // data = { content: "SQL injection is ", index: 0 }
});
```

#### **`complete`**
Response complete.

```javascript
socket.on('complete', (data) => {
  console.log('Complete:', data.response);
  // data = { response: "...", confidence_score: 0.92, ... }
});
```

#### **`error`**
Error occurred.

```javascript
socket.on('error', (error) => {
  console.error('Error:', error.message);
  // error = { message: "Rate limit exceeded", code: 429 }
});
```

#### **`disconnect`**
Disconnected from server.

```javascript
socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
});
```

---

## 📊 Data Models

### **ChatRequest**

```typescript
interface ChatRequest {
  message: string;              // User query (required)
  user_id: string;              // User ID (required)
  session_id?: string;          // Session ID (optional)
  access_level?: AccessLevel;   // Access level (optional)
  include_sources?: boolean;    // Include sources (default: true)
  format?: ResponseFormat;      // Response format (default: markdown)
  stream?: boolean;             // Enable streaming (default: false)
  metadata?: Record<string, any>; // Additional context
}
```

### **ChatResponse**

```typescript
interface ChatResponse {
  success: boolean;             // Request success
  response: string;             // AI response text
  session_id: string;           // Session ID
  query_id: string;             // Query ID
  query_type: QueryType;        // Query type detected
  sources?: Source[];           // Source citations
  citations?: string[];         // Text citations
  quick_replies?: string[];     // Suggested follow-ups
  confidence_score: number;     // Confidence (0-1)
  processing_time_ms: number;   // Processing time
  tokens_used: number;          // LLM tokens used
}
```

### **AccessLevel**

```typescript
enum AccessLevel {
  PUBLIC = "public",         // 10 queries/day
  SALES = "sales",           // 100 queries/day
  CUSTOMER = "customer",     // 1,000 queries/day
  DEVELOPER = "developer",   // 500 queries/day
  ADMIN = "admin",           // 2,000 queries/day
  MILITARY = "military"      // Unlimited
}
```

### **QueryType**

```typescript
enum QueryType {
  GENERAL = "general",
  SCAN_ANALYSIS = "scan_analysis",
  VULNERABILITY_EXPLANATION = "vulnerability_explanation",
  THREAT_INTELLIGENCE = "threat_intelligence",
  REMEDIATION = "remediation",
  COMPLIANCE = "compliance",
  CODE_GENERATION = "code_generation",
  API_DOCUMENTATION = "api_documentation",
  SYSTEM_CONFIGURATION = "system_configuration"
}
```

---

## ⚠️ Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": 429,
    "type": "RateLimitError",
    "message": "Rate limit exceeded. You have reached your daily quota.",
    "details": {
      "limit": 1000,
      "used": 1000,
      "reset_at": "2025-10-18T00:00:00Z"
    },
    "recovery": "Wait until midnight UTC or upgrade your access level."
  }
}
```

### **Error Codes**

| Code | Type | Description |
|------|------|-------------|
| 400 | ValidationError | Invalid input parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | AccessDeniedError | Insufficient permissions |
| 404 | NotFound | Resource not found |
| 429 | RateLimitError | Rate limit exceeded |
| 500 | InternalServerError | Server error |
| 503 | ServiceUnavailable | Service temporarily unavailable |

---

## ⏱️ Rate Limiting

Rate limits are enforced per user per day:

| Access Level | Daily Limit | Burst Limit |
|--------------|-------------|-------------|
| Public | 10 | 5/minute |
| Sales | 100 | 20/minute |
| Customer | 1,000 | 50/minute |
| Developer | 500 | 30/minute |
| Admin | 2,000 | 100/minute |
| Military | Unlimited | Unlimited |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 500
X-RateLimit-Reset: 1697500800
```

---

## 💻 Code Examples

### **Python**

```python
import requests

# Send message
response = requests.post(
    'http://localhost:5000/api/copilot/chat',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'message': 'What is SQL injection?',
        'user_id': 'user_123',
        'access_level': 'customer'
    }
)

data = response.json()
print(data['response'])
```

### **JavaScript (Fetch)**

```javascript
const response = await fetch('http://localhost:5000/api/copilot/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    message: 'What is SQL injection?',
    user_id: 'user_123',
    access_level: 'customer'
  })
});

const data = await response.json();
console.log(data.response);
```

### **JavaScript (WebSocket)**

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  socket.emit('chat', {
    message: 'What is SQL injection?',
    user_id: 'user_123'
  });
});

socket.on('chunk', (data) => {
  process.stdout.write(data.content);
});

socket.on('complete', (data) => {
  console.log('\n\nConfidence:', data.confidence_score);
});
```

### **cURL**

```bash
curl -X POST http://localhost:5000/api/copilot/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "message": "What is SQL injection?",
    "user_id": "user_123",
    "access_level": "customer"
  }'
```

---

## 📞 Support

- **Documentation**: https://enterprisescanner.com/docs/ai-copilot
- **Email**: support@enterprisescanner.com
- **GitHub**: https://github.com/enterprisescanner/ai-copilot

---

**Last Updated**: October 17, 2025  
**API Version**: 1.0.0
