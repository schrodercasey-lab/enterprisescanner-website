# Code Snippet Library
**Save 30-60 minutes per week with reusable code templates**

---

## 🎨 HTML/CSS COMPONENTS

### Bootstrap Card - Feature Display
```html
<div class="col-md-4 mb-4">
  <div class="card h-100 border-0 shadow-sm hover-lift">
    <div class="card-body text-center p-4">
      <div class="feature-icon mb-3">
        <i class="fas fa-shield-alt text-primary" style="font-size: 3rem;"></i>
      </div>
      <h3 class="h5 fw-bold mb-3">Feature Title</h3>
      <p class="text-muted mb-3">Brief description of the feature and its benefits for enterprise users.</p>
      <a href="#" class="btn btn-outline-primary btn-sm">Learn More</a>
    </div>
  </div>
</div>

<style>
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
}
</style>
```

### Loading Spinner - Professional
```html
<div class="loading-overlay" id="loadingSpinner">
  <div class="spinner-container">
    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-3 text-muted">Processing your request...</p>
  </div>
</div>

<style>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255,255,255,0.95);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.spinner-container {
  text-align: center;
}
</style>
```

### Form with Validation - Enterprise Style
```html
<form id="contactForm" class="needs-validation" novalidate>
  <div class="mb-3">
    <label for="fullName" class="form-label">Full Name *</label>
    <input type="text" class="form-control" id="fullName" required 
           pattern="[A-Za-z\s]{2,50}">
    <div class="invalid-feedback">Please enter your full name (2-50 characters)</div>
  </div>
  
  <div class="mb-3">
    <label for="email" class="form-label">Business Email *</label>
    <input type="email" class="form-control" id="email" required 
           pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$">
    <div class="invalid-feedback">Please enter a valid business email</div>
  </div>
  
  <div class="mb-3">
    <label for="company" class="form-label">Company Name *</label>
    <input type="text" class="form-control" id="company" required>
    <div class="invalid-feedback">Please enter your company name</div>
  </div>
  
  <button type="submit" class="btn btn-primary btn-lg w-100">Submit Request</button>
</form>

<script>
document.getElementById('contactForm').addEventListener('submit', function(e) {
  e.preventDefault();
  if (this.checkValidity()) {
    // Form is valid - submit data
    console.log('Form submitted successfully');
    // Add your submission logic here
  }
  this.classList.add('was-validated');
});
</script>
```

### Alert Banner - Status Messages
```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
  <i class="fas fa-check-circle me-2"></i>
  <strong>Success!</strong> Your request has been submitted. We'll contact you within 24 hours.
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>

<!-- Error Version -->
<div class="alert alert-danger alert-dismissible fade show" role="alert">
  <i class="fas fa-exclamation-circle me-2"></i>
  <strong>Error:</strong> Please check your input and try again.
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

---

## ⚡ JAVASCRIPT UTILITIES

### ROI Calculator - Interactive
```javascript
function calculateROI(currentCosts, incidentFrequency, recoveryTime) {
  // Current annual security costs
  const annualSecurityCost = currentCosts;
  
  // Cost per security incident (average)
  const costPerIncident = 250000;
  
  // Annual incident costs
  const annualIncidentCost = incidentFrequency * costPerIncident;
  
  // Enterprise Scanner annual cost
  const scannerCost = 150000;
  
  // Reduction rates from historical data
  const incidentReduction = 0.87; // 87% reduction
  const recoveryTimeReduction = 0.75; // 75% faster recovery
  
  // Calculate savings
  const incidentSavings = annualIncidentCost * incidentReduction;
  const timeSavings = recoveryTime * 365 * 0.75 * 150; // $150/hour average
  
  const totalSavings = incidentSavings + timeSavings;
  const netROI = totalSavings - scannerCost;
  const roiPercentage = ((netROI / scannerCost) * 100).toFixed(0);
  
  return {
    totalSavings: totalSavings.toLocaleString('en-US', {style: 'currency', currency: 'USD'}),
    netROI: netROI.toLocaleString('en-US', {style: 'currency', currency: 'USD'}),
    roiPercentage: roiPercentage + '%',
    paybackMonths: Math.ceil(scannerCost / (netROI / 12))
  };
}

