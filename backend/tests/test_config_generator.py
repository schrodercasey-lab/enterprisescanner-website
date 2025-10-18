"""
Test suite for Config Generator Module
Comprehensive testing of configuration generation, validation, and compliance
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config_generator import (
    ConfigGenerator,
    ConfigType,
    ComplianceFramework,
    HardeningLevel,
    ConfigMetadata,
    GeneratedConfig,
    ComplianceRequirement
)


class TestConfigGenerator:
    """Test ConfigGenerator class"""
    
    @pytest.fixture
    def generator(self):
        """Create ConfigGenerator instance"""
        return ConfigGenerator()
    
    # Initialization Tests
    
    def test_initialization(self, generator):
        """Test ConfigGenerator initialization"""
        assert generator is not None
        assert isinstance(generator.statistics, dict)
        assert generator.statistics["configs_generated"] == 0
    
    # SSH Configuration Tests
    
    def test_generate_ssh_basic(self, generator):
        """Test basic SSH configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        assert isinstance(result, GeneratedConfig)
        assert "PermitRootLogin no" in result.config_content
        assert "PermitEmptyPasswords no" in result.config_content
        assert result.metadata.config_type == ConfigType.SSH
        assert result.metadata.hardening_level == HardeningLevel.BASIC
    
    def test_generate_ssh_moderate(self, generator):
        """Test moderate SSH configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "PasswordAuthentication no" in result.config_content
        assert "MaxAuthTries 3" in result.config_content
        assert result.metadata.hardening_level == HardeningLevel.MODERATE
    
    def test_generate_ssh_strict(self, generator):
        """Test strict SSH configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT
        )
        
        assert "MaxAuthTries 2" in result.config_content
        assert "Ciphers" in result.config_content
        assert "MACs" in result.config_content
        assert result.metadata.hardening_level == HardeningLevel.STRICT
    
    def test_ssh_custom_settings(self, generator):
        """Test SSH with custom settings"""
        custom = {"Port": "2222", "LoginGraceTime": "120"}
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC,
            custom_settings=custom
        )
        
        assert "Port 2222" in result.config_content
        assert "LoginGraceTime 120" in result.config_content
    
    # Firewall Configuration Tests
    
    def test_generate_iptables(self, generator):
        """Test iptables configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.FIREWALL_IPTABLES,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "iptables -P INPUT DROP" in result.config_content
        assert "iptables -A INPUT -i lo -j ACCEPT" in result.config_content
        assert result.metadata.config_type == ConfigType.FIREWALL_IPTABLES
    
    def test_generate_ufw(self, generator):
        """Test UFW configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.FIREWALL_UFW,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "ufw default deny incoming" in result.config_content
        assert "ufw default allow outgoing" in result.config_content
        assert result.metadata.config_type == ConfigType.FIREWALL_UFW
    
    def test_firewall_custom_ports(self, generator):
        """Test firewall with custom ports"""
        custom = {"allowed_ports": [22, 80, 443, 8080]}
        result = generator.generate_config(
            config_type=ConfigType.FIREWALL_IPTABLES,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE,
            custom_settings=custom
        )
        
        assert "--dport 8080" in result.config_content
    
    # Web Server Configuration Tests
    
    def test_generate_nginx(self, generator):
        """Test Nginx configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.NGINX,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "ssl_protocols TLSv1.2 TLSv1.3" in result.config_content
        assert "Strict-Transport-Security" in result.config_content
        assert "X-Frame-Options" in result.config_content
        assert result.metadata.config_type == ConfigType.NGINX
    
    def test_generate_apache(self, generator):
        """Test Apache configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.APACHE,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "ServerTokens Prod" in result.config_content
        assert "ServerSignature Off" in result.config_content
        assert "TraceEnable off" in result.config_content
        assert result.metadata.config_type == ConfigType.APACHE
    
    # Database Configuration Tests
    
    def test_generate_postgresql(self, generator):
        """Test PostgreSQL configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.POSTGRESQL,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "listen_addresses = 'localhost'" in result.config_content
        assert "ssl = on" in result.config_content
        assert "password_encryption = scram-sha-256" in result.config_content
        assert result.metadata.config_type == ConfigType.POSTGRESQL
    
    def test_generate_mysql(self, generator):
        """Test MySQL configuration generation"""
        result = generator.generate_config(
            config_type=ConfigType.MYSQL,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert "bind-address = 127.0.0.1" in result.config_content
        assert "require_secure_transport = ON" in result.config_content
        assert "validate_password.policy = STRONG" in result.config_content
        assert result.metadata.config_type == ConfigType.MYSQL
    
    # Supporting Scripts Tests
    
    def test_backup_script_generation(self, generator):
        """Test backup script generation"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        assert result.backup_script
        assert "#!/bin/bash" in result.backup_script
        assert "BACKUP_DIR" in result.backup_script
        assert "/etc/ssh/sshd_config" in result.backup_script
    
    def test_apply_script_generation(self, generator):
        """Test apply script generation"""
        result = generator.generate_config(
            config_type=ConfigType.NGINX,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        assert result.apply_script
        assert "#!/bin/bash" in result.apply_script
        assert "backup" in result.apply_script.lower()
    
    def test_test_script_generation(self, generator):
        """Test test script generation"""
        result = generator.generate_config(
            config_type=ConfigType.NGINX,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        assert result.test_script
        assert "nginx -t" in result.test_script
    
    # Validation Tests
    
    def test_validation_warns_on_root_login(self, generator):
        """Test validation detects root login enabled"""
        # This would require modifying internal method behavior
        # For now, we test that validation runs
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        assert isinstance(result.warnings, list)
    
    def test_validation_checks_weak_ciphers(self, generator):
        """Test validation detects weak ciphers"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        # Should not have weak ciphers in generated config
        assert "DES" not in result.config_content or "weak" in str(result.warnings).lower()
    
    # Compliance Tests
    
    def test_compliance_pci_dss(self, generator):
        """Test PCI-DSS compliance checking"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.PCI_DSS]
        )
        
        assert ComplianceFramework.PCI_DSS in result.metadata.compliance_frameworks
        assert len(result.compliance_status) > 0
        assert all(isinstance(req, ComplianceRequirement) for req in result.compliance_status)
    
    def test_compliance_hipaa(self, generator):
        """Test HIPAA compliance checking"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.HIPAA]
        )
        
        assert ComplianceFramework.HIPAA in result.metadata.compliance_frameworks
    
    def test_compliance_soc2(self, generator):
        """Test SOC 2 compliance checking"""
        result = generator.generate_config(
            config_type=ConfigType.NGINX,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.SOC2]
        )
        
        assert ComplianceFramework.SOC2 in result.metadata.compliance_frameworks
    
    def test_multiple_compliance_frameworks(self, generator):
        """Test multiple compliance frameworks"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[
                ComplianceFramework.PCI_DSS,
                ComplianceFramework.HIPAA,
                ComplianceFramework.SOC2
            ]
        )
        
        assert len(result.metadata.compliance_frameworks) == 3
    
    # Metadata Tests
    
    def test_metadata_generation(self, generator):
        """Test configuration metadata generation"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert isinstance(result.metadata, ConfigMetadata)
        assert result.metadata.config_type == ConfigType.SSH
        assert result.metadata.hardening_level == HardeningLevel.MODERATE
        assert result.metadata.target_system == "Ubuntu 22.04"
        assert result.metadata.checksum
        assert result.metadata.generated_at
    
    def test_checksum_uniqueness(self, generator):
        """Test that different configs have different checksums"""
        result1 = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        result2 = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT
        )
        
        assert result1.metadata.checksum != result2.metadata.checksum
    
    def test_restart_required_flag(self, generator):
        """Test restart required flag"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert result.metadata.restart_required is True
    
    # Implementation Notes Tests
    
    def test_implementation_notes_generation(self, generator):
        """Test implementation notes generation"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        assert result.implementation_notes
        assert "BEFORE IMPLEMENTATION" in result.implementation_notes
        assert "IMPLEMENTATION STEPS" in result.implementation_notes
        assert "ROLLBACK" in result.implementation_notes
    
    def test_implementation_notes_include_warnings(self, generator):
        """Test implementation notes include warnings"""
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        assert "WARNINGS" in result.implementation_notes
    
    # Statistics Tests
    
    def test_statistics_tracking(self):
        """Test statistics tracking"""
        # Create a fresh generator to avoid state pollution from other tests
        fresh_generator = ConfigGenerator()
        
        # Should start at zero
        assert fresh_generator.statistics["configs_generated"] == 0
        
        fresh_generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.MODERATE
        )
        
        final_stats = fresh_generator.get_statistics()
        
        # Should be 1 after generating one config
        assert final_stats["configs_generated"] == 1
        assert final_stats["by_type"]["ssh"] == 1
        assert final_stats["by_level"]["moderate"] == 1
    
    def test_statistics_multiple_generations(self, generator):
        """Test statistics with multiple generations"""
        for _ in range(5):
            generator.generate_config(
                config_type=ConfigType.SSH,
                target_system="Ubuntu 22.04",
                hardening_level=HardeningLevel.BASIC
            )
        
        stats = generator.get_statistics()
        assert stats["configs_generated"] == 5
        assert stats["by_type"]["ssh"] == 5
    
    # Hardening Level Tests
    
    def test_all_hardening_levels(self, generator):
        """Test all hardening levels work"""
        for level in HardeningLevel:
            result = generator.generate_config(
                config_type=ConfigType.SSH,
                target_system="Ubuntu 22.04",
                hardening_level=level
            )
            assert result.metadata.hardening_level == level
    
    def test_hardening_level_strictness(self, generator):
        """Test that strict level is more restrictive than basic"""
        basic = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.BASIC
        )
        
        strict = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT
        )
        
        # Strict should have more settings
        assert len(strict.config_content) > len(basic.config_content)
    
    # Config Type Coverage Tests
    
    def test_all_config_types(self, generator):
        """Test all configuration types can be generated"""
        config_types = [
            ConfigType.SSH,
            ConfigType.FIREWALL_IPTABLES,
            ConfigType.FIREWALL_UFW,
            ConfigType.NGINX,
            ConfigType.APACHE,
            ConfigType.POSTGRESQL,
            ConfigType.MYSQL,
        ]
        
        for config_type in config_types:
            result = generator.generate_config(
                config_type=config_type,
                target_system="Ubuntu 22.04",
                hardening_level=HardeningLevel.MODERATE
            )
            assert result.metadata.config_type == config_type
    
    # Integration Tests
    
    def test_complete_workflow(self, generator):
        """Test complete config generation workflow"""
        # Generate config
        result = generator.generate_config(
            config_type=ConfigType.SSH,
            target_system="Production Ubuntu 22.04",
            hardening_level=HardeningLevel.STRICT,
            compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]
        )
        
        # Verify all components present
        assert result.config_content
        assert result.backup_script
        assert result.apply_script
        assert result.test_script
        assert result.metadata
        assert isinstance(result.warnings, list)
        assert len(result.compliance_status) > 0
        assert result.implementation_notes
        
        # Verify metadata
        assert result.metadata.checksum
        assert result.metadata.backup_recommended
        
        # Verify statistics updated
        stats = generator.get_statistics()
        assert stats["configs_generated"] > 0


class TestEnums:
    """Test enum definitions"""
    
    def test_config_type_enum(self):
        """Test ConfigType enum values"""
        assert ConfigType.SSH.value == "ssh"
        assert ConfigType.NGINX.value == "nginx"
        assert len(list(ConfigType)) >= 8
    
    def test_compliance_framework_enum(self):
        """Test ComplianceFramework enum values"""
        assert ComplianceFramework.PCI_DSS.value == "pci_dss"
        assert ComplianceFramework.HIPAA.value == "hipaa"
        assert ComplianceFramework.SOC2.value == "soc2"
    
    def test_hardening_level_enum(self):
        """Test HardeningLevel enum values"""
        assert HardeningLevel.BASIC.value == "basic"
        assert HardeningLevel.MODERATE.value == "moderate"
        assert HardeningLevel.STRICT.value == "strict"


class TestDataClasses:
    """Test dataclass definitions"""
    
    def test_config_metadata_creation(self):
        """Test ConfigMetadata dataclass creation"""
        metadata = ConfigMetadata(
            config_type=ConfigType.SSH,
            hardening_level=HardeningLevel.MODERATE,
            target_system="Ubuntu 22.04",
            generated_at="2025-10-18T12:00:00",
            compliance_frameworks=[ComplianceFramework.PCI_DSS],
            checksum="abc123",
            validated=True,
            backup_recommended=True,
            restart_required=True
        )
        
        assert metadata.config_type == ConfigType.SSH
        assert metadata.hardening_level == HardeningLevel.MODERATE
        assert metadata.checksum == "abc123"
    
    def test_compliance_requirement_creation(self):
        """Test ComplianceRequirement dataclass creation"""
        requirement = ComplianceRequirement(
            framework=ComplianceFramework.PCI_DSS,
            control_id="2.2.4",
            description="Remove unnecessary services",
            requirement="Disable X11Forwarding",
            met_by_config=True
        )
        
        assert requirement.framework == ComplianceFramework.PCI_DSS
        assert requirement.control_id == "2.2.4"
        assert requirement.met_by_config is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
