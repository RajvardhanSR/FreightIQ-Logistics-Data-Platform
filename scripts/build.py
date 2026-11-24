#!/usr/bin/env python3
"""
FreightIQ Static Site Generator & Build Pipeline
Generates production HTML files in dist/ with zero external runtime dependencies.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.site_meta import SITE_CONFIG, NAVIGATION
from src.data.module1_data_quality import ARTICLES as M1_ARTICLES
from src.data.module2_shipment_data import ARTICLES as M2_ARTICLES
from src.data.module3_validation import ARTICLES as M3_ARTICLES
from src.data.module4_troubleshooting import ARTICLES as M4_ARTICLES
from src.data.tools_data import TOOLS

ALL_ARTICLES = M1_ARTICLES + M2_ARTICLES + M3_ARTICLES + M4_ARTICLES
DIST_DIR = PROJECT_ROOT / "dist"

def render_header(current_url=""):
    nav_links_html = ""
    for item in NAVIGATION:
        active_class = " active" if current_url.startswith(item["url"]) else ""
        nav_links_html += f"""
        <li class="nav-item">
          <a href="{item['url']}" class="{active_class}">{item['title']}</a>
        </li>
        """

    return f"""
    <header class="site-header">
      <div class="header-container">
        <a href="/" class="brand-logo" aria-label="FreightIQ Homepage">
          <div class="brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
          </div>
          <span>Freight<span style="color: var(--accent-blue);">IQ</span></span>
          <span class="brand-badge">PROD</span>
        </a>

        <nav aria-label="Main Navigation">
          <ul class="nav-links">
            {nav_links_html}
          </ul>
        </nav>

        <div class="nav-actions">
          <a href="/tools" class="btn btn-secondary btn-sm">Developer Tools</a>
          <a href="/data-quality" class="btn btn-primary btn-sm">Explore Hub</a>
          <button class="mobile-menu-btn" aria-label="Toggle navigation menu">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
    </header>
    """

def render_footer():
    return f"""
    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-top">
          <div class="footer-brand">
            <a href="/" class="brand-logo">
              <div class="brand-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <span>Freight<span style="color: var(--accent-blue);">IQ</span></span>
            </a>
            <p>{SITE_CONFIG['tagline']}</p>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">
              An engineering-grade knowledge platform and developer suite built for logistics data engineers, supply chain architects, and ETL developers.
            </p>
          </div>

          <div class="footer-col">
            <h4>Module 1: Data Quality</h4>
            <ul class="footer-links">
              <li><a href="/data-quality">Data Quality Hub</a></li>
              <li><a href="/data-quality/dimensions">6 Core Dimensions</a></li>
              <li><a href="/data-quality/completeness">Data Completeness</a></li>
              <li><a href="/data-quality/accuracy">Data Accuracy</a></li>
              <li><a href="/data-quality/consistency">Data Consistency</a></li>
              <li><a href="/data-quality/timeliness">Data Timeliness</a></li>
              <li><a href="/data-quality/uniqueness">Data Uniqueness</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Module 2: Shipment Data</h4>
            <ul class="footer-links">
              <li><a href="/shipment-data">Shipment Data Hub</a></li>
              <li><a href="/shipment-data/lifecycle">Shipment Lifecycle</a></li>
              <li><a href="/shipment-data/shipment-ids">Master Shipment IDs</a></li>
              <li><a href="/shipment-data/tracking-numbers">Carrier Tracking Formats</a></li>
              <li><a href="/shipment-data/status-events">Status Events & EDI 214</a></li>
              <li><a href="/shipment-data/delivery-dates">Delivery Dates & EDD</a></li>
              <li><a href="/shipment-data/location-data">Geospatial PostGIS Data</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Module 3: Validation</h4>
            <ul class="footer-links">
              <li><a href="/validation">Validation Hub</a></li>
              <li><a href="/validation/sql-techniques">SQL Validation Techniques</a></li>
              <li><a href="/validation/null-validation-sql">NULL Auditing in SQL</a></li>
              <li><a href="/validation/duplicate-record-detection">Duplicate Detection</a></li>
              <li><a href="/validation/data-type-validation">Data Type Enforcement</a></li>
              <li><a href="/validation/range-boundary-validation">Range Boundary Checks</a></li>
              <li><a href="/validation/json-schema-validation">JSON Schema Webhooks</a></li>
              <li><a href="/validation/api-validation">Carrier API Validation</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Module 4: Troubleshooting</h4>
            <ul class="footer-links">
              <li><a href="/troubleshooting">Troubleshooting Hub</a></li>
              <li><a href="/troubleshooting/pipeline-quality">Pipeline Quality & SLOs</a></li>
              <li><a href="/troubleshooting/etl-validation">ETL Reconciliation</a></li>
              <li><a href="/troubleshooting/real-time-monitoring">Real-Time Monitoring</a></li>
              <li><a href="/troubleshooting/automated-testing">Automated Pipeline Tests</a></li>
              <li><a href="/troubleshooting/pipeline-data-mismatches">Data Mismatch Triage</a></li>
              <li><a href="/troubleshooting/sql-errors">SQL Warehouse Errors</a></li>
              <li><a href="/troubleshooting/api-errors">Carrier API Failures</a></li>
              <li><a href="/troubleshooting/database-constraint-errors">Constraint Violations</a></li>
            </ul>
          </div>
        </div>

        <div class="footer-bottom">
          <div>
            &copy; {SITE_CONFIG['current_year']} {SITE_CONFIG['brand_name']}. Built by <a href="/about">{SITE_CONFIG['author_name']}</a>. All rights reserved.
          </div>
          <div style="display: flex; gap: 1.5rem;">
            <a href="/tools">Developer Tools</a>
            <a href="/about">About & Architecture</a>
            <a href="/sitemap.xml">XML Sitemap</a>
          </div>
        </div>
      </div>
    </footer>
    """

def wrap_page(title, meta_title, meta_desc, canonical_url, content_html, structured_data_json="", current_url="", is_tool=False):
    og_image = f"{SITE_CONFIG['domain']}/images/og-card.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta_title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{canonical_url}">
  
  <!-- Google tag (gtag.js) - Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-E774PRL6K7"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-E774PRL6K7');
  </script>
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{meta_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:site_name" content="{SITE_CONFIG['brand_name']}">
  <meta property="og:image" content="{og_image}">

  <!-- Twitter / X -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{canonical_url}">
  <meta name="twitter:title" content="{meta_title}">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{og_image}">

  <!-- Typography & Styling -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles/main.css">

  <!-- Schema.org Structured Data -->
  {structured_data_json}
</head>
<body>
  {render_header(current_url)}
  
  <main id="main-content">
    {content_html}
  </main>

  {render_footer()}

  <script src="/scripts/tools.js"></script>
</body>
</html>
"""

