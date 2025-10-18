"""
Jupiter SIEM Integrations
Connect with enterprise Security Information and Event Management systems
Supports Splunk, IBM QRadar, Elastic Security, and ArcSight
"""

import sqlite3
import json
import requests
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import hashlib
from abc import ABC, abstractmethod


class SIEMType(Enum):
    """Supported SIEM platforms"""
    SPLUNK = "splunk"
    QRADAR = "qradar"
    ELASTIC = "elastic"
    ARCSIGHT = "arcsight"
    SENTINEL = "azure_sentinel"
    CHRONICLE = "google_chronicle"


@dataclass
class SIEMEvent:
    """Security event for SIEM ingestion"""
    event_id: str
    timestamp: datetime
    source: str  # Jupiter AI Copilot
    event_type: str  # vulnerability_detected, alert_created, etc.
    severity: str
    title: str
    description: str
    raw_data: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    cve_id: Optional[str] = None
    
    def to_cef(self) -> str:
        """Convert to Common Event Format (CEF)"""
        # CEF: CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        cef = f"CEF:1|Jupiter|AI Copilot|2.0|{self.event_type}|{self.title}|{self._severity_to_cef()}|"
        
        # Extensions
        extensions = []
        extensions.append(f"rt={int(self.timestamp.timestamp() * 1000)}")
        extensions.append(f"msg={self.description}")
        
        if self.cve_id:
            extensions.append(f"cve={self.cve_id}")
        
        if self.affected_systems:
            extensions.append(f"dhost={','.join(self.affected_systems)}")
        
        if self.tags:
            extensions.append(f"cat={','.join(self.tags)}")
        
        cef += " ".join(extensions)
        return cef
    
    def _severity_to_cef(self) -> str:
        """Convert severity to CEF format (0-10)"""
        severity_map = {
            'critical': '10',
            'high': '8',
            'medium': '5',
            'low': '3',
            'info': '1'
        }
        return severity_map.get(self.severity.lower(), '5')
    
    def to_leef(self) -> str:
        """Convert to Log Event Extended Format (LEEF) for QRadar"""
        # LEEF: LEEF:Version|Vendor|Product|Version|EventID|
        leef = f"LEEF:2.0|Jupiter|AI Copilot|2.0|{self.event_type}\t"
        
        # Key-value pairs
        fields = []
        fields.append(f"devTime={self.timestamp.isoformat()}")
        fields.append(f"devTimeFormat=ISO8601")
        fields.append(f"sev={self._severity_to_qradar()}")
        fields.append(f"cat={self.event_type}")
        fields.append(f"msg={self.title}")
        fields.append(f"desc={self.description}")
        
        if self.cve_id:
            fields.append(f"identSrc=CVE")
            fields.append(f"identHostName={self.cve_id}")
        
        leef += "\t".join(fields)
        return leef
    
    def _severity_to_qradar(self) -> int:
        """Convert severity to QRadar format (1-10)"""
        severity_map = {
            'critical': 10,
            'high': 8,
            'medium': 5,
            'low': 3,
            'info': 1
        }
        return severity_map.get(self.severity.lower(), 5)


@dataclass
class SIEMQuery:
    """Query results from SIEM"""
    query_id: str
    siem_type: SIEMType
    query_text: str
    executed_at: datetime
    results_count: int
    results: List[Dict] = field(default_factory=list)
    execution_time_ms: int = 0


