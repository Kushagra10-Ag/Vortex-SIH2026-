import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  Dimensions, Animated, RefreshControl,
} from 'react-native';
import { fetchTotalSales, fetchBills, fetchProducts } from "../../services/api";
import { router,useRouter } from 'expo-router';
import Svg, { Path, Circle, Defs, LinearGradient, Stop, Text as SvgText, Line } from 'react-native-svg';
const { width, height } = Dimensions.get('window');

// ── Animated Line Chart ──────────────────────────────────────────────────────
function AnimatedLineChart({
  data, chartWidth, chartHeight, color,
}: {
  data: { label: string; value: number }[];
  chartWidth: number;
  chartHeight: number;
  color: string;
}) {
  const animValue = useRef(new Animated.Value(0)).current;
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    animValue.setValue(0);
    const listener = animValue.addListener(({ value }) => setProgress(value));
    Animated.timing(animValue, {
      toValue: 1,
      duration: 1600,
      useNativeDriver: false,
    }).start();
    return () => animValue.removeListener(listener);
  }, [data]);

  const padL = 44, padR = 12, padT = 12, padB = 32;
  const w = chartWidth - padL - padR;
  const h = chartHeight - padT - padB;

const vals = data.map(d => d?.value || 0);
  const minV = Math.min(...vals) * 0.92;
  const maxV = Math.max(...vals) * 1.05;
  const range = maxV - minV;

  const toX = (i: number) => padL + (i / (data.length - 1)) * w;
  const toY = (v: number) => padT + h - ((v - minV) / range) * h;
  if (!data || data.length < 2) {
  return null;
}
  const allPoints = data.map((d, i) => ({ x: toX(i), y: toY(d.value) }));

  const total = allPoints.length - 1;
const exactIndex = progress * total;

const baseIndex = Math.floor(exactIndex);
const nextIndex = Math.min(baseIndex + 1, total);
const t = exactIndex - baseIndex;

const interpolatedPoint = {
  x: allPoints[baseIndex].x + (allPoints[nextIndex].x - allPoints[baseIndex].x) * t,
  y: allPoints[baseIndex].y + (allPoints[nextIndex].y - allPoints[baseIndex].y) * t,
};

const displayPoints = [
  ...allPoints.slice(0, baseIndex + 1),
  interpolatedPoint,
];


  const buildPath = (pts: { x: number; y: number }[]) =>
    pts.reduce((acc, p, i) => {
      if (i === 0) return `M${p.x},${p.y}`;
      const prev = pts[i - 1];
      const cpx = (prev.x + p.x) / 2;
      return `${acc} C${cpx},${prev.y} ${cpx},${p.y} ${p.x},${p.y}`;
    }, '');

  const linePath = buildPath(displayPoints);
  const areaPath = displayPoints.length > 1
    ? `${linePath} L${displayPoints[displayPoints.length - 1].x},${padT + h} L${displayPoints[0].x},${padT + h} Z`
    : '';

  // Y-axis grid values
  const yTicks = Array.from({ length: 5 }, (_, i) => Math.round(minV + (range / 4) * i));

  return (
    <Svg width={chartWidth} height={chartHeight}>
      <Defs>
        <LinearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <Stop offset="0" stopColor={color} stopOpacity="0.35" />
          <Stop offset="1" stopColor={color} stopOpacity="0.02" />
        </LinearGradient>
      </Defs>

      {/* Grid lines + Y labels */}
      {yTicks.map((v, i) => {
        const y = toY(v);
        return (
          <React.Fragment key={i}>
            <Line
              x1={padL} y1={y} x2={chartWidth - padR} y2={y}
              stroke="rgba(255,255,255,0.06)" strokeWidth={1}
            />
            <SvgText x={padL - 6} y={y + 4} fontSize={9} fill="rgba(255,255,255,0.3)" textAnchor="end">
              {v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v}
            </SvgText>
          </React.Fragment>
        );
      })}

      {/* X labels */}
      {data.map((d, i) => (
        <SvgText
          key={i} x={toX(i)} y={chartHeight - 6}
          fontSize={9} fill="rgba(255,255,255,0.35)" textAnchor="middle"
        >
          {d.label}
        </SvgText>
      ))}

      {/* Area fill */}
      {areaPath ? <Path d={areaPath} fill="url(#areaGrad)" /> : null}

      {/* Line */}
      {linePath ? (
        <Path d={linePath} stroke={color} strokeWidth={2.5} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      ) : null}

      {/* Dots */}
      {displayPoints.map((p, i) => (
        <Circle key={i} cx={p.x} cy={p.y} r={i === displayPoints.length - 1 ? 5 : 3.5}
          fill={i === displayPoints.length - 1 ? color : '#1E2D45'}
          stroke={color} strokeWidth={2}
        />
      ))}
    </Svg>
  );
}