def generate_article_jsonld(article, canonical_url):
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "TechArticle",
                "@id": f"{canonical_url}#article",
                "isPartOf": {
                    "@type": "WebPage",
                    "@id": canonical_url
                },
                "headline": article["title"],
                "description": article["meta_desc"],
                "inLanguage": "en-US",
                "mainEntityOfPage": canonical_url,
                "datePublished": "2026-11-01T08:00:00+00:00",
                "dateModified": "2026-11-11T12:00:00+00:00",
                "author": {
                    "@type": "Person",
                    "name": SITE_CONFIG["author_name"],
                    "jobTitle": SITE_CONFIG["author_title"],
                    "url": f"{SITE_CONFIG['domain']}/about"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": SITE_CONFIG["brand_name"],
                    "url": SITE_CONFIG["domain"],
                    "logo": {
                        "@type": "ImageObject",
                        "url": f"{SITE_CONFIG['domain']}/images/logo.png"
                    }
                },
                "keywords": article["primary_keyword"]
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": SITE_CONFIG["domain"]
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": article["category"],
                        "item": f"{SITE_CONFIG['domain']}/{article['slug'].split('/')[0]}"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": article["title"],
                        "item": canonical_url
                    }
                ]
            }
        ]
    }
    return f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>'

def build_article_page(article):
    # Determine module slug
    module_slug = article["url_path"].split("/")[0]
    
    # Get all sibling articles in this module for the sidebar
    sibling_articles = [a for a in ALL_ARTICLES if a["url_path"].startswith(module_slug)]
    
    sidebar_links = ""
    for a in sibling_articles:
        active = " active" if a["slug"] == article["slug"] else ""
        clean_url = f"/{a['url_path'].replace('.html', '').replace('/index', '')}"
        sidebar_links += f'<li><a href="{clean_url}" class="{active}">{a["title"]}</a></li>'

    # Build Table of Contents
    toc_links = ""
    for item in article.get("toc", []):
        toc_links += f'<li class="toc-item"><a href="#{item["id"]}" class="toc-link">{item["title"]}</a></li>'

    # Build Related Articles from other modules
    other_articles = [a for a in ALL_ARTICLES if not a["url_path"].startswith(module_slug)][:3]
    related_cards = ""
    for oa in other_articles:
        clean_oa_url = f"/{oa['url_path'].replace('.html', '').replace('/index', '')}"
        related_cards += f"""
        <a href="{clean_oa_url}" class="related-card">
          <div class="related-category">{oa['category']}</div>
          <div class="related-title">{oa['title']}</div>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">{oa['reading_time']} &bull; {oa['primary_keyword']}</p>
        </a>
        """

    canonical_clean = f"{SITE_CONFIG['domain']}/{article['url_path'].replace('.html', '').replace('/index', '')}"

    article_html = f"""
    <div class="article-wrapper">
      <!-- Left Navigation Sidebar -->
      <aside class="article-sidebar">
        <div class="sidebar-heading">{article['category']} Module Guides</div>
        <ul class="sidebar-list">
          {sidebar_links}
        </ul>

        <div style="padding: 1.25rem; background: var(--bg-tertiary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); margin-top: 2rem;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--accent-blue); text-transform: uppercase;">Interactive Tool</div>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0.5rem 0 1rem;">Test SQL assertions live in the client-side sandbox.</p>
          <a href="/tools/sql-playground" class="btn btn-primary btn-sm" style="width: 100%;">Launch Playground &rarr;</a>
        </div>
      </aside>

      <!-- Center Main Content -->
      <article class="article-main">
        <header class="article-header">
          <nav class="breadcrumbs" aria-label="Breadcrumb">
            <a href="/">Home</a>
            <span class="breadcrumbs-sep">/</span>
            <a href="/{module_slug}">{article['category']}</a>
            <span class="breadcrumbs-sep">/</span>
            <span style="color: var(--text-primary);">{article['title']}</span>
          </nav>

          <h1 class="article-title">{article['title']}</h1>
          
          <div class="article-meta">
            <span class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              {article['reading_time']}
            </span>
            <span class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              Updated: {article['updated_at']}
            </span>
            <span class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              By {article['author']}
            </span>
          </div>

          <div style="background: rgba(56, 189, 248, 0.05); border-left: 3px solid var(--accent-blue); padding: 1rem 1.25rem; border-radius: 4px; margin-top: 1.5rem; color: var(--text-secondary); font-size: 1.05rem; line-height: 1.7;">
            {article['intro']}
          </div>
        </header>

        <div class="article-content">
          {article['content_html']}
        </div>

        <!-- Cross-Module Contextual Linking -->
        <section class="related-section">
          <h3>Related Engineering Guides</h3>
          <p style="color: var(--text-muted); font-size: 0.95rem;">Continue exploring related data architecture principles across other modules:</p>
          <div class="related-grid">
            {related_cards}
          </div>
        </section>

        <!-- Author Card -->
        <div style="display: flex; gap: 1.5rem; align-items: center; margin-top: 4rem; padding: 1.75rem; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.25rem; color: #070B14; flex-shrink: 0;">
            RR
          </div>
          <div>
            <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary);">{article['author']}</div>
            <div style="font-size: 0.85rem; color: var(--accent-blue); margin-bottom: 0.4rem;">{article['author_title']}</div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">{SITE_CONFIG['author_bio']}</p>
          </div>
        </div>
      </article>

      <!-- Right Table of Contents -->
      <aside class="article-toc">
        <div class="toc-title">On This Page</div>
        <ul class="toc-list">
          {toc_links}
        </ul>
      </aside>
    </div>
    """

    jsonld = generate_article_jsonld(article, canonical_clean)
    return wrap_page(
        title=article["title"],
        meta_title=article["meta_title"],
        meta_desc=article["meta_desc"],
        canonical_url=canonical_clean,
        content_html=article_html,
        structured_data_json=jsonld,
        current_url=f"/{module_slug}"
    )

