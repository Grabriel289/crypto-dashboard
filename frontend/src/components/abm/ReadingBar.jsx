import React from 'react';

const STATE_COLORS = {
  ENTRY:        { color: "#00e676", label: "ENTRY ZONE" },
  RISING:       { color: "#ffeb3b", label: "RISING" },
  PEAK_WARNING: { color: "#ff9800", label: "PEAK WARNING" },
  EXIT:         { color: "#f4511e", label: "EXIT ZONE" },
  NEUTRAL:      { color: "#90a4ae", label: "NEUTRAL" },
};

const ETH_ROC_LABELS = {
  STRONG:   { color: "#00e676", label: "STRONG" },
  POSITIVE: { color: "#00bcd4", label: "POSITIVE" },
  WARNING:  { color: "#ff9800", label: "WARNING" },
  BEARISH:  { color: "#f4511e", label: "BEARISH" },
};

function ReadingBar({ bmCurrent, ethRocCurrent, bmSignal, ethRocSignal, btcGate, combinedState }) {
  const stateInfo = STATE_COLORS[combinedState] || STATE_COLORS.NEUTRAL;
  const ethInfo = ETH_ROC_LABELS[ethRocSignal] || ETH_ROC_LABELS.POSITIVE;
  const gatePassed = btcGate === "PASS";

  const formatValue = (val) => {
    if (val == null) return "--";
    const sign = val >= 0 ? "+" : "";
    return `${sign}${val.toFixed(1)}%`;
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
          {formatValue(bmCurrent)}
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

      {/* ETH/BTC ROC */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-cyber-text-muted">ETH/BTC ROC:</span>
        <span className="text-base font-bold font-mono" style={{ color: ethInfo.color }}>
          {formatValue(ethRocCurrent)}
        </span>
        <span
          className="text-xs font-semibold px-2 py-0.5 rounded-full"
          style={{
            color: ethInfo.color,
            background: ethInfo.color + "18",
            border: `1px solid ${ethInfo.color}44`,
          }}
        >
          {ethInfo.label}
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
