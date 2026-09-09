import React, { useState } from 'react';
import Svg, { Rect, Text as SvgText, Defs, LinearGradient, Stop } from 'react-native-svg';
import { colors } from '../constants/theme';
import { Pressable } from 'react-native';

interface DataPoint { label: string; value: number; }
interface Props { data: DataPoint[]; width?: number; height?: number; color?: string; }

export default function BarChart({ data, width = 300, height = 160, color = colors.primary }: Props) {
  const pad = { top: 12, bottom: 28, left: 8, right: 8 };
  const chartW = width - pad.left - pad.right;
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const chartH = height - pad.top - pad.bottom;
  const maxV = Math.max(...data.map(d => d.value));
  const barW = (chartW / data.length) * 0.55;
  const gap = chartW / data.length;

  return (
    <Svg width={width} height={height}>
      <Defs>
        <LinearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
          <Stop offset="0" stopColor={color} stopOpacity="1" />
          <Stop offset="1" stopColor={color} stopOpacity="0.4" />
        </LinearGradient>
      </Defs>
      {data.map((d, i) => {
  const barH = (d.value / maxV) * chartH;
  const x = pad.left + i * gap + (gap - barW) / 2;
  const y = pad.top + chartH - barH;

  return (
    <React.Fragment key={i}>
      
      {/* BAR */}
      <Rect
  x={x}
  y={y}
  width={barW}
  height={barH}
  rx={6}
  fill={activeIndex === i ? "#6366F1" : "url(#barGrad)"}
  onPressIn={() => setActiveIndex(i)}
  onPressOut={() => setActiveIndex(null)}
/>
    {activeIndex === i && (
  <>
    {/* Value Tooltip */}
    <SvgText
      x={x + barW / 2}
      y={y - 10}
      textAnchor="middle"
      fontSize={12}
      fill="#fff"
      fontWeight="bold"
    >
      ₹{d.value}
    </SvgText>

    {/* Glow effect */}
    <Rect
      x={x}
      y={y}
      width={barW}
      height={barH}
      rx={6}
      fill="rgba(99,102,241,0.15)"
    />
  </>
)}
      {/* VALUE ON HOVER */}
      {activeIndex === i && (
        <SvgText
          x={x + barW / 2}
          y={y - 6}
          textAnchor="middle"
          fontSize={11}
          fill="#fff"
          fontWeight="bold"
        >
          ₹{d.value}
        </SvgText>
      )}

      {/* LABEL */}
      <SvgText
        x={x + barW / 2}
        y={height - 6}
        textAnchor="middle"
        fontSize={9}
        fill={colors.textSub}
      >
        {d.label}
      </SvgText>

    </React.Fragment>
  );
})}
    </Svg>
  );
}