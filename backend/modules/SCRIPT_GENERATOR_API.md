# Script Generator Module - API Documentation

## Quick Start

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage

# Initialize the generator
generator = ScriptGenerator()

# Generate a remediation script
result = generator.generate_remediation_script(
    vulnerability_type=VulnerabilityType.SQL_INJECTION,
    language=ScriptLanguage.PYTHON,
    target_system="Ubuntu 22.04 LTS",
    cvss_score=8.5,
    context={"file_path": "/var/www/app/database.py"}
)

# Use the generated scripts
print(result.remediation_script)  # Main fix
print(result.rollback_script)     # Undo changes
print(result.test_script)         # Verify fix
```

---

## API Reference

### ScriptGenerator Class

Main class for generating vulnerability remediation scripts.

#### Constructor

```python
generator = ScriptGenerator()
```

No parameters required. Initializes with default template directory and empty statistics.

#### Methods

##### `generate_remediation_script()`

Generate a complete remediation package for a vulnerability.

**Parameters**:
- `vulnerability_type` (VulnerabilityType): Type of vulnerability to remediate
- `language` (ScriptLanguage): Target script language (PYTHON, BASH, or POWERSHELL)
- `target_system` (str): Target operating system/platform (e.g., "Ubuntu 22.04")
- `cvss_score` (float): CVSS score of the vulnerability (0.0-10.0)
- `context` (Dict, optional): Additional context like file paths, configurations

**Returns**: `GeneratedScript` object containing:
- `remediation_script`: Main fix script
- `rollback_script`: Undo script
- `test_script`: Validation script
- `metadata`: Script metadata (checksums, timestamps, etc.)
- `safety_warnings`: List of detected safety issues
- `execution_notes`: Detailed execution guidance

**Example**:
```python
result = generator.generate_remediation_script(
    vulnerability_type=VulnerabilityType.XSS,
    language=ScriptLanguage.PYTHON,
    target_system="CentOS 8",
    cvss_score=7.5,
    context={"file_path": "/app/views.py"}
)
```

##### `get_statistics()`

Get generation statistics.

**Returns**: Dictionary with:
- `scripts_generated`: Total scripts created
- `safety_violations`: Safety warnings issued
- `rollbacks_created`: Rollback scripts generated
- `languages`: Count by language (python, bash, powershell)
- `vulnerability_types`: Count by vulnerability type

**Example**:
```python
stats = generator.get_statistics()
print(f"Generated {stats['scripts_generated']} scripts")
print(f"Python: {stats['languages']['python']}")
```

---

### Enums

#### ScriptLanguage

Supported script languages.

**Values**:
- `ScriptLanguage.PYTHON` - Python 3.x scripts
- `ScriptLanguage.BASH` - Bash shell scripts
- `ScriptLanguage.POWERSHELL` - PowerShell scripts

#### VulnerabilityType

Common vulnerability types.

**Values**:
- `VulnerabilityType.SQL_INJECTION` - SQL injection vulnerabilities
- `VulnerabilityType.XSS` - Cross-site scripting
- `VulnerabilityType.CSRF` - Cross-site request forgery
- `VulnerabilityType.WEAK_AUTH` - Weak authentication
- `VulnerabilityType.INSECURE_CRYPTO` - Insecure cryptography
- `VulnerabilityType.PERMISSION_ISSUE` - Permission/access control issues
- `VulnerabilityType.DEPENDENCY_VULN` - Dependency vulnerabilities
- `VulnerabilityType.CONFIG_ERROR` - Configuration errors
- `VulnerabilityType.HARDCODED_SECRET` - Hardcoded secrets/credentials
- `VulnerabilityType.PATH_TRAVERSAL` - Path traversal vulnerabilities

---

### Data Classes

#### ScriptMetadata

Metadata for generated scripts.

**Attributes**:
- `language` (ScriptLanguage): Script language
- `vulnerability_type` (VulnerabilityType): Vulnerability type
- `cvss_score` (float): CVSS score
- `target_system` (str): Target system
- `generated_at` (str): ISO timestamp
- `safety_checked` (bool): Whether safety checks passed
- `has_rollback` (bool): Whether rollback script exists
- `checksum` (str): SHA-256 checksum

#### GeneratedScript

Container for complete remediation package.

**Attributes**:
- `remediation_script` (str): Main remediation script
- `rollback_script` (str): Rollback/undo script
- `test_script` (str): Test/validation script
- `metadata` (ScriptMetadata): Script metadata
- `safety_warnings` (List[str]): Safety warnings/issues
- `execution_notes` (str): Detailed execution guidance

---

## Usage Examples

### Example 1: SQL Injection Remediation

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage

generator = ScriptGenerator()

# Generate Python script for SQL injection
result = generator.generate_remediation_script(
    vulnerability_type=VulnerabilityType.SQL_INJECTION,
    language=ScriptLanguage.PYTHON,
    target_system="Ubuntu 22.04",
    cvss_score=8.5,
    context={"file_path": "/app/database.py"}
)

# Save scripts to files
with open('remediation.py', 'w') as f:
    f.write(result.remediation_script)

with open('rollback.py', 'w') as f:
    f.write(result.rollback_script)

with open('test.py', 'w') as f:
    f.write(result.test_script)

# Check for safety warnings
if result.safety_warnings:
    print("⚠️  Safety warnings:")
    for warning in result.safety_warnings:
        print(f"  - {warning}")
else:
    print("✅ No safety issues detected")

# Display execution notes
print("\n" + result.execution_notes)
```

