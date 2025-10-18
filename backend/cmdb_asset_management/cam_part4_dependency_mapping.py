"""
Military Upgrade #26: CMDB & Asset Management
Part 4: Dependency Mapping and Visualization

This module implements comprehensive dependency mapping, service
topology visualization, and blast radius analysis.

Key Features:
- Automatic dependency discovery
- Service topology mapping
- Blast radius calculation
- Circular dependency detection
- Critical path identification

Use Cases:
- Change impact assessment
- Incident root cause analysis
- Service restoration prioritization
- Architecture optimization

Compliance:
- ITIL v4 Service Management
- NIST 800-53 CM-8 (Component Inventory)
- Site Reliability Engineering (SRE) best practices
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class DependencyType(Enum):
    """Dependency relationship types"""
    HARD = "hard"  # Critical dependency - failure causes cascade
    SOFT = "soft"  # Non-critical - degraded but functional
    OPTIONAL = "optional"  # Can function without


@dataclass
class Dependency:
    """Dependency relationship"""
    source_id: str
    target_id: str
    dependency_type: DependencyType
    
    source_name: str = ""
    target_name: str = ""
    
    # Characteristics
    bidirectional: bool = False
    latency_sensitive: bool = False
    
    # Discovery
    discovered_at: datetime = field(default_factory=datetime.now)
    discovery_method: str = "manual"  # manual, auto, network_trace
    
    # Health
    last_verified: Optional[datetime] = None
    health_check_enabled: bool = True


@dataclass
class ServiceTopology:
    """Service topology graph"""
    service_id: str
    service_name: str
    
    dependencies: List[Dependency] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)  # CIs that depend on this
    
    # Topology metrics
    depth: int = 0  # Distance from root
    criticality_score: float = 0.0
    
    # Path information
    critical_path: bool = False


@dataclass
class BlastRadius:
    """Blast radius analysis result"""
    source_id: str
    source_name: str
    
    directly_impacted: List[str] = field(default_factory=list)
    indirectly_impacted: List[str] = field(default_factory=list)
    total_impacted: int = 0
    
    affected_services: List[str] = field(default_factory=list)
    affected_users_estimate: int = 0
    
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL


class DependencyMapper:
    """Dependency mapping and visualization engine"""
    
    def __init__(self):
        self.dependencies: List[Dependency] = []
        self.topologies: Dict[str, ServiceTopology] = {}
    
    def add_dependency(self, source_id: str, target_id: str,
                      dependency_type: DependencyType,
                      source_name: str = "", target_name: str = "",
                      **kwargs) -> Dependency:
        """Add dependency relationship"""
        dependency = Dependency(
            source_id=source_id,
            target_id=target_id,
            dependency_type=dependency_type,
            source_name=source_name or source_id,
            target_name=target_name or target_id,
            **kwargs
        )
        
        self.dependencies.append(dependency)
        
        print(f"🔗 Dependency added: {source_name} → {target_name} ({dependency_type.value})")
        
        return dependency
    
    def discover_dependencies_from_logs(self, ci_id: str, log_data: List[Dict[str, Any]]) -> List[Dependency]:
        """Automatically discover dependencies from logs"""
        discovered = []
        
        print(f"\n🔍 Discovering dependencies for {ci_id} from logs...")
        
        # Analyze log data for connection patterns
        connection_targets = set()
        for log_entry in log_data:
            # Look for outbound connections
            if 'destination' in log_entry:
                connection_targets.add(log_entry['destination'])
        
        # Create dependency records
        for target in connection_targets:
            dependency = self.add_dependency(
                source_id=ci_id,
                target_id=target,
                dependency_type=DependencyType.SOFT,
                discovery_method="auto"
            )
            discovered.append(dependency)
        
        print(f"   ✅ Discovered {len(discovered)} dependencies")
        
        return discovered
    
    def build_service_topology(self, service_id: str) -> ServiceTopology:
        """Build complete service topology"""
        topology = ServiceTopology(
            service_id=service_id,
            service_name=service_id
        )
        
        # Find all dependencies for this service
        service_deps = [d for d in self.dependencies if d.source_id == service_id]
        topology.dependencies = service_deps
        
        # Find all dependents (reverse dependencies)
        topology.dependents = [
            d.source_id for d in self.dependencies
            if d.target_id == service_id
        ]
        
        # Calculate depth (distance from root)
        topology.depth = self._calculate_depth(service_id, visited=set())
        
        # Calculate criticality score
        topology.criticality_score = self._calculate_criticality(service_id)
        
        self.topologies[service_id] = topology
        
        print(f"\n🗺️ Service topology built: {service_id}")
        print(f"   Dependencies: {len(topology.dependencies)}")
        print(f"   Dependents: {len(topology.dependents)}")
        print(f"   Depth: {topology.depth}")
        print(f"   Criticality: {topology.criticality_score:.2f}")
        
        return topology
    
    def _calculate_depth(self, ci_id: str, visited: Set[str], current_depth: int = 0) -> int:
        """Calculate dependency depth (distance from leaf nodes)"""
        if ci_id in visited:
            return current_depth
        
        visited.add(ci_id)
        
        # Find dependencies
        deps = [d for d in self.dependencies if d.source_id == ci_id]
        
        if not deps:
            return current_depth
        
        # Calculate max depth of dependencies
        max_depth = current_depth
        for dep in deps:
            dep_depth = self._calculate_depth(dep.target_id, visited, current_depth + 1)
            max_depth = max(max_depth, dep_depth)
        
        return max_depth
    
    def _calculate_criticality(self, ci_id: str) -> float:
        """Calculate criticality score based on dependent count"""
        # Count how many other CIs depend on this one
        dependent_count = sum(1 for d in self.dependencies if d.target_id == ci_id)
        
        # Count hard dependencies (more critical)
        hard_dependents = sum(
            1 for d in self.dependencies
            if d.target_id == ci_id and d.dependency_type == DependencyType.HARD
        )
        
        # Score: base + dependents + (hard_dependents * 2)
        score = 10 + (dependent_count * 5) + (hard_dependents * 10)
        
        return min(score, 100)  # Cap at 100
    
    def calculate_blast_radius(self, ci_id: str, failure_type: str = "complete") -> BlastRadius:
        """Calculate blast radius of CI failure"""
        blast = BlastRadius(
            source_id=ci_id,
            source_name=ci_id
        )
        
        print(f"\n💥 Calculating blast radius: {ci_id}")
        
        # Find directly impacted (immediate dependents)
        blast.directly_impacted = [
            d.source_id for d in self.dependencies
            if d.target_id == ci_id
        ]
        
        # Find indirectly impacted (cascade failures)
        blast.indirectly_impacted = self._find_cascade_failures(
            ci_id,
            blast.directly_impacted.copy(),
            visited=set()
        )
        
        blast.total_impacted = len(blast.directly_impacted) + len(blast.indirectly_impacted)
        
        # Determine severity
        if blast.total_impacted >= 10:
            blast.severity = "CRITICAL"
        elif blast.total_impacted >= 5:
            blast.severity = "HIGH"
        elif blast.total_impacted >= 2:
            blast.severity = "MEDIUM"
        else:
            blast.severity = "LOW"
        
        # Estimate affected users (simplified)
        blast.affected_users_estimate = blast.total_impacted * 100
        
        print(f"   Direct impact: {len(blast.directly_impacted)} CIs")
        print(f"   Indirect impact: {len(blast.indirectly_impacted)} CIs")
        print(f"   Total impact: {blast.total_impacted} CIs")
        print(f"   Severity: {blast.severity}")
        
        return blast
    
    def _find_cascade_failures(self, failed_ci: str, already_failed: List[str],
                               visited: Set[str]) -> List[str]:
        """Find CIs that fail due to cascade"""
        if failed_ci in visited:
            return []
        
        visited.add(failed_ci)
        cascade = []
        
        # Find CIs with HARD dependencies on failed CI
        hard_deps = [
            d.source_id for d in self.dependencies
            if d.target_id == failed_ci
            and d.dependency_type == DependencyType.HARD
            and d.source_id not in already_failed
        ]
        
        cascade.extend(hard_deps)
        
        # Recursively find cascades
        for dep_ci in hard_deps:
            sub_cascade = self._find_cascade_failures(
                dep_ci,
                already_failed + cascade,
                visited
            )
            cascade.extend(sub_cascade)
        
        return list(set(cascade))  # Remove duplicates
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains"""
        cycles = []
        
        print(f"\n🔄 Detecting circular dependencies...")
        
        # Get all unique CIs
        all_cis = set()
        for dep in self.dependencies:
            all_cis.add(dep.source_id)
            all_cis.add(dep.target_id)
        
        # Check each CI for cycles
        for ci_id in all_cis:
            cycle = self._find_cycle(ci_id, [ci_id], set())
            if cycle:
                # Normalize cycle representation
                cycle_sorted = tuple(sorted(cycle))
                if cycle_sorted not in [tuple(sorted(c)) for c in cycles]:
                    cycles.append(cycle)
        
        if cycles:
            print(f"   ⚠️ Found {len(cycles)} circular dependencies:")
            for i, cycle in enumerate(cycles, 1):
                print(f"      {i}. {' → '.join(cycle)} → {cycle[0]}")
        else:
            print(f"   ✅ No circular dependencies detected")
        
        return cycles
    
    def _find_cycle(self, current_ci: str, path: List[str], visited: Set[str]) -> Optional[List[str]]:
        """Find cycle starting from current CI"""
        if current_ci in visited:
            return None
        
        visited.add(current_ci)
        
        # Find dependencies
        deps = [d.target_id for d in self.dependencies if d.source_id == current_ci]
        
        for dep_id in deps:
            if dep_id in path:
                # Cycle found
                cycle_start = path.index(dep_id)
                return path[cycle_start:] + [dep_id]
            
            # Continue searching
            cycle = self._find_cycle(dep_id, path + [dep_id], visited.copy())
            if cycle:
                return cycle
        
        return None
    
    def identify_critical_path(self, service_id: str) -> List[str]:
        """Identify critical path for service"""
        critical_path = []
        
        print(f"\n🎯 Identifying critical path: {service_id}")
        
        # Start from service and traverse HARD dependencies
        self._traverse_critical_path(service_id, critical_path, set())
        
        print(f"   Critical path length: {len(critical_path)}")
        print(f"   Path: {' → '.join(critical_path)}")
        
        return critical_path
    
    def _traverse_critical_path(self, ci_id: str, path: List[str], visited: Set[str]):
        """Recursively traverse critical path"""
        if ci_id in visited:
            return
        
        visited.add(ci_id)
        path.append(ci_id)
        
        # Find HARD dependencies
        hard_deps = [
            d.target_id for d in self.dependencies
            if d.source_id == ci_id and d.dependency_type == DependencyType.HARD
        ]
        
        for dep_id in hard_deps:
            self._traverse_critical_path(dep_id, path, visited)
    
    def export_dependency_graph(self, format: str = "json") -> str:
        """Export dependency graph for visualization"""
        graph = {
            'nodes': [],
            'edges': []
        }
        
        # Get unique nodes
        nodes = set()
        for dep in self.dependencies:
            nodes.add(dep.source_id)
            nodes.add(dep.target_id)
        
        for node_id in nodes:
            topology = self.topologies.get(node_id)
            graph['nodes'].append({
                'id': node_id,
                'criticality': topology.criticality_score if topology else 0,
                'depth': topology.depth if topology else 0
            })
        
        # Add edges
        for dep in self.dependencies:
            graph['edges'].append({
                'source': dep.source_id,
                'target': dep.target_id,
                'type': dep.dependency_type.value
            })
        
        if format == "json":
            return json.dumps(graph, indent=2)
        else:
            return str(graph)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dependency mapping statistics"""
        by_type = {}
        for dep in self.dependencies:
            dtype = dep.dependency_type.value
            by_type[dtype] = by_type.get(dtype, 0) + 1
        
        return {
            'total_dependencies': len(self.dependencies),
            'by_type': by_type,
            'total_topologies': len(self.topologies),
            'circular_dependencies': len(self.detect_circular_dependencies())
        }


# Example usage
if __name__ == "__main__":
    mapper = DependencyMapper()
    
    # Add dependencies
    mapper.add_dependency("web-app", "database", DependencyType.HARD,
                         source_name="Web Application", target_name="Database")
    mapper.add_dependency("web-app", "cache", DependencyType.SOFT,
                         source_name="Web Application", target_name="Cache")
    mapper.add_dependency("api", "database", DependencyType.HARD,
                         source_name="API", target_name="Database")
    mapper.add_dependency("api", "web-app", DependencyType.SOFT,
                         source_name="API", target_name="Web Application")
    
    # Build topology
    topology = mapper.build_service_topology("web-app")
    
    # Calculate blast radius
    blast = mapper.calculate_blast_radius("database")
    
    # Detect circular dependencies
    mapper.detect_circular_dependencies()
    
    # Statistics
    stats = mapper.get_statistics()
    print(f"\n📊 Dependency Statistics:")
    print(f"   Total dependencies: {stats['total_dependencies']}")
