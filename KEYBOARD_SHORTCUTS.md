# Keyboard Shortcuts Cheatsheet
**Save 2-3 hours per week with efficient keyboard workflows**

---

## 🖥️ VS CODE ESSENTIALS

### File Navigation
| Shortcut | Action | Use Case |
|----------|--------|----------|
| `Ctrl+P` | Quick Open | Jump to any file instantly |
| `Ctrl+Shift+P` | Command Palette | Run any VS Code command |
| `Ctrl+Tab` | Switch Editors | Cycle through open files |
| `Ctrl+\` | Split Editor | Work on multiple files side-by-side |
| `Ctrl+W` | Close Editor | Close current file |
| `Ctrl+K Ctrl+W` | Close All Editors | Clean slate |
| `Ctrl+Shift+E` | Explorer Focus | Navigate file tree |
| `Ctrl+G` | Go to Line | Jump to specific line number |
| `Ctrl+Shift+O` | Go to Symbol | Jump to function/class in file |

### Editing
| Shortcut | Action | Pro Tip |
|----------|--------|---------|
| `Ctrl+D` | Select Next Occurrence | Multi-cursor editing magic |
| `Ctrl+Shift+L` | Select All Occurrences | Change all instances at once |
| `Alt+Click` | Add Cursor | Multiple cursor positions |
| `Ctrl+Shift+K` | Delete Line | Faster than selecting + delete |
| `Alt+Up/Down` | Move Line Up/Down | Reorder code quickly |
| `Ctrl+Shift+[/]` | Fold/Unfold Code | Collapse functions/blocks |
| `Ctrl+/` | Toggle Comment | Comment out code lines |
| `Ctrl+Space` | Trigger IntelliSense | Autocomplete suggestions |
| `F2` | Rename Symbol | Refactor variable/function names |
| `Ctrl+.` | Quick Fix | AI suggestions for fixes |

### Search & Replace
| Shortcut | Action | Usage |
|----------|--------|-------|
| `Ctrl+F` | Find | Search in current file |
| `Ctrl+H` | Replace | Find and replace in file |
| `Ctrl+Shift+F` | Find in Files | Search across entire workspace |
| `Ctrl+Shift+H` | Replace in Files | Global find & replace |
| `F3` / `Shift+F3` | Find Next/Previous | Navigate search results |
| `Alt+Enter` | Select All Matches | Select all search results |

### Terminal
| Shortcut | Action | Benefit |
|----------|--------|---------|
| `` Ctrl+` `` | Toggle Terminal | Quick terminal access |
| `Ctrl+Shift+` `` | New Terminal | Multiple terminal instances |
| `Ctrl+Shift+5` | Split Terminal | Side-by-side terminals |
| `Ctrl+C` | Kill Process | Stop running command |

### Productivity Boosters
| Shortcut | Action | Time Saved |
|----------|--------|-----------|
| `Ctrl+K Z` | Zen Mode | Distraction-free coding |
| `Ctrl+B` | Toggle Sidebar | More screen space |
| `Ctrl+J` | Toggle Panel | Hide/show terminal/output |
| `Ctrl+Shift+V` | Markdown Preview | Preview .md files |
| `Ctrl+K V` | Markdown Side Preview | Edit & preview together |

---

## 💻 POWERSHELL EFFICIENCY

### Command Line Navigation
| Shortcut | Action | Example |
|----------|--------|---------|
| `Tab` | Autocomplete | Type `cd we` + Tab → `cd website` |
| `Ctrl+R` | Search History | Search previous commands |
| `F7` | Command History | Visual history selector |
| `Up/Down` | Navigate History | Cycle through recent commands |
| `Ctrl+C` | Cancel Command | Stop current operation |
| `Ctrl+L` | Clear Screen | Clean terminal (`cls` shortcut) |