### Example 2: XSS Remediation with Error Handling

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage

generator = ScriptGenerator()

try:
    result = generator.generate_remediation_script(
        vulnerability_type=VulnerabilityType.XSS,
        language=ScriptLanguage.PYTHON,
        target_system="Debian 11",
        cvss_score=6.8,
        context={"file_path": "/app/templates/index.html"}
    )
    
    # Verify script integrity
    print(f"Checksum: {result.metadata.checksum}")
    print(f"Generated: {result.metadata.generated_at}")
    
    # Execute only if safe
    if not result.safety_warnings:
        # Execute remediation
        import subprocess
        subprocess.run(['python', 'remediation.py'])
    else:
        print("Manual review required due to safety warnings")
        
except Exception as e:
    print(f"Error generating script: {e}")
```

### Example 3: Batch Processing Multiple Vulnerabilities

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage

generator = ScriptGenerator()

# List of vulnerabilities to remediate
vulnerabilities = [
    {
        "type": VulnerabilityType.SQL_INJECTION,
        "file": "/app/models.py",
        "cvss": 8.5
    },
    {
        "type": VulnerabilityType.XSS,
        "file": "/app/views.py",
        "cvss": 7.2
    },
    {
        "type": VulnerabilityType.WEAK_AUTH,
        "file": "/app/auth.py",
        "cvss": 9.0
    }
]

results = []
for vuln in vulnerabilities:
    result = generator.generate_remediation_script(
        vulnerability_type=vuln["type"],
        language=ScriptLanguage.PYTHON,
        target_system="Ubuntu 22.04",
        cvss_score=vuln["cvss"],
        context={"file_path": vuln["file"]}
    )
    results.append(result)

# Generate summary report
print(f"\nGenerated {len(results)} remediation scripts")
print(f"Total warnings: {sum(len(r.safety_warnings) for r in results)}")

# Show statistics
stats = generator.get_statistics()
print(f"\nStatistics:")
print(f"  Scripts: {stats['scripts_generated']}")
print(f"  Safety violations: {stats['safety_violations']}")
```

### Example 4: Cross-Language Remediation

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage

generator = ScriptGenerator()

# Generate remediation for the same vulnerability in multiple languages
vulnerability = VulnerabilityType.SQL_INJECTION
languages = [
    ScriptLanguage.PYTHON,
    ScriptLanguage.BASH,
    ScriptLanguage.POWERSHELL
]

for lang in languages:
    result = generator.generate_remediation_script(
        vulnerability_type=vulnerability,
        language=lang,
        target_system="Ubuntu 22.04",
        cvss_score=8.0,
        context={"file_path": "/app/database"}
    )
    
    # Save with language-specific extension
    ext = {'python': 'py', 'bash': 'sh', 'powershell': 'ps1'}[lang.value]
    filename = f"remediation_{lang.value}.{ext}"
    
    with open(filename, 'w') as f:
        f.write(result.remediation_script)
    
    print(f"✅ Generated {filename}")
