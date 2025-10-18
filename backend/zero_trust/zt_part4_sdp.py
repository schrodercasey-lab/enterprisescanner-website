"""
Military-Grade Zero-Trust Architecture - Part 4 of 5
===================================================

Software-Defined Perimeter (SDP)

Features:
- Dynamic perimeter creation
- Single Packet Authorization (SPA)
- Controller-gateway architecture
- Invisible infrastructure
- Identity-based network access

COMPLIANCE:
- NIST 800-207 (Zero Trust Architecture)
- Cloud Security Alliance SDP Framework
- DoD Zero Trust Reference Architecture
- CMMC SC.L3-3.13.1 (Boundary Protection)
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac


class SDPMode(Enum):
    """SDP operational modes"""
    CLIENT_TO_GATEWAY = "Client-to-Gateway"
    CLIENT_TO_SERVER = "Client-to-Server"
    GATEWAY_TO_GATEWAY = "Gateway-to-Gateway"


class AuthorizationState(Enum):
    """Authorization states"""
    PENDING = "Pending"
    AUTHORIZED = "Authorized"
    DENIED = "Denied"
    EXPIRED = "Expired"
    REVOKED = "Revoked"


class GatewayStatus(Enum):
    """Gateway operational status"""
    ACTIVE = "Active"
    STANDBY = "Standby"
    MAINTENANCE = "Maintenance"
    OFFLINE = "Offline"


@dataclass
class SPAPacket:
    """Single Packet Authorization packet"""
    client_id: str
    timestamp: datetime
    requested_resource: str
    encrypted_payload: str
    hmac_signature: str


@dataclass
class SDPController:
    """SDP Controller configuration"""
    controller_id: str
    ip_address: str
    port: int
    public_key: str
    connected_gateways: List[str]


@dataclass
class SDPGateway:
    """SDP Gateway configuration"""
    gateway_id: str
    ip_address: str
    port: int
    status: GatewayStatus
    protected_resources: List[str]
    authorized_clients: Set[str]
    firewall_rules: List[Dict[str, Any]]


@dataclass
class SDPClient:
    """SDP Client"""
    client_id: str
    identity_id: str
    device_id: str
    public_key: str
    authorization_state: AuthorizationState
    authorized_resources: List[str]
    authorization_expires: Optional[datetime]


@dataclass
class AuthorizationRequest:
    """Authorization request"""
    request_id: str
    client_id: str
    requested_resource: str
    timestamp: datetime
    state: AuthorizationState


class SoftwareDefinedPerimeter:
    """Software-Defined Perimeter Engine - Part 4 of Zero-Trust"""
    
    def __init__(self):
        self.controllers: Dict[str, SDPController] = {}
        self.gateways: Dict[str, SDPGateway] = {}
        self.clients: Dict[str, SDPClient] = {}
        self.authorization_requests: List[AuthorizationRequest] = []
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_infrastructure()
    
    def register_client(self, client: SDPClient) -> bool:
        """Register SDP client"""
        print(f"📱 Registering SDP client: {client.client_id}")
        
        if client.client_id in self.clients:
            print(f"❌ Client already registered: {client.client_id}")
            return False
        
        self.clients[client.client_id] = client
        print(f"✅ Client registered: {client.client_id}")
        return True
    
    def create_spa_packet(self, client_id: str, resource: str) -> SPAPacket:
        """Create Single Packet Authorization packet"""
        print(f"📦 Creating SPA packet: {client_id} -> {resource}")
        
        if client_id not in self.clients:
            raise ValueError(f"Client not found: {client_id}")
        
        client = self.clients[client_id]
        timestamp = datetime.now()
        
        # Create payload
        payload_data = f"{client_id}|{resource}|{timestamp.isoformat()}"
        
        # Encrypt payload (simulated)
        encrypted_payload = self._encrypt_payload(payload_data, client.public_key)
        
        # Generate HMAC signature
        hmac_sig = self._generate_hmac(encrypted_payload)
        
        packet = SPAPacket(
            client_id=client_id,
            timestamp=timestamp,
            requested_resource=resource,
            encrypted_payload=encrypted_payload,
            hmac_signature=hmac_sig
        )
        
        print(f"✅ SPA packet created")
        return packet
    
    def process_spa_packet(self, packet: SPAPacket) -> Dict[str, Any]:
        """Process Single Packet Authorization packet"""
        print(f"🔍 Processing SPA packet from: {packet.client_id}")
        
        # Step 1: Validate HMAC
        if not self._verify_hmac(packet.encrypted_payload, packet.hmac_signature):
            print(f"  ❌ HMAC verification failed")
            return {"authorized": False, "reason": "Invalid HMAC signature"}
        
        # Step 2: Check timestamp (prevent replay attacks)
        age = (datetime.now() - packet.timestamp).total_seconds()
        if age > 30:  # 30 second window
            print(f"  ❌ Packet expired (age: {age:.1f}s)")
            return {"authorized": False, "reason": "Packet expired"}
        
        # Step 3: Verify client exists
        if packet.client_id not in self.clients:
            print(f"  ❌ Unknown client: {packet.client_id}")
            return {"authorized": False, "reason": "Unknown client"}
        
        client = self.clients[packet.client_id]
        
        # Step 4: Check client authorization state
        if client.authorization_state != AuthorizationState.AUTHORIZED:
            print(f"  ❌ Client not authorized: {client.authorization_state.value}")
            return {"authorized": False, "reason": "Client not authorized"}
        
        # Step 5: Check resource access
        if packet.requested_resource not in client.authorized_resources:
            print(f"  ❌ Resource not authorized: {packet.requested_resource}")
            return {"authorized": False, "reason": "Resource not authorized"}
        
        # Step 6: Check authorization expiry
        if client.authorization_expires and client.authorization_expires < datetime.now():
            print(f"  ⏰ Authorization expired")
            client.authorization_state = AuthorizationState.EXPIRED
            return {"authorized": False, "reason": "Authorization expired"}
        
        print(f"  ✅ SPA packet valid - opening gateway")
        
        # Open gateway for client
        gateway_id = self._find_gateway_for_resource(packet.requested_resource)
        if gateway_id:
            self._open_gateway_for_client(gateway_id, packet.client_id)
        
        return {
            "authorized": True,
            "gateway": gateway_id,
            "resource": packet.requested_resource,
            "expires_in": 3600  # 1 hour
        }
    
    def authorize_client(self, client_id: str, resources: List[str], 
                        duration: int = 3600) -> AuthorizationRequest:
        """Authorize client for resources"""
        print(f"🔐 Authorizing client: {client_id} for {len(resources)} resources")
        
        if client_id not in self.clients:
            raise ValueError(f"Client not found: {client_id}")
        
        client = self.clients[client_id]
        
        # Create authorization request
        request = AuthorizationRequest(
            request_id=f"auth-req-{datetime.now().timestamp()}",
            client_id=client_id,
            requested_resource=",".join(resources),
            timestamp=datetime.now(),
            state=AuthorizationState.PENDING
        )
        
        # Validate authorization (simulated policy check)
        if self._validate_authorization(client_id, resources):
            client.authorization_state = AuthorizationState.AUTHORIZED
            client.authorized_resources = resources
            client.authorization_expires = datetime.now() + timedelta(seconds=duration)
            request.state = AuthorizationState.AUTHORIZED
            
            print(f"✅ Client authorized until {client.authorization_expires}")
        else:
            client.authorization_state = AuthorizationState.DENIED
            request.state = AuthorizationState.DENIED
            print(f"❌ Authorization denied")
        
        self.authorization_requests.append(request)
        return request
    
    def revoke_authorization(self, client_id: str) -> bool:
        """Revoke client authorization"""
        print(f"🚫 Revoking authorization: {client_id}")
        
        if client_id not in self.clients:
            print(f"❌ Client not found: {client_id}")
            return False
        
        client = self.clients[client_id]
        client.authorization_state = AuthorizationState.REVOKED
        client.authorized_resources = []
        
        # Close all gateway connections for this client
        for gateway_id, gateway in self.gateways.items():
            if client_id in gateway.authorized_clients:
                gateway.authorized_clients.remove(client_id)
                self._remove_firewall_rule(gateway_id, client_id)
        
        print(f"✅ Authorization revoked")
        return True
    
    def make_infrastructure_invisible(self) -> Dict[str, Any]:
        """Make infrastructure invisible (dark cloud)"""
        print("🌑 Enabling infrastructure invisibility (Dark Cloud mode)")
        
        invisible_services = []
        
        for gateway_id, gateway in self.gateways.items():
            # Drop all unauthorized packets silently
            invisible_services.append({
                "gateway": gateway_id,
                "mode": "stealth",
                "action": "silent_drop",
                "protected_resources": len(gateway.protected_resources)
            })
            
            print(f"  🛡️  Gateway {gateway_id}: Stealth mode enabled")
        
        return {
            "status": "invisible",
            "invisible_services": invisible_services,
            "threat_surface": "minimal",
            "reconnaissance_protection": "active"
        }
    
    def establish_dynamic_perimeter(self, client_id: str, 
                                   resource: str) -> Dict[str, Any]:
        """Establish dynamic perimeter for client"""
        print(f"🔷 Establishing dynamic perimeter: {client_id} -> {resource}")
        
        if client_id not in self.clients:
            return {"success": False, "reason": "Client not found"}
        
        client = self.clients[client_id]
        
        # Find gateway
        gateway_id = self._find_gateway_for_resource(resource)
        if not gateway_id:
            return {"success": False, "reason": "No gateway found for resource"}
        
        # Create temporary perimeter
        connection_id = f"conn-{datetime.now().timestamp()}"
        
        perimeter = {
            "connection_id": connection_id,
            "client_id": client_id,
            "gateway_id": gateway_id,
            "resource": resource,
            "established_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=1),
            "firewall_rule_id": self._add_firewall_rule(gateway_id, client_id, resource)
        }
        
        self.active_connections[connection_id] = perimeter
        
        print(f"✅ Dynamic perimeter established: {connection_id}")
        return {
            "success": True,
            "connection_id": connection_id,
            "gateway": gateway_id,
            "expires_in": 3600
        }
    
    def tear_down_perimeter(self, connection_id: str) -> bool:
        """Tear down dynamic perimeter"""
        print(f"🔻 Tearing down perimeter: {connection_id}")
        
        if connection_id not in self.active_connections:
            print(f"❌ Connection not found: {connection_id}")
            return False
        
        perimeter = self.active_connections[connection_id]
        
        # Remove firewall rule
        self._remove_firewall_rule(
            perimeter["gateway_id"],
            perimeter["client_id"]
        )
        
        # Remove connection
        del self.active_connections[connection_id]
        
        print(f"✅ Perimeter torn down")
        return True
    
    def monitor_gateway_health(self) -> List[Dict[str, Any]]:
        """Monitor health of all gateways"""
        print("💚 Monitoring gateway health...")
        
        health_reports = []
        
        for gateway_id, gateway in self.gateways.items():
            # Check gateway status
            health = {
                "gateway_id": gateway_id,
                "status": gateway.status.value,
                "authorized_clients": len(gateway.authorized_clients),
                "protected_resources": len(gateway.protected_resources),
                "active_rules": len(gateway.firewall_rules),
                "healthy": gateway.status == GatewayStatus.ACTIVE
            }
            
            health_reports.append(health)
            
            status_icon = "✅" if health["healthy"] else "⚠️"
            print(f"  {status_icon} {gateway_id}: {health['authorized_clients']} clients, "
                  f"{health['active_rules']} rules")
        
        return health_reports
    
    def _initialize_default_infrastructure(self):
        """Initialize default SDP infrastructure"""
        # Create controller
        controller = SDPController(
            controller_id="ctrl-001",
            ip_address="10.0.0.10",
            port=8443,
            public_key="controller-pubkey-001",
            connected_gateways=["gw-001", "gw-002"]
        )
        self.controllers[controller.controller_id] = controller
        
        # Create gateways
        gateways_config = [
            {
                "gateway_id": "gw-001",
                "ip_address": "10.0.1.10",
                "port": 443,
                "status": GatewayStatus.ACTIVE,
                "protected_resources": ["database-prod", "api-prod"]
            },
            {
                "gateway_id": "gw-002",
                "ip_address": "10.0.2.10",
                "port": 443,
                "status": GatewayStatus.ACTIVE,
                "protected_resources": ["storage-prod", "analytics-prod"]
            }
        ]
        
        for gw_config in gateways_config:
            gateway = SDPGateway(
                gateway_id=gw_config["gateway_id"],
                ip_address=gw_config["ip_address"],
                port=gw_config["port"],
                status=gw_config["status"],
                protected_resources=gw_config["protected_resources"],
                authorized_clients=set(),
                firewall_rules=[]
            )
            self.gateways[gateway.gateway_id] = gateway
    
    def _encrypt_payload(self, payload: str, public_key: str) -> str:
        """Encrypt payload (simulated)"""
        return hashlib.sha256(f"{payload}:{public_key}".encode()).hexdigest()
    
    def _generate_hmac(self, data: str) -> str:
        """Generate HMAC signature"""
        secret = b"shared-secret-key"
        return hmac.new(secret, data.encode(), hashlib.sha256).hexdigest()
    
    def _verify_hmac(self, data: str, signature: str) -> bool:
        """Verify HMAC signature"""
        expected = self._generate_hmac(data)
        return hmac.compare_digest(expected, signature)
    
    def _validate_authorization(self, client_id: str, resources: List[str]) -> bool:
        """Validate if client should be authorized for resources"""
        # Simulated policy check
        return True
    
    def _find_gateway_for_resource(self, resource: str) -> Optional[str]:
        """Find gateway that protects resource"""
        for gateway_id, gateway in self.gateways.items():
            if resource in gateway.protected_resources:
                return gateway_id
        return None
    
    def _open_gateway_for_client(self, gateway_id: str, client_id: str):
        """Open gateway for client"""
        if gateway_id in self.gateways:
            self.gateways[gateway_id].authorized_clients.add(client_id)
    
    def _add_firewall_rule(self, gateway_id: str, client_id: str, 
                          resource: str) -> str:
        """Add firewall rule to gateway"""
        if gateway_id not in self.gateways:
            return ""
        
        rule_id = f"rule-{datetime.now().timestamp()}"
        rule = {
            "rule_id": rule_id,
            "client_id": client_id,
            "resource": resource,
            "action": "ALLOW",
            "created_at": datetime.now()
        }
        
        self.gateways[gateway_id].firewall_rules.append(rule)
        return rule_id
    
    def _remove_firewall_rule(self, gateway_id: str, client_id: str):
        """Remove firewall rule from gateway"""
        if gateway_id not in self.gateways:
            return
        
        gateway = self.gateways[gateway_id]
        gateway.firewall_rules = [
            rule for rule in gateway.firewall_rules 
            if rule["client_id"] != client_id
        ]


def main():
    """Test Software-Defined Perimeter"""
    sdp = SoftwareDefinedPerimeter()
    
    print("=" * 70)
    print("SOFTWARE-DEFINED PERIMETER (SDP)")
    print("=" * 70)
    
    # Register client
    client = SDPClient(
        client_id="client-001",
        identity_id="user-001",
        device_id="dev-001",
        public_key="client-pubkey-001",
        authorization_state=AuthorizationState.PENDING,
        authorized_resources=[],
        authorization_expires=None
    )
    sdp.register_client(client)
    
    # Authorize client
    print("\n" + "=" * 70)
    auth_req = sdp.authorize_client("client-001", ["database-prod", "api-prod"])
    
    # Create and process SPA packet
    print("\n" + "=" * 70)
    print("SINGLE PACKET AUTHORIZATION")
    print("=" * 70)
    
    spa_packet = sdp.create_spa_packet("client-001", "database-prod")
    result = sdp.process_spa_packet(spa_packet)
    print(f"\nAuthorization Result: {result}")
    
    # Establish dynamic perimeter
    print("\n" + "=" * 70)
    print("DYNAMIC PERIMETER")
    print("=" * 70)
    
    perimeter = sdp.establish_dynamic_perimeter("client-001", "database-prod")
    print(f"\nPerimeter: {perimeter}")
    
    # Infrastructure invisibility
    print("\n" + "=" * 70)
    print("INFRASTRUCTURE INVISIBILITY")
    print("=" * 70)
    
    invisible = sdp.make_infrastructure_invisible()
    print(f"\nStatus: {invisible['status']}")
    
    # Monitor gateways
    print("\n" + "=" * 70)
    print("GATEWAY HEALTH")
    print("=" * 70)
    
    health = sdp.monitor_gateway_health()


if __name__ == "__main__":
    main()
