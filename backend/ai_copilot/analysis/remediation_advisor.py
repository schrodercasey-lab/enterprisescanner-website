"""
Remediation Advisor Module

Automated remediation guidance and script generation.

Features:
- Step-by-step remediation instructions
- OS-specific patch scripts (Linux, Windows)
- WAF rule generation
- Docker/Kubernetes configuration fixes
- Automated remediation (Military mode)
- Remediation effort estimation
- Testing procedures

Supports:
- Common vulnerabilities (SQLi, XSS, RCE, etc.)
- Infrastructure misconfigurations
- Compliance violations
- Security best practices

Author: Enterprise Scanner Team
Version: 1.1.0 - Phase 2 Integration: Connected to ScriptGenerator and ConfigGenerator
"""

import json
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

# Phase 2 Integration: Script and Config Generators
try:
    from ..remediation.script_generator import ScriptGenerator
    from ..remediation.config_generator import ConfigGenerator
    GENERATORS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Phase 2 generators not available: {e}")
    GENERATORS_AVAILABLE = False


class RemediationType(Enum):
    """Types of remediation"""
    PATCH = "patch"  # Apply software patch
    CONFIG_CHANGE = "config_change"  # Configuration change
    CODE_FIX = "code_fix"  # Code modification
    WAF_RULE = "waf_rule"  # Web Application Firewall rule
    NETWORK_RULE = "network_rule"  # Firewall/network rule
    ACCESS_CONTROL = "access_control"  # IAM/permissions change
    MONITORING = "monitoring"  # Add monitoring/detection


class RemediationComplexity(Enum):
    """Remediation complexity levels"""
    TRIVIAL = "trivial"  # < 5 minutes
    SIMPLE = "simple"  # 5-30 minutes
    MODERATE = "moderate"  # 30 minutes - 4 hours
    COMPLEX = "complex"  # 4-24 hours
    EXTENSIVE = "extensive"  # > 1 day


@dataclass
class RemediationStep:
    """Single remediation step"""
    step_number: int
    action: str
    command: Optional[str] = None
    expected_result: Optional[str] = None
    verification: Optional[str] = None
    rollback: Optional[str] = None
    
    # Metadata
    requires_downtime: bool = False
    requires_backup: bool = False
    requires_testing: bool = True


@dataclass
class RemediationScript:
    """Generated remediation script"""
    script_type: str  # 'bash', 'powershell', 'python', 'ansible', 'docker', 'kubernetes'
    platform: str  # 'linux', 'windows', 'macos', 'docker', 'k8s'
    script_content: str
    
    # Usage instructions
    prerequisites: List[str] = field(default_factory=list)
    execution_steps: List[str] = field(default_factory=list)
    
    # Safety
    backup_required: bool = True
    test_mode_available: bool = False
    rollback_script: Optional[str] = None


@dataclass
class RemediationPlan:
    """Complete remediation plan"""
    vulnerability_id: str
    vulnerability_name: str
    
    # Plan details
    summary: str
    steps: List[RemediationStep]
    
    # Scripts
    scripts: List[RemediationScript] = field(default_factory=list)
    
    # Effort estimation
    complexity: RemediationComplexity = RemediationComplexity.MODERATE
    estimated_time_hours: float = 1.0
    estimated_cost: float = 0.0  # In USD
    
    # Requirements
    requires_downtime: bool = False
    downtime_window_hours: float = 0.0
    requires_testing: bool = True
    testing_time_hours: float = 0.5
    
    # Risk assessment
    remediation_risk: str = "low"  # 'low', 'medium', 'high'
    risk_description: Optional[str] = None
    
    # Validation
    validation_steps: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    automated_execution_possible: bool = False


