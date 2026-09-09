import { Tabs } from 'expo-router';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';

interface TabIconProps {
  icon: string;
  focused: boolean;
  label: string;
}

function TabIcon({ icon, focused, label }: TabIconProps) {
  const iconStyle: ViewStyle = focused
    ? { ...styles.iconWrap, ...styles.iconWrapActive }
    : styles.iconWrap;

  return (
    <View style={styles.tabItem}>
      <View style={iconStyle}>
        <Text style={styles.iconText}>{icon}</Text>
      </View>
      <Text style={focused ? styles.tabLabelActive : styles.tabLabel}>{label}</Text>
    </View>
  );
}

function HeaderTitle({ title }: { title: string }) {
  return (
    <View style={styles.headerTitleRow}>
      <Text style={styles.headerEmoji}>💼</Text>
      <Text style={styles.headerText}>{title}</Text>
    </View>
  );
}

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: '#0D1B2A' },
        headerShadowVisible: false,
        headerTitleAlign: 'center',
        headerTintColor: '#fff',
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          headerTitle: () => <HeaderTitle title="BIZMATE" />,
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="⊞" focused={focused} label="DASHBOARD" />
          ),
        }}
      />
      <Tabs.Screen
        name="billing"
        options={{
          headerTitle: () => <HeaderTitle title="SALES" />,
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="🛒" focused={focused} label="Billing" />
          ),
        }}
      />
      <Tabs.Screen
        name="inventory"
        options={{
          headerTitle: () => <HeaderTitle title="INVENTORY" />,
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="📦" focused={focused} label="INVENTORY" />
          ),
        }}
      />
      <Tabs.Screen
        name="analytics"
        options={{
          headerTitle: () => <HeaderTitle title="ANALYTICS" />,
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="📉" focused={focused} label="ANALYTICS" />
          ),
        }}
      />
      <Tabs.Screen
        name="chatbot"
        options={{
          headerTitle: () => <HeaderTitle title="AI ASSISTANT" />,
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="🤖" focused={focused} label="CHATBOT" />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#0D1B2A',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.06)',
    height: 72,
    paddingBottom: 10,
    paddingTop: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 20,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerEmoji: { fontSize: 20 },
  headerText: {
    fontSize: 17,
    fontWeight: '900',
    color: '#fff',
    letterSpacing: 3,
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
    gap: 3,
  },
  iconWrap: {
    width: 40,
    height: 30,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
  },
  iconWrapActive: {
    backgroundColor: 'rgba(79,142,247,0.2)',
  },
  iconText: {
    fontSize: 20,
    color: 'rgba(255,255,255,0.55)',
  },
  tabLabel: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.3)',
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  tabLabelActive: {
    fontSize: 9,
    color: '#4F8EF7',
    fontWeight: '700',
    letterSpacing: 0.3,
  },
});