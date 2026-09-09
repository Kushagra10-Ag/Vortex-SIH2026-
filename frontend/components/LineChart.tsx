import React, { useState, useEffect, useRef } from 'react';
import Svg, { Path, Circle, Defs, LinearGradient, Stop, Text as SvgText, Line } from 'react-native-svg';
import { Animated } from 'react-native';

interface DataPoint { label: string; value: number; }
interface Props {
  data: DataPoint[];
  width?: number;
  height?: number;
  color?: string;
}

export default function LineChart({
  data,
  width = 300,
  height = 180,
  color = "#4F8EF7",
}: Props) {

  const animValue = useRef(new Animated.Value(0)).current;
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    animValue.setValue(0);
    const listener = animValue.addListener(({ value }) => setProgress(value));

    Animated.timing(animValue, {
      toValue: 1,
      duration: 1500,
      useNativeDriver: false,
    }).start();

    return () => animValue.removeListener(listener);
  }, [data]);

  const pad = { top: 12, bottom: 28, left: 10, right: 10 };
  const chartW = width - pad.left - pad.right;
  const chartH = height - pad.top - pad.bottom;

  const vals = data.map(d => d.value);
  const minV = Math.min(...vals) * 0.9;
  const maxV = Math.max(...vals) * 1.05;
  const range = maxV - minV;

  const toX = (i: number) => pad.left + (i / (data.length - 1)) * chartW;
  const toY = (v: number) => pad.top + chartH - ((v - minV) / range) * chartH;

  if (!data || data.length < 2) return null;

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

  const areaPath =
    displayPoints.length > 1
      ? `${linePath} L${displayPoints[displayPoints.length - 1].x},${pad.top + chartH} L${displayPoints[0].x},${pad.top + chartH} Z`
      : '';

  return (
    <Svg width={width} height={height}>
      <Defs>
        <LinearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
          <Stop offset="0" stopColor={color} stopOpacity="0.3" />
          <Stop offset="1" stopColor={color} stopOpacity="0.05" />
        </LinearGradient>
      </Defs>

      {/* Area */}
      {areaPath ? <Path d={areaPath} fill="url(#grad)" /> : null}

      {/* Line */}
      {linePath ? (
        <Path
          d={linePath}
          stroke={color}
          strokeWidth={2.5}
          fill="none"
          strokeLinecap="round"
        />
      ) : null}

      {/* Points */}
      {displayPoints.map((p, i) => (
        <Circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={i === displayPoints.length - 1 ? 5 : 3}
          fill={i === displayPoints.length - 1 ? color : "#1E293B"}
          stroke={color}
          strokeWidth={2}
        />
      ))}

      {/* Labels */}
      {data.map((d, i) => (
        <SvgText
          key={i}
          x={toX(i)}
          y={height - 6}
          textAnchor="middle"
          fontSize={9}
          fill="rgba(255,255,255,0.4)"
        >
          {d.label}
        </SvgText>
      ))}
    </Svg>
  );
}