"""
Military-Grade Advanced Visualization & Analytics - Part 2 of 4
===============================================================

Geospatial Threat Maps & MITRE ATT&CK Navigator Integration

Features:
- Interactive threat world maps
- Attack origin geolocation
- MITRE ATT&CK technique heatmap
- Coverage gap visualization
- Real-time threat tracking

TECHNOLOGY:
- Leaflet.js / Mapbox for maps
- MITRE ATT&CK Navigator integration
- GeoJSON data format
- IP geolocation databases
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


class ThreatSeverity(Enum):
    """Threat severity for map visualization"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


class AttackPhase(Enum):
    """MITRE ATT&CK attack phases"""
    RECONNAISSANCE = "Reconnaissance"
    INITIAL_ACCESS = "Initial Access"
    EXECUTION = "Execution"
    PERSISTENCE = "Persistence"
    PRIVILEGE_ESCALATION = "Privilege Escalation"
    DEFENSE_EVASION = "Defense Evasion"
    CREDENTIAL_ACCESS = "Credential Access"
    DISCOVERY = "Discovery"
    LATERAL_MOVEMENT = "Lateral Movement"
    COLLECTION = "Collection"
    EXFILTRATION = "Exfiltration"
    IMPACT = "Impact"


@dataclass
class GeoLocation:
    """Geographic location"""
    latitude: float
    longitude: float
    country: str
    city: str
    asn: Optional[str] = None


@dataclass
class ThreatMarker:
    """Threat marker on map"""
    marker_id: str
    location: GeoLocation
    severity: ThreatSeverity
    threat_type: str
    source_ip: str
    timestamp: datetime
    description: str


@dataclass
class ATTACKTechniqueCoverage:
    """MITRE ATT&CK technique coverage"""
    technique_id: str
    technique_name: str
    tactic: str
    detection_coverage: int  # 0-100%
    prevention_coverage: int  # 0-100%
    detections_count: int


@dataclass
class NavigatorLayer:
    """MITRE ATT&CK Navigator layer"""
    name: str
    description: str
    domain: str  # enterprise, mobile, ics
    version: str
    techniques: List[Dict[str, Any]]


