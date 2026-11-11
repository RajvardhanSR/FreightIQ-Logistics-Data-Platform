/**
 * FreightIQ Interactive Developer Tools Suite
 * Safe, zero-credential client-side implementations
 */

// ============================================================================
// 1. SQL Validation Playground Engine
// ============================================================================

const SAMPLE_DATABASE = {
  shipments: [
    { shipment_id: "SHP-1001", tracking_number: "1Z9999999999999991", carrier_code: "UPS", origin_hub: "ORD", destination_hub: "DFW", weight_kg: 14.50, status: "DELIVERED", created_at: "2026-11-01 08:30:00", delivered_at: "2026-11-03 14:15:00" },
    { shipment_id: "SHP-1002", tracking_number: "794612345678", carrier_code: "FDX", origin_hub: "MEM", destination_hub: "JFK", weight_kg: 2.10, status: "IN_TRANSIT", created_at: "2026-11-02 10:15:00", delivered_at: null },
    { shipment_id: "SHP-1003", tracking_number: null, carrier_code: "DHL", origin_hub: "CVG", destination_hub: "LAX", weight_kg: 45.00, status: "PICKED_UP", created_at: "2026-11-02 12:00:00", delivered_at: null },
    { shipment_id: "SHP-1004", tracking_number: "1Z8888888888888882", carrier_code: "UPS", origin_hub: "ATL", destination_hub: null, weight_kg: -5.00, status: "ORDER_CREATED", created_at: "2026-11-03 09:00:00", delivered_at: null },
    { shipment_id: "SHP-1005", tracking_number: "794698765432", carrier_code: "FDX", origin_hub: "IND", destination_hub: "SEA", weight_kg: 120.50, status: "DELIVERED", created_at: "2026-11-04 14:00:00", delivered_at: "2026-11-03 11:00:00" }, // chron error
    { shipment_id: "SHP-1006", tracking_number: "794612345678", carrier_code: "FDX", origin_hub: "MEM", destination_hub: "BOS", weight_kg: 8.40, status: "DELIVERED", created_at: "2026-11-01 16:20:00", delivered_at: "2026-11-03 18:00:00" }, // duplicate tracking
    { shipment_id: "SHP-1007", tracking_number: "9400100000000000000001", carrier_code: "USPS", origin_hub: "DEN", destination_hub: "MIA", weight_kg: 0.00, status: "PICKED_UP", created_at: "2026-11-04 07:15:00", delivered_at: null }, // zero weight
    { shipment_id: "SHP-1008", tracking_number: "MAEU1234567", carrier_code: "MSK", origin_hub: "SGSIN", destination_hub: "USLAX", weight_kg: 18450.00, status: "IN_TRANSIT", created_at: "2026-10-20 04:00:00", delivered_at: null }
  ],
  tracking_events: [
    { event_id: "EVT-901", shipment_id: "SHP-1001", event_code: "PU", event_timestamp: "2026-11-01 10:00:00", location_code: "ORD", message: "Package picked up by carrier" },
    { event_id: "EVT-902", shipment_id: "SHP-1001", event_code: "DL", event_timestamp: "2026-11-03 14:15:00", location_code: "DFW", message: "Delivered to dock door 4" },
    { event_id: "EVT-903", shipment_id: "SHP-1002", event_code: "IT", event_timestamp: "2026-11-02 18:45:00", location_code: "MEM", message: "Departed FedEx sorting facility" },
    { event_id: "EVT-904", shipment_id: "SHP-9999", event_code: "AR", event_timestamp: "2026-11-03 01:20:00", location_code: "PHX", message: "Orphan event - no master shipment" }
  ]
};

const SQL_PRESETS = {
  null_audit: `-- Check for NULL or missing critical shipment identifiers
SELECT 
  shipment_id, 
  tracking_number, 
  carrier_code, 
  destination_hub, 
  status
FROM shipments
WHERE tracking_number IS NULL 
   OR destination_hub IS NULL 
   OR carrier_code IS NULL;`,

  duplicates: `-- Identify duplicate tracking numbers across different shipment IDs
SELECT 
  tracking_number, 
  COUNT(*) as record_count,
  COUNT(DISTINCT shipment_id) as distinct_shipments
FROM shipments
WHERE tracking_number IS NOT NULL
GROUP BY tracking_number
HAVING COUNT(*) > 1;`,

  weight_boundaries: `-- Detect invalid cargo weight records (tare/gross physics violations)
SELECT 
  shipment_id, 
  tracking_number, 
  weight_kg, 
  carrier_code,
  CASE 
    WHEN weight_kg <= 0 THEN 'CRITICAL: Zero or negative weight'
    WHEN weight_kg > 25000 THEN 'WARNING: Overweight container threshold'
    ELSE 'VALID'
  END as validation_flag
FROM shipments
WHERE weight_kg <= 0 OR weight_kg > 25000;`,

  chronological_anomalies: `-- Detect chronological paradoxes (Delivered timestamp before Creation timestamp)
SELECT 
  shipment_id, 
  tracking_number, 
  created_at, 
  delivered_at,
  'Delivered prior to creation time' as anomaly_reason
FROM shipments
WHERE delivered_at IS NOT NULL 
  AND delivered_at < created_at;`,

  orphan_events: `-- Detect orphan tracking events with no parent shipment record
SELECT 
  e.event_id, 
  e.shipment_id, 
  e.event_code, 
  e.event_timestamp, 
  e.message
FROM tracking_events e
WHERE e.shipment_id NOT IN (SELECT s.shipment_id FROM shipments s);`
};

