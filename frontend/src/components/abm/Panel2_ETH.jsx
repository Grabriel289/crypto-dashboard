import React, { useMemo } from 'react';
import {
  ComposedChart, CartesianGrid, XAxis, YAxis, Tooltip,
  ReferenceLine, Area, Line, ResponsiveContainer,
} from 'recharts';

function PeakWarningDot({ cx, cy, payload, index }) {
  if (index < 1 || !cx || !cy) return null;
  const prevRoc = payload._prev;
  if (prevRoc == null) return null;

  // Peak warning: ROC crosses 0 downward
  if (prevRoc > 0 && payload.roc <= 0) {
    return (
      <g>
        <circle cx={cx} cy={cy} r={6} fill="#ff9800" stroke="#0f1420" strokeWidth={2} />
        <text x={cx - 28} y={cy - 12} fill="#ff9800" fontSize={11} fontWeight="bold">
          PEAK
        </text>
      </g>
    );
  }
  return null;
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg px-3 py-2 text-sm" style={{ background: "#0f1420", border: "1px solid rgba(255,255,255,0.1)" }}>
      <div className="text-cyber-text-muted mb-1">{d.date}</div>
      <div className="font-mono font-bold" style={{ color: d.roc >= 0 ? "#00bcd4" : "#ff9800" }}>
        ETH/BTC ROC: {d.roc >= 0 ? "+" : ""}{d.roc.toFixed(2)}%
      </div>
    </div>
  );
}

function Panel2_ETH({ data, ethRocSignal }) {
  // Inject _prev for signal dot detection
  const enriched = useMemo(() => {
    if (!data || data.length === 0) return [];
    return data.map((d, i) => ({
      ...d,
      _prev: i > 0 ? data[i - 1].roc : null,
    }));
  }, [data]);

  // Compute XAxis ticks: show every 14th date
  const ticks = useMemo(() => {
    if (!enriched.length) return [];
    return enriched.filter((_, i) => i % 14 === 0).map(d => d.date);
  }, [enriched]);

  if (!enriched.length) return null;

  const signalColor = ethRocSignal === "STRONG" ? "#00e676"
    : ethRocSignal === "POSITIVE" ? "#00bcd4"
    : ethRocSignal === "WARNING" ? "#ff9800"
    : ethRocSignal === "BEARISH" ? "#f4511e"
    : "#90a4ae";

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-cyber-text-muted uppercase tracking-wider">
          Panel 2: ETH/BTC ROC (14D)
        </span>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: signalColor,
            background: signalColor + "18",
            border: `1px solid ${signalColor}44`,
          }}
        >
          {ethRocSignal}
        </span>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={enriched} margin={{ top: 8, right: 50, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="ethRocGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00bcd4" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#00bcd4" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="rgba(84,110,122,0.2)" />

          <XAxis
            dataKey="date"
            tick={{ fill: "#546e7a", fontSize: 11 }}
            ticks={ticks}
            axisLine={{ stroke: "rgba(84,110,122,0.3)" }}
            tickLine={false}
          />
          <YAxis
            domain={[-12, 12]}
            tick={{ fill: "#546e7a", fontSize: 11 }}
            tickFormatter={(v) => `${v > 0 ? "+" : ""}${v}%`}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Reference lines */}
          <ReferenceLine y={3} stroke="#00e676" strokeDasharray="5 5"
            label={{ value: "Strong +3%", position: "right", fill: "#00e676", fontSize: 11 }} />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.3)" strokeWidth={1} />
          <ReferenceLine y={-3} stroke="#ff9800" strokeDasharray="5 5"
            label={{ value: "Warn -3%", position: "right", fill: "#ff9800", fontSize: 11 }} />

          {/* Area fill */}
          <Area
            type="monotone"
            dataKey="roc"
            fill="url(#ethRocGradient)"
            stroke="none"
            isAnimationActive={false}
          />

          {/* Main line with peak warning dots */}
          <Line
            type="monotone"
            dataKey="roc"
            stroke="#00bcd4"
            strokeWidth={2}
            dot={<PeakWarningDot />}
            activeDot={{ r: 4, fill: "#00bcd4" }}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Panel2_ETH;
