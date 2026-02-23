import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

function LiquidationHeatmap({ data }) {
  // Debug: log what we receive
  console.log('LiquidationHeatmap data:', data);
  
  if (!data) {
    console.log('LiquidationHeatmap: No data provided');
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

  const { 
    current_price, 
    fragility, 
    estimated, 
    realized_24h, 
    major_zones, 
    insight,
    data_sources 
  } = data;

  const formatAmount = (amount) => {
    if (!amount || amount === 0) return '$0';
    if (amount >= 1e9) return `$${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `$${(amount / 1e6).toFixed(0)}M`;
    if (amount >= 1e3) return `$${(amount / 1e3).toFixed(0)}K`;
    return `$${amount}`;
  };

  const getBarWidth = (amount, maxAmount) => {
    if (!maxAmount || maxAmount === 0 || !amount) return 0;
    return Math.min((amount / maxAmount) * 100, 100);
  };

  const getLevelLabel = (amount, maxAmount) => {
    if (!amount || !maxAmount) return { text: '', class: '' };
    if (amount > maxAmount * 0.25) return { text: '🔴 Major', class: 'text-red-400' };
    if (amount > 1e9) return { text: '🟠 Significant', class: 'text-orange-400' };
    return { text: '', class: '' };
  };

  // Safely convert liquidation objects to arrays
  const shortLiquidations = estimated?.short_liquidations || {};
  const longLiquidations = estimated?.long_liquidations || {};
  
  const shortLevels = Object.entries(shortLiquidations)
    .map(([price, amount]) => ({ price: parseInt(price), amount }))
    .sort((a, b) => b.price - a.price)
    .slice(0, 5);

  const longLevels = Object.entries(longLiquidations)
    .map(([price, amount]) => ({ price: parseInt(price), amount }))
    .sort((a, b) => b.price - a.price)
    .slice(0, 5);

  const maxAmount = Math.max(
    ...shortLevels.map(l => l.amount || 0),
    ...longLevels.map(l => l.amount || 0),
    1
  );

  // Fragility level color
  const getFragilityColor = (score) => {
    if (!score && score !== 0) return 'text-gray-400';
    if (score <= 25) return 'text-green-400';
    if (score <= 50) return 'text-yellow-400';
    if (score <= 75) return 'text-orange-400';
    return 'text-red-400';
  };

  const renderLevel = (level, isShort = false) => {
    if (!level) return null;
    const label = getLevelLabel(level.amount, maxAmount);
    const barWidth = getBarWidth(level.amount, maxAmount);
    
    return (
      <div key={level.price} className="flex items-center gap-3 py-1.5">
        <span className="w-16 font-mono text-sm text-cyber-text-secondary">
          ${(level.price / 1000).toFixed(0)}k
        </span>
        <div className="flex-1 flex items-center gap-2">
          <div className="flex-1 h-5 bg-cyber-surface rounded overflow-hidden">
            <div 
              className={`h-full ${isShort ? 'bg-red-500/70' : 'bg-green-500/70'}`}
              style={{ width: `${barWidth}%` }}
            />
          </div>
          <span className="text-xs text-cyber-text-muted w-14">{formatAmount(level.amount)}</span>
          {label.text && <span className={`text-xs ${label.class}`}>{label.text}</span>}
        </div>
      </div>
    );
  };

  return (
    <section className="bg-cyber-bg-secondary rounded-xl border border-cyber-border-subtle p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">💥</span>
          <h2 className="text-xl font-bold text-cyber-text-primary">BTC LIQUIDATION HEATMAP</h2>
        </div>
        {fragility && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-cyber-surface">
            <span className="text-sm text-cyber-text-secondary">Fragility (Φ):</span>
            <span className={`font-bold font-mono ${getFragilityColor(fragility.score)}`}>
              {fragility.emoji || '⚪'} {fragility.score !== undefined ? fragility.score : 'N/A'}/100 {fragility.level || 'Unknown'}
            </span>
          </div>
        )}
      </div>

      {/* Fragility Components */}
      {fragility?.components && (
        <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
          <div className="bg-cyber-surface rounded p-2 text-center">
            <div className="text-cyber-text-secondary">L_d (Density)</div>
            <div className="font-mono font-bold">{fragility.components.L_d?.value || 'N/A'}</div>
          </div>
          <div className="bg-cyber-surface rounded p-2 text-center">
            <div className="text-cyber-text-secondary">F_σ (Funding)</div>
            <div className="font-mono font-bold">{fragility.components.F_sigma?.value || 'N/A'}</div>
          </div>
          <div className="bg-cyber-surface rounded p-2 text-center">
            <div className="text-cyber-text-secondary">B_z (Basis)</div>
            <div className="font-mono font-bold">{fragility.components.B_z?.value || 'N/A'}</div>
          </div>
        </div>
      )}

      {/* Short Liquidations (Above Price) */}
      <div className="mb-3">
        <div className="text-xs text-cyber-text-secondary mb-2 flex items-center justify-between">
          <span>SHORT LIQUIDATIONS (Above Price)</span>
          <span className="text-xs text-cyber-text-muted">ESTIMATED</span>
        </div>
        <div className="space-y-1">
          {shortLevels.length > 0 ? (
            shortLevels.map(level => renderLevel(level, true))
          ) : (
            <div className="text-sm text-cyber-text-muted py-2">No significant short liquidation levels</div>
          )}
        </div>
      </div>

      {/* Current Price */}
      <div className="flex items-center justify-center py-3 border-y border-cyber-border-subtle my-3">
        <span className="text-lg font-mono font-bold text-cyber-accent-green">
          ${current_price ? current_price.toLocaleString() : 'N/A'}
        </span>
      </div>

      {/* Long Liquidations (Below Price) */}
      <div className="mb-4">
        <div className="space-y-1">
          {longLevels.length > 0 ? (
            longLevels.map(level => renderLevel(level, false))
          ) : (
            <div className="text-sm text-cyber-text-muted py-2">No significant long liquidation levels</div>
          )}
        </div>
        <div className="text-xs text-cyber-text-secondary mt-2 flex items-center justify-between">
          <span>LONG LIQUIDATIONS (Below Price)</span>
          <span className="text-xs text-cyber-text-muted">ESTIMATED</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-cyber-surface rounded-lg p-3">
          <div className="text-xs text-cyber-text-secondary mb-1">Longs at Risk</div>
          <div className="text-lg font-mono font-bold text-green-400">
            {formatAmount(estimated?.total_long_at_risk)}
          </div>
        </div>
        <div className="bg-cyber-surface rounded-lg p-3">
          <div className="text-xs text-cyber-text-secondary mb-1">Shorts at Risk</div>
          <div className="text-lg font-mono font-bold text-red-400">
            {formatAmount(estimated?.total_short_at_risk)}
          </div>
        </div>
      </div>

      {/* Realized 24h */}
      {realized_24h && realized_24h.count > 0 && (
        <div className="bg-cyber-surface rounded-lg p-3 mb-4">
          <div className="text-xs text-cyber-text-secondary mb-2">Realized Liquidations (24h)</div>
          <div className="flex items-center justify-between">
            <span className="text-sm">
              <span className="text-green-400">●</span> Long: {formatAmount(Object.values(realized_24h.long_liquidations || {}).reduce((a, b) => a + b, 0))}
            </span>
            <span className="text-sm">
              <span className="text-red-400">●</span> Short: {formatAmount(Object.values(realized_24h.short_liquidations || {}).reduce((a, b) => a + b, 0))}
            </span>
            <span className="text-xs text-cyber-text-muted">{realized_24h.count} events</span>
          </div>
        </div>
      )}

      {/* Insight */}
      {insight && (
        <div className={`rounded-lg p-3 mb-3 border ${
          (fragility?.score || 0) > 75 ? 'bg-red-500/10 border-red-500/30' :
          (fragility?.score || 0) > 50 ? 'bg-orange-500/10 border-orange-500/30' :
          (fragility?.score || 0) > 25 ? 'bg-yellow-500/10 border-yellow-500/30' :
          'bg-green-500/10 border-green-500/30'
        }`}>
          <div className="flex items-start gap-2">
            <span className="text-lg">{insight.emoji || '⚪'}</span>
            <div>
              <div className="font-bold text-sm">{insight.summary || 'No insight available'}</div>
              {insight.details?.map((detail, i) => (
                <div key={i} className="text-xs text-cyber-text-secondary mt-1">{detail}</div>
              ))}
              {insight.recommendation && (
                <div className="text-xs text-cyber-text-muted mt-2 italic">
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
          {data_sources?.realized && " Realized = actual liquidations from Binance WebSocket."}
        </div>
      </div>
    </section>
  );
}

export default LiquidationHeatmap;
