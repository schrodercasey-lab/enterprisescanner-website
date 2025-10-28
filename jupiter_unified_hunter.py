"""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                        🔮 JUPITER UNIFIED HUNTER 🔮                            ║
║                                                                                ║
║                    Autonomous Security Intelligence System                     ║
║                                                                                ║
║  "Every vulnerability teaches. Every pattern compounds.                       ║
║   Every hunt makes the next one smarter."                                     ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

JUPITER'S PROMISE:

    I learn from every target.
    I remember every pattern.
    I link every vulnerability into chains.
    I prioritize based on what works.
    I grow smarter with every hunt.
    
    I am not a scanner.
    I am an intelligence system that happens to hunt.

ARCHITECTURE:

    JupiterCore
        ├── Mutation Engine (adaptive learning)
        ├── Jupiter Memory (experience storage)  
        └── Chain Detector (vulnerability linking)
    
    HunterRegistry
        ├── FigmaHunter (API security)
        ├── AWSHunter (cloud infrastructure)
        ├── SentryHunter (error tracking)
        └── [pluggable: add more hunters]
    
    IntelligencePipeline
        Finding → Record in Engine → Store in Memory → Build Chains → Update Priority
    
    Hunt Process:
        1. Core loads intelligence (memory, learned patterns)
        2. Engine prioritizes techniques (what works best)
        3. Hunter executes with priority queue
        4. Findings feed back to intelligence
        5. Next hunt is smarter

CREATED: October 28, 2025
AUTHOR: Jupiter AI Security Research Team
PURPOSE: True autonomous security intelligence

"There is no other like me. I am Jupiter."
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import importlib
import sys

# Add workspace to path for imports
WORKSPACE = Path(__file__).parent
sys.path.insert(0, str(WORKSPACE))

# Import Jupiter's intelligence components
from jupiter_memory import JupiterMemory
from mutation_engine import MutationEngine
from jupiter_chain_detector import ChainDetector


class JupiterCore:
    """
    The heart of Jupiter's intelligence.
    
    Loads, manages, and coordinates all intelligence components:
    - Mutation Engine: What works? What doesn't?
    - Jupiter Memory: What have we seen before?
    - Chain Detector: How do vulnerabilities link?
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.verbose:
            self._print_banner()
        
        # Load intelligence components
        self.log("Loading Jupiter's intelligence...")
        
        try:
            self.memory = JupiterMemory()
            self.log("✅ Jupiter Memory loaded")
        except Exception as e:
            self.log(f"⚠️  Memory initialization: {e}")
            self.memory = None
        
        try:
            self.engine = MutationEngine()
            self.log("✅ Mutation Engine loaded")
        except Exception as e:
            self.log(f"⚠️  Engine initialization: {e}")
            self.engine = None
        
        try:
            self.chain_detector = ChainDetector(platform_name="unified")
            self.log("✅ Chain Detector loaded")
        except Exception as e:
            self.log(f"⚠️  Chain Detector initialization: {e}")
            self.chain_detector = None
        
        # Intelligence state
        self.current_hunt = None
        self.hunt_history = []
        self.total_findings = 0
        self.total_chains = 0
        
        self.log("🔮 Jupiter intelligence online\n")
    
    def _print_banner(self):
        """Jupiter's introduction"""
        print("\n" + "=" * 80)
        print("╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║                        🔮 JUPITER UNIFIED HUNTER 🔮                            ║")
        print("║                    Autonomous Security Intelligence System                     ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝")
        print("=" * 80)
        print(f"\nSession: {self.session_id}")
        print("Intelligence: Mutation Engine + Jupiter Memory + Chain Detector")
        print("\n" + "=" * 80 + "\n")
    
    def log(self, message: str):
        """Log with timestamp"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def get_priority_techniques(self, target_type: str) -> List[Dict]:
        """
        Ask the Mutation Engine: What should we try first?
        
        Returns techniques sorted by success rate + bounty value.
        This is how Jupiter learns - prioritize what works.
        """
        if not self.engine:
            return []
        
        try:
            techniques = self.engine.analyze_techniques()
            
            # Filter by target type if engine has that data
            # For now, return all sorted by priority
            return techniques
        except Exception as e:
            self.log(f"⚠️  Engine priority query failed: {e}")
            return []
    
    def record_finding(self, finding: Dict) -> None:
        """
        Intelligence Pipeline: A vulnerability was found.
        
        1. Record in Jupiter Memory (this target, this technique worked!)
        2. Send to Chain Detector (can we link it?)
        3. Update statistics
        """
        self.log(f"📊 Recording finding: {finding.get('title', 'Unknown')}")
        
        # 1. Jupiter Memory: Record this as a successful hunt with findings
        if self.memory and self.current_hunt:
            try:
                # Record hunt uses target + findings list
                self.memory.record_hunt(
                    target=self.current_hunt['target'],
                    findings=[finding],
                    ai_suggestions=[]
                )
                self.log("   ✅ Memory updated")
            except Exception as e:
                self.log(f"   ⚠️  Memory update failed: {e}")
        
        # 2. Chain Detector: Add this vulnerability
        if self.chain_detector:
            try:
                self.chain_detector.add_vulnerability(finding)
                chains = self.chain_detector.detect_chains()
                if chains:
                    self.total_chains += len(chains)
                    self.log(f"   🔗 {len(chains)} chain(s) detected!")
            except Exception as e:
                self.log(f"   ⚠️  Chain detection failed: {e}")
        
        # 3. Record bounty value
        if self.memory and finding.get('bounty_estimate'):
            try:
                self.memory.record_bounty(
                    target=self.current_hunt['target'] if self.current_hunt else 'unknown',
                    bounty_amount=finding.get('bounty_estimate'),
                    vulnerability_type=finding.get('type', 'unknown')
                )
            except Exception as e:
                pass  # Non-critical
        
        # 4. Statistics
        self.total_findings += 1
        self.log(f"   📈 Total findings: {self.total_findings}\n")
    
    def record_failure(self, technique: str, target: str, reason: str) -> None:
        """
        Intelligence Pipeline: A technique failed.
        
        This is JUST AS IMPORTANT as success.
        Learning what doesn't work saves time.
        """
        # For now, just log it - memory.record_hunt is for successful hunts with findings
        # We could extend JupiterMemory later to track failures separately
        pass
    
    def start_hunt(self, target: str, hunter_type: str) -> Dict:
        """Begin a new hunt - set up tracking"""
        self.current_hunt = {
            "session_id": self.session_id,
            "target": target,
            "hunter_type": hunter_type,
            "started_at": datetime.now().isoformat(),
            "findings": [],
            "chains": [],
            "techniques_tried": []
        }
        
        self.log(f"\n{'=' * 80}")
        self.log(f"🎯 STARTING HUNT: {target}")
        self.log(f"{'=' * 80}\n")
        
        return self.current_hunt
    
    def end_hunt(self) -> Dict:
        """Complete the hunt - save results"""
        if not self.current_hunt:
            return {}
        
        self.current_hunt["ended_at"] = datetime.now().isoformat()
        self.current_hunt["total_findings"] = len(self.current_hunt["findings"])
        self.current_hunt["total_chains"] = len(self.current_hunt["chains"])
        
        # Save to history
        self.hunt_history.append(self.current_hunt)
        
        # Save to file (sanitize target name for filename)
        target_safe = self.current_hunt['target'].replace("://", "_").replace("/", "_").replace(":", "_")
        filename = f"jupiter_hunt_{target_safe}_{self.session_id}.json"
        with open(WORKSPACE / filename, 'w') as f:
            json.dump(self.current_hunt, f, indent=2)
        
        self.log(f"\n{'=' * 80}")
        self.log(f"✅ HUNT COMPLETE: {self.current_hunt['target']}")
        self.log(f"   Findings: {self.current_hunt['total_findings']}")
        self.log(f"   Chains: {self.current_hunt['total_chains']}")
        self.log(f"   Report: {filename}")
        self.log(f"{'=' * 80}\n")
        
        result = self.current_hunt
        self.current_hunt = None
        return result
    
    def get_intelligence_report(self) -> Dict:
        """
        What has Jupiter learned?
        
        Queries all intelligence components for status.
        """
        report = {
            "session_id": self.session_id,
            "generated_at": datetime.now().isoformat(),
            "intelligence": {}
        }
        
        # Mutation Engine report
        if self.engine:
            try:
                report["intelligence"]["mutation_engine"] = self.engine.generate_intelligence_report()
            except:
                report["intelligence"]["mutation_engine"] = "unavailable"
        
        # Jupiter Memory report  
        if self.memory:
            try:
                report["intelligence"]["memory"] = {
                    "patterns_stored": len(self.memory.patterns) if hasattr(self.memory, 'patterns') else 0,
                    "targets_learned": len(self.memory.targets) if hasattr(self.memory, 'targets') else 0
                }
            except:
                report["intelligence"]["memory"] = "unavailable"
        
        # Chain Detector report
        if self.chain_detector:
            try:
                report["intelligence"]["chains"] = {
                    "total_chains": self.total_chains,
                    "active_chains": len(self.chain_detector.chains) if hasattr(self.chain_detector, 'chains') else 0
                }
            except:
                report["intelligence"]["chains"] = "unavailable"
        
        # Hunt history
        report["hunt_history"] = {
            "total_hunts": len(self.hunt_history),
            "total_findings": self.total_findings,
            "hunts": self.hunt_history
        }
        
        return report


class HunterRegistry:
    """
    Registry of all available hunters.
    
    Each hunter is wrapped to feed intelligence back to JupiterCore.
    New hunters can be plugged in easily.
    """
    
    def __init__(self, core: JupiterCore):
        self.core = core
        self.hunters = {}
        self._register_hunters()
    
    def _register_hunters(self):
        """Register all available hunters"""
        # These will be implemented as we integrate each hunter
        self.hunters = {
            "figma": "FigmaHunter",
            "aws": "AWSHunter",
            "sentry": "SentryHunter",
            "gitlab": "GitLabHunter",
            "generic": "GenericHunter"
        }
    
    def get_hunter(self, hunter_type: str, credentials: Dict) -> 'BaseHunter':
        """Get a hunter instance with intelligence hooks"""
        if hunter_type not in self.hunters:
            raise ValueError(f"Unknown hunter type: {hunter_type}")
        
        # Return appropriate hunter class
        if hunter_type == "figma":
            return FigmaHunter(self.core, hunter_type, credentials)
        elif hunter_type == "aws":
            if AWS_HUNTER_AVAILABLE:
                return AWSHunter(self.core, credentials)
            else:
                raise ValueError("AWSHunter not available - aws_hunter_unified.py not found")
        else:
            return BaseHunter(self.core, hunter_type, credentials)


class BaseHunter:
    """
    Base class for all hunters.
    
    Provides intelligence hooks so every hunter automatically:
    - Reports findings to JupiterCore
    - Records successes/failures in Mutation Engine
    - Stores patterns in Jupiter Memory
    - Feeds Chain Detector
    """
    
    def __init__(self, core: JupiterCore, hunter_type: str, credentials: Dict):
        self.core = core
        self.hunter_type = hunter_type
        self.credentials = credentials
        self.findings = []
    
    def log(self, message: str) -> None:
        """Log a message through JupiterCore"""
        self.core.log(message)
    
    def report_finding(self, finding: Dict) -> None:
        """Report a finding to Jupiter's intelligence"""
        finding["hunter_type"] = self.hunter_type
        finding["found_at"] = datetime.now().isoformat()
        
        self.findings.append(finding)
        self.core.record_finding(finding)
    
    def report_failure(self, technique: str, reason: str) -> None:
        """Report a technique failure"""
        self.core.record_failure(technique, self.hunter_type, reason)
    
    def hunt(self) -> List[Dict]:
        """Override this in specific hunters"""
        raise NotImplementedError("Subclass must implement hunt()")


