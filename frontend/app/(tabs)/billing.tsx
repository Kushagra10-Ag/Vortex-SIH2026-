import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, Dimensions, Alert, ActivityIndicator,
} from 'react-native';
import { colors, radius } from '../../constants/theme';
import { mockDailySalesTrend } from '../../mock/data';
import LineChart from '../../components/LineChart';
import { fetchProducts, createBill, openBillPdf } from "../../services/api";

const { width } = Dimensions.get('window');
interface BillItem { id: string; name: string; price: number; qty: number; }

export default function Billing() {
  const [isFocused, setIsFocused] = useState(false);

  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [products, setProducts] = useState<any[]>([]);
  const [billItems, setBillItems] = useState<BillItem[]>([]);
  const [customerName, setCustomerName] = useState('');
  const [phone, setPhone] = useState('');
  const [payMethod, setPayMethod] = useState<'Cash' | 'Card' | 'UPI'>('Cash');
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const subtotal = billItems.reduce((sum, item) => sum + item.price * item.qty, 0);
  const tax = Math.round(subtotal * 0.10);
  const discount = 0;
  const total = subtotal + tax - discount;

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
  setLoadingProducts(true);
  try {
    const data = await fetchProducts();
    console.log("RAW BACKEND DATA:", JSON.stringify(data, null, 2)); // 🔥
  const formatted = data.map((p: any) => ({
  id: String(p.id),
  name: p.name,
  category: p.category,
  selling_price: p.selling_price,   // ✅ FIXED
  qty: p.quantity,          // ✅ FIXED
  expiry: ''                // (optional for now)
}));
    setProducts(formatted);
    console.log("FORMATTED:", formatted);
  } catch (e) {
    Alert.alert("Error", "Failed to load products.");
    console.log("loadProducts error:", e);
  } finally {
    setLoadingProducts(false);
  }
  
};

  const handleSearch = (t: string) => {
    setSearch(t);
    
  };

  const addItem = (p: any) => {
    const existing = billItems.find(b => b.id === p.id);
    if (existing) {
      setBillItems(billItems.map(b =>
        b.id === p.id ? { ...b, qty: b.qty + 1 } : b
      ));
    } else {
      setBillItems([
        ...billItems,
        {
          id: p.id,
          name: p.name,
          price: p.selling_price,
          qty: 1,
        }
      ]);
    }
    setSearch('');
  };

  const updateQty = (id: string, delta: number) => {
    setBillItems(billItems.map(b =>
      b.id === id ? { ...b, qty: Math.max(1, b.qty + delta) } : b
    ));
  };

  const removeItem = (id: string) =>
    setBillItems(billItems.filter(b => b.id !== id));