// ── Dashboard ────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [refreshing, setRefreshing] = useState(false);
  const [period, setPeriod] = useState<'WEEKLY' | 'MONTHLY'>('WEEKLY');
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(24)).current;

  ;
  const { width, height } = Dimensions.get('window');
  const [salesData, setSalesData] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [weeklyData, setWeeklyData] = useState<{ label: string; value: number }[]>([]);
const [monthlyData, setMonthlyData] = useState<{ label: string; value: number }[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  useEffect(() => {
  loadData();

  Animated.parallel([
    Animated.timing(fadeAnim, { toValue: 1, duration: 600, useNativeDriver: true }),
    Animated.timing(slideAnim, { toValue: 0, duration: 600, useNativeDriver: true }),
  ]).start();
}, []);

const loadData = async (currentPeriod = period) => {
  try {
    const bills = await fetchBills();
    const prods = await fetchProducts();

    // Build weekly data from real bills
    const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const weeklyTotals = new Array(7).fill(0);
    bills.forEach((b: any) => {
      const d = new Date(b.created_at);
      const dow = (d.getDay() + 6) % 7; // Mon=0, Sun=6
      weeklyTotals[dow] += b.total_amount || 0;
    });
    const weekly = dayLabels.map((label, i) => ({ label, value: weeklyTotals[i] }));

    // Build monthly data from real bills
    const monthLabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const monthlyTotals = new Array(12).fill(0);
    bills.forEach((b: any) => {
      const d = new Date(b.created_at);
      monthlyTotals[d.getMonth()] += b.total_amount || 0;
    });
    const monthly = monthLabels.map((label, i) => ({ label, value: monthlyTotals[i] }));

    const tx = bills.map((b: any) => ({
      id: b.id,
      name: b.customer_name || 'Walk-in',
      amount: b.total_amount,
      time: new Date(b.created_at).toLocaleTimeString(),
      initials: (b.customer_name || 'W')[0].toUpperCase(),
      color: '#4F8EF7',
    }));

    setTransactions(tx);
    setProducts(prods);
    setSalesData(currentPeriod === 'WEEKLY' ? weekly : monthly);

    // store both for toggle switching
    setWeeklyData(weekly);
    setMonthlyData(monthly);

  } catch (e) {
    console.log(e);
  }
};
  const onRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1200);
  };

  const chartData = salesData;

  const totalSales = transactions.reduce((sum, t) => sum + t.amount, 0);

