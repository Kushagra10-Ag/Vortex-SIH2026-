# BIZmate — Master Project Plan & AI Development Guide

> **Document Purpose**: This file serves as the single source of truth for the entire BIZmate project. Any AI assistant (Antigravity, ChatGPT, Claude, Cursor, Copilot, etc.) or developer joining this codebase should read this file first to understand the architecture, design principles, API contracts, database schema, edge AI subsystem, and phased milestones.

---

## 1. Project Vision & Overview

**BIZmate** is an intelligent, AI-powered Kirana and retail store management platform. It transforms traditional small retail stores into smart, automated micro-warehouses by combining:
1. **Core Retail Operations**: Fast POS billing, inventory tracking, batch/expiry management, and PDF tax invoice generation.
2. **AI & Forecasting**: 7-day machine learning sales forecasting (scikit-learn `RandomForestRegressor`) and an executive LLM assistant (Google Gemini) with real-time store context.
3. **IoT & Edge Store Monitoring**: Real-time camera event detection (crowd surge, shelf void detection, queue overflow, theft signals), smart load-cell shelf monitoring, environmental sensors (temperature, humidity), ultrasonic/IR stock depth sensors, and automated footfall counting.

### Tech Stack Summary
- **Frontend**: React Native (Expo Router v5), TypeScript, React Native SVG, Lucide/Vector Icons.
- **Backend**: Python 3.13, Flask 3.1, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-JWT-Extended, Flask-CORS.
- **Database**: PostgreSQL (SQLAlchemy ORM) with connection string via `DATABASE_URL`.
- **Edge AI & Computer Vision**: Python 3, OpenCV, Ultralytics YOLOv11 / YOLOv8, ByteTrack/DeepSORT tracking.
- **Machine Learning**: scikit-learn (`RandomForestRegressor`), NumPy, Pandas, Joblib.
- **Generative AI**: Google Gemini API (`gemini-1.5-flash` / Google Generative AI SDK).
- **Reporting & Documents**: ReportLab (vector PDF billing invoice generation).

---

## 2. System Architecture & Information Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND LAYER                                   │
│  React Native / Expo App (iOS, Android, Web)                                │
│  ├── POS Billing Screen & PDF Invoicing                                     │
│  ├── Inventory & Expiry Matrix Tracker                                      │
│  ├── Analytics Dashboard (KPIs, Trends, Category Charts)                    │
│  ├── AI Business Chatbot (Gemini Assistant)                                 │
│  └── Store IoT & Edge Monitoring Dashboard (Live Occupancy & Shelves)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST (JSON)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND LAYER (Flask API)                        │
│  run.py -> create_app() [Port 5000]                                         │
│  ├── Middleware: auth.py (JWT), permissions.py (RBAC), error_handler.py    │
│  ├── Routes (11 Blueprints):                                                │
│  │   /auth, /inventory, /billing, /analytics, /ai, /chatbot,               │
│  │   /dashboard, /monitoring, /alerts, /devices, /sensors                   │
│  ├── Controllers: Request routing & validation                              │
│  ├── Services: Pure business logic & orchestration                         │
│  └── Utilities: PDF generator, structured logging, standardized responses   │
└──────────────────┬──────────────────────────────────────▲───────────────────┘
                   │ SQLAlchemy ORM                       │ Ingest REST API
                   ▼                                      │ (Events & Telemetry)