function runSqlPlayground() {
  const querySelect = document.getElementById("sql-preset-select");
  const editor = document.getElementById("sql-editor");
  const output = document.getElementById("sql-output");
  const stats = document.getElementById("sql-stats");

  if (!editor || !output) return;

  const query = editor.value.trim();
  const startTime = performance.now();

  try {
    let results = [];
    let queryLower = query.toLowerCase();

    if (queryLower.includes("where tracking_number is null")) {
      results = SAMPLE_DATABASE.shipments
        .filter(s => s.tracking_number === null || s.destination_hub === null || s.carrier_code === null)
        .map(s => ({ shipment_id: s.shipment_id, tracking_number: s.tracking_number || "[NULL]", carrier_code: s.carrier_code, destination_hub: s.destination_hub || "[NULL]", status: s.status }));
    } else if (queryLower.includes("having count(*) > 1") || queryLower.includes("distinct_shipments")) {
      const counts = {};
      SAMPLE_DATABASE.shipments.forEach(s => {
        if (!s.tracking_number) return;
        counts[s.tracking_number] = (counts[s.tracking_number] || 0) + 1;
      });
      results = Object.keys(counts)
        .filter(k => counts[k] > 1)
        .map(k => ({ tracking_number: k, record_count: counts[k], distinct_shipments: counts[k] }));
    } else if (queryLower.includes("weight_kg <= 0") || queryLower.includes("validation_flag")) {
      results = SAMPLE_DATABASE.shipments
        .filter(s => s.weight_kg <= 0 || s.weight_kg > 25000)
        .map(s => ({
          shipment_id: s.shipment_id,
          tracking_number: s.tracking_number || "N/A",
          weight_kg: s.weight_kg,
          carrier_code: s.carrier_code,
          validation_flag: s.weight_kg <= 0 ? "CRITICAL: Zero or negative weight" : "WARNING: Overweight container threshold"
        }));
    } else if (queryLower.includes("delivered_at < created_at") || queryLower.includes("anomaly_reason")) {
      results = SAMPLE_DATABASE.shipments
        .filter(s => s.delivered_at && s.delivered_at < s.created_at)
        .map(s => ({
          shipment_id: s.shipment_id,
          tracking_number: s.tracking_number,
          created_at: s.created_at,
          delivered_at: s.delivered_at,
          anomaly_reason: "Delivered prior to creation time"
        }));
    } else if (queryLower.includes("orphan") || queryLower.includes("tracking_events")) {
      const validShipmentIds = new Set(SAMPLE_DATABASE.shipments.map(s => s.shipment_id));
      results = SAMPLE_DATABASE.tracking_events
        .filter(e => !validShipmentIds.has(e.shipment_id))
        .map(e => ({
          event_id: e.event_id,
          shipment_id: e.shipment_id,
          event_code: e.event_code,
          event_timestamp: e.event_timestamp,
          message: e.message
        }));
    } else {
      // Default: Return all shipments
      results = SAMPLE_DATABASE.shipments.map(s => ({
        shipment_id: s.shipment_id,
        tracking_number: s.tracking_number || "NULL",
        carrier_code: s.carrier_code,
        weight_kg: s.weight_kg,
        status: s.status
      }));
    }

    const elapsed = (performance.now() - startTime).toFixed(2);
    if (stats) {
      stats.innerHTML = `<span class="badge-emerald" style="padding: 2px 8px; border-radius: 4px;">Status: Success</span> &nbsp; Rows: <strong>${results.length}</strong> &nbsp; Execution Time: <strong>${elapsed} ms</strong>`;
    }

    if (results.length === 0) {
      output.innerHTML = `<div style="padding: 2rem; text-align: center; color: var(--text-muted);">No records matched the validation assertion filter (All records clean).</div>`;
      return;
    }

    const cols = Object.keys(results[0]);
    let html = `<table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;"><thead><tr style="border-bottom: 2px solid var(--border-medium);">`;
    cols.forEach(c => {
      html += `<th style="padding: 8px 12px; text-align: left; color: var(--accent-blue); background: var(--bg-tertiary);">${c}</th>`;
    });
    html += `</tr></thead><tbody>`;

    results.forEach(row => {
      html += `<tr style="border-bottom: 1px solid var(--border-subtle);">`;
      cols.forEach(c => {
        let val = row[c];
        let colorStyle = "";
        if (typeof val === "string" && (val.includes("CRITICAL") || val.includes("NULL"))) {
          colorStyle = "color: var(--accent-rose); font-weight: 600;";
        } else if (typeof val === "string" && val.includes("WARNING")) {
          colorStyle = "color: var(--accent-amber); font-weight: 600;";
        }
        html += `<td style="padding: 8px 12px; ${colorStyle}">${val}</td>`;
      });
      html += `</tr>`;
    });
    html += `</tbody></table>`;
    output.innerHTML = html;

  } catch (err) {
    if (stats) {
      stats.innerHTML = `<span style="background: rgba(244,63,94,0.15); color: var(--accent-rose); padding: 2px 8px; border-radius: 4px;">Syntax Error</span>`;
    }
    output.innerHTML = `<div class="status-banner status-error">Execution Error: ${err.message}</div>`;
  }
}

// ============================================================================
// 2. JSON Shipment Schema Validator Engine
// ============================================================================

