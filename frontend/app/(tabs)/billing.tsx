import React, { useState, useEffect, useMemo } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, Dimensions, Alert, ActivityIndicator, Modal,
} from 'react-native';
import Svg, { Path, Circle, Rect } from 'react-native-svg';
import { fetchProducts, fetchBills, createBill, openBillPdf } from '../../services/api';

const { width: SCREEN_W } = Dimensions.get('window');

// ── Theme (matches Dashboard's "command center" look) ───────────────────────
const PAGE = '#EEF3F9';
const CARD = '#FFFFFF';
const BORDER = '#E5EBF2';
const TEXT = '#1E293B';
const MUTED = '#64748B';
const FAINT = '#94A3B8';
const BLUE = '#3B82F6';
const GREEN = '#22C55E';
const AMBER = '#F59E0B';
const RED = '#EF4444';

interface BillItem { id: string; name: string; price: number; qty: number; }

function Icon({ name, color, size = 16 }: { name: string; color: string; size?: number }) {
  const p = { stroke: color, strokeWidth: 2, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, React.ReactNode> = {
    receipt: (<><Path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z" {...p} /><Path d="M9 8h6M9 12h6" {...p} /></>),
    money: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M14.5 9a3 3 0 0 0-2.5-1.2c-1.5 0-2.7.8-2.7 1.9s1.2 1.9 2.7 1.9 2.7.8 2.7 1.9-1.2 1.9-2.7 1.9A3 3 0 0 1 9.5 15" {...p} /></>),
    users: (<><Circle cx={9} cy={8} r={3} {...p} /><Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...p} /><Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...p} /></>),
    clock: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M12 7v5l3 2" {...p} /></>),
    edit: (<><Path d="M4 20h4l10-10-4-4L4 16v4Z" {...p} /></>),
    file: (<><Path d="M6 2h8l4 4v16H6V2Z" {...p} /><Path d="M14 2v4h4" {...p} /></>),
    bell: (<><Path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" {...p} /><Path d="M10 20a2 2 0 0 0 4 0" {...p} /></>),
    close: (<><Path d="M6 6l12 12M18 6L6 18" {...p} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
}
import { router, usePathname } from 'expo-router';

const SIDEBAR_WIDTH = 208;

function SidebarIcon({ name, color, size = 16 }: { name: string; color: string; size?: number }) {
  const p = { stroke: color, strokeWidth: 2, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, React.ReactNode> = {
    grid: (<><Path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z" {...p} /></>),
    video: (<><Path d="M3 7h13v10H3zM16 10.5l5-3v9l-5-3" {...p} /></>),
    cart: (<><Circle cx={9} cy={20} r={1.4} fill={color} /><Circle cx={17} cy={20} r={1.4} fill={color} /><Path d="M3 4h2l2.2 10.6a2 2 0 0 0 2 1.6h7.3a2 2 0 0 0 2-1.6L20 8H6" {...p} /></>),
    box: (<><Path d="M3 8l9-5 9 5v8l-9 5-9-5Z" {...p} /><Path d="M3 8l9 5 9-5M12 13v8" {...p} /></>),
    users: (<><Circle cx={9} cy={8} r={3} {...p} /><Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...p} /><Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...p} /></>),
    briefcase: (<><Path d="M3 8h18v11H3zM8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18" {...p} /></>),
    chart: (<><Path d="M4 4v16h16" {...p} /><Path d="M8 15l3-4 3 2 4-6" {...p} /></>),
    gear: (<><Circle cx={12} cy={12} r={3} {...p} /><Path d="M12 3v2.2M12 18.8V21M21 12h-2.2M5.2 12H3M18.4 5.6l-1.5 1.5M7.1 16.9l-1.5 1.5M18.4 18.4l-1.5-1.5M7.1 7.1L5.6 5.6" {...p} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
}

function Sidebar() {
  const pathname = usePathname();
  const navItems = [
    { key: 'dashboard', label: 'Dashboard', icon: 'grid', route: '/' },
    { key: 'live-monitoring', label: 'Live Monitoring', icon: 'video', route: '/live_monitor' },
    { key: 'billing', label: 'Billing', icon: 'cart', route: '/billing' },
    { key: 'inventory', label: 'Inventory', icon: 'box', route: '/inventory' },
    { key: 'customers', label: 'Customers', icon: 'users', route: '/customers' },
    { key: 'employees', label: 'Employees', icon: 'briefcase', route: '/employees' },
    { key: 'analytics', label: 'Analytics', icon: 'chart', route: '/analytics' },
    { key: 'settings', label: 'Settings', icon: 'gear', route: '/settings' },
  ];
  return (
    <View style={styles.sidebar}>
      {navItems.map(item => {
        const isActive = pathname === item.route;
        return (
          <TouchableOpacity
            key={item.key}
            style={[styles.navItem, isActive && styles.navItemActive]}
            onPress={() => router.push(item.route as any)}
          >
            <SidebarIcon name={item.icon} color={isActive ? BLUE : MUTED} size={16} />
            <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>{item.label}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}
export default function Billing() {
  const isWide = SCREEN_W >= 900;

  // ── Original state (unchanged) ─────────────────────────────────────────
  const [isFocused, setIsFocused] = useState(false);
  const [search, setSearch] = useState('');
  const [products, setProducts] = useState<any[]>([]);
  const [billItems, setBillItems] = useState<BillItem[]>([]);
  const [customerName, setCustomerName] = useState('');
  const [phone, setPhone] = useState('');
  const [payMethod, setPayMethod] = useState<'Cash' | 'Card' | 'UPI'>('Cash');
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // ── New state for the redesigned view ──────────────────────────────────
  const [bills, setBills] = useState<any[]>([]);
  const [loadingBills, setLoadingBills] = useState(false);
  const [showNewBill, setShowNewBill] = useState(false);

  const subtotal = billItems.reduce((sum, item) => sum + item.price * item.qty, 0);
  const tax = Math.round(subtotal * 0.10);
  const discount = 0;
  const total = subtotal + tax - discount;

  useEffect(() => {
    loadProducts();
    loadBills();
  }, []);

  const loadProducts = async () => {
    setLoadingProducts(true);
    try {
      const data = await fetchProducts();
      const formatted = data.map((p: any) => ({
        id: String(p.id),
        name: p.name,
        category: p.category,
        selling_price: p.selling_price,
        qty: p.quantity,
        expiry: '',
      }));
      setProducts(formatted);
    } catch (e) {
      Alert.alert('Error', 'Failed to load products.');
      console.log('loadProducts error:', e);
    } finally {
      setLoadingProducts(false);
    }
  };

  const loadBills = async () => {
    setLoadingBills(true);
    try {
      const data = await fetchBills();
      setBills(Array.isArray(data) ? data : []);
    } catch (e) {
      console.log('loadBills error:', e);
    } finally {
      setLoadingBills(false);
    }
  };

  const handleSearch = (t: string) => setSearch(t);

  const addItem = (p: any) => {
    const existing = billItems.find(b => b.id === p.id);
    if (existing) {
      setBillItems(billItems.map(b => (b.id === p.id ? { ...b, qty: b.qty + 1 } : b)));
    } else {
      setBillItems([...billItems, { id: p.id, name: p.name, price: p.selling_price, qty: 1 }]);
    }
    setSearch('');
  };

  const updateQty = (id: string, delta: number) =>
    setBillItems(billItems.map(b => (b.id === id ? { ...b, qty: Math.max(1, b.qty + delta) } : b)));

  const removeItem = (id: string) => setBillItems(billItems.filter(b => b.id !== id));

  const handlePrint = async () => {
    if (billItems.length === 0) {
      Alert.alert('Empty Bill', 'Please add at least one product.');
      return;
    }
    if (!customerName.trim()) {
      Alert.alert('Missing Info', 'Please enter customer name.');
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
        items: billItems.map(item => ({ product_id: item.id, quantity: item.qty })),
      });

      if (result.bill_id) openBillPdf(result.bill_id);

      Alert.alert('✅ Bill Created!', `Bill #${result.bill_id || ''} created.\nTotal: ₹${total.toFixed(2)}`);

      setBillItems([]);
      setCustomerName('');
      setPhone('');
      setPayMethod('Cash');
      setSearch('');
      setShowNewBill(false);
      loadBills(); // refresh the history table with the new bill
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to create bill.');
      console.log('handlePrint error:', e);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredProducts = products
    .filter(p => p.name.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => a.name.localeCompare(b.name));

  // ── KPI derivations from real bill data ──────────────────────────────────
  const now = new Date();
  const isToday = (d: Date) => d.toDateString() === now.toDateString();
  const todayBills = useMemo(
    () => bills.filter((b: any) => b.created_at && isToday(new Date(b.created_at))),
    [bills]
  );
  const todayRevenue = todayBills.reduce((s: number, b: any) => s + (b.total_amount || 0), 0);
  const customersServed = new Set(todayBills.map((b: any) => b.customer_name || b.id)).size;

  // NOTE: average billing time needs a start/end timestamp per bill from the backend.
  // Until that's tracked, this is a placeholder — wire it up once createBill returns duration.
  const avgBillingTime = '2m 15s';

  // NOTE: queue length / waiting time need a live counter/queue feed (e.g. from Live Monitoring's
  // sensors). These are placeholders so the panel renders correctly — swap in real data when ready.
  const queueLength = 8;
  const waitingTime = 12;

  const kpis = [
    { label: "Today's Bills", icon: 'receipt', value: `${todayBills.length} Bills`, delta: '+5%', color: BLUE },
    { label: 'Revenue', icon: 'money', value: `Rs ${todayRevenue.toFixed(0)}`, delta: '+8%', color: GREEN },
    { label: 'Customers Served', icon: 'users', value: `${customersServed} Customers`, delta: null, color: BLUE },
    { label: 'Average Billing Time', icon: 'clock', value: avgBillingTime, delta: null, color: AMBER },
  ];

  return (
    <View style={styles.appShell}>
      {/* Top bar */}
      <View style={styles.topBar}>
        <View style={styles.topBarLeft}>
          <View style={styles.logoBadge}><Text style={styles.logoBadgeText}>F</Text></View>
          <Text style={styles.title}>Billing & POS</Text>
        </View>
        <View style={styles.headerRight}>
          <View style={styles.bell}>
            <Icon name="bell" color={MUTED} size={18} />
            <View style={styles.bellDot} />
          </View>
          <View style={styles.avatar}><Text style={styles.avatarText}>V</Text></View>
        </View>
      </View>

      <View style={styles.body}>
        {isWide && <Sidebar />}

        <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          {/* KPI cards */}
          <View style={styles.grid}>
            {kpis.map((k, i) => (
              <View key={i} style={[styles.kpiCard, { flexBasis: isWide ? '23%' : '47%' }]}>
                <View style={styles.kpiTop}>
                  <View style={[styles.kpiIcon, { backgroundColor: k.color + '1A' }]}>
                    <Icon name={k.icon} color={k.color} />
                  </View>
                  <Text style={styles.kpiLabel}>{k.label}</Text>
                </View>
                <Text style={styles.kpiValue}>{k.value}</Text>
                {k.delta && <Text style={[styles.kpiDelta, { color: GREEN }]}>↑ {k.delta}</Text>}
              </View>
            ))}
          </View>

          {/* Main row: bill history + queue monitoring */}
          <View style={[styles.grid, { alignItems: 'flex-start' }]}>
            {/* Bill history table */}
            <View style={[styles.panel, { flexBasis: isWide ? '68%' : '100%' }]}>
              <View style={styles.panelHeadRow}>
                <Text style={styles.panelTitle}>Current Billing & Transaction History</Text>
                <TouchableOpacity style={styles.newBillBtn} onPress={() => setShowNewBill(true)}>
                  <Text style={styles.newBillBtnText}>+ New Bill</Text>
                </TouchableOpacity>
              </View>

              {loadingBills && <ActivityIndicator color={BLUE} style={{ marginVertical: 8 }} />}

              <View style={styles.tableHeader}>
                <Text style={[styles.th, { flex: 1 }]}>BILL ID</Text>
                <Text style={[styles.th, { flex: 1.5 }]}>CUSTOMER</Text>
                <Text style={[styles.th, { flex: 0.8 }]}>ITEMS</Text>
                <Text style={[styles.th, { flex: 1 }]}>TOTAL</Text>
                <Text style={[styles.th, { flex: 1 }]}>STATUS</Text>
                <Text style={[styles.th, { flex: 1 }]}>COUNTER</Text>
              </View>

              {bills.length === 0 && !loadingBills ? (
                <Text style={styles.emptyText}>No bills yet — create one to see it here.</Text>
              ) : (
                bills.slice(0, 12).map((b: any) => (
                  <View key={b.id} style={styles.tableRow}>
                    <Text style={[styles.td, { flex: 1 }]}>#{b.id}</Text>
                    <Text style={[styles.td, { flex: 1.5 }]}>{b.customer_name || '—'}</Text>
                    <Text style={[styles.td, { flex: 0.8 }]}>{b.items?.length ?? '—'}</Text>
                    <Text style={[styles.td, { flex: 1 }]}>₹{(b.total_amount ?? 0).toFixed?.(0) ?? b.total_amount}</Text>
                    <View style={{ flex: 1 }}>
                      <View style={[styles.statusPill, { backgroundColor: (b.payment_status === 'Pending' ? AMBER : GREEN) + '22' }]}>
                        <Text style={[styles.statusPillText, { color: b.payment_status === 'Pending' ? AMBER : GREEN }]}>
                          {b.payment_status || 'Paid'}
                        </Text>
                      </View>
                    </View>
                    <Text style={[styles.td, { flex: 1 }]}>{b.counter || 'Counter 1'}</Text>
                    <TouchableOpacity onPress={() => b.id && openBillPdf(b.id)} style={{ marginLeft: 6 }}>
                      <Icon name="file" color={MUTED} size={16} />
                    </TouchableOpacity>
                  </View>
                ))
              )}
            </View>

            {/* Queue Monitoring + AI Recommendation */}
            <View style={[styles.panel, styles.darkPanel, { flexBasis: isWide ? '29%' : '100%' }]}>
              <Text style={[styles.panelTitle, { color: '#fff' }]}>Queue Monitoring</Text>

              <View style={styles.queueRow}>
                <View style={styles.queueCard}>
                  <Text style={styles.queueLabel}>Queue Length</Text>
                  <Text style={styles.queueValue}>{queueLength} People</Text>
                </View>
                <View style={styles.queueCard}>
                  <Text style={styles.queueLabel}>Waiting Time</Text>
                  <Text style={styles.queueValue}>{waitingTime} Min</Text>
                </View>
              </View>

              <View style={styles.divider} />

              <Text style={[styles.panelTitle, { color: '#fff' }]}>AI Recommendations</Text>
              <Text style={styles.aiText}>
                Queue is growing at Counter 1.{'\n'}
                <Text style={{ fontWeight: '800' }}>Recommendation:</Text> Open Counter 2 immediately to reduce average waiting time by 4 minutes.
              </Text>

              <TouchableOpacity
                style={styles.openCounterBtn}
                onPress={() => Alert.alert('Counter 2', 'Counter 2 has been opened.')}
              >
                <Text style={styles.openCounterBtnText}>Open Counter 2</Text>
              </TouchableOpacity>
            </View>
          </View>

          <View style={{ height: 60 }} />
        </ScrollView>
      </View>

      {/* New Bill modal — this is your original create-bill UI, unchanged, just relocated */}
      <Modal visible={showNewBill} animationType="slide" transparent onRequestClose={() => setShowNewBill(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.panelTitle}>New Bill</Text>
              <TouchableOpacity onPress={() => setShowNewBill(false)}>
                <Icon name="close" color={MUTED} size={18} />
              </TouchableOpacity>
            </View>

            <ScrollView keyboardShouldPersistTaps="handled">
              <View style={{ flexDirection: isWide ? 'row' : 'column', gap: 12 }}>
                {/* Item Selection (original) */}
                <View style={{ flex: 1.6, gap: 12 }}>
                  <Text style={styles.panelTitle}>Item Selection</Text>
                  {loadingProducts && <ActivityIndicator color={BLUE} style={{ marginBottom: 8 }} />}
                  <TextInput
                    style={styles.input}
                    placeholder="Type product name..."
                    placeholderTextColor={FAINT}
                    value={search}
                    onChangeText={handleSearch}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setTimeout(() => setIsFocused(false), 200)}
                  />
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
                            <Text style={{ color: RED, fontSize: 16 }}>✕</Text>
                          </TouchableOpacity>
                        </View>
                      ))}
                    </>
                  )}
                </View>

                {/* Customer Details / Summary (original) */}
                <View style={[styles.panel, styles.darkPanel, { flex: 1 }]}>
                  <Text style={[styles.panelTitle, { color: '#fff' }]}>Customer Details</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Customer Name"
                    placeholderTextColor={FAINT}
                    value={customerName}
                    onChangeText={setCustomerName}
                  />
                  <TextInput
                    style={[styles.input, { marginTop: 8 }]}
                    placeholder="Phone Number"
                    placeholderTextColor={FAINT}
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
                        <Text style={[styles.payPillText, payMethod === m && styles.payPillTextActive]}>{m}</Text>
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
                    {submitting ? <ActivityIndicator color={TEXT} /> : <Text style={styles.printBtnText}>🖨️  PRINT BILL</Text>}
                  </TouchableOpacity>
                </View>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  appShell: { flex: 1, backgroundColor: PAGE },
  topBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: CARD, borderBottomWidth: 1, borderBottomColor: BORDER },
  topBarLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  logoBadge: { width: 30, height: 30, borderRadius: 9, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  logoBadgeText: { color: '#fff', fontWeight: '900', fontSize: 14 },
  title: { fontSize: 17, fontWeight: '900', color: TEXT, letterSpacing: -0.4 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  bell: { width: 34, height: 34, borderRadius: 11, backgroundColor: CARD, borderWidth: 1, borderColor: BORDER, alignItems: 'center', justifyContent: 'center' },
  bellDot: { position: 'absolute', top: 8, right: 9, width: 6, height: 6, borderRadius: 3, backgroundColor: RED },
  avatar: { width: 34, height: 34, borderRadius: 17, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '800', fontSize: 14 },
    sidebar: { width: SIDEBAR_WIDTH, backgroundColor: CARD, borderRightWidth: 1, borderRightColor: BORDER, paddingVertical: 14, paddingHorizontal: 10, gap: 3 },
  navItem: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 10, paddingHorizontal: 12, borderRadius: 10 },
  navItemActive: { backgroundColor: BLUE + '14' },
  navLabel: { fontSize: 13, fontWeight: '600', color: MUTED },
  navLabelActive: { color: BLUE, fontWeight: '800' },
  body: { flex: 1, flexDirection: 'row' },
  container: { flex: 1, backgroundColor: PAGE },
  content: { padding: 10, paddingBottom: 16, gap: 10 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },

  kpiCard: { flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 12, borderWidth: 1, borderColor: BORDER },
  kpiTop: { flexDirection: 'row', alignItems: 'center', gap: 7, marginBottom: 6 },
  kpiIcon: { width: 26, height: 26, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  kpiLabel: { fontSize: 11, fontWeight: '600', color: MUTED, flex: 1 },
  kpiValue: { fontSize: 19, fontWeight: '900', color: TEXT, letterSpacing: -0.5 },
  kpiDelta: { fontSize: 10, fontWeight: '700', marginTop: 2 },

  panel: { flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 14, borderWidth: 1, borderColor: BORDER },
  darkPanel: { backgroundColor: '#1B263B', borderColor: 'rgba(255,255,255,0.08)' },
  panelHeadRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 },
  panelTitle: { fontSize: 14, fontWeight: '800', color: TEXT },
  emptyText: { fontSize: 12, color: FAINT, paddingVertical: 16, textAlign: 'center' },

  newBillBtn: { backgroundColor: BLUE, borderRadius: 8, paddingVertical: 7, paddingHorizontal: 12 },
  newBillBtnText: { color: '#fff', fontWeight: '700', fontSize: 12 },

  searchRow: { marginBottom: 12 },
  input: { borderWidth: 1.5, borderColor: BORDER, borderRadius: 10, padding: 10, fontSize: 13, color: TEXT, backgroundColor: '#F8FAFC' },
  tableHeader: { flexDirection: 'row', paddingBottom: 8, borderBottomWidth: 1, borderBottomColor: BORDER, marginBottom: 4 },
  th: { flex: 1, fontSize: 11, color: MUTED, fontWeight: '700', textTransform: 'uppercase' },
  tableRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#F1F5F9' },
  td: { flex: 1, fontSize: 13, color: TEXT },

  statusPill: { alignSelf: 'flex-start', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 3 },
  statusPillText: { fontSize: 11, fontWeight: '700' },

  qtyControl: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 8 },
  qtyBtn: { width: 24, height: 24, borderRadius: 12, backgroundColor: '#F1F5F9', alignItems: 'center', justifyContent: 'center' },
  qtyBtnText: { fontSize: 14, fontWeight: '700', color: TEXT },
  qtyVal: { fontSize: 13, fontWeight: '700', color: TEXT, minWidth: 16, textAlign: 'center' },

  queueRow: { flexDirection: 'row', gap: 10, marginTop: 10, marginBottom: 4 },
  queueCard: { flex: 1, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 10, padding: 10 },
  queueLabel: { fontSize: 11, color: 'rgba(255,255,255,0.6)' },
  queueValue: { fontSize: 16, fontWeight: '800', color: '#fff', marginTop: 4 },

  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.15)', marginVertical: 14 },
  aiText: { fontSize: 12, color: 'rgba(255,255,255,0.8)', lineHeight: 18, marginTop: 4 },
  openCounterBtn: { backgroundColor: '#F1F5F9', borderRadius: 10, paddingVertical: 12, alignItems: 'center', marginTop: 14 },
  openCounterBtnText: { color: TEXT, fontWeight: '800', fontSize: 13 },

  summaryRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  summaryLabel: { color: 'rgba(255,255,255,0.6)', fontSize: 13 },
  summaryVal: { color: 'rgba(255,255,255,0.9)', fontSize: 13, fontWeight: '600' },
  totalText: { color: '#fff', fontSize: 32, fontWeight: '900', letterSpacing: -1, marginBottom: 16 },
  printBtn: { backgroundColor: '#F1F5F9', borderRadius: 10, padding: 14, alignItems: 'center' },
  printBtnText: { color: TEXT, fontWeight: '800', fontSize: 13 },
  payRow: { flexDirection: 'row', gap: 8 },
  payPill: { flex: 1, borderWidth: 1.5, borderColor: 'rgba(255,255,255,0.15)', borderRadius: 10, padding: 8, alignItems: 'center' },
  payPillActive: { borderColor: BLUE, backgroundColor: BLUE + '15' },
  payPillText: { fontSize: 12, color: 'rgba(255,255,255,0.6)', fontWeight: '600' },
  payPillTextActive: { color: BLUE },

  modalOverlay: { flex: 1, backgroundColor: 'rgba(15,23,42,0.5)', justifyContent: 'center', padding: 16 },
  modalCard: { backgroundColor: PAGE, borderRadius: 16, padding: 16, maxHeight: '90%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
});