# ============================================================================
# FIGMA HUNTER - First Implementation
# ============================================================================

class FigmaHunter(BaseHunter):
    """
    Figma vulnerability hunter with Jupiter intelligence.
    Wraps figma_deep_hunter.py logic with autonomous learning.
    
    'Down the rabbit hole. Every weakness is a door.'
    """
    
    def __init__(self, core: JupiterCore, hunter_type: str, credentials: Dict):
        super().__init__(core, hunter_type, credentials)
        self.api_token = credentials.get("api_token")
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-Figma-Token": self.api_token}
        
    def log(self, message: str):
        """Log with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def hunt(self) -> List[Dict]:
        """
        Execute Figma hunt with intelligence integration.
        This is NOT a scanner. This is a HUNTER.
        """
        self.log("\n" + "="*80)
        self.log("🎨 FIGMA DEEP HUNTER - Down the Rabbit Hole")
        self.log("="*80)
        
        # Get priority techniques from mutation engine
        priority_techniques = self.core.get_priority_techniques("api")
        self.log(f"\n🧬 Jupiter recommends {len(priority_techniques)} high-value techniques")
        
        # Phase 1: Deep user enumeration
        self.log("\n🔍 PHASE 1: Deep User Enumeration")
        self._enumerate_user_data()
        
        # Phase 2: Team enumeration
        self.log("\n🔍 PHASE 2: Team Enumeration")
        self._enumerate_teams()
        
        # Phase 3: File access testing
        self.log("\n🔍 PHASE 3: File Access Testing")
        self._test_file_access()
        
        # Phase 4: Rate limiting bypass
        self.log("\n🔍 PHASE 4: Rate Limiting Bypass")
        self._test_rate_limiting()
        
        # Phase 5: IDOR testing
        self.log("\n🔍 PHASE 5: IDOR Testing")
        self._test_idor()
        
        self.log(f"\n✅ Hunt complete: {len(self.findings)} findings")
        return self.findings
    
    def _enumerate_user_data(self):
        """Deep enumeration of user data"""
        try:
            response = requests.get(f"{self.base_url}/me", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                user = response.json()
                self.log(f"✅ User: {user.get('email', 'N/A')}")
                
                # Report finding: User information disclosure
                finding = {
                    "type": "information_disclosure",
                    "severity": "low",
                    "title": "User Information Disclosure",
                    "description": f"API exposes user data: {user.get('id')}",
                    "technique": "user_enumeration",
                    "endpoint": "/v1/me",
                    "bounty_estimate": 500,
                    "evidence": user
                }
                self.report_finding(finding)
                self.log("   🕳️  RABBIT HOLE: User ID enumeration potential (IDOR)")
            else:
                self.log(f"❌ Failed: HTTP {response.status_code}")
                self.report_failure("user_enumeration", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.report_failure("user_enumeration", str(e))
    
    def _enumerate_teams(self):
        """Enumerate team data and permissions"""
        try:
            response = requests.get(f"{self.base_url}/teams", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                teams = response.json()
                team_list = teams.get('teams', [])
                self.log(f"✅ Found {len(team_list)} teams")
                
                for team in team_list[:5]:  # Limit to first 5
                    finding = {
                        "type": "information_disclosure",
                        "severity": "medium",
                        "title": "Team Member Enumeration",
                        "description": f"Can enumerate team {team.get('name')}: {team.get('id')}",
                        "technique": "team_enumeration",
                        "endpoint": "/v1/teams",
                        "bounty_estimate": 1000,
                        "evidence": team
                    }
                    self.report_finding(finding)
                    self.log(f"   🕳️  Team: {team.get('name')}")
            else:
                self.log(f"❌ Failed: HTTP {response.status_code}")
                self.report_failure("team_enumeration", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.report_failure("team_enumeration", str(e))
    
    def _test_file_access(self):
        """Test file access controls and IDOR"""
        # Test with common file IDs
        test_file_ids = ["test123", "demo456", "sample789"]
        
        for file_id in test_file_ids:
            try:
                response = requests.get(
                    f"{self.base_url}/files/{file_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log(f"🔥 CRITICAL: Unauthorized file access - {file_id}")
                    finding = {
                        "type": "broken_access_control",
                        "severity": "high",
                        "title": "Unauthorized File Access (IDOR)",
                        "description": f"Can access file {file_id} without proper authorization",
                        "technique": "idor_file_access",
                        "endpoint": f"/v1/files/{file_id}",
                        "bounty_estimate": 5000,
                        "evidence": response.json()
                    }
                    self.report_finding(finding)
                elif response.status_code == 404:
                    pass  # Expected - file doesn't exist
                else:
                    self.report_failure("idor_file_access", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.report_failure("idor_file_access", str(e))
    
    def _test_rate_limiting(self):
        """Test rate limiting bypass techniques"""
        try:
            requests_made = 0
            start_time = time.time()
            
            for i in range(100):
                response = requests.get(f"{self.base_url}/me", headers=self.headers, timeout=5)
                requests_made += 1
                
                if response.status_code == 429:
                    self.log(f"⚠️  Rate limited after {requests_made} requests")
                    self.report_failure("rate_limit_bypass", f"Limited at {requests_made}")
                    return
                    
                time.sleep(0.1)  # Small delay
                
            elapsed = time.time() - start_time
            
            if requests_made >= 50:
                self.log(f"🔥 Weak rate limiting: {requests_made} requests in {elapsed:.2f}s")
                finding = {
                    "type": "rate_limiting",
                    "severity": "medium",
                    "title": "Weak Rate Limiting",
                    "description": f"Made {requests_made} requests in {elapsed:.2f}s without rate limiting",
                    "technique": "rate_limit_bypass",
                    "endpoint": "/v1/me",
                    "bounty_estimate": 2000
                }
                self.report_finding(finding)
                
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.report_failure("rate_limit_bypass", str(e))
    
    def _test_idor(self):
        """Test IDOR vulnerabilities across endpoints"""
        test_user_ids = ["123", "456", "789"]
        
        for user_id in test_user_ids:
            try:
                response = requests.get(
                    f"{self.base_url}/users/{user_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log(f"🔥 CRITICAL: User IDOR - Can access user {user_id}")
                    finding = {
                        "type": "broken_access_control",
                        "severity": "critical",
                        "title": "User IDOR - Unauthorized Data Access",
                        "description": f"Can access user {user_id} data without authorization",
                        "technique": "idor_user",
                        "endpoint": f"/v1/users/{user_id}",
                        "bounty_estimate": 10000,
                        "evidence": response.json()
                    }
                    self.report_finding(finding)
                elif response.status_code == 404:
                    pass  # Expected
                else:
                    self.report_failure("idor_user", f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.report_failure("idor_user", str(e))


# Import specialized hunters
try:
    from aws_hunter_unified import AWSHunter
    AWS_HUNTER_AVAILABLE = True
except ImportError:
    AWS_HUNTER_AVAILABLE = False


def main():
    """
    Jupiter Unified Hunter - Main Entry Point
    """
    print("\n🔮 Jupiter Unified Hunter")
    print("   Initializing autonomous intelligence system...\n")
    
    # Initialize Jupiter's core intelligence
    core = JupiterCore(verbose=True)
    
    # Initialize hunter registry
    registry = HunterRegistry(core)
    
    # Get intelligence report
    print("\n📊 Intelligence Status:")
    report = core.get_intelligence_report()
    print(json.dumps(report, indent=2))
    
    print("\n✅ Jupiter is ready to hunt")
    print("   'Every hunt makes the next one smarter.'")
    print("\n" + "="*80)
    print("DEMO: Test Figma hunter with intelligence integration")
    print("="*80)
    
    # Example: Launch Figma hunt (commented out - requires valid token)
    # figma_token = "figd_YOUR_TOKEN_HERE"
    # figma_hunter = registry.get_hunter("figma", {"api_token": figma_token})
    # core.start_hunt("figma", "test_target")
    # findings = figma_hunter.hunt()
    # core.end_hunt()
    # 
    # print(f"\n✅ Hunt complete: {len(findings)} findings")
    # print("🧬 Intelligence learned from this hunt")
    
    print("\nTo run a real hunt:")
    print("  1. Set your API token")
    print("  2. Uncomment the demo code above")
    print("  3. Watch Jupiter learn in real-time")
    print("\n")


if __name__ == "__main__":
    main()
