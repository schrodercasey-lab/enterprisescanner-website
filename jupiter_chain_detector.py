#!/usr/bin/env python3
"""
🔗 JUPITER VULNERABILITY CHAIN DETECTOR
Finds combinations of vulnerabilities that multiply impact
Single vulnerability: $10k → Chained vulnerabilities: $30k-$100k
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from itertools import combinations

class VulnerabilityChain:
    def __init__(self, vulnerabilities: List[Dict]):
        self.vulnerabilities = vulnerabilities
        self.chains = []
        self.impact_multipliers = {
            "2-chain": 1.5,
            "3-chain": 2.0,
            "4-chain": 3.0,
            "5-chain": 5.0
        }
        
    def calculate_chain_value(self, chain_length: int, base_severity: str) -> int:
        """Calculate bounty value for chained vulnerabilities"""
        base_values = {
            "CRITICAL": 30000,
            "HIGH": 15000,
            "MEDIUM": 5000,
            "LOW": 1000
        }
        
        base = base_values.get(base_severity, 5000)
        multiplier_key = f"{chain_length}-chain"
        multiplier = self.impact_multipliers.get(multiplier_key, chain_length * 0.5)
        
        return int(base * multiplier)

class ChainDetector:
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.vulnerabilities = []
        self.chains = []
        self.chain_patterns = self._load_chain_patterns()
        
    def log(self, message, level="INFO"):
        """Enhanced logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "CRITICAL": "🔴",
            "CHAIN": "🔗",
            "MULTIPLY": "✖️",
            "JACKPOT": "💰"
        }.get(level, "•")
        
        print(f"[{timestamp}] {emoji} {message}")
        
    def _load_chain_patterns(self) -> Dict:
        """Load known vulnerability chain patterns"""
        return {
            # GraphQL Chains
            "graphql_introspection_to_mutation": {
                "name": "Introspection → Mutation Bypass",
                "vulnerabilities": ["graphql_introspection", "mutation_authorization_bypass"],
                "impact": "CRITICAL",
                "description": "Use introspection to map all mutations, then exploit authorization bypass",
                "multiplier": 2.0,
                "example": "Discover admin mutations via introspection, execute without authorization"
            },
            
            "idor_to_mutation": {
                "name": "IDOR → Data Mutation",
                "vulnerabilities": ["idor", "mutation_authorization_bypass"],
                "impact": "CRITICAL",
                "description": "Access other users' IDs via IDOR, then mutate their data",
                "multiplier": 2.5,
                "example": "Read victim's user ID, then modify their account settings"
            },
            
            # REST API Chains
            "read_to_write_escalation": {
                "name": "Read Access → Write Operations",
                "vulnerabilities": ["information_disclosure", "authorization_bypass"],
                "impact": "CRITICAL",
                "description": "Use read-only access to gather IDs, then write with bypassed auth",
                "multiplier": 2.0,
                "example": "Read customer IDs with read key, create charges with same key"
            },
            
            "token_disclosure_to_hijack": {
                "name": "Token Disclosure → Account Takeover",
                "vulnerabilities": ["information_disclosure", "session_hijacking"],
                "impact": "CRITICAL",
                "description": "Leak tokens in responses, use to hijack sessions",
                "multiplier": 3.0,
                "example": "API returns refresh_token in response, use to take over account"
            },
            
            # OAuth Chains
            "scope_escalation_to_admin": {
                "name": "Scope Escalation → Admin Access",
                "vulnerabilities": ["oauth_scope_escalation", "privilege_escalation"],
                "impact": "CRITICAL",
                "description": "Escalate OAuth scopes, then escalate privileges to admin",
                "multiplier": 2.5,
                "example": "Read scope performs write, write scope sets isAdmin=true"
            },
            
            "oauth_redirect_to_token_theft": {
                "name": "Redirect Manipulation → Token Theft",
                "vulnerabilities": ["redirect_uri_bypass", "token_disclosure"],
                "impact": "CRITICAL",
                "description": "Manipulate redirect URI to steal OAuth tokens",
                "multiplier": 2.0,
                "example": "Bypass redirect validation, steal access token"
            },
            
            # IDOR Chains
            "idor_enumeration_to_data_dump": {
                "name": "IDOR → Mass Data Extraction",
                "vulnerabilities": ["idor", "rate_limit_bypass"],
                "impact": "CRITICAL",
                "description": "Enumerate all user IDs, extract all user data",
                "multiplier": 3.0,
                "example": "Access /users/1 through /users/100000, dump entire database"
            },
            
            "idor_to_privilege_escalation": {
                "name": "IDOR → Privilege Escalation",
                "vulnerabilities": ["idor", "privilege_escalation"],
                "impact": "CRITICAL",
                "description": "Access admin user via IDOR, copy their privileges",
                "multiplier": 2.5,
                "example": "Read admin user object, set own isAdmin to true"
            },
            
            # Multi-Stage Chains
            "recon_to_exploitation": {
                "name": "Information Gathering → Full Exploitation",
                "vulnerabilities": ["information_disclosure", "idor", "mutation_authorization_bypass"],
                "impact": "CRITICAL",
                "description": "Leak internal IDs, use IDOR to access resources, mutate data",
                "multiplier": 3.0,
                "example": "API leaks user IDs → Access via IDOR → Modify via mutation"
            },
            
            "authentication_bypass_chain": {
                "name": "Auth Bypass → Complete Takeover",
                "vulnerabilities": ["authentication_bypass", "session_hijacking", "privilege_escalation"],
                "impact": "CRITICAL",
                "description": "Bypass auth, hijack admin session, escalate privileges",
                "multiplier": 4.0,
                "example": "Skip login → Steal admin session → Set isAdmin=true"
            },
            
            # Business Logic Chains
            "rate_limit_to_brute_force": {
                "name": "Rate Limit Bypass → Credential Stuffing",
                "vulnerabilities": ["rate_limit_bypass", "authentication_bypass"],
                "impact": "HIGH",
                "description": "Bypass rate limits to brute force credentials",
                "multiplier": 2.0,
                "example": "No rate limit on /login → Brute force passwords"
            },
            
            "cache_poisoning_to_xss": {
                "name": "Cache Poisoning → Stored XSS",
                "vulnerabilities": ["cache_poisoning", "xss"],
                "impact": "HIGH",
                "description": "Poison cache with XSS payload, affect all users",
                "multiplier": 2.5,
                "example": "Cache malicious response, serve XSS to everyone"
            }
        }
        
    def add_vulnerability(self, vuln: Dict):
        """Add vulnerability to detection pool"""
        self.vulnerabilities.append(vuln)
        
    def detect_chains(self) -> List[Dict]:
        """Detect vulnerability chains"""
        self.log("Analyzing vulnerabilities for chain patterns...", "CHAIN")
        
        # Check for known patterns
        self._detect_known_patterns()
        
        # Check for similar vulnerability clusters
        self._detect_similar_clusters()
        
        # Check for sequential exploitation paths
        self._detect_sequential_paths()
        
        return self.chains
        
    def _detect_known_patterns(self):
        """Detect known chain patterns"""
        for pattern_name, pattern in self.chain_patterns.items():
            required_vulns = set(pattern["vulnerabilities"])
            
            # Check if we have all required vulnerabilities
            found_vulns = []
            for vuln in self.vulnerabilities:
                vuln_type = vuln.get("type", "").lower()
                
                # Match vulnerability types
                for required in required_vulns:
                    if required.replace("_", " ") in vuln_type or \
                       required in vuln.get("category", "").lower():
                        found_vulns.append(vuln)
                        break
                        
            # If we found all required vulnerabilities, it's a chain
            if len(found_vulns) >= len(required_vulns):
                chain = {
                    "pattern": pattern_name,
                    "name": pattern["name"],
                    "vulnerabilities": found_vulns,
                    "impact": pattern["impact"],
                    "description": pattern["description"],
                    "example": pattern["example"],
                    "multiplier": pattern["multiplier"],
                    "chain_length": len(found_vulns),
                    "detected_at": datetime.now().isoformat()
                }
                
                # Calculate bounty
                base_bounty = sum([self._estimate_bounty(v) for v in found_vulns])
                chain["bounty_individual"] = base_bounty
                chain["bounty_chained"] = int(base_bounty * pattern["multiplier"])
                chain["bounty_increase"] = chain["bounty_chained"] - chain["bounty_individual"]
                
                self.chains.append(chain)
                
                self.log(f"🔗 CHAIN DETECTED: {pattern['name']}", "CRITICAL")
                self.log(f"   Multiplier: {pattern['multiplier']}x", "MULTIPLY")
                self.log(f"   Bounty increase: ${chain['bounty_increase']:,}", "JACKPOT")
                
    def _detect_similar_clusters(self):
        """Detect clusters of similar vulnerabilities"""
        # Group by category
        categories = {}
        for vuln in self.vulnerabilities:
            category = vuln.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(vuln)
            
        # Look for clusters (3+ similar vulnerabilities)
        for category, vulns in categories.items():
            if len(vulns) >= 3:
                chain = {
                    "pattern": "vulnerability_cluster",
                    "name": f"Multiple {category} Vulnerabilities",
                    "vulnerabilities": vulns,
                    "impact": "HIGH",
                    "description": f"Multiple {category} vulnerabilities can be chained for greater impact",
                    "multiplier": 1.5,
                    "chain_length": len(vulns),
                    "detected_at": datetime.now().isoformat()
                }
                
                base_bounty = sum([self._estimate_bounty(v) for v in vulns])
                chain["bounty_individual"] = base_bounty
                chain["bounty_chained"] = int(base_bounty * 1.5)
                chain["bounty_increase"] = chain["bounty_chained"] - chain["bounty_individual"]
                
                self.chains.append(chain)
                
                self.log(f"🔗 CLUSTER: {len(vulns)} {category} vulnerabilities", "CHAIN")
                
    def _detect_sequential_paths(self):
        """Detect sequential exploitation paths"""
        # Look for vulnerabilities that can be chained sequentially
        
        # Pattern 1: Read → Write
        read_vulns = [v for v in self.vulnerabilities if "read" in v.get("description", "").lower() or 
                     "disclosure" in v.get("type", "").lower()]
        write_vulns = [v for v in self.vulnerabilities if "write" in v.get("description", "").lower() or
                      "mutation" in v.get("type", "").lower() or
                      "create" in v.get("description", "").lower()]
                      
        if read_vulns and write_vulns:
            chain = {
                "pattern": "read_write_chain",
                "name": "Read Access → Write Operations",
                "vulnerabilities": read_vulns + write_vulns,
                "impact": "CRITICAL",
                "description": "Use read vulnerability to gather data, then exploit write vulnerability",
                "multiplier": 2.0,
                "chain_length": len(read_vulns) + len(write_vulns),
                "detected_at": datetime.now().isoformat()
            }
            
            base_bounty = sum([self._estimate_bounty(v) for v in chain["vulnerabilities"]])
            chain["bounty_individual"] = base_bounty
            chain["bounty_chained"] = int(base_bounty * 2.0)
            chain["bounty_increase"] = chain["bounty_chained"] - chain["bounty_individual"]
            
            self.chains.append(chain)
            
            self.log(f"🔗 PATH: Read → Write exploitation chain", "CHAIN")
            
    def _estimate_bounty(self, vuln: Dict) -> int:
        """Estimate bounty for single vulnerability"""
        severity = vuln.get("severity", "MEDIUM")
        
        base_values = {
            "CRITICAL": 30000,
            "HIGH": 15000,
            "MEDIUM": 5000,
            "LOW": 1000
        }
        
        return base_values.get(severity, 5000)
        
    def generate_report(self) -> Dict:
        """Generate chain detection report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jupiter_chains_{self.platform_name.lower()}_{timestamp}.json"
        
        # Calculate total impact
        total_individual = sum([c["bounty_individual"] for c in self.chains])
        total_chained = sum([c["bounty_chained"] for c in self.chains])
        total_increase = total_chained - total_individual
        
        report = {
            "scan_date": datetime.now().isoformat(),
            "platform": self.platform_name,
            "scanner": "Jupiter Vulnerability Chain Detector v1.0",
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "chains_detected": len(self.chains),
                "average_chain_length": sum([c["chain_length"] for c in self.chains]) / len(self.chains) if self.chains else 0,
                "bounty_without_chains": total_individual,
                "bounty_with_chains": total_chained,
                "bounty_increase": total_increase,
                "multiplier": round(total_chained / total_individual, 2) if total_individual > 0 else 1.0
            },
            "chains": self.chains,
            "vulnerabilities": self.vulnerabilities
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        self.log(f"Report saved: {filename}", "SUCCESS")
        
        # Print summary
        print()
        print("="*70)
        print("🔗 VULNERABILITY CHAIN ANALYSIS")
        print("="*70)
        print()
        print(f"Platform: {self.platform_name}")
        print(f"Vulnerabilities analyzed: {len(self.vulnerabilities)}")
        print(f"Chains detected: {len(self.chains)}")
        print()
        
        if self.chains:
            print("💰 BOUNTY IMPACT:")
            print(f"   Individual vulnerabilities: ${total_individual:,}")
            print(f"   Chained exploitation: ${total_chained:,}")
            print(f"   Increase: ${total_increase:,} ({report['summary']['multiplier']}x)")
            print()
            
            print("🔗 TOP CHAINS:")
            sorted_chains = sorted(self.chains, key=lambda x: x["bounty_increase"], reverse=True)
            
            for i, chain in enumerate(sorted_chains[:5], 1):
                print(f"\n{i}. {chain['name']}")
                print(f"   Impact: {chain['impact']}")
                print(f"   Vulnerabilities: {chain['chain_length']}")
                print(f"   Multiplier: {chain['multiplier']}x")
                print(f"   Bounty increase: ${chain['bounty_increase']:,}")
                print(f"   Description: {chain['description']}")
                
        else:
            print("✅ No vulnerability chains detected")
            print("   Individual vulnerabilities are isolated")
            
        print()
        print(f"Full report: {filename}")
        print()
        
        return report

def load_scan_results(filename: str) -> List[Dict]:
    """Load vulnerabilities from previous scan"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Extract vulnerabilities from different report formats
        vulnerabilities = []
        
        # GraphQL scan format
        if "vulnerabilities" in data:
            vulnerabilities.extend(data["vulnerabilities"])
            
        # REST API scan format
        if "findings" in data:
            vulnerabilities.extend(data["findings"])
            
        # OAuth scan format
        if "validation_results" in data:
            for result in data["validation_results"]:
                if result.get("validated"):
                    vulnerabilities.append({
                        "type": result.get("test"),
                        "severity": result.get("severity", "HIGH"),
                        "description": result.get("impact", ""),
                        "category": "oauth"
                    })
                    
        return vulnerabilities
        
    except Exception as e:
        print(f"Error loading scan results: {str(e)}")
        return []

