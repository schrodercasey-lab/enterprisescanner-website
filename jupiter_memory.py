"""
JUPITER MEMORY - Learning System
Saves findings across runs so Jupiter gets smarter over time.

This is the foundation for the Mutation Engine.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class JupiterMemory:
    """
    Persistent memory system for Jupiter.
    Learns from every hunt to improve future scans.
    
    This is how Jupiter "remembers" and gets smarter.
    """
    
    def __init__(self, memory_file: str = "jupiter_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load existing memory or create new."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Initialize fresh memory
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "total_hunts": 0,
            "targets": {},  # Track what we've learned per target
            "techniques": {
                "jwt_attacks": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "graphql_injection": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "idor": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "oauth_bypass": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "ssrf": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "mass_assignment": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "xss": {"attempts": 0, "successes": 0, "bounty_earned": 0},
                "sqli": {"attempts": 0, "successes": 0, "bounty_earned": 0},
            },
            "ai_suggestions": [],  # Track AI-generated ideas
            "effective_endpoints": [],  # Endpoints that yielded findings
        }
    
    def _save_memory(self):
        """Persist memory to disk."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def record_hunt(self, target: str, findings: List[Dict], ai_suggestions: List[Dict] = None):
        """
        Record a hunt and what was learned.
        
        Args:
            target: Target domain (e.g., "shopify.com")
            findings: List of vulnerabilities found
            ai_suggestions: AI-generated attack ideas (even if not exploitable)
        """
        self.memory["total_hunts"] += 1
        
        # Initialize target memory if first time
        if target not in self.memory["targets"]:
            self.memory["targets"][target] = {
                "first_scanned": datetime.now().isoformat(),
                "total_scans": 0,
                "total_findings": 0,
                "findings_history": [],
                "technologies": [],
                "effective_endpoints": [],
                "failed_techniques": []
            }
        
        target_mem = self.memory["targets"][target]
        target_mem["total_scans"] += 1
        target_mem["last_scanned"] = datetime.now().isoformat()
        target_mem["total_findings"] += len(findings)
        
        # Record findings
        for finding in findings:
            target_mem["findings_history"].append({
                "date": datetime.now().isoformat(),
                "type": finding.get("type", "unknown"),
                "severity": finding.get("severity", "unknown"),
                "endpoint": finding.get("endpoint", "unknown")
            })
            
            # Track which endpoints are productive
            endpoint = finding.get("endpoint", "")
            if endpoint and endpoint not in target_mem["effective_endpoints"]:
                target_mem["effective_endpoints"].append(endpoint)
            
            # Update technique success
            technique = self._map_to_technique(finding.get("type", ""))
            if technique in self.memory["techniques"]:
                self.memory["techniques"][technique]["attempts"] += 1
                self.memory["techniques"][technique]["successes"] += 1
        
        # Record AI suggestions (even if not exploitable - they're learning data)
        if ai_suggestions:
            for suggestion in ai_suggestions:
                self.memory["ai_suggestions"].append({
                    "date": datetime.now().isoformat(),
                    "target": target,
                    "suggestion": suggestion.get("description", ""),
                    "exploited": False  # Will be updated if it works
                })
        
        self._save_memory()
        print(f"\n💾 Memory updated: {len(findings)} findings recorded")
    
    def _map_to_technique(self, finding_type: str) -> str:
        """Map finding type to technique category."""
        type_lower = finding_type.lower()
        
        if "jwt" in type_lower or "token" in type_lower:
            return "jwt_attacks"
        elif "graphql" in type_lower:
            return "graphql_injection"
        elif "idor" in type_lower or "object reference" in type_lower:
            return "idor"
        elif "oauth" in type_lower or "redirect" in type_lower:
            return "oauth_bypass"
        elif "ssrf" in type_lower:
            return "ssrf"
        elif "mass assignment" in type_lower:
            return "mass_assignment"
        elif "xss" in type_lower:
            return "xss"
        elif "sql" in type_lower or "injection" in type_lower:
            return "sqli"
        
        return "unknown"
    
    def get_target_intel(self, target: str) -> Optional[Dict]:
        """
        Retrieve what we've learned about a target.
        
        Returns:
            Dictionary with learned intelligence, or None if first scan
        """
        return self.memory["targets"].get(target)
    
    def get_technique_priority(self) -> List[tuple]:
        """
        Get techniques sorted by success rate.
        This tells Jupiter what attacks to prioritize.
        
        Returns:
            List of (technique, success_rate, bounty_earned) tuples
        """
        priorities = []
        
        for tech, stats in self.memory["techniques"].items():
            attempts = stats["attempts"]
            successes = stats["successes"]
            bounty = stats["bounty_earned"]
            
            # Calculate success rate
            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            
            priorities.append((tech, success_rate, bounty))
        
        # Sort by success rate, then bounty
        priorities.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        return priorities
    
    def should_skip_technique(self, target: str, technique: str) -> bool:
        """
        Decide if Jupiter should skip a technique on this target.
        
        Args:
            target: Target domain
            technique: Technique name (e.g., "jwt_attacks")
        
        Returns:
            True if this technique has failed multiple times on this target
        """
        target_mem = self.memory["targets"].get(target)
        if not target_mem:
            return False  # First time, try everything
        
        # If a technique failed 3+ times on this target, skip it
        failed = target_mem.get("failed_techniques", [])
        failure_count = sum(1 for f in failed if f == technique)
        
        return failure_count >= 3
    
    def record_bounty(self, technique: str, amount: int):
        """
        Record a bounty earned from a specific technique.
        This is how the Mutation Engine learns value.
        
        Args:
            technique: Technique that earned bounty
            amount: Bounty amount in USD
        """
        if technique in self.memory["techniques"]:
            self.memory["techniques"][technique]["bounty_earned"] += amount
            self._save_memory()
            print(f"\n💰 Bounty recorded: {technique} earned ${amount:,}")
    
    def get_learning_summary(self) -> str:
        """
        Generate a human-readable summary of what Jupiter has learned.
        """
        summary = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    🧠 JUPITER MEMORY BANK                      ║
