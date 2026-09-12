# BIZmate — Frontend Design System, UI/UX Specifications & Checkpoints

> **Document Purpose**: This file is the master reference for all frontend architecture, design tokens, screen components, UI/UX workflows, and milestone checkpoints for the BIZmate React Native (Expo) mobile application. All frontend teammates and AI assistants must record design decisions and checkpoint progress here.

---

## 1. Design Philosophy & Guidelines

BIZmate is designed for fast-paced retail and Kirana store environments. Store owners and cashiers often operate on mobile phones or tablets while attending to customers.

### Core Principles
1. **Speed & Ergonomics**: Fast, one-tap actions for billing, barcode search, and alert resolution. Key actions must be within thumb reach.
2. **High Visual Clarity**: High-contrast typography and clear color-coded statuses (e.g., Red for critical expiry/out-of-stock, Green for healthy stock, Amber for low thresholds).
3. **Real-time Awareness**: Live store telemetry (occupancy count, cooler temperature, billing counter queue length, empty shelf warnings) visible without navigating deeply into menus.
4. **Offline Resilience**: Clean loading skeletons and fallback states when network or edge devices have temporary latency.

---

## 2. Design System Tokens

Tokens are centralized in [`frontend/constants/theme.ts`](file:///c:/SIH2026/frontend/constants/theme.ts).

### Color Palette
| Token | Hex Value | Semantic Usage |
|---|---|---|
| `primary` | `#4F8EF7` | Main brand color, active tab icons, primary action buttons |
| `accent` | `#00C896` | Success states, healthy stock, paid bills, completed actions |
| `warning` | `#FFB020` | Low stock warnings, near-expiry items, threshold alerts, queue congestion |
| `danger` | `#FF6B6B` | Critical alerts, expired items, empty shelves, delete buttons |
| `purple` | `#7B61FF` | AI features (Gemini chatbot, ML forecast badges, YOLO vision detections) |
| `dark` | `#1A2332` | Headings, primary typography, high-contrast dark elements |
| `darkCard` | `#1E2D40` | Dark mode surface, dark KPI background cards |
| `card` | `#FFFFFF` | Standard card surface background |
| `bg` | `#F0F2F5` | Main screen background |
| `border` | `#E8ECF0` | Dividers, card borders, input borders |
| `textSub` | `#8899AA` | Secondary labels, timestamps, measurement units |
| `navBg` | `#FFFFFF` | Bottom tab bar and top header background |

### Typography Scale
- **Display / Hero KPI**: 28px – 32px (Bold)
- **Screen Header**: 22px – 24px (Bold)
- **Section Header**: 16px – 18px (SemiBold)
- **Card Title**: 14px – 16px (Medium / SemiBold)
- **Body Text**: 13px – 14px (Regular)
- **Captions & Units**: 11px – 12px (Medium, `#8899AA`)

### Corner Radiuses
- `radius.sm`: 10px (Badges, small buttons, tags)
- `radius.md`: 16px (Input fields, standard cards, list items)
- `radius.lg`: 22px (Modal sheets, featured cards)
- `radius.xl`: 28px (Pill buttons, floating action buttons)

---

## 3. Screen Inventory & Component Catalog

```
frontend/app/
├── _layout.tsx                 # Root navigation stack with theme provider
├── login.tsx                   # Store owner / cashier login screen
└── (tabs)/                     # Bottom navigation tabs
    ├── _layout.tsx             # 5 core tabs with vector icons
    ├── index.tsx               # Home Dashboard (Retail KPIs + IoT Telemetry + Queue Status)
    ├── inventory.tsx           # Product catalog, stock filters, add/edit modal
    ├── billing.tsx             # POS Terminal, product search, cart, checkout & PDF
    ├── analytics.tsx           # Charts (Revenue Line, Sales Bar, Category Pie)
    └── chatbot.tsx             # Gemini AI Retail Assistant chat screen
```

### Existing Screens Breakdown
1. **Home Screen (`(tabs)/index.tsx`)**:
   - Daily Revenue & Sales KPI cards.
   - Quick Action buttons: "New Bill", "Add Product", "Stock Report".
   - Recent Bills list with payment method badges.
   - Critical Expiry Warning card.
   - *[Latest Additions]*: Live Store Occupancy indicator & IoT Fleet status chip.

2. **Inventory Screen (`(tabs)/inventory.tsx`)**:
   - Search bar with instant SKU/name filtering.
   - Category pill selector (All, Staples, Dairy, Snacks, Beverages, Personal Care).
   - Product list items showing Selling Price, Cost Price, Quantity, Batch, and Expiry.
   - Floating Action Button (FAB) triggering Add Product Modal with form validation.

3. **Billing Screen (`(tabs)/billing.tsx`)**:
   - Fast product lookup list with stock quantity badges.
   - Real-time cart drawer with quantity counter (`+` / `-`).
   - Customer name & phone inputs.
   - Payment method toggle: Cash / UPI / Card.
   - Calculation engine: Subtotal, 5% Tax, Custom Discount, Grand Total.
   - "Generate Bill & Download PDF" trigger opening ReportLab PDF invoice.

4. **Analytics Screen (`(tabs)/analytics.tsx`)**:
   - Metric cards: Total Revenue, Average Daily Sales, Top Product, Growth %.
   - Custom SVG Charts:
     - `LineChart.tsx`: Weekly/Monthly revenue trends.
     - `BarChart.tsx`: Monthly sales comparison.
     - `PieChart.tsx`: Category distribution breakdown.
   - Expiry Risk Table with Critical/High/Medium badges.

5. **AI Chatbot Screen (`(tabs)/chatbot.tsx`)**:
   - Real-time conversational interface connected to Google Gemini.
   - Pre-prompt shortcut chips: "What are today's top sellers?", "Show near-expiry stock", "Suggest restocking list".
   - Injected store context (revenue, low stock, customer trends).

---

## 4. Edge AI & IoT UI Components

To interface with the newly created backend monitoring services and the `edge-ai/` detection pipeline, the following UI modules are specified:

### A. Store Occupancy & Gate Footfall Badge
- **Location**: Top of Home Dashboard (`(tabs)/index.tsx`).
- **Visuals**:
  - Live visitor count: `Occupancy: 8 inside store` (Green dot if <15, Amber if 15–25, Red if >25).
  - Daily In/Out summary: `▲ 142 entries | ▼ 134 exits`.

### B. Billing Counter Queue Monitor
- **Location**: Home Dashboard & Billing Screen header.
- **Data Source**: `edge-ai/ai/queue_detector.py` via `/monitoring/camera-events`.
- **Visuals**:
  - Badge: `Queue: 3 people waiting (Est. wait 4m)`.
  - Alert Banner (if queue > 5): `⚠️ Counter 1 Congested — Customer wait time exceeding 6 minutes`.

### C. Smart Shelf Health & Out-of-Stock Bar
- **Location**: Home Dashboard & Dedicated Shelves Modal.
- **Data Source**: `edge-ai/ai/shelf_detector.py` + Ultrasonic/Load-cell sensors via `/monitoring/shelves`.
- **Visuals**:
  - Card showing shelf code (e.g. `SHELF-A1 (Aashirvaad Atta)`).
  - Visual fill meter: Horizontal segmented bar showing percentage fill.
  - State indicator:
    - Normal (Green, fill > 50%)
    - Low Stock (Amber, fill 20% – 50%)
    - Empty / Refill Now (Red, fill < 20%) with one-tap "Restock" trigger.

### D. Live IoT Telemetry Carousel
- **Location**: Dedicated Telemetry section on Home or Monitoring screen.
- **Widgets**:
  - **Dairy Cooler Sensor**: Shows temperature gauge `3.8°C` (Warning badge if > 6°C).
  - **Store Floor Climate**: Shows `24.2°C` and `52% Humidity`.
  - **Hardware Fleet Status**: `6 / 6 Devices Online` with green pulse indicator.

### E. System Alerts Center / Floating Banner
- **Location**: Global notification badge in header.
- **Visuals**:
  - Tapping opens slide-up Alert Tray.
  - Each item displays Severity (`CRITICAL` in Red, `WARNING` in Amber, `INFO` in Blue).
  - Swipe to mark as read or "Resolve" button with one-tap acknowledgment.

---

## 5. Frontend API Integration Contracts (`api.ts`)

The frontend [`frontend/services/api.ts`](file:///c:/SIH2026/frontend/services/api.ts) file will export the following typed functions to consume the backend endpoints and Edge-AI telemetry:

```typescript
// --- Types ---
export interface DashboardOverview {
  kpis: {
    total_revenue: number;
    today_revenue: number;
    total_bills: number;
    total_products: number;
    low_stock_products: number;
  };
  iot_fleet: {
    total: number;
    online: number;
    offline: number;
  };
  smart_shelves: {
    total_shelves: number;
    avg_fill_percentage: number;
    empty_shelves: number;
  };
  footfall: {
    today_visitors: number;
    current_occupancy: number;
  };
  alerts_overview: {
    open: number;
    critical: number;
  };
}

export interface SmartShelf {
  id: number;
  shelf_code: string;
  section: string;
  product_name: string | null;
  current_stock_estimate: number;
  capacity: number;
  fill_percentage: number;
  status: 'normal' | 'low_stock' | 'empty';
}

export interface StoreAlert {
  id: number;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  category: string;
  is_read: boolean;
  is_resolved: boolean;
  created_at: string;
}

export interface CameraVisionEvent {
  id: number;
  camera_id: string;
  event_type: string;
  confidence: number;
  details: Record<string, any>;
  timestamp: string;
}

// --- API Functions ---
export const fetchDashboardOverview = async (): Promise<DashboardOverview | null> => {
  const res = await fetch(`${BASE_URL}/dashboard/overview`);
  const data = await res.json();
  return data.success ? data.data : null;
};

export const fetchSmartShelves = async (): Promise<SmartShelf[]> => {
  const res = await fetch(`${BASE_URL}/monitoring/shelves`);
  const data = await res.json();
  return data.success ? data.shelves : [];
};

export const fetchActiveAlerts = async (): Promise<StoreAlert[]> => {
  const res = await fetch(`${BASE_URL}/alerts`);
  const data = await res.json();
  return data.success ? data.alerts : [];
};

export const resolveAlert = async (alertId: number): Promise<boolean> => {
  const res = await fetch(`${BASE_URL}/alerts/${alertId}/resolve`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resolved_by: 'Owner' }),
  });
  return res.ok;
};

export const fetchRecentCameraEvents = async (limit = 10): Promise<CameraVisionEvent[]> => {
  const res = await fetch(`${BASE_URL}/monitoring/camera-events?limit=${limit}`);
  const data = await res.json();
  return data.success ? data.events : [];
};
```

---

## 6. Frontend Roadmap & Checkpoint Tracker

Use this section to track and record frontend iterations and future checkpoints.

| Checkpoint | Milestone Description | Target Scope | Status |
|---|---|---|---|
| **v1.0** | **Core Retail Kirana App** | POS billing, inventory CRUD, revenue analytics, Gemini chatbot, ReportLab PDF printing. | `COMPLETED` |
| **v2.0** | **Backend Edge/IoT Readiness** | REST endpoints for `/dashboard`, `/monitoring`, `/shelves`, `/sensors`, `/alerts`, and `/devices`. | `COMPLETED` |
| **v2.1** | **Edge-AI Architecture Scaffold** | Complete `edge-ai/` module structure (`camera/`, `ai/`, `sensors/`, `events/`, `communication/`). | `COMPLETED` |
| **v2.2** | **Home Dashboard Telemetry** | Integrate `fetchDashboardOverview` in `index.tsx`. Add Live Occupancy counter, IoT Device status chip, and Open Alerts badge. | `IN PROGRESS` |
| **v2.3** | **Smart Shelf Visualizer** | Add Visual Shelf fill-percentage cards on Home / Inventory screen with out-of-stock restock buttons. | `PLANNED` |
| **v2.4** | **Queue Length & Vision Activity Feed** | Add Billing Counter wait-time widget and live vision events timeline powered by `edge-ai/`. | `PLANNED` |
| **v2.5** | **Alerts Notification Center** | Slide-up modal or top bar dropdown showing real-time critical alerts with one-tap "Mark Resolved". | `PLANNED` |
| **v3.0** | **Hardware Bluetooth POS & Offline Sync** | Support ESC/POS Bluetooth thermal receipt printers, local SQLite offline cache for bills when Wi-Fi drops. | `FUTURE` |

---

## 7. Change Log & History

- **2026-09-10**:
  - Scaffolded the complete `edge-ai/` subsystem with video streaming, YOLO inference, sensors, and event dispatchers.
  - Updated `design.md` with Queue Monitor UI, Camera Vision Event timeline, and Ultrasonic/IR sensor visualizer specifications.
  - Advanced milestone checkpoints to include Edge-AI vision integration (Checkpoint v2.1 marked `COMPLETED`, v2.2 `IN PROGRESS`).
- **2026-09-09**:
  - Created initial master `design.md` covering typography, design tokens, screen architecture, IoT component specifications, and roadmap checkpoints.
  - Linked design specifications with backend monitoring and telemetry endpoints.
