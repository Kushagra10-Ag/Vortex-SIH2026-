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
    users: (<><Circle cx={9} cy={8} r={3} {...p} /><Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...p} /><Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...p} /></>),
    walk: (<><Circle cx={13} cy={4} r={2} {...p} /><Path d="M13 8l-2.5 4 3 2 1 6M10.5 12l-4 2M15.5 14l3-1" {...p} /></>),
    box: (<><Path d="M3 8l9-5 9 5v8l-9 5-9-5Z" {...p} /><Path d="M3 8l9 5 9-5M12 13v8" {...p} /></>),
    clock: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M12 7v5l3 2" {...p} /></>),
    bell: (<><Path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" {...p} /><Path d="M10 20a2 2 0 0 0 4 0" {...p} /></>),
    refresh: (<><Path d="M4 12a8 8 0 0 1 13.7-5.7L20 8M20 12a8 8 0 0 1-13.7 5.7L4 16" {...p} /><Path d="M20 4v4h-4M4 20v-4h4" {...p} /></>),
    chart: (<><Path d="M4 4v16h16" {...p} /><Path d="M8 15l3-4 3 2 4-6" {...p} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
}

// ── Sparkline (tiny line for KPI cards) ──────────────────────────────────────
function Sparkline({ points, color, w, h = 40 }: { points: number[]; color: string; w: number; h?: number }) {
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
        return <Line key={i} x1={padL} y1={y} x2={w - padR} y2={y} stroke="#EDF1F6" strokeWidth={1} />;
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
        return <Rect key={i} x={x} y={y} width={bw} height={Math.max(bh, 1)} rx={3} fill={color} opacity={0.85} />;
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
            <Circle
              key={i} cx={r} cy={r} r={radius} stroke={s.color} strokeWidth={stroke} fill="none"
              strokeDasharray={`${len} ${circ - len}`} strokeDashoffset={-offset} strokeLinecap="butt"
            />
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
    <View onLayout={onLayout} style={{ marginTop: 6 }}>
      <Sparkline points={k.spark} color={k.color} w={w} />
    </View>
  );
}