const JSON_PAYLOAD_PRESETS = {
  valid_fedex: {
    title: "Valid FedEx Express Milestone Webhook",
    json: JSON.stringify({
      event_id: "evt_fdx_882910471",
      carrier_code: "FDX",
      tracking_number: "794612345678",
      shipment: {
        master_id: "SHP-2026-8810",
        service_level: "PRIORITY_OVERNIGHT",
        gross_weight_kg: 4.85,
        pieces_count: 1
      },
      milestone: {
        status_code: "OUT_FOR_DELIVERY",
        timestamp: "2026-11-11T07:45:00Z",
        location: {
          facility_code: "MEM-HUB-01",
          city: "Memphis",
          state: "TN",
          country_iso: "USA",
          coordinates: {
            latitude: 35.0456,
            longitude: -89.9767
          }
        }
      }
    }, null, 2)
  },

  valid_ocean: {
    title: "Valid Ocean Container Gate-In (Maersk)",
    json: JSON.stringify({
      event_id: "evt_msk_992100",
      carrier_code: "MSK",
      tracking_number: "MSKU1829304",
      shipment: {
        master_id: "SHP-OCN-4402",
        service_level: "OCEAN_FCL",
        gross_weight_kg: 24200.00,
        pieces_count: 1
      },
      milestone: {
        status_code: "IN_TRANSIT",
        timestamp: "2026-11-10T14:30:00Z",
        location: {
          facility_code: "USLAX-TRM4",
          city: "Los Angeles",
          country_iso: "USA",
          coordinates: {
            latitude: 33.7431,
            longitude: -118.2672
          }
        }
      }
    }, null, 2)
  },

  invalid_missing_keys: {
    title: "Invalid: Missing Tracking Number & Bad Timestamp",
    json: JSON.stringify({
      event_id: "evt_err_001",
      carrier_code: "UPS",
      shipment: {
        master_id: "SHP-ERR-001",
        service_level: "GROUND",
        gross_weight_kg: 12.0
      },
      milestone: {
        status_code: "IN_TRANSIT",
        timestamp: "Wednesday, Nov 11 at 3pm", // Invalid ISO-8601
        location: {
          city: "Chicago"
        }
      }
    }, null, 2)
  },

  invalid_physics: {
    title: "Invalid: Negative Weight & Illegal Status Enum",
    json: JSON.stringify({
      event_id: "evt_err_002",
      carrier_code: "DHL",
      tracking_number: "DHL9988776655",
      shipment: {
        master_id: "SHP-ERR-002",
        service_level: "EXPRESS",
        gross_weight_kg: -15.50, // Negative weight violation
        pieces_count: 0 // Pieces must be >= 1
      },
      milestone: {
        status_code: "TELEPORTED_TO_DESTINATION", // Illegal Enum
        timestamp: "2026-11-11T12:00:00Z",
        location: {
          facility_code: "CVG-MAIN",
          country_iso: "USA"
        }
      }
    }, null, 2)
  }
};

function runJsonSchemaValidator() {
  const editor = document.getElementById("json-editor");
  const resultDiv = document.getElementById("json-results");

  if (!editor || !resultDiv) return;

  const rawJson = editor.value.trim();
  const errors = [];
  let parsed = null;

  try {
    parsed = JSON.parse(rawJson);
  } catch (e) {
    resultDiv.innerHTML = `
      <div class="status-banner status-error">
        <span>❌ Malformed JSON: ${e.message}</span>
      </div>
      <p style="color: var(--text-muted); font-size: 0.85rem;">Ensure all keys are enclosed in double quotes and syntax has valid braces.</p>
    `;
    return;
  }

  // Schema Rules Validation
  if (!parsed.event_id || typeof parsed.event_id !== "string") {
    errors.push({ path: "$.event_id", message: "Required string property 'event_id' is missing or not a string." });
  }

  const validCarriers = ["FDX", "UPS", "DHL", "MSK", "CMA", "USPS"];
  if (!parsed.carrier_code || !validCarriers.includes(parsed.carrier_code)) {
    errors.push({ path: "$.carrier_code", message: `Carrier code must be one of [${validCarriers.join(", ")}]. Got: ${JSON.stringify(parsed.carrier_code)}` });
  }

  if (!parsed.tracking_number || typeof parsed.tracking_number !== "string" || parsed.tracking_number.length < 5) {
    errors.push({ path: "$.tracking_number", message: "Required string 'tracking_number' missing or shorter than 5 chars." });
  }

  if (!parsed.shipment || typeof parsed.shipment !== "object") {
    errors.push({ path: "$.shipment", message: "Required object 'shipment' missing." });
  } else {
    if (typeof parsed.shipment.gross_weight_kg !== "number" || parsed.shipment.gross_weight_kg <= 0) {
      errors.push({ path: "$.shipment.gross_weight_kg", message: `Gross weight must be a positive number > 0. Got: ${parsed.shipment.gross_weight_kg}` });
    }
    if (parsed.shipment.pieces_count !== undefined && (typeof parsed.shipment.pieces_count !== "number" || parsed.shipment.pieces_count < 1)) {
      errors.push({ path: "$.shipment.pieces_count", message: "Pieces count must be an integer >= 1." });
    }
  }

  if (!parsed.milestone || typeof parsed.milestone !== "object") {
    errors.push({ path: "$.milestone", message: "Required object 'milestone' missing." });
  } else {
    const validStatuses = ["ORDER_CREATED", "PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION", "FAILED_ATTEMPT"];
    if (!validStatuses.includes(parsed.milestone.status_code)) {
      errors.push({ path: "$.milestone.status_code", message: `Invalid status code '${parsed.milestone.status_code}'. Allowed enums: ${validStatuses.join(", ")}` });
    }

    // ISO-8601 validation
    const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;
    if (!parsed.milestone.timestamp || !isoRegex.test(parsed.milestone.timestamp)) {
      errors.push({ path: "$.milestone.timestamp", message: `Timestamp must follow strict ISO-8601 UTC format (YYYY-MM-DDTHH:MM:SSZ). Got: '${parsed.milestone.timestamp}'` });
    }
  }

  if (errors.length === 0) {
    resultDiv.innerHTML = `
      <div class="status-banner status-success">
        <span>✓ JSON Payload Valid: Conforms strictly to Logistics Webhook Schema Draft-07</span>
      </div>
      <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-md); font-size: 0.85rem;">
        <div style="color: var(--accent-emerald); font-weight: 700; margin-bottom: 0.5rem;">Validation Summary:</div>
        <ul style="margin: 0; padding-left: 1.25rem; color: var(--text-secondary);">
          <li>Carrier Code: <code>${parsed.carrier_code}</code> (Verified Registry)</li>
          <li>Tracking Number: <code>${parsed.tracking_number}</code> (Format OK)</li>
          <li>Milestone State: <code>${parsed.milestone.status_code}</code> (Valid State Machine Step)</li>
          <li>Timestamp: <code>${parsed.milestone.timestamp}</code> (Valid ISO-8601 UTC)</li>
          <li>Payload Weight: <code>${parsed.shipment.gross_weight_kg} kg</code> (Valid Physics Boundary)</li>
        </ul>
      </div>
    `;
  } else {
    let errorRows = errors.map(err => `
      <div style="border-left: 3px solid var(--accent-rose); background: rgba(244,63,94,0.06); padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 4px;">
        <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent-rose); font-weight: 700;">${err.path}</div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 2px;">${err.message}</div>
      </div>
    `).join("");

    resultDiv.innerHTML = `
      <div class="status-banner status-error">
        <span>❌ Schema Validation Failed: ${errors.length} violation(s) detected</span>
      </div>
      <div>${errorRows}</div>
    `;
  }
}