### Text Editing
| Shortcut | Action | Usage |
|----------|--------|-------|
| `Ctrl+A` | Select All | Select entire line |
| `Home/End` | Line Start/End | Jump to line boundaries |
| `Ctrl+Left/Right` | Word Jump | Navigate by words |
| `Ctrl+Backspace` | Delete Word | Remove word backward |
| `Alt+F7` | Clear History | Remove command history |

### Pro Tips
```powershell
# Create aliases for common commands (add to $PROFILE)
Set-Alias -Name d -Value simple_deploy.ps1
Set-Alias -Name b -Value simple_backup.ps1
Set-Alias -Name h -Value "ssh root@enterprisescanner.com ./health_check.sh"
Set-Alias -Name crm -Value update_crm.ps1
Set-Alias -Name report -Value weekly_report.ps1

# Usage after aliases:
# d -test        # Quick deploy test
# b              # Quick backup
# h              # Health check
# crm            # CRM update
# report         # Weekly report
```

---

## 🔒 SSH SHORTCUTS

### Connection Aliases (Add to SSH Config)
```bash
# File: C:\Users\YourUsername\.ssh\config

Host prod
    HostName enterprisescanner.com
    User root
    IdentityFile ~/.ssh/id_rsa
    
Host staging
    HostName staging.enterprisescanner.com
    User deploy
    IdentityFile ~/.ssh/id_rsa
```

**Usage:**
```powershell
ssh prod           # Connect to production instantly
ssh staging        # Connect to staging instantly
scp file.txt prod:/var/www/html/  # Quick file copy
```

### SSH Session Management
| Command | Action | Example |
|---------|--------|---------|
| `~.` | Disconnect | Force disconnect frozen SSH |
| `Ctrl+D` | Exit | Clean exit from SSH |
| `Enter ~ Ctrl+Z` | Background SSH | Return later with `fg` |

---

## 🌐 BROWSER PRODUCTIVITY (Chrome/Edge)

### Tab Management
| Shortcut | Action | Daily Use |
|----------|--------|-----------|
| `Ctrl+T` | New Tab | Open new tab |
| `Ctrl+W` | Close Tab | Close current tab |
| `Ctrl+Shift+T` | Reopen Closed Tab | Undo accidental close |
| `Ctrl+Tab` | Next Tab | Cycle through tabs |
| `Ctrl+Shift+Tab` | Previous Tab | Cycle backward |
| `Ctrl+1-8` | Jump to Tab | Direct tab navigation |
| `Ctrl+9` | Last Tab | Jump to rightmost tab |
| `Ctrl+Shift+N` | Incognito | Private browsing |

### Page Navigation
| Shortcut | Action | Usage |
|----------|--------|-------|
| `Ctrl+L` | Address Bar | Focus URL bar |
| `Alt+Left/Right` | Back/Forward | Navigate history |
| `Ctrl+R` | Reload | Refresh page |
| `Ctrl+Shift+R` | Hard Reload | Clear cache + reload |
| `F5` | Refresh | Quick reload |
| `Ctrl+F` | Find | Search on page |
| `Space/Shift+Space` | Scroll Down/Up | Page navigation |

### Developer Tools
| Shortcut | Action | Dev Use |
|----------|--------|---------|
| `F12` | DevTools | Open developer tools |
| `Ctrl+Shift+I` | DevTools (Alt) | Alternative shortcut |
| `Ctrl+Shift+J` | Console | JavaScript console |
| `Ctrl+Shift+C` | Element Inspector | Select element on page |
| `Ctrl+Shift+M` | Device Toolbar | Mobile responsive testing |
| `Ctrl+P` | File Search | Find source file in DevTools |

---

## 📊 WINDOWS SYSTEM SHORTCUTS

### Window Management
| Shortcut | Action | Productivity Boost |
|----------|--------|-------------------|
| `Win+D` | Show Desktop | Minimize all windows |
| `Win+E` | File Explorer | Quick access to files |
| `Win+L` | Lock Screen | Secure workstation |
| `Win+Tab` | Task View | See all open windows |
| `Win+Left/Right` | Snap Window | Split screen layout |
| `Win+Up` | Maximize | Full screen window |
| `Win+Down` | Minimize/Restore | Toggle window size |
| `Alt+Tab` | Switch Apps | Cycle through programs |
| `Win+Shift+S` | Screenshot | Snipping tool |
| `Win+V` | Clipboard History | Access previous copies |

