"""
RAG (Retrieval-Augmented Generation) System

Combines knowledge base search with LLM generation for accurate,
context-aware responses with citations.

Features:
- Context retrieval from knowledge base
- Re-ranking for relevance
- Prompt augmentation with retrieved context
- Citation generation
- Source attribution
- Confidence scoring

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class RetrievedContext:
    """Context retrieved from knowledge base"""
    content: str
    source: str
    doc_type: str
    relevance_score: float
    chunk_id: str
    
    # Citation information
    doc_title: str = ""
    page_number: Optional[int] = None
    section: Optional[str] = None


@dataclass
class Citation:
    """Source citation"""
    citation_id: int
    source: str
    doc_title: str
    doc_type: str
    relevance_score: float
    
    # Optional details
    excerpt: Optional[str] = None
    url: Optional[str] = None
    page: Optional[int] = None


@dataclass
class RAGResponse:
    """Response from RAG system"""
    answer: str
    citations: List[Citation]
    contexts_used: List[RetrievedContext]
    
    # Confidence and quality metrics
    confidence_score: float = 0.0
    answer_supported: bool = True  # Whether answer is supported by retrieved context
    
    # Performance metrics
    retrieval_time_ms: int = 0
    generation_time_ms: int = 0
    total_time_ms: int = 0
    
    # Metadata
    query: str = ""
    contexts_retrieved: int = 0
    contexts_used_count: int = 0
    model_used: str = ""


class RAGSystem:
    """
    Retrieval-Augmented Generation System
    
    Enhances LLM responses with knowledge base context
    """
    
    def __init__(
        self,
        knowledge_base=None,
        llm_provider=None,
        top_k_retrieve: int = 10,  # Retrieve top 10 chunks
        top_k_use: int = 5,  # Use top 5 for context
        max_context_length: int = 4000  # Max tokens in context
    ):
        """
        Initialize RAG system
        
        Args:
            knowledge_base: KnowledgeBase instance
            llm_provider: LLMProvider instance
            top_k_retrieve: Number of chunks to retrieve
            top_k_use: Number of chunks to use in prompt
            max_context_length: Max context tokens
        """
        self.logger = logging.getLogger(__name__)
        
        self.knowledge_base = knowledge_base
        self.llm_provider = llm_provider
        
        self.top_k_retrieve = top_k_retrieve
        self.top_k_use = top_k_use
        self.max_context_length = max_context_length
        
        # Initialize if not provided
        if not self.knowledge_base:
            try:
                from backend.ai_copilot.knowledge.knowledge_base import KnowledgeBase
                self.knowledge_base = KnowledgeBase()
            except Exception as e:
                self.logger.warning(f"Knowledge base not available: {e}")
        
        if not self.llm_provider:
            try:
                from backend.ai_copilot.utils.llm_providers import LLMProvider
                self.llm_provider = LLMProvider(provider="openai", model="gpt-4-turbo")
            except Exception as e:
                self.logger.warning(f"LLM provider not available: {e}")
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_retrieval_time_ms': 0,
            'avg_generation_time_ms': 0,
            'avg_contexts_retrieved': 0,
            'avg_contexts_used': 0
        }
        
        self.logger.info("RAG System initialized")
    
    def generate(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        doc_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> RAGResponse:
        """
        Generate response using RAG
        
        Args:
            query: User query
            conversation_history: Previous messages
            doc_types: Filter by document types
            tags: Filter by tags
            system_prompt: Custom system prompt
            
        Returns:
            RAGResponse object
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        try:
            # Step 1: Retrieve relevant context
            retrieval_start = time.time()
            contexts = self._retrieve_context(query, doc_types, tags)
            retrieval_time = int((time.time() - retrieval_start) * 1000)
            
            # Step 2: Re-rank contexts
            contexts = self._rerank_contexts(contexts, query)
            
            # Step 3: Select top contexts within token budget
            selected_contexts = self._select_contexts(contexts, self.top_k_use)
            
            # Step 4: Build augmented prompt
            augmented_messages = self._build_augmented_prompt(
                query,
                selected_contexts,
                conversation_history,
                system_prompt
            )
            
            # Step 5: Generate response
            generation_start = time.time()
            llm_response = self._generate_with_llm(augmented_messages)
            generation_time = int((time.time() - generation_start) * 1000)
            
            # Step 6: Extract citations
            citations = self._generate_citations(selected_contexts)
            
            # Step 7: Calculate confidence
            confidence = self._calculate_confidence(
                llm_response.content,
                selected_contexts,
                llm_response.total_tokens
            )
            
            # Build response
            total_time = int((time.time() - start_time) * 1000)
            
            rag_response = RAGResponse(
                answer=llm_response.content,
                citations=citations,
                contexts_used=selected_contexts,
                confidence_score=confidence,
                answer_supported=True,
                retrieval_time_ms=retrieval_time,
                generation_time_ms=generation_time,
                total_time_ms=total_time,
                query=query,
                contexts_retrieved=len(contexts),
                contexts_used_count=len(selected_contexts),
                model_used=llm_response.model
            )
            
            # Update statistics
            self.stats['successful_queries'] += 1
            self._update_stats(rag_response)
            
            return rag_response
            
        except Exception as e:
            self.logger.error(f"RAG generation failed: {e}", exc_info=True)
            self.stats['failed_queries'] += 1
            
            # Return error response
            return RAGResponse(
                answer=f"I apologize, but I encountered an error: {str(e)}",
                citations=[],
                contexts_used=[],
                confidence_score=0.0,
                answer_supported=False,
                query=query
            )
    
    def _retrieve_context(
        self,
        query: str,
        doc_types: Optional[List[str]],
        tags: Optional[List[str]]
    ) -> List[RetrievedContext]:
        """Retrieve relevant context from knowledge base"""
        if not self.knowledge_base:
            return []
        
        # Search knowledge base
        search_results = self.knowledge_base.search(
            query=query,
            top_k=self.top_k_retrieve,
            doc_types=doc_types,
            tags=tags
        )
        
        # Convert to RetrievedContext objects
        contexts = []
        for result in search_results:
            context = RetrievedContext(
                content=result.chunk.content,
                source=result.chunk.source,
                doc_type=result.chunk.doc_type,
                relevance_score=result.score,
                chunk_id=result.chunk.chunk_id,
                doc_title=result.chunk.doc_title
            )
            contexts.append(context)
        
        return contexts
    
    def _rerank_contexts(
        self,
        contexts: List[RetrievedContext],
        query: str
    ) -> List[RetrievedContext]:
        """
        Re-rank contexts for relevance
        
        In production, would use cross-encoder model for better re-ranking
        For now, use simple heuristics
        """
        query_terms = query.lower().split()
        
        for context in contexts:
            content_lower = context.content.lower()
            
            # Boost for exact query match
            if query.lower() in content_lower:
                context.relevance_score *= 1.3
            
            # Boost for multiple query terms
            term_matches = sum(1 for term in query_terms if term in content_lower)
            context.relevance_score += (term_matches / len(query_terms)) * 0.2
            
            # Boost certain document types
            if context.doc_type in ['documentation', 'api_spec']:
                context.relevance_score *= 1.1
        
        # Re-sort by updated scores
        contexts.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return contexts
    
    def _select_contexts(
        self,
        contexts: List[RetrievedContext],
        max_contexts: int
    ) -> List[RetrievedContext]:
        """
        Select contexts within token budget
        
        Takes top K contexts that fit within max_context_length
        """
        selected = []
        total_tokens = 0
        
        for context in contexts[:max_contexts]:
            # Estimate tokens (rough: 4 chars per token)
            context_tokens = len(context.content) // 4
            
            if total_tokens + context_tokens <= self.max_context_length:
                selected.append(context)
                total_tokens += context_tokens
            else:
                break
        
        return selected
    
    def _build_augmented_prompt(
        self,
        query: str,
        contexts: List[RetrievedContext],
        conversation_history: Optional[List[Dict[str, str]]],
        system_prompt: Optional[str]
    ) -> List[Dict[str, str]]:
        """
        Build prompt with retrieved context
        
        Format:
        SYSTEM: You are a helpful assistant. Use the following context...
        [Context 1]
        [Context 2]
        ...
        USER: [query]
        """
        messages = []
        
        # System prompt
        if not system_prompt:
            system_prompt = """You are an AI security assistant for Enterprise Scanner. 
Use the following context to answer the user's question accurately. 
If the context doesn't contain enough information, say so clearly.
Always cite your sources using [Source N] notation."""
        
        # Add context to system prompt
        if contexts:
            system_prompt += "\n\n--- CONTEXT ---\n"
            for i, context in enumerate(contexts, 1):
                system_prompt += f"\n[Source {i}] ({context.doc_title}):\n{context.content}\n"
            system_prompt += "\n--- END CONTEXT ---\n"
        
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages
        
        # Add user query
        messages.append({
            'role': 'user',
            'content': query
        })
        
        return messages
    
    def _generate_with_llm(self, messages: List[Dict[str, str]]):
        """Generate response using LLM"""
        if not self.llm_provider:
            raise Exception("LLM provider not available")
        
        return self.llm_provider.complete(
            messages=messages,
            temperature=0.3,  # Lower temperature for accuracy
            max_tokens=1000
        )
    
    def _generate_citations(
        self,
        contexts: List[RetrievedContext]
    ) -> List[Citation]:
        """Generate citations from contexts"""
        citations = []
        
        for i, context in enumerate(contexts, 1):
            citation = Citation(
                citation_id=i,
                source=context.source,
                doc_title=context.doc_title,
                doc_type=context.doc_type,
                relevance_score=context.relevance_score,
                excerpt=context.content[:200] + "..." if len(context.content) > 200 else context.content
            )
            citations.append(citation)
        
        return citations
    
    def _calculate_confidence(
        self,
        answer: str,
        contexts: List[RetrievedContext],
        tokens_used: int
    ) -> float:
        """
        Calculate confidence score for answer
        
        Based on:
        - Number of contexts used
        - Average relevance of contexts
        - Answer length (very short answers may be uncertain)
        """
        if not contexts:
            return 0.3  # Low confidence without context
        
        # Base confidence from context relevance
        avg_relevance = sum(c.relevance_score for c in contexts) / len(contexts)
        confidence = avg_relevance * 0.6
        
        # Boost for multiple contexts
        context_boost = min(len(contexts) / 5, 1.0) * 0.2
        confidence += context_boost
        
        # Boost for longer, detailed answers
        answer_length_boost = min(len(answer) / 500, 1.0) * 0.2
        confidence += answer_length_boost
        
        # Cap at 0.95 (never 100% certain)
        confidence = min(confidence, 0.95)
        
        return confidence
    
    def _update_stats(self, response: RAGResponse):
        """Update statistics with response metrics"""
        n = self.stats['successful_queries']
        
        # Update averages
        self.stats['avg_retrieval_time_ms'] = (
            (self.stats['avg_retrieval_time_ms'] * (n - 1) + response.retrieval_time_ms) / n
        )
        self.stats['avg_generation_time_ms'] = (
            (self.stats['avg_generation_time_ms'] * (n - 1) + response.generation_time_ms) / n
        )
        self.stats['avg_contexts_retrieved'] = (
            (self.stats['avg_contexts_retrieved'] * (n - 1) + response.contexts_retrieved) / n
        )
        self.stats['avg_contexts_used'] = (
            (self.stats['avg_contexts_used'] * (n - 1) + response.contexts_used_count) / n
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return self.stats.copy()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("RAG (RETRIEVAL-AUGMENTED GENERATION) SYSTEM")
    print("="*70)
    
    # Initialize RAG system
    print("\n1. Initializing RAG System...")
    rag = RAGSystem(
        top_k_retrieve=10,
        top_k_use=5,
        max_context_length=4000
    )
    
    # Mock some retrieved contexts
    print("\n2. Testing RAG with Mock Data...")
    mock_contexts = [
        RetrievedContext(
            content="SQL injection is a code injection technique that exploits security vulnerabilities in web applications. Attackers can manipulate SQL queries to access unauthorized data.",
            source="docs/vulnerabilities/sqli.md",
            doc_type="documentation",
            relevance_score=0.92,
            chunk_id="doc1_chunk_0",
            doc_title="SQL Injection Guide"
        ),
        RetrievedContext(
            content="To prevent SQL injection, use parameterized queries (prepared statements), validate all user input, and implement least privilege database access controls.",
            source="docs/best_practices/secure_coding.md",
            doc_type="documentation",
            relevance_score=0.88,
            chunk_id="doc2_chunk_1",
            doc_title="Secure Coding Practices"
        )
    ]
    
    # Test citation generation
    citations = rag._generate_citations(mock_contexts)
    
    print("\n   Generated Citations:")
    for citation in citations:
        print(f"\n   [{citation.citation_id}] {citation.doc_title}")
        print(f"       Source: {citation.source}")
        print(f"       Type: {citation.doc_type}")
        print(f"       Relevance: {citation.relevance_score:.2f}")
        print(f"       Excerpt: {citation.excerpt[:100]}...")
    
    # Test confidence calculation
    print("\n3. Testing Confidence Scoring:")
    confidence = rag._calculate_confidence(
        answer="SQL injection is a common web vulnerability...",
        contexts=mock_contexts,
        tokens_used=200
    )
    print(f"   Confidence Score: {confidence:.2f}")
    
    # Statistics
    print("\n4. RAG System Statistics:")
    stats = rag.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("RAG SYSTEM MODULE COMPLETE ✅")
    print("="*70)
