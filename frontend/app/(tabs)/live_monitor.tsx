import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  Dimensions, RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import Svg, { Path, Circle, Rect } from 'react-native-svg';

// ── Theme (matches Dashboard.tsx) ─────────────────────────────────────────
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

// ⚠️ Adjust this to match your actual Flask blueprint prefix / host.
const API_BASE = 'http://localhost:5000/api/monitoring';

// ── Icons ──────────────────────────────────────────────────────────────────
function Icon({ name, color, size = 15 }: { name: string; color: string; size?: number }) {
  const p = { stroke: color, strokeWidth: 2, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, React.ReactNode> = {
    grid: (<><Rect x={4} y={4} width={7} height={7} rx={1.5} {...p} /><Rect x={13} y={4} width={7} height={7} rx={1.5} {...p} /><Rect x={4} y={13} width={7} height={7} rx={1.5} {...p} /><Rect x={13} y={13} width={7} height={7} rx={1.5} {...p} /></>),
    video: (<><Rect x={3} y={7} width={13} height={10} rx={2} {...p} /><Path d="M16 10.5l5-3v9l-5-3" {...p} /></>),
    cart: (<><Circle cx={9} cy={20} r={1.4} fill={color} /><Circle cx={17} cy={20} r={1.4} fill={color} /><Path d="M3 4h2l2.2 10.6a2 2 0 0 0 2 1.6h7.3a2 2 0 0 0 2-1.6L20 8H6" {...p} /></>),
    bot: (
  <>
    <Rect x={4} y={7} width={16} height={12} rx={3} {...p} />
    <Circle cx={9} cy={13} r={1.2} fill={color} />
    <Circle cx={15} cy={13} r={1.2} fill={color} />
    <Path d="M12 3v4M9 3h6" {...p} />
  </>
),
    box: (<><Path d="M3 8l9-5 9 5v8l-9 5-9-5Z" {...p} /><Path d="M3 8l9 5 9-5M12 13v8" {...p} /></>),
    users: (<><Circle cx={9} cy={8} r={3} {...p} /><Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...p} /><Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...p} /></>),
    briefcase: (<><Rect x={3} y={8} width={18} height={11} rx={2} {...p} /><Path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18" {...p} /></>),
    chart: (<><Path d="M4 4v16h16" {...p} /><Path d="M8 15l3-4 3 2 4-6" {...p} /></>),
    gear: (<><Circle cx={12} cy={12} r={3} {...p} /><Path d="M12 3v2.2M12 18.8V21M21 12h-2.2M5.2 12H3M18.4 5.6l-1.5 1.5M7.1 16.9l-1.5 1.5M18.4 18.4l-1.5-1.5M7.1 7.1L5.6 5.6" {...p} /></>),
    bell: (<><Path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" {...p} /><Path d="M10 20a2 2 0 0 0 4 0" {...p} /></>),
    person: (<><Circle cx={12} cy={8} r={3.2} {...p} /><Path d="M5 20a7 7 0 0 1 14 0" {...p} /></>),
    queue: (<><Rect x={3} y={6} width={3} height={13} rx={1} {...p} /><Rect x={8} y={3} width={3} height={16} rx={1} {...p} /><Rect x={13} y={8} width={3} height={11} rx={1} {...p} /><Rect x={18} y={5} width={3} height={14} rx={1} {...p} /></>),
    shelf: (<><Rect x={4} y={4} width={16} height={5} rx={1} {...p} /><Rect x={4} y={15} width={16} height={5} rx={1} {...p} /><Path d="M4 12h16" {...p} /></>),
    camera: (<><Path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Z" {...p} /><Circle cx={12} cy={13} r={3.4} {...p} /></>),
    speed: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M12 12l4-3" {...p} /></>),
    list: (<><Path d="M8 6h13M8 12h13M8 18h13" {...p} /><Circle cx={4} cy={6} r={1.4} fill={color} /><Circle cx={4} cy={12} r={1.4} fill={color} /><Circle cx={4} cy={18} r={1.4} fill={color} /></>),
    shield: (<><Path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3Z" {...p} /></>),
    cameraBig: (<><Rect x={5} y={9} width={22} height={17} rx={3} {...p} /><Circle cx={16} cy={17.5} r={5.2} {...p} /><Path d="M11 9l1.6-2.6h6.8L21 9" {...p} /><Circle cx={22.5} cy={12.5} r={0.8} fill={color} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
}

// ── Sidebar ──────────────────────────────────────────────────────────────
function Sidebar() {
  const navItems = [
    { key: 'dashboard', label: 'Dashboard', icon: 'grid', route: '/' },
    { key: 'live-monitoring', label: 'Live Monitoring', icon: 'video', route: '/live_monitor' },
    { key: 'billing', label: 'Billing', icon: 'cart', route: '/billing' },
    { key: 'inventory', label: 'Inventory', icon: 'box', route: '/inventory' },
    { key: 'analytics', label: 'Analytics', icon: 'chart', route: '/analytics' },
    { key: 'ai-assistant', label: 'AI Assistant', icon: 'bot', route: '/chatbot' },
  ];
  return (
    <View style={styles.sidebar}>
      {navItems.map((item) => {
        const isActive = item.key === 'live-monitoring';
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

// ── Small stat card (right-hand grid) ─────────────────────────────────────
function StatCard({ icon, iconColor, label, value, basis }: any) {
  return (
    <View style={[styles.statCard, { flexBasis: basis }]}>
      <View style={styles.statTop}>
        <View style={[styles.statIcon, { backgroundColor: iconColor + '1A' }]}>
          <Icon name={icon} color={iconColor} size={14} />
        </View>
        <Text style={styles.statLabel}>{label}</Text>
      </View>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

// ── Types matching your Flask payloads ────────────────────────────────────
interface RealtimeStatus {
  devices: { total: number; online: number; offline: number };
  cameras: { total: number; online: number };
  shelves: { total: number; needs_restock: number; avg_fill_percentage: number };
  footfall: { today_entries: number; current_occupancy: number };
  alerts: { total_open: number; critical: number };
}

interface CameraEvent {
  event_type: string;
  confidence: number;
  timestamp: string;
  camera_id_str?: string;
}

const EVENT_LABELS: Record<string, string> = {
  theft_alert: 'Theft Alert',
  queue_overflow: 'Queue Increased',
  out_of_stock_detected: 'Shelf Low',
  person_entered: 'Customer Entered',
  person_exited: 'Customer Exited',
};

function formatTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}

// ── Screen ─────────────────────────────────────────────────────────────────
export default function LiveMonitoring() {
  const { width } = Dimensions.get('window');
  const isWide = width >= 900;

  const [refreshing, setRefreshing] = useState(false);
  const [status, setStatus] = useState<RealtimeStatus | null>(null);
  const [events, setEvents] = useState<CameraEvent[]>([]);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [statusRes, eventsRes] = await Promise.all([
        fetch(`${API_BASE}/status`),
        fetch(`${API_BASE}/camera-events?limit=6`),
      ]);
      const statusJson = await statusRes.json();
      const eventsJson = await eventsRes.json();
      setStatus(statusJson);
      setEvents(Array.isArray(eventsJson) ? eventsJson : eventsJson.events || []);
    } catch (e) {
      console.log('[v0] live monitoring load error', e);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Poll every 5s so the screen behaves like a live feed
    pollRef.current = setInterval(loadData, 5000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [loadData]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setTimeout(() => setRefreshing(false), 500);
  };

  // ── Derive display values from real data ─────────────────────────────────
  const currentCustomers = status?.footfall.current_occupancy ?? 0;
  const queueAlertsCount = events.filter((e) => e.event_type === 'queue_overflow').length;
  const shelfAlertsCount = events.filter((e) => e.event_type === 'out_of_stock_detected').length;
  const peopleDetectedToday = status?.footfall.today_entries ?? 0;

  const shelfLabel = status
    ? status.shelves.needs_restock > 0 ? 'Attention' : 'Monitoring'
    : 'Loading…';
  const cameraLabel = status
    ? status.cameras.online > 0 ? 'Connected' : 'Connecting'
    : 'Connecting';

  const avgConfidence = events.length
    ? Math.round((events.reduce((s, e) => s + (e.confidence || 0), 0) / events.length) * 100)
    : 0;

  const detectionFPS = status?.cameras.online ? 12 : 0; // backend doesn't expose FPS yet — placeholder

  return (
    <View style={styles.appShell}>
      <View style={styles.topBar}>
        <View style={styles.topBarLeft}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoBadgeText}>F</Text>
          </View>
          <Text style={styles.title}>Live Monitoring</Text>
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
          {/* Top row: camera stream + stat grid */}
          <View style={styles.grid}>
            {/* Live camera panel */}
            <View style={[styles.panel, { flexBasis: isWide ? '46%' : '100%' }]}>
              <Text style={styles.panelTitle}>Live Mobile Camera Stream</Text>
              <View style={styles.cameraBox}>
                <Icon name="cameraBig" color={FAINT} size={64} />
                <Text style={styles.cameraWaiting}>
                  {status?.cameras.online ? 'Streaming…' : 'Waiting for Camera'}
                </Text>
              </View>
            </View>

            {/* Right-hand stat grid */}
            <View style={[styles.grid, { flexBasis: isWide ? '52%' : '100%', alignContent: 'flex-start' }]}>
              <StatCard basis="48%" icon="person" iconColor={BLUE} label="Current Customers" value={currentCustomers} />
              <StatCard basis="48%" icon="queue" iconColor={RED} label="Queue Length" value={queueAlertsCount} />
              <StatCard basis="48%" icon="shelf" iconColor={GREEN} label="Shelf Status" value={shelfLabel} />
              <StatCard basis="48%" icon="camera" iconColor={BLUE} label="Camera Status" value={cameraLabel} />
              <StatCard basis="48%" icon="speed" iconColor={GREEN} label="Detection FPS" value={detectionFPS} />

              {/* Detection timeline card */}
              <View style={[styles.panel, { flexBasis: '48%' }]}>
                <Text style={styles.panelTitle}>Detection Timeline</Text>
                {events.slice(0, 4).map((e, i) => (
                  <View key={i} style={styles.timelineRow}>
                    <View style={styles.timelineDot} />
                    <Text style={styles.timelineText}>
                      {formatTime(e.timestamp)} - {EVENT_LABELS[e.event_type] || e.event_type}
                    </Text>
                  </View>
                ))}
                {events.length === 0 && (
                  <Text style={styles.timelineEmpty}>No recent detections</Text>
                )}
              </View>
            </View>
          </View>

          {/* Detection statistics */}
          <View style={styles.panel}>
            <Text style={styles.panelTitle}>Detection Statistics</Text>
            <View style={styles.grid}>
              <StatCard basis={isWide ? '23%' : '48%'} icon="person" iconColor={BLUE} label="People Detected" value={peopleDetectedToday} />
              <StatCard basis={isWide ? '23%' : '48%'} icon="shelf" iconColor={RED} label="Shelf Alerts" value={shelfAlertsCount} />
              <StatCard basis={isWide ? '23%' : '48%'} icon="queue" iconColor={RED} label="Queue Alerts" value={queueAlertsCount} />
              <StatCard basis={isWide ? '23%' : '48%'} icon="shield" iconColor={BLUE} label="Confidence" value={`${avgConfidence}%`} />
            </View>
          </View>
        </ScrollView>
      </View>
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
  content: { padding: 10, paddingBottom: 16, gap: 10 },

  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },

  panel: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 12,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },
  panelTitle: { fontSize: 13, fontWeight: '800', color: TEXT, marginBottom: 10 },

  cameraBox: {
    height: 320, borderRadius: 12, backgroundColor: '#E4ECF5',
    alignItems: 'center', justifyContent: 'center', gap: 10,
  },
  cameraWaiting: { fontSize: 13, color: FAINT, fontWeight: '600' },

  statCard: {
    flexGrow: 1, backgroundColor: CARD, borderRadius: 14, padding: 11,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },
  statTop: { flexDirection: 'row', alignItems: 'center', gap: 7, marginBottom: 6 },
  statIcon: { width: 24, height: 24, borderRadius: 7, alignItems: 'center', justifyContent: 'center' },
  statLabel: { fontSize: 11, fontWeight: '600', color: MUTED, flex: 1 },
  statValue: { fontSize: 20, fontWeight: '900', color: TEXT, letterSpacing: -0.5 },

  timelineRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 5 },
  timelineDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: FAINT },
  timelineText: { fontSize: 11.5, color: TEXT, fontWeight: '600' },
  timelineEmpty: { fontSize: 11.5, color: FAINT },
});