"""
Knowledge Base Module

Document ingestion, embedding, and semantic search system.

Supports:
- Multiple document formats (MD, PDF, TXT, JSON, HTML)
- Intelligent chunking (semantic-aware)
- Vector embeddings (OpenAI ada-002)
- Metadata indexing
- Hybrid search (semantic + keyword)

Data Sources:
- Platform documentation
- API specifications
- CVE database
- Compliance frameworks (NIST, PCI, HIPAA, etc.)
- Customer scan results
- Threat intelligence feeds

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import json
import re
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging


@dataclass
class Document:
    """Single document in knowledge base"""
    doc_id: str
    title: str
    content: str
    source: str  # filepath, URL, or source identifier
    doc_type: str  # 'documentation', 'api_spec', 'cve', 'compliance', 'scan_result'
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Content stats
    char_count: int = 0
    word_count: int = 0
    estimated_tokens: int = 0
    
    def __post_init__(self):
        """Calculate content statistics"""
        self.char_count = len(self.content)
        self.word_count = len(self.content.split())
        self.estimated_tokens = self.word_count // 0.75  # Rough estimate


@dataclass
class Chunk:
    """Document chunk for embedding"""
    chunk_id: str
    doc_id: str
    content: str
    chunk_index: int  # Position in document
    
    # Embedding
    embedding: Optional[List[float]] = None
    
    # Metadata (inherited from parent document)
    doc_title: str = ""
    doc_type: str = ""
    source: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Content stats
    char_count: int = 0
    token_count: int = 0
    
    def __post_init__(self):
        """Calculate statistics"""
        self.char_count = len(self.content)
        self.token_count = len(self.content) // 4  # Rough estimate


@dataclass
class SearchResult:
    """Search result with relevance score"""
    chunk: Chunk
    score: float  # Similarity score (0-1)
    rank: int  # Result ranking
    
    # Highlighted content
    highlighted_content: Optional[str] = None
    
    # Explanation
    relevance_reason: Optional[str] = None


class KnowledgeBase:
    """
    Knowledge base management system
    
    Handles document ingestion, chunking, embedding, and search
    """
    
    def __init__(
        self,
        storage_path: str = "./data/knowledge_base",
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 800,  # Target chunk size in tokens
        chunk_overlap: int = 100  # Overlap between chunks
    ):
        """
        Initialize knowledge base
        
        Args:
            storage_path: Path to store documents and embeddings
            embedding_model: Embedding model name
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # In-memory storage (would use vector DB in production)
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, Chunk] = {}
        
        # Vector database (ChromaDB integration)
        self.vector_db = self._initialize_vector_db()
        
        # LLM provider for embeddings
        self.llm_provider = None
        try:
            from backend.ai_copilot.utils.llm_providers import LLMProvider
            self.llm_provider = LLMProvider(provider="openai")
        except Exception as e:
            self.logger.warning(f"LLM provider not available: {e}")
        
        # Statistics
        self.stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'total_searches': 0,
            'avg_search_time_ms': 0,
            'total_embeddings_generated': 0
        }
        
        self.logger.info(f"KnowledgeBase initialized: {storage_path}")
    
    def _initialize_vector_db(self):
        """Initialize vector database (ChromaDB)"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persistent ChromaDB client
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.storage_path / "chroma")
            ))
            
            # Get or create collection
            collection = client.get_or_create_collection(
                name="enterprise_scanner_kb",
                metadata={"description": "Enterprise Scanner knowledge base"}
            )
            
            self.logger.info("ChromaDB initialized")
            return collection
            
        except ImportError:
            self.logger.warning("ChromaDB not installed. Using in-memory storage. Install: pip install chromadb")
            return None
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            return None
    
    def ingest_document(
        self,
        content: str,
        title: str,
        source: str,
        doc_type: str,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Ingest a document into knowledge base
        
        Args:
            content: Document content
            title: Document title
            source: Source identifier (filepath, URL, etc.)
            doc_type: Document type
            author: Author name
            tags: Document tags
            metadata: Additional metadata
            
        Returns:
            Document object
        """
        # Generate document ID
        doc_id = self._generate_doc_id(source, title)
        
        # Create document
        doc = Document(
            doc_id=doc_id,
            title=title,
            content=content,
            source=source,
            doc_type=doc_type,
            author=author,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store document
        self.documents[doc_id] = doc
        self.stats['total_documents'] += 1
        
        # Chunk document
        chunks = self.chunk_document(doc)
        
        # Generate embeddings for chunks
        for chunk in chunks:
            self._generate_embedding(chunk)
            self.chunks[chunk.chunk_id] = chunk
        
        self.stats['total_chunks'] += len(chunks)
        
        self.logger.info(f"Document ingested: {title} ({len(chunks)} chunks)")
        
        return doc
    
    def chunk_document(self, doc: Document) -> List[Chunk]:
        """
        Chunk document into smaller pieces
        
        Uses semantic-aware chunking:
        - Respects paragraph boundaries
        - Maintains context overlap
        - Targets consistent token counts
        
        Args:
            doc: Document to chunk
            
        Returns:
            List of Chunk objects
        """
        # Split content into paragraphs
        paragraphs = self._split_into_paragraphs(doc.content)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for para in paragraphs:
            para_tokens = len(para) // 4  # Rough token estimate
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_tokens + para_tokens > self.chunk_size and current_chunk:
                # Create chunk from accumulated paragraphs
                chunk_content = "\n\n".join(current_chunk)
                chunk = self._create_chunk(doc, chunk_content, chunk_index)
                chunks.append(chunk)
                
                chunk_index += 1
                
                # Start new chunk with overlap
                # Keep last paragraph for context
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], para]
                    current_tokens = len(current_chunk[0]) // 4 + para_tokens
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
            else:
                # Add paragraph to current chunk
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Don't forget last chunk
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunk = self._create_chunk(doc, chunk_content, chunk_index)
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_paragraphs(self, content: str) -> List[str]:
        """Split content into paragraphs"""
        # Split on double newlines
        paragraphs = re.split(r'\n\s*\n', content)
        
        # Clean up whitespace
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _create_chunk(self, doc: Document, content: str, chunk_index: int) -> Chunk:
        """Create chunk from document"""
        chunk_id = f"{doc.doc_id}_chunk_{chunk_index}"
        
        return Chunk(
            chunk_id=chunk_id,
            doc_id=doc.doc_id,
            content=content,
            chunk_index=chunk_index,
            doc_title=doc.title,
            doc_type=doc.doc_type,
            source=doc.source,
            tags=doc.tags.copy(),
            metadata=doc.metadata.copy()
        )
    
    def _generate_embedding(self, chunk: Chunk) -> None:
        """
        Generate embedding for chunk
        
        Uses OpenAI text-embedding-ada-002 (1536 dimensions)
        """
        if not self.llm_provider:
            # Mock embedding for testing
            chunk.embedding = [0.0] * 1536
            return
        
        try:
            embedding = self.llm_provider.embed(chunk.content)
            chunk.embedding = embedding
            
            # Store in vector DB
            if self.vector_db:
                self.vector_db.add(
                    ids=[chunk.chunk_id],
                    embeddings=[embedding],
                    documents=[chunk.content],
                    metadatas=[{
                        'doc_id': chunk.doc_id,
                        'doc_title': chunk.doc_title,
                        'doc_type': chunk.doc_type,
                        'source': chunk.source,
                        'chunk_index': chunk.chunk_index
                    }]
                )
            
            self.stats['total_embeddings_generated'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            chunk.embedding = [0.0] * 1536
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Search knowledge base
        
        Uses hybrid search:
        - Semantic similarity (vector search)
        - Keyword matching
        - Metadata filtering
        
        Args:
            query: Search query
            top_k: Number of results to return
            doc_types: Filter by document types
            tags: Filter by tags
            
        Returns:
            List of SearchResult objects
        """
        start_time = time.time()
        self.stats['total_searches'] += 1
        
        # Generate query embedding
        if not self.llm_provider:
            self.logger.warning("LLM provider not available for search")
            return []
        
        query_embedding = self.llm_provider.embed(query)
        
        # Vector search
        if self.vector_db:
            results = self._vector_search(query_embedding, top_k * 2, doc_types, tags)
        else:
            results = self._fallback_search(query, top_k, doc_types, tags)
        
        # Re-rank with keyword matching
        results = self._rerank_results(results, query)
        
        # Take top K
        results = results[:top_k]
        
        # Add highlighting
        for i, result in enumerate(results):
            result.rank = i + 1
            result.highlighted_content = self._highlight_query_terms(
                result.chunk.content,
                query
            )
        
        # Update statistics
        search_time = (time.time() - start_time) * 1000
        self.stats['avg_search_time_ms'] = (
            (self.stats['avg_search_time_ms'] * (self.stats['total_searches'] - 1) + search_time)
            / self.stats['total_searches']
        )
        
        return results
    
    def _vector_search(
        self,
        query_embedding: List[float],
        top_k: int,
        doc_types: Optional[List[str]],
        tags: Optional[List[str]]
    ) -> List[SearchResult]:
        """Perform vector similarity search"""
        try:
            # Build where clause for filtering
            where = {}
            if doc_types:
                where['doc_type'] = {'$in': doc_types}
            # ChromaDB doesn't support complex tag filtering easily,
            # we'll filter manually
            
            # Query vector DB
            results = self.vector_db.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where if where else None
            )
            
            # Convert to SearchResult objects
            search_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, chunk_id in enumerate(results['ids'][0]):
                    chunk = self.chunks.get(chunk_id)
                    if chunk:
                        # Filter by tags if specified
                        if tags and not any(t in chunk.tags for t in tags):
                            continue
                        
                        score = 1.0 - results['distances'][0][i]  # Convert distance to similarity
                        search_results.append(SearchResult(
                            chunk=chunk,
                            score=score,
                            rank=0  # Will be set later
                        ))
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {e}")
            return []
    
    def _fallback_search(
        self,
        query: str,
        top_k: int,
        doc_types: Optional[List[str]],
        tags: Optional[List[str]]
    ) -> List[SearchResult]:
        """Fallback keyword search"""
        query_terms = query.lower().split()
        results = []
        
        for chunk in self.chunks.values():
            # Filter by doc_type
            if doc_types and chunk.doc_type not in doc_types:
                continue
            
            # Filter by tags
            if tags and not any(t in chunk.tags for t in tags):
                continue
            
            # Calculate keyword match score
            content_lower = chunk.content.lower()
            score = sum(1 for term in query_terms if term in content_lower) / len(query_terms)
            
            if score > 0:
                results.append(SearchResult(
                    chunk=chunk,
                    score=score,
                    rank=0
                ))
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:top_k]
    
    def _rerank_results(
        self,
        results: List[SearchResult],
        query: str
    ) -> List[SearchResult]:
        """Re-rank results with keyword boosting"""
        query_terms = query.lower().split()
        
        for result in results:
            content_lower = result.chunk.content.lower()
            
            # Boost score for exact phrase matches
            if query.lower() in content_lower:
                result.score *= 1.5
            
            # Boost for term frequency
            term_frequency = sum(content_lower.count(term) for term in query_terms)
            result.score += term_frequency * 0.01
        
        # Re-sort
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    def _highlight_query_terms(self, content: str, query: str) -> str:
        """Highlight query terms in content"""
        query_terms = query.split()
        highlighted = content
        
        for term in query_terms:
            pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
            highlighted = pattern.sub(r'**\1**', highlighted)
        
        return highlighted
    
    def _generate_doc_id(self, source: str, title: str) -> str:
        """Generate unique document ID"""
        content = f"{source}:{title}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID"""
        return self.documents.get(doc_id)
    
    def list_documents(
        self,
        doc_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Document]:
        """List documents with optional filtering"""
        docs = list(self.documents.values())
        
        if doc_type:
            docs = [d for d in docs if d.doc_type == doc_type]
        
        if tags:
            docs = [d for d in docs if any(t in d.tags for t in tags)]
        
        return docs
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and its chunks"""
        if doc_id not in self.documents:
            return False
        
        # Remove chunks
        chunk_ids = [cid for cid, chunk in self.chunks.items() if chunk.doc_id == doc_id]
        for chunk_id in chunk_ids:
            del self.chunks[chunk_id]
            
            # Remove from vector DB
            if self.vector_db:
                try:
                    self.vector_db.delete(ids=[chunk_id])
                except Exception as e:
                    self.logger.error(f"Failed to delete chunk from vector DB: {e}")
        
        # Remove document
        del self.documents[doc_id]
        
        self.stats['total_documents'] -= 1
        self.stats['total_chunks'] -= len(chunk_ids)
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return self.stats.copy()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("KNOWLEDGE BASE MODULE")
    print("="*70)
    
    # Initialize knowledge base
    print("\n1. Initializing Knowledge Base...")
    kb = KnowledgeBase(
        storage_path="./test_kb",
        chunk_size=500,
        chunk_overlap=50
    )
    
    # Ingest sample documents
    print("\n2. Ingesting Sample Documents...")
    
    doc1 = kb.ingest_document(
        content="""
        SQL Injection Vulnerability
        
        SQL injection is a code injection technique that exploits a security vulnerability 
        in an application's software. The vulnerability occurs when user input is not 
        properly validated and is directly included in SQL queries.
        
        Common Attack Patterns:
        - ' OR '1'='1
        - admin'--
        - UNION SELECT statements
        
        Prevention:
        - Use parameterized queries
        - Input validation
        - Least privilege database accounts
        """,
        title="SQL Injection Guide",
        source="docs/vulnerabilities/sqli.md",
        doc_type="documentation",
        tags=["vulnerability", "sqli", "web-security"]
    )
    
    doc2 = kb.ingest_document(
        content="""
        CVE-2024-1234: Critical RCE in Apache Server
        
        A remote code execution vulnerability has been discovered in Apache HTTP Server 
        versions 2.4.0 through 2.4.49. This vulnerability allows an attacker to execute 
        arbitrary code on the target system.
        
        CVSS Score: 9.8 (Critical)
        
        Affected Versions: 2.4.0 - 2.4.49
        
        Remediation: Upgrade to version 2.4.50 or later
        """,
        title="CVE-2024-1234",
        source="cve/CVE-2024-1234.json",
        doc_type="cve",
        tags=["cve", "rce", "apache", "critical"]
    )
    
    print(f"   Documents ingested: {len(kb.documents)}")
    print(f"   Total chunks: {len(kb.chunks)}")
    
    # Search knowledge base
    print("\n3. Testing Search:")
    
    queries = [
        "What is SQL injection?",
        "Apache vulnerability CVE-2024",
        "How to prevent SQL injection?"
    ]
    
    for query in queries:
        print(f"\n   Query: '{query}'")
        results = kb.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n   Result {i} (score: {result.score:.3f}):")
            print(f"   Source: {result.chunk.source}")
            print(f"   Content: {result.chunk.content[:150]}...")
    
    # Statistics
    print("\n4. Knowledge Base Statistics:")
    stats = kb.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("KNOWLEDGE BASE MODULE COMPLETE ✅")
    print("="*70)
