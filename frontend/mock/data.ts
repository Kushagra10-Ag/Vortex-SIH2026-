export const mockProducts = [
  { id: '1', name: 'Flour', category: 'Grains', price: 89, qty: 45, expiry: '2026-06-01', lowStock: false },
  { id: '2', name: 'Soap', category: 'Hygiene', price: 45, qty: 8, expiry: '2027-01-01', lowStock: true },
  { id: '3', name: 'Rice', category: 'Grains', price: 120, qty: 3, expiry: '2026-12-01', lowStock: true },
  { id: '4', name: 'Sugar', category: 'Condiments', price: 55, qty: 60, expiry: '2026-09-01', lowStock: false },
  { id: '5', name: 'Salt', category: 'Condiments', price: 20, qty: 5, expiry: '2028-01-01', lowStock: true },
  { id: '6', name: 'Cooking Oil', category: 'Oils', price: 180, qty: 22, expiry: '2026-08-01', lowStock: false },
  { id: '7', name: 'Biscuits', category: 'Snacks', price: 30, qty: 2, expiry: '2026-04-15', lowStock: true },
  { id: '8', name: 'Tea', category: 'Beverages', price: 95, qty: 18, expiry: '2026-11-01', lowStock: false },
  { id: '9', name: 'Coffee', category: 'Beverages', price: 210, qty: 12, expiry: '2026-10-01', lowStock: false },
  { id: '10', name: 'Shampoo', category: 'Hygiene', price: 145, qty: 7, expiry: '2027-06-01', lowStock: true },
  { id: '11', name: 'Chips', category: 'Snacks', price: 20, qty: 35, expiry: '2026-05-01', lowStock: false },
  { id: '12', name: 'Milk', category: 'Dairy', price: 60, qty: 15, expiry: '2026-04-02', lowStock: false },
];

export const mockWeeklySales = [
  { day: 'Mon', value: 3200 },
  { day: 'Tue', value: 3900 },
  { day: 'Wed', value: 3700 },
  { day: 'Thu', value: 4800 },
  { day: 'Fri', value: 4600 },
  { day: 'Sat', value: 5900 },
  { day: 'Sun', value: 4200 },
];

export const mockDailySalesTrend = [
  { hour: '9', value: 500 },
  { hour: '10', value: 750 },
  { hour: '11', value: 1100 },
  { hour: '12', value: 950 },
  { hour: '13', value: 820 },
  { hour: '14', value: 950 },
  { hour: '15', value: 1600 },
  { hour: '16', value: 1850 },
  { hour: '17', value: 1750 },
  { hour: '18', value: 1400 },
  { hour: '19', value: 1050 },
  { hour: '20', value: 800 },
  { hour: '21', value: 600 },
];

export const mockTransactions = [
  { id: 't1', name: 'Rahul', initials: 'RA', time: '2 mins ago', amount: 120.00, color: '#4F8EF7' },
  { id: 't2', name: 'Kushagra', initials: 'KU', time: '15 mins ago', amount: 45.50, color: '#7B61FF' },
  { id: 't3', name: 'Viduit', initials: 'VI', time: '1 hour ago', amount: 210.00, color: '#FF6B6B' },
  { id: 't4', name: 'Vishwa', initials: 'VS', time: '3 hours ago', amount: 89.00, color: '#00C896' },
  { id: 't5', name: 'Arjun', initials: 'AR', time: '5 hours ago', amount: 340.00, color: '#FFB020' },
  { id: 't6', name: 'Priya', initials: 'PR', time: 'Yesterday', amount: 175.00, color: '#FF6B6B' },
];

export const mockCategoryData = [
  { label: 'Grains', value: 35, color: '#4F8EF7' },
  { label: 'Hygiene', value: 20, color: '#7B61FF' },
  { label: 'Snacks', value: 15, color: '#FFB020' },
  { label: 'Beverages', value: 15, color: '#00C896' },
  { label: 'Others', value: 15, color: '#FF6B6B' },
];

export const mockMonthlySales = [
  { month: 'Oct', value: 68000 },
  { month: 'Nov', value: 75000 },
  { month: 'Dec', value: 92000 },
  { month: 'Jan', value: 71000 },
  { month: 'Feb', value: 83000 },
  { month: 'Mar', value: 95000 },
];

export const mockChatHistory = [
  { id: 'c1', role: 'assistant', text: "Hi! I'm BizMate AI. Ask me anything about your inventory, sales, or analytics!" },
];

export const categories = ['All', 'Grains', 'Hygiene', 'Snacks', 'Beverages', 'Dairy', 'Oils', 'Condiments'];
