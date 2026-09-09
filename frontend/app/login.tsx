import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Dimensions, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { colors, radius } from '../constants/theme';

const { width } = Dimensions.get('window');

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = () => {
    if (!email || !password) {
      setError('Please enter email and password');
      return;
    }
    setError('');
    setLoading(true);
    // Mock auth — swap with real API call
    setTimeout(() => {
      setLoading(false);
      router.replace('/(tabs)');
    }, 1000);
  };

  return (
    <View style={styles.container}>
      <View style={styles.bg1} />
      <View style={styles.bg2} />
      <View style={styles.bg3} />

      <View style={styles.card}>
        <View style={styles.logoWrap}>
          <Text style={styles.logoIcon}>📊</Text>
        </View>
        <Text style={styles.brand}>BIZMATE</Text>
        <Text style={styles.sub}>Your Smart Business Partner</Text>

        {error ? <View style={styles.errorBox}><Text style={styles.errorText}>{error}</Text></View> : null}

        <View style={styles.inputWrap}>
          <Text style={styles.inputLabel}>Email</Text>
          <TextInput
            style={styles.input}
            placeholder="you@business.com"
            placeholderTextColor={colors.textSub}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />
        </View>

        <View style={styles.inputWrap}>
          <Text style={styles.inputLabel}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            placeholderTextColor={colors.textSub}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </View>

        <TouchableOpacity style={styles.forgotWrap}>
          <Text style={styles.forgotText}>Forgot password?</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.btn, loading && styles.btnDisabled]} onPress={handleLogin} disabled={loading}>
          {loading
            ? <ActivityIndicator color="#fff" />
            : <Text style={styles.btnText}>Sign In →</Text>
          }
        </TouchableOpacity>

        <View style={styles.divRow}>
          <View style={styles.div} />
          <Text style={styles.divText}>or continue with</Text>
          <View style={styles.div} />
        </View>

        <View style={styles.socialRow}>
          {[{ icon: 'G', label: 'Google' }, { icon: 'f', label: 'Facebook' }, { icon: '🍎', label: 'Apple' }].map((s, i) => (
            <TouchableOpacity key={i} style={styles.socialBtn} onPress={handleLogin}>
              <Text style={styles.socialText}>{s.icon}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.hint}>Demo: any email + any password</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, backgroundColor: '#0D1B2A',
    alignItems: 'center', justifyContent: 'center',
  },
  bg1: { position: 'absolute', width: 350, height: 350, borderRadius: 175, backgroundColor: colors.primary + '18', top: -80, left: -80 },
  bg2: { position: 'absolute', width: 250, height: 250, borderRadius: 125, backgroundColor: '#7B61FF18', bottom: 80, right: -60 },
  bg3: { position: 'absolute', width: 150, height: 150, borderRadius: 75, backgroundColor: colors.accent + '12', top: 100, right: 30 },
  card: {
    width: width * 0.55,
    maxWidth: 480,
    backgroundColor: colors.card,
    borderRadius: 28, padding: 28,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 20 },
    shadowOpacity: 0.35,
    shadowRadius: 40,
    elevation: 20,
  },
  logoWrap: {
    width: 72, height: 72, borderRadius: 36,
    backgroundColor: colors.dark,
    alignItems: 'center', justifyContent: 'center',
    marginBottom: 14,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
  },
  logoIcon: { fontSize: 32 },
  brand: { fontSize: 28, fontWeight: '900', color: colors.text, letterSpacing: 4, marginBottom: 4 },
  sub: { fontSize: 13, color: colors.textSub, marginBottom: 24 },
  errorBox: { width: '100%', backgroundColor: colors.danger + '18', borderRadius: 10, padding: 10, marginBottom: 12, borderWidth: 1, borderColor: colors.danger + '40' },
  errorText: { color: colors.danger, fontSize: 12, textAlign: 'center' },
  inputWrap: { width: '100%', marginBottom: 12 },
  inputLabel: { fontSize: 11, fontWeight: '700', color: colors.textSub, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 },
  input: {
    borderWidth: 1.5, borderColor: colors.border, borderRadius: radius.sm,
    padding: 14, fontSize: 14, color: colors.text, backgroundColor: colors.bg,
  },
  forgotWrap: { alignSelf: 'flex-end', marginBottom: 20 },
  forgotText: { fontSize: 12, color: colors.primary, fontWeight: '600' },
  btn: {
    width: '100%', backgroundColor: colors.dark,
    borderRadius: radius.sm, padding: 16,
    alignItems: 'center',
    shadowColor: colors.dark,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 6,
  },
  btnDisabled: { opacity: 0.7 },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '800', letterSpacing: 0.5 },
  divRow: { flexDirection: 'row', alignItems: 'center', width: '100%', marginVertical: 18, gap: 10 },
  div: { flex: 1, height: 1, backgroundColor: colors.border },
  divText: { fontSize: 12, color: colors.textSub },
  socialRow: { flexDirection: 'row', gap: 14, marginBottom: 4 },
  socialBtn: {
    width: 54, height: 54, borderRadius: 14,
    borderWidth: 1.5, borderColor: colors.border,
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.bg,
  },
  socialText: { fontSize: 18, fontWeight: '700', color: colors.text },
  hint: { marginTop: 18, fontSize: 11, color: colors.textSub + '99' },
});