┌──────────────────────────────────────┐    ┌─────────────┴───────────────────┐
│         POSTGRESQL DATABASE          │    │         EDGE-AI SUBSYSTEM       │
│  • users         • products          │    │  edge-ai/ (Local Device / Pi)   │
│  • bills         • bill_items        │    │  ├── camera/ (RTSP/IP stream)   │
│  • devices       • camera_events     │    │  ├── ai/ (YOLOv11 & Trackers)   │
│  • shelf_status  • sensor_readings   │    │  ├── sensors/ (IR, Ultrasonic)  │
│  • footfall      • alerts            │    │  ├── events/ (Payload builder)  │
│                                      │    │  └── communication/ (REST/WS)   │
└──────────────────────────────────────┘    └─────────────────────────────────┘
```

---

## 3. Complete Codebase Structure

```
SIH2026/
├── plan.md                     # Master project plan & AI developer reference (THIS FILE)
├── design.md                   # Frontend UI/UX design system, screens & checkpoints
├── README.md                   # Repository overview & setup instructions
│
├── backend/                    # Core Flask REST API & Database Service
│   ├── run.py                  # Server entrypoint (runs on port 5000)
│   ├── config.py               # Root configuration (reads .env via python-dotenv)
│   ├── db.py                   # Root SQLAlchemy database export
│   ├── requirements.txt        # Backend dependencies
│   ├── .env                    # Environment variables (DB URL, JWT Secret, Gemini Key)
│   │
│   ├── ai_models/
│   │   └── sales_model.pkl     # Pre-trained RandomForestRegressor for 7-day sales
│   │
│   ├── migrations/             # Alembic migration scripts
│   │
│   └── app/
│       ├── __init__.py         # App factory (create_app), extension & blueprint registry
│       ├── config.py           # App Config class fallback
│       ├── db.py               # db = SQLAlchemy()
│       ├── gen_ai.py           # Google Gemini API client
│       ├── utils.py            # Original PDF invoice generator (ReportLab)
│       │
│       ├── models/             # SQLAlchemy ORM Models
│       │   ├── __init__.py     # Re-exports all models cleanly
│       │   ├── user.py         # User credentials, roles (owner, admin, cashier)
│       │   ├── product.py      # SKU, pricing, stock, batch, expiry dates
│       │   ├── bill.py         # Invoices, customer phone, subtotal, tax, discounts
│       │   ├── bill_item.py    # Line items with price snapshots
│       │   ├── device.py       # Hardware devices (cameras, sensor hubs, gateways)
│       │   ├── camera_event.py # Vision detections, confidence scores, bounding boxes
│       │   ├── sensor_reading.py# Temperature, humidity, shelf weight readings
│       │   ├── shelf_status.py # Smart shelves, fill percentage, estimated capacity
│       │   ├── footfall.py     # Hourly visitor counts, entry/exit, store occupancy
│       │   └── alert.py        # System and IoT alerts (severity, status, resolution)
│       │
│       ├── services/           # Business Logic Layer
│       │   ├── auth_service.py # Authentication, JWT generation, password hashes
│       │   ├── inventory_service.py # Stock CRUD, batching, low stock queries
│       │   ├── billing_service.py   # Bill creation, stock decrement, PDF generation
│       │   ├── analytics_service.py # Revenue trends, monthly graphs, expiry risks
│       │   ├── chatbot_service.py   # Gemini prompt engineering with store context
│       │   ├── ai_service.py        # 7-day ML forecasting model predictor
│       │   ├── dashboard_service.py # Consolidated KPI overview & telemetry
│       │   ├── monitoring_service.py# Real-time IoT metrics, cameras, footfall
│       │   ├── alert_service.py     # Alert creation, filtering, resolution
│       │   ├── device_service.py    # Device registration, status, heartbeats
│       │   ├── sensor_service.py    # Ingestion, threshold checks, anomaly detection
│       │   └── edge_ai_service.py   # Vision metadata parsing, sensor fusion
│       │
│       ├── controllers/        # Request Handlers
│       │   ├── auth_controller.py
│       │   ├── inventory_controller.py
│       │   ├── billing_controller.py
│       │   ├── analytics_controller.py
│       │   ├── chatbot_controller.py
│       │   ├── ai_controller.py
│       │   ├── dashboard_controller.py
│       │   ├── monitoring_controller.py
│       │   ├── alert_controller.py
│       │   ├── device_controller.py
│       │   └── sensor_controller.py
│       │
│       ├── routes/             # Flask Blueprints
│       │   ├── auth_routes.py        # /auth/register, /auth/login
│       │   ├── inventory_routes.py   # /inventory/products, /add-product, etc.
│       │   ├── billing_routes.py     # /billing/create-bill, /bills, /bill-pdf/<id>
│       │   ├── analytics_routes.py   # /analytics/dashboard, /total-sales, etc.
│       │   ├── ai_routes.py          # /ai/predict
│       │   ├── chatbot_routes.py     # /chatbot/chat
│       │   ├── dashboard_routes.py   # /dashboard/overview, /dashboard/telemetry
│       │   ├── monitoring_routes.py  # /monitoring/realtime, /shelves, /footfall
│       │   ├── alert_routes.py       # /alerts, /alerts/counts, /read, /resolve
│       │   ├── device_routes.py      # /devices/register, /list, /heartbeat
│       │   └── sensor_routes.py      # /sensors/readings, /latest, /summary
│       │
│       ├── utils/              # Modular Utilities
│       │   ├── __init__.py     # Re-exports helpers & backward-compatible PDF engine
│       │   ├── helpers.py      # Datetime parsers, UUID generators, math helpers
│       │   ├── validators.py   # Input validation rules
│       │   ├── constants.py    # Enums (DeviceType, AlertSeverity, UserRole)
│       │   ├── logger.py       # Centralized formatted logger
│       │   └── response.py     # success_response, error_response, paginated_response
│       │
│       ├── middleware/         # Custom Middleware
│       │   ├── __init__.py
│       │   ├── auth.py         # @token_required decorator
│       │   ├── permissions.py  # @roles_required, @admin_required, @owner_required
│       │   └── error_handler.py# Global exception, 404, 500, SQLAlchemy rollback handler
│       │
│       └── database/           # DB Utilities & Seeders
│           ├── __init__.py
│           ├── seed.py         # Comprehensive Kirana & IoT demo database seeder
│           └── migrations/     # Migration documentation
│
├── edge-ai/                    # Edge AI, Vision & Sensor Telemetry Pipeline
│   ├── app.py                  # Main entry point daemon
│   ├── config.py               # Edge configuration (backend URL, camera RTSP, sensor pins)
│   ├── requirements.txt        # Edge dependencies (opencv-python, ultralytics, requests)
│   ├── README.md               # Setup instructions for Jetson / Pi / PC
│   │
│   ├── camera/                 # Video Stream Ingestion
│   │   ├── __init__.py
│   │   ├── mobile_camera.py    # Connect to Android camera/IP stream (IP Webcam/RTSP)
│   │   ├── stream_handler.py   # Frame reader and buffer manager
│   │   ├── frame_processor.py  # Resize, normalize, color space conversion
│   │   └── reconnect.py        # Stream watchdog & auto-reconnect logic
│   │
│   ├── ai/                     # Computer Vision & Detection Pipeline
│   │   ├── __init__.py
│   │   ├── model_loader.py     # Singleton YOLO model weight loader
│   │   ├── people_detector.py  # Person detection & store occupancy estimation
│   │   ├── queue_detector.py   # Billing counter queue length & wait time analysis
│   │   ├── shelf_detector.py   # Shelf empty-slot / out-of-stock vision detection
│   │   ├── tracker.py          # Multi-object tracking (ByteTrack) across frames
│   │   └── inference.py        # Unified inference execution pipeline
│   │
│   ├── sensors/                # Hardware & Mock Sensor Interface
│   │   ├── __init__.py
│   │   ├── sensor_manager.py   # Central coordinator for all sensors
│   │   ├── ir_sensor.py        # IR break-beam sensor (aisle traffic/entry)
│   │   ├── ultrasonic_sensor.py# Ultrasonic distance sensor (shelf depth/fill)
│   │   ├── mock_sensor.py      # Simulator generating realistic demo telemetry
│   │   └── sensor_sender.py    # Transmits sensor readings to backend `/sensors/readings`
│   │
│   ├── events/                 # Event Structuring & Trigger Engine
│   │   ├── __init__.py
│   │   ├── event_builder.py    # Packages detections into standardized JSON payloads
│   │   ├── event_sender.py     # Dispatches events to backend `/monitoring/camera-events`
│   │   └── event_types.py      # Event type constants and threshold mappings
│   │
│   ├── communication/          # Networking & Protocol Layer
│   │   ├── __init__.py
│   │   ├── backend_client.py   # REST API client with retry & error handling
│   │   └── websocket_client.py # Low-latency WebSocket client for live telemetry
│   │
│   ├── utils/                  # Edge Utility Helpers
│   │   ├── __init__.py
│   │   ├── logger.py           # Timestamped structured edge logging
│   │   ├── helpers.py          # Time, FPS, and calculation helpers
│   │   ├── constants.py        # Edge constants and sensor boundaries
│   │   └── image_utils.py      # Bounding box drawing, cropping, base64 conversion
│   │
│   ├── weights/                # Neural Network Weights & Labels
│   │   ├── yolov11.pt          # YOLOv11 model weights file
│   │   └── coco.names          # Class names list (person, bottle, cup, etc.)
│   │
│   ├── tests/                  # Unit and integration tests for edge modules
│   └── logs/                   # Runtime execution logs
│
└── frontend/                   # React Native Expo Application
    ├── app/                    # Expo Router file-based screens
    │   ├── _layout.tsx         # Root stack layout
    │   ├── login.tsx           # Authentication screen
    │   └── (tabs)/             # Bottom navigation tabs
    │       ├── index.tsx       # Home / Overview
    │       ├── inventory.tsx   # Stock management
    │       ├── billing.tsx     # POS terminal & invoice creation
    │       ├── analytics.tsx   # Visual charts & KPIs
    │       └── chatbot.tsx     # AI assistant conversation
    ├── components/             # Reusable UI widgets (BarChart, LineChart, PieChart)
    ├── constants/              # theme.ts (Colors, fonts, radiuses)
    └── services/
        └── api.ts              # API client connecting React Native to Flask