const kpiCards = [
  { icon: '📈', label: 'TOTAL', value: `₹${totalSales.toFixed(2)}`, sub: 'Total Sales', accent: '#4F8EF7', dark: true },
  { icon: '📦', label: 'STOCK', value: products.length, sub: 'Total Items', accent: '#00C896', dark: false },
  { icon: '⚠️', label: 'ALERTS', value: products.filter(p => p.quantity < p.min_stock_level).length, sub: 'Low Stock', accent: '#FFB020', dark: false },
  { icon: '🧾', label: 'ACTIVITY', value: transactions.length, sub: 'Transactions', accent: '#7B61FF', dark: false },
];

  const chartW = width * 0.56;
  const chartH = 240;

  return (
    <Animated.ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#4F8EF7" />}
    >
      <Animated.View style={{ opacity: fadeAnim, transform: [{ translateY: slideAnim }] }}>
{/* Header greeting */}
<View style={styles.greetingRow}>
  <View>
    <Text style={styles.greetingTitle}></Text>
    <Text style={styles.greetingSub}>Here's your business at a glance</Text>
  </View>
  <View style={styles.dateBadge}>
    <Text style={styles.dateBadgeText}>
      {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
    </Text>
  </View>
</View>
        {/* KPI Cards */}
        <View style={styles.kpiRow}>
          {kpiCards.map((card, i) => (
            <View key={i} style={[styles.kpiCard, card.dark && styles.kpiCardDark]}>
  {/* Colored top strip */}
  <View style={[styles.kpiTopStrip, { backgroundColor: card.accent }]} />
  <View style={styles.kpiTop}>
    <View style={[styles.kpiIconWrap, { backgroundColor: card.accent + '33' }]}>
      <Text style={styles.kpiIcon}>{card.icon}</Text>
    </View>
    <Text style={[styles.kpiLabel, card.dark ? styles.kpiLabelOnDark : styles.kpiLabelOnLight]}>
      {card.label}
    </Text>
  </View>
  <Text style={[styles.kpiValue, card.dark ? styles.kpiValueOnDark : styles.kpiValueOnLight]}>
    {card.value}
  </Text>
  <Text style={[styles.kpiSub, card.dark ? styles.kpiSubOnDark : styles.kpiSubOnLight]}>
    {card.sub}
  </Text>
  {/* Progress bar */}
  <View style={styles.kpiBarBg}>
    <View style={[styles.kpiBarFill, { backgroundColor: card.accent, width: '65%' }]} />
  </View>
</View>
          ))}
        </View>

        {/* Main row */}
        <View style={styles.mainRow}>

          {/* Chart Panel */}
          <View style={[styles.panel, { flex: 1.45 }]}>
            <View style={styles.chartHeader}>
              <View>
                <Text style={styles.panelTitle}>Sales Performance</Text>
                <Text style={styles.panelSub}>
                  {period === 'WEEKLY' ? 'This Week' : 'Last 6 Months'}
                </Text>
              </View>
              <View style={styles.periodToggle}>
                <TouchableOpacity
                  onPress={() => { setPeriod('WEEKLY'); setSalesData(weeklyData); }}
                  style={[styles.periodBtn, period === 'WEEKLY' && styles.periodBtnActive]}
                >
                  <Text style={[styles.periodText, period === 'WEEKLY' && styles.periodTextActive]}>
                    WEEKLY
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  onPress={() => { setPeriod('MONTHLY'); setSalesData(monthlyData); }}
                  style={[styles.periodBtn, period === 'MONTHLY' && styles.periodBtnActive]}
                >
                  <Text style={[styles.periodText, period === 'MONTHLY' && styles.periodTextActive]}>
                    MONTHLY
                  </Text>
                </TouchableOpacity>
              </View>
            </View>

            <AnimatedLineChart
              data={chartData}
              chartWidth={chartW}
              chartHeight={chartH}
              color="#4F8EF7"
            />
          </View>

          {/* Transactions Panel */}
          <View style={[styles.panel, { flex: 1 }]}>
            <View style={styles.txHeader}>
              <Text style={styles.panelTitle}>Transactions</Text>
              <View style={styles.liveDot}>
                <View style={styles.livePulse} />
                <Text style={styles.liveText}>LIVE</Text>
              </View>
            </View>

            {transactions.slice(0, 4).map((t, i)  => (
              <View key={t.id} style={[styles.txRow, i === 3 && { borderBottomWidth: 0 }]}>
                <View style={[styles.avatar, { backgroundColor: t.color + '25' }]}>
                  <Text style={[styles.avatarText, { color: t.color }]}>{t.initials}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.txName}>{t.name}</Text>
                  <Text style={styles.txTime}>{t.time}</Text>
                </View>
                <Text style={styles.txAmount}>+₹{t.amount.toFixed(2)}</Text>
              </View>
            ))}

            <TouchableOpacity style={styles.viewAllBtn} onPress={() => router.push('/billing')}>
  <Text style={styles.viewAllText}>VIEW ALL ACTIVITY</Text>
</TouchableOpacity>
          </View>

        </View>
      </Animated.View>
    </Animated.ScrollView>
  );
}