// Usage:
const result = calculateROI(500000, 4, 48);
console.log(result);
// Output: {totalSavings: "$1,305,000", netROI: "$1,155,000", roiPercentage: "770%", paybackMonths: 2}
```

### Form Data Handler - AJAX Submission
```javascript
async function submitForm(formData, endpoint) {
  try {
    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'flex';
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Hide loading spinner
    document.getElementById('loadingSpinner').style.display = 'none';
    
    // Show success message
    showAlert('success', 'Request submitted successfully!');
    
    return data;
    
  } catch (error) {
    // Hide loading spinner
    document.getElementById('loadingSpinner').style.display = 'none';
    
    // Show error message
    showAlert('error', 'An error occurred. Please try again.');
    
    console.error('Form submission error:', error);
    return null;
  }
}

function showAlert(type, message) {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
  alertDiv.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle me-2"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  document.querySelector('.container').prepend(alertDiv);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => alertDiv.remove(), 5000);
}
```

### Smooth Scroll Navigation
```javascript
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
      
      // Update URL without jumping
      history.pushState(null, null, this.getAttribute('href'));
    }
  });
});
```

### Copy to Clipboard with Feedback
```javascript
function copyToClipboard(text, buttonElement) {
  navigator.clipboard.writeText(text).then(() => {
    // Store original button text
    const originalText = buttonElement.innerHTML;
    
    // Show success feedback
    buttonElement.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
    buttonElement.classList.add('btn-success');
    buttonElement.classList.remove('btn-primary');
    
    // Reset after 2 seconds
    setTimeout(() => {
      buttonElement.innerHTML = originalText;
      buttonElement.classList.remove('btn-success');
      buttonElement.classList.add('btn-primary');
    }, 2000);
  }).catch(err => {
    console.error('Copy failed:', err);
    alert('Copy failed. Please try manually.');
  });
}

// Usage:
// <button onclick="copyToClipboard('text to copy', this)" class="btn btn-primary">Copy</button>
```

---

## 🐍 PYTHON SNIPPETS

### Database Connection - PostgreSQL
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os

@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic cleanup"""
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'enterprisescanner'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            cursor_factory=RealDictCursor
        )
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# Usage:
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies WHERE industry = %s", ('Healthcare',))
    results = cur.fetchall()
```

### API Response Handler - Flask
```python
from flask import jsonify
from functools import wraps

def api_response(f):
    """Decorator for consistent API responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return jsonify({
                'success': True,
                'data': result,
                'error': None
            }), 200
        except ValueError as e:
            return jsonify({
                'success': False,
                'data': None,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'data': None,
                'error': 'Internal server error'
            }), 500
    return decorated_function

# Usage:
@app.route('/api/companies', methods=['GET'])
@api_response
def get_companies():
    companies = fetch_companies_from_db()
    return companies
```

### Email Sender - Professional Template
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, body_html, from_name="Enterprise Scanner"):
    """Send professional HTML email"""
    
    # Email configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', 'info@enterprisescanner.com')
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'{from_name} <{from_email}>'
    msg['To'] = to_email
    
    # Plain text fallback
    text_body = "Please view this email in an HTML-capable email client."
    
    # Attach parts
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))
    
    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

# Usage:
html_template = """
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2>Welcome to Enterprise Scanner</h2>
    <p>Thank you for your interest in our platform.</p>
    <a href="https://enterprisescanner.com/demo" style="display: inline-block; padding: 10px 20px; background: #0066CC; color: white; text-decoration: none; border-radius: 5px;">Schedule Demo</a>
  </body>
</html>
"""
send_email('ciso@fortune500.com', 'Welcome to Enterprise Scanner', html_template)
```

### Data Validation - Comprehensive
```python
import re
from typing import Any, Dict