```

---

## 4. API Endpoints Catalog

### Authentication (`/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register new user with email, name, password, role |
| `POST` | `/auth/login` | Login user, returns JWT token & user profile |

### Inventory (`/inventory`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/inventory/products` | Retrieve all inventory products with stock levels & batches |
| `POST` | `/inventory/add-product` | Add new product SKU |
| `PUT` | `/inventory/update-product/<id>` | Update product details, pricing, stock |
| `DELETE` | `/inventory/delete-product/<id>` | Remove product from inventory |

### Billing & POS (`/billing`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/billing/create-bill` | Generate bill, auto-decrement inventory stock |
| `GET` | `/billing/bills` | List all historical bills with customer & item details |
| `GET` | `/billing/bill-pdf/<id>` | Download professionally formatted PDF invoice |

### Analytics & AI (`/analytics`, `/ai`, `/chatbot`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/total-sales` | Return total cumulative revenue |
| `GET` | `/analytics/dashboard` | Aggregated analytics (KPIs, revenue trend, monthly sales, expiry matrix) |
| `GET` | `/analytics/product-performance` | Product-wise sales performance |
| `GET` | `/ai/predict` | 7-day future sales prediction from ML model |
| `POST` | `/chatbot/chat` | Send prompt to Gemini LLM injected with store context |

