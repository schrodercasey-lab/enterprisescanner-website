# Weekly Report Generator
# Automated status report for stakeholders
# Save 1-2 hours per week

param(
    [string]$WeekEnding = (Get-Date).ToString("yyyy-MM-dd")
)

Write-Host "`n=== Weekly Report Generator ===" -ForegroundColor Cyan
Write-Host "Week Ending: $WeekEnding`n" -ForegroundColor White

# Initialize report structure
$report = @{
    weekEnding = $WeekEnding
    achievements = @()
    metrics = @{}
    fortune500 = @{}
    challenges = @()
    nextWeek = @()
}

# Check if Fortune 500 tracker exists
$trackerPath = ".\fortune500_tracker.csv"
$hasTracker = Test-Path $trackerPath

if ($hasTracker) {
    Write-Host "[+] Reading Fortune 500 tracker..." -ForegroundColor Green
    
    try {
        $contacts = Import-Csv $trackerPath
        
        # Calculate Fortune 500 metrics
        $totalContacts = $contacts.Count
        $contacted = ($contacts | Where-Object { $_.Status -ne "Not contacted" }).Count
        $meetings = ($contacts | Where-Object { $_.Status -eq "Meeting scheduled" -or $_.Status -eq "In negotiation" }).Count
        
        # Convert Deal_Size to numeric (remove commas, convert to int)
        $totalPipeline = 0
        foreach ($contact in $contacts) {
            if ($contact.Deal_Size) {
                $dealValue = [int]($contact.Deal_Size -replace '[^\d]', '')
                $totalPipeline += $dealValue
            }
        }
        
        $activePipeline = 0
        foreach ($contact in ($contacts | Where-Object { $_.Status -eq "In negotiation" })) {
            if ($contact.Deal_Size) {
                $dealValue = [int]($contact.Deal_Size -replace '[^\d]', '')
                $activePipeline += $dealValue
            }
        }
        
        $report.fortune500 = @{
            totalContacts = $totalContacts
            contacted = $contacted
            meetings = $meetings
            totalPipeline = $totalPipeline
            activePipeline = $activePipeline
            conversionRate = if ($contacted -gt 0) { [math]::Round(($meetings / $contacted) * 100, 1) } else { 0 }
        }
        
        Write-Host "  Total Contacts: $totalContacts" -ForegroundColor White
        Write-Host "  Contacted: $contacted" -ForegroundColor White
        Write-Host "  Meetings: $meetings" -ForegroundColor White
        Write-Host "  Active Pipeline: `$$($activePipeline.ToString('N0'))" -ForegroundColor Yellow
    }
    catch {
        Write-Host "  [!] Error reading tracker: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "[!] Fortune 500 tracker not found at $trackerPath" -ForegroundColor Yellow
}

# Check for deployment logs
$deployLogs = Get-ChildItem -Path "." -Filter "deploy_*.log" -ErrorAction SilentlyContinue
if ($deployLogs) {
    $deployCount = $deployLogs.Count
    Write-Host "`n[+] Deployments this week: $deployCount" -ForegroundColor Green
    $report.metrics.deployments = $deployCount
}

# Check for backups
$backupPath = "C:\Backups\enterprisescanner"
if (Test-Path $backupPath) {
    $backups = Get-ChildItem -Path $backupPath -Filter "*.tar.gz" -ErrorAction SilentlyContinue
    if ($backups) {
        $backupCount = $backups.Count
        $latestBackup = ($backups | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        Write-Host "[+] Backups available: $backupCount (Latest: $latestBackup)" -ForegroundColor Green
        $report.metrics.backups = $backupCount
    }
}

# Check website files
$websitePath = ".\website"
if (Test-Path $websitePath) {
    $htmlFiles = (Get-ChildItem -Path $websitePath -Filter "*.html" -Recurse).Count
    $cssFiles = (Get-ChildItem -Path $websitePath -Filter "*.css" -Recurse).Count
    $jsFiles = (Get-ChildItem -Path $websitePath -Filter "*.js" -Recurse).Count
    
    Write-Host "`n[+] Website Assets:" -ForegroundColor Green
    Write-Host "  HTML files: $htmlFiles" -ForegroundColor White
    Write-Host "  CSS files: $cssFiles" -ForegroundColor White
    Write-Host "  JS files: $jsFiles" -ForegroundColor White
    
    $report.metrics.websiteFiles = @{
        html = $htmlFiles
        css = $cssFiles
        js = $jsFiles
    }
}

# Generate the report markdown
$reportContent = @"
# Weekly Status Report
**Week Ending:** $WeekEnding

---

## 🎯 Key Achievements

- [ ] **Add your achievements here** - Major milestones completed this week
- [ ] Example: Deployed 3 new features to production
- [ ] Example: Closed 2 Fortune 500 deals worth `$450K
- [ ] Example: Improved website load time by 40%

---

## 📊 Metrics & KPIs

### Fortune 500 Campaign
$(if ($hasTracker) {
"- **Total Targets:** $($report.fortune500.totalContacts) companies
- **Contacted:** $($report.fortune500.contacted) ($([math]::Round(($report.fortune500.contacted / $report.fortune500.totalContacts) * 100, 1))% of targets)
- **Meetings Scheduled:** $($report.fortune500.meetings)
- **Conversion Rate:** $($report.fortune500.conversionRate)% (contacted → meeting)
- **Total Pipeline:** `$$($report.fortune500.totalPipeline.ToString('N0'))
- **Active Negotiations:** `$$($report.fortune500.activePipeline.ToString('N0'))"
} else {
"- Fortune 500 tracker not found - add metrics manually"
})

### Technical Operations
$(if ($report.metrics.deployments) {
"- **Deployments:** $($report.metrics.deployments) this week"
} else {
"- **Deployments:** Add count manually"
})
$(if ($report.metrics.backups) {
"- **Backups:** $($report.metrics.backups) available"
} else {
"- **Backups:** Add count manually"
})
- **Website Uptime:** _Check server logs_
- **Average Response Time:** _Check performance dashboard_

### Development Progress
$(if ($report.metrics.websiteFiles) {
"- **Website Files:** $($report.metrics.websiteFiles.html) HTML, $($report.metrics.websiteFiles.css) CSS, $($report.metrics.websiteFiles.js) JS"
} else {
"- **Website Files:** Add count manually"
})
- **Code Commits:** _Check git log_
- **Issues Resolved:** _Check issue tracker_

---

## 🚀 Completed Tasks

### Phase 2 Week $(([math]::Ceiling((Get-Date).DayOfYear / 7)))
- [ ] Task 1 - Description and outcome
- [ ] Task 2 - Description and outcome
- [ ] Task 3 - Description and outcome

### Infrastructure & Deployment
- [ ] Server maintenance and updates
- [ ] Security patches applied
- [ ] Performance optimizations

### Business Development
- [ ] Fortune 500 outreach emails sent
- [ ] Demo meetings conducted
- [ ] Proposals submitted

---

## 🔧 Technical Improvements

- [ ] **Feature/Fix:** Brief description and impact
- [ ] **Performance:** What was improved and by how much
- [ ] **Security:** Any security enhancements
- [ ] **Code Quality:** Refactoring or optimization

---

## 🎨 Design & Content

- [ ] New pages or sections added
- [ ] UI/UX improvements
- [ ] Content updates (case studies, blog posts)
- [ ] Marketing materials created

---

## 🚧 Challenges & Blockers

### Technical Issues
- [ ] **Issue:** Description
  - **Impact:** How it affects progress
  - **Status:** Resolved / In Progress / Blocked
  - **Next Steps:** Action items

### Business Challenges
- [ ] **Challenge:** Description
  - **Impact:** Effect on revenue or timeline
  - **Strategy:** How we're addressing it

---

## 📅 Next Week Priorities

### Week of $(Get-Date).AddDays(7).ToString("MMM dd, yyyy")

#### High Priority (Must Complete)
1. [ ] **Fortune 500 Outreach:** Contact [X] new companies, follow up with [Y] prospects
2. [ ] **Product Development:** Complete [specific feature]
3. [ ] **Client Meetings:** [Number] demos scheduled

#### Medium Priority (Should Complete)
1. [ ] **Website Updates:** Deploy [feature/content]
2. [ ] **Documentation:** Update API docs / user guides
3. [ ] **Testing:** Security scan / performance testing

#### Low Priority (Nice to Have)
1. [ ] **Optimization:** Improve [specific metric]
2. [ ] **Research:** Investigate [new technology/approach]
3. [ ] **Content:** Blog post or case study draft

---

## 💡 Insights & Learnings

### What Worked Well
- Specific strategy or approach that succeeded
- Tool or process that improved efficiency
- Team collaboration or communication win

### What Could Be Better
- Process improvement opportunity
- Tool or technology to consider
- Skill gap to address

### Action Items for Improvement
1. [ ] Action item based on learnings
2. [ ] Process change to implement
3. [ ] Training or research needed

---

## 📈 Goal Progress

### Monthly Goals ($(Get-Date).ToString("MMMM yyyy")))
- **Revenue Target:** `$X / `$Y (Z%)
- **New Clients:** X / Y signed
- **Product Milestones:** X / Y completed

### Quarterly Goals (Q$(([math]::Ceiling((Get-Date).Month / 3))) $(Get-Date).ToString("yyyy")))
- **Major Objective 1:** Status and % complete
- **Major Objective 2:** Status and % complete
- **Major Objective 3:** Status and % complete

---

## 🎯 Key Meetings & Events Next Week

| Date | Event | Attendees | Purpose |
|------|-------|-----------|---------|
| Mon | Example: Team standup | Team | Weekly planning |
| Wed | Example: Client demo | ACME Corp CISO | Product demo |
| Fri | Example: Week review | Stakeholders | Progress report |

---

## 📞 Follow-Up Required

### High Priority
- [ ] **Contact Name (Company)** - Action needed by [date]
- [ ] **Internal Task** - Owner and deadline

### Medium Priority
- [ ] **Follow-up item** - Details

---

## 💰 Financial Summary

- **Revenue This Week:** `$X (from [source])
- **Pipeline Value:** `$Y active opportunities
- **Expenses:** `$Z (breakdown: hosting, tools, marketing)
- **Burn Rate:** `$X/month
- **Runway:** X months

---

**Report Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Generated By:** PowerShell Weekly Report Tool  
**Next Report Due:** $(Get-Date).AddDays(7).ToString("yyyy-MM-dd")

---

### Quick Links
- [Enterprise Scanner](https://enterprisescanner.com)
- [GitHub Repository](https://github.com/yourrepo)
- [Analytics Dashboard](https://analytics.enterprisescanner.com)
- [Project Board](https://yourprojectboard.com)

"@

# Save report to file
$reportFilename = "weekly_report_$WeekEnding.md"
$reportContent | Out-File -FilePath $reportFilename -Encoding UTF8

Write-Host "`n[+] Report generated: $reportFilename" -ForegroundColor Green
Write-Host "[+] Opening in default editor..." -ForegroundColor Cyan

# Open in default markdown editor (or notepad if no association)
try {
    Start-Process $reportFilename
}
catch {
    notepad $reportFilename
}

Write-Host "`n=== Complete ===" -ForegroundColor Cyan
Write-Host "Edit the report to add specific details, then share with stakeholders.`n" -ForegroundColor White

# Display summary
Write-Host "SUMMARY:" -ForegroundColor Yellow
Write-Host "- Report file: $reportFilename" -ForegroundColor White
if ($hasTracker) {
    Write-Host "- Fortune 500 metrics auto-populated from CSV" -ForegroundColor Green
}
Write-Host "- Fill in [ ] checkboxes with your achievements" -ForegroundColor White
Write-Host "- Update metrics marked with 'Add manually'" -ForegroundColor White
Write-Host "- Add specific details for challenges and next week priorities" -ForegroundColor White
Write-Host ""
