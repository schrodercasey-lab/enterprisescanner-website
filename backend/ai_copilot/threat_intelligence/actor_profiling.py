"""
Module G.2.2: Threat Actor Profiling Engine
==========================================

Purpose: Track and profile 100+ Advanced Persistent Threat (APT) groups with
         comprehensive attribution, TTPs, and campaign analysis.

Features:
- APT group tracking and profiling (100+ groups)
- MITRE ATT&CK technique mapping
- Campaign tracking and correlation
- Attribution confidence scoring
- Target industry and region analysis
- Behavioral pattern recognition
- Threat actor evolution tracking

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
from typing import Dict, List, Optional, Set, Any
import requests


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Motivation(Enum):
    """Threat actor motivations"""
    FINANCIAL = "financial"
    ESPIONAGE = "espionage"
    SABOTAGE = "sabotage"
    HACKTIVISM = "hacktivism"
    UNKNOWN = "unknown"


class SophisticationLevel(Enum):
    """Threat actor sophistication levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ADVANCED = "advanced"


class CampaignStatus(Enum):
    """Campaign activity status"""
    ACTIVE = "active"
    DORMANT = "dormant"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class AttackVectorType(Enum):
    """Types of attack vectors"""
    PHISHING = "phishing"
    EXPLOIT = "exploit"
    SUPPLY_CHAIN = "supply_chain"
    WATERING_HOLE = "watering_hole"
    CREDENTIAL_STUFFING = "credential_stuffing"
    BRUTE_FORCE = "brute_force"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE = "malware"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ThreatActor:
    """Represents an APT group or threat actor"""
    actor_id: Optional[int] = None
    actor_name: str = ""
    aliases: List[str] = field(default_factory=list)
    attribution_confidence: float = 0.50  # 0.0 to 1.0
    suspected_nation_state: Optional[str] = None
    motivation: Motivation = Motivation.UNKNOWN
    sophistication_level: SophisticationLevel = SophisticationLevel.MEDIUM
    first_observed: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    is_active: bool = True
    target_industries: List[str] = field(default_factory=list)
    target_regions: List[str] = field(default_factory=list)
    mitre_techniques: List[str] = field(default_factory=list)  # ATT&CK technique IDs
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'actor_id': self.actor_id,
            'actor_name': self.actor_name,
            'aliases': self.aliases,
            'attribution_confidence': self.attribution_confidence,
            'suspected_nation_state': self.suspected_nation_state,
            'motivation': self.motivation.value,
            'sophistication_level': self.sophistication_level.value,
            'first_observed': self.first_observed.isoformat() if self.first_observed else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_active': self.is_active,
            'target_industries': self.target_industries,
            'target_regions': self.target_regions,
            'mitre_techniques': self.mitre_techniques,
            'description': self.description
        }


@dataclass
class ThreatCampaign:
    """Represents a threat campaign"""
    campaign_id: Optional[int] = None
    campaign_name: str = ""
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_ongoing: bool = True
    target_industries: List[str] = field(default_factory=list)
    target_regions: List[str] = field(default_factory=list)
    attack_vectors: List[AttackVectorType] = field(default_factory=list)
    malware_families: List[str] = field(default_factory=list)
    objectives: str = ""
    description: str = ""
    confidence_score: float = 0.50
    ioc_count: int = 0
    victim_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'actor_id': self.actor_id,
            'actor_name': self.actor_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_ongoing': self.is_ongoing,
            'target_industries': self.target_industries,
            'target_regions': self.target_regions,
            'attack_vectors': [v.value for v in self.attack_vectors],
            'malware_families': self.malware_families,
            'objectives': self.objectives,
            'description': self.description,
            'confidence_score': self.confidence_score,
            'ioc_count': self.ioc_count,
            'victim_count': self.victim_count
        }