### Virtual Desktops
| Shortcut | Action | Multi-tasking |
|----------|--------|--------------|
| `Win+Ctrl+D` | New Desktop | Create workspace |
| `Win+Ctrl+Left/Right` | Switch Desktop | Navigate workspaces |
| `Win+Ctrl+F4` | Close Desktop | Remove workspace |

---

## 🎨 GIT SHORTCUTS (PowerShell Aliases)

### Quick Aliases (Add to PowerShell $PROFILE)
```powershell
function gs { git status }
function ga { git add . }
function gc { param($msg) git commit -m $msg }
function gp { git push }
function gl { git log --oneline -10 }
function gd { git diff }
function gb { git branch }
function gco { param($branch) git checkout $branch }

# Usage examples:
gs              # Check status
ga              # Stage all changes
gc "Fix bug"    # Commit with message
gp              # Push to remote
gl              # View recent commits
gd              # See changes
gb              # List branches
gco main        # Switch to main branch
```

---

## 🚀 CUSTOM EFFICIENCY ALIASES

### Add to PowerShell $PROFILE for Maximum Speed

```powershell
# File Location: $PROFILE (run 'notepad $PROFILE' to edit)

# Navigation Shortcuts
function .. { cd .. }
function ... { cd ..\.. }
function web { cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace\website }
function ws { cd C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace }

# Deployment Shortcuts
Set-Alias deploy simple_deploy.ps1
Set-Alias backup simple_backup.ps1
function dt { .\simple_deploy.ps1 -test }
function dall { .\simple_deploy.ps1 -all }
function dfile { param($file) .\simple_deploy.ps1 -file $file }

# Server Management
function health { ssh root@enterprisescanner.com "./health_check.sh" }
function logs { ssh root@enterprisescanner.com "tail -n 50 /var/log/nginx/access.log" }
function errors { ssh root@enterprisescanner.com "tail -n 50 /var/log/nginx/error.log" }
function restart { ssh root@enterprisescanner.com "systemctl restart nginx && docker-compose restart" }

# Fortune 500 CRM
Set-Alias crm update_crm.ps1
function contacts { Import-Csv .\fortune500_tracker.csv | Format-Table -AutoSize }
function hot-leads { Import-Csv .\fortune500_tracker.csv | Where-Object {$_.Priority -eq "High"} | Format-Table }

# Reporting
Set-Alias report weekly_report.ps1
Set-Alias perf perf_report.ps1

# Quick Commands
function ll { Get-ChildItem | Format-Table -AutoSize }
function size { Get-ChildItem | Sort-Object Length -Descending | Select-Object -First 10 Name, @{N="SizeMB";E={[math]::Round($_.Length/1MB,2)}} }
function ports { netstat -ano | findstr LISTENING }
function clear { cls }

# Git Shortcuts (if using git in PowerShell)
function gits { git status }
function gita { git add . }
function gitc { param($msg) git commit -m $msg }
function gitp { git push }

# System Info
function sysinfo { systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" }
function diskspace { Get-PSDrive -PSProvider FileSystem }

# Quick Testing
function testsite { Start-Process "https://enterprisescanner.com" }
function testlocal { Start-Process "http://localhost:8000" }
```

### Apply Profile Changes
```powershell
# After editing $PROFILE, reload it:
. $PROFILE

# Or restart PowerShell
```

---

## 💡 TIME-SAVING WORKFLOWS

### 1. Fast Deployment Workflow
```powershell
# Test changes
dt

# If good, deploy single file
dfile index.html

# Or deploy everything
dall

# Check health immediately after
health
```
**Time Saved:** 3-5 minutes per deployment (no typing full commands)