### IoT Devices (`/devices`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/devices/register` | Register new camera, sensor hub, or gateway |
| `GET` | `/devices` | List all devices (filters: `?status=`, `?type=`) |
| `GET` | `/devices/<id>` | Detailed device information |
| `PUT` | `/devices/<id>` | Update device status, IP, location |
| `DELETE` | `/devices/<id>` | Delete device |
| `POST` | `/devices/heartbeat` | Hardware ping to record alive status |

### Sensors (`/sensors`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/sensors/readings` | Ingest reading (checks thresholds, auto-alerts anomalies) |
| `GET` | `/sensors/readings/latest` | Latest sensor readings (filters: `?type=`, `?limit=`) |
| `GET` | `/sensors/readings/history/<id>`| Historical readings for a specific sensor (`?hours=`) |
| `GET` | `/sensors/summary` | Average temperature, humidity, and active sensor count |

### Store Monitoring & Vision (`/monitoring`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/monitoring/realtime` | Real-time overview of cameras, devices, shelves, footfall |
| `POST` | `/monitoring/camera-events` | Log vision event from camera detection model |
| `GET` | `/monitoring/camera-events` | List camera events (`?limit=`, `?type=`) |
| `GET` | `/monitoring/shelves` | List all smart shelves with fill percentage and stock |
| `PUT` | `/monitoring/shelves/<id>` | Update shelf stock estimate, capacity, or section |
| `POST` | `/monitoring/footfall` | Log visitor entry/exit and update live occupancy |
| `GET` | `/monitoring/footfall` | Footfall analytics (`?timeframe=today|week|24h`) |

