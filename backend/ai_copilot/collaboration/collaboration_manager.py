"""
Jupiter Collaboration Manager
Manages team collaboration, shared queries, and role-based access control
"""

import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Set
from enum import Enum
import hashlib


class UserRole(Enum):
    """User roles with different permissions"""
    ADMIN = "admin"  # Full access, user management
    ANALYST = "analyst"  # Standard security analyst
    VIEWER = "viewer"  # Read-only access
    AUDITOR = "auditor"  # Read-only + audit trail access
    CONTRIBUTOR = "contributor"  # Can create but not delete


@dataclass
class TeamMember:
    """Team member profile"""
    user_id: str
    username: str
    email: str
    role: UserRole
    department: str
    joined_at: datetime
    last_active: datetime
    permissions: Dict[str, bool] = field(default_factory=dict)
    is_active: bool = True
    profile_data: Dict = field(default_factory=dict)


@dataclass
class SharedQuery:
    """Shared Jupiter query with annotations"""
    query_id: str
    query_text: str
    created_by: str
    created_at: datetime
    results: str
    annotations: List[Dict] = field(default_factory=list)
    collaborators: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_archived: bool = False
    view_count: int = 0
    upvotes: int = 0


@dataclass
class Annotation:
    """Annotation on shared query or article"""
    annotation_id: str
    target_id: str  # Query ID or Article ID
    target_type: str  # "query" or "article"
    author_id: str
    content: str
    timestamp: datetime
    position: Optional[Dict] = None  # Line numbers, character ranges
    is_resolved: bool = False
    thread: List[Dict] = field(default_factory=list)


@dataclass
class CollaborationSession:
    """Active collaboration session"""
    session_id: str
    title: str
    description: str
    participants: List[str]
    created_by: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    shared_queries: List[str] = field(default_factory=list)
    shared_articles: List[str] = field(default_factory=list)
    chat_transcript: List[Dict] = field(default_factory=list)
    findings: List[Dict] = field(default_factory=list)
    is_active: bool = True


