"""
Module G.2.5: Threat Correlation Engine
========================================

Purpose: Correlate threat intelligence across multiple sources to identify
         patterns, reconstruct attack chains, and detect coordinated campaigns.

Features:
- Cross-source IoC correlation
- Campaign reconstruction from disparate indicators
- Attack chain analysis (kill chain mapping)
- Entity relationship mapping (actors, campaigns, malware)
- Temporal correlation analysis
- Confidence scoring for correlations
- Graph-based threat modeling
- Automated threat hunting queries

Author: Enterprise Scanner AI Development Team
Version: 1.0.0
Created: October 17, 2025
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
import hashlib


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Types of threat correlations"""
    IOC_MATCH = "ioc_match"  # Same IoC across sources
    CAMPAIGN_LINK = "campaign_link"  # Linked to same campaign
    ACTOR_ATTRIBUTION = "actor_attribution"  # Same threat actor
    MALWARE_FAMILY = "malware_family"  # Same malware family
    TTP_SIMILARITY = "ttp_similarity"  # Similar tactics/techniques
    TEMPORAL = "temporal"  # Time-based correlation
    INFRASTRUCTURE = "infrastructure"  # Shared infrastructure
    VICTIM_OVERLAP = "victim_overlap"  # Target overlap


class ConfidenceLevel(Enum):
    """Confidence levels for correlations"""
    LOW = "low"  # 0.0-0.4
    MEDIUM = "medium"  # 0.4-0.7
    HIGH = "high"  # 0.7-0.9
    VERY_HIGH = "very_high"  # 0.9-1.0


