import React from 'react';
import { TrendingUp } from 'lucide-react';
import ReadingBar from './ReadingBar';
import Panel1_BM from './Panel1_BM';
import Panel2_Breadth90D from './Panel2_Breadth90D';

const STATE_COLORS = {
  ENTRY:        { color: "#00e676", border: "rgba(0,230,118,0.35)" },
  RISING:       { color: "#ffeb3b", border: "rgba(255,235,59,0.25)" },
  PEAK_WARNING: { color: "#ff9800", border: "rgba(255,152,0,0.35)" },
  EXIT:         { color: "#f4511e", border: "rgba(244,81,30,0.35)" },
  NEUTRAL:      { color: "#90a4ae", border: "rgba(144,164,174,0.20)" },
};

const COMBINED_READING = [
  {
    key: "ENTRY",
    title: "Entry",
    color: "#00e676",
    desc: "Altcoin momentum is accelerating and the market has room to grow",
    action: "Open positions",
  },
  {
    key: "PEAK_WARNING",
    title: "Caution",
    color: "#ff9800",
    desc: "Most altcoins are already outperforming — the cycle may be near its peak",
    action: "Reduce / stop adding",
  },
  {
    key: "EXIT",
    title: "Exit",
    color: "#f4511e",
    desc: "Altcoin momentum is fading — rotation back to BTC or stablecoins",
    action: "Close positions",
  },
];

function ABMPanel({ data }) {
  if (!data || data.error) {
    return (
      <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">ALTCOIN BREADTH MOMENTUM</h2>
        </div>
        <div className="text-center text-cyber-text-muted py-8">
          {data?.error ? `Error: ${data.error}` : "Loading ABM data..."}
        </div>
      </section>
    );
  }

  const {
    bm_series, bm_current,
    breadth_90d_series, breadth_90d_current,
    breadth_30d, valid_count, outperform_count,
    btc_gate, combined_state, bm_signal, breadth_90d_signal,
  } = data;

  const stateColors = STATE_COLORS[combined_state] || STATE_COLORS.NEUTRAL;

  return (
    <section
      className="bg-cyber-bg-secondary rounded-xl p-6"
      style={{ border: `1px solid ${stateColors.border}` }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-cyber-accent-cyan" />
          <h2 className="text-xl font-bold text-white">ALTCOIN BREADTH MOMENTUM</h2>
        </div>
        <div className="flex items-center gap-3 text-sm text-cyber-text-muted">
          <span>{outperform_count ?? "--"}/{valid_count ?? "--"} coins tracked</span>
        </div>
      </div>

      {/* ReadingBar — current signal summary */}
      <ReadingBar
        bmCurrent={bm_current}
        breadth90dCurrent={breadth_90d_current}
        bmSignal={bm_signal}
        breadth90dSignal={breadth_90d_signal}
        btcGate={btc_gate}
        combinedState={combined_state}
      />

      {/* Panel 1: BM Signal Chart */}
      <Panel1_BM data={bm_series} bmSignal={bm_signal} />

      {/* Panel 2: Altcoin Breadth 90D Chart */}
      <Panel2_Breadth90D data={breadth_90d_series} breadth90dSignal={breadth_90d_signal} />

      {/* Combined Reading — 3 columns */}
      <div className="grid grid-cols-3 gap-3 mt-2">
        {COMBINED_READING.map((item) => {
          const isActive = combined_state === item.key;
          return (
            <div
              key={item.key}
              className="rounded-lg p-3"
              style={{
                background: isActive ? item.color + "15" : item.color + "08",
                border: `1px solid ${isActive ? item.color + "55" : item.color + "22"}`,
              }}
            >
              <div className="text-sm font-bold mb-2" style={{ color: item.color }}>
                {item.title}
                {isActive && <span className="ml-1 text-xs opacity-70">(ACTIVE)</span>}
              </div>
              <div className="text-xs text-cyber-text-secondary mb-2">
                {item.desc}
              </div>
              <div className="text-xs font-semibold" style={{ color: item.color }}>
                Action: {item.action}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-cyber-border-subtle">
        <p className="text-sm text-cyber-text-muted text-center">
          BM = Altcoin momentum signal | Breadth 90D = % of altcoins outperforming BTC | Updated hourly
        </p>
      </div>
    </section>
  );
}

export default ABMPanel;