// ============================================================================
// 3. Shipment Lifecycle Visualizer Engine
// ============================================================================

const LIFECYCLE_SCENARIOS = {
  happy_path: {
    title: "Standard Priority Delivery (Happy Path)",
    events: [
      { step: "ORDER_CREATED", timestamp: "2026-11-10 09:00:00", location: "Chicago, IL", desc: "Digital EDI 204 manifest accepted from shipper ERP." },
      { step: "PICKED_UP", timestamp: "2026-11-10 14:30:00", location: "ORD Logistics Gateway", desc: "Driver scanned parcel into pickup dispatch manifest." },
      { step: "IN_TRANSIT", timestamp: "2026-11-11 02:15:00", location: "Indianapolis Sorting Hub", desc: "Cross-dock linehaul transit sorting completed." },
      { step: "OUT_FOR_DELIVERY", timestamp: "2026-11-11 07:45:00", location: "Dallas Delivery Hub", desc: "Loaded onto last-mile delivery courier van." },
      { step: "DELIVERED", timestamp: "2026-11-11 13:20:00", location: "Customer Loading Dock", desc: "Signature captured at dock door 3. Proof of Delivery generated." }
    ],
    isValid: true
  },
  customs_delay: {
    title: "Cross-Border Customs Delay & Release",
    events: [
      { step: "ORDER_CREATED", timestamp: "2026-11-08 11:00:00", location: "Hamburg, Germany", desc: "Air Waybill (AWB) generated for international shipment." },
      { step: "PICKED_UP", timestamp: "2026-11-08 17:00:00", location: "HAM Airport Hub", desc: "Pallet accepted into international freight bond." },
      { step: "IN_TRANSIT", timestamp: "2026-11-09 08:30:00", location: "JFK International Hub", desc: "Aircraft arrived at New York cargo port." },
      { step: "EXCEPTION", timestamp: "2026-11-09 11:00:00", location: "JFK Customs Bond", desc: "Customs Hold: Missing Commercial Invoice Harmonized Tariff Code." },
      { step: "OUT_FOR_DELIVERY", timestamp: "2026-11-11 08:00:00", location: "New York Hub", desc: "Customs cleared. Released for priority road delivery." },
      { step: "DELIVERED", timestamp: "2026-11-11 15:45:00", location: "Consignee Facility", desc: "Successfully delivered with customs clearance stamp." }
    ],
    isValid: true
  },
  out_of_order_violation: {
    title: "Out-of-Order Transition Violation (Delivered before Pickup!)",
    events: [
      { step: "ORDER_CREATED", timestamp: "2026-11-10 09:00:00", location: "Seattle, WA", desc: "Order booked in WMS." },
      { step: "DELIVERED", timestamp: "2026-11-10 10:15:00", location: "Miami, FL", desc: "Carrier webhook emitted DELIVERED before parcel physical pickup!" },
      { step: "PICKED_UP", timestamp: "2026-11-10 16:00:00", location: "Seattle Hub", desc: "Carrier physical pickup scan occurred hours after delivered event." }
    ],
    isValid: false,
    errorMessage: "State Machine Invariant Broken: Transition ORDER_CREATED → DELIVERED without physical PICKED_UP or IN_TRANSIT events. Flagged as corrupted carrier webhook sequence."
  }
};

let currentLifecycleScenario = "happy_path";
let currentLifecycleStepIndex = 0;

