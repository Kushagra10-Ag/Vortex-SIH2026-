import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Path, Circle } from 'react-native-svg';

interface Slice { label: string; value: number; color: string; }
interface Props { data: Slice[]; size?: number; }

function polarToXY(cx: number, cy: number, r: number, angle: number) {
  return {
    x: cx + r * Math.cos((angle - 90) * (Math.PI / 180)),
    y: cy + r * Math.sin((angle - 90) * (Math.PI / 180)),
  };
}

export default function PieChart({ data, size = 160 }: Props) {
  const cx = size / 2, cy = size / 2, r = size / 2 - 10, inner = r * 0.55;
  const total = data.reduce((s, d) => s + d.value, 0);
  let startAngle = 0;

  return (
    <View style={styles.wrap}>
      <Svg width={size} height={size}>
        {data.map((slice, i) => {
          const angle = (slice.value / total) * 360;
          const end = startAngle + angle;
          const large = angle > 180 ? 1 : 0;
          const s = polarToXY(cx, cy, r, startAngle);
          const e = polarToXY(cx, cy, r, end);
          const si = polarToXY(cx, cy, inner, startAngle);
          const ei = polarToXY(cx, cy, inner, end);
          const path = `M${s.x},${s.y} A${r},${r} 0 ${large},1 ${e.x},${e.y} L${ei.x},${ei.y} A${inner},${inner} 0 ${large},0 ${si.x},${si.y} Z`;
          startAngle = end;
          return <Path key={i} d={path} fill={slice.color} />;
        })}
      </Svg>
      <View style={styles.legend}>
        {data.map((s, i) => (
          <View key={i} style={styles.item}>
            <View style={[styles.dot, { backgroundColor: s.color }]} />
            <Text style={styles.label}>{s.label}</Text>
            <Text style={styles.val}>{s.value}%</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  legend: { flex: 1, gap: 6 },
  item: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  label: { flex: 1, fontSize: 12, color: '#556677' },
  val: { fontSize: 12, fontWeight: '700', color: '#1A2332' },
});
