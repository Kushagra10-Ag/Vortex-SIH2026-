import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, Modal, ActivityIndicator, Alert,
} from 'react-native';
import { colors, radius } from '../../constants/theme';
import { fetchProducts, addProduct, updateProduct, deleteProduct } from '../../services/api';

// ✅ Type matches your backend Product model exactly
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
};

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

      // ✅ Map backend fields directly — no renaming
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
      }));
      console.log("FORMATTED:", formatted);
      setProducts(formatted);

      // ✅ Build category list dynamically from real data
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

  // ✅ Uses min_stock_level from backend instead of hardcoded 10
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
      };

      if (editProduct) {
        await updateProduct(editProduct.id, payload);
      } else {
        await addProduct(payload);
      }

      setModalVisible(false);
      await loadProducts(); // ✅ Refresh from backend after save

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
      {
        text: "Delete",
        style: "destructive",
        onPress: () => confirmDelete(id), // 🔥 separate function
      },
    ]
  );
};

const confirmDelete = async (id: string) => {
  try {
    console.log("Deleting:", id);

    await deleteProduct(id); // 🔥 ensure number
    await loadProducts(); // 🔥 refresh

  } catch (e) {
    console.log("Delete error:", e);
  }
};

  return (
<ScrollView
  style={styles.container}
  showsVerticalScrollIndicator={false}
  contentContainerStyle={{ paddingBottom: 100 }}
>      {/* Alert cards */}
      <View style={styles.alertRow}>
        <View style={[styles.alertCard, { backgroundColor: colors.warning + '18', borderColor: colors.warning + '44' }]}>
          <Text style={styles.alertIcon}>⚠️</Text>
          <View>
            <Text style={[styles.alertNum, { color: colors.warning }]}>{lowStockCount}</Text>
            <Text style={styles.alertLabel}>Low Stock</Text>
          </View>
        </View>
        <View style={[styles.alertCard, { backgroundColor: colors.danger + '18', borderColor: colors.danger + '44' }]}>
          <Text style={styles.alertIcon}>📅</Text>
          <View>
            <Text style={[styles.alertNum, { color: colors.danger }]}>{expiryCount}</Text>
            <Text style={styles.alertLabel}>Expiring Soon</Text>
          </View>
        </View>
        <View style={[styles.alertCard, { backgroundColor: colors.accent + '18', borderColor: colors.accent + '44' }]}>
          <Text style={styles.alertIcon}>📦</Text>
          <View>
            <Text style={[styles.alertNum, { color: colors.accent }]}>{products.length}</Text>
            <Text style={styles.alertLabel}>Total Items</Text>
          </View>
        </View>
      </View>

      {/* Search + Add */}
      <View style={styles.searchRow}>
        <TextInput
          style={styles.searchInput}
          placeholder="🔍  Search products..."
          placeholderTextColor={colors.textSub}
          value={search}
          onChangeText={setSearch}
        />
        <TouchableOpacity style={styles.addBtn} onPress={openAdd}>
          <Text style={styles.addBtnText}>+ Add</Text>
        </TouchableOpacity>
      </View>

      {/* Category filter — built from real backend data */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.catRow}>
        {categories.map(c => (
          <TouchableOpacity key={c} onPress={() => setSelCat(c)}
            style={[styles.catPill, selCat === c && styles.catPillActive]}>
            <Text style={[styles.catText, selCat === c && styles.catTextActive]}>{c}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Product list */}
{loading ? (
  <ActivityIndicator color={colors.primary} style={{ marginTop: 40 }} />
) : (
  <>
    {/* Table Header */}
    <View style={styles.tableHeader}>
      {['Product', 'Category', 'Price', 'Stock', 'Expiry', ''].map((h, i) => (
        <Text
          key={i}
          style={[
            styles.th,
            i === 0 && { flex: 1.5 },
            i === 1 && { flex: 1.5 },
          ]}
        >
          {h}
        </Text>
      ))}
    </View>

    {/* Rows */}
    {filtered.map(p => {
      const days = getDaysToExpiry(p.expiry_date);
      const isLow = p.quantity < p.min_stock_level;
      const isExpiring = days !== null && days < 30;

      return (
        <View key={p.id} style={[styles.row, isLow && styles.rowWarning]}>
          
          <View style={{ flex: 1.5 }}>
            <Text style={styles.productName}>{p.name}</Text>
            {isLow && (
              <View style={styles.lowBadge}>
                <Text style={styles.lowBadgeText}>Low</Text>
              </View>
            )}
          </View>

          <Text style={[styles.td, { flex: 1.5 }]}>{p.category}</Text>
          <Text style={styles.td}>₹{p.selling_price}</Text>

          <Text style={[
            styles.td,
            { color: isLow ? colors.danger : colors.accent, fontWeight: '700' }
          ]}>
            {p.quantity}
          </Text>

          <Text style={[
            styles.td,
            { color: isExpiring ? colors.danger : colors.textSub }
          ]}>
            {days !== null ? `${days}d` : '—'}
          </Text>

          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TouchableOpacity onPress={() => openEdit(p)}>
              <Text style={{ fontSize: 15 }}>✏️</Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => handleDelete(p.id)}>
              <Text style={{ fontSize: 15 }}>🗑️</Text>
            </TouchableOpacity>
          </View>

        </View>
      );
    })}
  </>
)}
    

  
        

      {/* Modal */}
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
                ] as const
              ).map(({ field, label, numeric }) => (
                <TextInput
                  key={field}
                  style={styles.modalInput}
                  placeholder={label}
                  placeholderTextColor={colors.textSub}
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
    </ScrollView>
  );
}