function renderLifecycle() {
  const scenario = LIFECYCLE_SCENARIOS[currentLifecycleScenario];
  const container = document.getElementById("lifecycle-steps-container");
  const eventDetails = document.getElementById("lifecycle-event-details");
  const statusBadge = document.getElementById("lifecycle-status-badge");

  if (!container || !eventDetails) return;

  if (statusBadge) {
    if (scenario.isValid) {
      statusBadge.className = "metric-badge badge-emerald";
      statusBadge.textContent = "Valid State Machine Sequence";
    } else {
      statusBadge.className = "metric-badge";
      statusBadge.style.background = "rgba(244,63,94,0.15)";
      statusBadge.style.color = "var(--accent-rose)";
      statusBadge.textContent = "Pipeline Anomaly Detected";
    }
  }

  const stepsList = ["ORDER_CREATED", "PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"];
  
  let html = `<div class="state-machine-canvas">`;
  scenario.events.forEach((evt, idx) => {
    let stateClass = "state-step";
    if (idx === currentLifecycleStepIndex) {
      stateClass += " active";
    } else if (idx < currentLifecycleStepIndex) {
      stateClass += " completed";
    }
    if (evt.step === "EXCEPTION" || (!scenario.isValid && idx === 1)) {
      stateClass += " error";
    }

    html += `
      <div class="${stateClass}" onclick="setLifecycleStep(${idx})">
        <div class="state-circle">${idx + 1}</div>
        <div class="state-name">${evt.step}</div>
        <div class="state-time">${evt.timestamp.split(" ")[1] || ""}</div>
      </div>
    `;
  });
  html += `</div>`;
  container.innerHTML = html;

  // Active event detail box
  const activeEvent = scenario.events[currentLifecycleStepIndex];
  let errBox = "";
  if (!scenario.isValid && currentLifecycleStepIndex === 1) {
    errBox = `
      <div class="status-banner status-error" style="margin-top: 1rem;">
        <strong>Validation Failure:</strong> ${scenario.errorMessage}
      </div>
    `;
  }

  eventDetails.innerHTML = `
    <div style="background: var(--bg-tertiary); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 style="margin: 0; color: var(--accent-blue);">${activeEvent.step} (Event #${currentLifecycleStepIndex + 1} of ${scenario.events.length})</h4>
        <span style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-muted);">${activeEvent.timestamp}</span>
      </div>
      <p style="margin: 0 0 0.5rem; color: var(--text-primary); font-weight: 500;">Location: <code>${activeEvent.location}</code></p>
      <p style="margin: 0; color: var(--text-secondary); font-size: 0.95rem;">${activeEvent.desc}</p>
      ${errBox}
    </div>
  `;
}

function setLifecycleStep(idx) {
  currentLifecycleStepIndex = idx;
  renderLifecycle();
}

function nextLifecycleStep() {
  const scenario = LIFECYCLE_SCENARIOS[currentLifecycleScenario];
  if (currentLifecycleStepIndex < scenario.events.length - 1) {
    currentLifecycleStepIndex++;
    renderLifecycle();
  }
}

function prevLifecycleStep() {
  if (currentLifecycleStepIndex > 0) {
    currentLifecycleStepIndex--;
    renderLifecycle();
  }
}

// ============================================================================
// 4. Data Quality Explorer Engine
// ============================================================================

function updateQualityExplorer() {
  const slider = document.getElementById("quality-defect-slider");
  const volumeSlider = document.getElementById("quality-volume-slider");
  if (!slider || !volumeSlider) return;

  const defectPct = parseFloat(slider.value);
  const totalRecords = parseInt(volumeSlider.value);
  
  const defectCount = Math.round((defectPct / 100) * totalRecords);
  const cleanRecords = totalRecords - defectCount;
  const score = (100 - defectPct).toFixed(1);

  // Update labels
  const defectLabel = document.getElementById("defect-pct-display");
  const volumeLabel = document.getElementById("volume-display");
  const scoreDisplay = document.getElementById("quality-score-display");
  const cleanCountDisplay = document.getElementById("clean-count-display");
  const defectCountDisplay = document.getElementById("defect-count-display");
  const qualityBar = document.getElementById("quality-progress-bar");

  if (defectLabel) defectLabel.textContent = `${defectPct.toFixed(1)}%`;
  if (volumeLabel) volumeLabel.textContent = totalRecords.toLocaleString();
  if (scoreDisplay) scoreDisplay.textContent = `${score}%`;
  if (cleanCountDisplay) cleanCountDisplay.textContent = cleanRecords.toLocaleString();
  if (defectCountDisplay) defectCountDisplay.textContent = defectCount.toLocaleString();

  if (qualityBar) {
    qualityBar.style.width = `${score}%`;
    if (score >= 98.0) {
      qualityBar.style.background = "var(--accent-emerald)";
    } else if (score >= 90.0) {
      qualityBar.style.background = "var(--accent-amber)";
    } else {
      qualityBar.style.background = "var(--accent-rose)";
    }
  }

  // Dimension Breakdown metrics
  const compMetric = (100 - defectPct * 0.9).toFixed(1);
  const accMetric = (100 - defectPct * 1.1).toFixed(1);
  const uniqMetric = (100 - defectPct * 0.4).toFixed(1);
  const timeMetric = (100 - defectPct * 0.7).toFixed(1);

  const dimComp = document.getElementById("dim-completeness");
  const dimAcc = document.getElementById("dim-accuracy");
  const dimUniq = document.getElementById("dim-uniqueness");
  const dimTime = document.getElementById("dim-timeliness");

  if (dimComp) dimComp.textContent = `${Math.max(0, compMetric)}%`;
  if (dimAcc) dimAcc.textContent = `${Math.max(0, accMetric)}%`;
  if (dimUniq) dimUniq.textContent = `${Math.max(0, uniqMetric)}%`;
  if (dimTime) dimTime.textContent = `${Math.max(0, timeMetric)}%`;
}

