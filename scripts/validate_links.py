#!/usr/bin/env python3
"""
FreightIQ Quality Assurance & Link Integrity Validator
Parses all compiled HTML pages in dist/ and validates every internal link and asset.
"""

import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if "id" in attrs_dict:
            self.anchors.add(attrs_dict["id"])
            
        if tag == "a" and "href" in attrs_dict:
            href = attrs_dict["href"]
            self.links.append(href)
        elif tag in ("link", "script", "img") and ("href" in attrs_dict or "src" in attrs_dict):
            src = attrs_dict.get("href") or attrs_dict.get("src")
            self.links.append(src)

def validate_site():
    print("🔍 Validating all internal links, anchors and assets across dist/...")
    
    html_files = list(DIST_DIR.rglob("*.html"))
    if not html_files:
        print("❌ No HTML files found in dist/. Run build.py first!")
        sys.exit(1)

    print(f"  Found {len(html_files)} HTML pages to audit.")
    
    # Map of all page IDs for anchor verification
    page_anchors = {}
    extracted_links = {}

    for file_path in html_files:
        rel_path = file_path.relative_to(DIST_DIR)
        parser = LinkExtractor()
        content = file_path.read_text(encoding="utf-8")
        parser.feed(content)
        
        page_anchors[str(rel_path)] = parser.anchors
        extracted_links[str(rel_path)] = parser.links

    errors = []
    checked_count = 0

    for source_file, links in extracted_links.items():
        for link in links:
            if not link or link.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
                continue

            checked_count += 1
            
            # Anchor-only link (#the-freight-data-challenge)
            if link.startswith("#"):
                anchor = link[1:]
                if anchor and anchor not in page_anchors.get(source_file, set()):
                    errors.append(f"Broken anchor '{link}' in {source_file}")
                continue

            # Split path and anchor
            parts = link.split("#")
            path_part = parts[0].strip("/")
            anchor_part = parts[1] if len(parts) > 1 else None

            # Resolve target file
            target_candidates = []
            if not path_part:
                target_candidates.append("index.html")
            else:
                target_candidates.append(path_part)
                target_candidates.append(f"{path_part}.html")
                target_candidates.append(f"{path_part}/index.html")

            found = False
            target_rel = None
            for cand in target_candidates:
                if (DIST_DIR / cand).exists():
                    found = True
                    target_rel = cand
                    break

            if not found:
                errors.append(f"Broken link '{link}' in {source_file} (Target not found)")
            elif anchor_part and target_rel in page_anchors:
                if anchor_part not in page_anchors[target_rel]:
                    errors.append(f"Broken anchor '#{anchor_part}' in link '{link}' from {source_file}")

    print(f"  Audited {checked_count} internal links and assets.")
    
    if errors:
        print(f"❌ Found {len(errors)} broken links:")
        for err in errors[:10]:
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more.")
        sys.exit(1)
    else:
        print("✅ 100% of internal links, assets, and anchors are valid!")

if __name__ == "__main__":
    validate_site()
