#!/bin/bash
# SQL Injection Remediation Script
# Target: {target_system}
# File: {file_path}
# Generated: {generated_at}

set -euo pipefail

FILE_PATH="{file_path}"
BACKUP_PATH="${{FILE_PATH}}.backup.$(date +%Y%m%d_%H%M%S)"

echo "Starting SQL injection remediation for $FILE_PATH"

# Create backup
if [ -f "$FILE_PATH" ]; then
    cp "$FILE_PATH" "$BACKUP_PATH"
    echo "✅ Backup created: $BACKUP_PATH"
else
    echo "❌ Error: File not found: $FILE_PATH"
    exit 1
fi

# Check for vulnerable patterns
echo "Scanning for SQL injection vulnerabilities..."

# Check for string concatenation in SQL queries
if grep -E "(SELECT|INSERT|UPDATE|DELETE).*\..*\..*" "$FILE_PATH" > /dev/null 2>&1; then
    echo "⚠️  Found SQL queries with string concatenation"
    echo "   Use prepared statements instead"
fi

# Check for direct variable interpolation
if grep -E "\$_(GET|POST|REQUEST)\[.*\]" "$FILE_PATH" | grep -E "(SELECT|INSERT|UPDATE)" > /dev/null 2>&1; then
    echo "⚠️  Found direct user input in SQL queries"
    echo "   Use parameterized queries"
fi

echo ""
echo "Remediation recommendations:"
echo "1. Replace all string concatenation with prepared statements"
echo "2. Use PDO with parameterized queries (PHP)"
echo "3. Validate and sanitize all user inputs"
echo "4. Use ORMs where possible (e.g., Doctrine, Eloquent)"
echo ""
echo "Example fix:"
echo '  BAD:  $sql = "SELECT * FROM users WHERE id = " . $_GET["id"];'
echo '  GOOD: $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");'
echo '        $stmt->execute([$_GET["id"]]);'
echo ""
echo "Backup saved to: $BACKUP_PATH"