// ============================================================================
// 5. Pipeline Troubleshooting Simulator Engine
// ============================================================================

const TROUBLESHOOT_SCENARIOS = {
  missing_id: {
    title: "Scenario 1: Missing Shipment ID in Carrier Ingestion Stream",
    service: "Kafka Ingestion Consumer",
    status: "CRITICAL_FAILURE",
    errorLog: `[2026-11-11 11:42:01.204 UTC] ERROR [consumer-worker-4] io.freightiq.ingest.CarrierWebhookConsumer:
NullPointerException: Required field 'shipment_id' evaluated to null for Carrier: 'FDX'
  at io.freightiq.pipeline.validation.ShipmentKeyValidator.assertNonEmpty(ShipmentKeyValidator.java:48)
  at io.freightiq.pipeline.transform.ShipmentEventEnricher.process(ShipmentEventEnricher.java:112)
  at org.apache.kafka.streams.processor.internals.StreamThread.runOnce(StreamThread.java:780)
[WARN] 142 records diverted to Dead Letter Queue (DLQ): dlq-shipment-events-invalid-key`,
    rootCause: "Carrier FedEx upgraded their API schema without sending the legacy 'shipment_id' header, passing instead 'master_tracking_id'. The strict validation gate rejected all 142 inbound records.",
    recommendedFix: `-- Data Ingestion Fallback Patch (SQL/dbt Transformation):
COALESCE(
  raw_payload->>'shipment_id', 
  raw_payload->>'master_tracking_id', 
  raw_payload->>'carrier_reference'
) AS normalized_shipment_id`
  },

  duplicate_webhook: {
    title: "Scenario 2: Duplicate Ingestion Causing Double-Counting in Warehouse",
    service: "PostgreSQL Analytics Warehouse",
    status: "DATA_CORRUPTION_RISK",
    errorLog: `[2026-11-11 10:14:22.091 UTC] ERROR [db-writer-1] org.postgresql.util.PSQLException:
ERROR: duplicate key value violates unique constraint "uq_shipment_events_fingerprint"
  Detail: Key (carrier_code, tracking_number, event_timestamp, event_code)=(UPS, 1Z9999999999999991, 2026-11-11 10:10:00, PU) already exists.
  Hint: Upstream webhook sender retried unacknowledged HTTP 200 payload 4 times.`,
    rootCause: "Network latency at the carrier API gateway caused 4 automatic HTTP retry attempts for the same pickup milestone, violating uniqueness constraints.",
    recommendedFix: `-- Idempotent Upsert Strategy (PostgreSQL):
INSERT INTO shipment_events (event_id, carrier_code, tracking_number, event_timestamp, status)
VALUES (:event_id, :carrier_code, :tracking_number, :event_timestamp, :status)
ON CONFLICT (carrier_code, tracking_number, event_timestamp, event_code) 
DO UPDATE SET 
  ingested_at = CURRENT_TIMESTAMP,
  retry_count = shipment_events.retry_count + 1;`
  },

  invalid_timestamp: {
    title: "Scenario 3: Non-Standard Timezone / Epoch Parsing Failure",
    service: "ETL Time Normalizer",
    status: "TRANSFORMATION_ERROR",
    errorLog: `[2026-11-11 08:31:19.412 UTC] ERROR [spark-executor-8] py4j.protocol.Py4JJavaError:
DateTimeParseException: Text '11/10/2026 04:30 PM CST' could not be parsed at index 2
  Expected format: ISO-8601 UTC (yyyy-MM-dd'T'HH:mm:ss'Z')
  Caused by: Regional logistics vendor transmitting localized non-UTC date strings.`,
    rootCause: "A local freight broker emitted non-standard US CST timestamp strings without timezone offsets, breaking the global UTC aggregation pipeline.",
    recommendedFix: `# Python / PySpark Robust Datetime Parsing Pattern:
from pyspark.sql.functions import coalesce, to_utc_timestamp, to_timestamp

df = df.withColumn("clean_event_time", coalesce(
    to_timestamp("raw_timestamp", "yyyy-MM-dd'T'HH:mm:ssXXX"),
    to_utc_timestamp(to_timestamp("raw_timestamp", "MM/dd/yyyy hh:mm a"), "America/Chicago"),
    to_timestamp("raw_timestamp", "yyyy-MM-dd HH:mm:ss")
))`
  },

  schema_mismatch: {
    title: "Scenario 4: Schema Drift — Upstream Renamed Payload Attribute",
    service: "Schema Registry / Avro Validator",
    status: "SCHEMA_DRIFT_ALERT",
    errorLog: `[2026-11-11 06:12:00.890 UTC] ERROR [schema-validator] io.confluent.kafka.schemaregistry.client.rest.exceptions.RestClientException:
Schema Incompatibility: Incompatible schema in subject 'carrier-maersk-events-value'
  Field 'gross_weight_kg' was removed and replaced by 'weight_metrics.gross_weight'
  Reader schema expected type 'double' at path '$.gross_weight_kg'`,
    rootCause: "Carrier Maersk restructured container weight metrics into a nested object without bumping major API version.",
    recommendedFix: `// Safe JSON Schema Adapter:
{
  "type": "object",
  "properties": {
    "gross_weight_kg": { "type": "number" },
    "weight_metrics": {
      "type": "object",
      "properties": {
        "gross_weight": { "type": "number" }
      }
    }
  },
  "anyOf": [
    { "required": ["gross_weight_kg"] },
    { "required": ["weight_metrics"] }
  ]
}`
  },

  api_timeout: {
    title: "Scenario 5: Carrier Rate Limit (HTTP 429) & Gateway Timeout (504)",
    service: "Carrier Poller Dispatcher",
    status: "RATE_LIMIT_BLOCKED",
    errorLog: `[2026-11-11 05:00:21.002 UTC] WARN [http-client-pool-3] io.freightiq.poller.CarrierApiClient:
HTTP/1.1 429 Too Many Requests received from https://api.carrier.com/v2/track
  Retry-After: 120 seconds
  X-RateLimit-Remaining: 0
  X-RateLimit-Limit: 1000 requests / 60 seconds
  All 12 concurrent workers paused.`,
    rootCause: "High-volume batch polling job exhausted carrier API rate quota, triggering a 2-minute API lockout.",
    recommendedFix: `# Token Bucket with Jittered Exponential Backoff (Python):
import time, random, requests

def fetch_tracking_with_backoff(url, max_retries=5):
    for attempt in range(max_retries):
        resp = requests.get(url)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
            jitter = random.uniform(0.5, 1.5)
            time.sleep(retry_after + jitter)
            continue
        return resp.json()`
  },

  fk_violation: {
    title: "Scenario 6: Foreign Key Constraint Error on Hub Location ID",
    service: "Warehouse Ingestion Loader",
    status: "DATABASE_CONSTRAINT_ERROR",
    errorLog: `[2026-11-11 03:22:45.311 UTC] ERROR [batch-loader-2] org.postgresql.util.PSQLException:
ERROR: insert or update on table "shipment_milestones" violates foreign key constraint "fk_milestone_hub_code"
  Detail: Key (hub_code)=(US-ORD-EXP9) is not present in table "dim_logistics_hubs".`,
    rootCause: "A newly opened carrier distribution center code 'US-ORD-EXP9' was referenced in a tracking event before master data dimensions were synchronized.",
    recommendedFix: `-- Foreign Key Auto-Healing Staging Pattern:
-- 1. Insert placeholder missing hubs into dimension table:
INSERT INTO dim_logistics_hubs (hub_code, hub_name, status)
SELECT DISTINCT s.hub_code, 'AUTO-DISCOVERED PENDING ENRICHMENT', 'PROVISIONAL'
FROM stg_shipment_events s
WHERE s.hub_code NOT IN (SELECT hub_code FROM dim_logistics_hubs);

-- 2. Then commit shipment milestones cleanly without FK crash.`
  }
};

