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

### Core Features
- ✅ Configurable RSS feed aggregation
- ✅ Keyword filtering
- ✅ Modern and responsive HTML reports
- ✅ Local execution (no cloud dependency)
- ✅ Automation via Windows Task Scheduler
- ✅ Email delivery via Gmail
- ✅ Automatic report cleanup
- ✅ Simple YAML configuration
- ✅ Smart summaries with AI-powered text extraction

### 🚀 Advanced Features (New!)
- 🎯 **Priority Tagging** - Automatic classification (Critical/High/Medium/Low) based on keywords
- 🔥 **TOP 3 Executive Summary** - Highlights the most important articles at the top
- 📈 **Trending Topics** - Weekly analysis of hot keywords and technologies
- 🔗 **Duplicate Detection** - Groups similar articles to avoid redundancy
- 🤖 **AI Summaries** - Optional OpenAI integration for intelligent summaries (GPT-4o-mini)
- 💬 **Teams/Slack Integration** - Automatic notifications to collaboration platforms
- 🎨 **Enhanced UI** - Color-coded priority badges, better visual hierarchy

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

## 🚀 Advanced Features Configuration

The tech watch solution includes powerful advanced features that enhance user experience and provide better insights.

### 🎯 Priority Tagging

Automatically classifies articles by priority level based on keywords.

**Configuration** (`config.yaml`):
```yaml
features:
  priority_tagging:
    enabled: true  # Set to false to disable
    rules:
      critical: ["cve", "vulnerability", "security patch", "breaking change"]
      high: ["deprecation", "end of life", "major update"]
      medium: ["new feature", "improvement", "release"]
      low: ["documentation", "blog", "announcement"]
```

**Benefits:**
- 🔴 **CRITICAL**: Security issues, breaking changes
- 🟠 **HIGH**: Important updates, deprecations
- 🟢 **MEDIUM**: New features, improvements
- ⚪ **LOW**: General news, documentation

**Visual Example:**
Each article displays a color-coded badge indicating its priority level.

---

### 🔥 Executive Summary (TOP 3)

Displays the 3 most important articles at the top of the report for quick scanning.

**Configuration** (`config.yaml`):
```yaml
features:
  executive_summary:
    enabled: true
    top_count: 3  # Number of top articles to display (1-10)
```

**Benefits:**
- ⚡ See critical updates in 10 seconds
- 📊 Priority-based ranking
- 🎯 Focus on what matters most

---

### 📈 Trending Topics Analysis

Analyzes keywords across all articles to identify hot topics and technologies.

**Configuration** (`config.yaml`):
```yaml
features:
  trends_analysis:
    enabled: true
    min_mentions: 2  # Minimum mentions to be considered a trend
```

**Benefits:**
- 🔥 Identify emerging technologies
- 📊 Track technology adoption
- 🎯 Spot important patterns

**Example Output:**
```
Trending Topics This Week
azure (15)  security (12)  terraform (8)  copilot (7)  kubernetes (5)
```

---

### 🔗 Duplicate Detection

Groups similar articles to avoid reading the same news from multiple sources.

**Configuration** (`config.yaml`):
```yaml
features:
  duplicate_detection:
    enabled: true
    similarity_threshold: 0.7  # 0.0 to 1.0 (higher = more strict)
```

**How it works:**
- Uses TF-IDF and cosine similarity
- Groups articles with >70% similarity
- Displays grouped articles together

**Benefits:**
- ⏱️ Save time by avoiding redundant reading
- 🔗 See all coverage of the same topic
- 📊 Understand topic importance by number of sources

---

### 🤖 AI-Powered Summaries (OpenAI)

Optional integration with OpenAI GPT-4o-mini for intelligent, context-aware summaries.

**Setup:**

1. **Get OpenAI API Key**:
   - Go to: https://platform.openai.com/api-keys
   - Create a new API key
   - Copy the key (starts with `sk-...`)

2. **Configure** (`config.yaml`):
```yaml
features:
  openai:
    enabled: true
    api_key: "sk-proj-your-api-key-here"
    model: "gpt-4o-mini"  # Cheaper and faster
    max_tokens: 100       # Summary length
```

**Cost:**
- ~$0.01 per day for 20-30 articles
- GPT-4o-mini is very affordable ($0.15/1M input tokens)

**Benefits:**
- 🤖 High-quality, context-aware summaries
- 📝 Tailored for DevOps/infrastructure context
- 🎯 Extract key technical points

**Visual:**
AI summaries appear in a green box below regular summaries with a 🤖 icon.

---

### 💬 Microsoft Teams Integration

Send automatic notifications to a Teams channel.

