import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, Modal, ActivityIndicator, Alert,
} from 'react-native';
import { router, usePathname } from 'expo-router';
import Svg, { Path, Circle, G } from 'react-native-svg';
import { colors, radius } from '../../constants/theme';
import { fetchProducts, addProduct, updateProduct, deleteProduct } from '../../services/api';

// ─────────────────────────────────────────────────────────────────────────
// Theme — matches the light "command center" look used on the Dashboard
// ─────────────────────────────────────────────────────────────────────────
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

const SIDEBAR_WIDTH = 208;

// ─────────────────────────────────────────────────────────────────────────
// Types — original Product fields kept exactly as-is, new shelf/AI fields
// are optional so nothing breaks if the backend doesn't send them yet.
// ─────────────────────────────────────────────────────────────────────────
type Product = {
  id: string;
  name: string;
  category: string;
  brand: string;
  cost_price: number;
  selling_price: number;
  quantity: number;
  min_stock_level: number;
  expiry_date: string;
  batch_number: string;
  // ✅ New shelf / AI monitoring fields
  shelf_name?: string;
  ai_detection?: string;      // OK | Degraded | Error
  cam_visibility?: string;    // Clear | Obscured
  last_scan?: string;         // e.g. "10m ago"
  restock_status?: string;    // Restocked | Pending | Priority
  recommendation?: string;
  ai_confidence?: number;     // 0–100
};

type FormState = {
  name: string;
  category: string;
  brand: string;
  cost_price: string;
  selling_price: string;
  quantity: string;
  min_stock_level: string;
  expiry_date: string;
  batch_number: string;
  shelf_name: string;
  ai_detection: string;
  cam_visibility: string;
  last_scan: string;
  restock_status: string;
  recommendation: string;
  ai_confidence: string;
};

const emptyForm: FormState = {
  name: '',
  category: '',
  brand: '',
  cost_price: '',
  selling_price: '',
  quantity: '',
  min_stock_level: '',
  expiry_date: '',
  batch_number: '',
  shelf_name: '',
  ai_detection: '',
  cam_visibility: '',
  last_scan: '',
  restock_status: '',
  recommendation: '',
  ai_confidence: '',
};

type ShelfStatus = 'Healthy' | 'Low' | 'Critical' | 'Empty';

// ─────────────────────────────────────────────────────────────────────────
// Shelf status derivation — same low-stock logic you already had,
// extended into the 4-state badge system (Healthy / Low / Critical / Empty)
// ─────────────────────────────────────────────────────────────────────────
function getShelfStatus(p: Product): { label: ShelfStatus; color: string; bg: string } {
  const min = p.min_stock_level || 0;
  if (p.quantity <= 0) return { label: 'Empty', color: RED, bg: RED + '1E' };
  if (min > 0 && p.quantity < min / 2) return { label: 'Critical', color: RED, bg: RED + '1E' };
  if (min > 0 && p.quantity < min) return { label: 'Low', color: AMBER, bg: AMBER + '1E' };
  return { label: 'Healthy', color: GREEN, bg: GREEN + '1E' };
}

function defaultRestockStatus(status: ShelfStatus) {
  if (status === 'Empty' || status === 'Critical') return 'Priority';
  if (status === 'Low') return 'Pending';
  return 'Restocked';
}

function defaultRecommendation(status: ShelfStatus, p: Product) {
  if (status === 'Empty') return 'Empty, Urgent!';
  if (status === 'Critical') return 'Immediate Restock!';
  if (status === 'Low') {
    const suggested = Math.max((p.min_stock_level || 0) * 2 - p.quantity, 1);
    return `Restock ${suggested} units`;
  }
  return 'No action';
}

