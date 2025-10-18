# Enterprise Scanner - Quick Start Guide
# Created: October 18, 2025

## 🚀 Backend Server Started!

### Server Information
- **Status**: Running
- **URL**: http://localhost:5000
- **Database**: SQLite (enterprise_scanner.db)
- **Port**: 5000

### 📡 Available API Endpoints

#### Lead Management
```
POST   http://localhost:5000/api/leads
GET    http://localhost:5000/api/leads
GET    http://localhost:5000/api/leads/<id>
PUT    http://localhost:5000/api/leads/<id>
```

#### Live Chat
```
POST   http://localhost:5000/api/chat
WS     ws://localhost:5000/socket.io
```

#### Security Assessments
```
POST   http://localhost:5000/api/security-assessment
GET    http://localhost:5000/api/security-assessment/<id>
```

#### Analytics
```
POST   http://localhost:5000/api/analytics/event
GET    http://localhost:5000/api/analytics/dashboard
```

### 🧪 Test the API

**Create a Lead (PowerShell):**
```powershell
$body = @{
    first_name = "John"
    last_name = "Smith"
    email = "jsmith@microsoft.com"
    company = "Microsoft Corporation"
    job_title = "CISO"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/leads" -Method POST -Body $body -ContentType "application/json"
```

**Or use curl:**
```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith", 
    "email": "jsmith@microsoft.com",
    "company": "Microsoft Corporation",
    "job_title": "CISO"
  }'
```

### 🌐 Connect Your Website

Update your website forms to send data to the backend:

**JavaScript (add to website/js/main.js):**
```javascript
// Contact form submission
document.getElementById('contactForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        company: document.getElementById('company').value,
        job_title: document.getElementById('jobTitle').value,
        message: document.getElementById('message').value
    };
    
    try {
        const response = await fetch('http://localhost:5000/api/leads', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert('Thank you! Your information has been saved.');
            console.log('Lead created:', result);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
```

### 📊 View Saved Leads

**Query the database:**
```powershell
python -c "import sqlite3; conn = sqlite3.connect('backend/enterprise_scanner.db'); cursor = conn.cursor(); cursor.execute('SELECT first_name, last_name, email, company FROM leads'); print('LEADS:'); for row in cursor.fetchall(): print(f'  {row[0]} {row[1]} - {row[2]} ({row[3]})'); conn.close()"
```

### 🔍 Health Check

Visit: http://localhost:5000/health

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "tables": 13,
  "fortune_500_companies": 5
}
```

### 🛑 Stop the Server

Press `Ctrl + C` in the terminal running the backend

### 📝 Logs

Server logs will appear in the terminal showing:
- Incoming requests
- Database operations
- Lead scoring calculations
- Fortune 500 detections
- Error messages (if any)

---

**Next Steps:**
1. ✅ Server running at http://localhost:5000
2. 🧪 Test API endpoints (examples above)
3. 🌐 Connect website forms to backend
4. 📊 View captured leads in database
5. 🚀 Deploy to production when ready

**Database Admin:**
- User: admin@enterprisescanner.com
- Password: Admin123!
- Role: admin

---

*Backend successfully started! Ready to capture Fortune 500 leads! 🎯*