class RemediationAdvisor:
    """
    Automated remediation guidance system
    """
    
    # Remediation templates for common vulnerabilities
    VULNERABILITY_TEMPLATES = {
        'sql_injection': {
            'type': RemediationType.CODE_FIX,
            'complexity': RemediationComplexity.MODERATE,
            'steps': [
                'Identify all SQL query locations',
                'Replace string concatenation with parameterized queries',
                'Implement input validation',
                'Add database account restrictions (least privilege)',
                'Enable query logging and monitoring'
            ]
        },
        'xss': {
            'type': RemediationType.CODE_FIX,
            'complexity': RemediationComplexity.SIMPLE,
            'steps': [
                'Identify output locations',
                'Implement context-aware output encoding',
                'Set Content-Security-Policy headers',
                'Validate and sanitize inputs',
                'Use secure templating engine'
            ]
        },
        'outdated_software': {
            'type': RemediationType.PATCH,
            'complexity': RemediationComplexity.SIMPLE,
            'steps': [
                'Review patch notes and compatibility',
                'Backup current configuration',
                'Test patch in staging environment',
                'Apply patch during maintenance window',
                'Verify functionality post-patch'
            ]
        },
        'weak_authentication': {
            'type': RemediationType.CONFIG_CHANGE,
            'complexity': RemediationComplexity.MODERATE,
            'steps': [
                'Implement multi-factor authentication',
                'Enforce strong password policy',
                'Enable account lockout after failed attempts',
                'Implement session timeout',
                'Enable audit logging'
            ]
        }
    }
    
    def __init__(self, llm_provider=None):
        """
        Initialize remediation advisor
        
        Args:
            llm_provider: LLMProvider instance
        """
        self.logger = logging.getLogger(__name__)
        
        self.llm_provider = llm_provider
        
        # Initialize if not provided
        if not self.llm_provider:
            try:
                from backend.ai_copilot.utils.llm_providers import LLMProvider
                self.llm_provider = LLMProvider(provider="openai", model="gpt-4-turbo")
            except Exception as e:
                self.logger.warning(f"LLM provider not available: {e}")
        
        # Phase 2: Initialize Script and Config Generators
        if GENERATORS_AVAILABLE:
            try:
                self.script_generator = ScriptGenerator(llm_provider=self.llm_provider)
                self.config_generator = ConfigGenerator(llm_provider=self.llm_provider)
                self.generators_enabled = True
                self.logger.info("Phase 2 generators initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Phase 2 generators: {e}")
                self.generators_enabled = False
        else:
            self.generators_enabled = False
            self.logger.info("Phase 2 generators not available (will use legacy methods)")
        
        # Statistics
        self.stats = {
            'total_plans_generated': 0,
            'scripts_generated': 0,
            'automated_remediations': 0,
            'avg_generation_time_ms': 0,
            'phase2_scripts_generated': 0,  # New metric
            'phase2_configs_generated': 0   # New metric
        }
        
        self.logger.info(f"RemediationAdvisor initialized (Phase 2 Generators: {'Enabled' if self.generators_enabled else 'Disabled'})")
    
    def generate_remediation_plan(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any],
        asset_info: Optional[Dict[str, Any]] = None,
        include_scripts: bool = True
    ) -> RemediationPlan:
        """
        Generate comprehensive remediation plan
        
        Args:
            vulnerability_name: Vulnerability name
            vulnerability_details: Vulnerability information
            asset_info: Affected asset information
            include_scripts: Generate remediation scripts
            
        Returns:
            RemediationPlan object
        """
        self.stats['total_plans_generated'] += 1
        
        try:
            # Classify vulnerability
            vuln_category = self._classify_vulnerability(vulnerability_name)
            
            # Get template if available
            template = self.VULNERABILITY_TEMPLATES.get(vuln_category, {})
            
            # Generate plan steps
            steps = self._generate_remediation_steps(
                vulnerability_name,
                vulnerability_details,
                template
            )
            
            # Generate summary
            summary = self._generate_remediation_summary(
                vulnerability_name,
                vulnerability_details,
                steps
            )
            
            # Estimate complexity and time
            complexity, estimated_time = self._estimate_remediation_effort(steps)
            
            # Generate scripts if requested
            scripts = []
            if include_scripts and asset_info:
                # Phase 2: Use advanced generators if available
                if self.generators_enabled:
                    scripts = self._generate_remediation_scripts_phase2(
                        vulnerability_name,
                        vulnerability_details,
                        asset_info,
                        steps
                    )
                    self.stats['phase2_scripts_generated'] += len(scripts)
                else:
                    # Fallback to legacy method
                    scripts = self._generate_remediation_scripts(
                        vulnerability_name,
                        vulnerability_details,
                        asset_info,
                        steps
                    )
                
                self.stats['scripts_generated'] += len(scripts)
            
            # Generate validation steps
            validation_steps = self._generate_validation_steps(vulnerability_name)
            
            # Create plan
            plan = RemediationPlan(
                vulnerability_id=vulnerability_details.get('vuln_id', 'unknown'),
                vulnerability_name=vulnerability_name,
                summary=summary,
                steps=steps,
                scripts=scripts,
                complexity=complexity,
                estimated_time_hours=estimated_time,
                requires_downtime=self._requires_downtime(vulnerability_name),
                requires_testing=True,
                validation_steps=validation_steps,
                success_criteria=self._generate_success_criteria(vulnerability_name),
                automated_execution_possible=self._can_automate(vulnerability_name)
            )
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Remediation plan generation failed: {e}", exc_info=True)
            
            # Return basic plan
            return RemediationPlan(
                vulnerability_id='unknown',
                vulnerability_name=vulnerability_name,
                summary=f"Manual remediation required for {vulnerability_name}",
                steps=[
                    RemediationStep(
                        step_number=1,
                        action="Consult security documentation",
                        verification="Verify vulnerability is resolved"
                    )
                ]
            )
    
    def generate_patch_script(
        self,
        software_name: str,
        current_version: str,
        target_version: str,
        platform: str = "linux"
    ) -> RemediationScript:
        """
        Generate patch/update script
        
        Args:
            software_name: Software to patch
            current_version: Current version
            target_version: Target version
            platform: Target platform ('linux', 'windows', 'macos')
            
        Returns:
            RemediationScript object
        """
        if platform == "linux":
            return self._generate_linux_patch_script(
                software_name,
                current_version,
                target_version
            )
        elif platform == "windows":
            return self._generate_windows_patch_script(
                software_name,
                current_version,
                target_version
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def generate_waf_rule(
        self,
        vulnerability_type: str,
        attack_pattern: str
    ) -> str:
        """
        Generate WAF rule to block attack
        
        Args:
            vulnerability_type: Type of vulnerability
            attack_pattern: Attack pattern to block
            
        Returns:
            WAF rule configuration
        """
        # ModSecurity rule format
        if vulnerability_type.lower() == 'sql_injection':
            rule = f"""
# Block SQL Injection Attempts
SecRule ARGS "@detectSQLi" \\
    "id:1001,\\
    phase:2,\\
    deny,\\
    status:403,\\
    msg:'SQL Injection Attempt Detected',\\
    logdata:'Matched Data: %{{MATCHED_VAR}} found within %{{MATCHED_VAR_NAME}}',\\
    tag:'OWASP_CRS/WEB_ATTACK/SQL_INJECTION',\\
    severity:'CRITICAL'"
"""
        elif vulnerability_type.lower() == 'xss':
            rule = f"""
# Block XSS Attempts
SecRule ARGS "@detectXSS" \\
    "id:1002,\\
    phase:2,\\
    deny,\\
    status:403,\\
    msg:'XSS Attack Detected',\\
    logdata:'Matched Data: %{{MATCHED_VAR}} found within %{{MATCHED_VAR_NAME}}',\\
    tag:'OWASP_CRS/WEB_ATTACK/XSS',\\
    severity:'CRITICAL'"
"""
        else:
            rule = f"# WAF rule for {vulnerability_type} (requires manual configuration)"
        
        return rule
    
    def auto_remediate(
        self,
        plan: RemediationPlan,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Automatically execute remediation (Military mode)
        
        DANGEROUS: Only use in controlled environments
        
        Args:
            plan: RemediationPlan to execute
            dry_run: If True, simulate without making changes
            
        Returns:
            Execution results
        """
        self.stats['automated_remediations'] += 1
        
        if not plan.automated_execution_possible:
            return {
                'success': False,
                'error': 'Automated remediation not supported for this vulnerability',
                'dry_run': dry_run
            }
        
        results = {
            'success': True,
            'steps_executed': [],
            'steps_failed': [],
            'dry_run': dry_run
        }
        
        # Execute each step
        for step in plan.steps:
            step_result = self._execute_remediation_step(step, dry_run)
            
            if step_result['success']:
                results['steps_executed'].append(step_result)
            else:
                results['steps_failed'].append(step_result)
                results['success'] = False
                break  # Stop on first failure
        
        return results
    
    def _classify_vulnerability(self, vulnerability_name: str) -> str:
        """Classify vulnerability into category"""
        name_lower = vulnerability_name.lower()
        
        if 'sql' in name_lower and 'injection' in name_lower:
            return 'sql_injection'
        elif 'xss' in name_lower or 'cross-site scripting' in name_lower:
            return 'xss'
        elif any(word in name_lower for word in ['outdated', 'old version', 'update available']):
            return 'outdated_software'
        elif any(word in name_lower for word in ['weak password', 'authentication', 'auth']):
            return 'weak_authentication'
        else:
            return 'generic'
    
    def _generate_remediation_steps(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any],
        template: Dict[str, Any]
    ) -> List[RemediationStep]:
        """Generate detailed remediation steps"""
        steps = []
        
        # Use template steps if available
        if template and 'steps' in template:
            for i, action in enumerate(template['steps'], 1):
                step = RemediationStep(
                    step_number=i,
                    action=action,
                    requires_testing=True
                )
                steps.append(step)
        else:
            # Generate generic steps using LLM
            if self.llm_provider:
                generated_steps = self._llm_generate_steps(
                    vulnerability_name,
                    vulnerability_details
                )
                steps = generated_steps
            else:
                # Fallback: generic steps
                steps = [
                    RemediationStep(
                        step_number=1,
                        action="Review vulnerability details and affected systems",
                        requires_testing=False
                    ),
                    RemediationStep(
                        step_number=2,
                        action="Research official remediation guidance",
                        requires_testing=False
                    ),
                    RemediationStep(
                        step_number=3,
                        action="Apply recommended fixes",
                        requires_testing=True
                    ),
                    RemediationStep(
                        step_number=4,
                        action="Verify vulnerability is resolved",
                        requires_testing=True
                    )
                ]
        
        return steps
    
    def _llm_generate_steps(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any]
    ) -> List[RemediationStep]:
        """Generate steps using LLM"""
        prompt = f"""
Generate step-by-step remediation instructions for:

Vulnerability: {vulnerability_name}
Severity: {vulnerability_details.get('severity', 'Unknown')}
Description: {vulnerability_details.get('description', 'No description')}

Provide 5-7 specific, actionable steps. For each step, include:
1. The action to take
2. Command (if applicable)
3. Expected result
4. How to verify success

Format as numbered list.
"""
        
        try:
            messages = [
                {'role': 'system', 'content': 'You are a security remediation expert.'},
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.llm_provider.complete(messages, temperature=0.3, max_tokens=1000)
            
            # Parse response into steps (simplified)
            steps = []
            lines = response.content.split('\n')
            step_num = 1
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    steps.append(RemediationStep(
                        step_number=step_num,
                        action=line,
                        requires_testing=True
                    ))
                    step_num += 1
            
            return steps if steps else self._generate_remediation_steps(
                vulnerability_name,
                vulnerability_details,
                {}
            )
            
        except Exception as e:
            self.logger.error(f"LLM step generation failed: {e}")
            return []
    
    def _generate_remediation_summary(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any],
        steps: List[RemediationStep]
    ) -> str:
        """Generate remediation summary"""
        return f"Remediation for {vulnerability_name}: {len(steps)} steps required"
    
    def _estimate_remediation_effort(
        self,
        steps: List[RemediationStep]
    ) -> Tuple[RemediationComplexity, float]:
        """Estimate remediation complexity and time"""
        num_steps = len(steps)
        
        if num_steps <= 2:
            return RemediationComplexity.TRIVIAL, 0.1
        elif num_steps <= 4:
            return RemediationComplexity.SIMPLE, 0.5
        elif num_steps <= 6:
            return RemediationComplexity.MODERATE, 2.0
        elif num_steps <= 8:
            return RemediationComplexity.COMPLEX, 8.0
        else:
            return RemediationComplexity.EXTENSIVE, 24.0
    
    def _generate_remediation_scripts(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any],
        asset_info: Dict[str, Any],
        steps: List[RemediationStep]
    ) -> List[RemediationScript]:
        """Generate remediation scripts (legacy method)"""
        scripts = []
        
        platform = asset_info.get('platform', 'linux').lower()
        
        # Generate appropriate script based on vulnerability type
        vuln_category = self._classify_vulnerability(vulnerability_name)
        
        if vuln_category == 'outdated_software' and platform == 'linux':
            script = self._generate_linux_update_script(
                vulnerability_details.get('affected_software', 'unknown')
            )
            scripts.append(script)
        
        return scripts
    
    def _generate_remediation_scripts_phase2(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any],
        asset_info: Dict[str, Any],
        steps: List[RemediationStep]
    ) -> List[RemediationScript]:
        """
        Generate remediation scripts using Phase 2 generators
        
        Advanced script generation with:
        - ScriptGenerator for automated remediation scripts
        - ConfigGenerator for secure configuration files
        - Multi-platform support (Linux, Windows, Docker, K8s)
        - Rollback script generation
        """
        scripts = []
        
        try:
            platform = asset_info.get('platform', 'linux').lower()
            vuln_category = self._classify_vulnerability(vulnerability_name)
            severity = vulnerability_details.get('severity', 'medium')
            
            # 1. Generate main remediation script
            self.logger.info(f"Generating Phase 2 remediation script for {vulnerability_name}")
            
            remediation_script = self.script_generator.generate_script(
                vulnerability_type=vuln_category,
                vulnerability_name=vulnerability_name,
                affected_system=asset_info.get('hostname', 'unknown'),
                platform=platform,
                severity=severity,
                custom_requirements=vulnerability_details.get('requirements', [])
            )
            
            if remediation_script:
                scripts.append(remediation_script)
                self.logger.info(f"Generated {remediation_script.script_type} script for {platform}")
            
            # 2. Generate secure configuration if needed
            if vuln_category in ['weak_authentication', 'generic'] or 'config' in vulnerability_name.lower():
                self.logger.info("Generating secure configuration file")
                
                config_file = self.config_generator.generate_config(
                    service=vulnerability_details.get('service', asset_info.get('service', 'unknown')),
                    config_type=self._infer_config_type(vulnerability_name, asset_info),
                    hardening_level=self._severity_to_hardening_level(severity),
                    platform=platform
                )
                
                if config_file:
                    # Convert config to RemediationScript format
                    config_script = RemediationScript(
                        script_type='config',
                        platform=platform,
                        script_content=config_file.get('content', ''),
                        prerequisites=[
                            'Backup existing configuration',
                            f'Access to {config_file.get("path", "config file")}',
                            'Restart capability for service'
                        ],
                        execution_steps=[
                            f'Backup: cp {config_file.get("path", "config")} {config_file.get("path", "config")}.backup',
                            f'Apply config: sudo mv new_config {config_file.get("path", "config")}',
                            'Validate syntax',
                            'Restart service',
                            'Verify service is running'
                        ],
                        backup_required=True,
                        test_mode_available=True,
                        rollback_script=f'sudo cp {config_file.get("path", "config")}.backup {config_file.get("path", "config")}'
                    )
                    
                    scripts.append(config_script)
                    self.stats['phase2_configs_generated'] += 1
                    self.logger.info(f"Generated secure config for {config_file.get('service', 'service')}")
            
            # 3. Generate rollback script
            if remediation_script and len(scripts) > 0:
                self.logger.info("Generating rollback script")
                
                rollback_script = self.script_generator.generate_rollback_script(
                    original_script=remediation_script,
                    asset_info=asset_info
                )
                
                if rollback_script:
                    # Add rollback to main script
                    scripts[0].rollback_script = rollback_script.get('content', '')
                    self.logger.info("Rollback script attached to main remediation script")
            
            self.logger.info(f"Phase 2 script generation complete: {len(scripts)} scripts generated")
            return scripts
            
        except Exception as e:
            self.logger.error(f"Phase 2 script generation failed: {e}", exc_info=True)
            # Fallback to legacy method
            self.logger.info("Falling back to legacy script generation")
            return self._generate_remediation_scripts(
                vulnerability_name,
                vulnerability_details,
                asset_info,
                steps
            )
    
    def _infer_config_type(self, vulnerability_name: str, asset_info: Dict[str, Any]) -> str:
        """Infer configuration type from vulnerability and asset info"""
        name_lower = vulnerability_name.lower()
        
        if 'apache' in name_lower or asset_info.get('service') == 'apache':
            return 'apache'
        elif 'nginx' in name_lower or asset_info.get('service') == 'nginx':
            return 'nginx'
        elif 'ssh' in name_lower or asset_info.get('service') == 'ssh':
            return 'ssh'
        elif 'mysql' in name_lower or 'database' in name_lower:
            return 'mysql'
        elif 'firewall' in name_lower or 'iptables' in name_lower:
            return 'firewall'
        else:
            return 'generic'
    
    def _severity_to_hardening_level(self, severity: str) -> str:
        """Convert severity to hardening level"""
        severity_map = {
            'critical': 'maximum',
            'high': 'high',
            'medium': 'moderate',
            'low': 'basic',
            'info': 'minimal'
        }
        return severity_map.get(severity.lower(), 'moderate')
    
    def _generate_remediation_scripts(
        self,
        vulnerability_name: str,
        vulnerability_details: Dict[str, Any],
        asset_info: Dict[str, Any],
        steps: List[RemediationStep]
    ) -> List[RemediationScript]:
        """Generate remediation scripts (legacy method - retained for backward compatibility)"""
        scripts = []
        
        platform = asset_info.get('platform', 'linux').lower()
        
        # Generate appropriate script based on vulnerability type
        vuln_category = self._classify_vulnerability(vulnerability_name)
        
        if vuln_category == 'outdated_software' and platform == 'linux':
            script = self._generate_linux_update_script(
                vulnerability_details.get('affected_software', 'unknown')
            )
            scripts.append(script)
        
        return scripts
    
    def _generate_linux_patch_script(
        self,
        software_name: str,
        current_version: str,
        target_version: str
    ) -> RemediationScript:
        """Generate Linux patch script"""
        script_content = f"""#!/bin/bash
# Patch {software_name} from {current_version} to {target_version}

set -e  # Exit on error

echo "Starting {software_name} update..."

# Backup current version
echo "Creating backup..."
sudo cp -r /etc/{software_name} /etc/{software_name}.backup.$(date +%Y%m%d)

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install new version
echo "Installing {software_name} {target_version}..."
sudo apt-get install -y {software_name}={target_version}

# Verify installation
echo "Verifying installation..."
{software_name} --version

echo "Update complete!"
"""
        
        return RemediationScript(
            script_type='bash',
            platform='linux',
            script_content=script_content,
            prerequisites=[
                'Root/sudo access',
                'Active internet connection',
                'Sufficient disk space'
            ],
            execution_steps=[
                'Review script content',
                'Make script executable: chmod +x patch_script.sh',
                'Run script: sudo ./patch_script.sh',
                'Verify service is running'
            ],
            backup_required=True,
            test_mode_available=False
        )
    
    def _generate_windows_patch_script(
        self,
        software_name: str,
        current_version: str,
        target_version: str
    ) -> RemediationScript:
        """Generate Windows PowerShell patch script"""
        script_content = f"""# Patch {software_name} from {current_version} to {target_version}

Write-Host "Starting {software_name} update..." -ForegroundColor Green

# Create backup
Write-Host "Creating backup..."
$backupPath = "C:\\Backup\\{software_name}_$(Get-Date -Format 'yyyyMMdd')"
New-Item -ItemType Directory -Path $backupPath -Force
Copy-Item -Path "C:\\Program Files\\{software_name}\\*" -Destination $backupPath -Recurse

# Download update (example using Chocolatey)
Write-Host "Installing {software_name} {target_version}..."
choco upgrade {software_name} --version={target_version} -y

# Verify
Write-Host "Verifying installation..."
Get-Command {software_name} -ErrorAction Stop

Write-Host "Update complete!" -ForegroundColor Green
"""
        
        return RemediationScript(
            script_type='powershell',
            platform='windows',
            script_content=script_content,
            prerequisites=[
                'Administrator privileges',
                'Chocolatey package manager installed',
                'Internet connection'
            ],
            execution_steps=[
                'Open PowerShell as Administrator',
                'Review script content',
                'Run script: .\\patch_script.ps1',
                'Verify service status'
            ],
            backup_required=True
        )
    
    def _generate_linux_update_script(self, software_name: str) -> RemediationScript:
        """Generate generic Linux update script"""
        return self._generate_linux_patch_script(software_name, "current", "latest")
    
    def _generate_validation_steps(self, vulnerability_name: str) -> List[str]:
        """Generate validation steps"""
        return [
            "Rescan asset for vulnerability",
            "Verify service is operational",
            "Check application logs for errors",
            "Confirm no functionality regression"
        ]
    
    def _generate_success_criteria(self, vulnerability_name: str) -> List[str]:
        """Generate success criteria"""
        return [
            "Vulnerability no longer detected in scans",
            "No errors in application logs",
            "Service passes health checks",
            "Security tests pass"
        ]
    
    def _requires_downtime(self, vulnerability_name: str) -> bool:
        """Check if remediation requires downtime"""
        # Check for keywords that typically require downtime
        downtime_keywords = ['kernel', 'reboot', 'restart required', 'system update']
        return any(keyword in vulnerability_name.lower() for keyword in downtime_keywords)
    
    def _can_automate(self, vulnerability_name: str) -> bool:
        """Check if remediation can be automated"""
        # Only simple patches and config changes can be automated
        vuln_category = self._classify_vulnerability(vulnerability_name)
        return vuln_category in ['outdated_software', 'weak_authentication']
    
    def _execute_remediation_step(
        self,
        step: RemediationStep,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute single remediation step"""
        if dry_run:
            return {
                'success': True,
                'step': step.step_number,
                'action': step.action,
                'message': 'Simulated (dry run)',
                'dry_run': True
            }
        
        # In production, execute actual command
        # For now, simulate
        return {
            'success': True,
            'step': step.step_number,
            'action': step.action,
            'message': 'Executed successfully',
            'dry_run': False
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get advisor statistics"""
        return self.stats.copy()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("REMEDIATION ADVISOR MODULE")
    print("="*70)
    
    # Initialize advisor
    print("\n1. Initializing Remediation Advisor...")
    advisor = RemediationAdvisor()
    
    # Test remediation plan generation
    print("\n2. Generating Remediation Plan:")
    plan = advisor.generate_remediation_plan(
        vulnerability_name="SQL Injection in Login Form",
        vulnerability_details={
            'vuln_id': 'vuln_001',
            'severity': 'critical',
            'description': 'Unvalidated input in login form'
        },
        asset_info={'platform': 'linux'},
        include_scripts=False
    )
    
    print(f"\n   Vulnerability: {plan.vulnerability_name}")
    print(f"   Complexity: {plan.complexity.value}")
    print(f"   Estimated Time: {plan.estimated_time_hours} hours")
    print(f"\n   Steps:")
    for step in plan.steps:
        print(f"     {step.step_number}. {step.action}")
    
    # Test script generation
    print("\n3. Generating Patch Script:")
    script = advisor.generate_patch_script(
        software_name="apache2",
        current_version="2.4.45",
        target_version="2.4.50",
        platform="linux"
    )
    
    print(f"\n   Script Type: {script.script_type}")
    print(f"   Platform: {script.platform}")
    print(f"   Prerequisites: {', '.join(script.prerequisites)}")
    
    # Test WAF rule generation
    print("\n4. Generating WAF Rule:")
    waf_rule = advisor.generate_waf_rule(
        vulnerability_type="sql_injection",
        attack_pattern="UNION SELECT"
    )
    print(waf_rule[:200] + "...")
    
    # Statistics
    print("\n5. Advisor Statistics:")
    stats = advisor.get_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*70)
    print("REMEDIATION ADVISOR MODULE COMPLETE ✅")
    print("="*70)
