import React from 'react';
import { AlertTriangle, Skull } from 'lucide-react';

function LiquidationHeatmap({ data }) {
  if (!data?.heatmap) return null;

  const { heatmap } = data;
  const { short_levels, long_levels, current_price, nearest_liquidation, total_longs, total_shorts } = heatmap;

  const formatAmount = (amount) => {
    if (amount >= 1e9) return `$${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `$${(amount / 1e6).toFixed(0)}M`;
    return `$${amount}`;
  };

  const getBarWidth = (amount) => {
    const max = 3e9; // Max expected liquidation
    return Math.min((amount / max) * 100, 100);
  };

  const getLabel = (amount) => {
    if (amount > 2.5e9) return { text: '💀 Liquidation wall', class: 'text-red-400' };
    if (amount > 1.5e9) return { text: '🔴 Major cluster', class: 'text-orange-400' };
    return { text: '', class: '' };
  };

  const renderLevel = (level, isShort = false) => {
    const label = getLabel(level.amount);
    const barWidth = getBarWidth(level.amount);
    
    return (
      <div key={level.price} className="flex items-center gap-4 py-2">
        <span className="w-20 font-mono text-cyber-text-secondary">${(level.price / 1000).toFixed(0)}k</span>
        <div className="flex-1 flex items-center gap-2">
          <div 
            className={`h-6 rounded ${isShort ? 'bg-red-500/50' : 'bg-green-500/50'}`}
            style={{ width: `${barWidth}%` }}
          />
          <span className="text-sm text-cyber-text-muted w-16">{formatAmount(level.amount)}</span>
          {label.text && <span className={`text-xs ${label.class}`}>{label.text}</span>}
        </div>
      </div>
    );
  };

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">💥</span>
        <h2 className="text-xl font-bold text-cyber-text-primary">BTC LIQUIDATION HEATMAP</h2>
      </div>

      {/* Short Liquidations (Above Price) */}
      <div className="mb-4">
        <div className="text-sm text-cyber-text-secondary mb-2 border-b border-cyber-border-subtle pb-2">
          ─────────────── SHORT LIQUIDATIONS (Above) ───────────────
        </div>
        <div className="space-y-1">
          {short_levels?.map(level => renderLevel(level, true))}
        </div>
      </div>

      {/* Current Price */}
      <div className="flex items-center justify-center py-4 border-y border-cyber-border-subtle my-4">
        <span className="text-lg font-mono font-bold text-cyber-accent-green">
          ════════════════ ▶ ${current_price?.toLocaleString()} CURRENT ◀ ════════════════
        </span>
      </div>

      {/* Long Liquidations (Below Price) */}
      <div className="mb-4">
        <div className="space-y-1">
          {long_levels?.map(level => renderLevel(level, false))}
        </div>
        <div className="text-sm text-cyber-text-secondary mt-2 pt-2 border-t border-cyber-border-subtle">
          ─────────────── LONG LIQUIDATIONS (Below) ────────────────
        </div>
      </div>

      {/* Summary */}
      <div className="bg-cyber-surface rounded-lg p-4 border border-cyber-border-subtle">
        <div className="flex items-center gap-2 text-yellow-400 mb-2">
          <AlertTriangle size={18} />
          <span className="font-bold">
            Nearest: ${nearest_liquidation?.price?.toLocaleString()} ({nearest_liquidation?.side}) — {formatAmount(nearest_liquidation?.amount)} at risk
          </span>
        </div>
        <div className="text-sm text-cyber-text-secondary">
          📊 Longs: {formatAmount(total_longs)} | Shorts: {formatAmount(total_shorts)}
        </div>
      </div>
    </section>
  );
}

export default LiquidationHeatmap;
