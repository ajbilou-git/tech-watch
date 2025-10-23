# 📡 How to Add New RSS Feeds

This guide explains how to add new RSS feeds and customize keywords for your tech watch.

## 🎯 Two Configuration Methods

### Method 1: External File (Recommended)

Use `feeds_config.yaml` for easier maintenance and sharing.

**Step 1:** Edit `config.yaml` and uncomment this line:
```yaml
feeds_config_file: "feeds_config.yaml"
```

**Step 2:** Edit `feeds_config.yaml` to add your feeds.

**Advantages:**
- ✅ Separate feeds from main config
- ✅ Easier to version control
- ✅ Shareable across teams
- ✅ Cleaner main configuration

### Method 2: Inline Configuration

Keep everything in `config.yaml` (current default).

Edit the `rss_feeds` section directly in `config.yaml`.

## 📝 Adding a New Feed

### Example: Add Microsoft 365 Blog

Edit `feeds_config.yaml`:

```yaml
feeds:
  # ... existing feeds ...
  
  # Microsoft 365
  microsoft_365:
    - name: "Microsoft 365 Blog"
      url: "https://www.microsoft.com/en-us/microsoft-365/blog/feed/"
      keywords: ["teams", "office", "sharepoint", "onedrive"]
      
    - name: "Microsoft 365 Updates"
      url: "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=Microsoft365Blog"
      keywords: []
```

### Example: Add AWS Blog

```yaml
feeds:
  aws_blog:
    - name: "AWS News Blog"
      url: "https://aws.amazon.com/blogs/aws/feed/"
      keywords: ["ec2", "s3", "lambda", "eks"]
```

### Example: Add Kubernetes Blog

```yaml
feeds:
  kubernetes:
    - name: "Kubernetes Blog"
      url: "https://kubernetes.io/feed.xml"
      keywords: []
      
    - name: "CNCF Blog"
      url: "https://www.cncf.io/blog/feed/"
      keywords: ["kubernetes", "k8s"]
```

## 🔍 Finding RSS Feed URLs

### Method 1: Check Blog Footer
Look for RSS icon (🔶) or "RSS" link in the blog footer.

### Method 2: Try Common Patterns
- `https://example.com/feed/`
- `https://example.com/rss/`
- `https://example.com/feed.xml`
- `https://example.com/blog/feed/`

### Method 3: Use Browser Extensions
- **Feedbro** (Chrome/Firefox) - Auto-detects RSS feeds
- **RSS Feed Reader** (Chrome) - Shows available feeds

### Method 4: GitHub Releases
For GitHub projects:
- `https://github.com/owner/repo/releases.atom`
- Example: `https://github.com/kubernetes/kubernetes/releases.atom`

## 🏷️ Keywords Strategy

### No Keywords (Get Everything)
```yaml
keywords: []
```
Use when you want ALL articles from a feed.

### Specific Keywords (Filtered)
```yaml
keywords: ["azure", "cloud", "migration"]
```
Use when a feed covers many topics but you only care about specific ones.

### Example: Azure Updates (Broad Feed)
```yaml
- name: "Azure Updates - All"
  url: "https://azurecomcdn.azureedge.net/en-us/updates/feed/"
  keywords: ["security", "database", "ai"]  # Filter only relevant updates
```

### Example: Focused Blog (Narrow Feed)
```yaml
- name: "Azure SQL Blog"
  url: "https://techcommunity.microsoft.com/.../AzureSQLBlog"
  keywords: []  # Already focused, take everything
```

## 🎨 Using Technology Keywords

Define reusable keyword groups in `feeds_config.yaml`:

```yaml
technology_keywords:
  cloud: ["azure", "aws", "gcp", "cloud"]
  security: ["security", "vulnerability", "cve", "threat"]
  devops: ["ci/cd", "pipeline", "terraform", "ansible"]
  ai_ml: ["ai", "ml", "openai", "machine learning"]
```

