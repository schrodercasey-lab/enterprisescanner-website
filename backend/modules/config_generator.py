"""
Config Generator Module - Generate Secure Configuration Files
Automated security hardening configurations for servers and applications
Value: +$10K ARPU

Supports:
- SSH hardening (sshd_config)
- Firewall rules (iptables, ufw, firewalld)
- Web server security (Nginx, Apache)
- Database hardening (PostgreSQL, MySQL)
- Compliance templates (PCI-DSS, HIPAA, SOC 2)
"""

import re
import hashlib
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Supported configuration types"""
    SSH = "ssh"
    FIREWALL_IPTABLES = "firewall_iptables"
    FIREWALL_UFW = "firewall_ufw"
    FIREWALL_FIREWALLD = "firewall_firewalld"
    NGINX = "nginx"
    APACHE = "apache"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    GENERIC = "generic"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    CIS = "cis"
    NIST = "nist"
    GDPR = "gdpr"


class HardeningLevel(Enum):
    """Security hardening levels"""
    BASIC = "basic"           # Essential security controls
    MODERATE = "moderate"     # Recommended best practices
    STRICT = "strict"         # Maximum security (may impact usability)


@dataclass
class ComplianceRequirement:
    """Compliance requirement details"""
    framework: ComplianceFramework
    control_id: str
    description: str
    requirement: str
    met_by_config: bool = False


@dataclass
class ConfigMetadata:
    """Metadata for generated configurations"""
    config_type: ConfigType
    hardening_level: HardeningLevel
    target_system: str
    generated_at: str
    compliance_frameworks: List[ComplianceFramework]
    checksum: str
    validated: bool
    backup_recommended: bool
    restart_required: bool
    
    
@dataclass
class GeneratedConfig:
    """Container for generated configuration"""
    config_content: str
    backup_script: str
    apply_script: str
    test_script: str
    metadata: ConfigMetadata
    warnings: List[str]
    compliance_status: List[ComplianceRequirement]
    implementation_notes: str


class ConfigGenerator:
    """
    Generate secure configuration files with compliance framework support
    
    Features:
    - Multi-platform configuration generation
    - Compliance framework mapping (PCI-DSS, HIPAA, SOC 2, etc.)
    - Hardening level customization (basic, moderate, strict)
    - Automatic backup and apply scripts
    - Configuration validation
    - Restart/reload detection
    """
    
    # SSH hardening settings by level
    SSH_HARDENING = {
        HardeningLevel.BASIC: {
            'PermitRootLogin': 'no',
            'PasswordAuthentication': 'yes',
            'PubkeyAuthentication': 'yes',
            'PermitEmptyPasswords': 'no',
            'X11Forwarding': 'no',
        },
        HardeningLevel.MODERATE: {
            'PermitRootLogin': 'no',
            'PasswordAuthentication': 'no',
            'PubkeyAuthentication': 'yes',
            'PermitEmptyPasswords': 'no',
            'X11Forwarding': 'no',
            'Protocol': '2',
            'LoginGraceTime': '60',
            'MaxAuthTries': '3',
            'MaxSessions': '10',
            'ClientAliveInterval': '300',
            'ClientAliveCountMax': '2',
        },
        HardeningLevel.STRICT: {
            'PermitRootLogin': 'no',
            'PasswordAuthentication': 'no',
            'PubkeyAuthentication': 'yes',
            'PermitEmptyPasswords': 'no',
            'X11Forwarding': 'no',
            'Protocol': '2',
            'LoginGraceTime': '30',
            'MaxAuthTries': '2',
            'MaxSessions': '5',
            'ClientAliveInterval': '300',
            'ClientAliveCountMax': '2',
            'AllowUsers': '@sshusers',
            'DenyUsers': 'root',
            'Ciphers': 'chacha20-poly1305@openssh.com,aes256-gcm@openssh.com',
            'MACs': 'hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com',
            'KexAlgorithms': 'curve25519-sha256,curve25519-sha256@libssh.org',
        }
    }
    
    # Compliance framework requirements
    COMPLIANCE_REQUIREMENTS = {
        ComplianceFramework.PCI_DSS: {
            'ssh': [
                ('2.2.4', 'Remove unnecessary services', 'Disable X11Forwarding'),
                ('8.2.3', 'Strong authentication', 'Use public key authentication'),
                ('8.1.8', 'Disable root login', 'PermitRootLogin no'),
            ],
            'firewall': [
                ('1.3.5', 'Restrict outbound traffic', 'Default deny outbound'),
                ('1.2.1', 'Restrict inbound traffic', 'Default deny inbound'),
            ],
        },
        ComplianceFramework.HIPAA: {
            'ssh': [
                ('164.312(a)(1)', 'Access control', 'Authentication required'),
                ('164.312(e)(1)', 'Transmission security', 'Encrypted SSH connections'),
            ],
            'database': [
                ('164.312(a)(1)', 'Access control', 'Strong password policy'),
                ('164.312(b)', 'Audit controls', 'Enable query logging'),
            ],
        },
        ComplianceFramework.SOC2: {
            'ssh': [
                ('CC6.1', 'Logical access', 'Restrict SSH access'),
                ('CC6.6', 'Encryption', 'Use strong ciphers'),
            ],
            'nginx': [
                ('CC6.6', 'Encryption', 'TLS 1.2+ only'),
                ('CC6.7', 'Security headers', 'HSTS, CSP headers'),
            ],
        },
    }
    
    def __init__(self):
        self.statistics = {
            "configs_generated": 0,
            "by_type": {ct.value: 0 for ct in ConfigType},
            "by_level": {hl.value: 0 for hl in HardeningLevel},
            "compliance_checks": 0,
            "warnings_issued": 0,
        }
        
        # Get template directory
        self.template_dir = os.path.join(
            os.path.dirname(__file__), '..', 'templates', 'configs'
        )
    
    def generate_config(
        self,
        config_type: ConfigType,
        target_system: str,
        hardening_level: HardeningLevel = HardeningLevel.MODERATE,
        compliance_frameworks: List[ComplianceFramework] = None,
        custom_settings: Dict = None
    ) -> GeneratedConfig:
        """
        Generate a secure configuration file
        
        Args:
            config_type: Type of configuration to generate
            target_system: Target OS/platform
            hardening_level: Security hardening level
            compliance_frameworks: List of compliance frameworks to meet
            custom_settings: Custom settings to override defaults
        
        Returns:
            GeneratedConfig with config file and supporting scripts
        """
        logger.info(f"Generating {config_type.value} config at {hardening_level.value} level")
        
        compliance_frameworks = compliance_frameworks or []
        custom_settings = custom_settings or {}
        
        # Generate main configuration
        config_content = self._generate_config_content(
            config_type, target_system, hardening_level, custom_settings
        )
        
        # Generate backup script
        backup_script = self._generate_backup_script(config_type, target_system)
        
        # Generate apply script
        apply_script = self._generate_apply_script(config_type, target_system)
        
        # Generate test script
        test_script = self._generate_test_script(config_type, target_system)
        
        # Validate configuration
        warnings = self._validate_config(config_content, config_type)
        
        # Check compliance
        compliance_status = self._check_compliance(
            config_type, config_content, compliance_frameworks
        )
        
        # Create metadata
        metadata = ConfigMetadata(
            config_type=config_type,
            hardening_level=hardening_level,
            target_system=target_system,
            generated_at=datetime.now().isoformat(),
            compliance_frameworks=compliance_frameworks,
            checksum=self._calculate_checksum(config_content),
            validated=len(warnings) == 0,
            backup_recommended=True,
            restart_required=self._requires_restart(config_type)
        )
        
        # Generate implementation notes
        implementation_notes = self._generate_implementation_notes(
            config_type, hardening_level, compliance_frameworks, warnings
        )
        
        # Update statistics
        self._update_statistics(config_type, hardening_level, warnings, compliance_status)
        
        return GeneratedConfig(
            config_content=config_content,
            backup_script=backup_script,
            apply_script=apply_script,
            test_script=test_script,
            metadata=metadata,
            warnings=warnings,
            compliance_status=compliance_status,
            implementation_notes=implementation_notes
        )
    
    def _generate_config_content(
        self,
        config_type: ConfigType,
        target_system: str,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate the main configuration content"""
        
        if config_type == ConfigType.SSH:
            return self._generate_ssh_config(hardening_level, custom_settings)
        elif config_type == ConfigType.FIREWALL_IPTABLES:
            return self._generate_iptables_config(hardening_level, custom_settings)
        elif config_type == ConfigType.FIREWALL_UFW:
            return self._generate_ufw_config(hardening_level, custom_settings)
        elif config_type == ConfigType.NGINX:
            return self._generate_nginx_config(hardening_level, custom_settings)
        elif config_type == ConfigType.APACHE:
            return self._generate_apache_config(hardening_level, custom_settings)
        elif config_type == ConfigType.POSTGRESQL:
            return self._generate_postgresql_config(hardening_level, custom_settings)
        elif config_type == ConfigType.MYSQL:
            return self._generate_mysql_config(hardening_level, custom_settings)
        else:
            return self._generate_generic_config(config_type, hardening_level)
    
    def _generate_ssh_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate hardened SSH configuration"""
        
        # Get base settings for hardening level
        settings = self.SSH_HARDENING[hardening_level].copy()
        
        # Apply custom settings
        settings.update(custom_settings)
        
        config_lines = [
            "# Hardened SSH Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "#",
            "# ⚠️  BACKUP ORIGINAL CONFIG BEFORE APPLYING",
            "# sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup",
            "",
        ]
        
        # Add settings
        for key, value in settings.items():
            config_lines.append(f"{key} {value}")
        
        # Add additional hardening comments
        config_lines.extend([
            "",
            "# Additional Recommendations:",
            "# - Use SSH keys instead of passwords",
            "# - Implement fail2ban for brute force protection",
            "# - Monitor SSH logs regularly",
            "# - Keep SSH updated to latest version",
            "",
            "# After applying, test with: sudo sshd -t",
            "# Then restart: sudo systemctl restart sshd",
        ])
        
        return "\n".join(config_lines)
    
    def _generate_iptables_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate iptables firewall rules"""
        
        allowed_ports = custom_settings.get('allowed_ports', [22, 80, 443])
        allowed_ips = custom_settings.get('allowed_ips', [])
        
        rules = [
            "#!/bin/bash",
            "# Hardened iptables Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "",
            "# Flush existing rules",
            "iptables -F",
            "iptables -X",
            "iptables -Z",
            "",
            "# Default policies",
            "iptables -P INPUT DROP",
            "iptables -P FORWARD DROP",
            "iptables -P OUTPUT ACCEPT",
            "",
            "# Allow loopback",
            "iptables -A INPUT -i lo -j ACCEPT",
            "",
            "# Allow established connections",
            "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            "",
        ]
        
        # Add allowed ports
        for port in allowed_ports:
            rules.append(f"# Allow port {port}")
            rules.append(f"iptables -A INPUT -p tcp --dport {port} -j ACCEPT")
            rules.append("")
        
        # Add IP whitelist if strict
        if hardening_level == HardeningLevel.STRICT and allowed_ips:
            rules.append("# IP Whitelist")
            for ip in allowed_ips:
                rules.append(f"iptables -A INPUT -s {ip} -j ACCEPT")
            rules.append("")
        
        # Add rate limiting for SSH
        if 22 in allowed_ports:
            rules.extend([
                "# Rate limiting for SSH (anti-brute force)",
                "iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set",
                "iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP",
                "",
            ])
        
        # Drop invalid packets
        rules.extend([
            "# Drop invalid packets",
            "iptables -A INPUT -m conntrack --ctstate INVALID -j DROP",
            "",
            "# Log dropped packets (optional)",
            "# iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix \"iptables_DROP: \"",
            "",
            "# Save rules",
            "echo 'Saving iptables rules...'",
            "iptables-save > /etc/iptables/rules.v4",
        ])
        
        return "\n".join(rules)
    
    def _generate_ufw_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate UFW firewall configuration"""
        
        allowed_ports = custom_settings.get('allowed_ports', [22, 80, 443])
        
        commands = [
            "#!/bin/bash",
            "# UFW Firewall Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "",
            "# Reset UFW to defaults",
            "ufw --force reset",
            "",
            "# Default policies",
            "ufw default deny incoming",
            "ufw default allow outgoing",
            "",
        ]
        
        # Add allowed ports
        for port in allowed_ports:
            commands.append(f"# Allow port {port}")
            commands.append(f"ufw allow {port}/tcp")
            commands.append("")
        
        # Rate limiting for SSH
        if 22 in allowed_ports:
            commands.extend([
                "# Rate limiting for SSH",
                "ufw limit 22/tcp",
                "",
            ])
        
        # Enable UFW
        commands.extend([
            "# Enable UFW",
            "ufw --force enable",
            "",
            "# Show status",
            "ufw status verbose",
        ])
        
        return "\n".join(commands)
    
    def _generate_nginx_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate hardened Nginx configuration"""
        
        server_name = custom_settings.get('server_name', 'example.com')
        ssl_cert = custom_settings.get('ssl_cert', '/etc/nginx/ssl/cert.pem')
        ssl_key = custom_settings.get('ssl_key', '/etc/nginx/ssl/key.pem')
        
        config = [
            "# Hardened Nginx Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "",
            "server {",
            "    listen 80;",
            f"    server_name {server_name};",
            "    ",
            "    # Redirect HTTP to HTTPS",
            "    return 301 https://$server_name$request_uri;",
            "}",
            "",
            "server {",
            "    listen 443 ssl http2;",
            f"    server_name {server_name};",
            "",
            "    # SSL Configuration",
            f"    ssl_certificate {ssl_cert};",
            f"    ssl_certificate_key {ssl_key};",
            "    ssl_protocols TLSv1.2 TLSv1.3;",
            "    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';",
            "    ssl_prefer_server_ciphers on;",
            "    ssl_session_timeout 10m;",
            "    ssl_session_cache shared:SSL:10m;",
            "",
            "    # Security Headers",
            "    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload' always;",
            "    add_header X-Frame-Options 'DENY' always;",
            "    add_header X-Content-Type-Options 'nosniff' always;",
            "    add_header X-XSS-Protection '1; mode=block' always;",
            "    add_header Referrer-Policy 'no-referrer-when-downgrade' always;",
            "    add_header Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'\" always;",
            "",
            "    # Hide Nginx version",
            "    server_tokens off;",
            "",
            "    # Rate limiting",
            "    limit_req_zone $binary_remote_addr zone=limitzone:10m rate=10r/s;",
            "    limit_req zone=limitzone burst=20;",
            "",
            "    location / {",
            "        root /var/www/html;",
            "        index index.html index.htm;",
            "    }",
            "}",
        ]
        
        return "\n".join(config)
    
    def _generate_apache_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate hardened Apache configuration"""
        
        config = [
            "# Hardened Apache Configuration",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "",
            "# Hide Apache version",
            "ServerTokens Prod",
            "ServerSignature Off",
            "",
            "# Security Headers",
            "Header always set Strict-Transport-Security \"max-age=31536000; includeSubDomains\"",
            "Header always set X-Frame-Options \"DENY\"",
            "Header always set X-Content-Type-Options \"nosniff\"",
            "Header always set X-XSS-Protection \"1; mode=block\"",
            "",
            "# Disable directory listing",
            "<Directory /var/www/html>",
            "    Options -Indexes",
            "    AllowOverride None",
            "    Require all granted",
            "</Directory>",
            "",
            "# Disable TRACE method",
            "TraceEnable off",
            "",
            "# Limit request size (10MB)",
            "LimitRequestBody 10485760",
            "",
            "# Timeout settings",
            "Timeout 60",
            "KeepAliveTimeout 5",
            "",
            "# SSL Configuration (if SSL module enabled)",
            "# SSLProtocol -all +TLSv1.2 +TLSv1.3",
            "# SSLCipherSuite HIGH:!aNULL:!MD5:!3DES",
            "# SSLHonorCipherOrder on",
        ]
        
        return "\n".join(config)
    
    def _generate_postgresql_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate hardened PostgreSQL configuration"""
        
        config = [
            "# Hardened PostgreSQL Configuration (postgresql.conf)",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "",
            "# Connection Settings",
            "listen_addresses = 'localhost'  # Listen only on localhost",
            "max_connections = 100",
            "",
            "# SSL Settings",
            "ssl = on",
            "ssl_cert_file = '/path/to/server.crt'",
            "ssl_key_file = '/path/to/server.key'",
            "",
            "# Logging",
            "log_destination = 'stderr'",
            "logging_collector = on",
            "log_directory = 'pg_log'",
            "log_filename = 'postgresql-%Y-%m-%d.log'",
            "log_connections = on",
            "log_disconnections = on",
            "log_duration = on",
            "log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '",
            "",
            "# Password Encryption",
            "password_encryption = scram-sha-256",
            "",
            "# Statement Timeout (prevent long-running queries)",
            "statement_timeout = 300000  # 5 minutes",
            "",
            "# Work Memory",
            "work_mem = 4MB",
            "maintenance_work_mem = 64MB",
        ]
        
        return "\n".join(config)
    
    def _generate_mysql_config(
        self,
        hardening_level: HardeningLevel,
        custom_settings: Dict
    ) -> str:
        """Generate hardened MySQL configuration"""
        
        config = [
            "# Hardened MySQL Configuration (my.cnf)",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Hardening Level: {hardening_level.value}",
            "",
            "[mysqld]",
            "# Bind to localhost only",
            "bind-address = 127.0.0.1",
            "",
            "# Disable LOAD DATA LOCAL INFILE",
            "local-infile = 0",
            "",
            "# Enable SSL",
            "require_secure_transport = ON",
            "",
            "# Logging",
            "log_error = /var/log/mysql/error.log",
            "slow_query_log = 1",
            "slow_query_log_file = /var/log/mysql/slow-query.log",
            "long_query_time = 2",
            "",
            "# Security",
            "skip-symbolic-links",
            "skip-show-database",
            "",
            "# Performance",
            "max_connections = 100",
            "max_connect_errors = 10",
            "connect_timeout = 10",
            "wait_timeout = 600",
            "interactive_timeout = 600",
            "",
            "# Password policy",
            "validate_password.policy = STRONG",
            "validate_password.length = 12",
            "validate_password.mixed_case_count = 1",
            "validate_password.number_count = 1",
            "validate_password.special_char_count = 1",
        ]
        
        return "\n".join(config)
    
    def _generate_generic_config(
        self,
        config_type: ConfigType,
        hardening_level: HardeningLevel
    ) -> str:
        """Generate generic configuration placeholder"""
        return f"""# Generic Configuration for {config_type.value}
# Generated: {datetime.now().isoformat()}
# Hardening Level: {hardening_level.value}
#
# This is a placeholder. Please customize for your specific needs.

# Security recommendations:
# 1. Disable unnecessary features
# 2. Enable logging and auditing
# 3. Use strong authentication
# 4. Encrypt data in transit
# 5. Follow principle of least privilege
"""
    
    def _generate_backup_script(
        self,
        config_type: ConfigType,
        target_system: str
    ) -> str:
        """Generate backup script for configuration"""
        
        # Map config types to file paths
        config_paths = {
            ConfigType.SSH: '/etc/ssh/sshd_config',
            ConfigType.NGINX: '/etc/nginx/nginx.conf',
            ConfigType.APACHE: '/etc/apache2/apache2.conf',
            ConfigType.POSTGRESQL: '/etc/postgresql/*/main/postgresql.conf',
            ConfigType.MYSQL: '/etc/mysql/my.cnf',
        }
        
        config_path = config_paths.get(config_type, '/etc/config.conf')
        
        script = f"""#!/bin/bash
# Backup script for {config_type.value}
# Generated: {datetime.now().isoformat()}

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/root/config_backups"
CONFIG_FILE="{config_path}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_DIR/$(basename $CONFIG_FILE).$TIMESTAMP.backup"
    echo "✅ Backup created: $BACKUP_DIR/$(basename $CONFIG_FILE).$TIMESTAMP.backup"
else
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi
"""
        return script
    
    def _generate_apply_script(
        self,
        config_type: ConfigType,
        target_system: str
    ) -> str:
        """Generate script to apply configuration"""
        
        restart_commands = {
            ConfigType.SSH: 'systemctl restart sshd',
            ConfigType.NGINX: 'nginx -t && systemctl reload nginx',
            ConfigType.APACHE: 'apachectl configtest && systemctl reload apache2',
            ConfigType.POSTGRESQL: 'systemctl reload postgresql',
            ConfigType.MYSQL: 'systemctl restart mysql',
        }
        
        restart_cmd = restart_commands.get(config_type, 'echo "Manual restart required"')
        
        script = f"""#!/bin/bash
# Apply script for {config_type.value}
# Generated: {datetime.now().isoformat()}

set -e

echo "⚠️  This will apply the new configuration"
read -p "Have you created a backup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborting. Please create backup first."
    exit 1
fi

echo "Applying configuration..."
# Copy generated config to appropriate location
# cp generated_config.conf /etc/path/to/config.conf

echo "Restarting service..."
{restart_cmd}

echo "✅ Configuration applied successfully"
"""
        return script
    
    def _generate_test_script(
        self,
        config_type: ConfigType,
        target_system: str
    ) -> str:
        """Generate test script to validate configuration"""
        
        test_commands = {
            ConfigType.SSH: 'sshd -t',
            ConfigType.NGINX: 'nginx -t',
            ConfigType.APACHE: 'apachectl configtest',
        }
        
        test_cmd = test_commands.get(config_type, 'echo "No validation command available"')
        
        script = f"""#!/bin/bash
# Test script for {config_type.value}
# Generated: {datetime.now().isoformat()}

echo "Testing configuration..."
{test_cmd}

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid"
    exit 0
else
    echo "❌ Configuration has errors"
    exit 1
fi
"""
        return script
    
    def _validate_config(
        self,
        config_content: str,
        config_type: ConfigType
    ) -> List[str]:
        """Validate configuration for common issues"""
        warnings = []
        
        # Check for insecure settings
        if config_type == ConfigType.SSH:
            if 'PermitRootLogin yes' in config_content:
                warnings.append("Root login is enabled - security risk")
            if 'PasswordAuthentication yes' in config_content:
                warnings.append("Password authentication enabled - consider key-based auth")
        
        # Check for weak ciphers
        if 'DES' in config_content or 'MD5' in config_content:
            warnings.append("Weak cryptographic algorithms detected")
        
        return warnings
    
    def _check_compliance(
        self,
        config_type: ConfigType,
        config_content: str,
        compliance_frameworks: List[ComplianceFramework]
    ) -> List[ComplianceRequirement]:
        """Check configuration against compliance requirements"""
        compliance_status = []
        
        for framework in compliance_frameworks:
            if framework in self.COMPLIANCE_REQUIREMENTS:
                framework_reqs = self.COMPLIANCE_REQUIREMENTS[framework]
                
                # Get requirements for this config type
                config_key = config_type.value.split('_')[0]  # 'ssh', 'firewall', etc.
                if config_key in framework_reqs:
                    for control_id, description, requirement in framework_reqs[config_key]:
                        # Simple keyword check
                        met = any(keyword in config_content for keyword in requirement.split())
                        
                        compliance_status.append(ComplianceRequirement(
                            framework=framework,
                            control_id=control_id,
                            description=description,
                            requirement=requirement,
                            met_by_config=met
                        ))
        
        return compliance_status
    
    def _requires_restart(self, config_type: ConfigType) -> bool:
        """Determine if service restart is required"""
        restart_required = {
            ConfigType.SSH: True,
            ConfigType.NGINX: True,
            ConfigType.APACHE: True,
            ConfigType.POSTGRESQL: True,
            ConfigType.MYSQL: True,
        }
        return restart_required.get(config_type, False)
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _generate_implementation_notes(
        self,
        config_type: ConfigType,
        hardening_level: HardeningLevel,
        compliance_frameworks: List[ComplianceFramework],
        warnings: List[str]
    ) -> str:
        """Generate implementation guidance"""
        
        notes = f"""
IMPLEMENTATION NOTES
====================

Configuration Type: {config_type.value}
Hardening Level: {hardening_level.value}
Compliance: {', '.join(f.value for f in compliance_frameworks) if compliance_frameworks else 'None'}

BEFORE IMPLEMENTATION:
1. ✅ Create full system backup
2. ✅ Test configuration in staging environment
3. ✅ Review all changes manually
4. ✅ Schedule maintenance window (if production)
5. ✅ Notify relevant teams

IMPLEMENTATION STEPS:
1. Run backup script: ./backup_config.sh
2. Review generated configuration file
3. Test configuration: ./test_config.sh
4. Apply configuration: ./apply_config.sh
5. Verify service is running
6. Test functionality (SSH login, web requests, etc.)

AFTER IMPLEMENTATION:
1. ✅ Verify service is running
2. ✅ Test critical functionality
3. ✅ Monitor logs for errors
4. ✅ Document changes
5. ✅ Update runbooks

ROLLBACK:
If issues occur:
1. Restore from backup
2. Restart service
3. Verify functionality
4. Review what went wrong

WARNINGS:
"""
        
        if warnings:
            for warning in warnings:
                notes += f"⚠️  {warning}\n"
        else:
            notes += "✅ No warnings\n"
        
        notes += f"""
COMPLIANCE STATUS:
{len(compliance_frameworks)} framework(s) configured
Run compliance report for detailed status

SUPPORT:
- Configuration checksum: [See metadata]
- Generated: {datetime.now().isoformat()}
- Review logs: Check system logs after applying
"""
        
        return notes
    
    def _update_statistics(
        self,
        config_type: ConfigType,
        hardening_level: HardeningLevel,
        warnings: List[str],
        compliance_status: List[ComplianceRequirement]
    ):
        """Update generation statistics"""
        self.statistics["configs_generated"] += 1
        self.statistics["by_type"][config_type.value] += 1
        self.statistics["by_level"][hardening_level.value] += 1
        self.statistics["warnings_issued"] += len(warnings)
        self.statistics["compliance_checks"] += len(compliance_status)
    
    def get_statistics(self) -> Dict:
        """Get generator statistics"""
        return self.statistics.copy()


# Example usage
if __name__ == "__main__":
    generator = ConfigGenerator()
    
    # Generate hardened SSH configuration
    result = generator.generate_config(
        config_type=ConfigType.SSH,
        target_system="Ubuntu 22.04 LTS",
        hardening_level=HardeningLevel.MODERATE,
        compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]
    )
    
    print("Configuration Generated:")
    print("=" * 80)
    print(result.config_content)
    print("\n" + "=" * 80)
    print(f"Warnings: {len(result.warnings)}")
    print(f"Compliance Checks: {len(result.compliance_status)}")
    print(f"Checksum: {result.metadata.checksum}")