// ─────────────────────────────────────────────────────────────────────────
// Small SVG icon set (shared style with Dashboard's sidebar icons)
// ─────────────────────────────────────────────────────────────────────────
function Icon({ name, color, size = 15 }: { name: string; color: string; size?: number }) {
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
    bell: (<><Path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" {...p} /><Path d="M10 20a2 2 0 0 0 4 0" {...p} /></>),
    edit: (<><Path d="M4 20h4l10.5-10.5a2 2 0 0 0 0-2.8l-1.2-1.2a2 2 0 0 0-2.8 0L4 16v4Z" {...p} /></>),
    trash: (<><Path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13" {...p} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
}

// Small donut used for "Overall Shelf Health"
function Donut({ slices, size }: { slices: { value: number; color: string }[]; size: number }) {
  const r = size / 2, stroke = size * 0.22, radius = r - stroke / 2;
  const total = slices.reduce((s, x) => s + x.value, 0) || 1;
  const circ = 2 * Math.PI * radius;
  let offset = 0;
  return (
    <Svg width={size} height={size}>
      <G rotation={-90} origin={`${r}, ${r}`}>
        <Circle cx={r} cy={r} r={radius} stroke="#EDF1F6" strokeWidth={stroke} fill="none" />
        {slices.map((s, i) => {
          const len = (s.value / total) * circ;
          const el = (
            <Circle
              key={i}
              cx={r} cy={r} r={radius}
              stroke={s.color} strokeWidth={stroke} fill="none"
              strokeDasharray={`${len} ${circ - len}`}
              strokeDashoffset={-offset}
              strokeLinecap="butt"
            />
          );
          offset += len;
          return el;
        })}
      </G>
    </Svg>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Sidebar — same nav items/routes as the Dashboard, but highlights
// whichever route is actually active (so it works correctly from any screen)
// ─────────────────────────────────────────────────────────────────────────
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
            <Icon name={item.icon} color={isActive ? BLUE : MUTED} size={16} />
            <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>{item.label}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Main screen
// ─────────────────────────────────────────────────────────────────────────
export default function Inventory() {
  const [search, setSearch] = useState('');
  const [selCat, setSelCat] = useState('All');
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editProduct, setEditProduct] = useState<Product | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await fetchProducts();

      // ✅ Map backend fields directly — new fields fall back gracefully if absent
      const formatted: Product[] = data.map((p: any) => ({
        id: String(p.id),
        name: p.name,
        category: p.category || '',
        brand: p.brand || '',
        cost_price: p.cost_price,
        selling_price: p.selling_price,
        quantity: p.quantity,
        min_stock_level: p.min_stock_level ?? 5,
        expiry_date: p.expiry_date || '',
        batch_number: p.batch_number || '',
        shelf_name: p.shelf_name || '',
        ai_detection: p.ai_detection || 'OK',
        cam_visibility: p.cam_visibility || 'Clear',
        last_scan: p.last_scan || '',
        restock_status: p.restock_status || '',
        recommendation: p.recommendation || '',
        ai_confidence: p.ai_confidence ?? undefined,
      }));
      setProducts(formatted);

      const cats = ['All', ...Array.from(new Set(formatted.map(p => p.category).filter(Boolean)))];
      setCategories(cats);

    } catch (e) {
      Alert.alert("Error", "Failed to load products.");
      console.log("loadProducts error:", e);
    } finally {
      setLoading(false);
    }
  };

  const filtered = products.filter(p =>
    (selCat === 'All' || p.category === selCat) &&
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  // ✅ Existing alert logic, unchanged
  const lowStockCount = products.filter(p => p.quantity < p.min_stock_level).length;
  const expiryCount = products.filter(p => {
    if (!p.expiry_date) return false;
    const days = Math.floor((new Date(p.expiry_date).getTime() - Date.now()) / 86400000);
    return days < 30;
  }).length;

  const getDaysToExpiry = (expiry: string) => {
    if (!expiry) return null;
    return Math.floor((new Date(expiry).getTime() - Date.now()) / 86400000);
  };

  // ✅ New shelf/AI derived summaries
  const shelfStatuses = products.map(getShelfStatus);
  const healthyCount = shelfStatuses.filter(s => s.label === 'Healthy').length;
  const lowCount = shelfStatuses.filter(s => s.label === 'Low').length;
  const riskCount = shelfStatuses.filter(s => s.label === 'Critical' || s.label === 'Empty').length;
  const healthPct = products.length ? Math.round((healthyCount / products.length) * 100) : 100;

  const aiFlagged = products.filter(p =>
    (p.ai_detection && p.ai_detection !== 'OK') ||
    (p.cam_visibility && p.cam_visibility !== 'Clear')
  );

  const openEdit = (p: Product) => {
    setEditProduct(p);
    setForm({
      name: p.name,
      category: p.category,
      brand: p.brand,
      cost_price: String(p.cost_price),
      selling_price: String(p.selling_price),
      quantity: String(p.quantity),
      min_stock_level: String(p.min_stock_level),
      expiry_date: p.expiry_date,
      batch_number: p.batch_number,
      shelf_name: p.shelf_name || '',
      ai_detection: p.ai_detection || '',
      cam_visibility: p.cam_visibility || '',
      last_scan: p.last_scan || '',
      restock_status: p.restock_status || '',
      recommendation: p.recommendation || '',
      ai_confidence: p.ai_confidence !== undefined ? String(p.ai_confidence) : '',
    });
    setModalVisible(true);
  };

  const openAdd = () => {
    setEditProduct(null);
    setForm(emptyForm);
    setModalVisible(true);
  };

  const handleSave = async () => {
    if (!form.name.trim() || !form.selling_price || !form.quantity) {
      Alert.alert("Missing Info", "Name, selling price and quantity are required.");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        name: form.name.trim(),
        category: form.category.trim(),
        brand: form.brand.trim(),
        cost_price: Number(form.cost_price),
        selling_price: Number(form.selling_price),
        quantity: Number(form.quantity),
        min_stock_level: Number(form.min_stock_level) || 5,
        expiry_date: form.expiry_date.trim(),
        batch_number: form.batch_number.trim(),
        shelf_name: form.shelf_name.trim(),
        ai_detection: form.ai_detection.trim(),
        cam_visibility: form.cam_visibility.trim(),
        last_scan: form.last_scan.trim(),
        restock_status: form.restock_status.trim(),
        recommendation: form.recommendation.trim(),
        ai_confidence: form.ai_confidence ? Number(form.ai_confidence) : undefined,
      };

      if (editProduct) {
        await updateProduct(editProduct.id, payload);
      } else {
        await addProduct(payload);
      }

      setModalVisible(false);
      await loadProducts();

    } catch (e: any) {
      Alert.alert("Error", e.message || "Failed to save product.");
      console.log("handleSave error:", e);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = (id: string) => {
    Alert.alert(
      "Delete Product",
      "Are you sure?",
      [
        { text: "Cancel", style: "cancel" },
        { text: "Delete", style: "destructive", onPress: () => confirmDelete(id) },
      ]
    );
  };

  const confirmDelete = async (id: string) => {
    try {
      await deleteProduct(id);
      await loadProducts();
    } catch (e) {
      console.log("Delete error:", e);
    }
  };

  return (
    <View style={styles.appShell}>
      {/* Top bar */}
      <View style={styles.topBar}>
        <View style={styles.topBarLeft}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoBadgeText}>F</Text>
          </View>
          <Text style={styles.title}>Retail Command Center</Text>
        </View>
        <View style={styles.headerRight}>
          <View style={styles.bell}>
            <Icon name="bell" color={MUTED} size={18} />
            <View style={styles.bellDot} />
          </View>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>V</Text>
          </View>
        </View>
      </View>

      <View style={styles.body}>
        <Sidebar />

        <ScrollView
          style={styles.container}
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.pageTitle}>Inventory Management</Text>

          {/* Existing low-stock / expiry / total alert cards — kept as-is */}
          <View style={styles.grid}>
            <View style={[styles.alertCard, { backgroundColor: AMBER + '14', borderColor: AMBER + '44' }]}>
              <Text style={styles.alertIcon}>⚠️</Text>
              <View>
                <Text style={[styles.alertNum, { color: AMBER }]}>{lowStockCount}</Text>
                <Text style={styles.alertLabel}>Low Stock</Text>
              </View>
            </View>
            <View style={[styles.alertCard, { backgroundColor: RED + '14', borderColor: RED + '44' }]}>
              <Text style={styles.alertIcon}>📅</Text>
              <View>
                <Text style={[styles.alertNum, { color: RED }]}>{expiryCount}</Text>
                <Text style={styles.alertLabel}>Expiring Soon</Text>
              </View>
            </View>
            <View style={[styles.alertCard, { backgroundColor: BLUE + '14', borderColor: BLUE + '44' }]}>
              <Text style={styles.alertIcon}>📦</Text>
              <View>
                <Text style={[styles.alertNum, { color: BLUE }]}>{products.length}</Text>
                <Text style={styles.alertLabel}>Total Items</Text>
              </View>
            </View>
          </View>

          {/* New: Shelf Status / AI Monitoring / Overall Shelf Health cards */}
          <View style={styles.grid}>
            <View style={[styles.panel, { flexBasis: '31.5%' }]}>
              <Text style={styles.panelTitle}>Shelf Status</Text>
              <View style={styles.statusLegendCol}>
                <View style={styles.statusLegendRow}>
                  <View style={[styles.legendDot, { backgroundColor: GREEN }]} />
                  <Text style={styles.legendText}>Healthy</Text>
                  <Text style={styles.legendVal}>{healthyCount}</Text>
                </View>
                <View style={styles.statusLegendRow}>
                  <View style={[styles.legendDot, { backgroundColor: AMBER }]} />
                  <Text style={styles.legendText}>Low</Text>
                  <Text style={styles.legendVal}>{lowCount}</Text>
                </View>
                <View style={styles.statusLegendRow}>
                  <View style={[styles.legendDot, { backgroundColor: RED }]} />
                  <Text style={styles.legendText}>Critical / Empty</Text>
                  <Text style={styles.legendVal}>{riskCount}</Text>
                </View>
              </View>
            </View>

            <View style={[styles.panel, { flexBasis: '31.5%' }]}>
              <Text style={styles.panelTitle}>AI-Based Shelf Monitoring</Text>
              <Text style={styles.aiSummaryNum}>{aiFlagged.length}</Text>
              <Text style={styles.aiSummaryLabel}>shelves flagged by AI</Text>
              {aiFlagged.slice(0, 2).map(p => (
                <Text key={p.id} style={styles.aiFlagRow} numberOfLines={1}>
                  • {p.name} — {p.ai_detection !== 'OK' ? p.ai_detection : p.cam_visibility}
                </Text>
              ))}
              {aiFlagged.length === 0 && (
                <Text style={styles.aiFlagRowOk}>All shelves reporting normally</Text>
              )}
            </View>

            <View style={[styles.panel, { flexBasis: '31.5%' }]}>
              <Text style={styles.panelTitle}>Overall Shelf Health</Text>
              <View style={styles.donutRow}>
                <View style={{ position: 'relative' }}>
                  <Donut
                    slices={[
                      { value: healthyCount, color: GREEN },
                      { value: lowCount, color: AMBER },
                      { value: riskCount, color: RED },
                    ]}
                    size={84}
                  />
                  <View style={styles.donutCenter}>
                    <Text style={styles.donutPct}>{healthPct}%</Text>
                  </View>
                </View>
                <View style={{ gap: 6 }}>
                  <View style={styles.statusLegendRow}>
                    <View style={[styles.legendDot, { backgroundColor: GREEN }]} />
                    <Text style={styles.legendText}>Green</Text>
                  </View>
                  <View style={styles.statusLegendRow}>
                    <View style={[styles.legendDot, { backgroundColor: AMBER }]} />
                    <Text style={styles.legendText}>Yellow</Text>
                  </View>
                  <View style={styles.statusLegendRow}>
                    <View style={[styles.legendDot, { backgroundColor: RED }]} />
                    <Text style={styles.legendText}>Red</Text>
                  </View>
                </View>
              </View>
            </View>
          </View>

          {/* Table section */}
          <View style={styles.panel}>
            <View style={styles.tableTopRow}>
              <Text style={styles.panelTitle}>Inventory &amp; Shelf Status Table</Text>
              <TouchableOpacity style={styles.addBtn} onPress={openAdd}>
                <Text style={styles.addBtnText}>+ Add New Product</Text>
              </TouchableOpacity>
            </View>

            {/* Search + category filter — kept */}
            <View style={styles.searchRow}>
              <TextInput
                style={styles.searchInput}
                placeholder="🔍  Search products..."
                placeholderTextColor={FAINT}
                value={search}
                onChangeText={setSearch}
              />
            </View>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.catRow}>
              {categories.map(c => (
                <TouchableOpacity key={c} onPress={() => setSelCat(c)}
                  style={[styles.catPill, selCat === c && styles.catPillActive]}>
                  <Text style={[styles.catText, selCat === c && styles.catTextActive]}>{c}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {loading ? (
              <ActivityIndicator color={BLUE} style={{ marginTop: 40 }} />
            ) : (
              <ScrollView horizontal showsHorizontalScrollIndicator={true}>
                <View>
                  {/* Table header */}
                  <View style={styles.tableHeader}>
                    <Text style={[styles.th, { width: 160 }]}>Product Details</Text>
                    <Text style={[styles.th, { width: 90 }]}>Shelf Name</Text>
                    <Text style={[styles.th, { width: 90 }]}>Shelf Status</Text>
                    <Text style={[styles.th, { width: 100 }]}>AI Detection</Text>
                    <Text style={[styles.th, { width: 90 }]}>Cam. Visibility</Text>
                    <Text style={[styles.th, { width: 80 }]}>Last Scan</Text>
                    <Text style={[styles.th, { width: 90 }]}>Restock Status</Text>
                    <Text style={[styles.th, { width: 130 }]}>Recommendation</Text>
                    <Text style={[styles.th, { width: 80 }]}>AI Conf. (%)</Text>
                    <Text style={[styles.th, { width: 70 }]}>Actions</Text>
                  </View>

                  {/* Rows */}
                  {filtered.map(p => {
                    const days = getDaysToExpiry(p.expiry_date);
                    const status = getShelfStatus(p);
                    const restock = p.restock_status || defaultRestockStatus(status.label);
                    const recommendation = p.recommendation || defaultRecommendation(status.label, p);
                    const confidence = p.ai_confidence !== undefined ? `${p.ai_confidence}%` : '—';

                    return (
                      <View key={p.id} style={styles.row}>
                        <View style={{ width: 160 }}>
                          <Text style={styles.productName}>{p.name}</Text>
                          <Text style={styles.productId}>ID: {p.id}</Text>
                          {days !== null && days < 30 && (
                            <Text style={styles.expiryNote}>Expires in {days}d</Text>
                          )}
                        </View>

                        <Text style={[styles.td, { width: 90 }]}>{p.shelf_name || '—'}</Text>

                        <View style={{ width: 90 }}>
                          <View style={[styles.badge, { backgroundColor: status.bg }]}>
                            <Text style={[styles.badgeText, { color: status.color }]}>{status.label}</Text>
                          </View>
                        </View>

                        <Text style={[styles.td, { width: 100 }]}>{p.ai_detection || 'OK'}</Text>
                        <Text style={[styles.td, { width: 90 }]}>{p.cam_visibility || 'Clear'}</Text>
                        <Text style={[styles.td, { width: 80 }]}>{p.last_scan || '—'}</Text>
                        <Text style={[styles.td, { width: 90 }]}>{restock}</Text>
                        <Text style={[styles.td, { width: 130 }]} numberOfLines={2}>{recommendation}</Text>
                        <Text style={[styles.td, { width: 80 }]}>{confidence}</Text>

                        <View style={{ width: 70, flexDirection: 'row', gap: 10 }}>
                          <TouchableOpacity onPress={() => openEdit(p)}>
                            <Icon name="edit" color={BLUE} size={16} />
                          </TouchableOpacity>
                          <TouchableOpacity onPress={() => handleDelete(p.id)}>
                            <Icon name="trash" color={RED} size={16} />
                          </TouchableOpacity>
                        </View>
                      </View>
                    );
                  })}
                </View>
              </ScrollView>
            )}
          </View>
        </ScrollView>
      </View>

      {/* Add / Edit modal — original fields + new shelf/AI fields */}
      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>
              {editProduct ? 'Edit Product' : 'Add Product'}
            </Text>

            <ScrollView showsVerticalScrollIndicator={false}>
              {(
                [
                  { field: 'name',            label: 'Name *',           numeric: false },
                  { field: 'category',        label: 'Category',         numeric: false },
                  { field: 'brand',           label: 'Brand',            numeric: false },
                  { field: 'cost_price',      label: 'Cost Price *',     numeric: true  },
                  { field: 'selling_price',   label: 'Selling Price *',  numeric: true  },
                  { field: 'quantity',        label: 'Quantity *',       numeric: true  },
                  { field: 'min_stock_level', label: 'Min Stock Level',  numeric: true  },
                  { field: 'expiry_date',     label: 'Expiry (YYYY-MM-DD)', numeric: false },
                  { field: 'batch_number',    label: 'Batch Number',     numeric: false },
                  { field: 'shelf_name',      label: 'Shelf Name (e.g. A3,B2)', numeric: false },
                  { field: 'ai_detection',    label: 'AI Detection (OK / Degraded / Error)', numeric: false },
                  { field: 'cam_visibility',  label: 'Camera Visibility (Clear / Obscured)', numeric: false },
                  { field: 'last_scan',       label: 'Last Scan (e.g. 10m ago)', numeric: false },
                  { field: 'restock_status',  label: 'Restock Status (Restocked / Pending / Priority)', numeric: false },
                  { field: 'recommendation',  label: 'Recommendation', numeric: false },
                  { field: 'ai_confidence',   label: 'AI Confidence (%)', numeric: true },
                ] as const
              ).map(({ field, label, numeric }) => (
                <TextInput
                  key={field}
                  style={styles.modalInput}
                  placeholder={label}
                  placeholderTextColor={FAINT}
                  value={form[field]}
                  onChangeText={v => setForm({ ...form, [field]: v })}
                  keyboardType={numeric ? 'numeric' : 'default'}
                />
              ))}
            </ScrollView>

            <View style={styles.modalBtns}>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setModalVisible(false)}>
                <Text style={styles.cancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.saveBtn, saving && { opacity: 0.6 }]}
                onPress={handleSave}
                disabled={saving}
              >
                {saving
                  ? <ActivityIndicator color="#fff" />
                  : <Text style={styles.saveText}>Save</Text>
                }
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  appShell: { flex: 1, backgroundColor: PAGE },

  topBar: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12,
    backgroundColor: CARD, borderBottomWidth: 1, borderBottomColor: BORDER,
  },
  topBarLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  logoBadge: { width: 30, height: 30, borderRadius: 9, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  logoBadgeText: { color: '#fff', fontWeight: '900', fontSize: 14 },
  title: { fontSize: 17, fontWeight: '900', color: TEXT, letterSpacing: -0.4 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  bell: { width: 34, height: 34, borderRadius: 11, backgroundColor: CARD, borderWidth: 1, borderColor: BORDER, alignItems: 'center', justifyContent: 'center' },
  bellDot: { position: 'absolute', top: 8, right: 9, width: 6, height: 6, borderRadius: 3, backgroundColor: RED },
  avatar: { width: 34, height: 34, borderRadius: 17, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '800', fontSize: 14 },

  body: { flex: 1, flexDirection: 'row' },

  sidebar: {
    width: SIDEBAR_WIDTH, backgroundColor: CARD,
    borderRightWidth: 1, borderRightColor: BORDER,
    paddingVertical: 14, paddingHorizontal: 10, gap: 3,
  },
  navItem: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 10, paddingHorizontal: 12, borderRadius: 10 },
  navItemActive: { backgroundColor: BLUE + '14' },
  navLabel: { fontSize: 13, fontWeight: '600', color: MUTED },
  navLabelActive: { color: BLUE, fontWeight: '800' },

  container: { flex: 1, backgroundColor: PAGE },
  content: { padding: 10, paddingBottom: 40, gap: 10 },

  pageTitle: { fontSize: 18, fontWeight: '900', color: TEXT, marginBottom: 2 },

  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },

  alertCard: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 10, borderRadius: radius.md, borderWidth: 1.5, padding: 12, minWidth: 140 },
  alertIcon: { fontSize: 20 },
  alertNum: { fontSize: 20, fontWeight: '900' },
  alertLabel: { fontSize: 11, color: MUTED },

  panel: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 14,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },
  panelTitle: { fontSize: 13, fontWeight: '800', color: TEXT, marginBottom: 10 },

  statusLegendCol: { gap: 8 },
  statusLegendRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  legendDot: { width: 10, height: 10, borderRadius: 5 },
  legendText: { fontSize: 12, color: MUTED, flex: 1 },
  legendVal: { fontSize: 12, fontWeight: '800', color: TEXT },

  aiSummaryNum: { fontSize: 26, fontWeight: '900', color: TEXT },
  aiSummaryLabel: { fontSize: 11, color: MUTED, marginBottom: 8 },
  aiFlagRow: { fontSize: 11, color: TEXT, marginTop: 3 },
  aiFlagRowOk: { fontSize: 11, color: GREEN, marginTop: 3, fontWeight: '600' },

  donutRow: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  donutCenter: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' },
  donutPct: { fontSize: 15, fontWeight: '900', color: TEXT },

  tableTopRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 },
  addBtn: { backgroundColor: BLUE, borderRadius: radius.sm, paddingHorizontal: 14, paddingVertical: 9 },
  addBtnText: { color: '#fff', fontWeight: '800', fontSize: 12 },

  searchRow: { flexDirection: 'row', gap: 10, marginBottom: 10 },
  searchInput: {
    flex: 1, borderWidth: 1, borderColor: BORDER, borderRadius: radius.sm,
    padding: 10, fontSize: 13, color: TEXT, backgroundColor: PAGE,
  },
  catRow: { marginBottom: 12 },
  catPill: {
    paddingHorizontal: 16, height: 32, borderRadius: 20, backgroundColor: PAGE,
    marginRight: 8, borderWidth: 1, borderColor: BORDER,
    justifyContent: 'center', alignItems: 'center',
  },
  catPillActive: { backgroundColor: BLUE },
  catText: { fontSize: 12, color: MUTED, fontWeight: '600' },
  catTextActive: { color: '#fff' },

  tableHeader: {
    flexDirection: 'row', paddingVertical: 8, paddingHorizontal: 12,
    backgroundColor: PAGE, borderRadius: radius.sm, marginBottom: 6,
  },
  th: { fontSize: 10, color: MUTED, fontWeight: '700', textTransform: 'uppercase' },

  row: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: CARD,
    borderRadius: radius.sm, padding: 12, marginBottom: 6,
    borderWidth: 1, borderColor: BORDER,
  },
  productName: { fontSize: 13, fontWeight: '700', color: TEXT },
  productId: { fontSize: 10, color: FAINT, marginTop: 1 },
  expiryNote: { fontSize: 10, color: RED, marginTop: 1, fontWeight: '600' },
  td: { fontSize: 12, color: MUTED },

  badge: { alignSelf: 'flex-start', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  badgeText: { fontSize: 10, fontWeight: '800' },

  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalCard: {
    backgroundColor: CARD, borderTopLeftRadius: 24, borderTopRightRadius: 24,
    padding: 24, maxHeight: '85%', borderWidth: 1, borderColor: BORDER,
  },
  modalTitle: { fontSize: 18, fontWeight: '800', color: TEXT, marginBottom: 16 },
  modalInput: {
    borderWidth: 1, borderColor: BORDER, borderRadius: radius.sm, padding: 12,
    fontSize: 13, color: TEXT, marginBottom: 10, backgroundColor: PAGE,
  },
  modalBtns: { flexDirection: 'row', gap: 12, marginTop: 8 },
  cancelBtn: { flex: 1, padding: 14, borderRadius: radius.sm, borderWidth: 1.5, borderColor: BORDER, alignItems: 'center' },
  cancelText: { color: MUTED, fontWeight: '700' },
  saveBtn: { flex: 1, padding: 14, borderRadius: radius.sm, backgroundColor: BLUE, alignItems: 'center' },
  saveText: { color: '#fff', fontWeight: '700' },
});
