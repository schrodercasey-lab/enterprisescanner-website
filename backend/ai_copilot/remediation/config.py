"""
Jupiter v3.0 - Module G.1: Configuration Management
Centralized configuration for autonomous remediation engine

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List
from pathlib import Path


@dataclass
class RemediationConfig:
    """Central configuration for remediation engine"""
    
    # Database Configuration
    database_path: str = "jupiter_remediation.db"
    connection_pool_size: int = 5
    connection_timeout: int = 30
    enable_wal_mode: bool = True
    
    # Risk Analysis Configuration
    risk_weights: Dict[str, float] = field(default_factory=lambda: {
        'severity': 0.25,
        'exploitability': 0.20,
        'asset_criticality': 0.20,
        'patch_maturity': 0.15,
        'dependencies': 0.10,
        'rollback_complexity': 0.10
    })
    
    autonomy_thresholds: Dict[int, float] = field(default_factory=lambda: {
        5: 0.85,  # FULL_AUTONOMY
        4: 0.70,  # HIGH_AUTONOMY
        3: 0.50,  # APPROVAL_REQUIRED
        2: 0.30,  # SUPERVISED
        1: 0.15,  # AI_ASSISTED
        0: 0.0    # MANUAL_ONLY
    })
    
    # Business Hours Configuration
    business_hours_start: int = 9
    business_hours_end: int = 17
    business_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Monday-Friday
    timezone: str = "UTC"
    
    # Compliance Configuration
    high_impact_compliance: List[str] = field(default_factory=lambda: [
        'PCI-DSS', 'HIPAA', 'SOX', 'FISMA', 'FedRAMP', 'GDPR', 'CCPA'
    ])
    
    # Caching Configuration
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    max_cache_entries: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "remediation.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_max_bytes: int = 10485760  # 10 MB
    log_backup_count: int = 5
    
    # Execution Configuration
    max_concurrent_remediations: int = 10
    execution_timeout_seconds: int = 3600  # 1 hour
    sandbox_timeout_seconds: int = 1800  # 30 minutes
    monitoring_duration_seconds: int = 300  # 5 minutes
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay_seconds: int = 60
    exponential_backoff: bool = True
    
    # Snapshot Configuration
    snapshot_retention_days: int = 30
    auto_cleanup_expired_snapshots: bool = True
    snapshot_verification_enabled: bool = True
    
    # Patch Configuration
    patch_signature_verification: bool = True
    patch_maturity_threshold_days: int = 7  # Minimum patch age for full autonomy
    trusted_patch_sources: List[str] = field(default_factory=lambda: [
        'vendor_official', 'os_package_manager', 'docker_registry'
    ])
    
    # Deployment Strategy Configuration
    default_strategy: str = "blue-green"
    canary_stages: List[int] = field(default_factory=lambda: [5, 25, 50, 100])  # Traffic %
    rolling_batch_size: int = 5
    deployment_health_check_interval: int = 30  # seconds
    
    # ML Model Configuration
    ml_model_path: str = "models/remediation_risk_model.pkl"
    ml_confidence_threshold: float = 0.85
    ml_retraining_interval_days: int = 30
    ml_min_training_samples: int = 1000
    
    # Audit Configuration
    blockchain_enabled: bool = False
    blockchain_network: str = "hyperledger"
    audit_retention_months: int = 12
    
    # Alert Configuration
    alert_on_autonomy_level: List[int] = field(default_factory=lambda: [3, 4, 5])
    alert_on_rollback: bool = True
    alert_on_failure: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ['email', 'slack'])
    
    @classmethod
    def from_file(cls, config_path: str) -> 'RemediationConfig':
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            RemediationConfig instance
        """
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to JSON file
        
        Args:
            config_path: Path to save JSON configuration
        """
        config_dict = asdict(self)
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def from_env(cls) -> 'RemediationConfig':
        """
        Load configuration from environment variables
        
        Environment variables should be prefixed with JUPITER_REMEDIATION_
        Example: JUPITER_REMEDIATION_DATABASE_PATH
        
        Returns:
            RemediationConfig instance
        """
        config = cls()
        
        # Override with environment variables if present
        env_mapping = {
            'JUPITER_REMEDIATION_DATABASE_PATH': 'database_path',
            'JUPITER_REMEDIATION_LOG_LEVEL': 'log_level',
            'JUPITER_REMEDIATION_CACHE_ENABLED': 'cache_enabled',
            'JUPITER_REMEDIATION_MAX_CONCURRENT': 'max_concurrent_remediations',
            'JUPITER_REMEDIATION_BLOCKCHAIN_ENABLED': 'blockchain_enabled',
        }
        
        for env_var, attr_name in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Type conversion based on attribute type
                attr_type = type(getattr(config, attr_name))
                if attr_type == bool:
                    value = value.lower() in ('true', '1', 'yes')
                elif attr_type == int:
                    value = int(value)
                elif attr_type == float:
                    value = float(value)
                setattr(config, attr_name, value)
        
        return config
    
    def validate(self) -> List[str]:
        """
        Validate configuration values
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate business hours
        if not 0 <= self.business_hours_start < 24:
            errors.append(f"Invalid business_hours_start: {self.business_hours_start} (must be 0-23)")
        if not 0 <= self.business_hours_end < 24:
            errors.append(f"Invalid business_hours_end: {self.business_hours_end} (must be 0-23)")
        if self.business_hours_start >= self.business_hours_end:
            errors.append("business_hours_start must be before business_hours_end")
        
        # Validate weights sum
        weights_sum = sum(self.risk_weights.values())
        if not 0.99 <= weights_sum <= 1.01:  # Allow small floating point errors
            errors.append(f"Risk weights must sum to 1.0, got {weights_sum}")
        
        # Validate thresholds are descending
        sorted_thresholds = sorted(self.autonomy_thresholds.items(), key=lambda x: x[0], reverse=True)
        for i in range(len(sorted_thresholds) - 1):
            if sorted_thresholds[i][1] < sorted_thresholds[i+1][1]:
                errors.append(f"Autonomy thresholds must be descending")
                break
        
        # Validate timeouts
        if self.execution_timeout_seconds <= 0:
            errors.append(f"execution_timeout_seconds must be positive")
        if self.sandbox_timeout_seconds <= 0:
            errors.append(f"sandbox_timeout_seconds must be positive")
        
        # Validate cache settings
        if self.cache_enabled and self.cache_ttl_seconds <= 0:
            errors.append(f"cache_ttl_seconds must be positive when caching enabled")
        
        # Validate ML settings
        if self.ml_confidence_threshold < 0 or self.ml_confidence_threshold > 1:
            errors.append(f"ml_confidence_threshold must be between 0 and 1")
        
        return errors


