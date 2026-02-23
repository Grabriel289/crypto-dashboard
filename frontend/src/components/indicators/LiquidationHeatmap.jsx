import React from 'react';
import { Info } from 'lucide-react';

function LiquidationHeatmap({ data }) {
  // If no data yet, show loading
  if (!data) {
    return (
      <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">💥</span>
          <h2 className="text-xl font-bold text-cyber-text-primary">BTC LIQUIDATION HEATMAP</h2>
        </div>
        <div className="text-cyber-text-secondary">Loading liquidation data...</div>
      </section>
    );
  }

  // Destructure with defaults
  const { 
    current_price = 0, 
    fragility = {}, 
    estimated = {}, 
    realized_24h = {}, 
    insight = {}
  } = data;

  const formatAmount = (amount) => {
    if (!amount || amount === 0) return '$0';
    if (amount >= 1e9) return `$${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `$${(amount / 1e6).toFixed(0)}M`;
    return `$${amount}`;
  };

  // Get fragility values with defaults
  const fragScore = fragility?.score ?? 50;
  const fragLevel = fragility?.level || 'Unknown';
  const fragEmoji = fragility?.emoji || '⚪';
  
  // Get liquidation data
  const longLiqs = estimated?.long_liquidations || {};
  const shortLiqs = estimated?.short_liquidations || {};
  const longAtRisk = estimated?.total_long_at_risk || 0;
  const shortAtRisk = estimated?.total_short_at_risk || 0;

  // Convert to arrays and sort
  const shortLevels = Object.entries(shortLiqs)
    .map(([price, amount]) => ({ price: parseInt(price), amount }))
    .sort((a, b) => b.price - a.price);

  const longLevels = Object.entries(longLiqs)
    .map(([price, amount]) => ({ price: parseInt(price), amount }))
    .sort((a, b) => b.price - a.price);

  // Calculate max for bar scaling
  const allAmounts = [...shortLevels, ...longLevels].map(l => l.amount);
  const maxAmount = allAmounts.length > 0 ? Math.max(...allAmounts) : 1;

  // Get color based on fragility score
  const getFragilityColor = (score) => {
    if (score <= 25) return 'text-green-400';
    if (score <= 50) return 'text-yellow-400';
    if (score <= 75) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">💥</span>
          <h2 className="text-xl font-bold text-cyber-text-primary">BTC LIQUIDATION HEATMAP</h2>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-cyber-surface">
          <span className="text-sm text-cyber-text-secondary">Fragility:</span>
          <span className={`font-bold font-mono ${getFragilityColor(fragScore)}`}>
            {fragEmoji} {fragScore.toFixed(1)}/100 {fragLevel}
          </span>
        </div>
      </div>

      {/* Short Liquidations (Above Price) */}
      <div className="mb-3">
        <div className="text-xs text-cyber-text-secondary mb-2 flex justify-between">
          <span>SHORT LIQUIDATIONS (Above Price)</span>
          <span className="text-cyber-text-muted">ESTIMATED</span>
        </div>
        <div className="space-y-1">
          {shortLevels.length > 0 ? shortLevels.map(level => {
            const width = maxAmount > 0 ? (level.amount / maxAmount) * 100 : 0;
            return (
              <div key={level.price} className="flex items-center gap-3">
                <span className="w-16 font-mono text-sm text-cyber-text-secondary">
                  ${(level.price / 1000).toFixed(0)}k
                </span>
                <div className="flex-1 flex items-center gap-2">
                  <div className="flex-1 h-5 bg-cyber-surface rounded overflow-hidden">
                    <div className="h-full bg-red-500/70" style={{ width: `${width}%` }} />
                  </div>
                  <span className="text-xs text-cyber-text-muted w-14">
                    {formatAmount(level.amount)}
                  </span>
                </div>
              </div>
            );
          }) : (
            <div className="text-sm text-cyber-text-muted py-2">No significant short liquidation levels</div>
          )}
        </div>
      </div>

      {/* Current Price */}
      <div className="flex items-center justify-center py-3 border-y border-cyber-border-subtle my-3">
        <span className="text-lg font-mono font-bold text-cyber-accent-green">
          ${current_price ? current_price.toLocaleString() : '---'}
        </span>
      </div>

      {/* Long Liquidations (Below Price) */}
      <div className="mb-4">
        <div className="space-y-1">
          {longLevels.length > 0 ? longLevels.map(level => {
            const width = maxAmount > 0 ? (level.amount / maxAmount) * 100 : 0;
            return (
              <div key={level.price} className="flex items-center gap-3">
                <span className="w-16 font-mono text-sm text-cyber-text-secondary">
                  ${(level.price / 1000).toFixed(0)}k
                </span>
                <div className="flex-1 flex items-center gap-2">
                  <div className="flex-1 h-5 bg-cyber-surface rounded overflow-hidden">
                    <div className="h-full bg-green-500/70" style={{ width: `${width}%` }} />
                  </div>
                  <span className="text-xs text-cyber-text-muted w-14">
                    {formatAmount(level.amount)}
                  </span>
                </div>
              </div>
            );
          }) : (
            <div className="text-sm text-cyber-text-muted py-2">No significant long liquidation levels</div>
          )}
        </div>
        <div className="text-xs text-cyber-text-secondary mt-2 flex justify-between">
          <span>LONG LIQUIDATIONS (Below Price)</span>
          <span className="text-cyber-text-muted">ESTIMATED</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-cyber-surface rounded-lg p-3">
          <div className="text-xs text-cyber-text-secondary mb-1">Longs at Risk</div>
          <div className="text-lg font-mono font-bold text-green-400">
            {formatAmount(longAtRisk)}
          </div>
        </div>
        <div className="bg-cyber-surface rounded-lg p-3">
          <div className="text-xs text-cyber-text-secondary mb-1">Shorts at Risk</div>
          <div className="text-lg font-mono font-bold text-red-400">
            {formatAmount(shortAtRisk)}
          </div>
        </div>
      </div>

      {/* Insight */}
      {insight?.summary && (
        <div className={`rounded-lg p-3 mb-3 border ${
          fragScore > 75 ? 'bg-red-500/10 border-red-500/30' :
          fragScore > 50 ? 'bg-orange-500/10 border-orange-500/30' :
          fragScore > 25 ? 'bg-yellow-500/10 border-yellow-500/30' :
          'bg-green-500/10 border-green-500/30'
        }`}>
          <div className="flex items-start gap-2">
            <span className="text-lg">{insight.emoji || '⚪'}</span>
            <div>
              <div className="font-bold text-sm">{insight.summary}</div>
              {insight.recommendation && (
                <div className="text-xs text-cyber-text-muted mt-1">
                  {insight.recommendation}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="flex items-start gap-2 text-xs text-cyber-text-muted bg-cyber-surface rounded p-2">
        <Info size={14} className="mt-0.5 flex-shrink-0" />
        <div>
          <span className="font-bold">ESTIMATED:</span> Calculated from OI + leverage assumptions. 
          Not actual pending liquidations (~60-70% accuracy).
        </div>
      </div>
    </section>
  );
}

export default LiquidationHeatmap;
