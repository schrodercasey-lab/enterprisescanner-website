#!/usr/bin/env python3
"""
Jupiter Config Integration Example
===================================

This example demonstrates how to integrate the Config Generator module with
the Jupiter vulnerability scanning platform to automatically generate security
hardening configurations based on discovered vulnerabilities.

Business Value:
- Automated remediation config generation (+$10K ARPU)
- 90% reduction in manual configuration time
- Compliance framework mapping (PCI-DSS, HIPAA, SOC2)
- Enterprise-grade security hardening

Usage:
    python jupiter_config_integration_example.py

Author: Enterprise Scanner Platform
Version: 1.0.0
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config_generator import (
    ConfigGenerator,
    ConfigType,
    HardeningLevel,
    ComplianceFramework,
    GeneratedConfig
)
from typing import List, Dict, Any, Set
import json
from datetime import datetime


class JupiterConfigIntegration:
    """
    Integration class that maps Jupiter vulnerability scan results to
    automated security configuration generation.
    """
    
    def __init__(self):
        self.config_generator = ConfigGenerator()
        self.vulnerability_mapping = self._build_vulnerability_mapping()
    
    def _build_vulnerability_mapping(self) -> Dict[str, Dict[str, Any]]:
        """
        Build mapping from vulnerability types to configuration remediation.
        
        Returns:
            Dict mapping vulnerability categories to config generation params
        """
        return {
            "SSH-001": {
                "config_type": ConfigType.SSH,
                "severity": "critical",
                "recommended_level": HardeningLevel.STRICT,
                "description": "Weak SSH configuration detected",
                "compliance": [ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]
            },
            "SSH-002": {
                "config_type": ConfigType.SSH,
                "severity": "high",
                "recommended_level": HardeningLevel.MODERATE,
                "description": "SSH password authentication enabled",
                "compliance": [ComplianceFramework.CIS]
            },
            "FW-001": {
                "config_type": ConfigType.FIREWALL_IPTABLES,
                "severity": "critical",
                "recommended_level": HardeningLevel.STRICT,
                "description": "No firewall rules configured",
                "compliance": [ComplianceFramework.PCI_DSS, ComplianceFramework.NIST]
            },
            "FW-002": {
                "config_type": ConfigType.FIREWALL_UFW,
                "severity": "high",
                "recommended_level": HardeningLevel.MODERATE,
                "description": "Firewall allows unrestricted access",
                "compliance": [ComplianceFramework.CIS]
            },
            "WEB-001": {
                "config_type": ConfigType.NGINX,
                "severity": "high",
                "recommended_level": HardeningLevel.STRICT,
                "description": "Missing security headers",
                "compliance": [ComplianceFramework.PCI_DSS, ComplianceFramework.GDPR]
            },
            "WEB-002": {
                "config_type": ConfigType.NGINX,
                "severity": "medium",
                "recommended_level": HardeningLevel.MODERATE,
                "description": "Weak TLS configuration",
                "compliance": [ComplianceFramework.HIPAA, ComplianceFramework.PCI_DSS]
            },
            "WEB-003": {
                "config_type": ConfigType.APACHE,
                "severity": "high",
                "recommended_level": HardeningLevel.STRICT,
                "description": "Server tokens exposed",
                "compliance": [ComplianceFramework.CIS]
            },
            "DB-001": {
                "config_type": ConfigType.POSTGRESQL,
                "severity": "critical",
                "recommended_level": HardeningLevel.STRICT,
                "description": "Database accessible from external networks",
                "compliance": [ComplianceFramework.PCI_DSS, ComplianceFramework.HIPAA]
            },
            "DB-002": {
                "config_type": ConfigType.MYSQL,
                "severity": "high",
                "recommended_level": HardeningLevel.STRICT,
                "description": "Weak database password policy",
                "compliance": [ComplianceFramework.SOC2, ComplianceFramework.HIPAA]
            },
            "DB-003": {
                "config_type": ConfigType.POSTGRESQL,
                "severity": "medium",
                "recommended_level": HardeningLevel.MODERATE,
                "description": "Database logging insufficient",
                "compliance": [ComplianceFramework.SOC2]
            }
        }
    
    def process_scan_results(
        self,
        scan_results: Dict[str, Any],
        target_system: str = "Ubuntu 22.04",
        organization_compliance: List[ComplianceFramework] = None
    ) -> Dict[str, List[GeneratedConfig]]:
        """
        Process Jupiter scan results and generate remediation configurations.
        
        Args:
            scan_results: Vulnerability scan results from Jupiter
            target_system: Target operating system
            organization_compliance: Required compliance frameworks
        
        Returns:
            Dict mapping vulnerability IDs to generated configs
        """
        results = {
            "configs_generated": [],
            "vulnerabilities_processed": 0,
            "critical_remediations": 0,
            "high_remediations": 0,
            "medium_remediations": 0,
            "compliance_coverage": set()
        }
        
        print("\n" + "="*70)
        print("JUPITER CONFIG INTEGRATION - Vulnerability Remediation")
        print("="*70)
        
        # Extract vulnerabilities
        vulnerabilities = scan_results.get('vulnerabilities', [])
        
        if not vulnerabilities:
            print("\n✅ No vulnerabilities found - system is secure!")
            return results
        
        print(f"\n📊 Processing {len(vulnerabilities)} vulnerabilities...")
        
        # Group vulnerabilities by config type
        config_groups: Dict[ConfigType, List[Dict]] = {}
        
        for vuln in vulnerabilities:
            vuln_id = vuln.get('id')
            
            if vuln_id not in self.vulnerability_mapping:
                print(f"⚠️  Unknown vulnerability type: {vuln_id} - skipping")
                continue
            
            mapping = self.vulnerability_mapping[vuln_id]
            config_type = mapping['config_type']
            
            if config_type not in config_groups:
                config_groups[config_type] = []
            
            config_groups[config_type].append({
                'vuln': vuln,
                'mapping': mapping
            })
            
            results['vulnerabilities_processed'] += 1
        
        print(f"\n🔧 Generating configurations for {len(config_groups)} component types...")
        
        # Generate configs for each group
        for config_type, vuln_group in config_groups.items():
            # Determine highest severity in group
            severities = [v['mapping']['severity'] for v in vuln_group]
            max_severity = self._get_max_severity(severities)
            
            # Determine hardening level
            if max_severity == 'critical':
                hardening_level = HardeningLevel.STRICT
                results['critical_remediations'] += len(vuln_group)
            elif max_severity == 'high':
                hardening_level = HardeningLevel.MODERATE
                results['high_remediations'] += len(vuln_group)
            else:
                hardening_level = HardeningLevel.BASIC
                results['medium_remediations'] += len(vuln_group)
            
            # Collect all compliance frameworks needed
            compliance_frameworks = set()
            for vuln_data in vuln_group:
                compliance_frameworks.update(vuln_data['mapping']['compliance'])
            
            if organization_compliance:
                compliance_frameworks.update(organization_compliance)
            
            compliance_list = list(compliance_frameworks)
            
            # Generate configuration
            print(f"\n{'='*70}")
            print(f"🔒 Generating {config_type.value.upper()} configuration...")
            print(f"   Severity: {max_severity.upper()}")
            print(f"   Hardening Level: {hardening_level.value}")
            print(f"   Vulnerabilities: {len(vuln_group)}")
            print(f"   Compliance: {', '.join([c.value.upper() for c in compliance_list])}")
            
            try:
                config = self.config_generator.generate_config(
                    config_type=config_type,
                    target_system=target_system,
                    hardening_level=hardening_level,
                    compliance_frameworks=compliance_list if compliance_list else None
                )
                
                # Add vulnerability context
                config.source_vulnerabilities = [v['vuln']['id'] for v in vuln_group]
                
                results['configs_generated'].append(config)
                results['compliance_coverage'].update(compliance_list)
                
                print(f"   ✅ Configuration generated successfully")
                print(f"   📝 Checksum: {config.metadata.checksum[:16]}...")
                
                if config.warnings:
                    print(f"   ⚠️  Warnings: {len(config.warnings)}")
                    for warning in config.warnings:
                        print(f"      - {warning}")
                
            except Exception as e:
                print(f"   ❌ Error generating config: {str(e)}")
        
        # Print summary
        print(f"\n{'='*70}")
        print("📊 REMEDIATION SUMMARY")
        print(f"{'='*70}")
        print(f"Vulnerabilities Processed: {results['vulnerabilities_processed']}")
        print(f"Configurations Generated: {len(results['configs_generated'])}")
        print(f"Critical Remediations: {results['critical_remediations']}")
        print(f"High Priority: {results['high_remediations']}")
        print(f"Medium Priority: {results['medium_remediations']}")
        print(f"Compliance Frameworks: {', '.join([c.value.upper() for c in results['compliance_coverage']])}")
        
        return results
    
    def _get_max_severity(self, severities: List[str]) -> str:
        """Get maximum severity from list."""
        severity_order = {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}
        max_sev = max(severities, key=lambda s: severity_order.get(s, 0))
        return max_sev
    
    def save_configs(
        self,
        configs: List[GeneratedConfig],
        output_dir: str = "./remediation_configs"
    ):
        """
        Save generated configurations to disk.
        
        Args:
            configs: List of generated configurations
            output_dir: Directory to save configs
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving configurations to {output_dir}...")
        
        for config in configs:
            config_name = f"{config.metadata.config_type.value}_{config.metadata.hardening_level.value}"
            
            # Save main config
            config_file = os.path.join(output_dir, f"{config_name}.conf")
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config.config_content)
            print(f"   ✅ Saved: {config_file}")
            
            # Save backup script
            backup_file = os.path.join(output_dir, f"{config_name}_backup.sh")
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(config.backup_script)
            os.chmod(backup_file, 0o755)
            print(f"   ✅ Saved: {backup_file}")
            
            # Save apply script
            apply_file = os.path.join(output_dir, f"{config_name}_apply.sh")
            with open(apply_file, 'w', encoding='utf-8') as f:
                f.write(config.apply_script)
            os.chmod(apply_file, 0o755)
            print(f"   ✅ Saved: {apply_file}")
            
            # Save test script
            test_file = os.path.join(output_dir, f"{config_name}_test.sh")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(config.test_script)
            os.chmod(test_file, 0o755)
            print(f"   ✅ Saved: {test_file}")
            
            # Save implementation notes
            notes_file = os.path.join(output_dir, f"{config_name}_notes.txt")
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(config.implementation_notes)
            print(f"   ✅ Saved: {notes_file}")
        
        print(f"\n✅ All configurations saved to {output_dir}")
    
    def generate_deployment_plan(
        self,
        configs: List[GeneratedConfig],
        output_file: str = "./deployment_plan.md"
    ):
        """
        Generate a deployment plan document.
        
        Args:
            configs: List of generated configurations
            output_file: Output file path
        """
        plan = []
        plan.append("# Security Hardening Deployment Plan")
        plan.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        plan.append(f"\nConfigurations: {len(configs)}")
        
        plan.append("\n## Overview\n")
        plan.append("This deployment plan provides step-by-step instructions for applying ")
        plan.append("security hardening configurations generated from vulnerability scan results.\n")
        
        plan.append("\n## Pre-Deployment Checklist\n")
        plan.append("- [ ] Review all configuration files")
        plan.append("- [ ] Verify backup systems are functioning")
        plan.append("- [ ] Schedule maintenance window")
        plan.append("- [ ] Notify stakeholders")
        plan.append("- [ ] Prepare rollback procedures")
        plan.append("- [ ] Test in development environment first\n")
        
        for i, config in enumerate(configs, 1):
            plan.append(f"\n## Step {i}: {config.metadata.config_type.value.upper()} Hardening\n")
            plan.append(f"**Hardening Level:** {config.metadata.hardening_level.value}  ")
            plan.append(f"**Target System:** {config.metadata.target_system}  ")
            plan.append(f"**Restart Required:** {'Yes' if config.metadata.restart_required else 'No'}  ")
            
            if hasattr(config, 'source_vulnerabilities'):
                plan.append(f"**Addresses Vulnerabilities:** {', '.join(config.source_vulnerabilities)}  ")
            
            plan.append("\n### Compliance Requirements\n")
            for req in config.compliance_status:
                plan.append(f"- **{req.framework.value.upper()}**: {req.control_id} - {req.description}")
            
            if config.warnings:
                plan.append("\n### ⚠️  Warnings\n")
                for warning in config.warnings:
                    plan.append(f"- {warning}")
            
            plan.append("\n### Deployment Steps\n")
            plan.append(f"1. **Backup current configuration:**")
            plan.append(f"   ```bash")
            plan.append(f"   ./{config.metadata.config_type.value}_{config.metadata.hardening_level.value}_backup.sh")
            plan.append(f"   ```\n")
            
            plan.append(f"2. **Test new configuration:**")
            plan.append(f"   ```bash")
            plan.append(f"   ./{config.metadata.config_type.value}_{config.metadata.hardening_level.value}_test.sh")
            plan.append(f"   ```\n")
            
            plan.append(f"3. **Apply configuration:**")
            plan.append(f"   ```bash")
            plan.append(f"   ./{config.metadata.config_type.value}_{config.metadata.hardening_level.value}_apply.sh")
            plan.append(f"   ```\n")
            
            plan.append(f"4. **Verify service status:**")
            if config.metadata.config_type == ConfigType.SSH:
                plan.append(f"   ```bash")
                plan.append(f"   systemctl status sshd")
                plan.append(f"   ```\n")
            elif config.metadata.config_type in [ConfigType.NGINX, ConfigType.APACHE]:
                service = config.metadata.config_type.value
                plan.append(f"   ```bash")
                plan.append(f"   systemctl status {service}")
                plan.append(f"   ```\n")
            
            plan.append(f"5. **Monitor logs for issues:**")
            plan.append(f"   ```bash")
            plan.append(f"   # Check for authentication or service errors")
            plan.append(f"   journalctl -u <service> -n 50 --no-pager")
            plan.append(f"   ```\n")
        
        plan.append("\n## Post-Deployment\n")
        plan.append("- [ ] Verify all services are running")
        plan.append("- [ ] Test application functionality")
        plan.append("- [ ] Monitor logs for 24 hours")
        plan.append("- [ ] Document any issues encountered")
        plan.append("- [ ] Update configuration management system")
        plan.append("- [ ] Schedule follow-up vulnerability scan\n")
        
        plan.append("\n## Rollback Procedures\n")
        plan.append("If issues occur, restore from backups:")
        plan.append("```bash")
        plan.append("# Restore backup (example for SSH)")
        plan.append("cp /etc/ssh/sshd_config.backup.$(date +%Y%m%d) /etc/ssh/sshd_config")
        plan.append("systemctl restart sshd")
        plan.append("```\n")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(plan))
        
        print(f"\n📋 Deployment plan saved to {output_file}")