class KillChainPhase(Enum):
    """Lockheed Martin Cyber Kill Chain phases"""
    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_AND_CONTROL = "command_and_control"
    ACTIONS_ON_OBJECTIVES = "actions_on_objectives"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ThreatCorrelation:
    """Represents a correlation between threat entities"""
    correlation_id: Optional[int] = None
    correlation_type: CorrelationType = CorrelationType.IOC_MATCH
    entity1_type: str = ""  # ioc, actor, campaign, malware
    entity1_id: str = ""
    entity1_name: str = ""
    entity2_type: str = ""
    entity2_id: str = ""
    entity2_name: str = ""
    confidence_score: float = 0.5  # 0.0-1.0
    evidence: List[str] = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    source_count: int = 1  # Number of sources confirming correlation
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get confidence level enum from score"""
        if self.confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence_score >= 0.7:
            return ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'correlation_id': self.correlation_id,
            'correlation_type': self.correlation_type.value,
            'entity1': {
                'type': self.entity1_type,
                'id': self.entity1_id,
                'name': self.entity1_name
            },
            'entity2': {
                'type': self.entity2_type,
                'id': self.entity2_id,
                'name': self.entity2_name
            },
            'confidence_score': self.confidence_score,
            'confidence_level': self.get_confidence_level().value,
            'evidence': self.evidence,
            'source_count': self.source_count
        }


@dataclass
class AttackChain:
    """Represents a reconstructed attack chain"""
    chain_id: Optional[int] = None
    campaign_name: str = ""
    threat_actor: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    phases: Dict[KillChainPhase, List[str]] = field(default_factory=dict)
    iocs: List[str] = field(default_factory=list)
    ttps: List[str] = field(default_factory=list)  # MITRE ATT&CK IDs
    malware_families: List[str] = field(default_factory=list)
    target_industries: List[str] = field(default_factory=list)
    victim_count: int = 0
    confidence_score: float = 0.5
    
    def get_completeness(self) -> float:
        """Calculate chain completeness (0.0-1.0)"""
        total_phases = len(KillChainPhase)
        covered_phases = len(self.phases)
        return covered_phases / total_phases if total_phases > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chain_id': self.chain_id,
            'campaign_name': self.campaign_name,
            'threat_actor': self.threat_actor,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'phases': {phase.value: indicators for phase, indicators in self.phases.items()},
            'completeness': self.get_completeness(),
            'ioc_count': len(self.iocs),
            'ttp_count': len(self.ttps),
            'victim_count': self.victim_count,
            'confidence_score': self.confidence_score
        }


@dataclass
class ThreatGraph:
    """Represents a graph of related threat entities"""
    graph_id: str
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # node_id -> properties
    edges: List[Tuple[str, str, float]] = field(default_factory=list)  # (source, target, weight)
    center_entity: str = ""
    entity_count: int = 0
    correlation_count: int = 0
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> None:
        """Add node to graph"""
        self.nodes[node_id] = {
            'type': node_type,
            'properties': properties
        }
        self.entity_count = len(self.nodes)
    
    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        """Add edge to graph"""
        self.edges.append((source, target, weight))
        self.correlation_count = len(self.edges)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'graph_id': self.graph_id,
            'center_entity': self.center_entity,
            'entity_count': self.entity_count,
            'correlation_count': self.correlation_count,
            'nodes': self.nodes,
            'edges': [{'source': s, 'target': t, 'weight': w} for s, t, w in self.edges]
        }


# =============================================================================
# Threat Correlation Engine
# =============================================================================

class ThreatCorrelationEngine:
    """
    Correlate threat intelligence across sources to detect patterns
    
    Capabilities:
    - Cross-source IoC correlation
    - Campaign reconstruction
    - Attack chain mapping
    - Entity relationship analysis
    - Temporal correlation detection
    - Confidence scoring
    - Graph-based threat modeling
    - Automated threat hunting
    """
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        """
        Initialize correlation engine
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.correlations: List[ThreatCorrelation] = []
        self.attack_chains: List[AttackChain] = []
        
        # Load existing correlations
        self._load_correlations()
        
        logger.info(f"ThreatCorrelationEngine initialized with {len(self.correlations)} correlations")
    
    def _load_correlations(self) -> None:
        """Load correlations from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT correlation_id, correlation_type, entity1_type, entity1_id,
                       entity2_type, entity2_id, confidence_score, evidence_json,
                       first_seen, last_seen, source_count
                FROM correlation_scores
                WHERE confidence_score >= 0.5
                ORDER BY confidence_score DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                try:
                    corr = ThreatCorrelation(
                        correlation_id=row[0],
                        correlation_type=CorrelationType(row[1]),
                        entity1_type=row[2],
                        entity1_id=row[3],
                        entity2_type=row[4],
                        entity2_id=row[5],
                        confidence_score=row[6],
                        evidence=json.loads(row[7]) if row[7] else [],
                        first_seen=datetime.fromisoformat(row[8]) if row[8] else None,
                        last_seen=datetime.fromisoformat(row[9]) if row[9] else None,
                        source_count=row[10] if row[10] else 1
                    )
                    self.correlations.append(corr)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid correlation: {e}")
            
            conn.close()
            logger.info(f"Loaded {len(self.correlations)} correlations")
            
        except Exception as e:
            logger.error(f"Error loading correlations: {e}")
    
    def correlate_iocs(self, lookback_days: int = 30) -> List[ThreatCorrelation]:
        """
        Correlate IoCs across multiple sources
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            List of IoC correlations
        """
        correlations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find IoCs appearing in multiple sources
            cursor.execute("""
                SELECT i.ioc_value, i.ioc_type, COUNT(DISTINCT s.source_id) as source_count,
                       GROUP_CONCAT(DISTINCT s.source_name) as sources,
                       MIN(i.first_seen) as first_seen,
                       MAX(i.last_seen) as last_seen
                FROM indicators_of_compromise i
                JOIN ioc_sources ios ON i.ioc_id = ios.ioc_id
                JOIN threat_intel_sources s ON ios.source_id = s.source_id
                WHERE i.last_seen >= date('now', '-' || ? || ' days')
                GROUP BY i.ioc_value, i.ioc_type
                HAVING source_count > 1
                ORDER BY source_count DESC
                LIMIT 100
            """, (lookback_days,))
            
            for row in cursor.fetchall():
                ioc_value = row[0]
                ioc_type = row[1]
                source_count = row[2]
                sources = row[3].split(',') if row[3] else []
                first_seen = datetime.fromisoformat(row[4]) if row[4] else None
                last_seen = datetime.fromisoformat(row[5]) if row[5] else None
                
                # Calculate confidence based on source count and reliability
                confidence = min(1.0, 0.5 + (source_count * 0.1))
                
                corr = ThreatCorrelation(
                    correlation_type=CorrelationType.IOC_MATCH,
                    entity1_type="ioc",
                    entity1_id=ioc_value,
                    entity1_name=f"{ioc_type}: {ioc_value}",
                    entity2_type="sources",
                    entity2_id="multi",
                    entity2_name=f"{source_count} sources",
                    confidence_score=confidence,
                    evidence=[f"Seen in: {', '.join(sources[:3])}"],
                    first_seen=first_seen,
                    last_seen=last_seen,
                    source_count=source_count
                )
                
                correlations.append(corr)
                self._save_correlation(corr)
            
            conn.close()
            logger.info(f"Found {len(correlations)} IoC correlations")
            
        except Exception as e:
            logger.error(f"Error correlating IoCs: {e}")
        
        return correlations
    
    def correlate_campaigns(self) -> List[ThreatCorrelation]:
        """
        Correlate campaigns across threat actors and IoCs
        
        Returns:
            List of campaign correlations
        """
        correlations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find campaigns with shared IoCs
            cursor.execute("""
                SELECT c1.campaign_id, c1.campaign_name, c2.campaign_id, c2.campaign_name,
                       COUNT(DISTINCT ic1.ioc_id) as shared_iocs
                FROM threat_campaigns c1
                JOIN ioc_campaigns ic1 ON c1.campaign_id = ic1.campaign_id
                JOIN ioc_campaigns ic2 ON ic1.ioc_id = ic2.ioc_id
                JOIN threat_campaigns c2 ON ic2.campaign_id = c2.campaign_id
                WHERE c1.campaign_id < c2.campaign_id
                  AND c1.is_active = 1
                  AND c2.is_active = 1
                GROUP BY c1.campaign_id, c2.campaign_id
                HAVING shared_iocs >= 3
                ORDER BY shared_iocs DESC
                LIMIT 50
            """)
            
            for row in cursor.fetchall():
                campaign1_id = row[0]
                campaign1_name = row[1]
                campaign2_id = row[2]
                campaign2_name = row[3]
                shared_iocs = row[4]
                
                confidence = min(1.0, 0.6 + (shared_iocs * 0.05))
                
                corr = ThreatCorrelation(
                    correlation_type=CorrelationType.CAMPAIGN_LINK,
                    entity1_type="campaign",
                    entity1_id=str(campaign1_id),
                    entity1_name=campaign1_name,
                    entity2_type="campaign",
                    entity2_id=str(campaign2_id),
                    entity2_name=campaign2_name,
                    confidence_score=confidence,
                    evidence=[f"{shared_iocs} shared IoCs"],
                    source_count=shared_iocs
                )
                
                correlations.append(corr)
                self._save_correlation(corr)
            
            conn.close()
            logger.info(f"Found {len(correlations)} campaign correlations")
            
        except Exception as e:
            logger.error(f"Error correlating campaigns: {e}")
        
        return correlations
    
    def correlate_actors_to_campaigns(self) -> List[ThreatCorrelation]:
        """
        Correlate threat actors to campaigns
        
        Returns:
            List of actor-campaign correlations
        """
        correlations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Actor to campaign mappings
            cursor.execute("""
                SELECT a.actor_id, a.actor_name, c.campaign_id, c.campaign_name,
                       c.confidence_score, c.is_active
                FROM threat_actors a
                JOIN threat_campaigns c ON a.actor_id = c.actor_id
                WHERE c.confidence_score >= 0.5
                ORDER BY c.confidence_score DESC
                LIMIT 100
            """)
            
            for row in cursor.fetchall():
                actor_id = row[0]
                actor_name = row[1]
                campaign_id = row[2]
                campaign_name = row[3]
                confidence = row[4]
                is_active = bool(row[5])
                
                evidence = ["Direct attribution from threat intelligence"]
                if is_active:
                    evidence.append("Campaign currently active")
                
                corr = ThreatCorrelation(
                    correlation_type=CorrelationType.ACTOR_ATTRIBUTION,
                    entity1_type="actor",
                    entity1_id=str(actor_id),
                    entity1_name=actor_name,
                    entity2_type="campaign",
                    entity2_id=str(campaign_id),
                    entity2_name=campaign_name,
                    confidence_score=confidence,
                    evidence=evidence,
                    source_count=1
                )
                
                correlations.append(corr)
                self._save_correlation(corr)
            
            conn.close()
            logger.info(f"Found {len(correlations)} actor-campaign correlations")
            
        except Exception as e:
            logger.error(f"Error correlating actors to campaigns: {e}")
        
        return correlations
    
    def correlate_by_ttps(self) -> List[ThreatCorrelation]:
        """
        Correlate threats by similar TTPs (MITRE ATT&CK)
        
        Returns:
            List of TTP correlations
        """
        correlations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find actors with similar TTPs
            cursor.execute("""
                SELECT a1.actor_id, a1.actor_name, a2.actor_id, a2.actor_name,
                       COUNT(DISTINCT t1.technique_id) as shared_ttps
                FROM threat_actors a1
                JOIN threat_actor_ttps t1 ON a1.actor_id = t1.actor_id
                JOIN threat_actor_ttps t2 ON t1.technique_id = t2.technique_id
                JOIN threat_actors a2 ON t2.actor_id = a2.actor_id
                WHERE a1.actor_id < a2.actor_id
                  AND a1.is_active = 1
                  AND a2.is_active = 1
                GROUP BY a1.actor_id, a2.actor_id
                HAVING shared_ttps >= 5
                ORDER BY shared_ttps DESC
                LIMIT 50
            """)
            
            for row in cursor.fetchall():
                actor1_id = row[0]
                actor1_name = row[1]
                actor2_id = row[2]
                actor2_name = row[3]
                shared_ttps = row[4]
                
                confidence = min(1.0, 0.5 + (shared_ttps * 0.05))
                
                corr = ThreatCorrelation(
                    correlation_type=CorrelationType.TTP_SIMILARITY,
                    entity1_type="actor",
                    entity1_id=str(actor1_id),
                    entity1_name=actor1_name,
                    entity2_type="actor",
                    entity2_id=str(actor2_id),
                    entity2_name=actor2_name,
                    confidence_score=confidence,
                    evidence=[f"{shared_ttps} shared MITRE ATT&CK techniques"],
                    source_count=shared_ttps
                )
                
                correlations.append(corr)
                self._save_correlation(corr)
            
            conn.close()
            logger.info(f"Found {len(correlations)} TTP correlations")
            
        except Exception as e:
            logger.error(f"Error correlating by TTPs: {e}")
        
        return correlations
    
    def correlate_temporal(self, time_window_hours: int = 24) -> List[ThreatCorrelation]:
        """
        Correlate threats based on temporal proximity
        
        Args:
            time_window_hours: Time window for correlation
            
        Returns:
            List of temporal correlations
        """
        correlations = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find IoCs appearing in similar timeframes
            cursor.execute("""
                SELECT i1.ioc_id, i1.ioc_value, i2.ioc_id, i2.ioc_value,
                       i1.first_seen, i2.first_seen,
                       (julianday(i2.first_seen) - julianday(i1.first_seen)) * 24 as hours_apart
                FROM indicators_of_compromise i1
                JOIN indicators_of_compromise i2 ON i1.ioc_id < i2.ioc_id
                WHERE i1.first_seen >= date('now', '-7 days')
                  AND i2.first_seen >= date('now', '-7 days')
                  AND ABS((julianday(i2.first_seen) - julianday(i1.first_seen)) * 24) <= ?
                  AND i1.threat_level IN ('high', 'critical')
                  AND i2.threat_level IN ('high', 'critical')
                ORDER BY hours_apart
                LIMIT 50
            """, (time_window_hours,))
            
            for row in cursor.fetchall():
                ioc1_id = row[0]
                ioc1_value = row[1]
                ioc2_id = row[2]
                ioc2_value = row[3]
                first_seen1 = row[4]
                first_seen2 = row[5]
                hours_apart = abs(row[6])
                
                confidence = max(0.3, 1.0 - (hours_apart / time_window_hours))
                
                corr = ThreatCorrelation(
                    correlation_type=CorrelationType.TEMPORAL,
                    entity1_type="ioc",
                    entity1_id=str(ioc1_id),
                    entity1_name=ioc1_value,
                    entity2_type="ioc",
                    entity2_id=str(ioc2_id),
                    entity2_name=ioc2_value,
                    confidence_score=confidence,
                    evidence=[f"Appeared within {hours_apart:.1f} hours"],
                    first_seen=datetime.fromisoformat(first_seen1) if first_seen1 else None
                )
                
                correlations.append(corr)
                self._save_correlation(corr)
            
            conn.close()
            logger.info(f"Found {len(correlations)} temporal correlations")
            
        except Exception as e:
            logger.error(f"Error with temporal correlation: {e}")
        
        return correlations
    
    def reconstruct_attack_chain(self, campaign_id: int) -> Optional[AttackChain]:
        """
        Reconstruct attack chain for a campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            AttackChain object or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign info
            cursor.execute("""
                SELECT c.campaign_name, c.actor_id, a.actor_name, c.start_date,
                       c.end_date, c.victim_count, c.confidence_score
                FROM threat_campaigns c
                LEFT JOIN threat_actors a ON c.actor_id = a.actor_id
                WHERE c.campaign_id = ?
            """, (campaign_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            chain = AttackChain(
                chain_id=campaign_id,
                campaign_name=row[0],
                threat_actor=row[2] if row[2] else "Unknown",
                start_date=datetime.fromisoformat(row[3]) if row[3] else None,
                end_date=datetime.fromisoformat(row[4]) if row[4] else None,
                victim_count=row[5] if row[5] else 0,
                confidence_score=row[6] if row[6] else 0.5
            )
            
            # Get TTPs and map to kill chain
            cursor.execute("""
                SELECT ttp.technique_id, ttp.technique_name, ttp.tactic
                FROM threat_actor_ttps ttp
                WHERE ttp.actor_id = ?
            """, (row[1],))
            
            ttp_mapping = {
                'Initial Access': KillChainPhase.DELIVERY,
                'Execution': KillChainPhase.EXPLOITATION,
                'Persistence': KillChainPhase.INSTALLATION,
                'Privilege Escalation': KillChainPhase.EXPLOITATION,
                'Defense Evasion': KillChainPhase.INSTALLATION,
                'Credential Access': KillChainPhase.EXPLOITATION,
                'Discovery': KillChainPhase.RECONNAISSANCE,
                'Lateral Movement': KillChainPhase.ACTIONS_ON_OBJECTIVES,
                'Collection': KillChainPhase.ACTIONS_ON_OBJECTIVES,
                'Command and Control': KillChainPhase.COMMAND_AND_CONTROL,
                'Exfiltration': KillChainPhase.ACTIONS_ON_OBJECTIVES,
                'Impact': KillChainPhase.ACTIONS_ON_OBJECTIVES
            }
            
            for ttp_row in cursor.fetchall():
                technique_id = ttp_row[0]
                technique_name = ttp_row[1]
                tactic = ttp_row[2]
                
                chain.ttps.append(technique_id)
                
                # Map to kill chain phase
                phase = ttp_mapping.get(tactic, KillChainPhase.ACTIONS_ON_OBJECTIVES)
                if phase not in chain.phases:
                    chain.phases[phase] = []
                chain.phases[phase].append(f"{technique_id}: {technique_name}")
            
            # Get IoCs
            cursor.execute("""
                SELECT i.ioc_value, i.ioc_type
                FROM indicators_of_compromise i
                JOIN ioc_campaigns ic ON i.ioc_id = ic.ioc_id
                WHERE ic.campaign_id = ?
                LIMIT 100
            """, (campaign_id,))
            
            chain.iocs = [f"{row[1]}: {row[0]}" for row in cursor.fetchall()]
            
            # Get malware families
            cursor.execute("""
                SELECT DISTINCT m.malware_name
                FROM malware_families m
                JOIN threat_campaigns c ON m.campaign_id = c.campaign_id
                WHERE c.campaign_id = ?
            """, (campaign_id,))
            
            chain.malware_families = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            logger.info(f"Reconstructed attack chain for {chain.campaign_name}")
            return chain
            
        except Exception as e:
            logger.error(f"Error reconstructing attack chain: {e}")
            return None
    
    def build_threat_graph(self, center_entity_id: str, entity_type: str, depth: int = 2) -> ThreatGraph:
        """
        Build threat graph from center entity
        
        Args:
            center_entity_id: ID of center entity
            entity_type: Type (actor, campaign, ioc)
            depth: Graph traversal depth
            
        Returns:
            ThreatGraph object
        """
        graph_id = hashlib.md5(f"{entity_type}:{center_entity_id}:{depth}".encode()).hexdigest()
        graph = ThreatGraph(graph_id=graph_id, center_entity=center_entity_id)
        
        # Add center node
        graph.add_node(center_entity_id, entity_type, {'name': center_entity_id, 'depth': 0})
        
        # BFS traversal of correlations
        visited = {center_entity_id}
        queue = [(center_entity_id, entity_type, 0)]
        
        while queue and len(graph.nodes) < 100:  # Limit graph size
            current_id, current_type, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            # Find correlations
            related = self._get_related_entities(current_id, current_type)
            
            for related_id, related_type, related_name, confidence in related:
                if related_id not in visited:
                    visited.add(related_id)
                    graph.add_node(related_id, related_type, {
                        'name': related_name,
                        'depth': current_depth + 1
                    })
                    queue.append((related_id, related_type, current_depth + 1))
                
                graph.add_edge(current_id, related_id, confidence)
        
        logger.info(f"Built threat graph with {graph.entity_count} entities, {graph.correlation_count} correlations")
        return graph
    
    def _get_related_entities(
        self,
        entity_id: str,
        entity_type: str
    ) -> List[Tuple[str, str, str, float]]:
        """Get entities related to given entity"""
        related = []
        
        for corr in self.correlations:
            if corr.entity1_id == entity_id and corr.entity1_type == entity_type:
                related.append((
                    corr.entity2_id,
                    corr.entity2_type,
                    corr.entity2_name,
                    corr.confidence_score
                ))
            elif corr.entity2_id == entity_id and corr.entity2_type == entity_type:
                related.append((
                    corr.entity1_id,
                    corr.entity1_type,
                    corr.entity1_name,
                    corr.confidence_score
                ))
        
        return related
    
    def _save_correlation(self, corr: ThreatCorrelation) -> None:
        """Save correlation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO correlation_scores (
                    correlation_type, entity1_type, entity1_id,
                    entity2_type, entity2_id, confidence_score,
                    evidence_json, first_seen, last_seen, source_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                corr.correlation_type.value,
                corr.entity1_type,
                corr.entity1_id,
                corr.entity2_type,
                corr.entity2_id,
                corr.confidence_score,
                json.dumps(corr.evidence),
                corr.first_seen.isoformat() if corr.first_seen else None,
                corr.last_seen.isoformat() if corr.last_seen else None,
                corr.source_count
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.debug(f"Error saving correlation: {e}")
    
    def run_full_correlation(self) -> Dict[str, int]:
        """
        Run full correlation analysis
        
        Returns:
            Stats dict with counts
        """
        stats = {
            'ioc_correlations': 0,
            'campaign_correlations': 0,
            'actor_correlations': 0,
            'ttp_correlations': 0,
            'temporal_correlations': 0
        }
        
        logger.info("Starting full correlation analysis...")
        
        # IoC correlation
        ioc_corrs = self.correlate_iocs(lookback_days=30)
        stats['ioc_correlations'] = len(ioc_corrs)
        
        # Campaign correlation
        campaign_corrs = self.correlate_campaigns()
        stats['campaign_correlations'] = len(campaign_corrs)
        
        # Actor-campaign correlation
        actor_corrs = self.correlate_actors_to_campaigns()
        stats['actor_correlations'] = len(actor_corrs)
        
        # TTP correlation
        ttp_corrs = self.correlate_by_ttps()
        stats['ttp_correlations'] = len(ttp_corrs)
        
        # Temporal correlation
        temporal_corrs = self.correlate_temporal(time_window_hours=24)
        stats['temporal_correlations'] = len(temporal_corrs)
        
        logger.info(f"Correlation analysis complete: {stats}")
        return stats
    
    def get_correlation_summary(self) -> Dict[str, Any]:
        """Get summary of correlations"""
        by_type = defaultdict(int)
        by_confidence = defaultdict(int)
        
        for corr in self.correlations:
            by_type[corr.correlation_type.value] += 1
            by_confidence[corr.get_confidence_level().value] += 1
        
        return {
            'total_correlations': len(self.correlations),
            'by_type': dict(by_type),
            'by_confidence': dict(by_confidence),
            'timestamp': datetime.now().isoformat()
        }


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize engine
    engine = ThreatCorrelationEngine()
    
    # Run full correlation
    print("\n=== Running Full Correlation Analysis ===")
    stats = engine.run_full_correlation()
    print(f"IoC Correlations: {stats['ioc_correlations']}")
    print(f"Campaign Correlations: {stats['campaign_correlations']}")
    print(f"Actor Correlations: {stats['actor_correlations']}")
    print(f"TTP Correlations: {stats['ttp_correlations']}")
    print(f"Temporal Correlations: {stats['temporal_correlations']}")
    
    # Get summary
    print("\n=== Correlation Summary ===")
    summary = engine.get_correlation_summary()
    print(f"Total Correlations: {summary['total_correlations']}")
    print(f"By Type: {summary['by_type']}")
    print(f"By Confidence: {summary['by_confidence']}")
    
    # Build threat graph example
    if engine.correlations:
        first_corr = engine.correlations[0]
        print(f"\n=== Building Threat Graph ===")
        graph = engine.build_threat_graph(first_corr.entity1_id, first_corr.entity1_type, depth=2)
        print(f"Entities: {graph.entity_count}")
        print(f"Correlations: {graph.correlation_count}")
