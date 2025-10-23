# 🔍 Tech Watch Solution

**Local** tech watch solution to monitor news and updates from technologies used in your infrastructure.

## 📋 Overview

This solution automatically analyzes RSS feeds from key technologies in your infrastructure and generates a daily HTML report containing:

- 🔒 **Azure Security** - MSRC, Azure Security Blog, Security Updates
- 🏛️ **Azure Architecture** - Architecture Blog, Best Practices, Design Patterns
- ☁️ **Azure Blog** - Azure General Blog, Azure DevOps Blog
- 🗄️ **Azure Database** - Azure SQL, Database Blog, Cosmos DB
- 🚀 **Azure App Services** - App Service Blog, Functions, Container Apps
- 🏗️ **Terraform** - HashiCorp Terraform Blog, AzureRM Provider, Core Releases
- ⚡ **HashiCorp** - HashiCorp Blog, Announcements
- 🐙 **GitHub Actions** - Actions Changelog, GitHub Blog, Runner Releases

## ✨ Features

- ✅ Configurable RSS feed aggregation
- ✅ Keyword filtering
- ✅ Modern and responsive HTML reports
- ✅ Local execution (no cloud dependency)
- ✅ Automation via Windows Task Scheduler
- ✅ Email delivery via Gmail
- ✅ Automatic report cleanup
- ✅ Simple YAML configuration
- ✅ Smart summaries with AI-powered text extraction

## 📦 Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **PowerShell 5.1+** (included in Windows 10/11)
- **Internet Access** to fetch RSS feeds
- **Gmail Account** (optional, for email delivery)

## 🚀 Installation

### 1. Install Python (if needed)

