# Changelog

All notable changes to the Tech Watch solution will be documented in this file.

## [2.0.0] - 2025-10-23

### 🚀 Major Features Added

#### Priority Tagging System
- Automatic classification of articles (Critical/High/Medium/Low)
- Keyword-based priority rules
- Color-coded badges in reports
- Customizable priority keywords

#### Executive Summary (TOP 3)
- Highlights most important articles at the top
- Priority-based ranking
- Quick-scan format for busy professionals
- Configurable number of top articles

#### Trending Topics Analysis
- Weekly keyword analysis
- Identifies hot topics and technologies
- Visual display with occurrence counts
- Helps spot emerging trends

#### Duplicate Detection
- Groups similar articles using ML (TF-IDF + cosine similarity)
- Reduces redundancy
- Shows coverage of same topic from multiple sources
- Configurable similarity threshold

#### AI-Powered Summaries (Optional)
- Integration with OpenAI GPT-4o-mini
- Context-aware intelligent summaries
- Tailored for DevOps/infrastructure audience
- Very affordable (~$0.01/day)

#### Collaboration Tools Integration
- Microsoft Teams webhooks
- Slack webhooks
- Automatic daily notifications
- Critical article alerts
- Trend summaries

### 🎨 UI/UX Improvements
- Enhanced HTML report design
- Priority badges with color coding
- Better visual hierarchy
- Responsive layout
- Improved readability

### 📦 Technical Changes
- Added `scikit-learn` for ML-based duplicate detection
- Added `openai` library for AI summaries
- Enhanced configuration with `features` section
- Improved modularity and extensibility
- Better error handling

### 📚 Documentation
- Comprehensive advanced features guide
- Teams/Slack setup instructions
- OpenAI integration guide
- Updated README with visual examples
- Enhanced QUICKSTART guide
- Created `config.example.yaml`
- Added `.gitignore` for security

### 🔧 Configuration
- New `features` section in `config.yaml`
- All advanced features toggleable
- Backward compatible (all features optional)
- Default configuration optimized

## [1.0.0] - 2025-10-XX

### Initial Release
- RSS feed aggregation
- HTML report generation
- Email delivery via Gmail
- Smart text summaries
- Windows Task Scheduler automation
- Configurable RSS feeds
- Keyword filtering
- Automatic cleanup
