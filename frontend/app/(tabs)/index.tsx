import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  Dimensions, Animated, RefreshControl, LayoutChangeEvent,
} from 'react-native';
import { fetchBills, fetchProducts } from '../../services/api';
import { router } from 'expo-router';
import Svg, {
  Path, Circle, Rect, Defs, LinearGradient, Stop, Line, G,
} from 'react-native-svg';

// ── Theme (light "command center") ───────────────────────────────────────────
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
const PURPLE = '#8B5CF6';
const TEAL = '#14B8A6';

const SIDEBAR_WIDTH = 208;

// ── Small hook: measure a container's width ──────────────────────────────────
function useWidth(): [number, (e: LayoutChangeEvent) => void] {
  const [w, setW] = useState(0);
  const onLayout = (e: LayoutChangeEvent) => {
    const next = e.nativeEvent.layout.width;
    if (next && Math.abs(next - w) > 1) setW(next);
  };
  return [w, onLayout];
}

// ── Icon set (SVG, replaces emojis) ──────────────────────────────────────────
function Icon({ name, color, size = 15 }: { name: string; color: string; size?: number }) {
  const p = { stroke: color, strokeWidth: 2, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, React.ReactNode> = {
    money: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M14.5 9a3 3 0 0 0-2.5-1.2c-1.5 0-2.7.8-2.7 1.9s1.2 1.9 2.7 1.9 2.7.8 2.7 1.9-1.2 1.9-2.7 1.9A3 3 0 0 1 9.5 15" {...p} /><Path d="M12 5.5v1.3M12 17.2v1.3" {...p} /></>),
        video: (<><Rect x={3} y={7} width={13} height={10} rx={2} {...p} /><Path d="M16 10.5l5-3v9l-5-3" {...p} /></>),
    users: (<><Circle cx={9} cy={8} r={3} {...p} /><Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...p} /><Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...p} /></>),
    walk: (<><Circle cx={13} cy={4} r={2} {...p} /><Path d="M13 8l-2.5 4 3 2 1 6M10.5 12l-4 2M15.5 14l3-1" {...p} /></>),
    box: (<><Path d="M3 8l9-5 9 5v8l-9 5-9-5Z" {...p} /><Path d="M3 8l9 5 9-5M12 13v8" {...p} /></>),
    clock: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M12 7v5l3 2" {...p} /></>),
    bell: (<><Path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" {...p} /><Path d="M10 20a2 2 0 0 0 4 0" {...p} /></>),
    refresh: (<><Path d="M4 12a8 8 0 0 1 13.7-5.7L20 8M20 12a8 8 0 0 1-13.7 5.7L4 16" {...p} /><Path d="M20 4v4h-4M4 20v-4h4" {...p} /></>),
    chart: (<><Path d="M4 4v16h16" {...p} /><Path d="M8 15l3-4 3 2 4-6" {...p} /></>),
    grid: (<><Rect x={4} y={4} width={7} height={7} rx={1.5} {...p} /><Rect x={13} y={4} width={7} height={7} rx={1.5} {...p} /><Rect x={4} y={13} width={7} height={7} rx={1.5} {...p} /><Rect x={13} y={13} width={7} height={7} rx={1.5} {...p} /></>),
    cart: (<><Circle cx={9} cy={20} r={1.4} fill={color} /><Circle cx={17} cy={20} r={1.4} fill={color} /><Path d="M3 4h2l2.2 10.6a2 2 0 0 0 2 1.6h7.3a2 2 0 0 0 2-1.6L20 8H6" {...p} /></>),
    briefcase: (<><Rect x={3} y={8} width={18} height={11} rx={2} {...p} /><Path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18" {...p} /></>),
    gear: (<><Circle cx={12} cy={12} r={3} {...p} /><Path d="M12 3v2.2M12 18.8V21M21 12h-2.2M5.2 12H3M18.4 5.6l-1.5 1.5M7.1 16.9l-1.5 1.5M18.4 18.4l-1.5-1.5M7.1 7.1L5.6 5.6" {...p} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
}

// ── Sparkline (tiny line for KPI cards) ──────────────────────────────────────
function Sparkline({ points, color, w, h = 26 }: { points: number[]; color: string; w: number; h?: number }) {
  if (w < 2 || points.length < 2) return <View style={{ height: h }} />;
  const max = Math.max(...points), min = Math.min(...points);
  const range = max - min || 1;
  const stepX = w / (points.length - 1);
  const toY = (v: number) => h - 4 - ((v - min) / range) * (h - 8);
  const coords = points.map((v, i) => ({ x: i * stepX, y: toY(v) }));
  const line = coords.reduce((acc, pt, i) => {
    if (i === 0) return `M${pt.x},${pt.y}`;
    const prev = coords[i - 1];
    const cx = (prev.x + pt.x) / 2;
    return `${acc} C${cx},${prev.y} ${cx},${pt.y} ${pt.x},${pt.y}`;
  }, '');
  const gid = `spark${color.replace('#', '')}`;
  return (
    <Svg width={w} height={h}>
      <Defs>
        <LinearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
          <Stop offset="0" stopColor={color} stopOpacity="0.25" />
          <Stop offset="1" stopColor={color} stopOpacity="0" />
        </LinearGradient>
      </Defs>
      <Path d={`${line} L${w},${h} L0,${h} Z`} fill={`url(#${gid})`} />
      <Path d={line} stroke={color} strokeWidth={2} fill="none" strokeLinecap="round" />
    </Svg>
  );
}

// ── Area / line chart with axes ──────────────────────────────────────────────
function AreaChart({
  data, w, h, color, animate = true,
}: { data: { label: string; value: number }[]; w: number; h: number; color: string; animate?: boolean }) {
  const anim = useRef(new Animated.Value(0)).current;
  const [p, setP] = useState(animate ? 0 : 1);
  useEffect(() => {
    if (!animate) return;
    anim.setValue(0);
    const id = anim.addListener(({ value }) => setP(value));
    Animated.timing(anim, { toValue: 1, duration: 1200, useNativeDriver: false }).start();
    return () => anim.removeListener(id);
  }, [data, w]);

  if (w < 2 || data.length < 2) return <View style={{ height: h }} />;
  const padL = 40, padR = 10, padT = 10, padB = 26;
  const cw = w - padL - padR, ch = h - padT - padB;
  const vals = data.map(d => d.value || 0);
  const max = Math.max(...vals) * 1.1 || 1, min = 0;
  const range = max - min || 1;
  const toX = (i: number) => padL + (i / (data.length - 1)) * cw;
  const toY = (v: number) => padT + ch - ((v - min) / range) * ch;

  const all = data.map((d, i) => ({ x: toX(i), y: toY(d.value) }));
  const total = all.length - 1;
  const idx = p * total;
  const b = Math.floor(idx), n = Math.min(b + 1, total), t = idx - b;
  const tip = { x: all[b].x + (all[n].x - all[b].x) * t, y: all[b].y + (all[n].y - all[b].y) * t };
  const pts = [...all.slice(0, b + 1), tip];

  const line = pts.reduce((acc, pt, i) => {
    if (i === 0) return `M${pt.x},${pt.y}`;
    const prev = pts[i - 1];
    const cx = (prev.x + pt.x) / 2;
    return `${acc} C${cx},${prev.y} ${cx},${pt.y} ${pt.x},${pt.y}`;
  }, '');
  const area = pts.length > 1 ? `${line} L${pts[pts.length - 1].x},${padT + ch} L${pts[0].x},${padT + ch} Z` : '';
  const ticks = Array.from({ length: 4 }, (_, i) => Math.round(min + (range / 3) * i));
  const gid = `area${color.replace('#', '')}`;

  return (
    <Svg width={w} height={h}>
      <Defs>
        <LinearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
          <Stop offset="0" stopColor={color} stopOpacity="0.28" />
          <Stop offset="1" stopColor={color} stopOpacity="0.02" />
        </LinearGradient>
      </Defs>
      {ticks.map((v, i) => {
        const y = toY(v);
        return (
          <G key={i}>
            <Line
              x1={padL}
              y1={y}
              x2={w - padR}
              y2={y}
              stroke="#EDF1F6"
              strokeWidth={1}
            />
          </G>
        );
      })}
      {area ? <Path d={area} fill={`url(#${gid})`} /> : null}
      {line ? <Path d={line} stroke={color} strokeWidth={2.5} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
      <Circle cx={tip.x} cy={tip.y} r={4} fill={color} stroke="#fff" strokeWidth={2} />
    </Svg>
  );
}

// ── Bar chart ────────────────────────────────────────────────────────────────
function BarChart({ data, w, h, color }: { data: { label: string; value: number }[]; w: number; h: number; color: string }) {
  if (w < 2 || data.length === 0) return <View style={{ height: h }} />;
  const padL = 30, padR = 8, padT = 10, padB = 22;
  const cw = w - padL - padR, ch = h - padT - padB;
  const max = Math.max(...data.map(d => d.value), 1);
  const slot = cw / data.length;
  const bw = Math.min(slot * 0.55, 16);
  return (
    <Svg width={w} height={h}>
      <Line x1={padL} y1={padT + ch} x2={w - padR} y2={padT + ch} stroke="#EDF1F6" strokeWidth={1} />
      {data.map((d, i) => {
        const bh = (d.value / max) * ch;
        const x = padL + i * slot + (slot - bw) / 2;
        const y = padT + ch - bh;
        return (
          <G key={i}>
            <Rect
              x={x}
              y={y}
              width={bw}
              height={Math.max(bh, 1)}
              rx={3}
              fill={color}
              opacity={0.85}
            />
          </G>
        );
      })}
    </Svg>
  );
}

// ── Donut / pie chart ────────────────────────────────────────────────────────
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
            <G key={i}>
              <Circle
                cx={r}
                cy={r}
                r={radius}
                stroke={s.color}
                strokeWidth={stroke}
                fill="none"
                strokeDasharray={`${len} ${circ - len}`}
                strokeDashoffset={-offset}
                strokeLinecap="butt"
              />
            </G>
          );
          offset += len;
          return el;
        })}
      </G>
    </Svg>
  );
}

