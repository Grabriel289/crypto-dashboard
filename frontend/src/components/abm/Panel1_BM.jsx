import React, { useMemo } from 'react';
import {
  ComposedChart, CartesianGrid, XAxis, YAxis, Tooltip,
  ReferenceLine, Area, Line, ResponsiveContainer,
} from 'recharts';

const BM_ENTRY = 5;
const BM_EXIT = -5;

function BMSignalDot({ cx, cy, payload, index }) {
  if (index < 1 || !cx || !cy) return null;
  // We rely on the data array's prev value being passed via payload._prev
  const prevBm = payload._prev;
  if (prevBm == null) return null;

  // Entry: crosses +5 upward
  if (prevBm < BM_ENTRY && payload.bm >= BM_ENTRY) {
    return <circle cx={cx} cy={cy} r={5} fill="#00e676" stroke="#0f1420" strokeWidth={2} />;
  }
  // Exit: crosses -5 downward
  if (prevBm > BM_EXIT && payload.bm <= BM_EXIT) {
    return <circle cx={cx} cy={cy} r={5} fill="#f4511e" stroke="#0f1420" strokeWidth={2} />;
  }
  return null;
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg px-3 py-2 text-xs" style={{ background: "#0f1420", border: "1px solid rgba(255,255,255,0.1)" }}>
      <div className="text-cyber-text-muted mb-1">{d.date}</div>
      <div className="font-mono font-bold" style={{ color: d.bm >= 0 ? "#00e676" : "#f4511e" }}>
        BM: {d.bm >= 0 ? "+" : ""}{d.bm.toFixed(2)}%
      </div>
    </div>
  );
}

function Panel1_BM({ data, bmSignal }) {
  // Inject _prev for signal dot detection
  const enriched = useMemo(() => {
    if (!data || data.length === 0) return [];
    return data.map((d, i) => ({
      ...d,
      _prev: i > 0 ? data[i - 1].bm : null,
    }));
  }, [data]);

  // Compute XAxis ticks: show every 14th date
  const ticks = useMemo(() => {
    if (!enriched.length) return [];
    return enriched.filter((_, i) => i % 14 === 0).map(d => d.date);
  }, [enriched]);

  if (!enriched.length) return null;

  const signalColor = bmSignal === "ENTRY" ? "#00e676"
    : bmSignal === "EXIT" ? "#f4511e"
    : bmSignal === "RISING" ? "#ffeb3b"
    : "#90a4ae";

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-cyber-text-muted uppercase tracking-wider">
          Panel 1: BM Signal (14D MoM)
        </span>
        <span
          className="text-[9px] font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: signalColor,
            background: signalColor + "18",
            border: `1px solid ${signalColor}44`,
          }}
        >
          {bmSignal}
        </span>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <ComposedChart data={enriched} margin={{ top: 8, right: 50, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="bmGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00e676" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#00e676" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="rgba(84,110,122,0.2)" />

          <XAxis
            dataKey="date"
            tick={{ fill: "#546e7a", fontSize: 9 }}
            ticks={ticks}
            axisLine={{ stroke: "rgba(84,110,122,0.3)" }}
            tickLine={false}
          />
          <YAxis
            domain={[-15, 15]}
            tick={{ fill: "#546e7a", fontSize: 9 }}
            tickFormatter={(v) => `${v > 0 ? "+" : ""}${v}%`}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Reference lines */}
          <ReferenceLine y={BM_ENTRY} stroke="#00e676" strokeDasharray="5 5"
            label={{ value: "Entry +5%", position: "right", fill: "#00e676", fontSize: 9 }} />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.3)" strokeWidth={1} />
          <ReferenceLine y={BM_EXIT} stroke="#f4511e" strokeDasharray="5 5"
            label={{ value: "Exit -5%", position: "right", fill: "#f4511e", fontSize: 9 }} />

          {/* Area fill */}
          <Area
            type="monotone"
            dataKey="bm"
            fill="url(#bmGradient)"
            stroke="none"
            isAnimationActive={false}
          />

          {/* Main line with signal dots */}
          <Line
            type="monotone"
            dataKey="bm"
            stroke="#00e676"
            strokeWidth={2}
            dot={<BMSignalDot />}
            activeDot={{ r: 4, fill: "#00e676" }}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export default Panel1_BM;