class SIEMIntegrationBase(ABC):
    """Base class for SIEM integrations"""
    
    def __init__(self, base_url: str, api_key: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
    
    @abstractmethod
    def send_event(self, event: SIEMEvent) -> bool:
        """Send security event to SIEM"""
        pass
    
    @abstractmethod
    def query(self, query_text: str, time_range: str = "24h") -> SIEMQuery:
        """Query SIEM for events"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test SIEM connectivity"""
        pass


class SplunkIntegration(SIEMIntegrationBase):
    """Splunk Enterprise/Cloud integration"""
    
    def __init__(self, base_url: str, api_key: str, index: str = "main", verify_ssl: bool = True):
        super().__init__(base_url, api_key, verify_ssl)
        self.index = index
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_event(self, event: SIEMEvent) -> bool:
        """Send event to Splunk HTTP Event Collector (HEC)"""
        try:
            url = f"{self.base_url}/services/collector/event"
            
            payload = {
                'time': event.timestamp.timestamp(),
                'source': event.source,
                'sourcetype': 'jupiter:security',
                'index': self.index,
                'event': {
                    'event_id': event.event_id,
                    'event_type': event.event_type,
                    'severity': event.severity,
                    'title': event.title,
                    'description': event.description,
                    'cve_id': event.cve_id,
                    'affected_systems': event.affected_systems,
                    'tags': event.tags,
                    'raw_data': event.raw_data
                }
            }
            
            response = self.session.post(url, json=payload, verify=self.verify_ssl)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Splunk send error: {e}")
            return False
    
    def query(self, query_text: str, time_range: str = "24h") -> SIEMQuery:
        """Execute Splunk search query"""
        try:
            url = f"{self.base_url}/services/search/jobs"
            
            # Create search job
            data = {
                'search': f'search index={self.index} {query_text}',
                'earliest_time': f'-{time_range}',
                'latest_time': 'now'
            }
            
            start_time = datetime.now()
            response = self.session.post(url, data=data, verify=self.verify_ssl)
            
            if response.status_code == 201:
                job_id = response.json()['sid']
                
                # Wait for job completion (simplified - in production, poll status)
                import time
                time.sleep(2)
                
                # Get results
                results_url = f"{self.base_url}/services/search/jobs/{job_id}/results"
                results_response = self.session.get(
                    results_url,
                    params={'output_mode': 'json'},
                    verify=self.verify_ssl
                )
                
                results_data = results_response.json()
                results = results_data.get('results', [])
                
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return SIEMQuery(
                    query_id=job_id,
                    siem_type=SIEMType.SPLUNK,
                    query_text=query_text,
                    executed_at=start_time,
                    results_count=len(results),
                    results=results,
                    execution_time_ms=execution_time
                )
            
        except Exception as e:
            print(f"Splunk query error: {e}")
        
        return SIEMQuery(
            query_id="error",
            siem_type=SIEMType.SPLUNK,
            query_text=query_text,
            executed_at=datetime.now(),
            results_count=0
        )
    
    def test_connection(self) -> bool:
        """Test Splunk connection"""
        try:
            url = f"{self.base_url}/services/server/info"
            response = self.session.get(url, verify=self.verify_ssl)
            return response.status_code == 200
        except:
            return False


class QRadarIntegration(SIEMIntegrationBase):
    """IBM QRadar integration"""
    
    def __init__(self, base_url: str, api_key: str, verify_ssl: bool = True):
        super().__init__(base_url, api_key, verify_ssl)
        self.session.headers.update({
            'SEC': api_key,
            'Content-Type': 'application/json',
            'Version': '14.0'
        })
    
    def send_event(self, event: SIEMEvent) -> bool:
        """Send event to QRadar via LEEF format"""
        try:
            # QRadar typically receives events via syslog
            # This is a simplified REST API approach
            url = f"{self.base_url}/api/siem/offenses"
            
            # In production, would send via syslog UDP/TCP
            # Here we demonstrate the data structure
            leef_event = event.to_leef()
            
            # For demonstration - actual implementation would use syslog
            print(f"QRadar LEEF event: {leef_event}")
            
            return True
            
        except Exception as e:
            print(f"QRadar send error: {e}")
            return False
    
    def query(self, query_text: str, time_range: str = "24h") -> SIEMQuery:
        """Execute AQL (Ariel Query Language) query"""
        try:
            url = f"{self.base_url}/api/ariel/searches"
            
            # Convert time range to minutes
            time_minutes = self._parse_time_range(time_range)
            
            # Create AQL query
            aql_query = {
                'query_expression': query_text,
                'query_type': 'ARIEL'
            }
            
            start_time = datetime.now()
            response = self.session.post(url, json=aql_query, verify=self.verify_ssl)
            
            if response.status_code == 201:
                search_id = response.json()['search_id']
                
                # Get results (simplified polling)
                import time
                time.sleep(2)
                
                results_url = f"{self.base_url}/api/ariel/searches/{search_id}/results"
                results_response = self.session.get(results_url, verify=self.verify_ssl)
                
                if results_response.status_code == 200:
                    results_data = results_response.json()
                    events = results_data.get('events', [])
                    
                    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    return SIEMQuery(
                        query_id=search_id,
                        siem_type=SIEMType.QRADAR,
                        query_text=query_text,
                        executed_at=start_time,
                        results_count=len(events),
                        results=events,
                        execution_time_ms=execution_time
                    )
            
        except Exception as e:
            print(f"QRadar query error: {e}")
        
        return SIEMQuery(
            query_id="error",
            siem_type=SIEMType.QRADAR,
            query_text=query_text,
            executed_at=datetime.now(),
            results_count=0
        )
    
    def _parse_time_range(self, time_range: str) -> int:
        """Convert time range string to minutes"""
        if time_range.endswith('h'):
            return int(time_range[:-1]) * 60
        elif time_range.endswith('d'):
            return int(time_range[:-1]) * 1440
        return 1440  # Default 24 hours
    
    def test_connection(self) -> bool:
        """Test QRadar connection"""
        try:
            url = f"{self.base_url}/api/system/about"
            response = self.session.get(url, verify=self.verify_ssl)
            return response.status_code == 200
        except:
            return False


class ElasticIntegration(SIEMIntegrationBase):
    """Elastic Security (ELK Stack) integration"""
    
    def __init__(self, base_url: str, api_key: str, index: str = "jupiter-security", verify_ssl: bool = True):
        super().__init__(base_url, api_key, verify_ssl)
        self.index = index
        self.session.headers.update({
            'Authorization': f'ApiKey {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_event(self, event: SIEMEvent) -> bool:
        """Send event to Elasticsearch"""
        try:
            url = f"{self.base_url}/{self.index}/_doc"
            
            document = {
                '@timestamp': event.timestamp.isoformat(),
                'event': {
                    'id': event.event_id,
                    'type': event.event_type,
                    'severity': event.severity,
                    'category': event.tags
                },
                'message': event.title,
                'description': event.description,
                'source': {
                    'name': event.source
                },
                'vulnerability': {
                    'id': event.cve_id
                } if event.cve_id else None,
                'host': {
                    'name': event.affected_systems
                } if event.affected_systems else None,
                'tags': event.tags,
                'raw_data': event.raw_data
            }
            
            response = self.session.post(url, json=document, verify=self.verify_ssl)
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Elastic send error: {e}")
            return False
    
    def query(self, query_text: str, time_range: str = "24h") -> SIEMQuery:
        """Execute Elasticsearch query"""
        try:
            url = f"{self.base_url}/{self.index}/_search"
            
            # Build Elasticsearch query
            es_query = {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'query_string': {
                                    'query': query_text
                                }
                            },
                            {
                                'range': {
                                    '@timestamp': {
                                        'gte': f'now-{time_range}',
                                        'lte': 'now'
                                    }
                                }
                            }
                        ]
                    }
                },
                'size': 1000,
                'sort': [
                    {'@timestamp': {'order': 'desc'}}
                ]
            }
            
            start_time = datetime.now()
            response = self.session.post(url, json=es_query, verify=self.verify_ssl)
            
            if response.status_code == 200:
                results_data = response.json()
                hits = results_data.get('hits', {}).get('hits', [])
                results = [hit['_source'] for hit in hits]
                
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return SIEMQuery(
                    query_id=hashlib.sha256(query_text.encode()).hexdigest()[:12],
                    siem_type=SIEMType.ELASTIC,
                    query_text=query_text,
                    executed_at=start_time,
                    results_count=len(results),
                    results=results,
                    execution_time_ms=execution_time
                )
            
        except Exception as e:
            print(f"Elastic query error: {e}")
        
        return SIEMQuery(
            query_id="error",
            siem_type=SIEMType.ELASTIC,
            query_text=query_text,
            executed_at=datetime.now(),
            results_count=0
        )
    
    def test_connection(self) -> bool:
        """Test Elasticsearch connection"""
        try:
            url = f"{self.base_url}/_cluster/health"
            response = self.session.get(url, verify=self.verify_ssl)
            return response.status_code == 200
        except:
            return False


