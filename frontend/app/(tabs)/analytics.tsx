import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  Dimensions, ActivityIndicator, Alert,
} from 'react-native';
import { colors, radius } from '../../constants/theme';
import LineChart from '../../components/LineChart';
import { Animated } from 'react-native';
import BarChart from '../../components/BarChart';
import PieChart from '../../components/PieChart';
import { fetchAnalyticsDashboard, fetchAIForecast } from '../../services/api';

const { width } = Dimensions.get('window');

export default function Analytics() {
  const fadeAnim = useState(new Animated.Value(0))[0];
  const [period, setPeriod] = useState<'Week' | 'Month' | '6M'>('Month');
  const [loading, setLoading] = useState(true);

  // ── Backend data ─────────────────────────────────────────────────────────
  const [kpis, setKpis] = useState<{
    totalRevenue: number;
    avgDaily: number;
    topProduct: string;
    growth: number;
  }>({ totalRevenue: 0, avgDaily: 0, topProduct: '—', growth: 0 });

  const [revenueTrend, setRevenueTrend] = useState<{ label: string; value: number }[]>([]);
  const [monthlySales, setMonthlySales] = useState<{ label: string; value: number }[]>([]);
  const [categoryData, setCategoryData] = useState<{ label: string; value: number; color: string }[]>([]);
  const [expiryRisk, setExpiryRisk] = useState<{ name: string; days: number }[]>([]);
  const [forecastData, setForecastData] = useState<{ label: string; value: number }[]>([]);

  useEffect(() => {
  loadDashboard();

  Animated.timing(fadeAnim, {
    toValue: 1,
    duration: 800,
    useNativeDriver: true,
  }).start();
}, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await fetchAnalyticsDashboard();
      console.log("Dashboard data:", data);
      // ── KPIs ──
      if (data.kpis) setKpis(data.kpis);

      // ── Charts ──
      if (data.revenueTrend?.length)  setRevenueTrend(data.revenueTrend);
      if (data.monthlySales?.length)  setMonthlySales(data.monthlySales);
if (data.categoryData && data.categoryData.length > 0) {
  const colorsList = [
    '#4F8EF7', '#00C896', '#FFB020',
    '#7B61FF', '#FF6B6B', '#00D4FF',
    '#A78BFA', '#34D399'
  ];

  const colored = data.categoryData.map((item: any, i: number) => {
    return {
      label: item.label,
      value: item.value,
      color: colorsList[i % colorsList.length],
    };
  });

  setCategoryData(colored);
}      if (data.expiryRisk?.length)    setExpiryRisk(data.expiryRisk);

      // ── AI Forecast ──
      const forecast = await fetchAIForecast();
      if (forecast?.length) setForecastData(forecast);

    } catch (e) {
      Alert.alert("Error", "Failed to load analytics.");
      console.log("loadDashboard error:", e);
    } finally {
      setLoading(false);
    }
  };

  // ── Period filter applied to revenueTrend ────────────────────────────────
  const getChartData = () => {
    if (!revenueTrend.length) return [];
    if (period === 'Week')  return revenueTrend.slice(-7);
    if (period === 'Month') return revenueTrend.slice(-30);
    return revenueTrend; // 6M — all
  };

  // ── Expiry risk label ─────────────────────────────────────────────────────
  const getRiskLevel = (days: number) => {
    if (days <= 7)  return { label: 'Critical', color: colors.danger };
    if (days <= 20) return { label: 'High',     color: colors.warning };
    return          { label: 'Medium',           color: colors.primary };
  };

  // ── Forecast stats ────────────────────────────────────────────────────────
  const forecastAvg = forecastData.length
    ? Math.round(forecastData.reduce((s, d) => s + d.value, 0) / forecastData.length)
    : 0;
  const forecastPeak = forecastData.length
    ? Math.max(...forecastData.map(d => d.value))
    : 0;
  const forecastPeakDay = forecastData.find(d => d.value === forecastPeak)?.label || '—';

  // ── KPI cards config ──────────────────────────────────────────────────────
  const kpiCards = [
    {
      icon: '💰',
      label: 'Total Revenue',
      value: `₹${(kpis.totalRevenue / 1000).toFixed(0)}K`,
      sub: `+${kpis.growth}%`,
      subColor: colors.accent,
    },
    {
      icon: '📊',
      label: 'Avg Daily Sales',
      value: `₹${Math.round(kpis.avgDaily)}`,
      sub: 'per day',
      subColor: colors.textSub,
    },
    {
      icon: '🏆',
      label: 'Top Product',
      value: kpis.topProduct || '—',
      sub: 'best seller',
      subColor: colors.primary,
    },
    {
      icon: '📈',
      label: 'Growth',
      value: `${kpis.growth}%`,
      sub: 'vs last period',
      subColor: colors.accent,
    },
  ];

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator color={colors.primary} size="large" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>

      {/* KPI Grid */}
      <View style={styles.kpiGrid}>
        {kpiCards.map((k, i) => (
          <View key={i} style={styles.kpiCard}>
            <Text style={styles.kpiIcon}>{k.icon}</Text>
            <Text style={styles.kpiValue}>{k.value}</Text>
            <Text style={styles.kpiLabel}>{k.label}</Text>
            <Text style={[styles.kpiSub, { color: k.subColor }]}>{k.sub}</Text>
          </View>
        ))}
      </View>

      {/* Revenue Trend */}
