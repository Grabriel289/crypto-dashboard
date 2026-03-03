import React from 'react';

const STATE_COLORS = {
  ENTRY:        { color: "#00e676", label: "ENTRY ZONE" },
  RISING:       { color: "#ffeb3b", label: "RISING" },
  PEAK_WARNING: { color: "#ff9800", label: "PEAK WARNING" },
  EXIT:         { color: "#f4511e", label: "EXIT ZONE" },
  NEUTRAL:      { color: "#90a4ae", label: "NEUTRAL" },
};

const BREADTH_90D_LABELS = {
  PEAK:     { color: "#ff9800", label: "PEAK" },
  HIGH:     { color: "#00e676", label: "HIGH" },
  MODERATE: { color: "#00bcd4", label: "MODERATE" },
  LOW:      { color: "#90a4ae", label: "LOW" },
};

function ReadingBar({ bmCurrent, breadth90dCurrent, bmSignal, breadth90dSignal, btcGate, combinedState }) {
  const stateInfo = STATE_COLORS[combinedState] || STATE_COLORS.NEUTRAL;
  const breadthInfo = BREADTH_90D_LABELS[breadth90dSignal] || BREADTH_90D_LABELS.MODERATE;
  const gatePassed = btcGate === "PASS";

  const formatBm = (val) => {
    if (val == null) return "--";
    const sign = val >= 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
  };

  const formatBreadth = (val) => {
    if (val == null) return "--";
    return `${val.toFixed(1)}%`;
  };

  return (
    <div
      className="rounded-lg px-4 py-3 mb-4 flex flex-wrap items-center gap-4 justify-between"
      style={{
        background: "rgba(255,255,255,0.02)",
        border: `1px solid ${stateInfo.color}33`,
      }}
    >
      {/* Label */}
      <span className="text-sm font-semibold text-cyber-text-muted uppercase tracking-wider">NOW</span>

      {/* BM Signal */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-cyber-text-muted">BM Signal:</span>
        <span className="text-base font-bold font-mono" style={{ color: stateInfo.color }}>
          {formatBm(bmCurrent)}
        </span>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: stateInfo.color,
            background: stateInfo.color + "18",
            border: `1px solid ${stateInfo.color}44`,
          }}
        >
          {stateInfo.label}
        </span>
      </div>

      {/* Divider */}
      <div className="hidden md:block w-px h-5" style={{ background: "rgba(255,255,255,0.1)" }} />

      {/* Breadth 90D */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-cyber-text-muted">Breadth 90D:</span>
        <span className="text-base font-bold font-mono" style={{ color: breadthInfo.color }}>
          {formatBreadth(breadth90dCurrent)}
        </span>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: breadthInfo.color,
            background: breadthInfo.color + "18",
            border: `1px solid ${breadthInfo.color}44`,
          }}
        >
          {breadthInfo.label}
        </span>
      </div>

      {/* Divider */}
      <div className="hidden md:block w-px h-5" style={{ background: "rgba(255,255,255,0.1)" }} />

      {/* BTC Gate */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-cyber-text-muted">BTC Gate:</span>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: gatePassed ? "#00e676" : "#f4511e",
            background: gatePassed ? "rgba(0,230,118,0.1)" : "rgba(244,81,30,0.1)",
            border: `1px solid ${gatePassed ? "rgba(0,230,118,0.3)" : "rgba(244,81,30,0.3)"}`,
          }}
        >
          {gatePassed ? "PASS" : "FAIL"}
        </span>
      </div>
    </div>
  );
}

export default ReadingBar;