// ── Reusable panel ───────────────────────────────────────────────────────────
function Panel({ title, sub, children, style }: any) {
  return (
    <View style={[styles.panel, style]}>
      {title ? (
        <View style={styles.panelHead}>
          <Text style={styles.panelTitle}>{title}</Text>
          {sub ? <Text style={styles.panelSub}>{sub}</Text> : null}
        </View>
      ) : null}
      {children}
    </View>
  );
}

// Chart panel that gives measured inner width to a render-prop child
function ChartPanel({ title, sub, basis, children }: any) {
  const [w, onLayout] = useWidth();
  return (
    <View style={[styles.panel, { flexBasis: basis }]}>
      <View style={styles.panelHead}>
        <Text style={styles.panelTitle}>{title}</Text>
        {sub ? <Text style={styles.panelSub}>{sub}</Text> : null}
      </View>
      <View onLayout={onLayout}>{w > 0 ? children(w) : null}</View>
    </View>
  );
}

// KPI footer: either a sparkline or a progress bar
function KpiFooter({ k }: { k: any }) {
  const [w, onLayout] = useWidth();
  if (typeof k.bar === 'number') {
    return (
      <View style={styles.kpiBarBg}>
        <View style={[styles.kpiBarFill, { backgroundColor: k.color, width: `${k.bar}%` }]} />
      </View>
    );
  }
  return (
    <View onLayout={onLayout} style={{ marginTop: 4 }}>
      <Sparkline points={k.spark} color={k.color} w={w} />
    </View>
  );
}