const handlePrint = async () => {
  if (billItems.length === 0) {
    Alert.alert("Empty Bill", "Please add at least one product.");
    return;
  }
  if (!customerName.trim()) {
    Alert.alert("Missing Info", "Please enter customer name.");
    return;
  }

  setSubmitting(true);
  try {
    const result = await createBill({
      customer_name: customerName.trim(),
      phone: phone.trim(),
      payment_method: payMethod,
      subtotal,
      tax_amount: tax,
      discount,
      total_amount: total,
      items: billItems.map(item => ({
        product_id: item.id,
        quantity: item.qty,
      })),
    });

    if (result.bill_id) {
      openBillPdf(result.bill_id);
    }

    Alert.alert(
      "✅ Bill Created!",
      `Bill #${result.bill_id || ''} created.\nTotal: ₹${total.toFixed(2)}`
    );

    setBillItems([]);
    setCustomerName('');
    setPhone('');
    setPayMethod('Cash');
    setSearch('');

  } catch (e: any) {
    Alert.alert("Error", e.message || "Failed to create bill.");
    console.log("handlePrint error:", e);
  } finally {
    setSubmitting(false);
  }
};

  const chartData = mockDailySalesTrend.map(d => ({ label: d.hour, value: d.value }));
  const filteredProducts = products
  .filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase())
  )
  .sort((a, b) => a.name.localeCompare(b.name));
  return (
  <ScrollView
    style={styles.container}
    showsVerticalScrollIndicator={false}
    keyboardShouldPersistTaps="handled"
  >
    <View style={{ flexDirection: 'row', gap: 12 }}>

      {/* LEFT COLUMN */}
      <View style={{ flex: 1.6, gap: 12 }}>

        {/* Item Selection */}
        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Item Selection</Text>
          {loadingProducts && (
            <ActivityIndicator color={colors.primary} style={{ marginBottom: 8 }} />
          )}
          <View style={styles.searchRow}>
            <TextInput
              style={styles.input}
              placeholder="Type product name..."
              placeholderTextColor={colors.textSub}
              value={search}
              onChangeText={handleSearch}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setTimeout(() => setIsFocused(false), 200)}
            />
          </View>
          <View style={styles.tableHeader}>
            <Text style={[styles.th, { flex: 2 }]}>PRODUCT</Text>
            <Text style={styles.th}>PRICE</Text>
            <Text style={styles.th}>STOCK</Text>
          </View>
          <ScrollView style={{ maxHeight: 200, marginBottom: 10 }}>
            {(isFocused ? filteredProducts : filteredProducts.slice(0, 4)).map(p => (
              <TouchableOpacity key={p.id} style={styles.tableRow} onPress={() => addItem(p)}>
                <Text style={[styles.td, { flex: 1.5 }]}>{p.name}</Text>
                <Text style={styles.td}>₹{p.selling_price}</Text>
                <Text style={styles.td}>Stock: {p.qty}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

        {/* Bill Items */}
        {billItems.length > 0 && (
          <>
            <View style={[styles.tableHeader, { marginTop: 8 }]}>
              <Text style={[styles.th, { flex: 2 }]}>ITEM</Text>
              <Text style={styles.th}>PRICE</Text>
              <Text style={styles.th}>QTY</Text>
              <Text style={styles.th}>TOTAL</Text>
              <Text style={[styles.th, { width: 20 }]}></Text>
            </View>

            {billItems.map(item => (
              <View key={item.id} style={styles.tableRow}>
                <Text style={[styles.td, { flex: 2 }]}>{item.name}</Text>
                <Text style={styles.td}>₹{item.price}</Text>
                <View style={styles.qtyControl}>
                  <TouchableOpacity onPress={() => updateQty(item.id, -1)} style={styles.qtyBtn}>
                    <Text style={styles.qtyBtnText}>−</Text>
                  </TouchableOpacity>
                  <Text style={styles.qtyVal}>{item.qty}</Text>
                  <TouchableOpacity onPress={() => updateQty(item.id, 1)} style={styles.qtyBtn}>
                    <Text style={styles.qtyBtnText}>+</Text>
                  </TouchableOpacity>
                </View>
                <Text style={styles.td}>₹{item.price * item.qty}</Text>
                <TouchableOpacity onPress={() => removeItem(item.id)}>
                  <Text style={{ color: '#FF4D4D', fontSize: 16 }}>✕</Text>
                </TouchableOpacity>
              </View>
            ))}
          </>
        )}

        </View>

        {/* Daily Sales Trend */}

        {/* Daily Sales Trend */}
        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Daily Sales Trend</Text>
          <LineChart
            data={chartData}
            width={width * 0.55}
            height={160}
            color={colors.primary}
          />
        </View>

      </View>

      {/* RIGHT COLUMN - tall single panel */}
      <View style={[styles.panel, styles.darkPanel, { flex: 1 }]}>

        <Text style={[styles.panelTitle, { color: '#fff' }]}>Customer Details</Text>
        <TextInput
          style={styles.input}
          placeholder="Customer Name"
          placeholderTextColor={colors.textSub}
          value={customerName}
          onChangeText={setCustomerName}
        />
        <TextInput
          style={[styles.input, { marginTop: 8 }]}
          placeholder="Phone Number"
          placeholderTextColor={colors.textSub}
          keyboardType="phone-pad"
          value={phone}
          onChangeText={setPhone}
        />

        <Text style={[styles.panelTitle, { color: '#fff', marginTop: 20 }]}>Payment Method</Text>
        <View style={styles.payRow}>
          {(['Cash', 'Card', 'UPI'] as const).map(m => (
            <TouchableOpacity
              key={m}
              onPress={() => setPayMethod(m)}
              style={[styles.payPill, payMethod === m && styles.payPillActive]}
            >
              <Text style={[styles.payPillText, payMethod === m && styles.payPillTextActive]}>
                {m}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={[styles.divider, { marginTop: 20 }]} />

        <Text style={[styles.panelTitle, { color: '#fff', marginTop: 4 }]}>Bill Summary</Text>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Subtotal</Text>
          <Text style={styles.summaryVal}>₹{subtotal}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Tax (10%)</Text>
          <Text style={styles.summaryVal}>₹{tax}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Discount</Text>
          <Text style={styles.summaryVal}>₹{discount}</Text>
        </View>

        <View style={styles.divider} />
        <Text style={styles.totalText}>₹{total.toFixed(2)}</Text>

        <TouchableOpacity
          style={[styles.printBtn, submitting && { opacity: 0.6 }]}
          onPress={handlePrint}
          disabled={submitting}
        >
          {submitting
            ? <ActivityIndicator color={colors.dark} />
            : <Text style={styles.printBtnText}>🖨️  PRINT BILL</Text>
          }
        </TouchableOpacity>

      </View>

    </View>
    <View style={{ height: 100 }} />
  </ScrollView>
);
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0D1B2A', padding: 12 },
  row: { flexDirection: 'row', gap: 12, marginBottom: 12 },
  panel: { backgroundColor: '#132032', borderRadius: radius.md, padding: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 8, elevation: 3 },
  darkPanel: { backgroundColor: '#1B263B', borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  panelTitle: { fontSize: 15, fontWeight: '700', color: '#E6EDF3', marginBottom: 12 },
searchRow: { marginBottom: 12 },
  input: { borderWidth: 1.5, borderColor: 'rgba(255,255,255,0.08)', borderRadius: radius.sm, padding: 10, fontSize: 13, color: '#E6EDF3', backgroundColor: '#0D1B2A' },
  tableHeader: { flexDirection: 'row', paddingBottom: 8, borderBottomWidth: 1, borderBottomColor: colors.border, marginBottom: 4 },
  th: { flex: 1, fontSize: 11, color: colors.textSub, fontWeight: '600', textTransform: 'uppercase' },
  tableRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: colors.border },
  td: { flex: 1, fontSize: 13, color: '#E6EDF3' },
  qtyControl: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 8 },
  qtyBtn: { width: 24, height: 24, borderRadius: 12, backgroundColor: colors.bg, alignItems: 'center', justifyContent: 'center' },
  qtyBtnText: { fontSize: 14, fontWeight: '700', color: colors.text },
  qtyVal: { fontSize: 13, fontWeight: '700', color: colors.text, minWidth: 16, textAlign: 'center' },
  summaryRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  summaryLabel: { color: 'rgba(255,255,255,0.6)', fontSize: 13 },
  summaryVal: { color: 'rgba(255,255,255,0.9)', fontSize: 13, fontWeight: '600' },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.15)', marginVertical: 12 },
  totalText: { color: '#fff', fontSize: 32, fontWeight: '900', letterSpacing: -1, marginBottom: 16 },
  printBtn: { backgroundColor: '#F1F5F9', borderRadius: radius.sm, padding: 14, alignItems: 'center' },
  printBtnText: { color: colors.dark, fontWeight: '800', fontSize: 13 },
  payRow: { flexDirection: 'row', gap: 8 },
  payPill: { flex: 1, borderWidth: 1.5, borderColor: colors.border, borderRadius: radius.sm, padding: 8, alignItems: 'center' },
  payPillActive: { borderColor: colors.primary, backgroundColor: colors.primary + '15' },
  payPillText: { fontSize: 12, color: colors.textSub, fontWeight: '600' },
  payPillTextActive: { color: colors.primary },
});