╚═══════════════════════════════════════════════════════════════╝

Total Hunts: {self.memory["total_hunts"]}
Targets Scanned: {len(self.memory["targets"])}
AI Suggestions Tested: {len(self.memory["ai_suggestions"])}

╔═══════════════════════════════════════════════════════════════╗
║                    🎯 TECHNIQUE EFFECTIVENESS                  ║
╚═══════════════════════════════════════════════════════════════╝
"""
        
        priorities = self.get_technique_priority()
        for i, (tech, success_rate, bounty) in enumerate(priorities[:5], 1):
            stats = self.memory["techniques"][tech]
            summary += f"\n{i}. {tech.replace('_', ' ').title()}\n"
            summary += f"   Success Rate: {success_rate:.1f}% ({stats['successes']}/{stats['attempts']})\n"
            summary += f"   Bounty Earned: ${bounty:,}\n"
        
        summary += f"\n\n╔═══════════════════════════════════════════════════════════════╗\n"
        summary += f"║                    🎓 TARGET KNOWLEDGE                        ║\n"
        summary += f"╚═══════════════════════════════════════════════════════════════╝\n"
        
        for target, data in list(self.memory["targets"].items())[:3]:
            summary += f"\n{target}:\n"
            summary += f"  Scans: {data['total_scans']}\n"
            summary += f"  Findings: {data['total_findings']}\n"
            summary += f"  Last Scanned: {data.get('last_scanned', 'Never')}\n"
        
        return summary
    
    def export_for_mutation_engine(self) -> Dict:
        """
        Export memory in format ready for Mutation Engine.
        
        Returns:
            Structured data for strategy mutation
        """
        return {
            "technique_weights": {
                tech: {
                    "weight": (stats["successes"] / max(stats["attempts"], 1)) * 10,
                    "priority": "HIGH" if stats["bounty_earned"] > 10000 else "MEDIUM",
                    "bounty_multiplier": 1 + (stats["bounty_earned"] / 50000)
                }
                for tech, stats in self.memory["techniques"].items()
            },
            "target_profiles": {
                target: {
                    "scan_priority": data["total_findings"] / max(data["total_scans"], 1),
                    "effective_endpoints": data["effective_endpoints"],
                    "avoid_techniques": data.get("failed_techniques", [])
                }
                for target, data in self.memory["targets"].items()
            }
        }


def test_memory():
    """Test the memory system."""
    mem = JupiterMemory("jupiter_memory_test.json")
    
    # Simulate a hunt
    mem.record_hunt(
        target="shopify.com",
        findings=[
            {
                "type": "JWT Algorithm Confusion",
                "severity": "CRITICAL",
                "endpoint": "https://admin.shopify.com/api/auth"
            }
        ],
        ai_suggestions=[
            {"description": "Cloudflare Cache Deception"},
            {"description": "GraphQL Introspection"}
        ]
    )
    
    # Simulate a bounty
    mem.record_bounty("jwt_attacks", 15000)
    
    # Show what we learned
    print(mem.get_learning_summary())
    
    # Check priorities
    print("\n📊 Technique Priorities:")
    for tech, rate, bounty in mem.get_technique_priority()[:3]:
        print(f"  {tech}: {rate:.1f}% success, ${bounty:,} earned")


if __name__ == "__main__":
    test_memory()
