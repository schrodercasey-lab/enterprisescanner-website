"""
Production Configuration Management for Phase 3
Handles environment-specific settings, secrets, and runtime configuration
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Phase3Config:
    """Phase 3 configuration settings"""
    
    # ===== Environment Settings =====
    environment: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    
    # ===== Logging Configuration =====
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE", None))
    log_format: str = field(default_factory=lambda: os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    # ===== Script Generator Settings =====
    script_output_dir: str = field(default_factory=lambda: os.getenv(
        "SCRIPT_OUTPUT_DIR",
        "./generated_scripts"
    ))
    max_script_size: int = field(default_factory=lambda: int(os.getenv(
        "MAX_SCRIPT_SIZE",
        "10485760"  # 10MB
    )))
    script_retention_days: int = field(default_factory=lambda: int(os.getenv(
        "SCRIPT_RETENTION_DAYS",
        "30"
    )))
    enable_script_validation: bool = field(default_factory=lambda: os.getenv(
        "ENABLE_SCRIPT_VALIDATION",
        "True"
    ).lower() == "true")
    
    # ===== Config Generator Settings =====
    config_output_dir: str = field(default_factory=lambda: os.getenv(
        "CONFIG_OUTPUT_DIR",
        "./generated_configs"
    ))
    backup_configs: bool = field(default_factory=lambda: os.getenv(
        "BACKUP_CONFIGS",
        "True"
    ).lower() == "true")
    config_backup_dir: str = field(default_factory=lambda: os.getenv(
        "CONFIG_BACKUP_DIR",
        "./config_backups"
    ))
    default_hardening_level: str = field(default_factory=lambda: os.getenv(
        "DEFAULT_HARDENING_LEVEL",
        "standard"
    ))
    
    # ===== Proactive Monitor Settings =====
    monitoring_interval: int = field(default_factory=lambda: int(os.getenv(
        "MONITORING_INTERVAL",
        "300"  # 5 minutes
    )))
    alert_retention_days: int = field(default_factory=lambda: int(os.getenv(
        "ALERT_RETENTION_DAYS",
        "90"
    )))
    default_monitoring_level: str = field(default_factory=lambda: os.getenv(
        "DEFAULT_MONITORING_LEVEL",
        "medium"
    ))
    enable_anomaly_detection: bool = field(default_factory=lambda: os.getenv(
        "ENABLE_ANOMALY_DETECTION",
        "True"
    ).lower() == "true")
    anomaly_confidence_threshold: float = field(default_factory=lambda: float(os.getenv(
        "ANOMALY_CONFIDENCE_THRESHOLD",
        "0.8"
    )))
    
    # ===== Alert Channel Configuration =====
    # Email
    email_enabled: bool = field(default_factory=lambda: os.getenv(
        "EMAIL_ENABLED",
        "False"
    ).lower() == "true")
    email_smtp_host: Optional[str] = field(default_factory=lambda: os.getenv("SMTP_HOST"))
    email_smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    email_use_tls: bool = field(default_factory=lambda: os.getenv(
        "EMAIL_USE_TLS",
        "True"
    ).lower() == "true")
    email_from: Optional[str] = field(default_factory=lambda: os.getenv("EMAIL_FROM"))
    email_password: Optional[str] = field(default_factory=lambda: os.getenv("EMAIL_PASSWORD"))
    email_to_list: List[str] = field(default_factory=lambda: [
        email.strip() 
        for email in os.getenv("EMAIL_TO_LIST", "").split(",") 
        if email.strip()
    ])
    
    # Slack
    slack_enabled: bool = field(default_factory=lambda: os.getenv(
        "SLACK_ENABLED",
        "False"
    ).lower() == "true")
    slack_webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL"))
    slack_channel: str = field(default_factory=lambda: os.getenv("SLACK_CHANNEL", "#security-alerts"))
    
    # Webhook
    webhook_enabled: bool = field(default_factory=lambda: os.getenv(
        "WEBHOOK_ENABLED",
        "False"
    ).lower() == "true")
    webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("WEBHOOK_URL"))
    webhook_auth_token: Optional[str] = field(default_factory=lambda: os.getenv("WEBHOOK_AUTH_TOKEN"))
    webhook_timeout: int = field(default_factory=lambda: int(os.getenv("WEBHOOK_TIMEOUT", "10")))
    
    # SMS (placeholder for future implementation)
    sms_enabled: bool = field(default_factory=lambda: os.getenv(
        "SMS_ENABLED",
        "False"
    ).lower() == "true")
    sms_provider: str = field(default_factory=lambda: os.getenv("SMS_PROVIDER", "twilio"))
    
    # ===== Performance Settings =====
    max_concurrent_operations: int = field(default_factory=lambda: int(os.getenv(
        "MAX_CONCURRENT_OPS",
        "10"
    )))
    operation_timeout: int = field(default_factory=lambda: int(os.getenv(
        "OPERATION_TIMEOUT",
        "300"  # 5 minutes
    )))
    enable_performance_monitoring: bool = field(default_factory=lambda: os.getenv(
        "ENABLE_PERFORMANCE_MONITORING",
        "True"
    ).lower() == "true")
    
    # ===== Database Settings =====
    db_path: str = field(default_factory=lambda: os.getenv(
        "PHASE3_DB_PATH",
        "./phase3.db"
    ))
    db_backup_enabled: bool = field(default_factory=lambda: os.getenv(
        "DB_BACKUP_ENABLED",
        "True"
    ).lower() == "true")
    db_backup_interval: int = field(default_factory=lambda: int(os.getenv(
        "DB_BACKUP_INTERVAL",
        "86400"  # 24 hours
    )))
    
    # ===== Security Settings =====
    enable_safety_checks: bool = field(default_factory=lambda: os.getenv(
        "ENABLE_SAFETY_CHECKS",
        "True"
    ).lower() == "true")
    require_code_review: bool = field(default_factory=lambda: os.getenv(
        "REQUIRE_CODE_REVIEW",
        "False"
    ).lower() == "true")
    max_dangerous_commands: int = field(default_factory=lambda: int(os.getenv(
        "MAX_DANGEROUS_COMMANDS",
        "3"
    )))
    
    def __post_init__(self):
        """Validate and setup configuration after initialization"""
        self._validate()
        self._setup_directories()
        self._setup_logging()
    
    def _validate(self):
        """Validate configuration values"""
        errors = []
        
        # Validate environment
        if self.environment not in ["development", "staging", "production"]:
            errors.append(f"Invalid environment: {self.environment}. Must be: development, staging, or production")
        
        # Validate monitoring interval
        if self.monitoring_interval < 60:
            errors.append(f"Monitoring interval must be >= 60 seconds (got {self.monitoring_interval})")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.log_level}. Must be one of: {', '.join(valid_log_levels)}")
        
        # Validate email config if enabled
        if self.email_enabled:
            if not self.email_smtp_host:
                errors.append("Email enabled but SMTP_HOST not configured")
            if not self.email_from:
                errors.append("Email enabled but EMAIL_FROM not configured")
            if not self.email_to_list:
                errors.append("Email enabled but EMAIL_TO_LIST not configured")
        
        # Validate Slack config if enabled
        if self.slack_enabled and not self.slack_webhook_url:
            errors.append("Slack enabled but SLACK_WEBHOOK_URL not configured")
        
        # Validate webhook config if enabled
        if self.webhook_enabled and not self.webhook_url:
            errors.append("Webhook enabled but WEBHOOK_URL not configured")
        
        # Validate performance settings
        if self.max_concurrent_operations < 1:
            errors.append(f"max_concurrent_operations must be >= 1 (got {self.max_concurrent_operations})")
        
        if self.operation_timeout < 10:
            errors.append(f"operation_timeout must be >= 10 seconds (got {self.operation_timeout})")
        
        if errors:
            error_msg = "Configuration validation failed:\n  - " + "\n  - ".join(errors)
            raise ValueError(error_msg)
        
        logger.info(f"✅ Configuration validated successfully (environment: {self.environment})")
    
    def _setup_directories(self):
        """Create required directories"""
        directories = [
            self.script_output_dir,
            self.config_output_dir,
        ]
        
        if self.backup_configs:
            directories.append(self.config_backup_dir)
        
        for directory in directories:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def _setup_logging(self):
        """Configure logging based on settings"""
        log_level = getattr(logging, self.log_level.upper())
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=self.log_format,
            handlers=[
                logging.StreamHandler()
            ]
        )
        
        # Add file handler if log file specified
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(self.log_format))
            logging.getLogger().addHandler(file_handler)
            
            logger.info(f"Logging to file: {self.log_file}")
    
    def get_alert_channels(self) -> List[str]:
        """Get list of enabled alert channels"""
        channels = []
        
        if self.email_enabled:
            channels.append("email")
        if self.slack_enabled:
            channels.append("slack")
        if self.webhook_enabled:
            channels.append("webhook")
        if self.sms_enabled:
            channels.append("sms")
        
        # Always include dashboard
        channels.append("dashboard")
        
        return channels
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'log_level': self.log_level,
            'monitoring_interval': self.monitoring_interval,
            'alert_channels': self.get_alert_channels(),
            'performance_monitoring_enabled': self.enable_performance_monitoring,
            'safety_checks_enabled': self.enable_safety_checks,
        }
    
    def print_config(self):
        """Print configuration summary"""
        print("\n" + "=" * 80)
        print("PHASE 3 CONFIGURATION")
        print("=" * 80)
        print(f"Environment:           {self.environment}")
        print(f"Debug Mode:            {self.debug}")
        print(f"Log Level:             {self.log_level}")
        print(f"Monitoring Interval:   {self.monitoring_interval}s")
        print(f"Alert Channels:        {', '.join(self.get_alert_channels())}")
        print(f"Script Output:         {self.script_output_dir}")
        print(f"Config Output:         {self.config_output_dir}")
        print(f"Database:              {self.db_path}")
        print(f"Safety Checks:         {'✓' if self.enable_safety_checks else '✗'}")
        print(f"Performance Monitor:   {'✓' if self.enable_performance_monitoring else '✗'}")
        print("=" * 80 + "\n")


# Singleton configuration instance
_config_instance = None

def get_config() -> Phase3Config:
    """Get singleton configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Phase3Config()
    return _config_instance


def reload_config() -> Phase3Config:
    """Reload configuration from environment"""
    global _config_instance
    _config_instance = Phase3Config()
    return _config_instance


# Initialize on module import
config = get_config()


if __name__ == "__main__":
    # Test configuration
    cfg = get_config()
    cfg.print_config()
