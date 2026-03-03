import React from 'react';
import { TrendingUp } from 'lucide-react';
import ReadingBar from './ReadingBar';
import Panel1_BM from './Panel1_BM';
import Panel2_ETH from './Panel2_ETH';

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
    title: "Entry Signal",
    color: "#00e676",
    p1: "BM crosses +5% upward",
    p2: "ETH/BTC ROC > 0",
    action: "Open positions",
  },
  {
    key: "PEAK_WARNING",
    title: "Peak Warning",
    color: "#ff9800",
    p1: "BM still positive",
    p2: "ETH/BTC ROC crosses 0 downward",
    action: "Reduce / stop adding",
  },
  {
    key: "EXIT",
    title: "Exit Signal",
    color: "#f4511e",
    p1: "BM crosses -5% downward",
    p2: "ETH/BTC ROC < -3%",
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
    eth_roc_series, eth_roc_current,
    breadth_30d, valid_count, outperform_count,
    btc_gate, combined_state, bm_signal, eth_roc_signal,
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
        <div className="flex items-center gap-3 text-xs text-cyber-text-muted">
          <span>Breadth: <span className="text-white font-mono">{breadth_30d?.toFixed(1) ?? "--"}%</span></span>
          <span>{outperform_count ?? "--"}/{valid_count ?? "--"} coins</span>
        </div>
      </div>

      {/* ReadingBar — current signal summary */}
      <ReadingBar
        bmCurrent={bm_current}
        ethRocCurrent={eth_roc_current}
        bmSignal={bm_signal}
        ethRocSignal={eth_roc_signal}
        btcGate={btc_gate}
        combinedState={combined_state}
      />

      {/* Panel 1: BM Signal Chart */}
      <Panel1_BM data={bm_series} bmSignal={bm_signal} />

      {/* Panel 2: ETH/BTC ROC Chart */}
      <Panel2_ETH data={eth_roc_series} ethRocSignal={eth_roc_signal} />

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
              <div className="text-xs font-bold mb-2" style={{ color: item.color }}>
                {item.title}
                {isActive && <span className="ml-1 text-[9px] opacity-70">(ACTIVE)</span>}
              </div>
              <div className="text-[10px] text-cyber-text-secondary mb-1">
                P1: {item.p1}
              </div>
              <div className="text-[10px] text-cyber-text-secondary mb-2">
                P2: {item.p2}
              </div>
              <div className="text-[10px] font-semibold" style={{ color: item.color }}>
                Action: {item.action}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-cyber-border-subtle">
        <p className="text-xs text-cyber-text-muted text-center">
          BM = Breadth Momentum (14D MoM of 30D altcoin outperformance vs BTC) | ETH/BTC ROC = 7D rate of change | Updated hourly
        </p>
      </div>
    </section>
  );
}

export default ABMPanel;
