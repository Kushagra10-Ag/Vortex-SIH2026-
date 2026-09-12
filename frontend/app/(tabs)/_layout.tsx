import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: { display: 'none' },
      }}
    >
      <Tabs.Screen name="index" />
      <Tabs.Screen name="billing" />
      <Tabs.Screen name="inventory" />
      <Tabs.Screen name="analytics" />
      <Tabs.Screen name="chatbot" />
    </Tabs>
  );
}