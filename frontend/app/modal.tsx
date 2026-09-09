import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { colors, radius } from '../constants/theme';

export default function Modal() {
  const router = useRouter();
  const params = useLocalSearchParams();

  return (
    <View style={styles.overlay}>
      <View style={styles.sheet}>
        <View style={styles.handle} />
        <Text style={styles.title}>{params.title || 'Details'}</Text>
        <Text style={styles.body}>{params.body || 'No content provided.'}</Text>
        <TouchableOpacity style={styles.closeBtn} onPress={() => router.back()}>
          <Text style={styles.closeBtnText}>Close</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  sheet: { backgroundColor: colors.card, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 28, minHeight: 200 },
  handle: { width: 40, height: 4, borderRadius: 2, backgroundColor: colors.border, alignSelf: 'center', marginBottom: 20 },
  title: { fontSize: 20, fontWeight: '800', color: colors.text, marginBottom: 12 },
  body: { fontSize: 14, color: colors.textSub, lineHeight: 22, marginBottom: 24 },
  closeBtn: { backgroundColor: colors.dark, borderRadius: radius.sm, padding: 16, alignItems: 'center' },
  closeBtnText: { color: '#fff', fontWeight: '800' },
});
