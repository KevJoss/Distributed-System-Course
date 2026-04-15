# 🗂️ Workshop 7: XML Schema Validation & Message Routing

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![lxml](https://img.shields.io/badge/lxml-XML%20Processing-green?style=for-the-badge)
![XSD](https://img.shields.io/badge/XSD-Schema%20Validation-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

This workshop simulates a **distributed message pipeline** using **XML as the data interchange format**, validating messages at each stage with **XSD schemas** (via `lxml`). It models the internal flow of a crop-disease diagnostic platform where image upload requests are validated, transformed, and routed through a Redis-like queue system.

---

## 🎯 Objectives

- Understand how **XML Schema Definition (XSD)** enforces structural and type contracts between distributed services.
- Simulate a **two-stage validation pipeline**: external ingestion (Broker) → internal routing (Router Worker).
- Practice the transformation of an **external XML payload** into a **sanitized internal XML message**.
- Test both **valid** and **malformed/malicious** input payloads.

---

## 📂 File Structure

```graphql
Workshop_7_XML/
├── 📁 schemas/
│   ├── ingestion.xsd   # Schema for external client upload requests (Broker input)
│   └── internal.xsd    # Schema for internal routing tasks (Router Worker input)
└── test_parser.py      # Full pipeline simulation with test cases
```

---

## 🏗️ Architecture Overview

The simulation mimics the following distributed flow:

```
[External Client / UI]
        │
        │  UploadRequest XML
        ▼
┌──────────────────┐
│  FastAPI Broker  │  ← validates against ingestion.xsd
│  (simulated)     │  ← generates internal DiagnosticTask XML
└────────┬─────────┘
         │  DiagnosticTask XML → Redis (router_queue)
         ▼
┌──────────────────────┐
│  Router Worker       │  ← validates against internal.xsd
│  (simulated)         │  ← simulates AI crop classification
└──────────────────────┘
         │
         ▼
   [tomato_queue / potato_queue / dropped]
```

---

## 📄 Schemas

### `ingestion.xsd` — External Upload Request

Validates the payload sent by the UI/client to the Broker:

| Field | Type | Constraint |
|---|---|---|
| `RequestID` | `xs:positiveInteger` | Required |
| `Client/Username` | `xs:string` | Required |
| `Timestamp` | `xs:dateTime` | Must be full ISO 8601 |
| `AttachedImage/ImageID` | `xs:positiveInteger` | Required |
| `AttachedImage/OriginalFileName` | `xs:string` | Required |
| `Status` | `UploadStatusEnum` | Must be `"Submitted"` |

### `internal.xsd` — Internal Diagnostic Task

Validates the message placed on the internal Redis queue by the Broker:

| Field | Type | Constraint |
|---|---|---|
| `TaskID` | `xs:positiveInteger` | Required |
| `Payload/ImageID` | `xs:positiveInteger` | Required |
| `Payload/ImagePath` | `xs:string` | Required |
| `Payload/DetectedCrop` | `CropTypeEnum` | `Tomato`, `Potato`, `Background`, `Pending` |
| `State/CurrentStatus` | `StatusEnum` | `Queued`, `Routing`, `Completed`, `Invalid` |

---

## 🔑 Key Components

### `XMLValidatorWrapper`
A reusable class that loads an `.xsd` schema at construction time and exposes a `validate_and_parse()` method. Returns a tuple `(is_valid: bool, doc: etree._Element | None, message: str)`.

```python
validator = XMLValidatorWrapper("schemas/ingestion.xsd")
is_valid, doc, msg = validator.validate_and_parse(xml_string)
```

### `fastapi_broker_wrapper(xml_payload)`
Simulates the **Broker endpoint**:
1. Validates the incoming `UploadRequest` XML against `ingestion.xsd`.
2. On success, extracts fields and generates a `DiagnosticTask` internal XML.
3. Prints the internal XML (simulating enqueue to Redis).

### `router_worker_wrapper(internal_xml)`
Simulates the **Router Worker**:
1. Consumes and validates the `DiagnosticTask` XML against `internal.xsd`.
2. Simulates an AI crop classification result.
3. Routes the task to the appropriate downstream queue (e.g., `tomato_queue`), or drops it if `Background`.

---

## ▶️ How to Run

**Requirements:**
```bash
pip install lxml
```

**Execute from the `Workshop_7_XML/` directory:**
```bash
python test_parser.py
```

**Expected output (Test Case 1 — Valid Upload):**
```
=== TEST CASE 1: VALID UPLOAD ===

--- [BROKER] Receiving external request ---
[BROKER] 202 Accepted. Request: 1. Image stored as: leaf.jpg
[BROKER] Internal XML generated. Enqueueing to Redis (router_queue)...
INTERNAL XML:
 ...

--- [ROUTER WORKER] Consuming from Redis ---
[ROUTER] Valid payload. Task: 1. Image: /shared/leaf.jpg
[ROUTER] Simulating AI classification...
[ROUTER] Result: Tomato. Routing to tomato_queue.
```

---

## 🧪 Test Cases

| # | Description | Expected Result |
|---|---|---|
| 1 | Valid `UploadRequest` XML | Broker accepts → Router routes to `tomato_queue` |
| 2 | Malformed XML (`RequestID` as string, invalid `Status`) | Broker rejects with `400 Bad Request` |

---

*Part of the Distributed Systems course at Yachay Tech — Final Project Pipeline Simulation.*
