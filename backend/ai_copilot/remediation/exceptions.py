"""
Jupiter v3.0 - Module G.1: Custom Exceptions
Exception hierarchy for autonomous remediation engine

Author: Jupiter Engineering Team
Created: October 17, 2025
Version: 1.0
"""


class RemediationError(Exception):
    """Base exception for all remediation errors"""
    pass


class RemediationDatabaseError(RemediationError):
    """Database operation errors"""
    
    def __init__(self, message: str, query: str = None, original_error: Exception = None):
        super().__init__(message)
        self.query = query
        self.original_error = original_error
    
    def __str__(self):
        parts = [super().__str__()]
        if self.query:
            parts.append(f"Query: {self.query}")
        if self.original_error:
            parts.append(f"Original error: {self.original_error}")
        return " | ".join(parts)


class ValidationError(RemediationError):
    """Input validation errors"""
    
    def __init__(self, message: str, field: str = None, value=None):
        super().__init__(message)
        self.field = field
        self.value = value
    
    def __str__(self):
        parts = [super().__str__()]
        if self.field:
            parts.append(f"Field: {self.field}")
        if self.value is not None:
            parts.append(f"Value: {self.value}")
        return " | ".join(parts)


class ConfigurationError(RemediationError):
    """Configuration errors"""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key
    
    def __str__(self):
        if self.config_key:
            return f"{super().__str__()} | Config key: {self.config_key}"
        return super().__str__()


class ExecutionError(RemediationError):
    """Remediation execution errors"""
    
    def __init__(self, message: str, execution_id: str = None, stage: str = None):
        super().__init__(message)
        self.execution_id = execution_id
        self.stage = stage
    
    def __str__(self):
        parts = [super().__str__()]
        if self.execution_id:
            parts.append(f"Execution ID: {self.execution_id}")
        if self.stage:
            parts.append(f"Stage: {self.stage}")
        return " | ".join(parts)


class RollbackError(RemediationError):
    """Rollback operation errors"""
    
    def __init__(self, message: str, snapshot_id: str = None, reason: str = None):
        super().__init__(message)
        self.snapshot_id = snapshot_id
        self.reason = reason
    
    def __str__(self):
        parts = [super().__str__()]
        if self.snapshot_id:
            parts.append(f"Snapshot ID: {self.snapshot_id}")
        if self.reason:
            parts.append(f"Reason: {self.reason}")
        return " | ".join(parts)


class PatchError(RemediationError):
    """Patch acquisition and verification errors"""
    
    def __init__(self, message: str, patch_id: str = None, source: str = None):
        super().__init__(message)
        self.patch_id = patch_id
        self.source = source
    
    def __str__(self):
        parts = [super().__str__()]
        if self.patch_id:
            parts.append(f"Patch ID: {self.patch_id}")
        if self.source:
            parts.append(f"Source: {self.source}")
        return " | ".join(parts)


class SandboxError(RemediationError):
    """Sandbox testing errors"""
    
    def __init__(self, message: str, sandbox_id: str = None, test_name: str = None):
        super().__init__(message)
        self.sandbox_id = sandbox_id
        self.test_name = test_name
    
    def __str__(self):
        parts = [super().__str__()]
        if self.sandbox_id:
            parts.append(f"Sandbox ID: {self.sandbox_id}")
        if self.test_name:
            parts.append(f"Test: {self.test_name}")
        return " | ".join(parts)


class AutonomyError(RemediationError):
    """Autonomy level and risk assessment errors"""
    
    def __init__(self, message: str, risk_score: float = None, recommended_level: int = None):
        super().__init__(message)
        self.risk_score = risk_score
        self.recommended_level = recommended_level
    
    def __str__(self):
        parts = [super().__str__()]
        if self.risk_score is not None:
            parts.append(f"Risk score: {self.risk_score:.2f}")
        if self.recommended_level is not None:
            parts.append(f"Recommended level: {self.recommended_level}")
        return " | ".join(parts)


class DeploymentError(RemediationError):
    """Deployment strategy and orchestration errors"""
    
    def __init__(self, message: str, deployment_id: str = None, strategy: str = None, stage: int = None):
        super().__init__(message)
        self.deployment_id = deployment_id
        self.strategy = strategy
        self.stage = stage
    
    def __str__(self):
        parts = [super().__str__()]
        if self.deployment_id:
            parts.append(f"Deployment ID: {self.deployment_id}")
        if self.strategy:
            parts.append(f"Strategy: {self.strategy}")
        if self.stage is not None:
            parts.append(f"Stage: {self.stage}")
        return " | ".join(parts)