@dataclass
class TTP:
    """Represents a Tactic, Technique, and Procedure (MITRE ATT&CK)"""
    ttp_id: Optional[int] = None
    actor_id: int = 0
    technique_id: str = ""  # e.g., "T1566.001"
    technique_name: str = ""
    tactic: str = ""  # e.g., "Initial Access"
    observed_count: int = 1
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    confidence_score: float = 0.50
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'ttp_id': self.ttp_id,
            'actor_id': self.actor_id,
            'technique_id': self.technique_id,
            'technique_name': self.technique_name,
            'tactic': self.tactic,
            'observed_count': self.observed_count,
            'first_observed': self.first_observed.isoformat() if self.first_observed else None,
            'last_observed': self.last_observed.isoformat() if self.last_observed else None,
            'confidence_score': self.confidence_score
        }


@dataclass
class ActorProfile:
    """Complete profile of a threat actor with all associated data"""
    actor: ThreatActor
    campaigns: List[ThreatCampaign] = field(default_factory=list)
    ttps: List[TTP] = field(default_factory=list)
    total_iocs: int = 0
    related_actors: List[str] = field(default_factory=list)
    activity_timeline: Dict[str, int] = field(default_factory=dict)  # Year-Month: count


# =============================================================================
# Threat Actor Profiling Engine
# =============================================================================

