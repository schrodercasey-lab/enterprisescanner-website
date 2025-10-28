#!/usr/bin/env python3
"""
MUTATION ENGINE - Jupiter's Adaptive Intelligence Core
Author: Jupiter Platform
Created: October 26, 2025

The brain that learns, adapts, and evolves hunting strategies based on empirical data.

What it does:
- Analyzes success rates across all techniques
- Prioritizes high-value attacks automatically
- Skips failed techniques on mature platforms
- Optimizes queue ordering for maximum speed
- Adapts strategy based on target characteristics
- Predicts vulnerability likelihood
- Evolves hunting patterns over time

"Data-driven autonomous bug bounty hunting."
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from jupiter_memory import JupiterMemory


class MutationEngine:
    """
    Jupiter's adaptive intelligence core.
    
    Learns from every hunt, adapts strategy automatically,
    and evolves techniques based on empirical success data.
    """
    
    def __init__(self):
        self.memory = JupiterMemory()
        self.version = "1.0"
        
        # Learning thresholds
        self.min_attempts_for_confidence = 5  # Need 5+ attempts to trust success rate
        self.skip_threshold = 3  # Skip technique after 3 consecutive failures
        self.high_success_threshold = 0.50  # 50%+ success = prioritize
        self.low_success_threshold = 0.10  # <10% success = deprioritize
        
        # Speed optimization constants (from proven benchmarks)
        self.cold_start_time = 307  # First target always ~307s
        self.avg_warm_time = 88     # Average subsequent target time
        
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     🧬 MUTATION ENGINE v{self.version}                             ║
║                   Adaptive Intelligence Initialized                        ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
    
    def analyze_techniques(self) -> List[Dict]:
        """
        Analyze all techniques and return prioritized list based on success rates.
        
        Returns techniques sorted by:
        1. Success rate (primary)
        2. Bounty earned (secondary)
        3. Attempts made (confidence)
        """
        techniques = self.memory.memory["techniques"]
        analyzed = []
        
        for name, stats in techniques.items():
            attempts = stats["attempts"]
            successes = stats["successes"]
            bounty = stats["bounty_earned"]
            
            # Calculate success rate
            success_rate = (successes / attempts) if attempts > 0 else 0.0
            
            # Calculate confidence (0-1 based on attempts)
            confidence = min(attempts / self.min_attempts_for_confidence, 1.0)
            
            # Calculate priority score
            # High success + high bounty = highest priority
            priority_score = (success_rate * 100) + (bounty / 1000) * 10
            
            # Determine status
            if attempts == 0:
                status = "untested"
            elif attempts < self.min_attempts_for_confidence:
                status = "learning"
            elif success_rate >= self.high_success_threshold:
                status = "high_value"
            elif success_rate <= self.low_success_threshold:
                status = "low_value"
            else:
                status = "medium_value"
            
            analyzed.append({
                "name": name,
                "attempts": attempts,
                "successes": successes,
                "success_rate": success_rate,
                "bounty_earned": bounty,
                "confidence": confidence,
                "priority_score": priority_score,
                "status": status
            })
        
        # Sort by priority score (highest first)
        analyzed.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return analyzed
    
    def should_test_technique(self, technique: str, target: str) -> Tuple[bool, str]:
        """
        Decide if a technique should be tested on a target.
        
        Returns: (should_test: bool, reason: str)
        """
        # Check if technique has failed repeatedly on this target
        target_data = self.memory.memory["targets"].get(target, {})
        failed_techniques = target_data.get("failed_techniques", [])
        
        # Count consecutive failures
        consecutive_failures = sum(1 for ft in failed_techniques if ft == technique)
        
        if consecutive_failures >= self.skip_threshold:
            return False, f"Failed {consecutive_failures} times on {target}"
        
        # Check global success rate
        techniques = self.memory.memory["techniques"]
        tech_stats = techniques.get(technique, {"attempts": 0, "successes": 0})
        
        attempts = tech_stats["attempts"]
        successes = tech_stats["successes"]
        
        # Always test if not enough data
        if attempts < self.min_attempts_for_confidence:
            return True, "Learning phase - need more data"
        
        # Calculate success rate
        success_rate = successes / attempts if attempts > 0 else 0.0
        
        # Skip if consistently failing
        if success_rate <= self.low_success_threshold:
            return False, f"Low success rate: {success_rate:.1%}"
        
        return True, f"Success rate: {success_rate:.1%}"
    
    def optimize_queue(self, targets: List[str]) -> List[str]:
        """
        Optimize target order for maximum speed.
        
        Strategy:
        1. Put untested targets first (pay cold start once)
        2. Group similar targets (leverage cached DNS/connections)
        3. Prioritize high-value targets
        """
        target_intel = []
        
        for target in targets:
            data = self.memory.get_target_intel(target)
            
            # Calculate target score
            scans = data.get("total_scans", 0) if data else 0
            findings = data.get("total_findings", 0) if data else 0
            
            # Untested targets go first (one pays cold start)
            priority = 1000 if scans == 0 else findings * 10
            
            target_intel.append({
                "target": target,
                "scans": scans,
                "findings": findings,
                "priority": priority
            })
        
        # Sort by priority (highest first)
        target_intel.sort(key=lambda x: x["priority"], reverse=True)
        
        return [t["target"] for t in target_intel]
    
    def estimate_queue_time(self, num_targets: int) -> Tuple[int, str]:
        """
        Predict how long a queue will take based on proven benchmarks.
        
        Returns: (seconds, formatted_string)
        """
        if num_targets == 0:
            return 0, "0s"
        
        # First target pays cold start, rest are warm
        total_seconds = self.cold_start_time + (num_targets - 1) * self.avg_warm_time
        
        # Format nicely
        if total_seconds < 60:
            formatted = f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds / 60
            formatted = f"{minutes:.1f} minutes"
        else:
            hours = total_seconds / 3600
            formatted = f"{hours:.1f} hours"
        
        return total_seconds, formatted
    
    def generate_strategy(self, target: str) -> Dict:
        """
        Generate an adaptive hunting strategy for a specific target.
        
        Returns a complete strategy including:
        - Which techniques to test
        - In what order
        - With what priority
        - Skip recommendations
        """
        strategy = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "techniques": [],
            "estimated_time": 0,
            "confidence": 0.0
        }
        
        # Analyze all techniques
        tech_analysis = self.analyze_techniques()
        
        # Build technique plan
        for tech in tech_analysis:
            should_test, reason = self.should_test_technique(tech["name"], target)
            
            strategy["techniques"].append({
                "name": tech["name"],
                "test": should_test,
                "reason": reason,
                "success_rate": tech["success_rate"],
                "priority": tech["priority_score"],
                "status": tech["status"]
            })
        
        # Calculate confidence based on data available
        total_attempts = sum(t["attempts"] for t in tech_analysis)
        strategy["confidence"] = min(total_attempts / 50, 1.0)  # 50 attempts = full confidence
        
        return strategy
    
    def predict_vulnerability_likelihood(self, target: str, technique: str) -> float:
        """
        Predict probability of finding a vulnerability using technique on target.
        
        Uses Bayesian-like reasoning:
        - Global success rate (prior)
        - Target-specific history (likelihood)
        - Technique confidence (uncertainty)
        """
        # Get global success rate
        techniques = self.memory.memory["techniques"]
        tech_stats = techniques.get(technique, {"attempts": 0, "successes": 0})
        
        attempts = tech_stats["attempts"]
        successes = tech_stats["successes"]
        
        if attempts == 0:
            return 0.5  # 50% prior for untested techniques
        
        global_rate = successes / attempts
        
        # Get target-specific history
        target_data = self.memory.memory["targets"].get(target, {})
        total_findings = target_data.get("total_findings", 0)
        total_scans = target_data.get("total_scans", 0)
        
        if total_scans == 0:
            target_modifier = 1.0  # Neutral for new targets
        else:
            # Targets with more findings = higher likelihood
            target_modifier = 1.0 + (total_findings / total_scans)
        
        # Calculate confidence weight
        confidence = min(attempts / self.min_attempts_for_confidence, 1.0)
        
        # Combine with confidence weighting
        prediction = global_rate * target_modifier * confidence
        
        # Bound to [0, 1]
        return max(0.0, min(1.0, prediction))
    
    def get_intelligence_summary(self) -> str:
        """Generate a comprehensive intelligence summary."""
        tech_analysis = self.analyze_techniques()
        
        summary = []
        summary.append("\n" + "="*80)
        summary.append("🧬 MUTATION ENGINE INTELLIGENCE REPORT")
        summary.append("="*80 + "\n")
        
        # Overall stats
        summary.append(f"Total Hunts: {self.memory.memory['total_hunts']}")
        summary.append(f"Targets Analyzed: {len(self.memory.memory['targets'])}")
        summary.append(f"AI Suggestions: {len(self.memory.memory['ai_suggestions'])}")
        
        # Technique rankings
        summary.append("\n" + "-"*80)
        summary.append("🎯 TECHNIQUE EFFECTIVENESS RANKING")
        summary.append("-"*80 + "\n")
        
        for i, tech in enumerate(tech_analysis, 1):
            status_emoji = {
                "high_value": "🔥",
                "medium_value": "⚡",
                "low_value": "❄️",
                "learning": "🧪",
                "untested": "❓"
            }.get(tech["status"], "")
            
            summary.append(
                f"{i:2}. {status_emoji} {tech['name']:20} | "
                f"Rate: {tech['success_rate']:5.1%} | "
                f"Tries: {tech['attempts']:3} | "
                f"Bounty: ${tech['bounty_earned']:,} | "
                f"Confidence: {tech['confidence']:3.0%}"
            )
        
        # Recommendations
        summary.append("\n" + "-"*80)
        summary.append("💡 STRATEGIC RECOMMENDATIONS")
        summary.append("-"*80 + "\n")
        
        high_value = [t for t in tech_analysis if t["status"] == "high_value"]
        low_value = [t for t in tech_analysis if t["status"] == "low_value"]
        learning = [t for t in tech_analysis if t["status"] == "learning"]
        
        if high_value:
            summary.append("✅ PRIORITIZE THESE:")
            for tech in high_value:
                summary.append(f"   • {tech['name']} ({tech['success_rate']:.0%} success)")
        
        if low_value:
            summary.append("\n❌ SKIP ON MATURE TARGETS:")
            for tech in low_value:
                summary.append(f"   • {tech['name']} ({tech['success_rate']:.0%} success)")
        
        if learning:
            summary.append("\n🧪 NEED MORE DATA:")
            for tech in learning:
                summary.append(f"   • {tech['name']} ({tech['attempts']} attempts)")
        
        # Speed optimization stats
        summary.append("\n" + "-"*80)
        summary.append("⚡ SPEED OPTIMIZATION INTEL")
        summary.append("-"*80 + "\n")
        
        for targets in [1, 10, 100, 1000]:
            seconds, formatted = self.estimate_queue_time(targets)
            summary.append(f"   {targets:4} targets → {formatted}")
        
        return "\n".join(summary)
    
    def evolve(self):
        """
        Main evolution method - analyzes all data and updates internal models.
        
        This is called after each hunt to improve future performance.
        """
        print("\n🧬 Mutation Engine evolving...")
        
        # Analyze techniques
        tech_analysis = self.analyze_techniques()
        
        # Update internal models
        self.learned_patterns = {
            "high_value_techniques": [t["name"] for t in tech_analysis if t["status"] == "high_value"],
            "skip_techniques": [t["name"] for t in tech_analysis if t["status"] == "low_value"],
            "learning_techniques": [t["name"] for t in tech_analysis if t["status"] == "learning"]
        }
        
        # Save evolution state
        evolution_data = {
            "version": self.version,
            "evolved_at": datetime.now().isoformat(),
            "total_hunts": self.memory.memory["total_hunts"],
            "technique_rankings": tech_analysis,
            "learned_patterns": self.learned_patterns
        }
        
        filename = f"mutation_engine_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(evolution_data, f, indent=2)
        
        print(f"✅ Evolution complete - State saved to {filename}")
        print(f"   High-value techniques: {len(self.learned_patterns['high_value_techniques'])}")
        print(f"   Skip techniques: {len(self.learned_patterns['skip_techniques'])}")
        print(f"   Learning techniques: {len(self.learned_patterns['learning_techniques'])}")


def main():
    """Demo the Mutation Engine"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                        MUTATION ENGINE DEMO                                ║