```

### Example 5: Integration with Jupiter AI Vulnerability Scanner

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage
# Assuming Jupiter AI scanner provides vulnerability data

generator = ScriptGenerator()

# Mock Jupiter AI vulnerability scan result
scan_result = {
    "vulnerability": "SQL Injection",
    "file": "/app/database.py",
    "line": 42,
    "severity": "HIGH",
    "cvss": 8.5,
    "description": "User input not sanitized before SQL query"
}

# Map Jupiter vulnerability to enum
vulnerability_map = {
    "SQL Injection": VulnerabilityType.SQL_INJECTION,
    "XSS": VulnerabilityType.XSS,
    "Weak Authentication": VulnerabilityType.WEAK_AUTH,
    # ... more mappings
}

# Detect language from file extension
def detect_language(filepath):
    if filepath.endswith('.py'):
        return ScriptLanguage.PYTHON
    elif filepath.endswith('.sh'):
        return ScriptLanguage.BASH
    elif filepath.endswith('.ps1'):
        return ScriptLanguage.POWERSHELL
    return ScriptLanguage.PYTHON  # default

# Generate remediation
vuln_type = vulnerability_map.get(scan_result["vulnerability"])
language = detect_language(scan_result["file"])

if vuln_type:
    result = generator.generate_remediation_script(
        vulnerability_type=vuln_type,
        language=language,
        target_system="Ubuntu 22.04",
        cvss_score=scan_result["cvss"],
        context={
            "file_path": scan_result["file"],
            "line_number": scan_result["line"],
            "description": scan_result["description"]
        }
    )
    
    print(f"✅ Generated remediation for {scan_result['vulnerability']}")
    print(f"📁 File: {scan_result['file']}")
    print(f"⚠️  Warnings: {len(result.safety_warnings)}")
    print(f"📋 Checksum: {result.metadata.checksum}")
```

---

## Safety Features

The Script Generator includes multiple safety layers:

### 1. Dangerous Command Detection

Automatically detects potentially dangerous commands:

**Bash**:
- `rm -rf /` (recursive delete)
- `dd if=... of=/dev/sda` (disk wipe)
- `mkfs.*` (filesystem format)
- `:(){ :|:& };:` (fork bomb)
- `curl ... | bash` (execute remote code)

**PowerShell**:
- `Remove-Item ... -Recurse -Force C:\` (recursive delete)
- `Format-Volume` (disk format)
- `Stop-Computer -Force` (forced shutdown)

**Python**:
- `os.system('rm -rf ...')` (dangerous shell commands)
- `eval(...)` (arbitrary code execution)
- `exec(...)` (arbitrary code execution)
- `shutil.rmtree('/')` (recursive delete)

### 2. Hardcoded Password Detection

Scans for patterns like:
```python
password = "secret123"  # ⚠️ Detected
api_key = 'sk-abc123'   # ⚠️ Detected
```

### 3. Python Syntax Validation

For Python scripts, performs AST parsing to catch syntax errors before execution.

### 4. Risk Assessment

Generates risk-based execution notes:
- **HIGH Risk** (CVSS ≥ 7.0): Requires change control, maintenance window
- **MEDIUM Risk** (4.0 ≤ CVSS < 7.0): Test in staging first
- **LOW Risk** (CVSS < 4.0): Can execute with monitoring

---

## Template System

The module uses external `.tpl` template files for easy customization.

### Template Location
```
backend/templates/remediation/
├── sql_injection_python.tpl
├── sql_injection_bash.tpl
├── xss_python.tpl
├── weak_authentication_python.tpl
└── generic.tpl
```

### Template Variables

Templates use Python string formatting with these variables:
- `{target_system}` - Target OS/platform
- `{file_path}` - File being remediated
- `{generated_at}` - ISO timestamp
- `{vulnerability_type}` - Vulnerability type
- `{language}` - Script language

### Adding Custom Templates

1. Create new template file: `<vuln_type>_<language>.tpl`
2. Use template variables as needed
3. Generator will automatically load it

Example - Create `csrf_python.tpl`:
```python
#!/usr/bin/env python3
"""
CSRF Remediation Script
Target: {target_system}
Generated: {generated_at}
"""

def add_csrf_protection():
    # Your remediation logic here
    pass

if __name__ == "__main__":
    add_csrf_protection()
```

---

## Error Handling

```python
from modules import ScriptGenerator, VulnerabilityType, ScriptLanguage

