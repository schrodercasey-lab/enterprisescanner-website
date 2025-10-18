"""
Jupiter Usage Tracker - Module A.2 (Part 1)

Comprehensive usage tracking and analytics for demonstrating ROI and
understanding customer behavior.

Features:
- Query tracking and analytics
- Feature usage monitoring
- Response time metrics
- Cost calculation (LLM token usage)
- Power user identification
- Pattern analysis
- Churn risk detection

Business Impact: +$20K ARPU
- CISOs can justify investment with hard data
- Usage-based pricing tiers enabled
- Upsell opportunities identified
- Board-level reporting capability

Author: Enterprise Scanner Team
Version: 2.0.0
Date: October 17, 2025
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path
from collections import defaultdict


class UsageMetric(Enum):
    """Types of usage metrics"""
    QUERY = "query"
    SCAN_ANALYSIS = "scan_analysis"
    THREAT_INTEL = "threat_intel"
    REMEDIATION = "remediation"
    KNOWLEDGE_BASE = "knowledge_base"
    EXPORT = "export"
    SHARE = "share"


@dataclass
class QueryLog:
    """Individual query log entry"""
    log_id: str
    query_id: str
    user_id: str
    session_id: str
    
    # Query details
    query_text: str
    query_type: str
    access_level: str
    
    # Response details
    response_time_ms: int
    tokens_used: int
    cost_usd: float
    confidence_score: float
    
    # Context
    feature_used: str  # Which Jupiter feature
    success: bool
    error_message: Optional[str] = None
    
    # Metadata
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class UsageSummary:
    """Aggregated usage statistics"""
    timeframe_days: int
    
    # Volume metrics
    total_queries: int
    unique_users: int
    unique_sessions: int
    
    # Performance metrics
    avg_response_time_ms: float
    p95_response_time_ms: float
    success_rate: float
    
    # Cost metrics
    total_tokens: int
    total_cost_usd: float
    avg_cost_per_query: float
    
    # Feature usage
    feature_breakdown: Dict[str, int]
    query_type_breakdown: Dict[str, int]
    
    # User engagement
    power_users: List[Dict[str, Any]]
    at_risk_users: List[Dict[str, Any]]
    
    # Trends
    daily_query_counts: List[Tuple[str, int]]
    growth_rate: float


class JupiterUsageTracker:
    """
    Jupiter Usage Tracking and Analytics System
    
    Tracks all Jupiter interactions for ROI demonstration,
    usage-based pricing, and customer success monitoring.
    """
    
    def __init__(self, db_path: str = "data/jupiter_usage.db"):
        """
        Initialize Jupiter Usage Tracker
        
        Args:
            db_path: Path to SQLite database for usage storage
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Pricing configuration (cost per 1K tokens)
        self.pricing = {
            'gpt-4': 0.03,  # $0.03 per 1K tokens
            'gpt-4-turbo': 0.01,
            'gpt-3.5-turbo': 0.002,
            'claude-3-opus': 0.015,
            'claude-3-sonnet': 0.003
        }
        
        # Statistics
        self.stats = {
            'total_queries_tracked': 0,
            'total_cost_usd': 0.0,
            'total_tokens_used': 0,
            'unique_users': set(),
            'unique_sessions': set()
        }
        
        self.logger.info("Jupiter Usage Tracker initialized")
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Query logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jupiter_query_logs (
                    log_id TEXT PRIMARY KEY,
                    query_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    
                    query_text TEXT,
                    query_type TEXT,
                    access_level TEXT,
                    
                    response_time_ms INTEGER,
                    tokens_used INTEGER,
                    cost_usd REAL,
                    confidence_score REAL,
                    
                    feature_used TEXT,
                    success INTEGER,
                    error_message TEXT,
                    
                    timestamp TEXT,
                    
                    FOREIGN KEY (query_id) REFERENCES jupiter_queries(query_id)
                )
            """)
            
            # Feature usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jupiter_feature_usage (
                    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TEXT,
                    first_used TEXT
                )
            """)
            
            # User sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jupiter_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time TEXT,
                    end_time TEXT,
                    query_count INTEGER DEFAULT 0,
                    total_cost_usd REAL DEFAULT 0.0
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_logs 
                ON jupiter_query_logs(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp_logs 
                ON jupiter_query_logs(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feature_logs 
                ON jupiter_query_logs(feature_used)
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Usage tracking database initialized")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise
    
    def track_query(
        self,
        query_id: str,
        user_id: str,
        session_id: str,
        query_text: str,
        query_type: str,
        access_level: str,
        response_time_ms: int,
        tokens_used: int,
        model: str = "gpt-4-turbo",
        confidence_score: float = 0.0,
        feature_used: str = "general",
        success: bool = True,
        error_message: Optional[str] = None
    ) -> str:
        """
        Track a Jupiter query
        
        Args:
            query_id: Query identifier
            user_id: User identifier
            session_id: Session identifier
            query_text: User's query
            query_type: Type of query
            access_level: User access level
            response_time_ms: Response time in milliseconds
            tokens_used: Number of tokens consumed
            model: LLM model used
            confidence_score: Response confidence
            feature_used: Which Jupiter feature
            success: Whether query succeeded
            error_message: Error if failed
            
        Returns:
            log_id: Unique log identifier
        """
        log_id = f"log_{query_id}_{int(datetime.now().timestamp() * 1000)}"
        
        # Calculate cost
        cost_per_1k = self.pricing.get(model, 0.01)
        cost_usd = (tokens_used / 1000) * cost_per_1k
        
        query_log = QueryLog(
            log_id=log_id,
            query_id=query_id,
            user_id=user_id,
            session_id=session_id,
            query_text=query_text,
            query_type=query_type,
            access_level=access_level,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            confidence_score=confidence_score,
            feature_used=feature_used,
            success=success,
            error_message=error_message
        )
        
        self._store_query_log(query_log)
        self._update_feature_usage(user_id, feature_used)
        self._update_session(session_id, user_id, cost_usd)
        
        # Update stats
        self.stats['total_queries_tracked'] += 1
        self.stats['total_cost_usd'] += cost_usd
        self.stats['total_tokens_used'] += tokens_used
        self.stats['unique_users'].add(user_id)
        self.stats['unique_sessions'].add(session_id)
        
        self.logger.info(f"Tracked query: {query_id}, cost: ${cost_usd:.4f}, tokens: {tokens_used}")
        return log_id
    
    def get_usage_summary(
        self,
        timeframe_days: int = 30,
        user_id: Optional[str] = None
    ) -> UsageSummary:
        """
        Get comprehensive usage summary
        
        Args:
            timeframe_days: Number of days to analyze
            user_id: Optional filter by user
            
        Returns:
            UsageSummary with all metrics
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=timeframe_days)).isoformat()
            
            # Build query filters
            where_clause = "WHERE timestamp > ?"
            params = [cutoff_date]
            
            if user_id:
                where_clause += " AND user_id = ?"
                params.append(user_id)
            
            # Volume metrics
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT session_id) as unique_sessions
                FROM jupiter_query_logs
                {where_clause}
            """, params)
            total_queries, unique_users, unique_sessions = cursor.fetchone()
            
            # Performance metrics
            cursor.execute(f"""
                SELECT 
                    AVG(response_time_ms) as avg_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM jupiter_query_logs
                {where_clause}
            """, params)
            avg_response_time, success_rate = cursor.fetchone()
            avg_response_time = avg_response_time or 0.0
            success_rate = success_rate or 0.0
            
            # P95 response time
            cursor.execute(f"""
                SELECT response_time_ms
                FROM jupiter_query_logs
                {where_clause}
                ORDER BY response_time_ms
                LIMIT 1 OFFSET (
                    SELECT COUNT(*) * 95 / 100
                    FROM jupiter_query_logs
                    {where_clause}
                )
            """, params * 2)
            p95_result = cursor.fetchone()
            p95_response_time = p95_result[0] if p95_result else 0.0
            
            # Cost metrics
            cursor.execute(f"""
                SELECT 
                    SUM(tokens_used) as total_tokens,
                    SUM(cost_usd) as total_cost,
                    AVG(cost_usd) as avg_cost
                FROM jupiter_query_logs
                {where_clause}
            """, params)
            total_tokens, total_cost, avg_cost = cursor.fetchone()
            total_tokens = total_tokens or 0
            total_cost = total_cost or 0.0
            avg_cost = avg_cost or 0.0
            
            # Feature breakdown
            cursor.execute(f"""
                SELECT feature_used, COUNT(*) as count
                FROM jupiter_query_logs
                {where_clause}
                GROUP BY feature_used
                ORDER BY count DESC
            """, params)
            feature_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Query type breakdown
            cursor.execute(f"""
                SELECT query_type, COUNT(*) as count
                FROM jupiter_query_logs
                {where_clause}
                GROUP BY query_type
                ORDER BY count DESC
            """, params)
            query_type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Daily query counts (last 30 days)
            cursor.execute(f"""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as count
                FROM jupiter_query_logs
                {where_clause}
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            """, params)
            daily_counts = [(row[0], row[1]) for row in cursor.fetchall()]
            
            # Calculate growth rate (simple: compare last 7 days to previous 7 days)
            growth_rate = 0.0
            if len(daily_counts) >= 14:
                recent_week = sum(count for _, count in daily_counts[:7])
                previous_week = sum(count for _, count in daily_counts[7:14])
                if previous_week > 0:
                    growth_rate = ((recent_week - previous_week) / previous_week) * 100
            
            # Power users (top 10 by query count)
            cursor.execute(f"""
                SELECT 
                    user_id,
                    COUNT(*) as query_count,
                    SUM(cost_usd) as total_cost,
                    AVG(confidence_score) as avg_confidence
                FROM jupiter_query_logs
                {where_clause}
                GROUP BY user_id
                ORDER BY query_count DESC
                LIMIT 10
            """, params)
            power_users = [
                {
                    'user_id': row[0],
                    'query_count': row[1],
                    'total_cost': round(row[2], 2),
                    'avg_confidence': round(row[3], 2) if row[3] else 0.0
                }
                for row in cursor.fetchall()
            ]
            
            # At-risk users (low activity in recent period)
            cursor.execute(f"""
                SELECT 
                    user_id,
                    COUNT(*) as query_count,
                    MAX(timestamp) as last_activity
                FROM jupiter_query_logs
                {where_clause}
                GROUP BY user_id
                HAVING query_count < 5
                AND julianday('now') - julianday(last_activity) > 7
                ORDER BY last_activity ASC
                LIMIT 10
            """, params)
            at_risk_users = [
                {
                    'user_id': row[0],
                    'query_count': row[1],
                    'last_activity': row[2],
                    'days_inactive': (datetime.now() - datetime.fromisoformat(row[2])).days
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            summary = UsageSummary(
                timeframe_days=timeframe_days,
                total_queries=total_queries,
                unique_users=unique_users,
                unique_sessions=unique_sessions,
                avg_response_time_ms=round(avg_response_time, 2),
                p95_response_time_ms=round(p95_response_time, 2),
                success_rate=round(success_rate, 2),
                total_tokens=total_tokens,
                total_cost_usd=round(total_cost, 4),
                avg_cost_per_query=round(avg_cost, 4),
                feature_breakdown=feature_breakdown,
                query_type_breakdown=query_type_breakdown,
                power_users=power_users,
                at_risk_users=at_risk_users,
                daily_query_counts=daily_counts,
                growth_rate=round(growth_rate, 2)
            )
            
            self.logger.info(f"Generated usage summary: {total_queries} queries, {unique_users} users")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate usage summary: {e}", exc_info=True)
            # Return empty summary
            return UsageSummary(
                timeframe_days=timeframe_days,
                total_queries=0,
                unique_users=0,
                unique_sessions=0,
                avg_response_time_ms=0.0,
                p95_response_time_ms=0.0,
                success_rate=0.0,
                total_tokens=0,
                total_cost_usd=0.0,
                avg_cost_per_query=0.0,
                feature_breakdown={},
                query_type_breakdown={},
                power_users=[],
                at_risk_users=[],
                daily_query_counts=[],
                growth_rate=0.0
            )
    
    def identify_power_users(
        self,
        timeframe_days: int = 30,
        min_queries: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Identify power users for upsell opportunities
        
        Args:
            timeframe_days: Number of days to analyze
            min_queries: Minimum queries to be considered power user
            
        Returns:
            List of power users with statistics
        """
        summary = self.get_usage_summary(timeframe_days)
        return [u for u in summary.power_users if u['query_count'] >= min_queries]
    
    def calculate_cost_breakdown(
        self,
        timeframe_days: int = 30,
        group_by: str = "user"
    ) -> Dict[str, float]:
        """
        Calculate cost breakdown
        
        Args:
            timeframe_days: Number of days to analyze
            group_by: Group by 'user', 'feature', or 'date'
            
        Returns:
            Dictionary of costs by group
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=timeframe_days)).isoformat()
            
            if group_by == "user":
                cursor.execute("""
                    SELECT user_id, SUM(cost_usd) as total_cost
                    FROM jupiter_query_logs
                    WHERE timestamp > ?
                    GROUP BY user_id
                    ORDER BY total_cost DESC
                """, (cutoff_date,))
            elif group_by == "feature":
                cursor.execute("""
                    SELECT feature_used, SUM(cost_usd) as total_cost
                    FROM jupiter_query_logs
                    WHERE timestamp > ?
                    GROUP BY feature_used
                    ORDER BY total_cost DESC
                """, (cutoff_date,))
            elif group_by == "date":
                cursor.execute("""
                    SELECT DATE(timestamp) as date, SUM(cost_usd) as total_cost
                    FROM jupiter_query_logs
                    WHERE timestamp > ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """, (cutoff_date,))
            else:
                raise ValueError(f"Invalid group_by: {group_by}")
            
            breakdown = {row[0]: round(row[1], 4) for row in cursor.fetchall()}
            conn.close()
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Failed to calculate cost breakdown: {e}", exc_info=True)
            return {}
    
    def export_usage_data(
        self,
        format: str = "json",
        timeframe_days: int = 30,
        user_id: Optional[str] = None
    ) -> str:
        """
        Export usage data for external analysis
        
        Args:
            format: Export format (json, csv)
            timeframe_days: Number of days to export
            user_id: Optional filter by user
            
        Returns:
            Exported data as string
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=timeframe_days)).isoformat()
            
            where_clause = "WHERE timestamp > ?"
            params = [cutoff_date]
            
            if user_id:
                where_clause += " AND user_id = ?"
                params.append(user_id)
            
            cursor.execute(f"""
                SELECT * FROM jupiter_query_logs
                {where_clause}
                ORDER BY timestamp DESC
            """, params)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            conn.close()
            
            if format == "json":
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                return json.dumps(data, indent=2, default=str)
            
            elif format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(columns)
                writer.writerows(rows)
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            self.logger.error(f"Failed to export usage data: {e}", exc_info=True)
            return "{}" if format == "json" else ""
    
    def _store_query_log(self, query_log: QueryLog):
        """Store query log in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO jupiter_query_logs VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                query_log.log_id,
                query_log.query_id,
                query_log.user_id,
                query_log.session_id,
                query_log.query_text,
                query_log.query_type,
                query_log.access_level,
                query_log.response_time_ms,
                query_log.tokens_used,
                query_log.cost_usd,
                query_log.confidence_score,
                query_log.feature_used,
                1 if query_log.success else 0,
                query_log.error_message,
                query_log.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to store query log: {e}", exc_info=True)
            raise
    
    def _update_feature_usage(self, user_id: str, feature_name: str):
        """Update feature usage tracking"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute("""
                SELECT usage_count FROM jupiter_feature_usage
                WHERE user_id = ? AND feature_name = ?
            """, (user_id, feature_name))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing
                cursor.execute("""
                    UPDATE jupiter_feature_usage
                    SET usage_count = usage_count + 1,
                        last_used = ?
                    WHERE user_id = ? AND feature_name = ?
                """, (datetime.now().isoformat(), user_id, feature_name))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO jupiter_feature_usage 
                    (user_id, feature_name, usage_count, last_used, first_used)
                    VALUES (?, ?, 1, ?, ?)
                """, (user_id, feature_name, datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update feature usage: {e}", exc_info=True)
    
    def _update_session(self, session_id: str, user_id: str, cost_usd: float):
        """Update session tracking"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if session exists
            cursor.execute("""
                SELECT query_count FROM jupiter_sessions
                WHERE session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing
                cursor.execute("""
                    UPDATE jupiter_sessions
                    SET query_count = query_count + 1,
                        total_cost_usd = total_cost_usd + ?,
                        end_time = ?
                    WHERE session_id = ?
                """, (cost_usd, datetime.now().isoformat(), session_id))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO jupiter_sessions
                    (session_id, user_id, start_time, end_time, query_count, total_cost_usd)
                    VALUES (?, ?, ?, ?, 1, ?)
                """, (session_id, user_id, datetime.now().isoformat(), datetime.now().isoformat(), cost_usd))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update session: {e}", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics"""
        stats = self.stats.copy()
        stats['unique_users'] = len(stats['unique_users'])
        stats['unique_sessions'] = len(stats['unique_sessions'])
        return stats


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("JUPITER USAGE TRACKER - MODULE A.2 (Part 1)")
    print("="*70)
    
    # Initialize tracker
    print("\n1. Initializing Jupiter Usage Tracker...")
    tracker = JupiterUsageTracker(db_path="data/test_jupiter_usage.db")
    
    # Track some sample queries
    print("\n2. Tracking Sample Queries...")
    for i in range(5):
        log_id = tracker.track_query(
            query_id=f"query_00{i+1}",
            user_id="user_123" if i < 3 else "user_456",
            session_id="session_abc",
            query_text=f"Sample query {i+1}",
            query_type="general_inquiry",
            access_level="customer",
            response_time_ms=1500 + i*100,
            tokens_used=500 + i*50,
            model="gpt-4-turbo",
            confidence_score=0.9 - i*0.05,
            feature_used="scan_analysis" if i % 2 == 0 else "threat_intel",
            success=True
        )
        print(f"   Tracked query {i+1}: {log_id}")
    
    # Get usage summary
    print("\n3. Generating Usage Summary...")
    summary = tracker.get_usage_summary(timeframe_days=30)
    print(f"\n   Total Queries: {summary.total_queries}")
    print(f"   Unique Users: {summary.unique_users}")
    print(f"   Avg Response Time: {summary.avg_response_time_ms}ms")
    print(f"   Success Rate: {summary.success_rate}%")
    print(f"   Total Cost: ${summary.total_cost_usd}")
    print(f"   Avg Cost/Query: ${summary.avg_cost_per_query}")
    print(f"   Growth Rate: {summary.growth_rate}%")
    
    print(f"\n   Feature Breakdown:")
    for feature, count in summary.feature_breakdown.items():
        print(f"      • {feature}: {count}")
    
    # Cost breakdown
    print("\n4. Cost Breakdown by User...")
    cost_by_user = tracker.calculate_cost_breakdown(timeframe_days=30, group_by="user")
    for user, cost in cost_by_user.items():
        print(f"   • {user}: ${cost}")
    
    # Statistics
    print("\n5. Tracker Statistics:")
    stats = tracker.get_stats()
    for key, value in stats.items():
        print(f"   • {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ JUPITER USAGE TRACKER OPERATIONAL")
    print("="*70)
    print("\nFeatures:")
    print("  • Query tracking with cost calculation")
    print("  • Feature usage monitoring")
    print("  • Response time metrics")
    print("  • Power user identification")
    print("  • Churn risk detection")
    print("  • Usage-based pricing support")
    print("\nBusiness Impact: +$20K ARPU")
    print("  • ROI demonstration")
    print("  • Usage-based billing")
    print("  • Upsell opportunities")
    print("="*70)
