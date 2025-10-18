#!/usr/bin/env python3
"""
Jupiter AI - Script Generator Integration Example

This example demonstrates how to integrate the Script Generator module
with Jupiter AI's vulnerability detection system for automated remediation.

Usage:
    python jupiter_integration_example.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules import (
    ScriptGenerator,
    VulnerabilityType,
    ScriptLanguage,
)


class JupiterIntegration:
    """Integration layer between Jupiter AI and Script Generator"""
    
    # Map Jupiter vulnerability names to VulnerabilityType enum
    VULNERABILITY_MAP = {
        "SQL Injection": VulnerabilityType.SQL_INJECTION,
        "SQLi": VulnerabilityType.SQL_INJECTION,
        "Cross-Site Scripting": VulnerabilityType.XSS,
        "XSS": VulnerabilityType.XSS,
        "CSRF": VulnerabilityType.CSRF,
        "Cross-Site Request Forgery": VulnerabilityType.CSRF,
        "Weak Authentication": VulnerabilityType.WEAK_AUTH,
        "Weak Password Policy": VulnerabilityType.WEAK_AUTH,
        "Insecure Cryptography": VulnerabilityType.INSECURE_CRYPTO,
        "Permission Issue": VulnerabilityType.PERMISSION_ISSUE,
        "Access Control": VulnerabilityType.PERMISSION_ISSUE,
        "Dependency Vulnerability": VulnerabilityType.DEPENDENCY_VULN,
        "Outdated Dependencies": VulnerabilityType.DEPENDENCY_VULN,
        "Configuration Error": VulnerabilityType.CONFIG_ERROR,
        "Misconfiguration": VulnerabilityType.CONFIG_ERROR,
        "Hardcoded Secret": VulnerabilityType.HARDCODED_SECRET,
        "Hardcoded Credentials": VulnerabilityType.HARDCODED_SECRET,
        "Path Traversal": VulnerabilityType.PATH_TRAVERSAL,
        "Directory Traversal": VulnerabilityType.PATH_TRAVERSAL,
    }
    
    # Map file extensions to script languages
    LANGUAGE_MAP = {
        '.py': ScriptLanguage.PYTHON,
        '.sh': ScriptLanguage.BASH,
        '.bash': ScriptLanguage.BASH,
        '.ps1': ScriptLanguage.POWERSHELL,
    }
    
    def __init__(self):
        self.generator = ScriptGenerator()
        self.remediation_log = []
    
    def detect_language(self, file_path: str) -> ScriptLanguage:
        """Detect script language from file extension"""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_MAP.get(ext, ScriptLanguage.PYTHON)
    
    def map_vulnerability(self, vuln_name: str) -> VulnerabilityType:
        """Map Jupiter vulnerability name to enum"""
        return self.VULNERABILITY_MAP.get(
            vuln_name,
            VulnerabilityType.CONFIG_ERROR  # default fallback
        )
    
    def process_vulnerability(self, vulnerability_data: dict) -> dict:
        """
        Process a vulnerability detected by Jupiter AI
        
        Args:
            vulnerability_data: Dictionary with vulnerability info
                {
                    'name': 'SQL Injection',
                    'file': '/app/database.py',
                    'line': 42,
                    'severity': 'HIGH',
                    'cvss': 8.5,
                    'description': 'User input not sanitized',
                    'target_system': 'Ubuntu 22.04'
                }
        
        Returns:
            Dictionary with remediation details
        """
        vuln_type = self.map_vulnerability(vulnerability_data['name'])
        language = self.detect_language(vulnerability_data['file'])
        
        print(f"\n{'='*80}")
        print(f"🔍 Processing: {vulnerability_data['name']}")
        print(f"📁 File: {vulnerability_data['file']}")
        print(f"📊 CVSS: {vulnerability_data['cvss']} ({vulnerability_data['severity']})")
        print(f"{'='*80}")
        
        # Generate remediation scripts
        result = self.generator.generate_remediation_script(
            vulnerability_type=vuln_type,
            language=language,
            target_system=vulnerability_data['target_system'],
            cvss_score=vulnerability_data['cvss'],
            context={
                'file_path': vulnerability_data['file'],
                'line_number': vulnerability_data.get('line'),
                'description': vulnerability_data.get('description')
            }
        )
        
        # Check safety warnings
        if result.safety_warnings:
            print(f"\n⚠️  Safety Warnings ({len(result.safety_warnings)}):")
            for warning in result.safety_warnings:
                print(f"  ⚠️  {warning}")
            print("\n  ⚠️  Manual review required before execution!")
        else:
            print("\n✅ No safety issues detected")
        
        # Log remediation
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'vulnerability': vulnerability_data['name'],
            'file': vulnerability_data['file'],
            'cvss': vulnerability_data['cvss'],
            'checksum': result.metadata.checksum,
            'warnings': len(result.safety_warnings),
            'has_rollback': result.metadata.has_rollback
        }
        self.remediation_log.append(log_entry)
        
        return {
            'vulnerability': vulnerability_data,
            'result': result,
            'status': 'READY' if not result.safety_warnings else 'REVIEW_REQUIRED'
        }
    
    def save_remediation_package(self, remediation: dict, output_dir: str = "remediation_output"):
        """Save remediation scripts to files"""
        vuln = remediation['vulnerability']
        result = remediation['result']
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create subdirectory for this vulnerability
        vuln_dir = output_path / f"{vuln['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        vuln_dir.mkdir(exist_ok=True)
        
        # Determine file extension
        ext_map = {
            ScriptLanguage.PYTHON: '.py',
            ScriptLanguage.BASH: '.sh',
            ScriptLanguage.POWERSHELL: '.ps1'
        }
        ext = ext_map.get(result.metadata.language, '.txt')
        
        # Save remediation script
        remediation_file = vuln_dir / f"remediation{ext}"
        remediation_file.write_text(result.remediation_script, encoding='utf-8')
        print(f"\n📝 Saved: {remediation_file}")
        
        # Save rollback script
        rollback_file = vuln_dir / f"rollback{ext}"
        rollback_file.write_text(result.rollback_script, encoding='utf-8')
        print(f"📝 Saved: {rollback_file}")
        
        # Save test script
        test_file = vuln_dir / f"test{ext}"
        test_file.write_text(result.test_script, encoding='utf-8')
        print(f"📝 Saved: {test_file}")
        
        # Save execution notes
        notes_file = vuln_dir / "EXECUTION_NOTES.txt"
        notes_file.write_text(result.execution_notes, encoding='utf-8')
        print(f"📝 Saved: {notes_file}")
        
        # Save metadata
        metadata_file = vuln_dir / "metadata.txt"
        metadata_content = f"""Vulnerability Remediation Metadata
{'='*50}

