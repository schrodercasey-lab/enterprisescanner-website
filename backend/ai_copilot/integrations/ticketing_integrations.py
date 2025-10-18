"""
Jupiter Ticketing System Integrations
Connect with enterprise IT Service Management and incident tracking platforms
Supports Jira, ServiceNow, PagerDuty
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


class TicketingSystem(Enum):
    """Supported ticketing platforms"""
    JIRA = "jira"
    SERVICENOW = "servicenow"
    PAGERDUTY = "pagerduty"
    FRESHSERVICE = "freshservice"
    ZENDESK = "zendesk"


class TicketPriority(Enum):
    """Ticket priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketStatus(Enum):
    """Ticket status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ON_HOLD = "on_hold"


@dataclass
class Ticket:
    """Universal ticket representation"""
    ticket_id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    cve_id: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    external_id: Optional[str] = None  # ID in external system
    external_url: Optional[str] = None  # Link to ticket in external system
    custom_fields: Dict = field(default_factory=dict)


class TicketingIntegrationBase(ABC):
    """Base class for ticketing integrations"""
    
    def __init__(self, base_url: str, auth: Dict[str, str], verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
    
    @abstractmethod
    def create_ticket(self, ticket: Ticket) -> Optional[str]:
        """Create ticket in external system"""
        pass
    
    @abstractmethod
    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """Update existing ticket"""
        pass
    
    @abstractmethod
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket details"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to ticketing system"""
        pass


