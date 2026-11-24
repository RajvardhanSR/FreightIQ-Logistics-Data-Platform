#!/usr/bin/env python3
"""
Generates a print-optimized, publication-grade HTML document for FreightIQ
and renders it into a high-resolution PDF using Headless Chrome.
"""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

HTML_OUT = DOCS_DIR / "documentation_print.html"
PDF_OUT = DOCS_DIR / "FreightIQ_Platform_Architecture_Documentation.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FreightIQ — Platform Architecture & Technical Documentation</title>
  <style>
    @page {
      size: A4;
      margin: 18mm 16mm 20mm 16mm;
      @bottom-right {
        content: counter(page);
      }
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: #1E293B;
      background: #FFFFFF;
      font-size: 10pt;
      line-height: 1.55;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    /* Cover Page */
    .cover-page {
      height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      page-break-after: always;
      padding: 40px 20px 20px 20px;
    }

    .cover-badge {
      display: inline-block;
      background: #0284C7;
      color: #FFFFFF;
      font-size: 8pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      padding: 4px 12px;
      border-radius: 4px;
      margin-bottom: 24px;
    }

    .cover-title {
      font-size: 32pt;
      font-weight: 800;
      line-height: 1.15;
      color: #0F172A;
      margin-bottom: 12px;
      letter-spacing: -0.5px;
    }

    .cover-subtitle {
      font-size: 16pt;
      font-weight: 400;
      color: #0284C7;
      margin-bottom: 24px;
      line-height: 1.3;
    }

    .cover-desc {
      font-size: 11pt;
      color: #475569;
      max-width: 600px;
      line-height: 1.6;
      border-left: 3px solid #0284C7;
      padding-left: 16px;
      margin-bottom: 40px;
    }

    .cover-meta-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 8px;
      padding: 20px;
      margin-top: auto;
    }

    .cover-meta-item {
      font-size: 9pt;
    }

    .cover-meta-label {
      font-size: 7.5pt;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: #64748B;
      margin-bottom: 3px;
    }

    .cover-meta-value {
      font-weight: 600;
      color: #0F172A;
    }

    /* Headings */
    h1 {
      font-size: 18pt;
      font-weight: 800;
      color: #0F172A;
      border-bottom: 2px solid #0284C7;
      padding-bottom: 6px;
      margin-top: 28px;
      margin-bottom: 14px;
      page-break-after: avoid;
    }

    h2 {
      font-size: 13pt;
      font-weight: 700;
      color: #1E293B;
      margin-top: 20px;
      margin-bottom: 10px;
      border-bottom: 1px solid #E2E8F0;
      padding-bottom: 4px;
      page-break-after: avoid;
    }

    h3 {
      font-size: 11pt;
      font-weight: 700;
      color: #0284C7;
      margin-top: 14px;
      margin-bottom: 6px;
      page-break-after: avoid;
    }

    p {
      margin-bottom: 10px;
      color: #334155;
    }

    ul, ol {
      margin-left: 20px;
      margin-bottom: 12px;
      color: #334155;
    }

    li {
      margin-bottom: 4px;
    }

    strong {
      color: #0F172A;
      font-weight: 600;
    }

    code {
      font-family: "SF Mono", Consolas, Menlo, Monaco, monospace;
      font-size: 8.5pt;
      background: #F1F5F9;
      color: #0369A1;
      padding: 1px 5px;
      border-radius: 3px;
      border: 1px solid #E2E8F0;
    }

    pre {
      background: #0F172A;
      color: #F8FAFC;
      font-family: "SF Mono", Consolas, Menlo, Monaco, monospace;
      font-size: 8pt;
      line-height: 1.45;
      padding: 12px 14px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 10px 0 14px;
      page-break-inside: avoid;
    }

    pre code {
      background: transparent;
      color: #F8FAFC;
      border: none;
      padding: 0;
    }

    /* Tables */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 16px;
      font-size: 8.5pt;
      page-break-inside: avoid;
    }

    th {
      background: #F1F5F9;
      color: #0F172A;
      font-weight: 700;
      text-align: left;
      padding: 7px 10px;
      border: 1px solid #CBD5E1;
      font-size: 8pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    td {
      padding: 6px 10px;
      border: 1px solid #CBD5E1;
      color: #334155;
      vertical-align: top;
    }

    tr:nth-child(even) td {
      background: #F8FAFC;
    }

    /* Callouts */
    .callout {
      padding: 10px 14px;
      border-radius: 6px;
      margin: 12px 0;
      border-left: 3px solid;
      background: #F8FAFC;
      page-break-inside: avoid;
    }

    .callout-info {
      border-color: #0284C7;
      background: #F0F9FF;
    }

    .callout-title {
      font-weight: 700;
      font-size: 9pt;
      margin-bottom: 3px;
      color: #0369A1;
    }

    /* Pipeline diagram box */
    .diagram-box {
      background: #0B1120;
      color: #F8FAFC;
      border-radius: 8px;
      padding: 16px;
      margin: 14px 0;
      page-break-inside: avoid;
    }

    .diagram-step {
      display: inline-block;
      background: #1E293B;
      border: 1px solid #38BDF8;
      color: #38BDF8;
      border-radius: 4px;
      padding: 6px 10px;
      font-size: 8pt;
      font-weight: 700;
      text-align: center;
      margin: 4px 2px;
    }

    .diagram-arrow {
      color: #94A3B8;
      font-weight: bold;
      margin: 0 4px;
    }

    .page-break {
      page-break-after: always;
    }

    .footer-bar {
      margin-top: 30px;
      padding-top: 8px;
      border-top: 1px solid #E2E8F0;
      font-size: 7.5pt;
      color: #94A3B8;
      display: flex;
      justify-content: space-between;
    }
  </style>
</head>
<body>

  <!-- COVER PAGE -->
  <div class="cover-page">
    <div>
      <div class="cover-badge">Official Architecture Specification</div>
      <h1 class="cover-title">FreightIQ</h1>
      <div class="cover-subtitle">The Engineering Behind Logistics Data</div>
      <div class="cover-desc">
        A comprehensive production engineering reference, visual design system, 32-guide content curriculum, zero-credential developer tool suite, and safe deployment specification for <strong>rajvardhansinghrathore.in</strong>.
      </div>
    </div>

    <div class="cover-meta-grid">
      <div class="cover-meta-item">
        <div class="cover-meta-label">Domain &amp; Platform</div>
        <div class="cover-meta-value">https://rajvardhansinghrathore.in</div>
      </div>
      <div class="cover-meta-item">
        <div class="cover-meta-label">Author &amp; Architect</div>
        <div class="cover-meta-value">Rajvardhan Singh Rathore</div>
      </div>
      <div class="cover-meta-item">
        <div class="cover-meta-label">Technical Stack</div>
        <div class="cover-meta-value">Python 3.12 SSG &bull; HTML5 &bull; Vanilla JS &bull; Nginx</div>
      </div>
      <div class="cover-meta-item">
        <div class="cover-meta-label">Infrastructure</div>
        <div class="cover-meta-value">AWS Lightsail Ubuntu 22.04 &bull; Cloudflare Full SSL</div>
      </div>
      <div class="cover-meta-item">
        <div class="cover-meta-label">Curriculum Depth</div>
        <div class="cover-meta-value">32 Production Guides &bull; 4 Core Modules &bull; 5 Live Tools</div>
      </div>
      <div class="cover-meta-item">
        <div class="cover-meta-label">Quality Assurance</div>
        <div class="cover-meta-value">4,394 Links Audited &bull; 100% Pass (0 Errors)</div>
      </div>
    </div>
  </div>

  <!-- TABLE OF CONTENTS -->
  <h2>Table of Contents</h2>
  <table style="margin-bottom: 24px;">
    <tbody>
      <tr><td><strong>1. Executive Summary &amp; Strategic Positioning</strong></td><td>Purpose, brand concept, and educational data platform identity</td></tr>
      <tr><td><strong>2. End-to-End System Architecture</strong></td><td>Upstream telemetry, edge validation gates, Kafka streaming, and analytics storage</td></tr>
      <tr><td><strong>3. Visual Identity &amp; Design System</strong></td><td>Stripe/Linear dark-first aesthetic, typography, and responsive micro-interactions</td></tr>
      <tr><td><strong>4. The 32 Technical Knowledge Guides</strong></td><td>Module 1 (Data Quality), Module 2 (Shipment Data), Module 3 (Validation), Module 4 (Troubleshooting)</td></tr>
      <tr><td><strong>5. Interactive Developer Tools Suite</strong></td><td>SQL Playground, JSON Validator, Lifecycle Visualizer, Quality Explorer, Troubleshooting Simulator</td></tr>
      <tr><td><strong>6. Technical SEO &amp; Structured Data</strong></td><td>Semantic HTML5, Schema.org JSON-LD graphs, canonical URLs, XML sitemap</td></tr>
      <tr><td><strong>7. Build Pipeline &amp; Codebase Architecture</strong></td><td>Reproducible Python static site generator, asset compilation, and link verification</td></tr>
      <tr><td><strong>8. Infrastructure &amp; Deployment Guide</strong></td><td>AWS Lightsail Nginx virtual host, non-destructive WordPress backup, Cloudflare SSL Full</td></tr>
      <tr><td><strong>9. Verification &amp; Localhost Runbook</strong></td><td>Audit results, local server management, and production checklist</td></tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 1 -->
  <h1>1. Executive Summary &amp; Strategic Positioning</h1>
  <p>In modern multimodal supply chains, freight data originates from thousands of disparate sources: EDI 214 telecommunications, unversioned carrier REST webhooks, IoT container trackers, and telematics gateways. Unlike traditional e-commerce data platforms where database schemas are controlled internally, freight data engineering operates in an asynchronous ecosystem characterized by late-arriving telemetry, vendor schema drift, and conflicting carrier nomenclatures (e.g., FedEx <code>PU</code> vs UPS <code>P</code> vs EDI 214 <code>AT7_X6</code>).</p>
  
  <p><strong>FreightIQ</strong> was created as an engineering-grade educational platform and interactive developer suite to address these challenges. It is <strong>not</strong> a transportation company or freight broker offering freight shipping; it is a <strong>technical knowledge platform</strong> delivering production schemas, SQL assertion suites, state machine validation frameworks, and interactive in-browser developer tools.</p>

  <!-- SECTION 2 -->
  <h1>2. End-to-End System Architecture</h1>
  <div class="diagram-box">
    <div style="font-size: 8pt; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px; font-weight: 700;">Data Pipeline Topology</div>
    <div style="display: flex; align-items: center; flex-wrap: wrap;">
      <span class="diagram-step">Carrier APIs<br><small style="color: #94A3B8;">Webhooks / EDI 214</small></span>
      <span class="diagram-arrow">&rarr;</span>
      <span class="diagram-step">Ingestion Gateway<br><small style="color: #94A3B8;">HMAC &amp; Rate Limiter</small></span>
      <span class="diagram-arrow">&rarr;</span>
      <span class="diagram-step" style="border-color: #34D399; color: #34D399;">Validation Engine<br><small style="color: #94A3B8;">JSON Schema &amp; FSM</small></span>
      <span class="diagram-arrow">&rarr;</span>
      <span class="diagram-step">ETL Pipeline<br><small style="color: #94A3B8;">dbt &amp; PostGIS</small></span>
      <span class="diagram-arrow">&rarr;</span>
      <span class="diagram-step">Analytics Dashboard<br><small style="color: #94A3B8;">Real-Time Visibility</small></span>
    </div>
  </div>

  <p>The architecture enforces four discrete validation gates:</p>
  <ul>
    <li><strong>Gate 1 (API Edge):</strong> Fast syntactic checks (&lt; 20ms) rejecting malformed JSON, unauthenticated tokens, and missing critical routing keys.</li>
    <li><strong>Gate 2 (Streaming Engine):</strong> Semantic validation (&lt; 150ms) enforcing state machine transitions, event deduplication (SHA-256 fingerprinting), and physical cargo boundaries.</li>
    <li><strong>Gate 3 (Warehouse Loading):</strong> Relational integrity assertions (&lt; 5 mins) validating foreign keys, historical drift, and cross-system ledger balances in PostgreSQL.</li>
    <li><strong>Gate 4 (Analytical Reconciliation):</strong> Automated dbt source-to-target reconciliation jobs verifying row counts, weight sums, and billing ledgers.</li>
  </ul>

  <!-- SECTION 3 -->
  <h1>3. Visual Identity &amp; Design System</h1>
  <p>The design system is engineered to match the quality of premium developer tools (Stripe, Linear, Datadog):</p>
  <ul>
    <li><strong>Color Palette:</strong> Deep slate backgrounds (<code>#070B14</code>, <code>#0D1424</code>), 1px glassmorphic card borders (<code>rgba(255, 255, 255, 0.08)</code>), electric blue (<code>#38BDF8</code>) and cyan (<code>#06B6D4</code>) accents.</li>
    <li><strong>Status Colors:</strong> Emerald (<code>#10B981</code>) for passing validations, Amber (<code>#F59E0B</code>) for latency alerts, and Rose (<code>#F43F5E</code>) for schema violations.</li>
    <li><strong>Typography:</strong> Inter for headlines and navigation; JetBrains Mono for code blocks, JSON schemas, SQL queries, and tabular data.</li>
  </ul>

  <div class="page-break"></div>

  <!-- SECTION 4 -->
  <h1>4. The 32 Technical Knowledge Guides</h1>
  <p>FreightIQ features 32 comprehensive, production-tested articles across four modules:</p>

  <h2>Module 1 — Data Quality (7 Guides)</h2>
  <table>
    <thead><tr><th>Route / Slug</th><th>Title &amp; Focus Area</th><th>Primary Technical Pattern</th></tr></thead>
    <tbody>
      <tr><td><code>/data-quality</code></td><td>Logistics Data Quality Framework</td><td>Multi-tier validation mesh; DQS composite scoring</td></tr>
      <tr><td><code>/data-quality/dimensions</code></td><td>The 6 Dimensions of Freight Data Quality</td><td>Completeness, accuracy, consistency, timeliness, uniqueness, validity</td></tr>
      <tr><td><code>/data-quality/completeness</code></td><td>Shipment Data Completeness</td><td>Detecting hidden NULLs, empty strings, and Null Island GPS glitches</td></tr>
      <tr><td><code>/data-quality/accuracy</code></td><td>Logistics Data Accuracy &amp; Verification</td><td>SOLAS VGM tare/gross weight checks and GPS speed velocity filters</td></tr>
      <tr><td><code>/data-quality/consistency</code></td><td>Cross-Carrier Status Normalization</td><td>Mapping FedEx, UPS, DHL, and EDI 214 into a 7-state canonical FSM</td></tr>
      <tr><td><code>/data-quality/timeliness</code></td><td>Event Latency &amp; SLA Tracking</td><td>Measuring lag quantiles (p50, p95, p99) and handling late-arriving events</td></tr>
      <tr><td><code>/data-quality/uniqueness</code></td><td>Deduplication Strategies for Webhooks</td><td>SHA-256 event fingerprinting and Redis SETNX sliding window caches</td></tr>
    </tbody>
  </table>

  <h2>Module 2 — Shipment Data (7 Guides)</h2>
  <table>
    <thead><tr><th>Route / Slug</th><th>Title &amp; Focus Area</th><th>Primary Technical Pattern</th></tr></thead>
    <tbody>
      <tr><td><code>/shipment-data</code></td><td>Shipment Data Architecture</td><td>Relational entity models; monthly range partitioning on events</td></tr>
      <tr><td><code>/shipment-data/lifecycle</code></td><td>Multimodal Shipment Lifecycle</td><td>Finite State Machine (FSM) topology, transition matrix, exception loops</td></tr>
      <tr><td><code>/shipment-data/shipment-ids</code></td><td>Master Shipment Identifiers</td><td>UUIDv7 (RFC 9562) vs ULID; B-tree index clustering benchmarks</td></tr>
      <tr><td><code>/shipment-data/tracking-numbers</code></td><td>Carrier Tracking Numbers</td><td>Checksum algorithms: UPS 1Z Modulo-10, FedEx Mod-11/7, ISO 6346 BIC</td></tr>
      <tr><td><code>/shipment-data/status-events</code></td><td>Status Events &amp; EDI 214</td><td>Event-sourcing architectures; ANSI X12 AT7 segment parsing to JSON</td></tr>
      <tr><td><code>/shipment-data/delivery-dates</code></td><td>Delivery Dates (EDD &amp; ADD)</td><td>Timezone normalization (UTC to recipient local calendar) and OTD math</td></tr>
      <tr><td><code>/shipment-data/location-data</code></td><td>Geospatial Logistics &amp; PostGIS</td><td>UN/LOCODE, IATA, SPLC; PostGIS polygon geofencing (ST_Contains)</td></tr>
    </tbody>
  </table>

  <h2>Module 3 — Validation (8 Guides)</h2>
  <table>
    <thead><tr><th>Route / Slug</th><th>Title &amp; Focus Area</th><th>Primary Technical Pattern</th></tr></thead>
    <tbody>
      <tr><td><code>/validation</code></td><td>Data Validation Architecture</td><td>Automated testing gates from edge gateways to dbt warehouse tests</td></tr>
      <tr><td><code>/validation/sql-techniques</code></td><td>Advanced SQL Validation Techniques</td><td>Window functions; LEAD()/LAG() chronological monotonicity assertions</td></tr>
      <tr><td><code>/validation/null-validation-sql</code></td><td>NULL Value Validation in SQL</td><td>Three-valued logic hazards and conditional mandatory attributes</td></tr>
      <tr><td><code>/validation/duplicate-record-detection</code></td><td>Duplicate Record Detection</td><td>ROW_NUMBER() window deduplication and 60-second temporal self-joins</td></tr>
      <tr><td><code>/validation/data-type-validation</code></td><td>Data Type Enforcement in ETL</td><td>Postal code string preservation and NUMERIC(12,4) exact decimal billing</td></tr>
      <tr><td><code>/validation/range-boundary-validation</code></td><td>Range Boundary Validation</td><td>Equipment physics constraints, DDL CHECK constraints, GPS bounding boxes</td></tr>
      <tr><td><code>/validation/json-schema-validation</code></td><td>JSON Schema Webhook Validation</td><td>Draft-07 specification, ISO-8601 UTC regex, fastjsonschema Python engine</td></tr>
      <tr><td><code>/validation/api-validation</code></td><td>Carrier API Ingestion Validation</td><td>HMAC-SHA256 signature verification and exponential backoff with jitter</td></tr>
    </tbody>
  </table>

  <h2>Module 4 — Troubleshooting (9 Guides)</h2>
  <table>
    <thead><tr><th>Route / Slug</th><th>Title &amp; Focus Area</th><th>Primary Technical Pattern</th></tr></thead>
    <tbody>
      <tr><td><code>/troubleshooting</code></td><td>Pipeline Incident Response</td><td>Incident severity matrix (SEV-1 to SEV-3) and automated DLQ re-drive</td></tr>
      <tr><td><code>/troubleshooting/pipeline-quality</code></td><td>Continuous Pipeline Quality &amp; SLOs</td><td>Freshness and completeness SLIs; daily Z-score statistical drift detection</td></tr>
      <tr><td><code>/troubleshooting/etl-validation</code></td><td>Source-to-Target Reconciliation</td><td>Row count parity, MD5 concatenated hashes, temporal watermarks</td></tr>
      <tr><td><code>/troubleshooting/real-time-monitoring</code></td><td>Real-Time Freight Data Monitoring</td><td>OpenTelemetry distributed tracing and Prometheus custom metrics</td></tr>
      <tr><td><code>/troubleshooting/automated-testing</code></td><td>Automated Testing for Pipelines</td><td>Test pyramid, PyTest synthetic carrier fixtures, CI/CD GitHub Actions</td></tr>
      <tr><td><code>/troubleshooting/pipeline-data-mismatches</code></td><td>Pipeline Data Mismatches</td><td>Systematic diagnosis for reconciling orders, manifests, and invoices</td></tr>
      <tr><td><code>/troubleshooting/sql-errors</code></td><td>Common Freight SQL Errors</td><td>Fixing division by zero with NULLIF and eliminating Cartesian fan-outs</td></tr>
      <tr><td><code>/troubleshooting/api-errors</code></td><td>Carrier API Failures &amp; Retries</td><td>Python Circuit Breaker pattern and dead-letter queue routing</td></tr>
      <tr><td><code>/troubleshooting/database-constraint-errors</code></td><td>Database Constraint Violations</td><td>Resolving out-of-order foreign key paradox with master stub auto-healing</td></tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- SECTION 5 -->
  <h1>5. Interactive Developer Tools Suite</h1>
  <p>FreightIQ features five client-side interactive developer utilities executing safely in the browser:</p>

  <h3>5.1 SQL Validation Playground (<code>/tools/sql-playground</code>)</h3>
  <p>Preloaded with sample logistics tables (<code>shipments</code>, <code>tracking_events</code>). Provides 5 runnable validation queries: NULL audit, duplicate detection, weight boundary violations, chronological anomalies (delivery before creation), and orphan event detection. Features an in-memory SQL execution engine showing query runtime (ms) and interactive tabular output.</p>

  <h3>5.2 JSON Shipment Schema Validator (<code>/tools/json-validator</code>)</h3>
  <p>Validates inbound carrier payloads against the FreightIQ Logistics Webhook Draft-07 specification. Preloaded with valid FedEx Express and Maersk container payloads alongside corrupted payloads demonstrating exact JSONPath violation reporting.</p>

  <h3>5.3 Shipment Lifecycle Visualizer (<code>/tools/lifecycle-visualizer</code>)</h3>
  <p>Interactive Finite State Machine (FSM) simulating milestone event scans. Demonstrates Happy Path delivery, customs delays, and out-of-order anomalies (flagging an event stream where <code>DELIVERED</code> arrives prior to <code>PICKED_UP</code>).</p>

  <h3>5.4 Data Quality Explorer (<code>/tools/quality-explorer</code>)</h3>
  <p>Dynamic 6-dimension mathematical simulator. Sliders for daily stream volume (10k to 1M events) and defect percentage (0% to 25%) dynamically calculate composite Data Quality Scores (DQS), clean vs quarantined record counts, and dimensional breakdowns.</p>

  <h3>5.5 Pipeline Troubleshooting Simulator (<code>/tools/troubleshooting-simulator</code>)</h3>
  <p>Hands-on incident response simulation covering 6 real-world pipeline outages (missing IDs, duplicate webhooks, timestamp parse failure, schema drift, API 429 timeouts, foreign key constraint crash). Features diagnostic stack traces, root cause analysis, and runnable remediation patches.</p>

  <!-- SECTION 6 -->
  <h1>6. Technical SEO &amp; Structured Data Architecture</h1>
  <p>Every page is optimized for technical search intent without keyword stuffing:</p>
  <ul>
    <li><strong>Schema.org JSON-LD:</strong>
      <ul>
        <li><code>WebSite</code> &amp; <code>Organization</code> on the homepage.</li>
        <li><code>TechArticle</code>, <code>BreadcrumbList</code>, and <code>Person</code> (Rajvardhan Singh Rathore) on every article.</li>
        <li><code>WebApplication</code> on interactive developer tool pages.</li>
      </ul>
    </li>
    <li><strong>Canonical URLs:</strong> Strict self-referential canonical tags targeting <code>https://rajvardhansinghrathore.in/...</code>.</li>
    <li><strong>Social Sharing:</strong> Open Graph (<code>og:*</code>) and Twitter Cards with custom SVG social images.</li>
    <li><strong>Sitemap:</strong> Automated XML sitemap (<code>dist/sitemap.xml</code>) indexing all 39 canonical endpoints.</li>
    <li><strong>Robots.txt:</strong> Universal search engine crawl directives with sitemap pointer.</li>
  </ul>

  <!-- SECTION 7 -->
  <h1>7. Build Pipeline &amp; Codebase Architecture</h1>
  <pre><code>/freightiq/
├── dist/                     # Production-ready static output (71 HTML files, assets)
├── src/
│   ├── data/                 # Structured article specifications &amp; metadata
│   ├── styles/main.css       # Production CSS stylesheet
│   └── scripts/tools.js      # Interactive developer tools JS engine
├── scripts/
│   ├── build.py              # Static site compiler (reproducible build)
│   ├── sitemap.py            # XML sitemap generator
│   ├── validate_links.py     # QA link &amp; anchor integrity crawler
│   ├── serve.py              # Local development server with clean URLs
│   └── deploy.sh             # Production deployment automation script
└── nginx/
    └── freightiq.conf        # Production Nginx virtual host configuration</code></pre>

  <p>The build pipeline is completely reproducible using standard Python 3.12 without external pip dependencies:</p>
  <pre><code>python3 scripts/build.py
python3 scripts/sitemap.py
python3 scripts/validate_links.py</code></pre>

  <div class="page-break"></div>

  <!-- SECTION 8 -->
  <h1>8. Infrastructure, Cloudflare &amp; Safe Deployment Guide</h1>
  
  <h3>Server Environment</h3>
  <ul>
    <li><strong>Host:</strong> AWS Lightsail, Mumbai (Static IP: <code>35.154.89.200</code>)</li>
    <li><strong>Operating System:</strong> Ubuntu 22.04 LTS (1 GB RAM, 2 vCPUs, 40 GB SSD)</li>
    <li><strong>Web Server:</strong> Nginx with HTTP/2 and Gzip compression</li>
    <li><strong>DNS &amp; SSL:</strong> Cloudflare (SSL/TLS Full, proxy enabled) &bull; Let's Encrypt origin certificate</li>
  </ul>

  <h3>Non-Destructive WordPress Preservation Safeguards</h3>
  <ol>
    <li><strong>Automated Backup:</strong> Before modifying configuration, <code>scripts/deploy.sh</code> creates an archive of existing web directories:
      <pre><code>cp -r /var/www/html /var/backups/wordpress_migration_$(date +%Y%m%d_%H%M%S)</code></pre>
    </li>
    <li><strong>Dedicated Web Root:</strong> FreightIQ is deployed to an isolated directory: <code>/var/www/freightiq</code>.</li>
    <li><strong>Reversible Virtual Host:</strong> Installed as <code>/etc/nginx/sites-available/freightiq.conf</code>. WordPress files and database tables remain untouched.</li>
  </ol>

  <h3>Nginx Virtual Host Configuration Highlights</h3>
  <ul>
    <li><strong>Cloudflare Real-IP Restoration:</strong> Automatically restores original client IPs via <code>CF-Connecting-IP</code>.</li>
    <li><strong>Security Headers:</strong> HSTS (<code>max-age=31536000</code>), <code>X-Content-Type-Options: nosniff</code>, <code>X-Frame-Options: SAMEORIGIN</code>, and Content-Security-Policy.</li>
    <li><strong>Clean URL Rewrites:</strong> <code>try_files $uri $uri/ $uri.html /index.html =404;</code></li>
    <li><strong>Caching:</strong> 1-year immutable cache headers on CSS, JS, and image assets.</li>
  </ul>

  <h3>Deployment Commands</h3>
  <pre><code># 1. Sync compiled dist files to Lightsail server
rsync -avz --delete dist/ ubuntu@35.154.89.200:/tmp/freightiq_dist/

# 2. Execute automated deployment and Nginx reload
ssh ubuntu@35.154.89.200 'sudo bash -s' &lt; scripts/deploy.sh</code></pre>

  <!-- SECTION 9 -->
  <h1>9. Verification, Quality Assurance &amp; Runbook</h1>
  
  <h3>Automated Link &amp; Anchor Audit Results</h3>
  <p>The link crawler <code>scripts/validate_links.py</code> executed an exhaustive audit across the entire build:</p>
  <ul>
    <li><strong>HTML Pages Inspected:</strong> 71</li>
    <li><strong>Internal Links, Anchors &amp; Assets Checked:</strong> <strong>4,394</strong></li>
    <li><strong>Broken Links / Anchor Glitches:</strong> <strong>0 (100% Valid)</strong></li>
  </ul>

  <h3>Local Development Server</h3>
  <p>To preview the platform locally with clean URL rewriting:</p>
  <pre><code>cd /Users/rajvardhansinghrathore/.gemini/antigravity/scratch/freightiq
python3 scripts/serve.py</code></pre>
  <p>The website is accessible at <strong>http://localhost:8080</strong>.</p>

  <div class="footer-bar">
    <span>FreightIQ &bull; The Engineering Behind Logistics Data</span>
    <span>https://rajvardhansinghrathore.in</span>
    <span>Author: Rajvardhan Singh Rathore</span>
  </div>

</body>
</html>
"""

HTML_OUT.write_text(html_content, encoding="utf-8")
print(f"✓ Print-optimized HTML generated at: {HTML_OUT}")

# Render PDF using headless Chrome
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_OUT}",
    str(HTML_OUT)
]

print(f"Generating PDF using Google Chrome headless engine...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"🎉 PDF successfully generated at: {PDF_OUT}")
    print(f"   PDF File Size: {PDF_OUT.stat().st_size / 1024:.1f} KB")
else:
    print(f"❌ Error generating PDF: {res.stderr}")
    sys.exit(1)