def build_homepage():
    canonical_url = SITE_CONFIG["domain"]
    
    # 4 Modules Overview cards
    modules_html = f"""
    <section class="section-container" id="modules-overview">
      <div class="section-header">
        <span class="section-tag">Core Knowledge Modules</span>
        <h2 class="section-title">The Four Pillars of Freight Data Engineering</h2>
        <p class="section-description">A systematic 32-guide engineering curriculum designed to eliminate telemetry anomalies, data mismatches, and compliance failures.</p>
      </div>

      <div class="modules-grid">
        <!-- Module 1 -->
        <a href="/data-quality" class="module-card">
          <div class="module-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <h3 class="module-card-title">Module 1: Data Quality</h3>
          <p class="module-card-desc">Architectural frameworks for the 6 core data quality dimensions in logistics: completeness, accuracy, consistency, timeliness, uniqueness, and validity.</p>
          <div class="module-card-footer">
            <span>7 In-Depth Articles</span>
            <span class="module-card-link">Explore Module &rarr;</span>
          </div>
        </a>

        <!-- Module 2 -->
        <a href="/shipment-data" class="module-card">
          <div class="module-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="3" width="15" height="13"></rect>
              <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
              <circle cx="5.5" cy="18.5" r="2.5"></circle>
              <circle cx="18.5" cy="18.5" r="2.5"></circle>
            </svg>
          </div>
          <h3 class="module-card-title">Module 2: Shipment Data</h3>
          <p class="module-card-desc">Relational entity models, finite state machines, UUIDv7 primary keys, carrier tracking regex checksums, EDI 214 mapping, and PostGIS geofencing.</p>
          <div class="module-card-footer">
            <span>7 In-Depth Articles</span>
            <span class="module-card-link">Explore Module &rarr;</span>
          </div>
        </a>

        <!-- Module 3 -->
        <a href="/validation" class="module-card">
          <div class="module-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 17 10 11 4 5"></polyline>
              <line x1="12" y1="19" x2="20" y2="19"></line>
            </svg>
          </div>
          <h3 class="module-card-title">Module 3: Validation</h3>
          <p class="module-card-desc">Advanced SQL assertion suites, window functions, conditional NULL audits, physics range constraints, JSON Schema Draft-07, and rate-limiting.</p>
          <div class="module-card-footer">
            <span>8 In-Depth Articles</span>
            <span class="module-card-link">Explore Module &rarr;</span>
          </div>
        </a>

        <!-- Module 4 -->
        <a href="/troubleshooting" class="module-card">
          <div class="module-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
            </svg>
          </div>
          <h3 class="module-card-title">Module 4: Troubleshooting</h3>
          <p class="module-card-desc">Incident triage playbooks, SLO/SLI error budgets, ETL source-to-target reconciliation, Prometheus observability, and SQL constraint resolution.</p>
          <div class="module-card-footer">
            <span>9 In-Depth Articles</span>
            <span class="module-card-link">Explore Module &rarr;</span>
          </div>
        </a>
      </div>
    </section>
    """

    # Dashboard Metrics Section
    dashboard_html = f"""
    <section class="section-container" style="background: rgba(13, 20, 36, 0.4); border-top: 1px solid var(--border-subtle); border-bottom: 1px solid var(--border-subtle);">
      <div class="section-header">
        <span class="section-tag">Telemetry Analytics</span>
        <h2 class="section-title">Illustrative Logistics Intelligence Dashboard</h2>
        <p class="section-description">Simulated live pipeline health across multi-carrier streaming ingestion gates.</p>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-label">Shipment Events Processed</span>
            <span class="metric-badge badge-blue">Last 24 Hours</span>
          </div>
          <div class="metric-value">1,428,950</div>
          <div class="metric-desc">
            <span class="live-dot"></span> Ingestion Rate: 16.5 events/sec
          </div>
          <div class="metric-disclaimer">* Illustrative sample metric</div>
        </div>

        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-label">Data Validation Pass Rate</span>
            <span class="metric-badge badge-emerald">Within SLA</span>
          </div>
          <div class="metric-value">99.84%</div>
          <div class="metric-desc">
            Passed 3-tier validation mesh
          </div>
          <div class="metric-disclaimer">* Illustrative sample metric</div>
        </div>

        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-label">Pipeline Ingestion Health</span>
            <span class="metric-badge badge-emerald">Operational</span>
          </div>
          <div class="metric-value">99.98%</div>
          <div class="metric-desc">
            p99 Ingestion Lag: 142 ms
          </div>
          <div class="metric-disclaimer">* Illustrative sample metric</div>
        </div>

        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-label">Duplicates Auto-Deduplicated</span>
            <span class="metric-badge badge-amber">Filtered</span>
          </div>
          <div class="metric-value">142</div>
          <div class="metric-desc">
            SHA-256 idempotency cache hit
          </div>
          <div class="metric-disclaimer">* Illustrative sample metric</div>
        </div>
      </div>
    </section>
    """

    # Interactive Lifecycle Section
    lifecycle_html = f"""
    <section class="section-container">
      <div class="section-header">
        <span class="section-tag">State Machine Architecture</span>
        <h2 class="section-title">The Multimodal Shipment Lifecycle</h2>
        <p class="section-description">A deterministic finite state machine prevents out-of-order anomalies and tracks physical custody handoffs.</p>
      </div>

      <div class="pipeline-visual-container">
        <div class="pipeline-header">
          <span style="font-weight: 700; color: var(--text-primary);">Interactive Event Timeline</span>
          <span id="lifecycle-status-badge" class="metric-badge badge-emerald">Valid State Machine Sequence</span>
        </div>

        <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <label for="lifecycle-scenario-select" style="font-size: 0.85rem; color: var(--text-muted);">Select Scenario:</label>
            <select id="lifecycle-scenario-select" class="tool-select">
              <option value="happy_path">Standard Delivery (Happy Path)</option>
              <option value="customs_delay">Cross-Border Customs Delay & Release</option>
              <option value="out_of_order_violation">Out-of-Order Transition Violation (Error Flagged)</option>
            </select>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <button id="lifecycle-prev-btn" class="btn btn-secondary btn-sm">&larr; Previous Scan</button>
            <button id="lifecycle-next-btn" class="btn btn-primary btn-sm">Next Scan &rarr;</button>
          </div>
        </div>

        <div id="lifecycle-steps-container"></div>
        <div id="lifecycle-event-details" style="margin-top: 1.5rem;"></div>
      </div>
    </section>
    """

    # Developer Tools Preview Section
    tools_preview_html = f"""
    <section class="section-container" style="background: rgba(13, 20, 36, 0.4); border-top: 1px solid var(--border-subtle); border-bottom: 1px solid var(--border-subtle);">
      <div class="section-header">
        <span class="section-tag">Interactive Engineering Suite</span>
        <h2 class="section-title">Zero-Credential Developer Tools</h2>
        <p class="section-description">Run real SQL validation assertions, test webhook schemas against Draft-07, and simulate pipeline triage directly in your browser.</p>
      </div>

      <div class="modules-grid">
        <a href="/tools/sql-playground" class="module-card">
          <div class="module-card-icon" style="background: rgba(56, 189, 248, 0.1); color: var(--accent-blue);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
          </div>
          <h3 class="module-card-title">SQL Validation Playground</h3>
          <p class="module-card-desc">Execute queries against preloaded shipment tables: detect NULL keys, duplicate tracking numbers, and weight boundary violations.</p>
          <div class="module-card-footer">
            <span class="badge-emerald" style="padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Runnable Engine</span>
            <span class="module-card-link">Launch Playground &rarr;</span>
          </div>
        </a>

        <a href="/tools/json-validator" class="module-card">
          <div class="module-card-icon" style="background: rgba(6, 182, 212, 0.1); color: var(--accent-cyan);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="16 18 22 12 16 6"></polyline>
              <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
          </div>
          <h3 class="module-card-title">JSON Schema Validator</h3>
          <p class="module-card-desc">Validate carrier webhook payloads against the Logistics Webhook Specification with instant path error pinpointing.</p>
          <div class="module-card-footer">
            <span class="badge-blue" style="padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Draft-07 Spec</span>
            <span class="module-card-link">Validate JSON &rarr;</span>
          </div>
        </a>

        <a href="/tools/quality-explorer" class="module-card">
          <div class="module-card-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--accent-emerald);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 20V10"></path>
              <path d="M12 20V4"></path>
              <path d="M6 20v-6"></path>
            </svg>
          </div>
          <h3 class="module-card-title">Data Quality Explorer</h3>
          <p class="module-card-desc">Interactive 6-dimension mathematical simulator. Adjust defect sliders to observe composite Data Quality Score (DQS) calculations.</p>
          <div class="module-card-footer">
            <span class="badge-emerald" style="padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Interactive Simulator</span>
            <span class="module-card-link">Open Explorer &rarr;</span>
          </div>
        </a>
      </div>

      <div style="text-align: center; margin-top: 3rem;">
        <a href="/tools" class="btn btn-secondary">Explore All 5 Interactive Developer Tools &rarr;</a>
      </div>
    </section>
    """

    # Featured Guides Section
    featured_guides_html = f"""
    <section class="section-container">
      <div class="section-header">
        <span class="section-tag">Curated Engineering Guides</span>
        <h2 class="section-title">Deep Technical Resources</h2>
        <p class="section-description">Practical, production-tested architectures written for real-world freight data systems.</p>
      </div>

      <div class="modules-grid">
        <a href="/data-quality/uniqueness" class="related-card" style="padding: 1.75rem;">
          <div class="related-category">Data Quality &bull; 12 min read</div>
          <div class="related-title" style="font-size: 1.2rem;">Deduplication Strategies for High-Velocity Freight Webhooks</div>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">Implement SHA-256 event fingerprinting, sliding window caches in Redis, and idempotent PostgreSQL UPSERTs.</p>
          <span class="module-card-link">Read Full Guide &rarr;</span>
        </a>

        <a href="/shipment-data/tracking-numbers" class="related-card" style="padding: 1.75rem;">
          <div class="related-category">Shipment Data &bull; 11 min read</div>
          <div class="related-title" style="font-size: 1.2rem;">Carrier Tracking Numbers: Formats, Checksums & Parsing</div>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">Mathematical verification algorithms: UPS 1Z Modulo-10, FedEx Mod-11/7, and ocean container ISO 6346 check digits.</p>
          <span class="module-card-link">Read Full Guide &rarr;</span>
        </a>

        <a href="/validation/sql-techniques" class="related-card" style="padding: 1.75rem;">
          <div class="related-category">Validation &bull; 14 min read</div>
          <div class="related-title" style="font-size: 1.2rem;">Advanced SQL Validation Techniques for Logistics Data</div>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">Window functions, LEAD/LAG chronological checks, and cumulative LTL load weight audits in PostgreSQL.</p>
          <span class="module-card-link">Read Full Guide &rarr;</span>
        </a>

        <a href="/troubleshooting/pipeline-data-mismatches" class="related-card" style="padding: 1.75rem;">
          <div class="related-category">Troubleshooting &bull; 11 min read</div>
          <div class="related-title" style="font-size: 1.2rem;">Troubleshooting Pipeline Data Mismatches: Reconciliation & Drift</div>
          <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">Systematic diagnosis for isolating discrepancies between manifest records, warehouse ledgers, and carrier invoices.</p>
          <span class="module-card-link">Read Full Guide &rarr;</span>
        </a>
      </div>
    </section>
    """

    # Final CTA Section
    final_cta_html = f"""
    <section class="section-container" style="text-align: center; padding: 6rem 1.5rem; background: radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.1) 0%, transparent 70%);">
      <h2 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; margin-bottom: 1rem; border: none;">Build Better Logistics Data Pipelines.</h2>
      <p style="max-width: 640px; margin: 0 auto 2.5rem; color: var(--text-secondary); font-size: 1.15rem;">
        Explore our 32-guide engineering curriculum and test your queries against production-grade schemas.
      </p>
      <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
        <a href="/data-quality" class="btn btn-primary" style="padding: 0.85rem 2rem;">Explore Knowledge Hub</a>
        <a href="/tools" class="btn btn-secondary" style="padding: 0.85rem 2rem;">Explore Developer Tools</a>
      </div>
    </section>
    """

    # Hero with animated pipeline
    hero_html = f"""
    <section class="hero-section">
      <div class="hero-pill">
        <span class="hero-pill-badge">FREIGHT DATA INTELLIGENCE</span>
        <span>Enterprise Logistics Knowledge Platform</span>
      </div>

      <h1 class="hero-title">Make Every Shipment Data-Ready.</h1>
      
      <p class="hero-subtitle">
        Explore practical frameworks, SQL validation techniques, shipment schemas and data engineering resources built for modern logistics ecosystems.
      </p>

      <div class="hero-ctas">
        <a href="/data-quality" class="btn btn-primary" style="padding: 0.85rem 1.75rem;">Explore Knowledge Hub</a>
        <a href="/tools" class="btn btn-secondary" style="padding: 0.85rem 1.75rem;">Explore Developer Tools</a>
      </div>

      <!-- Animated Data Pipeline Visual Concept -->
      <div class="pipeline-visual-container">
        <div class="pipeline-header">
          <span style="font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            Real-Time Logistics Data Flow Pipeline
          </span>
          <span class="pipeline-status-live">
            <span class="live-dot"></span> Pipeline Active: 1.42M events/day
          </span>
        </div>

        <div class="pipeline-flow">
          <!-- Node 1 -->
          <div class="pipeline-node">
            <div class="pipeline-node-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                <line x1="6" y1="6" x2="6.01" y2="6"></line>
                <line x1="6" y1="18" x2="6.01" y2="18"></line>
              </svg>
            </div>
            <div class="pipeline-node-title">Carrier APIs</div>
            <div class="pipeline-node-sub">EDI 214 &bull; Webhooks &bull; IoT</div>
          </div>

          <!-- Node 2 -->
          <div class="pipeline-node">
            <div class="pipeline-node-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
            </div>
            <div class="pipeline-node-title">Data Ingestion</div>
            <div class="pipeline-node-sub">Kafka &bull; HMAC &bull; DLQ</div>
          </div>

          <!-- Node 3 (Validation Center) -->
          <div class="pipeline-node" style="border-color: var(--accent-blue); background: rgba(56, 189, 248, 0.08); box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);">
            <div class="pipeline-node-icon" style="background: rgba(56, 189, 248, 0.2); color: #FFFFFF;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div class="pipeline-node-title" style="color: var(--accent-blue);">Validation Engine</div>
            <div class="pipeline-node-sub">JSON Schema &bull; FSM Assertions</div>
          </div>

          <!-- Node 4 -->
          <div class="pipeline-node">
            <div class="pipeline-node-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
              </svg>
            </div>
            <div class="pipeline-node-title">ETL Pipeline</div>
            <div class="pipeline-node-sub">dbt &bull; Normalization &bull; PostGIS</div>
          </div>

          <!-- Node 5 -->
          <div class="pipeline-node">
            <div class="pipeline-node-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
            </div>
            <div class="pipeline-node-title">Analytics Dashboard</div>
            <div class="pipeline-node-sub">Real-Time Control Tower</div>
          </div>
        </div>

        <!-- Animated Data Packet -->
        <div class="data-packet"></div>
      </div>
    </section>
    """

    content_html = f"""
    {hero_html}
    {dashboard_html}
    {modules_html}
    {lifecycle_html}
    {tools_preview_html}
    {featured_guides_html}
    {final_cta_html}
    """

    structured_data = f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@graph": [
        {{
          "@type": "WebSite",
          "@id": "{SITE_CONFIG['domain']}#website",
          "url": "{SITE_CONFIG['domain']}",
          "name": "{SITE_CONFIG['brand_name']}",
          "description": "{SITE_CONFIG['tagline']}",
          "publisher": {{
            "@type": "Person",
            "name": "{SITE_CONFIG['author_name']}",
            "jobTitle": "{SITE_CONFIG['author_title']}"
          }}
        }},
        {{
          "@type": "Organization",
          "@id": "{SITE_CONFIG['domain']}#organization",
          "name": "{SITE_CONFIG['brand_name']}",
          "url": "{SITE_CONFIG['domain']}",
          "logo": "{SITE_CONFIG['domain']}/images/logo.png"
        }}
      ]
    }}
    </script>
    """

    return wrap_page(
        title="FreightIQ — The Engineering Behind Logistics Data",
        meta_title="FreightIQ — The Engineering Behind Logistics Data",
        meta_desc="FreightIQ is a technical educational knowledge platform and developer suite covering logistics data engineering, carrier tracking schemas, SQL validation, and pipeline troubleshooting.",
        canonical_url=canonical_url,
        content_html=content_html,
        structured_data_json=structured_data,
        current_url="/"
    )

def build_standalone_tool_page(tool):
    tool_id = tool["tool_id"]
    canonical_clean = f"{SITE_CONFIG['domain']}/{tool['url_path'].replace('.html', '')}"

    if tool_id == "sql-playground":
        tool_workspace_html = """
        <div class="tool-workspace">
          <div class="tool-toolbar">
            <div class="tool-presets">
              <label for="sql-preset-select" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">Validation Assertion:</label>
              <select id="sql-preset-select" class="tool-select">
                <option value="null_audit">1. NULL Value Audit (Missing Keys)</option>
                <option value="duplicates">2. Duplicate Tracking Number Detection</option>
                <option value="weight_boundaries">3. Weight Boundary Violations (Tare/Gross)</option>
                <option value="chronological_anomalies">4. Chronological Anomaly (Delivered before Creation)</option>
                <option value="orphan_events">5. Orphan Status Events (Missing Parent)</option>
              </select>
            </div>
            <div>
              <button id="run-sql-btn" class="btn btn-primary btn-sm">▶ Run Assertion</button>
            </div>
          </div>

          <div class="tool-editor-split">
            <div class="tool-editor-pane">
              <div class="pane-title">
                <span>SQL Query Editor (PostgreSQL Syntax)</span>
                <span style="color: var(--accent-blue); font-size: 0.75rem;">In-Memory Sandbox</span>
              </div>
              <textarea id="sql-editor" class="code-textarea" spellcheck="false">-- Check for NULL or missing critical shipment identifiers
