"""
Module 2: Shipment Data
Contains complete technical articles for Shipment Data Hub and 6 core subtopics.
"""

ARTICLES = [
    {
        "slug": "shipment-data",
        "url_path": "shipment-data/index.html",
        "title": "Shipment Data Architecture: Entities, Relational Models & Schemas",
        "meta_title": "Shipment Data Architecture & Relational Schema Modeling | FreightIQ",
        "meta_desc": "Enterprise relational modeling for multimodal freight tracking. Complete entity-relationship diagram, PostgreSQL DDL schemas, and event-driven architectures.",
        "primary_keyword": "shipment tracking data schema",
        "category": "Shipment Data",
        "reading_time": "14 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Modeling freight data requires balancing high-frequency streaming events with immutable physical assets. This comprehensive guide outlines the entity relationships, PostgreSQL schemas, and indexing strategies for global freight platforms.",
        "toc": [
            {"id": "domain-entity-model", "title": "The Logistics Domain Entity Hierarchy"},
            {"id": "relational-ddl-schema", "title": "Production PostgreSQL DDL Specification"},
            {"id": "indexing-and-partitioning", "title": "Table Partitioning & High-Throughput Indexing"},
            {"id": "multimodal-handling", "title": "Multimodal vs Last-Mile Data Modeling"}
        ],
        "content_html": """
<section id="domain-entity-model">
  <h2>The Logistics Domain Entity Hierarchy</h2>
  <p>To accurately capture freight movements across ocean carriers, air waybills, customs brokers, and last-mile vans, data models must decouple the physical container or parcel from the commercial order:</p>
  <ul>
    <li><strong>Order (Commercial):</strong> The buyer/seller agreement with line items, purchase order numbers, and declared value.</li>
    <li><strong>Shipment (Logistical Master):</strong> The operational movement of goods between origin and destination under a master bill of lading (BOL).</li>
    <li><strong>Package / Unit / Container:</strong> The physical serialized vessel (pallet, 40ft dry container, parcel box).</li>
    <li><strong>Tracking Milestone / Status Event:</strong> The immutable point-in-time telemetry record capturing timestamp, location, and operational state.</li>
  </ul>
</section>

<section id="relational-ddl-schema">
  <h2>Production PostgreSQL DDL Specification</h2>
  <p>The following production schema implements foreign-key constraints, UUIDv7 primary keys, and JSONB payload metadata support:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL DDL</span>
      <button class="copy-btn">Copy DDL</button>
    </div>
    <pre><code>-- Master Shipments Table
CREATE TABLE master_shipments (
  shipment_id UUID PRIMARY KEY,
  shipper_account_id UUID NOT NULL,
  master_tracking_number VARCHAR(60) NOT NULL,
  carrier_scac VARCHAR(10) NOT NULL,
  transport_mode VARCHAR(20) NOT NULL CHECK (transport_mode IN ('PARCEL', 'LTL', 'FTL', 'OCEAN_FCL', 'OCEAN_LCL', 'AIR_FREIGHT')),
  current_status VARCHAR(30) NOT NULL DEFAULT 'ORDER_CREATED',
  
  -- Geographic Endpoints
  origin_unlocode CHAR(5),
  origin_postal_code VARCHAR(20),
  destination_unlocode CHAR(5),
  destination_postal_code VARCHAR(20) NOT NULL,
  
  -- Physical cargo constraints
  total_packages INT NOT NULL CHECK (total_packages >= 1),
  declared_weight_kg NUMERIC(10, 2) NOT NULL CHECK (declared_weight_kg > 0),
  volumetric_weight_kg NUMERIC(10, 2),
  
  -- Timestamps
  estimated_delivery_at TIMESTAMPTZ,
  actual_delivery_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Milestone Events (Immutable Telemetry Log)
CREATE TABLE shipment_milestone_events (
  event_id UUID PRIMARY KEY,
  shipment_id UUID NOT NULL REFERENCES master_shipments(shipment_id) ON DELETE CASCADE,
  carrier_event_code VARCHAR(30) NOT NULL,
  canonical_status VARCHAR(30) NOT NULL,
  event_timestamp TIMESTAMPTZ NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  -- Spatial data
  facility_code VARCHAR(30),
  location_name VARCHAR(100),
  latitude NUMERIC(9, 6),
  longitude NUMERIC(9, 6),
  
  -- Raw carrier audit payload
  raw_carrier_payload JSONB
);</code></pre>
  </div>
</section>

<section id="indexing-and-partitioning">
  <h2>Table Partitioning & High-Throughput Indexing</h2>
  <p>In high-scale logistics platforms processing &gt; 50 million events per month, <code>shipment_milestone_events</code> is range-partitioned by <code>event_timestamp</code> on a monthly cadence:</p>
  <pre><code>CREATE TABLE shipment_milestone_events (
  ...
) PARTITION BY RANGE (event_timestamp);

CREATE TABLE events_2026_11 PARTITION OF shipment_milestone_events
  FOR VALUES FROM ('2026-11-01 00:00:00+00') TO ('2026-12-01 00:00:00+00');</code></pre>
  <p>Composite B-tree indexes are added on <code>(shipment_id, event_timestamp DESC)</code> to accelerate the latest-status query pattern.</p>
</section>

<section id="multimodal-handling">
  <h2>Multimodal vs Last-Mile Data Modeling</h2>
  <p>Ocean and intermodal freight involve intermediate transshipment hubs, vessel IMO numbers, and container seals, while last-mile parcel networks track courier driver geofence proximity and recipient delivery signatures. Discover more in our <a href="/shipment-data/lifecycle">Shipment Lifecycle State Machine Guide</a>.</p>
</section>
        """
    },
    {
        "slug": "lifecycle",
        "url_path": "shipment-data/lifecycle.html",
        "title": "The Multimodal Shipment Lifecycle & State Machine",
        "meta_title": "Freight Shipment Lifecycle State Machine & Event Transitions | FreightIQ",
        "meta_desc": "Design deterministic finite state machines (FSM) for shipment tracking. Prevent out-of-order anomalies, manage exception branches, and enforce invariant rules.",
        "primary_keyword": "shipment lifecycle state machine",
        "category": "Shipment Data",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "A shipment is a dynamic state machine that traverses discrete physical gates. Implementing strict state machine validation prevents impossible transitions, such as delivering a parcel before it was picked up.",
        "toc": [
            {"id": "state-machine-topology", "title": "Finite State Machine Topology"},
            {"id": "valid-transitions-table", "title": "Transition Matrix & Transition Invariants"},
            {"id": "exception-loop-handling", "title": "Exception Loops & Failed Delivery Retries"},
            {"id": "python-state-validator", "title": "Python FSM State Transition Validator"}
        ],
        "content_html": """
<section id="state-machine-topology">
  <h2>Finite State Machine Topology</h2>
  <p>A resilient logistics state machine consists of forward progress states, temporary exception sub-states, and immutable terminal states:</p>
  <ul>
    <li><strong>Happy Path:</strong> <code>ORDER_CREATED</code> &rarr; <code>PICKED_UP</code> &rarr; <code>IN_TRANSIT</code> &rarr; <code>OUT_FOR_DELIVERY</code> &rarr; <code>DELIVERED</code></li>
    <li><strong>Exception Branch:</strong> <code>IN_TRANSIT</code> &rarr; <code>CUSTOMS_HOLD</code> &rarr; <code>IN_TRANSIT</code></li>
    <li><strong>Last-Mile Retry:</strong> <code>OUT_FOR_DELIVERY</code> &rarr; <code>FAILED_ATTEMPT</code> &rarr; <code>OUT_FOR_DELIVERY</code> &rarr; <code>DELIVERED</code></li>
    <li><strong>Abort State:</strong> <code>FAILED_ATTEMPT</code> &rarr; <code>RETURNED_TO_SENDER</code> (Terminal)</li>
  </ul>
</section>

<section id="valid-transitions-table">
  <h2>Transition Matrix & Transition Invariants</h2>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Current State</th>
          <th>Allowed Next States</th>
          <th>Disallowed (Invalid) Transitions</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>ORDER_CREATED</code></td>
          <td><code>PICKED_UP</code>, <code>CANCELED</code></td>
          <td><code>IN_TRANSIT</code>, <code>DELIVERED</code></td>
        </tr>
        <tr>
          <td><code>PICKED_UP</code></td>
          <td><code>IN_TRANSIT</code>, <code>EXCEPTION</code></td>
          <td><code>ORDER_CREATED</code>, <code>DELIVERED</code></td>
        </tr>
        <tr>
          <td><code>IN_TRANSIT</code></td>
          <td><code>OUT_FOR_DELIVERY</code>, <code>EXCEPTION</code></td>
          <td><code>ORDER_CREATED</code>, <code>PICKED_UP</code></td>
        </tr>
        <tr>
          <td><code>OUT_FOR_DELIVERY</code></td>
          <td><code>DELIVERED</code>, <code>FAILED_ATTEMPT</code></td>
          <td><code>ORDER_CREATED</code>, <code>PICKED_UP</code></td>
        </tr>
        <tr>
          <td><code>DELIVERED</code></td>
          <td><em>None (Terminal State)</em></td>
          <td>All states (Immutable)</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section id="exception-loop-handling">
  <h2>Exception Loops & Failed Delivery Retries</h2>
  <p>In last-mile logistics, an address error or security gate lockout triggers a <code>FAILED_ATTEMPT</code> state. Most parcel carriers permit up to 3 redelivery attempts before transitioning to <code>RETURNED_TO_SENDER</code>.</p>
</section>

<section id="python-state-validator">
  <h2>Python FSM State Transition Validator</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python State Machine</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>from enum import Enum
from typing import Set, Dict

class ShipmentState(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    EXCEPTION = "EXCEPTION"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    FAILED_ATTEMPT = "FAILED_ATTEMPT"
    DELIVERED = "DELIVERED"
    RETURNED_TO_SENDER = "RETURNED_TO_SENDER"

TRANSITIONS: Dict[ShipmentState, Set[ShipmentState]] = {
    ShipmentState.ORDER_CREATED: {ShipmentState.PICKED_UP, ShipmentState.EXCEPTION},
    ShipmentState.PICKED_UP: {ShipmentState.IN_TRANSIT, ShipmentState.EXCEPTION},
    ShipmentState.IN_TRANSIT: {ShipmentState.OUT_FOR_DELIVERY, ShipmentState.EXCEPTION},
    ShipmentState.EXCEPTION: {ShipmentState.IN_TRANSIT, ShipmentState.RETURNED_TO_SENDER},
    ShipmentState.OUT_FOR_DELIVERY: {ShipmentState.DELIVERED, ShipmentState.FAILED_ATTEMPT},
    ShipmentState.FAILED_ATTEMPT: {ShipmentState.OUT_FOR_DELIVERY, ShipmentState.RETURNED_TO_SENDER},
    ShipmentState.DELIVERED: set(),  # Terminal
    ShipmentState.RETURNED_TO_SENDER: set()  # Terminal
}

def validate_state_transition(current: ShipmentState, incoming: ShipmentState) -> bool:
    if current == incoming:
        return True  # Idempotent status repeat allowed
    allowed = TRANSITIONS.get(current, set())
    if incoming not in allowed:
        raise ValueError(f"Illegal state transition: {current.value} -> {incoming.value}")
    return True</code></pre>
  </div>
  <p>Experience dynamic state execution in our <a href="/tools/lifecycle-visualizer">Shipment Lifecycle Visualizer</a>.</p>
</section>
        """
    },
    {
        "slug": "shipment-ids",
        "url_path": "shipment-data/shipment-ids.html",
        "title": "Master Shipment Identifiers: UUIDv7 vs ULID vs Composite Keys",
        "meta_title": "Shipment Identifier Architecture: UUIDv7 vs ULID vs Composite | FreightIQ",
        "meta_desc": "Evaluate primary key architectures for global freight data. Why time-sortable UUIDv7 and ULID outperform random UUIDv4 and sequential auto-increments.",
        "primary_keyword": "master shipment identifier design",
        "category": "Shipment Data",
        "reading_time": "10 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In distributed logistics platforms where millions of carrier webhooks arrive concurrently, choosing the correct primary key strategy impacts database B-tree clustering, ingestion throughput, and data reconciliation.",
        "toc": [
            {"id": "the-identifier-challenge", "title": "The Distributed Shipment ID Problem"},
            {"id": "uuid4-vs-uuid7-vs-ulid", "title": "Comparison: UUIDv4 vs UUIDv7 vs ULID"},
            {"id": "uuid7-postgresql-benchmark", "title": "PostgreSQL Index Clustering & Performance"},
            {"id": "best-practice-standard", "title": "Recommended Identifier Standard"}
        ],
        "content_html": """
<section id="the-identifier-challenge">
  <h2>The Distributed Shipment ID Problem</h2>
  <p>In freight tech, traditional sequential integer IDs (<code>SERIAL</code> or <code>BIGINT AUTO_INCREMENT</code>) fail because multiple microservices (WMS, TMS, carrier integration gateways) create shipments asynchronously without central database lock coordination. Conversely, random UUIDv4 causes catastrophic B-tree index page fragmentation at scale.</p>
</section>

<section id="uuid4-vs-uuid7-vs-ulid">
  <h2>Comparison: UUIDv4 vs UUIDv7 vs ULID</h2>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Identifier Type</th>
          <th>Time Sortable?</th>
          <th>Entropy Bits</th>
          <th>Index Fragmentation</th>
          <th>PostgreSQL Native</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>UUIDv4</strong></td>
          <td>No (Random)</td>
          <td>122 bits</td>
          <td>Extreme (Random I/O)</td>
          <td>Yes (<code>uuid</code>)</td>
        </tr>
        <tr>
          <td><strong>UUIDv7</strong></td>
          <td>Yes (Unix Millisecond)</td>
          <td>74 bits</td>
          <td>Minimal (Append-only)</td>
          <td>Yes (RFC 9562 standard)</td>
        </tr>
        <tr>
          <td><strong>ULID</strong></td>
          <td>Yes (Unix Millisecond)</td>
          <td>80 bits</td>
          <td>Minimal (Append-only)</td>
          <td>Requires custom extension</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section id="uuid7-postgresql-benchmark">
  <h2>PostgreSQL Index Clustering & Performance</h2>
  <p>Because UUIDv7 embeds a 48-bit UNIX millisecond timestamp in the most significant bits, new inserts are sequentially ordered. In production benchmarks with 100M rows, UUIDv7 achieves 4.5x faster write throughput than UUIDv4 due to zero B-tree re-balancing splits.</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL 17+ / Function SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>-- Generating RFC 9562 UUIDv7 in SQL
CREATE OR REPLACE FUNCTION generate_uuid_v7() 
RETURNS UUID AS $$
DECLARE
  unix_time_ms BYTEA;
  uuid_bytes BYTEA;
BEGIN
  -- 48-bit timestamp in milliseconds
  unix_time_ms := substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint) from 3 for 6);
  -- 80 bits of cryptographic randomness with version 7 (0111) and variant 1 (10)
  uuid_bytes := unix_time_ms || gen_random_bytes(10);
  uuid_bytes := set_byte(uuid_bytes, 6, (get_byte(uuid_bytes, 6) & 15) | 112);
  uuid_bytes := set_byte(uuid_bytes, 8, (get_byte(uuid_bytes, 8) & 63) | 128);
  RETURN encode(uuid_bytes, 'hex')::uuid;
END;
$$ LANGUAGE plpgsql VOLATILE;</code></pre>
  </div>
</section>

<section id="best-practice-standard">
  <h2>Recommended Identifier Standard</h2>
  <p>Standardize on UUIDv7 for all primary keys in <code>master_shipments</code> and <code>shipment_milestones</code>. Store the carrier's external tracking number in an indexed string column with a uniqueness constraint scoped by <code>carrier_code</code>.</p>
</section>
        """
    },
    {
        "slug": "tracking-numbers",
        "url_path": "shipment-data/tracking-numbers.html",
        "title": "Carrier Tracking Numbers: Formats, Checksums & Parsing",
        "meta_title": "Carrier Tracking Number Checksum Algorithms & Regex Guide | FreightIQ",
        "meta_desc": "Comprehensive guide to carrier tracking number validation. Implement Modulo-10, Mod-7, Luhn algorithms and regex for FedEx, UPS 1Z, USPS, and ISO 6346 containers.",
        "primary_keyword": "carrier tracking number validation regex",
        "category": "Shipment Data",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Every global carrier encodes security and validation digits into their tracking numbers. Learn how to parse, sanitize, and execute mathematical checksum verification against FedEx, UPS, USPS, and ocean container numbers.",
        "toc": [
            {"id": "carrier-format-overview", "title": "Carrier Tracking Format Architecture"},
            {"id": "ups-1z-modulo10", "title": "UPS 1Z Modulo-10 Checksum Algorithm"},
            {"id": "fedex-mod11-mod7", "title": "FedEx 12-Digit & 15-Digit Mod-11/Mod-7"},
            {"id": "ocean-iso-6346", "title": "Ocean Container ISO 6346 (BIC) Check Digit Calculation"},
            {"id": "unified-parser-code", "title": "Unified Python Checksum Verification Engine"}
        ],
        "content_html": """
<section id="carrier-format-overview">
  <h2>Carrier Tracking Format Architecture</h2>
  <p>Tracking numbers are not arbitrary strings; they contain structural carrier codes, service tier identifiers, account numbers, package sequential sequences, and a final mathematical check digit:</p>
  <ul>
    <li><strong>UPS:</strong> 18 characters beginning with <code>1Z</code> (e.g., <code>1Z9999999999999991</code>). Uses Modulo-10 on character numeric equivalents.</li>
    <li><strong>FedEx Express:</strong> 12 digits (e.g., <code>794612345678</code>). Uses weighted Modulo-11 with weights <code>[3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]</code>.</li>
    <li><strong>FedEx Ground:</strong> 15 digits or 20 digits (SSCC-18 compliant).</li>
    <li><strong>USPS:</strong> 22 digits starting with <code>9400</code>, <code>9205</code>, or <code>9300</code>.</li>
    <li><strong>Ocean Container (ISO 6346):</strong> 4 letters (3 owner + 1 category) + 6 digits + 1 check digit (e.g., <code>MSKU1829304</code>).</li>
  </ul>
</section>

<section id="ups-1z-modulo10">
  <h2>UPS 1Z Modulo-10 Checksum Algorithm</h2>
  <p>The UPS 1Z check digit is calculated across characters 3 through 17:</p>
  <ol>
    <li>Letters are converted to numbers: A-Z map to $((\text{ASCII} - 63) \pmod{10})$.</li>
    <li>Odd position digits (1-indexed) are summed.</li>
    <li>Even position digits are multiplied by 2 and summed.</li>
    <li>The total sum modulo 10 is subtracted from 10 (or 0 if remainder is 0).</li>
  </ol>
</section>

<section id="fedex-mod11-mod7">
  <h2>FedEx 12-Digit & 15-Digit Mod-11/Mod-7</h2>
  <p>FedEx Express 12-digit barcodes multiply the first 11 digits by repeating weights <code>(3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1)</code>. The remainder modulo 11 determines the check digit (if 10, check digit is 0).</p>
</section>

<section id="ocean-iso-6346">
  <h2>Ocean Container ISO 6346 (BIC) Check Digit Calculation</h2>
  <p>Every shipping container in the world conforms to ISO 6346. Each character is mapped to an international value, multiplied by $2^i$, summed, and evaluated modulo 11.</p>
</section>

<section id="unified-parser-code">
  <h2>Unified Python Checksum Verification Engine</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Python Checksum Engine</span>
      <button class="copy-btn">Copy Code</button>
    </div>
    <pre><code>def verify_fedex_12(tracking: str) -> bool:
    if not tracking.isdigit() or len(tracking) != 12:
        return False
    weights = [3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
    total = sum(int(digit) * weight for digit, weight in zip(tracking[:11], weights))
    check = (total % 11) % 10
    return check == int(tracking[11])

def verify_iso6346_container(code: str) -> bool:
    code = code.strip().upper()
    if len(code) != 11:
        return False
    char_map = {
        'A': 10, 'B': 12, 'C': 13, 'D': 14, 'E': 15, 'F': 16, 'G': 17, 'H': 18, 'I': 19,
        'J': 20, 'K': 21, 'L': 23, 'M': 24, 'N': 25, 'O': 26, 'P': 27, 'Q': 28, 'R': 29,
        'S': 30, 'T': 31, 'U': 32, 'V': 34, 'W': 35, 'X': 36, 'Y': 37, 'Z': 38
    }
    total = 0
    for i, ch in enumerate(code[:10]):
        val = char_map[ch] if ch in char_map else int(ch)
        total += val * (2 ** i)
    check_digit = (total % 11) % 10
    return check_digit == int(code[10])</code></pre>
  </div>
</section>
        """
    },
    {
        "slug": "status-events",
        "url_path": "shipment-data/status-events.html",
        "title": "Shipment Status Events: Event-Driven Architecture & EDI 214",
        "meta_title": "Shipment Status Events & ANSI X12 EDI 214 Ingestion | FreightIQ",
        "meta_desc": "Design event-driven freight architectures using Kafka and EDI 214. Complete mapping of ANSI X12 AT7 segments and Kafka event-sourcing schemas.",
        "primary_keyword": "shipment status event tracking",
        "category": "Shipment Data",
        "reading_time": "12 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "In transportation networks, state changes arrive as asynchronous events. This guide unpacks event-sourcing architectures for freight, mapping legacy ANSI X12 EDI 214 transmissions to modern JSON Kafka event streams.",
        "toc": [
            {"id": "event-sourcing-principles", "title": "Event-Sourcing in Logistics Systems"},
            {"id": "edi-214-anatomy", "title": "Anatomy of an ANSI X12 EDI 214 Transaction"},
            {"id": "kafka-schema-spec", "title": "Kafka Avro / JSON Event Schema Specification"},
            {"id": "downstream-projection", "title": "Materializing Real-Time Status Projections"}
        ],
        "content_html": """
<section id="event-sourcing-principles">
  <h2>Event-Sourcing in Logistics Systems</h2>
  <p>Logistics tracking is naturally event-sourced. Rather than updating a single mutable row in place, platforms record every milestone scan as an append-only, immutable event. The current status of a shipment is simply the cumulative projection of all historical events ordered by timestamp.</p>
</section>

<section id="edi-214-anatomy">
  <h2>Anatomy of an ANSI X12 EDI 214 Transaction</h2>
  <p>The standard EDI 214 (Transportation Carrier Shipment Status Message) uses standardized segments:</p>
  <ul>
    <li><code>B10</code>: Carrier Reference Number, Shipment ID, SCAC.</li>
    <li><code>LX</code>: Transaction set line number.</li>
    <li><code>AT7</code>: Shipment Status Details (Status Code, Status Reason, Date, Time, Time Code).</li>
    <li><code>MS1</code>: Equipment, Location (City, State, Postal Code, Country).</li>
  </ul>
  
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">Raw EDI 214 Segment</span>
      <button class="copy-btn">Copy EDI</button>
    </div>
    <pre><code>ST*214*0001~
B10*1029384*SHP-9921*FDXG~
LX*1~
AT7*X6*NS***20261111*1430*LT~
MS1*MEMPHIS*TN*USA~
SE*6*0001~</code></pre>
  </div>
</section>

<section id="kafka-schema-spec">
  <h2>Kafka Avro / JSON Event Schema Specification</h2>
  <p>When translated into event streaming platforms, milestones adhere to strict JSON schemas:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">JSON Event Schema</span>
      <button class="copy-btn">Copy JSON</button>
    </div>
    <pre><code>{
  "event_id": "evt_01928374-1234-7000-8000-abcdef123456",
  "shipment_id": "shp_01928374-9999-7000-8000-111122223333",
  "source_protocol": "EDI_214",
  "carrier_scac": "FDXG",
  "canonical_status": "OUT_FOR_DELIVERY",
  "raw_status_code": "X6",
  "raw_reason_code": "NS",
  "event_timestamp": "2026-11-11T14:30:00Z",
  "location": {
    "city": "Memphis",
    "state": "TN",
    "country": "USA"
  }
}</code></pre>
  </div>
</section>

<section id="downstream-projection">
  <h2>Materializing Real-Time Status Projections</h2>
  <p>Kafka consumers aggregate incoming events, updating the master read-optimized view in PostgreSQL or Redis using idempotent transactions. Explore validation techniques in our <a href="/validation/sql-techniques">SQL Validation Techniques Guide</a>.</p>
</section>
        """
    },
    {
        "slug": "delivery-dates",
        "url_path": "shipment-data/delivery-dates.html",
        "title": "Estimated vs Actual Delivery Dates (EDD/ADD) Engineering",
        "meta_title": "Estimated vs Actual Delivery Dates (EDD/ADD) Architecture | FreightIQ",
        "meta_desc": "Engineering logic for dynamic Estimated Delivery Dates (EDD) and Actual Delivery Dates (ADD). Timezone normalization, appointment windows, and transit days.",
        "primary_keyword": "estimated delivery date schema logic",
        "category": "Shipment Data",
        "reading_time": "11 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Accurate ETA prediction requires modeling carrier transit lanes, operational cutoffs, weekend blackouts, and local destination timezones. This guide details how to engineer reliable EDD and ADD tracking data models.",
        "toc": [
            {"id": "edd-vs-add-definitions", "title": "Core Definitions: EDD, ADD & Appointment Windows"},
            {"id": "timezone-offsets-handling", "title": "Timezone Offsets & Local Daylight Savings"},
            {"id": "dynamic-eta-drift-detection", "title": "Detecting ETA Drift & Carrier SLA Penalties"},
            {"id": "sql-on-time-performance", "title": "SQL On-Time Delivery (OTD) Calculation Engine"}
        ],
        "content_html": """
<section id="edd-vs-add-definitions">
  <h2>Core Definitions: EDD, ADD & Appointment Windows</h2>
  <p>Transportation contracts distinguish between multiple milestone timestamps:</p>
  <ul>
    <li><strong>Initial Estimated Delivery Date (EDD_0):</strong> Baseline promise date calculated at booking time.</li>
    <li><strong>Dynamic Revised ETA ($\text{EDD}_t$):</strong> Continuous ML-forecasted arrival time updated during transit.</li>
    <li><strong>Appointment Delivery Window:</strong> Required delivery slot (e.g. 08:00 - 12:00) specified by freight receivers.</li>
    <li><strong>Actual Delivery Date (ADD):</strong> Immutable timestamp when the consignee signs Proof of Delivery (POD).</li>
  </ul>
</section>

<section id="timezone-offsets-handling">
  <h2>Timezone Offsets & Local Daylight Savings</h2>
  <p>All database timestamps must be persisted strictly in UTC (<code>TIMESTAMPTZ</code>). However, determining whether a delivery was on-time requires evaluating the local calendar day of the recipient destination:</p>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL Timezone Conversion</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>-- Evaluate whether delivery met 17:00 local business day deadline
SELECT 
  shipment_id,
  actual_delivery_at,
  destination_iana_timezone,
  (actual_delivery_at AT TIME ZONE destination_iana_timezone)::time AS local_delivery_time,
  CASE 
    WHEN (actual_delivery_at AT TIME ZONE destination_iana_timezone)::time <= TIME '17:00:00' 
    THEN 'WITHIN_BUSINESS_HOURS'
    ELSE 'AFTER_HOURS_DELIVERY'
  END AS delivery_window_classification
FROM master_shipments;</code></pre>
  </div>
</section>

<section id="dynamic-eta-drift-detection">
  <h2>Detecting ETA Drift & Carrier SLA Penalties</h2>
  <p>Track ETA revisions across carrier telemetry updates. If a carrier pushes the EDD backward more than twice during a single transit, automated alerts notify control tower specialists to investigate customs delays or missed connections.</p>
</section>

<section id="sql-on-time-performance">
  <h2>SQL On-Time Delivery (OTD) Calculation Engine</h2>
  <p>On-Time Delivery (OTD) is the defining KPI for carrier contract performance:</p>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostgreSQL SQL</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>SELECT 
  carrier_scac,
  COUNT(*) AS total_delivered_shipments,
  COUNT(CASE WHEN actual_delivery_at <= initial_edd THEN 1 END) AS on_time_deliveries,
  COUNT(CASE WHEN actual_delivery_at > initial_edd THEN 1 END) AS delayed_deliveries,
  ROUND(
    COUNT(CASE WHEN actual_delivery_at <= initial_edd THEN 1 END)::numeric / COUNT(*) * 100, 
    2
  ) AS on_time_percentage_score
FROM master_shipments
WHERE actual_delivery_at IS NOT NULL
GROUP BY carrier_scac;</code></pre>
  </div>
</section>
        """
    },
    {
        "slug": "location-data",
        "url_path": "shipment-data/location-data.html",
        "title": "Geospatial Logistics Data: UN/LOCODE, Geofencing & PostGIS",
        "meta_title": "Geospatial Logistics Data: UN/LOCODE & PostGIS Geofencing | FreightIQ",
        "meta_desc": "Model spatial freight data using PostGIS. Normalize UN/LOCODE, IATA, SPLC terminal codes, and implement high-performance geofencing polygon containment.",
        "primary_keyword": "logistics geospatial location data PostGIS",
        "category": "Shipment Data",
        "reading_time": "13 min read",
        "updated_at": "November 2026",
        "author": "Rajvardhan Singh Rathore",
        "author_title": "Logistics Data Architect",
        "intro": "Physical logistics is fundamentally geospatial. Learn how to normalize global port and terminal codes (UN/LOCODE, IATA) and execute real-time geofence polygon checks using PostGIS spatial indexes.",
        "toc": [
            {"id": "locode-and-terminal-standards", "title": "UN/LOCODE, IATA & SPLC Standards"},
            {"id": "postgis-spatial-modeling", "title": "PostGIS Spatial DDL & Polygon Modeling"},
            {"id": "geofence-containment-query", "title": "Automated Geofence Entry/Exit Detection"},
            {"id": "spatial-indexing-best-practices", "title": "R-Tree Spatial Indexing & Performance"}
        ],
        "content_html": """
<section id="locode-and-terminal-standards">
  <h2>UN/LOCODE, IATA & SPLC Standards</h2>
  <p>Global logistics data integrates three major location code taxonomies:</p>
  <ul>
    <li><strong>UN/LOCODE (United Nations Code for Trade and Transport Locations):</strong> 5-character string consisting of 2-letter ISO country code + 3-character location identifier (e.g., <code>USLAX</code> = Los Angeles Port, <code>SGSIN</code> = Singapore, <code>NLRTM</code> = Rotterdam).</li>
    <li><strong>IATA / ICAO:</strong> 3-letter airport codes used for air cargo logistics (e.g., <code>MEM</code>, <code>FRA</code>, <code>HKG</code>).</li>
    <li><strong>SPLC (Standard Point Location Code):</strong> 6-9 digit numeric code used in North American rail and motor freight.</li>
  </ul>
</section>

<section id="postgis-spatial-modeling">
  <h2>PostGIS Spatial DDL & Polygon Modeling</h2>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostGIS Spatial DDL</span>
      <button class="copy-btn">Copy DDL</button>
    </div>
    <pre><code>CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE logistics_geofenced_hubs (
  hub_id UUID PRIMARY KEY,
  unlocode CHAR(5) NOT NULL,
  hub_name VARCHAR(100) NOT NULL,
  facility_type VARCHAR(30) CHECK (facility_type IN ('PORT', 'AIRPORT', 'RAIL_RAMP', 'CROSS_DOCK', 'LAST_MILE_DEPOT')),
  geofence_polygon GEOMETRY(Polygon, 4326) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hubs_spatial ON logistics_geofenced_hubs USING GIST (geofence_polygon);</code></pre>
  </div>
</section>

<section id="geofence-containment-query">
  <h2>Automated Geofence Entry/Exit Detection</h2>
  <p>When a container telematics unit broadcasts GPS coordinates, determine if the asset has arrived within the terminal geofence using <code>ST_Contains</code>:</p>

  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">PostGIS Point-in-Polygon Query</span>
      <button class="copy-btn">Copy SQL</button>
    </div>
    <pre><code>SELECT 
  p.container_id,
  p.ping_timestamp,
  h.unlocode,
  h.hub_name,
  h.facility_type
FROM container_gps_pings p
JOIN logistics_geofenced_hubs h 
  ON ST_Contains(
       h.geofence_polygon, 
       ST_SetSRID(ST_MakePoint(p.longitude, p.latitude), 4326)
     )
WHERE p.ping_timestamp >= CURRENT_TIMESTAMP - INTERVAL '15 minutes';</code></pre>
  </div>
</section>

<section id="spatial-indexing-best-practices">
  <h2>R-Tree Spatial Indexing & Performance</h2>
  <p>Always maintain a GiST spatial index on polygon and point columns. For distance queries across broad geographic areas, use the <code>GEOGRAPHY</code> type to automatically account for the Earth's ellipsoidal curvature.</p>
</section>
        """
    }
]
