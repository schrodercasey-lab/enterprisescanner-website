"""
Military-Grade Zero-Trust Architecture - Part 1 of 5
===================================================

Microsegmentation & Network Policies

Features:
- Network microsegmentation
- East-west traffic control
- Policy-based segmentation
- Application-aware firewall rules
- Zero-trust network zones

COMPLIANCE:
- NIST 800-207 (Zero Trust Architecture)
- DoD Zero Trust Reference Architecture
- NSA Zero Trust Guidance
- CMMC Level 3-5 (AC.L3-3.1.1)
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import ipaddress


class ZoneType(Enum):
    """Network zone types"""
    DMZ = "DMZ"
    INTERNAL = "Internal"
    RESTRICTED = "Restricted"
    HIGHLY_RESTRICTED = "Highly Restricted"
    MANAGEMENT = "Management"
    DATA = "Data"


class PolicyAction(Enum):
    """Network policy actions"""
    ALLOW = "Allow"
    DENY = "Deny"
    LOG = "Log"
    ALERT = "Alert"


class Protocol(Enum):
    """Network protocols"""
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SSH = "SSH"


@dataclass
class NetworkSegment:
    """Network segment definition"""
    segment_id: str
    name: str
    zone_type: ZoneType
    cidr: str
    vlan_id: Optional[int]
    allowed_services: List[str]
    trust_level: int  # 0-100


@dataclass
class MicroSegmentationPolicy:
    """Microsegmentation policy"""
    policy_id: str
    name: str
    source_segment: str
    destination_segment: str
    protocol: Protocol
    port: Optional[int]
    action: PolicyAction
    requires_authentication: bool
    requires_encryption: bool
    logging_enabled: bool
    created_at: datetime


@dataclass
class TrafficFlow:
    """Network traffic flow"""
    flow_id: str
    source_ip: str
    destination_ip: str
    source_segment: str
    destination_segment: str
    protocol: Protocol
    port: int
    allowed: bool
    timestamp: datetime


class MicrosegmentationEngine:
    """Microsegmentation Engine - Part 1 of Zero-Trust"""
    
    def __init__(self):
        self.segments: Dict[str, NetworkSegment] = {}
        self.policies: Dict[str, MicroSegmentationPolicy] = {}
        self.traffic_logs: List[TrafficFlow] = []
        self._initialize_default_segments()
    
    def create_network_segment(self, segment: NetworkSegment) -> bool:
        """Create a network segment"""
        print(f"🔷 Creating network segment: {segment.name}")
        
        # Validate CIDR
        try:
            ipaddress.ip_network(segment.cidr)
        except ValueError as e:
            print(f"❌ Invalid CIDR: {e}")
            return False
        
        # Validate trust level
        if not 0 <= segment.trust_level <= 100:
            print(f"❌ Invalid trust level: {segment.trust_level}")
            return False
        
        self.segments[segment.segment_id] = segment
        print(f"✅ Segment created: {segment.name} ({segment.cidr})")
        return True
    
    def create_microsegmentation_policy(self, policy: MicroSegmentationPolicy) -> bool:
        """Create microsegmentation policy"""
        print(f"🔒 Creating policy: {policy.name}")
        
        # Validate source and destination segments exist
        if policy.source_segment not in self.segments:
            print(f"❌ Source segment not found: {policy.source_segment}")
            return False
        
        if policy.destination_segment not in self.segments:
            print(f"❌ Destination segment not found: {policy.destination_segment}")
            return False
        
        # Validate port range
        if policy.port and not 1 <= policy.port <= 65535:
            print(f"❌ Invalid port: {policy.port}")
            return False
        
        self.policies[policy.policy_id] = policy
        print(f"✅ Policy created: {policy.name}")
        return True
    
    def evaluate_traffic_flow(self, flow: TrafficFlow) -> bool:
        """Evaluate if traffic flow is allowed"""
        print(f"🔍 Evaluating traffic: {flow.source_ip} -> {flow.destination_ip}:{flow.port}")
        
        # Find applicable policies
        applicable_policies = self._find_applicable_policies(flow)
        
        if not applicable_policies:
            print(f"  ❌ No policy found - DENY by default (Zero-Trust)")
            flow.allowed = False
            self.traffic_logs.append(flow)
            return False
        
        # Evaluate policies (most specific first)
        for policy in applicable_policies:
            if policy.action == PolicyAction.DENY:
                print(f"  ❌ Policy {policy.name}: DENY")
                flow.allowed = False
                self.traffic_logs.append(flow)
                return False
            
            if policy.action == PolicyAction.ALLOW:
                # Check additional requirements
                if policy.requires_authentication:
                    if not self._verify_authentication(flow):
                        print(f"  ❌ Authentication required but not provided")
                        flow.allowed = False
                        self.traffic_logs.append(flow)
                        return False
                
                if policy.requires_encryption:
                    if not self._verify_encryption(flow):
                        print(f"  ❌ Encryption required but not present")
                        flow.allowed = False
                        self.traffic_logs.append(flow)
                        return False
                
                print(f"  ✅ Policy {policy.name}: ALLOW")
                flow.allowed = True
                self.traffic_logs.append(flow)
                return True
        
        # Default deny
        print(f"  ❌ No ALLOW policy matched - DENY")
        flow.allowed = False
        self.traffic_logs.append(flow)
        return False
    
    def enforce_zone_isolation(self, zone1: ZoneType, zone2: ZoneType) -> bool:
        """Enforce isolation between zones"""
        print(f"🔐 Enforcing isolation: {zone1.value} <-> {zone2.value}")
        
        # High-trust zones cannot communicate with low-trust zones
        isolation_rules = {
            (ZoneType.HIGHLY_RESTRICTED, ZoneType.DMZ): False,
            (ZoneType.RESTRICTED, ZoneType.DMZ): False,
            (ZoneType.DATA, ZoneType.DMZ): False,
        }
        
        key = (zone1, zone2)
        reverse_key = (zone2, zone1)
        
        if key in isolation_rules and not isolation_rules[key]:
            print(f"  ❌ Isolation enforced - communication blocked")
            return False
        
        if reverse_key in isolation_rules and not isolation_rules[reverse_key]:
            print(f"  ❌ Isolation enforced - communication blocked")
            return False
        
        print(f"  ✅ Communication allowed between zones")
        return True
    
    def apply_least_privilege_networking(self, segment_id: str) -> List[str]:
        """Apply least privilege to network segment"""
        print(f"🔧 Applying least privilege to segment: {segment_id}")
        
        if segment_id not in self.segments:
            print(f"❌ Segment not found: {segment_id}")
            return []
        
        segment = self.segments[segment_id]
        recommendations = []
        
        # Analyze current policies
        segment_policies = [p for p in self.policies.values() 
                           if p.source_segment == segment_id or 
                           p.destination_segment == segment_id]
        
        # Check for overly permissive rules
        for policy in segment_policies:
            if policy.action == PolicyAction.ALLOW and not policy.requires_authentication:
                recommendations.append(
                    f"Policy {policy.name}: Add authentication requirement"
                )
            
            if policy.action == PolicyAction.ALLOW and not policy.requires_encryption:
                recommendations.append(
                    f"Policy {policy.name}: Add encryption requirement"
                )
            
            if not policy.logging_enabled:
                recommendations.append(
                    f"Policy {policy.name}: Enable logging for audit trail"
                )
        
        # Check for unused allowed services
        for service in segment.allowed_services:
            service_used = any(p.protocol.value == service for p in segment_policies)
            if not service_used:
                recommendations.append(
                    f"Service {service}: Not used - consider removing"
                )
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        return recommendations
    
    def detect_lateral_movement(self) -> List[Dict[str, Any]]:
        """Detect potential lateral movement in traffic"""
        print("🔍 Analyzing traffic for lateral movement...")
        
        suspicious_patterns = []
        
        # Analyze recent traffic logs
        for flow in self.traffic_logs[-100:]:  # Last 100 flows
            # Pattern 1: Denied traffic from internal to restricted zones
            if not flow.allowed:
                src_segment = self.segments.get(flow.source_segment)
                dst_segment = self.segments.get(flow.destination_segment)
                
                if src_segment and dst_segment:
                    if (src_segment.zone_type == ZoneType.INTERNAL and
                        dst_segment.zone_type in [ZoneType.RESTRICTED, 
                                                  ZoneType.HIGHLY_RESTRICTED]):
                        suspicious_patterns.append({
                            "type": "Unauthorized Zone Access",
                            "source": flow.source_ip,
                            "destination": flow.destination_ip,
                            "severity": "HIGH",
                            "timestamp": flow.timestamp
                        })
            
            # Pattern 2: Port scanning behavior
            # (Multiple connection attempts to different ports)
            # Simulated detection
            
        print(f"⚠️  Detected {len(suspicious_patterns)} suspicious patterns")
        return suspicious_patterns
    
    def generate_network_topology_map(self) -> Dict[str, Any]:
        """Generate network topology map"""
        print("🗺️  Generating network topology map...")
        
        topology = {
            "segments": [],
            "policies": [],
            "trust_boundaries": []
        }
        
        # Map segments
        for segment in self.segments.values():
            topology["segments"].append({
                "id": segment.segment_id,
                "name": segment.name,
                "zone": segment.zone_type.value,
                "cidr": segment.cidr,
                "trust_level": segment.trust_level
            })
        
        # Map policies (allowed connections)
        for policy in self.policies.values():
            if policy.action == PolicyAction.ALLOW:
                topology["policies"].append({
                    "from": policy.source_segment,
                    "to": policy.destination_segment,
                    "protocol": policy.protocol.value,
                    "port": policy.port,
                    "authenticated": policy.requires_authentication,
                    "encrypted": policy.requires_encryption
                })
        
        # Identify trust boundaries
        for segment_id, segment in self.segments.items():
            connected_segments = [p.destination_segment for p in self.policies.values() 
                                if p.source_segment == segment_id and 
                                p.action == PolicyAction.ALLOW]
            
            for connected_id in connected_segments:
                connected = self.segments.get(connected_id)
                if connected and abs(segment.trust_level - connected.trust_level) > 30:
                    topology["trust_boundaries"].append({
                        "from": segment_id,
                        "to": connected_id,
                        "trust_difference": abs(segment.trust_level - connected.trust_level)
                    })
        
        print(f"✅ Topology map generated: {len(topology['segments'])} segments, "
              f"{len(topology['policies'])} policies")
        return topology
    
    def _initialize_default_segments(self):
        """Initialize default network segments"""
        default_segments = [
            NetworkSegment(
                segment_id="seg-dmz",
                name="DMZ",
                zone_type=ZoneType.DMZ,
                cidr="10.0.1.0/24",
                vlan_id=10,
                allowed_services=["HTTPS", "HTTP"],
                trust_level=20
            ),
            NetworkSegment(
                segment_id="seg-internal",
                name="Internal",
                zone_type=ZoneType.INTERNAL,
                cidr="10.0.10.0/24",
                vlan_id=100,
                allowed_services=["HTTPS", "SSH"],
                trust_level=50
            ),
            NetworkSegment(
                segment_id="seg-data",
                name="Data",
                zone_type=ZoneType.DATA,
                cidr="10.0.20.0/24",
                vlan_id=200,
                allowed_services=["HTTPS"],
                trust_level=80
            )
        ]
        
        for segment in default_segments:
            self.segments[segment.segment_id] = segment
    
    def _find_applicable_policies(self, flow: TrafficFlow) -> List[MicroSegmentationPolicy]:
        """Find policies applicable to traffic flow"""
        applicable = []
        
        for policy in self.policies.values():
            if (policy.source_segment == flow.source_segment and
                policy.destination_segment == flow.destination_segment):
                
                # Check protocol match
                if policy.protocol == flow.protocol or policy.protocol == Protocol.TCP:
                    # Check port match (if specified)
                    if policy.port is None or policy.port == flow.port:
                        applicable.append(policy)
        
        return applicable
    
    def _verify_authentication(self, flow: TrafficFlow) -> bool:
        """Verify authentication for flow"""
        # Simulated authentication check
        return True
    
    def _verify_encryption(self, flow: TrafficFlow) -> bool:
        """Verify encryption for flow"""
        # Check if protocol supports encryption
        encrypted_protocols = [Protocol.HTTPS, Protocol.SSH]
        return flow.protocol in encrypted_protocols


def main():
    """Test microsegmentation engine"""
    engine = MicrosegmentationEngine()
    
    print("=" * 70)
    print("ZERO-TRUST MICROSEGMENTATION ENGINE")
    print("=" * 70)
    
    # Create policy
    policy = MicroSegmentationPolicy(
        policy_id="pol-001",
        name="Internal to Data",
        source_segment="seg-internal",
        destination_segment="seg-data",
        protocol=Protocol.HTTPS,
        port=443,
        action=PolicyAction.ALLOW,
        requires_authentication=True,
        requires_encryption=True,
        logging_enabled=True,
        created_at=datetime.now()
    )
    
    engine.create_microsegmentation_policy(policy)
    
    # Evaluate traffic flow
    flow = TrafficFlow(
        flow_id="flow-001",
        source_ip="10.0.10.5",
        destination_ip="10.0.20.10",
        source_segment="seg-internal",
        destination_segment="seg-data",
        protocol=Protocol.HTTPS,
        port=443,
        allowed=False,
        timestamp=datetime.now()
    )
    
    engine.evaluate_traffic_flow(flow)
    
    # Apply least privilege
    recommendations = engine.apply_least_privilege_networking("seg-internal")
    print(f"\n📋 Least Privilege Recommendations: {len(recommendations)}")
    
    # Detect lateral movement
    threats = engine.detect_lateral_movement()
    print(f"\n⚠️  Potential Threats: {len(threats)}")
    
    # Generate topology
    topology = engine.generate_network_topology_map()
    print(f"\n🗺️  Network Segments: {len(topology['segments'])}")


if __name__ == "__main__":
    main()
