#!/usr/bin/env python3
"""
FreightIQ XML Sitemap Generator
Crawls all compiled HTML files in dist/ and outputs dist/sitemap.xml
"""

from pathlib import Path
from datetime import datetime, timezone
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.site_meta import SITE_CONFIG

DIST_DIR = PROJECT_ROOT / "dist"

def generate_sitemap():
    print("🗺️ Generating XML Sitemap...")
    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Collect all canonical URLs
    urls = []
    
    # Homepage
    urls.append({"loc": SITE_CONFIG["domain"] + "/", "priority": "1.0", "changefreq": "daily"})
    
    # Tools Hub
    urls.append({"loc": SITE_CONFIG["domain"] + "/tools", "priority": "0.9", "changefreq": "weekly"})
    
    # Interactive Tools
    tools_slugs = ["sql-playground", "json-validator", "lifecycle-visualizer", "quality-explorer", "troubleshooting-simulator"]
    for ts in tools_slugs:
        urls.append({"loc": f"{SITE_CONFIG['domain']}/tools/{ts}", "priority": "0.9", "changefreq": "weekly"})
        
    # About
    urls.append({"loc": f"{SITE_CONFIG['domain']}/about", "priority": "0.7", "changefreq": "monthly"})
    
    # Core Module Hubs
    module_hubs = ["data-quality", "shipment-data", "validation", "troubleshooting"]
    for mh in module_hubs:
        urls.append({"loc": f"{SITE_CONFIG['domain']}/{mh}", "priority": "0.9", "changefreq": "weekly"})
        
    # Module Articles
    from src.data.module1_data_quality import ARTICLES as M1
    from src.data.module2_shipment_data import ARTICLES as M2
    from src.data.module3_validation import ARTICLES as M3
    from src.data.module4_troubleshooting import ARTICLES as M4
    
    for a in (M1 + M2 + M3 + M4):
        if a["url_path"].endswith("index.html"):
            continue  # Already added as hub
        clean_path = a["url_path"].replace(".html", "")
        urls.append({"loc": f"{SITE_CONFIG['domain']}/{clean_path}", "priority": "0.8", "changefreq": "weekly"})
        
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for u in urls:
        xml_lines.append(f"""  <url>
    <loc>{u['loc']}</loc>
    <lastmod>{now_date}</lastmod>
    <changefreq>{u['changefreq']}</changefreq>
    <priority>{u['priority']}</priority>
  </url>""")
        
    xml_lines.append('</urlset>')
    
    sitemap_content = "\n".join(xml_lines)
    (DIST_DIR / "sitemap.xml").write_text(sitemap_content, encoding="utf-8")
    print(f"  ✓ Sitemap generated with {len(urls)} URLs at dist/sitemap.xml")

if __name__ == "__main__":
    generate_sitemap()