Vulnerability: {vuln['name']}
File: {vuln['file']}
CVSS Score: {vuln['cvss']}
Severity: {vuln['severity']}
Target System: {vuln['target_system']}

Generated: {result.metadata.generated_at}
Language: {result.metadata.language.value}
Checksum: {result.metadata.checksum}
Has Rollback: {result.metadata.has_rollback}
Safety Checked: {result.metadata.safety_checked}

Safety Warnings: {len(result.safety_warnings)}
"""
        if result.safety_warnings:
            metadata_content += "\nWarnings:\n"
            for warning in result.safety_warnings:
                metadata_content += f"  - {warning}\n"
        
        metadata_file.write_text(metadata_content, encoding='utf-8')
        print(f"📝 Saved: {metadata_file}")
        
        return vuln_dir
    
    def print_statistics(self):
        """Print remediation statistics"""
        stats = self.generator.get_statistics()
        
        print(f"\n{'='*80}")
        print("📊 REMEDIATION STATISTICS")
        print(f"{'='*80}")
        print(f"Total Scripts Generated: {stats['scripts_generated']}")
        print(f"Safety Violations: {stats['safety_violations']}")
        print(f"Rollbacks Created: {stats['rollbacks_created']}")
        
        print(f"\nBy Language:")
        for lang, count in stats['languages'].items():
            if count > 0:
                print(f"  {lang}: {count}")
        
        print(f"\nBy Vulnerability Type:")
        for vuln, count in stats['vulnerability_types'].items():
            if count > 0:
                print(f"  {vuln}: {count}")
        
        print(f"\nRemediation Log Entries: {len(self.remediation_log)}")


def main():
    """Example Jupiter AI integration workflow"""
    
    print("=" * 80)
    print("JUPITER AI - AUTOMATED REMEDIATION SYSTEM")
    print("Script Generator Integration Example")
    print("=" * 80)
    
    # Initialize integration
    jupiter = JupiterIntegration()
    
    # Simulate Jupiter AI vulnerability scan results
    vulnerabilities = [
        {
            'name': 'SQL Injection',
            'file': '/app/database.py',
            'line': 42,
            'severity': 'HIGH',
            'cvss': 8.5,
            'description': 'User input concatenated directly into SQL query',
            'target_system': 'Ubuntu 22.04 LTS'
        },
        {
            'name': 'XSS',
            'file': '/app/views.py',
            'line': 78,
            'severity': 'MEDIUM',
            'cvss': 6.8,
            'description': 'User input rendered without escaping',
            'target_system': 'Ubuntu 22.04 LTS'
        },
        {
            'name': 'Weak Authentication',
            'file': '/app/auth.py',
            'line': 15,
            'severity': 'HIGH',
            'cvss': 9.0,
            'description': 'Using MD5 for password hashing',
            'target_system': 'Ubuntu 22.04 LTS'
        }
    ]
    
    print(f"\n🔍 Processing {len(vulnerabilities)} vulnerabilities...\n")
    
    # Process each vulnerability
    remediations = []
    for vuln in vulnerabilities:
        remediation = jupiter.process_vulnerability(vuln)
        remediations.append(remediation)
        
        # Save remediation package
        output_dir = jupiter.save_remediation_package(remediation)
        print(f"📦 Remediation package: {output_dir}")
    
    # Print statistics
    jupiter.print_statistics()
    
    # Summary
    print(f"\n{'='*80}")
    print("✅ REMEDIATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total Vulnerabilities Processed: {len(remediations)}")
    print(f"Ready for Execution: {sum(1 for r in remediations if r['status'] == 'READY')}")
    print(f"Require Manual Review: {sum(1 for r in remediations if r['status'] == 'REVIEW_REQUIRED')}")
    
    print(f"\n{'='*80}")
    print("📋 NEXT STEPS")
    print(f"{'='*80}")
    print("1. Review generated scripts in 'remediation_output' directory")
    print("2. Read EXECUTION_NOTES.txt for each vulnerability")
    print("3. Test remediation scripts in staging environment")
    print("4. Execute remediation scripts with rollback ready")
    print("5. Run test scripts to verify fixes")
    print("6. Monitor systems for 24-48 hours post-remediation")
    
    print(f"\n✅ Script Generator integration example complete!\n")


if __name__ == "__main__":
    main()