generator = ScriptGenerator()

try:
    result = generator.generate_remediation_script(
        vulnerability_type=VulnerabilityType.SQL_INJECTION,
        language=ScriptLanguage.PYTHON,
        target_system="Ubuntu 22.04",
        cvss_score=8.5,
        context={"file_path": "/app/db.py"}
    )
except FileNotFoundError:
    print("Template file not found")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Best Practices

### 1. Always Review Safety Warnings
```python
if result.safety_warnings:
    print("⚠️  Review required:")
    for warning in result.safety_warnings:
        print(f"  - {warning}")
    # Manual review before execution
```

### 2. Test in Non-Production First
```python
# Read execution notes
print(result.execution_notes)

# Execute in staging
if target_system == "staging":
    execute_script(result.remediation_script)
```

### 3. Always Keep Rollback Ready
```python
# Save both remediation and rollback
with open('remediation.py', 'w') as f:
    f.write(result.remediation_script)

with open('rollback.py', 'w') as f:
    f.write(result.rollback_script)

# Execute with rollback plan
try:
    execute_remediation()
except Exception:
    execute_rollback()
```

### 4. Verify Checksums
```python
import hashlib

def verify_checksum(script, expected_checksum):
    actual = hashlib.sha256(script.encode()).hexdigest()
    return actual == expected_checksum

# Verify before execution
if verify_checksum(result.remediation_script, result.metadata.checksum):
    execute_script()
else:
    print("❌ Checksum mismatch - script may be corrupted")
```

### 5. Monitor Statistics
```python
# Check generation patterns
stats = generator.get_statistics()

if stats['safety_violations'] > 10:
    print("⚠️  High number of safety violations")
    print("Review template configurations")
```

---

## Integration Points

### With SIEM Systems
```python
# After SIEM detects vulnerability
siem_event = get_siem_event()

result = generator.generate_remediation_script(
    vulnerability_type=map_siem_to_vuln_type(siem_event),
    language=detect_target_language(siem_event),
    target_system=siem_event.source_system,
    cvss_score=siem_event.severity_score,
    context={"file_path": siem_event.affected_file}
)

# Send to ticketing system
create_ticket(
    title=f"Remediation for {siem_event.vulnerability}",
    script=result.remediation_script,
    rollback=result.rollback_script
)
```

### With Ticketing Systems
```python
# Attach scripts to tickets
ticket_id = create_jira_ticket("SQL Injection Detected")

add_attachment(ticket_id, "remediation.py", result.remediation_script)
add_attachment(ticket_id, "rollback.py", result.rollback_script)
add_attachment(ticket_id, "test.py", result.test_script)

add_comment(ticket_id, result.execution_notes)
```

### With Communication Platforms
```python
# Send to Slack
send_slack_message(
    channel="#security",
    message=f"🔒 Remediation script generated for SQL Injection\n"
            f"CVSS: {result.metadata.cvss_score}\n"
            f"Warnings: {len(result.safety_warnings)}\n"
            f"Checksum: {result.metadata.checksum[:16]}..."
)
```

---

## Performance Considerations

- **Template Loading**: Templates cached after first load
- **Generation Time**: < 100ms per script
- **Memory Usage**: < 10MB for typical workload
- **Concurrent Generation**: Thread-safe, supports parallel execution

---

## Troubleshooting

### Issue: Template not found
**Solution**: Check template directory path and ensure .tpl file exists
```python
import os
print(generator.template_dir)  # Verify path
```

### Issue: Safety warnings for valid code
**Solution**: Review DANGEROUS_PATTERNS and adjust if needed

### Issue: Unicode errors
**Solution**: Ensure UTF-8 encoding (already handled in module)

---

## Version History

### v1.0.0 (October 2025)
- Initial release
- Multi-language support (Python, Bash, PowerShell)
- 10 vulnerability types
- External template system
- Comprehensive safety validation
- 34 unit tests, 92% coverage

---

## Support

For issues or questions:
- Documentation: See `JUPITER_PHASE3_STEP4_COMPLETE.md`
- Test Suite: `backend/tests/test_script_generator.py`
- Examples: See Usage Examples section above

---

*Last Updated: October 18, 2025*  
*Version: 1.0.0*  
*Module Status: Production Ready ✅*