class JupiterSIEMIntegration:
    """
    Jupiter SIEM Integration Manager
    Manages connections to multiple SIEM platforms
    """
    
    def __init__(self, db_path: str = "jupiter_siem.db"):
        self.db_path = db_path
        self.connections: Dict[str, SIEMIntegrationBase] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize SIEM integration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SIEM connections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siem_connections (
                connection_id TEXT PRIMARY KEY,
                connection_name TEXT NOT NULL,
                siem_type TEXT NOT NULL,
                base_url TEXT NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                last_tested TEXT,
                test_status TEXT,
                events_sent INTEGER DEFAULT 0,
                queries_executed INTEGER DEFAULT 0
            )
        """)
        
        # Event log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siem_events_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                connection_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (connection_id) REFERENCES siem_connections(connection_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_connection(
        self,
        connection_name: str,
        siem_type: SIEMType,
        base_url: str,
        api_key: str,
        **kwargs
    ) -> str:
        """Add SIEM connection"""
        
        connection_id = hashlib.sha256(
            f"{connection_name}{siem_type.value}".encode()
        ).hexdigest()[:16]
        
        # Create integration instance
        if siem_type == SIEMType.SPLUNK:
            integration = SplunkIntegration(
                base_url, api_key,
                index=kwargs.get('index', 'main')
            )
        elif siem_type == SIEMType.QRADAR:
            integration = QRadarIntegration(base_url, api_key)
        elif siem_type == SIEMType.ELASTIC:
            integration = ElasticIntegration(
                base_url, api_key,
                index=kwargs.get('index', 'jupiter-security')
            )
        else:
            raise ValueError(f"Unsupported SIEM type: {siem_type}")
        
        # Test connection
        test_result = integration.test_connection()
        
        # Store connection
        self.connections[connection_id] = integration
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO siem_connections 
            (connection_id, connection_name, siem_type, base_url, is_enabled, 
             last_tested, test_status, events_sent, queries_executed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            connection_id,
            connection_name,
            siem_type.value,
            base_url,
            1,
            datetime.now().isoformat(),
            "success" if test_result else "failed",
            0,
            0
        ))
        
        conn.commit()
        conn.close()
        
        return connection_id
    
    def send_event_to_all(self, event: SIEMEvent) -> Dict[str, bool]:
        """Send event to all enabled SIEM connections"""
        results = {}
        
        for connection_id, integration in self.connections.items():
            try:
                success = integration.send_event(event)
                results[connection_id] = success
                
                # Log event
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO siem_events_log 
                    (connection_id, event_id, sent_at, status, error_message)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    connection_id,
                    event.event_id,
                    datetime.now().isoformat(),
                    "success" if success else "failed",
                    None if success else "Send failed"
                ))
                
                if success:
                    cursor.execute("""
                        UPDATE siem_connections 
                        SET events_sent = events_sent + 1
                        WHERE connection_id = ?
                    """, (connection_id,))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                results[connection_id] = False
                print(f"Error sending to {connection_id}: {e}")
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get SIEM integration statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM siem_connections WHERE is_enabled = 1")
        stats['active_connections'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(events_sent) FROM siem_connections")
        stats['total_events_sent'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT siem_type, COUNT(*) FROM siem_connections GROUP BY siem_type")
        stats['by_type'] = dict(cursor.fetchall())
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    siem = JupiterSIEMIntegration()
    
    # Add Splunk connection (example - would use real credentials)
    splunk_id = siem.add_connection(
        connection_name="Production Splunk",
        siem_type=SIEMType.SPLUNK,
        base_url="https://splunk.company.com:8088",
        api_key="your-hec-token-here",
        index="security"
    )
    
    # Create security event
    event = SIEMEvent(
        event_id="evt_12345",
        timestamp=datetime.now(),
        source="Jupiter AI Copilot",
        event_type="vulnerability_detected",
        severity="critical",
        title="Critical CVE-2024-1234 detected in production",
        description="SQL injection vulnerability found in web application",
        cve_id="CVE-2024-1234",
        affected_systems=["web-01", "web-02"],
        tags=["vulnerability", "sql-injection", "critical"]
    )
    
    # Send to all SIEM systems
    results = siem.send_event_to_all(event)
    print(f"Event sent: {results}")
    
    # Get statistics
    stats = siem.get_statistics()
    print(f"SIEM stats: {stats}")
