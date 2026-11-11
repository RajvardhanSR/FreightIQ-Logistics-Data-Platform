"""
Tools Data & Metadata
Contains definitions and UI components for the 5 interactive developer tools.
"""

TOOLS = [
    {
        "slug": "sql-playground",
        "url_path": "tools/sql-playground.html",
        "title": "SQL Validation Playground: Logistics Dataset Sandbox",
        "meta_title": "SQL Validation Playground for Logistics Data | FreightIQ",
        "meta_desc": "Interactive, client-side SQL playground preloaded with shipment datasets. Run validation queries for NULLs, duplicates, and range boundaries in real time.",
        "headline": "SQL Validation Playground",
        "badge": "Interactive Engine",
        "description": "Execute validation assertions directly in your browser against synthetic multimodal freight datasets. Test boundary rules, duplicate detection, and chronological invariants with zero database credentials exposed.",
        "tool_id": "sql-playground"
    },
    {
        "slug": "json-validator",
        "url_path": "tools/json-validator.html",
        "title": "JSON Shipment Schema Validator: Real-Time Spec Enforcement",
        "meta_title": "JSON Shipment Schema Validator (Draft-07 & 2020-12) | FreightIQ",
        "meta_desc": "Real-time client-side JSON Schema validator for carrier webhook payloads. Validate required keys, ISO-8601 timestamps, status enums, and physics boundaries.",
        "headline": "JSON Shipment Schema Validator",
        "badge": "Draft-07 & 2020-12",
        "description": "Verify carrier webhook payloads against the FreightIQ Logistics Webhook Specification. Real-time syntax checking, required field assertions, and human-readable path error diagnosis.",
        "tool_id": "json-validator"
    },
    {
        "slug": "lifecycle-visualizer",
        "url_path": "tools/lifecycle-visualizer.html",
        "title": "Shipment Lifecycle Visualizer: Interactive State Machine",
        "meta_title": "Shipment Lifecycle State Machine Visualizer | FreightIQ",
        "meta_desc": "Step through interactive logistics event streams. Inspect carrier milestones, valid state transitions, and detect out-of-order pipeline anomalies.",
        "headline": "Shipment Lifecycle Visualizer",
        "badge": "FSM Simulation",
        "description": "Explore multimodal shipment progression through a deterministic Finite State Machine (FSM). Step through realistic carrier event logs and observe how pipeline validation gates flag out-of-order anomalies.",
        "tool_id": "lifecycle-visualizer"
    },
    {
        "slug": "quality-explorer",
        "url_path": "tools/quality-explorer.html",
        "title": "Data Quality Explorer: 6 Dimensions Simulation",
        "meta_title": "Freight Data Quality Explorer: 6 Dimensions Simulator | FreightIQ",
        "meta_desc": "Interactive simulator for freight data quality dimensions. Adjust dataset volumes and defect ratios to observe real-time DQS scores and dimension breakdowns.",
        "headline": "Data Quality Explorer",
        "badge": "Real-Time Metric Math",
        "description": "Simulate and visualize the impact of data defects across high-velocity carrier streams. Dynamically tweak defect sliders to evaluate overall Data Quality Score (DQS) impact.",
        "tool_id": "quality-explorer"
    },
    {
        "slug": "troubleshooting-simulator",
        "url_path": "tools/troubleshooting-simulator.html",
        "title": "Pipeline Troubleshooting Simulator: Root Cause & Triage",
        "meta_title": "Logistics Pipeline Troubleshooting Simulator | FreightIQ",
        "meta_desc": "Simulate real-world logistics pipeline outages. Inspect error logs, identify root causes, and execute remediation scripts to resolve incidents in real time.",
        "headline": "Pipeline Troubleshooting Simulator",
        "badge": "Incident Triage Sandbox",
        "description": "Experience hands-on incident response for 6 real-world freight pipeline outages: missing shipment IDs, webhook duplicates, unparseable timestamps, schema drift, and carrier rate limits.",
        "tool_id": "troubleshooting-simulator"
    }
]