# Global configuration instance
_global_config: RemediationConfig = None


def get_config() -> RemediationConfig:
    """
    Get global configuration instance (singleton pattern)
    
    Returns:
        RemediationConfig instance
    """
    global _global_config
    
    if _global_config is None:
        # Try to load from file, then env, then defaults
        config_file = os.getenv('JUPITER_REMEDIATION_CONFIG', 'remediation_config.json')
        
        if os.path.exists(config_file):
            _global_config = RemediationConfig.from_file(config_file)
        else:
            _global_config = RemediationConfig.from_env()
        
        # Validate configuration
        errors = _global_config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")
    
    return _global_config


def set_config(config: RemediationConfig) -> None:
    """
    Set global configuration instance
    
    Args:
        config: RemediationConfig instance
    """
    global _global_config
    
    # Validate before setting
    errors = config.validate()
    if errors:
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")
    
    _global_config = config


def reset_config() -> None:
    """Reset global configuration to None (useful for testing)"""
    global _global_config
    _global_config = None


# Example usage
if __name__ == "__main__":
    # Create default config
    config = RemediationConfig()
    
    # Validate
    errors = config.validate()
    if errors:
        print(f"❌ Validation errors: {errors}")
    else:
        print("✅ Configuration valid")
    
    # Save to file
    config.save_to_file("remediation_config.json")
    print(f"✅ Configuration saved to remediation_config.json")
    
    # Load from file
    loaded_config = RemediationConfig.from_file("remediation_config.json")
    print(f"✅ Configuration loaded from file")
    
    # Print sample values
    print(f"\nSample Configuration:")
    print(f"  Database: {loaded_config.database_path}")
    print(f"  Cache Enabled: {loaded_config.cache_enabled}")
    print(f"  Log Level: {loaded_config.log_level}")
    print(f"  Max Concurrent: {loaded_config.max_concurrent_remediations}")
    print(f"  Business Hours: {loaded_config.business_hours_start}:00-{loaded_config.business_hours_end}:00")
