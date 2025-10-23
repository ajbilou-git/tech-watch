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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from pathlib import Path
from jinja2 import Template
from bs4 import BeautifulSoup
import traceback


class TechWatch:
    def __init__(self, config_path="config.yaml"):
        """Initialize the tech watch system"""
        self.config = self._load_config(config_path)
        self.articles = []
        self.errors = []
        
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
        # Sort articles by date (most recent first)
        sorted_articles = sorted(
            self.articles,
            key=lambda x: x['published'] if x['published'] else (0,),
            reverse=True
        )
        
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
                    <span class="feed-badge">{{ article.feed_name }}</span>
                    📅 {{ article.published_str }}
                </div>
                <div class="article-summary">
                    {{ article.summary }}
                </div>
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
            errors=self.errors
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