<Animated.View
  style={[
    styles.card,
    {
      opacity: fadeAnim,
      transform: [{
        translateY: fadeAnim.interpolate({
          inputRange: [0, 1],
          outputRange: [30, 0],
        }),
      }],
    },
  ]}
>        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Revenue Trend</Text>
          <View style={styles.periodRow}>
            {(['Week', 'Month', '6M'] as const).map(p => (
              <TouchableOpacity
                key={p}
                onPress={() => setPeriod(p)}
                style={[styles.periodPill, period === p && styles.periodActive]}
              >
                <Text style={[styles.periodText, period === p && styles.periodTextActive]}>{p}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        {getChartData().length > 0
          ? <LineChart data={getChartData()} width={width - 48} height={200} color={colors.primary}  />
          : <Text style={styles.emptyText}>No trend data yet</Text>
        }
</Animated.View>
      {/* Bar Chart + Pie side by side */}
<Animated.View style={[styles.row, { opacity: fadeAnim }]}>
          <View style={[styles.card, { flex: 1.3 }]}>
          <Text style={styles.cardTitle}>Monthly Sales</Text>
          {monthlySales.length > 0
            ? <BarChart data={monthlySales} width={(width - 56) * 0.55} height={170} color={colors.purple} />
            : <Text style={styles.emptyText}>No data yet</Text>
          }
        </View>
        <View style={[styles.card, { flex: 1 }]}>
          <Text style={[styles.cardTitle, { marginBottom: 12 }]}>By Category</Text>
          {categoryData.length > 0
            ? <PieChart data={categoryData} size={110} />
            : <Text style={styles.emptyText}>No data yet</Text>
          }
        </View>
</Animated.View>
      {/* AI Forecast */}
<Animated.View style={[styles.card, { backgroundColor: colors.dark, opacity: fadeAnim }]}>
          <View style={styles.cardHeader}>
          <View>
            <Text style={[styles.cardTitle, { color: '#fff' }]}>AI Sales Forecast</Text>
            <Text style={[styles.cardSub, { color: 'rgba(255,255,255,0.5)' }]}>Next 7 days prediction</Text>
          </View>
          <View style={styles.aiBadge}>
            <Text style={styles.aiBadgeText}>🤖 AI</Text>
          </View>
        </View>
        {forecastData.length > 0
          ? <>
              <LineChart data={forecastData} width={width - 48} height={160} color={colors.accent}  />
              <View style={styles.forecastInfo}>
                <View style={styles.forecastStat}>
                  <Text style={styles.forecastStatVal}>₹{forecastPeak.toLocaleString()}</Text>
                  <Text style={styles.forecastStatLabel}>Peak ({forecastPeakDay})</Text>
                </View>
                <View style={styles.forecastStat}>
                  <Text style={styles.forecastStatVal}>₹{forecastAvg.toLocaleString()}</Text>
                  <Text style={styles.forecastStatLabel}>Avg Forecast</Text>
                </View>
                <View style={styles.forecastStat}>
                  <Text style={[styles.forecastStatVal, { color: colors.accent }]}>+{kpis.growth}%</Text>
                  <Text style={styles.forecastStatLabel}>vs This Week</Text>
                </View>
              </View>
            </>
          : <Text style={[styles.emptyText, { color: 'rgba(255,255,255,0.4)' }]}>Forecast unavailable</Text>
        }
</Animated.View>
      {/* Expiry Risk Table */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Expiry Risk Items</Text>
        {expiryRisk.length > 0
          ? expiryRisk.map((item, i) => {
              const risk = getRiskLevel(item.days);
              return (
                <View key={i} style={styles.riskRow}>
                  <Text style={styles.riskName}>{item.name}</Text>
                  <Text style={styles.riskDays}>Expires in {item.days}d</Text>
                  <View style={[styles.riskBadge, { backgroundColor: risk.color }]}>
                    <Text style={styles.riskBadgeText}>{risk.label}</Text>
                  </View>
                </View>
              );
            })
          : <Text style={styles.emptyText}>No expiry risks 🎉</Text>
        }
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}
  const BG = '#0D1B2A';
const CARD = '#132032';
const BORDER = 'rgba(255,255,255,0.07)';
const styles = StyleSheet.create({


container: {
  flex: 1,
  backgroundColor: BG,
  padding: 14,
},

card: {
  backgroundColor: CARD,
  borderRadius: radius.md,
  padding: 16,
  marginBottom: 14,
  borderWidth: 1,
  borderColor: BORDER,
},
  kpiGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 14 },
kpiCard: {
  flex: 1,
  minWidth: '45%',
  backgroundColor: '#1E293B',
  borderRadius: 16,
  padding: 14,
  borderWidth: 1,
  borderColor: 'rgba(255,255,255,0.05)',
},  kpiIcon: { fontSize: 22, marginBottom: 6 },
  kpiValue: { fontSize: 20, fontWeight: '900', color: '#E6EDF3', letterSpacing: -0.5 },
  kpiLabel: { fontSize: 11, color: '#94A3B8', marginTop: 2 },
  kpiSub: { fontSize: 11, fontWeight: '600', marginTop: 4 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  row: { flexDirection: 'row', gap: 12, marginBottom: 14 },
  periodRow: { flexDirection: 'row', gap: 4, backgroundColor: colors.bg, borderRadius: 10, padding: 3 },
  periodPill: { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 8 },
  periodActive: { backgroundColor: colors.dark },
  periodText: { fontSize: 11, color: colors.textSub, fontWeight: '600' },
  periodTextActive: { color: '#fff' },
  aiBadge: { backgroundColor: colors.accent + '22', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 10 },
  aiBadgeText: { color: colors.accent, fontSize: 11, fontWeight: '700' },
  forecastInfo: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.1)' },
  forecastStat: { alignItems: 'center' },
  forecastStatVal: { fontSize: 16, fontWeight: '800', color: '#fff' },
  forecastStatLabel: { fontSize: 10, color: 'rgba(255,255,255,0.5)', marginTop: 2 },
  riskRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.06)' },
riskName: { 
  flex: 1, 
  fontSize: 13, 
  fontWeight: '700', 
  color: '#E6EDF3'   // ✅ bright like Sales screen
},  riskDays: { 
  fontSize: 12, 
  color: '#94A3B8'   // softer but visible
},
  riskBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, marginLeft: 10 },
  riskBadgeText: { color: '#fff', fontSize: 10, fontWeight: '800' },
  cardTitle: { color: '#fff', fontWeight: '800' },
cardSub: { color: 'rgba(255,255,255,0.4)' },
emptyText: { color: 'rgba(255,255,255,0.4)' },
});