Download and install Python from [python.org](https://www.python.org/downloads/).

**Important**: Check the "Add Python to PATH" box during installation.

### 2. Initial Setup

Open PowerShell in the `tech-watch` folder:

```powershell
cd C:\Users\YourUsername\Desktop\tech-watch
```

### 3. Configuration Ready! ✅

Your configuration is **already customized** with:
- ✅ Email: **abdelhadi.jbilou@gmail.com**
- ✅ 17 RSS feeds configured
- ✅ Monitoring last 14 days

To modify, edit `config.yaml`:

```yaml
email:
  to: "abdelhadi.jbilou@gmail.com"

output:
  folder: "./reports"
  days_back: 14
  retention_days: 30

rss_feeds:
  azure_security:
    - name: "Azure Security Blog"
      url: "https://azure.microsoft.com/en-us/blog/topics/security/feed/"
      keywords: []
  # ... 7 other categories ready to use
```

### 4. First Manual Run

```powershell
.\run_tech_watch.ps1 -OpenReport
```

This command will:
1. Automatically create a Python virtual environment
2. Install required dependencies
3. Fetch RSS feeds
4. Generate an HTML report
5. Send email (if configured)
6. Open the report in your browser

## 📧 Email Configuration

See [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed Gmail configuration instructions.

Quick setup:
1. Generate a Gmail App Password at https://myaccount.google.com/apppasswords
2. Edit `config.yaml`:
```yaml
email:
  to: "your.email@gmail.com"
  smtp_username: "your.email@gmail.com"
  smtp_password: "xxxx xxxx xxxx xxxx"  # 16-char App Password
```

## ⏰ Daily Automation

### Configure Windows Task Scheduler

Launch PowerShell **as Administrator**:

```powershell
# Default configuration (09:00 every morning)
.\setup_task_scheduler.ps1

# Or customize the time
.\setup_task_scheduler.ps1 -TaskTime "08:30"
```

The scheduled task will:
- ✅ Run every day at the chosen time
- ✅ Send email report
- ✅ Save HTML report locally
- ✅ Work even if you're logged out (if computer is on)

### Managing the Scheduled Task

**Check task**:
```powershell
Get-ScheduledTask -TaskName "MastermaintTechWatch"
```

**Run manually**:
```powershell
Start-ScheduledTask -TaskName "MastermaintTechWatch"
```

**Temporarily disable**:
```powershell
Disable-ScheduledTask -TaskName "MastermaintTechWatch"
```

**Re-enable**:
```powershell
Enable-ScheduledTask -TaskName "MastermaintTechWatch"
```

**Remove**:
```powershell
Unregister-ScheduledTask -TaskName "MastermaintTechWatch" -Confirm:$false
```

## 📁 Project Structure

```
tech-watch/
├── config.yaml                    # RSS feeds configuration
├── requirements.txt               # Python dependencies
├── tech_watch.py                  # Main Python script
├── run_tech_watch.ps1            # PowerShell execution script
├── setup_task_scheduler.ps1      # Automation setup
├── GMAIL_SETUP.md                # Email configuration guide
├── README.md                      # This documentation
├── QUICKSTART.md                 # 5-minute quick start guide
├── reports/                       # Generated reports
│   └── tech_watch_20251023.html
└── venv/                         # Virtual environment (auto-created)
```

## 🎨 Report Example

The generated HTML report contains:

```
🔍 Tech Watch Report
Daily digest of the latest technology updates and releases

📊 Daily Summary
├─ 45 Articles Collected
├─ 8 Categories
└─ 17 RSS Feeds Monitored

🔒 AZURE_SECURITY
├─ [MSRC] Security Update for Azure SQL
└─ [Azure Security Blog] New compliance features

🗄️ AZURE_DATABASE
├─ [Azure SQL Blog] Performance improvements in SQL Database
└─ [Azure Updates] Cosmos DB new features

🏗️ TERRAFORM
├─ [HashiCorp Blog] Terraform 1.6 available
└─ [AzureRM Provider] Release 3.86.0

🐙 GITHUB_ACTIONS
├─ [Actions Changelog] New workflow syntax
└─ [Runner Releases] v2.310.0
...
```

## 🔧 Advanced Customization

### Add a New RSS Feed

Edit `config.yaml`:

```yaml
rss_feeds:
  custom_category:
    - name: "My Custom Feed"
      url: "https://example.com/feed.xml"
      keywords: ["keyword1", "keyword2"]
```

### Change Monitoring Period

In `config.yaml`:

```yaml
output:
  days_back: 14  # Monitor last 14 days
```

### Customize Report Style

Modify the `html_template` section in `tech_watch.py` (lines 235-430).

## 🐛 Troubleshooting

### Issue: "Python is not recognized"

**Solution**: Add Python to PATH:
1. Search for "Environment Variables" in Windows
2. Edit the `Path` variable
3. Add Python installation path (e.g., `C:\Python312`)

### Issue: "Error loading RSS feeds"

**Solution**: Check your internet connection and corporate proxies.

### Issue: Scheduled task doesn't run

**Solution**:
1. Verify the computer is on at scheduled time
2. Open Windows Task Scheduler
3. Check the task history for `MastermaintTechWatch`

### Issue: "No recent articles found"

**Solution**: 
- Increase `days_back` in `config.yaml`
- Verify RSS feeds are accessible
- Remove or modify overly restrictive keywords

### Issue: Email not received

**Solution**:
- Check your Spam/Junk folder
- Verify Gmail App Password in `config.yaml`
- See [GMAIL_SETUP.md](GMAIL_SETUP.md) for troubleshooting

## 📊 Logs and History

Reports are kept in `./reports/` for 30 days (configurable).

To browse history:

```powershell
# List all reports
Get-ChildItem ./reports/

# Open a specific report
Start-Process ./reports/tech_watch_20251023.html
```

## 🔐 Security and Privacy

- ✅ Everything runs locally on your machine
- ✅ No data sent to third-party services
- ✅ Reports stay on your local disk
- ✅ No tracking or analytics
- ✅ Gmail App Password recommended over regular password

## 🆘 Support

For questions or issues:

1. Check this documentation
2. Review execution logs in PowerShell
3. Test manually with `.\run_tech_watch.ps1 -OpenReport`
4. Check [GMAIL_SETUP.md](GMAIL_SETUP.md) for email issues

## 📝 Changelog

### Version 1.1 (23/10/2025)
- ✅ Email delivery via Gmail
- ✅ Smart summaries with AI text extraction
- ✅ Full English translation
- ✅ Improved HTML report design
- ✅ 17 RSS feeds pre-configured

### Version 1.0 (23/10/2025)
- ✨ Initial release
- ✅ Support for 8 technology categories
- ✅ Windows Task Scheduler automation
- ✅ Responsive HTML reports

---

**Happy tech watching! 🚀**