let currentTroubleshootScenario = "missing_id";

function renderTroubleshootSimulator() {
  const scenario = TROUBLESHOOT_SCENARIOS[currentTroubleshootScenario];
  const title = document.getElementById("troubleshoot-title");
  const service = document.getElementById("troubleshoot-service");
  const log = document.getElementById("troubleshoot-log");
  const rootCause = document.getElementById("troubleshoot-root-cause");
  const fix = document.getElementById("troubleshoot-fix");
  const statusBadge = document.getElementById("troubleshoot-status-badge");
  const pipelineState = document.getElementById("pipeline-sim-diagram");

  if (!title || !log) return;

  title.textContent = scenario.title;
  if (service) service.textContent = `Failing Service: ${scenario.service}`;
  log.textContent = scenario.errorLog;
  if (rootCause) rootCause.textContent = scenario.rootCause;
  if (fix) fix.textContent = scenario.recommendedFix;

  if (statusBadge) {
    statusBadge.className = "metric-badge";
    statusBadge.style.background = "rgba(244,63,94,0.15)";
    statusBadge.style.color = "var(--accent-rose)";
    statusBadge.textContent = scenario.status;
  }

  if (pipelineState) {
    pipelineState.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; font-size: 0.8rem; overflow-x: auto; padding: 1rem 0;">
        <div style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--accent-emerald); color: var(--accent-emerald);">✓ Carrier API</div>
        <div style="color: var(--text-muted);">→</div>
        <div style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--accent-emerald); color: var(--accent-emerald);">✓ Ingestion Queue</div>
        <div style="color: var(--text-muted);">→</div>
        <div style="background: rgba(244,63,94,0.2); padding: 8px 12px; border-radius: 6px; border: 2px solid var(--accent-rose); color: var(--accent-rose); font-weight: 700; box-shadow: 0 0 15px rgba(244,63,94,0.4);">💥 ${scenario.service} [FAILED]</div>
        <div style="color: var(--text-muted);">→</div>
        <div style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-subtle); color: var(--text-muted);">⏳ Warehouse Analytics</div>
      </div>
    `;
  }
}

function resolveTroubleshootIncident() {
  const statusBadge = document.getElementById("troubleshoot-status-badge");
  const pipelineState = document.getElementById("pipeline-sim-diagram");
  const log = document.getElementById("troubleshoot-log");

  if (statusBadge) {
    statusBadge.className = "metric-badge badge-emerald";
    statusBadge.textContent = "RESOLVED & VERIFIED";
  }

  if (pipelineState) {
    pipelineState.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; font-size: 0.8rem; overflow-x: auto; padding: 1rem 0;">
        <div style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--accent-emerald); color: var(--accent-emerald);">✓ Carrier API</div>
        <div style="color: var(--text-muted);">→</div>
        <div style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--accent-emerald); color: var(--accent-emerald);">✓ Ingestion Queue</div>
        <div style="color: var(--text-muted);">→</div>
        <div style="background: rgba(16,185,129,0.15); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--accent-emerald); color: var(--accent-emerald); font-weight: 700;">✓ Validation Engine (Patch Applied)</div>
        <div style="color: var(--text-muted);">→</div>
        <div style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--accent-emerald); color: var(--accent-emerald);">✓ Warehouse Analytics Synced</div>
      </div>
    `;
  }

  if (log) {
    log.textContent = `[2026-11-11 11:45:00.000 UTC] INFO Remediation script applied successfully.
[INFO] Re-processing diverted records from Dead Letter Queue (DLQ)...
[INFO] 142 records parsed and committed with 0 errors.
[SUCCESS] Pipeline backpressure cleared. Health status: 100% HEALTHY.`;
  }
}