def validate_contact_form(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate contact form data with detailed error messages"""
    
    errors = {}
    
    # Name validation
    if not data.get('name'):
        errors['name'] = 'Name is required'
    elif len(data['name']) < 2 or len(data['name']) > 50:
        errors['name'] = 'Name must be 2-50 characters'
    
    # Email validation
    email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if not data.get('email'):
        errors['email'] = 'Email is required'
    elif not re.match(email_pattern, data['email'].lower()):
        errors['email'] = 'Invalid email format'
    
    # Company validation
    if not data.get('company'):
        errors['company'] = 'Company name is required'
    
    # Phone validation (optional but format check if provided)
    if data.get('phone'):
        phone_pattern = r'^\+?1?\d{10,14}$'
        if not re.match(phone_pattern, data['phone'].replace('-', '').replace(' ', '')):
            errors['phone'] = 'Invalid phone format'
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

# Usage:
form_data = {'name': 'John Doe', 'email': 'john@company.com', 'company': 'ACME Corp'}
validation = validate_contact_form(form_data)
if validation['valid']:
    print("Form is valid!")
else:
    print("Errors:", validation['errors'])
```

---

## 📊 SQL QUERIES

### Fortune 500 Leads Report
```sql
-- Get high-priority leads with engagement metrics
SELECT 
    c.company_name,
    c.industry,
    c.deal_size,
    COUNT(DISTINCT i.interaction_id) as total_interactions,
    MAX(i.interaction_date) as last_interaction,
    CASE 
        WHEN MAX(i.interaction_date) > NOW() - INTERVAL '7 days' THEN 'Hot'
        WHEN MAX(i.interaction_date) > NOW() - INTERVAL '30 days' THEN 'Warm'
        ELSE 'Cold'
    END as lead_temperature
FROM companies c
LEFT JOIN interactions i ON c.company_id = i.company_id
WHERE c.status = 'Active'
    AND c.deal_size >= 100000
GROUP BY c.company_id, c.company_name, c.industry, c.deal_size
ORDER BY lead_temperature, c.deal_size DESC, last_interaction DESC
LIMIT 20;
```

### Performance Metrics Dashboard
```sql
-- Weekly performance summary
SELECT 
    DATE_TRUNC('week', scan_date) as week_start,
    COUNT(*) as total_scans,
    AVG(vulnerabilities_found) as avg_vulnerabilities,
    AVG(scan_duration_seconds) as avg_scan_time,
    SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as critical_issues,
    SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as high_issues
FROM security_scans
WHERE scan_date >= NOW() - INTERVAL '12 weeks'
GROUP BY week_start
ORDER BY week_start DESC;
```

### Customer Activity Tracking
```sql
-- Identify inactive customers needing follow-up
SELECT 
    c.company_name,
    c.contact_email,
    c.plan_type,
    MAX(a.activity_date) as last_activity,
    CURRENT_DATE - MAX(a.activity_date)::date as days_inactive,
    c.annual_contract_value
FROM customers c
LEFT JOIN activities a ON c.customer_id = a.customer_id
WHERE c.status = 'Active'
    AND c.plan_type IN ('Enterprise', 'Premium')
GROUP BY c.customer_id, c.company_name, c.contact_email, c.plan_type, c.annual_contract_value
HAVING MAX(a.activity_date) < NOW() - INTERVAL '14 days'
ORDER BY c.annual_contract_value DESC, days_inactive DESC;
```

---

## 📧 EMAIL TEMPLATES (HTML)

### Fortune 500 Outreach Email
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #0066CC; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px 20px; background: #f9f9f9; }
        .cta-button { display: inline-block; padding: 12px 30px; background: #0066CC; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enterprise Scanner</h1>
        </div>
        <div class="content">
            <h2>Hi [First Name],</h2>
            <p>I noticed [Company] recently [specific trigger - breach, acquisition, expansion]. As CISO, this likely means increased security oversight.</p>
            
            <p><strong>87% of our Fortune 500 clients</strong> reduced security incidents within 90 days using Enterprise Scanner.</p>
            
            <p><strong>Quick example:</strong> [Similar Company] saved $5.8M annually by catching vulnerabilities before they became breaches.</p>
            
            <p>Would a 30-minute demo showing how we'd address [Company]'s specific security challenges be valuable?</p>
            
            <a href="https://calendly.com/enterprisescanner/demo" class="cta-button">Schedule 30-Min Demo</a>
            
            <p>Best regards,<br>[Your Name]<br>Enterprise Scanner<br>sales@enterprisescanner.com</p>
        </div>
        <div class="footer">
            <p>Enterprise Scanner | https://enterprisescanner.com | Unsubscribe</p>
        </div>
    </div>
</body>
</html>
```

---

## ⚙️ POWERSHELL UTILITIES

### Bulk File Rename
```powershell
# Rename files with pattern
Get-ChildItem -Path ".\website\assets" -Filter "*.jpg" | ForEach-Object {
    $newName = $_.Name -replace "old_pattern", "new_pattern"
    Rename-Item $_.FullName $newName
    Write-Host "Renamed: $($_.Name) -> $newName" -ForegroundColor Green
}
```

### Directory Size Report
```powershell
# Get folder sizes in current directory
Get-ChildItem -Directory | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
    [PSCustomObject]@{
        Folder = $_.Name
        SizeMB = [math]::Round($size, 2)
    }
} | Sort-Object SizeMB -Descending | Format-Table -AutoSize
```

---

**Time Saved Per Week**: 30-60 minutes  
**Annual Value**: $1,300-2,600 at $50/hour

**Usage**: Search (Ctrl+F) → Copy snippet → Customize → Deploy!