class MLModelError(RemediationError):
    """Machine learning model errors"""
    
    def __init__(self, message: str, model_path: str = None, confidence: float = None):
        super().__init__(message)
        self.model_path = model_path
        self.confidence = confidence
    
    def __str__(self):
        parts = [super().__str__()]
        if self.model_path:
            parts.append(f"Model: {self.model_path}")
        if self.confidence is not None:
            parts.append(f"Confidence: {self.confidence:.2%}")
        return " | ".join(parts)


class BlockchainError(RemediationError):
    """Blockchain audit trail errors"""
    
    def __init__(self, message: str, transaction_hash: str = None, block_number: int = None):
        super().__init__(message)
        self.transaction_hash = transaction_hash
        self.block_number = block_number
    
    def __str__(self):
        parts = [super().__str__()]
        if self.transaction_hash:
            parts.append(f"TX: {self.transaction_hash}")
        if self.block_number is not None:
            parts.append(f"Block: {self.block_number}")
        return " | ".join(parts)


class TimeoutError(RemediationError):
    """Operation timeout errors"""
    
    def __init__(self, message: str, operation: str = None, timeout_seconds: int = None):
        super().__init__(message)
        self.operation = operation
        self.timeout_seconds = timeout_seconds
    
    def __str__(self):
        parts = [super().__str__()]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.timeout_seconds is not None:
            parts.append(f"Timeout: {self.timeout_seconds}s")
        return " | ".join(parts)


class DependencyError(RemediationError):
    """Patch dependency resolution errors"""
    
    def __init__(self, message: str, patch_id: str = None, missing_dependencies: list = None):
        super().__init__(message)
        self.patch_id = patch_id
        self.missing_dependencies = missing_dependencies or []
    
    def __str__(self):
        parts = [super().__str__()]
        if self.patch_id:
            parts.append(f"Patch: {self.patch_id}")
        if self.missing_dependencies:
            parts.append(f"Missing: {', '.join(self.missing_dependencies)}")
        return " | ".join(parts)


class PermissionError(RemediationError):
    """Permission and authorization errors"""
    
    def __init__(self, message: str, user: str = None, required_permission: str = None):
        super().__init__(message)
        self.user = user
        self.required_permission = required_permission
    
    def __str__(self):
        parts = [super().__str__()]
        if self.user:
            parts.append(f"User: {self.user}")
        if self.required_permission:
            parts.append(f"Required: {self.required_permission}")
        return " | ".join(parts)


class VerificationError(RemediationError):
    """Post-execution verification errors"""
    
    def __init__(self, message: str, verification_type: str = None, expected=None, actual=None):
        super().__init__(message)
        self.verification_type = verification_type
        self.expected = expected
        self.actual = actual
    
    def __str__(self):
        parts = [super().__str__()]
        if self.verification_type:
            parts.append(f"Type: {self.verification_type}")
        if self.expected is not None:
            parts.append(f"Expected: {self.expected}")
        if self.actual is not None:
            parts.append(f"Actual: {self.actual}")
        return " | ".join(parts)


# Exception hierarchy for quick reference
"""
RemediationError (base)
├── RemediationDatabaseError
├── ValidationError
├── ConfigurationError
├── ExecutionError
├── RollbackError
├── PatchError
├── SandboxError
├── AutonomyError
├── DeploymentError
├── MLModelError
├── BlockchainError
├── TimeoutError
├── DependencyError
├── PermissionError
└── VerificationError
"""


# Example usage
if __name__ == "__main__":
    # Database error example
    try:
        raise RemediationDatabaseError(
            "Failed to insert remediation plan",
            query="INSERT INTO remediation_plans ...",
            original_error=Exception("constraint failed")
        )
    except RemediationDatabaseError as e:
        print(f"❌ Database Error: {e}")
    
    # Validation error example
    try:
        raise ValidationError(
            "Invalid severity value",
            field="severity",
            value=99
        )
    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
    
    # Execution error example
    try:
        raise ExecutionError(
            "Patch installation failed",
            execution_id="exec-12345",
            stage="INSTALLING"
        )
    except ExecutionError as e:
        print(f"❌ Execution Error: {e}")
    
    # Rollback error example
    try:
        raise RollbackError(
            "Snapshot restoration failed",
            snapshot_id="snap-67890",
            reason="Disk space insufficient"
        )
    except RollbackError as e:
        print(f"❌ Rollback Error: {e}")
    
    print("\n✅ Exception hierarchy defined and tested")