SELECT 
  shipment_id, 
  tracking_number, 
  carrier_code, 
  destination_hub, 
  status
FROM shipments
WHERE tracking_number IS NULL 
   OR destination_hub IS NULL 
   OR carrier_code IS NULL;</textarea>
            </div>

            <div class="tool-editor-pane">
              <div class="pane-title">
                <span>Query Results Viewport</span>
                <span id="sql-stats" style="font-size: 0.75rem; color: var(--text-muted);">Ready</span>
              </div>
              <div id="sql-output" class="result-viewport">
                <!-- Output populated by JS -->
              </div>
            </div>
          </div>
        </div>
        """
    elif tool_id == "json-validator":
        tool_workspace_html = """
        <div class="tool-workspace">
          <div class="tool-toolbar">
            <div class="tool-presets">
              <label for="json-preset-select" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">Sample Payload:</label>
              <select id="json-preset-select" class="tool-select">
                <option value="valid_fedex">1. Valid FedEx Express Milestone Webhook</option>
                <option value="valid_ocean">2. Valid Ocean Container Gate-In (Maersk)</option>
                <option value="invalid_missing_keys">3. Invalid: Missing Tracking Number & Bad Date</option>
                <option value="invalid_physics">4. Invalid: Negative Weight & Illegal Status Enum</option>
              </select>
            </div>
            <div>
              <button id="validate-json-btn" class="btn btn-primary btn-sm">✓ Validate Schema</button>
            </div>
          </div>

          <div class="tool-editor-split">
            <div class="tool-editor-pane">
              <div class="pane-title">
                <span>JSON Payload Input Editor</span>
                <span style="font-size: 0.75rem; color: var(--accent-blue);">Draft-07 Enforced</span>
              </div>
              <textarea id="json-editor" class="code-textarea" spellcheck="false"></textarea>
            </div>

            <div class="tool-editor-pane">
              <div class="pane-title">
                <span>Validation Results & Error Report</span>
              </div>
              <div id="json-results" class="result-viewport">
                <!-- Output populated by JS -->
              </div>
            </div>
          </div>
        </div>
        """
    elif tool_id == "lifecycle-visualizer":
        tool_workspace_html = """
        <div class="pipeline-visual-container" style="max-width: 100%;">
          <div class="pipeline-header">
            <span style="font-weight: 700; color: var(--text-primary);">Interactive Event Timeline & State Transition Gate</span>
            <span id="lifecycle-status-badge" class="metric-badge badge-emerald">Valid State Machine Sequence</span>
          </div>

          <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <label for="lifecycle-scenario-select" style="font-size: 0.85rem; color: var(--text-muted);">Select Scenario:</label>
              <select id="lifecycle-scenario-select" class="tool-select">
                <option value="happy_path">Standard Delivery (Happy Path)</option>
                <option value="customs_delay">Cross-Border Customs Delay & Release</option>
                <option value="out_of_order_violation">Out-of-Order Transition Violation (Error Flagged)</option>
              </select>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <button id="lifecycle-prev-btn" class="btn btn-secondary btn-sm">&larr; Previous Scan</button>
              <button id="lifecycle-next-btn" class="btn btn-primary btn-sm">Next Scan &rarr;</button>
            </div>
          </div>

          <div id="lifecycle-steps-container"></div>
          <div id="lifecycle-event-details" style="margin-top: 1.5rem;"></div>
        </div>
        """
    elif tool_id == "quality-explorer":
        tool_workspace_html = """
        <div class="tool-workspace" style="padding: 2.5rem;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;">
            <div>
              <h3 style="margin-top: 0;">Simulation Controls</h3>
              <p style="font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 2rem;">Adjust data stream volume and injected defect ratios to evaluate downstream composite Data Quality Scores (DQS).</p>

              <div style="margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem;">
                  <span>Injected Defect Ratio (NULLs, Schema Errors):</span>
                  <span id="defect-pct-display" style="color: var(--accent-rose); font-family: var(--font-mono);">2.5%</span>
                </div>
                <input type="range" id="quality-defect-slider" min="0" max="25" step="0.5" value="2.5" style="width: 100%; accent-color: var(--accent-blue);">
              </div>

              <div style="margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem;">
                  <span>Daily Shipment Stream Volume:</span>
                  <span id="volume-display" style="color: var(--accent-blue); font-family: var(--font-mono);">100,000</span>
                </div>
                <input type="range" id="quality-volume-slider" min="10000" max="1000000" step="10000" value="100000" style="width: 100%; accent-color: var(--accent-blue);">
              </div>

              <div style="background: var(--bg-tertiary); padding: 1.25rem; border-radius: var(--radius-md); font-size: 0.85rem; border: 1px solid var(--border-subtle);">
                <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">Mathematical Metric Formula:</div>
                <div style="font-family: var(--font-mono); color: var(--accent-cyan); margin-bottom: 0.5rem;">DQS = 0.25*Comp + 0.25*Acc + 0.15*Cons + 0.15*Time + 0.10*Uniq + 0.10*Valid</div>
                <div style="color: var(--text-muted);">Values below 98.0% trigger automated contract penalty audits with carrier dispatchers.</div>
              </div>
            </div>

            <div>
              <h3 style="margin-top: 0;">Real-Time Scorecard</h3>
              <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 2rem; text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.5rem;">Composite Data Quality Score</div>
                <div id="quality-score-display" style="font-size: 4rem; font-weight: 800; color: var(--text-primary); line-height: 1; font-family: var(--font-mono);">97.5%</div>
                
                <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; margin: 1.5rem 0;">
                  <div id="quality-progress-bar" style="width: 97.5%; height: 100%; background: var(--accent-emerald); transition: width 0.2s;"></div>
                </div>

                <div style="display: flex; justify-content: space-around; font-size: 0.85rem;">
                  <div>Clean Records: <strong id="clean-count-display" style="color: var(--accent-emerald);">97,500</strong></div>
                  <div>Quarantined Defective: <strong id="defect-count-display" style="color: var(--accent-rose);">2,500</strong></div>
                </div>
              </div>

              <!-- Breakdown grid -->
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-sm);">
                  <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Completeness</div>
                  <div id="dim-completeness" style="font-size: 1.5rem; font-weight: 700; color: var(--accent-blue);">97.8%</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-sm);">
                  <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Accuracy</div>
                  <div id="dim-accuracy" style="font-size: 1.5rem; font-weight: 700; color: var(--accent-blue);">97.2%</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-sm);">
                  <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Uniqueness</div>
                  <div id="dim-uniqueness" style="font-size: 1.5rem; font-weight: 700; color: var(--accent-emerald);">99.0%</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-sm);">
                  <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Timeliness</div>
                  <div id="dim-timeliness" style="font-size: 1.5rem; font-weight: 700; color: var(--accent-emerald);">98.2%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    elif tool_id == "troubleshooting-simulator":
        tool_workspace_html = """
        <div class="tool-workspace" style="padding: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;">
            <div>
              <label for="troubleshoot-scenario-select" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">Incident Outage Scenario:</label>
              <select id="troubleshoot-scenario-select" class="tool-select" style="margin-left: 0.5rem; max-width: 420px;">
                <option value="missing_id">1. Missing Shipment ID in Carrier Ingestion Stream</option>
                <option value="duplicate_webhook">2. Duplicate Ingestion Causing Double-Counting</option>
                <option value="invalid_timestamp">3. Non-Standard Timezone / Epoch Parsing Failure</option>
                <option value="schema_mismatch">4. Schema Drift — Upstream Renamed Payload Key</option>
                <option value="api_timeout">5. Carrier Rate Limit (HTTP 429) & Gateway Timeout</option>
                <option value="fk_violation">6. Foreign Key Constraint Error on Hub Location</option>
              </select>
            </div>
            <div>
              <span id="troubleshoot-status-badge" class="metric-badge" style="background: rgba(244,63,94,0.15); color: var(--accent-rose);">CRITICAL_FAILURE</span>
            </div>
          </div>

          <div id="pipeline-sim-diagram" style="margin-bottom: 2rem; background: var(--bg-card); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);"></div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
            <div>
              <h4 id="troubleshoot-title" style="margin-top: 0; color: var(--accent-blue);">Scenario Title</h4>
              <div id="troubleshoot-service" style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">Failing Service</div>
              
              <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem;">Diagnostic Stack Trace / Log:</div>
              <pre id="troubleshoot-log" style="background: var(--bg-code); padding: 1rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: #FB7185; overflow-x: auto; white-space: pre-wrap; max-height: 220px; font-family: var(--font-mono);"></pre>

              <div style="margin-top: 1.5rem;">
                <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.4rem;">Root Cause Analysis (RCA):</div>
                <p id="troubleshoot-root-cause" style="font-size: 0.9rem; color: var(--text-secondary); margin: 0;"></p>
              </div>
            </div>

            <div>
              <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem;">Remediation Patch / Fix Script:</div>
              <pre id="troubleshoot-fix" style="background: var(--bg-code); padding: 1.25rem; border-radius: var(--radius-sm); font-size: 0.85rem; color: #34D399; overflow-x: auto; font-family: var(--font-mono); border: 1px solid var(--border-subtle); max-height: 280px;"></pre>

              <div style="margin-top: 1.5rem; text-align: right;">
                <button id="troubleshoot-resolve-btn" class="btn btn-primary">⚡ Apply Resolution & Verify Fix</button>
              </div>
            </div>
          </div>
        </div>
        """

    content_html = f"""
    <div class="tool-container">
      <div class="tool-header">
        <nav class="breadcrumbs" style="justify-content: center; margin-bottom: 1rem;">
          <a href="/">Home</a>
          <span class="breadcrumbs-sep">/</span>
          <a href="/tools">Developer Tools</a>
          <span class="breadcrumbs-sep">/</span>
          <span>{tool['headline']}</span>
        </nav>
        <span class="metric-badge badge-blue" style="margin-bottom: 1rem; display: inline-block;">{tool['badge']}</span>
        <h1 style="font-size: clamp(2rem, 4vw, 2.75rem); margin-bottom: 1rem;">{tool['headline']}</h1>
        <p style="max-width: 720px; margin: 0 auto; color: var(--text-secondary); font-size: 1.1rem;">
          {tool['description']}
        </p>
      </div>

      {tool_workspace_html}

      <div style="margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span style="font-weight: 600; color: var(--text-primary);">Need the full theoretical architecture?</span>
          <span style="color: var(--text-muted); font-size: 0.9rem; margin-left: 0.5rem;">Read the comprehensive engineering guide.</span>
        </div>
        <a href="/data-quality" class="btn btn-secondary btn-sm">Explore Knowledge Hub &rarr;</a>
      </div>
    </div>
    """

    structured_data = f"""
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@graph": [
        {{
          "@type": "WebApplication",
          "@id": "{canonical_clean}#webapp",
          "name": "{tool['title']}",
          "applicationCategory": "DeveloperApplication",
          "operatingSystem": "All",
          "url": "{canonical_clean}",
          "author": {{
            "@type": "Person",
            "name": "{SITE_CONFIG['author_name']}"
          }}
        }},
        {{
          "@type": "BreadcrumbList",
          "@id": "{canonical_clean}#breadcrumb",
          "itemListElement": [
            {{
              "@type": "ListItem",
              "position": 1,
              "name": "Home",
              "item": "{SITE_CONFIG['domain']}"
            }},
            {{
              "@type": "ListItem",
              "position": 2,
              "name": "Developer Tools",
              "item": "{SITE_CONFIG['domain']}/tools"
            }},
            {{
              "@type": "ListItem",
              "position": 3,
              "name": "{tool['headline']}",
              "item": "{canonical_clean}"
            }}
          ]
        }}
      ]
    }}
    </script>
    """

    return wrap_page(
        title=tool["title"],
        meta_title=tool["meta_title"],
        meta_desc=tool["meta_desc"],
        canonical_url=canonical_clean,
        content_html=content_html,
        structured_data_json=structured_data,
        current_url="/tools",
        is_tool=True
    )