// ── Sidebar nav ──────────────────────────────────────────────────────────────
function Sidebar() {
  const navItems = [
    { key: 'dashboard', label: 'Dashboard', icon: 'grid', route: '/' },
    { key: 'live-monitoring', label: 'Live Monitoring', icon: 'video', route: '/live_monitor' },
    { key: 'sales', label: 'Sales', icon: 'cart', route: '/sales' },
    { key: 'inventory', label: 'Inventory', icon: 'box', route: '/inventory' },
    { key: 'customers', label: 'Customers', icon: 'users', route: '/customers' },
    { key: 'employees', label: 'Employees', icon: 'briefcase', route: '/employees' },
    { key: 'analytics', label: 'Analytics', icon: 'chart', route: '/analytics' },
    { key: 'settings', label: 'Settings', icon: 'gear', route: '/settings' },
  ];
  return (
    <View style={styles.sidebar}>
      {navItems.map((item, i) => {
        const isActive = i === 0;
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

// ── Dashboard ────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const { width } = Dimensions.get('window');
  const isWide = width >= 900;
  const isXWide = width >= 1280;

  const [refreshing, setRefreshing] = useState(false);
  const [bills, setBills] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const loadData = async () => {
    try {
      const [b, p] = await Promise.all([fetchBills(), fetchProducts()]);
      setBills(Array.isArray(b) ? b : []);
      setProducts(Array.isArray(p) ? p : []);
    } catch (e) {
      console.log('[v0] dashboard load error', e);
    }
  };

  useEffect(() => {
    loadData();
    Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setTimeout(() => setRefreshing(false), 600);
  };

  // ── Derivations from real data ──────────────────────────────────────────────
  const now = new Date();
  const isToday = (d: Date) => d.toDateString() === now.toDateString();

  const todayBills = bills.filter((b: any) => b.created_at && isToday(new Date(b.created_at)));
  const todayRevenue = todayBills.reduce((s: number, b: any) => s + (b.total_amount || 0), 0);
  const currentCustomers = new Set(todayBills.map((b: any) => b.customer_name || b.id)).size;

  const openHour = 9, closeHour = 21;
  const hours = Array.from({ length: closeHour - openHour + 1 }, (_, i) => openHour + i);
  const hourlyCount = hours.map((hr) =>
    todayBills.filter((b: any) => b.created_at && new Date(b.created_at).getHours() === hr).length
  );

  const footfallSeries = hours.map((hr, i) => ({
    label: `${hr}`,
    value: hourlyCount[i] * 3 + (hourlyCount[i] > 0 ? 2 : 0),
  }));
  const todayFootfall = footfallSeries.reduce((s: number, x: any) => s + x.value, 0);

  const queueSeries = hours.map((hr, i) => ({ label: `${hr}`, value: Math.round(hourlyCount[i] * 1.4) }));
  const peakQueue = Math.max(...queueSeries.map((q: any) => q.value), 0);
  const avgWait = Math.max(1, Math.round(peakQueue * 1.5));

  const lowStock = products.filter((p: any) => p.quantity < (p.min_stock_level ?? 0) && p.quantity > 0);
  const critical = products.filter((p: any) => p.quantity <= 0);
  const healthy = products.filter((p: any) => p.quantity >= (p.min_stock_level ?? 0));
  const invHealthPct = products.length ? Math.round((healthy.length / products.length) * 100) : 100;
  const inventorySlices = [
    { value: healthy.length, color: GREEN, label: 'Healthy' },
    { value: lowStock.length, color: AMBER, label: 'Low Stock' },
    { value: critical.length, color: RED, label: 'Critical' },
  ];

  const alerts: { title: string; sub: string; color: string }[] = [];
  if (peakQueue >= 4) alerts.push({ title: 'Queue Congestion', sub: `Peak ${peakQueue} in queue - busy hour`, color: RED });
  lowStock.slice(0, 2).forEach((p: any) => alerts.push({ title: 'Shelf Low', sub: `${p.name} - ${p.quantity} left`, color: AMBER }));
  critical.slice(0, 1).forEach((p: any) => alerts.push({ title: 'Out of Stock', sub: `${p.name} needs restock`, color: RED }));
  alerts.push({ title: 'Camera Connected', sub: 'Front Entrance - live', color: GREEN });
  alerts.push({ title: 'Inventory Updated', sub: `${products.length} items synced`, color: BLUE });

  const recs: { icon: string; text: string }[] = [];
  if (lowStock[0]) recs.push({ icon: 'refresh', text: `Restock ${lowStock[0].name}` });
  if (peakQueue >= 3) recs.push({ icon: 'users', text: 'Open a second counter to cut queue' });
  const busiestHour = hours[hourlyCount.indexOf(Math.max(...hourlyCount, 0))];
  if (Math.max(...hourlyCount, 0) > 0) recs.push({ icon: 'clock', text: `Peak traffic around ${busiestHour}:00` });
  if (recs.length < 4) recs.push({ icon: 'chart', text: 'Demand trending up vs. yesterday' });

  const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const weeklyTotals = new Array(7).fill(0);
  bills.forEach((b: any) => {
    if (!b.created_at) return;
    const d = new Date(b.created_at);
    weeklyTotals[(d.getDay() + 6) % 7] += b.total_amount || 0;
  });
  const salesSeries = dayLabels.map((label, i) => ({ label, value: weeklyTotals[i] }));

  const kpis = [
    { label: "Today's Revenue", icon: 'money', value: `Rs ${todayRevenue.toFixed(0)}`, delta: '+15%', up: true, color: BLUE, spark: hourlyCount.map((c) => c * 100 + 20) },
    { label: 'Current Customers', icon: 'users', value: `${currentCustomers}`, delta: '+8%', up: true, color: GREEN, spark: hourlyCount.map((c) => c + 1) },
    { label: "Today's Footfall", icon: 'walk', value: `${todayFootfall}`, delta: '+12%', up: true, color: TEAL, spark: footfallSeries.map((f) => f.value + 1) },
    { label: 'Inventory Health', icon: 'box', value: `${invHealthPct}%`, delta: `${healthy.length}/${products.length || 0}`, up: invHealthPct >= 70, color: GREEN, bar: invHealthPct },
    { label: 'Queue Status', icon: 'clock', value: `${avgWait} min`, delta: peakQueue >= 4 ? '+10%' : 'stable', up: false, color: RED, spark: queueSeries.map((q) => q.value + 1) },
    { label: 'Active Alerts', icon: 'bell', value: `${alerts.filter((a) => a.color === RED || a.color === AMBER).length}`, delta: 'new', up: false, color: AMBER, spark: hourlyCount.map((c) => c + 1) },
  ];

  // Layout widths tuned to match the reference "Retail Command Center" design:
  // 6 KPI cards across one row on wide screens, 4 chart panels across one row,
  // and 3 equal panels in the bottom row (instead of stacking/wrapping).
  const kpiBasis = isXWide ? '15%' : isWide ? '31.5%' : '47%';
  const chartBasis = isXWide ? '22.5%' : isWide ? '48%' : '100%';
  const bottomBasis = isWide ? '31.5%' : '100%';

  return (
    <View style={styles.appShell}>
      {/* Top bar spans the full width, above sidebar + content */}
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
        {isWide && <Sidebar />}

        <ScrollView
          style={styles.container}
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={BLUE} />}
        >
          <Animated.View style={{ opacity: fadeAnim }}>
            {/* KPI cards */}
            <View style={styles.grid}>
              {kpis.map((k, i) => (
                <View key={i} style={[styles.kpiCard, { flexBasis: kpiBasis }]}>
                  <View style={styles.kpiTop}>
                    <View style={[styles.kpiIcon, { backgroundColor: k.color + '1A' }]}>
                      <Icon name={k.icon} color={k.color} />
                    </View>
                    <Text style={styles.kpiLabel}>{k.label}</Text>
                  </View>
                  <Text style={styles.kpiValue}>{k.value}</Text>
                  <View style={styles.kpiDeltaRow}>
                    <Text style={[styles.kpiDelta, { color: k.up ? GREEN : RED }]}>
                      {k.up ? '↑' : '↓'} {k.delta}
                    </Text>
                  </View>
                  <KpiFooter k={k} />
                </View>
              ))}
            </View>

            {/* Charts */}
            <View style={styles.grid}>
              <ChartPanel basis={chartBasis} title="Sales Trend" sub="Revenue over the week">
                {(w: number) => <AreaChart data={salesSeries} w={w} h={104} color={BLUE} />}
              </ChartPanel>
              <ChartPanel basis={chartBasis} title="Footfall Trend" sub="Visitors per hour">
                {(w: number) => <AreaChart data={footfallSeries} w={w} h={104} color={GREEN} />}
              </ChartPanel>
              <ChartPanel basis={chartBasis} title="Queue Trend" sub="Queue length through the day">
                {(w: number) => <BarChart data={queueSeries} w={w} h={104} color={BLUE} />}
              </ChartPanel>
              <ChartPanel basis={chartBasis} title="Inventory Health" sub="% of products in stock">
                {() => (
                  <View style={styles.donutRow}>
                    <View style={{ position: 'relative' }}>
                      <Donut slices={inventorySlices} size={96} />
                      <View style={styles.donutCenter}>
                        <Text style={styles.donutPct}>{invHealthPct}%</Text>
                        <Text style={styles.donutLabel}>Healthy</Text>
                      </View>
                    </View>
                    <View style={styles.legend}>
                      {inventorySlices.map((s, i) => (
                        <View key={i} style={styles.legendRow}>
                          <View style={[styles.legendDot, { backgroundColor: s.color }]} />
                          <Text style={styles.legendText}>{s.label}</Text>
                          <Text style={styles.legendVal}>{s.value}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                )}
              </ChartPanel>
            </View>

            {/* Bottom row: AI recs / Alerts / Device status */}
            <View style={styles.grid}>
              <Panel title="AI Recommendation Panel" style={{ flexBasis: bottomBasis }}>
                {recs.slice(0, 4).map((r, i) => (
                  <View key={i} style={styles.recRow}>
                    <View style={styles.recIcon}><Icon name={r.icon} color={BLUE} /></View>
                    <Text style={styles.recText}>{r.text}</Text>
                  </View>
                ))}
              </Panel>

              <Panel title="Recent Alerts" style={{ flexBasis: bottomBasis }}>
                {alerts.slice(0, 4).map((a, i) => (
                  <View key={i} style={styles.alertRow}>
                    <View style={[styles.alertDot, { backgroundColor: a.color }]} />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.alertTitle}>{a.title}</Text>
                      <Text style={styles.alertSub}>{a.sub}</Text>
                    </View>
                  </View>
                ))}
                <TouchableOpacity style={styles.viewAll} onPress={() => router.push('/alerts')}>
                  <Text style={styles.viewAllText}>VIEW ALL ALERTS</Text>
                </TouchableOpacity>
              </Panel>

              <Panel title="Device Status" style={{ flexBasis: bottomBasis }}>
                <View style={styles.deviceGrid}>
                  <View style={styles.deviceCard}>
                    <Text style={styles.deviceName}>Mobile Camera</Text>
                    <View style={styles.deviceStatusRow}>
                      <View style={[styles.statusDot, { backgroundColor: GREEN }]} />
                      <Text style={[styles.deviceStatus, { color: GREEN }]}>Online</Text>
                    </View>
                  </View>
                  <View style={styles.deviceCard}>
                    <Text style={styles.deviceName}>IR Sensor</Text>
                    <Text style={styles.deviceWaiting}>Waiting for Connection</Text>
                  </View>
                  <View style={styles.deviceCard}>
                    <Text style={styles.deviceName}>Ultrasonic</Text>
                    <Text style={styles.deviceWaiting}>Waiting for Connection</Text>
                  </View>
                  <View style={styles.deviceCard}>
                    <Text style={styles.deviceName}>Scanners</Text>
                    <Text style={styles.deviceWaiting}>Waiting for Connection</Text>
                  </View>
                </View>
              </Panel>
            </View>
          </Animated.View>
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  appShell: { flex: 1, backgroundColor: PAGE },

  // Full-width top bar (logo + title on the left, bell + avatar on the right)
  topBar: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12,
    backgroundColor: CARD, borderBottomWidth: 1, borderBottomColor: BORDER,
  },
  topBarLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  logoBadge: { width: 30, height: 30, borderRadius: 9, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  logoBadgeText: { color: '#fff', fontWeight: '900', fontSize: 14 },

  // Row below the top bar: sidebar + scrollable content
  body: { flex: 1, flexDirection: 'row' },

  sidebar: {
    width: SIDEBAR_WIDTH, backgroundColor: CARD,
    borderRightWidth: 1, borderRightColor: BORDER,
    paddingVertical: 14, paddingHorizontal: 10, gap: 3,
  },
  navItem: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingVertical: 10, paddingHorizontal: 12, borderRadius: 10,
  },
  navItemActive: { backgroundColor: BLUE + '14' },
  navLabel: { fontSize: 13, fontWeight: '600', color: MUTED },
  navLabelActive: { color: BLUE, fontWeight: '800' },

  container: { flex: 1, backgroundColor: PAGE },
  content: { padding: 10, paddingBottom: 16, gap: 10 },

  title: { fontSize: 17, fontWeight: '900', color: TEXT, letterSpacing: -0.4 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  bell: { width: 34, height: 34, borderRadius: 11, backgroundColor: CARD, borderWidth: 1, borderColor: BORDER, alignItems: 'center', justifyContent: 'center' },
  bellDot: { position: 'absolute', top: 8, right: 9, width: 6, height: 6, borderRadius: 3, backgroundColor: RED },
  avatar: { width: 34, height: 34, borderRadius: 17, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '800', fontSize: 14 },

  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },

  kpiCard: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 11,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },
  kpiTop: { flexDirection: 'row', alignItems: 'center', gap: 7, marginBottom: 5 },
  kpiIcon: { width: 24, height: 24, borderRadius: 7, alignItems: 'center', justifyContent: 'center' },
  kpiLabel: { fontSize: 11, fontWeight: '600', color: MUTED, flex: 1 },
  kpiValue: { fontSize: 19, fontWeight: '900', color: TEXT, letterSpacing: -0.5 },
  kpiDeltaRow: { flexDirection: 'row', marginTop: 1 },
  kpiDelta: { fontSize: 10, fontWeight: '700' },
  kpiBarBg: { height: 5, backgroundColor: '#EDF1F6', borderRadius: 4, marginTop: 8, overflow: 'hidden' },
  kpiBarFill: { height: 5, borderRadius: 4 },

  panel: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 12,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },
  panelHead: { marginBottom: 6 },
  panelTitle: { fontSize: 13, fontWeight: '800', color: TEXT, letterSpacing: -0.2 },
  panelSub: { fontSize: 10, color: FAINT, marginTop: 1 },

  donutRow: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  donutCenter: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' },
  donutPct: { fontSize: 17, fontWeight: '900', color: TEXT },
  donutLabel: { fontSize: 9, color: MUTED },
  legend: { flex: 1, gap: 7 },
  legendRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  legendDot: { width: 10, height: 10, borderRadius: 5 },
  legendText: { fontSize: 12, color: MUTED, flex: 1 },
  legendVal: { fontSize: 12, fontWeight: '800', color: TEXT },

  recRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 7, borderBottomWidth: 1, borderBottomColor: '#F1F5F9' },
  recIcon: { width: 28, height: 28, borderRadius: 9, backgroundColor: '#EEF3F9', alignItems: 'center', justifyContent: 'center' },
  recText: { fontSize: 12, color: TEXT, fontWeight: '600', flex: 1 },

  alertRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 6 },
  alertDot: { width: 9, height: 9, borderRadius: 5 },
  alertTitle: { fontSize: 12, fontWeight: '700', color: TEXT },
  alertSub: { fontSize: 10, color: MUTED, marginTop: 1 },
  viewAll: { marginTop: 8, backgroundColor: '#F1F5F9', borderRadius: 9, paddingVertical: 8, alignItems: 'center' },
  viewAllText: { fontSize: 10, fontWeight: '800', color: MUTED, letterSpacing: 0.6 },

  deviceGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  deviceCard: { flexGrow: 1, flexBasis: '46%', backgroundColor: '#F8FAFC', borderRadius: 11, borderWidth: 1, borderColor: BORDER, padding: 11 },
  deviceName: { fontSize: 12, fontWeight: '700', color: TEXT },
  deviceStatusRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 6 },
  statusDot: { width: 8, height: 8, borderRadius: 4 },
  deviceStatus: { fontSize: 11, fontWeight: '700' },
  deviceWaiting: { fontSize: 10, color: FAINT, marginTop: 6 },
});