const BG = '#0D1B2A';
const CARD = '#132032';
const BORDER = 'rgba(255,255,255,0.07)';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: BG,
  },
  content: {
    padding: 14,
    paddingBottom: 24,
    minHeight: height - 140,
  },

  // KPI
  kpiRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 14,
  },
  kpiCard: {
  flex: 1,
  backgroundColor: CARD,
  borderRadius: 18,
  padding: 14,
  borderWidth: 1,
  borderColor: BORDER,
  overflow: 'hidden',
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 4 },
  shadowOpacity: 0.2,
  shadowRadius: 8,
  elevation: 4,
},
  kpiCardDark: {
    backgroundColor: '#1A2E45',
    borderColor: 'rgba(79,142,247,0.2)',
  },
  kpiTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  kpiIconWrap: {
    width: 30,
    height: 30,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  kpiIcon: { fontSize: 14 },
  kpiLabel: { fontSize: 8, fontWeight: '700', letterSpacing: 0.8 },
  kpiLabelOnDark: { color: 'rgba(255,255,255,0.4)' },
  kpiLabelOnLight: { color: 'rgba(255,255,255,0.35)' },
  kpiValue: { fontSize: 20, fontWeight: '900', letterSpacing: -0.5, marginBottom: 2 },
  kpiValueOnDark: { color: '#fff' },
  kpiValueOnLight: { color: '#fff' },
  kpiSub: { fontSize: 9, marginBottom: 10 },
  kpiSubOnDark: { color: 'rgba(255,255,255,0.4)' },
  kpiSubOnLight: { color: 'rgba(255,255,255,0.35)' },
  kpiAccentBar: {
    position: 'absolute',
    bottom: 0, left: 0, right: 0,
    height: 2.5,
    borderRadius: 2,
  },

  // Layout
  mainRow: {
    flexDirection: 'row',
    gap: 12,
    flex: 1,
  },
  panel: {
  backgroundColor: CARD,
  borderRadius: 20,
  padding: 16,
  borderWidth: 1,
  borderColor: BORDER,
  shadowColor: '#4F8EF7',
  shadowOffset: { width: 0, height: 4 },
  shadowOpacity: 0.08,
  shadowRadius: 16,
  elevation: 6,
},
  
  

  // Chart header
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 6,
  },
  periodToggle: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255,255,255,0.07)',
    borderRadius: 20,
    padding: 3,
  },
  periodBtn: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 16,
  },
  periodBtnActive: {
    backgroundColor: '#4F8EF7',
  },
  periodText: {
    fontSize: 8,
    fontWeight: '700',
    color: 'rgba(255,255,255,0.4)',
    letterSpacing: 0.5,
  },
  periodTextActive: { color: '#fff' },

  // Transactions
  txHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  liveDot: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    backgroundColor: 'rgba(0,200,150,0.12)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  livePulse: {
    width: 6, height: 6, borderRadius: 3,
    backgroundColor: '#00C896',
  },
  liveText: {
    fontSize: 8,
    fontWeight: '800',
    color: '#00C896',
    letterSpacing: 0.5,
  },
  txRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 9,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  avatar: {
    width: 36, height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { fontSize: 11, fontWeight: '800' },
  txName: { fontSize: 12, fontWeight: '700', color: '#fff' },
  txTime: { fontSize: 10, color: 'rgba(255,255,255,0.35)', marginTop: 1 },
  txAmount: { fontSize: 12, fontWeight: '800', color: '#00C896' },
  viewAllBtn: {
    marginTop: 12,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 10,
    padding: 11,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: BORDER,
  },
  viewAllText: {
    fontSize: 10,
    fontWeight: '800',
    color: 'rgba(255,255,255,0.4)',
    letterSpacing: 0.8,
  },
  greetingRow: {
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 16,
  paddingHorizontal: 2,
},
greetingTitle: {
  fontSize: 18,
  fontWeight: '900',
  color: '#fff',
  letterSpacing: -0.3,
},
greetingSub: {
  fontSize: 11,
  color: 'rgba(255,255,255,0.35)',
  marginTop: 2,
},
dateBadge: {
  backgroundColor: 'rgba(79,142,247,0.15)',
  borderWidth: 1,
  borderColor: 'rgba(79,142,247,0.3)',
  borderRadius: 10,
  paddingHorizontal: 12,
  paddingVertical: 6,
},
dateBadgeText: {
  fontSize: 11,
  fontWeight: '800',
  color: '#4F8EF7',
},
  kpiTopStrip: {
  position: 'absolute',
  top: 0, left: 0, right: 0,
  height: 3,
  borderTopLeftRadius: 18,
  borderTopRightRadius: 18,
},
kpiBarBg: {
  height: 3,
  backgroundColor: 'rgba(255,255,255,0.08)',
  borderRadius: 2,
  marginTop: 10,
},
kpiBarFill: {
  height: 3,
  borderRadius: 2,
},
panelTitle: {
  fontSize: 15,
  fontWeight: '900',
  color: '#fff',
  letterSpacing: -0.3,
  marginBottom: 2,
},
panelSub: {
  fontSize: 10,
  color: '#4F8EF7',
  marginBottom: 10,
  fontWeight: '600',
},
});