def build_tools_hub():
    canonical_clean = f"{SITE_CONFIG['domain']}/tools"
    
    tools_cards = ""
    for t in TOOLS:
        clean_url = f"/{t['url_path'].replace('.html', '')}"
        tools_cards += f"""
        <a href="{clean_url}" class="module-card">
          <div class="metric-badge badge-blue" style="width: fit-content; margin-bottom: 1rem;">{t['badge']}</div>
          <h3 class="module-card-title">{t['headline']}</h3>
          <p class="module-card-desc">{t['description']}</p>
          <div class="module-card-footer">
            <span style="color: var(--accent-emerald);">● Fully Functional Client-Side</span>
            <span class="module-card-link">Launch Tool &rarr;</span>
          </div>
        </a>
        """

    content_html = f"""
    <div class="section-container">
      <div class="section-header" style="text-align: center; max-width: 800px; margin: 0 auto 4rem;">
        <span class="section-tag">Interactive Suite</span>
        <h1 class="section-title">Logistics Developer & Validation Tools</h1>
        <p class="section-description" style="margin: 0 auto;">
          Safe, zero-credential interactive utilities engineered to test queries, validate schemas, simulate state transitions, and troubleshoot pipeline outages.
        </p>
      </div>

      <div class="modules-grid">
        {tools_cards}
      </div>
    </div>
    """

    return wrap_page(
        title="Logistics Developer Tools Hub | FreightIQ",
        meta_title="Logistics Developer Tools: SQL, JSON Schema & FSM | FreightIQ",
        meta_desc="Interactive developer suite for freight engineers: SQL Validation Playground, JSON Shipment Schema Validator, Lifecycle Visualizer, and Troubleshooting Simulator.",
        canonical_url=canonical_clean,
        content_html=content_html,
        current_url="/tools"
    )