**Setup:**

1. **Create Incoming Webhook** in Teams:
   - Open your Teams channel
   - Click `···` → **Connectors**
   - Search for **"Incoming Webhook"**
   - Click **Configure**
   - Name it "Tech Watch" and click **Create**
   - **Copy the webhook URL**

2. **Configure** (`config.yaml`):
```yaml
features:
  teams:
    enabled: true
    webhook_url: "https://outlook.office.com/webhook/..."
    mention_on_critical: false  # Set to true to @mention channel
```

**Benefits:**
- 📢 Share updates with your team automatically
- 🚨 Get instant alerts for critical articles
- 📊 Centralized notification hub

**Notifications include:**
- Daily summary with article count
- Top trending topics
- Critical alerts (if any)
- Link to full report

---

### 💬 Slack Integration

Send automatic notifications to a Slack channel.

**Setup:**

1. **Create Incoming Webhook** in Slack:
   - Go to: https://api.slack.com/messaging/webhooks
   - Click **Create your Slack app**
   - Choose "From scratch"
   - Name: "Tech Watch", choose workspace
   - Go to **Incoming Webhooks** → Enable
   - Click **Add New Webhook to Workspace**
   - Choose channel and authorize
   - **Copy the webhook URL**

2. **Configure** (`config.yaml`):
```yaml
features:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
```

**Benefits:**
- Same as Teams integration
- Works with Slack's notification system
- Can be routed to multiple channels

---

### 🎛️ Feature Management

**Enable/Disable Features:**

All features can be individually enabled or disabled:

```yaml
features:
  priority_tagging:
    enabled: true   # ✅ Active
  
  executive_summary:
    enabled: true   # ✅ Active
  
  duplicate_detection:
    enabled: false  # ❌ Disabled
  
  trends_analysis:
    enabled: true   # ✅ Active
  
  openai:
    enabled: false  # ❌ Disabled (requires API key)
  
  teams:
    enabled: false  # ❌ Disabled (requires webhook)
  
  slack:
    enabled: false  # ❌ Disabled (requires webhook)
```

**Recommended Setup:**

**Minimal** (free, no external dependencies):
```yaml
priority_tagging: enabled
executive_summary: enabled
trends_analysis: enabled
duplicate_detection: enabled
```

**Standard** (with email):
```yaml
+ Gmail email delivery
```

**Professional** (with collaboration tools):
```yaml
+ Teams or Slack integration
```

**Premium** (with AI):
```yaml
+ OpenAI summaries (~$0.30/month)
```

---

## 📁 Project Structure

```
tech-watch/
├── config.yaml                    # Main configuration file
├── feeds_config.yaml              # External RSS feeds configuration (optional)
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
│
├── tech_watch.py                  # Main Python script
│
├── run_tech_watch.ps1            # Main execution script
├── setup_task_scheduler.ps1      # Windows Task Scheduler automation
│
├── GMAIL_SETUP.md                # Email configuration guide
├── HOW_TO_ADD_FEEDS.md           # Guide to add new RSS feeds
├── README.md                      # Complete documentation
├── QUICKSTART.md                 # 5-minute quick start
│
├── reports/                       # Generated HTML reports
│   └── tech_watch_20251023.html
│
└── venv/                         # Python virtual environment (auto-created)
```

### 📄 Core Files

#### `config.yaml`
Main configuration file containing:
- **Email settings**: Gmail SMTP configuration
- **Output settings**: Report folder, retention period, monitoring days
- **Smart summary**: Enable/disable AI text extraction
- **RSS feeds**: Inline feed definitions (or reference to external file)

**Key parameters:**
- `days_back`: Number of days to monitor (1-14 recommended)
- `retention_days`: How long to keep old reports (30 default)
- `smtp_username/password`: Gmail credentials for email delivery

#### `feeds_config.yaml` *(Optional)*
External RSS feeds configuration for easier maintenance:
- **Technology keywords**: Reusable keyword groups (cloud, security, devops, etc.)
- **Feeds by category**: All RSS feed URLs and keywords
- **Easy to update**: Add new feeds without touching main config

**To activate:** Uncomment `feeds_config_file: "feeds_config.yaml"` in `config.yaml`

#### `requirements.txt`
Python package dependencies:
- `feedparser` - RSS feed parsing
- `pyyaml` - YAML configuration files
- `jinja2` - HTML template rendering
- `beautifulsoup4` - HTML cleaning for smart summaries
- `python-dateutil` - Date parsing
- `requests` - HTTP requests

### 🐍 Python Scripts

