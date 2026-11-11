"""
Module 4: Troubleshooting
Contains complete technical articles for Troubleshooting Hub and 8 core subtopics.
"""

ARTICLES = [
    {
        "slug": "troubleshooting",
        "url_path": "troubleshooting/index.html",
        "title": "Logistics Pipeline Troubleshooting & Incident Response",
        "meta_title": "Logistics Pipeline Troubleshooting & Incident Triage Guide | FreightIQ",
        "meta_desc": "Incident triage runbooks, root-cause analysis (RCA), and debugging playbooks for high-throughput supply chain and freight data pipelines.",
        "primary_keyword": "pipeline data mismatch troubleshooting",
        "category": "Troubleshooting",
        "reading_time": "14 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "When a carrier integration pipeline stalls during peak holiday freight surges, data engineering teams need clear diagnostic runbooks. This guide establishes a comprehensive incident response framework for logistics data platforms.",
        "toc": [
            {"id": "incident-severity-matrix", "title": "Logistics Data Incident Severity Matrix"},
            {"id": "five-step-triage-workflow", "title": "5-Step Pipeline Triage Framework"},
            {"id": "quarantine-drain-replay", "title": "Dead-Letter Queue Drain & Replay Playbook"},
            {"id": "post-mortem-template", "title": "Root Cause Analysis (RCA) Post-Mortem Standard"}
        ],
        "content_html": """
<section id="incident-severity-matrix">
  <h2>Logistics Data Incident Severity Matrix</h2>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Severity</th>
          <th>Definition</th>
          <th>SLA Response</th>
          <th>Example Incident</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><span style="color: var(--accent-rose); font-weight: 700;">SEV-1 (Critical)</span></td>
          <td>Complete pipeline halt or widespread data corruption affecting customs or billing.</td>
          <td>&lt; 15 mins</td>
          <td>All FedEx webhook ingests dropping due to unannounced API auth change.</td>
        </tr>
        <tr>
          <td><span style="color: var(--accent-amber); font-weight: 700;">SEV-2 (Major)</span></td>
          <td>High lag or localized data distortion in regional hub or secondary transport mode.</td>
          <td>&lt; 1 hour</td>
          <td>Kafka consumer lag exceeding 500,000 messages on ocean container topic.</td>
        </tr>
        <tr>
          <td><span style="color: var(--accent-blue); font-weight: 700;">SEV-3 (Moderate)</span></td>
          <td>Isolated schema drift or non-critical attribute null values.</td>
          <td>&lt; 4 hours</td>
          <td>Carrier missing driver truck plate IDs on LTL pickup events.</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section id="five-step-triage-workflow">
  <h2>5-Step Pipeline Triage Framework</h2>
  <ol>
    <li><strong>Isolate Ingestion Boundary:</strong> Verify whether the upstream carrier API is responding with HTTP 200, 429, or 504.</li>
    <li><strong>Inspect Kafka Lag & Buffers:</strong> Check partition lag on <code>telemetry-ingestion-v1</code> using Burrow or Prometheus metrics.</li>
    <li><strong>Check Dead-Letter Queue (DLQ):</strong> Sample payload headers in <code>dlq-carrier-events</code> to pinpoint parsing exception traces.</li>
    <li><strong>Apply Circuit Breaker:</strong> Pause faulty automated transformation workers to avoid cascading database locking.</li>
    <li><strong>Deploy Patch & Replay:</strong> Apply schema adapter patch and replay quarantined records back into staging.</li>
  </ol>
</section>

<section id="quarantine-drain-replay">
  <h2>Dead-Letter Queue Drain & Replay Playbook</h2>
  <p>Never discard records from the Dead-Letter Queue. Use an automated re-drive script to replay corrected events through the ingestion pipeline:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python DLQ Redrive Script</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>import json
from kafka import KafkaConsumer, KafkaProducer

dlq_consumer = KafkaConsumer('dlq-carrier-events', bootstrap_servers=['kafka:9092'], group_id='dlq-redrive-worker')
retry_producer = KafkaProducer(bootstrap_servers=['kafka:9092'])

for msg in dlq_consumer:
    payload = json.loads(msg.value.decode('utf-8'))
    # Apply schema translation or key normalization
    if 'carrier_reference' in payload and 'tracking_number' not in payload:
        payload['tracking_number'] = payload.pop('carrier_reference')
        
    # Re-publish to active ingestion topic
    retry_producer.send('active-shipment-events', json.dumps(payload).encode('utf-8'))</code></pre>
  </div>
</section>

<section id="post-mortem-template">
  <h2>Root Cause Analysis (RCA) Post-Mortem Standard</h2>
  <p>Simulate real-world incident triage scenarios in our interactive <a href="/tools/troubleshooting-simulator">Pipeline Troubleshooting Simulator</a>.</p>
</section>
        """
    },
    {
        "slug": "pipeline-quality",
        "url_path": "troubleshooting/pipeline-quality.html",
        "title": "Continuous Pipeline Quality: SLOs, SLIs & Data Drift",
        "meta_title": "Data Pipeline Quality: SLOs, SLIs & Schema Drift in Logistics | FreightIQ",
        "meta_desc": "Establish formal Service Level Indicators (SLIs) and Service Level Objectives (SLOs) for freight data freshness, completeness, and schema drift monitoring.",
        "primary_keyword": "data pipeline quality SLOs SLIs",
        "category": "Troubleshooting",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Treat your data pipeline like a production distributed application. Learn how to define concrete Service Level Objectives (SLOs) for freight data freshness and detect silent statistical data drift.",
        "toc": [
            {"id": "defining-freight-slis", "title": "Defining Logistics Data SLIs and SLOs"},
            {"id": "error-budgets-and-alerting", "title": "Error Budget Consumption & Alert Tiers"},
            {"id": "detecting-data-drift", "title": "Detecting Statistical Data Drift in SQL"},
            {"id": "automated-sla-dashboard", "title": "Building the Logistics SLI Dashboard"}
        ],
        "content_html": """
<section id="defining-freight-slis",
  <h2>Defining Logistics Data SLIs and SLOs</h2>
  <p>Modern data contracts require explicit mathematical SLIs:</p>
  <ul>
    <li><strong>Freshness SLI:</strong> Percentage of shipment events available in the warehouse within 5 minutes of physical scan ($99.5\%$ target).</li>
    <li><strong>Completeness SLI:</strong> Percentage of rows containing non-null carrier codes and tracking numbers ($99.9\%$ target).</li>
    <li><strong>Accuracy SLI:</strong> Percentage of GPS coordinates passing geofence containment ($99.0\%$ target).</li>
  </ul>
</section>

<section id="error-budgets-and-alerting">
  <h2>Error Budget Consumption & Alert Tiers</h2>
  <p>A $99.9\%$ monthly completeness SLO permits an error budget of 0.1% bad records. If a sudden surge consumes &gt; 20% of the 30-day error budget in a single hour, automated multi-window alerts fire to the on-call data reliability engineer.</p>
</section>

<section id="detecting-data-drift">
  <h2>Detecting Statistical Data Drift in SQL</h2>
  <p>Track distribution shifts in daily payload metrics (such as average parcel weight or status code frequency) using Z-score outlier detection:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Drift Detection SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>WITH daily_stats AS (
  SELECT 
    DATE(event_timestamp) AS event_date,
    COUNT(*) AS daily_volume,
    AVG(gross_weight_kg) AS avg_weight,
    STDDEV(gross_weight_kg) AS std_weight
  FROM fct_shipment_milestones
  GROUP BY DATE(event_timestamp)
),
historical_baseline AS (
  SELECT 
    AVG(daily_volume) AS mean_vol,
    STDDEV(daily_volume) AS std_vol
  FROM daily_stats
  WHERE event_date < CURRENT_DATE
)
SELECT 
  d.event_date,
  d.daily_volume,
  ROUND(((d.daily_volume - b.mean_vol) / NULLIF(b.std_vol, 0))::numeric, 2) AS volume_z_score,
  CASE 
    WHEN ABS((d.daily_volume - b.mean_vol) / NULLIF(b.std_vol, 0)) > 3.0 
    THEN 'ANOMALY: Severe Volume Drift'
    ELSE 'NORMAL'
  END AS drift_status
FROM daily_stats d
CROSS JOIN historical_baseline b
WHERE d.event_date = CURRENT_DATE;</code></pre>
  </div>
</section>

<section id="automated-sla-dashboard">
  <h2>Building the Logistics SLI Dashboard</h2>
  <p>Track live operational health across your carriers in our <a href="/tools/quality-explorer">Data Quality Explorer</a>.</p>
</section>
        """
    },
    {
        "slug": "etl-validation",
        "url_path": "troubleshooting/etl-validation.html",
        "title": "ETL Validation: Source-to-Target Reconciliation in Freight Warehouses",
        "meta_title": "ETL Source-to-Target Reconciliation in Freight Warehouses | FreightIQ",
        "meta_desc": "Architect automated source-to-target data reconciliation between streaming Kafka topics, staging lakes, and Snowflake/PostgreSQL warehouses.",
        "primary_keyword": "ETL source to target reconciliation",
        "category": "Troubleshooting",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "How do you guarantee that 10 million milestone events ingested into Kafka land accurately in Snowflake without loss, silent truncation, or duplication? This guide details automated source-to-target reconciliation pipelines.",
        "toc": [
            {"id": "reconciliation-layers", "title": "The Three Reconciliation Gates"},
            {"id": "hash-checksum-reconciliation", "title": "Row Hash Checksum Comparison"},
            {"id": "temporal-watermark-auditing", "title": "Temporal Watermark Row Count Parity"},
            {"id": "automated-reconciliation-job", "title": "Automated Python / SQL Reconciliation Runner"}
        ],
        "content_html": """
<section id="reconciliation-layers">
  <h2>The Three Reconciliation Gates</h2>
  <p>Source-to-target reconciliation verifies three key invariants:</p>
  <ul>
    <li><strong>Row Count Parity:</strong> Ingestion partition row count equals warehouse inserted row count.</li>
    <li><strong>Numerical Sum Parity:</strong> Sum of declared weights and invoice charges matches exactly between raw and gold layers.</li>
    <li><strong>Attribute Fidelity:</strong> Timestamps, codes, and IDs suffer zero unintended transformation shifts.</li>
  </ul>
</section>

<section id="hash-checksum-reconciliation">
  <h2>Row Hash Checksum Comparison</h2>
  <p>Compute MD5 or SHA-256 hashes of concatenated attributes across both source staging and final analytics tables:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Checksum Reconciliation</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>WITH source_hashes AS (
  SELECT 
    shipment_id,
    MD5(CONCAT_WS('|', shipment_id, carrier_scac, declared_weight_kg, current_status)) AS src_hash
  FROM stg_shipments
  WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
),
target_hashes AS (
  SELECT 
    shipment_id,
    MD5(CONCAT_WS('|', shipment_id, carrier_scac, declared_weight_kg, current_status)) AS tgt_hash
  FROM dim_shipments
  WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
)
SELECT 
  COALESCE(s.shipment_id, t.shipment_id) AS shipment_id,
  CASE 
    WHEN t.shipment_id IS NULL THEN 'MISSING_IN_TARGET_WAREHOUSE'
    WHEN s.shipment_id IS NULL THEN 'PHANTOM_RECORD_IN_TARGET'
    WHEN s.src_hash != t.tgt_hash THEN 'HASH_MISMATCH_DATA_DRIFT'
    ELSE 'MATCHED'
  END AS reconciliation_status
FROM source_hashes s
FULL OUTER JOIN target_hashes t ON s.shipment_id = t.shipment_id
WHERE s.src_hash IS DISTINCT FROM t.tgt_hash;</code></pre>
  </div>
</section>

<section id="temporal-watermark-auditing">
  <h2>Temporal Watermark Row Count Parity</h2>
  <p>By comparing Kafka high-watermark consumer offsets against database primary key sequences, pipelines detect lost batches before analytical dashboards generate executive reports.</p>
</section>

<section id="automated-reconciliation-job">
  <h2>Automated Python / SQL Reconciliation Runner</h2>
  <p>Discover how to integrate reconciliation tests into automated workflows in our <a href="/troubleshooting/automated-testing">Automated Testing Guide</a>.</p>
</section>
        """
    },
    {
        "slug": "real-time-monitoring",
        "url_path": "troubleshooting/real-time-monitoring.html",
        "title": "Real-Time Freight Data Monitoring with Prometheus & OpenTelemetry",
        "meta_title": "Real-Time Freight Data Monitoring with Prometheus & OTel | FreightIQ",
        "meta_desc": "Instrument logistics streaming microservices with Prometheus and OpenTelemetry. Track carrier webhook latency, dropped packets, and Kafka lag.",
        "primary_keyword": "real time logistics data monitoring",
        "category": "Troubleshooting",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In distributed logistics platforms, tracking a shipment requires tracing requests across 10+ microservices and third-party APIs. Discover how to instrument real-time telemetry with OpenTelemetry and Prometheus.",
        "toc": [
            {"id": "opentelemetry-logistics-spans", "title": "OpenTelemetry Distributed Tracing Spans"},
            {"id": "prometheus-custom-metrics", "title": "Prometheus Custom Metrics Instrumentation"},
            {"id": "grafana-dashboard-architecture", "title": "Operational Grafana Dashboard Design"},
            {"id": "alertmanager-pagerduty-routing", "title": "Alertmanager PagerDuty Routing Rules"}
        ],
        "content_html": """
<section id="opentelemetry-logistics-spans">
  <h2>OpenTelemetry Distributed Tracing Spans</h2>
  <p>When a carrier sends an HTTP webhook milestone, generate an OpenTelemetry distributed trace containing context tags:</p>
  <ul>
    <li><code>carrier.scac</code>: e.g. <code>FDX</code>, <code>UPS</code></li>
    <li><code>logistics.tracking_number</code>: Serialized tracking identifier</li>
    <li><code>transport.milestone_state</code>: e.g. <code>OUT_FOR_DELIVERY</code></li>
  </ul>
</section>

<section id="prometheus-custom-metrics">
  <h2>Prometheus Custom Metrics Instrumentation</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python Prometheus Client</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>from prometheus_client import Counter, Histogram

WEBHOOK_INCOMING_TOTAL = Counter(
    'freight_webhook_incoming_total',
    'Total inbound carrier webhooks received',
    ['carrier_code', 'http_status']
)

WEBHOOK_PROCESSING_LATENCY = Histogram(
    'freight_webhook_latency_seconds',
    'Latency of carrier webhook validation and Kafka publish',
    ['carrier_code'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# In HTTP Request handler:
with WEBHOOK_PROCESSING_LATENCY.labels(carrier_code="FDX").time():
    # Process validation logic
    WEBHOOK_INCOMING_TOTAL.labels(carrier_code="FDX", http_status="200").inc()</code></pre>
  </div>
</section>

<section id="grafana-dashboard-architecture">
  <h2>Operational Grafana Dashboard Design</h2>
  <p>A mission-critical logistics dashboard must prominently feature: carrier throughput rates (req/sec), Kafka consumer lag by partition, p99 validation latency, and DLQ drop rate.</p>
</section>

<section id="alertmanager-pagerduty-routing">
  <h2>Alertmanager PagerDuty Routing Rules</h2>
  <p>Route high-priority alerts directly to the logistics platform on-call rotation when error rates exceed $0.5\%$ over 5 consecutive minutes.</p>
</section>
        """
    },
    {
        "slug": "automated-testing",
        "url_path": "troubleshooting/automated-testing.html",
        "title": "Automated Testing for Freight Data Pipelines: Unit, Integration & Regression",
        "meta_title": "Automated Testing for Freight Data Pipelines: Unit & Integration | FreightIQ",
        "meta_desc": "Comprehensive guide to testing logistics pipelines. Synthetic carrier payload generation, mock EDI 214s, PyTest fixtures, and dbt test suites.",
        "primary_keyword": "automated testing logistics pipelines",
        "category": "Troubleshooting",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Don't let real customers discover data pipeline defects in production. Build a comprehensive automated test pyramid encompassing unit tests, synthetic carrier fixtures, and end-to-end integration assertions.",
        "toc": [
            {"id": "test-pyramid-for-data", "title": "The Data Engineering Test Pyramid"},
            {"id": "synthetic-carrier-fixtures", "title": "Generating Synthetic Carrier Payloads with PyTest"},
            {"id": "ci-cd-github-actions", "title": "CI/CD Pipeline Integration with GitHub Actions"},
            {"id": "regression-testing-data-diffs", "title": "Regression Testing via Data Diffs"}
        ],
        "content_html": """
<section id="test-pyramid-for-data">
  <h2>The Data Engineering Test Pyramid</h2>
  <p>Robust logistics testing requires three distinct layers:</p>
  <ul>
    <li><strong>Unit Tests (Fast, Local):</strong> Test individual functions: checksum calculations, postal code sanitization, timestamp parsing, regex checks.</li>
    <li><strong>Integration Tests (Docker / Testcontainers):</strong> Test interactions: Kafka consumer committing to PostgreSQL staging tables under schema constraints.</li>
    <li><strong>Data Warehouse Assertions (dbt / SQL):</strong> Test full table distributions: uniqueness, referential integrity, range boundaries.</li>
  </ul>
</section>

<section id="synthetic-carrier-fixtures">
  <h2>Generating Synthetic Carrier Payloads with PyTest</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PyTest Fixture Code</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>import pytest
from datetime import datetime, timezone

@pytest.fixture
def valid_fedex_payload():
    return {
        "event_id": "evt_test_001",
        "carrier_code": "FDX",
        "tracking_number": "794612345678",
        "shipment": {
            "master_id": "SHP-TEST-001",
            "service_level": "PRIORITY_OVERNIGHT",
            "gross_weight_kg": 5.4,
            "pieces_count": 1
        },
        "milestone": {
            "status_code": "OUT_FOR_DELIVERY",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }

def test_payload_validation_passes(valid_fedex_payload):
    from schema_validator import validate_shipment_payload
    result = validate_shipment_payload(valid_fedex_payload)
    assert result.is_valid is True
    assert len(result.errors) == 0</code></pre>
  </div>
</section>

<section id="ci-cd-github-actions">
  <h2>CI/CD Pipeline Integration with GitHub Actions</h2>
  <p>Run unit tests and dbt compile checks automatically on every pull request to protect the main production branch.</p>
</section>

<section id="regression-testing-data-diffs">
  <h2>Regression Testing via Data Diffs</h2>
  <p>Before deploying schema or transformation updates, run data-diff against a shadow replica database to verify that no historical reports alter their values.</p>
</section>
        """
    },
    {
        "slug": "pipeline-data-mismatches",
        "url_path": "troubleshooting/pipeline-data-mismatches.html",
        "title": "Troubleshooting Pipeline Data Mismatches: Reconciliation & Drift",
        "meta_title": "Troubleshooting Logistics Pipeline Data Mismatches | FreightIQ",
        "meta_desc": "Step-by-step diagnostic workflows for locating and resolving discrepancy between freight billing ledgers, manifest records, and carrier invoice amounts.",
        "primary_keyword": "pipeline data mismatch troubleshooting",
        "category": "Troubleshooting",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "When financial billing dashboards disagree with operational warehouse reports, supply chain operations stall. Learn how to systematically diagnose, isolate, and remediate data pipeline mismatches.",
        "toc": [
            {"id": "anatomy-of-a-mismatch", "title": "Anatomy of a Freight Data Discrepancy"},
            {"id": "four-step-isolation-method", "title": "The 4-Step Discrepancy Isolation Method"},
            {"id": "reconciliation-diagnostic-query", "title": "Diagnostic Reconciliation SQL Script"},
            {"id": "preventative-architecture", "title": "Preventative Architecture: Immutable Audit Logs"}
        ],
        "content_html": """
<section id="anatomy-of-a-mismatch">
  <h2>Anatomy of a Freight Data Discrepancy</h2>
  <p>Data discrepancies in logistics architectures typically stem from one of three flaws:</p>
  <ul>
    <li><strong>Late-Arriving Accessorial Charges:</strong> Carrier invoices include detention, fuel surcharge, or liftgate fees received weeks after delivery.</li>
    <li><strong>Timezone Normalization Disconnect:</strong> Billing runs on Eastern Time (US/Eastern) while warehouse scans are recorded in UTC, shifting cutoffs.</li>
    <li><strong>Dimensional Re-Weigh Discrepancy:</strong> Carrier high-speed sorting scales re-weigh packages and invoice based on dimensional weight rather than declared weight.</li>
  </ul>
</section>

<section id="four-step-isolation-method">
  <h2>The 4-Step Discrepancy Isolation Method</h2>
  <ol>
    <li>Identify the discrepancy boundary: Compare row counts and numerical sums at daily intervals.</li>
    <li>Isolate affected carrier partitions: Determine if the defect is systemic or confined to a specific carrier SCAC.</li>
    <li>Inspect raw audit payloads: Verify if the raw carrier JSON or EDI file matched the transformed warehouse values.</li>
    <li>Deploy targeted backfill: Apply idempotent update script across affected shipment partitions.</li>
  </ol>
</section>

<section id="reconciliation-diagnostic-query">
  <h2>Diagnostic Reconciliation SQL Script</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Discrepancy Audit SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>SELECT 
  o.shipment_id,
  o.declared_charge_usd AS erp_expected_charge,
  i.invoiced_charge_usd AS carrier_invoiced_charge,
  (i.invoiced_charge_usd - o.declared_charge_usd) AS variance_usd,
  ROUND(((i.invoiced_charge_usd - o.declared_charge_usd) / NULLIF(o.declared_charge_usd, 0) * 100)::numeric, 2) AS variance_pct,
  i.carrier_accessorial_notes
FROM erp_shipment_orders o
JOIN carrier_freight_invoices i ON o.tracking_number = i.tracking_number
WHERE ABS(i.invoiced_charge_usd - o.declared_charge_usd) > 5.00
ORDER BY variance_usd DESC;</code></pre>
  </div>
</section>

<section id="preventative-architecture">
  <h2>Preventative Architecture: Immutable Audit Logs</h2>
  <p>Discover real-world simulation of pipeline mismatches in our <a href="/tools/troubleshooting-simulator">Pipeline Troubleshooting Simulator</a>.</p>
</section>
        """
    },
    {
        "slug": "sql-errors",
        "url_path": "troubleshooting/sql-errors.html",
        "title": "Common SQL Errors in Freight Data Warehousing & How to Fix Them",
        "meta_title": "Fixing Common Freight SQL Warehouse Errors | FreightIQ",
        "meta_desc": "Diagnose and fix division by zero, timezone collation conflicts, CTE Cartesian products, and locking contention in high-volume logistics SQL databases.",
        "primary_keyword": "SQL data warehouse errors logistics",
        "category": "Troubleshooting",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "High-volume freight databases present unique SQL hurdles: massive event tables, concurrent UPSERT locks, and complex temporal aggregations. Here is the engineering guide to fixing the most common SQL runtime failures.",
        "toc": [
            {"id": "division-by-zero", "title": "1. Division by Zero in KPI Calculations"},
            {"id": "cartesian-product-fanouts", "title": "2. Cartesian Product Fan-Outs on Multimodal Joins"},
            {"id": "timezone-collation-errors", "title": "3. Timezone Operator & Collation Collisions"},
            {"id": "lock-contention-upsert", "title": "4. Deadlocks and Lock Contention during Concurrent UPSERTs"}
        ],
        "content_html": """
<section id="division-by-zero">
  <h2>1. Division by Zero in KPI Calculations</h2>
  <p>Calculating On-Time Delivery % or Exception Ratios crashes pipelines when a newly provisioned carrier has 0 delivered packages:</p>
  <pre><code>-- FAILS: division by zero error
SELECT on_time_count / total_count FROM carrier_stats;

-- FIXED: Use NULLIF to gracefully yield NULL
SELECT ROUND((on_time_count::numeric / NULLIF(total_count, 0)) * 100, 2) FROM carrier_stats;</code></pre>
</section>

<section id="cartesian-product-fanouts">
  <h2>2. Cartesian Product Fan-Outs on Multimodal Joins</h2>
  <p>Joining <code>master_shipments</code> to <code>shipment_milestone_events</code> without aggregating first causes metric inflation: an invoice amount of \$500 joined against 8 milestone scans calculates as \$4,000 total revenue!</p>
  <div class="callout callout-warning">
    <div class="callout-title">The Fan-Out Danger</div>
    <p>Always pre-aggregate one-to-many milestone events into a CTE before joining to commercial billing tables.</p>
  </div>
</section>

<section id="timezone-collation-errors">
  <h2>3. Timezone Operator & Collation Collisions</h2>
  <p>Comparing <code>TIMESTAMP WITHOUT TIME ZONE</code> to <code>TIMESTAMPTZ</code> causes PostgreSQL to perform implicit casts that bypass B-tree indexes, degrading query performance from 50ms to 45 seconds.</p>
</section>

<section id="lock-contention-upsert">
  <h2>4. Deadlocks and Lock Contention during Concurrent UPSERTs</h2>
  <p>When multiple Kafka consumer threads execute concurrent <code>INSERT ... ON CONFLICT DO UPDATE</code> on the same shipment row, deadlocks occur unless rows are sorted consistently by primary key before batch locking.</p>
</section>
        """
    },
    {
        "slug": "api-errors",
        "url_path": "troubleshooting/api-errors.html",
        "title": "Carrier API Failures: Timeouts, 429s, Webhook Drops & Retries",
        "meta_title": "Carrier API Failures: Timeouts, 429s & Retries | FreightIQ",
        "meta_desc": "Architectural guide to handling carrier API downtimes, HTTP 429 rate limits, 504 gateway timeouts, and dead-letter replay mechanisms.",
        "primary_keyword": "carrier API errors webhook retries",
        "category": "Troubleshooting",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "External carrier APIs are third-party systems outside your infrastructure control. When FedEx or UPS APIs experience degradations, your architecture must absorb failures gracefully without losing tracking events.",
        "toc": [
            {"id": "carrier-api-failure-modes", "title": "Common Carrier API Failure Modes"},
            {"id": "handling-429-rate-limits", "title": "Handling HTTP 429: Token Buckets & Jitter"},
            {"id": "circuit-breaker-pattern", "title": "The Circuit Breaker Pattern in Python"},
            {"id": "dead-letter-triage", "title": "DLQ Archival & Triage Workflows"}
        ],
        "content_html": """
<section id="carrier-api-failure-modes">
  <h2>Common Carrier API Failure Modes</h2>
  <ul>
    <li><strong>HTTP 429 Too Many Requests:</strong> Exceeded carrier rate quota during scheduled batch polling.</li>
    <li><strong>HTTP 504 Gateway Timeout:</strong> Carrier internal database degraded under peak seasonal parcel volume.</li>
    <li><strong>Silent Webhook Drops:</strong> Carrier failed to emit tracking updates for 6 hours due to unannounced network maintenance.</li>
  </ul>
</section>

<section id="handling-429-rate-limits">
  <h2>Handling HTTP 429: Token Buckets & Jitter</h2>
  <p>Respect carrier <code>Retry-After</code> response headers. If missing, employ exponential backoff with full randomized jitter to prevent synchronous retry thundering herds.</p>
</section>

<section id="circuit-breaker-pattern">
  <h2>The Circuit Breaker Pattern in Python</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python Circuit Breaker</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>import time

class CarrierCircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_state_change = time.time()

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            print("[ALERT] Carrier API Circuit Breaker tripped to OPEN!")

    def can_request(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_state_change > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN allows single canary probe</code></pre>
  </div>
</section>

<section id="dead-letter-triage">
  <h2>DLQ Archival & Triage Workflows</h2>
  <p>See our interactive simulation in the <a href="/tools/troubleshooting-simulator">Pipeline Troubleshooting Simulator</a>.</p>
</section>
        """
    },
    {
        "slug": "database-constraint-errors",
        "url_path": "troubleshooting/database-constraint-errors.html",
        "title": "Database Constraint Violations: Foreign Keys, Uniqueness & Deadlocks",
        "meta_title": "Database Constraint Violations in Logistics Pipelines | FreightIQ",
        "meta_desc": "How to resolve foreign key errors, uniqueness constraint violations, and upsert concurrency deadlocks in high-throughput freight relational databases.",
        "primary_keyword": "database constraint violation errors",
        "category": "Troubleshooting",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In event-driven freight architectures, milestone events frequently arrive before the parent shipment record has been written to the database. Learn how to engineer auto-healing foreign key and uniqueness constraint pipelines.",
        "toc": [
            {"id": "out-of-order-fk-paradox", "title": "The Out-of-Order Foreign Key Paradox"},
            {"id": "auto-provisioning-stubs", "title": "Auto-Provisioning Master Stubs (Auto-Healing Pattern)"},
            {"id": "idempotent-upsert-safety", "title": "Locking & Concurrency Safe UPSERTs"},
            {"id": "deferred-constraints-architecture", "title": "PostgreSQL DEFERRABLE Constraints"}
        ],
        "content_html": """
<section id="out-of-order-fk-paradox">
  <h2>The Out-of-Order Foreign Key Paradox</h2>
  <p>A customer places an order. Due to an upstream ERP sync delay, the shipment creation record is delayed by 10 minutes. Meanwhile, the driver at the dock immediately scans the barcode, generating a <code>PICKED_UP</code> milestone. The database rejects the milestone with:</p>
  <pre><code>ERROR: insert or update on table "shipment_milestones" violates foreign key constraint "fk_shipment"
Detail: Key (shipment_id)=(SHP-9921) is not present in table "master_shipments".</code></pre>
</section>

<section id="auto-provisioning-stubs">
  <h2>Auto-Provisioning Master Stubs (Auto-Healing Pattern)</h2>
  <p>Rather than failing the transaction, modern pipelines implement an auto-stubbing pattern: automatically insert a provisional placeholder row in <code>master_shipments</code> with status <code>PENDING_ENRICHMENT</code>, allowing the milestone to commit cleanly:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Auto-Healing SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>-- 1. Ensure master placeholder exists
INSERT INTO master_shipments (
  shipment_id, tracking_number, carrier_scac, current_status, is_provisional_stub
) VALUES (
  'SHP-9921', '794612345678', 'FDX', 'PENDING_ENRICHMENT', TRUE
)
ON CONFLICT (shipment_id) DO NOTHING;

-- 2. Insert milestone with guaranteed foreign-key integrity
INSERT INTO shipment_milestones (
  event_id, shipment_id, canonical_status, event_timestamp
) VALUES (
  'EVT-1001', 'SHP-9921', 'PICKED_UP', CURRENT_TIMESTAMP
);</code></pre>
  </div>
</section>

<section id="idempotent-upsert-safety">
  <h2>Locking & Concurrency Safe UPSERTs</h2>
  <p>When multiple asynchronous workers attempt to create or update the same master shipment, ensure that updates always update rather than throw duplicate key exceptions.</p>
</section>

<section id="deferred-constraints-architecture">
  <h2>PostgreSQL DEFERRABLE Constraints</h2>
  <p>Declare foreign keys as <code>DEFERRABLE INITIALLY DEFERRED</code> during large batch transactions so constraints are validated at transaction commit time rather than statement by statement.</p>
</section>
        """
    }
]