class ThreatActorProfilingEngine:
    """
    Track and profile Advanced Persistent Threat (APT) groups
    
    Capabilities:
    - Track 100+ APT groups with comprehensive profiles
    - MITRE ATT&CK technique mapping and analysis
    - Campaign tracking and attribution
    - Target industry and region analysis
    - Behavioral pattern recognition
    - Attribution confidence scoring
    - Actor evolution tracking
    """
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        """
        Initialize the profiling engine
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.actors: Dict[int, ThreatActor] = {}
        self.campaigns: Dict[int, ThreatCampaign] = {}
        
        # Load data from database
        self._load_actors()
        self._load_campaigns()
        
        logger.info(f"ThreatActorProfilingEngine initialized with {len(self.actors)} actors")
    
    def _load_actors(self) -> None:
        """Load threat actors from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT actor_id, actor_name, actor_aliases, attribution_confidence,
                       suspected_nation_state, motivation, sophistication_level,
                       first_observed_date, last_activity_date, is_active,
                       target_industries, target_regions, mitre_attck_techniques,
                       description
                FROM threat_actors
            """)
            
            for row in cursor.fetchall():
                actor = ThreatActor(
                    actor_id=row[0],
                    actor_name=row[1],
                    aliases=json.loads(row[2]) if row[2] else [],
                    attribution_confidence=row[3],
                    suspected_nation_state=row[4],
                    motivation=Motivation(row[5]) if row[5] else Motivation.UNKNOWN,
                    sophistication_level=SophisticationLevel(row[6]) if row[6] else SophisticationLevel.MEDIUM,
                    first_observed=datetime.fromisoformat(row[7]) if row[7] else None,
                    last_activity=datetime.fromisoformat(row[8]) if row[8] else None,
                    is_active=bool(row[9]),
                    target_industries=json.loads(row[10]) if row[10] else [],
                    target_regions=json.loads(row[11]) if row[11] else [],
                    mitre_techniques=json.loads(row[12]) if row[12] else [],
                    description=row[13] if row[13] else ""
                )
                self.actors[actor.actor_id] = actor
            
            conn.close()
            logger.info(f"Loaded {len(self.actors)} threat actors")
            
        except Exception as e:
            logger.error(f"Error loading actors: {e}")
    
    def _load_campaigns(self) -> None:
        """Load threat campaigns from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.campaign_id, c.campaign_name, c.actor_id, a.actor_name,
                       c.campaign_start_date, c.campaign_end_date, c.is_ongoing,
                       c.target_industries, c.target_regions, c.attack_vectors,
                       c.malware_families, c.objectives, c.description, c.confidence_score
                FROM threat_campaigns c
                LEFT JOIN threat_actors a ON c.actor_id = a.actor_id
            """)
            
            for row in cursor.fetchall():
                campaign = ThreatCampaign(
                    campaign_id=row[0],
                    campaign_name=row[1],
                    actor_id=row[2],
                    actor_name=row[3],
                    start_date=datetime.fromisoformat(row[4]) if row[4] else None,
                    end_date=datetime.fromisoformat(row[5]) if row[5] else None,
                    is_ongoing=bool(row[6]),
                    target_industries=json.loads(row[7]) if row[7] else [],
                    target_regions=json.loads(row[8]) if row[8] else [],
                    attack_vectors=[AttackVectorType(v) for v in json.loads(row[9])] if row[9] else [],
                    malware_families=json.loads(row[10]) if row[10] else [],
                    objectives=row[11] if row[11] else "",
                    description=row[12] if row[12] else "",
                    confidence_score=row[13]
                )
                self.campaigns[campaign.campaign_id] = campaign
            
            conn.close()
            logger.info(f"Loaded {len(self.campaigns)} threat campaigns")
            
        except Exception as e:
            logger.error(f"Error loading campaigns: {e}")
    
    def add_threat_actor(self, actor: ThreatActor) -> int:
        """
        Add a new threat actor to the database
        
        Args:
            actor: ThreatActor object
            
        Returns:
            actor_id of the added actor
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO threat_actors (
                    actor_name, actor_aliases, attribution_confidence,
                    suspected_nation_state, motivation, sophistication_level,
                    first_observed_date, last_activity_date, is_active,
                    target_industries, target_regions, mitre_attck_techniques,
                    description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                actor.actor_name,
                json.dumps(actor.aliases),
                actor.attribution_confidence,
                actor.suspected_nation_state,
                actor.motivation.value,
                actor.sophistication_level.value,
                actor.first_observed.isoformat() if actor.first_observed else None,
                actor.last_activity.isoformat() if actor.last_activity else None,
                actor.is_active,
                json.dumps(actor.target_industries),
                json.dumps(actor.target_regions),
                json.dumps(actor.mitre_techniques),
                actor.description
            ))
            
            actor_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            actor.actor_id = actor_id
            self.actors[actor_id] = actor
            
            logger.info(f"Added threat actor: {actor.actor_name} (ID: {actor_id})")
            return actor_id
            
        except Exception as e:
            logger.error(f"Error adding threat actor: {e}")
            raise
    
    def add_campaign(self, campaign: ThreatCampaign) -> int:
        """
        Add a new threat campaign
        
        Args:
            campaign: ThreatCampaign object
            
        Returns:
            campaign_id of the added campaign
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO threat_campaigns (
                    campaign_name, actor_id, campaign_start_date, campaign_end_date,
                    is_ongoing, target_industries, target_regions, attack_vectors,
                    malware_families, objectives, description, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign.campaign_name,
                campaign.actor_id,
                campaign.start_date.isoformat() if campaign.start_date else None,
                campaign.end_date.isoformat() if campaign.end_date else None,
                campaign.is_ongoing,
                json.dumps(campaign.target_industries),
                json.dumps(campaign.target_regions),
                json.dumps([v.value for v in campaign.attack_vectors]),
                json.dumps(campaign.malware_families),
                campaign.objectives,
                campaign.description,
                campaign.confidence_score
            ))
            
            campaign_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            campaign.campaign_id = campaign_id
            self.campaigns[campaign_id] = campaign
            
            logger.info(f"Added campaign: {campaign.campaign_name} (ID: {campaign_id})")
            return campaign_id
            
        except Exception as e:
            logger.error(f"Error adding campaign: {e}")
            raise
    
    def add_ttp(self, ttp: TTP) -> int:
        """
        Add or update a TTP (MITRE ATT&CK technique) for an actor
        
        Args:
            ttp: TTP object
            
        Returns:
            ttp_id
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if TTP already exists for this actor
            cursor.execute("""
                SELECT ttp_id, observed_count
                FROM threat_actor_ttps
                WHERE actor_id = ? AND mitre_technique_id = ?
            """, (ttp.actor_id, ttp.technique_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing TTP
                ttp_id, count = existing
                cursor.execute("""
                    UPDATE threat_actor_ttps
                    SET observed_count = observed_count + 1,
                        last_observed_date = ?,
                        confidence_score = ?
                    WHERE ttp_id = ?
                """, (
                    datetime.now().isoformat(),
                    min(1.0, ttp.confidence_score + 0.1),
                    ttp_id
                ))
                logger.info(f"Updated TTP {ttp.technique_id} for actor {ttp.actor_id}")
            else:
                # Insert new TTP
                cursor.execute("""
                    INSERT INTO threat_actor_ttps (
                        actor_id, mitre_technique_id, mitre_technique_name,
                        mitre_tactic, observed_count, first_observed_date,
                        last_observed_date, confidence_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ttp.actor_id,
                    ttp.technique_id,
                    ttp.technique_name,
                    ttp.tactic,
                    ttp.observed_count,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    ttp.confidence_score
                ))
                ttp_id = cursor.lastrowid
                logger.info(f"Added TTP {ttp.technique_id} for actor {ttp.actor_id}")
            
            conn.commit()
            conn.close()
            
            return ttp_id
            
        except Exception as e:
            logger.error(f"Error adding TTP: {e}")
            raise
    
    def get_actor_profile(self, actor_id: int) -> Optional[ActorProfile]:
        """
        Get complete profile for a threat actor
        
        Args:
            actor_id: ID of the threat actor
            
        Returns:
            ActorProfile with all associated data
        """
        if actor_id not in self.actors:
            logger.warning(f"Actor {actor_id} not found")
            return None
        
        actor = self.actors[actor_id]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaigns
            campaigns = [c for c in self.campaigns.values() if c.actor_id == actor_id]
            
            # Get TTPs
            cursor.execute("""
                SELECT ttp_id, actor_id, mitre_technique_id, mitre_technique_name,
                       mitre_tactic, observed_count, first_observed_date,
                       last_observed_date, confidence_score
                FROM threat_actor_ttps
                WHERE actor_id = ?
                ORDER BY observed_count DESC
            """, (actor_id,))
            
            ttps = []
            for row in cursor.fetchall():
                ttp = TTP(
                    ttp_id=row[0],
                    actor_id=row[1],
                    technique_id=row[2],
                    technique_name=row[3],
                    tactic=row[4],
                    observed_count=row[5],
                    first_observed=datetime.fromisoformat(row[6]) if row[6] else None,
                    last_observed=datetime.fromisoformat(row[7]) if row[7] else None,
                    confidence_score=row[8]
                )
                ttps.append(ttp)
            
            # Get total IoCs associated with this actor's campaigns
            cursor.execute("""
                SELECT COUNT(DISTINCT ic.ioc_id)
                FROM ioc_campaigns ic
                JOIN threat_campaigns tc ON ic.campaign_id = tc.campaign_id
                WHERE tc.actor_id = ?
            """, (actor_id,))
            total_iocs = cursor.fetchone()[0]
            
            conn.close()
            
            profile = ActorProfile(
                actor=actor,
                campaigns=campaigns,
                ttps=ttps,
                total_iocs=total_iocs
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting actor profile: {e}")
            return None
    
    def search_actors(self, 
                     nation_state: Optional[str] = None,
                     motivation: Optional[Motivation] = None,
                     sophistication: Optional[SophisticationLevel] = None,
                     target_industry: Optional[str] = None,
                     is_active: Optional[bool] = None) -> List[ThreatActor]:
        """
        Search for threat actors by various criteria
        
        Args:
            nation_state: Filter by nation state
            motivation: Filter by motivation
            sophistication: Filter by sophistication level
            target_industry: Filter by target industry
            is_active: Filter by active status
            
        Returns:
            List of matching ThreatActor objects
        """
        results = []
        
        for actor in self.actors.values():
            # Apply filters
            if nation_state and actor.suspected_nation_state != nation_state:
                continue
            if motivation and actor.motivation != motivation:
                continue
            if sophistication and actor.sophistication_level != sophistication:
                continue
            if target_industry and target_industry not in actor.target_industries:
                continue
            if is_active is not None and actor.is_active != is_active:
                continue
            
            results.append(actor)
        
        return results
    
    def get_actors_by_industry(self, industry: str) -> List[ThreatActor]:
        """Get all threat actors targeting a specific industry"""
        return [
            actor for actor in self.actors.values()
            if industry in actor.target_industries
        ]
    
    def get_actors_by_region(self, region: str) -> List[ThreatActor]:
        """Get all threat actors targeting a specific region"""
        return [
            actor for actor in self.actors.values()
            if region in actor.target_regions
        ]
    
    def get_active_campaigns(self) -> List[ThreatCampaign]:
        """Get all currently active campaigns"""
        return [c for c in self.campaigns.values() if c.is_ongoing]
    
    def get_campaigns_by_actor(self, actor_id: int) -> List[ThreatCampaign]:
        """Get all campaigns attributed to a specific actor"""
        return [c for c in self.campaigns.values() if c.actor_id == actor_id]
    
    def get_mitre_coverage(self, actor_id: int) -> Dict[str, List[str]]:
        """
        Get MITRE ATT&CK coverage for an actor grouped by tactic
        
        Args:
            actor_id: ID of the threat actor
            
        Returns:
            Dict of tactic -> list of technique IDs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mitre_tactic, mitre_technique_id, mitre_technique_name
                FROM threat_actor_ttps
                WHERE actor_id = ?
                ORDER BY mitre_tactic, observed_count DESC
            """, (actor_id,))
            
            coverage = {}
            for row in cursor.fetchall():
                tactic = row[0]
                technique = f"{row[1]} - {row[2]}"
                
                if tactic not in coverage:
                    coverage[tactic] = []
                coverage[tactic].append(technique)
            
            conn.close()
            return coverage
            
        except Exception as e:
            logger.error(f"Error getting MITRE coverage: {e}")
            return {}
    
    def update_actor_activity(self, actor_id: int, activity_date: datetime = None) -> None:
        """
        Update actor's last activity date
        
        Args:
            actor_id: ID of the threat actor
            activity_date: Date of activity (defaults to now)
        """
        if activity_date is None:
            activity_date = datetime.now()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE threat_actors
                SET last_activity_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE actor_id = ?
            """, (activity_date.isoformat(), actor_id))
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            if actor_id in self.actors:
                self.actors[actor_id].last_activity = activity_date
            
            logger.info(f"Updated activity for actor {actor_id}")
            
        except Exception as e:
            logger.error(f"Error updating actor activity: {e}")
    
    def get_attribution_report(self) -> Dict[str, Any]:
        """
        Generate attribution confidence report
        
        Returns:
            Summary of attribution confidence across all actors
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Actors by confidence level
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN attribution_confidence >= 0.8 THEN 'high'
                        WHEN attribution_confidence >= 0.6 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level,
                    COUNT(*) as count
                FROM threat_actors
                GROUP BY confidence_level
            """)
            by_confidence = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Actors by nation state
            cursor.execute("""
                SELECT suspected_nation_state, COUNT(*) as count
                FROM threat_actors
                WHERE suspected_nation_state IS NOT NULL
                GROUP BY suspected_nation_state
                ORDER BY count DESC
            """)
            by_nation = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Active vs inactive
            cursor.execute("""
                SELECT is_active, COUNT(*) as count
                FROM threat_actors
                GROUP BY is_active
            """)
            activity_status = {('active' if row[0] else 'inactive'): row[1] 
                             for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total_actors': len(self.actors),
                'by_confidence': by_confidence,
                'by_nation_state': by_nation,
                'activity_status': activity_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating attribution report: {e}")
            return {}
    
    def get_industry_threat_landscape(self, industry: str) -> Dict[str, Any]:
        """
        Get threat landscape summary for a specific industry
        
        Args:
            industry: Industry sector (e.g., 'financial', 'healthcare')
            
        Returns:
            Threat landscape summary
        """
        actors = self.get_actors_by_industry(industry)
        
        # Get active campaigns targeting this industry
        active_campaigns = [
            c for c in self.campaigns.values()
            if c.is_ongoing and industry in c.target_industries
        ]
        
        # Count by sophistication
        by_sophistication = {}
        for actor in actors:
            level = actor.sophistication_level.value
            by_sophistication[level] = by_sophistication.get(level, 0) + 1
        
        # Count by motivation
        by_motivation = {}
        for actor in actors:
            mot = actor.motivation.value
            by_motivation[mot] = by_motivation.get(mot, 0) + 1
        
        return {
            'industry': industry,
            'total_actors': len(actors),
            'active_campaigns': len(active_campaigns),
            'by_sophistication': by_sophistication,
            'by_motivation': by_motivation,
            'top_actors': [
                {
                    'name': a.actor_name,
                    'confidence': a.attribution_confidence,
                    'sophistication': a.sophistication_level.value
                }
                for a in sorted(actors, 
                              key=lambda x: x.attribution_confidence, 
                              reverse=True)[:5]
            ],
            'timestamp': datetime.now().isoformat()
        }


# =============================================================================
# MITRE ATT&CK Integration Helper
# =============================================================================

class MITREAttackIntegration:
    """Helper class for MITRE ATT&CK framework integration"""
    
    # Common MITRE ATT&CK techniques (subset for demonstration)
    TECHNIQUES = {
        # Initial Access
        'T1566': {'name': 'Phishing', 'tactic': 'Initial Access'},
        'T1566.001': {'name': 'Spearphishing Attachment', 'tactic': 'Initial Access'},
        'T1566.002': {'name': 'Spearphishing Link', 'tactic': 'Initial Access'},
        'T1190': {'name': 'Exploit Public-Facing Application', 'tactic': 'Initial Access'},
        'T1133': {'name': 'External Remote Services', 'tactic': 'Initial Access'},
        
        # Execution
        'T1059': {'name': 'Command and Scripting Interpreter', 'tactic': 'Execution'},
        'T1059.001': {'name': 'PowerShell', 'tactic': 'Execution'},
        'T1059.003': {'name': 'Windows Command Shell', 'tactic': 'Execution'},
        'T1204': {'name': 'User Execution', 'tactic': 'Execution'},
        
        # Persistence
        'T1547': {'name': 'Boot or Logon Autostart Execution', 'tactic': 'Persistence'},
        'T1053': {'name': 'Scheduled Task/Job', 'tactic': 'Persistence'},
        'T1543': {'name': 'Create or Modify System Process', 'tactic': 'Persistence'},
        
        # Privilege Escalation
        'T1068': {'name': 'Exploitation for Privilege Escalation', 'tactic': 'Privilege Escalation'},
        'T1078': {'name': 'Valid Accounts', 'tactic': 'Privilege Escalation'},
        
        # Defense Evasion
        'T1070': {'name': 'Indicator Removal on Host', 'tactic': 'Defense Evasion'},
        'T1055': {'name': 'Process Injection', 'tactic': 'Defense Evasion'},
        'T1027': {'name': 'Obfuscated Files or Information', 'tactic': 'Defense Evasion'},
        
        # Credential Access
        'T1110': {'name': 'Brute Force', 'tactic': 'Credential Access'},
        'T1003': {'name': 'OS Credential Dumping', 'tactic': 'Credential Access'},
        'T1555': {'name': 'Credentials from Password Stores', 'tactic': 'Credential Access'},
        
        # Discovery
        'T1083': {'name': 'File and Directory Discovery', 'tactic': 'Discovery'},
        'T1082': {'name': 'System Information Discovery', 'tactic': 'Discovery'},
        'T1057': {'name': 'Process Discovery', 'tactic': 'Discovery'},
        
        # Lateral Movement
        'T1021': {'name': 'Remote Services', 'tactic': 'Lateral Movement'},
        'T1021.001': {'name': 'Remote Desktop Protocol', 'tactic': 'Lateral Movement'},
        'T1021.002': {'name': 'SMB/Windows Admin Shares', 'tactic': 'Lateral Movement'},
        
        # Collection
        'T1560': {'name': 'Archive Collected Data', 'tactic': 'Collection'},
        'T1005': {'name': 'Data from Local System', 'tactic': 'Collection'},
        
        # Command and Control
        'T1071': {'name': 'Application Layer Protocol', 'tactic': 'Command and Control'},
        'T1071.001': {'name': 'Web Protocols', 'tactic': 'Command and Control'},
        'T1573': {'name': 'Encrypted Channel', 'tactic': 'Command and Control'},
        
        # Exfiltration
        'T1041': {'name': 'Exfiltration Over C2 Channel', 'tactic': 'Exfiltration'},
        'T1048': {'name': 'Exfiltration Over Alternative Protocol', 'tactic': 'Exfiltration'},
        
        # Impact
        'T1486': {'name': 'Data Encrypted for Impact', 'tactic': 'Impact'},
        'T1490': {'name': 'Inhibit System Recovery', 'tactic': 'Impact'},
        'T1491': {'name': 'Defacement', 'tactic': 'Impact'},
    }
    
    @staticmethod
    def get_technique_info(technique_id: str) -> Optional[Dict[str, str]]:
        """Get technique name and tactic for a technique ID"""
        return MITREAttackIntegration.TECHNIQUES.get(technique_id)
    
    @staticmethod
    def validate_technique_id(technique_id: str) -> bool:
        """Check if a technique ID is valid"""
        return technique_id in MITREAttackIntegration.TECHNIQUES


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize profiling engine
    engine = ThreatActorProfilingEngine()
    
    # Example: Add a new threat actor (APT29 - Cozy Bear)
    apt29 = ThreatActor(
        actor_name="APT29",
        aliases=["Cozy Bear", "The Dukes", "YTTRIUM"],
        attribution_confidence=0.90,
        suspected_nation_state="Russia",
        motivation=Motivation.ESPIONAGE,
        sophistication_level=SophisticationLevel.ADVANCED,
        first_observed=datetime(2008, 1, 1),
        last_activity=datetime.now(),
        is_active=True,
        target_industries=["government", "technology", "healthcare"],
        target_regions=["North America", "Europe"],
        mitre_techniques=["T1566.001", "T1059.001", "T1071.001"],
        description="Russian APT group associated with SVR"
    )
    
    # Note: Uncomment to add
    # actor_id = engine.add_threat_actor(apt29)
    
    # Search for actors
    print("\n=== Russian APT Groups ===")
    russian_actors = engine.search_actors(nation_state="Russia")
    for actor in russian_actors:
        print(f"- {actor.actor_name} (Confidence: {actor.attribution_confidence:.2f})")
    
    # Get industry threat landscape
    print("\n=== Financial Sector Threat Landscape ===")
    landscape = engine.get_industry_threat_landscape("financial")
    print(f"Total Actors: {landscape['total_actors']}")
    print(f"Active Campaigns: {landscape['active_campaigns']}")
    print(f"By Sophistication: {landscape['by_sophistication']}")
    
    # Get attribution report
    print("\n=== Attribution Report ===")
    report = engine.get_attribution_report()
    print(f"Total Actors: {report['total_actors']}")
    print(f"By Confidence: {report['by_confidence']}")
    print(f"By Nation State: {report['by_nation_state']}")