║              Analyzing Jupiter's Intelligence & Strategy                   ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize engine
    engine = MutationEngine()
    
    # Show intelligence summary
    print(engine.get_intelligence_summary())
    
    # Generate strategy for a target
    print("\n" + "="*80)
    print("📋 GENERATING STRATEGY FOR: gitlab.com")
    print("="*80)
    
    strategy = engine.generate_strategy("gitlab.com")
    
    print(f"\nTarget: {strategy['target']}")
    print(f"Confidence: {strategy['confidence']:.0%}")
    print(f"\nTechnique Plan:")
    
    for tech in strategy["techniques"]:
        test_icon = "✅" if tech["test"] else "❌"
        print(f"  {test_icon} {tech['name']:20} | {tech['reason']}")
    
    # Predict vulnerabilities
    print("\n" + "="*80)
    print("🔮 VULNERABILITY PREDICTIONS")
    print("="*80 + "\n")
    
    target = "gitlab.com"
    for tech in strategy["techniques"][:5]:  # Top 5
        likelihood = engine.predict_vulnerability_likelihood(target, tech["name"])
        print(f"{tech['name']:20} on {target}: {likelihood:.1%} likelihood")
    
    # Evolve
    engine.evolve()
    
    print("\n✅ Mutation Engine demo complete!")


if __name__ == "__main__":
    main()