Then reference them in your code or combine them:

```yaml
feeds:
  tech_news:
    - name: "Tech News"
      url: "https://example.com/feed/"
      keywords: ["azure", "security", "ai"]  # Combine multiple topics
```

## 📊 Feed Categories

Categories organize your report. Choose clear names:

**Good Examples:**
- `azure_security`
- `kubernetes`
- `python_releases`
- `devops_tools`

**Bad Examples:**
- `misc`
- `other`
- `blog1`

**Icon Mapping:**

The tech watch automatically assigns icons. To add new categories, edit `tech_watch.py`:

```python
category_icons = {
    'azure_security': '🔒',
    'azure_database': '🗄️',
    'kubernetes': '☸️',      # Add your new category
    'python': '🐍',          # Add your new category
}
```

## 🧪 Testing New Feeds

### Step 1: Test Feed URL
Visit the RSS URL in your browser. You should see XML content.

### Step 2: Validate Feed
Use online validators:
- https://validator.w3.org/feed/
- https://www.feedvalidator.org/

### Step 3: Test with Tech Watch

Add the feed to `feeds_config.yaml` and run:

```powershell
.\run_tech_watch.ps1 -OpenReport
```

Check the console output for:
```
Processing category: YOUR_NEW_CATEGORY
  Feed Name...
  X article(s) found
```

### Step 4: Check Report
Open the generated HTML report and verify:
- ✅ Category appears
- ✅ Articles are relevant
- ✅ Summaries are good
- ✅ Links work

## ⚙️ Advanced Configuration

### Multiple Keywords (OR logic)
```yaml
keywords: ["terraform", "infrastructure as code"]
```
Matches articles containing "terraform" OR "infrastructure as code".

### Adjust Days Back for Specific Feeds

Some blogs update rarely. You can't set per-feed `days_back`, but you can:
1. Increase global `days_back` in `config.yaml`
2. Or use keywords to filter more precisely

### Rate Limiting

The script fetches feeds sequentially. No rate limiting needed for RSS feeds.

## 📚 Popular RSS Feeds

### Cloud Platforms
```yaml
aws_blog:
  - name: "AWS News"
    url: "https://aws.amazon.com/blogs/aws/feed/"
    keywords: []

gcp_blog:
  - name: "Google Cloud Blog"
    url: "https://cloud.google.com/blog/feed/"
    keywords: []
```

### Programming Languages
```yaml
python:
  - name: "Python Insider"
    url: "https://blog.python.org/feeds/posts/default"
    keywords: []
    
  - name: "Real Python"
    url: "https://realpython.com/atom.xml"
    keywords: []

javascript:
  - name: "Node.js Blog"
    url: "https://nodejs.org/en/feed/blog.xml"
    keywords: []
```

### DevOps Tools
```yaml
docker:
  - name: "Docker Blog"
    url: "https://www.docker.com/blog/feed/"
    keywords: []

kubernetes:
  - name: "Kubernetes Blog"
    url: "https://kubernetes.io/feed.xml"
    keywords: []
```

### Security
```yaml
security:
  - name: "Krebs on Security"
    url: "https://krebsonsecurity.com/feed/"
    keywords: ["cloud", "microsoft", "google"]
    
  - name: "The Hacker News"
    url: "https://feeds.feedburner.com/TheHackersNews"
    keywords: ["cloud", "azure", "aws"]
```

## 🔧 Troubleshooting

### Feed Not Working?
1. Test URL in browser
2. Check for HTTPS vs HTTP
3. Some feeds require User-Agent headers (not supported currently)
4. Check if feed is behind authentication

### No Articles Found?
1. Increase `days_back` in `config.yaml`
2. Remove keywords to see all articles
3. Check if feed publishes regularly

### Wrong Category Icon?
Edit `tech_watch.py` and add your category to `category_icons` dict.

---

**Ready to expand your tech watch?** Edit `feeds_config.yaml` and run the script! 🚀