def build_about_page():
    canonical_clean = f"{SITE_CONFIG['domain']}/about"
    content_html = f"""
    <div class="article-wrapper single-column">
      <header class="article-header" style="border: none; text-align: center;">
        <span class="section-tag">Author & Architecture</span>
        <h1 class="article-title">About FreightIQ & Rajvardhan Singh Rathore</h1>
        <p style="font-size: 1.15rem; color: var(--text-secondary); max-width: 680px; margin: 1rem auto 0;">
          The Engineering Behind Logistics Data — Architectural principles, author background, and technical platform overview.
        </p>
      </header>

      <div class="article-content">
        <h2>Mission Statement</h2>
        <p>FreightIQ was created to solve an acute engineering challenge in transportation and global commerce: the lack of rigorous, production-grade technical literature for logistics data engineering. While general software engineering has rich resources for distributed systems and databases, logistics data architects often struggle with poorly documented EDI 214 standards, unversioned carrier webhooks, and complex physical state-machine anomalies.</p>

        <h2>Author Profile</h2>
        <div style="display: flex; gap: 1.5rem; align-items: center; padding: 2rem; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); margin: 2rem 0;">
          <div style="width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.5rem; color: #070B14; flex-shrink: 0;">
            RR
          </div>
          <div>
            <h3 style="margin: 0; font-size: 1.3rem;">Rajvardhan Singh Rathore</h3>
            <div style="color: var(--accent-blue); font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem;">Logistics Data Architect & Full-Stack Engineer</div>
            <p style="margin: 0; font-size: 0.9rem; color: var(--text-secondary);">
              Specializing in enterprise data platforms, streaming telemetry ingestion (Kafka/Flink), carrier EDI translation, and PostgreSQL spatial architectures. 
            </p>
          </div>
        </div>

        <h2>Platform Architecture & Engineering Stack</h2>
        <p>FreightIQ is engineered for maximum performance, security, and Core Web Vitals reliability:</p>
        <ul>
          <li><strong>Architecture:</strong> Python-compiled static site architecture producing pure semantic HTML5, zero-bloat CSS, and client-side JavaScript.</li>
          <li><strong>Hosting:</strong> AWS Lightsail, Ubuntu 22.04 LTS, Nginx web server with HTTP/2 and Brotli/Gzip compression.</li>
          <li><strong>Security & DNS:</strong> Cloudflare edge proxy with SSL/TLS Full mode, strict Content-Security-Policy (CSP), and automated HTTPS redirects.</li>
          <li><strong>Interactive Tools:</strong> In-browser zero-credential execution engines for SQL, JSON Schema Draft-07, and Finite State Machine visualization.</li>
          <li><strong>SEO:</strong> Complete 32-article canonical architecture with Schema.org JSON-LD (TechArticle, BreadcrumbList, WebSite, Organization).</li>
        </ul>

        <h2>Contact & Inquiries</h2>
        <p>For architectural collaborations, technical inquiries, or platform feedback, connect directly via <a href="https://rajvardhansinghrathore.in">rajvardhansinghrathore.in</a>.</p>
      </div>
    </div>
    """

    return wrap_page(
        title="About FreightIQ & Rajvardhan Singh Rathore",
        meta_title="About FreightIQ & Rajvardhan Singh Rathore | Logistics Data Architect",
        meta_desc="About FreightIQ and Rajvardhan Singh Rathore. Learn about the engineering philosophy, architecture, and technology behind this logistics data knowledge platform.",
        canonical_url=canonical_clean,
        content_html=content_html,
        current_url="/about"
    )

