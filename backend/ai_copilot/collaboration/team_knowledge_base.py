"""
Jupiter Team Knowledge Base
Shared knowledge repository for security teams
Enables documentation, best practices, and institutional knowledge sharing
"""

import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Set
from enum import Enum
import hashlib


class ArticleCategory(Enum):
    """Knowledge article categories"""
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    REMEDIATION_GUIDE = "remediation_guide"
    THREAT_INTELLIGENCE = "threat_intelligence"
    INCIDENT_RESPONSE = "incident_response"
    BEST_PRACTICES = "best_practices"
    TOOL_DOCUMENTATION = "tool_documentation"
    POLICY_PROCEDURE = "policy_procedure"
    CASE_STUDY = "case_study"
    RESEARCH_NOTES = "research_notes"


class ArticleStatus(Enum):
    """Article lifecycle status"""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class ArticleMetadata:
    """Metadata for knowledge articles"""
    author_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    tags: List[str]
    related_articles: List[str]  # Article IDs
    severity_level: Optional[str] = None  # For vulnerability articles
    cve_references: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    view_count: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0


@dataclass
class KnowledgeArticle:
    """Knowledge base article"""
    article_id: str
    title: str
    content: str
    category: ArticleCategory
    status: ArticleStatus
    metadata: ArticleMetadata
    search_keywords: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)  # File paths
    comments: List[Dict] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Export article to markdown format"""
        md = f"# {self.title}\n\n"
        md += f"**Category:** {self.category.value}\n"
        md += f"**Status:** {self.status.value}\n"
        md += f"**Author:** {self.metadata.author_id}\n"
        md += f"**Created:** {self.metadata.created_at.isoformat()}\n"
        md += f"**Version:** {self.metadata.version}\n\n"
        
        if self.metadata.tags:
            md += f"**Tags:** {', '.join(self.metadata.tags)}\n\n"
        
        if self.metadata.cve_references:
            md += f"**CVE References:** {', '.join(self.metadata.cve_references)}\n\n"
        
        md += "---\n\n"
        md += self.content
        
        if self.comments:
            md += "\n\n## Comments\n\n"
            for comment in self.comments:
                md += f"**{comment['author']}** ({comment['timestamp']}): {comment['text']}\n\n"
        
        return md


class JupiterKnowledgeBase:
    """
    Team knowledge base for Jupiter AI Copilot
    Enables teams to build and share security knowledge
    """
    
    def __init__(self, db_path: str = "jupiter_knowledge.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize knowledge base database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kb_articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                author_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                tags TEXT,
                related_articles TEXT,
                severity_level TEXT,
                cve_references TEXT,
                affected_systems TEXT,
                view_count INTEGER DEFAULT 0,
                helpful_votes INTEGER DEFAULT 0,
                unhelpful_votes INTEGER DEFAULT 0,
                search_keywords TEXT,
                attachments TEXT,
                comments TEXT
            )
        """)
        
        # Article revisions for version control
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kb_article_revisions (
                revision_id TEXT PRIMARY KEY,
                article_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                content TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                change_summary TEXT,
                FOREIGN KEY (article_id) REFERENCES kb_articles(article_id)
            )
        """)
        
        # Article access tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kb_article_access (
                access_id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                access_type TEXT,
                FOREIGN KEY (article_id) REFERENCES kb_articles(article_id)
            )
        """)
        
        # Full-text search index
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS kb_search_index 
            USING fts5(article_id, title, content, tags, keywords)
        """)
        
        conn.commit()
        conn.close()
    
    def create_article(
        self,
        title: str,
        content: str,
        category: ArticleCategory,
        author_id: str,
        tags: List[str] = None,
        severity_level: str = None,
        cve_references: List[str] = None,
        affected_systems: List[str] = None
    ) -> KnowledgeArticle:
        """Create new knowledge article"""
        
        # Generate article ID
        article_id = hashlib.sha256(
            f"{title}{author_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Create metadata
        metadata = ArticleMetadata(
            author_id=author_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            tags=tags or [],
            related_articles=[],
            severity_level=severity_level,
            cve_references=cve_references or [],
            affected_systems=affected_systems or []
        )
        
        # Generate search keywords
        search_keywords = self._generate_keywords(title, content, tags or [])
        
        article = KnowledgeArticle(
            article_id=article_id,
            title=title,
            content=content,
            category=category,
            status=ArticleStatus.DRAFT,
            metadata=metadata,
            search_keywords=search_keywords
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO kb_articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.article_id,
            article.title,
            article.content,
            article.category.value,
            article.status.value,
            metadata.author_id,
            metadata.created_at.isoformat(),
            metadata.updated_at.isoformat(),
            metadata.version,
            json.dumps(metadata.tags),
            json.dumps(metadata.related_articles),
            metadata.severity_level,
            json.dumps(metadata.cve_references),
            json.dumps(metadata.affected_systems),
            metadata.view_count,
            metadata.helpful_votes,
            metadata.unhelpful_votes,
            json.dumps(search_keywords),
            json.dumps(article.attachments),
            json.dumps(article.comments)
        ))
        
        # Add to search index
        cursor.execute("""
            INSERT INTO kb_search_index VALUES (?, ?, ?, ?, ?)
        """, (
            article.article_id,
            article.title,
            article.content,
            ' '.join(metadata.tags),
            ' '.join(search_keywords)
        ))
        
        conn.commit()
        conn.close()
        
        return article
    
    def _generate_keywords(self, title: str, content: str, tags: List[str]) -> List[str]:
        """Generate search keywords from article content"""
        keywords = set()
        
        # Add tags
        keywords.update([tag.lower() for tag in tags])
        
        # Extract technical terms (simplified)
        technical_terms = [
            'sql', 'xss', 'csrf', 'rce', 'lfi', 'rfi', 'xxe', 'ssrf',
            'authentication', 'authorization', 'encryption', 'injection',
            'vulnerability', 'exploit', 'patch', 'remediation', 'cve',
            'owasp', 'security', 'threat', 'malware', 'ransomware'
        ]
        
        text = (title + ' ' + content).lower()
        for term in technical_terms:
            if term in text:
                keywords.add(term)
        
        return list(keywords)
    
    def update_article(
        self,
        article_id: str,
        content: str = None,
        status: ArticleStatus = None,
        tags: List[str] = None,
        user_id: str = None,
        change_summary: str = None
    ) -> bool:
        """Update existing article with version control"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current article
        cursor.execute("SELECT * FROM kb_articles WHERE article_id = ?", (article_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        current_version = row[8]
        new_version = current_version + 1
        
        # Save revision
        revision_id = hashlib.sha256(
            f"{article_id}{new_version}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        cursor.execute("""
            INSERT INTO kb_article_revisions VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            revision_id,
            article_id,
            current_version,
            row[2],  # Current content
            user_id or "system",
            datetime.now().isoformat(),
            change_summary or "Updated article"
        ))
        
        # Update article
        if content:
            cursor.execute("""
                UPDATE kb_articles 
                SET content = ?, updated_at = ?, version = ?
                WHERE article_id = ?
            """, (content, datetime.now().isoformat(), new_version, article_id))
            
            # Update search index
            cursor.execute("""
                UPDATE kb_search_index SET content = ? WHERE article_id = ?
            """, (content, article_id))
        
        if status:
            cursor.execute("""
                UPDATE kb_articles SET status = ? WHERE article_id = ?
            """, (status.value, article_id))
        
        if tags:
            cursor.execute("""
                UPDATE kb_articles SET tags = ? WHERE article_id = ?
            """, (json.dumps(tags), article_id))
            
            cursor.execute("""
                UPDATE kb_search_index SET tags = ? WHERE article_id = ?
            """, (' '.join(tags), article_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def search_articles(
        self,
        query: str,
        category: ArticleCategory = None,
        tags: List[str] = None,
        severity_level: str = None,
        limit: int = 20
    ) -> List[KnowledgeArticle]:
        """Search knowledge base with full-text search"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build search query
        if query:
            # Full-text search
            cursor.execute("""
                SELECT a.* FROM kb_articles a
                JOIN kb_search_index s ON a.article_id = s.article_id
                WHERE kb_search_index MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
        else:
            cursor.execute("SELECT * FROM kb_articles LIMIT ?", (limit,))
        
        rows = cursor.fetchall()
        articles = []
        
        for row in rows:
            # Apply filters
            if category and row[3] != category.value:
                continue
            if severity_level and row[11] != severity_level:
                continue
            if tags:
                article_tags = json.loads(row[9])
                if not any(tag in article_tags for tag in tags):
                    continue
            
            metadata = ArticleMetadata(
                author_id=row[5],
                created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7]),
                version=row[8],
                tags=json.loads(row[9]),
                related_articles=json.loads(row[10]),
                severity_level=row[11],
                cve_references=json.loads(row[12]),
                affected_systems=json.loads(row[13]),
                view_count=row[14],
                helpful_votes=row[15],
                unhelpful_votes=row[16]
            )
            
            article = KnowledgeArticle(
                article_id=row[0],
                title=row[1],
                content=row[2],
                category=ArticleCategory(row[3]),
                status=ArticleStatus(row[4]),
                metadata=metadata,
                search_keywords=json.loads(row[17]),
                attachments=json.loads(row[18]),
                comments=json.loads(row[19])
            )
            
            articles.append(article)
        
        conn.close()
        return articles
    
    def get_article(self, article_id: str, user_id: str = None) -> Optional[KnowledgeArticle]:
        """Get specific article and track access"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM kb_articles WHERE article_id = ?", (article_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Track access
        if user_id:
            cursor.execute("""
                INSERT INTO kb_article_access (article_id, user_id, accessed_at, access_type)
                VALUES (?, ?, ?, ?)
            """, (article_id, user_id, datetime.now().isoformat(), "read"))
            
            # Increment view count
            cursor.execute("""
                UPDATE kb_articles SET view_count = view_count + 1
                WHERE article_id = ?
            """, (article_id,))
            
            conn.commit()
        
        metadata = ArticleMetadata(
            author_id=row[5],
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
            version=row[8],
            tags=json.loads(row[9]),
            related_articles=json.loads(row[10]),
            severity_level=row[11],
            cve_references=json.loads(row[12]),
            affected_systems=json.loads(row[13]),
            view_count=row[14],
            helpful_votes=row[15],
            unhelpful_votes=row[16]
        )
        
        article = KnowledgeArticle(
            article_id=row[0],
            title=row[1],
            content=row[2],
            category=ArticleCategory(row[3]),
            status=ArticleStatus(row[4]),
            metadata=metadata,
            search_keywords=json.loads(row[17]),
            attachments=json.loads(row[18]),
            comments=json.loads(row[19])
        )
        
        conn.close()
        return article
    
    def add_comment(self, article_id: str, author: str, text: str) -> bool:
        """Add comment to article"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT comments FROM kb_articles WHERE article_id = ?", (article_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        comments = json.loads(row[0])
        comments.append({
            'author': author,
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        cursor.execute("""
            UPDATE kb_articles SET comments = ? WHERE article_id = ?
        """, (json.dumps(comments), article_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def vote_helpful(self, article_id: str, helpful: bool = True) -> bool:
        """Vote on article helpfulness"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if helpful:
            cursor.execute("""
                UPDATE kb_articles SET helpful_votes = helpful_votes + 1
                WHERE article_id = ?
            """, (article_id,))
        else:
            cursor.execute("""
                UPDATE kb_articles SET unhelpful_votes = unhelpful_votes + 1
                WHERE article_id = ?
            """, (article_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_popular_articles(self, limit: int = 10) -> List[KnowledgeArticle]:
        """Get most viewed/helpful articles"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM kb_articles 
            WHERE status = 'published'
            ORDER BY view_count DESC, helpful_votes DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        articles = []
        
        for row in rows:
            metadata = ArticleMetadata(
                author_id=row[5],
                created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7]),
                version=row[8],
                tags=json.loads(row[9]),
                related_articles=json.loads(row[10]),
                severity_level=row[11],
                cve_references=json.loads(row[12]),
                affected_systems=json.loads(row[13]),
                view_count=row[14],
                helpful_votes=row[15],
                unhelpful_votes=row[16]
            )
            
            article = KnowledgeArticle(
                article_id=row[0],
                title=row[1],
                content=row[2],
                category=ArticleCategory(row[3]),
                status=ArticleStatus(row[4]),
                metadata=metadata,
                search_keywords=json.loads(row[17]),
                attachments=json.loads(row[18]),
                comments=json.loads(row[19])
            )
            
            articles.append(article)
        
        conn.close()
        return articles
    
    def get_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total articles
        cursor.execute("SELECT COUNT(*) FROM kb_articles")
        stats['total_articles'] = cursor.fetchone()[0]
        
        # Articles by status
        cursor.execute("""
            SELECT status, COUNT(*) FROM kb_articles GROUP BY status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # Articles by category
        cursor.execute("""
            SELECT category, COUNT(*) FROM kb_articles GROUP BY category
        """)
        stats['by_category'] = dict(cursor.fetchall())
        
        # Total views
        cursor.execute("SELECT SUM(view_count) FROM kb_articles")
        stats['total_views'] = cursor.fetchone()[0] or 0
        
        # Average helpful votes
        cursor.execute("""
            SELECT AVG(helpful_votes * 1.0 / NULLIF(helpful_votes + unhelpful_votes, 0))
            FROM kb_articles
        """)
        stats['avg_helpfulness'] = cursor.fetchone()[0] or 0
        
        # Most active authors
        cursor.execute("""
            SELECT author_id, COUNT(*) as article_count
            FROM kb_articles
            GROUP BY author_id
            ORDER BY article_count DESC
            LIMIT 5
        """)
        stats['top_authors'] = [{'author_id': row[0], 'articles': row[1]} 
                                for row in cursor.fetchall()]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    kb = JupiterKnowledgeBase()
    
    # Create sample article
    article = kb.create_article(
        title="SQL Injection Remediation Guide",
        content="""
        # SQL Injection Remediation
        
        ## Overview
        SQL injection is a code injection technique that exploits vulnerabilities
        in database-driven applications.
        
        ## Detection Methods
        1. Static code analysis
        2. Dynamic application testing
        3. Manual code review
        
        ## Remediation Steps
        1. Use parameterized queries
        2. Implement input validation
        3. Apply least privilege principles
        4. Use ORM frameworks
        
        ## Code Examples
        ```python
        # Vulnerable code
        query = f"SELECT * FROM users WHERE id = {user_id}"
        
        # Secure code
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        ```
        """,
        category=ArticleCategory.REMEDIATION_GUIDE,
        author_id="analyst_001",
        tags=["sql-injection", "database", "owasp-top-10"],
        severity_level="critical",
        cve_references=["CVE-2023-1234"]
    )
    
    print(f"Created article: {article.article_id}")
    print(f"Title: {article.title}")
    print(f"Status: {article.status.value}")
    
    # Search articles
    results = kb.search_articles("sql injection")
    print(f"\nSearch results: {len(results)} articles found")
    
    # Get statistics
    stats = kb.get_statistics()
    print(f"\nKnowledge base stats:")
    print(f"Total articles: {stats['total_articles']}")
    print(f"Total views: {stats['total_views']}")
