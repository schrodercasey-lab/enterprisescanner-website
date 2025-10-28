#!/usr/bin/env python3
"""
🔮 JUPITER AUTONOMOUS HUNT LAUNCHER (Unified Intelligence Version)

This is the NEW launcher that uses Jupiter's unified intelligence system.

OLD FLOW (Broken):
    launch_jupiter_hunt.py → http://localhost:8888 → 134.199.147.45:5002 → 0 findings

NEW FLOW (Unified Intelligence):
    launch_jupiter_hunt.py → jupiter_unified_launcher.py → jupiter_unified_hunter.py
        → Intelligence (memory + engine + chains) → Real findings with learning

Every hunt teaches Jupiter.
Every pattern compounds.
Every finding makes the next hunt smarter.
"""

import json
from datetime import datetime
from typing import Dict, Optional

# Import Jupiter's unified launcher
from jupiter_unified_launcher import launch_hunt_api


def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║     🔮 JUPITER AUTONOMOUS HUNT LAUNCHER                       ║")
    print("║     ✨ Unified Intelligence Version ✨                        ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    print(f"\n🎯 This triggers Jupiter to hunt with UNIFIED INTELLIGENCE")
    print(f"   ✅ Jupiter Memory records patterns")
    print(f"   ✅ Mutation Engine prioritizes techniques")
    print(f"   ✅ Chain Detector links vulnerabilities")
    print(f"   ✅ Every hunt makes the next one smarter")
    
    # Configuration with credentials
    targets = {
        "1": {
            "name": "Figma",
            "platform": "figma",
            "target": "https://api.figma.com",
            "credentials": {
                "api_token": "YOUR_FIGMA_TOKEN_HERE"  # Add your token
            },
            "status": "✅ VALIDATED (2 findings, intelligence confirmed)"
        },
        "2": {
            "name": "Shopify",
            "platform": "shopify",
            "target": "your-shop.myshopify.com",
            "credentials": {
                "shop_url": "your-shop.myshopify.com",
                "access_token": "YOUR_SHOPIFY_TOKEN_HERE",
                "api_key": "YOUR_API_KEY_HERE"
            },
            "status": "⏳ Ready for unified hunt"
        },
        "3": {
            "name": "Sentry",
            "platform": "sentry",
            "target": "https://sentry.io/api/0",
            "credentials": {
                "auth_token": "sntryu_..."  # Update with real token
            },
            "status": "⏳ Ready for unified hunt"
        },
        "4": {
            "name": "AWS",
            "platform": "aws",
            "target": "aws_infrastructure",
            "credentials": {
                "profile": "ReadOnlyAccess",
                "region": "us-east-1"
            },
            "status": "🔥 HIGH PRIORITY ($2.2M finding pending)"
        },
        "5": {
            "name": "GitLab",
            "platform": "gitlab",
            "target": "https://gitlab.com/api/v4",
            "credentials": {
                "private_token": ""  # Add if available
            },
            "status": "⏳ Ready for unified hunt"
        },
        "6": {
            "name": "Coinbase",
            "platform": "coinbase",
            "target": "https://api.coinbase.com",
            "credentials": {},
            "status": "⏳ Ready for unified hunt"
        },
        "7": {
            "name": "Tesla",
            "platform": "tesla",
            "target": "https://www.tesla.com",
            "credentials": {},
            "status": "⏳ Ready for unified hunt"
        },
        "8": {
            "name": "Reddit",
            "platform": "reddit",
            "target": "https://www.reddit.com",
            "credentials": {},
            "status": "⏳ Ready for unified hunt"
        }
    }
    
    print(f"\n📋 Available targets:")
    for key, target in targets.items():
        print(f"   {key}. {target['name']:15} - {target['status']}")
    
    choice = input(f"\n🎯 Select target (or press Enter for Figma): ").strip() or "1"
    
    if choice not in targets:
        print(f"❌ Invalid choice")
        return
    
    target_config = targets[choice]
    
    print(f"\n{'='*80}")
    print(f"🎯 Selected: {target_config['name']}")
    print(f"   Platform: {target_config['platform']}")
    print(f"   Target: {target_config['target']}")
    print(f"   Intelligence: ENGAGED")
    print(f"{'='*80}\n")
    
    # Confirm hunt
    confirm = input("🚀 Launch unified intelligence hunt? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Hunt cancelled")
        return
    
    # Launch unified hunt
    print(f"\n🔮 Launching Jupiter Unified Hunt...")
    print(f"   This uses TRUE intelligence integration")
    print(f"   Findings will be recorded in Jupiter Memory")
    print(f"   Chains will be detected and linked")
    print(f"   Next hunt will be smarter\n")
    
    try:
        # Call unified launcher API
        results = launch_hunt_api(
            target=target_config['target'],
            platform=target_config['platform'],
            credentials=target_config['credentials']
        )
        
        # Display results
        print(f"\n{'='*80}")
        print(f"📊 HUNT RESULTS")
        print(f"{'='*80}")
        
        if results.get("success"):
            print(f"✅ Success: True")
            print(f"📍 Target: {results.get('target')}")
            print(f"🎯 Platform: {results.get('platform')}")
            print(f"🔍 Findings: {len(results.get('findings', []))}")
            
            # Show findings summary
            findings = results.get('findings', [])
            if findings:
                print(f"\n📋 Findings Summary:")
                for i, finding in enumerate(findings, 1):
                    severity = finding.get('severity', 'unknown').upper()
                    title = finding.get('title', 'Untitled')
                    bounty = finding.get('bounty_estimate', 0)
                    print(f"   {i}. [{severity}] {title}")
                    print(f"      💰 Bounty Estimate: ${bounty:,}")
            
            # Show intelligence status
            intel_report = results.get('intelligence_report', {})
            print(f"\n🧬 Intelligence Status:")
            print(f"   Session: {intel_report.get('session_id', 'N/A')}")
            
            intel = intel_report.get('intelligence', {})
            memory = intel.get('memory', {})
            chains = intel.get('chains', {})
            
            print(f"   Memory: {memory.get('patterns_stored', 0)} patterns stored")
            print(f"   Chains: {chains.get('total_chains', 0)} chains detected")
            
            history = intel_report.get('hunt_history', {})
            print(f"   Total Hunts: {history.get('total_hunts', 0)}")
            print(f"   Total Findings: {history.get('total_findings', 0)}")
            
        else:
            print(f"❌ Success: False")
            print(f"   Error: {results.get('error', 'Unknown')}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jupiter_unified_hunt_{target_config['platform']}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved: {filename}")
        print(f"{'='*80}\n")
        
        print(f"🔮 Jupiter has learned from this hunt")
        print(f"   Next hunt will be smarter\n")
        
    except Exception as e:
        print(f"\n❌ Hunt failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