### 2. Quick Status Check Routine
```powershell
# Morning startup routine (one command at a time)
health          # Check server health
hot-leads       # See Fortune 500 hot prospects
gits            # Check git status
```
**Time Saved:** 5-10 minutes daily (automated checks)

### 3. Fortune 500 Follow-up Workflow
```powershell
# Review contacts
crm

# See hot leads
hot-leads

# Update after call (CRM prompts you)
crm
```
**Time Saved:** 2-3 minutes per contact update

### 4. Weekly Reporting Routine
```powershell
# Generate reports
report          # Weekly status report
perf           # Performance benchmark

# Review and email to stakeholders
```
**Time Saved:** 1-2 hours weekly (automated data collection)

---

## 🎯 CHEATSHEET QUICK REFERENCE CARD

### Most Used Commands (Print This!)
```
DEPLOYMENT              MONITORING              CRM
dt       Test deploy    health   Server check   crm      Update CRM
dall     Full deploy    logs     Access logs    contacts View all
dfile    Single file    errors   Error logs     hot-leads High priority

GIT                     NAVIGATION             REPORTS
gits     Status         ws       Workspace      report   Weekly
gita     Add all        web      Website dir    perf     Performance
gitc     Commit         ..       Up one level
gitp     Push           ...      Up two levels

VS CODE                 BROWSER                WINDOWS
Ctrl+P   Quick open     Ctrl+T   New tab        Win+E    Explorer
Ctrl+D   Multi-select   Ctrl+W   Close tab      Win+D    Desktop
Ctrl+/   Comment        F12      DevTools       Win+L    Lock
Ctrl+`   Terminal       Ctrl+L   Address bar    Win+V    Clipboard
```

---

## 📊 EFFICIENCY METRICS

### Time Saved Per Week by Category

| Category | Weekly Savings | Annual Hours | Annual Value ($50/hr) |
|----------|---------------|--------------|----------------------|
| VS Code Shortcuts | 30-45 min | 26-39 hrs | $1,300-1,950 |
| PowerShell Aliases | 45-60 min | 39-52 hrs | $1,950-2,600 |
| SSH Shortcuts | 15-30 min | 13-26 hrs | $650-1,300 |
| Browser Shortcuts | 30-45 min | 26-39 hrs | $1,300-1,950 |
| Custom Workflows | 30-45 min | 26-39 hrs | $1,300-1,950 |
| **TOTAL** | **2.5-3.75 hrs** | **130-195 hrs** | **$6,500-9,750** |

---

## 🏆 MASTERY CHALLENGES

### Week 1: VS Code Mastery
- [ ] Use `Ctrl+P` instead of file tree navigation for 1 week
- [ ] Practice multi-cursor editing with `Ctrl+D` daily
- [ ] Use `Ctrl+Shift+P` command palette 10+ times
- [ ] Goal: 10 minutes saved daily

### Week 2: PowerShell Efficiency
- [ ] Set up all custom aliases in $PROFILE
- [ ] Use aliases exclusively for 1 week (no full commands)
- [ ] Create 3 personal aliases for your workflow
- [ ] Goal: 15 minutes saved daily

### Week 3: Workflow Automation
- [ ] Run morning health check routine daily
- [ ] Use Fortune 500 CRM shortcuts exclusively
- [ ] Deploy with keyboard shortcuts only (no mouse)
- [ ] Goal: 20 minutes saved daily

### Week 4: Expert Level
- [ ] Never use mouse in terminal (keyboard only)
- [ ] Create custom workflows for repetitive tasks
- [ ] Teach shortcuts to team member
- [ ] Goal: 30+ minutes saved daily

---

**Total Time Saved: 2-3 hours per week**  
**Annual Value: $5,200-7,800 at $50/hour**  
**ROI: Infinite (zero cost to implement)**

**Pro Tip:** Print this cheatsheet and keep it visible at your desk. Muscle memory develops in 7-14 days!