### Alerts (`/alerts`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/alerts` | Create system, security, or stock alert |
| `GET` | `/alerts` | Get active alerts (`?severity=`, `?resolved=all`) |
| `GET` | `/alerts/counts` | Counts of critical, warning, info, and unread alerts |
| `PUT` | `/alerts/<id>/read` | Mark alert as read |
| `PUT` | `/alerts/<id>/resolve` | Resolve alert with resolver metadata |

### Dashboard (`/dashboard`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/overview` | Single-pane view combining sales KPIs, IoT fleet, shelves, footfall, alerts |
| `GET` | `/dashboard/telemetry` | Ultra-fast live telemetry stream (latest sensors, camera, occupancy) |

---

## 5. Edge AI & Vision Processing Pipeline

The `edge-ai/` module operates as an independent edge service running on the store computer, Raspberry Pi, or Jetson:

```
[Mobile / IP Camera] ──> [stream_handler.py] ──> [frame_processor.py]
                                                        │
                                                        ▼
                                                 [inference.py]
                                                        │
                     ┌──────────────────────────────────┼──────────────────────────────────┐
                     ▼                                  ▼                                  ▼
           [people_detector.py]                [queue_detector.py]                [shelf_detector.py]
          (Footfall & Occupancy)             (Counter Queue Length)             (Empty Slot / Refill)
                     │                                  │                                  │
                     └──────────────────────────────────┼──────────────────────────────────┘
                                                        │
                                                        ▼
                                               [event_builder.py]
                                                        │
                                                        ▼
                                               [backend_client.py]
                                                        │ HTTP POST /monitoring/camera-events
                                                        ▼
                                              [Flask Backend REST API]
```

### Key Capabilities
1. **Camera Ingestion (`camera/`)**:
   - Captures frames from RTSP streams, IP Webcam apps (e.g. Android smartphone running IP Webcam), or USB webcams.
   - Handles auto-reconnection if the Wi-Fi or stream drops (`reconnect.py`).
2. **AI Inference & Vision (`ai/`)**:
   - `model_loader.py`: Loads the YOLOv11 model into memory once.
   - `people_detector.py`: Counts people entering, exiting, and dwell time.
   - `queue_detector.py`: Detects people waiting at the billing counter and triggers queue overflow warnings if count > 5.
   - `shelf_detector.py`: Checks assigned shelf bounding regions for missing products.
   - `tracker.py`: Maintains persistent track IDs across frames using ByteTrack algorithm.
3. **Sensor Processing (`sensors/`)**:
   - `ir_sensor.py`: Monitors aisle movement or break-beam triggers.
   - `ultrasonic_sensor.py`: Measures shelf depth to calculate stock fullness.
   - `mock_sensor.py`: Generates realistic live readings for testing when physical hardware is not plugged in.
4. **Communication (`communication/`)**:
   - Posts camera events to `/monitoring/camera-events`.
   - Posts sensor readings to `/sensors/readings`.
   - Sends periodic hardware health heartbeats to `/devices/heartbeat`.

---

## 6. Database Schema & Relationships

### Core Relational Models
1. **`users`**: Store credentials, password hash, role (`owner`, `admin`, `cashier`).
2. **`products`**: Kirana SKUs, category, cost price, selling price, quantity, `min_stock_level`, batch number, expiry date.
3. **`bills`**: Customer details (name, phone), subtotal, tax amount, discount, total amount, payment method (`cash`, `upi`, `card`), timestamp.
4. **`bill_items`**: Foreign keys to `bills.id` and `products.id`. Captures historical snapshot of product name, category, prices, and quantity at purchase time.
5. **`devices`**: Hardware registry (`camera`, `sensor_hub`, `footfall_counter`, `edge_ai_box`), IP address, MAC, status (`online`, `offline`), last heartbeat.
6. **`camera_events`**: Vision detection events linked to `devices.id` (`person_detected`, `theft_alert`, `out_of_stock_detected`, `queue_overflow`), confidence score, bounding box.
7. **`sensor_readings`**: Time-series telemetry linked to `devices.id` (`temperature`, `humidity`, `weight`), thresholds, anomaly flag.
8. **`shelf_statuses`**: Smart shelves linked to `products.id` and `devices.id`, estimated unit count, capacity, fill percentage, status (`normal`, `low_stock`, `empty`).
9. **`footfall`**: Entrance traffic linked to `devices.id`, entry count, exit count, current occupancy, dwell time, hourly bucket.
10. **`alerts`**: Alert issues linked to `devices.id`, severity (`critical`, `warning`, `info`), category, resolution state (`is_resolved`, `resolved_by`, `resolved_at`).