class JupiterCollaborationManager:
    """
    Manages team collaboration for Jupiter AI Copilot
    Handles permissions, shared queries, and collaborative analysis
    """
    
    def __init__(self, db_path: str = "jupiter_collaboration.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize collaboration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Team members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                department TEXT,
                joined_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                permissions TEXT,
                is_active INTEGER DEFAULT 1,
                profile_data TEXT
            )
        """)
        
        # Shared queries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shared_queries (
                query_id TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                results TEXT,
                annotations TEXT,
                collaborators TEXT,
                tags TEXT,
                is_archived INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                upvotes INTEGER DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES team_members(user_id)
            )
        """)
        
        # Annotations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                annotation_id TEXT PRIMARY KEY,
                target_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                author_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                position TEXT,
                is_resolved INTEGER DEFAULT 0,
                thread TEXT,
                FOREIGN KEY (author_id) REFERENCES team_members(user_id)
            )
        """)
        
        # Collaboration sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaboration_sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                participants TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                ended_at TEXT,
                shared_queries TEXT,
                shared_articles TEXT,
                chat_transcript TEXT,
                findings TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES team_members(user_id)
            )
        """)
        
        # Query access log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_access_log (
                access_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                access_type TEXT,
                accessed_at TEXT NOT NULL,
                FOREIGN KEY (query_id) REFERENCES shared_queries(query_id),
                FOREIGN KEY (user_id) REFERENCES team_members(user_id)
            )
        """)
        
        # Team activity feed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_activity (
                activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES team_members(user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_team_member(
        self,
        username: str,
        email: str,
        role: UserRole,
        department: str = ""
    ) -> TeamMember:
        """Add new team member"""
        
        user_id = hashlib.sha256(email.encode()).hexdigest()[:16]
        
        # Default permissions based on role
        permissions = self._get_default_permissions(role)
        
        member = TeamMember(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            department=department,
            joined_at=datetime.now(),
            last_active=datetime.now(),
            permissions=permissions
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO team_members VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            member.user_id,
            member.username,
            member.email,
            member.role.value,
            member.department,
            member.joined_at.isoformat(),
            member.last_active.isoformat(),
            json.dumps(member.permissions),
            member.is_active,
            json.dumps(member.profile_data)
        ))
        
        # Log activity
        self._log_activity(
            user_id="system",
            activity_type="member_added",
            activity_data={'new_member': member.username, 'role': role.value}
        )
        
        conn.commit()
        conn.close()
        
        return member
    
    def _get_default_permissions(self, role: UserRole) -> Dict[str, bool]:
        """Get default permissions for role"""
        
        if role == UserRole.ADMIN:
            return {
                'read_queries': True,
                'create_queries': True,
                'delete_queries': True,
                'share_queries': True,
                'manage_users': True,
                'access_audit_logs': True,
                'create_articles': True,
                'delete_articles': True,
                'manage_channels': True
            }
        elif role == UserRole.ANALYST:
            return {
                'read_queries': True,
                'create_queries': True,
                'delete_queries': True,
                'share_queries': True,
                'manage_users': False,
                'access_audit_logs': False,
                'create_articles': True,
                'delete_articles': False,
                'manage_channels': False
            }
        elif role == UserRole.VIEWER:
            return {
                'read_queries': True,
                'create_queries': False,
                'delete_queries': False,
                'share_queries': False,
                'manage_users': False,
                'access_audit_logs': False,
                'create_articles': False,
                'delete_articles': False,
                'manage_channels': False
            }
        elif role == UserRole.AUDITOR:
            return {
                'read_queries': True,
                'create_queries': False,
                'delete_queries': False,
                'share_queries': False,
                'manage_users': False,
                'access_audit_logs': True,
                'create_articles': False,
                'delete_articles': False,
                'manage_channels': False
            }
        else:  # CONTRIBUTOR
            return {
                'read_queries': True,
                'create_queries': True,
                'delete_queries': False,
                'share_queries': True,
                'manage_users': False,
                'access_audit_logs': False,
                'create_articles': True,
                'delete_articles': False,
                'manage_channels': False
            }
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT permissions FROM team_members WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        permissions = json.loads(row[0])
        return permissions.get(permission, False)
    
    def share_query(
        self,
        query_text: str,
        results: str,
        created_by: str,
        tags: List[str] = None,
        collaborators: List[str] = None
    ) -> SharedQuery:
        """Share Jupiter query with team"""
        
        # Check permission
        if not self.check_permission(created_by, 'share_queries'):
            raise PermissionError(f"User {created_by} does not have share_queries permission")
        
        query_id = hashlib.sha256(
            f"{query_text}{created_by}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        shared_query = SharedQuery(
            query_id=query_id,
            query_text=query_text,
            created_by=created_by,
            created_at=datetime.now(),
            results=results,
            tags=tags or [],
            collaborators=collaborators or []
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO shared_queries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shared_query.query_id,
            shared_query.query_text,
            shared_query.created_by,
            shared_query.created_at.isoformat(),
            shared_query.results,
            json.dumps(shared_query.annotations),
            json.dumps(shared_query.collaborators),
            json.dumps(shared_query.tags),
            shared_query.is_archived,
            shared_query.view_count,
            shared_query.upvotes
        ))
        
        # Log activity
        self._log_activity(
            user_id=created_by,
            activity_type="query_shared",
            activity_data={'query_id': query_id, 'query_text': query_text[:100]}
        )
        
        conn.commit()
        conn.close()
        
        return shared_query
    
    def add_annotation(
        self,
        target_id: str,
        target_type: str,
        author_id: str,
        content: str,
        position: Dict = None
    ) -> Annotation:
        """Add annotation to shared query or article"""
        
        annotation_id = hashlib.sha256(
            f"{target_id}{author_id}{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        annotation = Annotation(
            annotation_id=annotation_id,
            target_id=target_id,
            target_type=target_type,
            author_id=author_id,
            content=content,
            timestamp=datetime.now(),
            position=position
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO annotations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            annotation.annotation_id,
            annotation.target_id,
            annotation.target_type,
            annotation.author_id,
            annotation.content,
            annotation.timestamp.isoformat(),
            json.dumps(annotation.position) if annotation.position else None,
            annotation.is_resolved,
            json.dumps(annotation.thread)
        ))
        
        # Update query annotations
        if target_type == "query":
            cursor.execute("""
                SELECT annotations FROM shared_queries WHERE query_id = ?
            """, (target_id,))
            row = cursor.fetchone()
            
            if row:
                annotations = json.loads(row[0])
                annotations.append({
                    'annotation_id': annotation_id,
                    'author_id': author_id,
                    'content': content,
                    'timestamp': annotation.timestamp.isoformat()
                })
                
                cursor.execute("""
                    UPDATE shared_queries SET annotations = ? WHERE query_id = ?
                """, (json.dumps(annotations), target_id))
        
        conn.commit()
        conn.close()
        
        return annotation
    
    def create_collaboration_session(
        self,
        title: str,
        created_by: str,
        description: str = "",
        participants: List[str] = None
    ) -> CollaborationSession:
        """Create collaborative analysis session"""
        
        session_id = hashlib.sha256(
            f"{title}{created_by}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        session = CollaborationSession(
            session_id=session_id,
            title=title,
            description=description,
            participants=participants or [created_by],
            created_by=created_by,
            created_at=datetime.now()
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO collaboration_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.title,
            session.description,
            json.dumps(session.participants),
            session.created_by,
            session.created_at.isoformat(),
            None,
            json.dumps(session.shared_queries),
            json.dumps(session.shared_articles),
            json.dumps(session.chat_transcript),
            json.dumps(session.findings),
            session.is_active
        ))
        
        # Log activity
        self._log_activity(
            user_id=created_by,
            activity_type="session_created",
            activity_data={'session_id': session_id, 'title': title}
        )
        
        conn.commit()
        conn.close()
        
        return session
    
    def add_to_session(
        self,
        session_id: str,
        query_id: str = None,
        article_id: str = None,
        finding: Dict = None
    ) -> bool:
        """Add query, article, or finding to session"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if query_id:
            cursor.execute("""
                SELECT shared_queries FROM collaboration_sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            
            if row:
                queries = json.loads(row[0])
                if query_id not in queries:
                    queries.append(query_id)
                    cursor.execute("""
                        UPDATE collaboration_sessions 
                        SET shared_queries = ? WHERE session_id = ?
                    """, (json.dumps(queries), session_id))
        
        if article_id:
            cursor.execute("""
                SELECT shared_articles FROM collaboration_sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            
            if row:
                articles = json.loads(row[0])
                if article_id not in articles:
                    articles.append(article_id)
                    cursor.execute("""
                        UPDATE collaboration_sessions 
                        SET shared_articles = ? WHERE session_id = ?
                    """, (json.dumps(articles), session_id))
        
        if finding:
            cursor.execute("""
                SELECT findings FROM collaboration_sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            
            if row:
                findings = json.loads(row[0])
                findings.append(finding)
                cursor.execute("""
                    UPDATE collaboration_sessions 
                    SET findings = ? WHERE session_id = ?
                """, (json.dumps(findings), session_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def _log_activity(self, user_id: str, activity_type: str, activity_data: Dict):
        """Log team activity"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO team_activity (user_id, activity_type, activity_data, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, activity_type, json.dumps(activity_data), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_team_activity_feed(self, limit: int = 50) -> List[Dict]:
        """Get recent team activity"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, m.username 
            FROM team_activity a
            JOIN team_members m ON a.user_id = m.user_id
            ORDER BY a.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        activities = [
            {
                'activity_id': row[0],
                'user_id': row[1],
                'username': row[5],
                'activity_type': row[2],
                'activity_data': json.loads(row[3]),
                'timestamp': row[4]
            }
            for row in rows
        ]
        
        conn.close()
        return activities
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Get user collaboration statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Shared queries
        cursor.execute("""
            SELECT COUNT(*) FROM shared_queries WHERE created_by = ?
        """, (user_id,))
        stats['queries_shared'] = cursor.fetchone()[0]
        
        # Annotations created
        cursor.execute("""
            SELECT COUNT(*) FROM annotations WHERE author_id = ?
        """, (user_id,))
        stats['annotations_created'] = cursor.fetchone()[0]
        
        # Sessions participated
        cursor.execute("""
            SELECT COUNT(*) FROM collaboration_sessions 
            WHERE participants LIKE ?
        """, (f'%"{user_id}"%',))
        stats['sessions_participated'] = cursor.fetchone()[0]
        
        # Total query views
        cursor.execute("""
            SELECT SUM(view_count) FROM shared_queries WHERE created_by = ?
        """, (user_id,))
        stats['total_query_views'] = cursor.fetchone()[0] or 0
        
        # Total upvotes received
        cursor.execute("""
            SELECT SUM(upvotes) FROM shared_queries WHERE created_by = ?
        """, (user_id,))
        stats['total_upvotes'] = cursor.fetchone()[0] or 0
        
        conn.close()
        return stats
    
    def get_team_statistics(self) -> Dict:
        """Get overall team collaboration statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total members
        cursor.execute("SELECT COUNT(*) FROM team_members WHERE is_active = 1")
        stats['total_members'] = cursor.fetchone()[0]
        
        # Members by role
        cursor.execute("""
            SELECT role, COUNT(*) FROM team_members 
            WHERE is_active = 1 GROUP BY role
        """)
        stats['by_role'] = dict(cursor.fetchall())
        
        # Total shared queries
        cursor.execute("SELECT COUNT(*) FROM shared_queries")
        stats['total_shared_queries'] = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute("SELECT COUNT(*) FROM collaboration_sessions WHERE is_active = 1")
        stats['active_sessions'] = cursor.fetchone()[0]
        
        # Total annotations
        cursor.execute("SELECT COUNT(*) FROM annotations")
        stats['total_annotations'] = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM team_activity 
            WHERE datetime(timestamp) > datetime('now', '-1 day')
        """)
        stats['recent_activity_count'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    collab = JupiterCollaborationManager()
    
    # Add team members
    admin = collab.add_team_member(
        username="john_admin",
        email="john@company.com",
        role=UserRole.ADMIN,
        department="Security Operations"
    )
    
    analyst = collab.add_team_member(
        username="jane_analyst",
        email="jane@company.com",
        role=UserRole.ANALYST,
        department="Vulnerability Analysis"
    )
    
    print(f"Added team members:")
    print(f"  Admin: {admin.username} ({admin.role.value})")
    print(f"  Analyst: {analyst.username} ({analyst.role.value})")
    
    # Share query
    query = collab.share_query(
        query_text="Analyze authentication bypass vulnerability",
        results="Critical vulnerability found in session management...",
        created_by=analyst.user_id,
        tags=["authentication", "critical"],
        collaborators=[admin.user_id]
    )
    
    print(f"\nShared query: {query.query_id}")
    
    # Create collaboration session
    session = collab.create_collaboration_session(
        title="Q4 Security Assessment",
        created_by=admin.user_id,
        description="Quarterly security review and remediation planning",
        participants=[admin.user_id, analyst.user_id]
    )
    
    print(f"Created session: {session.title} ({session.session_id})")
    
    # Add annotation
    annotation = collab.add_annotation(
        target_id=query.query_id,
        target_type="query",
        author_id=admin.user_id,
        content="Excellent analysis! Please escalate to security team immediately."
    )
    
    print(f"Added annotation: {annotation.annotation_id}")
    
    # Get statistics
    stats = collab.get_team_statistics()
    print(f"\nTeam statistics:")
    print(f"  Total members: {stats['total_members']}")
    print(f"  Shared queries: {stats['total_shared_queries']}")
    print(f"  Active sessions: {stats['active_sessions']}")
