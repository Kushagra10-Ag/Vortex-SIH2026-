import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, KeyboardAvoidingView, Platform, Animated, ActivityIndicator,
  Dimensions,
} from 'react-native';
import { router } from 'expo-router';
import Svg, { Path, Circle, Rect, G } from 'react-native-svg';
import { sendChatMessage, fetchBills, fetchProducts } from '../../services/api';

interface Message { id: string; role: 'user' | 'assistant'; text: string; }

// ── Theme (matches dashboard "command center" palette) ──────────────────────
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

const WELCOME: Message = {
  id: '0',
  role: 'assistant',
  text: "Hi there! I'm here to help with your store data. What can I analyze for you today?",
};

// ── Icon set (SVG, matches dashboard icon style) ─────────────────────────────
function Icon({ name, color, size = 15 }: { name: string; color: string; size?: number }) {
  const p = { stroke: color, strokeWidth: 2, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, React.ReactNode> = {
    grid: (<><Rect x={4} y={4} width={7} height={7} rx={1.5} {...p} /><Rect x={13} y={4} width={7} height={7} rx={1.5} {...p} /><Rect x={4} y={13} width={7} height={7} rx={1.5} {...p} /><Rect x={13} y={13} width={7} height={7} rx={1.5} {...p} /></>),
    video: (<><Rect x={3} y={7} width={13} height={10} rx={2} {...p} /><Path d="M16 10.5l5-3v9l-5-3" {...p} /></>),
    cart: (<><Circle cx={9} cy={20} r={1.4} fill={color} /><Circle cx={17} cy={20} r={1.4} fill={color} /><Path d="M3 4h2l2.2 10.6a2 2 0 0 0 2 1.6h7.3a2 2 0 0 0 2-1.6L20 8H6" {...p} /></>),
    box: (<><Path d="M3 8l9-5 9 5v8l-9 5-9-5Z" {...p} /><Path d="M3 8l9 5 9-5M12 13v8" {...p} /></>),
    users: (<><Circle cx={9} cy={8} r={3} {...p} /><Path d="M3.5 20a5.5 5.5 0 0 1 11 0" {...p} /><Path d="M16 5.5a3 3 0 0 1 0 5.8M17.5 15.5a5.5 5.5 0 0 1 3 4.5" {...p} /></>),
    briefcase: (<><Rect x={3} y={8} width={18} height={11} rx={2} {...p} /><Path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18" {...p} /></>),
    chart: (<><Path d="M4 4v16h16" {...p} /><Path d="M8 15l3-4 3 2 4-6" {...p} /></>),
    gear: (<><Circle cx={12} cy={12} r={3} {...p} /><Path d="M12 3v2.2M12 18.8V21M21 12h-2.2M5.2 12H3M18.4 5.6l-1.5 1.5M7.1 16.9l-1.5 1.5M18.4 18.4l-1.5-1.5M7.1 7.1L5.6 5.6" {...p} /></>),
    bell: (<><Path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" {...p} /><Path d="M10 20a2 2 0 0 0 4 0" {...p} /></>),
    bot: (<><Rect x={4} y={7} width={16} height={12} rx={3} {...p} /><Circle cx={9} cy={13} r={1.2} fill={color} /><Circle cx={15} cy={13} r={1.2} fill={color} /><Path d="M12 3v4M9 3h6" {...p} /></>),
    send: (<><Path d="M4 12l16-8-6 16-3-6-7-2Z" {...p} /></>),
    alert: (<><Path d="M12 3l9 16H3l9-16Z" {...p} /><Path d="M12 9.5v4.2" {...p} /><Circle cx={12} cy={16.7} r={0.9} fill={color} /></>),
    star: (<><Path d="M12 3l2.6 5.9 6.4.6-4.8 4.3 1.4 6.3L12 16.9 6.4 20.1l1.4-6.3-4.8-4.3 6.4-.6Z" {...p} /></>),
    clock: (<><Circle cx={12} cy={12} r={9} {...p} /><Path d="M12 7v5l3 2" {...p} /></>),
  };
  return <Svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</Svg>;
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
        const isActive = item.key === 'ai-assistant';
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

export default function Chatbot() {
  const { width } = Dimensions.get('window');
  const isWide = width >= 900;
  const isXWide = width >= 1280;

  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [bills, setBills] = useState<any[]>([]);
  const scrollRef = useRef<ScrollView>(null);
  const dotAnim = useRef(new Animated.Value(0)).current;
  const animRef = useRef<Animated.CompositeAnimation | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [p, b] = await Promise.all([fetchProducts(), fetchBills()]);
        setProducts(Array.isArray(p) ? p : []);
        setBills(Array.isArray(b) ? b : []);
      } catch (e) {
        console.log('[v0] chatbot insights load error', e);
      }
    })();
  }, []);

  useEffect(() => {
    if (isTyping) {
      animRef.current = Animated.loop(
        Animated.sequence([
          Animated.timing(dotAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
          Animated.timing(dotAnim, { toValue: 0, duration: 500, useNativeDriver: true }),
        ])
      );
      animRef.current.start();
    } else {
      animRef.current?.stop();
      dotAnim.setValue(0);
    }
  }, [isTyping]);

  const scrollToEnd = () =>
    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);

  const send = async (text?: string) => {
    const msgText = (text || input).trim();
    if (!msgText || isTyping) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: msgText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);
    scrollToEnd();

    const res = await sendChatMessage(msgText);

    setIsTyping(false);
    const botMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      text: res,
    };
    setMessages(prev => [...prev, botMsg]);
    scrollToEnd();
  };

  const handleKeyPress = ({ nativeEvent }: { nativeEvent: { key: string } }) => {
    if (nativeEvent.key === 'Enter') {
      send();
    }
  };

  // ── Suggested questions ──────────────────────────────────────────────────
  const suggested = [
    "Show today's sales",
    'Current queue',
    'Inventory health',
    'Store summary',
    "Today's footfall",
    'Low stock products',
  ];

  // ── AI Insights, derived from real data like the dashboard ──────────────
  const now = new Date();
  const isToday = (d: Date) => d.toDateString() === now.toDateString();
  const todayBills = bills.filter((b: any) => b.created_at && isToday(new Date(b.created_at)));

  const lowStock = products
    .filter((p: any) => p.quantity < (p.min_stock_level ?? 0) && p.quantity > 0)
    .sort((a: any, b: any) => a.quantity - b.quantity);

  const productTotals: Record<string, number> = {};
  todayBills.forEach((b: any) => {
    (b.items || []).forEach((it: any) => {
      const name = it.name || it.product_name || 'Item';
      productTotals[name] = (productTotals[name] || 0) + (it.total || it.amount || 0);
    });
  });
  const topProductEntry = Object.entries(productTotals).sort((a, b) => b[1] - a[1])[0];

  const openHour = 9, closeHour = 21;
  const hours = Array.from({ length: closeHour - openHour + 1 }, (_, i) => openHour + i);
  const hourlyCount = hours.map((hr) =>
    todayBills.filter((b: any) => b.created_at && new Date(b.created_at).getHours() === hr).length
  );
  const peakHour = hours[hourlyCount.indexOf(Math.max(...hourlyCount, 0))];
  const peakQueue = Math.max(...hourlyCount.map((c) => Math.round(c * 1.4)), 0);

  type Insight = { icon: string; color: string; title: string; sub: string };
  const insights: Insight[] = [];
  if (lowStock[0]) {
    insights.push({
      icon: 'alert', color: RED,
      title: `Restock ${lowStock[0].name}`,
      sub: `Inventory is low, only ${lowStock[0].quantity} units left`,
    });
  }
  if (peakQueue >= 3) {
    insights.push({
      icon: 'users', color: AMBER,
      title: 'Queue Growing',
      sub: `Queue size has increased to ${peakQueue} customers`,
    });
  }
  if (topProductEntry) {
    insights.push({
      icon: 'star', color: GREEN,
      title: 'Highest Selling Product',
      sub: `${topProductEntry[0]}, Rs ${topProductEntry[1].toFixed(0)} in sales today`,
    });
  }
  if (Math.max(...hourlyCount, 0) > 0) {
    insights.push({
      icon: 'clock', color: AMBER,
      title: 'Peak Shopping Hour',
      sub: `Expected to begin at ${peakHour}:00 today`,
    });
  }
  if (insights.length === 0) {
    insights.push({ icon: 'chart', color: BLUE, title: 'All Systems Normal', sub: 'No alerts to show right now' });
  }

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
        {isWide && <Sidebar />}

        <View style={styles.mainArea}>
          <View style={[styles.threeCol, !isXWide && styles.threeColStacked]}>
            {/* Suggested Questions */}
            <View style={[styles.panel, isXWide ? styles.sideColWidth : styles.fullWidth]}>
              <View style={styles.panelHeadBar}>
                <Text style={styles.panelHeadBarText}>Suggested Questions</Text>
              </View>
              <View style={styles.suggestedList}>
                {suggested.map((q) => (
                  <TouchableOpacity
                    key={q}
                    style={styles.suggestedChip}
                    onPress={() => send(q)}
                    disabled={isTyping}
                  >
                    <Text style={styles.suggestedChipText}>{q}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Conversation */}
            <KeyboardAvoidingView
              style={[styles.panel, styles.conversationPanel, isXWide ? styles.centerColWidth : styles.fullWidth]}
              behavior={Platform.OS === 'ios' ? 'padding' : undefined}
              keyboardVerticalOffset={90}
            >
              <Text style={styles.panelTitlePlain}>Conversation</Text>

              <ScrollView
                ref={scrollRef}
                style={styles.messages}
                showsVerticalScrollIndicator={false}
                onContentSizeChange={scrollToEnd}
              >
                {messages.map(m => (
                  <View key={m.id} style={[styles.bubble, m.role === 'user' ? styles.userBubble : styles.botBubble]}>
                    {m.role === 'user' ? (
                      <View style={{ alignItems: 'flex-end' }}>
                        <Text style={styles.senderLabel}>Admin</Text>
                        <View style={[styles.bubbleInner, styles.userBubbleInner]}>
                          <Text style={[styles.bubbleText, styles.userBubbleText]}>{m.text}</Text>
                        </View>
                      </View>
                    ) : (
                      <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 8 }}>
                        <View style={styles.botAvatarSmall}>
                          <Icon name="bot" color={BLUE} size={14} />
                        </View>
                        <View>
                          <Text style={styles.senderLabel}>Retail Assistant</Text>
                          <View style={[styles.bubbleInner, styles.botBubbleInner]}>
                            <Text style={styles.bubbleText}>{m.text}</Text>
                          </View>
                        </View>
                      </View>
                    )}
                  </View>
                ))}

                {isTyping && (
                  <View style={[styles.bubble, styles.botBubble]}>
                    <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: 8 }}>
                      <View style={styles.botAvatarSmall}>
                        <Icon name="bot" color={BLUE} size={14} />
                      </View>
                      <View style={styles.typingBubble}>
                        {[0, 1, 2].map(i => (
                          <Animated.View key={i} style={[styles.dot, { opacity: dotAnim, marginLeft: i * 6 }]} />
                        ))}
                      </View>
                    </View>
                  </View>
                )}
              </ScrollView>

              <View style={styles.inputRow}>
                <TextInput
                  style={styles.textInput}
                  placeholder="Ask about your business..."
                  placeholderTextColor={FAINT}
                  value={input}
                  onChangeText={setInput}
                  multiline
                  returnKeyType="send"
                  onSubmitEditing={() => send()}
                  onKeyPress={handleKeyPress}
                  blurOnSubmit={false}
                  editable={!isTyping}
                />
                <TouchableOpacity
                  style={[styles.sendBtn, (!input.trim() || isTyping) && styles.sendBtnDisabled]}
                  onPress={() => send()}
                  disabled={!input.trim() || isTyping}
                >
                  {isTyping
                    ? <ActivityIndicator color="#fff" size="small" />
                    : <Icon name="send" color="#fff" size={16} />
                  }
                </TouchableOpacity>
              </View>
            </KeyboardAvoidingView>

            {/* AI Insights */}
            <View style={[styles.panel, isXWide ? styles.sideColWidth : styles.fullWidth]}>
              <View style={styles.panelHeadBar}>
                <Text style={styles.panelHeadBarText}>AI Insights</Text>
              </View>
              <ScrollView showsVerticalScrollIndicator={false}>
                {insights.map((ins, i) => (
                  <View key={i} style={[styles.insightCard, { borderLeftColor: ins.color }]}>
                    <View style={[styles.insightIcon, { backgroundColor: ins.color + '1A' }]}>
                      <Icon name={ins.icon} color={ins.color} size={14} />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={styles.insightTitle}>{ins.title}</Text>
                      <Text style={styles.insightSub}>{ins.sub}</Text>
                    </View>
                  </View>
                ))}
              </ScrollView>
            </View>
          </View>
        </View>
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

  mainArea: { flex: 1, padding: 10 },
  threeCol: { flex: 1, flexDirection: 'row', gap: 10 },
  threeColStacked: { flexDirection: 'column' },

  panel: {
    backgroundColor: CARD, borderRadius: 14,
    borderWidth: 1, borderColor: BORDER,
    shadowColor: '#0F172A', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
    overflow: 'hidden',
  },
  fullWidth: { width: '100%', marginBottom: 10 },
  sideColWidth: { flexBasis: 240, flexGrow: 0, flexShrink: 0 },
  centerColWidth: { flex: 1 },

  panelHeadBar: { backgroundColor: '#0F2A57', paddingVertical: 12, paddingHorizontal: 14 },
  panelHeadBarText: { color: '#fff', fontWeight: '800', fontSize: 13 },
  panelTitlePlain: { fontSize: 14, fontWeight: '800', color: TEXT, padding: 14, paddingBottom: 8 },

  suggestedList: { padding: 10, gap: 8 },
  suggestedChip: { backgroundColor: '#F8FAFC', borderWidth: 1, borderColor: BORDER, borderRadius: 10, paddingVertical: 10, paddingHorizontal: 12 },
  suggestedChipText: { fontSize: 12.5, fontWeight: '600', color: TEXT },

  conversationPanel: { flex: 1 },
  messages: { flex: 1, paddingHorizontal: 14 },
  bubble: { marginBottom: 14 },
  userBubble: { alignItems: 'flex-end' },
  botBubble: { alignItems: 'flex-start' },
  senderLabel: { fontSize: 10.5, fontWeight: '700', color: MUTED, marginBottom: 3 },

  bubbleInner: { maxWidth: 420, borderRadius: 12, padding: 11 },
  userBubbleInner: { backgroundColor: BLUE + '14', borderWidth: 1, borderColor: BLUE + '33' },
  botBubbleInner: { backgroundColor: '#F8FAFC', borderWidth: 1, borderColor: BORDER },

  bubbleText: { fontSize: 13.5, color: TEXT, lineHeight: 19 },
  userBubbleText: { color: '#1D4ED8' },

  botAvatarSmall: {
    width: 26, height: 26, borderRadius: 13, backgroundColor: BLUE + '14',
    alignItems: 'center', justifyContent: 'center', marginTop: 14,
    borderWidth: 1, borderColor: BLUE + '33',
  },

  typingBubble: {
    backgroundColor: '#F8FAFC', borderRadius: 12, padding: 14,
    flexDirection: 'row', alignItems: 'center',
    borderWidth: 1, borderColor: BORDER,
  },
  dot: { width: 7, height: 7, borderRadius: 3.5, backgroundColor: FAINT },

  inputRow: {
    flexDirection: 'row', gap: 10, padding: 12,
    borderTopWidth: 1, borderTopColor: BORDER,
  },
  textInput: {
    flex: 1, borderWidth: 1.5, borderColor: BORDER, borderRadius: 12,
    padding: 11, fontSize: 13.5, color: TEXT, maxHeight: 100, backgroundColor: '#F8FAFC',
  },
  sendBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: BLUE, alignItems: 'center', justifyContent: 'center' },
  sendBtnDisabled: { backgroundColor: '#CBD5E1' },

  insightCard: {
    flexDirection: 'row', gap: 10, padding: 11, margin: 10, marginBottom: 0,
    backgroundColor: '#F8FAFC', borderRadius: 10, borderLeftWidth: 3,
    borderWidth: 1, borderColor: BORDER,
  },
  insightIcon: { width: 26, height: 26, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  insightTitle: { fontSize: 12, fontWeight: '800', color: TEXT },
  insightSub: { fontSize: 10.5, color: MUTED, marginTop: 2, lineHeight: 14 },
});