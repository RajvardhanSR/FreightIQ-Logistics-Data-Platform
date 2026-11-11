"""
Global Site Metadata and Navigation Registry
Domain: https://rajvardhansinghrathore.in
Brand: FreightIQ
"""

SITE_CONFIG = {
    "brand_name": "FreightIQ",
    "tagline": "The Engineering Behind Logistics Data.",
    "domain": "https://rajvardhansinghrathore.in",
    "author_name": "Rajvardhan Singh Rathore",
    "author_title": "Logistics Data Architect",
    "author_bio": "Logistics data engineer and solutions architect specializing in high-throughput freight data pipelines, EDI 214 integration, and supply chain telemetry validation.",
    "current_year": "2026",
    "category": "Logistics Data Analytics & Freight Data Engineering"
}

NAVIGATION = [
    {
        "title": "Data Quality",
        "url": "/data-quality",
        "sub_items": [
            {"title": "Overview Hub", "url": "/data-quality"},
            {"title": "6 Core Dimensions", "url": "/data-quality/dimensions"},
            {"title": "Data Completeness", "url": "/data-quality/completeness"},
            {"title": "Data Accuracy", "url": "/data-quality/accuracy"},
            {"title": "Data Consistency", "url": "/data-quality/consistency"},
            {"title": "Data Timeliness", "url": "/data-quality/timeliness"},
            {"title": "Data Uniqueness", "url": "/data-quality/uniqueness"}
        ]
    },
    {
        "title": "Shipment Data",
        "url": "/shipment-data",
        "sub_items": [
            {"title": "Overview Hub", "url": "/shipment-data"},
            {"title": "Shipment Lifecycle", "url": "/shipment-data/lifecycle"},
            {"title": "Master Shipment IDs", "url": "/shipment-data/shipment-ids"},
            {"title": "Carrier Tracking Numbers", "url": "/shipment-data/tracking-numbers"},
            {"title": "Shipment Status Events", "url": "/shipment-data/status-events"},
            {"title": "Delivery Date Logic", "url": "/shipment-data/delivery-dates"},
            {"title": "Geospatial Location Data", "url": "/shipment-data/location-data"}
        ]
    },
    {
        "title": "Validation",
        "url": "/validation",
        "sub_items": [
            {"title": "Overview Hub", "url": "/validation"},
            {"title": "SQL Validation Techniques", "url": "/validation/sql-techniques"},
            {"title": "NULL Validation in SQL", "url": "/validation/null-validation-sql"},
            {"title": "Duplicate Record Detection", "url": "/validation/duplicate-record-detection"},
            {"title": "Data Type Enforcement", "url": "/validation/data-type-validation"},
            {"title": "Range Boundary Validation", "url": "/validation/range-boundary-validation"},
            {"title": "JSON Schema Validation", "url": "/validation/json-schema-validation"},
            {"title": "Carrier API Validation", "url": "/validation/api-validation"}
        ]
    },
    {
        "title": "Troubleshooting",
        "url": "/troubleshooting",
        "sub_items": [
            {"title": "Overview Hub", "url": "/troubleshooting"},
            {"title": "Pipeline Quality & SLOs", "url": "/troubleshooting/pipeline-quality"},
            {"title": "ETL Source-to-Target", "url": "/troubleshooting/etl-validation"},
            {"title": "Real-Time Monitoring", "url": "/troubleshooting/real-time-monitoring"},
            {"title": "Automated Testing", "url": "/troubleshooting/automated-testing"},
            {"title": "Pipeline Data Mismatches", "url": "/troubleshooting/pipeline-data-mismatches"},
            {"title": "Common SQL Errors", "url": "/troubleshooting/sql-errors"},
            {"title": "Carrier API Errors", "url": "/troubleshooting/api-errors"},
            {"title": "Database Constraint Violations", "url": "/troubleshooting/database-constraint-errors"}
        ]
    },
    {
        "title": "Developer Tools",
        "url": "/tools",
        "sub_items": [
            {"title": "Tools Hub", "url": "/tools"},
            {"title": "SQL Playground", "url": "/tools/sql-playground"},
            {"title": "JSON Schema Validator", "url": "/tools/json-validator"},
            {"title": "Lifecycle Visualizer", "url": "/tools/lifecycle-visualizer"},
            {"title": "Data Quality Explorer", "url": "/tools/quality-explorer"},
            {"title": "Troubleshooting Simulator", "url": "/tools/troubleshooting-simulator"}
        ]
    }
]