def main():
    """Example usage of Jupiter Config Integration."""
    
    # Simulate Jupiter vulnerability scan results
    mock_scan_results = {
        "scan_id": "SCAN-2024-001",
        "target": "192.168.1.100",
        "timestamp": "2024-01-15T10:30:00Z",
        "vulnerabilities": [
            {
                "id": "SSH-001",
                "title": "Weak SSH Configuration",
                "severity": "critical",
                "description": "SSH server allows password authentication with weak ciphers",
                "affected_component": "OpenSSH 8.2p1"
            },
            {
                "id": "FW-001",
                "title": "No Firewall Rules",
                "severity": "critical",
                "description": "System has no firewall rules configured",
                "affected_component": "iptables"
            },
            {
                "id": "WEB-001",
                "title": "Missing Security Headers",
                "severity": "high",
                "description": "Nginx missing critical security headers (HSTS, CSP)",
                "affected_component": "Nginx 1.18.0"
            },
            {
                "id": "DB-001",
                "title": "Database Network Exposure",
                "severity": "critical",
                "description": "PostgreSQL accessible from external networks",
                "affected_component": "PostgreSQL 14.5"
            },
            {
                "id": "WEB-002",
                "title": "Weak TLS Configuration",
                "severity": "medium",
                "description": "Nginx supports TLS 1.0 and 1.1",
                "affected_component": "Nginx 1.18.0"
            }
        ]
    }
    
    # Initialize integration
    integration = JupiterConfigIntegration()
    
    # Process scan results with organizational compliance requirements
    results = integration.process_scan_results(
        scan_results=mock_scan_results,
        target_system="Ubuntu 22.04 LTS",
        organization_compliance=[
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.SOC2
        ]
    )
    
    # Save all generated configs
    integration.save_configs(
        configs=results['configs_generated'],
        output_dir="./remediation_configs"
    )
    
    # Generate deployment plan
    integration.generate_deployment_plan(
        configs=results['configs_generated'],
        output_file="./deployment_plan.md"
    )
    
    # Display statistics
    stats = integration.config_generator.get_statistics()
    print(f"\n{'='*70}")
    print("📈 CONFIG GENERATOR STATISTICS")
    print(f"{'='*70}")
    print(f"Total Configurations Generated: {stats['configs_generated']}")
    print(f"By Type: {json.dumps(stats['by_type'], indent=2)}")
    print(f"By Level: {json.dumps(stats['by_level'], indent=2)}")
    print(f"Compliance Checks: {stats['compliance_checks']}")
    print(f"Warnings Issued: {stats['warnings_issued']}")
    
    print(f"\n{'='*70}")
    print("✅ JUPITER CONFIG INTEGRATION COMPLETE")
    print(f"{'='*70}")
    print("\nNext Steps:")
    print("1. Review generated configurations in ./remediation_configs/")
    print("2. Review deployment plan in ./deployment_plan.md")
    print("3. Test configurations in development environment")
    print("4. Schedule production deployment during maintenance window")
    print("5. Run post-deployment vulnerability scan to verify fixes\n")


if __name__ == "__main__":
    main()