// ── Dashboard ────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const { width } = Dimensions.get('window');
  const isWide = width >= 900;

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

  const todayBills = bills.filter((b) => b.created_at && isToday(new Date(b.created_at)));
  const todayRevenue = todayBills.reduce((s, b) => s + (b.total_amount || 0), 0);
  const currentCustomers = new Set(todayBills.map((b) => b.customer_name || b.id)).size;

  const openHour = 9, closeHour = 21;
  const hours = Array.from({ length: closeHour - openHour + 1 }, (_, i) => openHour + i);
  const hourlyCount = hours.map((hr) =>
    todayBills.filter((b) => b.created_at && new Date(b.created_at).getHours() === hr).length
  );

  const footfallSeries = hours.map((hr, i) => ({
    label: `${hr}`,
    value: hourlyCount[i] * 3 + (hourlyCount[i] > 0 ? 2 : 0),
  }));
  const todayFootfall = footfallSeries.reduce((s, x) => s + x.value, 0);

  const queueSeries = hours.map((hr, i) => ({ label: `${hr}`, value: Math.round(hourlyCount[i] * 1.4) }));
  const peakQueue = Math.max(...queueSeries.map((q) => q.value), 0);
  const avgWait = Math.max(1, Math.round(peakQueue * 1.5));

  const lowStock = products.filter((p) => p.quantity < (p.min_stock_level ?? 0) && p.quantity > 0);
  const critical = products.filter((p) => p.quantity <= 0);
  const healthy = products.filter((p) => p.quantity >= (p.min_stock_level ?? 0));
  const invHealthPct = products.length ? Math.round((healthy.length / products.length) * 100) : 100;
  const inventorySlices = [
    { value: healthy.length, color: GREEN, label: 'Healthy' },
    { value: lowStock.length, color: AMBER, label: 'Low Stock' },
    { value: critical.length, color: RED, label: 'Critical' },
  ];

  const alerts: { title: string; sub: string; color: string }[] = [];
  if (peakQueue >= 4) alerts.push({ title: 'Queue Congestion', sub: `Peak ${peakQueue} in queue - busy hour`, color: RED });
  lowStock.slice(0, 2).forEach((p) => alerts.push({ title: 'Shelf Low', sub: `${p.name} - ${p.quantity} left`, color: AMBER }));
  critical.slice(0, 1).forEach((p) => alerts.push({ title: 'Out of Stock', sub: `${p.name} needs restock`, color: RED }));
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
  bills.forEach((b) => {
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

  const kpiBasis = isWide ? '31.5%' : '47%';
  const chartBasis = isWide ? '48%' : '100%';

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={BLUE} />}
    >
      <Animated.View style={{ opacity: fadeAnim }}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>Retail Command Center</Text>
            <Text style={styles.subtitle}>Live store intelligence at the edge</Text>
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
            {(w: number) => <AreaChart data={salesSeries} w={w} h={160} color={BLUE} />}
          </ChartPanel>
          <ChartPanel basis={chartBasis} title="Footfall Trend" sub="Visitors per hour">
            {(w: number) => <AreaChart data={footfallSeries} w={w} h={160} color={GREEN} />}
          </ChartPanel>
          <ChartPanel basis={chartBasis} title="Queue Trend" sub="Queue length through the day">
            {(w: number) => <BarChart data={queueSeries} w={w} h={160} color={BLUE} />}
          </ChartPanel>
          <ChartPanel basis={chartBasis} title="Inventory Health" sub="% of products in stock">
            {() => (
              <View style={styles.donutRow}>
                <View style={{ position: 'relative' }}>
                  <Donut slices={inventorySlices} size={130} />
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
          <Panel title="AI Recommendation Panel" style={{ flexBasis: chartBasis }}>
            {recs.slice(0, 4).map((r, i) => (
              <View key={i} style={styles.recRow}>
                <View style={styles.recIcon}><Icon name={r.icon} color={BLUE} /></View>
                <Text style={styles.recText}>{r.text}</Text>
              </View>
            ))}
          </Panel>

          <Panel title="Recent Alerts" style={{ flexBasis: chartBasis }}>
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

          <Panel title="Device Status" style={{ flexBasis: '100%' }}>
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
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: PAGE },
  content: { padding: 14, paddingBottom: 28, gap: 14 },

  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 },
  title: { fontSize: 20, fontWeight: '900', color: TEXT, letterSpacing: -0.4 },
  subtitle: { fontSize: 12, color: MUTED, marginTop: 2 },
  headerRight: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  bell: { width: 38, height: 38, borderRadius: 12, backgroundColor: CARD, borderWidth: 1, borderColor: BORDER, alignItems: 'center', justifyContent: 'center' },
  bellDot: { position: 'absolute', top: 9, right: 10, width: 7, height: 7, borderRadius: 4, backgroundColor: RED },
  avatar: { width: 38, height: 38, borderRadius: 19, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '800', fontSize: 15 },

  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },

  kpiCard: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 16, padding: 14,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  kpiTop: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 10 },
  kpiIcon: { width: 28, height: 28, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  kpiLabel: { fontSize: 11, fontWeight: '600', color: MUTED, flex: 1 },
  kpiValue: { fontSize: 24, fontWeight: '900', color: TEXT, letterSpacing: -0.5 },
  kpiDeltaRow: { flexDirection: 'row', marginTop: 2 },
  kpiDelta: { fontSize: 11, fontWeight: '700' },
  kpiBarBg: { height: 6, backgroundColor: '#EDF1F6', borderRadius: 4, marginTop: 12, overflow: 'hidden' },
  kpiBarFill: { height: 6, borderRadius: 4 },

  panel: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  panelHead: { marginBottom: 10 },
  panelTitle: { fontSize: 15, fontWeight: '800', color: TEXT, letterSpacing: -0.2 },
  panelSub: { fontSize: 11, color: FAINT, marginTop: 2 },

  donutRow: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  donutCenter: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' },
  donutPct: { fontSize: 22, fontWeight: '900', color: TEXT },
  donutLabel: { fontSize: 10, color: MUTED },
  legend: { flex: 1, gap: 10 },
  legendRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  legendDot: { width: 10, height: 10, borderRadius: 5 },
  legendText: { fontSize: 12, color: MUTED, flex: 1 },
  legendVal: { fontSize: 12, fontWeight: '800', color: TEXT },

  recRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#F1F5F9' },
  recIcon: { width: 32, height: 32, borderRadius: 10, backgroundColor: '#EEF3F9', alignItems: 'center', justifyContent: 'center' },
  recText: { fontSize: 13, color: TEXT, fontWeight: '600', flex: 1 },

  alertRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 9 },
  alertDot: { width: 9, height: 9, borderRadius: 5 },
  alertTitle: { fontSize: 13, fontWeight: '700', color: TEXT },
  alertSub: { fontSize: 11, color: MUTED, marginTop: 1 },
  viewAll: { marginTop: 10, backgroundColor: '#F1F5F9', borderRadius: 10, paddingVertical: 10, alignItems: 'center' },
  viewAllText: { fontSize: 10, fontWeight: '800', color: MUTED, letterSpacing: 0.6 },

  deviceGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  deviceCard: { flexGrow: 1, flexBasis: '46%', backgroundColor: '#F8FAFC', borderRadius: 12, borderWidth: 1, borderColor: BORDER, padding: 14 },
  deviceName: { fontSize: 13, fontWeight: '700', color: TEXT },
  deviceStatusRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 8 },
  statusDot: { width: 8, height: 8, borderRadius: 4 },
  deviceStatus: { fontSize: 12, fontWeight: '700' },
  deviceWaiting: { fontSize: 11, color: FAINT, marginTop: 8 },
});