---

## 7. Golden Rules for Teammates & AI Assistants

> [!IMPORTANT]
> **Rule 1: Never Break or Interrupt Existing Working Files.**
> When adding new features, prefer adding new files and cleanly extending registries rather than rewriting existing modules. Always maintain backward compatibility.

> [!TIP]
> **Rule 2: Keep Pure Separation of Concerns.**
> - `routes/`: Define endpoints, extract request parameters, return JSON.
> - `controllers/`: Validate inputs, delegate to services.
> - `services/`: Pure business logic and database queries.
> - `models/`: Table definitions and serialization helpers.
> - `edge-ai/`: Autonomous edge vision and sensor ingestor; interacts only via REST/WebSocket contracts.

> [!NOTE]
> **Rule 3: Database Seeding & Testing.**
> Always run `python -m app.database.seed` (or `python app/database/seed.py`) when setting up a fresh database environment so all sample products, devices, and sensors are populated.

---

## 8. Phased Development Milestones

### Phase 1: Core Kirana Retail & POS — [COMPLETED]
- [x] Product inventory CRUD with stock, batch, and expiry dates.
- [x] POS terminal with product search, cart calculation, auto-stock decrement.
- [x] PDF tax invoice generation with ReportLab.
- [x] Analytics dashboard with revenue trends and category distribution.
- [x] AI Sales forecast model (`sales_model.pkl`) and Gemini chatbot integration.

### Phase 2: IoT Hardware & Edge Monitoring Backend — [COMPLETED]
- [x] Models: `Device`, `CameraEvent`, `SensorReading`, `ShelfStatus`, `Footfall`, `Alert`.
- [x] Services: `device_service`, `sensor_service`, `monitoring_service`, `alert_service`, `dashboard_service`, `edge_ai_service`.
- [x] Blueprints & Endpoints: `/devices`, `/sensors`, `/monitoring`, `/alerts`, `/dashboard`.
- [x] Middleware: JWT verification, role-based access, error handlers.
- [x] Full database seed script with Kirana store sample devices and readings.

### Phase 3: Edge AI Subsystem Scaffolding & Pipeline — [IN PROGRESS]
- [x] Scaffolding: `edge-ai/` directories (`camera/`, `ai/`, `sensors/`, `events/`, `communication/`, `utils/`, `weights/`).
- [ ] Implement camera stream ingestion with Android IP camera/RTSP support (`mobile_camera.py`, `stream_handler.py`).
- [ ] Implement YOLO model loader & multi-task inference pipeline (`model_loader.py`, `inference.py`).
- [ ] Implement people counter, billing queue detector, and shelf vacancy detector.
- [ ] Implement sensor simulator & hardware GPIO reader (`mock_sensor.py`, `sensor_manager.py`).
- [ ] Connect Edge client to Flask backend endpoints (`backend_client.py`).

### Phase 4: Frontend IoT Telemetry & Dashboard Integration — [IN PROGRESS]
- [ ] Connect `frontend/services/api.ts` with new backend monitoring endpoints.
- [ ] Home Dashboard update: Live store occupancy badge, IoT device status indicator, critical alerts banner.
- [ ] Smart Shelf visualizer: Section-based progress bars for stock capacity and out-of-stock highlights.
- [ ] Real-time Sensor gauges: Cooler temperature display with threshold warnings.

### Phase 5: Production Readiness & Hardware Deployment — [PLANNED]
- [ ] Docker containerization (`Dockerfile` for Flask, `docker-compose.yml` with PostgreSQL).
- [ ] Edge AI deployment script (systemd daemon or Docker on Jetson/Raspberry Pi).
- [ ] Production WSGI server setup (Gunicorn).
- [ ] Expo production build (Android APK release).
