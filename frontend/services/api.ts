const BASE_URL = "http://127.0.0.1:5000";

import { Linking } from 'react-native';

export const fetchTotalSales = async () => {
  try {
    const res = await fetch(`${BASE_URL}/analytics/total-sales`);
    const data = await res.json();
    return data || {};
  } catch (error) {
    console.log("Error fetching sales:", error);
    return { total_sales: 0 };
  }
};

export const fetchBills = async () => {
  try {
    const res = await fetch(`${BASE_URL}/billing/bills`);
    const data = await res.json();
    return data || [];
  } catch (error) {
    console.log("Error fetching bills:", error);
    return [];
  }
};

export const fetchProducts = async () => {
  try {
    const res = await fetch(`${BASE_URL}/inventory/products`);
    const data = await res.json();
    return data || [];
  } catch (error) {
    console.log("Error fetching products:", error);
    return [];
  }
};

export const createBill = async (payload: {
  customer_name: string;
  phone: string;
  payment_method: string;
  subtotal: number;
  tax_amount: number;
  discount: number;
  total_amount: number;
  items: { product_id: string; quantity: number }[];
}) => {
  const res = await fetch(`${BASE_URL}/billing/create-bill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || `Server error: ${res.status}`);
  }
  return await res.json();
};

export const addProduct = async (payload: {
  name: string;
  category: string;
  brand: string;
  cost_price: number;
  selling_price: number;
  quantity: number;
  min_stock_level: number;
  expiry_date: string;
  batch_number: string;
}) => {
  const res = await fetch(`${BASE_URL}/inventory/add-product`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || `Server error: ${res.status}`);
  }
  return await res.json();
};

export const updateProduct = async (id: string, payload: {
  name: string;
  category: string;
  brand: string;
  cost_price: number;
  selling_price: number;
  quantity: number;
  min_stock_level: number;
  expiry_date: string;
  batch_number: string;
}) => {
  const res = await fetch(`${BASE_URL}/inventory/update-product/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || `Server error: ${res.status}`);
  }
  return await res.json();
};

export const deleteProduct = async (id: string) => {
  const res = await fetch(`${BASE_URL}/inventory/delete-product/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.message || `Server error: ${res.status}`);
  }
  return await res.json();
};

export const fetchAnalyticsDashboard = async () => {
  try {
    const res = await fetch(`${BASE_URL}/analytics/dashboard`);
    const data = await res.json();
    return data || {};
  } catch (error) {
    console.log("Error fetching analytics dashboard:", error);
    return {};
  }
};

export const fetchAIForecast = async () => {
  try {
    const res = await fetch(`${BASE_URL}/ai/sales-forecast`); // ✅ fixed: was /ai/sales-forecast
    const data = await res.json();
    return data || [];
  } catch (error) {
    console.log("Error fetching AI forecast:", error);
    return [];
  }
};

export const sendChatMessage = async (message: string): Promise<string> => {
  try {
    const res = await fetch(`${BASE_URL}/chatbot/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data.reply || "No response from AI"; // ✅ fixed: returns string not raw json
  } catch (error) {
    console.log("Chat error:", error);
    return "Sorry, I couldn't connect to BizMate AI right now.";
  }
};

export const openBillPdf = (bill_id: number | string) => {
  const url = `${BASE_URL}/billing/bill-pdf/${bill_id}`;
  Linking.openURL(url); // ✅ already correct
};
export const fetchDashboardOverview = async () => {
  try {
    const res = await fetch(`${BASE_URL}/dashboard/overview`);
    const data = await res.json();
    return data || {};
  } catch (error) {
    console.log("Dashboard error:", error);
    return {};
  }
};

export const fetchRealtimeTelemetry = async () => {
  try {
    const res = await fetch(`${BASE_URL}/dashboard/realtime`);
    const data = await res.json();
    return data || {};
  } catch (error) {
    console.log("Realtime error:", error);
    return {};
  }
};
export const fetchFullDashboard = async () => {
  try {
    const res = await fetch(`${BASE_URL}/dashboard/full`);
    const data = await res.json();
    return data || {};
  } catch (error) {
    console.log("Full dashboard error:", error);
    return {};
  }
};