"""
Module 3: Validation
Contains complete technical articles for Validation Hub and 7 core subtopics.
"""

ARTICLES = [
    {
        "slug": "validation",
        "url_path": "validation/index.html",
        "title": "Data Validation Architecture for Freight Pipelines",
        "meta_title": "Logistics Data Validation Architecture & Defense-in-Depth | FreightIQ",
        "meta_desc": "Architecting automated data validation gates for freight pipelines. Combine API JSON schema validation, Kafka streaming assertions, and dbt warehouse tests.",
        "primary_keyword": "SQL data validation techniques",
        "category": "Validation",
        "reading_time": "13 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In mission-critical transportation software, bad data costs real money. Learn how to construct an automated validation mesh across ingestion, streaming transformation, and analytical warehouse layers.",
        "toc": [
            {"id": "validation-mesh-topology", "title": "The Logistics Validation Mesh"},
            {"id": "gateway-schema-enforcement", "title": "Gate 1: Ingestion API Gateway Validation"},
            {"id": "stream-level-assertions", "title": "Gate 2: Streaming Transformation Assertions"},
            {"id": "warehouse-testing-framework", "title": "Gate 3: Warehouse & dbt Test Suites"},
            {"id": "dead-letter-architecture", "title": "Dead-Letter Queue (DLQ) & Quarantine Workflows"}
        ],
        "content_html": """
<section id="validation-mesh-topology">
  <h2>The Logistics Validation Mesh</h2>
  <p>Rather than relying solely on post-load batch SQL checks that discover errors hours after cargo has moved, modern data engineering enforces a defense-in-depth validation mesh:</p>
  <ul>
    <li><strong>Gate 1 (Edge Ingestion):</strong> Fast syntactic checks (&lt; 20ms) rejecting malformed JSON, unauthenticated tokens, and missing critical routing keys.</li>
    <li><strong>Gate 2 (Streaming Engine):</strong> Semantic validation (&lt; 150ms) enforcing state machine transitions, event deduplication, and physics constraints.</li>
    <li><strong>Gate 3 (Warehouse Loading):</strong> Relational integrity assertions (&lt; 5 mins) validating foreign keys, historical drift, and cross-system ledger balances.</li>
  </ul>
</section>

<section id="gateway-schema-enforcement">
  <h2>Gate 1: Ingestion API Gateway Validation</h2>
  <p>Incoming HTTP carrier webhooks must pass JSON Schema Draft-07 validation directly in the edge reverse proxy or serverless gateway before reaching Kafka. Malformed payloads are returned immediately with descriptive HTTP 400 Bad Request error envelopes.</p>
</section>

<section id="stream-level-assertions">
  <h2>Gate 2: Streaming Transformation Assertions</h2>
  <p>Apache Flink or Kafka Streams jobs evaluate business logic invariants. If an incoming milestone violates state progression (e.g. attempting to mark a shipment as <code>DELIVERED</code> when no <code>PICKED_UP</code> event exists), the event is diverted to a dead-letter quarantine topic.</p>
</section>

<section id="warehouse-testing-framework">
  <h2>Gate 3: Warehouse & dbt Test Suites</h2>
  <p>Continuous automated dbt assertions run on every transformation run:</p>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">dbt YAML Test Specification</span>
      <button class="copy-btn">Copy YAML</button>
    </div>
    <pre><code>version: 2

models:
  - name: fct_shipment_milestones
    columns:
      - name: milestone_id
        tests:
          - unique
          - not_null
      - name: gross_weight_kg
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0.01
              max_value: 25000.00
      - name: canonical_status
        tests:
          - accepted_values:
              values: ['ORDER_CREATED', 'PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED', 'EXCEPTION']</code></pre>
  </div>
</section>

<section id="dead-letter-architecture">
  <h2>Dead-Letter Queue (DLQ) & Quarantine Workflows</h2>
  <p>Quarantined records in the DLQ are enriched with error metadata, stack traces, and original raw payloads. Engineering teams can inspect, repair, and replay failed messages into the active pipeline using our <a href="/tools/troubleshooting-simulator">Pipeline Troubleshooting Simulator</a>.</p>
</section>
        """
    },
    {
        "slug": "sql-techniques",
        "url_path": "validation/sql-techniques.html",
        "title": "Advanced SQL Validation Techniques for Logistics Data",
        "meta_title": "Advanced SQL Validation Techniques for Logistics Data | FreightIQ",
        "meta_desc": "Master production SQL validation for freight data. Use window functions, CTE assertions, temporal lead/lag checks, and automated anomaly scans in PostgreSQL.",
        "primary_keyword": "SQL data validation techniques",
        "category": "Validation",
        "reading_time": "14 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "SQL remains the most expressive, performant engine for data validation in modern warehouses. This guide covers advanced PostgreSQL techniques: temporal sequence assertions, lead/lag anomaly checks, and automated discrepancy discovery.",
        "toc": [
            {"id": "temporal-lead-lag-checks", "title": "Temporal Invariants via LEAD() & LAG()"},
            {"id": "cumulative-window-weights", "title": "Cumulative Pallet Weight Integrity Audits"},
            {"id": "unmatched-reference-cte", "title": "Referential Cross-Checking with Assertive CTEs"},
            {"id": "automated-sql-test-runner", "title": "Building an Automated SQL Assertion Suite"}
        ],
        "content_html": """
<section id="temporal-lead-lag-checks">
  <h2>Temporal Invariants via LEAD() & LAG()</h2>
  <p>Physical packages must move forward in time. An event recorded at timestamp $t_n$ cannot have occurred prior to milestone $t_{n-1}$. Using PostgreSQL window functions, we detect chronological violations:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Window Function SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>WITH ordered_milestones AS (
  SELECT 
    shipment_id,
    event_id,
    canonical_status,
    event_timestamp,
    LAG(event_timestamp) OVER (
      PARTITION BY shipment_id 
      ORDER BY event_timestamp ASC
    ) AS prev_event_time,
    LAG(canonical_status) OVER (
      PARTITION BY shipment_id 
      ORDER BY event_timestamp ASC
    ) AS prev_status
  FROM fct_shipment_milestones
)
SELECT 
  shipment_id,
  event_id,
  canonical_status,
  event_timestamp,
  prev_status,
  prev_event_time,
  EXTRACT(EPOCH FROM (event_timestamp - prev_event_time)) AS delta_seconds
FROM ordered_milestones
WHERE event_timestamp < prev_event_time;</code></pre>
  </div>
</section>

<section id="cumulative-window-weights">
  <h2>Cumulative Pallet Weight Integrity Audits</h2>
  <p>In Less-Than-Truckload (LTL) linehauls, trailer capacity cannot exceed legal Department of Transportation (DOT) limits (typically 36,000 kg gross weight). Window functions compute rolling load weights across cross-dock transfers.</p>
</section>

<section id="unmatched-reference-cte">
  <h2>Referential Cross-Checking with Assertive CTEs</h2>
  <p>When tracking ocean container movements, container gate-out events must match corresponding vessel discharge manifests within the port operational window:</p>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL CTE Assertion</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>WITH gate_out_events AS (
  SELECT container_id, unlocode, event_timestamp AS gate_out_time
  FROM container_milestones
  WHERE status_code = 'GATE_OUT'
),
vessel_discharges AS (
  SELECT container_id, unlocode, event_timestamp AS discharge_time
  FROM container_milestones
  WHERE status_code = 'VESSEL_DISCHARGED'
)
SELECT 
  g.container_id,
  g.unlocode,
  g.gate_out_time,
  v.discharge_time,
  'Container gated out prior to vessel discharge' AS violation_reason
FROM gate_out_events g
JOIN vessel_discharges v ON g.container_id = v.container_id AND g.unlocode = v.unlocode
WHERE g.gate_out_time < v.discharge_time;</code></pre>
  </div>
</section>

<section id="automated-sql-test-runner">
  <h2>Building an Automated SQL Assertion Suite</h2>
  <p>Test your queries live against synthetic freight datasets in our interactive <a href="/tools/sql-playground">SQL Validation Playground</a>.</p>
</section>
        """
    },
    {
        "slug": "null-validation-sql",
        "url_path": "validation/null-validation-sql.html",
        "title": "NULL Value Validation in SQL: Mandatory Freight Attributes",
        "meta_title": "NULL Value Validation in SQL for Freight Databases | FreightIQ",
        "meta_desc": "Comprehensive SQL patterns for catching hidden NULLs, empty strings, and sentinel values in supply chain and logistics databases.",
        "primary_keyword": "NULL value validation SQL",
        "category": "Validation",
        "reading_time": "10 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In SQL, standard `IS NULL` assertions miss 60% of real-world missing data defects. Learn how to write bulletproof NULL validation queries that catch empty strings, whitespace, and carrier sentinel tokens.",
        "toc": [
            {"id": "the-sql-null-paradox", "title": "The SQL Three-Valued Logic Challenge"},
            {"id": "the-universal-null-predicate", "title": "The Universal Freight NULL Predicate"},
            {"id": "conditional-null-assertions", "title": "Conditional Mandatory Rules (CASE WHEN Validation)"},
            {"id": "production-null-audit-script", "title": "Production NULL Audit Query"}
        ],
        "content_html": """
<section id="the-sql-null-paradox">
  <h2>The SQL Three-Valued Logic Challenge</h2>
  <p>In ANSI SQL, <code>NULL</code> represents an unknown value, governed by three-valued logic (<code>TRUE</code>, <code>FALSE</code>, <code>UNKNOWN</code>). Expressions like <code>WHERE tracking_number != '1Z999'</code> evaluate to <code>UNKNOWN</code> for null rows and are silently discarded from results. Furthermore, carrier EDI integrations regularly send empty strings <code>''</code> or sentinel text tokens instead of genuine SQL NULLs.</p>
</section>

<section id="the-universal-null-predicate">
  <h2>The Universal Freight NULL Predicate</h2>
  <p>To catch all variations of missing data, establish a standardized SQL macro or expression:</p>
  <pre><code>-- Evaluates to TRUE whenever data is meaningfully missing
TRIM(COALESCE(column_val, '')) = '' 
OR UPPER(TRIM(column_val)) IN ('NULL', 'N/A', 'UNKNOWN', 'UNDEFINED', 'NONE')</code></pre>
</section>

<section id="conditional-null-assertions">
  <h2>Conditional Mandatory Rules (CASE WHEN Validation)</h2>
  <p>Certain freight attributes are mandatory only under specific conditions. For example, if <code>transport_mode = 'OCEAN_FCL'</code>, the <code>ocean_container_number</code> is mandatory; if <code>transport_mode = 'PARCEL'</code>, it should remain NULL:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>SELECT 
  shipment_id,
  transport_mode,
  carrier_scac,
  CASE 
    WHEN transport_mode IN ('OCEAN_FCL', 'OCEAN_LCL') AND NULLIF(TRIM(ocean_container_number), '') IS NULL 
      THEN 'FAILED: Missing mandatory ocean container number'
    WHEN transport_mode = 'AIR_FREIGHT' AND NULLIF(TRIM(air_waybill_number), '') IS NULL 
      THEN 'FAILED: Missing mandatory Master AWB'
    WHEN current_status = 'DELIVERED' AND actual_delivery_at IS NULL 
      THEN 'FAILED: Delivered status requires non-null actual_delivery_at'
    ELSE 'PASSED'
  END AS validation_result
FROM master_shipments
WHERE CASE 
    WHEN transport_mode IN ('OCEAN_FCL', 'OCEAN_LCL') AND NULLIF(TRIM(ocean_container_number), '') IS NULL THEN 1
    WHEN transport_mode = 'AIR_FREIGHT' AND NULLIF(TRIM(air_waybill_number), '') IS NULL THEN 1
    WHEN current_status = 'DELIVERED' AND actual_delivery_at IS NULL THEN 1
    ELSE 0
  END = 1;</code></pre>
  </div>
</section>

<section id="production-null-audit-script">
  <h2>Production NULL Audit Query</h2>
  <p>Schedule this query in your dbt orchestration pipeline to alert on completeness SLA breaches before morning dispatch shifts.</p>
</section>
        """
    },
    {
        "slug": "duplicate-record-detection",
        "url_path": "validation/duplicate-record-detection.html",
        "title": "Duplicate Record Detection: SQL Window Functions & Hash Matching",
        "meta_title": "Duplicate Record Detection in Freight SQL Pipelines | FreightIQ",
        "meta_desc": "Detect and deduplicate shipment records using ROW_NUMBER(), hash aggregations, and sliding temporal proximity in PostgreSQL and Snowflake.",
        "primary_keyword": "duplicate record detection SQL",
        "category": "Validation",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Duplicate records inflate delivery counts, distort carrier SLA reporting, and cause double-invoicing. This guide covers SQL techniques to pinpoint exact and fuzzy near-duplicate shipment records.",
        "toc": [
            {"id": "duplicate-taxonomy", "title": "Exact vs Near-Duplicate Shipments"},
            {"id": "row-number-deduplication", "title": "The ROW_NUMBER() Window Pattern"},
            {"id": "temporal-proximity-matching", "title": "Fuzzy Temporal Proximity Matching"},
            {"id": "automated-cleanup-script", "title": "Automated Staging Deduplication Query"}
        ],
        "content_html": """
<section id="duplicate-taxonomy">
  <h2>Exact vs Near-Duplicate Shipments</h2>
  <p>Logistics pipelines confront two varieties of duplicate records:</p>
  <ul>
    <li><strong>Exact Duplicates:</strong> Entire row identical across all columns due to network replay of HTTP webhooks.</li>
    <li><strong>Near-Duplicates:</strong> Same shipment and tracking number, but differing by minor timestamp fractions (e.g. 50ms apart) or slightly different carrier status text descriptions.</li>
  </ul>
</section>

<section id="row-number-deduplication">
  <h2>The ROW_NUMBER() Window Pattern</h2>
  <p>To eliminate duplicate events while preserving the most recent update, partition by the business key and order by ingestion time descending:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Deduplication CTE</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>WITH ranked_events AS (
  SELECT 
    event_id,
    shipment_id,
    carrier_scac,
    tracking_number,
    canonical_status,
    event_timestamp,
    ingested_at,
    ROW_NUMBER() OVER (
      PARTITION BY carrier_scac, tracking_number, canonical_status, event_timestamp
      ORDER BY ingested_at DESC
    ) AS row_num
  FROM raw_carrier_milestones
)
SELECT 
  event_id,
  shipment_id,
  carrier_scac,
  tracking_number,
  canonical_status,
  event_timestamp
FROM ranked_events
WHERE row_num = 1;</code></pre>
  </div>
</section>

<section id="temporal-proximity-matching">
  <h2>Fuzzy Temporal Proximity Matching</h2>
  <p>When driver hand-held scanners produce duplicate status pings within 60 seconds of each other, use temporal interval self-joins to collapse the duplicate events:</p>
  <pre><code>-- Find near-duplicate scans within 60-second window
SELECT 
  a.event_id AS primary_event_id,
  b.event_id AS duplicate_event_id,
  a.tracking_number,
  a.event_timestamp AS time_a,
  b.event_timestamp AS time_b
FROM shipment_milestone_events a
JOIN shipment_milestone_events b 
  ON a.tracking_number = b.tracking_number 
 AND a.canonical_status = b.canonical_status
 AND a.event_id &lt; b.event_id
 AND ABS(EXTRACT(EPOCH FROM (a.event_timestamp - b.event_timestamp))) &lt;= 60;</code></pre>
</section>

<section id="automated-cleanup-script">
  <h2>Automated Staging Deduplication Query</h2>
  <p>Explore this algorithm in action within our interactive <a href="/tools/sql-playground">SQL Validation Playground</a>.</p>
</section>
        """
    },
    {
        "slug": "data-type-validation",
        "url_path": "validation/data-type-validation.html",
        "title": "Data Type Enforcement & Schema Casting in Logistics ETL",
        "meta_title": "Data Type Enforcement & Schema Casting in Logistics ETL | FreightIQ",
        "meta_desc": "Prevent silent truncation, floating-point rounding errors in dimensional freight billing, and epoch timestamp parsing failures in logistics pipelines.",
        "primary_keyword": "ETL data type validation casting",
        "category": "Validation",
        "reading_time": "10 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Subtle type coercion bugs cause massive real-world problems: postal codes losing leading zeros, float rounding errors corrupting shipping rates, and epoch timestamp parsing failures. Learn how to engineer strict schema typing.",
        "toc": [
            {"id": "common-type-hazards", "title": "Top 4 Logistics Data Type Pitfalls"},
            {"id": "postal-code-string-typing", "title": "Postal Codes: Never Store as Integers"},
            {"id": "monetary-numeric-types", "title": "Freight Rates: NUMERIC vs FLOAT"},
            {"id": "safe-casting-functions", "title": "PostgreSQL Safe Casting & Regex Guards"}
        ],
        "content_html": """
<section id="common-type-hazards">
  <h2>Top 4 Logistics Data Type Pitfalls</h2>
  <p>Transportation data pipelines frequently suffer from four common schema mistakes:</p>
  <ol>
    <li><strong>Integer Postal Codes:</strong> Storing US ZIP codes or international postal codes as integers strips leading zeros (e.g., Boston <code>02108</code> becomes <code>2108</code>).</li>
    <li><strong>IEEE-754 Floats for Billing:</strong> Floating point numbers suffer from binary representation errors (e.g., $0.1 + 0.2 = 0.30000000000000004$), causing invoice ledger mismatches.</li>
    <li><strong>Millisecond vs Second Epochs:</strong> Ingesting a 13-digit Unix millisecond timestamp as a 10-digit second epoch shifts dates thousands of years into the future.</li>
    <li><strong>Implicit Varchar Truncation:</strong> Truncating long carrier reference strings without raising an exception.</li>
  </ol>
</section>

<section id="postal-code-string-typing">
  <h2>Postal Codes: Never Store as Integers</h2>
  <p>Always store postal codes as <code>VARCHAR(20)</code>. This preserves leading zeros and accommodates alphanumeric formats (e.g. UK <code>SW1A 1AA</code> or Canada <code>K1A 0B1</code>).</p>
</section>

<section id="monetary-numeric-types">
  <h2>Freight Rates: NUMERIC vs FLOAT</h2>
  <p>Always declare financial freight amounts, fuel surcharges, and customs duties using <code>NUMERIC(12, 4)</code> to guarantee exact decimal arithmetic.</p>
</section>

<section id="safe-casting-functions">
  <h2>PostgreSQL Safe Casting & Regex Guards</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Safe Casting SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>-- Safe Numeric Cast that returns NULL instead of raising exception
CREATE OR REPLACE FUNCTION safe_cast_numeric(val TEXT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN val::NUMERIC;
EXCEPTION WHEN OTHERS THEN
  RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Querying raw string columns safely
SELECT 
  raw_payload->>'tracking_number' AS tracking_number,
  safe_cast_numeric(raw_payload->>'gross_weight_kg') AS clean_weight_kg,
  CASE 
    WHEN safe_cast_numeric(raw_payload->>'gross_weight_kg') IS NULL 
    THEN 'REJECTED: Non-numeric gross weight value'
    ELSE 'ACCEPTED'
  END AS validation_audit
FROM raw_webhook_staging;</code></pre>
  </div>
</section>
        """
    },
    {
        "slug": "range-boundary-validation",
        "url_path": "validation/range-boundary-validation.html",
        "title": "Range Boundary Validation: Tare, Weight, Dimensions & GPS",
        "meta_title": "Logistics Range Boundary Validation: Weight, Cube & GPS | FreightIQ",
        "meta_desc": "Implement physics-based boundary constraints for LTL/FTL cargo weight, volumetric tare, and bounding-box latitude/longitude in PostgreSQL.",
        "primary_keyword": "range boundary validation data",
        "category": "Validation",
        "reading_time": "10 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Physical transport equipment is constrained by physical laws and legal highway weight limits. Discover how to build domain-aware range validation rules for freight weights, volumes, and GPS boundaries.",
        "toc": [
            {"id": "physical-boundary-rules", "title": "Physical Transport Equipment Limits"},
            {"id": "database-check-constraints", "title": "Database CHECK Constraints on DDL"},
            {"id": "gps-bounding-box-checks", "title": "GPS Coordinate Bounding Box Filtering"},
            {"id": "density-outlier-detection", "title": "Cargo Density Anomaly Detection"}
        ],
        "content_html": """
<section id="physical-boundary-rules">
  <h2>Physical Transport Equipment Limits</h2>
  <p>Transportation data validation rules should enforce physical and regulatory reality:</p>
  <ul>
    <li><strong>Standard Parcel:</strong> Weight between 0.05 kg and 70.0 kg; max length &le; 274 cm.</li>
    <li><strong>20ft ISO Shipping Container:</strong> Max gross mass = 30,480 kg; tare weight &approx; 2,200 kg.</li>
    <li><strong>40ft High Cube Container:</strong> Max gross mass = 32,500 kg; tare weight &approx; 3,800 kg.</li>
    <li><strong>Semi-Trailer Highway Limit:</strong> Max gross vehicle weight 36,287 kg (80,000 lbs US federal limit).</li>
  </ul>
</section>

<section id="database-check-constraints">
  <h2>Database CHECK Constraints on DDL</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL DDL CHECK Constraints</span>
      <button class="copy-btn">Copy DDL</button>
    </div>
    <pre><code>ALTER TABLE master_shipments
  ADD CONSTRAINT chk_weight_positive CHECK (declared_weight_kg > 0.01 AND declared_weight_kg <= 45000.00),
  ADD CONSTRAINT chk_packages_count CHECK (total_packages >= 1 AND total_packages <= 10000),
  ADD CONSTRAINT chk_valid_lat CHECK (origin_lat >= -90.0 AND origin_lat <= 90.0),
  ADD CONSTRAINT chk_valid_lon CHECK (origin_lon >= -180.0 AND origin_lon <= 180.0);</code></pre>
  </div>
</section>

<section id="gps-bounding-box-checks">
  <h2>GPS Coordinate Bounding Box Filtering</h2>
  <p>If a regional linehaul operates solely within continental North America, GPS coordinates falling outside the bounding box (Lat: 24.5&deg; to 49.4&deg;N, Lon: 66.9&deg; to 124.8&deg;W) are immediately isolated as sensor errors.</p>
</section>

<section id="density-outlier-detection">
  <h2>Cargo Density Anomaly Detection</h2>
  <p>Calculate cargo density ($\text{Density} = \frac{\text{Weight (kg)}}{\text{Volume} (m^3)}$). Liquid petroleum or iron ore has high density (~1000 - 7000 kg/m&sup3;); foam pillows have low density (~15 kg/m&sup3;). Records deviating from established commodity density ranges by &gt; 3 standard deviations are flagged for re-weigh inspection.</p>
</section>
        """
    },
    {
        "slug": "json-schema-validation",
        "url_path": "validation/json-schema-validation.html",
        "title": "JSON Schema Validation for Carrier Webhooks (Draft-07 & 2020-12)",
        "meta_title": "Carrier Webhook JSON Schema Validation (Draft-07 & 2020-12) | FreightIQ",
        "meta_desc": "Production-ready JSON Schema specifications for freight webhooks. Enforce mandatory keys, ISO-8601 timestamps, regex patterns, and numeric ranges.",
        "primary_keyword": "JSON schema validation shipment",
        "category": "Validation",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Carrier webhooks are notoriously erratic. By enforcing strict JSON Schema validation at the API edge, pipelines catch malformed payloads, unexpected data types, and missing identifiers before they enter the data lake.",
        "toc": [
            {"id": "draft07-vs-202012", "title": "JSON Schema Standards: Draft-07 vs 2020-12"},
            {"id": "production-shipment-schema", "title": "Production Carrier Webhook JSON Schema"},
            {"id": "edge-validation-implementation", "title": "Python & Node.js Edge Validation Code"},
            {"id": "testing-live-payloads", "title": "Interactive Validation in Browser"}
        ],
        "content_html": """
<section id="draft07-vs-202012">
  <h2>JSON Schema Standards: Draft-07 vs 2020-12</h2>
  <p>While Draft-07 remains the most universally supported schema format across legacy enterprise API gateways, Draft 2020-12 introduces powerful dynamic anchoring and vocabulary modules. For public logistics webhook endpoints, Draft-07 provides maximum library compatibility.</p>
</section>

<section id="production-shipment-schema">
  <h2>Production Carrier Webhook JSON Schema</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">JSON Schema (Draft-07)</span>
      <button class="copy-btn">Copy Schema</button>
    </div>
    <pre><code>{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CarrierShipmentWebhook",
  "type": "object",
  "required": ["event_id", "carrier_code", "tracking_number", "shipment", "milestone"],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_-]{8,64}$"
    },
    "carrier_code": {
      "type": "string",
      "enum": ["FDX", "UPS", "DHL", "MSK", "CMA", "USPS"]
    },
    "tracking_number": {
      "type": "string",
      "minLength": 8,
      "maxLength": 40
    },
    "shipment": {
      "type": "object",
      "required": ["master_id", "service_level", "gross_weight_kg"],
      "properties": {
        "master_id": { "type": "string" },
        "service_level": { "type": "string" },
        "gross_weight_kg": { "type": "number", "minimum": 0.01, "maximum": 50000.0 },
        "pieces_count": { "type": "integer", "minimum": 1 }
      }
    },
    "milestone": {
      "type": "object",
      "required": ["status_code", "timestamp"],
      "properties": {
        "status_code": {
          "type": "string",
          "enum": ["ORDER_CREATED", "PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION", "FAILED_ATTEMPT"]
        },
        "timestamp": {
          "type": "string",
          "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+-]\\d{2}:\\d{2})$"
        }
      }
    }
  }
}</code></pre>
  </div>
</section>

<section id="edge-validation-implementation">
  <h2>Python & Node.js Edge Validation Code</h2>
  <p>In Python, compile the schema with <code>fastjsonschema</code> or <code>jsonschema</code> for high-throughput sub-millisecond execution:</p>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python FastJSONSchema</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>import fastjsonschema

validate = fastjsonschema.compile(carrier_schema_dict)

def process_webhook(payload: dict):
    try:
        valid_data = validate(payload)
        return {"status": "accepted", "code": 200}
    except fastjsonschema.JsonSchemaException as e:
        return {"status": "rejected", "error": e.message, "path": e.path, "code": 400}</code></pre>
  </div>
</section>

<section id="testing-live-payloads">
  <h2>Interactive Validation in Browser</h2>
  <p>Paste your carrier webhook payloads directly into our <a href="/tools/json-validator">JSON Shipment Schema Validator Tool</a> to test schema compliance in real time.</p>
</section>
        """
    },
    {
        "slug": "api-validation",
        "url_path": "validation/api-validation.html",
        "title": "Carrier API Ingestion Validation: Idempotency, Rate Limits & Payloads",
        "meta_title": "Carrier API Ingestion Validation: Idempotency & Rate Limits | FreightIQ",
        "meta_desc": "Architect resilient carrier API ingestion pipelines. Handle HMAC webhook verification, exponential backoff with jitter for HTTP 429s, and idempotency.",
        "primary_keyword": "carrier API webhook payload validation",
        "category": "Validation",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Connecting directly to 50+ carrier APIs requires defending your ingestion infrastructure against webhook storms, rate-limit lockouts, and unauthenticated spoofed payloads. This guide provides production implementation patterns.",
        "toc": [
            {"id": "hmac-signature-verification", "title": "HMAC-SHA256 Webhook Security Verification"},
            {"id": "rate-limit-token-bucket", "title": "Carrier API Rate Limiting & Token Buckets"},
            {"id": "exponential-backoff-jitter", "title": "Exponential Backoff with Full Jitter"},
            {"id": "idempotency-key-caching", "title": "Idempotency Keys & Deduplication Caches"}
        ],
        "content_html": """
<section id="hmac-signature-verification">
  <h2>HMAC-SHA256 Webhook Security Verification</h2>
  <p>To prevent malicious spoofing of delivery confirmation milestones, carriers sign inbound webhook payloads with an HMAC-SHA256 signature transmitted in HTTP headers (e.g., <code>X-Carrier-Signature</code>). Gateways must verify this signature using timing-safe comparisons before parsing the body:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python HMAC Verification</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>import hmac, hashlib

def verify_carrier_webhook(raw_body_bytes: bytes, signature_header: str, secret_key: str) -> bool:
    computed = hmac.new(secret_key.encode("utf-8"), raw_body_bytes, hashlib.sha256).hexdigest()
    # Use compare_digest to prevent timing attack side-channels
    return hmac.compare_digest(computed, signature_header)</code></pre>
  </div>
</section>

<section id="rate-limit-token-bucket">
  <h2>Carrier API Rate Limiting & Token Buckets</h2>
  <p>When polling carrier tracking endpoints (FedEx Developer Portal, UPS OAuth API), clients are constrained by strict rate quotas (e.g., 50 requests/second). Implement a Redis-backed Token Bucket algorithm to smooth out batch spikes.</p>
</section>

<section id="exponential-backoff-jitter">
  <h2>Exponential Backoff with Full Jitter</h2>
  <p>When a carrier responds with HTTP 429 (Too Many Requests) or HTTP 503 (Service Unavailable), naïve retry loops cause "thundering herd" gateway crashes. Apply exponential backoff with full randomized jitter:</p>
  <p>$$t_{\text{sleep}} = \text{random}(0, \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}))$$</p>
</section>

<section id="idempotency-key-caching">
  <h2>Idempotency Keys & Deduplication Caches</h2>
  <p>Carrier requests must include an <code>Idempotency-Key</code> header. Discover real-world triage strategies in our <a href="/troubleshooting/api-errors">Carrier API Errors Troubleshooting Guide</a>.</p>
</section>
        """
    }
]
