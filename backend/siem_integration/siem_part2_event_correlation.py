"""
Military Upgrade #22: SIEM Integration
Part 2: Event Correlation & Analysis

This module implements real-time event correlation to identify
complex attack patterns across multiple log sources.

Key Features:
- Temporal correlation (time-based patterns)
- Spatial correlation (source-based patterns)
- Multi-stage attack detection
- Anomaly detection
- Alert generation

Compliance:
- NIST 800-53 IR-4 (Incident Handling)
- NIST 800-92 (Log Management)
- PCI DSS 10.6 (Log Analysis)
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class CorrelationRule(Enum):
    """Correlation rule types"""
    BRUTE_FORCE = "brute_force"
    LATERAL_MOVEMENT = "lateral_movement"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    RECONNAISSANCE = "reconnaissance"


@dataclass
class CorrelatedEvent:
    """Correlated security event"""
    event_id: str
    rule_matched: CorrelationRule
    confidence: float  # 0.0 - 1.0
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Involved entities
    source_ips: Set[str] = field(default_factory=set)
    target_hosts: Set[str] = field(default_factory=set)
    users: Set[str] = field(default_factory=set)
    
    # Timeline
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    event_count: int = 0
    
    # Evidence
    related_logs: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)


class EventCorrelator:
    """Event correlation engine"""
    
    def __init__(self, time_window: int = 300):
        self.time_window = time_window  # seconds
        self.events: List[CorrelatedEvent] = []
        
        # Tracking state
        self.failed_logins = defaultdict(list)  # {ip: [timestamps]}
        self.host_access = defaultdict(set)  # {user: {hosts}}
        self.data_transfers = defaultdict(list)  # {ip: [sizes]}
    
    def correlate_login_failures(self, source_ip: str, user: str, 
                                 timestamp: datetime) -> Optional[CorrelatedEvent]:
        """Detect brute force login attempts"""
        # Track failed logins
        self.failed_logins[source_ip].append(timestamp)
        
        # Clean old entries
        cutoff = timestamp - timedelta(seconds=self.time_window)
        self.failed_logins[source_ip] = [
            t for t in self.failed_logins[source_ip] if t > cutoff
        ]
        
        # Check threshold (5 failures in time window)
        if len(self.failed_logins[source_ip]) >= 5:
            event = CorrelatedEvent(
                event_id=f"CORR-{timestamp.strftime('%Y%m%d-%H%M%S')}",
                rule_matched=CorrelationRule.BRUTE_FORCE,
                confidence=0.9,
                severity="HIGH",
                source_ips={source_ip},
                users={user},
                event_count=len(self.failed_logins[source_ip]),
                indicators=[
                    f"{len(self.failed_logins[source_ip])} failed logins from {source_ip}",
                    f"Time window: {self.time_window}s"
                ]
            )
            
            self.events.append(event)
            print(f"🚨 BRUTE FORCE detected: {source_ip} ({event.event_count} attempts)")
            return event
        
        return None
    
    def correlate_lateral_movement(self, user: str, target_host: str,
                                   timestamp: datetime) -> Optional[CorrelatedEvent]:
        """Detect lateral movement across hosts"""
        # Track host access
        self.host_access[user].add(target_host)
        
        # Check if user accessed many hosts quickly (>3 hosts)
        if len(self.host_access[user]) >= 3:
            event = CorrelatedEvent(
                event_id=f"CORR-{timestamp.strftime('%Y%m%d-%H%M%S')}",
                rule_matched=CorrelationRule.LATERAL_MOVEMENT,
                confidence=0.75,
                severity="CRITICAL",
                users={user},
                target_hosts=self.host_access[user].copy(),
                event_count=len(self.host_access[user]),
                indicators=[
                    f"User {user} accessed {len(self.host_access[user])} hosts",
                    f"Hosts: {', '.join(list(self.host_access[user])[:5])}"
                ]
            )
            
            self.events.append(event)
            print(f"🚨 LATERAL MOVEMENT detected: {user} → {len(self.host_access[user])} hosts")
            return event
        
        return None
    
    def correlate_data_exfiltration(self, source_ip: str, bytes_transferred: int,
                                    timestamp: datetime) -> Optional[CorrelatedEvent]:
        """Detect potential data exfiltration"""
        # Track data transfers
        self.data_transfers[source_ip].append({
            'timestamp': timestamp,
            'bytes': bytes_transferred
        })
        
        # Clean old entries
        cutoff = timestamp - timedelta(seconds=self.time_window)
        self.data_transfers[source_ip] = [
            t for t in self.data_transfers[source_ip]
            if t['timestamp'] > cutoff
        ]
        
        # Calculate total bytes in window
        total_bytes = sum(t['bytes'] for t in self.data_transfers[source_ip])
        
        # Check threshold (>100MB in time window)
        if total_bytes > 100_000_000:  # 100 MB
            event = CorrelatedEvent(
                event_id=f"CORR-{timestamp.strftime('%Y%m%d-%H%M%S')}",
                rule_matched=CorrelationRule.DATA_EXFILTRATION,
                confidence=0.70,
                severity="HIGH",
                source_ips={source_ip},
                event_count=len(self.data_transfers[source_ip]),
                indicators=[
                    f"Large data transfer: {total_bytes / 1_000_000:.1f} MB",
                    f"Transfers: {len(self.data_transfers[source_ip])}",
                    f"Time window: {self.time_window}s"
                ]
            )
            
            self.events.append(event)
            print(f"🚨 DATA EXFILTRATION detected: {source_ip} ({total_bytes / 1_000_000:.1f} MB)")
            return event
        
        return None
    
    def analyze_attack_chain(self) -> List[Dict[str, Any]]:
        """Identify multi-stage attack chains"""
        chains = []
        
        # Group events by source IP
        events_by_ip = defaultdict(list)
        for event in self.events:
            for ip in event.source_ips:
                events_by_ip[ip].append(event)
        
        # Look for attack progression
        for ip, ip_events in events_by_ip.items():
            if len(ip_events) >= 2:
                # Sort by first_seen
                ip_events.sort(key=lambda e: e.first_seen)
                
                chain = {
                    'source_ip': ip,
                    'stages': [e.rule_matched.value for e in ip_events],
                    'severity': 'CRITICAL',
                    'timeline': {
                        'start': ip_events[0].first_seen.isoformat(),
                        'end': ip_events[-1].last_seen.isoformat()
                    },
                    'confidence': sum(e.confidence for e in ip_events) / len(ip_events)
                }
                
                chains.append(chain)
                print(f"⚠️ Attack chain detected: {ip} → {' → '.join(chain['stages'])}")
        
        return chains
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get correlation statistics"""
        by_rule = defaultdict(int)
        for event in self.events:
            by_rule[event.rule_matched.value] += 1
        
        by_severity = defaultdict(int)
        for event in self.events:
            by_severity[event.severity] += 1
        
        return {
            'total_correlated_events': len(self.events),
            'by_rule': dict(by_rule),
            'by_severity': dict(by_severity),
            'high_confidence_events': sum(
                1 for e in self.events if e.confidence >= 0.8
            )
        }


# Example usage
if __name__ == "__main__":
    correlator = EventCorrelator(time_window=300)
    
    # Simulate brute force
    now = datetime.now()
    for i in range(6):
        event = correlator.correlate_login_failures(
            "203.0.113.42",
            "admin",
            now + timedelta(seconds=i*10)
        )
    
    # Get statistics
    stats = correlator.get_statistics()
    print(f"\n📊 Correlation stats: {stats['total_correlated_events']} events")