// ============================================================================
// Global Initializer & Event Listeners
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  // SQL Playground Events
  const sqlPreset = document.getElementById("sql-preset-select");
  if (sqlPreset) {
    sqlPreset.addEventListener("change", (e) => {
      const q = SQL_PRESETS[e.target.value];
      const editor = document.getElementById("sql-editor");
      if (q && editor) {
        editor.value = q;
        runSqlPlayground();
      }
    });
  }

  const runSqlBtn = document.getElementById("run-sql-btn");
  if (runSqlBtn) {
    runSqlBtn.addEventListener("click", runSqlPlayground);
  }

  // JSON Validator Events
  const jsonPreset = document.getElementById("json-preset-select");
  if (jsonPreset) {
    jsonPreset.addEventListener("change", (e) => {
      const p = JSON_PAYLOAD_PRESETS[e.target.value];
      const editor = document.getElementById("json-editor");
      if (p && editor) {
        editor.value = p.json;
        runJsonSchemaValidator();
      }
    });
  }

  const validateJsonBtn = document.getElementById("validate-json-btn");
  if (validateJsonBtn) {
    validateJsonBtn.addEventListener("click", runJsonSchemaValidator);
  }

  // Lifecycle Events
  const lifecycleScenarioSelect = document.getElementById("lifecycle-scenario-select");
  if (lifecycleScenarioSelect) {
    lifecycleScenarioSelect.addEventListener("change", (e) => {
      currentLifecycleScenario = e.target.value;
      currentLifecycleStepIndex = 0;
      renderLifecycle();
    });
  }

  const nextStepBtn = document.getElementById("lifecycle-next-btn");
  if (nextStepBtn) nextStepBtn.addEventListener("click", nextLifecycleStep);
  const prevStepBtn = document.getElementById("lifecycle-prev-btn");
  if (prevStepBtn) prevStepBtn.addEventListener("click", prevLifecycleStep);

  // Quality Explorer Events
  const qualitySlider = document.getElementById("quality-defect-slider");
  if (qualitySlider) qualitySlider.addEventListener("input", updateQualityExplorer);
  const volumeSlider = document.getElementById("quality-volume-slider");
  if (volumeSlider) volumeSlider.addEventListener("input", updateQualityExplorer);

  // Troubleshooter Events
  const tsScenarioSelect = document.getElementById("troubleshoot-scenario-select");
  if (tsScenarioSelect) {
    tsScenarioSelect.addEventListener("change", (e) => {
      currentTroubleshootScenario = e.target.value;
      renderTroubleshootSimulator();
    });
  }

  const resolveBtn = document.getElementById("troubleshoot-resolve-btn");
  if (resolveBtn) {
    resolveBtn.addEventListener("click", resolveTroubleshootIncident);
  }

  // Copy code button handler
  document.querySelectorAll(".copy-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const codeBlock = btn.closest(".code-block-wrapper")?.querySelector("code");
      if (codeBlock) {
        navigator.clipboard.writeText(codeBlock.innerText).then(() => {
          const originalText = btn.innerHTML;
          btn.innerHTML = `✓ Copied!`;
          btn.style.color = "var(--accent-emerald)";
          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.color = "";
          }, 2000);
        });
      }
    });
  });

  // Mobile navigation toggle
  const mobileBtn = document.querySelector(".mobile-menu-btn");
  const navLinks = document.querySelector(".nav-links");
  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener("click", () => {
      const isVisible = navLinks.style.display === "flex";
      navLinks.style.display = isVisible ? "none" : "flex";
      if (!isVisible) {
        navLinks.style.flexDirection = "column";
        navLinks.style.position = "absolute";
        navLinks.style.top = "4.25rem";
        navLinks.style.left = "0";
        navLinks.style.right = "0";
        navLinks.style.background = "var(--bg-secondary)";
        navLinks.style.padding = "1.5rem";
        navLinks.style.borderBottom = "1px solid var(--border-medium)";
      }
    });
  }

  // Initial runs
  if (document.getElementById("sql-editor")) runSqlPlayground();
  if (document.getElementById("json-editor")) runJsonSchemaValidator();
  if (document.getElementById("lifecycle-steps-container")) renderLifecycle();
  if (document.getElementById("quality-defect-slider")) updateQualityExplorer();
  if (document.getElementById("troubleshoot-title")) renderTroubleshootSimulator();
});
