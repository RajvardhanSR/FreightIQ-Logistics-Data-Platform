"""
Module 1: Data Quality
Contains complete technical articles for Data Quality Hub and 6 core dimensions.
"""

ARTICLES = [
    {
        "slug": "data-quality",
        "url_path": "data-quality/index.html",
        "title": "Logistics Data Quality Framework & Architecture",
        "meta_title": "Logistics Data Quality Framework: Complete Engineering Guide | FreightIQ",
        "meta_desc": "Architectural framework for real-time logistics data quality. Learn how to design multi-tier validation gates across carrier webhooks, Kafka streams, and analytical warehouses.",
        "primary_keyword": "data quality dimensions in ETL",
        "category": "Data Quality",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In multimodal supply chains, freight data originates from thousands of disparate sources: EDI 214 transmissions, REST webhooks, IoT container trackers, and telematics gateways. This guide outlines an enterprise framework for continuous data quality validation.",
        "toc": [
            {"id": "the-freight-data-challenge", "title": "The Logistics Data Defect Dilemma"},
            {"id": "multi-tier-architecture", "title": "Four-Tier Defense-in-Depth Architecture"},
            {"id": "the-six-dimensions", "title": "The 6 Dimensions in Freight Context"},
            {"id": "sql-quality-auditing", "title": "Automated SQL Quality Auditing"},
            {"id": "monitoring-and-slas", "title": "Operational SLAs and Data Contracts"},
            {"id": "next-steps", "title": "Implementation Roadmap & Next Steps"}
        ],
        "content_html": """
<section id="the-freight-data-challenge">
  <h2>The Logistics Data Defect Dilemma</h2>
  <p>Modern global logistics networks process millions of milestone updates daily. However, unlike traditional e-commerce transaction streams where schemas are controlled internally, freight data engineering operates in an adversarial data ecosystem characterized by:</p>
  <ul>
    <li><strong>Upstream Schema Drift:</strong> Third-party logistics (3PL) providers and ocean container lines alter JSON webhook payloads without versioning.</li>
    <li><strong>Asynchronous & Out-of-Sequence Telemetry:</strong> Cell-tower dead zones cause GPS pings and status milestones to arrive hours after delivery.</li>
    <li><strong>Carrier Discrepancy:</strong> FedEx, UPS, Maersk, and regional couriers utilize incompatible status nomenclatures (e.g., <code>PU</code> vs <code>PICKUP_COMPLETED</code> vs <code>A01</code>).</li>
  </ul>
  <p>A single unvalidated shipment record with an invalid gross weight or a corrupted timestamp cascades into failed customs clearances, billing disputes, and inaccurate ETA predictions.</p>
</section>

<section id="multi-tier-architecture">
  <h2>Four-Tier Defense-in-Depth Architecture</h2>
  <p>To eliminate dirty data before it pollutes reporting layers, a modern logistics data architecture enforces validation across four distinct layers:</p>
  
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Validation Layer</th>
          <th>Technology</th>
          <th>Latency Threshold</th>
          <th>Enforcement Action</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Layer 1: Gateway & Ingestion</strong></td>
          <td>JSON Schema / API Gateway</td>
          <td>&lt; 50 ms</td>
          <td>HTTP 400 rejection / Dead-Letter Queue (DLQ)</td>
        </tr>
        <tr>
          <td><strong>Layer 2: Stream Validation</strong></td>
          <td>Kafka Streams / Flink</td>
          <td>&lt; 200 ms</td>
          <td>Quarantine topic diversion, alerting webhook</td>
        </tr>
        <tr>
          <td><strong>Layer 3: Warehouse Staging</strong></td>
          <td>PostgreSQL / Snowflake / dbt</td>
          <td>1 - 5 mins</td>
          <td>Automated dbt test assertions, staging isolation</td>
        </tr>
        <tr>
          <td><strong>Layer 4: Analytical Reconciliation</strong></td>
          <td>Great Expectations / Soda Core</td>
          <td>Hourly batch</td>
          <td>Executive anomaly alerts, automated reconciliation</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section id="the-six-dimensions">
  <h2>The 6 Dimensions in Freight Context</h2>
  <p>Standard data quality dimensions must be translated into explicit logistics physical invariants:</p>
  <div class="callout callout-info">
    <div class="callout-title">Physical Invariant Principle</div>
    <p>In freight engineering, every digital record corresponds to a physical asset moving through space and time. Validation rules must model the laws of physics: container tare weights cannot be negative, and a vessel cannot travel from Singapore to Los Angeles in 4 hours.</p>
  </div>
  <ul>
    <li><strong>Completeness:</strong> All mandatory attributes (Waybill ID, Carrier SCAC, Origin UN/LOCODE, Destination Hub) must be non-null.</li>
    <li><strong>Accuracy:</strong> Geospatial coordinates must match geofenced hub boundaries; reported weights must match scale tickets.</li>
    <li><strong>Consistency:</strong> The sum of individual pallet weights must equal master manifest gross weight within ±0.5%.</li>
    <li><strong>Timeliness:</strong> Ingestion latency (<code>ingested_at - event_timestamp</code>) must not exceed 15 minutes for air/express or 4 hours for ocean linehaul.</li>
    <li><strong>Uniqueness:</strong> A unique composite key of <code>(carrier_code, tracking_number, event_timestamp, event_code)</code> must prevent double-counting.</li>
    <li><strong>Validity:</strong> Dates must adhere to ISO-8601 UTC; status codes must conform to the unified canonical state machine.</li>
  </ul>
</section>

<section id="sql-quality-auditing">
  <h2>Automated SQL Quality Auditing</h2>
  <p>The following production SQL assertion tests raw staging tables for composite defect indicators, computing an aggregated Data Quality Score (DQS):</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL / Snowflake SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>WITH audit_metrics AS (
  SELECT 
    COUNT(*) AS total_shipments,
    -- Completeness assertions
    COUNT(CASE WHEN tracking_number IS NULL OR tracking_number = '' THEN 1 END) AS missing_tracking_ids,
    COUNT(CASE WHEN destination_hub_code IS NULL THEN 1 END) AS missing_destination_hubs,
    
    -- Accuracy & Boundary assertions
    COUNT(CASE WHEN gross_weight_kg <= 0 OR gross_weight_kg > 25000 THEN 1 END) AS invalid_weight_anomalies,
    COUNT(CASE WHEN origin_lat NOT BETWEEN -90 AND 90 OR origin_lon NOT BETWEEN -180 AND 180 THEN 1 END) AS invalid_gps_coords,
    
    -- Timeliness assertions (events delayed > 24h)
    COUNT(CASE WHEN ingested_at - event_timestamp > INTERVAL '24 hours' THEN 1 END) AS delayed_telemetry_events,
    
    -- Chronological consistency assertions
    COUNT(CASE WHEN delivered_at IS NOT NULL AND delivered_at < picked_up_at THEN 1 END) AS delivery_before_pickup_anomalies
  FROM stg_carrier_shipments
  WHERE ingested_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
)
SELECT 
  total_shipments,
  ROUND((1.0 - (missing_tracking_ids + missing_destination_hubs)::numeric / NULLIF(total_shipments * 2, 0)) * 100, 2) AS completeness_score_pct,
  ROUND((1.0 - (invalid_weight_anomalies + invalid_gps_coords)::numeric / NULLIF(total_shipments * 2, 0)) * 100, 2) AS accuracy_score_pct,
  ROUND((1.0 - (delivery_before_pickup_anomalies)::numeric / NULLIF(total_shipments, 0)) * 100, 2) AS consistency_score_pct,
  ROUND((1.0 - (delayed_telemetry_events)::numeric / NULLIF(total_shipments, 0)) * 100, 2) AS timeliness_score_pct
FROM audit_metrics;</code></pre>
  </div>
</section>

<section id="monitoring-and-slas">
  <h2>Operational SLAs and Data Contracts</h2>
  <p>Production logistics teams should publish formal Data Contracts with carrier partners and internal platform teams. If a carrier's data defect rate exceeds 0.2% over a rolling 7-day period, automated webhooks notify vendor management for contract penalty review.</p>
</section>

<section id="next-steps">
  <h2>Implementation Roadmap & Next Steps</h2>
  <p>To implement this framework across your logistics pipeline, explore our deep-dive guides into each individual dimension:</p>
  <ul>
    <li><a href="/data-quality/dimensions">The 6 Dimensions of Freight Data Quality</a></li>
    <li><a href="/data-quality/completeness">Shipment Data Completeness: Detecting Missing Attributes</a></li>
    <li><a href="/validation/sql-techniques">Advanced SQL Validation Techniques for Logistics Data</a></li>
    <li><a href="/tools/sql-playground">Test your queries in the SQL Validation Playground</a></li>
  </ul>
</section>
        """
    },
    {
        "slug": "dimensions",
        "url_path": "data-quality/dimensions.html",
        "title": "The 6 Dimensions of Freight Data Quality",
        "meta_title": "The 6 Dimensions of Freight Data Quality Explained | FreightIQ",
        "meta_desc": "Explore the six dimensions of data quality applied specifically to supply chain and freight logistics: Completeness, Accuracy, Consistency, Timeliness, Uniqueness, Validity.",
        "primary_keyword": "freight data quality dimensions",
        "category": "Data Quality",
        "reading_time": "10 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "While general data quality frameworks define six abstract dimensions, logistics systems require concrete mathematical formulas and physical boundary rules. This guide operationalizes each dimension for transportation data pipelines.",
        "toc": [
            {"id": "dimensions-matrix", "title": "Logistics Data Quality Dimensions Matrix"},
            {"id": "dimension-completeness", "title": "1. Completeness"},
            {"id": "dimension-accuracy", "title": "2. Accuracy"},
            {"id": "dimension-consistency", "title": "3. Consistency"},
            {"id": "dimension-timeliness", "title": "4. Timeliness"},
            {"id": "dimension-uniqueness", "title": "5. Uniqueness"},
            {"id": "dimension-validity", "title": "6. Validity"},
            {"id": "composite-dqs", "title": "Computing the Composite Data Quality Score (DQS)"}
        ],
        "content_html": """
<section id="dimensions-matrix">
  <h2>Logistics Data Quality Dimensions Matrix</h2>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Dimension</th>
          <th>Freight Definition</th>
          <th>Failure Example</th>
          <th>Target SLA</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Completeness</strong></td>
          <td>Availability of all required shipment manifest fields</td>
          <td>Missing consignee postal code or carrier SCAC</td>
          <td>&gt; 99.8%</td>
        </tr>
        <tr>
          <td><strong>Accuracy</strong></td>
          <td>Degree to which digital record matches physical truth</td>
          <td>Recorded weight 150 kg, actual scale ticket 1500 kg</td>
          <td>&gt; 99.5%</td>
        </tr>
        <tr>
          <td><strong>Consistency</strong></td>
          <td>Harmony across multimodal status records and ERPs</td>
          <td>WMS says 'SHIPPED' but Carrier API returns 'UNKNOWN'</td>
          <td>&gt; 99.0%</td>
        </tr>
        <tr>
          <td><strong>Timeliness</strong></td>
          <td>Time elapsed between physical event and digital ingestion</td>
          <td>Delivery milestone ingested 36 hours post-handover</td>
          <td>&lt; 15 min lag</td>
        </tr>
        <tr>
          <td><strong>Uniqueness</strong></td>
          <td>Absence of duplicate event or billing entries</td>
          <td>Carrier webhook retries causing duplicate PU scans</td>
          <td>100.0%</td>
        </tr>
        <tr>
          <td><strong>Validity</strong></td>
          <td>Adherence to domain schemas, enums and regex standards</td>
          <td>Invalid ISO-8601 date '11/12/2026 2pm'</td>
          <td>&gt; 99.9%</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section id="dimension-completeness">
  <h2>1. Completeness</h2>
  <p>In freight ETL pipelines, completeness is measured as a field-level and record-level ratio:</p>
  <p>$$\text{Completeness Rate} = \frac{\sum_{i=1}^{N} \text{Non-Null Mandatory Attributes}}{N \times \text{Total Required Attributes}} \times 100$$</p>
  <p>Mandatory freight keys include <code>master_shipment_id</code>, <code>carrier_code</code>, <code>service_tier</code>, <code>origin_location_code</code>, and <code>destination_location_code</code>.</p>
</section>

<section id="dimension-accuracy">
  <h2>2. Accuracy</h2>
  <p>Accuracy verifies digital claims against physical ground truth. For example, geofencing coordinates from trailer GPS pings must fall within the polygon radius of the specified logistics terminal:</p>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostGIS SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>-- Assert event GPS is within 500 meters of reported terminal hub
SELECT 
  e.event_id,
  e.shipment_id,
  ST_Distance(
    ST_SetSRID(ST_MakePoint(e.longitude, e.latitude), 4326)::geography,
    h.geofence_center::geography
  ) AS distance_meters
FROM stg_tracking_events e
JOIN dim_logistics_hubs h ON e.reported_hub_code = h.hub_code
WHERE ST_Distance(
  ST_SetSRID(ST_MakePoint(e.longitude, e.latitude), 4326)::geography,
  h.geofence_center::geography
) > 500;</code></pre>
  </div>
</section>

<section id="dimension-consistency">
  <h2>3. Consistency</h2>
  <p>Ensures that multiple reporting systems tell the same story. In intermodal freight (rail + truck + ocean), state machines must progress monotonically without conflicting terminal statuses.</p>
</section>

<section id="dimension-timeliness">
  <h2>4. Timeliness</h2>
  <p>Calculates the ingestion latency quantile ($p_{95}, p_{99}$):</p>
  <p>$$\text{Latency} = t_{\text{ingested\_at}} - t_{\text{event\_occurred\_at}}$$</p>
  <p>Late-arriving facts corrupt dynamic routing algorithms and trigger erroneous customer SLA breach penalties.</p>
</section>

<section id="dimension-uniqueness">
  <h2>5. Uniqueness</h2>
  <p>Guarantees idempotency. Carrier HTTP webhook retries must never generate duplicate billing entries or double-counted delivery events in the enterprise data warehouse.</p>
</section>

<section id="dimension-validity">
  <h2>6. Validity</h2>
  <p>Strict schema syntax adherence: tracking numbers must pass standard carrier checksum algorithms (such as UPS Modulo-10 or ISO 6346 container check digits), and timestamps must follow ISO-8601 UTC format.</p>
</section>

<section id="composite-dqs">
  <h2>Computing the Composite Data Quality Score (DQS)</h2>
  <p>Enterprise logistics platforms combine the 6 dimensions into a weighted score:</p>
  <p>$$\text{DQS} = 0.25 C_{\text{comp}} + 0.25 A_{\text{acc}} + 0.15 K_{\text{cons}} + 0.15 T_{\text{time}} + 0.10 U_{\text{uniq}} + 0.10 V_{\text{valid}}$$</p>
  <p>Explore our interactive <a href="/tools/quality-explorer">Data Quality Explorer Tool</a> to simulate variations in these parameters.</p>
</section>
        """
    },
    {
        "slug": "completeness",
        "url_path": "data-quality/completeness.html",
        "title": "Shipment Data Completeness: Detecting Missing Attributes",
        "meta_title": "Shipment Data Completeness & NULL Auditing in Freight ETL | FreightIQ",
        "meta_desc": "How to detect, isolate, and remediate missing attributes in carrier tracking manifests, EDI 214s, and webhook payloads using SQL and automated validation gates.",
        "primary_keyword": "shipment data completeness validation",
        "category": "Data Quality",
        "reading_time": "9 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Incomplete freight data represents one of the primary drivers of warehouse processing delays and customs rejection. Learn the engineering patterns for detecting missing values and enforcing completeness contracts.",
        "toc": [
            {"id": "completeness-impact", "title": "The Operational Cost of Missing Data"},
            {"id": "identifying-hidden-nulls", "title": "Detecting 'Hidden' NULLs"},
            {"id": "sql-completeness-matrix", "title": "SQL Completeness Matrix Analysis"},
            {"id": "remediation-patterns", "title": "Automated Backfill & Fallback Pipelines"}
        ],
        "content_html": """
<section id="completeness-impact">
  <h2>The Operational Cost of Missing Data</h2>
  <p>When an air cargo manifest lacks a Harmonized Tariff Schedule (HTS) code or a parcel milestone lacks a destination postal code, downstream routing engines cannot allocate delivery sorters. In automated sorting facilities, incomplete records trigger exception lane diverts, degrading operational throughput by up to 18%.</p>
</section>

<section id="identifying-hidden-nulls">
  <h2>Detecting 'Hidden' NULLs</h2>
  <p>In carrier integrations, missing values frequently arrive disguised as non-null dummy strings:</p>
  <ul>
    <li>Empty string: <code>""</code></li>
    <li>Whitespace only: <code>"   "</code></li>
    <li>Default string tokens: <code>"NULL"</code>, <code>"N/A"</code>, <code>"UNKNOWN"</code>, <code>"00000"</code>, <code>"undefined"</code></li>
    <li>Zero coordinates: <code>lat: 0.0, lon: 0.0</code> (Null Island)</li>
  </ul>
  
  <div class="callout callout-warning">
    <div class="callout-title">The Null Island Trap</div>
    <p>GPS tracking units with uncalibrated satellite fixes often default to latitude 0.0, longitude 0.0 (off the coast of Ghana). Unless caught during cleaning, standard distance calculations will flag shipments as teleporting across the Atlantic Ocean.</p>
  </div>
</section>

<section id="sql-completeness-matrix">
  <h2>SQL Completeness Matrix Analysis</h2>
  <p>Use the following normalized NULL-scrubber pattern to assess completeness across all staging columns:</p>
  
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>SELECT 
  COUNT(*) AS total_rows,
  -- Check true nulls and hidden nulls
  ROUND(COUNT(CASE WHEN NULLIF(TRIM(carrier_code), '') IS NULL OR UPPER(TRIM(carrier_code)) IN ('N/A', 'UNKNOWN', 'NULL') THEN 1 END)::numeric / COUNT(*) * 100, 2) AS carrier_code_missing_pct,
  ROUND(COUNT(CASE WHEN NULLIF(TRIM(origin_postal_code), '') IS NULL OR origin_postal_code IN ('00000', '99999') THEN 1 END)::numeric / COUNT(*) * 100, 2) AS origin_postal_missing_pct,
  ROUND(COUNT(CASE WHEN NULLIF(TRIM(destination_postal_code), '') IS NULL THEN 1 END)::numeric / COUNT(*) * 100, 2) AS dest_postal_missing_pct,
  ROUND(COUNT(CASE WHEN (latitude = 0.0 AND longitude = 0.0) OR latitude IS NULL THEN 1 END)::numeric / COUNT(*) * 100, 2) AS gps_missing_pct
FROM raw_carrier_milestones
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';</code></pre>
  </div>
</section>

<section id="remediation-patterns">
  <h2>Automated Backfill & Fallback Pipelines</h2>
  <p>When missing fields are detected, production pipelines utilize a multi-level fallback cascade:</p>
  <ol>
    <li><strong>Reference Master Manifest:</strong> Look up destination details in the upstream shipper ERP Order table using <code>purchase_order_number</code>.</li>
    <li><strong>Carrier Master API Lookup:</strong> Asynchronously call the carrier tracking REST endpoint to retrieve official delivery coordinates.</li>
    <li><strong>Quarantine Staging:</strong> If critical routing keys cannot be resolved within 30 minutes, route to the Dead-Letter Queue (DLQ) for human operator review.</li>
  </ol>
</section>
        """
    },
    {
        "slug": "accuracy",
        "url_path": "data-quality/accuracy.html",
        "title": "Logistics Data Accuracy & Cross-System Verification",
        "meta_title": "Logistics Data Accuracy: Cross-System Verification & Auditing | FreightIQ",
        "meta_desc": "Architectural guide to verifying physical freight accuracy: gross vs tare weight validation, geospatial polygon containment, and rate sheet audit techniques.",
        "primary_keyword": "logistics data accuracy verification",
        "category": "Data Quality",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In freight data pipelines, accuracy measures how faithfully digital records reflect physical reality. Discover how to build cross-system verification pipelines that detect billing discrepancies and sensor calibration errors.",
        "toc": [
            {"id": "accuracy-vs-validity", "title": "Accuracy vs Validity: The Critical Difference"},
            {"id": "weight-physics-validation", "title": "Tare, Gross & Volumetric Weight Auditing"},
            {"id": "geospatial-verification", "title": "Geospatial Boundary & Speed Checks"},
            {"id": "financial-reconciliation", "title": "Carrier Invoice Rate Sheet Reconciliation"}
        ],
        "content_html": """
<section id="accuracy-vs-validity">
  <h2>Accuracy vs Validity: The Critical Difference</h2>
  <p>A data point can be completely valid in format yet totally inaccurate in substance. For example, a parcel weight recorded as <code>0.01 kg</code> is a perfectly valid positive float under JSON Schema rules, but physically inaccurate for a heavy machinery motor. Data accuracy requires semantic cross-referencing against real-world physical constraints.</p>
</section>

<section id="weight-physics-validation">
  <h2>Tare, Gross & Volumetric Weight Auditing</h2>
  <p>International freight depends on three interrelated weight measurements:</p>
  <ul>
    <li><strong>Tare Weight:</strong> Weight of the empty container or pallet.</li>
    <li><strong>Net Weight:</strong> Weight of the actual cargo goods inside.</li>
    <li><strong>Gross Weight:</strong> $\text{Gross} = \text{Tare} + \text{Net}$. Verified Gross Mass (VGM) is legally required by IMO SOLAS regulations.</li>
    <li><strong>Dimensional (Volumetric) Weight:</strong> Calculated as $\frac{L \times W \times H}{5000}$ (cm/kg standard IATA divisor).</li>
  </ul>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>-- SOLAS VGM Invariant Assertion: Gross must exceed Tare by at least Net weight
SELECT 
  container_id,
  booking_reference,
  tare_weight_kg,
  cargo_net_weight_kg,
  reported_gross_vgm_kg,
  ABS(reported_gross_vgm_kg - (tare_weight_kg + cargo_net_weight_kg)) AS discrepancy_kg
FROM container_manifests
WHERE ABS(reported_gross_vgm_kg - (tare_weight_kg + cargo_net_weight_kg)) > 50.0;</code></pre>
  </div>
</section>

<section id="geospatial-verification">
  <h2>Geospatial Boundary & Speed Checks</h2>
  <p>IoT telematics trackers frequently broadcast erroneous satellite coordinates caused by multipath interference in urban canyons. To detect false GPS points, pipelines execute sequential velocity assertions:</p>
  <p>$$\text{Speed} = \frac{\text{HaversineDistance}(p_1, p_2)}{\Delta t}$$</p>
  <p>If the calculated velocity between two pings exceeds 120 km/h for a freight truck or 950 km/h for air cargo, the ping is quarantined as GPS drift.</p>
</section>

<section id="financial-reconciliation">
  <h2>Carrier Invoice Rate Sheet Reconciliation</h2>
  <p>Freight audit and payment (FAP) engines continuously compare carrier invoiced amounts against contract rate cards. Any discrepancy greater than ±1.5% is automatically flagged for freight settlement review.</p>
</section>
        """
    },
    {
        "slug": "consistency",
        "url_path": "data-quality/consistency.html",
        "title": "Cross-Carrier Status Code Normalization & Consistency",
        "meta_title": "Cross-Carrier Freight Status Code Normalization Architecture | FreightIQ",
        "meta_desc": "How to design canonical logistics status abstraction layers. Normalize disparate FedEx, UPS, DHL, and EDI 214 event codes into a unified state machine.",
        "primary_keyword": "freight status consistency normalization",
        "category": "Data Quality",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Every carrier speaks a different language: EDI 214 uses X12 status reason codes, parcel carriers use custom strings, and ocean liners use DCSA standards. This guide details how to build a unified canonical translation layer.",
        "toc": [
            {"id": "the-carrier-babel-problem", "title": "The Heterogeneous Status Code Problem"},
            {"id": "canonical-state-model", "title": "The Canonical 7-State Unified Model"},
            {"id": "mapping-table-spec", "title": "Carrier-to-Canonical Crosswalk Table"},
            {"id": "handling-conflicting-milestones", "title": "Resolving Conflicting Carrier Timelines"}
        ],
        "content_html": """
<section id="the-carrier-babel-problem">
  <h2>The Heterogeneous Status Code Problem</h2>
  <p>When engineering global logistics control towers, integrating multiple carriers creates severe semantic consistency challenges:</p>
  <ul>
    <li><strong>FedEx:</strong> Emits codes like <code>PU</code> (Pickup), <code>DP</code> (Departed), <code>AR</code> (Arrived), <code>OD</code> (Out for Delivery), <code>DL</code> (Delivered).</li>
    <li><strong>UPS:</strong> Emits milestone types like <code>I</code> (In Transit), <code>X</code> (Exception), <code>D</code> (Delivered), <code>P</code> (Pickup).</li>
    <li><strong>EDI 214:</strong> Uses ANSI X12 AT7 segments with status reason codes like <code>AF</code> (Actual Departure), <code>AG</code> (Estimated Arrival), <code>X6</code> (En Route to Delivery).</li>
    <li><strong>DCSA (Ocean):</strong> Digital Container Shipping Association codes like <code>GTIN</code> (Gate In), <code>LOAD</code> (Loaded on Board), <code>DISC</code> (Discharged).</li>
  </ul>
</section>

<section id="canonical-state-model">
  <h2>The Canonical 7-State Unified Model</h2>
  <p>To provide predictable visibility to customers and downstream ERP systems, data platforms map all raw inbound milestones into a 7-stage canonical state machine:</p>
  <ol>
    <li><code>ORDER_CREATED</code>: Digital manifest or booking confirmed.</li>
    <li><code>PICKED_UP</code>: First physical carrier receipt scan.</li>
    <li><code>IN_TRANSIT</code>: Intermediate linehaul, sorting, or ocean transit.</li>
    <li><code>CUSTOMS_HOLD / EXCEPTION</code>: Regulatory or operational delay.</li>
    <li><code>OUT_FOR_DELIVERY</code>: Dispatched on last-mile courier or drayage truck.</li>
    <li><code>DELIVERED</code>: Final consignee signature captured.</li>
    <li><code>RETURNED_TO_SENDER</code>: Canceled or failed delivery loop.</li>
  </ol>
</section>

<section id="mapping-table-spec">
  <h2>Carrier-to-Canonical Crosswalk Table</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL DDL & Mapping Query</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>CREATE TABLE carrier_status_crosswalk (
  carrier_code VARCHAR(10) NOT NULL,
  raw_status_code VARCHAR(30) NOT NULL,
  raw_reason_code VARCHAR(30),
  canonical_status VARCHAR(30) NOT NULL,
  is_terminal_state BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (carrier_code, raw_status_code)
);

-- Sample Mapping Rules
INSERT INTO carrier_status_crosswalk VALUES
('FDX', 'OD', NULL, 'OUT_FOR_DELIVERY', FALSE),
('FDX', 'DL', NULL, 'DELIVERED', TRUE),
('UPS', 'D', NULL, 'DELIVERED', TRUE),
('UPS', 'X', 'ADDR_ERROR', 'EXCEPTION', FALSE),
('EDI214', 'AT7_X6', NULL, 'OUT_FOR_DELIVERY', FALSE),
('EDI214', 'AT7_D1', NULL, 'DELIVERED', TRUE);

-- Real-Time Status Transformation Query
SELECT 
  w.event_id,
  w.carrier_code,
  w.raw_status,
  COALESCE(c.canonical_status, 'UNKNOWN_STATUS_EXCEPTION') AS normalized_status,
  COALESCE(c.is_terminal_state, FALSE) AS is_terminal
FROM raw_carrier_webhooks w
LEFT JOIN carrier_status_crosswalk c 
  ON w.carrier_code = c.carrier_code 
 AND w.raw_status = c.raw_status_code;</code></pre>
  </div>
</section>

<section id="handling-conflicting-milestones">
  <h2>Resolving Conflicting Carrier Timelines</h2>
  <p>Occasionally, an upstream carrier will emit an earlier status after a later status (for example, receiving an <code>IN_TRANSIT</code> scan 2 hours after a <code>DELIVERED</code> scan). The canonical state engine enforces monotonicity: once a terminal state (<code>DELIVERED</code>) has been recorded, non-terminal updates are recorded as supplementary telemetry notes rather than reversing the master state.</p>
</section>
        """
    },
    {
        "slug": "timeliness",
        "url_path": "data-quality/timeliness.html",
        "title": "Event Latency, SLA Tracking & Shipment Data Timeliness",
        "meta_title": "Freight Data Timeliness: Ingestion Latency & SLA Tracking | FreightIQ",
        "meta_desc": "Measure and optimize telemetry latency in logistics streaming pipelines. Techniques for tracking late-arriving carrier events and real-time SLA metrics.",
        "primary_keyword": "shipment event latency timeliness",
        "category": "Data Quality",
        "reading_time": "10 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "A delivery notification that arrives 8 hours late is useless for last-mile exception handling. This technical guide examines how to measure, alert, and optimize event latency across streaming logistics pipelines.",
        "toc": [
            {"id": "anatomy-of-latency", "title": "Anatomy of Freight Telemetry Latency"},
            {"id": "measuring-ingestion-lag", "title": "Measuring Lag with Window Functions in SQL"},
            {"id": "handling-out-of-order-events", "title": "Handling Late-Arriving Events in Stream Processors"},
            {"id": "sla-alerting-architecture", "title": "Prometheus & Grafana SLA Alerting Architecture"}
        ],
        "content_html": """
<section id="anatomy-of-latency">
  <h2>Anatomy of Freight Telemetry Latency</h2>
  <p>The total latency of a shipment event comprises three distinct sequential stages:</p>
  <ul>
    <li><strong>Carrier Internal Lag ($L_1$):</strong> Time between physical driver barcode scan and the carrier's internal server recording the event.</li>
    <li><strong>Transmission Lag ($L_2$):</strong> Time taken by the carrier's webhook or EDI dispatcher to send the message over HTTP/AS2.</li>
    <li><strong>Ingestion & Processing Lag ($L_3$):</strong> Time between HTTP gateway receipt, Kafka queuing, and database warehouse commit.</li>
  </ul>
  <p>$$\text{Total Latency} = L_1 + L_2 + L_3 = t_{\text{warehouse\_commit}} - t_{\text{physical\_scan}}$$</p>
</section>

<section id="measuring-ingestion-lag">
  <h2>Measuring Lag with Window Functions in SQL</h2>
  <p>To diagnose which carrier integrations are degrading SLA benchmarks, run percentile distribution queries:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>SELECT 
  carrier_code,
  COUNT(*) AS total_events,
  ROUND(AVG(EXTRACT(EPOCH FROM (ingested_at - event_timestamp)) / 60)::numeric, 1) AS avg_lag_minutes,
  ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (ingested_at - event_timestamp)) / 60)::numeric, 1) AS p50_lag_minutes,
  ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (ingested_at - event_timestamp)) / 60)::numeric, 1) AS p95_lag_minutes,
  ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (ingested_at - event_timestamp)) / 60)::numeric, 1) AS p99_lag_minutes
FROM stg_tracking_milestones
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY carrier_code
ORDER BY p95_lag_minutes DESC;</code></pre>
  </div>
</section>

<section id="handling-out-of-order-events">
  <h2>Handling Late-Arriving Events in Stream Processors</h2>
  <p>In Apache Flink and Kafka Streams, handling out-of-order milestones requires configured watermarks. A watermark delay of 15 minutes allows 98% of late-arriving events to be joined into time-windowed aggregations without triggering state store bloat.</p>
</section>

<section id="sla-alerting-architecture">
  <h2>Prometheus & Grafana SLA Alerting Architecture</h2>
  <p>Expose custom Prometheus gauges measuring <code>logistics_carrier_lag_seconds{carrier="FDX"}</code>. Configure PagerDuty alerts if the 95th percentile exceeds 900 seconds over a rolling 15-minute sliding window.</p>
</section>
        """
    },
    {
        "slug": "uniqueness",
        "url_path": "data-quality/uniqueness.html",
        "title": "Deduplication Strategies for High-Velocity Freight Webhooks",
        "meta_title": "Freight Webhook Deduplication: Idempotency & SHA-256 Fingerprinting | FreightIQ",
        "meta_desc": "Architectural patterns for eliminating duplicate shipment events. Implement idempotency keys, sliding window deduplication in Redis, and PostgreSQL UPSERTs.",
        "primary_keyword": "freight webhook deduplication strategies",
        "category": "Data Quality",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Network retries and carrier poller overlaps routinely produce duplicate shipment milestone records. This guide covers how to design robust deduplication layers using SHA-256 event fingerprinting and database upsert patterns.",
        "toc": [
            {"id": "causes-of-duplicates", "title": "Why Duplicates Plague Logistics Pipelines"},
            {"id": "fingerprinting-strategy", "title": "Event Fingerprinting: SHA-256 Hashing"},
            {"id": "redis-sliding-window", "title": "Real-Time Deduplication via Redis SETNX"},
            {"id": "idempotent-database-upsert", "title": "Idempotent Database UPSERT Patterns"}
        ],
        "content_html": """
<section id="causes-of-duplicates">
  <h2>Why Duplicates Plague Logistics Pipelines</h2>
  <p>In high-throughput transportation networks, duplicate data events arise from three primary mechanisms:</p>
  <ul>
    <li><strong>Carrier Webhook At-Least-Once Delivery:</strong> Upstream API gateways that do not receive an immediate HTTP 200 within 2,000ms automatically retry the identical payload up to 5 times.</li>
    <li><strong>Redundant Driver Scanning:</strong> Couriers scanning a barcode multiple times at parcel handoff produce duplicate timestamped events.</li>
    <li><strong>Hybrid Polling & Webhooks:</strong> Systems that combine webhooks with periodic batch polling frequently ingest the same milestone twice.</li>
  </ul>
</section>

<section id="fingerprinting-strategy">
  <h2>Event Fingerprinting: SHA-256 Hashing</h2>
  <p>Because different carriers omit unique event IDs, pipeline engines compute a deterministic SHA-256 fingerprint hash based on the physical event tuple:</p>
  <p>$$\text{Fingerprint} = \text{SHA256}(\text{carrier} \mathbin{\Vert} \text{tracking\_num} \mathbin{\Vert} \text{status\_code} \mathbin{\Vert} \text{ISO\_timestamp} \mathbin{\Vert} \text{location\_code})$$</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python (Pydantic / Hashlib)</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>import hashlib

def compute_event_fingerprint(carrier_code: str, tracking_number: str, status_code: str, timestamp_iso: str, location_code: str) -> str:
    raw_key = f"{carrier_code.strip().upper()}|{tracking_number.strip()}|{status_code.strip()}|{timestamp_iso.strip()}|{location_code.strip()}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

# Example usage:
fp = compute_event_fingerprint("FDX", "794612345678", "OUT_FOR_DELIVERY", "2026-11-11T07:45:00Z", "MEM-HUB-01")
# Returns: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'</code></pre>
  </div>
</section>

<section id="redis-sliding-window">
  <h2>Real-Time Deduplication via Redis SETNX</h2>
  <p>At the edge ingestion API gateway, incoming events check their fingerprint against Redis with a 48-hour TTL:</p>
  <pre><code>SET event:fp:e3b0c44298fc1c149afbf4... 1 EX 172800 NX</code></pre>
  <p>If Redis returns <code>null</code>, the key already exists; the gateway returns HTTP 200 (acknowledging receipt) but drops the payload from Kafka publishing, saving downstream compute.</p>
</section>

<section id="idempotent-database-upsert">
  <h2>Idempotent Database UPSERT Patterns</h2>
  <p>In the data warehouse, tables enforce a unique constraint on the fingerprint, performing idempotent updates on conflict:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>CREATE TABLE shipment_status_events (
  event_fingerprint CHAR(64) PRIMARY KEY,
  carrier_code VARCHAR(10) NOT NULL,
  tracking_number VARCHAR(60) NOT NULL,
  status_code VARCHAR(30) NOT NULL,
  event_timestamp TIMESTAMPTZ NOT NULL,
  location_code VARCHAR(30),
  ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  duplicate_attempt_count INT DEFAULT 0
);

-- Idempotent Write
INSERT INTO shipment_status_events (
  event_fingerprint, carrier_code, tracking_number, status_code, event_timestamp, location_code
) VALUES (
  'e3b0c44298fc1c149afbf4...', 'FDX', '794612345678', 'OUT_FOR_DELIVERY', '2026-11-11 07:45:00+00', 'MEM-HUB-01'
)
ON CONFLICT (event_fingerprint) 
DO UPDATE SET 
  duplicate_attempt_count = shipment_status_events.duplicate_attempt_count + 1,
  ingested_at = CURRENT_TIMESTAMP;</code></pre>
  </div>
</section>
        """
    }
]
