#!/usr/bin/env python3
"""
Local tech watch solution for mastermaint-infra
Aggregates RSS feeds from technologies used in the infrastructure
"""

import feedparser
import yaml
import os
import sys
import re
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from pathlib import Path
from jinja2 import Template
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import traceback
import requests


class TechWatch:
    def __init__(self, config_path="config.yaml"):
        """Initialize the tech watch system"""
        self.config = self._load_config(config_path)
        self.articles = []
        self.errors = []
        self.trends = []
        self.duplicate_groups = []
        self.top_articles = []
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Check if external feeds config file is specified
            if 'feeds_config_file' in config and config['feeds_config_file']:
                feeds_config_path = os.path.join(
                    os.path.dirname(config_path), 
                    config['feeds_config_file']
                )
                if os.path.exists(feeds_config_path):
                    with open(feeds_config_path, 'r', encoding='utf-8') as f:
                        feeds_config = yaml.safe_load(f)
                        config['rss_feeds'] = feeds_config.get('feeds', {})
                        config['technology_keywords'] = feeds_config.get('technology_keywords', {})
                    print(f"Loaded feeds from: {feeds_config_path}")
            
            return config
        except Exception as e:
            print(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def _is_recent(self, published_date, days_back):
        """Check if an article is recent"""
        if not published_date:
            return True  # If no date, include by default
        
        try:
            if isinstance(published_date, str):
                pub_date = date_parser.parse(published_date)
            else:
                pub_date = datetime(*published_date[:6])
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            return pub_date >= cutoff_date
        except:
            return True
    
    def _matches_keywords(self, entry, keywords):
        """Check if article contains any of the keywords"""
        if not keywords:
            return True
        
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        return any(keyword.lower() in text for keyword in keywords)
    
    def _clean_html(self, html_text):
        """Clean HTML and extract plain text"""
        if not html_text:
            return ""
        
        # Use BeautifulSoup to clean HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _create_smart_summary(self, text, max_length=300):
        """Create an intelligent summary by extracting the most relevant sentences"""
        if not text:
            return ""
        
        # Clean HTML text
        clean_text = self._clean_html(text)
        
        if len(clean_text) <= max_length:
            return clean_text
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return clean_text[:max_length] + "..."
        
        # Calculate a simple score for each sentence based on:
        # - Position (first sentences are important)
        # - Length (neither too short nor too long)
        # - Presence of technical keywords
        technical_keywords = ['azure', 'terraform', 'github', 'security', 'update', 
                            'release', 'new', 'feature', 'improvement', 'fix', 
                            'version', 'support', 'api', 'cloud', 'database']
        
        scored_sentences = []
        for idx, sentence in enumerate(sentences[:10]):  # Limit to first 10
            score = 0
            
            # Score based on position (first sentences are important)
            score += (10 - idx) * 2
            
            # Score based on optimal length (50-150 characters)
            length = len(sentence)
            if 50 <= length <= 150:
                score += 5
            elif length < 50:
                score -= 2
            
            # Score based on technical keywords
            sentence_lower = sentence.lower()
            keyword_count = sum(1 for kw in technical_keywords if kw in sentence_lower)
            score += keyword_count * 3
            
            scored_sentences.append((score, sentence))
        
        # Sort by score and take best sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        # Build summary
        summary = ""
        for score, sentence in scored_sentences:
            if len(summary) + len(sentence) + 2 <= max_length:
                summary += sentence + ". "
            else:
                break
        
        if not summary:
            summary = sentences[0][:max_length] + "..."
        
        return summary.strip()
    
    def _calculate_priority(self, article):
        """Calculate priority score for an article"""
        features = self.config.get('features', {})
        priority_config = features.get('priority_tagging', {})
        
        if not priority_config.get('enabled', False):
            return 'medium', 50
        
        rules = priority_config.get('rules', {})
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Check critical keywords
        for keyword in rules.get('critical', []):
            if keyword.lower() in text:
                return 'critical', 100
        
        # Check high priority keywords
        for keyword in rules.get('high', []):
            if keyword.lower() in text:
                return 'high', 75
        
        # Check medium priority keywords
        for keyword in rules.get('medium', []):
            if keyword.lower() in text:
                return 'medium', 50
        
        # Default to low
        return 'low', 25
    
    def _detect_duplicates(self):
        """Detect and group similar articles"""
        features = self.config.get('features', {})
        dup_config = features.get('duplicate_detection', {})
        
        if not dup_config.get('enabled', False) or len(self.articles) < 2:
            return []
        
        threshold = dup_config.get('similarity_threshold', 0.7)
        
        # Create text corpus
        texts = [f"{a['title']} {a['summary']}" for a in self.articles]
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Group similar articles
        grouped = set()
        groups = []
        
        for i in range(len(self.articles)):
            if i in grouped:
                continue
            
            group = [i]
            for j in range(i + 1, len(self.articles)):
                if j not in grouped and similarity_matrix[i][j] >= threshold:
                    group.append(j)
                    grouped.add(j)
            
            if len(group) > 1:
                groups.append({
                    'articles': [self.articles[idx] for idx in group],
                    'count': len(group)
                })
                grouped.add(i)
        
        return groups
    
    def _analyze_trends(self):
        """Analyze trends from collected articles"""
        features = self.config.get('features', {})
        trends_config = features.get('trends_analysis', {})
        
        if not trends_config.get('enabled', False):
            return []
        
        min_mentions = trends_config.get('min_mentions', 2)
        
        # Extract keywords from all articles
        all_text = ' '.join([f"{a['title']} {a['summary']}" for a in self.articles])
        
        # Common tech keywords to look for
        tech_keywords = [
            'azure', 'terraform', 'github', 'kubernetes', 'docker', 'python',
            'copilot', 'ai', 'security', 'vulnerability', 'release', 'update',
            'deprecation', 'feature', 'api', 'cloud', 'database', 'sql',
            'devops', 'ci/cd', 'container', 'serverless', 'function'
        ]
        
        # Count keyword occurrences
        keyword_counts = Counter()
        all_text_lower = all_text.lower()
        
        for keyword in tech_keywords:
            count = all_text_lower.count(keyword)
            if count >= min_mentions:
                keyword_counts[keyword] = count
        
        # Get top trends
        top_trends = keyword_counts.most_common(10)
        
        return [{'keyword': k, 'count': c} for k, c in top_trends]
    
    def _get_openai_summary(self, article):
        """Get AI-powered summary using OpenAI"""
        features = self.config.get('features', {})
        openai_config = features.get('openai', {})
        
        if not openai_config.get('enabled', False):
            return None
        
        api_key = openai_config.get('api_key', '')
        if not api_key:
            return None
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            text = f"Title: {article['title']}\n\n{article['summary']}"
            
            response = client.chat.completions.create(
                model=openai_config.get('model', 'gpt-4o-mini'),
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this tech article in 2-3 clear sentences for a DevOps engineer."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=openai_config.get('max_tokens', 100),
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"  OpenAI error: {e}")
            return None
    
    def _send_to_teams(self, content, is_critical=False):
        """Send notification to Microsoft Teams"""
        features = self.config.get('features', {})
        teams_config = features.get('teams', {})
        
        if not teams_config.get('enabled', False):
            return False
        
        webhook_url = teams_config.get('webhook_url', '')
        if not webhook_url:
            return False
        
        try:
            message = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "Tech Watch Report",
                "themeColor": "FF0000" if is_critical else "0078D7",
                "title": "🔍 Tech Watch Update",
                "text": content
            }
            
            response = requests.post(webhook_url, json=message)
            return response.status_code == 200
        except Exception as e:
            print(f"  Teams error: {e}")
            return False
    
    def _send_to_slack(self, content, is_critical=False):
        """Send notification to Slack"""
        features = self.config.get('features', {})
        slack_config = features.get('slack', {})
        
        if not slack_config.get('enabled', False):
            return False
        
        webhook_url = slack_config.get('webhook_url', '')
        if not webhook_url:
            return False
        
        try:
            message = {
                "text": f"🔍 *Tech Watch Update*\n\n{content}",
                "color": "#ff0000" if is_critical else "#0078d7"
            }
            
            response = requests.post(webhook_url, json=message)
            return response.status_code == 200
        except Exception as e:
            print(f"  Slack error: {e}")
            return False
    
    def fetch_feeds(self):
        """Fetch all configured RSS feeds"""
        days_back = self.config['output']['days_back']
        
        for category, feeds in self.config['rss_feeds'].items():
            print(f"\nProcessing category: {category.upper()}")
            
            for feed_config in feeds:
                feed_name = feed_config['name']
                feed_url = feed_config['url']
                keywords = feed_config.get('keywords', [])
                
                try:
                    print(f"  {feed_name}...")
                    feed = feedparser.parse(feed_url)
                    
                    if feed.bozo:
                        print(f"  Warning for {feed_name}: {feed.bozo_exception}")
                    
                    count = 0
                    for entry in feed.entries[:20]:  # Limit to 20 articles per feed
                        published = entry.get('published_parsed') or entry.get('updated_parsed')
                        
                        if self._is_recent(published, days_back) and self._matches_keywords(entry, keywords):
                            # Create smart summary if enabled
                            raw_summary = entry.get('summary', entry.get('description', ''))
                            
                            # Check if smart summaries are enabled
                            use_smart_summary = self.config['output'].get('smart_summary', True)
                            max_length = self.config['output'].get('summary_max_length', 300)
                            
                            if use_smart_summary:
                                smart_summary = self._create_smart_summary(raw_summary, max_length=max_length)
                                final_summary = smart_summary if smart_summary else raw_summary[:max_length]
                            else:
                                final_summary = raw_summary[:max_length]
                            
                            article = {
                                'category': category,
                                'feed_name': feed_name,
                                'title': entry.get('title', 'Untitled'),
                                'link': entry.get('link', '#'),
                                'summary': final_summary,
                                'published': published,
                                'published_str': self._format_date(published)
                            }
                            
                            # Calculate priority
                            priority_level, priority_score = self._calculate_priority(article)
                            article['priority'] = priority_level
                            article['priority_score'] = priority_score
                            
                            # Try OpenAI summary if enabled
                            openai_summary = self._get_openai_summary(article)
                            if openai_summary:
                                article['ai_summary'] = openai_summary
                            
                            self.articles.append(article)
                            count += 1
                    
                    print(f"  {count} article(s) found")
                    
                except Exception as e:
                    error_msg = f"Error with {feed_name}: {str(e)}"
                    print(f"  {error_msg}")
                    self.errors.append(error_msg)
        
        print(f"\nTotal: {len(self.articles)} articles collected")
        return self.articles
    
    def _format_date(self, date_tuple):
        """Format a date for display"""
        if not date_tuple:
            return "Unknown date"
        try:
            if isinstance(date_tuple, str):
                dt = date_parser.parse(date_tuple)
            else:
                dt = datetime(*date_tuple[:6])
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return "Unknown date"
    
    def generate_report(self):
        """Generate an HTML report"""
        # Analyze trends
        print("\nAnalyzing trends...")
        self.trends = self._analyze_trends()
        
        # Detect duplicates
        print("Detecting duplicate articles...")
        self.duplicate_groups = self._detect_duplicates()
        
        # Sort articles by priority and date
        sorted_articles = sorted(
            self.articles,
            key=lambda x: (x.get('priority_score', 50), x['published'] if x['published'] else (0,)),
            reverse=True
        )
        
        # Get TOP articles for executive summary
        features = self.config.get('features', {})
        exec_config = features.get('executive_summary', {})
        if exec_config.get('enabled', True):
            top_count = exec_config.get('top_count', 3)
            self.top_articles = sorted_articles[:top_count]
        
        # Group by category
        by_category = {}
        for article in sorted_articles:
            cat = article['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        # HTML Template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech Watch - {{ date }}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { margin: 0 0 10px 0; font-size: 2.5em; }
        .header p { margin: 0; opacity: 0.9; font-size: 1.1em; }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary h2 { margin-top: 0; color: #667eea; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .stat-value { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 0.9em; }
        .category {
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .category-header {
            background: #667eea;
            color: white;
            padding: 20px;
            font-size: 1.5em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .category-content { padding: 20px; }
        .article {
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 5px;
            transition: transform 0.2s;
        }
        .article:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .article-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .article-title a {
            color: #333;
            text-decoration: none;
        }
        .article-title a:hover {
            color: #667eea;
        }
        .article-meta {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .article-summary {
            color: #555;
            line-height: 1.6;
        }
        .feed-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-right: 10px;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }
        .errors {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .errors h3 {
            margin-top: 0;
            color: #856404;
        }
        .error-item {
            color: #856404;
            margin: 5px 0;
        }
        .priority-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
            margin-right: 10px;
            text-transform: uppercase;
        }
        .priority-critical {
            background: #dc3545;
            color: white;
        }
        .priority-high {
            background: #fd7e14;
            color: white;
        }
        .priority-medium {
            background: #28a745;
            color: white;
        }
        .priority-low {
            background: #6c757d;
            color: white;
        }
        .top-articles {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .top-articles h2 {
            margin-top: 0;
            font-size: 2em;
        }
        .top-article-item {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ffd700;
        }
        .top-article-item:last-child {
            margin-bottom: 0;
        }
        .top-article-item a {
            color: white;
            text-decoration: none;
            font-size: 1.1em;
            font-weight: bold;
        }
        .top-article-item a:hover {
            text-decoration: underline;
        }
        .trends-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .trends-section h2 {
            margin-top: 0;
            color: #667eea;
        }
        .trend-item {
            display: inline-block;
            background: #e7f3ff;
            color: #0066cc;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            font-weight: 500;
        }
        .trend-count {
            background: #0066cc;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: 5px;
            font-size: 0.9em;
        }
        .duplicates-section {
            background: #fff9e6;
            border: 1px solid #ffcc00;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .duplicates-section h4 {
            margin-top: 0;
            color: #856404;
        }
        .ai-summary {
            background: #e8f5e9;
            border-left: 3px solid #4caf50;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
            font-style: italic;
        }
        .ai-summary::before {
            content: "🤖 AI Summary: ";
            font-weight: bold;
            color: #4caf50;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Tech Watch Report</h1>
        <p style="font-size: 1.1em; margin: 10px 0;">Daily digest of the latest technology updates and releases</p>
        <p style="opacity: 0.8;">Automated monitoring of Azure, Terraform, GitHub Actions, and related technologies • {{ date }}</p>
    </div>

    {% if errors %}
    <div class="errors">
        <h3>⚠️ Warnings</h3>
        {% for error in errors %}
        <div class="error-item">• {{ error }}</div>
        {% endfor %}
    </div>
    {% endif %}

    {% if top_articles %}
    <div class="top-articles">
        <h2>🔥 TOP {{ top_articles|length }} - Must Read Today</h2>
        {% for article in top_articles %}
        <div class="top-article-item">
            <div style="margin-bottom: 5px;">
                <span class="priority-badge priority-{{ article.priority }}">{{ article.priority }}</span>
                <span style="opacity: 0.8; font-size: 0.9em;">{{ article.category|upper }}</span>
            </div>
            <a href="{{ article.link }}" target="_blank">{{ article.title }}</a>
            <div style="margin-top: 8px; font-size: 0.95em; opacity: 0.9;">{{ article.summary[:150] }}...</div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if trends %}
    <div class="trends-section">
        <h2>📈 Trending Topics This Week</h2>
        <div>
            {% for trend in trends %}
            <span class="trend-item">{{ trend.keyword }}<span class="trend-count">{{ trend.count }}</span></span>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="summary">
        <h2>📊 Daily Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{{ total_articles }}</div>
                <div class="stat-label">Articles Collected</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ total_categories }}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ total_feeds }}</div>
                <div class="stat-label">RSS Feeds Monitored</div>
            </div>
        </div>
    </div>

    {% for category, articles in by_category.items() %}
    <div class="category">
        <div class="category-header">
            {{ category_icons.get(category, '📰') }} {{ category }}
        </div>
        <div class="category-content">
            {% for article in articles %}
            <div class="article">
                <div class="article-title">
                    <a href="{{ article.link }}" target="_blank">{{ article.title }}</a>
                </div>
                <div class="article-meta">
                    <span class="priority-badge priority-{{ article.priority }}">{{ article.priority }}</span>
                    <span class="feed-badge">{{ article.feed_name }}</span>
                    📅 {{ article.published_str }}
                </div>
                <div class="article-summary">
                    {{ article.summary }}
                </div>
                {% if article.ai_summary %}
                <div class="ai-summary">
                    {{ article.ai_summary }}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}

    <div class="footer">
        <p>Automatically generated tech watch report</p>
        <p>{{ generation_time }}</p>
    </div>
