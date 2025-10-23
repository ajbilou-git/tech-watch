# 🚀 Quick Start - 5 Minutes

## Step 1: Check Python

Open PowerShell and type:

```powershell
python --version
```

If you see a version (e.g., `Python 3.11.x`), go to Step 2.

Otherwise, install Python: https://www.python.org/downloads/

## Step 2: Configuration Ready ✅

Your configuration is already customized with:
- ✅ Email: abdelhadi.jbilou@gmail.com
- ✅ RSS Feeds: Azure Security, Architecture, Database, App Services, Terraform, HashiCorp, GitHub Actions
- ✅ Smart summaries enabled

You can modify `config.yaml` if needed.

## Step 3: First Test

In PowerShell, from this folder:

```powershell
.\run_tech_watch.ps1 -OpenReport
```

⏱️ First run: ~2 minutes (dependency installation)  
⏱️ Subsequent runs: ~30 seconds

## Step 4: Setup Email (Optional)

To receive daily email reports:

1. Generate a Gmail App Password: https://myaccount.google.com/apppasswords
2. Edit `config.yaml` and fill in:
   - `smtp_username`: Your Gmail address
   - `smtp_password`: The 16-character App Password

See [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed instructions.

## Step 5: Automate (Optional)

Launch PowerShell **as Administrator**:

```powershell
.\setup_task_scheduler.ps1
```

That's it! You'll receive a report every morning at 9 AM. 🎉

---

## 🚀 New Features Included!

Your tech watch now includes:
- 🎯 **Priority Tagging** - Auto-classification (Critical/High/Medium/Low)
- 🔥 **TOP 3 Summary** - Most important articles highlighted
- 📈 **Trending Topics** - Weekly keyword analysis
- 🔗 **Duplicate Detection** - Groups similar articles
- 🤖 **AI Summaries** - Optional OpenAI integration
- 💬 **Teams/Slack** - Optional collaboration tool notifications

All features are enabled by default (except AI and Teams/Slack which require setup).

---

## 📖 Need Help?

- **Advanced Features**: See [README.md](README.md#-advanced-features-configuration)
- **Email Setup**: See [GMAIL_SETUP.md](GMAIL_SETUP.md)
- **Add RSS Feeds**: See [HOW_TO_ADD_FEEDS.md](HOW_TO_ADD_FEEDS.md)
