# 🏪 BizMate — Smart Business Management App

A fully interactive React Native (Expo) frontend for BizMate, built in TypeScript.  
Designed to connect to your FastAPI backend.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start Expo
npx expo start
```

Then press:
- **`i`** → iOS Simulator
- **`a`** → Android Emulator
- **`w`** → Web Browser
- **Scan QR** → Expo Go on your phone

---

## 📱 Screens

| Screen | File | Description |
|--------|------|-------------|
| **Login** | `app/login.tsx` | Email/password + social login. Navigates to tabs on success. |
| **Dashboard** | `app/(tabs)/index.tsx` | KPI cards, animated weekly sales chart, recent transactions |
| **Billing** | `app/(tabs)/billing.tsx` | Product autocomplete, live bill builder, customer details, Cash/Card/UPI |
| **Inventory** | `app/(tabs)/inventory.tsx` | Full CRUD table, low-stock alerts, expiry tracking, category filter |
| **Analytics** | `app/(tabs)/analytics.tsx` | Revenue trend, bar chart, donut pie, AI forecast, expiry risk table |
| **AI Chat** | `app/(tabs)/chatbot.tsx` | Conversational AI with quick prompts and typing indicator |
| **Modal** | `app/modal.tsx` | Reusable bottom-sheet modal |

---

## 🗂️ Project Structure

```
bizmate/
├── app/
│   ├── _layout.tsx           ← Root stack navigator
│   ├── index.tsx             ← Redirect to /login
│   ├── login.tsx             ← Login screen
│   ├── modal.tsx             ← Reusable modal
│   └── (tabs)/
│       ├── _layout.tsx       ← Tab bar navigator
│       ├── index.tsx         ← Dashboard
│       ├── billing.tsx       ← Billing
│       ├── inventory.tsx     ← Inventory
│       ├── analytics.tsx     ← Analytics
│       └── chatbot.tsx       ← AI Chatbot
│
├── components/
│   ├── LineChart.tsx         ← Custom SVG line/area chart
│   ├── BarChart.tsx          ← Custom SVG bar chart
│   └── PieChart.tsx          ← Custom SVG donut chart
│
├── constants/
│   └── theme.ts              ← Colors, spacing, border radius
│
├── mock/
│   └── data.ts               ← All mock data (swap with API calls)
│
├── app.json
├── package.json
├── babel.config.js
└── tsconfig.json
```

---

## 🔌 Connecting to Your FastAPI Backend

All mock data lives in `mock/data.ts`. Replace with real API calls:

```typescript
// Example: fetch inventory
const BASE_URL = 'http://YOUR_IP:8000';

const res = await fetch(`${BASE_URL}/api/inventory/products`);
const products = await res.json();
```

### Backend endpoint mapping:

| Screen | Backend Route |
|--------|--------------|
| Dashboard stats | `GET /api/analytics/summary` |
| Weekly sales chart | `GET /api/analytics/sales?period=week` |
| Recent transactions | `GET /api/billing/transactions?limit=5` |
| Billing — add item | `GET /api/inventory/products?search=X` |
| Billing — submit bill | `POST /api/billing/bill` |
| Inventory list | `GET /api/inventory/products` |
| Inventory CRUD | `POST/PUT/DELETE /api/inventory/products/:id` |
| Analytics charts | `GET /api/analytics/sales?period=month` |
| AI Forecast | `GET /api/analytics/forecast` |
| Chatbot | `POST /api/chatbot/query` |

---

## 🎨 Tech Stack

- **React Native** + **Expo** ~52
- **expo-router** v4 (file-based routing)
- **TypeScript** strict mode
- **react-native-svg** — all charts built from scratch (no heavy libraries)
- Zero external UI libraries — all components hand-crafted

---

## 📝 Notes

- Charts are fully custom SVG — lightweight and fast
- All screens are production-ready; just swap mock data for API calls
- The chatbot uses keyword matching locally — wire up `POST /api/chatbot/query` for real AI
- Low-stock and expiry logic is computed client-side from inventory data
