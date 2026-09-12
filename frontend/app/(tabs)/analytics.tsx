import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Animated,
  Dimensions,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { router } from 'expo-router';
import Svg, { Circle, Path, Rect ,G} from 'react-native-svg';
import { useRouter } from 'expo-router';
import { colors } from '../../constants/theme';
import LineChart from '../../components/LineChart';
import BarChart from '../../components/BarChart';
import PieChart from '../../components/PieChart';
import {
  fetchAIForecast,
  fetchAnalyticsDashboard,
  fetchBills,
  fetchProducts,
} from '../../services/api';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

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

type Tab = 'business' | 'shopper' | 'queue' | 'inventory';

type Point = {
  label: string;
  value: number;
};

type BusinessKpis = {
  totalRevenue: number;
  avgDaily: number;
  topProduct: string;
  growth: number;
};

function Icon({
  icon,
  color = MUTED,
}: {
  icon: string;
  color?: string;
}) {
  const common = {
    stroke: color,
    strokeWidth: 2,
    fill: 'none',
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  };

  const icons: Record<string, React.ReactNode> = {
    grid: (
      <>
        <Rect x={4} y={4} width={7} height={7} rx={1.5} {...common} />
        <Rect x={13} y={4} width={7} height={7} rx={1.5} {...common} />
        <Rect x={4} y={13} width={7} height={7} rx={1.5} {...common} />
        <Rect x={13} y={13} width={7} height={7} rx={1.5} {...common} />
      </>
    ),
    video: (
      <>
        <Rect x={3} y={7} width={13} height={10} rx={2} {...common} />
        <Path d="M16 10.5l5-3v9l-5-3" {...common} />
      </>
    ),
    cart: (
      <>
        <Circle cx={9} cy={20} r={1.4} fill={color} />
        <Circle cx={17} cy={20} r={1.4} fill={color} />
        <Path d="M3 4h2l2.2 10.6a2 2 0 0 0 2 1.6h7.3a2 2 0 0 0 2-1.6L20 8H6" {...common} />
      </>
    ),
    box: (
      <>
        <Path d="M3 8l9-5 9 5v8l-9 5-9-5Z" {...common} />
        <Path d="M3 8l9 5 9-5M12 13v8" {...common} />
      </>
    ),
    users: (
      <>
        <Circle cx={9} cy={8} r={3} {...common} />
        <Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...common} />
        <Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...common} />
      </>
    ),
    briefcase: (
      <>
        <Rect x={3} y={8} width={18} height={11} rx={2} {...common} />
        <Path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18" {...common} />
      </>
    ),
    chart: (
      <>
        <Path d="M4 4v16h16" {...common} />
        <Path d="M8 15l3-4 3 2 4-6" {...common} />
      </>
    ),
    bot: (
  <>
    <Rect x={4} y={7} width={16} height={12} rx={3} {...common} />
    <Circle cx={9} cy={13} r={1.2} fill={color} />
    <Circle cx={15} cy={13} r={1.2} fill={color} />
    <Path d="M12 3v4M9 3h6" {...common} />
  </>
),
    gear: (
      <>
        <Circle cx={12} cy={12} r={3} {...common} />
        <Path d="M12 3v2.2M12 18.8V21M21 12h-2.2M5.2 12H3M18.4 5.6l-1.5 1.5M7.1 16.9l-1.5 1.5M18.4 18.4l-1.5-1.5M7.1 7.1L5.6 5.6" {...common} />
      </>
    ),
  };

  return (
    <Svg width={16} height={16} viewBox="0 0 24 24">
      {icons[icon]}
    </Svg>
  );
}
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
        const isActive = item.key === 'analytics';

        return (
          <TouchableOpacity
            key={item.key}
            style={[styles.navItem, isActive && styles.navItemActive]}
            onPress={() => router.push(item.route as any)}
          >
            <Icon icon={item.icon} color={isActive ? BLUE : MUTED} />
            <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>
              {item.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

function TopBar() {
  return (
    <View style={styles.topBar}>
      <View style={styles.topBarLeft}>
        <View style={styles.logoBadge}>
          <Text style={styles.logoText}>F</Text>
        </View>

        <Text style={styles.appTitle}>BizMate</Text>
      </View>

      <View style={styles.topBarRight}>
        <View style={styles.bell}>
          <Text style={styles.bellText}>♧</Text>
          <View style={styles.bellDot} />
        </View>

        <View style={styles.avatar}>
          <Text style={styles.avatarText}>V</Text>
        </View>
      </View>
    </View>
  );
}

function TabButton({
  active,
  label,
  onPress,
}: {
  active: boolean;
  label: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.85}
      style={[styles.tabButton, active && styles.tabButtonActive]}
    >
      <Text style={[styles.tabButtonTitle, active && styles.tabButtonTitleActive]}>
        {label}
      </Text>
      <Text style={[styles.tabButtonHint, active && styles.tabButtonHintActive]}>
        Click to view
      </Text>
    </TouchableOpacity>
  );
}

function StatCard({
  icon,
  label,
  value,
  detail,
  color,
}: {
  icon: string;
  label: string;
  value: string;
  detail: string;
  color: string;
}) {
  return (
    <View style={styles.statCard}>
      <View style={styles.statHeader}>
        <View style={[styles.statIconWrap, { backgroundColor: `${color}18` }]}>
          <Text style={[styles.statIcon, { color }]}>{icon}</Text>
        </View>
        <Text style={styles.statLabel}>{label}</Text>
      </View>

      <Text numberOfLines={1} style={styles.statValue}>
        {value}
      </Text>

      <Text style={[styles.statDetail, { color }]}>{detail}</Text>
    </View>
  );
}

function Panel({
  title,
  subtitle,
  children,
  style,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  style?: any;
}) {
  return (
    <View style={[styles.panel, style]}>
      <View style={styles.panelHeader}>
        <Text style={styles.panelTitle}>{title}</Text>
        {subtitle ? <Text style={styles.panelSubtitle}>{subtitle}</Text> : null}
      </View>

      <View style={styles.panelBody}>{children}</View>
    </View>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <View style={styles.emptyState}>
      <Text style={styles.emptyText}>{text}</Text>
    </View>
  );
}

export default function Analytics() {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const isWide = SCREEN_WIDTH >= 900;
  const isXWide = SCREEN_WIDTH >= 1280;

  const [activeTab, setActiveTab] = useState<Tab>('business');
  const [period, setPeriod] = useState<'Week' | 'Month' | '6M'>('Month');
  const [loading, setLoading] = useState(true);

  const [kpis, setKpis] = useState<BusinessKpis>({
    totalRevenue: 0,
    avgDaily: 0,
    topProduct: '—',
    growth: 0,
  });

  const [revenueTrend, setRevenueTrend] = useState<Point[]>([]);
  const [monthlySales, setMonthlySales] = useState<Point[]>([]);
  const [categoryData, setCategoryData] = useState<
    { label: string; value: number; color: string }[]
  >([]);
  const [expiryRisk, setExpiryRisk] = useState<{ name: string; days: number }[]>([]);
  const [forecastData, setForecastData] = useState<Point[]>([]);
  const [bills, setBills] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);

  useEffect(() => {
    loadAnalytics();

    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 450,
      useNativeDriver: true,
    }).start();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);

    try {
      const [analytics, forecast, allBills, allProducts] = await Promise.all([
        fetchAnalyticsDashboard(),
        fetchAIForecast(),
        fetchBills(),
        fetchProducts(),
      ]);

      if (analytics?.kpis) setKpis(analytics.kpis);
      if (analytics?.revenueTrend?.length) setRevenueTrend(analytics.revenueTrend);
      if (analytics?.monthlySales?.length) setMonthlySales(analytics.monthlySales);
      if (analytics?.expiryRisk?.length) setExpiryRisk(analytics.expiryRisk);
      if (forecast?.length) setForecastData(forecast);

      if (analytics?.categoryData?.length) {
        const chartColors = [
          BLUE,
          GREEN,
          AMBER,
          PURPLE,
          RED,
          TEAL,
          '#A78BFA',
          '#34D399',
        ];

        setCategoryData(
          analytics.categoryData.map((item: any, index: number) => ({
            label: item.label,
            value: item.value,
            color: chartColors[index % chartColors.length],
          }))
        );
      }

      setBills(Array.isArray(allBills) ? allBills : []);
      setProducts(Array.isArray(allProducts) ? allProducts : []);
    } finally {
      setLoading(false);
    }
  };

  const getBusinessTrend = () => {
    if (period === 'Week') return revenueTrend.slice(-7);
    if (period === 'Month') return revenueTrend.slice(-30);
    return revenueTrend;
  };

  const storeMetrics = useMemo(() => {
    const now = new Date();
    const isToday = (date: Date) => date.toDateString() === now.toDateString();

    const todayBills = bills.filter(
      (bill) => bill.created_at && isToday(new Date(bill.created_at))
    );

    const currentCustomers = new Set(
      todayBills.map((bill) => bill.customer_name || bill.id)
    ).size;

    const hours = Array.from({ length: 13 }, (_, index) => index + 9);

    const hourlyBills = hours.map((hour) =>
      todayBills.filter(
        (bill) =>
          bill.created_at &&
          new Date(bill.created_at).getHours() === hour
      ).length
    );

    const footfallTrend = hours.map((hour, index) => ({
      label: `${hour}:00`,
      value: hourlyBills[index] * 3 + (hourlyBills[index] ? 2 : 0),
    }));

    const queueTrend = hours.map((hour, index) => ({
      label: `${hour}:00`,
      value: Math.round(hourlyBills[index] * 1.4),
    }));

    const todayFootfall = footfallTrend.reduce(
      (sum, item) => sum + item.value,
      0
    );

    const peakFootfall = footfallTrend.reduce(
      (best, item) => (item.value > best.value ? item : best),
      { label: '—', value: 0 }
    );

    const peakQueue = Math.max(
      ...queueTrend.map((item) => item.value),
      0
    );

    const avgQueue = queueTrend.length
      ? Math.round(
          queueTrend.reduce((sum, item) => sum + item.value, 0) /
            queueTrend.length
        )
      : 0;

    const lowStock = products.filter(
      (product) =>
        product.quantity > 0 &&
        product.quantity < (product.min_stock_level ?? 0)
    );

    const critical = products.filter((product) => product.quantity <= 0);

    const healthy = products.filter(
      (product) => product.quantity >= (product.min_stock_level ?? 0)
    );

    const inventoryHealth = products.length
      ? Math.round((healthy.length / products.length) * 100)
      : 100;

    const restockingTrend = products
      .slice(0, 7)
      .map((product, index) => ({
        label: product.name?.slice(0, 7) || `Item ${index + 1}`,
        value: Math.max(0, (product.min_stock_level ?? 0) - product.quantity),
      }))
      .reverse();

    return {
      currentCustomers,
      todayFootfall,
      peakHour: peakFootfall.value ? peakFootfall.label : '—',
      avgDwellTime: 0,
      footfallTrend,
      avgQueue,
      congestion: Math.min(100, peakQueue * 20),
      waitingTime: Math.round(peakQueue * 1.5),
      queueTrend,
      healthy,
      lowStock,
      critical,
      inventoryHealth,
      restockingTrend,
    };
  }, [bills, products]);

  const chartWidth = isXWide ? 420 : isWide ? 300 : SCREEN_WIDTH - 48;
  const businessKpiBasis = isXWide ? '23.8%' : isWide ? '48.8%' : '100%';

  const renderBusiness = () => (
    <>
      <View style={styles.grid}>
        <View style={[styles.statWrapper, { flexBasis: businessKpiBasis }]}>
          <StatCard
            icon="₹"
            label="Total Revenue"
            value={`₹${(kpis.totalRevenue / 1000).toFixed(0)}K`}
            detail={`+${kpis.growth}% vs previous period`}
            color={GREEN}
          />
        </View>

        <View style={[styles.statWrapper, { flexBasis: businessKpiBasis }]}>
          <StatCard
            icon="⌁"
            label="Avg Daily Sales"
            value={`₹${Math.round(kpis.avgDaily)}`}
            detail="Average daily revenue"
            color={BLUE}
          />
        </View>

        <View style={[styles.statWrapper, { flexBasis: businessKpiBasis }]}>
          <StatCard
            icon="★"
            label="Top Product"
            value={kpis.topProduct || '—'}
            detail="Best-selling product"
            color={PURPLE}
          />
        </View>

        <View style={[styles.statWrapper, { flexBasis: businessKpiBasis }]}>
          <StatCard
            icon="↗"
            label="Growth"
            value={`${kpis.growth}%`}
            detail="Compared with last period"
            color={TEAL}
          />
        </View>
      </View>

      <View style={styles.dashboardRow}>
        <Panel
          title="Sales Trend"
          subtitle="Revenue over the selected period"
          style={styles.largePanel}
        >
          <View style={styles.periodRow}>
            {(['Week', 'Month', '6M'] as const).map((item) => (
              <TouchableOpacity
                key={item}
                onPress={() => setPeriod(item)}
                style={[
                  styles.periodButton,
                  period === item && styles.periodButtonActive,
                ]}
              >
                <Text
                  style={[
                    styles.periodText,
                    period === item && styles.periodTextActive,
                  ]}
                >
                  {item}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {getBusinessTrend().length ? (
            <LineChart
              data={getBusinessTrend()}
              width={chartWidth}
              height={150}
              color={BLUE}
            />
          ) : (
            <EmptyState text="No sales trend data yet" />
          )}
        </Panel>

        <Panel
          title="Monthly Sales"
          subtitle="Revenue by month"
          style={styles.smallPanel}
        >
          {monthlySales.length ? (
            <BarChart
              data={monthlySales}
              width={chartWidth * 0.75}
              height={150}
              color={PURPLE}
            />
          ) : (
            <EmptyState text="No monthly sales data" />
          )}
        </Panel>

        <Panel
          title="Product Categories"
          subtitle="Sales distribution"
          style={styles.smallPanel}
        >
          {categoryData.length ? (
            <PieChart data={categoryData} size={130} />
          ) : (
            <EmptyState text="No category data" />
          )}
        </Panel>
      </View>

      <View style={styles.dashboardRow}>
        <Panel
          title="AI Sales Forecast"
          subtitle="Projected demand for the next seven days"
          style={styles.largePanel}
        >
          {forecastData.length ? (
            <LineChart
              data={forecastData}
              width={chartWidth}
              height={125}
              color={TEAL}
            />
          ) : (
            <EmptyState text="Forecast unavailable" />
          )}
        </Panel>

        <Panel
          title="Expiry Risk Items"
          subtitle="Products requiring attention"
          style={styles.smallPanel}
        >
          {expiryRisk.length ? (
            expiryRisk.slice(0, 4).map((item, index) => {
              const riskColor =
                item.days <= 7
                  ? RED
                  : item.days <= 20
                    ? AMBER
                    : BLUE;

              return (
                <View key={`${item.name}-${index}`} style={styles.riskRow}>
                  <View style={{ flex: 1 }}>
                    <Text numberOfLines={1} style={styles.riskName}>
                      {item.name}
                    </Text>
                    <Text style={styles.riskDays}>Expires in {item.days} days</Text>
                  </View>

                  <View
                    style={[
                      styles.riskBadge,
                      { backgroundColor: `${riskColor}18` },
                    ]}
                  >
                    <Text style={[styles.riskBadgeText, { color: riskColor }]}>
                      {item.days <= 7 ? 'Critical' : 'Monitor'}
                    </Text>
                  </View>
                </View>
              );
            })
          ) : (
            <EmptyState text="No expiry risks" />
          )}
        </Panel>
      </View>
    </>
  );

  const renderShopper = () => (
    <>
      <View style={styles.grid}>
        <View style={styles.statWrapper}>
          <StatCard
            icon="♙"
            label="Current Customers"
            value={`${storeMetrics.currentCustomers}`}
            detail="Customers in store now"
            color={BLUE}
          />
        </View>

        <View style={styles.statWrapper}>
          <StatCard
            icon="♧"
            label="Today's Footfall"
            value={`${storeMetrics.todayFootfall}`}
            detail="Estimated visitors today"
            color={GREEN}
          />
        </View>

        <View style={styles.statWrapper}>
          <StatCard
            icon="◷"
            label="Peak Hour"
            value={storeMetrics.peakHour}
            detail="Highest traffic period"
            color={AMBER}
          />
        </View>

        <View style={styles.statWrapper}>
          <StatCard
            icon="◌"
            label="Average Dwell Time"
            value={`${storeMetrics.avgDwellTime} min`}
            detail="Requires camera dwell data"
            color={PURPLE}
          />
        </View>
      </View>

      <View style={styles.dashboardRow}>
        <Panel
          title="Footfall Trend"
          subtitle="Estimated store visitors by hour"
          style={styles.fullPanel}
        >
          <LineChart
            data={storeMetrics.footfallTrend}
            width={isXWide ? 960 : chartWidth}
            height={260}
            color={GREEN}
          />
        </Panel>
      </View>
    </>
  );

  const renderQueue = () => (
    <>
      <View style={styles.grid}>
        <View style={styles.statWrapper}>
          <StatCard
            icon="♙"
            label="Average Queue"
            value={`${storeMetrics.avgQueue}`}
            detail="Average people waiting"
            color={BLUE}
          />
        </View>

        <View style={styles.statWrapper}>
          <StatCard
            icon="⚠"
            label="Congestion"
            value={`${storeMetrics.congestion}%`}
            detail={
              storeMetrics.congestion > 70
                ? 'High congestion'
                : storeMetrics.congestion > 40
                  ? 'Moderate congestion'
                  : 'Low congestion'
            }
            color={
              storeMetrics.congestion > 70
                ? RED
                : storeMetrics.congestion > 40
                  ? AMBER
                  : GREEN
            }
          />
        </View>

        <View style={styles.statWrapper}>
          <StatCard
            icon="◷"
            label="Waiting Time"
            value={`${storeMetrics.waitingTime} min`}
            detail="Estimated average wait"
            color={PURPLE}
          />
        </View>
      </View>

      <View style={styles.dashboardRow}>
        <Panel
          title="Queue Trend"
          subtitle="Queue length throughout the day"
          style={styles.fullPanel}
        >
          <BarChart
            data={storeMetrics.queueTrend}
            width={isXWide ? 960 : chartWidth}
            height={260}
            color={PURPLE}
          />
        </Panel>
      </View>
    </>
  );

  const renderInventory = () => {
    const inventoryData = [
      {
        label: 'Healthy',
        value: storeMetrics.healthy.length,
        color: GREEN,
      },
      {
        label: 'Low Stock',
        value: storeMetrics.lowStock.length,
        color: AMBER,
      },
      {
        label: 'Critical',
        value: storeMetrics.critical.length,
        color: RED,
      },
    ];

    return (
      <>
        <View style={styles.grid}>
          <View style={styles.statWrapper}>
            <StatCard
              icon="✓"
              label="Healthy Products"
              value={`${storeMetrics.healthy.length}`}
              detail={`${storeMetrics.inventoryHealth}% inventory health`}
              color={GREEN}
            />
          </View>

          <View style={styles.statWrapper}>
            <StatCard
              icon="!"
              label="Low Stock"
              value={`${storeMetrics.lowStock.length}`}
              detail="Needs restocking soon"
              color={AMBER}
            />
          </View>

          <View style={styles.statWrapper}>
            <StatCard
              icon="×"
              label="Critical Stock"
              value={`${storeMetrics.critical.length}`}
              detail="Restock immediately"
              color={RED}
            />
          </View>
        </View>

        <View style={styles.dashboardRow}>
          <Panel
            title="Inventory Health"
            subtitle="Current stock condition"
            style={styles.smallPanel}
          >
            <PieChart data={inventoryData} size={170} />
          </Panel>

          <Panel
            title="Restocking Trend"
            subtitle="Products below their stock threshold"
            style={styles.largePanel}
          >
            {storeMetrics.restockingTrend.length ? (
              <BarChart
                data={storeMetrics.restockingTrend}
                width={chartWidth}
                height={230}
                color={TEAL}
              />
            ) : (
              <EmptyState text="No restocking data yet" />
            )}
          </Panel>
        </View>
      </>
    );
  };

  const tabContent = {
    business: renderBusiness(),
    shopper: renderShopper(),
    queue: renderQueue(),
    inventory: renderInventory(),
  };

  return (
    <View style={styles.appShell}>
      <TopBar />

      <View style={styles.body}>
        {isWide && <Sidebar />}

        <View style={styles.content}>
          <View style={styles.contentHeader}>
            <View>
              <Text style={styles.pageTitle}>Analytics</Text>
              <Text style={styles.pageSubtitle}>
              </Text>
            </View>

            <TouchableOpacity style={styles.refreshButton} onPress={loadAnalytics}>
              <Text style={styles.refreshButtonText}>↻ Refresh</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.tabs}>
            <TabButton
              active={activeTab === 'business'}
              label="Business Analytics"
              onPress={() => setActiveTab('business')}
            />
            <TabButton
              active={activeTab === 'shopper'}
              label="Shopper Analytics"
              onPress={() => setActiveTab('shopper')}
            />
            <TabButton
              active={activeTab === 'queue'}
              label="Queue Analytics"
              onPress={() => setActiveTab('queue')}
            />
            <TabButton
              active={activeTab === 'inventory'}
              label="Inventory Analytics"
              onPress={() => setActiveTab('inventory')}
            />
          </View>

          {loading ? (
            <View style={styles.loadingArea}>
              <Text style={styles.loadingText}>Loading analytics…</Text>
            </View>
          ) : (
            <Animated.View style={[styles.analyticsArea, { opacity: fadeAnim }]}>
              {tabContent[activeTab]}
            </Animated.View>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  appShell: {
    flex: 1,
    backgroundColor: PAGE,
  },
  topBar: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12,
    backgroundColor: CARD, borderBottomWidth: 1, borderBottomColor: BORDER,
  },

topBarLeft: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  logoBadge: { width: 30, height: 30, borderRadius: 9, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  logoText: {
  color: '#fff',
  fontWeight: '900',
  fontSize: 14,
},

appTitle: {
  fontSize: 17,
  fontWeight: '900',
  color: TEXT,
  letterSpacing: -0.4,
},

topBarRight: {
  flexDirection: 'row',
  alignItems: 'center',
  gap: 12,
},
  bell: { width: 34, height: 34, borderRadius: 11, backgroundColor: CARD, borderWidth: 1, borderColor: BORDER, alignItems: 'center', justifyContent: 'center' },
  bellDot: { position: 'absolute', top: 8, right: 9, width: 6, height: 6, borderRadius: 3, backgroundColor: RED },
  avatar: { width: 34, height: 34, borderRadius: 17, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '800', fontSize: 14 },
  body: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
  width: SIDEBAR_WIDTH,
  backgroundColor: CARD,
  borderRightWidth: 1,
  borderRightColor: BORDER,
  paddingVertical: 14,
  paddingHorizontal: 10,
  gap: 3,
},
  navItem: {
  flexDirection: 'row',
  alignItems: 'center',
  gap: 10,
  paddingVertical: 10,
  paddingHorizontal: 12,
  borderRadius: 10,
},
  navItemActive: {
    backgroundColor: '#EAF1FF',
  },
  icon: {
    width: 20,
    fontSize: 17,
    textAlign: 'center',
  },
  navLabel: {
    color: MUTED,
    fontSize: 13,
    fontWeight: '600',
  },
  navLabelActive: {
    color: BLUE,
    fontWeight: '800',
  },
  content: {
  flex: 1,
  backgroundColor: PAGE,
  padding: 10,
  gap: 10,
},

contentHeader: {
  height: 40,
  marginBottom: 4,
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-between',
},

pageTitle: {
  fontSize: 20,
  fontWeight: '900',
  color: TEXT,
},

pageSubtitle: {
  fontSize: 10,
  color: FAINT,
  marginTop: 1,
},
  refreshButton: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 9,
    backgroundColor: BLUE,
  },
  refreshButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '800',
  },
  tabs: {
  height: 48,
  flexDirection: 'row',
  gap: 10,
  marginBottom: 10,
},

tabButton: {
  flex: 1,
  borderRadius: 10,
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: CARD,
  borderWidth: 1,
  borderColor: BORDER,
},
  tabButtonActive: {
    backgroundColor: '#173F7A',
    borderColor: '#173F7A',
  },
  tabButtonTitle: {
    color: TEXT,
    fontSize: 12,
    fontWeight: '800',
  },
  tabButtonTitleActive: {
    color: '#FFFFFF',
  },
  tabButtonHint: {
    color: FAINT,
    fontSize: 9,
    marginTop: 3,
  },
  tabButtonHintActive: {
    color: '#D8E6FF',
  },
  analyticsArea: {
    flex: 1,
    gap: 10,
  },
  loadingArea: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: MUTED,
    fontSize: 14,
    fontWeight: '700',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  statWrapper: {
    flexGrow: 1,
    flexBasis: '23.8%',
  },
  statCard: {
  height: 104,
  padding: 11,
  borderRadius: 14,
  backgroundColor: CARD,
  borderWidth: 1,
  borderColor: BORDER,
},


  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statIconWrap: {
    width: 27,
    height: 27,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
  },
  statIcon: {
    fontSize: 15,
    fontWeight: '900',
  },
  statLabel: {
    flex: 1,
    color: MUTED,
    fontSize: 11,
    fontWeight: '700',
  },
  statValue: {
    color: TEXT,
    fontSize: 22,
    fontWeight: '900',
    marginTop: 10,
  },
  statDetail: {
    fontSize: 10,
    fontWeight: '700',
    marginTop: 2,
  },
  dashboardRow: {
    flexDirection: 'row',
    gap: 10,
    flex: 1,
  },
  panel: {
  flexGrow: 1,
  minHeight: 0,
  padding: 12,
  borderRadius: 14,
  backgroundColor: CARD,
  borderWidth: 1,
  borderColor: BORDER,
},
  fullPanel: {
    flex: 1,
  },
  largePanel: {
    flex: 1.65,
  },
  smallPanel: {
    flex: 1,
  },
  panelHeader: {
    marginBottom: 6,
  },
  panelTitle: {
    color: TEXT,
    fontSize: 13,
    fontWeight: '800',
  },
  panelSubtitle: {
    color: FAINT,
    fontSize: 10,
    marginTop: 2,
  },
  panelBody: {
    flex: 1,
    minHeight: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  periodRow: {
    position: 'absolute',
    top: -35,
    right: 0,
    flexDirection: 'row',
    gap: 4,
  },
  periodButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: '#F1F5F9',
  },
  periodButtonActive: {
    backgroundColor: BLUE,
  },
  periodText: {
    color: MUTED,
    fontSize: 9,
    fontWeight: '700',
  },
  periodTextActive: {
    color: '#FFFFFF',
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    color: FAINT,
    fontSize: 12,
  },
  riskRow: {
    width: '100%',
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  riskName: {
    color: TEXT,
    fontSize: 12,
    fontWeight: '700',
  },
  riskDays: {
    color: MUTED,
    fontSize: 10,
    marginTop: 2,
  },
  riskBadge: {
    paddingHorizontal: 7,
    paddingVertical: 4,
    borderRadius: 7,
  },
  bellText: {
  fontSize: 19,
  color: MUTED,
},
  riskBadgeText: {
    fontSize: 9,
    fontWeight: '800',
  },
});