class GeospatialThreatEngine:
    """Geospatial Threat Mapping Engine - Part 2"""
    
    def __init__(self):
        self.threat_markers: List[ThreatMarker] = []
        self.attack_coverage: List[ATTACKTechniqueCoverage] = []
        self._initialize_attack_coverage()
    
    def add_threat_marker(self, source_ip: str, severity: ThreatSeverity,
                         threat_type: str, description: str) -> ThreatMarker:
        """Add threat marker to map"""
        print(f"📍 Adding threat marker: {source_ip}")
        
        # Geolocate IP
        location = self._geolocate_ip(source_ip)
        
        marker = ThreatMarker(
            marker_id=f"MARKER-{len(self.threat_markers) + 1:06d}",
            location=location,
            severity=severity,
            threat_type=threat_type,
            source_ip=source_ip,
            timestamp=datetime.now(),
            description=description
        )
        
        self.threat_markers.append(marker)
        
        print(f"✅ Threat marker added: {location.country}")
        return marker
    
    def generate_threat_heatmap(self) -> Dict[str, Any]:
        """Generate global threat heatmap data"""
        print("🗺️ Generating threat heatmap...")
        
        # Aggregate threats by country
        country_counts = {}
        for marker in self.threat_markers:
            country = marker.location.country
            country_counts[country] = country_counts.get(country, 0) + 1
        
        # Generate heatmap data
        heatmap_data = []
        for country, count in country_counts.items():
            # Get country center coordinates (simplified)
            lat, lon = self._get_country_center(country)
            heatmap_data.append({
                "lat": lat,
                "lon": lon,
                "intensity": count,
                "country": country
            })
        
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [point["lon"], point["lat"]]
                    },
                    "properties": {
                        "intensity": point["intensity"],
                        "country": point["country"]
                    }
                }
                for point in heatmap_data
            ]
        }
    
    def generate_attack_flow_map(self, attack_campaign: str) -> Dict[str, Any]:
        """Generate attack flow visualization"""
        print(f"🎯 Generating attack flow map for: {attack_campaign}")
        
        # Simulate attack flow: Origin -> Target
        flows = [
            {
                "source": {"lat": 55.7558, "lon": 37.6173, "country": "Russia"},
                "target": {"lat": 38.9072, "lon": -77.0369, "country": "USA"},
                "attack_type": "Spear Phishing",
                "severity": "HIGH"
            },
            {
                "source": {"lat": 39.9042, "lon": 116.4074, "country": "China"},
                "target": {"lat": 51.5074, "lon": -0.1278, "country": "UK"},
                "attack_type": "Supply Chain",
                "severity": "CRITICAL"
            }
        ]
        
        return {
            "campaign": attack_campaign,
            "flows": flows,
            "total_attacks": len(flows)
        }
    
    def generate_attack_navigator_layer(self, layer_name: str) -> NavigatorLayer:
        """Generate MITRE ATT&CK Navigator layer"""
        print(f"🧭 Generating ATT&CK Navigator layer: {layer_name}")
        
        techniques = []
        
        for coverage in self.attack_coverage:
            # Color based on coverage
            if coverage.detection_coverage >= 75:
                color = "#00ff00"  # Green - good coverage
            elif coverage.detection_coverage >= 50:
                color = "#ffff00"  # Yellow - moderate coverage
            elif coverage.detection_coverage >= 25:
                color = "#ff9900"  # Orange - low coverage
            else:
                color = "#ff0000"  # Red - poor coverage
            
            techniques.append({
                "techniqueID": coverage.technique_id,
                "tactic": coverage.tactic,
                "color": color,
                "score": coverage.detection_coverage,
                "comment": f"Detection: {coverage.detection_coverage}%, "
                          f"Prevention: {coverage.prevention_coverage}%"
            })
        
        layer = NavigatorLayer(
            name=layer_name,
            description="Detection and prevention coverage heatmap",
            domain="enterprise-attack",
            version="13.1",
            techniques=techniques
        )
        
        print(f"✅ Navigator layer created with {len(techniques)} techniques")
        return layer
    
    def export_navigator_json(self, layer: NavigatorLayer) -> str:
        """Export Navigator layer as JSON"""
        navigator_json = {
            "name": layer.name,
            "versions": {
                "attack": layer.version,
                "navigator": "4.9.1",
                "layer": "4.5"
            },
            "domain": layer.domain,
            "description": layer.description,
            "techniques": layer.techniques,
            "gradient": {
                "colors": ["#ff0000", "#ffff00", "#00ff00"],
                "minValue": 0,
                "maxValue": 100
            }
        }
        
        return json.dumps(navigator_json, indent=2)
    
    def identify_coverage_gaps(self) -> List[str]:
        """Identify MITRE ATT&CK coverage gaps"""
        print("🔍 Identifying coverage gaps...")
        
        gaps = []
        
        for coverage in self.attack_coverage:
            if coverage.detection_coverage < 50 or coverage.prevention_coverage < 50:
                gaps.append(
                    f"{coverage.technique_id} {coverage.technique_name} - "
                    f"Detection: {coverage.detection_coverage}%, "
                    f"Prevention: {coverage.prevention_coverage}%"
                )
        
        print(f"⚠️ Found {len(gaps)} coverage gaps")
        return gaps
    
    def _geolocate_ip(self, ip: str) -> GeoLocation:
        """Geolocate IP address (simulated)"""
        # In production, use MaxMind GeoIP2 or similar service
        ip_geo_db = {
            "192.168.1.1": GeoLocation(55.7558, 37.6173, "Russia", "Moscow", "AS12345"),
            "10.0.0.1": GeoLocation(39.9042, 116.4074, "China", "Beijing", "AS23456"),
            "172.16.0.1": GeoLocation(37.7749, -122.4194, "USA", "San Francisco", "AS34567")
        }
        
        # Default to USA if not found
        return ip_geo_db.get(ip, GeoLocation(38.9072, -77.0369, "USA", "Washington DC", None))
    
    def _get_country_center(self, country: str) -> Tuple[float, float]:
        """Get country center coordinates"""
        centers = {
            "USA": (38.9072, -77.0369),
            "Russia": (55.7558, 37.6173),
            "China": (39.9042, 116.4074),
            "UK": (51.5074, -0.1278),
            "Germany": (52.5200, 13.4050)
        }
        return centers.get(country, (0.0, 0.0))
    
    def _initialize_attack_coverage(self):
        """Initialize ATT&CK coverage data"""
        self.attack_coverage = [
            ATTACKTechniqueCoverage(
                technique_id="T1566",
                technique_name="Phishing",
                tactic="Initial Access",
                detection_coverage=85,
                prevention_coverage=75,
                detections_count=12
            ),
            ATTACKTechniqueCoverage(
                technique_id="T1078",
                technique_name="Valid Accounts",
                tactic="Initial Access",
                detection_coverage=65,
                prevention_coverage=50,
                detections_count=8
            ),
            ATTACKTechniqueCoverage(
                technique_id="T1059",
                technique_name="Command and Scripting Interpreter",
                tactic="Execution",
                detection_coverage=70,
                prevention_coverage=60,
                detections_count=15
            ),
            ATTACKTechniqueCoverage(
                technique_id="T1003",
                technique_name="OS Credential Dumping",
                tactic="Credential Access",
                detection_coverage=45,
                prevention_coverage=30,
                detections_count=5
            ),
            ATTACKTechniqueCoverage(
                technique_id="T1486",
                technique_name="Data Encrypted for Impact",
                tactic="Impact",
                detection_coverage=55,
                prevention_coverage=40,
                detections_count=7
            )
        ]


def main():
    """Test geospatial threat engine"""
    engine = GeospatialThreatEngine()
    
    # Add threat markers
    engine.add_threat_marker(
        source_ip="192.168.1.1",
        severity=ThreatSeverity.CRITICAL,
        threat_type="APT Activity",
        description="Suspected APT28 reconnaissance"
    )
    
    engine.add_threat_marker(
        source_ip="10.0.0.1",
        severity=ThreatSeverity.HIGH,
        threat_type="Malware C2",
        description="Command and control communication detected"
    )
    
    # Generate threat heatmap
    heatmap = engine.generate_threat_heatmap()
    print(f"Heatmap features: {len(heatmap['features'])}")
    
    # Generate attack flow map
    flow_map = engine.generate_attack_flow_map("SolarWinds Campaign")
    print(f"Attack flows: {flow_map['total_attacks']}")
    
    # Generate ATT&CK Navigator layer
    layer = engine.generate_attack_navigator_layer("Detection Coverage 2024")
    print(f"Navigator techniques: {len(layer.techniques)}")
    
    # Identify coverage gaps
    gaps = engine.identify_coverage_gaps()
    print(f"Coverage gaps: {len(gaps)}")


if __name__ == "__main__":
    main()
