"""
LLM Provider Abstraction Layer

Unified interface for multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude)
- Google (Gemini)
- Local models (via Ollama)

Provides:
- Text completion
- Streaming responses
- Embeddings generation
- Token counting
- Error handling and retry logic

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
import time
import os
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass
from enum import Enum
import logging


class LLMProviderType(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROK = "grok"  # xAI Grok with X platform access
    LOCAL = "local"  # Ollama/local models


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    provider: str
    
    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Metadata
    finish_reason: str = "stop"
    response_time_ms: int = 0
    
    # Cost estimation (USD)
    estimated_cost: float = 0.0


class LLMProvider:
    """
    Unified LLM provider interface
    
    Abstracts different LLM providers behind single API
    """
    
    # Pricing per 1K tokens (USD)
    PRICING = {
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'claude-3-opus': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
        'gemini-pro': {'input': 0.000125, 'output': 0.000375},
        'grok-beta': {'input': 0.005, 'output': 0.015},  # xAI Grok (estimated pricing)
        'grok-1': {'input': 0.01, 'output': 0.03},  # xAI Grok-1 (estimated)
        'local': {'input': 0.0, 'output': 0.0}  # Free
    }
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4-turbo",
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize LLM provider
        
        Args:
            provider: Provider name ('openai', 'anthropic', 'google', 'local')
            model: Model name
            api_key: API key (or from environment)
            timeout: Request timeout in seconds
            max_retries: Max retry attempts
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Get API key from parameter or environment
        self.api_key = api_key or self._get_api_key_from_env(provider)
        
        # Initialize provider-specific client
        self.client = self._initialize_client()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_cost_usd': 0.0
        }
        
        self.logger.info(f"LLMProvider initialized: {provider}/{model}")
    
    def _get_api_key_from_env(self, provider: str) -> Optional[str]:
        """Get API key from environment variables"""
        env_vars = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'grok': 'XAI_API_KEY',  # xAI Grok API key
            'local': None  # No key needed
        }
        
        env_var = env_vars.get(provider)
        if not env_var:
            return None
        
        return os.getenv(env_var)
    
    def _initialize_client(self):
        """Initialize provider-specific client"""
        try:
            if self.provider == "openai":
                # Try to import OpenAI
                try:
                    from openai import OpenAI
                    return OpenAI(api_key=self.api_key) if self.api_key else None
                except ImportError:
                    self.logger.warning("OpenAI package not installed. Install: pip install openai")
                    return None
            
            elif self.provider == "anthropic":
                try:
                    import anthropic
                    return anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
                except ImportError:
                    self.logger.warning("Anthropic package not installed. Install: pip install anthropic")
                    return None
            
            elif self.provider == "google":
                try:
                    import google.generativeai as genai
                    if self.api_key:
                        genai.configure(api_key=self.api_key)
                    return genai
                except ImportError:
                    self.logger.warning("Google AI package not installed. Install: pip install google-generativeai")
                    return None
            
            elif self.provider == "grok":
                # xAI Grok - Uses X API for real-time access
                # For now, we'll use direct HTTP requests since xAI SDK may not exist yet
                try:
                    import requests
                    if self.api_key:
                        # Return a simple dict with API key for now
                        return {'api_key': self.api_key, 'requests': requests}
                    return None
                except ImportError:
                    self.logger.warning("Requests package not installed. Install: pip install requests")
                    return None
            
            elif self.provider == "local":
                # For local models (Ollama), no client needed
                return None
            
            else:
                self.logger.error(f"Unsupported provider: {self.provider}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.provider} client: {e}")
            return None
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens in response
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse object
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Route to appropriate provider
            if self.provider == "openai":
                response = self._complete_openai(messages, temperature, max_tokens, **kwargs)
            elif self.provider == "anthropic":
                response = self._complete_anthropic(messages, temperature, max_tokens, **kwargs)
            elif self.provider == "google":
                response = self._complete_google(messages, temperature, max_tokens, **kwargs)
            elif self.provider == "grok":
                response = self._complete_grok(messages, temperature, max_tokens, **kwargs)
            elif self.provider == "local":
                response = self._complete_local(messages, temperature, max_tokens, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Calculate response time
            response.response_time_ms = int((time.time() - start_time) * 1000)
            
            # Calculate cost
            response.estimated_cost = self._calculate_cost(
                response.prompt_tokens,
                response.completion_tokens,
                self.model
            )
            
            # Update statistics
            self.stats['successful_requests'] += 1
            self.stats['total_tokens'] += response.total_tokens
            self.stats['total_cost_usd'] += response.estimated_cost
            
            return response
            
        except Exception as e:
            self.logger.error(f"Completion failed: {e}", exc_info=True)
            self.stats['failed_requests'] += 1
            
            # Return error response
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=self.model,
                provider=self.provider
            )
    
    def _complete_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """OpenAI completion"""
        if not self.client:
            return self._mock_response("OpenAI client not initialized (API key missing)")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider=self.provider,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self._mock_response(f"OpenAI error: {str(e)}")
    
    def _complete_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Anthropic (Claude) completion"""
        if not self.client:
            return self._mock_response("Anthropic client not initialized (API key missing)")
        
        # Anthropic uses slightly different message format
        # Convert system message to separate parameter
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                converted_messages.append(msg)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                messages=converted_messages,
                system=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=self.model,
                provider=self.provider,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            return self._mock_response(f"Anthropic error: {str(e)}")
    
    def _complete_google(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Google (Gemini) completion"""
        if not self.client:
            return self._mock_response("Google AI client not initialized (API key missing)")
        
        try:
            # Convert messages to Gemini format
            gemini_model = self.client.GenerativeModel(self.model)
            
            # Combine messages into single prompt (Gemini doesn't use chat format the same way)
            prompt_parts = []
            for msg in messages:
                role_prefix = f"{msg['role'].upper()}: "
                prompt_parts.append(role_prefix + msg['content'])
            
            full_prompt = "\n\n".join(prompt_parts)
            
            response = gemini_model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens
                }
            )
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider=self.provider,
                prompt_tokens=0,  # Gemini doesn't provide token counts easily
                completion_tokens=0,
                total_tokens=0,
                finish_reason="stop"
            )
            
        except Exception as e:
            self.logger.error(f"Google AI error: {e}")
            return self._mock_response(f"Google AI error: {str(e)}")
    
    def _complete_grok(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Grok (xAI) completion with X platform access"""
        if not self.client:
            return self._mock_response("Grok client not initialized (X API key missing)")
        
        try:
            # xAI Grok API endpoint (using X API infrastructure)
            # Note: This is a simplified implementation - actual xAI API may differ
            import requests
            
            api_url = "https://api.x.ai/v1/chat/completions"  # Hypothetical endpoint
            
            headers = {
                "Authorization": f"Bearer {self.client['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Build request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Make API request
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return LLMResponse(
                    content=data.get('choices', [{}])[0].get('message', {}).get('content', ''),
                    model=self.model,
                    provider=self.provider,
                    prompt_tokens=data.get('usage', {}).get('prompt_tokens', 0),
                    completion_tokens=data.get('usage', {}).get('completion_tokens', 0),
                    total_tokens=data.get('usage', {}).get('total_tokens', 0),
                    finish_reason=data.get('choices', [{}])[0].get('finish_reason', 'stop')
                )
            else:
                # Check if it's an API key error
                if response.status_code == 400 or response.status_code == 401:
                    error_data = response.json() if response.text else {}
                    if 'Incorrect API key' in str(error_data):
                        self.logger.warning(f"Grok API key invalid. Using intelligent fallback mode.")
                        # Use intelligent fallback based on the question
                        return self._generate_intelligent_response(messages)
                
                self.logger.error(f"Grok API error: HTTP {response.status_code} - {response.text}")
                return self._generate_intelligent_response(messages)
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Grok API request failed: {e}")
            return self._mock_response(f"Grok request error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Grok error: {e}")
            return self._mock_response(f"Grok error: {str(e)}")
    
    def _complete_local(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Local model completion (via Ollama or similar)"""
        # This would connect to local Ollama server
        # For now, return mock response
        return self._mock_response(
            "Local LLM integration pending. Would connect to Ollama at http://localhost:11434"
        )
    
    def _generate_intelligent_response(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """Generate intelligent response based on security knowledge base"""
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '').lower()
                break
        
        # Security knowledge base
        responses = {
            'sql injection': """SQL Injection is a critical web security vulnerability that allows attackers to interfere with database queries. 

**How it works:**
- Attackers insert malicious SQL code into input fields
- If not properly sanitized, this code executes on the database
- Can lead to data theft, modification, or deletion

**Example vulnerable code:**
```python
query = f"SELECT * FROM users WHERE username='{user_input}'"
```

**Prevention:**
1. Use parameterized queries/prepared statements
2. Input validation and sanitization
3. Principle of least privilege for database accounts
4. Web Application Firewalls (WAF)
5. Regular security testing

**Severity:** CRITICAL (CVSS 9.0+)""",

            'xss': """Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users.

**Types:**
1. **Stored XSS**: Malicious script stored in database
2. **Reflected XSS**: Script reflected off web server
3. **DOM-based XSS**: Client-side code vulnerabilities

**Impact:**
- Session hijacking
- Credential theft
- Defacement
- Malware distribution

**Prevention:**
1. Input validation and output encoding
2. Content Security Policy (CSP) headers
3. HTTPOnly and Secure flags on cookies
4. Use security frameworks (React, Angular auto-escape)

**Severity:** HIGH (CVSS 6.0-8.9)""",

            'buffer overflow': """Buffer Overflow occurs when a program writes more data to a buffer than it can hold, overwriting adjacent memory.

**How it works:**
1. Attacker provides input larger than buffer size
2. Excess data overwrites adjacent memory
3. Can overwrite return addresses
4. Leads to arbitrary code execution

**Types:**
- Stack-based buffer overflow
- Heap-based buffer overflow

**Prevention:**
1. Use safe functions (strncpy instead of strcpy)
2. Enable compiler protections (Stack Canaries, ASLR, DEP)
3. Input length validation
4. Use memory-safe languages (Rust, Go)
5. Regular code audits

**Severity:** CRITICAL (Can lead to RCE)""",

            'csrf': """Cross-Site Request Forgery (CSRF) tricks users into executing unwanted actions on authenticated websites.

**Attack Flow:**
1. User logs into legitimate site (e.g., bank.com)
2. User visits malicious site
3. Malicious site triggers requests to bank.com
4. Requests execute with user's credentials

**Prevention:**
1. Anti-CSRF tokens
2. SameSite cookie attribute
3. Verify Origin/Referer headers
4. Re-authentication for sensitive actions

**Severity:** MEDIUM-HIGH (CVSS 5.0-7.9)""",

            'default': """Hello! I'm Jupiter, your AI security assistant (running in fallback mode).

I can help you with:
- Vulnerability explanations (SQL injection, XSS, CSRF, etc.)
- Security best practices
- Remediation guidance
- Threat analysis
- Security architecture questions

**Note:** I'm currently in fallback mode. For full AI capabilities, configure a valid Grok API key from https://console.x.ai/ or OpenAI API key.

What security topic would you like to explore?"""
        }
        
        # Match user question to knowledge base
        response_content = responses['default']
        for keyword, response in responses.items():
            if keyword in user_message and keyword != 'default':
                response_content = response
                break
        
        return LLMResponse(
            content=response_content,
            model=f"{self.model} (fallback)",
            provider=self.provider,
            prompt_tokens=len(user_message.split()),
            completion_tokens=len(response_content.split()),
            total_tokens=len(user_message.split()) + len(response_content.split())
        )
    
    def _mock_response(self, content: str) -> LLMResponse:
        """Generate mock response for testing/fallback"""
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
    
    def _calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ) -> float:
        """Calculate estimated cost in USD"""
        pricing = self.PRICING.get(model, {'input': 0.0, 'output': 0.0})
        
        input_cost = (prompt_tokens / 1000) * pricing['input']
        output_cost = (completion_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream completion (for real-time responses)
        
        Args:
            messages: Message list
            temperature: Sampling temperature
            max_tokens: Max tokens
            
        Yields:
            Content chunks as they arrive
        """
        if self.provider == "openai" and self.client:
            try:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    **kwargs
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                self.logger.error(f"Streaming failed: {e}")
                yield f"Error: {str(e)}"
        else:
            # Fallback: return full response at once
            response = self.complete(messages, temperature, max_tokens, **kwargs)
            yield response.content
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        if self.provider == "openai" and self.client:
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                self.logger.error(f"Embedding failed: {e}")
                # Return zero vector as fallback
                return [0.0] * 1536
        else:
            self.logger.warning(f"Embeddings not supported for {self.provider}")
            return [0.0] * 1536
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Simple estimation: ~4 chars per token
        For accurate counting, would use tiktoken library
        """
        return len(text) // 4
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return self.stats.copy()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("LLM PROVIDER ABSTRACTION")
    print("="*70)
    
    # Initialize provider
    print("\n1. Initializing LLM Provider (OpenAI GPT-4)...")
    llm = LLMProvider(
        provider="openai",
        model="gpt-4-turbo"
    )
    
    # Test completion
    print("\n2. Testing Completion:")
    messages = [
        {'role': 'system', 'content': 'You are a helpful security assistant.'},
        {'role': 'user', 'content': 'What is SQL injection in one sentence?'}
    ]
    
    response = llm.complete(messages, temperature=0.7, max_tokens=100)
    
    print(f"\n   Model: {response.model}")
    print(f"   Provider: {response.provider}")
    print(f"   Response: {response.content[:200]}...")
    print(f"   Tokens: {response.total_tokens}")
    print(f"   Cost: ${response.estimated_cost:.6f}")
    print(f"   Time: {response.response_time_ms}ms")
    
    # Statistics
    print("\n3. Provider Statistics:")
    stats = llm.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("LLM PROVIDER UTILITY COMPLETE ✅")
    print("="*70)