const styles = StyleSheet.create({
container: {
  flex: 1,
  backgroundColor: '#020617',  // ✅ SAME as Sales
},  alertRow: { flexDirection: 'row', gap: 10, marginBottom: 14 },
  alertCard: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 10, borderRadius: radius.md, borderWidth: 1.5, padding: 12 },
  alertIcon: { fontSize: 22 },
  alertNum: { fontSize: 22, fontWeight: '900' },
  alertLabel: { fontSize: 11, color: colors.textSub },
  searchRow: { flexDirection: 'row', gap: 10, marginBottom: 10 },
searchInput: {
  flex: 1,
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.1)',
  borderRadius: radius.sm,
  padding: 10,
  fontSize: 13,
  color: '#E6EDF3',
  backgroundColor: '#0F172A',
},  addBtn: { backgroundColor: colors.primary, borderRadius: radius.sm, paddingHorizontal: 18, justifyContent: 'center' },
  addBtnText: { color: '#fff', fontWeight: '800', fontSize: 13 },
  catRow: { marginBottom: 12 },
catPill: {
  paddingHorizontal: 16,
  height: 32,                 // ✅ FIXED HEIGHT
  borderRadius: 20,
  backgroundColor: '#0F172A',
  marginRight: 8,
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.05)',
  justifyContent: 'center',   // ✅ vertical center
  alignItems: 'center',       // ✅ horizontal center
},
catPillActive: {
  backgroundColor: '#2563EB',
},  catText: {
  fontSize: 12,
  color: colors.textSub,
  fontWeight: '600',
  textAlign: 'center',   // ✅ ensure centering
},
  catTextActive: { color: '#fff' },
tableHeader: {
  flexDirection: 'row',
  paddingVertical: 8,
  paddingHorizontal: 12,
  backgroundColor: '#0F172A',  // same as sales
  borderRadius: radius.sm,
  marginBottom: 6,
},  th: { flex: 1, fontSize: 11, color: 'rgba(255,255,255,0.6)', fontWeight: '700', textTransform: 'uppercase' },
row: {
  flexDirection: 'row',
  alignItems: 'center',
  backgroundColor: '#1E293B',   // ✅ dark like sales
  borderRadius: radius.sm,
  padding: 12,
  marginBottom: 6,
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.05)',
},  rowWarning: { borderLeftWidth: 3, borderLeftColor: colors.warning },
productName: {
  fontSize: 13,
  fontWeight: '700',
  color: '#E6EDF3',   // bright text like sales
},  lowBadge: { backgroundColor: colors.danger + '22', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, alignSelf: 'flex-start', marginTop: 2 },
  lowBadgeText: { color: colors.danger, fontSize: 9, fontWeight: '700' },
td: {
  flex: 1,
  fontSize: 13,
  color: '#CBD5E1',   // same as sales
},  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
modalCard: {
  backgroundColor: '#0F172A',   // ✅ DARK like your UI
  borderTopLeftRadius: 24,
  borderTopRightRadius: 24,
  padding: 24,
  maxHeight: '85%',
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.05)',
},
  modalTitle: { fontSize: 18, fontWeight: '800', color: colors.text, marginBottom: 16 },
modalInput: {
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.1)',
  borderRadius: radius.sm,
  padding: 12,
  fontSize: 13,
  color: '#E6EDF3',
  marginBottom: 10,
  backgroundColor: '#020617',   // ✅ match main bg
},
  modalBtns: { flexDirection: 'row', gap: 12, marginTop: 8 },
  cancelBtn: { flex: 1, padding: 14, borderRadius: radius.sm, borderWidth: 1.5, borderColor: colors.border, alignItems: 'center' },
  cancelText: { color: colors.textSub, fontWeight: '700' },
  saveBtn: { flex: 1, padding: 14, borderRadius: radius.sm, backgroundColor: '#2563EB', alignItems: 'center' },
  saveText: { color: '#fff', fontWeight: '700' },
});