def main():
    print("🚀 Starting FreightIQ Production Build Pipeline...")
    
    # 1. Clean dist directory
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    
    # 2. Create subdirectories
    (DIST_DIR / "styles").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "scripts").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "images").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "data-quality").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "shipment-data").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "validation").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "troubleshooting").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "tools").mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "about").mkdir(parents=True, exist_ok=True)

    # 3. Copy static CSS and JS
    shutil.copy2(PROJECT_ROOT / "src" / "styles" / "main.css", DIST_DIR / "styles" / "main.css")
    shutil.copy2(PROJECT_ROOT / "src" / "scripts" / "tools.js", DIST_DIR / "scripts" / "tools.js")
    print("  ✓ Assets copied (CSS & JS)")

    # 4. Generate Homepage
    home_html = build_homepage()
    (DIST_DIR / "index.html").write_text(home_html, encoding="utf-8")
    print("  ✓ Homepage generated (dist/index.html)")

    # 5. Generate All 31 Module Articles
    print(f"  ✓ Compiling {len(ALL_ARTICLES)} Technical Articles across 4 Modules...")
    for article in ALL_ARTICLES:
        html = build_article_page(article)
        target_path = DIST_DIR / article["url_path"]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(html, encoding="utf-8")
        
        # If the file is e.g. data-quality/dimensions.html, also write data-quality/dimensions/index.html for clean URLs
        if not target_path.name == "index.html":
            clean_dir = target_path.parent / target_path.stem
            clean_dir.mkdir(parents=True, exist_ok=True)
            (clean_dir / "index.html").write_text(html, encoding="utf-8")

    # 6. Generate Standalone Developer Tools & Hub
    print(f"  ✓ Compiling {len(TOOLS)} Interactive Developer Tools...")
    for tool in TOOLS:
        html = build_standalone_tool_page(tool)
        target_path = DIST_DIR / tool["url_path"]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(html, encoding="utf-8")

        # Also create clean URL directory
        clean_dir = target_path.parent / target_path.stem
        clean_dir.mkdir(parents=True, exist_ok=True)
        (clean_dir / "index.html").write_text(html, encoding="utf-8")

    tools_hub_html = build_tools_hub()
    (DIST_DIR / "tools" / "index.html").write_text(tools_hub_html, encoding="utf-8")

    # 7. Generate About Page
    about_html = build_about_page()
    (DIST_DIR / "about" / "index.html").write_text(about_html, encoding="utf-8")
    print("  ✓ About & Architecture page generated (dist/about/index.html)")

    # 8. Generate robots.txt
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_CONFIG['domain']}/sitemap.xml
"""
    (DIST_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")
    print("  ✓ robots.txt generated")

    print("\n🎉 Build Pipeline Completed Successfully!")
    print(f"   Total Pages in dist/: {len(list(DIST_DIR.rglob('*.html')))}")

if __name__ == "__main__":
    main()