def main():
    """Interactive chain detection"""
    print()
    print("="*70)
    print("🔗 JUPITER VULNERABILITY CHAIN DETECTOR")
    print("="*70)
    print()
    print("Find vulnerability combinations that multiply impact")
    print()
    
    print("Select input method:")
    print("  1. Load from scan file")
    print("  2. Manual entry")
    print()
    
    choice = input("Select method (1-2): ").strip()
    
    if choice == "1":
        print()
        filename = input("Scan results file (JSON): ").strip()
        
        vulnerabilities = load_scan_results(filename)
        
        if not vulnerabilities:
            print("❌ No vulnerabilities found in file")
            return
            
        print(f"✅ Loaded {len(vulnerabilities)} vulnerabilities")
        print()
        
        platform_name = input("Platform name: ").strip()
        
        detector = ChainDetector(platform_name)
        
        for vuln in vulnerabilities:
            detector.add_vulnerability(vuln)
            
        print()
        detector.detect_chains()
        print()
        detector.generate_report()
        
    elif choice == "2":
        print()
        platform_name = input("Platform name: ").strip()
        
        detector = ChainDetector(platform_name)
        
        print()
        print("Enter vulnerabilities (or 'done' to finish):")
        print()
        
        while True:
            vuln_type = input("Vulnerability type (or 'done'): ").strip()
            
            if vuln_type.lower() == 'done':
                break
                
            severity = input("Severity (CRITICAL/HIGH/MEDIUM/LOW): ").strip().upper()
            description = input("Description: ").strip()
            category = input("Category: ").strip()
            
            vuln = {
                "type": vuln_type,
                "severity": severity,
                "description": description,
                "category": category
            }
            
            detector.add_vulnerability(vuln)
            print()
            
        print()
        detector.detect_chains()
        print()
        detector.generate_report()
        
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