class JiraIntegration(TicketingIntegrationBase):
    """Atlassian Jira integration"""
    
    def __init__(
        self,
        base_url: str,
        auth: Dict[str, str],  # {'email': 'user@company.com', 'api_token': 'token'}
        project_key: str,
        issue_type: str = "Bug",
        verify_ssl: bool = True
    ):
        super().__init__(base_url, auth, verify_ssl)
        self.project_key = project_key
        self.issue_type = issue_type
        
        # Set up authentication
        self.session.auth = (auth['email'], auth['api_token'])
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def create_ticket(self, ticket: Ticket) -> Optional[str]:
        """Create Jira issue"""
        try:
            url = f"{self.base_url}/rest/api/3/issue"
            
            # Map priority
            priority_map = {
                TicketPriority.CRITICAL: "Highest",
                TicketPriority.HIGH: "High",
                TicketPriority.MEDIUM: "Medium",
                TicketPriority.LOW: "Low"
            }
            
            issue_data = {
                'fields': {
                    'project': {'key': self.project_key},
                    'summary': ticket.title,
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': ticket.description
                                    }
                                ]
                            }
                        ]
                    },
                    'issuetype': {'name': self.issue_type},
                    'priority': {'name': priority_map.get(ticket.priority, "Medium")}
                }
            }
            
            # Add labels
            if ticket.labels:
                issue_data['fields']['labels'] = ticket.labels
            
            # Add CVE information
            if ticket.cve_id:
                issue_data['fields']['labels'] = issue_data['fields'].get('labels', [])
                issue_data['fields']['labels'].append(ticket.cve_id)
            
            # Add assignee if provided
            if ticket.assignee:
                issue_data['fields']['assignee'] = {'name': ticket.assignee}
            
            response = self.session.post(url, json=issue_data, verify=self.verify_ssl)
            
            if response.status_code == 201:
                result = response.json()
                external_id = result['key']
                external_url = f"{self.base_url}/browse/{external_id}"
                return external_id
            else:
                print(f"Jira create error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Jira create exception: {e}")
            return None
    
    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """Update Jira issue"""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
            
            update_data = {'fields': {}}
            
            # Map status updates to transitions (simplified)
            if 'status' in updates:
                # Would need to call transitions endpoint
                pass
            
            if 'priority' in updates:
                priority_map = {
                    'critical': 'Highest',
                    'high': 'High',
                    'medium': 'Medium',
                    'low': 'Low'
                }
                update_data['fields']['priority'] = {
                    'name': priority_map.get(updates['priority'], 'Medium')
                }
            
            if 'assignee' in updates:
                update_data['fields']['assignee'] = {'name': updates['assignee']}
            
            response = self.session.put(url, json=update_data, verify=self.verify_ssl)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Jira update exception: {e}")
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get Jira issue details"""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
            response = self.session.get(url, verify=self.verify_ssl)
            
            if response.status_code == 200:
                issue = response.json()
                fields = issue['fields']
                
                # Map Jira priority to our priority
                priority_map = {
                    'Highest': TicketPriority.CRITICAL,
                    'High': TicketPriority.HIGH,
                    'Medium': TicketPriority.MEDIUM,
                    'Low': TicketPriority.LOW
                }
                
                # Map Jira status
                status_map = {
                    'Open': TicketStatus.OPEN,
                    'In Progress': TicketStatus.IN_PROGRESS,
                    'Resolved': TicketStatus.RESOLVED,
                    'Closed': TicketStatus.CLOSED
                }
                
                return Ticket(
                    ticket_id=issue['key'],
                    title=fields['summary'],
                    description=fields.get('description', {}).get('content', [{}])[0].get('content', [{}])[0].get('text', ''),
                    priority=priority_map.get(fields.get('priority', {}).get('name'), TicketPriority.MEDIUM),
                    status=status_map.get(fields.get('status', {}).get('name'), TicketStatus.OPEN),
                    created_at=datetime.fromisoformat(fields['created'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(fields['updated'].replace('Z', '+00:00')),
                    assignee=fields.get('assignee', {}).get('displayName'),
                    reporter=fields.get('reporter', {}).get('displayName'),
                    labels=fields.get('labels', []),
                    external_id=issue['key'],
                    external_url=f"{self.base_url}/browse/{issue['key']}"
                )
        except Exception as e:
            print(f"Jira get exception: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """Test Jira connection"""
        try:
            url = f"{self.base_url}/rest/api/3/myself"
            response = self.session.get(url, verify=self.verify_ssl)
            return response.status_code == 200
        except:
            return False


class ServiceNowIntegration(TicketingIntegrationBase):
    """ServiceNow IT Service Management integration"""
    
    def __init__(
        self,
        base_url: str,
        auth: Dict[str, str],  # {'username': 'user', 'password': 'pass'}
        table: str = "incident",
        verify_ssl: bool = True
    ):
        super().__init__(base_url, auth, verify_ssl)
        self.table = table
        
        # Set up authentication
        self.session.auth = (auth['username'], auth['password'])
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_ticket(self, ticket: Ticket) -> Optional[str]:
        """Create ServiceNow incident"""
        try:
            url = f"{self.base_url}/api/now/table/{self.table}"
            
            # Map priority (ServiceNow uses 1-5 scale)
            priority_map = {
                TicketPriority.CRITICAL: "1",
                TicketPriority.HIGH: "2",
                TicketPriority.MEDIUM: "3",
                TicketPriority.LOW: "4"
            }
            
            incident_data = {
                'short_description': ticket.title,
                'description': ticket.description,
                'priority': priority_map.get(ticket.priority, "3"),
                'category': 'Security',
                'subcategory': 'Vulnerability'
            }
            
            # Add CVE information
            if ticket.cve_id:
                incident_data['u_cve_id'] = ticket.cve_id
            
            # Add affected systems
            if ticket.affected_systems:
                incident_data['u_affected_systems'] = ', '.join(ticket.affected_systems)
            
            response = self.session.post(url, json=incident_data, verify=self.verify_ssl)
            
            if response.status_code == 201:
                result = response.json()['result']
                return result['sys_id']
            else:
                print(f"ServiceNow create error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"ServiceNow create exception: {e}")
            return None
    
    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """Update ServiceNow incident"""
        try:
            url = f"{self.base_url}/api/now/table/{self.table}/{ticket_id}"
            
            update_data = {}
            
            if 'status' in updates:
                status_map = {
                    'open': '1',
                    'in_progress': '2',
                    'resolved': '6',
                    'closed': '7'
                }
                update_data['state'] = status_map.get(updates['status'], '1')
            
            if 'priority' in updates:
                priority_map = {
                    'critical': '1',
                    'high': '2',
                    'medium': '3',
                    'low': '4'
                }
                update_data['priority'] = priority_map.get(updates['priority'], '3')
            
            response = self.session.patch(url, json=update_data, verify=self.verify_ssl)
            return response.status_code == 200
            
        except Exception as e:
            print(f"ServiceNow update exception: {e}")
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ServiceNow incident details"""
        try:
            url = f"{self.base_url}/api/now/table/{self.table}/{ticket_id}"
            response = self.session.get(url, verify=self.verify_ssl)
            
            if response.status_code == 200:
                incident = response.json()['result']
                
                priority_map = {
                    '1': TicketPriority.CRITICAL,
                    '2': TicketPriority.HIGH,
                    '3': TicketPriority.MEDIUM,
                    '4': TicketPriority.LOW
                }
                
                status_map = {
                    '1': TicketStatus.OPEN,
                    '2': TicketStatus.IN_PROGRESS,
                    '6': TicketStatus.RESOLVED,
                    '7': TicketStatus.CLOSED
                }
                
                return Ticket(
                    ticket_id=incident['sys_id'],
                    title=incident['short_description'],
                    description=incident.get('description', ''),
                    priority=priority_map.get(incident.get('priority'), TicketPriority.MEDIUM),
                    status=status_map.get(incident.get('state'), TicketStatus.OPEN),
                    created_at=datetime.fromisoformat(incident['sys_created_on']),
                    updated_at=datetime.fromisoformat(incident['sys_updated_on']),
                    assignee=incident.get('assigned_to', {}).get('display_value'),
                    external_id=incident['number'],
                    external_url=f"{self.base_url}/incident.do?sys_id={incident['sys_id']}"
                )
        except Exception as e:
            print(f"ServiceNow get exception: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """Test ServiceNow connection"""
        try:
            url = f"{self.base_url}/api/now/table/sys_user"
            params = {'sysparm_limit': '1'}
            response = self.session.get(url, params=params, verify=self.verify_ssl)
            return response.status_code == 200
        except:
            return False


class PagerDutyIntegration(TicketingIntegrationBase):
    """PagerDuty incident management integration"""
    
    def __init__(
        self,
        api_key: str,
        service_id: str,
        escalation_policy_id: str,
        verify_ssl: bool = True
    ):
        super().__init__("https://api.pagerduty.com", {'api_key': api_key}, verify_ssl)
        self.service_id = service_id
        self.escalation_policy_id = escalation_policy_id
        
        # Set up authentication
        self.session.headers.update({
            'Authorization': f'Token token={api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.pagerduty+json;version=2'
        })
    
    def create_ticket(self, ticket: Ticket) -> Optional[str]:
        """Create PagerDuty incident"""
        try:
            url = f"{self.base_url}/incidents"
            
            # Map priority
            urgency_map = {
                TicketPriority.CRITICAL: "high",
                TicketPriority.HIGH: "high",
                TicketPriority.MEDIUM: "low",
                TicketPriority.LOW: "low"
            }
            
            incident_data = {
                'incident': {
                    'type': 'incident',
                    'title': ticket.title,
                    'service': {
                        'id': self.service_id,
                        'type': 'service_reference'
                    },
                    'urgency': urgency_map.get(ticket.priority, "low"),
                    'body': {
                        'type': 'incident_body',
                        'details': ticket.description
                    },
                    'escalation_policy': {
                        'id': self.escalation_policy_id,
                        'type': 'escalation_policy_reference'
                    }
                }
            }
            
            response = self.session.post(url, json=incident_data, verify=self.verify_ssl)
            
            if response.status_code == 201:
                result = response.json()['incident']
                return result['id']
            else:
                print(f"PagerDuty create error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"PagerDuty create exception: {e}")
            return None
    
    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """Update PagerDuty incident"""
        try:
            url = f"{self.base_url}/incidents/{ticket_id}"
            
            update_data = {'incident': {}}
            
            if 'status' in updates:
                status_map = {
                    'resolved': 'resolved',
                    'in_progress': 'acknowledged'
                }
                update_data['incident']['status'] = status_map.get(updates['status'])
            
            if 'priority' in updates:
                urgency_map = {
                    'critical': 'high',
                    'high': 'high',
                    'medium': 'low',
                    'low': 'low'
                }
                update_data['incident']['urgency'] = urgency_map.get(updates['priority'])
            
            response = self.session.put(url, json=update_data, verify=self.verify_ssl)
            return response.status_code == 200
            
        except Exception as e:
            print(f"PagerDuty update exception: {e}")
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get PagerDuty incident details"""
        try:
            url = f"{self.base_url}/incidents/{ticket_id}"
            response = self.session.get(url, verify=self.verify_ssl)
            
            if response.status_code == 200:
                incident = response.json()['incident']
                
                urgency_map = {
                    'high': TicketPriority.HIGH,
                    'low': TicketPriority.MEDIUM
                }
                
                status_map = {
                    'triggered': TicketStatus.OPEN,
                    'acknowledged': TicketStatus.IN_PROGRESS,
                    'resolved': TicketStatus.RESOLVED
                }
                
                return Ticket(
                    ticket_id=incident['id'],
                    title=incident['title'],
                    description=incident.get('body', {}).get('details', ''),
                    priority=urgency_map.get(incident.get('urgency'), TicketPriority.MEDIUM),
                    status=status_map.get(incident.get('status'), TicketStatus.OPEN),
                    created_at=datetime.fromisoformat(incident['created_at']),
                    updated_at=datetime.fromisoformat(incident['updated_at']),
                    external_id=incident['incident_number'],
                    external_url=incident['html_url']
                )
        except Exception as e:
            print(f"PagerDuty get exception: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """Test PagerDuty connection"""
        try:
            url = f"{self.base_url}/users"
            params = {'limit': 1}
            response = self.session.get(url, params=params, verify=self.verify_ssl)
            return response.status_code == 200
        except:
            return False


class JupiterTicketingIntegration:
    """
    Jupiter Ticketing Integration Manager
    Manages connections to multiple ticketing platforms
    """
    
    def __init__(self, db_path: str = "jupiter_ticketing.db"):
        self.db_path = db_path
        self.connections: Dict[str, TicketingIntegrationBase] = {}
        self._init_database()
    
    def _init_database(self):
        """Initialize ticketing integration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ticketing connections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticketing_connections (
                connection_id TEXT PRIMARY KEY,
                connection_name TEXT NOT NULL,
                system_type TEXT NOT NULL,
                base_url TEXT,
                is_enabled INTEGER DEFAULT 1,
                last_tested TEXT,
                test_status TEXT,
                tickets_created INTEGER DEFAULT 0
            )
        """)
        
        # Tickets created
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                connection_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                external_id TEXT,
                external_url TEXT,
                cve_id TEXT,
                FOREIGN KEY (connection_id) REFERENCES ticketing_connections(connection_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_connection(
        self,
        connection_name: str,
        system_type: TicketingSystem,
        **kwargs
    ) -> str:
        """Add ticketing system connection"""
        
        connection_id = hashlib.sha256(
            f"{connection_name}{system_type.value}".encode()
        ).hexdigest()[:16]
        
        # Create integration instance based on system type
        if system_type == TicketingSystem.JIRA:
            integration = JiraIntegration(
                base_url=kwargs['base_url'],
                auth=kwargs['auth'],
                project_key=kwargs['project_key'],
                issue_type=kwargs.get('issue_type', 'Bug')
            )
        elif system_type == TicketingSystem.SERVICENOW:
            integration = ServiceNowIntegration(
                base_url=kwargs['base_url'],
                auth=kwargs['auth'],
                table=kwargs.get('table', 'incident')
            )
        elif system_type == TicketingSystem.PAGERDUTY:
            integration = PagerDutyIntegration(
                api_key=kwargs['api_key'],
                service_id=kwargs['service_id'],
                escalation_policy_id=kwargs['escalation_policy_id']
            )
        else:
            raise ValueError(f"Unsupported ticketing system: {system_type}")
        
        # Test connection
        test_result = integration.test_connection()
        
        # Store connection
        self.connections[connection_id] = integration
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO ticketing_connections 
            (connection_id, connection_name, system_type, base_url, is_enabled, 
             last_tested, test_status, tickets_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            connection_id,
            connection_name,
            system_type.value,
            kwargs.get('base_url', 'api.pagerduty.com'),
            1,
            datetime.now().isoformat(),
            "success" if test_result else "failed",
            0
        ))
        
        conn.commit()
        conn.close()
        
        return connection_id
    
    def create_ticket(self, connection_id: str, ticket: Ticket) -> Optional[str]:
        """Create ticket in specific system"""
        
        if connection_id not in self.connections:
            print(f"Connection {connection_id} not found")
            return None
        
        integration = self.connections[connection_id]
        external_id = integration.create_ticket(ticket)
        
        if external_id:
            # Store ticket in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tickets 
                (ticket_id, connection_id, title, description, priority, status, 
                 created_at, updated_at, external_id, external_url, cve_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket.ticket_id,
                connection_id,
                ticket.title,
                ticket.description,
                ticket.priority.value,
                ticket.status.value,
                ticket.created_at.isoformat(),
                ticket.updated_at.isoformat(),
                external_id,
                ticket.external_url,
                ticket.cve_id
            ))
            
            cursor.execute("""
                UPDATE ticketing_connections 
                SET tickets_created = tickets_created + 1
                WHERE connection_id = ?
            """, (connection_id,))
            
            conn.commit()
            conn.close()
        
        return external_id
    
    def get_statistics(self) -> Dict:
        """Get ticketing integration statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM ticketing_connections WHERE is_enabled = 1")
        stats['active_connections'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tickets")
        stats['total_tickets_created'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT system_type, COUNT(*) FROM ticketing_connections GROUP BY system_type")
        stats['by_system'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
        stats['by_priority'] = dict(cursor.fetchall())
        
        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    ticketing = JupiterTicketingIntegration()
    
    # Add Jira connection
    jira_id = ticketing.add_connection(
        connection_name="Production Jira",
        system_type=TicketingSystem.JIRA,
        base_url="https://company.atlassian.net",
        auth={'email': 'admin@company.com', 'api_token': 'token'},
        project_key="SEC",
        issue_type="Security Vulnerability"
    )
    
    # Create ticket
    ticket = Ticket(
        ticket_id="jup_tick_12345",
        title="Critical vulnerability CVE-2024-1234",
        description="SQL injection found in web application requiring immediate patching",
        priority=TicketPriority.CRITICAL,
        status=TicketStatus.OPEN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        cve_id="CVE-2024-1234",
        affected_systems=["web-01", "web-02"],
        labels=["security", "sql-injection", "critical"]
    )
    
    external_id = ticketing.create_ticket(jira_id, ticket)
    print(f"Ticket created: {external_id}")
    
    stats = ticketing.get_statistics()
    print(f"Ticketing stats: {stats}")
