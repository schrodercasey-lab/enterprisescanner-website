"""
Secure Secrets Management for Phase 3
Handles sensitive credentials with multiple backend support
"""

import os
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Manage sensitive credentials securely
    
    Supports multiple backends (in priority order):
    1. AWS Secrets Manager
    2. Azure Key Vault
    3. HashiCorp Vault
    4. Environment Variables
    5. .env file (development only)
    """
    
    def __init__(self, use_cloud_secrets: bool = None):
        """
        Initialize secrets manager
        
        Args:
            use_cloud_secrets: Whether to use cloud secret managers.
                              If None, auto-detect based on ENV variable.
        """
        env = os.getenv("ENV", "development")
        
        if use_cloud_secrets is None:
            # Only use cloud secrets in production
            self.use_cloud_secrets = (env == "production")
        else:
            self.use_cloud_secrets = use_cloud_secrets
        
        self.secrets_cache: Dict[str, str] = {}
        
        # Try to load .env file in development
        if env == "development":
            self._load_env_file()
    
    def _load_env_file(self):
        """Load .env file if it exists (development only)"""
        env_file = Path(__file__).parent.parent / ".env"
        
        if env_file.exists():
            try:
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Only set if not already in environment
                            if key.strip() not in os.environ:
                                os.environ[key.strip()] = value.strip()
                logger.info(f"Loaded environment variables from {env_file}")
            except Exception as e:
                logger.warning(f"Failed to load .env file: {e}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value
        
        Priority:
        1. Cache
        2. Cloud Secrets Manager (if enabled)
        3. Environment Variable
        4. Default value
        
        Args:
            key: Secret key name
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # Check cache first
        if key in self.secrets_cache:
            return self.secrets_cache[key]
        
        # Try cloud secrets if enabled
        if self.use_cloud_secrets:
            value = self._get_from_cloud(key)
            if value:
                self.secrets_cache[key] = value
                return value
        
        # Fall back to environment variable
        value = os.getenv(key, default)
        
        if value:
            self.secrets_cache[key] = value
        
        return value
    
    def _get_from_cloud(self, key: str) -> Optional[str]:
        """
        Get secret from cloud provider
        
        In production, this would integrate with:
        - AWS Secrets Manager
        - Azure Key Vault
        - HashiCorp Vault
        
        Args:
            key: Secret key name
            
        Returns:
            Secret value or None
        """
        # AWS Secrets Manager
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            client = boto3.client('secretsmanager')
            try:
                response = client.get_secret_value(SecretId=key)
                return response['SecretString']
            except ClientError:
                pass  # Try next provider
        except ImportError:
            pass  # AWS SDK not available
        
        # Azure Key Vault
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            vault_url = os.getenv("AZURE_VAULT_URL")
            if vault_url:
                credential = DefaultAzureCredential()
                client = SecretClient(vault_url=vault_url, credential=credential)
                try:
                    secret = client.get_secret(key)
                    return secret.value
                except Exception:
                    pass  # Try next provider
        except ImportError:
            pass  # Azure SDK not available
        
        # HashiCorp Vault
        try:
            import hvac
            
            vault_url = os.getenv("VAULT_ADDR")
            vault_token = os.getenv("VAULT_TOKEN")
            
            if vault_url and vault_token:
                client = hvac.Client(url=vault_url, token=vault_token)
                try:
                    secret = client.secrets.kv.v2.read_secret_version(path=key)
                    return secret['data']['data'].get('value')
                except Exception:
                    pass  # Secret not found
        except ImportError:
            pass  # Vault SDK not available
        
        return None
    
    def set_secret(self, key: str, value: str, persist: bool = False):
        """
        Set secret in cache and optionally persist
        
        Args:
            key: Secret key name
            value: Secret value
            persist: Whether to persist to cloud (not implemented for security)
        """
        self.secrets_cache[key] = value
        
        # In production, this could push to cloud secrets manager
        if persist and self.use_cloud_secrets:
            logger.warning(f"Secret persistence not implemented for: {key}")
    
    def validate_required_secrets(self, required_keys: list) -> bool:
        """
        Validate that all required secrets are available
        
        Args:
            required_keys: List of required secret keys
            
        Returns:
            True if all secrets available
            
        Raises:
            ValueError: If any required secrets are missing
        """
        missing = []
        
        for key in required_keys:
            if not self.get_secret(key):
                missing.append(key)
        
        if missing:
            error_msg = f"Missing required secrets: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"✅ All {len(required_keys)} required secrets validated")
        return True
    
    def validate_alert_secrets(self) -> bool:
        """Validate secrets required for alert channels"""
        required = []
        
        # Check which alert channels are enabled
        if os.getenv("EMAIL_ENABLED", "false").lower() == "true":
            required.extend([
                "EMAIL_FROM",
                "EMAIL_PASSWORD",
                "SMTP_HOST"
            ])
        
        if os.getenv("SLACK_ENABLED", "false").lower() == "true":
            required.append("SLACK_WEBHOOK_URL")
        
        if os.getenv("WEBHOOK_ENABLED", "false").lower() == "true":
            required.extend([
                "WEBHOOK_URL",
                "WEBHOOK_AUTH_TOKEN"
            ])
        
        if required:
            return self.validate_required_secrets(required)
        
        logger.info("No alert channels enabled, no secrets required")
        return True
    
    def mask_secret(self, value: str, visible_chars: int = 4) -> str:
        """
        Mask secret for logging
        
        Args:
            value: Secret value to mask
            visible_chars: Number of characters to show
            
        Returns:
            Masked secret string
        """
        if not value:
            return "<empty>"
        
        if len(value) <= visible_chars:
            return "*" * len(value)
        
        return value[:visible_chars] + "*" * (len(value) - visible_chars)
    
    def get_secrets_summary(self) -> Dict[str, str]:
        """Get summary of configured secrets (masked)"""
        summary = {}
        
        secret_keys = [
            "EMAIL_PASSWORD",
            "WEBHOOK_AUTH_TOKEN",
            "SLACK_WEBHOOK_URL",
            "SMTP_HOST",
            "WEBHOOK_URL"
        ]
        
        for key in secret_keys:
            value = self.get_secret(key)
            if value:
                summary[key] = self.mask_secret(value)
            else:
                summary[key] = "<not configured>"
        
        return summary


# Singleton instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get singleton secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


if __name__ == "__main__":
    # Test secrets manager
    manager = get_secrets_manager()
    
    print("\n" + "=" * 80)
    print("SECRETS MANAGER TEST")
    print("=" * 80)
    
    # Test getting a secret
    test_secret = manager.get_secret("EMAIL_FROM", "not-configured")
    print(f"EMAIL_FROM: {manager.mask_secret(test_secret)}")
    
    # Show summary
    print("\nConfigured Secrets:")
    summary = manager.get_secrets_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("=" * 80 + "\n")