#### `tech_watch.py`
Main application script (600+ lines):
- **Feed aggregation**: Fetches RSS feeds from configured sources
- **Smart filtering**: Filters by date range and keywords
- **AI summaries**: Extracts key sentences using text analysis
- **HTML generation**: Creates beautiful, responsive reports
- **Email delivery**: Sends reports via Gmail SMTP
- **Auto-cleanup**: Deletes old reports based on retention policy

**Key functions:**
- `fetch_feeds()` - Downloads and parses RSS feeds
- `_create_smart_summary()` - Generates intelligent summaries
- `generate_report()` - Creates HTML report
- `send_email()` - Delivers report via email
- `cleanup_old_reports()` - Removes outdated files

### 💻 PowerShell Scripts

#### `run_tech_watch.ps1`
Main execution script that:
1. Checks Python installation
2. Creates virtual environment (first run)
3. Installs/updates dependencies
4. Runs `tech_watch.py`
5. Opens report in browser (with `-OpenReport` flag)

**Usage:**
```powershell
.\run_tech_watch.ps1              # Run and save report
.\run_tech_watch.ps1 -OpenReport  # Run and open in browser
```

#### `setup_task_scheduler.ps1`
Automation configuration script:
- Creates Windows scheduled task
- Configures daily execution (default: 9 AM)
- Sets up automatic report generation and email delivery
- Requires administrator privileges

**Usage:**
```powershell
.\setup_task_scheduler.ps1                # Default 9:00 AM
.\setup_task_scheduler.ps1 -TaskTime "08:30"  # Custom time
```

### 📂 Directories

#### `reports/`
Contains all generated HTML reports:
- `tech_watch_YYYYMMDD.html` - Daily reports
- Files older than `retention_days` are automatically deleted
- Excluded from Git (in `.gitignore`)

**Typical size:** ~100 KB per report

#### `venv/`
Python virtual environment:
- Auto-created on first run
- Contains isolated Python packages
- Platform-specific (Windows/Linux/Mac)
- Excluded from Git (in `.gitignore`)

**Typical size:** ~50 MB

### 🔒 Configuration Files

#### `.gitignore`
Defines files to exclude from Git:
```
venv/              # Virtual environment
reports/           # Generated reports
*.pyc              # Python bytecode
__pycache__/       # Python cache
config.yaml        # Contains sensitive data (Gmail password)
```

**Important:** Always add sensitive files here before pushing to Git!

## 🎨 Report Example

The generated HTML report now includes advanced features:

```
🔍 Tech Watch Report
Daily digest of the latest technology updates and releases
Automated monitoring of Azure, Terraform, GitHub Actions, and related technologies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 TOP 3 - Must Read Today

  🔴 CRITICAL  AZURE_SECURITY
  Azure SQL Database - Critical Security Patch CVE-2025-1234
  A critical vulnerability has been discovered in Azure SQL Database...
  
  🟠 HIGH  TERRAFORM
  Terraform 1.8 Release - Breaking Changes
  HashiCorp announces Terraform 1.8 with several breaking changes...
  
  🟢 MEDIUM  GITHUB_ACTIONS
  GitHub Actions - New Workflow Syntax
  GitHub introduces a new workflow syntax for better readability...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Trending Topics This Week

azure(15)  security(12)  terraform(8)  github(7)  copilot(5)  
kubernetes(4)  sql(4)  update(3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Daily Summary

45 Articles Collected  |  8 Categories  |  17 RSS Feeds Monitored

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 AZURE_SECURITY

  🔴 CRITICAL  [MSRC]  📅 10/23/2025 09:15
  Security Update for Azure SQL Database
  A critical security patch has been released...
  🤖 AI Summary: This update addresses a remote code execution 
  vulnerability affecting Azure SQL Database instances...
  
  🟢 MEDIUM  [Azure Security Blog]  📅 10/23/2025 08:30
  New Compliance Features in Azure Security Center
  Microsoft announces enhanced compliance monitoring...

🗄️ AZURE_DATABASE

  🟢 MEDIUM  [Azure SQL Blog]  📅 10/22/2025 14:20
  Performance Improvements in SQL Database
  New query optimization features have been introduced...

🏗️ TERRAFORM

  🟠 HIGH  [HashiCorp Blog]  📅 10/23/2025 11:00
  Terraform 1.8 Released
  This major release includes breaking changes...

...
```

**Visual Features:**
- 🎨 Color-coded priority badges (Red/Orange/Green/Gray)
- 🔥 TOP 3 section with most important articles
- 📈 Trending keywords with occurrence counts
- 🤖 Optional AI summaries in green boxes
- 🏷️ Category-based organization with icons
- 📱 Responsive design for mobile viewing

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