</body>
</html>
        """
        
        # Icons per category
        category_icons = {
            'azure_security': '🔒',
            'azure_architecture': '🏛️',
            'azure_blog': '☁️',
            'azure_database': '🗄️',
            'azure_app_services': '🚀',
            'terraform': '🏗️',
            'hashicorp': '⚡',
            'github_actions': '🐙'
        }
        
        # Count unique feeds
        unique_feeds = set()
        for article in self.articles:
            unique_feeds.add(article['feed_name'])
        
        # Generate HTML
        template = Template(html_template)
        html = template.render(
            date=datetime.now().strftime("%m/%d/%Y"),
            by_category=by_category,
            total_articles=len(self.articles),
            total_categories=len(by_category),
            total_feeds=len(unique_feeds),
            generation_time=datetime.now().strftime("%m/%d/%Y at %H:%M:%S"),
            category_icons=category_icons,
            errors=self.errors,
            top_articles=self.top_articles,
            trends=self.trends,
            duplicate_groups=self.duplicate_groups
        )
        
        return html
    
    def save_report(self, html):
        """Save the HTML report"""
        output_folder = Path(self.config['output']['folder'])
        output_folder.mkdir(parents=True, exist_ok=True)
        
        filename = f"tech_watch_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = output_folder / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\nReport saved: {filepath.absolute()}")
        return filepath
    
    def cleanup_old_reports(self):
        """Delete old reports"""
        output_folder = Path(self.config['output']['folder'])
        retention_days = self.config['output']['retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        if not output_folder.exists():
            return
        
        deleted = 0
        for file in output_folder.glob("tech_watch_*.html"):
            if file.stat().st_mtime < cutoff_date.timestamp():
                file.unlink()
                deleted += 1
        
        if deleted > 0:
            print(f"{deleted} old report(s) deleted")
    
    def send_email(self, html, filepath):
        """Send the report via email using Gmail SMTP"""
        email_config = self.config.get('email', {})
        
        # Check if email is configured
        to_email = email_config.get('to', '')
        smtp_server = email_config.get('smtp_server', '')
        smtp_username = email_config.get('smtp_username', '')
        smtp_password = email_config.get('smtp_password', '')
        
        if not all([to_email, smtp_server, smtp_username, smtp_password]):
            print("\nEmail not configured. Skipping email sending.")
            print("To enable email, configure SMTP settings in config.yaml")
            return False
        
        try:
            print(f"\nSending email to {to_email}...")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Tech Watch Report - {datetime.now().strftime('%m/%d/%Y')}"
            msg['From'] = email_config.get('from_email', smtp_username)
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html, 'html')
            msg.attach(html_part)
            
            # Connect to Gmail SMTP server
            smtp_port = email_config.get('smtp_port', 587)
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Enable security
            
            # Login and send email
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg.as_string())
            server.quit()
            
            print(f"Email sent successfully to {to_email}!")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("\nEmail authentication failed!")
            print("For Gmail: Make sure you're using an 'App Password', not your regular password")
            print("Generate one at: https://myaccount.google.com/apppasswords")
            return False
        except Exception as e:
            print(f"\nError sending email: {e}")
            return False
    
    def run(self):
        """Run the complete tech watch"""
        print("=" * 60)
        print("Starting mastermaint tech watch")
        print("=" * 60)
        
        # Fetch feeds
        self.fetch_feeds()
        
        if len(self.articles) == 0:
            print("\nNo recent articles found")
            return None
        
        # Generate report
        print("\nGenerating HTML report...")
        html = self.generate_report()
        
        # Save
        filepath = self.save_report(html)
        
        # Send email if configured
        self.send_email(html, filepath)
        
        # Send Teams/Slack notifications if enabled
        if self.top_articles:
            critical_articles = [a for a in self.top_articles if a.get('priority') == 'critical']
            if critical_articles:
                message = f"🚨 {len(critical_articles)} CRITICAL article(s) found!\n\n"
                for a in critical_articles[:3]:
                    message += f"• {a['title']}\n  {a['link']}\n\n"
                self._send_to_teams(message, is_critical=True)
                self._send_to_slack(message, is_critical=True)
            else:
                message = f"📊 Tech Watch Report - {len(self.articles)} articles collected\n"
                if self.trends:
                    message += f"🔥 Top trends: {', '.join([t['keyword'] for t in self.trends[:5]])}\n"
                message += f"\nView full report: file://{filepath}"
                self._send_to_teams(message)
                self._send_to_slack(message)
        
        # Cleanup
        self.cleanup_old_reports()
        
        print("\n" + "=" * 60)
        print("Tech watch completed successfully!")
        print("=" * 60)
        
        return filepath


def main():
    """Main entry point"""
    try:
        watch = TechWatch()
        watch.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
